"""
Test script to verify the scoring logic is working correctly
"""
import requests
import json

def test_scoring_scenario(scenario_name, test_data):
    print(f"\n=== Testing {scenario_name} ===")
    
    try:
        response = requests.post('http://localhost:5000/api/submit-assessment', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result_data = response.json()
            print("✅ Success!")
            print(f"Total Score: {result_data.get('total_score', 'N/A')}/{result_data.get('max_score', 'N/A')}")
            
            breakdown = result_data.get('breakdown', {})
            print(f"Intelligence: {breakdown.get('intelligence', 'N/A')}")
            print(f"Physical: {breakdown.get('physical', 'N/A')}")
            print(f"Linguistic: {breakdown.get('linguistic', 'N/A')}")
            
            debug_info = result_data.get('debug_info', {})
            print(f"Physical completed: {debug_info.get('physical_completed', 'N/A')}")
            print(f"Physical success_count: {debug_info.get('physical_success_count', 'N/A')}")
            print(f"Linguistic completed: {debug_info.get('linguistic_completed', 'N/A')}")
            print(f"Linguistic success_count: {debug_info.get('linguistic_success_count', 'N/A')}")
            
            return result_data
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Test Case 1: Perfect score - all tasks completed with success
perfect_score_data = {
    "age_group": "0-1",
    "intelligence_responses": [
        {"question_id": "q1", "question": "Test Q1", "user_answer": "A", "correct_answer": "A", "correct": True},
        {"question_id": "q2", "question": "Test Q2", "user_answer": "B", "correct_answer": "B", "correct": True},
        {"question_id": "q3", "question": "Test Q3", "user_answer": "C", "correct_answer": "C", "correct": True},
        {"question_id": "q4", "question": "Test Q4", "user_answer": "D", "correct_answer": "D", "correct": True}
    ],
    "physical_details": {
        "task_type": "physical_assessment",
        "task_name": "Physical Development Assessment",
        "success_count": 5,  # Successful detection
        "total_attempts": 1,
        "completion_time": 30,
        "success_rate": 1,
        "feedback": "Successfully completed physical task",
        "completed": True,
        "skipped": False
    },
    "linguistic_details": {
        "task_type": "linguistic_assessment",
        "task_name": "Linguistic Development Assessment", 
        "success_count": 1,  # Successful recognition
        "total_attempts": 1,
        "completion_time": 20,
        "success_rate": 1,
        "feedback": "Successfully completed linguistic task",
        "completed": True,
        "skipped": False
    }
}

# Test Case 2: Attempted but failed - tasks completed but no success
failed_tasks_data = {
    "age_group": "0-1",
    "intelligence_responses": [
        {"question_id": "q1", "question": "Test Q1", "user_answer": "A", "correct_answer": "A", "correct": True},
        {"question_id": "q2", "question": "Test Q2", "user_answer": "B", "correct_answer": "A", "correct": False},
        {"question_id": "q3", "question": "Test Q3", "user_answer": "C", "correct_answer": "A", "correct": False},
        {"question_id": "q4", "question": "Test Q4", "user_answer": "D", "correct_answer": "A", "correct": False}
    ],
    "physical_details": {
        "task_type": "physical_assessment",
        "task_name": "Physical Development Assessment",
        "success_count": 0,  # No successful detection
        "total_attempts": 1,
        "completion_time": 30,
        "success_rate": 0,
        "feedback": "Physical task attempted but not completed",
        "completed": True,  # Attempted but failed
        "skipped": False
    },
    "linguistic_details": {
        "task_type": "linguistic_assessment",
        "task_name": "Linguistic Development Assessment", 
        "success_count": 0,  # No successful recognition
        "total_attempts": 1,
        "completion_time": 20,
        "success_rate": 0,
        "feedback": "Linguistic task attempted but not completed",
        "completed": True,  # Attempted but failed
        "skipped": False
    }
}

# Test Case 3: Mixed results
mixed_results_data = {
    "age_group": "0-1",
    "intelligence_responses": [
        {"question_id": "q1", "question": "Test Q1", "user_answer": "A", "correct_answer": "A", "correct": True},
        {"question_id": "q2", "question": "Test Q2", "user_answer": "B", "correct_answer": "B", "correct": True},
        {"question_id": "q3", "question": "Test Q3", "user_answer": "C", "correct_answer": "A", "correct": False},
        {"question_id": "q4", "question": "Test Q4", "user_answer": "D", "correct_answer": "A", "correct": False}
    ],
    "physical_details": {
        "task_type": "physical_assessment", 
        "task_name": "Physical Development Assessment",
        "success_count": 3,  # Some success
        "total_attempts": 1,
        "completion_time": 30,
        "success_rate": 1,
        "feedback": "Successfully completed physical task",
        "completed": True,
        "skipped": False
    },
    "linguistic_details": {
        "task_type": "linguistic_assessment",
        "task_name": "Linguistic Development Assessment", 
        "success_count": 0,  # No success
        "total_attempts": 1,
        "completion_time": 20,
        "success_rate": 0,
        "feedback": "Linguistic task attempted but not completed",
        "completed": True,
        "skipped": False
    }
}

print("🧪 Testing Assessment Scoring Logic")
print("=" * 50)

# Run tests
result1 = test_scoring_scenario("Perfect Score (6/6)", perfect_score_data)
result2 = test_scoring_scenario("Failed Tasks (1/6)", failed_tasks_data) 
result3 = test_scoring_scenario("Mixed Results (3/6)", mixed_results_data)

print("\n" + "=" * 50)
print("📊 Expected vs Actual Results:")
print("=" * 50)

if result1:
    print(f"Perfect Score: Expected 6/6, Got {result1.get('total_score')}/{result1.get('max_score')}")
if result2:
    print(f"Failed Tasks: Expected 1/6, Got {result2.get('total_score')}/{result2.get('max_score')}")  
if result3:
    print(f"Mixed Results: Expected 3/6, Got {result3.get('total_score')}/{result3.get('max_score')}")

print("\n🎯 Key Rule: Physical/Linguistic score = 1 ONLY if (completed = True AND success_count > 0)")
