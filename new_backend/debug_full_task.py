import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get column names first
cursor.execute('PRAGMA table_info(ai_task_responses)')
columns = cursor.fetchall()
print("Table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n" + "="*50)

# Get all data for result_id 48
cursor.execute('SELECT * FROM ai_task_responses WHERE result_id = 48')
tasks = cursor.fetchall()

print(f'Found {len(tasks)} task responses for result_id 48:')
for i, task in enumerate(tasks):
    print(f'\nTask {i+1}:')
    for j, col in enumerate(columns):
        col_name = col[1]
        value = task[j]
        print(f'  {col_name}: {value}')

conn.close()
