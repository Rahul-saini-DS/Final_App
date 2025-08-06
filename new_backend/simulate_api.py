import sqlite3

def simulate_api_logic(child_id):
    """Simulate the exact logic from the API endpoint"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Get all assessment results for this child (same as API)
    cursor.execute('''
        SELECT ar.id, ar.completed_at, ar.age_group, ar.intelligence_score, ar.physical_score, ar.linguistic_score, ar.total_score
        FROM assessment_results ar
        WHERE ar.child_id = ?
        ORDER BY ar.completed_at DESC
    ''', (child_id,))
    assessment_results = cursor.fetchall()
    
    if not assessment_results:
        print(f"No results found for child_id {child_id}")
        return
        
    # Process the latest attempt
    result_id, completed_at, age_group, intelligence_score, physical_score, linguistic_score, total_score = assessment_results[0]
    print(f"Processing result_id: {result_id}")
    
    # Get AI task responses for this attempt
    cursor.execute('''
        SELECT atr.*
        FROM ai_task_responses atr
        WHERE atr.result_id = ?
        ORDER BY atr.created_at ASC
    ''', (result_id,))
    ai_task_responses = cursor.fetchall()
    
    # Apply the EXACT logic from the API
    physical_binary = 0
    linguistic_binary = 0
    
    for resp in ai_task_responses:
        task_type = resp[3]  # task_type column (corrected)
        original_success = resp[5]  # success_count column (corrected)
        was_skipped = resp[11] == 'true'  # was_skipped column (corrected)
        was_completed = resp[10] == 'true'  # was_completed column (corrected)
        
        print(f"\nTask: {task_type}")
        print(f"  success_count: {original_success}")
        print(f"  was_completed: {was_completed}")
        print(f"  was_skipped: {was_skipped}")
        
        # Apply the UPDATED logic from app.py
        if task_type == 'physical' or task_type == 'physical_assessment':
            task_success = 1 if (was_completed and original_success >= 5) else 0
            physical_binary = task_success
            print(f"  -> Physical score: {task_success}")
        elif task_type == 'linguistic' or task_type == 'linguistic_assessment':
            task_success = 1 if (was_completed and original_success >= 1) else 0
            linguistic_binary = task_success
            print(f"  -> Linguistic score: {task_success}")
    
    print(f"\nFINAL API SCORES:")
    print(f"Physical: {physical_binary}")
    print(f"Linguistic: {linguistic_binary}")
    
    conn.close()

# Test with child_id = 10
simulate_api_logic(10)
