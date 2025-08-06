#!/usr/bin/env python
"""Test the timezone fix in the API response"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timezone_utils import convert_utc_to_ist
import sqlite3

# Test with actual database data
conn = sqlite3.connect('assessment.db')
cursor = conn.cursor()

# Get the latest assessment timestamp
cursor.execute('SELECT completed_at FROM assessment_results WHERE id = 49')
result = cursor.fetchone()

if result:
    original_time = result[0]
    converted_time = convert_utc_to_ist(original_time)
    
    print("Timezone Conversion Test:")
    print(f"Database UTC time: {original_time}")
    print(f"Converted IST time: {converted_time}")
    print(f"Expected format: 'Aug 06, 2025, 08:50 AM'")
    print(f"Match expected: {'✅ YES' if 'Aug 06, 2025' in converted_time and 'AM' in converted_time else '❌ NO'}")
else:
    print("No data found")

conn.close()
