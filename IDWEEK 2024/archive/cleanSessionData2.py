import requests
from bs4 import BeautifulSoup
import json
import csv

base_url = "http://local.dev.meetings.com/IDWEEK/_viewSessionData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(265, 530)]

# Loop through each URL and extract data
presentations = []
for url, file_id in zip(urls, range(265, 531)):
  # Fetch the HTML content for the current URL
  response = requests.get(url)
  response.raise_for_status()  # Raise an exception for bad status codes

  # Parse the fetched HTML content using BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find all the presentation list items
  presentation_list = soup.find_all('li', class_='list-group-item loadbyurl')

  # Extract information from each list item
  for item in presentation_list:
      presid = item.get('data-presid')  # Extract presentation ID
      url = item.get('data-url')  # Extract presentation URL (relative URL)

      # Construct the absolute URL for the presentation
      full_url = f"{base_url.rstrip('#id#')}{url}"  

      # Extract time, title, and presenter details
      time = item.find('div', class_='prestime').text.strip()
      title = item.find('div', class_='prestitle').text.strip(), ' '

      # Handle presenters if available
      presenter_tag = item.find('small', class_='presentation-presenters')
      if presenter_tag:
          presenter = presenter_tag.text.strip()
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
json_filename = 'presentations.json'
with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(presentations, json_file, ensure_ascii=False, indent=4)
print(f"Data has been written to {json_filename}")

# Output to CSV
csv_filename = 'presentations.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['file_id', 'presid', 'url', 'time', 'title', 'presenter'])
    writer.writeheader()
    writer.writerows(presentations)
print(f"Data has been written to {csv_filename}")