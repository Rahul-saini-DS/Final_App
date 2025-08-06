import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Test updated logic for child_id = 10
child_id = 10

cursor.execute('SELECT ar.id FROM assessment_results ar WHERE ar.child_id = ? ORDER BY ar.completed_at DESC LIMIT 1', (child_id,))
result = cursor.fetchone()

if result:
    result_id = result[0]
    
    cursor.execute('SELECT task_type, success_count, was_completed FROM ai_task_responses WHERE result_id = ?', (result_id,))
    tasks = cursor.fetchall()
    
    print('=== UPDATED BACKEND LOGIC ===')
    for task_type, success_count, was_completed in tasks:
        if task_type == 'physical_assessment':
            task_success = 1 if (was_completed == 'true' and success_count >= 5) else 0
            print(f'Physical: success_count={success_count}, completed={was_completed} -> score={task_success}')
        elif task_type == 'linguistic_assessment':  
            task_success = 1 if (was_completed == 'true' and success_count >= 1) else 0
            print(f'Linguistic: success_count={success_count}, completed={was_completed} -> score={task_success}')

conn.close()
