# Python csv Module Documentation

The `csv` module provides functionality to read from and write to CSV (Comma-Separated Values) files. It handles the complexities of CSV format including proper escaping, quoting, and different dialects.

## Basic Usage

### Reading CSV Files

```python
import csv

# Basic reading
with open('data.csv', 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        print(row)  # Each row is a list

# Reading with headers
with open('data.csv', 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    headers = next(csv_reader)  # Read first row as headers
    for row in csv_reader:
        print(dict(zip(headers, row)))
```

### Writing CSV Files

```python
import csv

# Basic writing
data = [
    ['Name', 'Age', 'City'],
    ['John', '30', 'New York'],
    ['Jane', '25', 'Los Angeles']
]

with open('output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(data)

# Writing individual rows
with open('output.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Name', 'Age', 'City'])  # Header
    csv_writer.writerow(['John', '30', 'New York'])
    csv_writer.writerow(['Jane', '25', 'Los Angeles'])
```

## DictReader and DictWriter

### Reading with DictReader

```python
import csv

# Read CSV as dictionaries
with open('data.csv', 'r', newline='') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    
    # Print headers
    print(csv_reader.fieldnames)
    
    # Read each row as a dictionary
    for row in csv_reader:
        print(row['Name'], row['Age'], row['City'])

# Custom field names
with open('data.csv', 'r', newline='') as csvfile:
    csv_reader = csv.DictReader(
        csvfile, 
        fieldnames=['name', 'age', 'location']
    )
    next(csv_reader)  # Skip header row if present
    
    for row in csv_reader:
        print(row['name'], row['age'], row['location'])
```

### Writing with DictWriter

```python
import csv

# Write CSV from dictionaries
data = [
    {'Name': 'John', 'Age': '30', 'City': 'New York'},
    {'Name': 'Jane', 'Age': '25', 'City': 'Los Angeles'},
    {'Name': 'Bob', 'Age': '35', 'City': 'Chicago'}
]

with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['Name', 'Age', 'City']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    csv_writer.writeheader()  # Write header row
    csv_writer.writerows(data)  # Write all rows
    
    # Or write individual rows
    # for row in data:
    #     csv_writer.writerow(row)
```

## CSV Dialects and Formatting

### Built-in Dialects

```python
import csv

# Excel dialect (default)
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile, dialect='excel')
    for row in reader:
        print(row)

# Excel tab-delimited
with open('data.tsv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile, dialect='excel-tab')
    for row in reader:
        print(row)

# Unix dialect
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile, dialect='unix')
    for row in reader:
        print(row)
```

### Custom Dialects

```python
import csv

# Register custom dialect
csv.register_dialect('pipes', delimiter='|', quoting=csv.QUOTE_ALL)

# Use custom dialect
with open('pipe_data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile, dialect='pipes')
    for row in reader:
        print(row)

# Custom dialect class
class CustomDialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = True
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

# Register and use
csv.register_dialect('custom', CustomDialect)
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile, dialect='custom')
    for row in reader:
        print(row)
```

## Advanced Parameters

### Reader/Writer Parameters

```python
import csv

# Custom delimiter and quoting
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(
        csvfile,
        delimiter=';',          # Field separator
        quotechar='"',          # Quote character
        doublequote=True,       # Handle doubled quotes
        skipinitialspace=True,  # Skip whitespace after delimiter
        lineterminator='\n'     # Line terminator
    )
    for row in reader:
        print(row)

# Quoting options
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(
        csvfile,
        quoting=csv.QUOTE_ALL        # Quote all fields
        # quoting=csv.QUOTE_MINIMAL  # Quote only when necessary
        # quoting=csv.QUOTE_NONNUMERIC  # Quote non-numeric fields
        # quoting=csv.QUOTE_NONE     # Never quote
    )
    writer.writerow(['Name', 'Age', 'Description'])
    writer.writerow(['John Doe', 30, 'Software Engineer'])
```

### Escaping and Special Characters

```python
import csv

# Handle special characters
data_with_special_chars = [
    ['Name', 'Description'],
    ['John "Johnny" Doe', 'Says: "Hello, World!"'],
    ['Jane\nSmith', 'Multi\nline\ndescription'],
    ['Bob,Jr.', 'Name contains, comma']
]

with open('special_chars.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerows(data_with_special_chars)

# Read back
with open('special_chars.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(repr(row))  # Use repr to see escape characters
```

## Error Handling

### Common CSV Errors

```python
import csv

def safe_csv_read(filename):
    """Safely read CSV with error handling"""
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Detect dialect
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = 'excel'  # Fallback to default
            
            reader = csv.reader(csvfile, dialect=dialect)
            
            rows = []
            for line_num, row in enumerate(reader, 1):
                try:
                    # Validate row
                    if not row:  # Skip empty rows
                        continue
                    rows.append(row)
                    
                except csv.Error as e:
                    print(f"Error on line {line_num}: {e}")
                    continue
                    
            return rows
            
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return []
    except PermissionError:
        print(f"Permission denied: {filename}")
        return []
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        return []

# Usage
data = safe_csv_read('data.csv')
```

### Validation and Cleaning

```python
import csv
import re

def clean_csv_data(input_file, output_file, required_columns=None):
    """Clean and validate CSV data"""
    valid_rows = []
    errors = []
    
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Validate headers
        if required_columns:
            missing_cols = set(required_columns) - set(reader.fieldnames)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
        
        for line_num, row in enumerate(reader, 2):  # Start at 2 (after header)
            try:
                # Clean whitespace
                cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                
                # Validate data (example: email format)
                if 'email' in cleaned_row:
                    email = cleaned_row['email']
                    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                        errors.append(f"Line {line_num}: Invalid email format")
                        continue
                
                # Validate numeric fields (example: age)
                if 'age' in cleaned_row:
                    age = cleaned_row['age']
                    if age and not age.isdigit():
                        errors.append(f"Line {line_num}: Age must be numeric")
                        continue
                
                valid_rows.append(cleaned_row)
                
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
    
    # Write cleaned data
    if valid_rows:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(valid_rows)
    
    return len(valid_rows), errors

# Usage
valid_count, errors = clean_csv_data(
    'messy_data.csv', 
    'clean_data.csv',
    required_columns=['name', 'email']
)
print(f"Processed {valid_count} valid rows")
for error in errors:
    print(error)
```

## Working with Large CSV Files

### Memory-Efficient Processing

```python
import csv

def process_large_csv(filename, chunk_size=1000):
    """Process large CSV files in chunks"""
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        chunk = []
        for row in reader:
            chunk.append(row)
            
            if len(chunk) >= chunk_size:
                # Process chunk
                yield chunk
                chunk = []
        
        # Process remaining rows
        if chunk:
            yield chunk

# Usage
for chunk in process_large_csv('large_file.csv', chunk_size=500):
    # Process each chunk
    print(f"Processing chunk of {len(chunk)} rows")
    # Your processing logic here
```

### Streaming CSV Processing

```python
import csv
from collections import defaultdict

def analyze_csv_streaming(filename):
    """Analyze CSV data without loading everything into memory"""
    stats = {
        'total_rows': 0,
        'column_stats': defaultdict(lambda: {'count': 0, 'unique_values': set()})
    }
    
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            stats['total_rows'] += 1
            
            for column, value in row.items():
                if value:  # Skip empty values
                    col_stats = stats['column_stats'][column]
                    col_stats['count'] += 1
                    
                    # Only keep track of unique values for small sets
                    if len(col_stats['unique_values']) < 100:
                        col_stats['unique_values'].add(value)
    
    # Convert sets to counts for final output
    for column, col_stats in stats['column_stats'].items():
        col_stats['unique_count'] = len(col_stats['unique_values'])
        del col_stats['unique_values']  # Save memory
    
    return stats

# Usage
stats = analyze_csv_streaming('data.csv')
print(f"Total rows: {stats['total_rows']}")
for column, col_stats in stats['column_stats'].items():
    print(f"{column}: {col_stats['count']} values, {col_stats['unique_count']} unique")
```

## Conference Data Processing Examples

### Session Data Export

```python
import csv
from datetime import datetime

def export_session_data(sessions, filename):
    """Export conference session data to CSV"""
    fieldnames = [
        'session_id', 'title', 'date', 'start_time', 'end_time',
        'location', 'track', 'speakers', 'abstract', 'keywords'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for session in sessions:
            # Handle speaker list
            speakers = '; '.join(session.get('speakers', []))
            
            # Format datetime
            session_date = session.get('datetime', '')
            if isinstance(session_date, datetime):
                session_date = session_date.strftime('%Y-%m-%d')
            
            row = {
                'session_id': session.get('id', ''),
                'title': session.get('title', ''),
                'date': session_date,
                'start_time': session.get('start_time', ''),
                'end_time': session.get('end_time', ''),
                'location': session.get('location', ''),
                'track': session.get('track', ''),
                'speakers': speakers,
                'abstract': session.get('abstract', ''),
                'keywords': session.get('keywords', '')
            }
            
            writer.writerow(row)

# Usage
sessions = [
    {
        'id': 'S001',
        'title': 'Antimicrobial Resistance Trends',
        'date': datetime(2024, 3, 15),
        'start_time': '09:00',
        'end_time': '10:30',
        'location': 'Room A',
        'track': 'Clinical Research',
        'speakers': ['Dr. Smith', 'Dr. Johnson'],
        'abstract': 'Analysis of resistance patterns...',
        'keywords': 'AMR, surveillance'
    }
]

export_session_data(sessions, 'conference_sessions.csv')
```

### Poster Data Processing

```python
import csv
import re

def process_poster_csv(input_file, output_file):
    """Process poster data CSV with cleaning and standardization"""
    
    def clean_author_names(authors_str):
        """Clean and standardize author names"""
        if not authors_str:
            return []
        
        # Split by common delimiters
        authors = re.split(r'[,;]|\band\b', authors_str)
        
        cleaned_authors = []
        for author in authors:
            # Clean whitespace and common prefixes
            author = author.strip()
            author = re.sub(r'^(Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s+', '', author)
            
            if author:
                cleaned_authors.append(author)
        
        return cleaned_authors
    
    def extract_affiliations(text):
        """Extract affiliations from text"""
        # Common patterns for affiliations
        affiliation_patterns = [
            r'([A-Z][^,]+(?:University|Hospital|Institute|Center|Medical|Research))',
            r'(\d+[^,]+(?:University|Hospital|Institute|Center|Medical))',
        ]
        
        affiliations = []
        for pattern in affiliation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            affiliations.extend(matches)
        
        return list(set(affiliations))  # Remove duplicates
    
    processed_data = []
    
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Clean authors
            authors_list = clean_author_names(row.get('authors', ''))
            
            # Extract affiliations
            abstract_text = row.get('abstract', '')
            affiliations = extract_affiliations(abstract_text)
            
            processed_row = {
                'poster_id': row.get('poster_id', ''),
                'title': row.get('title', '').strip(),
                'authors': '; '.join(authors_list),
                'author_count': len(authors_list),
                'affiliations': '; '.join(affiliations),
                'abstract': abstract_text.strip(),
                'keywords': row.get('keywords', '').strip(),
                'session': row.get('session', '').strip(),
                'category': row.get('category', '').strip()
            }
            
            processed_data.append(processed_row)
    
    # Write processed data
    if processed_data:
        fieldnames = list(processed_data[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)
    
    return len(processed_data)

# Usage
processed_count = process_poster_csv('raw_posters.csv', 'processed_posters.csv')
print(f"Processed {processed_count} poster records")
```

### Data Merging and Deduplication

```python
import csv
from collections import defaultdict

def merge_conference_csvs(file_list, output_file, merge_key='title'):
    """Merge multiple conference CSV files and remove duplicates"""
    
    merged_data = {}
    all_fieldnames = set()
    
    for filename in file_list:
        print(f"Processing {filename}")
        
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            all_fieldnames.update(reader.fieldnames)
            
            for row in reader:
                key = row.get(merge_key, '').strip().lower()
                
                if key:  # Skip rows with empty merge key
                    if key in merged_data:
                        # Merge data (prefer non-empty values)
                        existing_row = merged_data[key]
                        for field, value in row.items():
                            if value and not existing_row.get(field):
                                existing_row[field] = value
                    else:
                        merged_data[key] = dict(row)
    
    # Write merged data
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(all_fieldnames))
        writer.writeheader()
        writer.writerows(merged_data.values())
    
    return len(merged_data)

# Usage
conference_files = [
    'idweek_sessions.csv',
    'eccmid_sessions.csv',
    'escmid_sessions.csv'
]

merged_count = merge_conference_csvs(
    conference_files, 
    'all_conference_sessions.csv',
    merge_key='title'
)
print(f"Merged to {merged_count} unique sessions")
```

### Analytics and Reporting

```python
import csv
from collections import Counter, defaultdict

def generate_conference_analytics(csv_file):
    """Generate analytics report from conference CSV data"""
    
    stats = {
        'total_records': 0,
        'speakers_by_count': Counter(),
        'sessions_by_track': Counter(),
        'sessions_by_date': Counter(),
        'top_keywords': Counter(),
        'affiliation_analysis': defaultdict(int)
    }
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            stats['total_records'] += 1
            
            # Track analysis
            track = row.get('track', 'Unknown')
            stats['sessions_by_track'][track] += 1
            
            # Date analysis
            date = row.get('date', 'Unknown')
            stats['sessions_by_date'][date] += 1
            
            # Speaker count analysis
            speakers = row.get('speakers', '')
            if speakers:
                speaker_count = len([s.strip() for s in speakers.split(';') if s.strip()])
                stats['speakers_by_count'][speaker_count] += 1
            
            # Keyword analysis
            keywords = row.get('keywords', '')
            if keywords:
                for keyword in keywords.split(','):
                    keyword = keyword.strip().lower()
                    if keyword:
                        stats['top_keywords'][keyword] += 1
            
            # Affiliation analysis
            affiliations = row.get('affiliations', '')
            if affiliations:
                for affiliation in affiliations.split(';'):
                    affiliation = affiliation.strip()
                    if affiliation:
                        stats['affiliation_analysis'][affiliation] += 1
    
    return stats

def export_analytics_report(stats, report_file):
    """Export analytics as CSV report"""
    with open(report_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Summary statistics
        writer.writerow(['Analytics Report'])
        writer.writerow(['Total Records', stats['total_records']])
        writer.writerow([])
        
        # Top tracks
        writer.writerow(['Top Tracks'])
        writer.writerow(['Track', 'Count'])
        for track, count in stats['sessions_by_track'].most_common(10):
            writer.writerow([track, count])
        writer.writerow([])
        
        # Top keywords
        writer.writerow(['Top Keywords'])
        writer.writerow(['Keyword', 'Count'])
        for keyword, count in stats['top_keywords'].most_common(20):
            writer.writerow([keyword, count])
        writer.writerow([])
        
        # Speaker distribution
        writer.writerow(['Speaker Count Distribution'])
        writer.writerow(['Speaker Count', 'Session Count'])
        for speaker_count, session_count in sorted(stats['speakers_by_count'].items()):
            writer.writerow([speaker_count, session_count])

# Usage
analytics = generate_conference_analytics('conference_sessions.csv')
export_analytics_report(analytics, 'conference_analytics.csv')
```

## Best Practices

### Encoding and Unicode

```python
import csv

def safe_csv_operations(input_file, output_file):
    """Handle CSV with proper encoding"""
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)
                print(f"Successfully read with {encoding} encoding")
                break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not decode file with any common encoding")
    
    # Write with UTF-8 encoding (recommended)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
```

### Performance Tips

```python
import csv

# Use appropriate data structures
def efficient_csv_processing():
    # For large files, use generators
    def csv_rows(filename):
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                yield row
    
    # Process without loading all data into memory
    for row in csv_rows('large_file.csv'):
        # Process individual row
        process_row(row)
    
    # For lookups, use dictionaries
    lookup_data = {}
    with open('lookup.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lookup_data[row['key']] = row
    
    # Fast lookups
    result = lookup_data.get('search_key')
```

This documentation covers the essential features of Python's `csv` module for reading, writing, and processing CSV files - crucial for handling conference data exports and generating structured reports in data processing pipelines.