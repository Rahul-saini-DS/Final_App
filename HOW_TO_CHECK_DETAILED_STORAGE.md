# 🔍 How to Check if Detailed Answers are Being Stored

## **STEP 1: Check Database Structure**

1. **Open terminal in new_backend folder**
2. **Run this command:**
   ```bash
   python simple_db_check.py
   ```

## **STEP 2: Start the Backend and Take a Test Assessment**

1. **Start backend:**
   ```bash
   python app.py
   ```

2. **Open frontend and take an assessment**
   - Answer the intelligence questions
   - Complete or skip the AI tasks
   - Submit the assessment

## **STEP 3: Check if Data Was Stored**

### **Option A: Direct Database Query**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Check latest assessment
cursor.execute('SELECT id, total_score, completed_at FROM assessment_results ORDER BY completed_at DESC LIMIT 1')
latest = cursor.fetchone()
if latest:
    assessment_id = latest[0]
    print(f'Latest Assessment ID: {assessment_id}')
    
    # Check detailed question responses
    cursor.execute('SELECT COUNT(*) FROM question_responses WHERE result_id = ?', (assessment_id,))
    q_count = cursor.fetchone()[0]
    print(f'Question responses stored: {q_count}')
    
    # Check AI task responses  
    cursor.execute('SELECT COUNT(*) FROM ai_task_responses WHERE result_id = ?', (assessment_id,))
    ai_count = cursor.fetchone()[0]
    print(f'AI task responses stored: {ai_count}')
    
    if q_count > 0:
        cursor.execute('SELECT question_text, child_answer, is_correct FROM question_responses WHERE result_id = ? LIMIT 3', (assessment_id,))
        for q in cursor.fetchall():
            print(f'Q: {q[0][:40]}...')
            print(f'A: {q[1]} ({'✅' if q[2] == 'true' else '❌'})')
else:
    print('No assessments found')
conn.close()
"
```

### **Option B: Use the New API Endpoints**

1. **Get child responses:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/child-responses/1
   ```

2. **Get assessment insights:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/assessment-insights/1
   ```

## **STEP 4: What You Should See**

### **If Working Correctly:**
- ✅ `question_responses` table has records
- ✅ `ai_task_responses` table has records  
- ✅ Each assessment creates multiple detail records
- ✅ API endpoints return detailed analysis

### **If NOT Working:**
- ❌ Tables exist but are empty
- ❌ Only basic assessment_results records
- ❌ API returns empty arrays

## **STEP 5: Visual Verification**

### **Check in Frontend:**
1. **Take an assessment**
2. **Go to Results page** 
3. **Look for detailed breakdown**
4. **Check if individual question responses are visible**

### **Check API Response:**
The submit assessment should now return:
```json
{
  "message": "Assessment submitted successfully",
  "result_id": 123,
  "total_score": 2.5,
  "details_saved": {
    "intelligence_questions": 4,
    "physical_task": true,
    "linguistic_task": true
  }
}
```

## **TROUBLESHOOTING:**

### **If No Detailed Data:**
1. **Check if tables were created:**
   ```bash
   python simple_db_check.py
   ```

2. **Check backend logs for errors**

3. **Verify frontend is sending detailed data:**
   - Open browser dev tools
   - Check Network tab during assessment submission
   - Look for `intelligence_responses`, `physical_details`, `linguistic_details` in request

### **If Tables Don't Exist:**
Run the backend once - it will create tables automatically when first assessment is submitted.

## **QUICK TEST:**

Run this to insert test data and verify storage:
```bash
python test_detailed_storage.py
```

This will show you exactly what data is being stored and how to retrieve it.
