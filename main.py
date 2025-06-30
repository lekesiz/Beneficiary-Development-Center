"""
Hybrid Flask app for Google App Engine - serves frontend and provides real backend structure
"""

import os
import logging
import json
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import sqlite3
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the absolute path of the frontend dist directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

# Use /tmp directory for SQLite on App Engine (writable)
# In production, this should be Cloud SQL
DB_PATH = '/tmp/bdc.db'

logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Dist directory: {DIST_DIR}")
logger.info(f"Dist directory exists: {os.path.exists(DIST_DIR)}")

app = Flask(__name__)
CORS(app)

# Global database connection for in-memory database
db_conn = None

# Initialize database
def init_db():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  name TEXT NOT NULL,
                  role TEXT NOT NULL,
                  tenant_id TEXT DEFAULT 'tenant-1',
                  is_active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create beneficiaries table
    c.execute('''CREATE TABLE IF NOT EXISTS beneficiaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  first_name TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  phone TEXT,
                  status TEXT DEFAULT 'active',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create programs table  
    c.execute('''CREATE TABLE IF NOT EXISTS programs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  status TEXT DEFAULT 'active',
                  start_date DATE,
                  end_date DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create courses table
    c.execute('''CREATE TABLE IF NOT EXISTS courses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  duration_hours INTEGER,
                  status TEXT DEFAULT 'active',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    
    # Create default users if not exist
    import hashlib
    
    # Super admin
    c.execute("SELECT id FROM users WHERE email = ?", ('superadmin@bdc.com',))
    if not c.fetchone():
        password_hash = hashlib.sha256('SuperAdmin2024!'.encode()).hexdigest()
        c.execute("""INSERT INTO users (email, password, name, role, tenant_id, is_active)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ('superadmin@bdc.com', password_hash, 'Super Admin', 'super_admin', 'tenant-1', 1))
        logger.info("Super admin user created: superadmin@bdc.com / SuperAdmin2024!")
    
    # Regular admin (for backward compatibility)
    c.execute("SELECT id FROM users WHERE email = ?", ('admin@example.com',))
    if not c.fetchone():
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("""INSERT INTO users (email, password, name, role, tenant_id, is_active)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ('admin@example.com', password_hash, 'Admin User', 'admin', 'tenant-1', 1))
        logger.info("Admin user created: admin@example.com / admin123")
    
    # Regular user
    c.execute("SELECT id FROM users WHERE email = ?", ('user@example.com',))
    if not c.fetchone():
        password_hash = hashlib.sha256('user123'.encode()).hexdigest()
        c.execute("""INSERT INTO users (email, password, name, role, tenant_id, is_active)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ('user@example.com', password_hash, 'Test User', 'user', 'tenant-1', 1))
        logger.info("Test user created: user@example.com / user123")
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Mock JWT secret
JWT_SECRET = 'mock-jwt-secret-key-2024'

# Mock user data
MOCK_USERS = {
    'admin@example.com': {
        'password': 'admin123',
        'id': '1',
        'name': 'Admin User',
        'role': 'admin',
        'tenant_id': 'tenant-1'
    },
    'user@example.com': {
        'password': 'user123',
        'id': '2',
        'name': 'Test User',
        'role': 'user',
        'tenant_id': 'tenant-1'
    }
}

# API Routes
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'BDC Platform API',
        'version': '1.0.0'
    }), 200

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Real login endpoint with database"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Get user from database
        c.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
        user_row = c.fetchone()
        
        if not user_row:
            conn.close()
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user_row['password'] != password_hash:
            conn.close()
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate tokens
        access_payload = {
            'user_id': str(user_row['id']),
            'email': email,
            'role': user_row['role'],
            'tenant_id': user_row['tenant_id'],
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        refresh_payload = {
            'user_id': str(user_row['id']),
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm='HS256')
        
        # Prepare user response
        permissions = ['view_all', 'edit_all', 'delete_all', 'manage_users'] if user_row['role'] in ['admin', 'super_admin'] else ['view_own', 'edit_own']
        
        conn.close()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user_row['id']),
                'email': email,
                'name': user_row['name'],
                'role': user_row['role'],
                'roles': [{'name': user_row['role'], 'id': '1'}],
                'tenant_id': user_row['tenant_id'],
                'is_active': True,
                'permissions': permissions
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@app.route('/api/v1/auth/logout', methods=['POST'])
def logout():
    """Mock logout endpoint"""
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/v1/auth/refresh', methods=['POST'])
def refresh():
    """Mock token refresh endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'No token provided'}), 401
        
        # Generate new access token
        access_payload = {
            'user_id': '1',
            'email': 'admin@example.com',
            'role': 'admin',
            'tenant_id': 'tenant-1',
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Token refresh failed'}), 500

@app.route('/api/v1/auth/me', methods=['GET'])
def get_current_user():
    """Mock get current user endpoint"""
    return jsonify({
        'user': {
            'id': '1',
            'email': 'admin@example.com',
            'name': 'Admin User',
            'role': 'admin',
            'roles': [{'name': 'admin', 'id': '1'}],
            'tenant_id': 'tenant-1',
            'is_active': True,
            'permissions': ['view_all', 'edit_all', 'delete_all']
        }
    }), 200

# Beneficiaries endpoints
@app.route('/api/v1/beneficiaries', methods=['GET'])
def get_beneficiaries():
    """Get all beneficiaries"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM beneficiaries WHERE status = 'active' ORDER BY created_at DESC")
        rows = c.fetchall()
        
        beneficiaries = []
        for row in rows:
            beneficiaries.append({
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'phone': row['phone'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        return jsonify({'beneficiaries': beneficiaries, 'total': len(beneficiaries)}), 200
        
    except Exception as e:
        logger.error(f"Error getting beneficiaries: {str(e)}")
        return jsonify({'message': 'Error fetching beneficiaries'}), 500

@app.route('/api/v1/beneficiaries', methods=['POST'])
def create_beneficiary():
    """Create a new beneficiary"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('first_name') or not data.get('last_name') or not data.get('email'):
            return jsonify({'message': 'First name, last name, and email are required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if email already exists
        c.execute("SELECT id FROM beneficiaries WHERE email = ?", (data['email'],))
        if c.fetchone():
            conn.close()
            return jsonify({'message': 'Email already exists'}), 409
        
        # Insert new beneficiary
        c.execute("""INSERT INTO beneficiaries (first_name, last_name, email, phone, status)
                     VALUES (?, ?, ?, ?, ?)""",
                  (data['first_name'], data['last_name'], data['email'], 
                   data.get('phone', ''), data.get('status', 'active')))
        
        beneficiary_id = c.lastrowid
        conn.commit()
        
        # Get the created beneficiary
        c.execute("SELECT * FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        conn.row_factory = sqlite3.Row
        row = c.fetchone()
        
        beneficiary = {
            'id': row['id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'phone': row['phone'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        return jsonify(beneficiary), 201
        
    except Exception as e:
        logger.error(f"Error creating beneficiary: {str(e)}")
        return jsonify({'message': 'Error creating beneficiary'}), 500

@app.route('/api/v1/beneficiaries/<int:beneficiary_id>', methods=['GET'])
def get_beneficiary(beneficiary_id):
    """Get a single beneficiary"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'message': 'Beneficiary not found'}), 404
        
        beneficiary = {
            'id': row['id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'phone': row['phone'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        return jsonify(beneficiary), 200
        
    except Exception as e:
        logger.error(f"Error getting beneficiary: {str(e)}")
        return jsonify({'message': 'Error fetching beneficiary'}), 500

@app.route('/api/v1/beneficiaries/<int:beneficiary_id>', methods=['PUT'])
def update_beneficiary(beneficiary_id):
    """Update a beneficiary"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if beneficiary exists
        c.execute("SELECT id FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'message': 'Beneficiary not found'}), 404
        
        # Update beneficiary
        updates = []
        params = []
        
        if 'first_name' in data:
            updates.append("first_name = ?")
            params.append(data['first_name'])
        if 'last_name' in data:
            updates.append("last_name = ?")
            params.append(data['last_name'])
        if 'email' in data:
            updates.append("email = ?")
            params.append(data['email'])
        if 'phone' in data:
            updates.append("phone = ?")
            params.append(data['phone'])
        if 'status' in data:
            updates.append("status = ?")
            params.append(data['status'])
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(beneficiary_id)
        
        query = f"UPDATE beneficiaries SET {', '.join(updates)} WHERE id = ?"
        c.execute(query, params)
        conn.commit()
        
        # Get updated beneficiary
        conn.row_factory = sqlite3.Row
        c.execute("SELECT * FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        row = c.fetchone()
        
        beneficiary = {
            'id': row['id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'phone': row['phone'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        return jsonify(beneficiary), 200
        
    except Exception as e:
        logger.error(f"Error updating beneficiary: {str(e)}")
        return jsonify({'message': 'Error updating beneficiary'}), 500

@app.route('/api/v1/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    """Delete a beneficiary"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if beneficiary exists
        c.execute("SELECT id FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'message': 'Beneficiary not found'}), 404
        
        # Delete beneficiary
        c.execute("DELETE FROM beneficiaries WHERE id = ?", (beneficiary_id,))
        conn.commit()
        conn.close()
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Error deleting beneficiary: {str(e)}")
        return jsonify({'message': 'Error deleting beneficiary'}), 500

# Programs endpoints
@app.route('/api/v1/programs', methods=['GET'])
def get_programs():
    """Get all programs"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM programs WHERE status = 'active' ORDER BY created_at DESC")
        rows = c.fetchall()
        
        programs = []
        for row in rows:
            programs.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'status': row['status'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        return jsonify({'programs': programs, 'total': len(programs)}), 200
        
    except Exception as e:
        logger.error(f"Error getting programs: {str(e)}")
        return jsonify({'message': 'Error fetching programs'}), 500

@app.route('/api/v1/programs', methods=['POST'])
def create_program():
    """Create a new program"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'message': 'Program name is required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Insert new program
        c.execute("""INSERT INTO programs (name, description, status, start_date, end_date)
                     VALUES (?, ?, ?, ?, ?)""",
                  (data['name'], data.get('description', ''), data.get('status', 'active'),
                   data.get('start_date'), data.get('end_date')))
        
        program_id = c.lastrowid
        conn.commit()
        
        # Get the created program
        c.execute("SELECT * FROM programs WHERE id = ?", (program_id,))
        conn.row_factory = sqlite3.Row
        row = c.fetchone()
        
        program = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'status': row['status'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        return jsonify(program), 201
        
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        return jsonify({'message': 'Error creating program'}), 500

@app.route('/api/v1/programs/<int:program_id>', methods=['DELETE'])
def delete_program(program_id):
    """Delete a program"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if program exists
        c.execute("SELECT id FROM programs WHERE id = ?", (program_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'message': 'Program not found'}), 404
        
        # Delete program
        c.execute("DELETE FROM programs WHERE id = ?", (program_id,))
        conn.commit()
        conn.close()
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Error deleting program: {str(e)}")
        return jsonify({'message': 'Error deleting program'}), 500

# Courses endpoints
@app.route('/api/v1/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM courses WHERE status = 'active' ORDER BY created_at DESC")
        rows = c.fetchall()
        
        courses = []
        for row in rows:
            courses.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'duration_hours': row['duration_hours'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        return jsonify({'courses': courses, 'total': len(courses)}), 200
        
    except Exception as e:
        logger.error(f"Error getting courses: {str(e)}")
        return jsonify({'message': 'Error fetching courses'}), 500

@app.route('/api/v1/courses', methods=['POST'])
def create_course():
    """Create a new course"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Course name is required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""INSERT INTO courses (name, description, duration_hours, status)
                     VALUES (?, ?, ?, ?)""",
                  (data['name'], data.get('description', ''), 
                   data.get('duration_hours', 0), data.get('status', 'active')))
        
        course_id = c.lastrowid
        conn.commit()
        
        c.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        conn.row_factory = sqlite3.Row
        row = c.fetchone()
        
        course = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'duration_hours': row['duration_hours'],
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        return jsonify(course), 201
        
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        return jsonify({'message': 'Error creating course'}), 500

@app.route('/api/v1/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'message': 'Course not found'}), 404
        
        c.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
        conn.close()
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        return jsonify({'message': 'Error deleting course'}), 500

# Sessions endpoints
@app.route('/api/v1/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    return jsonify({
        'sessions': [
            {
                'id': '1',
                'title': 'Introduction to Web Development',
                'course_id': '1',
                'course_name': 'Web Development Basics',
                'date': '2024-06-28',
                'start_time': '10:00',
                'end_time': '12:00',
                'location': 'Online',
                'instructor': 'John Smith',
                'status': 'scheduled',
                'max_participants': 30,
                'enrolled_count': 25
            },
            {
                'id': '2',
                'title': 'React Fundamentals',
                'course_id': '2',
                'course_name': 'Advanced React',
                'date': '2024-06-30',
                'start_time': '14:00',
                'end_time': '16:00',
                'location': 'Room A',
                'instructor': 'Jane Doe',
                'status': 'scheduled',
                'max_participants': 25,
                'enrolled_count': 20
            }
        ],
        'total': 2
    }), 200

# Coach Notes endpoints
@app.route('/api/v1/coach-notes', methods=['GET'])
def get_coach_notes():
    """Get all coach notes"""
    return jsonify({
        'notes': [
            {
                'id': '1',
                'student_id': '1',
                'student_name': 'John Doe',
                'subject': 'Progress Update',
                'content': 'Student is showing excellent progress in JavaScript',
                'category': 'progress',
                'created_at': '2024-06-25T10:00:00Z',
                'updated_at': '2024-06-25T10:00:00Z'
            },
            {
                'id': '2',
                'student_id': '2',
                'student_name': 'Jane Smith',
                'subject': 'Areas for Improvement',
                'content': 'Needs more practice with React hooks',
                'category': 'feedback',
                'created_at': '2024-06-24T14:30:00Z',
                'updated_at': '2024-06-24T14:30:00Z'
            }
        ],
        'total': 2
    }), 200

@app.route('/api/v1/coach-notes', methods=['POST'])
def create_coach_note():
    """Create a new coach note"""
    data = request.get_json()
    
    return jsonify({
        'id': '3',
        'student_id': data.get('student_id'),
        'student_name': data.get('student_name', 'Student'),
        'subject': data.get('subject'),
        'content': data.get('content'),
        'category': data.get('category', 'general'),
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }), 201

@app.route('/api/v1/coach-notes/<note_id>', methods=['DELETE'])
def delete_coach_note(note_id):
    """Delete a coach note"""
    return '', 204

# Learning paths endpoints  
@app.route('/api/v1/learning-paths', methods=['GET'])
def get_learning_paths_api():
    """Get all learning paths"""
    return jsonify({
        'learning_paths': [
            {
                'id': '1',
                'title': 'Full Stack Developer Path',
                'description': 'Become a full stack web developer',
                'level': 'intermediate',
                'duration': '6 months',
                'modules_count': 12,
                'enrolled_count': 156,
                'rating': 4.8,
                'status': 'active'
            },
            {
                'id': '2',
                'title': 'Data Science Fundamentals',
                'description': 'Start your data science journey',
                'level': 'beginner',
                'duration': '4 months',
                'modules_count': 8,
                'enrolled_count': 203,
                'rating': 4.9,
                'status': 'active'
            }
        ],
        'total': 2
    }), 200

# Evaluations endpoints
@app.route('/api/v1/evaluations', methods=['GET'])
def get_evaluations():
    """Get all evaluations"""
    return jsonify({
        'evaluations': [
            {
                'id': '1',
                'title': 'JavaScript Skills Assessment',
                'description': 'Test your JavaScript knowledge',
                'type': 'quiz',
                'duration_minutes': 60,
                'total_questions': 30,
                'passing_score': 70,
                'status': 'published',
                'created_at': '2024-06-01T10:00:00Z'
            },
            {
                'id': '2',
                'title': 'React Development Test',
                'description': 'Evaluate your React skills',
                'type': 'practical',
                'duration_minutes': 120,
                'total_questions': 20,
                'passing_score': 75,
                'status': 'published',
                'created_at': '2024-06-10T14:00:00Z'
            }
        ],
        'total': 2
    }), 200

# Reports endpoints
@app.route('/api/v1/reports/my-development', methods=['GET'])
def get_my_development_report():
    """Get personal development report"""
    return jsonify({
        'summary': {
            'courses_completed': 8,
            'courses_in_progress': 3,
            'total_hours': 124,
            'average_score': 85.5,
            'certificates_earned': 5
        },
        'recent_achievements': [
            {
                'title': 'JavaScript Certification',
                'date': '2024-06-20',
                'type': 'certificate',
                'score': 92
            },
            {
                'title': 'React Basics Course',
                'date': '2024-06-15',
                'type': 'course_completion',
                'score': 88
            }
        ],
        'skill_progress': [
            {'skill': 'JavaScript', 'level': 85},
            {'skill': 'React', 'level': 75},
            {'skill': 'HTML/CSS', 'level': 90},
            {'skill': 'Node.js', 'level': 60}
        ]
    }), 200

# Chat endpoints
@app.route('/api/v1/chat/conversations', methods=['GET'])
def get_conversations():
    """Get chat conversations"""
    return jsonify({
        'conversations': [
            {
                'id': 1,
                'type': 'direct',
                'participants': [
                    {
                        'id': 1,
                        'firstName': 'John',
                        'lastName': 'Doe',
                        'fullName': 'John Doe',
                        'role': 'student'
                    },
                    {
                        'id': 2,
                        'firstName': 'Jane',
                        'lastName': 'Smith',
                        'fullName': 'Jane Smith',
                        'role': 'trainer'
                    }
                ],
                'lastMessage': {
                    'id': 1,
                    'content': 'Thanks for the help!',
                    'sender': {'id': 1, 'fullName': 'John Doe'},
                    'createdAt': '2024-06-27T15:30:00Z'
                },
                'unreadCount': 0,
                'isPinned': False,
                'isMuted': False,
                'createdAt': '2024-06-20T10:00:00Z',
                'updatedAt': '2024-06-27T15:30:00Z'
            }
        ],
        'total': 1,
        'hasMore': False
    }), 200

# Bilan endpoints
@app.route('/api/v1/bilan/dashboard', methods=['GET'])
def get_bilan_dashboard():
    """Get bilan dashboard data"""
    return jsonify({
        'summary': {
            'total_assessments': 15,
            'completed_assessments': 8,
            'in_progress': 4,
            'upcoming': 3,
            'average_score': 82.5
        },
        'recent_assessments': [
            {
                'id': '1',
                'title': '360° Feedback Assessment',
                'type': '360',
                'status': 'completed',
                'completion_date': '2024-06-20',
                'score': 85
            },
            {
                'id': '2',
                'title': 'Skills Gap Analysis',
                'type': 'skills',
                'status': 'in_progress',
                'progress': 60
            }
        ],
        'career_insights': {
            'recommended_paths': 3,
            'skill_matches': 75,
            'market_demand': 'high'
        }
    }), 200

@app.route('/api/v1/bilan/overview', methods=['GET'])
def get_bilan_overview():
    """Get bilan overview data"""
    return jsonify({
        'modules': {
            'assessment_360': {
                'status': 'active',
                'total_assessments': 5,
                'completed': 3,
                'average_score': 82
            },
            'career_intelligence': {
                'status': 'active',
                'recommended_paths': 4,
                'skill_matches': 12,
                'market_insights': 8
            },
            'compliance': {
                'status': 'active',
                'documents': 15,
                'up_to_date': 12,
                'expiring_soon': 3
            },
            'learning': {
                'status': 'active',
                'paths_created': 6,
                'active_learners': 45,
                'completion_rate': 78
            }
        },
        'recent_activity': [
            {
                'type': 'assessment_completed',
                'title': '360 Feedback - Q2 2024',
                'user': 'John Doe',
                'date': '2024-06-25T10:00:00Z'
            },
            {
                'type': 'path_enrolled',
                'title': 'Data Science Career Path',
                'user': 'Jane Smith',
                'date': '2024-06-24T14:30:00Z'
            }
        ]
    }), 200

@app.route('/api/v1/bilan/assessments', methods=['GET'])
def get_bilan_assessments():
    """Get all assessments"""
    return jsonify({
        'assessments': [
            {
                'id': '1',
                'title': '360° Feedback Assessment',
                'description': 'Comprehensive feedback from peers and managers',
                'type': '360',
                'status': 'active',
                'questions': 25,
                'duration': 30,
                'created_at': '2024-01-15T10:00:00Z'
            },
            {
                'id': '2',
                'title': 'Technical Skills Assessment',
                'description': 'Evaluate your technical competencies',
                'type': 'skills',
                'status': 'active',
                'questions': 40,
                'duration': 45,
                'created_at': '2024-02-01T10:00:00Z'
            },
            {
                'id': '3',
                'title': 'Leadership Assessment',
                'description': 'Assess your leadership qualities',
                'type': 'leadership',
                'status': 'active',
                'questions': 30,
                'duration': 35,
                'created_at': '2024-02-15T10:00:00Z'
            }
        ],
        'total': 3
    }), 200

@app.route('/api/v1/bilan/assessments/<assessment_id>', methods=['GET'])
def get_bilan_assessment_detail(assessment_id):
    """Get assessment detail"""
    return jsonify({
        'id': assessment_id,
        'title': '360° Feedback Assessment',
        'description': 'Comprehensive feedback from peers and managers',
        'type': '360',
        'status': 'active',
        'questions': [
            {
                'id': '1',
                'text': 'How would you rate the communication skills?',
                'type': 'rating',
                'scale': 5
            },
            {
                'id': '2',
                'text': 'What are the key strengths?',
                'type': 'text'
            }
        ],
        'participants': [
            {
                'id': '1',
                'name': 'Manager',
                'role': 'manager',
                'status': 'completed'
            },
            {
                'id': '2',
                'name': 'Peer 1',
                'role': 'peer',
                'status': 'pending'
            }
        ]
    }), 200

@app.route('/api/v1/bilan/career-paths', methods=['GET'])
def get_career_paths():
    """Get career paths"""
    return jsonify({
        'paths': [
            {
                'id': '1',
                'title': 'Frontend Developer',
                'description': 'Master modern web development',
                'level': 'intermediate',
                'duration': '6 months',
                'skills': ['HTML/CSS', 'JavaScript', 'React', 'Vue.js'],
                'demand': 'high',
                'salary_range': '$70k - $120k'
            },
            {
                'id': '2',
                'title': 'Data Scientist',
                'description': 'Become a data science expert',
                'level': 'advanced',
                'duration': '9 months',
                'skills': ['Python', 'Machine Learning', 'Statistics', 'SQL'],
                'demand': 'very high',
                'salary_range': '$90k - $150k'
            }
        ],
        'total': 2
    }), 200

@app.route('/api/v1/bilan/learning-paths', methods=['GET'])
def get_learning_paths():
    """Get learning paths"""
    return jsonify({
        'paths': [
            {
                'id': '1',
                'title': 'Web Development Fundamentals',
                'description': 'Learn the basics of web development',
                'modules': 8,
                'duration': '3 months',
                'level': 'beginner',
                'enrolled': 125,
                'rating': 4.8
            },
            {
                'id': '2',
                'title': 'Advanced React Development',
                'description': 'Master React and its ecosystem',
                'modules': 12,
                'duration': '4 months',
                'level': 'advanced',
                'enrolled': 89,
                'rating': 4.9
            }
        ],
        'total': 2
    }), 200

@app.route('/api/v1/bilan/compliance/documents', methods=['GET'])
def get_compliance_documents():
    """Get compliance documents"""
    return jsonify({
        'documents': [
            {
                'id': '1',
                'title': 'Skills Certificate - Web Development',
                'type': 'certificate',
                'status': 'valid',
                'issue_date': '2024-01-15',
                'expiry_date': '2026-01-15',
                'issuer': 'BDC Academy'
            },
            {
                'id': '2',
                'title': 'Professional Development Plan',
                'type': 'plan',
                'status': 'active',
                'last_updated': '2024-06-01',
                'next_review': '2024-12-01'
            }
        ],
        'total': 2
    }), 200

# Add a catch-all API route that returns a proper JSON response
@app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all_api(path):
    """Catch-all for unimplemented API endpoints"""
    return jsonify({
        'message': 'This endpoint is being implemented',
        'endpoint': f'/api/v1/{path}',
        'method': request.method,
        'status': 'under_construction'
    }), 501

# Serve React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app for all non-API routes"""
    # Don't serve React app for API routes
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # Check if path is a file
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    
    # For all other routes, serve index.html (React app)
    return send_from_directory(DIST_DIR, 'index.html')

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=8080, debug=True)