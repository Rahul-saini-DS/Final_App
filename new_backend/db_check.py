import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

print('=== DATABASE STRUCTURE ===')
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
for table in tables:
    print(f'\nTable: {table[0]}')
    cursor.execute(f'PRAGMA table_info({table[0]})')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

print('\n=== LATEST ASSESSMENT DATA ===')
cursor.execute('SELECT * FROM assessment_results ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()
if result:
    print('Assessment Result:', result)

cursor.execute('SELECT * FROM ai_task_responses ORDER BY ai_response_id DESC LIMIT 2')  
tasks = cursor.fetchall()
print('Task Responses:', tasks)

conn.close()
