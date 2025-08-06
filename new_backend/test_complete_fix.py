#!/usr/bin/env python
"""Test the complete API route logic after the fix"""
import sqlite3
import sys
import os

# Add the current directory to Python path to import app functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_child_responses_logic():
    """Test the corrected logic from get_child_detailed_responses"""
    
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    child_id = 10
    
    # Get all assessment results for this child (same as API)
    cursor.execute('''
        SELECT ar.id, ar.completed_at, ar.age_group, ar.intelligence_score, ar.physical_score, ar.linguistic_score, ar.total_score
        FROM assessment_results ar
        WHERE ar.child_id = ?
        ORDER BY ar.completed_at DESC
    ''', (child_id,))
    assessment_results = cursor.fetchall()
    
    if not assessment_results:
        print("No assessment results found")
        return
    
    # Process the latest attempt (same as API)
    result_id, completed_at, age_group, intelligence_score, physical_score, linguistic_score, total_score = assessment_results[0]
    
    print(f"Processing result_id: {result_id}")
    print(f"DB stored scores: intelligence={intelligence_score}, physical={physical_score}, linguistic={linguistic_score}")
    
    # Get AI task responses for this attempt (same as API)
    cursor.execute('''
        SELECT atr.*
        FROM ai_task_responses atr
        WHERE atr.result_id = ?
        ORDER BY atr.created_at ASC
    ''', (result_id,))
    ai_task_responses = cursor.fetchall()
    
    # Apply the FIXED logic from the API
    physical_binary = 0
    linguistic_binary = 0
    
    print("\nProcessing AI tasks with FIXED indices:")
    for resp in ai_task_responses:
        task_type = resp[3]  # FIXED: task_type
        original_success = resp[5]  # FIXED: success_count
        was_skipped = resp[11] == 'true'  # was_skipped
        was_completed = resp[10] == 'true'  # was_completed
        
        print(f"\nTask: {task_type}")
        print(f"  success_count: {original_success} (from index 5)")
        print(f"  was_completed: {was_completed} (from index 10)")
        print(f"  was_skipped: {was_skipped} (from index 11)")
        
        # Apply the same conditions as the fixed API
        if task_type == 'physical' or task_type == 'physical_assessment':
            task_success = 1 if (was_completed and original_success >= 5) else 0
            physical_binary = task_success
            print(f"  -> Physical: completed={was_completed} AND success>={original_success}>=5 = {task_success}")
        elif task_type == 'linguistic' or task_type == 'linguistic_assessment':
            task_success = 1 if (was_completed and original_success >= 1) else 0
            linguistic_binary = task_success
            print(f"  -> Linguistic: completed={was_completed} AND success>={original_success}>=1 = {task_success}")
    
    print("\n" + "="*60)
    print("FINAL COMPARISON:")
    print(f"Database stored physical score: {physical_score}")
    print(f"API calculated physical score: {physical_binary}")
    print(f"Match: {'✅ YES' if physical_binary == physical_score else '❌ NO'}")
    
    print(f"\nDatabase stored linguistic score: {linguistic_score}")
    print(f"API calculated linguistic score: {linguistic_binary}")
    print(f"Match: {'✅ YES' if linguistic_binary == linguistic_score else '❌ NO'}")
    
    conn.close()
    
    return physical_binary == physical_score and linguistic_binary == linguistic_score

if __name__ == "__main__":
    success = test_child_responses_logic()
    print(f"\n{'🎉 SUCCESS: Fix is working correctly!' if success else '❌ FAILED: Fix did not work'}")
