import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

print('=== LATEST ASSESSMENT ===')
cursor.execute('SELECT * FROM assessment_results ORDER BY timestamp DESC LIMIT 1')
latest = cursor.fetchone()
if latest:
    print(f'ID: {latest[0]}, Child: {latest[1]}, Age: {latest[2]}')
    print(f'Intelligence: {latest[3]}, Physical: {latest[4]}, Linguistic: {latest[5]}, Total: {latest[6]}')
    print(f'Timestamp: {latest[7]}')
    
    # Check task details
    print('\n=== TASK DETAILS ===')
    cursor.execute('SELECT * FROM ai_task_responses WHERE result_id = ?', (latest[0],))
    tasks = cursor.fetchall()
    for task in tasks:
        print(f'Task: {task[2]}, Success Count: {task[6]}, Completed: {task[8]}')

conn.close()
