import requests
import re
from bs4 import BeautifulSoup
import time

# List of URLs
urls = [
    # 'https://online.eccmid.org/programme-live-1?programType=listing&embed=1&typeHideAllBut=55&page=1&orderBy=1'
]

# Open a file for writing
with open('eccmid_posters.txt', 'w', encoding='utf-8') as file:
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
        time.sleep(7)