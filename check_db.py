import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

cursor = connection.cursor()
cursor.execute("SELECT app, name FROM django_migrations WHERE app='stor'")
print("Migrations in DB:", cursor.fetchall())

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'stor_%'")
print("Tables in DB:", cursor.fetchall())
