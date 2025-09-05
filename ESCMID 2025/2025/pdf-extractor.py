import tabula
import pandas as pd
import os
import re
import csv

def clean_text(text):
    """Clean text to avoid illegal characters"""
    if not isinstance(text, str):
        return ""
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    return text.strip()

def process_pdf_with_tabula(pdf_file, output_csv="tabula_output.csv"):
    """
    Use Tabula to extract tables from the PDF directly
    """
    print(f"Processing PDF {pdf_file} with Tabula...")
    
    try:
        # Extract all tables from the PDF
        # Use lattice=True for tables with visible borders
        # Use stream=True for tables without clear borders
        tables = tabula.read_pdf(
            pdf_file, 
            pages='all', 
            multiple_tables=True,
            stream=True,  # Use stream mode for non-bordered tables
            guess=True,   # Let Tabula guess table areas
            area="all",   # Extract from entire page
            silent=True   # Reduce Java output
        )
        
        print(f"Extracted {len(tables)} tables from PDF")
        
        # If no tables were found, try different parameters
        if not tables:
            print("No tables found with stream mode, trying lattice mode...")
            tables = tabula.read_pdf(
                pdf_file, 
                pages='all', 
                multiple_tables=True,
                lattice=True,  # Use lattice mode for bordered tables
                guess=True,
                area="all",
                silent=True
            )
            print(f"Extracted {len(tables)} tables with lattice mode")
        
        # Process extracted tables
        all_rows = []
        
        for i, table in enumerate(tables):
            # Clean the table data
            for col in table.columns:
                if pd.api.types.is_string_dtype(table[col]):
                    table[col] = table[col].apply(lambda x: clean_text(x) if isinstance(x, str) else x)
            
            print(f"Table {i+1} has {len(table)} rows and {len(table.columns)} columns")
            
            # Try to identify if this is a session or presentation table
            # by looking at column names and data patterns
            
            # Add a source column to track which table each row came from
            table['source_table'] = f"Table_{i+1}"
            
            # Add each row to our collection
            for _, row in table.iterrows():
                all_rows.append(row.to_dict())
        
        # Convert to a single DataFrame
        if all_rows:
            combined_df = pd.DataFrame(all_rows)
            combined_df.to_csv(output_csv, index=False)
            print(f"Combined data saved to {output_csv}")
            return output_csv
        else:
            print("No data extracted from tables")
            return None
            
    except Exception as e:
        print(f"Error during Tabula processing: {str(e)}")
        return None

def extract_session_info(pdf_file, output_csv="session_info.csv"):
    """
    Specialized extraction for conference session information
    """
    try:
        # Use Tabula with specific parameters for the ESCMID format
        # We'll focus on extracting the session headers
        tables = tabula.read_pdf(
            pdf_file, 
            pages='all', 
            multiple_tables=True,
            stream=True,
            guess=False,  # Don't guess - we'll specify areas
            columns=[50, 100, 200, 300, 400],  # Specify column separations
            area=(50, 0, 300, 595),  # Top area where session headers appear
            silent=True
        )
        
        # Process the tables to extract session information
        sessions = []
        
        for table in tables:
            # Try to identify session headers
            for _, row in table.iterrows():
                row_str = ' '.join([str(val) for val in row.values if not pd.isna(val)])
                
                # Look for session pattern like "EW001 08:30 - 10:30 Hall 2"
                session_match = re.search(r'((?:EW|OS|ME|SP|SY|KN|FO|LB|EF)\d+)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\s+Hall\s+(\w+)', row_str)
                
                if session_match:
                    session_id = session_match.group(1)
                    start_time = session_match.group(2)
                    end_time = session_match.group(3)
                    hall = session_match.group(4)
                    
                    # Add to our sessions list
                    sessions.append({
                        'Session ID': clean_text(session_id),
                        'Start Time': clean_text(start_time),
                        'End Time': clean_text(end_time),
                        'Hall': clean_text(hall),
                        'Session Type': '',  # Will try to extract this
                        'Session Title': '',  # Will try to extract this
                        'Chairs': ''  # Will try to extract this
                    })
        
        # Save the sessions data
        if sessions:
            sessions_df = pd.DataFrame(sessions)
            sessions_df.to_csv(output_csv, index=False)
            print(f"Extracted {len(sessions)} sessions to {output_csv}")
            return output_csv
        else:
            print("No session information extracted")
            return None
            
    except Exception as e:
        print(f"Error extracting session information: {str(e)}")
        return None

def extract_presentations(pdf_file, output_csv="presentations.csv"):
    """
    Specialized extraction for presentation information
    """
    try:
        # Use different Tabula settings to target presentation areas
        tables = tabula.read_pdf(
            pdf_file, 
            pages='all', 
            multiple_tables=True,
            stream=True,
            guess=True,
            area=(300, 0, 750, 595),  # Lower part of the page where presentations appear
            silent=True
        )
        
        presentations = []
        
        for table in tables:
            # Look for presentation patterns
            for _, row in table.iterrows():
                row_str = ' '.join([str(val) for val in row.values if not pd.isna(val)])
                
                # Look for patterns like "W0001 08:30 Title..."
                pres_match = re.search(r'([WOMEFSL]\d{4})\s+(\d{2}:\d{2})\s+(.*)', row_str)
                
                if pres_match:
                    pres_id = pres_match.group(1)
                    pres_time = pres_match.group(2)
                    pres_content = pres_match.group(3)
                    
                    # Try to parse the content for title, speaker, location
                    title = pres_content
                    speaker = ""
                    location = ""
                    
                    location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\(([^)]+)\)$', pres_content)
                    if location_match:
                        speaker = location_match.group(1).strip()
                        location = location_match.group(2).strip()
                        title = pres_content[:pres_content.find(speaker)].strip()
                    
                    presentations.append({
                        'Session ID': '',  # We'll need to match this separately
                        'Presentation ID': clean_text(pres_id),
                        'Time': clean_text(pres_time),
                        'Title': clean_text(title),
                        'Speaker': clean_text(speaker),
                        'Location': clean_text(location)
                    })
        
        # Save the presentations data
        if presentations:
            presentations_df = pd.DataFrame(presentations)
            presentations_df.to_csv(output_csv, index=False)
            print(f"Extracted {len(presentations)} presentations to {output_csv}")
            return output_csv
        else:
            print("No presentation information extracted")
            return None
            
    except Exception as e:
        print(f"Error extracting presentation information: {str(e)}")
        return None

def pdf_to_csv_tabula(pdf_file):
    """
    Process PDF using Tabula with multiple approaches
    """
    print("\nAttempting to extract data from PDF using Tabula...")
    
    # Create output filenames
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_output = os.path.join(base_dir, "tabula_raw_output.csv")
    sessions_output = os.path.join(base_dir, "tabula_sessions.csv")
    presentations_output = os.path.join(base_dir, "tabula_presentations.csv")
    
    # Try general extraction first
    general_result = process_pdf_with_tabula(pdf_file, raw_output)
    
    # Try specialized extractions
    sessions_result = extract_session_info(pdf_file, sessions_output)
    presentations_result = extract_presentations(pdf_file, presentations_output)
    
    print("\nTabula extraction summary:")
    print(f"- Raw data extraction: {'Success' if general_result else 'Failed'}")
    print(f"- Sessions extraction: {'Success' if sessions_result else 'Failed'}")
    print(f"- Presentations extraction: {'Success' if presentations_result else 'Failed'}")
    
    return general_result, sessions_result, presentations_result

if __name__ == "__main__":
    print("Tabula Direct PDF Processing Script")
    print("----------------------------------")
    print("This script uses Tabula-py to extract tabular data directly from PDFs")
    print("Requirements: Java must be installed and accessible")
    
    pdf_file = input("Enter path to PDF file: ")
    
    if os.path.exists(pdf_file):
        pdf_to_csv_tabula(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found")