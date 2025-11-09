# Quick PostgreSQL Setup Instructions for Katalyst

## ✅ Good News!
Your Django configuration is now correct and the .env file is properly set up with:
- DB_NAME: katalyst_db
- DB_USER: katalyst_user
- DB_PASSWORD: ROHINI
- DB_HOST: localhost
- DB_PORT: 5432

## 🚀 Next Step: Create PostgreSQL Database

You need to create the database and user in PostgreSQL. Choose ONE of the methods below:

---

## Method 1: Using Command Line (psql)

1. Open **Command Prompt** or **PowerShell** as Administrator

2. Connect to PostgreSQL:
   ```
   psql -U postgres
   ```

3. Enter your PostgreSQL superuser password (the one you set during PostgreSQL installation)

4. Run these commands one by one:
   ```sql
   CREATE DATABASE katalyst_db;
   CREATE USER katalyst_user WITH PASSWORD 'ROHINI';
   GRANT ALL PRIVILEGES ON DATABASE katalyst_db TO katalyst_user;
   \c katalyst_db
   GRANT ALL ON SCHEMA public TO katalyst_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO katalyst_user;
   \q
   ```

---

## Method 2: Using pgAdmin (GUI - Easier!)

### Step 1: Create Database
1. Open **pgAdmin**
2. Connect to your PostgreSQL server (localhost)
3. Right-click on **"Databases"** → **Create** → **Database**
4. Fill in:
   - Database: `katalyst_db`
   - Owner: postgres (for now)
5. Click **Save**

### Step 2: Create User
1. Right-click on **"Login/Group Roles"** → **Create** → **Login/Group Role**
2. In **General** tab:
   - Name: `katalyst_user`
3. In **Definition** tab:
   - Password: `ROHINI`
4. In **Privileges** tab:
   - Enable: "Can login?" checkbox
5. Click **Save**

### Step 3: Grant Privileges
1. Right-click on **katalyst_db** → **Properties**
2. Go to **Security** tab
3. Click the **+** button
4. Select **katalyst_user**
5. Grant all privileges:
   - ✅ Connect
   - ✅ Create
   - ✅ Temporary
   - ✅ All
6. Click **Save**

---

## After Database Setup

Once you've created the database and user, run:

```bash
cd C:\Users\DELL\hackcbs\LazySheeps\backend
python manage.py migrate
```

This will create all the necessary tables in your PostgreSQL database.

---

## Troubleshooting

### "psql: command not found"
PostgreSQL bin folder is not in your PATH. 

**Solution:**
- Find PostgreSQL installation (usually `C:\Program Files\PostgreSQL\14\bin\`)
- Add to PATH, or use full path:
  ```
  "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres
  ```

### "password authentication failed"
Wrong password for postgres user.

**Solution:**
- Reset password using pg_hba.conf (advanced)
- Or reinstall PostgreSQL and remember the password

### PostgreSQL not installed?
Download and install from: https://www.postgresql.org/download/windows/

During installation:
- Remember the password you set for 'postgres' user
- Default port: 5432 (keep this)
- Install pgAdmin (GUI tool)

---

## Quick Test

After migration, test the connection:

```bash
python manage.py dbshell
```

This should open PostgreSQL command line. Type `\dt` to see tables, `\q` to quit.

---

## 🎉 You're Almost There!

Once the database is created and migrations run successfully, your Katalyst project will be running on PostgreSQL!
