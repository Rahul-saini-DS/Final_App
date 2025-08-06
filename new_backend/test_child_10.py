import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Test what the backend returns for child_id = 10
child_id = 10

cursor.execute('SELECT ar.id, ar.intelligence_score, ar.physical_score, ar.linguistic_score FROM assessment_results ar WHERE ar.child_id = ? ORDER BY ar.completed_at DESC LIMIT 1', (child_id,))
result = cursor.fetchone()

if result:
    result_id, intelligence, physical, linguistic = result
    print(f'Database scores: Intelligence={intelligence}, Physical={physical}, Linguistic={linguistic}')
    
    # Get task details
    cursor.execute('SELECT task_type, success_count, was_completed FROM ai_task_responses WHERE result_id = ?', (result_id,))
    tasks = cursor.fetchall()
    
    for task_type, success_count, was_completed in tasks:
        backend_score = 1 if (was_completed == 'true' and success_count > 0) else 0
        print(f'{task_type}: backend_calculated={backend_score}, was_completed={was_completed}, success_count={success_count}')
else:
    print('No results found for child_id = 10')

conn.close()
