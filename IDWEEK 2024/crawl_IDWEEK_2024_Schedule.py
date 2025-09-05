import requests
from bs4 import BeautifulSoup
import re

def extract_schedule_info(html_file, output_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    items = soup.find_all('li', class_='list-group-item list-row loadbyurl')

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for item in items:
            # Extract prestime
            prestime = item.find('div', class_='prestime').text.strip()
            time_parts = re.findall(r'\d+:\d+ [AP]M', prestime)
            start_time = time_parts[0] if time_parts else "N/A"
            end_time = time_parts[1] if len(time_parts) > 1 else "N/A"
            time_zone = "US PT"  # Fixed time zone as per your instruction

            # Extract meeting number and title
            number_title = item.find('div', class_='number-title')
            meeting_number = number_title.text.split('-')[0].strip() if number_title else "N/A"
            meeting_title = ' - '.join(number_title.text.split('-')[1:]).strip() if number_title else "N/A"

            # Extract categories
            categories = item.find('div', class_='categories')
            category_list = [cat.text.strip() for cat in categories.find_all('span', class_='category')] if categories else []
            categories_str = ', '.join(category_list)

            # Extract location
            location = item.find('div', class_='location')
            location_str = f"Location: {location.text.strip()}" if location else "Location: N/A"

            # Extract PresentationID
            presid = item.get('data-presid', 'N/A')

            # Extract Data URL
            data_url = item.get('data-url', 'N/A')

            # Write extracted information to file
            outfile.write(f"Start Time: {start_time}\n")
            outfile.write(f"End Time: {end_time}\n")
            outfile.write(f"Time Zone: {time_zone}\n")
            outfile.write(f"Meeting Number: {meeting_number}\n")
            outfile.write(f"Meeting Title: {meeting_title}\n")
            outfile.write(f"{location_str}\n")
            outfile.write(f"Categories: {categories_str}\n")
            outfile.write(f"PresentationID: {presid}\n")
            outfile.write(f"Data URL: {data_url}\n")
            outfile.write("-" * 50 + "\n")

# Usage
extract_schedule_info('IDWEEK/schedule.html', 'idweek_2024_sessions2.txt')
print("Extraction complete. Results saved to idweek_2024_sessions2.txt")
