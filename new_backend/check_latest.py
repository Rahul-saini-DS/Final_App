import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

print('=== LATEST ASSESSMENT ===')
cursor.execute('SELECT * FROM assessment_results ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()
if result:
    print(f'Database scores: Intelligence={result[3]}, Physical={result[4]}, Linguistic={result[5]}, Total={result[6]}')
    
    print('\n=== TASK DETAILS ===')
    cursor.execute('SELECT task_type, success_count, was_completed, was_skipped FROM ai_task_responses WHERE result_id = ?', (result[0],))
    tasks = cursor.fetchall()
    for task in tasks:
        print(f'{task[0]}: success_count={task[1]}, completed={task[2]}, skipped={task[3]}')

conn.close()
