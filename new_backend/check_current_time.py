from datetime import datetime
import pytz

# Check current times
print('Current time comparison:')
print(f'System time (local): {datetime.now()}')

ist = pytz.timezone('Asia/Kolkata')
utc = pytz.UTC

current_ist = datetime.now(ist)
current_utc = datetime.now(utc)

print(f'Current IST: {current_ist.strftime("%b %d, %Y, %I:%M %p")}')
print(f'Current UTC: {current_utc.strftime("%b %d, %Y, %I:%M %p")}')
print(f'IST Hour: {current_ist.hour}, UTC Hour: {current_utc.hour}')
print(f'Time difference: IST is {current_ist.hour - current_utc.hour} hours ahead of UTC')

# Test what would happen if we store current time in database
simulated_db_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f'\nIf we store current local time in DB: {simulated_db_time}')

# Convert it back (assuming it was UTC)
dt_utc = datetime.strptime(simulated_db_time, '%Y-%m-%d %H:%M:%S')
dt_utc = utc.localize(dt_utc)
dt_ist_converted = dt_utc.astimezone(ist)
print(f'Converting as if it was UTC: {dt_ist_converted.strftime("%b %d, %Y, %I:%M %p")}')
print('This would be WRONG - it adds another 5:30 hours!')
