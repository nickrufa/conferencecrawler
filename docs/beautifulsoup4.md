# Beautiful Soup 4 Documentation

Beautiful Soup is a Python library for pulling data out of HTML and XML files, providing idiomatic ways to navigate, search, and modify the parse tree.

## Installation

```bash
pip install beautifulsoup4
```

Alternative installation methods:
```bash
easy_install beautifulsoup4
python setup.py install  # From source
```

## Basic Usage

### Initialize BeautifulSoup Object

```python
from bs4 import BeautifulSoup

# From string
soup = BeautifulSoup("<html>data</html>")

# From file
soup = BeautifulSoup(open("index.html"))

# With specific parser
soup = BeautifulSoup(html_doc, "html.parser")
```

### Parser Selection

Beautiful Soup supports multiple parsers:

```python
# Python's built-in HTML parser (default)
soup = BeautifulSoup(markup, "html.parser")

# lxml HTML parser (fast, lenient, external dependency)
soup = BeautifulSoup(markup, "lxml")

# lxml XML parser (very fast, XML-only)
soup = BeautifulSoup(markup, "xml")

# html5lib (pure Python, very lenient like web browsers)
soup = BeautifulSoup(markup, "html5lib")
```

### Basic Document Parsing

```python
from bs4 import BeautifulSoup

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
</body>
</html>
"""

soup = BeautifulSoup(html_doc, 'html.parser')

# Pretty print
print(soup.prettify())
```

## Navigation

### Basic Tag Access

```python
# Access tags directly
soup.title          # <title>The Dormouse's story</title>
soup.title.name     # 'title'
soup.title.string   # "The Dormouse's story"
soup.title.parent.name  # 'head'
soup.p              # First <p> tag
soup.p['class']     # ['title']
soup.a              # First <a> tag
```

### Navigation Attributes

```python
# Parent navigation
tag.parent          # Direct parent
tag.parents         # Generator of all ancestors

# Sibling navigation
tag.next_sibling    # Next sibling
tag.previous_sibling # Previous sibling
tag.next_siblings   # Generator of all next siblings
tag.previous_siblings # Generator of all previous siblings

# Element navigation (parse order)
tag.next_element    # Next parsed element
tag.previous_element # Previous parsed element
```

## Searching

### find_all() Method

```python
# Find all tags by name
soup.find_all('a')

# Find tags with attributes
soup.find_all('a', class_='sister')
soup.find_all('a', attrs={'class': 'sister'})
soup.find_all(id="link2")

# Using regular expressions
import re
soup.find_all(href=re.compile("elsie"))
soup.find_all(re.compile("^b"))  # Tags starting with 'b'

# Find with boolean (all tags)
soup.find_all(True)

# Limit results
soup.find_all('a', limit=2)

# Text content matching
soup.find_all(text="Elsie")
```

### find() Method

```python
# Find first occurrence
soup.find('a')
soup.find(id="link3")
```

### CSS Selectors

```python
# Basic selectors
soup.select('p.title')        # <p> with class 'title'
soup.select('p.story')        # <p> with class 'story'
soup.select('a[href]')        # <a> tags with href attribute

# Attribute selectors
soup.select('a[href="http://example.com/elsie"]')  # Exact match
soup.select('a[href^="http://"]')                   # Starts with
soup.select('a[href$="elsie"]')                     # Ends with
soup.select('a[href*=".com"]')                      # Contains

# Language attribute matching
soup.select('p[lang|=en]')    # lang="en" or lang="en-us", etc.
```

### Shorthand Syntax

```python
# These are equivalent
soup.find_all("a")
soup("a")

# For child elements
soup.title.find_all(text=True)
soup.title(text=True)
```

## Working with Tags and Attributes

### Tag Attributes

```python
tag = soup.b

# Access attributes (dictionary-like)
tag['class']        # Get attribute value
tag.attrs           # All attributes as dict

# Modify attributes
tag['class'] = 'verybold'
tag['id'] = 1

# Remove attributes
del tag['class']

# Safe access
tag.get('class')    # Returns None if not found

# Multi-valued attributes (like class)
css_soup = BeautifulSoup('<p class="body strikeout"></p>')
css_soup.p['class']  # ['body', 'strikeout']
```

### String Content

```python
# Access string content
tag.string           # NavigableString object
str(tag.string)      # Convert to Python string
unicode(tag.string)  # Convert to Unicode string

# Replace string content
tag.string.replace_with("New content")
```

## Modifying the Tree

### Creating New Elements

```python
# Create new tag
new_tag = soup.new_tag("a", href="http://www.example.com")
new_tag.string = "Link text."

# Create new string
new_string = soup.new_string(" there")

# Create comment
from bs4 import Comment
new_comment = soup.new_string("Nice to see you.", Comment)
```

### Adding Elements

```python
# Append to tag
tag.append("Hello")
tag.append(new_tag)
tag.append(new_string)
```

## Advanced Features

### SoupStrainer (Parsing Only What You Need)

```python
from bs4 import SoupStrainer

# Parse only 'a' tags
only_a_tags = SoupStrainer("a")
soup = BeautifulSoup(html_doc, "html.parser", parse_only=only_a_tags)

# Parse only tags with specific ID
only_tags_with_id_link2 = SoupStrainer(id="link2")

# Parse only short strings
def is_short_string(string):
    return len(string) < 10

only_short_strings = SoupStrainer(text=is_short_string)
```

### Encoding Handling

```python
# Beautiful Soup auto-detects encoding
soup = BeautifulSoup(markup)
print(soup.original_encoding)

# Specify encoding if detection fails
soup = BeautifulSoup(markup, from_encoding="iso-8859-8")

# Unicode, Dammit for encoding detection
from bs4 import UnicodeDammit

dammit = UnicodeDammit("Sacr\xe9 bleu!", ["latin-1", "iso-8859-1"])
print(dammit.unicode_markup)  # Sacré bleu!
print(dammit.original_encoding)  # latin-1
```

### Output Formatting

```python
# Pretty print
soup.prettify()

# Convert to string
str(soup)
unicode(soup)

# Output formatters for entities
from bs4.element import CData
soup.a.string = CData("one < three")
print(soup.a.prettify(formatter="xml"))
```

### Smart Quotes Conversion

```python
from bs4 import UnicodeDammit

markup = b"<p>I just \x93love\x94 Microsoft Word\x92s smart quotes</p>"

# Convert to ASCII quotes
unicode_markup = UnicodeDammit(markup, ["windows-1252"], 
                              smart_quotes_to="ascii").unicode_markup
# Result: '<p>I just "love" Microsoft Word\'s smart quotes</p>'

# Convert to XML entities
unicode_markup = UnicodeDammit(markup, ["windows-1252"], 
                              smart_quotes_to="xml").unicode_markup
# Result: '<p>I just &#x201C;love&#x201D; Microsoft Word&#x2019;s smart quotes</p>'
```

## HTML vs XML Parsing

```python
# HTML parsing (handles malformed HTML)
soup_html = BeautifulSoup("<a><b /></a>", "html.parser")

# XML parsing (stricter, preserves self-closing tags)
soup_xml = BeautifulSoup("<a><b /></a>", "xml")
```

## Common Patterns for Web Scraping

```python
from bs4 import BeautifulSoup
import requests

# Fetch and parse web page
response = requests.get('https://example.com')
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all links
links = soup.find_all('a', href=True)
for link in links:
    print(link['href'])

# Extract table data
table = soup.find('table')
rows = table.find_all('tr')
for row in rows:
    cells = row.find_all('td')
    print([cell.get_text(strip=True) for cell in cells])

# Extract form fields
form = soup.find('form')
inputs = form.find_all('input')
for input_tag in inputs:
    print(f"{input_tag.get('name')}: {input_tag.get('type')}")
```