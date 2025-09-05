import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import time
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 2500)]

def print_html_snippet(html_content, chars=500):
    logging.info(f"First {chars} characters of HTML content:")
    logging.info(html_content[:chars])
    logging.info("...")

def extract_data_from_html(html_content, url):
    decoded_html = html.unescape(html_content)
    soup = BeautifulSoup(decoded_html, 'html.parser')
    data = {'url': url}

    # Find the main content div
    content_div = soup.find('div', class_='card', id=lambda x: x and x.startswith('poster-info-'))

    if content_div:
        logging.info(f"Main content div found for {url}")

        # Extract poster ID
        poster_id = content_div.get('id', '')
        data['poster_id'] = poster_id.replace('poster-info-', '')

        # Extract presenting author(s)
        presenting_author = soup.find('h2', string='Presenting Author(s)')
        if presenting_author:
            presenting_author_li = presenting_author.find_next('li', class_='speakerrow')
            if presenting_author_li:
                presenting_author_name_elem = presenting_author_li.find('p', class_='speaker-name')
                presenting_author_name = presenting_author_name_elem.get_text(strip=True) if presenting_author_name_elem else ''
                presenting_author_details = presenting_author_li.find('p', class_='text-muted prof-text')
                # Replace <br> tags with semicolon and space
                if presenting_author_details:
                    for br in presenting_author_details.find_all('br'):
                        br.replace_with('; ')
                    presenting_author_details = presenting_author_details.get_text(strip=True)
                data['presenting_author_name'] = presenting_author_name
                data['presenting_author_details'] = presenting_author_details

        # Extract co-author(s)
        co_authors = soup.find_all('h2', string='Co-Author(s)')
        co_author_data = []
        for co_author in co_authors:
            co_author_li = co_author.find_next('li', class_='speakerrow')
            while co_author_li:
                co_author_name_elem = co_author_li.find('p', class_='speaker-name')
                co_author_name = co_author_name_elem.get_text(strip=True) if co_author_name_elem else ''
                co_author_details = co_author_li.find('p', class_='text-muted prof-text')
                # Replace <br> tags with semicolon and space
                if co_author_details:
                    for br in co_author_details.find_all('br'):
                        br.replace_with('; ')
                    co_author_details = co_author_details.get_text(strip=True)
                co_author_data.append({'name': co_author_name, 'details': co_author_details})
                co_author_li = co_author_li.find_next_sibling('li', class_='speakerrow')
        
        data['co_authors'] = co_author_data

    else:
        logging.error(f"Main content div not found for {url}")
        data['error'] = 'Main content div not found'
    
    return data

def save_data_to_csv(extracted_data, filename='poster_output4.csv'):
    fieldnames = set()
    for data in extracted_data:
        fieldnames.update(data.keys())

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in extracted_data:
            # Ensure all values are strings and replace newlines
            cleaned_row = {k: str(v).replace('\n', ' ').strip() if v is not None else '' for k, v in row.items()}
            writer.writerow(cleaned_row)

    logging.info(f"Data saved to {filename}")

def save_data_to_json(extracted_data, filename='poster_output4.json'):
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(extracted_data, jsonfile, indent=4, ensure_ascii=False)
    logging.info(f"Data saved to {filename}")

def main():
    all_data = []

    for url in urls:
        try:
            logging.info(f"Processing URL: {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response content length: {len(response.text)}")
            
            extracted_data = extract_data_from_html(response.text, url)
            all_data.append(extracted_data)

            # Save raw HTML for debugging
            # with open(f'raw_html_{url.split("=")[-1]}.html', 'w', encoding='utf-8') as file:
            #     file.write(response.text)
            # logging.info(f"Raw HTML saved to raw_html_{url.split('=')[-1]}.html")

            time.sleep(.25)
        
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
    
    save_data_to_csv(all_data)
    save_data_to_json(all_data)

if __name__ == '__main__':
    main()