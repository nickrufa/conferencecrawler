import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 23)]

def print_html_snippet(html_content, chars=500):
    logging.info(f"First {chars} characters of HTML content:")
    logging.info(html_content[:chars])
    logging.info("...")

def extract_data_from_html(html_content, url):
    decoded_html = html.unescape(html_content)
    soup = BeautifulSoup(decoded_html, 'html.parser')
    data = {'url': url}

    content_div = soup.find('div', class_='card', id=lambda x: x and x.startswith('poster-info-'))
    
    if content_div:
        logging.info(f"Main content div found for {url}")
        
        # Extract poster ID
        poster_id = content_div.get('id', '')
        data['poster_id'] = poster_id.replace('poster-info-', '')

        # Extract title
        title_elem = content_div.find('h1')
        if title_elem:
            data['title'] = title_elem.text.strip()

        # Extract session and track
        info_div = content_div.find('div', class_='col-md-12')
        if info_div:
            lines = list(info_div.stripped_strings)
            if len(lines) >= 2:
                data['trackname'] = lines[0]
                data['sessionname'] = lines[1]

        # Extract date, time, and location
        tidbit_elems = content_div.find_all('div', class_='pres-tidbit')
        if tidbit_elems:
            data['date'] = tidbit_elems[0].text.strip() if len(tidbit_elems) > 0 else ''
            if len(tidbit_elems) > 1:
                time_text = tidbit_elems[1].text.strip()
                data['time'] = time_text  # Store full time string
            data['location'] = tidbit_elems[2].text.strip() if len(tidbit_elems) > 2 else ''

        # Extract abstract
        abstract_elem = content_div.find('div', class_='abstract-content')
        if abstract_elem:
            data['abstract'] = abstract_elem.text.strip()

        # Extract presenters
        presenters = []
        presenter_elems = content_div.find_all('div', class_='col-xs-9')
        for elem in presenter_elems:
            presenter = {}
            name_elem = elem.find('a')
            if name_elem:
                presenter['name'] = name_elem.text.strip()
            details = list(elem.stripped_strings)[1:]
            if details:
                presenter['title'] = details[0]
                presenter['affiliation'] = ' '.join(details[1:])
            presenters.append(presenter)
        data['presenters'] = presenters

        logging.info(f"Data extracted successfully for {url}")
    else:
        logging.error(f"Main content div not found for {url}")
        data['error'] = 'Main content div not found'

    return data

def save_data_to_csv(extracted_data, filename='output.csv'):
    keys = set().union(*(d.keys() for d in extracted_data))
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(extracted_data)
    logging.info(f"Data saved to {filename}")

def save_data_to_json(extracted_data, filename='output.json'):
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
            with open(f'raw_html_{url.split("=")[-1]}.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
            logging.info(f"Raw HTML saved to raw_html_{url.split('=')[-1]}.html")

            time.sleep(.5)
        
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
    
    save_data_to_csv(all_data)
    save_data_to_json(all_data)

if __name__ == '__main__':
    main()