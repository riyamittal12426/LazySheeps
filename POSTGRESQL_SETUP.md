# PostgreSQL Setup Guide for Katalyst

This guide will help you migrate from SQLite to PostgreSQL for the Katalyst project.

## 📋 Prerequisites

- PostgreSQL 14.x or higher installed
- pgAdmin (optional, for GUI management)
- Python environment with psycopg2-binary installed

## 🚀 Quick Setup

### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run the installer
- Remember the password you set for the `postgres` user
- Default port: 5432

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database and User

Open PostgreSQL command line (psql) or pgAdmin and run:

```sql
-- Create database
CREATE DATABASE katalyst_db;

-- Create user with password
CREATE USER katalyst_user WITH PASSWORD 'your_secure_password';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE katalyst_db TO katalyst_user;

-- Connect to the database
\c katalyst_db

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO katalyst_user;
```

### Step 3: Configure Environment Variables

Create/update `.env` file in `backend/` directory:

```env
# PostgreSQL Database Configuration
DB_NAME=katalyst_db
DB_USER=katalyst_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 4: Install PostgreSQL Adapter

```bash
cd backend
pip install psycopg2-binary
```

### Step 5: Run Migrations

```bash
# Make sure you're in the backend directory with virtual environment activated
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Start Django Server

```bash
python manage.py runserver
```

## 🔄 Migrating Data from SQLite (Optional)

If you have existing data in SQLite that you want to migrate:

### Option 1: Using Django dumpdata/loaddata

```bash
# 1. Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > data_backup.json

# 2. Update settings.py to use PostgreSQL

# 3. Run migrations on PostgreSQL
python manage.py migrate

# 4. Load data into PostgreSQL
python manage.py loaddata data_backup.json
```

### Option 2: Using pgloader (Advanced)

Install pgloader and run:

```bash
pgloader db.sqlite3 postgresql://katalyst_user:your_password@localhost/katalyst_db
```

## 🔍 Verify Installation

### Check Database Connection

Create a test script `test_db.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    row = cursor.fetchone()
    print("PostgreSQL version:", row[0])
```

Run it:
```bash
python test_db.py
```

### Check Tables

```bash
python manage.py dbshell
```

In PostgreSQL shell:
```sql
\dt  -- List all tables
\d api_repository  -- Describe repository table
```

## 🛠️ Common Issues & Solutions

### Issue 1: "Error loading psycopg2 module"

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue 2: "FATAL: password authentication failed"

**Solution:**
- Check your password in `.env` file
- Verify user exists: `\du` in psql
- Reset password:
  ```sql
  ALTER USER katalyst_user WITH PASSWORD 'new_password';
  ```

### Issue 3: "FATAL: database does not exist"

**Solution:**
```sql
CREATE DATABASE katalyst_db;
```

### Issue 4: "permission denied for schema public"

**Solution:**
```sql
\c katalyst_db
GRANT ALL ON SCHEMA public TO katalyst_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO katalyst_user;
```

### Issue 5: Port 5432 already in use

**Solution:**
- Find process using port: `netstat -ano | findstr :5432` (Windows)
- Kill process or change PostgreSQL port in both PostgreSQL config and `.env`

## 📊 Performance Optimization

### Add Indexes (Optional, for production)

```sql
-- Connect to database
\c katalyst_db

-- Add indexes for frequently queried fields
CREATE INDEX idx_commit_sha ON api_commit(sha);
CREATE INDEX idx_commit_contributor ON api_commit(contributor_id, committed_at DESC);
CREATE INDEX idx_repository_org ON api_repository(organization_id);
CREATE INDEX idx_activity_contributor ON api_activitylog(contributor_id, timestamp DESC);
```

### Configure PostgreSQL for Development

Edit `postgresql.conf`:

```conf
# Memory settings (adjust based on your system)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# Connection settings
max_connections = 100

# Logging (helpful for debugging)
log_statement = 'all'
log_duration = on
```

## 🔐 Security Best Practices

1. **Strong Password**: Use a strong, unique password for `katalyst_user`
2. **Limited Privileges**: Don't use `postgres` superuser in production
3. **Network Access**: Configure `pg_hba.conf` to limit connections
4. **SSL/TLS**: Enable SSL for production deployments
5. **Regular Backups**: Set up automated backups

### Example Backup Command

```bash
# Backup
pg_dump -U katalyst_user -h localhost katalyst_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U katalyst_user -h localhost katalyst_db < backup_20251109.sql
```

## 🎯 Production Deployment

### Using Docker

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: katalyst_db
      POSTGRES_USER: katalyst_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

### Using Managed PostgreSQL (Cloud)

**AWS RDS:**
1. Create RDS PostgreSQL instance
2. Update `.env` with RDS endpoint
3. Add RDS security group to allow your IP

**Heroku:**
```bash
heroku addons:create heroku-postgresql:hobby-dev
heroku config:get DATABASE_URL
```

**DigitalOcean:**
1. Create managed PostgreSQL database
2. Get connection string
3. Update `.env` with connection details

## 📚 Additional Resources

- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [Django PostgreSQL Guide](https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [pgAdmin](https://www.pgadmin.org/)

## ✅ Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `katalyst_db` created
- [ ] User `katalyst_user` created with proper permissions
- [ ] `.env` file configured with correct credentials
- [ ] `psycopg2-binary` installed in virtual environment
- [ ] Migrations run successfully
- [ ] Superuser created (optional)
- [ ] Django server starts without errors
- [ ] Can create/read data through Django admin or API

---

**Migration Complete!** 🎉

Your Katalyst project is now running on PostgreSQL for better performance, scalability, and production readiness.
