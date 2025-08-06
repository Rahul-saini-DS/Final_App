import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get the raw data for result_id 48
cursor.execute('SELECT id, child_id, intelligence_score, physical_score, linguistic_score, created_at FROM assessment_results WHERE id = 48')
result = cursor.fetchone()
print(f"Result ID 48 data: {result}")

# Get task responses for result_id 48
cursor.execute('SELECT id, task_type, success_count, was_completed FROM ai_task_responses WHERE result_id = 48 ORDER BY task_type')
tasks = cursor.fetchall()
print(f"\nTask responses for result_id 48:")
for task in tasks:
    print(f"Task ID {task[0]}: {task[1]} - count={task[2]}, completed={task[3]}")

# Calculate what the scores SHOULD be based on our logic
physical_should_be = 0
linguistic_should_be = 0

for task in tasks:
    task_type = task[1]
    count = task[2]
    completed = task[3]
    
    if task_type == 'physical_assessment':
        if completed and count >= 5:
            physical_should_be = 1
    elif task_type == 'linguistic_assessment':
        if completed and count >= 1:
            linguistic_should_be = 1

print(f"\nCalculated scores should be:")
print(f"Physical: {physical_should_be}")
print(f"Linguistic: {linguistic_should_be}")

conn.close()
