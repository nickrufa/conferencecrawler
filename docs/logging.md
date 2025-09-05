# Python logging Module Documentation

The `logging` module provides a flexible framework for emitting log messages from Python programs. It's designed to allow both simple and complex logging configurations for applications and libraries.

## Basic Usage

### Simple Logging

```python
import logging

# Basic configuration
logging.basicConfig(level=logging.DEBUG)

# Log messages at different levels
logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')
```

### Quick Start

```python
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

# Use logging
logging.info('Application started')
logging.warning('This is a warning')
logging.error('An error occurred')
```

## Logging Levels

### Standard Levels

```python
import logging

# Numeric values
logging.DEBUG    # 10
logging.INFO     # 20
logging.WARNING  # 30
logging.ERROR    # 40
logging.CRITICAL # 50

# Level comparison
logging.getLogger().setLevel(logging.WARNING)
logging.info('This will not be shown')      # Below WARNING
logging.warning('This will be shown')       # At WARNING level
logging.error('This will also be shown')    # Above WARNING
```

### Custom Levels

```python
import logging

# Add custom level
TRACE = 5
logging.addLevelName(TRACE, 'TRACE')

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

logging.Logger.trace = trace

# Use custom level
logger = logging.getLogger()
logger.setLevel(TRACE)
logger.trace('Trace message')
```

## Loggers, Handlers, and Formatters

### Logger Hierarchy

```python
import logging

# Get loggers
root_logger = logging.getLogger()  # Root logger
app_logger = logging.getLogger('myapp')
module_logger = logging.getLogger('myapp.module')

# Logger hierarchy
# myapp.module inherits from myapp, which inherits from root

# Set levels
app_logger.setLevel(logging.INFO)
module_logger.setLevel(logging.DEBUG)
```

### Handlers

```python
import logging
import sys

# Create logger
logger = logging.getLogger('myapp')
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Rotating file handler
rotating_handler = logging.handlers.RotatingFileHandler(
    'app.log', maxBytes=10*1024*1024, backupCount=5
)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Test logging
logger.debug('Debug message')    # Only to file
logger.info('Info message')      # To console and file
```

### Formatters

```python
import logging

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# More detailed formatter
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# JSON formatter (custom)
class JsonFormatter(logging.Formatter):
    def format(self, record):
        import json
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno
        }
        return json.dumps(log_record)

# Apply formatter to handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)
```

## Configuration

### Basic Configuration

```python
import logging

# Configure with basicConfig
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='application.log',
    filemode='a'  # 'w' for overwrite, 'a' for append
)
```

### Dictionary Configuration

```python
import logging.config

config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
```

### Configuration File (INI Format)

```python
# logging.conf
"""
[loggers]
keys=root,myapp

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[logger_myapp]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=myapp
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=simpleFormatter
args=('app.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""

# Load configuration
import logging.config
logging.config.fileConfig('logging.conf')

# Use configured logger
logger = logging.getLogger('myapp')
logger.info('Application started')
```

### YAML Configuration

```python
import logging.config
import yaml

# config.yaml
yaml_config = """
version: 1
disable_existing_loggers: false
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple
    stream: ext://sys.stdout
  file_handler:
    class: logging.FileHandler
    level: INFO
    formatter: simple
    filename: app.log
loggers:
  myapp:
    level: DEBUG
    handlers: [console, file_handler]
    propagate: no
root:
  level: DEBUG
  handlers: [console]
"""

# Load and apply configuration
config = yaml.safe_load(yaml_config)
logging.config.dictConfig(config)
```

## Advanced Handlers

### Rotating File Handlers

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Size-based rotation
size_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Time-based rotation
time_handler = TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=30
)

# Different rotation intervals
# 'S' - Seconds
# 'M' - Minutes  
# 'H' - Hours
# 'D' - Days
# 'midnight' - Roll over at midnight
# 'W0'-'W6' - Roll over on a certain weekday (0=Monday)

logger = logging.getLogger('myapp')
logger.addHandler(time_handler)
```

### Network Handlers

```python
import logging
from logging.handlers import SMTPHandler, HTTPHandler, SysLogHandler

# Email handler
smtp_handler = SMTPHandler(
    mailhost=('smtp.example.com', 587),
    fromaddr='app@example.com',
    toaddrs=['admin@example.com'],
    subject='Application Error',
    credentials=('username', 'password'),
    secure=()
)
smtp_handler.setLevel(logging.ERROR)

# HTTP handler
http_handler = HTTPHandler(
    host='logging.example.com',
    url='/logs',
    method='POST'
)

# Syslog handler
syslog_handler = SysLogHandler(address=('localhost', 514))

logger = logging.getLogger('myapp')
logger.addHandler(smtp_handler)
logger.addHandler(http_handler)
```

### Custom Handlers

```python
import logging

class DatabaseHandler(logging.Handler):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
    
    def emit(self, record):
        try:
            # Format the record
            msg = self.format(record)
            
            # Insert into database
            cursor = self.db_connection.cursor()
            cursor.execute(
                "INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
                (record.created, record.levelname, msg)
            )
            self.db_connection.commit()
        except Exception:
            self.handleError(record)

# Usage
# db_handler = DatabaseHandler(db_connection)
# logger.addHandler(db_handler)
```

## Filters

### Basic Filtering

```python
import logging

class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO

# Apply filter
logger = logging.getLogger('myapp')
handler = logging.StreamHandler()
handler.addFilter(InfoFilter())
logger.addHandler(handler)

# Only INFO messages will be handled
logger.info('This will be shown')
logger.warning('This will be filtered out')
logger.error('This will be filtered out')
```

### Context Filtering

```python
import logging
import threading

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.thread_id = threading.current_thread().ident
        record.user_id = getattr(threading.current_thread(), 'user_id', 'unknown')
        return True

# Apply context filter
logger = logging.getLogger('myapp')
handler = logging.StreamHandler()
handler.addFilter(ContextFilter())
formatter = logging.Formatter(
    '%(asctime)s - %(thread_id)s - %(user_id)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set thread context
threading.current_thread().user_id = 'user123'
logger.info('User action logged')
```

## Exception Logging

### Logging Exceptions

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = 10 / 0
except ZeroDivisionError:
    # Log exception with traceback
    logger.exception('Division by zero occurred')
    
    # Alternative ways to log exceptions
    logger.error('Division by zero occurred', exc_info=True)
    
    # Log with custom message
    logger.error('Math operation failed', exc_info=True)
    
    # Log exception object
    import sys
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error('Exception: %s', exc_value, exc_info=True)
```

### Custom Exception Information

```python
import logging
import traceback

def log_exception_details(logger, exception, context=None):
    """Log detailed exception information"""
    exc_type = type(exception).__name__
    exc_message = str(exception)
    exc_traceback = traceback.format_exc()
    
    log_message = f"""
Exception Details:
Type: {exc_type}
Message: {exc_message}
Context: {context or 'None'}
Traceback:
{exc_traceback}
"""
    
    logger.error(log_message)

# Usage
try:
    # Some operation
    data = {'key': 'value'}
    result = data['missing_key']
except KeyError as e:
    log_exception_details(logger, e, context='Data processing')
```

## Performance Considerations

### Lazy Formatting

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Inefficient - string formatting always happens
expensive_operation = lambda: "very expensive calculation"
logger.debug('Debug: ' + expensive_operation())  # Bad

# Efficient - formatting only happens if message is logged
logger.debug('Debug: %s', expensive_operation)  # Good

# Using f-strings (Python 3.6+)
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f'Debug: {expensive_operation()}')  # Conditional
```

### Using LoggerAdapter

```python
import logging

class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f'[{self.extra["context"]}] {msg}', kwargs

# Create adapter
logger = logging.getLogger(__name__)
context_logger = ContextAdapter(logger, {'context': 'DataProcessor'})

# Use adapter
context_logger.info('Processing started')  # [DataProcessor] Processing started
context_logger.error('Processing failed')  # [DataProcessor] Processing failed
```

## Conference Data Processing Examples

### Session Crawler Logging

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_crawler_logging():
    """Setup logging for conference crawler"""
    logger = logging.getLogger('conference_crawler')
    logger.setLevel(logging.DEBUG)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler for detailed logs
    file_handler = RotatingFileHandler(
        'crawler.log', maxBytes=10*1024*1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Usage in crawler
logger = setup_crawler_logging()

def crawl_session_data(session_url):
    logger.info(f'Starting crawl for session: {session_url}')
    
    try:
        # Crawling logic
        response = requests.get(session_url)
        logger.debug(f'Response status: {response.status_code}')
        
        if response.status_code == 200:
            logger.info('Session data retrieved successfully')
            return response.text
        else:
            logger.warning(f'Unexpected status code: {response.status_code}')
            
    except requests.RequestException as e:
        logger.exception(f'Failed to crawl session data: {session_url}')
        raise
    
    except Exception as e:
        logger.exception(f'Unexpected error crawling session: {session_url}')
        raise
```

### PDF Processing Logging

```python
import logging
from pathlib import Path

def setup_pdf_processing_logging(log_dir='logs'):
    """Setup logging for PDF processing operations"""
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger('pdf_processor')
    logger.setLevel(logging.DEBUG)
    
    # File handler with date-based rotation
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        f'{log_dir}/pdf_processing.log',
        when='midnight',
        interval=1,
        backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = logging.FileHandler(f'{log_dir}/pdf_errors.log')
    error_handler.setLevel(logging.ERROR)
    
    # Formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    error_formatter = logging.Formatter(
        '%(asctime)s - ERROR - %(funcName)s:%(lineno)d\n%(message)s\n' + '='*50
    )
    
    file_handler.setFormatter(detailed_formatter)
    error_handler.setFormatter(error_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

# Usage in PDF processing
logger = setup_pdf_processing_logging()

def extract_poster_data(pdf_path):
    logger.info(f'Processing PDF: {pdf_path}')
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.debug(f'PDF has {len(pdf_reader.pages)} pages')
            
            extracted_text = []
            for page_num, page in enumerate(pdf_reader.pages):
                logger.debug(f'Extracting text from page {page_num + 1}')
                text = page.extract_text()
                extracted_text.append(text)
                
        logger.info(f'Successfully extracted text from {len(extracted_text)} pages')
        return extracted_text
        
    except FileNotFoundError:
        logger.error(f'PDF file not found: {pdf_path}')
        raise
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f'PDF read error for {pdf_path}: {str(e)}')
        raise
    except Exception as e:
        logger.exception(f'Unexpected error processing PDF: {pdf_path}')
        raise
```

### Data Processing Pipeline Logging

```python
import logging
import time
from contextlib import contextmanager

@contextmanager
def log_operation(logger, operation_name, level=logging.INFO):
    """Context manager for logging operations with timing"""
    start_time = time.time()
    logger.log(level, f'{operation_name} started')
    
    try:
        yield
        duration = time.time() - start_time
        logger.log(level, f'{operation_name} completed in {duration:.2f}s')
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f'{operation_name} failed after {duration:.2f}s: {str(e)}')
        raise

# Usage
logger = logging.getLogger('data_pipeline')

def process_conference_data():
    with log_operation(logger, 'Conference data processing'):
        # Data processing steps
        with log_operation(logger, 'Loading raw data', logging.DEBUG):
            raw_data = load_raw_data()
            
        with log_operation(logger, 'Cleaning data', logging.DEBUG):
            cleaned_data = clean_data(raw_data)
            
        with log_operation(logger, 'Generating reports'):
            reports = generate_reports(cleaned_data)
            
        return reports
```

## Best Practices

### Logger Configuration

```python
import logging
import sys

def get_logger(name):
    """Get a properly configured logger"""
    logger = logging.getLogger(name)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
```

### Structured Logging

```python
import logging
import json

class StructuredMessage:
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs
    
    def __str__(self):
        return json.dumps({
            'message': self.message,
            **self.kwargs
        })

# Usage
logger = logging.getLogger(__name__)

logger.info(StructuredMessage(
    'Session processed',
    session_id='12345',
    duration_ms=1500,
    status='success'
))
```

This documentation covers the essential features of Python's `logging` module, providing flexible and powerful logging capabilities crucial for monitoring conference crawler operations and debugging data processing pipelines.