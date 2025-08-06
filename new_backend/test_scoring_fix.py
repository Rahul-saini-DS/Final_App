#!/usr/bin/env python
"""Test the scoring logic with the actual database data"""
import sqlite3

conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get AI task responses for result_id 48
cursor.execute('''
    SELECT *
    FROM ai_task_responses atr
    WHERE atr.result_id = 48
    ORDER BY atr.created_at ASC
''')
ai_task_responses = cursor.fetchall()

print("Testing the fixed scoring logic:")
print("=" * 50)

physical_binary = 0
linguistic_binary = 0

for resp in ai_task_responses:
    task_type = resp[3]  # Fixed index
    original_success = resp[5]  # Fixed index 
    was_skipped = resp[11] == 'true'
    was_completed = resp[10] == 'true'
    
    print(f"\nTask: {task_type}")
    print(f"  success_count: {original_success}")
    print(f"  was_completed: {was_completed}")
    print(f"  was_skipped: {was_skipped}")
    
    # Apply the same logic as the fixed code
    if task_type == 'physical' or task_type == 'physical_assessment':
        task_success = 1 if (was_completed and original_success >= 5) else 0
        physical_binary = task_success
        print(f"  -> Physical binary calculated: {physical_binary}")
    elif task_type == 'linguistic' or task_type == 'linguistic_assessment':
        task_success = 1 if (was_completed and original_success >= 1) else 0
        linguistic_binary = task_success
        print(f"  -> Linguistic binary calculated: {linguistic_binary}")

print("\n" + "=" * 50)
print("FINAL RESULTS:")
print(f"Physical score: {physical_binary}")
print(f"Linguistic score: {linguistic_binary}")

# Compare with database stored scores
cursor.execute('SELECT intelligence_score, physical_score, linguistic_score FROM assessment_results WHERE id = 48')
db_scores = cursor.fetchone()
print(f"\nDatabase stored scores: intelligence={db_scores[0]}, physical={db_scores[1]}, linguistic={db_scores[2]}")

print(f"\nShould the frontend show physical as {physical_binary}? {'YES' if physical_binary == db_scores[1] else 'NO'}")

conn.close()
