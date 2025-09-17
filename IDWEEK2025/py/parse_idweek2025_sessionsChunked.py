#!/usr/bin/env python3
"""
IDWeek 2025 Session Crawler - Chunked Version
Crawls local session data in chunks of 300 records, saving each chunk to separate JSON files
Includes resume functionality in case of crashes
"""

import requests
from session_parser_fixed import SessionHTMLParserFixed
import json
import csv
import time
import logging
from typing import List, Dict, Any
import sys
import os
import gzip

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IDWeek2025SessionCrawlerChunked:
    """Chunked crawler for IDWeek 2025 session data from local server"""
    
    def __init__(self, base_url: str = "http://local.dev.conferencecrawler.com/IDWEEK2025/cfml_viewer/sessions.cfm", chunk_size: int = 150):
        self.base_url = base_url
        self.parser = SessionHTMLParserFixed()
        self.session = requests.Session()
        self.chunk_size = chunk_size
        self.all_crawled_data = []
        
    def find_last_completed_chunk(self, base_filename: str = "idweek2025_sessions_chunked") -> int:
        """Find the last completed chunk to resume from"""
        chunk_num = 1
        while (os.path.exists(f"{base_filename}-{chunk_num}.json") or 
               os.path.exists(f"{base_filename}-{chunk_num}.json.gz")):
            chunk_num += 1
        return chunk_num - 1
        
    def get_chunk_range(self, chunk_num: int, total_start: int, total_end: int) -> tuple:
        """Calculate start and end IDs for a specific chunk"""
        chunk_start = total_start + (chunk_num - 1) * self.chunk_size
        chunk_end = min(chunk_start + self.chunk_size - 1, total_end)
        return chunk_start, chunk_end
    
    def clean_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean session data to reduce file size by removing verbose/redundant fields"""
        cleaned = session_data.copy()
        
        # Clean speaker data - keep only essential fields
        if 'speakers' in cleaned and isinstance(cleaned['speakers'], list):
            cleaned_speakers = []
            for speaker in cleaned['speakers'][:5]:  # Limit to first 5 speakers
                cleaned_speaker = {
                    'name': speaker.get('name', ''),
                    'title': speaker.get('title', ''),
                    'institution': speaker.get('institution', '')
                }
                # Only include location if it's different from institution
                location = speaker.get('location', '')
                if location and location != cleaned_speaker['institution']:
                    cleaned_speaker['location'] = location
                cleaned_speakers.append(cleaned_speaker)
            cleaned['speakers'] = cleaned_speakers
        
        # Clean presentations - limit and compress
        if 'presentations' in cleaned and isinstance(cleaned['presentations'], list):
            cleaned_presentations = []
            for pres in cleaned['presentations'][:10]:  # Limit to first 10 presentations
                cleaned_pres = {
                    'title': pres.get('title', ''),
                    'time': pres.get('time', ''),
                }
                # Only include speaker if different from session speakers
                speaker_name = pres.get('speaker', {}).get('name', '')
                if speaker_name:
                    cleaned_pres['speaker_name'] = speaker_name
                cleaned_presentations.append(cleaned_pres)
            cleaned['presentations'] = cleaned_presentations
        
        # Clean disclosures - compress format
        if 'disclosures' in cleaned and isinstance(cleaned['disclosures'], list):
            if len(cleaned['disclosures']) > 5:  # If more than 5, just note the count
                cleaned['disclosures'] = f"[{len(cleaned['disclosures'])} disclosure statements]"
            else:
                # Keep short version
                disc_summary = []
                for disc in cleaned['disclosures']:
                    speaker = disc.get('speaker', '')
                    disclosure = disc.get('disclosure', '')
                    if 'no' in disclosure.lower() or 'none' in disclosure.lower():
                        disc_summary.append(f"{speaker}: None")
                    else:
                        disc_summary.append(f"{speaker}: Has disclosures")
                cleaned['disclosures'] = disc_summary
        
        # Clean tracks - limit to 3 most relevant
        if 'tracks' in cleaned and isinstance(cleaned['tracks'], dict):
            all_tracks = cleaned['tracks'].get('all_tracks', [])
            if len(all_tracks) > 3:
                cleaned['tracks']['all_tracks'] = all_tracks[:3]
                cleaned['tracks']['track_count'] = f"{len(all_tracks)} total"
        
        # Remove source_url to save space (can be reconstructed)
        if 'source_url' in cleaned:
            del cleaned['source_url']
        
        return cleaned
        
    def crawl_session_chunk(self, start_id: int, end_id: int, chunk_num: int, delay: float = 0.5) -> List[Dict[str, Any]]:
        """
        Crawl sessions for a specific chunk range
        
        Args:
            start_id: Starting session ID for this chunk
            end_id: Ending session ID for this chunk
            chunk_num: Chunk number for identification
            delay: Delay between requests in seconds
            
        Returns:
            List of parsed session data for this chunk
        """
        results = []
        failed_ids = []
        
        logger.info(f"=== CHUNK {chunk_num} ===")
        logger.info(f"Crawling sessions {start_id} to {end_id} ({end_id - start_id + 1} sessions)")
        
        for session_id in range(start_id, end_id + 1):
            try:
                url = f"{self.base_url}?thisID={session_id}"
                logger.info(f"Crawling session {session_id}/{end_id} (Chunk {chunk_num}): {url}")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Parse the HTML content
                session_data = self.parser.parse_session_html(response.text)
                session_data['session_id'] = session_id
                session_data['source_url'] = url
                session_data['chunk_number'] = chunk_num
                
                # Clean the session data to reduce file size
                cleaned_session_data = self.clean_session_data(session_data)
                
                results.append(cleaned_session_data)
                
                # Add delay between requests
                if delay > 0:
                    time.sleep(delay)
                    
            except requests.RequestException as e:
                logger.error(f"Request failed for session {session_id}: {e}")
                failed_ids.append(session_id)
                
            except Exception as e:
                logger.error(f"Unexpected error processing session {session_id}: {e}")
                failed_ids.append(session_id)
            
            # Progress update every 25 sessions (more frequent for chunks)
            if session_id % 25 == 0:
                progress_in_chunk = session_id - start_id + 1
                total_in_chunk = end_id - start_id + 1
                logger.info(f"Chunk {chunk_num} progress: {progress_in_chunk}/{total_in_chunk} sessions processed")
        
        if failed_ids:
            logger.warning(f"Chunk {chunk_num}: Failed to process {len(failed_ids)} sessions: {failed_ids}")
        
        return results
        
    def save_chunk_to_json(self, chunk_data: List[Dict[str, Any]], chunk_num: int, filename_base: str = "idweek2025_sessions_chunked", compress: bool = True):
        """Save a single chunk to JSON file (optionally compressed)"""
        if not chunk_data:
            logger.warning(f"No data to save for chunk {chunk_num}")
            return
            
        filename = f"{filename_base}-{chunk_num}.json"
        if compress:
            filename += ".gz"
        
        # Add chunk metadata
        chunk_info = {
            "chunk_info": {
                "chunk_number": chunk_num,
                "chunk_size": len(chunk_data),
                "crawl_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "first_session_id": chunk_data[0]['session_id'] if chunk_data else None,
                "last_session_id": chunk_data[-1]['session_id'] if chunk_data else None,
                "compressed": compress
            },
            "sessions": chunk_data
        }
        
        json_str = json.dumps(chunk_info, separators=(',', ':'), ensure_ascii=False)
        
        if compress:
            with gzip.open(filename, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        # Get file size for logging
        file_size = os.path.getsize(filename)
        size_str = f"{file_size:,} bytes"
        if file_size > 1024:
            size_str += f" ({file_size/1024:.1f} KB)"
        if file_size > 1024*1024:
            size_str += f" ({file_size/(1024*1024):.1f} MB)"
            
        logger.info(f"✅ Saved chunk {chunk_num}: {len(chunk_data)} sessions to {filename} ({size_str})")
        
    def crawl_all_chunks(self, start_id: int = 1, end_id: int = 1013, delay: float = 0.5, resume: bool = True):
        """
        Crawl all sessions in chunks, with resume capability
        
        Args:
            start_id: Overall starting session ID
            end_id: Overall ending session ID  
            delay: Delay between requests in seconds
            resume: Whether to resume from last completed chunk
        """
        
        # Calculate total chunks needed
        total_sessions = end_id - start_id + 1
        total_chunks = (total_sessions + self.chunk_size - 1) // self.chunk_size
        
        logger.info(f"Starting chunked crawl: {total_sessions} sessions across {total_chunks} chunks")
        logger.info(f"Chunk size: {self.chunk_size} sessions per chunk")
        
        start_chunk = 1
        if resume:
            last_completed = self.find_last_completed_chunk()
            if last_completed > 0:
                start_chunk = last_completed + 1
                logger.info(f"Resuming from chunk {start_chunk} (found {last_completed} completed chunks)")
        
        failed_chunks = []
        
        for chunk_num in range(start_chunk, total_chunks + 1):
            try:
                logger.info(f"\n🚀 Starting chunk {chunk_num}/{total_chunks}")
                
                # Calculate range for this chunk
                chunk_start, chunk_end = self.get_chunk_range(chunk_num, start_id, end_id)
                
                # Crawl this chunk
                chunk_data = self.crawl_session_chunk(chunk_start, chunk_end, chunk_num, delay)
                
                # Save chunk immediately
                self.save_chunk_to_json(chunk_data, chunk_num)
                
                # Add to overall data collection
                self.all_crawled_data.extend(chunk_data)
                
                logger.info(f"✅ Chunk {chunk_num} completed successfully!")
                
                # Small delay between chunks
                if chunk_num < total_chunks:
                    logger.info("Pausing 2 seconds between chunks...")
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Chunk {chunk_num} failed with error: {e}")
                failed_chunks.append(chunk_num)
                continue
        
        # Final summary
        completed_chunks = total_chunks - len(failed_chunks)
        logger.info(f"\n=== CRAWL SUMMARY ===")
        logger.info(f"Total chunks: {total_chunks}")
        logger.info(f"Completed chunks: {completed_chunks}")
        logger.info(f"Failed chunks: {len(failed_chunks)} {failed_chunks if failed_chunks else ''}")
        logger.info(f"Total sessions processed: {len(self.all_crawled_data)}")
        
        return self.all_crawled_data
        
    def combine_chunks_to_final_files(self, base_filename: str = "idweek2025_sessions_chunked"):
        """Combine all chunk files into final consolidated files"""
        chunk_num = 1
        all_sessions = []
        
        # Load all chunk files (check both compressed and uncompressed)
        while True:
            filename = f"{base_filename}-{chunk_num}.json"
            filename_gz = f"{base_filename}-{chunk_num}.json.gz"
            
            if os.path.exists(filename_gz):
                logger.info(f"Loading {filename_gz}")
                try:
                    with gzip.open(filename_gz, 'rt', encoding='utf-8') as f:
                        chunk_data = json.load(f)
                        sessions = chunk_data.get('sessions', [])
                        all_sessions.extend(sessions)
                        logger.info(f"Loaded {len(sessions)} sessions from chunk {chunk_num}")
                except Exception as e:
                    logger.error(f"Error loading chunk {chunk_num}: {e}")
            elif os.path.exists(filename):
                logger.info(f"Loading {filename}")
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        chunk_data = json.load(f)
                        sessions = chunk_data.get('sessions', [])
                        all_sessions.extend(sessions)
                        logger.info(f"Loaded {len(sessions)} sessions from chunk {chunk_num}")
                except Exception as e:
                    logger.error(f"Error loading chunk {chunk_num}: {e}")
            else:
                break
                
            chunk_num += 1
        
        if not all_sessions:
            logger.warning("No session data found in chunk files")
            return
            
        # Save combined JSON
        combined_filename = "idweek2025_sessions_combined.json"
        with open(combined_filename, 'w', encoding='utf-8') as f:
            json.dump(all_sessions, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved {len(all_sessions)} sessions to {combined_filename}")
        
        # Save combined CSV
        self.all_crawled_data = all_sessions
        self.save_to_csv("idweek2025_sessions_combined.csv")
        self.save_presentations_csv("idweek2025_presentations_combined.csv")
        
    def save_to_csv(self, filename: str = "idweek2025_sessions_combined.csv"):
        """Save crawled data to CSV file (flattened) - same as original"""
        if not self.all_crawled_data:
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
        for session in self.all_crawled_data:
            if 'error' in session:
                continue
                
            # Basic session info
            flat_record = {
                'session_id': session.get('session_id', ''),
                'source_url': session.get('source_url', ''),
                'chunk_number': session.get('chunk_number', ''),
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
            
            logger.info(f"✅ Saved {len(flattened_data)} session records to {filename}")
    
    def save_presentations_csv(self, filename: str = "idweek2025_presentations_combined.csv"):
        """Save individual presentations to separate CSV"""
        if not self.all_crawled_data:
            logger.warning("No data to save")
            return
        
        presentation_records = []
        
        for session in self.all_crawled_data:
            if 'error' in session:
                continue
            
            session_info = {
                'session_id': session.get('session_id', ''),
                'chunk_number': session.get('chunk_number', ''),
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
            
            logger.info(f"✅ Saved {len(presentation_records)} presentation records to {filename}")
    
    def get_stats(self):
        """Get crawling statistics"""
        parser_stats = self.parser.get_stats()
        return {
            'total_crawled': len(self.all_crawled_data),
            'successful_parses': parser_stats['parsed_count'],
            'parse_errors': parser_stats['error_count']
        }


def main():
    """Main crawling function"""
    # Parse command line arguments
    start_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1013
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    chunk_size = int(sys.argv[4]) if len(sys.argv) > 4 else 150
    
    logger.info(f"Starting IDWeek 2025 chunked session crawl")
    logger.info(f"Range: IDs {start_id}-{end_id}")
    logger.info(f"Delay: {delay}s between requests")
    logger.info(f"Chunk size: {chunk_size} sessions per chunk")
    
    crawler = IDWeek2025SessionCrawlerChunked(chunk_size=chunk_size)
    
    # Crawl all chunks
    crawler.crawl_all_chunks(start_id, end_id, delay, resume=True)
    
    # Combine chunks into final files
    logger.info("\n📋 Combining all chunks into final files...")
    crawler.combine_chunks_to_final_files()
    
    # Print final statistics
    stats = crawler.get_stats()
    logger.info(f"\n=== FINAL STATS ===")
    logger.info(f"Total sessions processed: {stats['total_crawled']}")
    logger.info(f"Successful parses: {stats['successful_parses']}")
    logger.info(f"Parse errors: {stats['parse_errors']}")
    logger.info(f"✅ Chunked crawl complete!")


if __name__ == "__main__":
    main()