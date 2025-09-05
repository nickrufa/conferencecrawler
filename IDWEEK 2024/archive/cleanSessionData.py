import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import logging
import html

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "http://local.dev.meetings.com/IDWEEK/_viewSessionData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(264, 532)]

def print_html_snippet(html_content, chars=500):
    logging.info(f"First {chars} characters of HTML content:")
    logging.info(html_content[:chars])
    logging.info("...")

def extract_data_from_html(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {'url': url}

    content_div = soup.find('div', class_='popup_content')
    
    if content_div:
        logging.info(f"Main content div found for {url}")
        
        # Extract track names
        tracks = content_div.find_all('a', href=lambda x: x and x.startswith('/SearchByBucket.asp?pfp=Track'))
        data['tracknames'] = [track.text.strip() for track in tracks]
        logging.info(f"Extracted tracks: {data['tracknames']}")

        # Extract title
        title_elem = content_div.find('h1')
        if title_elem:
            data['title'] = title_elem.text.strip()
            logging.info(f"Extracted title: {data['title']}")

        # Extract date, time, and location
        tidbit_elems = content_div.find_all('div', class_='pres-tidbit')
        if tidbit_elems:
            data['date'] = tidbit_elems[0].text.strip() if len(tidbit_elems) > 0 else ''
            data['time'] = tidbit_elems[1].text.strip() if len(tidbit_elems) > 1 else ''
            data['location'] = tidbit_elems[2].text.strip() if len(tidbit_elems) > 2 else ''
            logging.info(f"Extracted date: {data['date']}, time: {data['time']}, location: {data['location']}")

        # Extract presentations
        presentations = []
        presentations_header = content_div.find('h2', class_='role-title', text='Presentations:')
        if presentations_header:
            pres_rows = presentations_header.find_next_siblings('div', class_='row')
            for row in pres_rows:
                presentation = {}
                time_elem = row.find('span', class_='tipsytip')
                if time_elem:
                    presentation['time'] = time_elem.text.strip()
                
                title_elem = row.find('div', class_='prestitle')
                if title_elem:
                    title_text = title_elem.contents[0]
                    if isinstance(title_text, str):
                        presentation['title'] = title_text.strip()
                    
                    speaker_elem = title_elem.find('span', class_='biopopup')
                    if speaker_elem:
                        presentation['speaker'] = speaker_elem.text.strip()
                    
                    affiliation = title_elem.find('small', class_='presentation-presenters')
                    if affiliation:
                        affiliation_text = affiliation.text.split('–')[-1] if '–' in affiliation.text else ''
                        presentation['affiliation'] = affiliation_text.strip()
                
                presentations.append(presentation)
                logging.info(f"Extracted presentation: {presentation}")
        
        data['presentations'] = presentations
        logging.info(f"Extracted {len(presentations)} presentations")

        logging.info(f"Data extracted successfully for {url}")
    else:
        logging.error(f"Main content div not found for {url}")
        data['error'] = 'Main content div not found'

    return data

def save_data_to_csv(extracted_data, filename='ddd-output.csv'):
    fieldnames = ['url', 'tracknames', 'title', 'date', 'time', 'location',
                  'presentation_time', 'presentation_title', 'presentation_speaker', 'presentation_affiliation']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for session in extracted_data:
            base_row = {field: session.get(field, '') for field in fieldnames if field not in ['presentation_time', 'presentation_title', 'presentation_speaker', 'presentation_affiliation']}
            
            # Convert list fields to strings
            if isinstance(base_row['tracknames'], list):
                base_row['tracknames'] = '; '.join(base_row['tracknames'])

            if 'presentations' in session and session['presentations']:
                for presentation in session['presentations']:
                    row = base_row.copy()
                    row['presentation_time'] = presentation.get('time', '')
                    row['presentation_title'] = presentation.get('title', '')
                    row['presentation_speaker'] = presentation.get('speaker', '')
                    row['presentation_affiliation'] = presentation.get('affiliation', '')
                    writer.writerow(row)
            else:
                writer.writerow(base_row)

    logging.info(f"Data saved to {filename}")

def save_data_to_json(extracted_data, filename='ddd-output.json'):
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

    # Print the extracted data for debugging
    for session in all_data:
        logging.info(f"Session title: {session.get('title', 'N/A')}")
        logging.info(f"Number of presentations: {len(session.get('presentations', []))}")
        for presentation in session.get('presentations', []):
            logging.info(f"  Presentation: {presentation.get('title', 'N/A')}")

if __name__ == '__main__':
    main()