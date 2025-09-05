# Python os Module Documentation

The `os` module provides a portable way to interact with the operating system, including file and directory operations, environment variables, and process management.

## Basic File and Directory Operations

### Directory Operations

```python
import os

# Get current working directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Change directory
os.chdir('/path/to/directory')

# Create directory
os.mkdir('new_directory')

# Create nested directories
os.makedirs('path/to/nested/directory', exist_ok=True)  # exist_ok prevents error if exists

# Remove empty directory
os.rmdir('empty_directory')

# Remove directory and all contents
import shutil
shutil.rmtree('directory_with_contents')

# List directory contents
files = os.listdir('.')  # Current directory
print(files)

# List with full paths
for item in os.listdir('.'):
    full_path = os.path.join('.', item)
    print(full_path)
```

### File Operations

```python
import os

# Check if path exists
if os.path.exists('file.txt'):
    print("File exists")

# Check if it's a file or directory
if os.path.isfile('path'):
    print("It's a file")
elif os.path.isdir('path'):
    print("It's a directory")

# Get file size
size = os.path.getsize('file.txt')
print(f"File size: {size} bytes")

# Get file modification time
import time
mod_time = os.path.getmtime('file.txt')
print(f"Modified: {time.ctime(mod_time)}")

# Rename file or directory
os.rename('old_name.txt', 'new_name.txt')

# Remove file
os.remove('file_to_delete.txt')
# Alternative: os.unlink('file_to_delete.txt')
```

## Path Manipulation

### Path Construction

```python
import os

# Join paths (works across operating systems)
path = os.path.join('directory', 'subdirectory', 'file.txt')
print(path)  # directory/subdirectory/file.txt (Unix) or directory\subdirectory\file.txt (Windows)

# Split path components
directory, filename = os.path.split('/path/to/file.txt')
print(f"Directory: {directory}")  # /path/to
print(f"Filename: {filename}")    # file.txt

# Split extension
name, extension = os.path.splitext('document.pdf')
print(f"Name: {name}")       # document
print(f"Extension: {extension}")  # .pdf

# Get directory name
dirname = os.path.dirname('/path/to/file.txt')  # /path/to

# Get base name
basename = os.path.basename('/path/to/file.txt')  # file.txt

# Get absolute path
abs_path = os.path.abspath('relative/path.txt')
print(abs_path)

# Normalize path (resolve . and .. components)
normalized = os.path.normpath('/path/to/../other/./file.txt')
print(normalized)  # /path/other/file.txt
```

### Path Information

```python
import os

# Check if path is absolute
is_absolute = os.path.isabs('/absolute/path')  # True
is_relative = os.path.isabs('relative/path')   # False

# Common path prefix
common = os.path.commonpath(['/path/to/file1.txt', '/path/to/file2.txt'])
print(common)  # /path/to

# Relative path between two paths
rel_path = os.path.relpath('/path/to/target', '/path/from/here')
print(rel_path)

# Expand user directory (~)
home_path = os.path.expanduser('~/documents')
print(home_path)  # /home/username/documents (Unix) or C:\Users\username\documents (Windows)

# Expand environment variables
expanded = os.path.expandvars('$HOME/documents')  # Unix
expanded = os.path.expandvars('%USERPROFILE%\\documents')  # Windows
```

## Environment Variables

### Reading Environment Variables

```python
import os

# Get environment variable
home = os.environ.get('HOME')  # Returns None if not found
print(f"Home directory: {home}")

# Get with default value
path = os.environ.get('PATH', '/usr/bin')

# Get all environment variables
for key, value in os.environ.items():
    print(f"{key} = {value}")

# Check if environment variable exists
if 'API_KEY' in os.environ:
    api_key = os.environ['API_KEY']
else:
    print("API_KEY not set")

# Alternative using getenv
api_key = os.getenv('API_KEY', 'default_key')
```

### Setting Environment Variables

```python
import os

# Set environment variable (only for current process)
os.environ['MY_VAR'] = 'my_value'

# Set multiple variables
os.environ.update({
    'API_KEY': 'secret123',
    'DEBUG': 'true',
    'LOG_LEVEL': 'info'
})

# Remove environment variable
if 'TEMP_VAR' in os.environ:
    del os.environ['TEMP_VAR']

# Or use pop with default
removed_value = os.environ.pop('TEMP_VAR', None)
```

## Process Management

### Process Information

```python
import os

# Get process ID
pid = os.getpid()
print(f"Current process ID: {pid}")

# Get parent process ID
ppid = os.getppid()
print(f"Parent process ID: {ppid}")

# Get user ID (Unix only)
try:
    uid = os.getuid()
    print(f"User ID: {uid}")
except AttributeError:
    print("getuid() not available on Windows")

# Get group ID (Unix only)
try:
    gid = os.getgid()
    print(f"Group ID: {gid}")
except AttributeError:
    print("getgid() not available on Windows")
```

### Running External Commands

```python
import os

# Simple command execution (deprecated - use subprocess instead)
# os.system('ls -l')  # Don't use this

# Better approach using subprocess
import subprocess

# Run command and get output
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(result.stdout)

# Using os.popen (also deprecated)
# with os.popen('ls -l') as pipe:
#     output = pipe.read()
#     print(output)

# Spawn new process (Unix only)
try:
    pid = os.fork()
    if pid == 0:
        # Child process
        print("This is the child process")
    else:
        # Parent process
        print(f"Created child process with PID: {pid}")
        os.wait()  # Wait for child to complete
except AttributeError:
    print("fork() not available on Windows")
```

## File Permissions and Stats

### File Statistics

```python
import os
import stat
import time

# Get file statistics
file_stats = os.stat('file.txt')

print(f"Size: {file_stats.st_size} bytes")
print(f"Modified: {time.ctime(file_stats.st_mtime)}")
print(f"Created: {time.ctime(file_stats.st_ctime)}")
print(f"Accessed: {time.ctime(file_stats.st_atime)}")
print(f"Mode: {oct(file_stats.st_mode)}")

# Check file type using stat module
mode = file_stats.st_mode
if stat.S_ISREG(mode):
    print("Regular file")
elif stat.S_ISDIR(mode):
    print("Directory")
elif stat.S_ISLNK(mode):
    print("Symbolic link")
```

### File Permissions (Unix/Linux)

```python
import os
import stat

# Change file permissions
os.chmod('file.txt', 0o644)  # rw-r--r--
os.chmod('script.py', 0o755)  # rwxr-xr-x

# Using stat constants
os.chmod('file.txt', stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

# Check permissions
file_stats = os.stat('file.txt')
mode = file_stats.st_mode

# Check if readable by owner
if mode & stat.S_IRUSR:
    print("Readable by owner")

# Check if executable
if mode & stat.S_IXUSR:
    print("Executable by owner")

# Change ownership (Unix only, requires appropriate permissions)
try:
    os.chown('file.txt', 1000, 1000)  # uid, gid
except (AttributeError, PermissionError):
    print("Cannot change ownership")
```

## Walking Directory Trees

### Basic Directory Walking

```python
import os

# Walk through directory tree
for root, dirs, files in os.walk('/path/to/directory'):
    print(f"Directory: {root}")
    
    # Process subdirectories
    for dirname in dirs:
        full_path = os.path.join(root, dirname)
        print(f"  Subdirectory: {full_path}")
    
    # Process files
    for filename in files:
        full_path = os.path.join(root, filename)
        print(f"  File: {full_path}")
    
    print()  # Blank line between directories
```

### Advanced Directory Walking

```python
import os
import fnmatch

def find_files(directory, pattern='*', recursive=True):
    """Find files matching pattern in directory"""
    matches = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, pattern):
                matches.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(directory, filename))
    
    return matches

# Usage examples
pdf_files = find_files('/documents', '*.pdf')
python_files = find_files('/project', '*.py')
config_files = find_files('/etc', '*.conf', recursive=False)

# Walk with filtering
def walk_with_filter(directory, include_dirs=None, exclude_dirs=None):
    """Walk directory with filtering"""
    for root, dirs, files in os.walk(directory):
        # Filter directories
        if exclude_dirs:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        if include_dirs:
            dirs[:] = [d for d in dirs if d in include_dirs]
        
        yield root, dirs, files

# Example: skip .git and __pycache__ directories
for root, dirs, files in walk_with_filter('.', exclude_dirs={'.git', '__pycache__'}):
    print(f"Processing: {root}")
```

## Platform-Specific Operations

### Cross-Platform Considerations

```python
import os

# Check operating system
if os.name == 'nt':  # Windows
    print("Running on Windows")
    path_separator = '\\'
elif os.name == 'posix':  # Unix/Linux/macOS
    print("Running on Unix-like system")
    path_separator = '/'

# Better way to get path separator
print(f"Path separator: {os.sep}")
print(f"Alternative path separator: {os.altsep}")  # None on Unix, '/' on Windows
print(f"Path list separator: {os.pathsep}")  # ':' on Unix, ';' on Windows
print(f"Line separator: {repr(os.linesep)}")  # '\n' on Unix, '\r\n' on Windows

# Platform-specific paths
if os.name == 'nt':
    config_dir = os.path.join(os.environ['APPDATA'], 'MyApp')
else:
    config_dir = os.path.join(os.path.expanduser('~'), '.myapp')

print(f"Config directory: {config_dir}")
```

### Temporary Files and Directories

```python
import os
import tempfile

# Get temporary directory
temp_dir = tempfile.gettempdir()
print(f"Temp directory: {temp_dir}")

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    temp_file.write('Temporary data')
    temp_filename = temp_file.name

print(f"Temporary file created: {temp_filename}")

# Clean up temporary file
os.remove(temp_filename)

# Create temporary directory
temp_dir = tempfile.mkdtemp()
print(f"Temporary directory: {temp_dir}")

# Use temporary directory
temp_file_path = os.path.join(temp_dir, 'temp_data.txt')
with open(temp_file_path, 'w') as f:
    f.write('Some data')

# Clean up temporary directory
import shutil
shutil.rmtree(temp_dir)
```

## Conference Data Processing Examples

### Directory Setup for Conference Data

```python
import os
import time
from datetime import datetime

def setup_conference_directories(conference_name, year, base_dir='./conferences'):
    """Setup directory structure for conference data"""
    
    # Create base conference directory
    conf_dir = os.path.join(base_dir, f"{conference_name}_{year}")
    
    # Create subdirectories
    subdirs = [
        'raw_data',
        'processed_data', 
        'exports',
        'logs',
        'temp',
        'archive'
    ]
    
    created_dirs = []
    
    for subdir in subdirs:
        full_path = os.path.join(conf_dir, subdir)
        try:
            os.makedirs(full_path, exist_ok=True)
            created_dirs.append(full_path)
            print(f"Created directory: {full_path}")
        except OSError as e:
            print(f"Error creating directory {full_path}: {e}")
    
    # Create a README file
    readme_path = os.path.join(conf_dir, 'README.txt')
    with open(readme_path, 'w') as f:
        f.write(f"Conference: {conference_name} {year}\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Structure:\n")
        for subdir in subdirs:
            f.write(f"  {subdir}/\n")
    
    return conf_dir, created_dirs

# Usage
conf_dir, dirs = setup_conference_directories('ECCMID', 2024)
print(f"Conference directory setup complete: {conf_dir}")
```

### File Organization and Cleanup

```python
import os
import shutil
import time

def organize_downloaded_files(download_dir, organized_dir):
    """Organize downloaded conference files by type"""
    
    file_types = {
        'pdf': ['pdf'],
        'images': ['png', 'jpg', 'jpeg', 'gif'],
        'documents': ['doc', 'docx', 'txt'],
        'data': ['csv', 'json', 'xml', 'xlsx'],
        'html': ['html', 'htm']
    }
    
    # Create organized directory structure
    for category in file_types.keys():
        category_dir = os.path.join(organized_dir, category)
        os.makedirs(category_dir, exist_ok=True)
    
    # Process files
    moved_files = {}
    
    for filename in os.listdir(download_dir):
        file_path = os.path.join(download_dir, filename)
        
        if os.path.isfile(file_path):
            # Get file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower().lstrip('.')
            
            # Find category
            category = 'other'  # default
            for cat, extensions in file_types.items():
                if ext in extensions:
                    category = cat
                    break
            
            # Create category directory if needed
            category_dir = os.path.join(organized_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)
            
            # Move file
            dest_path = os.path.join(category_dir, filename)
            
            # Handle duplicate names
            counter = 1
            original_dest = dest_path
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(original_dest)
                dest_path = f"{name}_{counter}{ext}"
                counter += 1
            
            try:
                shutil.move(file_path, dest_path)
                moved_files[filename] = dest_path
                print(f"Moved: {filename} -> {category}/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
    
    return moved_files

def cleanup_old_files(directory, days_old=30):
    """Remove files older than specified days"""
    current_time = time.time()
    cutoff_time = current_time - (days_old * 24 * 60 * 60)
    
    removed_files = []
    
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            
            try:
                file_mtime = os.path.getmtime(file_path)
                
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    removed_files.append(file_path)
                    print(f"Removed old file: {file_path}")
                    
            except OSError as e:
                print(f"Error processing {file_path}: {e}")
    
    return removed_files

# Usage
organized_files = organize_downloaded_files('./downloads', './organized')
old_files = cleanup_old_files('./temp', days_old=7)
```

### Log File Management

```python
import os
import glob
import gzip
import time
from datetime import datetime, timedelta

def rotate_log_files(log_dir, max_files=10):
    """Rotate and compress old log files"""
    
    log_pattern = os.path.join(log_dir, '*.log')
    log_files = glob.glob(log_pattern)
    
    for log_file in log_files:
        # Get file modification time
        mod_time = os.path.getmtime(log_file)
        mod_date = datetime.fromtimestamp(mod_time)
        
        # If file is more than 1 day old, compress it
        if datetime.now() - mod_date > timedelta(days=1):
            # Create compressed filename with timestamp
            timestamp = mod_date.strftime('%Y%m%d_%H%M%S')
            basename = os.path.basename(log_file)
            name, ext = os.path.splitext(basename)
            
            compressed_name = f"{name}_{timestamp}{ext}.gz"
            compressed_path = os.path.join(log_dir, compressed_name)
            
            # Compress the file
            try:
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove original file
                os.remove(log_file)
                print(f"Compressed and removed: {log_file}")
                
            except Exception as e:
                print(f"Error compressing {log_file}: {e}")
    
    # Remove excess compressed files
    compressed_pattern = os.path.join(log_dir, '*.gz')
    compressed_files = glob.glob(compressed_pattern)
    
    if len(compressed_files) > max_files:
        # Sort by modification time (oldest first)
        compressed_files.sort(key=os.path.getmtime)
        
        # Remove oldest files
        for old_file in compressed_files[:-max_files]:
            try:
                os.remove(old_file)
                print(f"Removed old compressed log: {old_file}")
            except Exception as e:
                print(f"Error removing {old_file}: {e}")

def monitor_disk_space(directory, threshold_percent=90):
    """Monitor disk space and warn if usage is high"""
    
    if os.name == 'posix':
        # Unix/Linux
        statvfs = os.statvfs(directory)
        total_space = statvfs.f_frsize * statvfs.f_blocks
        free_space = statvfs.f_frsize * statvfs.f_available
        used_space = total_space - free_space
        usage_percent = (used_space / total_space) * 100
        
    elif os.name == 'nt':
        # Windows
        import shutil
        total, used, free = shutil.disk_usage(directory)
        usage_percent = (used / total) * 100
    
    print(f"Disk usage: {usage_percent:.1f}%")
    
    if usage_percent > threshold_percent:
        print(f"Warning: Disk usage above {threshold_percent}%!")
        return False
    
    return True

# Usage
rotate_log_files('./logs', max_files=5)
if not monitor_disk_space('./data', threshold_percent=85):
    print("Consider cleaning up old files")
```

### Configuration File Handling

```python
import os
import json
import configparser

def load_conference_config(config_dir='./config'):
    """Load configuration files for conference processing"""
    
    config_files = {
        'main': os.path.join(config_dir, 'main.json'),
        'databases': os.path.join(config_dir, 'databases.ini'),
        'api_keys': os.path.join(config_dir, 'api_keys.json')
    }
    
    config = {}
    
    # Load JSON config
    if os.path.exists(config_files['main']):
        with open(config_files['main'], 'r') as f:
            config['main'] = json.load(f)
    
    # Load INI config
    if os.path.exists(config_files['databases']):
        parser = configparser.ConfigParser()
        parser.read(config_files['databases'])
        config['databases'] = {
            section: dict(parser[section]) 
            for section in parser.sections()
        }
    
    # Load API keys from environment or file
    config['api_keys'] = {}
    
    # Try environment variables first
    api_keys_from_env = {
        'conference_api': os.environ.get('CONFERENCE_API_KEY'),
        'storage_key': os.environ.get('STORAGE_KEY')
    }
    
    for key, value in api_keys_from_env.items():
        if value:
            config['api_keys'][key] = value
    
    # Load from file if not in environment
    if os.path.exists(config_files['api_keys']):
        with open(config_files['api_keys'], 'r') as f:
            file_keys = json.load(f)
            
        # Only use file keys if not already set from environment
        for key, value in file_keys.items():
            if key not in config['api_keys']:
                config['api_keys'][key] = value
    
    return config

def create_default_config(config_dir='./config'):
    """Create default configuration files"""
    
    os.makedirs(config_dir, exist_ok=True)
    
    # Default main config
    main_config = {
        'conferences': ['ECCMID', 'IDWeek', 'ESCMID'],
        'output_formats': ['csv', 'json'],
        'max_concurrent_requests': 5,
        'request_delay': 1.0,
        'timeout': 30
    }
    
    main_config_path = os.path.join(config_dir, 'main.json')
    with open(main_config_path, 'w') as f:
        json.dump(main_config, f, indent=2)
    
    # Default database config
    db_config = configparser.ConfigParser()
    db_config['DEFAULT'] = {
        'host': 'localhost',
        'port': '5432',
        'timeout': '30'
    }
    
    db_config['development'] = {
        'database': 'conference_dev',
        'username': 'dev_user'
    }
    
    db_config['production'] = {
        'database': 'conference_prod',
        'username': 'prod_user'
    }
    
    db_config_path = os.path.join(config_dir, 'databases.ini')
    with open(db_config_path, 'w') as f:
        db_config.write(f)
    
    print(f"Created default configuration in {config_dir}")

# Usage
config = load_conference_config()
if not config:
    create_default_config()
    config = load_conference_config()

print("Configuration loaded:")
for section, data in config.items():
    print(f"  {section}: {data}")
```

## Best Practices

### Safe File Operations

```python
import os
import tempfile
import shutil

def safe_file_write(filename, content):
    """Safely write file with atomic operation"""
    
    # Write to temporary file first
    temp_dir = os.path.dirname(filename)
    
    with tempfile.NamedTemporaryFile(
        mode='w', 
        dir=temp_dir, 
        delete=False,
        prefix=f"{os.path.basename(filename)}.tmp"
    ) as temp_file:
        temp_file.write(content)
        temp_filename = temp_file.name
    
    try:
        # Atomic move (on same filesystem)
        shutil.move(temp_filename, filename)
        print(f"Successfully wrote {filename}")
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise e

def safe_directory_operations(func):
    """Decorator for safe directory operations"""
    def wrapper(*args, **kwargs):
        original_dir = os.getcwd()
        try:
            return func(*args, **kwargs)
        finally:
            os.chdir(original_dir)
    return wrapper

@safe_directory_operations
def process_in_directory(target_dir):
    """Example function that changes directories safely"""
    os.chdir(target_dir)
    # Do processing here
    files = os.listdir('.')
    return files

# Usage
safe_file_write('important_data.txt', 'Critical information')
files = process_in_directory('/some/other/directory')
```

### Error Handling

```python
import os
import errno

def robust_file_operations():
    """Example of robust file operations with error handling"""
    
    try:
        # Try to create directory
        os.makedirs('/path/to/directory')
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("Directory already exists")
        elif e.errno == errno.EACCES:
            print("Permission denied")
        else:
            print(f"Error creating directory: {e}")
            raise
    
    try:
        # Try to read file
        with open('config.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Config file not found, using defaults")
        content = "default_config"
    except PermissionError:
        print("Permission denied reading config file")
        raise
    except IOError as e:
        print(f"I/O error reading config: {e}")
        raise
    
    return content
```

This documentation covers the essential features of Python's `os` module for interacting with the operating system - crucial for file management, directory operations, and system integration in conference data processing workflows.