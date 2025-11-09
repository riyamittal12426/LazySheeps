import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
tables = cursor.fetchall()

print('\n' + '='*60)
print('✅ PostgreSQL Migration Complete!')
print('='*60)
print(f'\nTotal tables created: {len(tables)}\n')
print('Tables:')
for table in tables:
    print(f'  • {table[0]}')

cursor.execute("SELECT version()")
version = cursor.fetchone()
print(f'\n📊 Database: {version[0].split(",")[0]}')

cursor.close()
connection.close()

print('\n' + '='*60)
print('🎉 Katalyst is now running on PostgreSQL!')
print('='*60)
print('\nNext steps:')
print('  1. python manage.py createsuperuser  (optional)')
print('  2. python manage.py runserver')
print('\n')
