import mysql.connector
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='eccmid_extraction.log'
)

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '5melly0nion',
    'database': 'medinfo'
}

def connect_to_database():
    """Establish connection to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("Successfully connected to database")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL: {err}")
        raise

def extract_session_id(html_content):
    """Extract session ID from the class attribute of the first div"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        first_div = soup.find('div', id='modal-sessions-div')
        if first_div and 'class' in first_div.attrs:
            class_string = first_div['class']
            session_id_match = re.search(r'session-id-(\d+)', ' '.join(class_string))
            if session_id_match:
                return session_id_match.group(1)
        return None
    except Exception as e:
        logging.error(f"Error extracting session ID: {e}")
        return None

def extract_session_data(html_content):
    """Extract all relevant session information from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract data into a dictionary
        data = {
            'session_id': None,
            'session_type': None,
            'session_title': None,
            'session_hall': None,
            'session_date': None,
            'session_time_start': None,
            'session_time_end': None,
            'session_timezone': None,
            'session_category': None,
            'session_description': None,
            'session_organized_by': None,
            'session_chairs': [],
            'session_presentations': []
        }
        
        # Get session ID from class
        first_div = soup.find('div', id='modal-sessions-div')
        if first_div and 'class' in first_div.attrs:
            class_string = ' '.join(first_div['class'])
            session_id_match = re.search(r'session-id-(\d+)', class_string)
            if session_id_match:
                data['session_id'] = session_id_match.group(1)
        
        # Get session type
        session_type_elem = soup.select_one('.session-details-cotype-name')
        if session_type_elem:
            data['session_type'] = session_type_elem.text.strip()
        
        # Get session title
        title_elem = soup.find('h3')
        if title_elem:
            data['session_title'] = title_elem.text.strip()
        
        # Get hall, date, time
        header_div = soup.select_one('.modal-session-header')
        if header_div:
            location_info = header_div.find(text=True, recursive=False)
            if location_info:
                location_text = location_info.strip()
                
                # Extract hall
                hall_match = re.search(r'Hall\s+(\d+)', location_text)
                if hall_match:
                    data['session_hall'] = f"Hall {hall_match.group(1)}"
                
                # Extract date and time
                date_match = re.search(r'(\d{2}/\d{2})', location_text)
                if date_match:
                    data['session_date'] = date_match.group(1)
                
                time_match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', location_text)
                if time_match:
                    data['session_time_start'] = time_match.group(1)
                    data['session_time_end'] = time_match.group(2)
            
            # Get timezone
            timezone_elem = header_div.select_one('.modal-session-abbr-timezone')
            if timezone_elem:
                data['session_timezone'] = timezone_elem.text.strip()
        
        # Get category
        category_elem = soup.select_one('.modal-cat-name')
        if category_elem:
            data['session_category'] = category_elem.text.strip()
        
        # Get description
        desc_elem = soup.select_one('.modal-program-detail-session-desc')
        if desc_elem:
            data['session_description'] = desc_elem.text.strip()
        
        # Get organized by
        organized_by_elem = soup.select_one('.modal-session-organized-by strong')
        if organized_by_elem:
            data['session_organized_by'] = organized_by_elem.text.strip()
        
        # Get chairs
        chairs_container = soup.select_one('.modal-session-moderators')
        if chairs_container:
            chair_elements = chairs_container.select('.modal-session-faculties')
            for chair in chair_elements:
                chair_name = chair.text.strip()
                data['session_chairs'].append(chair_name)
        
        # Get presentations - now with more detailed information
        presentations_container = soup.select_one('.modal-sessions-interventions')
        if presentations_container:
            presentation_groups = presentations_container.select('.modal-sessions-interventions-group')
            
            for group in presentation_groups:
                presentation = {
                    'title': None,
                    'presenters': [],
                    'presenter_details': []  # New field for more detailed presenter info
                }
                
                # Get presentation title
                title_span = group.find('span', style="font-weight: bold")
                if title_span:
                    presentation['title'] = title_span.text.strip()
                
                # Get presenters with more details
                presenter_divs = group.select('.clearfix')
                for presenter_div in presenter_divs:
                    faculty_div = presenter_div.select_one('.modal-session-faculties')
                    if faculty_div:
                        # Get full presenter text (name and country)
                        presenter_text = faculty_div.text.strip()
                        presentation['presenters'].append(presenter_text)
                        
                        # Extract firstname, lastname, and country separately
                        firstname_span = faculty_div.select_one('.fo-user__firstname-speaker')
                        lastname_span = faculty_div.select_one('.fo-user__lastname-speaker')
                        
                        presenter_details = {}
                        if firstname_span:
                            presenter_details['firstname'] = firstname_span.text.strip()
                        if lastname_span:
                            presenter_details['lastname'] = lastname_span.text.strip()
                        
                        # Extract country if available
                        country_match = re.search(r',\s*([^,]+)$', presenter_text)

def format_extracted_data(data):
    """Format the extracted data for SQL update"""
    # Format chairs list to string
    chairs_str = '; '.join(data.get('session_chairs', []))
    
    # Format presentations list to a more detailed string
    presentations = []
    for p in data.get('session_presentations', []):
        title = p.get('title', '')
        presenters = '; '.join(p.get('presenters', []))
        
        # Format presenter details if available
        presenter_details = []
        for pd in p.get('presenter_details', []):
            pd_str = ""
            if pd.get('firstname') and pd.get('lastname'):
                pd_str += f"{pd.get('firstname')} {pd.get('lastname')}"
            if pd.get('country'):
                pd_str += f", {pd.get('country')}"
            if pd.get('data_id'):
                pd_str += f" (ID: {pd.get('data_id')})"
            presenter_details.append(pd_str)
        
        presenter_details_str = ' | '.join(presenter_details)
        presentations.append(f"{title} [{presenters}] [{presenter_details_str}]")
    
    presentations_str = ' || '.join(presentations)
    
    # Create a formatted data dictionary for SQL update
    formatted_data = {
        'session_id': data.get('session_id'),
        'session_type': data.get('session_type'),
        'session_title': data.get('session_title'),
        'session_hall': data.get('session_hall'),
        'session_date': data.get('session_date'),
        'session_time_start': data.get('session_time_start'),
        'session_time_end': data.get('session_time_end'),
        'session_timezone': data.get('session_timezone'),
        'session_category': data.get('session_category'),
        'session_description': data.get('session_description'),
        'session_organized_by': data.get('session_organized_by'),
        'session_chairs': chairs_str,
        'session_presentations': presentations_str
    }
    
    return formatted_data

# This function is no longer needed as we're using a different approach with a temporary table
# Keeping it commented for reference
"""
def update_session_record(conn, record_id, data):
    Update a session record with extracted data
    try:
        cursor = conn.cursor()
        
        # Define the columns to update
        cols_to_update = [
            'sessionType', 'sessionTitle', 'sessionHall', 'sessionDate',
            'sessionTimeStart', 'sessionTimeEnd', 'sessionTimezone',
            'sessionCategory', 'sessionDescription', 'sessionOrganizedBy',
            'sessionChairs', 'sessionPresentations'
        ]
        
        # Map the formatted data to table columns
        update_values = {
            'sessionType': data.get('session_type'),
            'sessionTitle': data.get('session_title'),
            'sessionHall': data.get('session_hall'),
            'sessionDate': data.get('session_date'),
            'sessionTimeStart': data.get('session_time_start'),
            'sessionTimeEnd': data.get('session_time_end'),
            'sessionTimezone': data.get('session_timezone'),
            'sessionCategory': data.get('session_category'),
            'sessionDescription': data.get('session_description'),
            'sessionOrganizedBy': data.get('session_organized_by'),
            'sessionChairs': data.get('session_chairs'),
            'sessionPresentations': data.get('session_presentations')
        }
        
        # Build the SQL update query
        set_clause = ', '.join([f"{col} = %s" for col in cols_to_update])
        query = f"UPDATE ECCMID_2025 SET {set_clause} WHERE id = %s"
        
        # Create the parameters list in the correct order
        params = [update_values[col] for col in cols_to_update]
        params.append(record_id)
        
        # Execute the update
        cursor.execute(query, params)
        conn.commit()
        
        logging.info(f"Updated record ID {record_id} successfully")
        return True
    
    except mysql.connector.Error as err:
        logging.error(f"Error updating record: {err}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
"""

def process_all_records():
    """Process all records in the database"""
    conn = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        
        # Create a temporary table to hold the extracted data
        try:
            cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS ECC_Extracted (
                id INT NOT NULL,
                session_id VARCHAR(25),
                session_type VARCHAR(255),
                session_title VARCHAR(255),
                session_hall VARCHAR(50),
                session_date VARCHAR(50),
                session_time_start VARCHAR(50),
                session_time_end VARCHAR(50),
                session_timezone VARCHAR(50),
                session_category VARCHAR(255),
                session_description TEXT,
                session_organized_by VARCHAR(255),
                session_chairs TEXT,
                session_presentations TEXT,
                PRIMARY KEY (id)
            )
            """)
            
            # Create a temporary table for presentations (sub-sessions)
            cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS ECC_Presentations (
                id INT NOT NULL AUTO_INCREMENT,
                parent_session_id INT,
                presentation_title VARCHAR(255),
                presentation_order INT,
                presenters TEXT,
                presenter_details TEXT,
                PRIMARY KEY (id),
                INDEX (parent_session_id)
            )
            """)
            
            conn.commit()
            logging.info("Temporary tables created successfully")
        except mysql.connector.Error as err:
            logging.error(f"Error creating temporary tables: {err}")
            conn.rollback()
            return
        
        # Query to get all records
        cursor.execute("SELECT id, sessionId, sessionData FROM ECCMID_2025")
        records = cursor.fetchall()
        
        processed_count = 0
        error_count = 0
        presentation_count = 0
        
        for record in records:
            record_id = record['id']
            html_content = record['sessionData']
            
            if not html_content:
                logging.warning(f"Record ID {record_id}: Empty sessionData")
                continue
            
            # Extract and process the data
            extracted_data = extract_session_data(html_content)
            
            if not extracted_data or not extracted_data.get('session_id'):
                logging.warning(f"Record ID {record_id}: Could not extract complete data")
                error_count += 1
                continue
            
            # Verify the extracted session ID matches the recorded one (if available)
            if record['sessionId'] and extracted_data.get('session_id') and record['sessionId'] != f"session-id-{extracted_data.get('session_id')}":
                logging.warning(f"Record ID {record_id}: SessionID mismatch. DB: {record['sessionId']}, Extracted: session-id-{extracted_data.get('session_id')}")
            
            # Format the extracted data
            formatted_data = format_extracted_data(extracted_data)
            
            # Insert the formatted data into the temporary table
            try:
                insert_query = """
                INSERT INTO ECC_Extracted (
                    id, session_id, session_type, session_title, session_hall, 
                    session_date, session_time_start, session_time_end, session_timezone,
                    session_category, session_description, session_organized_by,
                    session_chairs, session_presentations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                insert_params = (
                    record_id, 
                    formatted_data.get('session_id'),
                    formatted_data.get('session_type'),
                    formatted_data.get('session_title'),
                    formatted_data.get('session_hall'),
                    formatted_data.get('session_date'),
                    formatted_data.get('session_time_start'),
                    formatted_data.get('session_time_end'),
                    formatted_data.get('session_timezone'),
                    formatted_data.get('session_category'),
                    formatted_data.get('session_description'),
                    formatted_data.get('session_organized_by'),
                    formatted_data.get('session_chairs'),
                    formatted_data.get('session_presentations')
                )
                cursor.execute(insert_query, insert_params)
                
                # Insert the presentations into the presentations table
                for idx, presentation in enumerate(extracted_data.get('session_presentations', [])):
                    presentation_title = presentation.get('title', '')
                    presenters_text = '; '.join(presentation.get('presenters', []))
                    presenter_details = json.dumps(presentation.get('presenter_details', []))
                    
                    presentation_insert = """
                    INSERT INTO ECC_Presentations (
                        parent_session_id, presentation_title, presentation_order, 
                        presenters, presenter_details
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(presentation_insert, (
                        record_id,
                        presentation_title,
                        idx + 1,
                        presenters_text,
                        presenter_details
                    ))
                    presentation_count += 1
                
                conn.commit()
                processed_count += 1
                
            except mysql.connector.Error as err:
                logging.error(f"Error inserting into temporary table for record {record_id}: {err}")
                conn.rollback()
                error_count += 1
        
        # Print summary of extraction results
        logging.info(f"Processing complete. Total records: {len(records)}, Processed: {processed_count}, Presentations: {presentation_count}, Errors: {error_count}")
        
        # Optionally view the extracted data
        cursor.execute("SELECT * FROM ECC_Extracted LIMIT 5")
        sample_results = cursor.fetchall()
        logging.info(f"Sample of extracted session data: {sample_results}")
        
        cursor.execute("SELECT * FROM ECC_Presentations LIMIT 5")
        sample_presentations = cursor.fetchall()
        logging.info(f"Sample of extracted presentation data: {sample_presentations}")
        
        # Provide options to update the main table or export data
        print("\nExtraction complete. Options:")
        print("1. Update the main ECCMID_2025 table with the extracted data")
        print("2. Export all extracted data to CSV files")
        print("3. Create a new table for presentations (sub-sessions)")
        print("4. Exit without updating")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            # Update the main ECCMID_2025 table with the extracted data
            try:
                cursor.execute("""
                ALTER TABLE ECCMID_2025 
                ADD COLUMN IF NOT EXISTS sessionTitle VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionHall VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionDate VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimeStart VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimeEnd VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimezone VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionCategory VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionDescription TEXT,
                ADD COLUMN IF NOT EXISTS sessionOrganizedBy VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionChairs TEXT,
                ADD COLUMN IF NOT EXISTS sessionPresentations TEXT
                """)
                
                update_query = """
                UPDATE ECCMID_2025 e
                JOIN ECC_Extracted ex ON e.id = ex.id
                SET 
                    e.sessionType = ex.session_type,
                    e.sessionTitle = ex.session_title,
                    e.sessionHall = ex.session_hall,
                    e.sessionDate = ex.session_date,
                    e.sessionLocalStart = ex.session_time_start,
                    e.sessionLocalEnd = ex.session_time_end,
                    e.sessionTimezone = ex.session_timezone,
                    e.sessionCategory = ex.session_category,
                    e.sessionDescription = ex.session_description,
                    e.sessionOrganizedBy = ex.session_organized_by,
                    e.sessionChairs = ex.session_chairs,
                    e.sessionPresentations = ex.session_presentations
                """
                cursor.execute(update_query)
                conn.commit()
                print(f"Successfully updated {cursor.rowcount} records in the main ECCMID_2025 table.")
                logging.info(f"Successfully updated {cursor.rowcount} records in the main ECCMID_2025 table.")
            except mysql.connector.Error as err:
                logging.error(f"Error updating main table: {err}")
                conn.rollback()
                print(f"Error updating main table: {err}")
        
        elif choice == '2':
            # Export both tables to CSV
            import csv
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sessions_filename = f"eccmid_sessions_{timestamp}.csv"
            presentations_filename = f"eccmid_presentations_{timestamp}.csv"
            
            # Export sessions
            cursor.execute("SELECT * FROM ECC_Extracted")
            sessions_data = cursor.fetchall()
            
            with open(sessions_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                if sessions_data:
                    csv_writer.writerow(sessions_data[0].keys())
                    # Write data
                    for row in sessions_data:
                        csv_writer.writerow(row.values())
            
            # Export presentations
            cursor.execute("SELECT * FROM ECC_Presentations")
            presentations_data = cursor.fetchall()
            
            with open(presentations_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                if presentations_data:
                    csv_writer.writerow(presentations_data[0].keys())
                    # Write data
                    for row in presentations_data:
                        csv_writer.writerow(row.values())
            
            print(f"Sessions data exported to {sessions_filename}")
            print(f"Presentations data exported to {presentations_filename}")
            logging.info(f"Data exported to {sessions_filename} and {presentations_filename}")
            
        elif choice == '3':
            # Create a new permanent table for presentations
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS ECC_Session_Presentations (
                    id INT NOT NULL AUTO_INCREMENT,
                    parent_session_id INT,
                    presentation_title VARCHAR(255),
                    presentation_order INT,
                    presenters TEXT,
                    presenter_details TEXT,
                    PRIMARY KEY (id),
                    INDEX (parent_session_id),
                    FOREIGN KEY (parent_session_id) REFERENCES ECCMID_2025(id) ON DELETE CASCADE
                )
                """)
                
                # Copy data from temporary table to permanent table
                cursor.execute("""
                INSERT INTO ECC_Session_Presentations (
                    parent_session_id, presentation_title, presentation_order, 
                    presenters, presenter_details
                )
                SELECT parent_session_id, presentation_title, presentation_order,
                       presenters, presenter_details
                FROM ECC_Presentations
                """)
                
                conn.commit()
                print(f"Successfully created and populated ECC_Session_Presentations table with {cursor.rowcount} records.")
                logging.info(f"Successfully created and populated presentations table with {cursor.rowcount} records.")
            except mysql.connector.Error as err:
                logging.error(f"Error creating presentations table: {err}")
                conn.rollback()
                print(f"Error creating presentations table: {err}")
        
        cursor.close()
        
    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")
        print(f"An error occurred during processing: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    process_all_records()
, presenter_text)
                        if country_match:
                            presenter_details['country'] = country_match.group(1).strip()
                        
                        # Add data_id if available
                        if 'data-id' in faculty_div.attrs:
                            presenter_details['data_id'] = faculty_div['data-id']
                        
                        presentation['presenter_details'].append(presenter_details)
                
                data['session_presentations'].append(presentation)
        
        return data
    
    except Exception as e:
        logging.error(f"Error extracting session data: {e}")
        return {}

def format_extracted_data(data):
    """Format the extracted data for SQL update"""
    # Format chairs list to string
    chairs_str = '; '.join(data.get('session_chairs', []))
    
    # Format presentations list to string
    presentations = []
    for p in data.get('session_presentations', []):
        title = p.get('title', '')
        presenters = '; '.join(p.get('presenters', []))
        presentations.append(f"{title} [{presenters}]")
    
    presentations_str = ' || '.join(presentations)
    
    # Create a formatted data dictionary for SQL update
    formatted_data = {
        'session_id': data.get('session_id'),
        'session_type': data.get('session_type'),
        'session_title': data.get('session_title'),
        'session_hall': data.get('session_hall'),
        'session_date': data.get('session_date'),
        'session_time_start': data.get('session_time_start'),
        'session_time_end': data.get('session_time_end'),
        'session_timezone': data.get('session_timezone'),
        'session_category': data.get('session_category'),
        'session_description': data.get('session_description'),
        'session_organized_by': data.get('session_organized_by'),
        'session_chairs': chairs_str,
        'session_presentations': presentations_str
    }
    
    return formatted_data

# This function is no longer needed as we're using a different approach with a temporary table
# Keeping it commented for reference
"""
def update_session_record(conn, record_id, data):
    Update a session record with extracted data
    try:
        cursor = conn.cursor()
        
        # Define the columns to update
        cols_to_update = [
            'sessionType', 'sessionTitle', 'sessionHall', 'sessionDate',
            'sessionTimeStart', 'sessionTimeEnd', 'sessionTimezone',
            'sessionCategory', 'sessionDescription', 'sessionOrganizedBy',
            'sessionChairs', 'sessionPresentations'
        ]
        
        # Map the formatted data to table columns
        update_values = {
            'sessionType': data.get('session_type'),
            'sessionTitle': data.get('session_title'),
            'sessionHall': data.get('session_hall'),
            'sessionDate': data.get('session_date'),
            'sessionTimeStart': data.get('session_time_start'),
            'sessionTimeEnd': data.get('session_time_end'),
            'sessionTimezone': data.get('session_timezone'),
            'sessionCategory': data.get('session_category'),
            'sessionDescription': data.get('session_description'),
            'sessionOrganizedBy': data.get('session_organized_by'),
            'sessionChairs': data.get('session_chairs'),
            'sessionPresentations': data.get('session_presentations')
        }
        
        # Build the SQL update query
        set_clause = ', '.join([f"{col} = %s" for col in cols_to_update])
        query = f"UPDATE ECCMID_2025 SET {set_clause} WHERE id = %s"
        
        # Create the parameters list in the correct order
        params = [update_values[col] for col in cols_to_update]
        params.append(record_id)
        
        # Execute the update
        cursor.execute(query, params)
        conn.commit()
        
        logging.info(f"Updated record ID {record_id} successfully")
        return True
    
    except mysql.connector.Error as err:
        logging.error(f"Error updating record: {err}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
"""

def process_all_records():
    """Process all records in the database"""
    conn = None
    try:
        conn = connect_to_database()
        cursor = conn.cursor(dictionary=True)
        
        # Create a temporary table to hold the extracted data
        try:
            cursor.execute("""
            CREATE TEMPORARY TABLE IF NOT EXISTS ECC_Extracted (
                id INT NOT NULL,
                session_id VARCHAR(25),
                session_type VARCHAR(255),
                session_title VARCHAR(255),
                session_hall VARCHAR(50),
                session_date VARCHAR(50),
                session_time_start VARCHAR(50),
                session_time_end VARCHAR(50),
                session_timezone VARCHAR(50),
                session_category VARCHAR(255),
                session_description TEXT,
                session_organized_by VARCHAR(255),
                session_chairs TEXT,
                session_presentations TEXT,
                PRIMARY KEY (id)
            )
            """)
            conn.commit()
            logging.info("Temporary table created successfully")
        except mysql.connector.Error as err:
            logging.error(f"Error creating temporary table: {err}")
            conn.rollback()
            return
        
        # Query to get all records
        cursor.execute("SELECT id, sessionId, sessionData FROM ECCMID_2025")
        records = cursor.fetchall()
        
        processed_count = 0
        error_count = 0
        
        for record in records:
            record_id = record['id']
            html_content = record['sessionData']
            
            if not html_content:
                logging.warning(f"Record ID {record_id}: Empty sessionData")
                continue
            
            # Extract and process the data
            extracted_data = extract_session_data(html_content)
            
            if not extracted_data or not extracted_data.get('session_id'):
                logging.warning(f"Record ID {record_id}: Could not extract complete data")
                error_count += 1
                continue
            
            # Verify the extracted session ID matches the recorded one (if available)
            if record['sessionId'] and extracted_data.get('session_id') and record['sessionId'] != f"session-id-{extracted_data.get('session_id')}":
                logging.warning(f"Record ID {record_id}: SessionID mismatch. DB: {record['sessionId']}, Extracted: session-id-{extracted_data.get('session_id')}")
            
            # Format the extracted data
            formatted_data = format_extracted_data(extracted_data)
            
            # Insert the formatted data into the temporary table
            try:
                insert_query = """
                INSERT INTO ECC_Extracted (
                    id, session_id, session_type, session_title, session_hall, 
                    session_date, session_time_start, session_time_end, session_timezone,
                    session_category, session_description, session_organized_by,
                    session_chairs, session_presentations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                insert_params = (
                    record_id, 
                    formatted_data.get('session_id'),
                    formatted_data.get('session_type'),
                    formatted_data.get('session_title'),
                    formatted_data.get('session_hall'),
                    formatted_data.get('session_date'),
                    formatted_data.get('session_time_start'),
                    formatted_data.get('session_time_end'),
                    formatted_data.get('session_timezone'),
                    formatted_data.get('session_category'),
                    formatted_data.get('session_description'),
                    formatted_data.get('session_organized_by'),
                    formatted_data.get('session_chairs'),
                    formatted_data.get('session_presentations')
                )
                cursor.execute(insert_query, insert_params)
                conn.commit()
                processed_count += 1
            except mysql.connector.Error as err:
                logging.error(f"Error inserting into temporary table for record {record_id}: {err}")
                conn.rollback()
                error_count += 1
        
        # Print summary of extraction results
        logging.info(f"Processing complete. Total records: {len(records)}, Processed: {processed_count}, Errors: {error_count}")
        
        # Optionally view the extracted data
        cursor.execute("SELECT * FROM ECC_Extracted LIMIT 5")
        sample_results = cursor.fetchall()
        logging.info(f"Sample of extracted data: {sample_results}")
        
        # Provide options to update the main table
        print("\nExtraction complete. Options:")
        print("1. Update the main ECCMID_2025 table with the extracted data")
        print("2. Export the extracted data to a CSV file")
        print("3. Exit without updating")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            # Update the main ECCMID_2025 table with the extracted data
            try:
                cursor.execute("""
                ALTER TABLE ECCMID_2025 
                ADD COLUMN IF NOT EXISTS sessionTitle VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionHall VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionDate VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimeStart VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimeEnd VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionTimezone VARCHAR(50),
                ADD COLUMN IF NOT EXISTS sessionCategory VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionDescription TEXT,
                ADD COLUMN IF NOT EXISTS sessionOrganizedBy VARCHAR(255),
                ADD COLUMN IF NOT EXISTS sessionChairs TEXT,
                ADD COLUMN IF NOT EXISTS sessionPresentations TEXT
                """)
                
                update_query = """
                UPDATE ECCMID_2025 e
                JOIN ECC_Extracted ex ON e.id = ex.id
                SET 
                    e.sessionType = ex.session_type,
                    e.sessionTitle = ex.session_title,
                    e.sessionHall = ex.session_hall,
                    e.sessionDate = ex.session_date,
                    e.sessionLocalStart = ex.session_time_start,
                    e.sessionLocalEnd = ex.session_time_end,
                    e.sessionTimezone = ex.session_timezone,
                    e.sessionCategory = ex.session_category,
                    e.sessionDescription = ex.session_description,
                    e.sessionOrganizedBy = ex.session_organized_by,
                    e.sessionChairs = ex.session_chairs,
                    e.sessionPresentations = ex.session_presentations
                """
                cursor.execute(update_query)
                conn.commit()
                print(f"Successfully updated {cursor.rowcount} records in the main ECCMID_2025 table.")
                logging.info(f"Successfully updated {cursor.rowcount} records in the main ECCMID_2025 table.")
            except mysql.connector.Error as err:
                logging.error(f"Error updating main table: {err}")
                conn.rollback()
                print(f"Error updating main table: {err}")
        
        elif choice == '2':
            # Export to CSV
            import csv
            from datetime import datetime
            
            filename = f"eccmid_extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            cursor.execute("SELECT * FROM ECC_Extracted")
            all_data = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                csv_writer.writerow(all_data[0].keys())
                # Write data
                for row in all_data:
                    csv_writer.writerow(row.values())
            
            print(f"Data exported to {filename}")
            logging.info(f"Data exported to {filename}")
        
        cursor.close()
        
    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")
        print(f"An error occurred during processing: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    process_all_records()