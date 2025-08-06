import requests
import json

try:
    # Test the API endpoint
    response = requests.get('http://localhost:5000/api/child-responses/10', 
                          headers={'Authorization': 'Bearer dummy-token'})
    
    if response.status_code == 200:
        data = response.json()
        print('=== API RESPONSE ===')
        print(f"Child ID: {data.get('child_id')}")
        
        if data.get('summary') and data.get('summary').get('latest_attempt'):
            latest = data['summary']['latest_attempt']
            print(f"Latest attempt scores:")
            print(f"  Intelligence: {latest.get('intelligence_score')}")
            print(f"  Physical: {latest.get('physical_score')}")
            print(f"  Linguistic: {latest.get('linguistic_score')}")
            print(f"  Total: {latest.get('total_score')}")
        
        if data.get('attempts') and len(data['attempts']) > 0:
            attempt = data['attempts'][0]
            print(f"\nAttempt details:")
            print(f"  Intelligence: {attempt['scores']['intelligence']}")
            print(f"  Physical: {attempt['scores']['physical']}")
            print(f"  Linguistic: {attempt['scores']['linguistic']}")
            
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Request failed: {e}")
