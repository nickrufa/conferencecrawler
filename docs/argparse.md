# Python argparse Module Documentation

The `argparse` module provides an easy and flexible way to parse command-line arguments and options in Python programs. It automatically generates help and usage messages and issues errors when users give invalid arguments.

## Basic Usage

### Simple Argument Parser

```python
import argparse

# Create parser
parser = argparse.ArgumentParser(description='Process conference data')

# Add arguments
parser.add_argument('input_file', help='Input file path')
parser.add_argument('output_file', help='Output file path')

# Parse arguments
args = parser.parse_args()

# Use arguments
print(f"Input: {args.input_file}")
print(f"Output: {args.output_file}")

# Usage: python script.py input.csv output.csv
```

### Arguments with Options

```python
import argparse

parser = argparse.ArgumentParser(description='Conference data crawler')

# Positional arguments
parser.add_argument('conference', help='Conference name (ECCMID, IDWeek, etc.)')

# Optional arguments
parser.add_argument('-o', '--output', help='Output directory', default='./output')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('--format', choices=['csv', 'json', 'xml'], default='csv', 
                   help='Output format')

args = parser.parse_args()

# Usage examples:
# python crawler.py ECCMID
# python crawler.py IDWeek --output /data --verbose --format json
```

## Argument Types and Actions

### Argument Types

```python
import argparse

parser = argparse.ArgumentParser()

# String (default)
parser.add_argument('--name', type=str, help='Conference name')

# Integer
parser.add_argument('--year', type=int, help='Conference year')

# Float
parser.add_argument('--timeout', type=float, help='Request timeout in seconds')

# File objects
parser.add_argument('--input', type=argparse.FileType('r'), help='Input file')
parser.add_argument('--output', type=argparse.FileType('w'), help='Output file')

# Custom type validation
def valid_date(date_string):
    try:
        from datetime import datetime
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}")

parser.add_argument('--start-date', type=valid_date, help='Start date (YYYY-MM-DD)')

args = parser.parse_args()
```

### Argument Actions

```python
import argparse

parser = argparse.ArgumentParser()

# Store value (default)
parser.add_argument('--name', action='store')

# Store constant
parser.add_argument('--debug', action='store_const', const=True, default=False)

# Boolean flags
parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
parser.add_argument('--quiet', action='store_false', help='Disable output')

# Count occurrences (-v, -vv, -vvv)
parser.add_argument('-v', '--verbose', action='count', default=0, 
                   help='Increase verbosity')

# Append to list
parser.add_argument('--include', action='append', help='Include pattern')

# Append constant to list
parser.add_argument('--feature', action='append_const', const='advanced', 
                   dest='features')

args = parser.parse_args()

# Usage:
# python script.py --include "*.pdf" --include "*.csv" -vv
# Results in: args.include = ['*.pdf', '*.csv'], args.verbose = 2
```

## Advanced Features

### Subcommands

```python
import argparse

# Main parser
parser = argparse.ArgumentParser(description='Conference data toolkit')
parser.add_argument('--config', help='Configuration file')

# Create subparsers
subparsers = parser.add_subparsers(dest='command', help='Available commands')

# Crawl command
crawl_parser = subparsers.add_parser('crawl', help='Crawl conference data')
crawl_parser.add_argument('conference', help='Conference name')
crawl_parser.add_argument('--year', type=int, required=True, help='Conference year')
crawl_parser.add_argument('--output', default='./data', help='Output directory')

# Process command
process_parser = subparsers.add_parser('process', help='Process extracted data')
process_parser.add_argument('input_dir', help='Input directory')
process_parser.add_argument('--format', choices=['csv', 'json'], default='csv')
process_parser.add_argument('--clean', action='store_true', help='Clean data')

# Export command
export_parser = subparsers.add_parser('export', help='Export processed data')
export_parser.add_argument('data_file', help='Data file to export')
export_parser.add_argument('--template', help='Export template')

args = parser.parse_args()

# Handle subcommands
if args.command == 'crawl':
    print(f"Crawling {args.conference} {args.year}")
elif args.command == 'process':
    print(f"Processing {args.input_dir}")
elif args.command == 'export':
    print(f"Exporting {args.data_file}")
else:
    parser.print_help()

# Usage:
# python tool.py crawl ECCMID --year 2024
# python tool.py process ./raw_data --format json --clean
# python tool.py export data.csv --template report
```

### Argument Groups

```python
import argparse

parser = argparse.ArgumentParser(description='Conference crawler')

# Create argument groups
input_group = parser.add_argument_group('Input options')
input_group.add_argument('--url', help='Base URL to crawl')
input_group.add_argument('--input-file', help='Input file with URLs')
input_group.add_argument('--resume', help='Resume from checkpoint')

output_group = parser.add_argument_group('Output options')
output_group.add_argument('--output-dir', default='./output', help='Output directory')
output_group.add_argument('--format', choices=['csv', 'json', 'xml'], default='csv')
output_group.add_argument('--compress', action='store_true', help='Compress output')

crawler_group = parser.add_argument_group('Crawler options')
crawler_group.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
crawler_group.add_argument('--threads', type=int, default=1, help='Number of threads')
crawler_group.add_argument('--user-agent', help='Custom user agent')

args = parser.parse_args()
```

### Mutually Exclusive Groups

```python
import argparse

parser = argparse.ArgumentParser()

# Create mutually exclusive group
mode_group = parser.add_mutually_exclusive_group(required=True)
mode_group.add_argument('--crawl', action='store_true', help='Crawl mode')
mode_group.add_argument('--process', action='store_true', help='Process mode')
mode_group.add_argument('--export', action='store_true', help='Export mode')

# Another exclusive group
format_group = parser.add_mutually_exclusive_group()
format_group.add_argument('--json', action='store_true', help='JSON output')
format_group.add_argument('--csv', action='store_true', help='CSV output')

args = parser.parse_args()

# Usage (valid):
# python script.py --crawl --json
# python script.py --process --csv

# Usage (invalid - will show error):
# python script.py --crawl --process
```

## Configuration and Customization

### Default Values and Required Arguments

```python
import argparse
import os

parser = argparse.ArgumentParser()

# Required arguments
parser.add_argument('conference', help='Conference name')
parser.add_argument('--year', required=True, type=int, help='Conference year')

# Default values
parser.add_argument('--output', default='./output', help='Output directory')
parser.add_argument('--format', default='csv', help='Output format')

# Defaults from environment variables
parser.add_argument('--api-key', 
                   default=os.environ.get('API_KEY'), 
                   help='API key (default: from API_KEY env var)')

# Conditional required
parser.add_argument('--database-url', help='Database URL')
parser.add_argument('--export-db', action='store_true', help='Export to database')

args = parser.parse_args()

# Check conditional requirements
if args.export_db and not args.database_url:
    parser.error('--database-url is required when --export-db is used')
```

### Custom Help and Descriptions

```python
import argparse

# Custom formatter
class CustomHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string

parser = argparse.ArgumentParser(
    description='Conference Data Extraction Toolkit',
    epilog='''
Examples:
  %(prog)s crawl ECCMID --year 2024 --output ./eccmid_data
  %(prog)s process ./raw_data --clean --format json
  %(prog)s export data.csv --template summary
    ''',
    formatter_class=CustomHelpFormatter,
    prog='conference-tool'
)

# Add arguments with detailed help
parser.add_argument('command', 
                   choices=['crawl', 'process', 'export'],
                   help='Command to execute')

parser.add_argument('--config', 
                   metavar='FILE',
                   help='Configuration file path (default: ./config.yaml)')

args = parser.parse_args()
```

### Configuration File Integration

```python
import argparse
import configparser
import json
import yaml

def load_config_file(config_path):
    """Load configuration from various file formats"""
    if config_path.endswith('.json'):
        with open(config_path) as f:
            return json.load(f)
    elif config_path.endswith(('.yml', '.yaml')):
        with open(config_path) as f:
            return yaml.safe_load(f)
    elif config_path.endswith('.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)
        return dict(config['DEFAULT'])
    else:
        raise ValueError(f"Unsupported config format: {config_path}")

def parse_args_with_config():
    """Parse arguments with config file support"""
    # First pass: get config file
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config', help='Configuration file')
    args, remaining = parser.parse_known_args()
    
    # Load defaults from config file
    defaults = {}
    if args.config:
        try:
            file_config = load_config_file(args.config)
            defaults.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Main parser with defaults
    main_parser = argparse.ArgumentParser(description='Conference crawler')
    main_parser.set_defaults(**defaults)
    
    # Add all arguments
    main_parser.add_argument('--config', help='Configuration file')
    main_parser.add_argument('--conference', required=True, help='Conference name')
    main_parser.add_argument('--year', type=int, required=True, help='Conference year')
    main_parser.add_argument('--output', default='./output', help='Output directory')
    main_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    return main_parser.parse_args()

# Usage
args = parse_args_with_config()
```

## Error Handling and Validation

### Custom Validation

```python
import argparse
import os
import re

def validate_conference_name(value):
    """Validate conference name"""
    valid_conferences = ['ECCMID', 'IDWeek', 'ESCMID', 'ICAAC']
    if value.upper() not in valid_conferences:
        raise argparse.ArgumentTypeError(
            f"Invalid conference: {value}. Must be one of {valid_conferences}"
        )
    return value.upper()

def validate_year(value):
    """Validate conference year"""
    year = int(value)
    if year < 2000 or year > 2030:
        raise argparse.ArgumentTypeError(f"Year must be between 2000 and 2030")
    return year

def validate_output_dir(value):
    """Validate output directory"""
    if os.path.exists(value) and not os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"Output path exists but is not a directory: {value}")
    return value

def validate_email(value):
    """Validate email address"""
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(f"Invalid email format: {value}")
    return value

parser = argparse.ArgumentParser()
parser.add_argument('--conference', type=validate_conference_name, required=True)
parser.add_argument('--year', type=validate_year, required=True)
parser.add_argument('--output', type=validate_output_dir, default='./output')
parser.add_argument('--email', type=validate_email, help='Notification email')

try:
    args = parser.parse_args()
except argparse.ArgumentTypeError as e:
    print(f"Validation error: {e}")
    exit(1)
```

### Error Handling

```python
import argparse
import sys

def handle_parsing_errors():
    """Gracefully handle argument parsing errors"""
    parser = argparse.ArgumentParser(description='Conference data tool')
    parser.add_argument('--conference', required=True, help='Conference name')
    parser.add_argument('--year', type=int, required=True, help='Conference year')
    
    try:
        args = parser.parse_args()
        return args
    except SystemExit as e:
        if e.code != 0:  # Only handle error exits, not help exits
            print("Error: Invalid arguments provided")
            print("Use --help for usage information")
        sys.exit(e.code)

# Alternative: custom error handler
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"\nError: {message}", file=sys.stderr)
        print("Use --help for more information", file=sys.stderr)
        sys.exit(2)

parser = CustomArgumentParser(description='Conference tool')
parser.add_argument('--conference', required=True)
```

## Conference Data Processing Examples

### Conference Crawler CLI

```python
import argparse
import logging
import sys
from datetime import datetime

def setup_crawler_cli():
    """Setup comprehensive CLI for conference crawler"""
    parser = argparse.ArgumentParser(
        description='Conference Data Crawler - Extract data from medical conferences',
        epilog='''
Examples:
  %(prog)s crawl ECCMID --year 2024 --sessions --posters
  %(prog)s crawl IDWeek --year 2024 --output ./idweek_data --delay 2.0
  %(prog)s process ./raw_data --clean --export-csv --export-json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                       help='Increase verbosity (-v, -vv, -vvv)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress all output except errors')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl conference data')
    crawl_parser.add_argument('conference', type=str.upper,
                             choices=['ECCMID', 'IDWEEK', 'ESCMID'],
                             help='Conference name')
    crawl_parser.add_argument('--year', type=int, required=True,
                             help='Conference year')
    crawl_parser.add_argument('--output', '-o', default='./data',
                             help='Output directory (default: ./data)')
    
    # Data type options
    data_group = crawl_parser.add_argument_group('Data types')
    data_group.add_argument('--sessions', action='store_true',
                           help='Crawl session data')
    data_group.add_argument('--posters', action='store_true',
                           help='Crawl poster data')
    data_group.add_argument('--abstracts', action='store_true',
                           help='Crawl abstract data')
    data_group.add_argument('--all', action='store_true',
                           help='Crawl all available data types')
    
    # Crawler options
    crawler_group = crawl_parser.add_argument_group('Crawler options')
    crawler_group.add_argument('--delay', type=float, default=1.0,
                              help='Delay between requests in seconds (default: 1.0)')
    crawler_group.add_argument('--threads', type=int, default=1,
                              help='Number of concurrent threads (default: 1)')
    crawler_group.add_argument('--resume', help='Resume from checkpoint file')
    crawler_group.add_argument('--user-agent', 
                              default='ConferenceCrawler/1.0',
                              help='Custom user agent string')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process crawled data')
    process_parser.add_argument('input_dir', help='Directory containing raw data')
    process_parser.add_argument('--output', '-o', default='./processed',
                               help='Output directory for processed data')
    
    # Processing options
    process_group = process_parser.add_argument_group('Processing options')
    process_group.add_argument('--clean', action='store_true',
                              help='Clean and normalize data')
    process_group.add_argument('--deduplicate', action='store_true',
                              help='Remove duplicate entries')
    process_group.add_argument('--merge', action='store_true',
                              help='Merge related data sources')
    
    # Export options
    export_group = process_parser.add_argument_group('Export options')
    export_group.add_argument('--export-csv', action='store_true',
                             help='Export as CSV files')
    export_group.add_argument('--export-json', action='store_true',
                             help='Export as JSON files')
    export_group.add_argument('--export-excel', action='store_true',
                             help='Export as Excel files')
    export_group.add_argument('--export-sql', action='store_true',
                             help='Generate SQL insert statements')
    
    return parser

def main():
    """Main application entry point"""
    parser = setup_crawler_cli()
    args = parser.parse_args()
    
    # Setup logging based on verbosity
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Validate arguments
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle crawl command
    if args.command == 'crawl':
        # Check that at least one data type is selected
        if not any([args.sessions, args.posters, args.abstracts, args.all]):
            print("Error: Must specify at least one data type to crawl")
            print("Use --sessions, --posters, --abstracts, or --all")
            return 1
        
        print(f"Crawling {args.conference} {args.year}")
        print(f"Output directory: {args.output}")
        print(f"Delay: {args.delay}s, Threads: {args.threads}")
        
        if args.all:
            print("Crawling all available data types")
        else:
            data_types = []
            if args.sessions: data_types.append('sessions')
            if args.posters: data_types.append('posters')
            if args.abstracts: data_types.append('abstracts')
            print(f"Crawling: {', '.join(data_types)}")
    
    # Handle process command
    elif args.command == 'process':
        if not any([args.export_csv, args.export_json, args.export_excel, args.export_sql]):
            print("Warning: No export format specified, defaulting to CSV")
            args.export_csv = True
        
        print(f"Processing data from: {args.input_dir}")
        print(f"Output directory: {args.output}")
        
        operations = []
        if args.clean: operations.append('cleaning')
        if args.deduplicate: operations.append('deduplication')
        if args.merge: operations.append('merging')
        
        if operations:
            print(f"Operations: {', '.join(operations)}")
        
        export_formats = []
        if args.export_csv: export_formats.append('CSV')
        if args.export_json: export_formats.append('JSON')
        if args.export_excel: export_formats.append('Excel')
        if args.export_sql: export_formats.append('SQL')
        print(f"Export formats: {', '.join(export_formats)}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

### PDF Processing Tool

```python
import argparse
import os
from pathlib import Path

def create_pdf_tool_parser():
    """Create parser for PDF processing tool"""
    parser = argparse.ArgumentParser(
        description='Conference PDF Processing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=Path, help='Single PDF file to process')
    input_group.add_argument('--directory', type=Path, help='Directory of PDF files')
    input_group.add_argument('--list', type=argparse.FileType('r'), 
                           help='Text file with list of PDF paths')
    
    # Output options
    parser.add_argument('--output', '-o', type=Path, default=Path('./output'),
                       help='Output directory (default: ./output)')
    parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt',
                       help='Output format (default: txt)')
    
    # Processing options
    processing_group = parser.add_argument_group('Processing options')
    processing_group.add_argument('--extract-text', action='store_true', default=True,
                                 help='Extract text content (default: True)')
    processing_group.add_argument('--extract-tables', action='store_true',
                                 help='Extract table data')
    processing_group.add_argument('--extract-metadata', action='store_true',
                                 help='Extract PDF metadata')
    
    # Filtering options
    filter_group = parser.add_argument_group('Filtering options')
    filter_group.add_argument('--page-range', help='Page range (e.g., 1-5, 2,4,6)')
    filter_group.add_argument('--min-pages', type=int, help='Minimum number of pages')
    filter_group.add_argument('--max-pages', type=int, help='Maximum number of pages')
    filter_group.add_argument('--pattern', help='Only process files matching regex pattern')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced options')
    advanced_group.add_argument('--parallel', type=int, default=1,
                               help='Number of parallel processes (default: 1)')
    advanced_group.add_argument('--timeout', type=int, default=300,
                               help='Timeout per file in seconds (default: 300)')
    advanced_group.add_argument('--skip-errors', action='store_true',
                               help='Continue processing on errors')
    
    return parser

def validate_pdf_args(args):
    """Validate PDF tool arguments"""
    errors = []
    
    # Check input exists
    if args.file and not args.file.exists():
        errors.append(f"File does not exist: {args.file}")
    elif args.directory and not args.directory.exists():
        errors.append(f"Directory does not exist: {args.directory}")
    elif args.directory and not args.directory.is_dir():
        errors.append(f"Path is not a directory: {args.directory}")
    
    # Validate page range
    if args.page_range:
        try:
            parse_page_range(args.page_range)
        except ValueError as e:
            errors.append(f"Invalid page range: {e}")
    
    # Validate parallel processing
    if args.parallel < 1:
        errors.append("Parallel processes must be >= 1")
    
    return errors

def parse_page_range(range_str):
    """Parse page range string like '1-5,7,9-11'"""
    pages = set()
    for part in range_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)
```

### Data Analysis CLI

```python
import argparse
from datetime import date, datetime

def create_analysis_parser():
    """Create parser for data analysis tool"""
    parser = argparse.ArgumentParser(
        description='Conference Data Analysis Tool',
        prog='conference-analysis'
    )
    
    # Input data
    parser.add_argument('data_files', nargs='+', help='Data files to analyze')
    
    # Analysis types
    analysis_group = parser.add_argument_group('Analysis types')
    analysis_group.add_argument('--summary', action='store_true',
                               help='Generate summary statistics')
    analysis_group.add_argument('--trends', action='store_true',
                               help='Analyze trends over time')
    analysis_group.add_argument('--networks', action='store_true',
                               help='Analyze collaboration networks')
    analysis_group.add_argument('--topics', action='store_true',
                               help='Perform topic analysis')
    
    # Filtering options
    filter_group = parser.add_argument_group('Filtering options')
    filter_group.add_argument('--start-date', type=date.fromisoformat,
                             help='Start date (YYYY-MM-DD)')
    filter_group.add_argument('--end-date', type=date.fromisoformat,
                             help='End date (YYYY-MM-DD)')
    filter_group.add_argument('--conferences', nargs='+',
                             help='Filter by conference names')
    filter_group.add_argument('--keywords', nargs='+',
                             help='Filter by keywords')
    
    # Output options
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument('--output', '-o', default='analysis_results',
                             help='Output directory (default: analysis_results)')
    output_group.add_argument('--format', choices=['html', 'pdf', 'json'], 
                             default='html', help='Report format')
    output_group.add_argument('--charts', action='store_true',
                             help='Generate charts and visualizations')
    
    return parser

def main():
    # Multiple parser example
    parser = create_analysis_parser()
    args = parser.parse_args()
    
    # Validate date range
    if args.start_date and args.end_date:
        if args.start_date > args.end_date:
            parser.error("Start date must be before end date")
    
    # Check analysis types
    if not any([args.summary, args.trends, args.networks, args.topics]):
        print("No analysis type specified, running summary analysis")
        args.summary = True
    
    print(f"Analyzing {len(args.data_files)} data files")
    if args.start_date:
        print(f"Date range: {args.start_date} to {args.end_date or 'present'}")
    
    # Run analysis based on arguments
    run_analysis(args)

def run_analysis(args):
    """Run analysis based on parsed arguments"""
    # Implementation would go here
    pass

if __name__ == '__main__':
    main()
```

## Best Practices

### Argument Organization

```python
import argparse

def create_well_organized_parser():
    """Example of well-organized argument parser"""
    parser = argparse.ArgumentParser(
        description='Conference Data Processing Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Group related arguments
    input_group = parser.add_argument_group('Input options')
    input_group.add_argument('--input', required=True, help='Input file/directory')
    input_group.add_argument('--format', choices=['csv', 'json'], default='csv')
    
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument('--output', default='./results', help='Output directory')
    output_group.add_argument('--compress', action='store_true', help='Compress output')
    
    # Use descriptive names and help text
    parser.add_argument('--conference-name', dest='conference_name',
                       help='Name of the conference to process')
    
    # Provide examples in help
    parser.add_argument('--date-format', 
                       help='Date format string (e.g., %%Y-%%m-%%d)')
    
    return parser
```

### Testing Argument Parsing

```python
import argparse
import unittest
from unittest.mock import patch

class TestArgumentParsing(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()  # Your parser creation function
    
    def test_required_arguments(self):
        """Test that required arguments are enforced"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])  # Should fail without required args
    
    def test_valid_arguments(self):
        """Test parsing valid arguments"""
        args = self.parser.parse_args(['--conference', 'ECCMID', '--year', '2024'])
        self.assertEqual(args.conference, 'ECCMID')
        self.assertEqual(args.year, 2024)
    
    def test_default_values(self):
        """Test default values are applied"""
        args = self.parser.parse_args(['--conference', 'ECCMID', '--year', '2024'])
        self.assertEqual(args.output, './output')  # Default value
    
    @patch('sys.argv', ['script.py', '--conference', 'ECCMID', '--year', '2024'])
    def test_with_mocked_argv(self):
        """Test with mocked command line arguments"""
        args = self.parser.parse_args()
        self.assertEqual(args.conference, 'ECCMID')

# Run tests
if __name__ == '__main__':
    unittest.main()
```

This documentation covers the essential features of Python's `argparse` module for creating robust command-line interfaces - crucial for building user-friendly tools for conference data processing and analysis.