import sqlite3

# Connect to the database and check the most recent assessment
conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get the most recent assessment result
cursor.execute('''
    SELECT ar.*, c.child_name 
    FROM assessment_results ar
    LEFT JOIN children c ON ar.child_id = c.id  
    ORDER BY ar.completed_at DESC 
    LIMIT 1
''')
latest_result = cursor.fetchone()

if latest_result:
    result_id = latest_result[0]
    print(f"=== LATEST ASSESSMENT (ID: {result_id}) ===")
    print(f"Child ID: {latest_result[2]}")
    print(f"Age Group: {latest_result[3]}")
    print(f"Intelligence: {latest_result[4]}")
    print(f"Physical: {latest_result[5]}")
    print(f"Linguistic: {latest_result[6]}")
    print(f"Total: {latest_result[7]}")
    print(f"Date: {latest_result[8]}")
    
    print(f"\n=== INTELLIGENCE QUESTIONS FOR RESULT {result_id} ===")
    cursor.execute('''
        SELECT question_id, question_text, child_answer, correct_answer, is_correct
        FROM question_responses 
        WHERE result_id = ?
        ORDER BY created_at
    ''', (result_id,))
    questions = cursor.fetchall()
    
    correct_count = 0
    for i, q in enumerate(questions, 1):
        is_correct = q[4] == 'true'
        if is_correct:
            correct_count += 1
        print(f"Q{i}: {q[1]}")
        print(f"   Child Answer: {q[2]}")
        print(f"   Correct Answer: {q[3]}")
        print(f"   Is Correct: {is_correct} ({'✅' if is_correct else '❌'})")
        print()
    
    print(f"Intelligence Score Calculation: {correct_count}/{len(questions)}")
    
    print(f"\n=== AI TASKS FOR RESULT {result_id} ===")
    cursor.execute('''
        SELECT task_type, task_name, success_count, was_completed, was_skipped, ai_feedback
        FROM ai_task_responses 
        WHERE result_id = ?
        ORDER BY created_at
    ''', (result_id,))
    ai_tasks = cursor.fetchall()
    
    for task in ai_tasks:
        task_type, task_name, success_count, was_completed, was_skipped, feedback = task
        binary_result = 1 if (was_completed == 'true' and success_count > 0) else 0
        
        print(f"Task: {task_type} ({task_name})")
        print(f"   Success Count: {success_count}")
        print(f"   Was Completed: {was_completed}")
        print(f"   Was Skipped: {was_skipped}")
        print(f"   Binary Result: {binary_result}")
        print(f"   Feedback: {feedback}")
        print()
    
    # Calculate expected total
    physical_score = 1 if any(t[0] in ['physical', 'physical_assessment'] and t[2] > 0 and t[3] == 'true' for t in ai_tasks) else 0
    linguistic_score = 1 if any(t[0] in ['linguistic', 'linguistic_assessment'] and t[2] > 0 and t[3] == 'true' for t in ai_tasks) else 0
    expected_total = correct_count + physical_score + linguistic_score
    
    print(f"=== SCORE VERIFICATION ===")
    print(f"Intelligence: {correct_count}/{len(questions)}")
    print(f"Physical: {physical_score}/1")
    print(f"Linguistic: {linguistic_score}/1")
    print(f"Expected Total: {expected_total}/{len(questions) + 2}")
    print(f"Stored Total: {latest_result[7]}")
    print(f"Match: {'✅' if expected_total == latest_result[7] else '❌'}")

else:
    print("No assessment results found")

conn.close()
