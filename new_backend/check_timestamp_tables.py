import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Database tables with timestamp columns:')
for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    
    timestamp_cols = [col[1] for col in columns if 'TIMESTAMP' in col[2] or 'created_at' in col[1] or 'completed_at' in col[1]]
    if timestamp_cols:
        print(f'  {table_name}: {timestamp_cols}')

conn.close()
