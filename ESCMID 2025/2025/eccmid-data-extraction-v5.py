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
    location = header.find('strong').text.strip() if header and header.find('strong') else ''
    date_time = header.get_text(strip=True).replace(location, '').split('|') if header else []
    date = date_time[1].strip() if len(date_time) > 1 else ''
    time_range = date_time[2].strip().split('CET')[0].strip() if len(date_time) > 2 else ''
    timezone = 'CET' if header and 'CET' in header.get_text() else ''
    session_type = soup.find('span', class_='session-details-cotype-name').text.strip() if soup.find('span', class_='session-details-cotype-name') else ''
    category = soup.find('h4', class_='modal-cat-name').text.strip() if soup.find('h4', class_='modal-cat-name') else ''
    title = soup.find('h3').text.strip() if soup.find('h3') else ''

    # Insert main session
    cursor.execute("""
        INSERT INTO ECCMID_2025_Sessions (sessionId, title, location, date, timeRange, timezone, sessionType, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (session_id, title, location, date, time_range, timezone, session_type, category))
    main_session_row_id = cursor.lastrowid

    # Extract chair(s) - handle multiple
    chair_div = soup.find('div', class_='modal-session-moderators')
    if chair_div:
        chairs = chair_div.find_all('div', class_='modal-session-faculties')
        if chairs:
            # For simplicity, store first chair in main row; additional chairs could go elsewhere if needed
            chair = chairs[0]
            chair_name = f"{chair.find('span', class_='fo-user__firstname-speaker').text} {chair.find('span', class_='fo-user__lastname-speaker').text}"
            chair_country = chair.find('span', class_='modal-session-moderator-country').text.replace(',', '').strip() if chair.find('span', class_='modal-session-moderator-country') else ''
            cursor.execute("""
                UPDATE ECCMID_2025_Sessions SET chairName = %s, chairCountry = %s WHERE id = %s
            """, (chair_name, chair_country, main_session_row_id))

    # Extract sub-sessions (presentations)
    interventions = soup.find_all('div', class_='modal-sessions-interventions-group')
    for intervention in interventions:
        sub_title_span = intervention.find('span', style='font-weight: bold')
        sub_title = sub_title_span.text.strip() if sub_title_span else 'Untitled Presentation'  # Fallback for missing span

        # Handle multiple presenters
        presenters = intervention.find_all('div', class_='modal-session-faculties')
        if presenters:
            # Store first presenter in the row; additional presenters could be logged or stored separately
            presenter = presenters[0]
            presenter_name = f"{presenter.find('span', class_='fo-user__firstname-speaker').text} {presenter.find('span', class_='fo-user__lastname-speaker').text}"
            presenter_country = presenter.text.split(',')[-1].strip() if ',' in presenter.text else ''
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