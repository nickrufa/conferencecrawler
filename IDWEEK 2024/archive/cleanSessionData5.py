import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import csv

base_url = "http://local.dev.meetings.com/IDWEEK/_viewSessionData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(265, 530)]

# Loop through each URL and extract data
presentations = []
for url, file_id in zip(urls, range(265, 530)):
  # Fetch the HTML content
  response = requests.get(url)
  response.raise_for_status()  # Raise an exception for bad status codes

  # Try different encodings based on common possibilities
  encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
  for encoding in encodings:
      try:
          content = response.content.decode(encoding)
          break
      except UnicodeDecodeError:
          continue

  # If no encoding worked, use a default (e.g., 'utf-8')
  if not content:
      content = response.content.decode('utf-8', errors='ignore')

  # Parse the fetched HTML content using BeautifulSoup
  soup = BeautifulSoup(content, 'html.parser')

  # Find all the presentation list items
  presentation_list = soup.find_all('li', class_='list-group-item loadbyurl')

  # Extract information from each list item
  for item in presentation_list:
      presid = item.get('data-presid')  # Extract presentation ID
      url = item.get('data-url')  # Extract presentation URL (relative URL)

      # Construct the absolute URL for the presentation
      full_url = f"{base_url.rstrip('#id#')}{url}"  

      # Find the time, title, and presenter containers (handle potential None)
      time_container = item.find('div', class_='prestime')
      title_container = item.find('div', class_='prestitle')
      presenter_container = item.find('small', class_='presentation-presenters')

      # Extract the time
      time = time_container.text.strip() if time_container else 'N/A'

      # Extract the title, handling potential merging
      title_parts = title_container.find_all(string=True, recursive=False) if title_container else []
      title = ' '.join([part.strip() for part in title_parts if part.strip()])

      # Extract the presenter, handling potential merging and None container
      presenter_parts = []
      if presenter_container:
          # Recursively find all text nodes within the presenter container
          for child in presenter_container.descendants:
              if child.name == 'p' or child.name == 'span':
                  presenter_parts.extend(child.find_all(string=True, recursive=False))
          presenter = ' '.join([part.strip() for part in presenter_parts if part.strip()])
      else:
          presenter = 'N/A'

      # Store the extracted details in a dictionary, including the file ID
      presentations.append({
          'file_id': file_id,
          'presid': presid,
          'url': full_url,  # Use the absolute URL
          'time': time,
          'title': title,
          'presenter': presenter
      })

# Output to JSON
json_filename = '6-presentations.json'
with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(presentations, json_file, ensure_ascii=False, indent=4)
print(f"Data has been written to {json_filename}")

# Output to CSV using pandas
df = pd.DataFrame(presentations)
csv_filename = '6-presentations.csv'
df.to_csv(csv_filename, index=False)
print(f"Data has been written to {csv_filename}")
