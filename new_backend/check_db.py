import sqlite3

# Connect to database
conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Check recent assessment results
print("=== RECENT ASSESSMENT RESULTS ===")
cursor.execute('SELECT id, child_id, age_group, intelligence_score, physical_score, linguistic_score, total_score, completed_at FROM assessment_results ORDER BY completed_at DESC LIMIT 5')
results = cursor.fetchall()
for r in results:
    print(f"ID: {r[0]}, Child: {r[1]}, Age: {r[2]}, Intel: {r[3]}, Phys: {r[4]}, Ling: {r[5]}, Total: {r[6]}, Date: {r[7]}")

print("\n=== QUESTION RESPONSES ===")
cursor.execute('SELECT result_id, question_id, child_answer, correct_answer, is_correct FROM question_responses ORDER BY created_at DESC LIMIT 10')
responses = cursor.fetchall()
for r in responses:
    print(f"Result: {r[0]}, Q: {r[1]}, Child Answer: {r[2]}, Correct: {r[3]}, Is Correct: {r[4]}")

print("\n=== AI TASK RESPONSES ===")
cursor.execute('SELECT result_id, task_type, success_count, was_completed, was_skipped FROM ai_task_responses ORDER BY created_at DESC LIMIT 10')
ai_responses = cursor.fetchall()
for r in ai_responses:
    print(f"Result: {r[0]}, Type: {r[1]}, Success: {r[2]}, Completed: {r[3]}, Skipped: {r[4]}")

conn.close()
