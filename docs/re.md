# Python re (Regular Expressions) Documentation

The `re` module provides regular expression matching operations similar to those found in Perl. Both patterns and strings to be searched can be Unicode strings as well as 8-bit strings.

## Basic Usage

### Importing and Basic Matching

```python
import re

# Basic pattern matching
pattern = r'\d+'  # Match one or more digits
text = "I have 5 apples and 12 oranges"

# Find first match
match = re.search(pattern, text)
if match:
    print(match.group())  # Output: '5'

# Find all matches
matches = re.findall(pattern, text)
print(matches)  # Output: ['5', '12']
```

### Common Functions

#### re.search()
Find the first occurrence of pattern in string.

```python
import re

text = "The price is $25.99"
match = re.search(r'\$(\d+\.\d+)', text)
if match:
    print(match.group(0))  # Full match: '$25.99'
    print(match.group(1))  # First group: '25.99'
```

#### re.match()
Check if pattern matches at the beginning of string.

```python
# Only matches at start of string
pattern = r'\d+'
print(re.match(pattern, "123abc"))    # Match object
print(re.match(pattern, "abc123"))    # None
```

#### re.findall()
Return all non-overlapping matches as a list.

```python
text = "Contact: john@email.com or mary@company.org"
emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
print(emails)  # ['john@email.com', 'mary@company.org']
```

#### re.finditer()
Return an iterator of match objects.

```python
text = "Error at line 10, Error at line 25"
for match in re.finditer(r'line (\d+)', text):
    print(f"Found at position {match.start()}: line {match.group(1)}")
```

#### re.sub()
Replace occurrences of pattern.

```python
text = "The date is 2023-12-25"
# Replace date format
new_text = re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\2/\3/\1', text)
print(new_text)  # "The date is 12/25/2023"

# Using a function for replacement
def format_date(match):
    year, month, day = match.groups()
    return f"{month}/{day}/{year}"

new_text = re.sub(r'(\d{4})-(\d{2})-(\d{2})', format_date, text)
```

#### re.split()
Split string by pattern.

```python
text = "apple,banana;cherry:date"
fruits = re.split(r'[,;:]', text)
print(fruits)  # ['apple', 'banana', 'cherry', 'date']

# Limit number of splits
limited = re.split(r'[,;:]', text, maxsplit=2)
print(limited)  # ['apple', 'banana', 'cherry:date']
```

## Pattern Syntax

### Basic Characters
```python
# Literal characters
re.search(r'hello', "hello world")  # Matches 'hello'

# Escape special characters
re.search(r'\$\d+', "$50")  # Matches '$50'
```

### Character Classes
```python
# Predefined character classes
r'\d'    # Digit [0-9]
r'\D'    # Non-digit [^0-9]
r'\w'    # Word character [a-zA-Z0-9_]
r'\W'    # Non-word character [^a-zA-Z0-9_]
r'\s'    # Whitespace [ \t\n\r\f\v]
r'\S'    # Non-whitespace [^ \t\n\r\f\v]

# Custom character classes
r'[abc]'      # Any of a, b, or c
r'[a-z]'      # Any lowercase letter
r'[A-Z0-9]'   # Any uppercase letter or digit
r'[^0-9]'     # Any character except digits

# Examples
text = "Phone: 123-456-7890"
phone = re.search(r'\d{3}-\d{3}-\d{4}', text)
```

### Quantifiers
```python
r'a?'     # 0 or 1 'a'
r'a*'     # 0 or more 'a's
r'a+'     # 1 or more 'a's
r'a{3}'   # Exactly 3 'a's
r'a{2,4}' # Between 2 and 4 'a's
r'a{2,}'  # 2 or more 'a's

# Non-greedy quantifiers
r'a*?'    # 0 or more 'a's (non-greedy)
r'a+?'    # 1 or more 'a's (non-greedy)

# Examples
html = "<tag>content</tag>"
# Greedy: matches entire string
match = re.search(r'<.*>', html)

# Non-greedy: matches just the first tag
match = re.search(r'<.*?>', html)
```

### Anchors and Boundaries
```python
r'^'      # Start of string
r'$'      # End of string
r'\b'     # Word boundary
r'\B'     # Non-word boundary

# Examples
text = "The cat sat on the mat"
# Find 'cat' as whole word only
match = re.search(r'\bcat\b', text)

# Find words starting with 'th'
matches = re.findall(r'\bth\w*', text, re.IGNORECASE)
print(matches)  # ['The', 'the']
```

## Groups and Capturing

### Basic Groups
```python
# Parentheses create groups
pattern = r'(\d{4})-(\d{2})-(\d{2})'
text = "Today is 2023-12-25"

match = re.search(pattern, text)
if match:
    print(match.group(0))  # Full match: '2023-12-25'
    print(match.group(1))  # First group: '2023'
    print(match.group(2))  # Second group: '12'
    print(match.group(3))  # Third group: '25'
    print(match.groups()) # All groups: ('2023', '12', '25')
```

### Named Groups
```python
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
text = "Today is 2023-12-25"

match = re.search(pattern, text)
if match:
    print(match.group('year'))   # '2023'
    print(match.group('month'))  # '12'
    print(match.group('day'))    # '25'
    print(match.groupdict())     # {'year': '2023', 'month': '12', 'day': '25'}
```

### Non-capturing Groups
```python
# (?:...) creates a non-capturing group
pattern = r'(?:Mr|Ms|Dr)\. (\w+)'
text = "Hello Dr. Smith"

match = re.search(pattern, text)
if match:
    print(match.group(1))  # 'Smith' (only captured group)
```

## Flags and Modifiers

### Common Flags
```python
import re

text = "Hello WORLD"

# Case insensitive
re.search(r'hello', text, re.IGNORECASE)  # or re.I

# Multiline mode (^ and $ match line boundaries)
multiline_text = """Line 1
Line 2
Line 3"""
re.findall(r'^Line', multiline_text, re.MULTILINE)  # or re.M

# Dot matches newlines
re.search(r'Line.*Line', multiline_text, re.DOTALL)  # or re.S

# Verbose mode (allows comments and whitespace)
pattern = re.compile(r'''
    \d{3}     # Area code
    -         # Separator
    \d{3}     # First three digits
    -         # Separator
    \d{4}     # Last four digits
''', re.VERBOSE)  # or re.X

# Combine flags
re.search(r'hello', text, re.IGNORECASE | re.MULTILINE)
```

## Compiled Patterns

### Using re.compile()
```python
# Compile pattern for reuse
pattern = re.compile(r'\b\w+@\w+\.\w+\b')

text1 = "Contact john@email.com"
text2 = "Email mary@company.org"

# Reuse compiled pattern
match1 = pattern.search(text1)
match2 = pattern.search(text2)

# All methods available on compiled patterns
emails = pattern.findall("Send to john@email.com and mary@company.org")
```

### Performance Benefits
```python
import re
import time

pattern_string = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
compiled_pattern = re.compile(pattern_string)

text = "Contact john@email.com or mary@company.org" * 10000

# Without compilation (slower for repeated use)
start = time.time()
for _ in range(1000):
    re.findall(pattern_string, text)
print(f"Without compilation: {time.time() - start:.3f}s")

# With compilation (faster for repeated use)
start = time.time()
for _ in range(1000):
    compiled_pattern.findall(text)
print(f"With compilation: {time.time() - start:.3f}s")
```

## Advanced Patterns

### Lookahead and Lookbehind
```python
# Positive lookahead (?=...)
# Find 'test' followed by 'ing'
text = "testing, tested, test"
matches = re.findall(r'test(?=ing)', text)  # ['test']

# Negative lookahead (?!...)
# Find 'test' NOT followed by 'ing'
matches = re.findall(r'test(?!ing)', text)  # ['test', 'test']

# Positive lookbehind (?<=...)
# Find numbers preceded by '$'
text = "Price $25, Quantity 10"
matches = re.findall(r'(?<=\$)\d+', text)  # ['25']

# Negative lookbehind (?<!...)
# Find numbers NOT preceded by '$'
matches = re.findall(r'(?<!\$)\d+', text)  # ['10']
```

### Backreferences
```python
# Find repeated words
text = "This is is a test test"
matches = re.findall(r'\b(\w+)\s+\1\b', text)  # ['is', 'test']

# Find matching quotes
text = 'He said "Hello" and then "Goodbye"'
matches = re.findall(r'(["\']).*?\1', text)  # ['"', '"']
```

## Common Use Cases

### Email Validation
```python
def validate_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return re.match(pattern, email) is not None

print(validate_email("user@example.com"))  # True
print(validate_email("invalid.email"))     # False
```

### Phone Number Extraction
```python
def extract_phone_numbers(text):
    # Various phone number formats
    patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',        # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\.\d{3}\.\d{4}\b',      # 123.456.7890
    ]
    
    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))
    
    return phones

text = "Call 123-456-7890 or (555) 123-4567"
print(extract_phone_numbers(text))
```

### URL Extraction
```python
def extract_urls(text):
    pattern = r'https?://(?:[-\w.])+(?::\d+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(pattern, text)

text = "Visit https://example.com or http://test.org:8080/path?param=value"
print(extract_urls(text))
```

### Data Cleaning
```python
def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-alphanumeric except spaces and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)
    
    # Remove multiple punctuation
    text = re.sub(r'[.,!?]{2,}', '.', text)
    
    return text.strip()

messy_text = "Hello!!!   This    is   a   messy   text...   "
print(clean_text(messy_text))  # "Hello. This is a messy text."
```

### Log Parsing
```python
def parse_log_entry(log_line):
    # Parse Apache log format
    pattern = r'(\S+) \S+ \S+ \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+|-)'
    match = re.match(pattern, log_line)
    
    if match:
        return {
            'ip': match.group(1),
            'timestamp': match.group(2),
            'method': match.group(3),
            'url': match.group(4),
            'protocol': match.group(5),
            'status': int(match.group(6)),
            'size': int(match.group(7)) if match.group(7) != '-' else 0
        }
    return None

log_line = '192.168.1.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
parsed = parse_log_entry(log_line)
print(parsed)
```

### Configuration File Parsing
```python
def parse_config(config_text):
    config = {}
    
    # Match key = value pairs
    pattern = r'^\s*([^#\s][^=]*?)\s*=\s*(.*?)\s*$'
    
    for line in config_text.split('\n'):
        match = re.match(pattern, line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Remove quotes if present
            value = re.sub(r'^["\']|["\']$', '', value)
            
            config[key] = value
    
    return config

config_text = """
# Database settings
host = "localhost"
port = 5432
username = admin
# Connection timeout
timeout = 30
"""

config = parse_config(config_text)
print(config)  # {'host': 'localhost', 'port': '5432', 'username': 'admin', 'timeout': '30'}
```

## Error Handling

### Common Exceptions
```python
import re

try:
    # Invalid regex pattern
    re.compile(r'[')  # Missing closing bracket
except re.error as e:
    print(f"Regex error: {e}")

try:
    # Invalid group reference
    match = re.search(r'(\d+)', "123")
    print(match.group(2))  # Group 2 doesn't exist
except IndexError as e:
    print(f"Group error: {e}")
```

### Validating Patterns
```python
def is_valid_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

print(is_valid_regex(r'\d+'))    # True
print(is_valid_regex(r'['))      # False
```

## Best Practices

### Pattern Organization
```python
# Use raw strings for regex patterns
pattern = r'\d+'  # Good
pattern = '\\d+'  # Works but less readable

# Compile patterns used multiple times
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def find_emails(text):
    return EMAIL_PATTERN.findall(text)
```

### Readability
```python
# Use verbose mode for complex patterns
PHONE_PATTERN = re.compile(r'''
    (?:                 # Non-capturing group for area code
        \((\d{3})\)     # Area code in parentheses
        \s*             # Optional whitespace
    |                   # OR
        (\d{3})         # Area code without parentheses
        [-.]?           # Optional separator
    )
    (\d{3})             # First three digits
    [-.]?               # Optional separator
    (\d{4})             # Last four digits
''', re.VERBOSE)
```

### Performance Considerations
```python
# Avoid catastrophic backtracking
# Bad: can cause exponential time complexity
bad_pattern = r'(a+)+b'

# Good: more specific matching
good_pattern = r'a+b'

# Use non-capturing groups when you don't need the match
# Less efficient
pattern = r'(https?://)([^/]+)(.*)'

# More efficient if you don't need the protocol group
pattern = r'(?:https?://)([^/]+)(.*)'
```

This documentation covers the essential features of Python's `re` module for regular expression processing, which is crucial for text parsing and data extraction in your conference crawler applications.