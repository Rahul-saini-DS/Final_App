import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get the latest assessment with all details
print("=== COMPLETE ASSESSMENT ANALYSIS ===")
cursor.execute('SELECT * FROM assessment_results ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()

if result:
    result_id = result[0]
    print(f"Assessment Result ID: {result_id}")
    print(f"Intelligence Score: {result[3]}")
    print(f"Physical Score: {result[4]}")
    print(f"Linguistic Score: {result[5]}")
    print(f"Total Score: {result[6]}")
    
    print("\n=== AI TASK DETAILS ===")
    cursor.execute('SELECT * FROM ai_task_responses WHERE result_id = ?', (result_id,))
    tasks = cursor.fetchall()
    
    for task in tasks:
        print(f"Task Type: {task[4]}")
        print(f"Success Count: {task[6]}")
        print(f"Completed: {task[11]}")
        print(f"Skipped: {task[12]}")
        print("---")
        
    print("\n=== BACKEND LOGIC TEST ===")
    # Test the scoring logic
    for task in tasks:
        task_type = task[4]
        success_count = task[6]
        completed = task[11] == 'true'
        skipped = task[12] == 'true'
        
        if 'physical' in task_type:
            # Backend logic: 1 if completed AND success_count >= 5
            calculated_score = 1 if (completed and success_count >= 5) else 0
            print(f"Physical: completed={completed}, success_count={success_count} -> score={calculated_score}")
            
        elif 'linguistic' in task_type:
            # Backend logic: 1 if completed AND success_count >= 1  
            calculated_score = 1 if (completed and success_count >= 1) else 0
            print(f"Linguistic: completed={completed}, success_count={success_count} -> score={calculated_score}")

conn.close()
