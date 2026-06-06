from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = sqlite3.connect('admission.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            country TEXT NOT NULL,
            email TEXT NOT NULL,
            program TEXT NOT NULL,
            academic_year TEXT NOT NULL,
            gpa REAL,
            entrance_exam_score TEXT,
            extracurricular TEXT,
            essay TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id)
        );
        
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            seats INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    db.commit()
    db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        confirm_password = request.form.get('confirm_password')
        
        error = None
        
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not full_name:
            error = 'Full name is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        
        if error is None:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO users (email, password, full_name) VALUES (?, ?, ?)',
                    (email, generate_password_hash(password), full_name)
                )
                db.commit()
                db.close()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                db.close()
                error = 'Email already registered.'
        
        flash(error, 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        error = None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        db.close()
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        
        flash(error, 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user['role'] == 'admin':
        applications = db.execute('SELECT * FROM applications ORDER BY applied_at DESC').fetchall()
        total_applications = len(applications)
        pending = len([a for a in applications if a['status'] == 'pending'])
        approved = len([a for a in applications if a['status'] == 'approved'])
        rejected = len([a for a in applications if a['status'] == 'rejected'])
        
        db.close()
        
        return render_template('admin_dashboard.html', 
                             total_applications=total_applications,
                             pending=pending,
                             approved=approved,
                             rejected=rejected,
                             applications=applications)
    else:
        applications = db.execute('SELECT * FROM applications WHERE user_id = ? ORDER BY applied_at DESC', 
                                 (session['user_id'],)).fetchall()
        db.close()
        
        return render_template('student_dashboard.html', applications=applications)

@app.route('/application/new', methods=['GET', 'POST'])
@login_required
def new_application():
    db = get_db()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        country = request.form.get('country')
        email = request.form.get('email')
        program = request.form.get('program')
        academic_year = request.form.get('academic_year')
        gpa = request.form.get('gpa')
        entrance_exam_score = request.form.get('entrance_exam_score')
        extracurricular = request.form.get('extracurricular')
        essay = request.form.get('essay')
        
        try:
            cursor = db.execute(
                '''INSERT INTO applications 
                (user_id, full_name, dob, gender, phone, address, city, state, zip_code, country, email, program, academic_year, gpa, entrance_exam_score, extracurricular, essay)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session['user_id'], full_name, dob, gender, phone, address, city, state, zip_code, country, email, program, academic_year, gpa, entrance_exam_score, extracurricular, essay)
            )
            db.commit()
            application_id = cursor.lastrowid
            
            # Handle file uploads
            if 'documents' in request.files:
                files = request.files.getlist('documents')
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{application_id}_{filename}")
                        file.save(filepath)
                        db.execute(
                            'INSERT INTO documents (application_id, document_type, file_path) VALUES (?, ?, ?)',
                            (application_id, filename.rsplit('.', 1)[1].upper(), filepath)
                        )
            
            db.commit()
            db.close()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('view_application', app_id=application_id))
        except Exception as e:
            db.close()
            flash(f'Error submitting application: {str(e)}', 'danger')
    
    programs = db.execute('SELECT * FROM programs').fetchall()
    db.close()
    
    return render_template('application_form.html', programs=programs)

@app.route('/application/<int:app_id>')
@login_required
def view_application(app_id):
    db = get_db()
    application = db.execute('SELECT * FROM applications WHERE id = ?', (app_id,)).fetchone()
    
    if not application:
        db.close()
        flash('Application not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check permission
    if session['role'] != 'admin' and application['user_id'] != session['user_id']:
        db.close()
        flash('You do not have permission to view this application.', 'danger')
        return redirect(url_for('dashboard'))
    
    documents = db.execute('SELECT * FROM documents WHERE application_id = ?', (app_id,)).fetchall()
    db.close()
    
    return render_template('view_application.html', application=application, documents=documents)

@app.route('/application/<int:app_id>/update-status', methods=['POST'])
@admin_required
def update_application_status(app_id):
    status = request.form.get('status')
    
    db = get_db()
    db.execute('UPDATE applications SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
              (status, app_id))
    db.commit()
    
    # Create notification
    application = db.execute('SELECT user_id FROM applications WHERE id = ?', (app_id,)).fetchone()
    db.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)',
              (application['user_id'], f'Your application status has been updated to: {status}'))
    db.commit()
    db.close()
    
    flash('Application status updated successfully!', 'success')
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/programs', methods=['GET', 'POST'])
@admin_required
def manage_programs():
    db = get_db()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        seats = request.form.get('seats')
        
        db.execute(
            'INSERT INTO programs (name, description, duration, seats) VALUES (?, ?, ?, ?)',
            (name, description, duration, seats)
        )
        db.commit()
        flash('Program added successfully!', 'success')
    
    programs = db.execute('SELECT * FROM programs').fetchall()
    db.close()
    
    return render_template('manage_programs.html', programs=programs)

@app.route('/api/statistics')
@admin_required
def get_statistics():
    db = get_db()
    
    # Applications by status
    status_stats = db.execute('''
        SELECT status, COUNT(*) as count FROM applications GROUP BY status
    ''').fetchall()
    
    # Applications by program
    program_stats = db.execute('''
        SELECT program, COUNT(*) as count FROM applications GROUP BY program
    ''').fetchall()
    
    # Recent applications
    recent = db.execute('''
        SELECT full_name, program, status, applied_at FROM applications ORDER BY applied_at DESC LIMIT 10
    ''').fetchall()
    
    db.close()
    
    return jsonify({
        'status_stats': [dict(row) for row in status_stats],
        'program_stats': [dict(row) for row in program_stats],
        'recent': [dict(row) for row in recent]
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
