import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get the scores for result_id 48
cursor.execute('SELECT intelligence_score, physical_score, linguistic_score FROM assessment_results WHERE id = 48')
result = cursor.fetchone()
print('Scores for result_id 48:', result)

# Get task details for result_id 48
cursor.execute('SELECT task_type, success_count, was_completed FROM ai_task_responses WHERE result_id = 48')
tasks = cursor.fetchall()
print('\nTask details for result_id 48:')
for task in tasks:
    print(f'{task[0]}: count={task[1]}, completed={task[2]}')

conn.close()
