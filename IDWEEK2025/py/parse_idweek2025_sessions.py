#!/usr/bin/env python3
"""
IDWeek 2025 Session Crawler
Crawls local session data using the session HTML parser
"""

import requests
from session_parser_fixed import SessionHTMLParserFixed
import json
import csv
import time
import logging
from typing import List, Dict, Any
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IDWeek2025SessionCrawler:
    """Crawler for IDWeek 2025 session data from local server"""
    
    def __init__(self, base_url: str = "http://local.dev.conferencecrawler.com/IDWEEK2025/cfml_viewer/sessions.cfm"):
        self.base_url = base_url
        self.parser = SessionHTMLParserFixed()
        self.session = requests.Session()
        self.crawled_data = []
        
    def crawl_session_range(self, start_id: int = 1, end_id: int = 1013, delay: float = 0.5) -> List[Dict[str, Any]]:
        """
        Crawl sessions from start_id to end_id
        
        Args:
            start_id: Starting session ID
            end_id: Ending session ID  
            delay: Delay between requests in seconds
            
        Returns:
            List of parsed session data
        """
        results = []
        failed_ids = []
        
        logger.info(f"Starting crawl of sessions {start_id} to {end_id}")
        
        for session_id in range(start_id, end_id + 1):
            try:
                url = f"{self.base_url}?thisID={session_id}"
                logger.info(f"Crawling session {session_id}/{end_id}: {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse the HTML content
                session_data = self.parser.parse_session_html(response.text)
                session_data['session_id'] = session_id
                session_data['source_url'] = url
                
                results.append(session_data)
                
                # Add delay between requests
                if delay > 0:
                    time.sleep(delay)
                    
            except requests.RequestException as e:
                logger.error(f"Request failed for session {session_id}: {e}")
                failed_ids.append(session_id)
                
            except Exception as e:
                logger.error(f"Unexpected error processing session {session_id}: {e}")
                failed_ids.append(session_id)
            
            # Progress update every 50 sessions
            if session_id % 50 == 0:
                logger.info(f"Progress: {session_id}/{end_id} sessions processed")
        
        if failed_ids:
            logger.warning(f"Failed to process {len(failed_ids)} sessions: {failed_ids[:10]}{'...' if len(failed_ids) > 10 else ''}")
        
        self.crawled_data = results
        return results
    
    def save_to_json(self, filename: str = "idweek2025_sessions.json"):
        """Save crawled data to JSON file"""
        if not self.crawled_data:
            logger.warning("No data to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.crawled_data)} sessions to {filename}")
    
    def save_to_csv(self, filename: str = "idweek2025_sessions.csv"):
        """Save crawled data to CSV file (flattened)"""
        if not self.crawled_data:
            logger.warning("No data to save")
            return
        
        def sanitize_csv_field(value):
            """Clean field values to prevent CSV formatting issues"""
            if not isinstance(value, str):
                return value
            # Replace newlines with semicolons, clean up whitespace
            return value.replace('\n', '; ').replace('\r', '').strip()
        
        # Flatten the nested data structure for CSV
        flattened_data = []
        for session in self.crawled_data:
            if 'error' in session:
                continue
                
            # Basic session info
            flat_record = {
                'session_id': session.get('session_id', ''),
                'source_url': session.get('source_url', ''),
                'primary_track': sanitize_csv_field(session.get('tracks', {}).get('primary_track', '')),
                'all_tracks': '; '.join(session.get('tracks', {}).get('all_tracks', [])),
                'track_count': session.get('tracks', {}).get('track_count', 0),
                'session_type': sanitize_csv_field(session.get('session_info', {}).get('type', '')),
                'session_number': sanitize_csv_field(session.get('session_info', {}).get('number', '')),
                'session_title': sanitize_csv_field(session.get('session_info', {}).get('title', '')),
                'full_title': sanitize_csv_field(session.get('session_info', {}).get('full_title', '')),
                'date': sanitize_csv_field(session.get('schedule', {}).get('date', '')),
                'time': sanitize_csv_field(session.get('schedule', {}).get('time', '')),
                'timezone': sanitize_csv_field(session.get('schedule', {}).get('timezone', '')),
                'location': sanitize_csv_field(session.get('schedule', {}).get('location', '')),
            }
            
            # Credit information
            credits = session.get('credits', {})
            flat_record.update({
                'cme_hours': sanitize_csv_field(credits.get('cme_hours', '')),
                'moc_hours': sanitize_csv_field(credits.get('moc_hours', '')),
                'cne_hours': sanitize_csv_field(credits.get('cne_hours', '')),
                'acpe_hours': sanitize_csv_field(credits.get('acpe_hours', '')),
                'acpe_number': sanitize_csv_field(credits.get('acpe_number', '')),
                'pace_hours': sanitize_csv_field(credits.get('pace_hours', '')),
                'ce_broker_hours': sanitize_csv_field(credits.get('ce_broker_hours', '')),
            })
            
            # Speaker information
            speakers = session.get('speakers', [])
            if speakers:
                # Primary speaker
                primary_speaker = speakers[0]
                flat_record.update({
                    'primary_speaker_name': sanitize_csv_field(primary_speaker.get('name', '')),
                    'primary_speaker_title': sanitize_csv_field(primary_speaker.get('title', '')),
                    'primary_speaker_department': sanitize_csv_field(primary_speaker.get('department', '')),
                    'primary_speaker_institution': sanitize_csv_field(primary_speaker.get('institution', '')),
                    'primary_speaker_location': sanitize_csv_field(primary_speaker.get('location', '')),
                })
            
            # Speaker counts and lists
            flat_record['total_speakers'] = len(speakers)
            flat_record['all_speakers'] = sanitize_csv_field('; '.join([s.get('name', '') for s in speakers]))
            
            # Disclosure information
            disclosures = session.get('disclosures', [])
            flat_record['disclosure_count'] = len(disclosures)
            if disclosures:
                disclosure_text = ' | '.join([f"{d.get('speaker', '')}: {d.get('disclosure', '')}" for d in disclosures])
                flat_record['disclosures'] = sanitize_csv_field(disclosure_text)
            else:
                flat_record['disclosures'] = ''
            
            # Presentation information
            presentations = session.get('presentations', [])
            flat_record['presentation_count'] = len(presentations)
            if presentations:
                pres_titles = [p.get('title', '') for p in presentations]
                flat_record['presentation_titles'] = sanitize_csv_field(' | '.join(pres_titles))
                
                pres_times = [p.get('time', '') for p in presentations]
                flat_record['presentation_times'] = sanitize_csv_field(' | '.join(pres_times))
                
                pres_speakers = [p.get('speaker', {}).get('name', '') for p in presentations]
                flat_record['presentation_speakers'] = sanitize_csv_field(' | '.join(pres_speakers))
            else:
                flat_record.update({
                    'presentation_titles': '',
                    'presentation_times': '',
                    'presentation_speakers': ''
                })
            
            flattened_data.append(flat_record)
        
        # Write to CSV
        if flattened_data:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = flattened_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)
            
            logger.info(f"Saved {len(flattened_data)} session records to {filename}")
    
    def save_presentations_csv(self, filename: str = "idweek2025_presentations.csv"):
        """Save individual presentations to separate CSV"""
        if not self.crawled_data:
            logger.warning("No data to save")
            return
        
        presentation_records = []
        
        for session in self.crawled_data:
            if 'error' in session:
                continue
            
            session_info = {
                'session_id': session.get('session_id', ''),
                'session_type': session.get('session_info', {}).get('type', ''),
                'session_title': session.get('session_info', {}).get('title', ''),
                'session_date': session.get('schedule', {}).get('date', ''),
                'session_location': session.get('schedule', {}).get('location', ''),
            }
            
            presentations = session.get('presentations', [])
            for pres in presentations:
                pres_record = session_info.copy()
                pres_record.update({
                    'presentation_id': pres.get('presentation_id', ''),
                    'presentation_time': pres.get('time', ''),
                    'presentation_title': pres.get('title', ''),
                    'speaker_name': pres.get('speaker', {}).get('name', ''),
                    'speaker_affiliation': pres.get('speaker', {}).get('affiliation', ''),
                })
                presentation_records.append(pres_record)
        
        if presentation_records:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = presentation_records[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(presentation_records)
            
            logger.info(f"Saved {len(presentation_records)} presentation records to {filename}")
    
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
    end_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1013
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    
    logger.info(f"Starting IDWeek 2025 session crawl: IDs {start_id}-{end_id} with {delay}s delay")
    
    crawler = IDWeek2025SessionCrawler()
    
    # Crawl the data
    results = crawler.crawl_session_range(start_id, end_id, delay)
    
    # Save results
    crawler.save_to_json()
    crawler.save_to_csv()
    crawler.save_presentations_csv()
    
    # Print statistics
    stats = crawler.get_stats()
    logger.info(f"Crawl complete! Stats: {stats}")


if __name__ == "__main__":
    main()