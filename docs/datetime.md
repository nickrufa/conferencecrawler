# Python datetime Module Documentation

The `datetime` module supplies classes for manipulating dates and times in both simple and complex ways. It provides classes for dates, times, time intervals, and time zones.

## Basic Classes

### datetime.datetime
Represents a specific moment in time (date + time).

```python
from datetime import datetime

# Current date and time
now = datetime.now()
print(now)  # 2023-12-25 14:30:45.123456

# Specific date and time
dt = datetime(2023, 12, 25, 14, 30, 45)
print(dt)  # 2023-12-25 14:30:45

# From string
dt = datetime.strptime("2023-12-25 14:30", "%Y-%m-%d %H:%M")
```

### datetime.date
Represents a date (year, month, day).

```python
from datetime import date

# Current date
today = date.today()
print(today)  # 2023-12-25

# Specific date
d = date(2023, 12, 25)
print(d)  # 2023-12-25

# From datetime
dt = datetime.now()
d = dt.date()
```

### datetime.time
Represents time (hour, minute, second, microsecond).

```python
from datetime import time

# Specific time
t = time(14, 30, 45)
print(t)  # 14:30:45

# With microseconds
t = time(14, 30, 45, 123456)
print(t)  # 14:30:45.123456

# From datetime
dt = datetime.now()
t = dt.time()
```

### datetime.timedelta
Represents duration (difference between dates/times).

```python
from datetime import datetime, timedelta

# Duration
delta = timedelta(days=7, hours=3, minutes=30)
print(delta)  # 7 days, 3:30:00

# Add/subtract from datetime
now = datetime.now()
future = now + delta
past = now - delta

print(f"Now: {now}")
print(f"Future: {future}")
print(f"Past: {past}")
```

## Creating Dates and Times

### Current Date/Time
```python
from datetime import datetime, date, time

# Current datetime
now = datetime.now()
utc_now = datetime.utcnow()

# Current date
today = date.today()

# No direct way to get current time only
current_time = datetime.now().time()
```

### From Components
```python
from datetime import datetime, date, time

# Specific datetime
dt = datetime(2023, 12, 25, 14, 30, 45, 123456)

# Specific date
d = date(2023, 12, 25)

# Specific time
t = time(14, 30, 45, 123456)
```

### From Strings (Parsing)
```python
from datetime import datetime

# Using strptime (string parse time)
dt1 = datetime.strptime("2023-12-25", "%Y-%m-%d")
dt2 = datetime.strptime("25/12/2023 14:30", "%d/%m/%Y %H:%M")
dt3 = datetime.strptime("Dec 25, 2023", "%b %d, %Y")

# ISO format
dt4 = datetime.fromisoformat("2023-12-25T14:30:45")
```

### From Timestamps
```python
import time
from datetime import datetime

# From UNIX timestamp
timestamp = time.time()
dt = datetime.fromtimestamp(timestamp)

# From specific timestamp
dt = datetime.fromtimestamp(1703520645)  # Specific timestamp
```

## Formatting Dates and Times

### String Formatting
```python
from datetime import datetime

dt = datetime(2023, 12, 25, 14, 30, 45)

# Various formats
print(dt.strftime("%Y-%m-%d"))           # 2023-12-25
print(dt.strftime("%d/%m/%Y"))           # 25/12/2023
print(dt.strftime("%B %d, %Y"))          # December 25, 2023
print(dt.strftime("%A, %B %d, %Y"))      # Monday, December 25, 2023
print(dt.strftime("%Y-%m-%d %H:%M:%S"))  # 2023-12-25 14:30:45

# ISO format
print(dt.isoformat())  # 2023-12-25T14:30:45

# Default string representation
print(str(dt))  # 2023-12-25 14:30:45
```

### Common Format Codes
```python
# Date formatting codes
%Y  # Year with century (2023)
%y  # Year without century (23)
%m  # Month as number (01-12)
%B  # Full month name (December)
%b  # Abbreviated month name (Dec)
%d  # Day of month (01-31)
%A  # Full weekday name (Monday)
%a  # Abbreviated weekday name (Mon)
%w  # Weekday as number (0=Sunday, 6=Saturday)

# Time formatting codes
%H  # Hour (00-23)
%I  # Hour (01-12)
%M  # Minute (00-59)
%S  # Second (00-59)
%f  # Microsecond (000000-999999)
%p  # AM/PM

# Examples
dt = datetime(2023, 12, 25, 14, 30, 45)
print(f"Date: {dt:%Y-%m-%d}")           # Date: 2023-12-25
print(f"Time: {dt:%H:%M:%S}")           # Time: 14:30:45
print(f"Full: {dt:%A, %B %d, %Y}")      # Full: Monday, December 25, 2023
```

## Date/Time Arithmetic

### Using timedelta
```python
from datetime import datetime, timedelta

now = datetime.now()

# Add/subtract time
future = now + timedelta(days=30)           # 30 days from now
past = now - timedelta(weeks=2)             # 2 weeks ago
later = now + timedelta(hours=3, minutes=30)  # 3.5 hours from now

print(f"Now: {now}")
print(f"30 days from now: {future}")
print(f"2 weeks ago: {past}")
```

### Calculating Differences
```python
from datetime import datetime

start = datetime(2023, 1, 1)
end = datetime(2023, 12, 25)

# Calculate difference
diff = end - start
print(f"Days: {diff.days}")                    # 358
print(f"Total seconds: {diff.total_seconds()}") # Total seconds in difference

# Time components
print(f"Days: {diff.days}")
print(f"Seconds: {diff.seconds}")
print(f"Microseconds: {diff.microseconds}")
```

### Working with Time Periods
```python
from datetime import datetime, timedelta

# Calculate age
birth_date = datetime(1990, 5, 15)
today = datetime.now()
age = today - birth_date

years = age.days // 365
print(f"Approximate age: {years} years")

# Calculate business days
def add_business_days(start_date, days):
    current = start_date
    while days > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Sunday=6
            days -= 1
    return current

start = datetime(2023, 12, 22)  # Friday
result = add_business_days(start, 5)  # Add 5 business days
print(result)  # Will skip weekend
```

## Working with Dates

### Date Properties and Methods
```python
from datetime import date

d = date(2023, 12, 25)

# Properties
print(d.year)      # 2023
print(d.month)     # 12
print(d.day)       # 25

# Weekday (Monday=0, Sunday=6)
print(d.weekday())  # 0 (Monday)

# ISO weekday (Monday=1, Sunday=7)
print(d.isoweekday())  # 1 (Monday)

# Day of year
print(d.timetuple().tm_yday)  # Day number in year

# Replace components
new_date = d.replace(year=2024)
print(new_date)  # 2024-12-25
```

### Date Ranges and Iteration
```python
from datetime import date, timedelta

start_date = date(2023, 12, 1)
end_date = date(2023, 12, 31)

# Generate date range
dates = []
current = start_date
while current <= end_date:
    dates.append(current)
    current += timedelta(days=1)

print(f"December 2023 has {len(dates)} days")

# Get all Mondays in December 2023
mondays = [d for d in dates if d.weekday() == 0]
print(f"Mondays in December 2023: {mondays}")
```

## Time Zones

### Basic Timezone Handling
```python
from datetime import datetime, timezone, timedelta

# UTC timezone
utc_now = datetime.now(timezone.utc)
print(utc_now)

# Specific timezone offset
est = timezone(timedelta(hours=-5))  # Eastern Standard Time
est_time = datetime.now(est)
print(est_time)

# Convert between timezones
utc_time = datetime.now(timezone.utc)
local_time = utc_time.astimezone()  # Convert to local timezone
```

### Using pytz (Third-party Library)
```python
# pip install pytz
import pytz
from datetime import datetime

# Create timezone-aware datetime
utc = pytz.UTC
eastern = pytz.timezone('US/Eastern')
pacific = pytz.timezone('US/Pacific')

# Current time in different zones
utc_now = datetime.now(utc)
eastern_now = utc_now.astimezone(eastern)
pacific_now = utc_now.astimezone(pacific)

print(f"UTC: {utc_now}")
print(f"Eastern: {eastern_now}")
print(f"Pacific: {pacific_now}")
```

## Common Use Cases

### Conference Date Processing
```python
from datetime import datetime, timedelta
import re

def parse_conference_date(date_str):
    """Parse various conference date formats"""
    formats = [
        "%B %d, %Y",           # December 25, 2023
        "%b %d, %Y",           # Dec 25, 2023
        "%Y-%m-%d",            # 2023-12-25
        "%d/%m/%Y",            # 25/12/2023
        "%m/%d/%Y",            # 12/25/2023
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")

# Examples
dates = [
    "December 25, 2023",
    "Dec 25, 2023", 
    "2023-12-25",
    "25/12/2023"
]

for date_str in dates:
    try:
        parsed = parse_conference_date(date_str)
        print(f"'{date_str}' -> {parsed.strftime('%Y-%m-%d')}")
    except ValueError as e:
        print(e)
```

### Date Range Validation
```python
from datetime import datetime, date

def validate_conference_dates(start_date, end_date):
    """Validate conference date range"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    today = date.today()
    
    # Check if dates are in the future
    if start_date < today:
        return False, "Conference start date is in the past"
    
    # Check if start is before end
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    # Check reasonable duration (not more than 30 days)
    if (end_date - start_date).days > 30:
        return False, "Conference duration too long (>30 days)"
    
    return True, "Valid date range"

# Example usage
result = validate_conference_dates("2024-03-15", "2024-03-18")
print(result)
```

### Scheduling and Deadlines
```python
from datetime import datetime, timedelta

class ConferenceSchedule:
    def __init__(self, conference_start):
        self.conference_start = conference_start
        
    def get_deadlines(self):
        """Calculate important deadlines based on conference start"""
        deadlines = {}
        
        # Abstract submission deadline (6 months before)
        deadlines['abstract_deadline'] = self.conference_start - timedelta(days=180)
        
        # Full paper deadline (4 months before)  
        deadlines['paper_deadline'] = self.conference_start - timedelta(days=120)
        
        # Early registration (2 months before)
        deadlines['early_registration'] = self.conference_start - timedelta(days=60)
        
        # Regular registration (2 weeks before)
        deadlines['regular_registration'] = self.conference_start - timedelta(days=14)
        
        return deadlines

# Example
conference_start = datetime(2024, 6, 15)
schedule = ConferenceSchedule(conference_start)
deadlines = schedule.get_deadlines()

for deadline_type, deadline_date in deadlines.items():
    print(f"{deadline_type}: {deadline_date.strftime('%B %d, %Y')}")
```

### Log Timestamp Processing
```python
from datetime import datetime
import re

def parse_log_timestamp(log_line):
    """Extract and parse timestamps from log files"""
    # Common log timestamp patterns
    patterns = [
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', "%Y-%m-%d %H:%M:%S"),
        (r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}', "%d/%b/%Y:%H:%M:%S"),
        (r'\w{3} \d{2} \d{2}:\d{2}:\d{2}', "%b %d %H:%M:%S"),
    ]
    
    for pattern, fmt in patterns:
        match = re.search(pattern, log_line)
        if match:
            timestamp_str = match.group()
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
    
    return None

# Example log lines
log_lines = [
    "2023-12-25 14:30:45 INFO: Processing started",
    "25/Dec/2023:14:30:45 +0000 GET /api/data",
    "Dec 25 14:30:45 server: Connection established"
]

for log in log_lines:
    timestamp = parse_log_timestamp(log)
    if timestamp:
        print(f"Found timestamp: {timestamp}")
```

## Working with Time Intervals

### Creating Time Intervals
```python
from datetime import timedelta

# Different ways to create timedeltas
delta1 = timedelta(days=7)
delta2 = timedelta(hours=3, minutes=30)
delta3 = timedelta(weeks=2, days=3, hours=12)
delta4 = timedelta(seconds=3600)  # 1 hour

# From string (custom function)
def parse_duration(duration_str):
    """Parse duration strings like '2h 30m' or '1d 3h'"""
    import re
    
    total_seconds = 0
    
    # Extract days, hours, minutes, seconds
    patterns = {
        'days': r'(\d+)d',
        'hours': r'(\d+)h', 
        'minutes': r'(\d+)m',
        'seconds': r'(\d+)s'
    }
    
    multipliers = {
        'days': 86400,    # 24 * 60 * 60
        'hours': 3600,    # 60 * 60
        'minutes': 60,
        'seconds': 1
    }
    
    for unit, pattern in patterns.items():
        match = re.search(pattern, duration_str)
        if match:
            value = int(match.group(1))
            total_seconds += value * multipliers[unit]
    
    return timedelta(seconds=total_seconds)

# Examples
duration1 = parse_duration("2h 30m")  # 2 hours 30 minutes
duration2 = parse_duration("1d 3h")   # 1 day 3 hours
```

### Time Calculations
```python
from datetime import datetime, timedelta

# Conference session planning
session_start = datetime(2024, 6, 15, 9, 0)  # 9:00 AM
session_duration = timedelta(hours=1, minutes=30)  # 1.5 hours
break_duration = timedelta(minutes=15)  # 15 minutes

sessions = []
current_time = session_start

for i in range(4):  # 4 sessions
    session_end = current_time + session_duration
    sessions.append({
        'session': i + 1,
        'start': current_time.strftime("%H:%M"),
        'end': session_end.strftime("%H:%M")
    })
    
    # Next session starts after break
    current_time = session_end + break_duration

for session in sessions:
    print(f"Session {session['session']}: {session['start']} - {session['end']}")
```

## Best Practices

### Always Use Timezone-Aware Datetimes
```python
from datetime import datetime, timezone

# Good: timezone-aware
utc_now = datetime.now(timezone.utc)

# Less ideal: naive datetime
naive_now = datetime.now()

# Convert naive to timezone-aware
aware_now = naive_now.replace(tzinfo=timezone.utc)
```

### Store Dates in ISO Format
```python
from datetime import datetime

# Store dates as ISO strings for databases/JSON
dt = datetime.now()
iso_string = dt.isoformat()  # "2023-12-25T14:30:45.123456"

# Parse back from ISO string
parsed_dt = datetime.fromisoformat(iso_string)
```

### Handle Date Parsing Errors
```python
from datetime import datetime

def safe_parse_date(date_str, formats):
    """Safely parse date with multiple format attempts"""
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")

# Usage with error handling
formats = ["%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y"]
try:
    date_obj = safe_parse_date("2023-12-25", formats)
except ValueError as e:
    print(f"Date parsing failed: {e}")
```

### Performance Considerations
```python
from datetime import datetime

# Reuse format strings
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Instead of creating format string each time
dates = []
for date_str in date_strings:
    dt = datetime.strptime(date_str, DATE_FORMAT)
    dates.append(dt)

# Cache parsed dates if reused
date_cache = {}

def get_parsed_date(date_str):
    if date_str not in date_cache:
        date_cache[date_str] = datetime.strptime(date_str, DATE_FORMAT)
    return date_cache[date_str]
```

This documentation covers the essential datetime functionality needed for conference data processing, log parsing, and time-based operations in your conference crawler applications.