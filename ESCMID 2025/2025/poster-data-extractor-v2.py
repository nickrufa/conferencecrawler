#!/usr/bin/env python3
# Poster Data Extractor - Parses conference poster HTML and exports to JSON or MySQL
# Created: March 18, 2025

import os
import re
import json
import argparse
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime

def extract_poster_data(html_content):
    """
    Extract poster information from the HTML content using BeautifulSoup.
    
    Args:
        html_content (str): HTML content as a string
        
    Returns:
        list: List of dictionaries containing extracted poster data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    poster_divs = soup.find_all('div', class_='row program-list-tr session-row locator-interv-row pb-4')
    
    posters = []
    
    for poster_div in poster_divs:
        poster_data = {}
        
        # Extract poster ID and abstract number
        try:
            poster_id = poster_div.get('data-intervention-reference')
            poster_data['poster_id'] = poster_id
            
            abstract_div = poster_div.find('div', {'data-poster-label': 'Poster'})
            if abstract_div:
                abstract_number_elem = abstract_div.find('p', class_='pt-2 pb-0')
                if abstract_number_elem and abstract_number_elem.find('strong'):
                    abstract_number = abstract_number_elem.find('strong').next_sibling.strip()
                    poster_data['abstract_number'] = abstract_number
        except Exception as e:
            print(f"Error extracting poster ID or abstract: {e}")
        
        # Extract location information
        try:
            location_div = poster_div.find('div', class_='col-12 d-flex align-items-center overflow-hidden text-break pt-4 pb-2')
            if location_div and location_div.find('span', class_='map-link-modal'):
                location = location_div.find('span', class_='map-link-modal').text.strip()
                sector, row, position = [item.strip() for item in location.split('/')]
                poster_data['sector'] = sector
                poster_data['row'] = row
                poster_data['position'] = position
        except Exception as e:
            print(f"Error extracting location info: {e}")
        
        # Extract title
        try:
            title_div = poster_div.find('p', class_='pb-0 d-inline')
            if title_div:
                title = title_div.get_text().replace('Abstract Title:', '').strip()
                poster_data['title'] = title
        except Exception as e:
            print(f"Error extracting title: {e}")
        
        # Extract date and session info
        try:
            date_div = poster_div.find('p', class_='pb-2')
            if date_div and date_div.find('strong', text=re.compile('Date:')):
                date_text = date_div.get_text().replace('Date:', '').strip()
                poster_data['date'] = date_text
                
            session_div = poster_div.find('p', class_='pb-0')
            if session_div and session_div.find('strong', text=re.compile('Session title:')):
                session = session_div.get_text().replace('Session title:', '').strip()
                poster_data['session'] = session
        except Exception as e:
            print(f"Error extracting date/session: {e}")
        
        # Extract presenter
        try:
            presenter_div = poster_div.find('div', class_='col-12 d-flex align-items-center overflow-hidden text-break pb-2')
            if presenter_div and presenter_div.find('strong', text=re.compile('Poster Presenter:')):
                presenter = presenter_div.find('p', class_='pb-0').text.strip()
                poster_data['presenter'] = presenter
        except Exception as e:
            print(f"Error extracting presenter: {e}")
        
        # Extract co-authors - completely rewritten for accuracy
        try:
            # Find the div that contains co-authors
            authors_div = None
            for div in poster_div.find_all('div', class_='col-12'):
                if div.find('span', class_='font-weight-bold', text=re.compile('Co-Authors:')):
                    authors_div = div
                    break
                    
            if authors_div:
                authors = []
                # Skip the first span (which contains "Co-Authors:")
                span_elements = authors_div.find_all('span', recursive=False)
                
                for span in span_elements:
                    if 'font-weight-bold' in span.get('class', []):
                        continue  # Skip the "Co-Authors:" label
                        
                    # Get text and clean it (remove commas at the end)
                    author_text = span.get_text().strip()
                    author_text = re.sub(r',\s*$', '', author_text)
                    
                    if author_text:
                        authors.append(author_text)
                
                poster_data['co_authors'] = authors
        except Exception as e:
            print(f"Error extracting co-authors: {e}")
        
        posters.append(poster_data)
    
    return posters

def save_to_json(posters, output_file='posters.json'):
    """
    Save extracted poster data to a JSON file.
    
    Args:
        posters (list): List of dictionaries containing poster data
        output_file (str): Path to output JSON file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posters, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(posters)} posters to {output_file}")

def save_to_mysql(posters, config):
    """
    Save extracted poster data to a MySQL database.
    
    Args:
        posters (list): List of dictionaries containing poster data
        config (dict): MySQL connection configuration
    """
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posters (
            poster_id VARCHAR(10) PRIMARY KEY,
            abstract_number VARCHAR(20),
            sector VARCHAR(10),
            row VARCHAR(10),
            position VARCHAR(10),
            title TEXT,
            date VARCHAR(50),
            session TEXT,
            presenter VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS co_authors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            poster_id VARCHAR(10),
            author_name VARCHAR(255),
            FOREIGN KEY (poster_id) REFERENCES posters(poster_id) ON DELETE CASCADE
        )
        ''')
        
        # Insert data into the database
        for poster in posters:
            # Insert poster data
            insert_poster = '''
            INSERT INTO posters (poster_id, abstract_number, sector, row, position, title, date, session, presenter)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                abstract_number = VALUES(abstract_number),
                sector = VALUES(sector),
                row = VALUES(row),
                position = VALUES(position),
                title = VALUES(title),
                date = VALUES(date),
                session = VALUES(session),
                presenter = VALUES(presenter)
            '''
            
            poster_values = (
                poster.get('poster_id', ''),
                poster.get('abstract_number', ''),
                poster.get('sector', ''),
                poster.get('row', ''),
                poster.get('position', ''),
                poster.get('title', ''),
                poster.get('date', ''),
                poster.get('session', ''),
                poster.get('presenter', '')
            )
            
            cursor.execute(insert_poster, poster_values)
            
            # Delete existing co-authors for this poster (to handle updates)
            if 'poster_id' in poster:
                cursor.execute('DELETE FROM co_authors WHERE poster_id = %s', (poster['poster_id'],))
            
            # Insert co-authors
            if 'co_authors' in poster and poster['co_authors']:
                for author in poster['co_authors']:
                    cursor.execute(
                        'INSERT INTO co_authors (poster_id, author_name) VALUES (%s, %s)',
                        (poster['poster_id'], author)
                    )
        
        # Commit the changes
        conn.commit()
        
        # Get the count of posters
        cursor.execute('SELECT COUNT(*) FROM posters')
        count = cursor.fetchone()[0]
        
        print(f"Successfully saved {count} posters to MySQL database")
        
    except Exception as e:
        print(f"Error saving to MySQL: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    parser = argparse.ArgumentParser(description='Extract poster data from HTML and save to JSON or MySQL')
    parser.add_argument('input_file', help='Path to the HTML file containing poster data')
    parser.add_argument('--output', '-o', default='posters.json', help='Path to the output JSON file (default: posters.json)')
    parser.add_argument('--mysql', action='store_true', help='Save to MySQL instead of JSON')
    parser.add_argument('--host', default='localhost', help='MySQL host (default: localhost)')
    parser.add_argument('--user', default='root', help='MySQL username (default: root)')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='posters_db', help='MySQL database name (default: posters_db)')
    
    args = parser.parse_args()
    
    # Read the HTML file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    # Extract poster data
    posters = extract_poster_data(html_content)
    
    if args.mysql:
        # Save to MySQL
        mysql_config = {
            'host': args.host,
            'user': args.user,
            'password': args.password,
            'database': args.database
        }
        save_to_mysql(posters, mysql_config)
    else:
        # Save to JSON
        save_to_json(posters, args.output)

if __name__ == "__main__":
    main()
