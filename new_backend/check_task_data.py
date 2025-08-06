import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get latest assessment
cursor.execute('SELECT id FROM assessment_results ORDER BY id DESC LIMIT 1')
result_id = cursor.fetchone()[0]

print('=== AI TASK DATA ===')
cursor.execute('SELECT task_type, success_count, was_completed, was_skipped FROM ai_task_responses WHERE result_id = ?', (result_id,))
tasks = cursor.fetchall()

for task in tasks:
    task_type, success_count, was_completed, was_skipped = task
    print(f'{task_type}:')
    print(f'  success_count: {success_count}')
    print(f'  was_completed: {was_completed}')
    print(f'  was_skipped: {was_skipped}')
    
    # Test the UPDATED backend logic with proper thresholds
    if task_type == 'physical_assessment':
        backend_score = 1 if (was_completed == 'true' and success_count >= 5) else 0
    elif task_type == 'linguistic_assessment':
        backend_score = 1 if (was_completed == 'true' and success_count >= 1) else 0
    else:
        backend_score = 1 if (was_completed == 'true' and success_count > 0) else 0
    
    print(f'  updated_backend_score: {backend_score}')
    print()

conn.close()
