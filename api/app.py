#!/usr/bin/env python3
"""
Conference Crawler API
Flask application for managing conference assignments
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'conference_crawler.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# Table creation removed - database should already exist with your data

@app.route('/api/conferences/<conference_id>/users', methods=['GET'])
def get_conference_users(conference_id):
    """Get all users for a specific conference"""
    try:
        conn = get_db_connection()

        users = conn.execute('''
            SELECT
                id as user_id,
                (firstname || ' ' || lastname) as name,
                firstname,
                lastname,
                email,
                department,
                title,
                degree,
                external_id,
                external_system,
                active,
                created_at
            FROM conference_users
            WHERE conference_id = ? AND active = 1
            ORDER BY lastname, firstname
        ''', (conference_id,)).fetchall()

        conn.close()

        # Convert to list of dictionaries
        result = []
        for user in users:
            user_dict = {
                'user_id': user['user_id'],
                'name': user['name'],  # This is the concatenated firstname + lastname
                'firstname': user['firstname'],
                'lastname': user['lastname'],
                'email': user['email'],
                'department': user['department'],
                'title': user['title'],
                'degree': user['degree'],
                'external_id': user['external_id'],
                'external_system': user['external_system'],
                'conference_role': 'msd',  # Default role since not in table
                'active': bool(user['active']),
                'assigned_date': user['created_at'],  # Using created_at since no assigned_date
                'created_at': user['created_at']
            }
            result.append(user_dict)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@app.route('/api/conferences/<conference_id>/assignments', methods=['GET', 'POST'])
def handle_assignments(conference_id):
    """Get or save assignments for a conference"""
    try:
        conn = get_db_connection()

        if request.method == 'GET':
            # Get all assignments for this conference
            assignments_rows = conn.execute('''
                SELECT session_id, user_id
                FROM conference_assignments
                WHERE conference_id = ?
                ORDER BY session_id, user_id
            ''', (conference_id,)).fetchall()

            # Convert to frontend format: {sessionId: [userId1, userId2]}
            assignments = {}
            for row in assignments_rows:
                session_id = row['session_id']
                user_id = row['user_id']

                if session_id not in assignments:
                    assignments[session_id] = []
                assignments[session_id].append(user_id)

            conn.close()
            return jsonify({'assignments': assignments})

        elif request.method == 'POST':
            # Save assignments (bulk operation)
            data = request.get_json()

            if not data or 'assignments' not in data:
                return jsonify({'error': 'Bad Request', 'message': 'No assignments data provided'}), 400

            # Begin transaction
            conn.execute('BEGIN TRANSACTION')

            try:
                # Clear existing assignments for this conference
                conn.execute('''
                    DELETE FROM conference_assignments
                    WHERE conference_id = ?
                ''', (conference_id,))

                # Insert new assignments
                for assignment in data['assignments']:
                    # Validate that user exists in conference_users
                    user_check = conn.execute('''
                        SELECT user_id FROM conference_users
                        WHERE conference_id = ? AND user_id = ? AND active = 1
                    ''', (conference_id, assignment['user_id'])).fetchone()

                    if user_check:
                        conn.execute('''
                            INSERT INTO conference_assignments (
                                conference_id, session_id, user_id, assigned_date, assigned_by
                            ) VALUES (?, ?, ?, ?, ?)
                        ''', (
                            conference_id,
                            assignment['session_id'],
                            assignment['user_id'],
                            datetime.now().isoformat(),
                            'system'
                        ))

                conn.execute('COMMIT')
                conn.close()

                return jsonify({
                    'success': True,
                    'message': 'Assignments saved successfully',
                    'count': len(data['assignments'])
                })

            except Exception as e:
                conn.execute('ROLLBACK')
                conn.close()
                raise e

    except Exception as e:
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/conferences/<conference_id>/assignments/bulk', methods=['POST'])
def bulk_assignments(conference_id):
    """Bulk assignment operations (alias for POST to assignments endpoint)"""
    return handle_assignments(conference_id)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Run the Flask app (database should already be initialized)
    app.run(host='0.0.0.0', port=5001, debug=True)