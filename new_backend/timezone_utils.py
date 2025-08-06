"""
Timezone utility functions for converting database timestamps to IST (India Standard Time)
"""
from datetime import datetime
import pytz

def convert_utc_to_ist(utc_timestamp_str):
    """
    Convert UTC timestamp string from database to IST formatted string
    
    Args:
        utc_timestamp_str (str): UTC timestamp in format 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        str: Formatted IST timestamp like 'Aug 06, 2025, 08:50 AM'
    """
    try:
        # Define timezones
        utc = pytz.UTC
        ist = pytz.timezone('Asia/Kolkata')
        
        # Parse the database timestamp (assuming it's UTC)
        dt_utc = datetime.strptime(utc_timestamp_str, '%Y-%m-%d %H:%M:%S')
        dt_utc = utc.localize(dt_utc)
        
        # Convert to IST
        dt_ist = dt_utc.astimezone(ist)
        
        # Format as requested: "Aug 6, 2025, 02:32 AM" style
        return dt_ist.strftime("%b %d, %Y, %I:%M %p")
        
    except Exception as e:
        # Fallback to original timestamp if conversion fails
        print(f"Warning: Timezone conversion failed for '{utc_timestamp_str}': {e}")
        return utc_timestamp_str

def convert_utc_to_ist_datetime(utc_timestamp_str):
    """
    Convert UTC timestamp string to IST datetime object
    
    Args:
        utc_timestamp_str (str): UTC timestamp in format 'YYYY-MM-DD HH:MM:SS'
    
    Returns:
        datetime: IST datetime object
    """
    try:
        # Define timezones
        utc = pytz.UTC
        ist = pytz.timezone('Asia/Kolkata')
        
        # Parse the database timestamp (assuming it's UTC)
        dt_utc = datetime.strptime(utc_timestamp_str, '%Y-%m-%d %H:%M:%S')
        dt_utc = utc.localize(dt_utc)
        
        # Convert to IST
        dt_ist = dt_utc.astimezone(ist)
        return dt_ist
        
    except Exception as e:
        print(f"Warning: Timezone conversion failed for '{utc_timestamp_str}': {e}")
        # Return original as naive datetime
        return datetime.strptime(utc_timestamp_str, '%Y-%m-%d %H:%M:%S')

def get_current_ist():
    """
    Get current time in IST
    
    Returns:
        datetime: Current IST datetime object
    """
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def get_current_ist_string():
    """
    Get current time in IST as formatted string
    
    Returns:
        str: Current IST time as formatted string
    """
    return get_current_ist().strftime("%b %d, %Y, %I:%M %p")

if __name__ == "__main__":
    # Test the functions
    test_time = "2025-08-06 03:20:23"
    print(f"UTC: {test_time}")
    print(f"IST: {convert_utc_to_ist(test_time)}")
    print(f"Current IST: {get_current_ist_string()}")
