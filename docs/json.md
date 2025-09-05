# Python json Module Documentation

The `json` module provides functionality for encoding and decoding JSON (JavaScript Object Notation) data. It's essential for working with APIs, configuration files, and data interchange in modern applications.

## Basic Usage

### Encoding Python Objects to JSON

```python
import json

# Basic data types
data = {
    'conference': 'ECCMID',
    'year': 2024,
    'active': True,
    'sessions': ['Morning', 'Afternoon', 'Evening'],
    'location': None,
    'metadata': {
        'created': '2024-01-01',
        'version': 1.0
    }
}

# Convert to JSON string
json_string = json.dumps(data)
print(json_string)

# Pretty-print JSON with indentation
json_pretty = json.dumps(data, indent=2)
print(json_pretty)

# Compact JSON (no extra whitespace)
json_compact = json.dumps(data, separators=(',', ':'))
print(json_compact)
```

### Decoding JSON to Python Objects

```python
import json

# JSON string
json_data = '''
{
    "conference": "ECCMID",
    "year": 2024,
    "active": true,
    "sessions": ["Morning", "Afternoon", "Evening"],
    "location": null,
    "metadata": {
        "created": "2024-01-01",
        "version": 1.0
    }
}
'''

# Parse JSON string
data = json.loads(json_data)
print(f"Conference: {data['conference']}")
print(f"Year: {data['year']}")
print(f"Sessions: {data['sessions']}")

# Access nested data
print(f"Created: {data['metadata']['created']}")
```

## File Operations

### Reading from JSON Files

```python
import json

# Read JSON from file
try:
    with open('conference_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded data: {data}")
    
except FileNotFoundError:
    print("JSON file not found")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

### Writing to JSON Files

```python
import json

data = {
    'conference': 'ECCMID',
    'year': 2024,
    'sessions': [
        {'id': 1, 'title': 'Opening Session', 'time': '09:00'},
        {'id': 2, 'title': 'Research Updates', 'time': '10:30'}
    ]
}

# Write JSON to file
with open('conference_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Append to existing JSON array (requires special handling)
def append_to_json_array(filename, new_item):
    """Safely append item to JSON array file"""
    try:
        # Read existing data
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Ensure data is a list
    if not isinstance(data, list):
        data = [data]
    
    # Append new item
    data.append(new_item)
    
    # Write back to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Usage
new_session = {'id': 3, 'title': 'Panel Discussion', 'time': '14:00'}
append_to_json_array('sessions.json', new_session)
```

## JSON Encoding Options

### Formatting and Pretty Printing

```python
import json

data = {
    'conferences': ['ECCMID', 'IDWeek', 'ESCMID'],
    'years': [2022, 2023, 2024],
    'details': {
        'location': 'Multiple Cities',
        'format': 'Hybrid'
    }
}

# Different indentation levels
print("Indent 2:")
print(json.dumps(data, indent=2))

print("\nIndent 4:")
print(json.dumps(data, indent=4))

# Custom separators
print("\nCustom separators:")
print(json.dumps(data, indent=2, separators=(' | ', ' = ')))

# Sort keys alphabetically
print("\nSorted keys:")
print(json.dumps(data, indent=2, sort_keys=True))

# Ensure ASCII output (escape non-ASCII characters)
unicode_data = {'name': 'Médecine', 'emoji': '🔬'}
print("\nASCII output:")
print(json.dumps(unicode_data, ensure_ascii=True))

print("\nUnicode output:")
print(json.dumps(unicode_data, ensure_ascii=False))
```

### Handling Special Data Types

```python
import json
from datetime import datetime, date
from decimal import Decimal

# Custom JSON encoder for special types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            # Handle custom objects
            return obj.__dict__
        
        # Let the base class handle other types
        return super().default(obj)

# Example data with special types
data = {
    'conference_date': datetime(2024, 3, 15, 9, 0, 0),
    'end_date': date(2024, 3, 18),
    'registration_fee': Decimal('150.50'),
    'topics': {'AI', 'ML', 'Bioinformatics'},
    'timestamp': datetime.now()
}

# Encode with custom encoder
json_string = json.dumps(data, cls=CustomJSONEncoder, indent=2)
print(json_string)

# Alternative: using default parameter
def json_serial(obj):
    """JSON serializer for objects not serializable by default"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    
    raise TypeError(f"Type {type(obj)} not serializable")

json_string = json.dumps(data, default=json_serial, indent=2)
print(json_string)
```

## JSON Decoding Options

### Custom Object Hooks

```python
import json
from datetime import datetime, date

def custom_object_hook(obj):
    """Custom object hook for JSON decoding"""
    # Convert ISO date strings back to datetime objects
    for key, value in obj.items():
        if isinstance(value, str):
            # Try to parse as datetime
            try:
                if 'T' in value and value.endswith('Z') or '+' in value:
                    obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                elif len(value) == 10 and value.count('-') == 2:
                    obj[key] = date.fromisoformat(value)
            except ValueError:
                pass  # Not a date string
    
    return obj

# JSON data with date strings
json_data = '''
{
    "conference": "ECCMID",
    "start_date": "2024-03-15",
    "registration_deadline": "2024-02-01T23:59:59+00:00",
    "sessions": [
        {"title": "Opening", "datetime": "2024-03-15T09:00:00+00:00"}
    ]
}
'''

# Parse with custom object hook
data = json.loads(json_data, object_hook=custom_object_hook)

print(f"Start date type: {type(data['start_date'])}")
print(f"Registration deadline type: {type(data['registration_deadline'])}")
print(f"Session datetime type: {type(data['sessions'][0]['datetime'])}")
```

### Parse Floats and Integers with Custom Types

```python
import json
from decimal import Decimal

# Parse JSON with Decimal for precise decimal handling
def parse_decimal(obj):
    """Parse float strings as Decimal objects"""
    return Decimal(obj)

def parse_int(obj):
    """Custom integer parsing"""
    return int(obj)

json_data = '{"price": "150.50", "year": "2024", "discount": "10.25"}'

# Parse with custom number handling
data = json.loads(
    json_data,
    parse_float=parse_decimal,
    parse_int=parse_int
)

print(f"Price: {data['price']} (type: {type(data['price'])})")
print(f"Year: {data['year']} (type: {type(data['year'])})")
print(f"Discount: {data['discount']} (type: {type(data['discount'])})")
```

## Error Handling

### JSON Decoding Errors

```python
import json

def safe_json_loads(json_string):
    """Safely load JSON with error handling"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Error at line {e.lineno}, column {e.colno}")
        print(f"Error message: {e.msg}")
        return None

# Examples of invalid JSON
invalid_jsons = [
    '{"missing_quote: "value"}',  # Missing quote
    '{"trailing_comma": "value",}',  # Trailing comma
    '{"invalid": undefined}',  # Invalid value
    '{invalid_key: "value"}',  # Unquoted key
    '{"unclosed": "value"'  # Unclosed brace
]

for i, invalid_json in enumerate(invalid_jsons, 1):
    print(f"\nTesting invalid JSON {i}:")
    print(f"Input: {invalid_json}")
    result = safe_json_loads(invalid_json)
    print(f"Result: {result}")
```

### File Operations with Error Handling

```python
import json
import os

def safe_load_json(filename, default=None):
    """Safely load JSON file with error handling"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return default
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {filename}: {e}")
        return default
    except IOError as e:
        print(f"I/O error reading {filename}: {e}")
        return default

def safe_save_json(data, filename, backup=True):
    """Safely save JSON file with optional backup"""
    
    # Create backup if file exists
    if backup and os.path.exists(filename):
        backup_filename = f"{filename}.backup"
        try:
            os.rename(filename, backup_filename)
            print(f"Created backup: {backup_filename}")
        except OSError as e:
            print(f"Could not create backup: {e}")
            return False
    
    try:
        # Write to temporary file first
        temp_filename = f"{filename}.tmp"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic move to final location
        os.rename(temp_filename, filename)
        print(f"Successfully saved: {filename}")
        return True
        
    except (IOError, OSError) as e:
        print(f"Error saving {filename}: {e}")
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        return False

# Usage examples
data = safe_load_json('config.json', default={'default': 'config'})
success = safe_save_json({'new': 'data'}, 'output.json')
```

## Conference Data Processing Examples

### Session Data Processing

```python
import json
from datetime import datetime, timedelta

def process_conference_sessions(raw_data_file, output_file):
    """Process raw conference session data into structured JSON"""
    
    # Load raw data
    with open(raw_data_file, 'r') as f:
        raw_sessions = json.load(f)
    
    processed_sessions = []
    
    for session in raw_sessions:
        processed_session = {
            'id': session.get('id'),
            'title': session.get('title', '').strip(),
            'abstract': session.get('abstract', '').strip(),
            'speakers': [
                {
                    'name': speaker.get('name', '').strip(),
                    'affiliation': speaker.get('affiliation', '').strip(),
                    'email': speaker.get('email', '').lower() if speaker.get('email') else None
                }
                for speaker in session.get('speakers', [])
            ],
            'schedule': {
                'date': session.get('date'),
                'start_time': session.get('start_time'),
                'end_time': session.get('end_time'),
                'duration_minutes': calculate_duration(
                    session.get('start_time'), 
                    session.get('end_time')
                )
            },
            'location': {
                'room': session.get('room', '').strip(),
                'building': session.get('building', '').strip(),
                'capacity': session.get('capacity')
            },
            'categories': session.get('categories', []),
            'keywords': [kw.strip().lower() for kw in session.get('keywords', []) if kw.strip()],
            'status': session.get('status', 'scheduled'),
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source': 'conference_crawler',
                'version': '1.0'
            }
        }
        
        # Validate required fields
        if processed_session['id'] and processed_session['title']:
            processed_sessions.append(processed_session)
    
    # Sort sessions by date and time
    processed_sessions.sort(key=lambda x: (x['schedule']['date'], x['schedule']['start_time']))
    
    # Save processed data
    output_data = {
        'conference': 'ECCMID 2024',
        'total_sessions': len(processed_sessions),
        'processing_date': datetime.now().isoformat(),
        'sessions': processed_sessions
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return len(processed_sessions)

def calculate_duration(start_time, end_time):
    """Calculate duration in minutes between start and end time"""
    if not start_time or not end_time:
        return None
    
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        
        if end < start:  # Next day
            end += timedelta(days=1)
        
        duration = end - start
        return int(duration.total_seconds() / 60)
    except ValueError:
        return None

# Usage
processed_count = process_conference_sessions('raw_sessions.json', 'processed_sessions.json')
print(f"Processed {processed_count} sessions")
```

### API Response Handling

```python
import json
import requests
from datetime import datetime

class ConferenceAPIClient:
    """Client for conference API with JSON handling"""
    
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_sessions(self, conference_id, year):
        """Get conference sessions"""
        url = f"{self.base_url}/conferences/{conference_id}/{year}/sessions"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Validate response structure
            if not isinstance(data, dict) or 'sessions' not in data:
                raise ValueError("Invalid response format")
            
            return self._process_sessions(data['sessions'])
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
            return None
        except ValueError as e:
            print(f"Response validation error: {e}")
            return None
    
    def create_session(self, session_data):
        """Create new conference session"""
        url = f"{self.base_url}/sessions"
        
        # Prepare JSON payload
        payload = {
            'title': session_data.get('title'),
            'abstract': session_data.get('abstract'),
            'speakers': session_data.get('speakers', []),
            'schedule': session_data.get('schedule', {}),
            'created_at': datetime.now().isoformat()
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload,  # Automatically encodes as JSON
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Create session failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
            return None
    
    def _process_sessions(self, sessions):
        """Process and validate session data"""
        processed = []
        
        for session in sessions:
            if not isinstance(session, dict):
                continue
            
            # Clean and validate session data
            processed_session = {
                'id': session.get('id'),
                'title': session.get('title', '').strip(),
                'speakers': self._process_speakers(session.get('speakers', [])),
                'schedule': self._process_schedule(session.get('schedule', {}))
            }
            
            if processed_session['id'] and processed_session['title']:
                processed.append(processed_session)
        
        return processed
    
    def _process_speakers(self, speakers):
        """Process speaker data"""
        processed = []
        
        for speaker in speakers:
            if isinstance(speaker, dict):
                processed_speaker = {
                    'name': speaker.get('name', '').strip(),
                    'affiliation': speaker.get('affiliation', '').strip(),
                    'bio': speaker.get('bio', '').strip()
                }
                
                if processed_speaker['name']:
                    processed.append(processed_speaker)
        
        return processed
    
    def _process_schedule(self, schedule):
        """Process schedule data"""
        if not isinstance(schedule, dict):
            return {}
        
        return {
            'date': schedule.get('date'),
            'start_time': schedule.get('start_time'),
            'end_time': schedule.get('end_time'),
            'room': schedule.get('room', '').strip()
        }

# Usage
client = ConferenceAPIClient('https://api.conference.com', api_key='your-api-key')

# Get sessions
sessions = client.get_sessions('eccmid', 2024)
if sessions:
    print(f"Retrieved {len(sessions)} sessions")

# Create new session
new_session = {
    'title': 'AI in Medical Research',
    'abstract': 'Discussion on AI applications...',
    'speakers': [
        {'name': 'Dr. Smith', 'affiliation': 'University Hospital'}
    ],
    'schedule': {
        'date': '2024-03-15',
        'start_time': '10:00',
        'end_time': '11:00',
        'room': 'Hall A'
    }
}

result = client.create_session(new_session)
if result:
    print(f"Created session with ID: {result.get('id')}")
```

### Configuration Management

```python
import json
import os
from typing import Dict, Any, Optional

class ConfigurationManager:
    """Manage JSON configuration files for conference processing"""
    
    def __init__(self, config_dir: str = './config'):
        self.config_dir = config_dir
        self.configs: Dict[str, Any] = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all JSON configuration files"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            self.create_default_configs()
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                config_name = filename[:-5]  # Remove .json extension
                self.load_config(config_name)
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific configuration file"""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.configs[config_name] = config
            print(f"Loaded config: {config_name}")
            return config
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config {config_name}: {e}")
            return None
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.configs[config_name] = config_data
            print(f"Saved config: {config_name}")
            return True
            
        except IOError as e:
            print(f"Error saving config {config_name}: {e}")
            return False
    
    def get_config(self, config_name: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        if config_name not in self.configs:
            return default
        
        config = self.configs[config_name]
        
        if key is None:
            return config
        
        # Support nested keys with dot notation
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config(self, config_name: str, key: str, value: Any) -> bool:
        """Set configuration value"""
        if config_name not in self.configs:
            self.configs[config_name] = {}
        
        config = self.configs[config_name]
        
        # Support nested keys with dot notation
        keys = key.split('.')
        current = config
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save to file
        return self.save_config(config_name, self.configs[config_name])
    
    def create_default_configs(self):
        """Create default configuration files"""
        
        # Database configuration
        database_config = {
            "host": "localhost",
            "port": 5432,
            "database": "conference_data",
            "username": "conference_user",
            "pool_size": 10,
            "timeout": 30
        }
        self.save_config('database', database_config)
        
        # Crawler configuration
        crawler_config = {
            "conferences": {
                "eccmid": {
                    "base_url": "https://eccmid.com",
                    "session_path": "/sessions",
                    "poster_path": "/posters"
                },
                "idweek": {
                    "base_url": "https://idweek.org",
                    "session_path": "/program/sessions",
                    "poster_path": "/program/posters"
                }
            },
            "request_settings": {
                "delay_seconds": 1.0,
                "timeout_seconds": 30,
                "max_retries": 3,
                "user_agent": "ConferenceCrawler/1.0"
            },
            "output_settings": {
                "formats": ["json", "csv"],
                "backup_enabled": True,
                "compression_enabled": False
            }
        }
        self.save_config('crawler', crawler_config)
        
        # Processing configuration
        processing_config = {
            "text_processing": {
                "clean_html": True,
                "normalize_whitespace": True,
                "extract_emails": True,
                "extract_affiliations": True
            },
            "data_validation": {
                "require_title": True,
                "require_abstract": False,
                "min_abstract_length": 50,
                "max_title_length": 200
            },
            "export_settings": {
                "include_metadata": True,
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M"
            }
        }
        self.save_config('processing', processing_config)

# Usage example
def main():
    """Example usage of configuration manager"""
    config_manager = ConfigurationManager()
    
    # Get configuration values
    db_host = config_manager.get_config('database', 'host', 'localhost')
    db_port = config_manager.get_config('database', 'port', 5432)
    
    print(f"Database: {db_host}:{db_port}")
    
    # Get nested configuration
    eccmid_url = config_manager.get_config('crawler', 'conferences.eccmid.base_url')
    request_delay = config_manager.get_config('crawler', 'request_settings.delay_seconds', 1.0)
    
    print(f"ECCMID URL: {eccmid_url}")
    print(f"Request delay: {request_delay}s")
    
    # Update configuration
    config_manager.set_config('crawler', 'request_settings.delay_seconds', 2.0)
    
    # Get entire configuration
    processing_config = config_manager.get_config('processing')
    print(f"Processing config keys: {list(processing_config.keys())}")

if __name__ == '__main__':
    main()
```

### Data Validation and Cleaning

```python
import json
import re
from datetime import datetime
from typing import List, Dict, Any

class ConferenceDataValidator:
    """Validate and clean conference data in JSON format"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Validation patterns
        self.email_pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
        self.time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        self.date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    def validate_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean session data"""
        cleaned_data = {}
        
        # Validate required fields
        cleaned_data['id'] = self._validate_id(session_data.get('id'))
        cleaned_data['title'] = self._validate_title(session_data.get('title'))
        cleaned_data['abstract'] = self._clean_text(session_data.get('abstract', ''))
        
        # Validate speakers
        cleaned_data['speakers'] = self._validate_speakers(session_data.get('speakers', []))
        
        # Validate schedule
        cleaned_data['schedule'] = self._validate_schedule(session_data.get('schedule', {}))
        
        # Validate location
        cleaned_data['location'] = self._validate_location(session_data.get('location', {}))
        
        # Clean categories and keywords
        cleaned_data['categories'] = self._clean_list(session_data.get('categories', []))
        cleaned_data['keywords'] = self._clean_keywords(session_data.get('keywords', []))
        
        # Validate metadata
        cleaned_data['metadata'] = self._validate_metadata(session_data.get('metadata', {}))
        
        return cleaned_data
    
    def _validate_id(self, session_id: Any) -> str:
        """Validate session ID"""
        if not session_id:
            self.errors.append("Missing session ID")
            return ""
        
        session_id = str(session_id).strip()
        
        if not session_id:
            self.errors.append("Empty session ID")
            return ""
        
        return session_id
    
    def _validate_title(self, title: Any) -> str:
        """Validate session title"""
        if not title:
            self.errors.append("Missing session title")
            return ""
        
        title = self._clean_text(str(title))
        
        if len(title) < 5:
            self.warnings.append(f"Very short title: '{title}'")
        elif len(title) > 200:
            self.warnings.append(f"Very long title: '{title[:50]}...'")
        
        return title
    
    def _validate_speakers(self, speakers: Any) -> List[Dict[str, str]]:
        """Validate speaker data"""
        if not isinstance(speakers, list):
            self.errors.append("Speakers must be a list")
            return []
        
        validated_speakers = []
        
        for i, speaker in enumerate(speakers):
            if not isinstance(speaker, dict):
                self.warnings.append(f"Speaker {i+1} is not a dictionary")
                continue
            
            cleaned_speaker = {
                'name': self._clean_text(speaker.get('name', '')),
                'affiliation': self._clean_text(speaker.get('affiliation', '')),
                'email': self._validate_email(speaker.get('email', '')),
                'bio': self._clean_text(speaker.get('bio', ''))
            }
            
            if cleaned_speaker['name']:
                validated_speakers.append(cleaned_speaker)
            else:
                self.warnings.append(f"Speaker {i+1} missing name")
        
        return validated_speakers
    
    def _validate_schedule(self, schedule: Any) -> Dict[str, str]:
        """Validate schedule data"""
        if not isinstance(schedule, dict):
            self.errors.append("Schedule must be a dictionary")
            return {}
        
        cleaned_schedule = {}
        
        # Validate date
        date_str = schedule.get('date', '')
        if date_str and self.date_pattern.match(str(date_str)):
            cleaned_schedule['date'] = str(date_str)
        elif date_str:
            self.warnings.append(f"Invalid date format: {date_str}")
        
        # Validate times
        for time_field in ['start_time', 'end_time']:
            time_str = schedule.get(time_field, '')
            if time_str and self.time_pattern.match(str(time_str)):
                cleaned_schedule[time_field] = str(time_str)
            elif time_str:
                self.warnings.append(f"Invalid {time_field} format: {time_str}")
        
        # Validate duration
        duration = schedule.get('duration_minutes')
        if duration is not None:
            try:
                duration_int = int(duration)
                if 0 < duration_int <= 480:  # Max 8 hours
                    cleaned_schedule['duration_minutes'] = duration_int
                else:
                    self.warnings.append(f"Unusual duration: {duration_int} minutes")
            except ValueError:
                self.warnings.append(f"Invalid duration: {duration}")
        
        return cleaned_schedule
    
    def _validate_location(self, location: Any) -> Dict[str, str]:
        """Validate location data"""
        if not isinstance(location, dict):
            return {}
        
        return {
            'room': self._clean_text(location.get('room', '')),
            'building': self._clean_text(location.get('building', '')),
            'address': self._clean_text(location.get('address', ''))
        }
    
    def _validate_email(self, email: Any) -> str:
        """Validate email address"""
        if not email:
            return ""
        
        email = str(email).strip().lower()
        
        if self.email_pattern.match(email):
            return email
        else:
            self.warnings.append(f"Invalid email format: {email}")
            return ""
    
    def _validate_metadata(self, metadata: Any) -> Dict[str, Any]:
        """Validate metadata"""
        if not isinstance(metadata, dict):
            return {
                'validated_at': datetime.now().isoformat(),
                'validator_version': '1.0'
            }
        
        cleaned_metadata = dict(metadata)
        cleaned_metadata['validated_at'] = datetime.now().isoformat()
        cleaned_metadata['validator_version'] = '1.0'
        
        return cleaned_metadata
    
    def _clean_text(self, text: Any) -> str:
        """Clean text content"""
        if not text:
            return ""
        
        text = str(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove HTML tags (basic)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode common HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        return text
    
    def _clean_list(self, items: Any) -> List[str]:
        """Clean list of strings"""
        if not isinstance(items, list):
            return []
        
        cleaned_items = []
        
        for item in items:
            if item:
                cleaned_item = self._clean_text(item)
                if cleaned_item and cleaned_item not in cleaned_items:
                    cleaned_items.append(cleaned_item)
        
        return cleaned_items
    
    def _clean_keywords(self, keywords: Any) -> List[str]:
        """Clean and normalize keywords"""
        cleaned_keywords = self._clean_list(keywords)
        
        # Convert to lowercase and sort
        cleaned_keywords = sorted(set(kw.lower() for kw in cleaned_keywords))
        
        return cleaned_keywords
    
    def validate_json_file(self, input_file: str, output_file: str) -> Dict[str, int]:
        """Validate entire JSON file"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.errors.append(f"Cannot load JSON file: {e}")
            return {'processed': 0, 'errors': len(self.errors), 'warnings': len(self.warnings)}
        
        if isinstance(data, dict) and 'sessions' in data:
            sessions = data['sessions']
        elif isinstance(data, list):
            sessions = data
        else:
            self.errors.append("Invalid JSON structure: expected sessions array or object with sessions key")
            return {'processed': 0, 'errors': len(self.errors), 'warnings': len(self.warnings)}
        
        validated_sessions = []
        
        for i, session in enumerate(sessions):
            print(f"Validating session {i+1}/{len(sessions)}")
            
            try:
                validated_session = self.validate_session_data(session)
                validated_sessions.append(validated_session)
            except Exception as e:
                self.errors.append(f"Error validating session {i+1}: {e}")
        
        # Save validated data
        output_data = {
            'conference': data.get('conference', 'Unknown') if isinstance(data, dict) else 'Unknown',
            'validation_date': datetime.now().isoformat(),
            'total_sessions': len(validated_sessions),
            'validation_summary': {
                'errors': len(self.errors),
                'warnings': len(self.warnings)
            },
            'sessions': validated_sessions
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.errors.append(f"Cannot save validated data: {e}")
        
        # Print summary
        print(f"\nValidation complete:")
        print(f"Processed: {len(validated_sessions)} sessions")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        return {
            'processed': len(validated_sessions),
            'errors': len(self.errors),
            'warnings': len(self.warnings)
        }

# Usage
validator = ConferenceDataValidator()
results = validator.validate_json_file('raw_sessions.json', 'validated_sessions.json')
```

## Best Practices

### Performance Optimization

```python
import json
from io import StringIO

def efficient_json_processing():
    """Examples of efficient JSON processing"""
    
    # Use json.dumps with separators for compact output
    data = {'key': 'value', 'numbers': [1, 2, 3]}
    compact_json = json.dumps(data, separators=(',', ':'))
    
    # Use StringIO for in-memory JSON operations
    json_buffer = StringIO()
    json.dump(data, json_buffer)
    json_string = json_buffer.getvalue()
    
    # Parse large JSON files incrementally (for very large files)
    def parse_large_json_stream(file_path):
        """Parse large JSON files line by line (JSONL format)"""
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    yield json.loads(line.strip())
                except json.JSONDecodeError:
                    continue  # Skip invalid lines
    
    # Use object_hook for efficient parsing of known structures
    def efficient_datetime_hook(obj):
        """Efficient datetime parsing"""
        for key, value in obj.items():
            if key.endswith('_at') and isinstance(value, str):
                try:
                    from datetime import datetime
                    obj[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
        return obj
```

### Security Considerations

```python
import json

def secure_json_handling():
    """Examples of secure JSON handling"""
    
    def safe_json_loads(json_string, max_size=1024*1024):  # 1MB limit
        """Safely load JSON with size limit"""
        if len(json_string) > max_size:
            raise ValueError(f"JSON string too large: {len(json_string)} bytes")
        
        return json.loads(json_string)
    
    def validate_json_structure(data, expected_keys):
        """Validate JSON structure against expected keys"""
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
        
        missing_keys = set(expected_keys) - set(data.keys())
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        return data
    
    def sanitize_json_output(data):
        """Remove sensitive information from JSON output"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = sanitize_json_output(value)
            return sanitized
        elif isinstance(data, list):
            return [sanitize_json_output(item) for item in data]
        else:
            return data
    
    # Example usage
    user_data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'secret123',
        'api_key': 'abc123def456'
    }
    
    safe_data = sanitize_json_output(user_data)
    print(json.dumps(safe_data, indent=2))
```

This documentation covers the essential features of Python's `json` module for working with JSON data - crucial for API interactions, configuration management, and data interchange in conference data processing applications.