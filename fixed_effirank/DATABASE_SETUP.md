# Database Setup Guide

Complete guide for setting up Supabase with the TLS System.

## ✅ Compatibility Status

**Your SQL schema (`supabase_schema_modular.sql`) is 100% compatible with the fixed application!**

### What Matches Perfectly

| Component | SQL Schema | App Expects | Status |
|-----------|-----------|-------------|--------|
| Table name | `history_snapshots` | `history_snapshots` | ✅ Perfect |
| ID column | `id BIGSERIAL` | `id` | ✅ Perfect |
| Timestamp | `timestamp TIMESTAMPTZ` | `timestamp` | ✅ Perfect |
| Date | `date DATE` | `date` | ✅ Perfect |
| Week number | `week_number INTEGER` | `week_number` | ✅ Perfect |
| Week range | `week_range TEXT` | `week_range` | ✅ Perfect |
| Rankings | `rankings_json JSONB` | `rankings_json` | ✅ Perfect |
| Analysis | `analysis_json JSONB` | `analysis_json` | ✅ Perfect |

### Database Operations Supported

| Operation | Method | SQL Feature | Works? |
|-----------|--------|-------------|--------|
| Insert snapshot | `insert_history()` | Table insert | ✅ Yes |
| Get all history | `get_all_history()` | Select all | ✅ Yes |
| Delete all | `delete_all_history()` | Delete query | ✅ Yes |
| Get count | `get_history_count()` | Count query | ✅ Yes |
| Test connection | `connect()` | Select query | ✅ Yes |

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign in / Create account
3. Click "New Project"
4. Fill in:
   - **Name**: TLS System
   - **Database Password**: (save this!)
   - **Region**: Choose closest to you
5. Wait ~2 minutes for setup

### Step 2: Run SQL Schema
1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire `supabase_schema_modular.sql` file
4. Paste into editor
5. Click **Run** (bottom right)
6. ✅ Should see "Success. No rows returned"

### Step 3: Get Credentials
1. Go to **Settings** → **API**
2. Copy these two values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Project API keys** → **anon/public** key

### Step 4: Configure App
Edit `.streamlit/secrets.toml`:

```toml
# Supabase Database
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

### Step 5: Test Connection
Run your app:
```bash
streamlit run app.py
```

Check sidebar - should show:
- 🟢 Database Connected

## 📊 Using Enhanced Features

Your SQL schema includes advanced features! To use them, you have two options:

### Option 1: Keep Current Setup (Recommended for Now)
Everything already works! The basic `database.py` uses:
- ✅ `insert_history()` - Works perfectly
- ✅ `get_all_history()` - Works perfectly  
- ✅ `delete_all_history()` - Works perfectly
- ✅ `get_history_count()` - Works perfectly

**No changes needed!**

### Option 2: Use Enhanced Features (Advanced)
Replace `modules/database.py` with `modules/database_enhanced.py` to get:

**New Methods Available:**
- `get_recent_history(days=30)` - Get last 30 days
- `get_history_stats()` - Statistics view
- `get_history_paginated(page, size)` - Paginated results
- `cleanup_old_history(months=12)` - Delete old records
- `archive_old_history()` - Archive before delete
- `get_history_by_date_range(start, end)` - Date range query
- `get_history_by_week(week_number)` - Week query

**To enable enhanced features:**
```bash
# Backup original
cp modules/database.py modules/database_original.py

# Use enhanced version
cp modules/database_enhanced.py modules/database.py
```

## 🔍 Verification

### Check Table Created
In Supabase dashboard → **Table Editor**, you should see:
- `history_snapshots` table
- `history_archive` table
- `recent_history` view
- `history_stats` view

### Check Functions Created
In Supabase dashboard → **Database** → **Functions**, you should see:
- `cleanup_old_history()`
- `manual_cleanup_history()`
- `archive_old_history()`
- `get_history_paginated()`

### Test in SQL Editor
```sql
-- Check table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'history_snapshots';

-- Check if empty (new install)
SELECT COUNT(*) FROM history_snapshots;

-- View statistics
SELECT * FROM history_stats;
```

## 🛠️ Features Your Schema Provides

### 1. Auto-Cleanup (If pg_cron Available)
Automatically deletes records older than 1 year every day at 2 AM.

**Check if enabled:**
```sql
SELECT * FROM cron.job WHERE jobname = 'cleanup-old-tls-history';
```

**Note**: `pg_cron` may not be available on Supabase free tier. If not available, use manual cleanup (see below).

### 2. Manual Cleanup
Run anytime to delete old records:

```sql
-- Delete records older than 12 months
SELECT * FROM manual_cleanup_history(12);

-- Delete records older than 6 months
SELECT * FROM manual_cleanup_history(6);
```

In your app (with enhanced database.py):
```python
db_manager.cleanup_old_history(months=12)
```

### 3. Archive Before Delete
Move old records to archive instead of deleting:

```sql
SELECT archive_old_history();
```

In your app:
```python
db_manager.archive_old_history()
```

### 4. Pagination
Get records in pages for better performance:

```sql
-- Get first page (10 records)
SELECT * FROM get_history_paginated(1, 10);

-- Get second page
SELECT * FROM get_history_paginated(2, 10);
```

In your app:
```python
records, total = db_manager.get_history_paginated(page=1, page_size=10)
```

### 5. Statistics
Quick overview of your data:

```sql
SELECT * FROM history_stats;
```

In your app:
```python
stats = db_manager.get_history_stats()
# stats = {
#   'total_records': 150,
#   'last_7_days': 7,
#   'last_30_days': 30,
#   'last_90_days': 90,
#   'older_than_1_year': 10
# }
```

### 6. Recent History View
Pre-filtered view of last 30 days:

```sql
SELECT * FROM recent_history;
```

In your app:
```python
recent = db_manager.get_recent_history(days=30)
```

## 🔐 Security Features

Your schema includes Row Level Security (RLS):

### Policies Created
- ✅ **Read**: Authenticated users can read all records
- ✅ **Insert**: Authenticated users can create records
- ✅ **Delete**: Authenticated users can delete records

### What This Means
- Users need valid API key to access data
- Public cannot access your database
- All operations are logged
- Secure by default

## 📈 Performance Features

### Indexes Created
Your schema creates indexes on:
- `timestamp` (for date queries)
- `date` (for date filtering)
- `week_number` (for week queries)
- `created_at` (for recent queries)

**Result**: Fast queries even with thousands of records!

### Auto-Update Timestamp
Every time a record is updated, `updated_at` automatically updates.

## 🐛 Troubleshooting

### "Table already exists" error
This is fine! It means you ran the schema before. The schema uses `CREATE TABLE IF NOT EXISTS` so it won't break.

### "pg_cron not available" message
**Expected on Supabase free tier.** The schema handles this gracefully. You can:
1. Use manual cleanup: `SELECT manual_cleanup_history(12);`
2. Use app cleanup: `db_manager.cleanup_old_history(12)`
3. Set up scheduled cleanup externally (see schema file comments)

### Connection fails in app
Check:
1. Correct URL in secrets.toml (should start with `https://`)
2. Correct API key (use **anon/public** key, not service_role)
3. Internet connection active
4. Supabase project is active (not paused)

### Can't see data in app
Check:
1. Database connected (🟢 in sidebar)
2. History snapshots created (insert some data)
3. RLS policies allow your API key

## 📝 Maintenance

### Weekly
- Check `history_stats` view for record count
- Monitor table size (see schema file for query)

### Monthly
- Run cleanup if auto-cleanup not available:
  ```sql
  SELECT manual_cleanup_history(12);
  ```
- Check for duplicate snapshots:
  ```sql
  SELECT date, week_number, COUNT(*) 
  FROM history_snapshots 
  GROUP BY date, week_number 
  HAVING COUNT(*) > 1;
  ```

### Quarterly
- Review archive table size
- Backup important historical data
- Rotate database credentials

## 🎯 Summary

**Your SQL schema is production-ready and fully compatible!**

✅ **What Works Out of the Box:**
- All basic operations (insert, select, delete, count)
- Row level security
- Performance indexes
- Auto-update timestamps
- Manual cleanup capability

✅ **What's Optional (Advanced):**
- Auto-cleanup with pg_cron
- Pagination functions
- Statistics views
- Archive functionality

✅ **What You Need to Do:**
1. Create Supabase project
2. Run SQL schema
3. Add credentials to secrets.toml
4. Start using the app!

**No code changes needed - everything is compatible!** 🎉

---

**Quick Reference:**

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

**Test connection:**
```bash
streamlit run app.py
# Check sidebar for 🟢 Database Connected
```

**You're ready to go!** 🚀
