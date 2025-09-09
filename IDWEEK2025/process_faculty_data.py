#!/usr/bin/env python3
"""
IDWeek 2025 Faculty Data Processor
Processes raw HTML data from IDWEEK_Faculty_2025 table and populates normalized structure
"""

import mysql.connector
import json
import logging
from typing import Dict, List, Optional
from faculty_html_parser import FacultyHTMLParser
import argparse
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faculty_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FacultyDataProcessor:
    """Process faculty HTML data and populate normalized database structure"""
    
    def __init__(self, db_config: Dict):
        """
        Initialize with database configuration
        
        Args:
            db_config: Dictionary with database connection parameters
        """
        self.db_config = db_config
        self.parser = FacultyHTMLParser()
        self.connection = None
        self.stats = {
            'processed': 0,
            'parsed_successfully': 0,
            'parse_errors': 0,
            'db_errors': 0,
            'posters_created': 0,
            'relationships_created': 0
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
    
    def process_all_faculty(self, limit: Optional[int] = None, offset: int = 0):
        """
        Process all faculty records with raw_data
        
        Args:
            limit: Maximum number of records to process
            offset: Number of records to skip
        """
        try:
            self.connect_db()
            cursor = self.connection.cursor(dictionary=True)
            
            # Get faculty records that need processing
            query = """
                SELECT id, presenterid, raw_data 
                FROM IDWEEK_Faculty_2025 
                WHERE raw_data IS NOT NULL 
                AND (parsing_status IS NULL OR parsing_status != 'parsed')
                ORDER BY id
            """
            
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            
            cursor.execute(query)
            faculty_records = cursor.fetchall()
            
            logger.info(f"Found {len(faculty_records)} faculty records to process")
            
            for record in faculty_records:
                self.process_single_faculty(record)
            
            cursor.close()
            self.print_statistics()
            
        except Exception as e:
            logger.error(f"Error processing faculty data: {e}")
            raise
        finally:
            self.disconnect_db()
    
    def process_single_faculty(self, record: Dict):
        """
        Process a single faculty record
        
        Args:
            record: Database record dictionary
        """
        faculty_id = record['id']
        presenter_id = record['presenterid']
        raw_data = record['raw_data']
        
        try:
            logger.info(f"Processing faculty ID {faculty_id}, presenter {presenter_id}")
            
            # Parse the HTML data
            parsed_data = self.parser.parse_faculty_data(raw_data, faculty_id)
            
            # Update faculty table with parsed data
            self.update_faculty_record(faculty_id, parsed_data)
            
            # Process posters if parsing was successful
            if parsed_data['parsing_status'] == 'parsed':
                for poster_data in parsed_data['posters']:
                    poster_id = self.create_or_update_poster(poster_data)
                    if poster_id:
                        self.create_faculty_poster_relationship(faculty_id, poster_id)
                
                self.stats['parsed_successfully'] += 1
            else:
                self.stats['parse_errors'] += 1
            
            self.stats['processed'] += 1
            
            if self.stats['processed'] % 10 == 0:
                logger.info(f"Processed {self.stats['processed']} records so far...")
            
        except Exception as e:
            logger.error(f"Error processing faculty {faculty_id}: {e}")
            self.stats['db_errors'] += 1
            
            # Mark as error in database
            self.mark_faculty_error(faculty_id, str(e))
    
    def update_faculty_record(self, faculty_id: int, parsed_data: Dict):
        """Update faculty record with parsed data"""
        cursor = self.connection.cursor()
        
        faculty_info = parsed_data['faculty']
        
        update_query = """
            UPDATE IDWEEK_Faculty_2025 SET
                full_name = %s,
                credentials = %s,
                job_title = %s,
                organization = %s,
                photo_url = %s,
                email = %s,
                disclosure_info = %s,
                biography = %s,
                parsing_status = %s,
                parse_error_msg = %s,
                dlm = NOW()
            WHERE id = %s
        """
        
        values = (
            faculty_info.get('full_name'),
            faculty_info.get('credentials'),
            faculty_info.get('job_title'),
            faculty_info.get('organization'),
            faculty_info.get('photo_url'),
            faculty_info.get('email'),
            faculty_info.get('disclosure_info'),
            faculty_info.get('biography'),
            parsed_data['parsing_status'],
            parsed_data.get('parse_error'),
            faculty_id
        )
        
        cursor.execute(update_query, values)
        self.connection.commit()
        cursor.close()
    
    def create_or_update_poster(self, poster_data: Dict) -> Optional[str]:
        """
        Create or update poster record
        
        Returns:
            poster_id if successful, None otherwise
        """
        if not poster_data.get('poster_id'):
            return None
        
        cursor = self.connection.cursor()
        
        try:
            # Try to insert, update if already exists
            insert_query = """
                INSERT INTO IDWEEK_Posters_2025 
                (poster_id, poster_number, title, presentation_date, presentation_time, time_zone, url_reference)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    poster_number = VALUES(poster_number),
                    title = VALUES(title),
                    presentation_date = VALUES(presentation_date),
                    presentation_time = VALUES(presentation_time),
                    time_zone = VALUES(time_zone),
                    url_reference = VALUES(url_reference),
                    dlm = NOW()
            """
            
            values = (
                poster_data['poster_id'],
                poster_data.get('poster_number'),
                poster_data.get('title'),
                poster_data.get('presentation_date'),
                poster_data.get('presentation_time'),
                poster_data.get('time_zone'),
                poster_data.get('url_reference')
            )
            
            cursor.execute(insert_query, values)
            
            if cursor.rowcount > 0:
                self.stats['posters_created'] += 1
            
            self.connection.commit()
            return poster_data['poster_id']
            
        except mysql.connector.Error as e:
            logger.error(f"Error creating poster {poster_data.get('poster_id')}: {e}")
            return None
        finally:
            cursor.close()
    
    def create_faculty_poster_relationship(self, faculty_id: int, poster_id: str):
        """Create faculty-poster relationship"""
        cursor = self.connection.cursor()
        
        try:
            insert_query = """
                INSERT IGNORE INTO IDWEEK_Faculty_Posters_2025 
                (faculty_id, poster_id, role)
                VALUES (%s, %s, 'presenter')
            """
            
            cursor.execute(insert_query, (faculty_id, poster_id))
            
            if cursor.rowcount > 0:
                self.stats['relationships_created'] += 1
            
            self.connection.commit()
            
        except mysql.connector.Error as e:
            logger.error(f"Error creating relationship faculty {faculty_id} - poster {poster_id}: {e}")
        finally:
            cursor.close()
    
    def mark_faculty_error(self, faculty_id: int, error_msg: str):
        """Mark faculty record as having a parsing error"""
        try:
            cursor = self.connection.cursor()
            
            update_query = """
                UPDATE IDWEEK_Faculty_2025 SET
                    parsing_status = 'error',
                    parse_error_msg = %s,
                    dlm = NOW()
                WHERE id = %s
            """
            
            cursor.execute(update_query, (error_msg, faculty_id))
            self.connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error marking faculty {faculty_id} as error: {e}")
    
    def print_statistics(self):
        """Print processing statistics"""
        logger.info("=" * 50)
        logger.info("PROCESSING STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total processed: {self.stats['processed']}")
        logger.info(f"Successfully parsed: {self.stats['parsed_successfully']}")
        logger.info(f"Parse errors: {self.stats['parse_errors']}")
        logger.info(f"Database errors: {self.stats['db_errors']}")
        logger.info(f"Posters created/updated: {self.stats['posters_created']}")
        logger.info(f"Faculty-poster relationships: {self.stats['relationships_created']}")
        
        if self.stats['processed'] > 0:
            success_rate = (self.stats['parsed_successfully'] / self.stats['processed']) * 100
            logger.info(f"Success rate: {success_rate:.1f}%")
    
    def get_processing_summary(self):
        """Get summary of what needs to be processed"""
        try:
            self.connect_db()
            cursor = self.connection.cursor(dictionary=True)
            
            # Count records by status
            status_query = """
                SELECT 
                    COALESCE(parsing_status, 'pending') as status,
                    COUNT(*) as count
                FROM IDWEEK_Faculty_2025 
                WHERE raw_data IS NOT NULL
                GROUP BY parsing_status
            """
            
            cursor.execute(status_query)
            status_counts = cursor.fetchall()
            
            logger.info("Current processing status:")
            for row in status_counts:
                logger.info(f"  {row['status']}: {row['count']} records")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error getting processing summary: {e}")
        finally:
            self.disconnect_db()


def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Process IDWeek 2025 Faculty HTML Data')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--port', type=int, default=3306, help='Database port')
    parser.add_argument('--limit', type=int, help='Limit number of records to process')
    parser.add_argument('--offset', type=int, default=0, help='Offset for record processing')
    parser.add_argument('--summary', action='store_true', help='Show processing summary only')
    
    args = parser.parse_args()
    
    db_config = {
        'host': args.host,
        'user': args.user,
        'password': args.password,
        'database': args.database,
        'port': args.port
    }
    
    processor = FacultyDataProcessor(db_config)
    
    if args.summary:
        processor.get_processing_summary()
    else:
        logger.info("Starting faculty data processing...")
        processor.process_all_faculty(limit=args.limit, offset=args.offset)
        logger.info("Processing completed!")


if __name__ == "__main__":
    main()