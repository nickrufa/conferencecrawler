#!/usr/bin/env python3
"""
IDWeek 2025 Poster Crawler
Crawls local poster data using the poster HTML parser
"""

import requests
from poster_html_parser import PosterHTMLParser, parse_poster_batch
import json
import csv
import time
import logging
from typing import List, Dict, Any
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IDWeek2025PosterCrawler:
    """Crawler for IDWeek 2025 poster data from local server"""
    
    def __init__(self, base_url: str = "http://local.dev.conferencecrawler.com/IDWEEK2025/cfml_viewer/posters.cfm"):
        self.base_url = base_url
        self.parser = PosterHTMLParser()
        self.session = requests.Session()
        self.crawled_data = []
        
    def crawl_poster_range(self, start_id: int = 1, end_id: int = 2169, delay: float = 0.5) -> List[Dict[str, Any]]:
        """
        Crawl posters from start_id to end_id
        
        Args:
            start_id: Starting poster ID
            end_id: Ending poster ID  
            delay: Delay between requests in seconds
            
        Returns:
            List of parsed poster data
        """
        results = []
        failed_ids = []
        
        logger.info(f"Starting crawl of posters {start_id} to {end_id}")
        
        for poster_id in range(start_id, end_id + 1):
            try:
                url = f"{self.base_url}?thisID={poster_id}"
                logger.info(f"Crawling poster {poster_id}/{end_id}: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse the HTML content
                poster_data = self.parser.parse_poster_html(response.text)
                poster_data['poster_id'] = poster_id
                poster_data['source_url'] = url
                
                results.append(poster_data)
                
                # Add delay between requests
                if delay > 0:
                    time.sleep(delay)
                    
            except requests.RequestException as e:
                logger.error(f"Request failed for poster {poster_id}: {e}")
                failed_ids.append(poster_id)
                
            except Exception as e:
                logger.error(f"Unexpected error processing poster {poster_id}: {e}")
                failed_ids.append(poster_id)
            
            # Progress update every 50 posters
            if poster_id % 50 == 0:
                logger.info(f"Progress: {poster_id}/{end_id} posters processed")
        
        if failed_ids:
            logger.warning(f"Failed to process {len(failed_ids)} posters: {failed_ids[:10]}{'...' if len(failed_ids) > 10 else ''}")
        
        self.crawled_data = results
        return results
    
    def save_to_json(self, filename: str = "idweek2025_posters.json"):
        """Save crawled data to JSON file"""
        if not self.crawled_data:
            logger.warning("No data to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.crawled_data)} posters to {filename}")
    
    def save_to_csv(self, filename: str = "idweek2025_posters.csv"):
        """Save crawled data to CSV file"""
        if not self.crawled_data:
            logger.warning("No data to save")
            return
        
        # Flatten the nested data structure for CSV
        flattened_data = []
        for poster in self.crawled_data:
            if 'error' in poster:
                continue
                
            flat_record = {
                'poster_id': poster.get('poster_id', ''),
                'source_url': poster.get('source_url', ''),
                'track_code': poster.get('track_info', {}).get('code', ''),
                'track_name': poster.get('track_info', {}).get('full_name', ''),
                'session_type': poster.get('session_info', {}).get('type', ''),
                'presentation_id': poster.get('presentation_details', {}).get('id', ''),
                'title': poster.get('presentation_details', {}).get('title', ''),
                'date': poster.get('schedule', {}).get('date', ''),
                'time': poster.get('schedule', {}).get('time', ''),
                'timezone': poster.get('schedule', {}).get('timezone', ''),
                'location': poster.get('schedule', {}).get('location', ''),
            }
            
            # Add author information
            authors = poster.get('authors', {})
            presenting_authors = authors.get('presenting', [])
            co_authors = authors.get('co_authors', [])
            
            # Primary presenting author
            if presenting_authors:
                flat_record.update({
                    'presenting_author_name': presenting_authors[0].get('name', ''),
                    'presenting_author_title': presenting_authors[0].get('title', ''),
                    'presenting_author_institution': presenting_authors[0].get('institution', ''),
                    'presenting_author_location': presenting_authors[0].get('location', ''),
                })
            
            # Count authors
            flat_record['total_presenting_authors'] = len(presenting_authors)
            flat_record['total_co_authors'] = len(co_authors)
            
            # All author names (semicolon separated)
            all_presenting = [auth.get('name', '') for auth in presenting_authors]
            all_co_authors = [auth.get('name', '') for auth in co_authors]
            
            flat_record['all_presenting_authors'] = '; '.join(all_presenting)
            flat_record['all_co_authors'] = '; '.join(all_co_authors)
            
            flattened_data.append(flat_record)
        
        # Write to CSV
        if flattened_data:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = flattened_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
            
            logger.info(f"Saved {len(flattened_data)} poster records to {filename}")
    
    def get_stats(self):
        """Get crawling statistics"""
        parser_stats = self.parser.get_stats()
        return {
            'total_crawled': len(self.crawled_data),
            'successful_parses': parser_stats['parsed_count'],
            'parse_errors': parser_stats['error_count']
        }


def main():
    """Main crawling function"""
    # Parse command line arguments
    start_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_id = int(sys.argv[2]) if len(sys.argv) > 2 else 2169
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    
    logger.info(f"Starting IDWeek 2025 poster crawl: IDs {start_id}-{end_id} with {delay}s delay")
    
    crawler = IDWeek2025PosterCrawler()
    
    # Crawl the data
    results = crawler.crawl_poster_range(start_id, end_id, delay)
    
    # Save results
    crawler.save_to_json()
    crawler.save_to_csv()
    
    # Print statistics
    stats = crawler.get_stats()
    logger.info(f"Crawl complete! Stats: {stats}")


if __name__ == "__main__":
    main()