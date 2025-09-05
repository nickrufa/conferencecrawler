import mysql.connector
from bs4 import BeautifulSoup
import os
import sys
import pandas as pd
import tempfile

# Import the extraction functions
from eccmid_extraction import extract_session_data, format_extracted_data

def test_extraction_without_db():
    """Test the extraction function with the sample data files directly, without using a database"""
    # Create a dataframe to hold the results
    results_df = pd.DataFrame(columns=[
        'file_name', 'session_id', 'session_type', 'session_title', 'session_hall',
        'session_date', 'session_time_start', 'session_time_end', 'session_timezone',
        'session_category', 'session_description', 'session_organized_by',
        'session_chairs', 'session_presentations'
    ])
    
    try:
        # Read sample files
        for i in range(1, 5):
            file_name = f"paste{'-' + str(i) if i > 1 else ''}.txt"
            
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    html_content = file.read()
            except FileNotFoundError:
                print(f"File {file_name} not found!")
                continue
                
            print(f"\n--- Processing {file_name} ---")
            
            # Extract and format data
            extracted_data = extract_session_data(html_content)
            formatted_data = format_extracted_data(extracted_data)
            
            # Add to dataframe
            formatted_data['file_name'] = file_name
            results_df = pd.concat([results_df, pd.DataFrame([formatted_data])], ignore_index=True)
            
            # Print extracted information
            print(f"Session ID: {formatted_data.get('session_id')}")
            print(f"Session Type: {formatted_data.get('session_type')}")
            print(f"Session Title: {formatted_data.get('session_title')}")
            print(f"Session Hall: {formatted_data.get('session_hall')}")
            print(f"Session Date: {formatted_data.get('session_date')}")
            print(f"Session Time: {formatted_data.get('session_time_start')} - {formatted_data.get('session_time_end')} {formatted_data.get('session_timezone')}")
            print(f"Session Category: {formatted_data.get('session_category')}")
            
            print("\nSession Description:")
            print(formatted_data.get('session_description', 'N/A')[:150] + "..." if formatted_data.get('session_description') else 'N/A')
            
            print("\nOrganized By:")
            print(formatted_data.get('session_organized_by', 'N/A'))
            
            print("\nChairs:")
            print(formatted_data.get('session_chairs', 'N/A'))
            
            print("\nPresentations:")
            presentations = formatted_data.get('session_presentations', 'N/A')
            print(presentations[:150] + "..." if len(presentations) > 150 else presentations)
            
            print("\n" + "="*50)
        
        # Export results to a CSV file
        csv_file = "eccmid_extraction_results.csv"
        results_df.to_csv(csv_file, index=False)
        print(f"\nExtraction results saved to {csv_file}")
    
    except Exception as e:
        print(f"Error during testing: {e}")

def test_extraction():
    """Test the extraction function with the sample data"""
    try:
        # Read sample files
        for i in range(1, 5):
            file_name = f"paste{'-' + str(i) if i > 1 else ''}.txt"
            
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    html_content = file.read()
            except FileNotFoundError:
                print(f"File {file_name} not found!")
                continue
                
            print(f"\n--- Processing {file_name} ---")
            
            # Extract and format data
            extracted_data = extract_session_data(html_content)
            formatted_data = format_extracted_data(extracted_data)
            
            # Print extracted information
            print(f"Session ID: {formatted_data.get('session_id')}")
            print(f"Session Type: {formatted_data.get('session_type')}")
            print(f"Session Title: {formatted_data.get('session_title')}")
            print(f"Session Hall: {formatted_data.get('session_hall')}")
            print(f"Session Date: {formatted_data.get('session_date')}")
            print(f"Session Time: {formatted_data.get('session_time_start')} - {formatted_data.get('session_time_end')} {formatted_data.get('session_timezone')}")
            print(f"Session Category: {formatted_data.get('session_category')}")
            
            print("\nSession Description:")
            print(formatted_data.get('session_description', 'N/A')[:150] + "..." if formatted_data.get('session_description') else 'N/A')
            
            print("\nOrganized By:")
            print(formatted_data.get('session_organized_by', 'N/A'))
            
            print("\nChairs:")
            print(formatted_data.get('session_chairs', 'N/A'))
            
            print("\nPresentations:")
            presentations = formatted_data.get('session_presentations', 'N/A')
            print(presentations[:150] + "..." if len(presentations) > 150 else presentations)
            
            print("\n" + "="*50)
    
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    # Test the extraction functions without database
    test_extraction_without_db()