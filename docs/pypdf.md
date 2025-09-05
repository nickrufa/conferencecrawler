# PyPDF Documentation

PyPDF (formerly PyPDF2) is a free, open-source, pure-Python library for manipulating PDF files, supporting splitting, merging, cropping, transforming, adding data, and extracting text and metadata. Note: PyPDF2 has been succeeded by PyPDF.

## Installation

### Basic Installation
```bash
pip install pypdf
```

### Installation with Optional Dependencies
```bash
# Install with all optional dependencies (recommended)
pip install pypdf[full]

# Install with cryptography support (for AES encryption/decryption)
pip install pypdf[crypto]

# Install with image extraction support
pip install pypdf[image]
```

### Alternative Installation Methods
```bash
# Install for current user only
pip install --user pypdf

# Install development version from Git
pip install git+https://github.com/py-pdf/pypdf.git
```

### System Dependencies
For JBIG2 image support on Ubuntu:
```bash
sudo apt-get install jbig2dec
```

## Basic Usage

### Reading PDF Files

```python
from pypdf import PdfReader

# Open a PDF file
reader = PdfReader("example.pdf")

# Get number of pages
print(f"Number of pages: {len(reader.pages)}")

# Access specific page
page = reader.pages[0]  # First page

# Get document metadata
print(reader.metadata)

# Check if PDF is encrypted
print(reader.is_encrypted)
```

### Writing PDF Files

```python
from pypdf import PdfWriter

# Create a new PDF writer
writer = PdfWriter()

# Add pages from reader
reader = PdfReader("source.pdf")
writer.append(reader)  # Add all pages

# Or add specific pages
for page_num in [0, 2, 4]:  # Add pages 1, 3, 5
    writer.add_page(reader.pages[page_num])

# Add a blank page
writer.add_blank_page(width=612, height=792)  # Letter size

# Save to file
with open("output.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Text Extraction

### Basic Text Extraction

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")
page = reader.pages[0]

# Extract all text
text = page.extract_text()
print(text)

# Extract text with specific orientation
text_upright = page.extract_text(0)  # Only upright text
text_rotated = page.extract_text((0, 90))  # Upright and 90° rotated

# Extract in layout mode (preserves formatting)
text_layout = page.extract_text(extraction_mode="layout")

# Layout mode options
text_compact = page.extract_text(
    extraction_mode="layout", 
    layout_mode_space_vertically=False
)
```

### Advanced Text Extraction with Visitor Functions

```python
from pypdf import PdfReader

def visitor_body(text, cm, tm, font_dict, font_size):
    """Extract text only from body area (exclude headers/footers)"""
    y = cm[5]  # Get y-coordinate
    if 50 < y < 720:  # Only text in body area
        parts.append(text)

reader = PdfReader("example.pdf")
page = reader.pages[0]
parts = []

page.extract_text(visitor_text=visitor_body)
body_text = "".join(parts)
print(body_text)
```

## PDF Merging and Splitting

### Merging PDFs

```python
from pypdf import PdfWriter, PdfReader

def merge_pdfs(pdf_list, output_path):
    writer = PdfWriter()
    
    for pdf_path in pdf_list:
        reader = PdfReader(pdf_path)
        writer.append(reader)
    
    with open(output_path, "wb") as output_file:
        writer.write(output_file)

# Usage
pdf_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
merge_pdfs(pdf_files, "merged.pdf")
```

### Splitting PDFs

```python
from pypdf import PdfReader, PdfWriter

def split_pdf(input_path, output_dir):
    reader = PdfReader(input_path)
    
    for page_num, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        
        output_path = f"{output_dir}/page_{page_num + 1}.pdf"
        with open(output_path, "wb") as output_file:
            writer.write(output_path)

# Usage
split_pdf("large_document.pdf", "pages/")
```

## PDF Transformations

### Page Rotation

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Rotate page 90 degrees clockwise
    page.rotate_clockwise(90)
    writer.add_page(page)

with open("rotated.pdf", "wb") as output_file:
    writer.write(output_file)
```

### Scaling and Cropping

```python
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

reader = PdfReader("document.pdf")
writer = PdfWriter()
page = reader.pages[0]

# Scale page (0.5 = 50% of original size)
page.scale_by(0.5)

# Crop page (left, bottom, right, top)
crop_box = RectangleObject([50, 50, 500, 700])
page.cropbox = crop_box

# Manual adjustment of all page boxes
mediabox = page.mediabox
page.mediabox = RectangleObject((mediabox.left, mediabox.bottom, mediabox.right, mediabox.top))
page.cropbox = RectangleObject((mediabox.left, mediabox.bottom, mediabox.right, mediabox.top))

writer.add_page(page)

with open("modified.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Working with Forms

### Reading Form Data

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")

# Get all form fields
fields = reader.get_fields()
print("All fields:", fields)

# Get text fields only
text_fields = reader.get_form_text_fields()
print("Text fields:", text_fields)  # Returns dict like {"field_name": "value"}
```

### Filling Forms

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

# Copy pages
writer.append(reader)

# Update form field values
writer.update_page_form_field_values(
    writer.pages[0],
    {"field_name": "new_value", "another_field": "another_value"}
)

with open("filled_form.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Annotations

### Reading Annotations

```python
from pypdf import PdfReader

reader = PdfReader("annotated.pdf")

for page in reader.pages:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            subtype = obj["/Subtype"]
            
            if subtype == "/Text":
                print(f"Text annotation: {obj['/Contents']}")
            elif subtype == "/FreeText":
                print(f"Free text: {obj['/Contents']}")
```

### Adding Annotations

```python
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText, Link

reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.add_page(reader.pages[0])

# Add free text annotation
free_text = FreeText(
    text="Hello World\nSecond line",
    rect=(50, 550, 200, 650),  # (left, bottom, right, top)
    font="Arial",
    font_size="14pt",
    font_color="ff0000",  # Red
    background_color="ffff00",  # Yellow background
    border_color="0000ff"  # Blue border
)

writer.add_annotation(page_number=0, annotation=free_text)

# Add URL link annotation
link = Link(
    rect=(50, 400, 200, 450),
    url="https://example.com"
)

writer.add_annotation(page_number=0, annotation=link)

with open("annotated.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Encryption and Security

### Checking Encryption Status

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")

if reader.is_encrypted:
    print("PDF is encrypted")
    # Try to decrypt with password
    if reader.decrypt("password"):
        print("Successfully decrypted")
    else:
        print("Failed to decrypt")
```

### Encrypting PDFs

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

# Copy all pages
writer.append(reader)

# Encrypt with passwords
writer.encrypt(
    user_password="user_pass",
    owner_password="owner_pass",
    use_128bit=True
)

with open("encrypted.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Watermarks and Stamps

### Adding Watermarks

```python
from pypdf import PdfReader, PdfWriter, Transformation
from PIL import Image
from io import BytesIO

def image_to_pdf(image_path):
    """Convert image to PDF for stamping"""
    img = Image.open(image_path)
    img_as_pdf = BytesIO()
    img.save(img_as_pdf, "pdf")
    return PdfReader(img_as_pdf)

def add_watermark(content_pdf, watermark_image, output_pdf):
    # Convert image to PDF
    watermark_pdf = image_to_pdf(watermark_image)
    watermark_page = watermark_pdf.pages[0]
    
    # Process content PDF
    reader = PdfReader(content_pdf)
    writer = PdfWriter()
    
    for page in reader.pages:
        # Merge watermark onto each page
        page.merge_transformed_page(
            watermark_page,
            Transformation()  # Can add scaling, rotation, translation
        )
        writer.add_page(page)
    
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

# Usage
add_watermark("document.pdf", "watermark.png", "watermarked.pdf")
```

## Working with Bookmarks/Outlines

### Reading Bookmarks

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
outlines = reader.get_outlines()

def print_bookmarks(bookmarks, indent=0):
    for bookmark in bookmarks:
        if isinstance(bookmark, list):
            print_bookmarks(bookmark, indent + 1)
        else:
            print("  " * indent + bookmark.title)

print_bookmarks(outlines)
```

### Adding Bookmarks

```python
from pypdf import PdfWriter, PdfReader

reader = PdfReader("document.pdf")
writer = PdfWriter()

# Copy pages
for page in reader.pages:
    writer.add_page(page)

# Add bookmarks
parent_bookmark = writer.add_bookmark("Chapter 1", 0)  # Page 0
writer.add_bookmark("Section 1.1", 1, parent=parent_bookmark)  # Page 1
writer.add_bookmark("Chapter 2", 5)  # Page 5

with open("bookmarked.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Memory Operations (BytesIO)

### Working with In-Memory PDFs

```python
from pypdf import PdfReader, PdfWriter
from io import BytesIO

# Read from memory
with open("example.pdf", "rb") as file:
    pdf_bytes = BytesIO(file.read())

reader = PdfReader(pdf_bytes)

# Write to memory
writer = PdfWriter()
writer.append(reader)

output_bytes = BytesIO()
writer.write(output_bytes)

# Get bytes data
pdf_data = output_bytes.getvalue()

# Save from memory
with open("output.pdf", "wb") as file:
    file.write(pdf_data)
```

## Advanced Features

### Custom Transformations

```python
from pypdf import PdfReader, PdfWriter, Transformation

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Create transformation matrix
    transformation = Transformation().rotate(45).scale(0.8).translate(100, 50)
    
    # Apply transformation
    page.add_transformation(transformation)
    writer.add_page(page)

with open("transformed.pdf", "wb") as output_file:
    writer.write(output_file)
```

### JavaScript in PDFs

```python
from pypdf import PdfWriter

writer = PdfWriter()
# Add pages...

# Add JavaScript
js_code = """
this.print({
    bUI: false,
    bSilent: true,
    bShrinkToFit: true
});
"""
writer.addJS(js_code)

with open("auto_print.pdf", "wb") as output_file:
    writer.write(output_file)
```

## Error Handling and Debugging

### Handling Encrypted PDFs

```python
from pypdf import PdfReader
from pypdf.errors import PdfReadError

try:
    reader = PdfReader("document.pdf")
    
    if reader.is_encrypted:
        # Try common passwords
        passwords = ["", "password", "123456"]
        for pwd in passwords:
            if reader.decrypt(pwd):
                print(f"Decrypted with password: {pwd}")
                break
        else:
            print("Could not decrypt PDF")
            exit(1)
    
    # Process PDF...
    
except PdfReadError as e:
    print(f"Error reading PDF: {e}")
```

### Logging Configuration

```python
import logging
from pypdf import PdfReader

# Configure pypdf logging
logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)  # Only show errors

# Or set to DEBUG for verbose output
# logger.setLevel(logging.DEBUG)

reader = PdfReader("document.pdf")
```

## Migration from PyPDF2

### Key Changes (PyPDF2 1.x to PyPDF 2.x)

#### Class Renamings:
```python
# Old (PyPDF2 1.x)
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger

# New (PyPDF 2.x)
from pypdf import PdfReader, PdfWriter, PdfMerger
```

#### Method Renamings:
```python
# Old
reader.getPage(0)
reader.getNumPages()
writer.addPage(page)

# New
reader.pages[0]
len(reader.pages)
writer.add_page(page)
```

#### Property Access:
```python
# Old
reader.getDocumentInfo()
reader.isEncrypted

# New
reader.metadata
reader.is_encrypted
```

## Common Patterns

### PDF Processing Pipeline

```python
from pypdf import PdfReader, PdfWriter

def process_pdf(input_path, output_path):
    """Complete PDF processing example"""
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for i, page in enumerate(reader.pages):
        # Handle rotation if needed
        if page.rotation != 0:
            page.transfer_rotation_to_content()
        
        # Add page number watermark
        # (implementation details omitted for brevity)
        
        writer.add_page(page)
    
    # Add metadata
    writer.add_metadata({
        "/Title": "Processed Document",
        "/Author": "PyPDF Script",
        "/Creator": "Python PyPDF"
    })
    
    with open(output_path, "wb") as output_file:
        writer.write(output_file)

# Usage
process_pdf("input.pdf", "processed.pdf")
```

### Batch PDF Processing

```python
import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter

def batch_process(input_dir, output_dir, operation):
    """Process all PDFs in directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for pdf_file in input_path.glob("*.pdf"):
        try:
            reader = PdfReader(pdf_file)
            writer = PdfWriter()
            
            # Apply operation
            operation(reader, writer)
            
            output_file = output_path / pdf_file.name
            with open(output_file, "wb") as f:
                writer.write(f)
                
            print(f"Processed: {pdf_file.name}")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")

def rotate_pages(reader, writer):
    """Example operation: rotate all pages 90 degrees"""
    for page in reader.pages:
        page.rotate_clockwise(90)
        writer.add_page(page)

# Usage
batch_process("input_pdfs/", "output_pdfs/", rotate_pages)
```

This documentation covers the most common use cases for PyPDF. For advanced features and detailed API documentation, refer to the official PyPDF documentation and examples.