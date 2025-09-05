import re
import csv

input_file = "conference_text.txt"
output_file = "conference_data.csv"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove page markers
content = re.sub(r'---- PAGE \d+ ----\n\n(No text found on this page\n\n)?', '', content)

# Extract session blocks
session_blocks = re.findall(r'((?:EW|SP)\d+).+?(?=(?:EW|SP)\d+|$)', content, re.DOTALL)

# Process each session
rows = []
for block in session_blocks:
    # Extract basic info
    session_id = re.search(r'(EW|SP)\d+', block)
    session_id = session_id.group(0) if session_id else ""
    
    # Extract presentation IDs and content
    presentations = re.findall(r'(W\d+)\s+(\d{2}:\d{2})\s+(.*?)(?=W\d+|\Z)', block, re.DOTALL)
    
    for pres in presentations:
        pres_id = pres[0]
        pres_time = pres[1]
        pres_content = pres[2].strip().replace('\n', ' ')
        
        rows.append([session_id, pres_id, pres_time, pres_content])

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Session ID', 'Presentation ID', 'Time', 'Content'])
    writer.writerows(rows)

print(f"Data exported to {output_file}")