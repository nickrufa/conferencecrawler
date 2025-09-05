import requests
import re
from bs4 import BeautifulSoup

# List of URLs
urls = [
    'https://online.eccmid.org/programme-live-1?programType=listing&embed=1&typeHideAllBut=55&page=1&orderBy=1'
]

# Open a file for writing
with open('eccmid_posters_2023_03_28.txt', 'w', encoding='iso-8859-15') as file:
    # Loop through the URLs
    for url in urls:
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')

        # Find all divs with class 'session-row'
        session_rows = soup.find_all('div', class_='session-row')

        for session_row in session_rows:
            # For each 'session-row', find all 'span' and 'p' tags
            text_elements = session_row.find_all(['span', 'p'])
            for element in text_elements:
                # Print the text from each 'span' and 'p' tag
                #print(element.get_text(strip=True))
                output_line = f"π{element.get_text(strip=False)}\n"
                file.write(output_line)  # Write the output to the file
