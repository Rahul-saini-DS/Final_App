import requests
import json

# Test the API endpoint directly
url = "http://localhost:5000/api/child-responses/10"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MzU2NjUwMDl9.KFJrP3HSQdOh3iUVekPpYxiB3dU5n-e--CqMD1JJw8w"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== API Response ===")
        print(json.dumps(data, indent=2))
        
        if data.get('summary') and data['summary'].get('latest_attempt'):
            latest = data['summary']['latest_attempt']
            print(f"\n=== Latest Attempt Scores ===")
            print(f"Physical Score: {latest.get('physical_score')}")
            print(f"Linguistic Score: {latest.get('linguistic_score')}")
            print(f"Intelligence Score: {latest.get('intelligence_score')}")
            print(f"Total Score: {latest.get('total_score')}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Connection error: {e}")
    print("Make sure the Flask backend is running on http://localhost:5000")
