import requests
import re
from bs4 import BeautifulSoup
import time

# List of URLs
urls = [
    'https://eccmid2024.key4.live/programme-live-1?coday=2024-04-26&embed=1&dtFormat=d/m',
    'https://eccmid2024.key4.live/programme-live-1?coday=2024-04-27&embed=1&dtFormat=d/m',
    'https://eccmid2024.key4.live/programme-live-1?coday=2024-04-28&embed=1&dtFormat=d/m',
    'https://eccmid2024.key4.live/programme-live-1?coday=2024-04-29&embed=1&dtFormat=d/m',
    'https://eccmid2024.key4.live/programme-live-1?coday=2024-04-30&embed=1&dtFormat=d/m'
]

# Open a file for writing
with open('eccmid_sessions.txt', 'w', encoding='utf-8') as file:
    # Loop through the URLs
    for url in urls:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')

        # ... (existing code for data extraction)
        program_session_card_references = soup.find_all('span', class_='program-session-card-reference')
        for program_session_card_reference in program_session_card_references:
            program_session_code = program_session_card_reference.find('strong').text.strip()
            output_line = f"Code: {program_session_code}\n"
            file.write(output_line)  # Write the output to the file
        
            # print(f"Code: {program_session_code}")

        # Delay between requests (e.g., 5 seconds)
        time.sleep(12)