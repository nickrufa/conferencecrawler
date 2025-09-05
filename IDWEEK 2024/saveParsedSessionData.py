import requests
import re
from bs4 import BeautifulSoup
import mysql.connector

base_url = "http://local.dev.meetings.com/index.cfm?page=sessions&thisPageAction=view&thisSessionType=ePoster%20Flash%20Session"

urls = [f"{base_url}&thisID={i}" for i in range(1, 433)]

for url in urls:

    # Connect to MySQL database
    # mydb = mysql.connector.connect(
    # host="database-1.cluster-cheaomfkb77i.us-east-1.rds.amazonaws.com",
    # user="awsrdsadmin",
    # password="Z1Wz5!u44fiO99$yJtXvhBLF1$Qp!",
    # database="occ3"
    # )

    # Create a cursor object
    # mycursor = mydb.cursor()

    # Loop through the URLs
    # Open a file for writing
    with open('eccmid_cats.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')

            # ... (existing code for data extraction)
            session_header_div = soup.find('div', class_='session-header')

            # Remove leading/trailing whitespace from the entire div
            session_header_text = session_header_div.get_text().strip()
            #print(f"Session Header (with whitespace removed): {session_header_text}")

            # Access individual elements
            date_time = session_header_div.contents[0].strip()
            date_time_split = re.sub(r'[,\s+]+', 'π', date_time)

            # Split the string into Day/Month and Start/End Time
            date_month, start_end_time = date_time_split.split('π', 1)
            start_end_time = start_end_time.replace('π', '')

            # print("day_month:", date_month)
            # print("start_end_time:", start_end_time)

            timezone_span = session_header_div.find('span', class_='session-abbr-timezone')
            timezone = timezone_span.text.strip() if timezone_span else ''

            # Use regex to extract session type and color
            session_type_pattern = r'<span style="color:(#\w+)">\s*<i.*?></i>\s*(.*?)</span>'
            session_type_match = re.search(session_type_pattern, str(session_header_div))

            if session_type_match:
                session_color = session_type_match.group(1)
                session_type = session_type_match.group(2)
            else:
                session_color = ''
                session_type = ''

            location_span = session_header_div.find('span', class_='float-right')
            location = location_span.text.strip() if location_span else ''

            #print(f"Date and Time: {date_time}")
            # print(f"timezone: {timezone}")
            # print(f"session_type: {session_type}")
            # print(f"session_color: {session_color}")
            # print(f"location: {location}")

            session_cat = soup.find('div', class_='title-cat').h4.text.strip()
            print(f"session_category: {session_cat}")

            session_name = soup.find('div', class_='session-name').h3.text.strip()
            # print(f"session_name: {session_name}")

            # Create a formatted string to store in the database
            # data_to_store = f"day_month: {date_month}π\n"
            # data_to_store += f"start_end_time: {start_end_time}π\n"
            # data_to_store += f"timezone: {timezone}π\n"
            # data_to_store += f"session_type: {session_type}π\n"
            # data_to_store += f"session_color: {session_color}π\n"
            # data_to_store += f"location: {location}π\n"
            data_to_store = f"{session_cat}"
            # data_to_store += f"session_name: {session_name}π\n"

            def extract_country(full_text, first_name, last_name):
                # Remove first and last name from the text to isolate the country part
                country_part = full_text.replace(first_name, '').replace(last_name, '').strip()
                
                # Split the remaining text by commas to handle potential multi-part country names
                parts = [part.strip() for part in country_part.split(',')]
                
                # If there are multiple parts, join them with a comma (preserving multi-word countries)
                if len(parts) > 1:
                    country = ', '.join(parts)
                # If there's only one part, return it directly (for single-word countries)
                elif len(parts) == 1:
                    country = parts[0]
                else:
                    country = ''

                return country

            # Assuming 'soup' is your BeautifulSoup object from the HTML content
            faculty_sections = soup.find_all('div', class_='sessions-interventions-group')

            for faculty_section in faculty_sections:
                faculty_member = faculty_section.find('div', class_='session-faculties')
                if faculty_member:
                    full_text = faculty_member.get_text(separator=" ", strip=True)
                    first_name_el = faculty_member.find('span', class_='fo-user__firstname-speaker')
                    last_name_el = faculty_member.find('span', class_='fo-user__lastname-speaker')

                    first_name = first_name_el.text.strip() if first_name_el else ''
                    last_name = last_name_el.text.strip() if last_name_el else ''

                    country = extract_country(full_text, first_name, last_name)
                    country = country.replace(",", "", 1).strip()

                    pattern = r'data-id="(\d+)"'
                    match = re.search(pattern, str(faculty_member))

                    data_id = match.group(1) if match else ""

                    # data_to_store = f"faculty: {data_id} '{first_name}' '{last_name}' '{country}'π\n"

            # Extract the thisID value from the URL
            thisID = int(url.split('&thisID=')[1].split('&')[0])

            # # Update the sessionData column for the corresponding thisID
            # sql = "UPDATE ECCMID_2024 SET category = %s WHERE id = %s"
            # values = (data_to_store, thisID)
            # mycursor.execute(sql, values)
            # mydb.commit()  # Commit the changes to the database
            data_to_store += f"id: {thisID}\n"
            
            # print(data_to_store)
            # print("--------------------")
            output_line = f": {data_to_store}\n"
            file.write(output_line)  # Write the output to the file

        # Close the cursor and database connection
        # mycursor.close()
        # mydb.close()