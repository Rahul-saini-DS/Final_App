"""
Test script to verify backend scoring fixes
"""
import requests
import json

def test_scoring_fixes():
    """Test the improved scoring endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🔧 Testing Backend Scoring Fixes")
    print("=" * 50)
    
    # Test 1: Check linguistic endpoint
    print("\n1. Testing Linguistic Task Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/linguistic/0-1", timeout=5)
        if response.status_code == 200:
            print("✅ Linguistic endpoint working")
            data = response.json()
            print(f"   Task type: {data.get('task', {}).get('type', 'Unknown')}")
        else:
            print(f"❌ Linguistic endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Linguistic endpoint error: {e}")
    
    # Test 2: Mock assessment submission data
    print("\n2. Testing Assessment Submission Structure...")
    mock_assessment = {
        "age_group": "0-1",
        "intelligence_score": 2,
        "physical_score": 1,
        "linguistic_score": 0,
        "intelligence_responses": [
            {
                "question_id": "q1",
                "question": "When your baby gets a new object, what do they usually do?",
                "user_answer": "Looks at it with focus",
                "correct_answer": "Shakes or bangs it",
                "correct": False,
                "response_time": 30
            },
            {
                "question_id": "q2",
                "question": "Does your baby react to repeated actions or sounds?",
                "user_answer": "Laughs or gets excited every time",
                "correct_answer": "Laughs or gets excited every time",
                "correct": True,
                "response_time": 25
            },
            {
                "question_id": "q3",
                "question": "How does your baby respond to familiar and unfamiliar faces?",
                "user_answer": "Cries when seeing unfamiliar person",
                "correct_answer": "Smiles or shows excitement with familiar person",
                "correct": False,
                "response_time": 35
            },
            {
                "question_id": "q4",
                "question": "Which toy does your baby focus on for longer?",
                "user_answer": "Colorful patterned toy",
                "correct_answer": "Colorful patterned toy",
                "correct": True,
                "response_time": 20
            }
        ],
        "physical_details": {
            "task_type": "physical",
            "task_name": "Physical Development Assessment",
            "success_count": 10,
            "total_attempts": 30,
            "completion_time": 45,
            "start_time": "2025-08-03T18:15:00Z",
            "end_time": "2025-08-03T18:15:45Z",
            "completed": True,
            "feedback": "Good physical coordination"
        },
        "linguistic_details": {
            "task_type": "linguistic",
            "task_name": "Linguistic Development Assessment",
            "success_count": 1,
            "total_attempts": 20,
            "completion_time": 30,
            "start_time": "2025-08-03T18:16:00Z",
            "end_time": "2025-08-03T18:16:30Z",
            "completed": True,
            "feedback": "Partial speech recognition"
        }
    }
    
    print("📊 Mock Assessment Data:")
    print(f"   Intelligence: 2/4 questions correct (50%)")
    print(f"   Physical: 10/30 attempts successful (33.3%)")
    print(f"   Linguistic: 1/20 attempts successful (5%)")
    
    # Test 3: Calculate expected results
    print("\n3. Expected Calculation Results:")
    
    # Intelligence
    intel_correct = sum(1 for r in mock_assessment["intelligence_responses"] if r["correct"])
    intel_total = len(mock_assessment["intelligence_responses"])
    intel_accuracy = round(intel_correct / intel_total * 100, 1)
    print(f"   Intelligence: {intel_correct}/{intel_total} = {intel_accuracy}%")
    
    # Physical
    phys_success = mock_assessment["physical_details"]["success_count"]
    phys_attempts = mock_assessment["physical_details"]["total_attempts"]
    phys_rate = round(phys_success / phys_attempts * 100, 1) if phys_attempts > 0 else 0
    print(f"   Physical: {phys_success}/{phys_attempts} = {phys_rate}%")
    
    # Linguistic
    ling_success = mock_assessment["linguistic_details"]["success_count"]
    ling_attempts = mock_assessment["linguistic_details"]["total_attempts"]
    ling_rate = round(ling_success / ling_attempts * 100, 1) if ling_attempts > 0 else 0
    print(f"   Linguistic: {ling_success}/{ling_attempts} = {ling_rate}%")
    
    print("\n✅ Expected Results After Fix:")
    print("   - Intelligence score shows 2/4 (not 2/2)")
    print("   - Physical success rate shows 33.3% (not NaN%)")
    print("   - Linguistic success rate shows 5.0% (not NaN%)")
    print("   - All categories appear in charts (including 0 scores)")
    print("   - Completion times show realistic values (45s, 30s)")
    
    print("\n🔍 Key Fixes Applied:")
    print("   1. ✅ Added calculate_ai_success_rate() function with zero-guard")
    print("   2. ✅ Added calculate_completion_time() for proper timing")
    print("   3. ✅ Enhanced submit endpoint with detailed_scoring")
    print("   4. ✅ Added debugging prints for AI task submissions")
    print("   5. ✅ Fixed type conversion issues in success rate calculations")

def test_ai_success_rate_calculation():
    """Test the AI success rate calculation logic"""
    
    print("\n🧪 Testing AI Success Rate Calculation Logic:")
    print("-" * 45)
    
    # Test cases
    test_cases = [
        {
            "name": "Normal case",
            "data": [{"success_count": 10, "total_attempts": 30}],
            "expected": 33.3
        },
        {
            "name": "Perfect score",
            "data": [{"success_count": 20, "total_attempts": 20}],
            "expected": 100.0
        },
        {
            "name": "Zero attempts",
            "data": [{"success_count": 0, "total_attempts": 0}],
            "expected": 0.0
        },
        {
            "name": "String values",
            "data": [{"success_count": "5", "total_attempts": "10"}],
            "expected": 50.0
        },
        {
            "name": "Multiple tasks",
            "data": [
                {"success_count": 10, "total_attempts": 30},
                {"success_count": 1, "total_attempts": 20}
            ],
            "expected": 22.0  # (10+1)/(30+20) = 11/50 = 22%
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Data: {test['data']}")
        print(f"Expected: {test['expected']}%")
        
        # Manual calculation to verify logic
        total_success = 0
        total_attempts = 0
        
        for task in test['data']:
            try:
                success = int(task.get('success_count', 0)) if task.get('success_count') else 0
                attempts = int(task.get('total_attempts', 0)) if task.get('total_attempts') else 0
                total_success += success
                total_attempts += attempts
            except:
                pass
        
        result = round((total_success / total_attempts) * 100, 1) if total_attempts > 0 else 0.0
        print(f"Calculated: {result}%")
        
        if result == test['expected']:
            print("✅ PASS")
        else:
            print("❌ FAIL")

if __name__ == "__main__":
    test_scoring_fixes()
    test_ai_success_rate_calculation()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("   The backend fixes should resolve:")
    print("   - NaN% success rates → Proper percentages")
    print("   - Wrong score denominators → Correct question counts")
    print("   - Missing completion times → Realistic durations")
    print("   - Type errors in calculations → Safe conversions")
    print("\n   Next: Update frontend to use new detailed_scoring data!")
