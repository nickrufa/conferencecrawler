#!/usr/bin/env python3
"""
Populate database with initial conference and user data
"""

import sqlite3
import json
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'conference_crawler.db')

def init_database():
    """Initialize database with tables"""
    conn = sqlite3.connect(DATABASE_PATH)

    # Create conferences table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conferences (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            department TEXT,
            title TEXT,
            degree TEXT,
            territory TEXT,
            phone TEXT,
            external_id INTEGER,
            external_system TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create conference_users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conference_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conference_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'attendee',
            active BOOLEAN DEFAULT 1,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conference_id) REFERENCES conferences(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(conference_id, user_id)
        )
    ''')

    # Create conference_assignments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conference_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conference_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_by TEXT DEFAULT 'system',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conference_id) REFERENCES conferences(id) ON DELETE CASCADE,
            UNIQUE(conference_id, session_id, user_id)
        )
    ''')

    conn.commit()
    conn.close()

def populate_database():
    """Populate database with IDWeek 2025 conference and MSD data"""
    conn = sqlite3.connect(DATABASE_PATH)

    # Insert IDWeek 2025 conference
    conn.execute('''
        INSERT OR REPLACE INTO conferences (id, title, location, start_date, end_date, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        'idweek2025',
        'IDWeek 2025',
        'Los Angeles, CA',
        '2025-10-18',
        '2025-10-22',
        'Infectious Diseases Week 2025',
        'active'
    ))

    # MSD data (sorted alphabetically by last name, no degree field)
    msds = [
        {
            "id": "msd_2",
            "melintaId": 168,
            "name": "Saagar Akundi",
            "role": "Medical Science Director",
            "email": "sakundi@melinta.com",
            "department": "Medical Affairs",
            "territory": "South Central",
            "phone": "(512) 507-7816"
        },
        {
            "id": "msd_4",
            "melintaId": 142,
            "name": "Christina Andrzejewski",
            "role": "Medical Science Director",
            "email": "candrzejewski@melinta.com",
            "department": "Medical Affairs",
            "territory": "Atlantic Capital",
            "phone": "(908) 968-1300"
        },
        {
            "id": "msd_1",
            "melintaId": 172,
            "name": "Sandy Estrada",
            "role": "Senior Medical Science Director",
            "email": "sestrada@melinta.com",
            "department": "Medical Affairs",
            "territory": "Multiple Territories",
            "phone": "(239) 233-9380"
        },
        {
            "id": "msd_6",
            "melintaId": 156,
            "name": "Marianna Fedorenko",
            "role": "Medical Science Director",
            "email": "mfedorenko@melinta.com",
            "department": "Medical Affairs",
            "territory": "NYC Metro, NJ",
            "phone": "(201) 394-3552"
        },
        {
            "id": "msd_5",
            "melintaId": 146,
            "name": "Erica Fernandez",
            "role": "Medical Science Director",
            "email": "efernandez@melinta.com",
            "department": "Medical Affairs",
            "territory": "Midwest, North Central Ozarks",
            "phone": "(312) 219-3032"
        },
        {
            "id": "msd_8",
            "melintaId": 166,
            "name": "Ronak Gandhi",
            "role": "Medical Science Director",
            "email": "rgandhi@melinta.com",
            "department": "Medical Affairs",
            "territory": "New England & Upstate NY",
            "phone": "(781) 799-4372"
        },
        {
            "id": "msd_9",
            "melintaId": 210,
            "name": "Sarah Brooks Minor",
            "role": "Medical Science Director",
            "email": "sminor@melinta.com",
            "department": "Medical Affairs",
            "territory": "South Sunbelt",
            "phone": "(407) 922-1882"
        },
        {
            "id": "msd_7",
            "melintaId": 157,
            "name": "Michael North",
            "role": "Medical Science Director",
            "email": "mnorth@melinta.com",
            "department": "Medical Affairs",
            "territory": "West",
            "phone": "(303) 913-8961"
        },
        {
            "id": "test_8",
            "melintaId": 8,
            "name": "Nancy Robasco",
            "role": "Tester",
            "email": "nancy@cmeunited.com",
            "department": "Testing",
            "territory": "Test Territory",
            "phone": None
        },
        {
            "id": "test_163",
            "melintaId": 163,
            "name": "Nick Rufa",
            "role": "Tester",
            "email": "nrufa@melinta.com",
            "department": "Testing",
            "territory": "Test Territory",
            "phone": None
        },
        {
            "id": "msd_3",
            "melintaId": 141,
            "name": "Besu Teshome",
            "role": "Medical Science Director",
            "email": "bteshome@melinta.com",
            "department": "Medical Affairs",
            "territory": "South Central Ozarks",
            "phone": "(512) 228-1208"
        }
    ]

    # Insert users
    for msd in msds:
        conn.execute('''
            INSERT OR REPLACE INTO users (
                id, name, email, department, title, territory, phone, external_id, external_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            msd["id"],
            msd["name"],
            msd["email"],
            msd["department"],
            msd["role"],
            msd["territory"],
            msd.get("phone"),
            msd["melintaId"],
            "melinta"
        ))

        # Assign users to IDWeek 2025 conference
        conference_role = "msd" if "msd_" in msd["id"] else ("admin" if msd["id"] == "test_8" else "tester")

        conn.execute('''
            INSERT OR REPLACE INTO conference_users (conference_id, user_id, role, active)
            VALUES (?, ?, ?, ?)
        ''', ('idweek2025', msd["id"], conference_role, 1))

    conn.commit()
    conn.close()
    print(f"✅ Database populated with {len(msds)} users for IDWeek 2025")

if __name__ == '__main__':
    init_database()
    populate_database()