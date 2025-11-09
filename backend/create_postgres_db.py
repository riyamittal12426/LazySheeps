"""
Script to create PostgreSQL database and user for Katalyst
Run this with: python create_postgres_db.py
"""

import psycopg2
from psycopg2 import sql
import sys

def create_database():
    print("=" * 60)
    print("Katalyst PostgreSQL Database Setup")
    print("=" * 60)
    
    # Ask for postgres superuser password
    print("\nPlease enter your PostgreSQL 'postgres' user password:")
    print("(This is the password you set when installing PostgreSQL)")
    postgres_password = input("Password: ")
    
    try:
        # Connect to PostgreSQL default database (postgres)
        print("\n[1/5] Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=postgres_password,
            host='localhost',
            port='5432'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("✓ Connected successfully!")
        
        # Check if database exists
        print("\n[2/5] Checking if katalyst_db already exists...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'katalyst_db'"
        )
        db_exists = cursor.fetchone()
        
        if db_exists:
            print("⚠ Database 'katalyst_db' already exists. Skipping creation.")
        else:
            # Create database
            print("[2/5] Creating database 'katalyst_db'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier('katalyst_db'))
            )
            print("✓ Database created successfully!")
        
        # Check if user exists
        print("\n[3/5] Checking if user 'katalyst_user' already exists...")
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = 'katalyst_user'"
        )
        user_exists = cursor.fetchone()
        
        if user_exists:
            print("⚠ User 'katalyst_user' already exists. Updating password...")
            cursor.execute(
                sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                    sql.Identifier('katalyst_user')
                ),
                ['ROHINI']
            )
            print("✓ Password updated!")
        else:
            # Create user
            print("[3/5] Creating user 'katalyst_user'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier('katalyst_user')
                ),
                ['ROHINI']
            )
            print("✓ User created successfully!")
        
        # Grant privileges
        print("\n[4/5] Granting privileges to katalyst_user...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier('katalyst_db'),
                sql.Identifier('katalyst_user')
            )
        )
        print("✓ Privileges granted!")
        
        cursor.close()
        conn.close()
        
        # Connect to katalyst_db to grant schema privileges
        print("\n[5/5] Setting up schema privileges...")
        conn2 = psycopg2.connect(
            dbname='katalyst_db',
            user='postgres',
            password=postgres_password,
            host='localhost',
            port='5432'
        )
        conn2.autocommit = True
        cursor2 = conn2.cursor()
        
        cursor2.execute("GRANT ALL ON SCHEMA public TO katalyst_user")
        cursor2.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO katalyst_user"
        )
        cursor2.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO katalyst_user"
        )
        print("✓ Schema privileges configured!")
        
        cursor2.close()
        conn2.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 60)
        print("\nDatabase Configuration:")
        print("  - Database: katalyst_db")
        print("  - User: katalyst_user")
        print("  - Password: ROHINI")
        print("  - Host: localhost")
        print("  - Port: 5432")
        print("\nNext steps:")
        print("  1. Run: python manage.py migrate")
        print("  2. Run: python manage.py runserver")
        print("\n🚀 You're ready to go!")
        
    except psycopg2.OperationalError as e:
        print("\n❌ ERROR: Could not connect to PostgreSQL")
        print(f"\nDetails: {e}")
        print("\nPossible issues:")
        print("  1. PostgreSQL is not running")
        print("  2. Wrong password for 'postgres' user")
        print("  3. PostgreSQL is not installed")
        print("\nSolutions:")
        print("  - Check if PostgreSQL service is running")
        print("  - Verify your postgres user password")
        print("  - Install PostgreSQL from: https://www.postgresql.org/download/")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
