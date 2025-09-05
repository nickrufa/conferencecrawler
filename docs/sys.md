# Python sys Module Documentation

The `sys` module provides access to system-specific parameters and functions used or maintained by the Python interpreter. It allows interaction with the runtime environment, command-line arguments, and system configuration.

## Command-Line Arguments

### Basic Argument Access

```python
import sys

# sys.argv contains command-line arguments
# argv[0] is the script name, argv[1:] are the arguments

print(f"Script name: {sys.argv[0]}")
print(f"Number of arguments: {len(sys.argv) - 1}")

if len(sys.argv) > 1:
    print("Arguments:")
    for i, arg in enumerate(sys.argv[1:], 1):
        print(f"  {i}: {arg}")
else:
    print("No arguments provided")

# Example usage: python script.py arg1 arg2 arg3
# Output:
# Script name: script.py
# Number of arguments: 3
# Arguments:
#   1: arg1
#   2: arg2
#   3: arg3
```

### Processing Arguments

```python
import sys

def parse_simple_args():
    """Simple argument parsing example"""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <conference> [year] [--verbose]")
        sys.exit(1)
    
    conference = sys.argv[1]
    year = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    verbose = '--verbose' in sys.argv
    
    return conference, year, verbose

# Usage
try:
    conference, year, verbose = parse_simple_args()
    print(f"Conference: {conference}")
    if year:
        print(f"Year: {year}")
    if verbose:
        print("Verbose mode enabled")
except SystemExit:
    pass  # Handle graceful exit
```

## Standard I/O Streams

### Standard Input/Output/Error

```python
import sys

# Standard output (usually console)
sys.stdout.write("Hello, World!\n")
sys.stdout.flush()  # Force immediate output

# Standard error (usually console, for error messages)
sys.stderr.write("Error message\n")
sys.stderr.flush()

# Standard input (usually keyboard)
print("Enter some text: ", end='')
sys.stdout.flush()
user_input = sys.stdin.readline().strip()
print(f"You entered: {user_input}")

# Check if streams are connected to a terminal
print(f"stdout is a TTY: {sys.stdout.isatty()}")
print(f"stderr is a TTY: {sys.stderr.isatty()}")
print(f"stdin is a TTY: {sys.stdin.isatty()}")
```

### Redirecting Streams

```python
import sys
import io

# Redirect stdout to capture output
original_stdout = sys.stdout
captured_output = io.StringIO()

sys.stdout = captured_output

print("This will be captured")
print("This too")

# Restore original stdout
sys.stdout = original_stdout

# Get captured output
output = captured_output.getvalue()
print(f"Captured: {output}")

# Context manager for temporary redirection
from contextlib import redirect_stdout, redirect_stderr

with redirect_stdout(io.StringIO()) as captured:
    print("Captured output")
    captured_text = captured.getvalue()

print(f"Captured text: {captured_text}")

# Redirect to file
with open('output.log', 'w') as log_file:
    with redirect_stdout(log_file):
        print("This goes to the file")
        print("This too")
```

## System Information

### Python Version and Platform

```python
import sys
import platform

# Python version information
print(f"Python version: {sys.version}")
print(f"Version info: {sys.version_info}")
print(f"Major version: {sys.version_info.major}")
print(f"Minor version: {sys.version_info.minor}")
print(f"Micro version: {sys.version_info.micro}")

# Check Python version programmatically
if sys.version_info >= (3, 8):
    print("Python 3.8 or higher")
else:
    print("Python version is older than 3.8")

# Platform information
print(f"Platform: {sys.platform}")  # 'win32', 'linux', 'darwin', etc.
print(f"Architecture: {platform.architecture()}")
print(f"Machine type: {platform.machine()}")

# Executable information
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.exec_prefix}")
```

### Memory and Performance

```python
import sys

# Memory information
def get_size(obj, seen=None):
    """Get size of object including nested objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    
    seen.add(obj_id)
    
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        try:
            size += sum([get_size(i, seen) for i in obj])
        except TypeError:
            pass
    
    return size

# Example usage
data = {
    'conferences': ['ECCMID', 'IDWeek', 'ESCMID'],
    'years': [2022, 2023, 2024],
    'metadata': {'count': 3, 'active': True}
}

print(f"Size of data: {sys.getsizeof(data)} bytes")
print(f"Deep size of data: {get_size(data)} bytes")

# Reference counting
import gc
ref_count = sys.getrefcount(data)
print(f"Reference count: {ref_count}")

# Garbage collection information
print(f"Garbage collection counts: {gc.get_count()}")
```

### System Limits and Configuration

```python
import sys

# Integer size limits
print(f"Max int size: {sys.maxsize}")
print(f"Float info: {sys.float_info}")

# String and Unicode limits
print(f"Max Unicode: {sys.maxunicode}")

# Recursion limit
print(f"Recursion limit: {sys.getrecursionlimit()}")

# Set custom recursion limit (be careful!)
original_limit = sys.getrecursionlimit()
sys.setrecursionlimit(2000)
print(f"New recursion limit: {sys.getrecursionlimit()}")
sys.setrecursionlimit(original_limit)  # Restore

# File system encoding
print(f"File system encoding: {sys.getfilesystemencoding()}")
print(f"Default encoding: {sys.getdefaultencoding()}")

# Check 64-bit vs 32-bit
print(f"Word size: {sys.maxsize.bit_length()} bits")
is_64bit = sys.maxsize > 2**32
print(f"64-bit Python: {is_64bit}")
```

## Module and Path Management

### Module Path

```python
import sys
import os

# Python path (where modules are searched)
print("Python module search paths:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Add custom module path
custom_path = '/path/to/custom/modules'
if custom_path not in sys.path:
    sys.path.append(custom_path)

# Insert at beginning (higher priority)
sys.path.insert(0, './local_modules')

# Remove path
if custom_path in sys.path:
    sys.path.remove(custom_path)

# Get loaded modules
print(f"\nLoaded modules: {len(sys.modules)}")
print("Some loaded modules:")
for name in sorted(list(sys.modules.keys())[:10]):
    module = sys.modules[name]
    print(f"  {name}: {getattr(module, '__file__', 'built-in')}")
```

### Module Information

```python
import sys

def get_module_info(module_name):
    """Get information about a loaded module"""
    if module_name in sys.modules:
        module = sys.modules[module_name]
        info = {
            'name': module_name,
            'file': getattr(module, '__file__', 'built-in'),
            'package': getattr(module, '__package__', None),
            'doc': getattr(module, '__doc__', '')[:100] + '...' if getattr(module, '__doc__', '') else None
        }
        return info
    else:
        return None

# Check specific modules
modules_to_check = ['os', 'sys', 'json', 'requests']
for module_name in modules_to_check:
    info = get_module_info(module_name)
    if info:
        print(f"Module: {info['name']}")
        print(f"  File: {info['file']}")
        print(f"  Package: {info['package']}")
        if info['doc']:
            print(f"  Doc: {info['doc']}")
    else:
        print(f"Module {module_name} not loaded")
    print()
```

## Exit and Exception Handling

### Program Exit

```python
import sys
import atexit

def cleanup_function():
    """Function called on program exit"""
    print("Performing cleanup...")
    # Close files, save data, etc.

# Register cleanup function
atexit.register(cleanup_function)

def exit_with_code(message, code=1):
    """Exit program with message and code"""
    if code == 0:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}", file=sys.stderr)
    
    sys.exit(code)

# Examples of different exit scenarios
def main():
    if len(sys.argv) < 2:
        exit_with_code("No arguments provided", 1)
    
    if sys.argv[1] == 'success':
        exit_with_code("Operation completed successfully", 0)
    elif sys.argv[1] == 'error':
        exit_with_code("An error occurred", 2)
    else:
        print("Processing...")
        # Normal program execution

# Uncomment to test different scenarios:
# main()
```

### Exception Handling

```python
import sys
import traceback

def handle_exceptions():
    """Demonstrate exception handling with sys"""
    
    # Get current exception information
    try:
        raise ValueError("Example error")
    except ValueError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        print(f"Exception type: {exc_type.__name__}")
        print(f"Exception value: {exc_value}")
        print(f"Exception traceback: {exc_traceback}")
        
        # Print formatted traceback
        traceback.print_exc()
        
        # Format traceback as string
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Formatted traceback:\n{tb_str}")

# Custom exception handler
def custom_exception_handler(exc_type, exc_value, exc_traceback):
    """Custom exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle Ctrl+C gracefully
        print("\nProgram interrupted by user")
        sys.exit(0)
    else:
        # Log exception details
        print(f"Unhandled exception: {exc_type.__name__}: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

# Set custom exception handler
sys.excepthook = custom_exception_handler

# Test exception handling
handle_exceptions()
```

## Conference Data Processing Examples

### Command-Line Conference Crawler

```python
import sys
import os
import json
from datetime import datetime

def create_conference_crawler():
    """Command-line conference data crawler"""
    
    def show_usage():
        """Show usage information"""
        program_name = os.path.basename(sys.argv[0])
        print(f"""
Usage: {program_name} <command> [options]

Commands:
  crawl <conference> <year>     Crawl conference data
  process <input_file>          Process raw data
  export <data_file> <format>   Export processed data

Options:
  --verbose                     Enable verbose output
  --output <directory>          Output directory (default: ./data)
  --help                        Show this help message

Examples:
  {program_name} crawl ECCMID 2024 --output ./eccmid_data
  {program_name} process raw_data.json --verbose
  {program_name} export processed_data.json csv
        """)
    
    def parse_arguments():
        """Parse command-line arguments"""
        if len(sys.argv) < 2:
            show_usage()
            sys.exit(1)
        
        if '--help' in sys.argv:
            show_usage()
            sys.exit(0)
        
        command = sys.argv[1]
        verbose = '--verbose' in sys.argv
        
        # Find output directory
        output_dir = './data'
        if '--output' in sys.argv:
            try:
                output_index = sys.argv.index('--output')
                if output_index + 1 < len(sys.argv):
                    output_dir = sys.argv[output_index + 1]
                else:
                    print("Error: --output requires a directory argument", file=sys.stderr)
                    sys.exit(1)
            except ValueError:
                pass
        
        return command, verbose, output_dir
    
    def crawl_command():
        """Handle crawl command"""
        if len(sys.argv) < 4:
            print("Error: crawl command requires conference and year", file=sys.stderr)
            show_usage()
            sys.exit(1)
        
        conference = sys.argv[2]
        year = sys.argv[3]
        
        if not year.isdigit():
            print(f"Error: Year must be numeric, got '{year}'", file=sys.stderr)
            sys.exit(1)
        
        return conference, int(year)
    
    def process_command():
        """Handle process command"""
        if len(sys.argv) < 3:
            print("Error: process command requires input file", file=sys.stderr)
            show_usage()
            sys.exit(1)
        
        input_file = sys.argv[2]
        
        if not os.path.exists(input_file):
            print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
            sys.exit(1)
        
        return input_file
    
    def export_command():
        """Handle export command"""
        if len(sys.argv) < 4:
            print("Error: export command requires data file and format", file=sys.stderr)
            show_usage()
            sys.exit(1)
        
        data_file = sys.argv[2]
        export_format = sys.argv[3]
        
        if not os.path.exists(data_file):
            print(f"Error: Data file does not exist: {data_file}", file=sys.stderr)
            sys.exit(1)
        
        if export_format not in ['csv', 'json', 'excel']:
            print(f"Error: Unsupported format '{export_format}'. Use: csv, json, excel", file=sys.stderr)
            sys.exit(1)
        
        return data_file, export_format
    
    # Main execution
    try:
        command, verbose, output_dir = parse_arguments()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if verbose:
            print(f"Command: {command}")
            print(f"Output directory: {output_dir}")
            print(f"Python version: {sys.version}")
        
        if command == 'crawl':
            conference, year = crawl_command()
            print(f"Crawling {conference} {year}...")
            
            # Simulate crawling
            result = {
                'conference': conference,
                'year': year,
                'crawled_at': datetime.now().isoformat(),
                'sessions': 150,
                'posters': 300
            }
            
            output_file = os.path.join(output_dir, f'{conference.lower()}_{year}_raw.json')
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"Results saved to: {output_file}")
        
        elif command == 'process':
            input_file = process_command()
            print(f"Processing {input_file}...")
            
            # Simulate processing
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            data['processed_at'] = datetime.now().isoformat()
            data['status'] = 'processed'
            
            output_file = os.path.join(output_dir, 'processed_data.json')
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Processed data saved to: {output_file}")
        
        elif command == 'export':
            data_file, export_format = export_command()
            print(f"Exporting {data_file} as {export_format}...")
            
            # Simulate export
            base_name = os.path.splitext(os.path.basename(data_file))[0]
            output_file = os.path.join(output_dir, f'{base_name}.{export_format}')
            
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            if export_format == 'csv':
                import csv
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Key', 'Value'])
                    for key, value in data.items():
                        writer.writerow([key, str(value)])
            
            print(f"Exported to: {output_file}")
        
        else:
            print(f"Error: Unknown command '{command}'", file=sys.stderr)
            show_usage()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if '--verbose' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)

# Run the crawler
if __name__ == '__main__':
    create_conference_crawler()
```

### System Resource Monitor

```python
import sys
import time
import psutil
import json

def monitor_system_resources(duration=60, interval=5):
    """Monitor system resources during data processing"""
    
    print(f"Starting resource monitoring for {duration} seconds...")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Process ID: {os.getpid()}")
    
    start_time = time.time()
    measurements = []
    
    try:
        while time.time() - start_time < duration:
            # Get current process
            process = psutil.Process()
            
            # System information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # Process information
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            measurement = {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_available': memory_info.available,
                    'disk_percent': (disk_info.used / disk_info.total) * 100
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'python_objects': len(gc.get_objects()) if 'gc' in sys.modules else 0
                },
                'python': {
                    'recursion_limit': sys.getrecursionlimit(),
                    'reference_count': sys.gettotalrefcount() if hasattr(sys, 'gettotalrefcount') else 0
                }
            }
            
            measurements.append(measurement)
            
            # Print current status
            print(f"Time: {time.time() - start_time:.1f}s | "
                  f"CPU: {cpu_percent:.1f}% | "
                  f"Memory: {memory_info.percent:.1f}% | "
                  f"Process Memory: {process_memory.rss / 1024 / 1024:.1f}MB")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    # Save measurements
    output_file = f'resource_monitor_{int(time.time())}.json'
    with open(output_file, 'w') as f:
        json.dump(measurements, f, indent=2)
    
    print(f"Resource measurements saved to: {output_file}")
    return measurements

def analyze_resource_data(measurements_file):
    """Analyze saved resource measurements"""
    
    with open(measurements_file, 'r') as f:
        measurements = json.load(f)
    
    if not measurements:
        print("No measurements to analyze")
        return
    
    # Calculate statistics
    cpu_values = [m['system']['cpu_percent'] for m in measurements]
    memory_values = [m['process']['memory_rss'] for m in measurements]
    
    stats = {
        'duration': measurements[-1]['timestamp'] - measurements[0]['timestamp'],
        'measurement_count': len(measurements),
        'cpu': {
            'avg': sum(cpu_values) / len(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values)
        },
        'memory': {
            'avg_mb': sum(memory_values) / len(memory_values) / 1024 / 1024,
            'max_mb': max(memory_values) / 1024 / 1024,
            'min_mb': min(memory_values) / 1024 / 1024
        }
    }
    
    print("Resource Usage Analysis:")
    print(f"Duration: {stats['duration']:.1f} seconds")
    print(f"Measurements: {stats['measurement_count']}")
    print(f"CPU - Avg: {stats['cpu']['avg']:.1f}%, Max: {stats['cpu']['max']:.1f}%, Min: {stats['cpu']['min']:.1f}%")
    print(f"Memory - Avg: {stats['memory']['avg_mb']:.1f}MB, Max: {stats['memory']['max_mb']:.1f}MB, Min: {stats['memory']['min_mb']:.1f}MB")
    
    return stats

# Usage example
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor_system_resources(duration)
    elif len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        if file_path:
            analyze_resource_data(file_path)
        else:
            print("Usage: python script.py analyze <measurements_file>")
    else:
        print("Usage:")
        print("  python script.py monitor [duration]")
        print("  python script.py analyze <measurements_file>")
```

### Environment Configuration Manager

```python
import sys
import os
import json

class ConfigurationManager:
    """Manage application configuration based on environment"""
    
    def __init__(self):
        self.config = self.load_configuration()
    
    def load_configuration(self):
        """Load configuration based on environment and command line"""
        config = {
            'environment': self.detect_environment(),
            'python_info': {
                'version': sys.version,
                'executable': sys.executable,
                'platform': sys.platform,
                'path': sys.path.copy()
            },
            'application': {}
        }
        
        # Load from environment variables
        env_config = self.load_from_environment()
        config.update(env_config)
        
        # Override with command line arguments
        cli_config = self.parse_cli_config()
        config['application'].update(cli_config)
        
        return config
    
    def detect_environment(self):
        """Detect current environment"""
        if 'PRODUCTION' in os.environ:
            return 'production'
        elif 'TESTING' in os.environ:
            return 'testing'
        elif 'DEVELOPMENT' in os.environ:
            return 'development'
        else:
            # Auto-detect based on various indicators
            if sys.stdin.isatty():
                return 'development'  # Interactive terminal
            else:
                return 'production'   # Non-interactive (likely deployed)
    
    def load_from_environment(self):
        """Load configuration from environment variables"""
        env_config = {
            'database': {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': int(os.environ.get('DB_PORT', 5432)),
                'name': os.environ.get('DB_NAME', 'conference_data'),
                'user': os.environ.get('DB_USER', 'user'),
                'password': os.environ.get('DB_PASSWORD', '')
            },
            'api': {
                'key': os.environ.get('API_KEY', ''),
                'base_url': os.environ.get('API_BASE_URL', 'https://api.example.com'),
                'timeout': int(os.environ.get('API_TIMEOUT', 30))
            },
            'logging': {
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
                'file': os.environ.get('LOG_FILE', 'application.log')
            }
        }
        
        return env_config
    
    def parse_cli_config(self):
        """Parse configuration from command line arguments"""
        cli_config = {}
        
        # Look for configuration arguments
        args = sys.argv[1:]  # Skip script name
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == '--config-file' and i + 1 < len(args):
                config_file = args[i + 1]
                file_config = self.load_config_file(config_file)
                cli_config.update(file_config)
                i += 2
            elif arg == '--verbose':
                cli_config['verbose'] = True
                i += 1
            elif arg == '--debug':
                cli_config['debug'] = True
                i += 1
            elif arg == '--output' and i + 1 < len(args):
                cli_config['output_dir'] = args[i + 1]
                i += 2
            elif arg.startswith('--set-') and '=' in arg:
                # Handle --set-key=value format
                key_value = arg[6:]  # Remove '--set-'
                key, value = key_value.split('=', 1)
                cli_config[key] = value
                i += 1
            else:
                i += 1
        
        return cli_config
    
    def load_config_file(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load config file {config_file}: {e}", file=sys.stderr)
            return {}
    
    def get(self, key, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, filename='config.json'):
        """Save current configuration to file"""
        # Remove sensitive information before saving
        safe_config = self.config.copy()
        if 'database' in safe_config and 'password' in safe_config['database']:
            safe_config['database'] = safe_config['database'].copy()
            safe_config['database']['password'] = '***HIDDEN***'
        
        with open(filename, 'w') as f:
            json.dump(safe_config, f, indent=2)
        
        print(f"Configuration saved to {filename}")
    
    def print_config(self, hide_sensitive=True):
        """Print current configuration"""
        config_to_print = self.config.copy()
        
        if hide_sensitive:
            # Hide sensitive values
            sensitive_keys = ['password', 'key', 'secret', 'token']
            self._hide_sensitive_values(config_to_print, sensitive_keys)
        
        print("Current Configuration:")
        print(json.dumps(config_to_print, indent=2))
    
    def _hide_sensitive_values(self, obj, sensitive_keys):
        """Recursively hide sensitive values in configuration"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    obj[key] = '***HIDDEN***'
                elif isinstance(value, (dict, list)):
                    self._hide_sensitive_values(value, sensitive_keys)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._hide_sensitive_values(item, sensitive_keys)

# Usage example
def main():
    """Main function demonstrating configuration management"""
    config_manager = ConfigurationManager()
    
    # Handle special commands
    if '--print-config' in sys.argv:
        config_manager.print_config()
        return
    
    if '--save-config' in sys.argv:
        config_manager.save_config()
        return
    
    # Normal application startup
    print(f"Environment: {config_manager.get('environment')}")
    print(f"Python version: {config_manager.get('python_info.version')}")
    print(f"Database host: {config_manager.get('database.host')}")
    print(f"API timeout: {config_manager.get('api.timeout')} seconds")
    
    if config_manager.get('application.verbose'):
        print("Verbose mode enabled")
    
    if config_manager.get('application.debug'):
        print("Debug mode enabled")
        config_manager.print_config(hide_sensitive=False)

if __name__ == '__main__':
    main()
```

## Best Practices

### Safe System Operations

```python
import sys
import signal
import atexit

class SafeSystemOperations:
    """Safe system operations with proper cleanup"""
    
    def __init__(self):
        self.cleanup_functions = []
        self.setup_signal_handlers()
        self.setup_exit_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}, shutting down gracefully...")
            self.cleanup()
            sys.exit(0)
        
        # Handle common termination signals
        if hasattr(signal, 'SIGINT'):   # Ctrl+C
            signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):  # Termination signal
            signal.signal(signal.SIGTERM, signal_handler)
    
    def setup_exit_handlers(self):
        """Setup exit handlers for cleanup"""
        atexit.register(self.cleanup)
    
    def add_cleanup_function(self, func, *args, **kwargs):
        """Add function to be called during cleanup"""
        self.cleanup_functions.append((func, args, kwargs))
    
    def cleanup(self):
        """Perform cleanup operations"""
        print("Performing cleanup operations...")
        
        for func, args, kwargs in reversed(self.cleanup_functions):
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error during cleanup: {e}", file=sys.stderr)
    
    def safe_exit(self, message="", code=0):
        """Safe exit with cleanup"""
        if message:
            if code == 0:
                print(message)
            else:
                print(message, file=sys.stderr)
        
        self.cleanup()
        sys.exit(code)

# Usage
safe_ops = SafeSystemOperations()

def my_cleanup():
    print("Cleaning up resources...")

safe_ops.add_cleanup_function(my_cleanup)
```

### Performance Monitoring

```python
import sys
import time
import functools

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Record initial state
        initial_refs = sys.gettotalrefcount() if hasattr(sys, 'gettotalrefcount') else 0
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Record final state
            end_time = time.time()
            final_refs = sys.gettotalrefcount() if hasattr(sys, 'gettotalrefcount') else 0
            
            # Print performance metrics
            duration = end_time - start_time
            ref_diff = final_refs - initial_refs
            
            print(f"Performance metrics for {func.__name__}:")
            print(f"  Duration: {duration:.3f} seconds")
            print(f"  Reference count change: {ref_diff}")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"Function {func.__name__} failed after {duration:.3f} seconds: {e}")
            raise
    
    return wrapper

# Usage
@monitor_performance
def process_conference_data(data):
    # Simulate processing
    time.sleep(0.1)
    return len(data)
```

This documentation covers the essential features of Python's `sys` module for interacting with the Python interpreter and system environment - crucial for building robust command-line tools and system-aware applications in conference data processing workflows.