import pdfplumber
import os

pdf_path = "conference_sessions.pdf"
text_path = "conference_text.txt"

# Simple text extraction with page numbers
try:
    with open(text_path, "w", encoding="utf-8") as text_file:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text_file.write(f"\n\n---- PAGE {i+1} ----\n\n")
                text = page.extract_text() or "No text found on this page"
                text_file.write(text)
                text_file.write("\n")
    
    print(f"Successfully extracted text to {text_path}")
    print("You can now open this text file and copy/paste the relevant data into Excel manually")
    
except Exception as e:
    print(f"Error: {str(e)}")