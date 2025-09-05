# pdfplumber Documentation

pdfplumber is a Python library for extracting detailed information from PDFs, including text, characters, rectangles, and lines, with features for table extraction and visual debugging.

## Installation

```bash
pip install pdfplumber
```

## Basic Usage

### Opening PDF Files

```python
import pdfplumber

# Open a PDF file
with pdfplumber.open("path/to/file.pdf") as pdf:
    first_page = pdf.pages[0]
    print(first_page.chars[0])

# With password protection
with pdfplumber.open("protected.pdf", password="secret") as pdf:
    # Process PDF...
    pass

# With custom layout analysis parameters
laparams = {"detect_vertical": True}
with pdfplumber.open("document.pdf", laparams=laparams) as pdf:
    # Process PDF...
    pass
```

### Accessing PDF Structure

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    # Get metadata
    print(pdf.metadata)
    
    # Get number of pages
    print(f"Number of pages: {len(pdf.pages)}")
    
    # Access specific page
    page = pdf.pages[0]
    
    # Close when done (automatic with context manager)
    pdf.close()
```

## Text Extraction

### Basic Text Extraction

```python
with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    
    # Extract all text from page
    text = page.extract_text()
    print(text)
    
    # Extract with custom tolerances
    text = page.extract_text(x_tolerance=3, y_tolerance=3)
    
    # Extract with layout preservation
    text = page.extract_text(layout=True)
```

### Simple Text Extraction

```python
# Faster, simplified text extraction
page = pdf.pages[0]
text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
```

### Word Extraction

```python
# Extract words with bounding boxes
words = page.extract_words(
    x_tolerance=3,
    y_tolerance=3,
    keep_blank_chars=False,
    use_text_flow=False,
    return_chars=False,
    split_at_punctuation=False
)

for word in words[:5]:
    print(f"Word: '{word['text']}' at ({word['x0']}, {word['top']})")
```

### Text Search

```python
# Search for patterns in text
matches = page.search(
    pattern=r"\d{4}-\d{2}-\d{2}",  # Date pattern
    regex=True,
    case=True,
    return_groups=True,
    return_chars=True
)

for match in matches:
    print(f"Found: {match['text']} at ({match['x0']}, {match['top']})")
```

## Character-Level Analysis

### Accessing Characters

```python
page = pdf.pages[0]

# Get all characters
chars = page.chars

# Examine first character
first_char = chars[0]
print(f"Character: '{first_char['text']}'")
print(f"Font: {first_char['fontname']}")
print(f"Size: {first_char['size']}")
print(f"Position: ({first_char['x0']}, {first_char['top']})")
print(f"Color: {first_char['stroking_color']}")
```

### Character Transformation Matrix

```python
from pdfplumber.ctm import CTM

# Get character transformation matrix
char = pdf.pages[0].chars[3]
char_ctm = CTM(*char["matrix"])

# Get rotation
rotation = char_ctm.skew_x
print(f"Character rotation: {rotation}")
```

## Table Extraction

### Basic Table Extraction

```python
with pdfplumber.open("table_document.pdf") as pdf:
    page = pdf.pages[0]
    
    # Extract the largest table
    table = page.extract_table()
    
    # Print table data
    for row in table[:5]:  # First 5 rows
        print(row)
    
    # Extract all tables
    tables = page.extract_tables()
    print(f"Found {len(tables)} tables")
```

### Custom Table Settings

```python
# Define custom table extraction settings
table_settings = {
    "vertical_strategy": "lines",      # Use detected lines
    "horizontal_strategy": "text",     # Use text alignment
    "snap_tolerance": 3,
    "snap_y_tolerance": 5,
    "intersection_x_tolerance": 15,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1
}

# Extract table with custom settings
table = page.extract_table(table_settings)
```

### Advanced Table Detection

```python
# Find table objects (more detailed)
tables = page.find_tables(table_settings)

for table in tables:
    print(f"Table with {len(table.rows)} rows and {len(table.cells)} cells")
    print(f"Bounding box: {table.bbox}")
    
    # Extract table data
    data = table.extract()
    
    # Access specific cells
    for row in table.rows[:3]:
        for cell in row.cells:
            print(f"Cell: {cell.text}")

# Find the largest table only
largest_table = page.find_table(table_settings)
```

## Visual Debugging

### Creating Page Images

```python
# Convert page to image
page = pdf.pages[0]
im = page.to_image(resolution=150)

# Display in Jupyter
im  # Automatically displays

# Save image
im.save("page_image.png", format="PNG")

# Show in image viewer
im.show()
```

### Drawing on Images

```python
im = page.to_image()

# Draw detected lines
im.draw_lines(page.lines, stroke="red", stroke_width=2)

# Draw rectangles
im.draw_rects(page.rects, fill="blue", stroke="green")

# Draw circles at character positions
char_centers = [(char['x0'], char['top']) for char in page.chars[:10]]
im.draw_circles(char_centers, radius=3, fill="yellow")

# Draw vertical and horizontal lines
im.draw_vline(100, stroke="purple", stroke_width=1)
im.draw_hline(200, stroke="orange", stroke_width=1)

# Reset drawings
im.reset()

# Copy image
im_copy = im.copy()
```

### Table Debugging

```python
# Debug table finder
im = page.to_image()
im.debug_tablefinder(table_settings)

# This overlays:
# - Detected lines (red)
# - Intersections (circles) 
# - Tables (light blue)
```

## Working with Different Object Types

### Lines

```python
page = pdf.pages[0]

# Access all lines
lines = page.lines

for line in lines[:5]:
    print(f"Line from ({line['x0']}, {line['y0']}) to ({line['x1']}, {line['y1']})")
    print(f"Width: {line['linewidth']}, Color: {line['stroking_color']}")
```

### Rectangles

```python
# Access rectangles
rects = page.rects

for rect in rects[:5]:
    print(f"Rectangle: {rect['width']}x{rect['height']} at ({rect['x0']}, {rect['top']})")
    print(f"Fill: {rect['fill']}, Stroke: {rect['stroke']}")
```

### Curves

```python
# Access curves
curves = page.curves

for curve in curves[:3]:
    print(f"Curve with {len(curve['pts'])} points")
    print(f"Points: {curve['pts']}")
    print(f"Path: {curve['path']}")
```

### Images

```python
# Access images
images = page.images

for image in images:
    print(f"Image: {image['width']}x{image['height']}")
    print(f"Color space: {image['colorspace']}")
    print(f"Bits: {image['bits']}")
```

## Advanced Features

### Structure Tree Analysis

```python
# Access structure tree (tagged PDFs)
with pdfplumber.open("tagged_document.pdf") as pdf:
    page = pdf.pages[0]
    
    for element in page.structure_tree:
        print(f"Element type: {element['type']}")
        print(f"Marked content IDs: {element['mcids']}")
        
        # Access child elements
        for child in element.children:
            print(f"  Child type: {child['type']}")
```

### Form Field Extraction

```python
from pdfplumber.utils.pdfinternals import resolve_and_decode, resolve

def extract_form_fields(pdf):
    """Extract form field names and values"""
    form_data = []
    
    def parse_field_helper(form_data, field, prefix=None):
        resolved_field = field.resolve()
        field_name = '.'.join(filter(lambda x: x, [prefix, resolve_and_decode(resolved_field.get("T"))]))
        
        if "Kids" in resolved_field:
            for kid_field in resolved_field["Kids"]:
                parse_field_helper(form_data, kid_field, prefix=field_name)
        
        if "T" in resolved_field or "TU" in resolved_field:
            alternate_name = resolve_and_decode(resolved_field.get("TU")) if resolved_field.get("TU") else None
            field_value = resolve_and_decode(resolved_field["V"]) if 'V' in resolved_field else None
            form_data.append([field_name, alternate_name, field_value])
    
    if "AcroForm" in pdf.doc.catalog:
        fields = resolve(resolve(pdf.doc.catalog["AcroForm"])["Fields"])
        for field in fields:
            parse_field_helper(form_data, field)
    
    return form_data

# Usage
with pdfplumber.open("form_document.pdf") as pdf:
    form_fields = extract_form_fields(pdf)
    for field_name, alt_name, value in form_fields:
        print(f"Field: {field_name} = {value}")
```

### Coordinate Conversion

```python
# Convert from PDF coordinate space to pdfplumber coordinate space
def convert_bbox_coordinates(element, page):
    x0, y0, x1, y1 = element['attributes']['BBox']
    top = page.height - y1
    bottom = page.height - y0
    doctop = page.initial_doctop + top
    return (x0, top, x1, bottom)
```

## Working with Data

### Converting to DataFrames

```python
import pandas as pd

# Extract table and convert to DataFrame
table = page.extract_table()
if table:
    df = pd.DataFrame(table[1:], columns=table[0])  # First row as headers
    
    # Clean data
    for column in ["Date", "Amount"]:
        if column in df.columns:
            df[column] = df[column].str.replace(" ", "")
    
    print(df.head())
```

### Data Processing Example

```python
# Define column names
COLUMNS = [
    "state", "permit", "handgun", "long_gun", "other", 
    "multiple", "admin", "totals"
]

def parse_value(i, x):
    """Parse cell values"""
    if i == 0:  # State name
        return x
    if x == "":
        return None
    return int(x.replace(",", ""))

def parse_row(row):
    """Convert row to dictionary"""
    return {COLUMNS[i]: parse_value(i, cell) 
            for i, cell in enumerate(row)}

# Process table
table = page.extract_table()
data = [parse_row(row) for row in table[1:]]  # Skip header

# Sort by a column
sorted_data = sorted(data, key=lambda x: x.get("handgun", 0), reverse=True)

for row in sorted_data[:5]:
    print(f"{row['state']}: {row['handgun']:,d} handgun checks")
```

## PDF Repair

### Repair on the Fly

```python
# Repair PDF while opening (not saved to disk)
with pdfplumber.open("corrupted.pdf", repair=True) as pdf:
    text = pdf.pages[0].extract_text()
    print(text)
```

### Repair and Save

```python
# Repair and save to new file
import pdfplumber

pdfplumber.repair("corrupted.pdf", outfile="repaired.pdf")

# Now work with the repaired file
with pdfplumber.open("repaired.pdf") as pdf:
    text = pdf.pages[0].extract_text()
    print(text)
```

## Command Line Interface

### Basic Usage

```bash
# Extract to CSV
pdfplumber document.pdf > output.csv

# Extract to JSON (more detailed)
pdfplumber document.pdf --format json > output.json

# Extract plain text
pdfplumber document.pdf --format text > output.txt
```

### Advanced CLI Options

```bash
# Extract specific pages
pdfplumber document.pdf --pages 1 3-5 10

# Extract specific object types
pdfplumber document.pdf --types char rect line

# Custom layout parameters
pdfplumber document.pdf --laparams '{"detect_vertical": true}'

# Set precision for floating-point numbers
pdfplumber document.pdf --precision 2
```

## Performance Tips

### Processing Large PDFs

```python
# Process pages individually to manage memory
with pdfplumber.open("large_document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"Processing page {i+1}")
        
        # Extract what you need
        text = page.extract_text()
        tables = page.extract_tables()
        
        # Process data immediately
        # ... your processing logic ...
        
        # Clear page from memory if needed
        # (pages are automatically cleaned up)
```

### Optimizing Table Extraction

```python
# Use appropriate strategies for your document
fast_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "edge_min_length": 3
}

# For documents with inconsistent formatting
robust_settings = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3
}
```

## Error Handling

### Common Issues

```python
import pdfplumber

try:
    with pdfplumber.open("document.pdf") as pdf:
        for page in pdf.pages:
            try:
                text = page.extract_text()
                tables = page.extract_tables()
                
            except Exception as e:
                print(f"Error processing page {page.page_number}: {e}")
                continue
                
except FileNotFoundError:
    print("PDF file not found")
except Exception as e:
    print(f"Error opening PDF: {e}")
```

### Handling Malformed PDFs

```python
# Try repair first
try:
    with pdfplumber.open("problematic.pdf", repair=True) as pdf:
        text = pdf.pages[0].extract_text()
except Exception as e:
    print(f"Even repair couldn't fix this PDF: {e}")
    
    # Try with ghostscript repair
    # gs -o repaired.pdf -sDEVICE=pdfwrite original.pdf
```

## Comparison with Other Libraries

### pdfplumber vs PyPDF2/pypdf
- **pdfplumber**: Better for text extraction, table detection, visual debugging
- **PyPDF2/pypdf**: Better for PDF manipulation (merging, splitting, rotating)

### pdfplumber vs pymupdf
- **pdfplumber**: Pure Python, better debugging tools, more detailed object access
- **pymupdf**: Much faster, requires non-Python dependencies, less detailed analysis

### pdfplumber vs camelot/tabula-py
- **pdfplumber**: More flexible, visual debugging, handles various PDF structures
- **camelot/tabula-py**: Specialized for table extraction, may be better for complex tables

## Common Patterns

### Conference Paper Processing

```python
def extract_conference_data(pdf_path):
    """Extract structured data from conference PDFs"""
    with pdfplumber.open(pdf_path) as pdf:
        extracted_data = []
        
        for page in pdf.pages:
            # Extract text
            text = page.extract_text()
            
            # Look for specific patterns
            title_match = re.search(r'^(.+?)\n', text)
            author_match = re.search(r'Authors?:\s*(.+?)\n', text)
            
            # Extract tables if present
            tables = page.extract_tables()
            
            page_data = {
                'page_number': page.page_number,
                'title': title_match.group(1) if title_match else None,
                'authors': author_match.group(1) if author_match else None,
                'tables': tables,
                'full_text': text
            }
            
            extracted_data.append(page_data)
    
    return extracted_data
```

### Batch Processing

```python
import os
from pathlib import Path

def process_pdf_directory(input_dir, output_dir):
    """Process all PDFs in a directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for pdf_file in input_path.glob("*.pdf"):
        try:
            print(f"Processing {pdf_file.name}")
            
            with pdfplumber.open(pdf_file) as pdf:
                # Extract data
                all_text = ""
                all_tables = []
                
                for page in pdf.pages:
                    all_text += page.extract_text() + "\n\n"
                    all_tables.extend(page.extract_tables())
                
                # Save results
                text_file = output_path / f"{pdf_file.stem}.txt"
                with open(text_file, 'w') as f:
                    f.write(all_text)
                
                # Save tables as CSV
                if all_tables:
                    import csv
                    csv_file = output_path / f"{pdf_file.stem}_tables.csv"
                    with open(csv_file, 'w', newline='') as f:
                        writer = csv.writer(f)
                        for table in all_tables:
                            writer.writerows(table)
                            writer.writerow([])  # Separator
                            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

# Usage
process_pdf_directory("input_pdfs/", "output_data/")
```

This documentation covers the essential features of pdfplumber for PDF text extraction, table detection, and visual debugging - all crucial for processing conference documents and extracting structured data.