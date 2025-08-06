#!/usr/bin/env python
"""Test timezone conversion for database timestamps"""
import sqlite3
from datetime import datetime
import pytz

# Check current database timestamps and convert to IST
conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()
cursor.execute('SELECT completed_at FROM assessment_results WHERE id = 48 OR id = 49 ORDER BY id DESC LIMIT 2')
results = cursor.fetchall()

print('Database timestamps conversion:')
utc = pytz.UTC
ist = pytz.timezone('Asia/Kolkata')

for i, result in enumerate(results):
    db_time_str = result[0]
    print(f'  {i+1}: Raw DB: {db_time_str}')
    
    # Parse the database timestamp (assuming it's UTC)
    dt_utc = datetime.strptime(db_time_str, '%Y-%m-%d %H:%M:%S')
    dt_utc = utc.localize(dt_utc)
    
    # Convert to IST
    dt_ist = dt_utc.astimezone(ist)
    print(f'      IST: {dt_ist.strftime("%b %d, %Y, %I:%M %p")}')

conn.close()
