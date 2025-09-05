import re
import pandas as pd
import os

input_file = "conference_text.txt"
output_file = "conference_structured.xlsx"

# Read the entire text file
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove page headers and empty page markers
content = re.sub(r'---- PAGE \d+ ----\n\n(No text found on this page\n\n)?', '', content)

# List to store all sessions
all_sessions = []
all_presentations = []

# Pattern to identify session blocks
session_pattern = r'((?:EW|SP)\d+)\s+-\s+Hall\s+(\w+)\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+(Educational Session|Special Session)\s+(.*?)(?=(?:EW|SP)\d+|$)'
session_matches = re.finditer(session_pattern, content, re.DOTALL)

for match in session_matches:
    session_id = match.group(1)
    hall = match.group(2)
    start_time = match.group(3)
    end_time = match.group(4)
    session_type = match.group(5)
    session_details = match.group(6).strip()
    
    # Extract session title (usually the first line of session_details)
    title_lines = session_details.split('\n')
    session_title = title_lines[0].strip()
    
    # Extract Chairs
    chairs_match = re.search(r'Chairs\s+(.*?)(?:\n\n|\nW\d+)', session_details, re.DOTALL)
    chairs = chairs_match.group(1).replace('\n', ' ').strip() if chairs_match else ""
    
    # Store session information
    all_sessions.append({
        'Session ID': session_id,
        'Hall': hall,
        'Start Time': start_time,
        'End Time': end_time, 
        'Session Type': session_type,
        'Session Title': session_title,
        'Chairs': chairs
    })
    
    # Extract individual presentations
    presentation_pattern = r'(W\d+)\s+(\d{2}:\d{2})\s+(.*?)(?=\n(?:W\d+|\nCo-organised|$))'
    presentation_matches = re.finditer(presentation_pattern, session_details)
    
    for p_match in presentation_matches:
        presentation_id = p_match.group(1)
        presentation_time = p_match.group(2)
        presentation_details = p_match.group(3).strip()
        
        # Split title and presenter
        if '(' in presentation_details:
            # Last parenthesis contains speaker location
            title_end = presentation_details.rfind('(')
            title = presentation_details[:title_end].strip()
            
            # Extract speaker name (right before the last location)
            speaker_parts = re.split(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+\(', presentation_details)
            speaker = speaker_parts[-2] if len(speaker_parts) > 1 else ""
            
            # Extract location
            location_match = re.search(r'\((.*?)\)$', presentation_details)
            location = location_match.group(1) if location_match else ""
        else:
            title = presentation_details
            speaker = ""
            location = ""
        
        all_presentations.append({
            'Session ID': session_id,
            'Presentation ID': presentation_id,
            'Time': presentation_time,
            'Title': title.replace('\n', ' '),
            'Speaker': speaker,
            'Location': location
        })

# Create DataFrames
df_sessions = pd.DataFrame(all_sessions)
df_presentations = pd.DataFrame(all_presentations)

# Write to Excel with multiple sheets
with pd.ExcelWriter(output_file) as writer:
    df_sessions.to_excel(writer, sheet_name='Sessions', index=False)
    df_presentations.to_excel(writer, sheet_name='Presentations', index=False)

print(f"Extracted {len(all_sessions)} sessions and {len(all_presentations)} presentations")
print(f"Data saved to {output_file}")