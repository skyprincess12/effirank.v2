# Deployment Guide

Complete guide for deploying the TLS Cost Input & Ranking System v2.1.0

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Streamlit Cloud Deployment](#streamlit-cloud)
3. [Docker Deployment](#docker-deployment)
4. [AWS EC2 Deployment](#aws-ec2)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Development

### Prerequisites
```bash
python --version  # Should be 3.8+
pip --version
```

### Setup
```bash
# 1. Navigate to project directory
cd effirank_v2_fixed

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create secrets file
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# 6. Edit secrets file with your credentials
nano .streamlit/secrets.toml  # or use your preferred editor

# 7. Run the application
streamlit run app.py
```

### Development Mode Features
- Auto-reload on file changes
- Debug mode enabled
- Local storage (no cloud required)
- Detailed error messages

---

## ☁️ Streamlit Cloud

### Step 1: Prepare Repository

1. Create GitHub repository
2. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - TLS System v2.1.0"
git remote add origin https://github.com/yourusername/tls-system.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set main file: `app.py`
5. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud dashboard:
1. Go to app settings
2. Click "Secrets"
3. Paste contents of your `secrets.toml`
4. Save

### Step 4: Configure Advanced Settings

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### Important Notes

- Free tier: 1 GB RAM, shared CPU
- App will sleep after inactivity
- Public URLs (use authentication!)
- Maximum file upload: 200 MB

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  tls-system:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    volumes:
      - ./data:/app/data
      - ./.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t tls-system:2.1.0 .

# Run container
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro \
  --name tls-system \
  tls-system:2.1.0

# Or use docker-compose
docker-compose up -d
```

### Docker Tips

- Use volumes for data persistence
- Mount secrets as read-only
- Configure proper logging
- Set resource limits
- Use health checks

---

## ☁️ AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. **Instance Type**: t3.small (2 vCPU, 2 GB RAM minimum)
2. **OS**: Ubuntu 22.04 LTS
3. **Storage**: 20 GB SSD
4. **Security Group**:
   - SSH (22) from your IP
   - HTTP (80) from anywhere
   - HTTPS (443) from anywhere
   - Custom (8501) from anywhere (Streamlit)

### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install nginx (reverse proxy)
sudo apt install nginx -y

# Clone repository
git clone https://github.com/yourusername/tls-system.git
cd tls-system
```

### Step 3: Application Setup

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup secrets
mkdir -p .streamlit
nano .streamlit/secrets.toml  # Add your secrets
```

### Step 4: Systemd Service

Create `/etc/systemd/system/tls-system.service`:

```ini
[Unit]
Description=TLS Cost Input & Ranking System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/tls-system
Environment="PATH=/home/ubuntu/tls-system/venv/bin"
ExecStart=/home/ubuntu/tls-system/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable tls-system
sudo systemctl start tls-system
sudo systemctl status tls-system
```

### Step 5: Nginx Reverse Proxy

Create `/etc/nginx/sites-available/tls-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/tls-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🔐 Environment Variables

### Required Variables

```bash
# In .streamlit/secrets.toml or environment

# Users (at least one admin required)
USERS__ADMIN__PASSWORD="secure_password"
USERS__ADMIN__ROLE="admin"

# System
HISTORY_DELETE_PASSCODE="secure_delete_passcode"
```

### Optional Variables

```bash
# Database
SUPABASE_URL="https://yourproject.supabase.co"
SUPABASE_KEY="your-anon-key"

# Weather API
OPENWEATHER__API_KEY="your-api-key"
```

### Security Best Practices

1. **Never commit secrets to Git**
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

2. **Use strong passwords**
   ```bash
   # Generate secure password
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Rotate credentials regularly**
4. **Use environment-specific secrets**
5. **Encrypt secrets at rest**

---

## 💾 Database Setup

### Supabase Setup

1. **Create Account**
   - Go to [supabase.com](https://supabase.com)
   - Create new project

2. **Create Table**

```sql
CREATE TABLE history_snapshots (
    id BIGSERIAL PRIMARY KEY,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    week_range TEXT NOT NULL,
    rankings_json JSONB NOT NULL,
    analysis_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_history_date ON history_snapshots(date);
CREATE INDEX idx_history_week ON history_snapshots(week_number);
```

3. **Get Credentials**
   - Project URL: Settings → API → Project URL
   - Anon Key: Settings → API → Project API keys → anon/public

4. **Configure Row Level Security (RLS)**

```sql
-- Enable RLS
ALTER TABLE history_snapshots ENABLE ROW LEVEL SECURITY;

-- Allow read for all
CREATE POLICY "Allow public read"
ON history_snapshots FOR SELECT
USING (true);

-- Allow insert for all
CREATE POLICY "Allow public insert"
ON history_snapshots FOR INSERT
WITH CHECK (true);

-- Allow delete for all
CREATE POLICY "Allow public delete"
ON history_snapshots FOR DELETE
USING (true);
```

### Local PostgreSQL Setup (Alternative)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb tls_system

# Create user
sudo -u postgres createuser tls_user

# Set password
sudo -u postgres psql -c "ALTER USER tls_user WITH PASSWORD 'your_password';"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tls_system TO tls_user;"
```

---

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check secrets file
cat .streamlit/secrets.toml

# Check logs
tail -f ~/.tls_app_data/app.log
```

### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501
# or
netstat -ano | findstr :8501  # Windows

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Test connection
python -c "
from supabase import create_client
url = 'YOUR_URL'
key = 'YOUR_KEY'
client = create_client(url, key)
result = client.table('history_snapshots').select('count').limit(1).execute()
print('Connection successful:', result)
"
```

### Memory Issues

```bash
# Check memory usage
free -h

# Increase swap (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Permission Issues

```bash
# Fix data directory permissions
chmod 755 ~/.tls_app_data
chmod 644 ~/.tls_app_data/*

# Fix app directory permissions
chmod -R 755 /path/to/app
```

---

## 📊 Monitoring

### Application Logs

```bash
# View logs
tail -f ~/.tls_app_data/app.log

# Search for errors
grep ERROR ~/.tls_app_data/app.log

# Monitor in real-time
watch -n 1 "tail -20 ~/.tls_app_data/app.log"
```

### System Resources

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network
netstat -tuln
```

### Streamlit Metrics

Access built-in metrics at: `http://your-app-url/_stcore/health`

---

## 🚀 Performance Optimization

### 1. Enable Caching
Already implemented in v2.1.0!

### 2. Use CDN for Static Assets
```python
# In config.py
ENABLE_CDN = True
CDN_URL = "https://cdn.yoursite.com"
```

### 3. Database Query Optimization
- Use indexes
- Limit result sets
- Cache frequently accessed data

### 4. Load Balancing
Use nginx or AWS ELB for multiple instances

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review troubleshooting section
3. Check GitHub issues
4. Contact support team

---

**Deployment Checklist:**

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Secrets configured
- [ ] Database setup (optional)
- [ ] Weather API configured (optional)
- [ ] Application starts successfully
- [ ] All pages load without errors
- [ ] Authentication working
- [ ] Data persistence working
- [ ] SSL configured (production)
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Documentation reviewed

**Status**: Ready for Production ✅
