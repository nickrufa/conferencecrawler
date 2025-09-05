import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 3)]

def print_html_snippet(html_content, chars=500):
    logging.info(f"First {chars} characters of HTML content:")
    logging.info(html_content[:chars])
    logging.info("...")

def extract_data_from_html(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {'url': url}

    # Print HTML snippet for debugging
    print_html_snippet(html_content)

    # Find the main content div
    content_div = soup.find('div', id=lambda x: x and x.startswith('poster-info-'))
    
    if content_div:
        logging.info(f"Main content div found for {url}")
        # ... (rest of the extraction logic remains the same)
    else:
        logging.error(f"Main content div not found for {url}")
        logging.info("Searching for alternative structures...")
        
        # Look for other potential identifying elements
        h1_elem = soup.find('h1')
        if h1_elem:
            logging.info(f"Found h1 element: {h1_elem.text.strip()}")
        
        col_md_12 = soup.find('div', class_='col-md-12')
        if col_md_12:
            logging.info(f"Found div with class 'col-md-12': {col_md_12.text.strip()[:100]}")
        
        pres_tidbits = soup.find_all('div', class_='pres-tidbit')
        if pres_tidbits:
            logging.info(f"Found {len(pres_tidbits)} 'pres-tidbit' elements")
            for tidbit in pres_tidbits[:3]:  # Print first 3 tidbits
                logging.info(f" - {tidbit.text.strip()}")
        
        data['error'] = 'Main content div not found'

    return data

# ... (rest of the script remains the same)

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

            time.sleep(1)
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
    
    save_data_to_csv(all_data)
    save_data_to_json(all_data)

if __name__ == '__main__':
    main()