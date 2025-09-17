#!/usr/bin/env python3
"""
Combine IDWeek 2025 sessions and posters into a single JSON file
"""

import json
import sys
from pathlib import Path

def combine_data():
    """Combine sessions and posters data"""

    # Load sessions data
    sessions_file = Path('idweek2025_sessions.json')
    if not sessions_file.exists():
        print(f"Error: {sessions_file} not found")
        sys.exit(1)

    with open(sessions_file, 'r', encoding='utf-8') as f:
        sessions = json.load(f)

    # Load posters data
    posters_file = Path('original_data/idweek2025_posters.json')
    if not posters_file.exists():
        print(f"Error: {posters_file} not found")
        sys.exit(1)

    with open(posters_file, 'r', encoding='utf-8') as f:
        posters = json.load(f)

    print(f"Loaded {len(sessions)} sessions and {len(posters)} posters")

    # Add data_type field to distinguish sessions from posters
    for session in sessions:
        session['data_type'] = 'session'
        # Normalize session_info.type for sessions
        if 'session_info' in session and session['session_info'].get('type'):
            session['session_info']['type'] = session['session_info']['type']
        else:
            session['session_info'] = session.get('session_info', {})
            session['session_info']['type'] = 'Session'

    for poster in posters:
        poster['data_type'] = 'poster'
        # Set poster type consistently
        if 'session_info' not in poster:
            poster['session_info'] = {}
        poster['session_info']['type'] = 'Poster'

    # Combine both arrays
    combined_data = sessions + posters

    print(f"Combined total: {len(combined_data)} items")

    # Write combined data
    output_file = Path('idweek2025_combined.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)

    print(f"Combined data written to {output_file}")

    # Print summary statistics
    session_types = {}
    for item in combined_data:
        item_type = item.get('session_info', {}).get('type', 'Unknown')
        session_types[item_type] = session_types.get(item_type, 0) + 1

    print("\nData type breakdown:")
    for session_type, count in sorted(session_types.items()):
        print(f"  {session_type}: {count}")

if __name__ == '__main__':
    combine_data()