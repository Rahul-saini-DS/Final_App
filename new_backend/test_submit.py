import requests
import json

# Test the submit-assessment endpoint with sample data
test_data = {
    "age_group": "0-1",
    "intelligence_score": 2,  # This will be ignored by new backend logic
    "physical_score": 1,      # This will be ignored by new backend logic
    "linguistic_score": 0,    # This will be ignored by new backend logic
    "total_score": 3,         # This will be ignored by new backend logic
    "intelligence_responses": [
        {
            "question_id": "test1",
            "question": "Test question 1",
            "user_answer": "Option A",
            "correct_answer": "Option A", 
            "correct": True,
            "response_time": 5,
            "difficulty": 1,
            "attempts": 1
        },
        {
            "question_id": "test2",
            "question": "Test question 2",
            "user_answer": "Option B",
            "correct_answer": "Option A",
            "correct": False,
            "response_time": 8,
            "difficulty": 1,
            "attempts": 1
        },
        {
            "question_id": "test3",
            "question": "Test question 3",
            "user_answer": "Option C",
            "correct_answer": "Option C",
            "correct": True,
            "response_time": 4,
            "difficulty": 1,
            "attempts": 1
        }
    ],
    "physical_details": {
        "task_type": "physical_assessment",
        "task_name": "Physical Development Assessment",
        "success_count": 5,
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
        "success_count": 0,
        "total_attempts": 1,
        "completion_time": 20,
        "success_rate": 0,
        "feedback": "Linguistic task attempted but not completed",
        "completed": True,
        "skipped": False
    }
}

try:
    response = requests.post('http://localhost:5000/api/submit-assessment', 
                           json=test_data,
                           headers={'Content-Type': 'application/json'})
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        result_data = response.json()
        print("\n=== EXPECTED vs ACTUAL ===")
        print(f"Expected Intelligence: 2/3 (2 correct out of 3)")
        print(f"Actual Intelligence: {result_data.get('breakdown', {}).get('intelligence', 'N/A')}")
        print(f"Expected Physical: 1/1 (completed with success_count > 0)")
        print(f"Actual Physical: {result_data.get('breakdown', {}).get('physical', 'N/A')}")
        print(f"Expected Linguistic: 0/1 (completed but success_count = 0)")
        print(f"Actual Linguistic: {result_data.get('breakdown', {}).get('linguistic', 'N/A')}")
        print(f"Expected Total: 3/5")
        print(f"Actual Total: {result_data.get('total_score', 'N/A')}/{result_data.get('max_score', 'N/A')}")
        
        if 'debug_info' in result_data:
            print("\n=== DEBUG INFO ===")
            debug = result_data['debug_info']
            for key, value in debug.items():
                print(f"{key}: {value}")
    
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to backend. Make sure it's running on localhost:5000")
except Exception as e:
    print(f"ERROR: {e}")
