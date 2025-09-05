import re
import pandas as pd

def parse_conference_program(input_file, output_file):
    """
    Parse a conference program text file with a specialized parser for ESCMID Global 2025.
    
    Parameters:
    input_file (str): Path to the text file containing conference program
    output_file (str): Path to save the Excel output
    """
    print(f"Processing {input_file}...")
    
    # Read the text file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove page markers and empty page notices
    content = re.sub(r'---- PAGE \d+ ----\n\n(No text found on this page\n\n)?', '', content)
    
    # Lists to store extracted data
    sessions = []
    presentations = []
    
    # Extract session blocks
    # This pattern looks for session ID, time, hall number, and type
    session_pattern = r'((?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+)\s+(\d{2}:\d{2})(?:\s*-\s*(\d{2}:\d{2}))?\s+Hall\s+(\w+)\s*\n+((?:Educational|Special|Open Forum|1-hour Oral|1-hour Case|2-hour Oral|2-hour Symposium|Meet-the-Expert|Keynote Lecture|ePoster Flash)\s+Session|Session)'
    
    session_matches = re.finditer(session_pattern, content)
    
    for match in session_matches:
        session_id = match.group(1)
        start_time = match.group(2)
        end_time = match.group(3) if match.group(3) else ""
        hall = match.group(4)
        session_type = match.group(5).strip()
        
        # Find the session title (typically follows the session type)
        session_pos = match.end()
        next_session_pos = content.find('\n' + session_id, session_pos)
        if next_session_pos == -1:
            next_session_pos = content.find('\nEW', session_pos)
        if next_session_pos == -1:
            next_session_pos = content.find('\nOS', session_pos)
        if next_session_pos == -1:
            next_session_pos = content.find('\nME', session_pos)
        if next_session_pos == -1:
            next_session_pos = content.find('\nSP', session_pos)
        if next_session_pos == -1:
            next_session_pos = len(content)
            
        session_block = content[session_pos:next_session_pos]
        
        # Extract title - it's the first line after session type
        title_match = re.search(r'\n(.*?)(?:\nChairs|\n\n)', session_block)
        session_title = title_match.group(1).strip() if title_match else ""
        
        # Extract chairs
        chairs_match = re.search(r'Chairs\s+(.*?)(?:\n\n|\nCo-organised|\nW\d{4}|\nO\d{4}|\nM\d{4}|\nF\d{4}|\nE\d{4}|\nL\d{4}|\nS\d{4})', session_block, re.DOTALL)
        chairs = chairs_match.group(1).replace('\n', ' ').strip() if chairs_match else ""
        
        # Store session info
        sessions.append({
            'Session ID': session_id,
            'Start Time': start_time,
            'End Time': end_time,
            'Hall': hall,
            'Session Type': session_type,
            'Session Title': session_title,
            'Chairs': chairs
        })
        
        # Extract presentations for this session
        # This pattern matches presentation codes (W/O/M/F/E/L/S) with time and content
        pres_pattern = r'([WOMFELS]\d{4})\s+(\d{2}:\d{2})\s+(.*?)(?=\n[WOMFELS]\d{4}|\nCo-organised|\n\n(?:EW|OS|ME|SP|SY|KN|FO|LB|EF)|$)'
        pres_matches = re.finditer(pres_pattern, session_block, re.DOTALL)
        
        for p_match in pres_matches:
            pres_id = p_match.group(1)
            pres_time = p_match.group(2)
            pres_content = p_match.group(3).strip().replace('\n', ' ')
            
            # Try to separate title from presenter and location
            title = pres_content
            speaker = ""
            location = ""
            
            # Look for the last part in parentheses for location
            location_match = re.search(r'([A-Za-z][a-zA-Z\s\.,\-]+)\(([^)]+)\)$', pres_content)
            if location_match:
                # Found pattern like "Name (Location)"
                speaker = location_match.group(1).strip()
                location = location_match.group(2).strip()
                title = pres_content[:pres_content.rfind(speaker)].strip()
            else:
                # Try another pattern where location is at the end without a clear speaker
                location_match = re.search(r'\(([^)]+)\)$', pres_content)
                if location_match:
                    location = location_match.group(1).strip()
                    title_part = pres_content[:pres_content.rfind('(')].strip()
                    
                    # Try to extract speaker from the title part - often marked with * or at the end
                    speaker_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\*?$', title_part)
                    if speaker_match:
                        speaker = speaker_match.group(1).strip()
                        title = title_part[:title_part.rfind(speaker)].strip()
                    else:
                        title = title_part
            
            # Handle special case where title and speaker are merged
            if not speaker and "*" in title:
                parts = title.split("*", 1)
                if len(parts) > 1:
                    potential_speaker = parts[0].strip()
                    if re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', potential_speaker):
                        speaker = potential_speaker
                        title = parts[1].strip()
            
            presentations.append({
                'Session ID': session_id,
                'Presentation ID': pres_id,
                'Time': pres_time,
                'Title': title,
                'Speaker': speaker,
                'Location': location
            })
    
    # Create DataFrames
    sessions_df = pd.DataFrame(sessions)
    presentations_df = pd.DataFrame(presentations)
    
    # Sort by IDs
    if not sessions_df.empty:
        sessions_df = sessions_df.sort_values('Session ID')
    if not presentations_df.empty:
        presentations_df = presentations_df.sort_values(['Session ID', 'Presentation ID'])
    
    # Write to Excel
    with pd.ExcelWriter(output_file) as writer:
        sessions_df.to_excel(writer, sheet_name='Sessions', index=False)
        presentations_df.to_excel(writer, sheet_name='Presentations', index=False)
    
    print(f"Extracted {len(sessions)} sessions and {len(presentations)} presentations")
    print(f"Data saved to {output_file}")
    return len(sessions), len(presentations)


def extract_session_presentation_csv(input_file, output_file):
    """
    A simpler parser that focuses on extracting presentation information 
    and matching it to sessions, then saving to CSV.
    """
    print(f"Processing {input_file} for CSV export...")
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove page markers
    content = re.sub(r'---- PAGE \d+ ----\n\n(No text found on this page\n\n)?', '', content)
    
    # Extract session information
    session_pattern = r'((?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+)\s+(\d{2}:\d{2})(?:\s*-\s*(\d{2}:\d{2}))?\s+Hall\s+(\w+)'
    session_matches = re.findall(session_pattern, content)
    
    # Create a dictionary of session IDs to their details
    sessions = {}
    for match in session_matches:
        session_id = match[0]
        hall = match[3]
        sessions[session_id] = {
            'hall': hall,
            'start_time': match[1],
            'end_time': match[2] if match[2] else ''
        }
    
    # Extract all presentations
    presentation_pattern = r'([WOMFELS]\d{4})\s+(\d{2}:\d{2})\s+(.*?)(?=\n[WOMFELS]\d{4}|\n\n)'
    presentation_matches = re.finditer(presentation_pattern, content, re.DOTALL)
    
    rows = []
    
    for match in presentation_matches:
        pres_id = match.group(1)
        time = match.group(2)
        details = match.group(3).strip().replace('\n', ' ')
        
        # Find which session this belongs to
        text_before = content[:match.start()]
        session_matches = list(re.finditer(r'((?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+)\s+\d{2}:\d{2}', text_before))
        
        session_id = ""
        hall = ""
        if session_matches:
            session_id = session_matches[-1].group(1)
            if session_id in sessions:
                hall = sessions[session_id]['hall']
        
        rows.append([session_id, hall, pres_id, time, details])
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(rows, columns=['Session ID', 'Hall', 'Presentation ID', 'Time', 'Details'])
    df.to_csv(output_file, index=False)
    
    print(f"Extracted {len(rows)} presentations to {output_file}")
    return len(rows)


if __name__ == "__main__":
    input_file = "conference_text.txt"
    output_file = "conference_program.xlsx"
    csv_output = "conference_program.csv"
    
    # Run both parsers
    sessions_count, presentations_count = parse_conference_program(input_file, output_file)
    csv_count = extract_session_presentation_csv(input_file, csv_output)
    
    print("\nSummary:")
    print(f"Complete parser: {sessions_count} sessions, {presentations_count} presentations -> {output_file}")
    print(f"Simple CSV parser: {csv_count} presentations -> {csv_output}")
    print("\nYou can use either file depending on your needs:")
    print(f"1. {output_file} - Structured Excel with separate sheets for sessions and presentations")
    print(f"2. {csv_output} - Simple CSV with all presentations and their session information")
