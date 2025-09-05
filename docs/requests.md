# Requests Documentation

Requests is a simple, elegant Python HTTP library that makes sending HTTP requests incredibly easy, supporting features like connection pooling, authentication, and automatic content decompression.

## Installation

```bash
python -m pip install requests
```

Alternative installation methods:
```bash
# From source
git clone https://github.com/psf/requests.git
cd requests
python -m pip install .

# With extras
python -m pip install 'requests[socks]'     # SOCKS proxy support
python -m pip install 'requests[security]'  # Security extras with Certifi
```

## Basic Usage

### Making HTTP Requests

```python
import requests

# GET request
r = requests.get('https://api.github.com/events')

# POST request with data
r = requests.post('https://httpbin.org/post', data={'key': 'value'})

# Other HTTP methods
r = requests.put('https://httpbin.org/put', data={'key': 'value'})
r = requests.delete('https://httpbin.org/delete')
r = requests.head('https://httpbin.org/get')
r = requests.options('https://httpbin.org/get')
```

### Passing URL Parameters

```python
# Using params parameter
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.get('https://httpbin.org/get', params=payload)
print(r.url)  # https://httpbin.org/get?key1=value1&key2=value2

# Multiple values for the same key
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
r = requests.get('https://httpbin.org/get', params=payload)
```

## Handling Response Content

### Text Content

```python
r = requests.get('https://api.github.com/events')
print(r.text)        # Unicode text
print(r.encoding)    # Current encoding
r.encoding = 'ISO-8859-1'  # Change encoding
```

### Binary Content

```python
r = requests.get('https://api.github.com/events')
print(r.content)     # Bytes

# Saving binary content to file
with open('filename.jpg', 'wb') as f:
    for chunk in r.iter_content(chunk_size=128):
        f.write(chunk)
```

### JSON Content

```python
r = requests.get('https://api.github.com/events')
json_data = r.json()  # Automatically decode JSON
```

### Raw Socket Response

```python
r = requests.get('https://api.github.com/events', stream=True)
print(r.raw)
print(r.raw.read(10))  # Read 10 bytes
```

## Sending Data

### Form Data

```python
# Simple form data
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post('https://httpbin.org/post', data=payload)

# Multiple values per key
payload_tuples = [('key1', 'value1'), ('key1', 'value2')]
r = requests.post('https://httpbin.org/post', data=payload_tuples)

payload_dict = {'key1': ['value1', 'value2']}
r = requests.post('https://httpbin.org/post', data=payload_dict)
```

### JSON Data

```python
import json

payload = {'some': 'data'}

# Method 1: Manual JSON encoding
r = requests.post('https://httpbin.org/post', data=json.dumps(payload))

# Method 2: Using json parameter (recommended)
r = requests.post('https://httpbin.org/post', json=payload)
```

### File Uploads

```python
# Simple file upload
files = {'file': open('report.xls', 'rb')}
r = requests.post('https://httpbin.org/post', files=files)

# With explicit filename and content type
files = {
    'file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})
}
r = requests.post('https://httpbin.org/post', files=files)

# Sending strings as files
files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
r = requests.post('https://httpbin.org/post', files=files)

# Multiple files
multiple_files = [
    ('images', ('foo.png', open('foo.png', 'rb'), 'image/png')),
    ('images', ('bar.png', open('bar.png', 'rb'), 'image/png'))
]
r = requests.post('https://httpbin.org/post', files=multiple_files)
```

### Custom Headers

```python
headers = {'user-agent': 'my-app/0.0.1'}
r = requests.get('https://api.github.com/user', headers=headers)
```

## Response Handling

### Status Codes

```python
r = requests.get('https://httpbin.org/get')
print(r.status_code)  # 200

# Using status code constants
print(r.status_code == requests.codes.ok)  # True

# Raise exception for bad status codes
bad_r = requests.get('https://httpbin.org/status/404')
print(bad_r.status_code)  # 404
bad_r.raise_for_status()  # Raises HTTPError
```

### Response Headers

```python
r = requests.get('https://httpbin.org/get')
print(r.headers)
print(r.headers['Content-Type'])      # Case-insensitive
print(r.headers.get('content-type'))  # Safe access
```

## Cookies

### Receiving Cookies

```python
url = 'http://example.com/some/cookie/setting/url'
r = requests.get(url)
print(r.cookies['example_cookie_name'])
```

### Sending Cookies

```python
# Simple cookies
cookies = {'cookies_are': 'working'}
r = requests.get('https://httpbin.org/cookies', cookies=cookies)

# Advanced cookie management
jar = requests.cookies.RequestsCookieJar()
jar.set('tasty_cookie', 'yum', domain='httpbin.org', path='/cookies')
jar.set('gross_cookie', 'blech', domain='httpbin.org', path='/elsewhere')
r = requests.get('https://httpbin.org/cookies', cookies=jar)
```

## Redirection Handling

```python
# Default: automatic redirect following
r = requests.get('http://github.com/')
print(r.url)         # https://github.com/ (redirected)
print(r.status_code) # 200
print(r.history)     # [<Response [301]>]

# Disable redirects
r = requests.get('http://github.com/', allow_redirects=False)
print(r.status_code) # 301
print(r.history)     # []

# Enable redirects for HEAD requests
r = requests.head('http://github.com/', allow_redirects=True)
```

## Timeouts

```python
# Single timeout value (applies to both connect and read)
r = requests.get('https://github.com', timeout=5)

# Separate connect and read timeouts
r = requests.get('https://github.com', timeout=(3.05, 27))

# Disable timeout (wait forever)
r = requests.get('https://github.com', timeout=None)
```

## Authentication

### Basic Authentication

```python
from requests.auth import HTTPBasicAuth

# Using HTTPBasicAuth class
auth = HTTPBasicAuth('user', 'pass')
r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=auth)

# Using tuple shorthand
r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
```

### OAuth 1.0

```python
from requests_oauthlib import OAuth1

# Requires requests-oauthlib: pip install requests-oauthlib
auth = OAuth1('YOUR_APP_KEY', 'YOUR_APP_SECRET',
              'USER_OAUTH_TOKEN', 'USER_OAUTH_TOKEN_SECRET')
r = requests.get('https://api.twitter.com/1.1/account/verify_credentials.json', auth=auth)
```

### Custom Authentication

```python
from requests.auth import AuthBase

class PizzaAuth(AuthBase):
    """Attaches HTTP Pizza Authentication to the given Request object."""
    def __init__(self, username):
        self.username = username

    def __call__(self, r):
        r.headers['X-Pizza'] = self.username
        return r

r = requests.get('http://pizzabin.org/admin', auth=PizzaAuth('kenneth'))
```

## Streaming

### Streaming Downloads

```python
r = requests.get('https://httpbin.org/stream/20', stream=True)

# Process line by line
for line in r.iter_lines():
    if line:  # Filter out keep-alive lines
        decoded_line = line.decode('utf-8')
        print(decoded_line)

# Process in chunks
for chunk in r.iter_content(chunk_size=1024):
    if chunk:
        print(chunk)
```

### Context Manager Usage

```python
with requests.get('https://httpbin.org/stream/20', stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode('utf-8'))
```

## Sessions

### Using Sessions for Persistent Parameters

```python
s = requests.Session()

# Set default headers
s.headers.update({'x-test': 'true'})

# Make requests using session
r = s.get('https://httpbin.org/headers')

# Session persists cookies
r = s.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
r = s.get('https://httpbin.org/cookies')  # Will include the cookie
```

### Transport Adapters

```python
import requests

class MyAdapter(requests.adapters.HTTPAdapter):
    pass

s = requests.Session()
s.mount('https://github.com/', MyAdapter())
```

## Proxies

### Basic Proxy Configuration

```python
# Using proxies parameter
proxies = {
    'http': 'http://10.1.1.10:3128',
    'https': 'http://10.1.1.10:1080'
}
r = requests.get('https://httpbin.org/get', proxies=proxies)

# With authentication
proxies = {
    'http': 'http://user:pass@10.1.1.10:3128'
}
```

### Environment Variables

```bash
export HTTP_PROXY="http://10.1.1.10:3128"
export HTTPS_PROXY="http://10.1.1.10:1080"
export ALL_PROXY="socks5://10.1.1.10:3434"
```

## Event Hooks

```python
def print_url(r, *args, **kwargs):
    print(r.url)

def record_hook(r, *args, **kwargs):
    # Custom logic here
    pass

# Single hook
r = requests.get('https://httpbin.org/', hooks={'response': print_url})

# Multiple hooks
r = requests.get('https://httpbin.org/', hooks={'response': [print_url, record_hook]})
```

## Error Handling

### Exception Types

```python
import requests

try:
    r = requests.get('http://invalid.url', timeout=1)
except requests.exceptions.ConnectionError:
    print("Connection error occurred")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.TooManyRedirects:
    print("Too many redirects")
except requests.exceptions.HTTPError:
    print("HTTP error occurred")
except requests.exceptions.RequestException:
    print("General request exception")

# Check status and raise for HTTP errors
r = requests.get('https://httpbin.org/status/404')
try:
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
```

## Advanced Usage

### Request and Response Objects

```python
from requests import Request, Session

s = requests.Session()

# Create and prepare a request
req = Request('POST', 'https://httpbin.org/post', 
              data={'key': 'value'}, 
              headers={'Custom-Header': 'value'})
prepped = req.prepare()

# Modify the prepared request if needed
prepped.body = 'modified data'

# Send the prepared request
r = s.send(prepped)
```

### SSL Certificate Verification

```python
# Disable SSL verification (not recommended for production)
r = requests.get('https://httpbin.org', verify=False)

# Custom CA bundle
r = requests.get('https://httpbin.org', verify='/path/to/certfile')

# Get default CA bundle path
from requests.utils import DEFAULT_CA_BUNDLE_PATH
print(DEFAULT_CA_BUNDLE_PATH)
```

## Debugging

### Enable Debug Logging

```python
import requests
import logging

# Enable debug logging for urllib3 (used by requests)
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
    
HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Now make requests to see detailed debug output
requests.get('https://httpbin.org/get')
```

## Common Patterns

### API Client Example

```python
import requests

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def get(self, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        return self.session.get(url, **kwargs)
    
    def post(self, endpoint, data=None, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        return self.session.post(url, json=data, **kwargs)

# Usage
client = APIClient('https://api.example.com', 'your-api-key')
response = client.get('users/123')
```

### Retry Logic with Exponential Backoff

```python
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Usage
session = requests_retry_session()
response = session.get('https://httpbin.org/status/500')
```