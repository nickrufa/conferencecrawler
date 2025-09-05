import requests
import re
from bs4 import BeautifulSoup
import time

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 3)]

# Function to extract data from the HTML content
def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extracting specific data from the HTML
    data = {}
    
    # Extract poster title
    title_tag = soup.find('h1')
    if title_tag:
        data['title'] = title_tag.text.strip()

    # Extract poster session
    session_tag = soup.find('p', text=re.compile('Poster Session:'))
    if session_tag:
        data['poster_session'] = session_tag.text.strip()

    # Extract authors
    authors = []
    author_tags = soup.find_all('li', class_='speakerrow')
    for author_tag in author_tags:
        name_tag = author_tag.find('p', class_='speaker-name')
        affiliation_tag = author_tag.find('p', class_='text-muted')
        if name_tag and affiliation_tag:
            authors.append({
                'name': name_tag.text.strip(),
                'affiliation': affiliation_tag.text.strip()
            })
    data['authors'] = authors

    return data

# Parse the static HTML content
extracted_data = extract_data_from_html(html_content)

# Print the extracted data
print(f"Title: {extracted_data.get('title', 'N/A')}")
print(f"Poster Session: {extracted_data.get('poster_session', 'N/A')}")
print("Authors:")
for author in extracted_data['authors']:
    print(f"  - Name: {author['name']}")
    print(f"    Affiliation: {author['affiliation']}")
