# Python tempfile Module Documentation

The `tempfile` module provides utilities for creating temporary files and directories in a secure and cross-platform manner. It handles the complexities of temporary file management including cleanup, security, and platform differences.

## Basic Usage

### Temporary Files

```python
import tempfile
import os

# Create a temporary file
with tempfile.NamedTemporaryFile() as temp_file:
    # Write data to temporary file
    temp_file.write(b'This is temporary data')
    temp_file.flush()  # Ensure data is written
    
    print(f"Temporary file: {temp_file.name}")
    
    # Read data back
    temp_file.seek(0)
    data = temp_file.read()
    print(f"Data: {data}")

# File is automatically deleted when context manager exits

# Create temporary file that persists
temp_file = tempfile.NamedTemporaryFile(delete=False)
temp_file.write(b'Persistent temporary data')
temp_filename = temp_file.name
temp_file.close()

print(f"Persistent temp file: {temp_filename}")

# Must manually clean up
os.unlink(temp_filename)
```

### Temporary Directories

```python
import tempfile
import os

# Create temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Temporary directory: {temp_dir}")
    
    # Create files in temporary directory
    temp_file_path = os.path.join(temp_dir, 'data.txt')
    with open(temp_file_path, 'w') as f:
        f.write('Some data')
    
    # List contents
    print(f"Contents: {os.listdir(temp_dir)}")

# Directory and all contents are automatically deleted

# Create persistent temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Persistent temp directory: {temp_dir}")

# Must manually clean up
import shutil
shutil.rmtree(temp_dir)
```

## Temporary File Options

### File Modes and Text Handling

```python
import tempfile

# Text mode temporary file
with tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8') as temp_file:
    temp_file.write('This is text data\n')
    temp_file.write('Line 2\n')
    
    # Read back
    temp_file.seek(0)
    content = temp_file.read()
    print(content)

# Binary mode (default)
with tempfile.NamedTemporaryFile(mode='w+b') as temp_file:
    temp_file.write(b'Binary data')
    
    temp_file.seek(0)
    data = temp_file.read()
    print(f"Binary data: {data}")

# Read-only temporary file
with tempfile.NamedTemporaryFile(mode='r+') as temp_file:
    temp_file.write('Initial data')
    temp_file.seek(0)
    content = temp_file.read()
    print(content)
```

### Custom Prefixes, Suffixes, and Directories

```python
import tempfile

# Custom prefix and suffix
with tempfile.NamedTemporaryFile(
    prefix='conference_',
    suffix='.csv',
    dir='/tmp'  # Custom directory (Unix) or None for system default
) as temp_file:
    print(f"Temp file: {temp_file.name}")
    # Filename will be like: /tmp/conference_abc123.csv

# Custom directory for temporary files
custom_temp_dir = './temp_data'
os.makedirs(custom_temp_dir, exist_ok=True)

with tempfile.NamedTemporaryFile(dir=custom_temp_dir) as temp_file:
    print(f"Custom location: {temp_file.name}")

# Custom directory name pattern
temp_dir = tempfile.mkdtemp(
    prefix='conference_',
    suffix='_data',
    dir='./temp'
)
print(f"Custom temp directory: {temp_dir}")
# Cleanup required
shutil.rmtree(temp_dir)
```

## Advanced Features

### Temporary File with Specific Name

```python
import tempfile
import os

# Create temporary file with known name
def create_named_temp_file(filename, content):
    """Create a temporary file with specific name in temp directory"""
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    
    with open(temp_path, 'w') as f:
        f.write(content)
    
    return temp_path

# Usage
temp_path = create_named_temp_file('conference_data.json', '{"test": "data"}')
print(f"Created: {temp_path}")

# Manual cleanup
os.remove(temp_path)

# Safer approach with collision handling
def create_safe_named_temp_file(filename, content):
    """Create temporary file handling name collisions"""
    temp_dir = tempfile.gettempdir()
    base, ext = os.path.splitext(filename)
    
    counter = 1
    temp_path = os.path.join(temp_dir, filename)
    
    while os.path.exists(temp_path):
        new_filename = f"{base}_{counter}{ext}"
        temp_path = os.path.join(temp_dir, new_filename)
        counter += 1
    
    with open(temp_path, 'w') as f:
        f.write(content)
    
    return temp_path
```

### SpooledTemporaryFile

```python
import tempfile

# SpooledTemporaryFile keeps data in memory until it exceeds max_size
with tempfile.SpooledTemporaryFile(max_size=1024, mode='w+') as spooled_file:
    # Small data stays in memory
    spooled_file.write('Small amount of data')
    print(f"In memory: {not spooled_file._rolled}")
    
    # Large data gets written to disk
    spooled_file.write('x' * 2000)  # Exceeds max_size
    print(f"In memory: {not spooled_file._rolled}")
    
    # Can still read/write normally
    spooled_file.seek(0)
    content = spooled_file.read(50)
    print(f"First 50 chars: {content}")

# Spooled file with custom threshold
def process_large_data(data_generator, max_memory=1024*1024):  # 1MB
    """Process large data with memory-efficient temporary storage"""
    with tempfile.SpooledTemporaryFile(max_size=max_memory, mode='w+') as temp_file:
        # Write data
        for chunk in data_generator:
            temp_file.write(chunk)
        
        # Process data
        temp_file.seek(0)
        return process_file_data(temp_file)

def process_file_data(file_obj):
    """Process data from file-like object"""
    # Example processing
    lines = file_obj.readlines()
    return len(lines)
```

### TemporaryFile vs NamedTemporaryFile

```python
import tempfile

# TemporaryFile - no visible name in filesystem
with tempfile.TemporaryFile() as temp_file:
    temp_file.write(b'Data without name')
    # No temp_file.name attribute available
    # File is invisible in directory listings

# NamedTemporaryFile - has visible name
with tempfile.NamedTemporaryFile() as temp_file:
    temp_file.write(b'Data with name')
    print(f"File name: {temp_file.name}")
    # File is visible in directory listings until deleted

# Choose based on security needs:
# - TemporaryFile: More secure, no name visible
# - NamedTemporaryFile: Useful when other processes need to access file
```

## Configuration and Settings

### Temporary Directory Location

```python
import tempfile
import os

# Get current temporary directory
temp_dir = tempfile.gettempdir()
print(f"System temp directory: {temp_dir}")

# Get temporary directory with environment variable precedence
# Checks: TMPDIR, TEMP, TMP environment variables, then system default
temp_dir_env = tempfile.gettempdir()
print(f"Temp directory (with env): {temp_dir_env}")

# Set custom temporary directory
original_tmpdir = os.environ.get('TMPDIR')
os.environ['TMPDIR'] = '/custom/temp/path'

# This will now use the custom path (if it exists)
custom_temp_dir = tempfile.gettempdir()
print(f"Custom temp directory: {custom_temp_dir}")

# Restore original
if original_tmpdir:
    os.environ['TMPDIR'] = original_tmpdir
else:
    del os.environ['TMPDIR']

# Platform-specific temporary directories
if os.name == 'nt':  # Windows
    # Uses TEMP, TMP environment variables or C:\Temp
    print("Windows temp directory")
elif os.name == 'posix':  # Unix/Linux/macOS
    # Uses TMPDIR environment variable or /tmp
    print("Unix-like temp directory")
```

### Security Considerations

```python
import tempfile
import os
import stat

def create_secure_temp_file():
    """Create temporary file with secure permissions"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    
    # Set restrictive permissions (owner read/write only)
    os.chmod(temp_filename, stat.S_IRUSR | stat.S_IWUSR)
    
    return temp_filename

def create_secure_temp_dir():
    """Create temporary directory with secure permissions"""
    temp_dir = tempfile.mkdtemp()
    
    # Set restrictive permissions (owner read/write/execute only)
    os.chmod(temp_dir, stat.S_IRWXU)
    
    return temp_dir

# Check permissions
temp_file = create_secure_temp_file()
file_stat = os.stat(temp_file)
print(f"File permissions: {oct(file_stat.st_mode)}")

temp_dir = create_secure_temp_dir()
dir_stat = os.stat(temp_dir)
print(f"Directory permissions: {oct(dir_stat.st_mode)}")

# Cleanup
os.remove(temp_file)
os.rmdir(temp_dir)
```

## Conference Data Processing Examples

### Temporary PDF Processing

```python
import tempfile
import os
import shutil

def process_pdf_with_temp_workspace(pdf_path, processing_func):
    """Process PDF using temporary workspace"""
    
    with tempfile.TemporaryDirectory(prefix='pdf_processing_') as temp_dir:
        print(f"Processing PDF in: {temp_dir}")
        
        # Copy PDF to temporary workspace
        temp_pdf_path = os.path.join(temp_dir, 'input.pdf')
        shutil.copy2(pdf_path, temp_pdf_path)
        
        # Create subdirectories for processing
        extract_dir = os.path.join(temp_dir, 'extracted')
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(extract_dir)
        os.makedirs(output_dir)
        
        try:
            # Process PDF
            results = processing_func(temp_pdf_path, extract_dir, output_dir)
            
            # Copy results back to permanent location
            if 'output_files' in results:
                for output_file in results['output_files']:
                    if os.path.exists(output_file):
                        dest_file = os.path.basename(output_file)
                        shutil.copy2(output_file, dest_file)
                        print(f"Saved: {dest_file}")
            
            return results
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            # Temp directory will be cleaned up automatically
            raise

def extract_conference_posters(pdf_path, extract_dir, output_dir):
    """Example PDF processing function"""
    # Simulate PDF processing
    import time
    time.sleep(0.1)  # Simulate processing time
    
    # Create mock output files
    text_output = os.path.join(output_dir, 'extracted_text.txt')
    with open(text_output, 'w') as f:
        f.write('Mock extracted text from conference posters')
    
    json_output = os.path.join(output_dir, 'poster_data.json')
    with open(json_output, 'w') as f:
        f.write('{"posters": [{"id": "P001", "title": "Mock Poster"}]}')
    
    return {
        'status': 'success',
        'output_files': [text_output, json_output],
        'poster_count': 1
    }

# Usage
results = process_pdf_with_temp_workspace(
    'conference_posters.pdf', 
    extract_conference_posters
)
print(f"Processing complete: {results}")
```

### Batch Data Processing with Temporary Storage

```python
import tempfile
import csv
import json
import os

def batch_process_conference_data(input_files, batch_size=100):
    """Process conference data files in batches using temporary storage"""
    
    with tempfile.TemporaryDirectory(prefix='batch_processing_') as temp_dir:
        print(f"Batch processing workspace: {temp_dir}")
        
        batch_results = []
        current_batch = []
        batch_num = 1
        
        for input_file in input_files:
            print(f"Processing: {input_file}")
            
            # Read and validate input file
            with open(input_file, 'r') as f:
                if input_file.endswith('.csv'):
                    reader = csv.DictReader(f)
                    data = list(reader)
                elif input_file.endswith('.json'):
                    data = json.load(f)
                else:
                    continue
            
            current_batch.extend(data)
            
            # Process batch when it reaches target size
            if len(current_batch) >= batch_size:
                batch_result = process_batch(current_batch, batch_num, temp_dir)
                batch_results.append(batch_result)
                current_batch = []
                batch_num += 1
        
        # Process remaining data
        if current_batch:
            batch_result = process_batch(current_batch, batch_num, temp_dir)
            batch_results.append(batch_result)
        
        # Combine all batch results
        final_results = combine_batch_results(batch_results, temp_dir)
        
        return final_results

def process_batch(data_batch, batch_num, temp_dir):
    """Process a single batch of data"""
    
    # Create temporary file for batch processing
    batch_file = os.path.join(temp_dir, f'batch_{batch_num}.json')
    
    with open(batch_file, 'w') as f:
        json.dump(data_batch, f)
    
    # Simulate batch processing
    processed_data = []
    for item in data_batch:
        # Example processing: normalize conference names
        if 'conference' in item:
            item['conference'] = item['conference'].upper()
        
        # Add processing timestamp
        from datetime import datetime
        item['processed_at'] = datetime.now().isoformat()
        
        processed_data.append(item)
    
    # Save processed batch
    processed_file = os.path.join(temp_dir, f'processed_batch_{batch_num}.json')
    with open(processed_file, 'w') as f:
        json.dump(processed_data, f)
    
    return {
        'batch_num': batch_num,
        'input_file': batch_file,
        'output_file': processed_file,
        'record_count': len(processed_data)
    }

def combine_batch_results(batch_results, temp_dir):
    """Combine results from all batches"""
    
    combined_data = []
    total_records = 0
    
    for batch_result in batch_results:
        with open(batch_result['output_file'], 'r') as f:
            batch_data = json.load(f)
            combined_data.extend(batch_data)
            total_records += batch_result['record_count']
    
    # Save final combined results
    final_output = 'combined_conference_data.json'
    with open(final_output, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    return {
        'output_file': final_output,
        'total_records': total_records,
        'batch_count': len(batch_results)
    }

# Usage
input_files = ['eccmid_2024.csv', 'idweek_2024.json', 'escmid_2025.csv']
results = batch_process_conference_data(input_files, batch_size=50)
print(f"Batch processing complete: {results}")
```

### Temporary File Cache for Web Scraping

```python
import tempfile
import requests
import hashlib
import os
import time
import pickle
from urllib.parse import urlparse

class TemporaryCache:
    """Temporary cache for web scraping results"""
    
    def __init__(self, cache_duration=3600):  # 1 hour default
        self.temp_dir = tempfile.mkdtemp(prefix='scraping_cache_')
        self.cache_duration = cache_duration
        print(f"Cache directory: {self.temp_dir}")
    
    def _get_cache_path(self, url):
        """Generate cache file path for URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.temp_dir, f"cache_{url_hash}.pkl")
    
    def get(self, url):
        """Get cached response for URL"""
        cache_path = self._get_cache_path(url)
        
        if os.path.exists(cache_path):
            # Check if cache is still valid
            cache_time = os.path.getmtime(cache_path)
            if time.time() - cache_time < self.cache_duration:
                try:
                    with open(cache_path, 'rb') as f:
                        cached_response = pickle.load(f)
                    print(f"Cache hit: {url}")
                    return cached_response
                except Exception:
                    # Remove corrupted cache file
                    os.remove(cache_path)
        
        return None
    
    def set(self, url, response_data):
        """Cache response data for URL"""
        cache_path = self._get_cache_path(url)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(response_data, f)
            print(f"Cached: {url}")
        except Exception as e:
            print(f"Failed to cache {url}: {e}")
    
    def clear(self):
        """Clear all cached data"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("Cache cleared")
    
    def __del__(self):
        """Cleanup cache on deletion"""
        self.clear()

def scrape_with_cache(urls, cache_duration=1800):
    """Scrape URLs with temporary caching"""
    
    cache = TemporaryCache(cache_duration)
    results = {}
    
    try:
        for url in urls:
            print(f"Processing: {url}")
            
            # Try to get from cache first
            cached_data = cache.get(url)
            
            if cached_data:
                results[url] = cached_data
            else:
                # Fetch from web
                try:
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    # Prepare data for caching
                    response_data = {
                        'url': url,
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'content': response.text,
                        'timestamp': time.time()
                    }
                    
                    # Cache the response
                    cache.set(url, response_data)
                    results[url] = response_data
                    
                    # Be nice to the server
                    time.sleep(1)
                    
                except requests.RequestException as e:
                    print(f"Error fetching {url}: {e}")
                    results[url] = None
        
        return results
        
    finally:
        # Cleanup cache
        cache.clear()

# Usage
conference_urls = [
    'https://example.com/eccmid/sessions',
    'https://example.com/idweek/posters',
    'https://example.com/escmid/abstracts'
]

scraped_data = scrape_with_cache(conference_urls, cache_duration=3600)
print(f"Scraped {len(scraped_data)} URLs")
```

### Large File Processing with Temporary Chunks

```python
import tempfile
import os
import csv
import json

def process_large_csv_file(large_csv_path, chunk_size=10000):
    """Process large CSV file using temporary chunks"""
    
    with tempfile.TemporaryDirectory(prefix='csv_chunks_') as temp_dir:
        print(f"Processing large CSV in chunks: {temp_dir}")
        
        chunk_files = []
        processed_results = []
        
        # Split large file into chunks
        with open(large_csv_path, 'r') as input_file:
            reader = csv.DictReader(input_file)
            headers = reader.fieldnames
            
            chunk_num = 1
            current_chunk = []
            
            for row in reader:
                current_chunk.append(row)
                
                if len(current_chunk) >= chunk_size:
                    # Save chunk to temporary file
                    chunk_file = os.path.join(temp_dir, f'chunk_{chunk_num}.csv')
                    
                    with open(chunk_file, 'w', newline='') as chunk_output:
                        writer = csv.DictWriter(chunk_output, fieldnames=headers)
                        writer.writeheader()
                        writer.writerows(current_chunk)
                    
                    chunk_files.append(chunk_file)
                    current_chunk = []
                    chunk_num += 1
            
            # Handle remaining rows
            if current_chunk:
                chunk_file = os.path.join(temp_dir, f'chunk_{chunk_num}.csv')
                
                with open(chunk_file, 'w', newline='') as chunk_output:
                    writer = csv.DictWriter(chunk_output, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(current_chunk)
                
                chunk_files.append(chunk_file)
        
        # Process each chunk
        for chunk_file in chunk_files:
            print(f"Processing chunk: {os.path.basename(chunk_file)}")
            
            with open(chunk_file, 'r') as f:
                chunk_reader = csv.DictReader(f)
                chunk_data = list(chunk_reader)
            
            # Process chunk data (example: extract statistics)
            chunk_stats = analyze_chunk_data(chunk_data)
            processed_results.append(chunk_stats)
            
            # Save processed chunk
            processed_file = chunk_file.replace('.csv', '_processed.json')
            with open(processed_file, 'w') as f:
                json.dump(chunk_stats, f, indent=2)
        
        # Combine results from all chunks
        final_stats = combine_chunk_statistics(processed_results)
        
        return final_stats

def analyze_chunk_data(chunk_data):
    """Analyze a chunk of conference data"""
    stats = {
        'record_count': len(chunk_data),
        'conferences': {},
        'years': {},
        'authors': set(),
        'keywords': {}
    }
    
    for record in chunk_data:
        # Conference statistics
        conference = record.get('conference', 'Unknown')
        stats['conferences'][conference] = stats['conferences'].get(conference, 0) + 1
        
        # Year statistics
        year = record.get('year', 'Unknown')
        stats['years'][year] = stats['years'].get(year, 0) + 1
        
        # Author statistics
        authors = record.get('authors', '').split(';')
        for author in authors:
            author = author.strip()
            if author:
                stats['authors'].add(author)
        
        # Keyword statistics
        keywords = record.get('keywords', '').split(',')
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword:
                stats['keywords'][keyword] = stats['keywords'].get(keyword, 0) + 1
    
    # Convert set to count
    stats['author_count'] = len(stats['authors'])
    del stats['authors']  # Remove set (not JSON serializable)
    
    return stats

def combine_chunk_statistics(chunk_results):
    """Combine statistics from all chunks"""
    combined = {
        'total_records': 0,
        'conferences': {},
        'years': {},
        'author_count': 0,
        'keywords': {},
        'chunk_count': len(chunk_results)
    }
    
    author_names = set()
    
    for chunk_stats in chunk_results:
        combined['total_records'] += chunk_stats['record_count']
        combined['author_count'] += chunk_stats['author_count']
        
        # Combine conference counts
        for conf, count in chunk_stats['conferences'].items():
            combined['conferences'][conf] = combined['conferences'].get(conf, 0) + count
        
        # Combine year counts
        for year, count in chunk_stats['years'].items():
            combined['years'][year] = combined['years'].get(year, 0) + count
        
        # Combine keyword counts
        for keyword, count in chunk_stats['keywords'].items():
            combined['keywords'][keyword] = combined['keywords'].get(keyword, 0) + count
    
    # Sort results
    combined['top_conferences'] = sorted(
        combined['conferences'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    combined['top_keywords'] = sorted(
        combined['keywords'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:20]
    
    return combined

# Usage
stats = process_large_csv_file('large_conference_dataset.csv', chunk_size=5000)
print(f"Processing complete: {stats['total_records']} total records")
print(f"Top conferences: {stats['top_conferences'][:5]}")
print(f"Top keywords: {stats['top_keywords'][:10]}")
```

## Best Practices

### Context Manager Pattern

```python
import tempfile
import contextlib

@contextlib.contextmanager
def temporary_workspace(prefix='work_', cleanup_on_error=True):
    """Context manager for temporary workspace with error handling"""
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    except Exception as e:
        if cleanup_on_error:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise e
    else:
        # Normal cleanup
        import shutil
        shutil.rmtree(temp_dir)

# Usage
with temporary_workspace(prefix='conference_') as workspace:
    # Do work in temporary workspace
    work_file = os.path.join(workspace, 'data.txt')
    with open(work_file, 'w') as f:
        f.write('Working data')
    
    # Workspace is automatically cleaned up
```

### Error Handling and Cleanup

```python
import tempfile
import atexit
import shutil

class SafeTemporaryManager:
    """Safe temporary file manager with guaranteed cleanup"""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
        
        # Register cleanup function
        atexit.register(self.cleanup_all)
    
    def create_temp_file(self, **kwargs):
        """Create temporary file with tracking"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, **kwargs)
        self.temp_files.append(temp_file.name)
        return temp_file
    
    def create_temp_dir(self, **kwargs):
        """Create temporary directory with tracking"""
        temp_dir = tempfile.mkdtemp(**kwargs)
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup_all(self):
        """Clean up all tracked temporary files and directories"""
        # Clean up files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass
        
        # Clean up directories
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except OSError:
                pass
        
        self.temp_files.clear()
        self.temp_dirs.clear()

# Usage
temp_manager = SafeTemporaryManager()

# Create tracked temporary resources
temp_file = temp_manager.create_temp_file(suffix='.csv')
temp_dir = temp_manager.create_temp_dir(prefix='data_')

# Use resources
with open(temp_file.name, 'w') as f:
    f.write('Important data')

# Cleanup happens automatically at program exit
```

This documentation covers the essential features of Python's `tempfile` module for creating and managing temporary files and directories - crucial for secure and efficient temporary storage in conference data processing workflows.