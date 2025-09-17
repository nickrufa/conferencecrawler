#!/usr/bin/env python3
"""
Faculty Deduplication and Cross-Conference Processor
Migrates faculty data to normalized structure and handles cross-conference matching
"""

import mysql.connector
import logging
import re
from typing import Dict, List, Optional, Tuple
from faculty_html_parser import FacultyHTMLParser
import argparse
from difflib import SequenceMatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faculty_deduplication.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FacultyDeduplicationProcessor:
    """Process and deduplicate faculty across conferences"""
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.parser = FacultyHTMLParser()
        self.connection = None
        self.stats = {
            'faculty_processed': 0,
            'new_faculty_created': 0,
            'existing_faculty_matched': 0,
            'posters_migrated': 0,
            'relationships_created': 0,
            'parsing_errors': 0
        }
    
    def connect_db(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Database connection established")
        except mysql.connector.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def normalize_name(self, full_name: str) -> str:
        """Normalize faculty name for matching across conferences"""
        if not full_name:
            return ""
        
        # Remove credentials
        name = re.sub(r',\s*(MD|PhD|PharmD|MPH|MS|MSc|DrPH|DO|DVM|RN|PA|NP|APRN|CPhT|RPh)(\s*,\s*(MD|PhD|PharmD|MPH|MS|MSc|DrPH|DO|DVM|RN|PA|NP|APRN|CPhT|RPh))*\s*$', '', full_name, flags=re.IGNORECASE)
        
        # Normalize whitespace and convert to lowercase
        name = re.sub(r'\s+', ' ', name.strip().lower())
        
        return name
    
    def find_matching_faculty(self, normalized_name: str, email: str = None) -> Optional[int]:
        """Find existing faculty by normalized name or email"""
        cursor = self.connection.cursor()
        
        try:
            # First try exact normalized name match
            if normalized_name:
                cursor.execute(
                    "SELECT faculty_id FROM Faculty_Master WHERE normalized_name = %s",
                    (normalized_name,)
                )
                result = cursor.fetchone()
                if result:
                    return result[0]
            
            # Then try email match
            if email:
                cursor.execute(
                    "SELECT faculty_id FROM Faculty_Master WHERE email = %s",
                    (email,)
                )
                result = cursor.fetchone()
                if result:
                    return result[0]
            
            # Finally try fuzzy matching on normalized names
            if normalized_name:
                cursor.execute("SELECT faculty_id, normalized_name FROM Faculty_Master")
                all_faculty = cursor.fetchall()
                
                for faculty_id, existing_name in all_faculty:
                    if existing_name and self._names_similar(normalized_name, existing_name):
                        logger.info(f"Fuzzy match found: '{normalized_name}' -> '{existing_name}' (ID: {faculty_id})")
                        return faculty_id
            
            return None
            
        except mysql.connector.Error as e:
            logger.error(f"Error finding matching faculty: {e}")
            return None
        finally:
            cursor.close()
    
    def _names_similar(self, name1: str, name2: str, threshold: float = 0.9) -> bool:
        """Check if two normalized names are similar enough to be the same person"""
        if not name1 or not name2:
            return False
        
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Also check if one name is contained in the other (for middle name variations)
        name1_words = set(name1.split())
        name2_words = set(name2.split())
        
        # If all words from shorter name are in longer name
        if len(name1_words) <= len(name2_words):
            word_match = name1_words.issubset(name2_words)
        else:
            word_match = name2_words.issubset(name1_words)
        
        return similarity >= threshold or (word_match and similarity >= 0.8)
    
    def create_or_update_faculty(self, faculty_data: Dict, conference_data: Dict) -> int:
        """Create new faculty or update existing one"""
        normalized_name = self.normalize_name(faculty_data.get('full_name', ''))
        email = faculty_data.get('email')
        
        # Try to find existing faculty
        faculty_id = self.find_matching_faculty(normalized_name, email)
        
        cursor = self.connection.cursor()
        
        try:
            if faculty_id:
                # Update existing faculty
                logger.info(f"Updating existing faculty ID {faculty_id}: {faculty_data.get('full_name')}")
                
                update_query = """
                    UPDATE Faculty_Master SET
                        full_name = COALESCE(%s, full_name),
                        credentials = COALESCE(%s, credentials),
                        email = COALESCE(%s, email),
                        photo_url = COALESCE(%s, photo_url),
                        primary_organization = COALESCE(%s, primary_organization),
                        biography = COALESCE(%s, biography),
                        disclosure_info = COALESCE(%s, disclosure_info),
                        updated_date = NOW()
                    WHERE faculty_id = %s
                """
                
                cursor.execute(update_query, (
                    faculty_data.get('full_name'),
                    faculty_data.get('credentials'),
                    faculty_data.get('email'),
                    faculty_data.get('photo_url'),
                    faculty_data.get('organization'),
                    faculty_data.get('biography'),
                    faculty_data.get('disclosure_info'),
                    faculty_id
                ))
                
                self.stats['existing_faculty_matched'] += 1
                
            else:
                # Create new faculty
                logger.info(f"Creating new faculty: {faculty_data.get('full_name')}")
                
                insert_query = """
                    INSERT INTO Faculty_Master 
                    (full_name, normalized_name, credentials, email, photo_url, 
                     primary_organization, biography, disclosure_info)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    faculty_data.get('full_name'),
                    normalized_name,
                    faculty_data.get('credentials'),
                    faculty_data.get('email'),
                    faculty_data.get('photo_url'),
                    faculty_data.get('organization'),
                    faculty_data.get('biography'),
                    faculty_data.get('disclosure_info')
                ))
                
                faculty_id = cursor.lastrowid
                self.stats['new_faculty_created'] += 1
            
            # Create conference participation record
            self.create_conference_participation(faculty_id, conference_data, cursor)
            
            self.connection.commit()
            return faculty_id
            
        except mysql.connector.Error as e:
            logger.error(f"Error creating/updating faculty: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def create_conference_participation(self, faculty_id: int, conference_data: Dict, cursor):
        """Create conference participation record"""
        insert_query = """
            INSERT INTO Faculty_Conference_Participation
            (faculty_id, conference_year, conference_name, presenter_id, 
             job_title, organization, raw_data, parsing_status, parse_error_msg)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                job_title = VALUES(job_title),
                organization = VALUES(organization),
                raw_data = VALUES(raw_data),
                parsing_status = VALUES(parsing_status),
                parse_error_msg = VALUES(parse_error_msg),
                updated_date = NOW()
        """
        
        cursor.execute(insert_query, (
            faculty_id,
            conference_data['conference_year'],
            conference_data['conference_name'],
            conference_data['presenter_id'],
            conference_data.get('job_title'),
            conference_data.get('organization'),
            conference_data.get('raw_data'),
            conference_data.get('parsing_status', 'parsed'),
            conference_data.get('parse_error_msg')
        ))
    
    def migrate_posters(self, old_posters: List[Dict], faculty_id: int, conference_year: int, conference_name: str):
        """Migrate poster data to new structure"""
        cursor = self.connection.cursor()
        
        try:
            for poster_data in old_posters:
                if not poster_data.get('poster_id'):
                    continue
                
                # Create/update poster
                poster_insert_query = """
                    INSERT INTO Conference_Posters
                    (poster_id, conference_year, conference_name, poster_number, 
                     title, presentation_date, presentation_time, time_zone, url_reference)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        poster_number = VALUES(poster_number),
                        title = VALUES(title),
                        presentation_date = VALUES(presentation_date),
                        presentation_time = VALUES(presentation_time),
                        time_zone = VALUES(time_zone),
                        url_reference = VALUES(url_reference),
                        updated_date = NOW()
                """
                
                cursor.execute(poster_insert_query, (
                    poster_data['poster_id'],
                    conference_year,
                    conference_name,
                    poster_data.get('poster_number'),
                    poster_data.get('title'),
                    poster_data.get('presentation_date'),
                    poster_data.get('presentation_time'),
                    poster_data.get('time_zone'),
                    poster_data.get('url_reference')
                ))
                
                # Get poster_db_id
                cursor.execute(
                    "SELECT poster_db_id FROM Conference_Posters WHERE poster_id = %s AND conference_year = %s AND conference_name = %s",
                    (poster_data['poster_id'], conference_year, conference_name)
                )
                poster_db_id = cursor.fetchone()[0]
                
                # Create faculty-poster relationship
                relationship_query = """
                    INSERT IGNORE INTO Faculty_Poster_Relationships
                    (faculty_id, poster_db_id, role)
                    VALUES (%s, %s, 'presenter')
                """
                
                cursor.execute(relationship_query, (faculty_id, poster_db_id))
                
                self.stats['posters_migrated'] += 1
                self.stats['relationships_created'] += 1
            
            self.connection.commit()
            
        except mysql.connector.Error as e:
            logger.error(f"Error migrating posters: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def process_idweek_2025_data(self):
        """Process IDWeek 2025 faculty data"""
        try:
            self.connect_db()
            cursor = self.connection.cursor(dictionary=True)
            
            # Get all IDWeek 2025 faculty records with raw data
            cursor.execute("""
                SELECT id, presenterid, raw_data 
                FROM IDWEEK_Faculty_2025 
                WHERE raw_data IS NOT NULL
            """)
            
            records = cursor.fetchall()
            logger.info(f"Found {len(records)} IDWeek 2025 faculty records to process")
            
            for record in records:
                try:
                    # Parse HTML data
                    parsed_data = self.parser.parse_faculty_data(record['raw_data'], record['id'])
                    
                    if parsed_data['parsing_status'] == 'error':
                        self.stats['parsing_errors'] += 1
                        continue
                    
                    # Prepare conference data
                    conference_data = {
                        'conference_year': 2025,
                        'conference_name': 'IDWEEK',
                        'presenter_id': record['presenterid'],
                        'job_title': parsed_data['faculty'].get('job_title'),
                        'organization': parsed_data['faculty'].get('organization'),
                        'raw_data': record['raw_data'],
                        'parsing_status': 'parsed'
                    }
                    
                    # Create or match faculty
                    faculty_id = self.create_or_update_faculty(parsed_data['faculty'], conference_data)
                    
                    # Migrate posters
                    self.migrate_posters(parsed_data['posters'], faculty_id, 2025, 'IDWEEK')
                    
                    # Create migration tracking record
                    self.create_migration_record(faculty_id, 'IDWEEK_Faculty_2025', record['id'], 2025, 'IDWEEK')
                    
                    self.stats['faculty_processed'] += 1
                    
                    if self.stats['faculty_processed'] % 10 == 0:
                        logger.info(f"Processed {self.stats['faculty_processed']} faculty records...")
                
                except Exception as e:
                    logger.error(f"Error processing record {record['id']}: {e}")
                    continue
            
            cursor.close()
            self.print_stats()
            
        except Exception as e:
            logger.error(f"Error processing IDWeek 2025 data: {e}")
            raise
        finally:
            self.disconnect_db()
    
    def create_migration_record(self, faculty_id: int, old_table: str, old_id: int, year: int, conference: str):
        """Create migration tracking record"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT IGNORE INTO Faculty_ID_Migration
                (new_faculty_id, old_table_name, old_record_id, conference_year, conference_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (faculty_id, old_table, old_id, year, conference))
            self.connection.commit()
        except mysql.connector.Error as e:
            logger.error(f"Error creating migration record: {e}")
        finally:
            cursor.close()
    
    def print_stats(self):
        """Print processing statistics"""
        logger.info("=" * 50)
        logger.info("FACULTY DEDUPLICATION STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Faculty processed: {self.stats['faculty_processed']}")
        logger.info(f"New faculty created: {self.stats['new_faculty_created']}")
        logger.info(f"Existing faculty matched: {self.stats['existing_faculty_matched']}")
        logger.info(f"Posters migrated: {self.stats['posters_migrated']}")
        logger.info(f"Relationships created: {self.stats['relationships_created']}")
        logger.info(f"Parsing errors: {self.stats['parsing_errors']}")
        
        if self.stats['faculty_processed'] > 0:
            match_rate = (self.stats['existing_faculty_matched'] / self.stats['faculty_processed']) * 100
            logger.info(f"Faculty match rate: {match_rate:.1f}%")


def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Process Faculty Data with Deduplication')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--port', type=int, default=3306, help='Database port')
    
    args = parser.parse_args()
    
    db_config = {
        'host': args.host,
        'user': args.user,
        'password': args.password,
        'database': args.database,
        'port': args.port
    }
    
    processor = FacultyDeduplicationProcessor(db_config)
    logger.info("Starting faculty deduplication processing...")
    processor.process_idweek_2025_data()
    logger.info("Processing completed!")


if __name__ == "__main__":
    main()