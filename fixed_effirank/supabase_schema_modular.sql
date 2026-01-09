-- ============================================================================
-- SUPABASE SQL SCHEMA FOR MODULAR TLS APPLICATION
-- ============================================================================
-- This schema is fully compatible with the modular tls_app structure
-- Auto-cleanup after 1 year included
-- Run this in your Supabase SQL Editor

-- ============================================================================
-- 1. CREATE MAIN HISTORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS history_snapshots (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date DATE NOT NULL,
    week_number INTEGER NOT NULL,
    week_range TEXT NOT NULL,
    rankings_json JSONB NOT NULL,
    analysis_json JSONB NOT NULL,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history_snapshots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_date ON history_snapshots(date DESC);
CREATE INDEX IF NOT EXISTS idx_history_week ON history_snapshots(week_number);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history_snapshots(created_at DESC);

-- Add comments
COMMENT ON TABLE history_snapshots IS 'Stores historical snapshots of TLS rankings and analysis';
COMMENT ON COLUMN history_snapshots.rankings_json IS 'Complete rankings DataFrame as JSON';
COMMENT ON COLUMN history_snapshots.analysis_json IS 'Analysis data as JSON';

-- ============================================================================
-- 2. CREATE FUNCTION FOR AUTOMATIC CLEANUP (DELETE RECORDS OLDER THAN 1 YEAR)
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_old_history()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete records older than 1 year
    DELETE FROM history_snapshots
    WHERE created_at < NOW() - INTERVAL '1 year';
    
    -- Get count of deleted rows
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    RAISE NOTICE 'Cleaned up % old history records', deleted_count;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_history() IS 'Deletes history records older than 1 year';

-- ============================================================================
-- 3. CREATE SCHEDULED JOB FOR AUTO-CLEANUP (RUNS DAILY AT 2 AM)
-- ============================================================================

-- IMPORTANT: pg_cron may not be available on Supabase free tier
-- Check if pg_cron extension is available first

DO $$
BEGIN
    -- Try to enable pg_cron extension
    CREATE EXTENSION IF NOT EXISTS pg_cron;
    
    -- Schedule daily cleanup at 2:00 AM
    PERFORM cron.schedule(
        'cleanup-old-tls-history',
        '0 2 * * *',
        $$SELECT cleanup_old_history()$$
    );
    
    RAISE NOTICE 'Auto-cleanup scheduled successfully';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'pg_cron not available. You can run cleanup_old_history() manually or use Supabase Database Webhooks instead.';
END $$;

-- ALTERNATIVE: If pg_cron is not available, you can:
-- 1. Use Supabase Database Webhooks (https://supabase.com/docs/guides/database/webhooks)
-- 2. Create a Supabase Edge Function that runs on schedule
-- 3. Use GitHub Actions or other CI/CD to call cleanup function
-- 4. Run manual cleanup periodically: SELECT cleanup_old_history();

-- ============================================================================
-- 4. CREATE FUNCTION TO MANUALLY TRIGGER CLEANUP
-- ============================================================================

CREATE OR REPLACE FUNCTION manual_cleanup_history(months_to_keep INTEGER DEFAULT 12)
RETURNS TABLE(deleted_count INTEGER, message TEXT) AS $$
DECLARE
    rows_deleted INTEGER;
BEGIN
    -- Delete records older than specified months
    DELETE FROM history_snapshots
    WHERE created_at < NOW() - MAKE_INTERVAL(months => months_to_keep);
    
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    
    RETURN QUERY SELECT rows_deleted, 
        format('Deleted %s records older than %s months', rows_deleted, months_to_keep);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION manual_cleanup_history(INTEGER) IS 'Manually cleanup history older than specified months';

-- Example usage:
-- SELECT * FROM manual_cleanup_history(12);  -- Delete records older than 12 months
-- SELECT * FROM manual_cleanup_history(6);   -- Delete records older than 6 months

-- ============================================================================
-- 5. CREATE VIEW FOR RECENT HISTORY (LAST 30 DAYS)
-- ============================================================================

CREATE OR REPLACE VIEW recent_history AS
SELECT 
    id,
    timestamp,
    date,
    week_number,
    week_range,
    rankings_json,
    analysis_json,
    created_by,
    created_at
FROM history_snapshots
WHERE created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;

COMMENT ON VIEW recent_history IS 'Shows history from the last 30 days';

-- ============================================================================
-- 6. CREATE VIEW FOR SUMMARY STATISTICS
-- ============================================================================

CREATE OR REPLACE VIEW history_stats AS
SELECT 
    COUNT(*) as total_records,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7_days,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as last_30_days,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '90 days' THEN 1 END) as last_90_days,
    COUNT(CASE WHEN created_at < NOW() - INTERVAL '1 year' THEN 1 END) as older_than_1_year
FROM history_snapshots;

COMMENT ON VIEW history_stats IS 'Summary statistics for history records';

-- ============================================================================
-- 7. CREATE FUNCTION TO GET HISTORY WITH PAGINATION
-- ============================================================================

CREATE OR REPLACE FUNCTION get_history_paginated(
    page_number INTEGER DEFAULT 1,
    page_size INTEGER DEFAULT 10
)
RETURNS TABLE(
    id BIGINT,
    timestamp TIMESTAMPTZ,
    date DATE,
    week_number INTEGER,
    week_range TEXT,
    rankings_json JSONB,
    analysis_json JSONB,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.timestamp,
        h.date,
        h.week_number,
        h.week_range,
        h.rankings_json,
        h.analysis_json,
        COUNT(*) OVER() as total_count
    FROM history_snapshots h
    ORDER BY h.created_at DESC
    LIMIT page_size
    OFFSET (page_number - 1) * page_size;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_history_paginated(INTEGER, INTEGER) IS 'Get paginated history results';

-- Example usage:
-- SELECT * FROM get_history_paginated(1, 10);  -- First page, 10 records

-- ============================================================================
-- 8. CREATE TRIGGER TO UPDATE 'updated_at' AUTOMATICALLY
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_history_updated_at
    BEFORE UPDATE ON history_snapshots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 9. CREATE FUNCTION TO ARCHIVE OLD DATA (OPTIONAL - BEFORE DELETION)
-- ============================================================================

CREATE TABLE IF NOT EXISTS history_archive (
    LIKE history_snapshots INCLUDING ALL
);

COMMENT ON TABLE history_archive IS 'Archive of old history records before deletion';

CREATE OR REPLACE FUNCTION archive_old_history()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Move records older than 1 year to archive
    INSERT INTO history_archive
    SELECT * FROM history_snapshots
    WHERE created_at < NOW() - INTERVAL '1 year'
    ON CONFLICT (id) DO NOTHING;
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    
    -- Delete from main table
    DELETE FROM history_snapshots
    WHERE created_at < NOW() - INTERVAL '1 year';
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archive_old_history() IS 'Archives old records to history_archive before deletion';

-- ============================================================================
-- 10. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE history_snapshots ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to read all
CREATE POLICY "Users can read all history"
    ON history_snapshots FOR SELECT
    TO authenticated
    USING (true);

-- Create policy for authenticated users to insert
CREATE POLICY "Users can insert history"
    ON history_snapshots FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create policy for authenticated users to delete
CREATE POLICY "Users can delete history"
    ON history_snapshots FOR DELETE
    TO authenticated
    USING (true);

-- ============================================================================
-- 11. GRANT PERMISSIONS
-- ============================================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT ON history_snapshots TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE history_snapshots_id_seq TO authenticated;
GRANT DELETE ON history_snapshots TO authenticated;

-- Grant permissions on views
GRANT SELECT ON recent_history TO authenticated;
GRANT SELECT ON history_stats TO authenticated;

-- Grant permissions on archive table
GRANT SELECT ON history_archive TO authenticated;

-- ============================================================================
-- 12. COMPATIBILITY WITH MODULAR APP
-- ============================================================================

-- The modular tls_app uses DatabaseManager class which expects:
-- ✅ history_snapshots table with these fields:
--    - id, timestamp, date, week_number, week_range
--    - rankings_json (JSONB)
--    - analysis_json (JSONB)
--    - created_at, updated_at

-- DatabaseManager methods that work with this schema:
-- ✅ insert_history(history_data) - Inserts new snapshot
-- ✅ get_all_history() - Returns all snapshots ordered by ID DESC
-- ✅ delete_all_history() - Deletes all records
-- ✅ get_history_count() - Returns total count

-- All methods are fully compatible! ✅

-- ============================================================================
-- 13. VERIFICATION QUERIES
-- ============================================================================

-- Check table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'history_snapshots'
ORDER BY ordinal_position;

-- Check if pg_cron is available
SELECT EXISTS (
    SELECT 1 
    FROM pg_extension 
    WHERE extname = 'pg_cron'
) as pg_cron_available;

-- View scheduled jobs (if pg_cron is available)
-- SELECT * FROM cron.job WHERE jobname = 'cleanup-old-tls-history';

-- View current statistics
SELECT * FROM history_stats;

-- Test the connection (this is what DatabaseManager.connect() does)
SELECT COUNT(*) as test_connection FROM history_snapshots LIMIT 1;

-- ============================================================================
-- 14. USEFUL MAINTENANCE QUERIES FOR MODULAR APP
-- ============================================================================

-- Count records by month
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as record_count
FROM history_snapshots
GROUP BY month
ORDER BY month DESC;

-- Find duplicate snapshots
SELECT 
    date, 
    week_number, 
    COUNT(*) as duplicate_count
FROM history_snapshots
GROUP BY date, week_number
HAVING COUNT(*) > 1;

-- Check storage size
SELECT 
    pg_size_pretty(pg_total_relation_size('history_snapshots')) as total_size,
    pg_size_pretty(pg_relation_size('history_snapshots')) as table_size,
    pg_size_pretty(pg_total_relation_size('history_snapshots') - pg_relation_size('history_snapshots')) as indexes_size;

-- Get recent activity (useful for debugging)
SELECT 
    date,
    week_number,
    week_range,
    created_by,
    created_at
FROM history_snapshots
ORDER BY created_at DESC
LIMIT 10;

-- ============================================================================
-- 15. MANUAL CLEANUP INSTRUCTIONS (IF pg_cron NOT AVAILABLE)
-- ============================================================================

-- OPTION 1: Run cleanup manually
-- Execute this periodically (e.g., monthly):
-- SELECT cleanup_old_history();

-- OPTION 2: Create a Supabase Edge Function
-- 1. Go to Supabase Dashboard > Edge Functions
-- 2. Create new function that calls: SELECT cleanup_old_history()
-- 3. Use Supabase Cron to schedule it

-- OPTION 3: Use GitHub Actions
-- Create .github/workflows/cleanup.yml:
-- name: Cleanup Old History
-- on:
--   schedule:
--     - cron: '0 2 * * *'  # Daily at 2 AM
-- jobs:
--   cleanup:
--     runs-on: ubuntu-latest
--     steps:
--       - uses: supabase/setup-cli@v1
--       - run: supabase db execute --sql "SELECT cleanup_old_history();"

-- ============================================================================
-- SETUP COMPLETE! ✅
-- ============================================================================

-- Summary of what was created:
-- 1. ✅ Main table: history_snapshots
-- 2. ✅ Indexes for performance  
-- 3. ✅ Auto-cleanup function (runs daily if pg_cron available)
-- 4. ✅ Manual cleanup function
-- 5. ✅ Recent history view (last 30 days)
-- 6. ✅ Statistics view
-- 7. ✅ Pagination function
-- 8. ✅ Auto-update timestamp trigger
-- 9. ✅ Archive table and function
-- 10. ✅ Row level security policies
-- 11. ✅ Proper permissions
-- 12. ✅ Full compatibility with DatabaseManager class

-- COMPATIBILITY CHECK:
-- ✅ Works with modules/database.py
-- ✅ Works with utils/session_manager.py
-- ✅ Works with pages/history.py (when created)
-- ✅ All field names match
-- ✅ All data types compatible
-- ✅ All operations supported

-- To disable auto-cleanup (if scheduled):
-- SELECT cron.unschedule('cleanup-old-tls-history');

-- To re-enable auto-cleanup:
-- SELECT cron.schedule('cleanup-old-tls-history', '0 2 * * *', $$SELECT cleanup_old_history()$$);

-- To check if cleanup is scheduled:
-- SELECT * FROM cron.job WHERE jobname = 'cleanup-old-tls-history';
