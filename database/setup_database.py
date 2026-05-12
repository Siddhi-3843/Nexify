# ============================================================
# Nexify - Database Setup
# This file loads our CSV data into a SQLite database
# ============================================================

import sqlite3        # built into Python — no install needed!
import pandas as pd   # for reading CSV files
import os             # for file path operations

# ============================================================
# 1. CONNECT TO DATABASE
# ============================================================

# This creates the database file if it doesn't exist yet
# Think of it like opening a filing cabinet — 
# if it doesn't exist, we create a new one
DB_PATH = 'database/nexify.db'

print("Connecting to database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
# cursor is like a pen — we use it to write to the database

print(f"✅ Database created at: {DB_PATH}")

# ============================================================
# 2. CREATE TABLES
# ============================================================
# Tables are like spreadsheet sheets inside the database
# Each table has columns with specific data types

print("\nCreating tables...")

# --- Members Table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        member_id     TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        email         TEXT NOT NULL,
        phone         TEXT,
        tier          TEXT NOT NULL,
        join_date     TEXT NOT NULL,
        churn_date    TEXT,
        age           INTEGER,
        city          TEXT,
        gender        TEXT
    )
''')
# TEXT = any text value
# INTEGER = whole number
# PRIMARY KEY = unique identifier for each row
# NOT NULL = this field must have a value
# IF NOT EXISTS = don't crash if table already exists

# --- Payments Table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id      TEXT PRIMARY KEY,
        member_id       TEXT NOT NULL,
        date            TEXT NOT NULL,
        amount          REAL NOT NULL,
        status          TEXT NOT NULL,
        payment_method  TEXT,
        FOREIGN KEY (member_id) REFERENCES members(member_id)
    )
''')
# REAL = decimal number
# FOREIGN KEY = links payments to members table
# This means every payment MUST belong to a real member

# --- Classes Table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS classes (
        class_id        TEXT PRIMARY KEY,
        class_name      TEXT NOT NULL,
        instructor      TEXT NOT NULL,
        capacity        INTEGER NOT NULL,
        duration_mins   INTEGER,
        day             TEXT,
        time            TEXT
    )
''')

# --- Bookings Table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id      TEXT PRIMARY KEY,
        member_id       TEXT NOT NULL,
        class_id        TEXT NOT NULL,
        booking_date    TEXT NOT NULL,
        status          TEXT NOT NULL,
        FOREIGN KEY (member_id) REFERENCES members(member_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
''')

print("✅ All tables created!")

# ============================================================
# 3. LOAD CSV DATA INTO TABLES
# ============================================================

print("\nLoading data into database...")

# --- Load Members ---
members_df = pd.read_csv('data/raw/members.csv')
members_df.to_sql(
    'members',      # table name
    conn,           # database connection
    if_exists='replace',  # replace if already exists
    index=False     # don't add extra index column
)
print(f"✅ Loaded {len(members_df)} members")

# --- Load Payments ---
payments_df = pd.read_csv('data/raw/payments.csv')
payments_df.to_sql(
    'payments',
    conn,
    if_exists='replace',
    index=False
)
print(f"✅ Loaded {len(payments_df)} payments")

# --- Load Classes ---
classes_df = pd.read_csv('data/raw/classes.csv')
classes_df.to_sql(
    'classes',
    conn,
    if_exists='replace',
    index=False
)
print(f"✅ Loaded {len(classes_df)} classes")

# --- Load Bookings ---
bookings_df = pd.read_csv('data/raw/bookings.csv')
bookings_df.to_sql(
    'bookings',
    conn,
    if_exists='replace',
    index=False
)
print(f"✅ Loaded {len(bookings_df)} bookings")

# ============================================================
# 4. VERIFY DATA WITH TEST QUERIES
# ============================================================

print("\nVerifying data with test queries...")

# Test Query 1 — Count members by tier
print("\n📊 Members by tier:")
result = cursor.execute('''
    SELECT tier, COUNT(*) as count
    FROM members
    GROUP BY tier
    ORDER BY count DESC
''').fetchall()
for row in result:
    print(f"   {row[0]}: {row[1]} members")

# Test Query 2 — Total revenue
print("\n💰 Total revenue:")
result = cursor.execute('''
    SELECT 
        SUM(amount) as total_revenue,
        COUNT(*) as total_payments,
        SUM(CASE WHEN status='failed' 
            THEN 1 ELSE 0 END) as failed_payments
    FROM payments
''').fetchone()
print(f"   Total Revenue:   ${result[0]:,.2f}")
print(f"   Total Payments:  {result[1]}")
print(f"   Failed Payments: {result[2]}")

# Test Query 3 — Most popular classes
print("\n🏋️ Most popular classes:")
result = cursor.execute('''
    SELECT c.class_name, COUNT(b.booking_id) as bookings
    FROM bookings b
    JOIN classes c ON b.class_id = c.class_id
    GROUP BY c.class_name
    ORDER BY bookings DESC
    LIMIT 3
''').fetchall()
for row in result:
    print(f"   {row[0]}: {row[1]} bookings")

# Test Query 4 — Active vs churned members
print("\n👥 Active vs Churned members:")
result = cursor.execute('''
    SELECT 
        SUM(CASE WHEN churn_date IS NULL 
            THEN 1 ELSE 0 END) as active,
        SUM(CASE WHEN churn_date IS NOT NULL 
            THEN 1 ELSE 0 END) as churned
    FROM members
''').fetchone()
print(f"   Active:  {result[0]} members")
print(f"   Churned: {result[1]} members")

# ============================================================
# 5. SAVE AND CLOSE
# ============================================================

conn.commit()   # save all changes
conn.close()    # close the connection

print("\n" + "="*50)
print("DATABASE SETUP COMPLETE!")
print("="*50)
print(f"\nDatabase saved to: {DB_PATH}")
print("You can now query this database from anywhere!")