import mysql.connector
from bs4 import BeautifulSoup

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="5melly0nion",
    database="medinfo"
)
cursor = db.cursor()

# Fetch session data from ECCMID_2025
cursor.execute("SELECT sessionId, sessionData FROM ECCMID_2025")
sessions = cursor.fetchall()

for session_id, session_html in sessions:
    soup = BeautifulSoup(session_html, 'html.parser')

    # Extract main session details
    header = soup.find('div', class_='modal-session-header-bg-type')
    location = header.find('strong').text.strip() if header.find('strong') else ''
    date_time = header.get_text(strip=True).replace(location, '').split('|')
    date = date_time[1].strip() if len(date_time) > 1 else ''
    time_range = date_time[2].strip().split('CET')[0].strip() if len(date_time) > 2 else ''
    timezone = 'CET' if 'CET' in header.get_text() else ''
    session_type = soup.find('span', class_='session-details-cotype-name').text.strip()
    category = soup.find('h4', class_='modal-cat-name').text.strip()
    title = soup.find('h3').text.strip()

    # Insert main session
    cursor.execute("""
        INSERT INTO ECCMID_2025_Sessions (sessionId, title, location, date, timeRange, timezone, sessionType, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (session_id, title, location, date, time_range, timezone, session_type, category))
    main_session_row_id = cursor.lastrowid

    # Extract chair(s)
    chair_div = soup.find('div', class_='modal-session-moderators')
    if chair_div:
        chair = chair_div.find('div', class_='modal-session-faculties')
        if chair:
            chair_name = f"{chair.find('span', class_='fo-user__firstname-speaker').text} {chair.find('span', class_='fo-user__lastname-speaker').text}"
            chair_country = chair.find('span', class_='modal-session-moderator-country').text.replace(',', '').strip()
            cursor.execute("""
                UPDATE ECCMID_2025_Sessions SET chairName = %s, chairCountry = %s WHERE id = %s
            """, (chair_name, chair_country, main_session_row_id))

    # Extract sub-sessions (presentations)
    interventions = soup.find_all('div', class_='modal-sessions-interventions-group')
    for intervention in interventions:
        sub_title = intervention.find('span', style='font-weight: bold').text.strip()
        presenter = intervention.find('div', class_='modal-session-faculties')
        if presenter:
            presenter_name = f"{presenter.find('span', class_='fo-user__firstname-speaker').text} {presenter.find('span', class_='fo-user__lastname-speaker').text}"
            presenter_country = presenter.text.split(',')[-1].strip()
        else:
            presenter_name, presenter_country = None, None

        # Insert sub-session
        cursor.execute("""
            INSERT INTO ECCMID_2025_Sessions (sessionId, parentSessionId, title, presenterName, presenterCountry)
            VALUES (%s, %s, %s, %s, %s)
        """, (session_id, main_session_row_id, sub_title, presenter_name, presenter_country))

# Commit changes and close connection
db.commit()
cursor.close()
db.close()

print("Session and sub-session data extracted and stored successfully.")