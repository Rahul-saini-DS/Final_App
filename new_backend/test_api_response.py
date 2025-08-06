#!/usr/bin/env python
"""Test the API response for child 10"""
import requests
import json

try:
    # Test without authentication first
    response = requests.get('http://localhost:5000/api/child-responses/10')
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['attempts']:
            latest = data['attempts'][0]
            print('Latest attempt scores:')
            print(f'  Physical: {latest["scores"]["physical"]}')
            print(f'  Linguistic: {latest["scores"]["linguistic"]}')
            print(f'  Intelligence: {latest["scores"]["intelligence"]}')
            print(f'  Total: {latest["scores"]["total"]}')
            
            print('\nAI Tasks from API:')
            for task in latest['ai_tasks']:
                print(f'  {task["task_type"]}: success={task["success"]}, completed={task["was_completed"]}')
        else:
            print('No attempts found')
    else:
        print(f'Response: {response.text}')
        
except requests.ConnectionError:
    print("Error: Could not connect to server. Is Flask running?")
except Exception as e:
    print(f'Error: {e}')
