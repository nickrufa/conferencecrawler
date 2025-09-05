import pandas as pd
import csv
import re
import os
import subprocess

def extract_from_pdf(pdf_file, output_dir="./"):
    """
    Extract content from PDF file using pdftotext
    
    Parameters:
    pdf_file (str): Path to the PDF file
    output_dir (str): Directory to save extracted files
    """
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Output files
    text_file = os.path.join(output_dir, "conference_text.txt")
    
    # Extract text without layout preservation
    try:
        subprocess.run(["pdftotext", "-raw", pdf_file, text_file], check=True)
        print(f"Successfully extracted text to {text_file}")
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None
    
    return text_file

def clean_text(text):
    """Clean text to avoid illegal characters"""
    if not isinstance(text, str):
        return ""
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    return text.strip()

def extract_data_by_line(text_file, output_dir="./"):
    """
    Extract data line by line, focusing on presentation and session IDs
    """
    if not os.path.exists(text_file):
        print(f"Error: {text_file} not found")
        return None
    
    presentations_csv = os.path.join(output_dir, "manual_presentations.csv")
    sessions_csv = os.path.join(output_dir, "manual_sessions.csv")
    
    # Lists to store our data
    presentations = []
    sessions = []
    current_session = None
    
    # Read the file line by line
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Process each line
    for i, line in enumerate(lines):
        clean_line = clean_text(line)
        
        # Skip empty lines
        if not clean_line:
            continue
        
        # Check for session headers first (they have specific patterns)
        session_match = re.search(r'((?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+)\s+(\d{2}:\d{2})(?:\s*-\s*(\d{2}:\d{2}))?\s+Hall\s+(\w+)', clean_line)
        
        if session_match:
            # Found a session header
            session_id = session_match.group(1)
            start_time = session_match.group(2)
            end_time = session_match.group(3) if session_match.group(3) else ""
            hall = session_match.group(4)
            
            # Get session type and title from following lines
            session_type = ""
            session_title = ""
            
            # Look ahead at next lines for session type and title
            for j in range(1, 5):  # Look at next few lines
                if i + j < len(lines):
                    next_line = clean_text(lines[i + j])
                    
                    if "Session" in next_line:
                        session_type = next_line
                    elif next_line and session_type and not session_title:
                        # First non-empty line after session type is likely the title
                        session_title = next_line
            
            # Create session record
            current_session = {
                'Session ID': session_id,
                'Start Time': start_time,
                'End Time': end_time,
                'Hall': hall,
                'Session Type': session_type,
                'Session Title': session_title,
                'Chairs': ""  # We'll try to fill this in later
            }
            
            sessions.append(current_session)
            continue
        
        # Look for chairs
        if current_session and clean_line.startswith("Chairs"):
            chairs_text = clean_line[6:].strip()  # Remove "Chairs" prefix
            
            # There may be multiple lines of chairs
            chair_lines = [chairs_text]
            j = i + 1
            while j < len(lines) and not re.match(r'[WOMEFSL]\d{4}', lines[j]) and not re.match(r'(?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+', lines[j]):
                chair_line = clean_text(lines[j])
                if chair_line and not chair_line.startswith("Co-organised"):
                    chair_lines.append(chair_line)
                j += 1
            
            current_session['Chairs'] = " ".join(chair_lines)
            continue
        
        # Check for presentation IDs
        pres_match = re.search(r'([WOMEFSL]\d{4})\s+(\d{2}:\d{2})\s+(.*)', clean_line)
        
        if pres_match and current_session:
            pres_id = pres_match.group(1)
            pres_time = pres_match.group(2)
            pres_content = pres_match.group(3)
            
            # Presentations often span multiple lines
            # Collect lines until we hit another presentation ID or session ID
            full_content = [pres_content]
            j = i + 1
            while j < len(lines):
                next_line = clean_text(lines[j])
                if re.match(r'[WOMEFSL]\d{4}', next_line) or re.match(r'(?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+', next_line):
                    break
                if next_line and not next_line.startswith("Co-organised"):
                    full_content.append(next_line)
                j += 1
            
            # Join the content
            full_content = " ".join(full_content)
            
            # Try to separate title, speaker, and location
            title = full_content
            speaker = ""
            location = ""
            
            # Look for typical pattern: Title Speaker (Location)
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\(([^)]+)\)$', full_content)
            if location_match:
                speaker = location_match.group(1).strip()
                location = location_match.group(2).strip()
                title = full_content[:full_content.find(speaker)].strip()
            
            presentations.append({
                'Session ID': current_session['Session ID'],
                'Presentation ID': pres_id,
                'Time': pres_time,
                'Title': title,
                'Speaker': speaker,
                'Location': location
            })
    
    # Write to CSV files
    with open(sessions_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Session ID', 'Start Time', 'End Time', 'Hall', 
                                              'Session Type', 'Session Title', 'Chairs'])
        writer.writeheader()
        writer.writerows(sessions)
    
    with open(presentations_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Session ID', 'Presentation ID', 'Time', 
                                              'Title', 'Speaker', 'Location'])
        writer.writeheader()
        writer.writerows(presentations)
    
    print(f"Extracted {len(sessions)} sessions to {sessions_csv}")
    print(f"Extracted {len(presentations)} presentations to {presentations_csv}")
    
    return sessions_csv, presentations_csv

def convert_to_sql(sessions_csv, presentations_csv, output_dir="./"):
    """
    Convert the CSV data to SQL insert statements
    """
    sql_file = os.path.join(output_dir, "conference_data.sql")
    
    try:
        # Read the CSV files
        sessions_df = pd.read_csv(sessions_csv)
        presentations_df = pd.read_csv(presentations_csv)
        
        with open(sql_file, 'w', encoding='utf-8') as f:
            # Write SQL header
            f.write("-- ESCMID Global 2025 Conference Program\n")
            f.write("-- Generated SQL Insert Statements\n\n")
            
            # Create sessions table
            f.write("-- Sessions Table\n")
            f.write("CREATE TABLE IF NOT EXISTS sessions (\n")
            f.write("    id VARCHAR(10) PRIMARY KEY,\n")
            f.write("    start_time VARCHAR(5),\n")
            f.write("    end_time VARCHAR(5),\n")
            f.write("    hall VARCHAR(10),\n")
            f.write("    session_type TEXT,\n")
            f.write("    title TEXT,\n")
            f.write("    chairs TEXT\n")
            f.write(");\n\n")
            
            # Write session insert statements
            f.write("-- Session Data\n")
            for _, row in sessions_df.iterrows():
                f.write(f"INSERT INTO sessions VALUES (\n")
                f.write(f"    '{row['Session ID']}',\n")
                f.write(f"    '{row['Start Time']}',\n")
                f.write(f"    '{row['End Time']}',\n")
                f.write(f"    '{row['Hall']}',\n")
                f.write(f"    '{row['Session Type'].replace(\"'\", \"''\")}',\n")
                f.write(f"    '{row['Session Title'].replace(\"'\", \"''\")}',\n")
                f.write(f"    '{row['Chairs'].replace(\"'\", \"''\")}'\n")
                f.write(f");\n")
            
            # Create presentations table
            f.write("\n-- Presentations Table\n")
            f.write("CREATE TABLE IF NOT EXISTS presentations (\n")
            f.write("    id VARCHAR(10) PRIMARY KEY,\n")
            f.write("    session_id VARCHAR(10),\n")
            f.write("    presentation_time VARCHAR(5),\n")
            f.write("    title TEXT,\n")
            f.write("    speaker TEXT,\n")
            f.write("    location TEXT,\n")
            f.write("    FOREIGN KEY (session_id) REFERENCES sessions(id)\n")
            f.write(");\n\n")
            
            # Write presentation insert statements
            f.write("-- Presentation Data\n")
            for _, row in presentations_df.iterrows():
                f.write(f"INSERT INTO presentations VALUES (\n")
                f.write(f"    '{row['Presentation ID']}',\n")
                f.write(f"    '{row['Session ID']}',\n")
                f.write(f"    '{row['Time']}',\n")
                f.write(f"    '{row['Title'].replace(\"'\", \"''\")}',\n")
                f.write(f"    '{row['Speaker'].replace(\"'\", \"''\")}',\n")
                f.write(f"    '{row['Location'].replace(\"'\", \"''\")}'\n")
                f.write(f");\n")
        
        print(f"SQL statements saved to {sql_file}")
        return sql_file
        
    except Exception as e:
        print(f"Error converting to SQL: {str(e)}")
        return None

def process_pdf(pdf_file):
    """
    Process a PDF file to extract conference program data
    """
    print(f"Processing {pdf_file}...")
    
    # Extract text from PDF
    text_file = extract_from_pdf(pdf_file)
    if not text_file:
        return
    
    # Process the text file line by line
    sessions_csv, presentations_csv = extract_data_by_line(text_file)
    if not sessions_csv or not presentations_csv:
        return
    
    # Convert to SQL (optional)
    sql_file = convert_to_sql(sessions_csv, presentations_csv)
    
    print("\nProcessing complete!")
    print(f"Text extraction: {text_file}")
    print(f"Sessions CSV: {sessions_csv}")
    print(f"Presentations CSV: {presentations_csv}")
    if sql_file:
        print(f"SQL statements: {sql_file}")

if __name__ == "__main__":
    print("Manual PDF Data Extraction Script")
    print("--------------------------------")
    print("This script extracts conference program data from PDF files")
    print("It processes the text line by line to identify sessions and presentations")
    
    pdf_file = input("Enter path to PDF file: ")
    
    if os.path.exists(pdf_file):
        process_pdf(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found")
