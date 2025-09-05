import re
import csv
import PyPDF2
import os
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def parse_session(session_text):
    """Parse a single session block into structured data."""
    # Basic structure to capture
    session_data = {
        'session_id': None,
        'time': None,
        'hall': None,
        'session_type': None,
        'title': None,
        'chairs': [],
        'presentations': []
    }
    
    # Extract session ID, time, and hall
    session_header_pattern = r'([A-Z]+\d+)\s+(\d{2}:\d{2}\s*-\s*\d{2}:\d{2})\s+Hall\s+(\w+)'
    header_match = re.search(session_header_pattern, session_text)
    
    if header_match:
        session_data['session_id'] = header_match.group(1)
        session_data['time'] = header_match.group(2)
        session_data['hall'] = header_match.group(3)
    
    # Extract session type
    type_pattern = r'(Educational Session|Special Session|1-hour Oral Session|2-hour Symposium|Meet-the-Expert|ePoster Flash Session|Journal Session)'
    type_match = re.search(type_pattern, session_text)
    if type_match:
        session_data['session_type'] = type_match.group(1)
    
    # Extract title - usually the line after session type
    lines = session_text.split('\n')
    for i, line in enumerate(lines):
        if type_match and type_match.group(1) in line and i+1 < len(lines):
            title_candidate = lines[i+1].strip()
            if len(title_candidate) > 0 and not re.match(r'^Chairs', title_candidate):
                session_data['title'] = title_candidate
    
    # Extract chairs
    chairs_pattern = r'Chairs\s+(.*?)(?=\n\w+\d+\s+\d{2}:\d{2}|\n\S+\s+with:|\nCo-organised|\Z)'
    chairs_match = re.search(chairs_pattern, session_text, re.DOTALL)
    if chairs_match:
        chairs_text = chairs_match.group(1).strip()
        # Split by line breaks or commas
        raw_chairs = re.split(r'\n|,', chairs_text)
        for chair in raw_chairs:
            chair = chair.strip()
            if chair and not chair.startswith('Co-organised'):
                # Separate name from affiliation (in parentheses)
                name_match = re.match(r'(.*?)(?:\s+\(|$)', chair)
                if name_match:
                    session_data['chairs'].append(name_match.group(1).strip())
    
    # Extract presentations (ID, time, title, presenter)
    presentation_pattern = r'([A-Z]\d+)\s+(\d{2}:\d{2})\s+(.*?)([A-Za-zÀ-ÿ][\w\s.\'-]+(?:\([^)]+\)))'
    presentations = re.finditer(presentation_pattern, session_text)
    
    for p in presentations:
        presentation = {
            'id': p.group(1),
            'time': p.group(2),
            'title': p.group(3).strip(),
            'presenter': p.group(4).strip()
        }
        session_data['presentations'].append(presentation)
    
    return session_data

def extract_sessions(text):
    """Extract all sessions from the text."""
    # Pattern to identify session blocks
    session_pattern = r'([A-Z]+\d+)\s+(\d{2}:\d{2}\s*-\s*\d{2}:\d{2})\s+Hall\s+(\w+).*?(?=(?:[A-Z]+\d+)\s+\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\s+Hall|\Z)'
    
    sessions = []
    session_matches = re.finditer(session_pattern, text, re.DOTALL)
    
    for match in session_matches:
        session_text = match.group(0)
        session_data = parse_session(session_text)
        sessions.append(session_data)
    
    return sessions

def extract_date(text):
    """Extract the conference date from the text."""
    date_pattern = r'Friday,\s+(\d+\s+[A-Za-z]+\s+\d{4})'
    date_match = re.search(date_pattern, text)
    if date_match:
        return date_match.group(1)
    return None

def write_to_csv(sessions, output_file, date=None):
    """Write parsed session data to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Session ID', 'Time', 'Hall', 'Session Type', 
                     'Title', 'Chairs', 'Presentation ID', 'Presentation Time', 
                     'Presentation Title', 'Presenter']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for session in sessions:
            # If session has presentations
            if session['presentations']:
                for presentation in session['presentations']:
                    writer.writerow({
                        'Date': date,
                        'Session ID': session['session_id'],
                        'Time': session['time'],
                        'Hall': session['hall'],
                        'Session Type': session['session_type'],
                        'Title': session['title'],
                        'Chairs': '; '.join(session['chairs']),
                        'Presentation ID': presentation['id'],
                        'Presentation Time': presentation['time'],
                        'Presentation Title': presentation['title'],
                        'Presenter': presentation['presenter']
                    })
            else:
                # Write session without presentations
                writer.writerow({
                    'Date': date,
                    'Session ID': session['session_id'],
                    'Time': session['time'],
                    'Hall': session['hall'],
                    'Session Type': session['session_type'],
                    'Title': session['title'],
                    'Chairs': '; '.join(session['chairs']),
                    'Presentation ID': '',
                    'Presentation Time': '',
                    'Presentation Title': '',
                    'Presenter': ''
                })
                
def main():
    # Path to your PDF file
    pdf_path = input("Enter the path to your ESCMID conference PDF: ")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return
    
    # Output CSV path
    output_path = input("Enter the path for output CSV (default: escmid_sessions.csv): ") or "escmid_sessions.csv"
    
    # Extract text from PDF
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    
    # Extract date
    date = extract_date(text)
    print(f"Conference date: {date}")
    
    # Extract sessions
    print("Parsing sessions...")
    sessions = extract_sessions(text)
    print(f"Found {len(sessions)} sessions")
    
    # Write to CSV
    print(f"Writing data to {output_path}...")
    write_to_csv(sessions, output_path, date)
    
    print("Done!")

if __name__ == "__main__":
    main()