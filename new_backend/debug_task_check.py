import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

cursor.execute('SELECT task_type, success_count, was_completed FROM ai_task_responses WHERE result_id = 48')
tasks = cursor.fetchall()
print('Task details for result_id 48:')
for task in tasks:
    print(f'task_type="{task[0]}", success_count={task[1]}, completed="{task[2]}"')
    print(f'  Physical condition check: task_type in ["physical", "physical_assessment"]: {task[0] in ["physical", "physical_assessment"]}')
    print(f'  Success threshold check: success_count >= 5: {task[1] >= 5}')
    print(f'  Completed check: was_completed == "true": {task[2] == "true"}')
    if task[0] in ['physical', 'physical_assessment']:
        result = 1 if (task[2] == 'true' and task[1] >= 5) else 0
        print(f'  --> Final physical_binary would be: {result}')
        
conn.close()
