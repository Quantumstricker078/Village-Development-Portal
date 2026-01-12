# app.py - Village Development Information Portal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'village_portal_secret_key_2024'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            publish_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valid_until TIMESTAMP,
            attachment_url TEXT,
            created_by INTEGER
        )
    ''')
    
    # Create schemes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            department TEXT,
            eligibility TEXT,
            benefits TEXT,
            apply_link TEXT,
            published_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            contact_number TEXT,
            address TEXT,
            in_charge TEXT,
            city TEXT
        )
    ''')
    
    # Create beneficiaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            scheme_id INTEGER,
            mobile TEXT,
            status TEXT DEFAULT 'Pending',
            registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            message TEXT,
            submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'New'
        )
    ''')
    
    # Insert default admin user
    try:
        hashed_password = generate_password_hash('admin123')
        cursor.execute(
            'INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
            ('Admin User', 'admin@villageportal.com', hashed_password, 'admin')
        )
    except:
        pass
    
    # Insert sample data
    cursor.execute('''
        INSERT OR IGNORE INTO schemes (title, description, department, eligibility, benefits, apply_link) 
        VALUES 
        ('Farmers Loan Scheme', 'Financial assistance for farmers for agricultural development', 'Agriculture', 'Farmers with minimum 2 acres land', 'Up to ₹1,00,000 loan at 4% interest rate', '#'),
        ('Student Scholarship', 'Scholarship for meritorious students from rural areas', 'Education', 'Students with 80%+ marks in previous year', '₹5000 per year for educational expenses', '#'),
        ('Health Insurance', 'Free health insurance for below poverty line families', 'Health', 'Families with annual income less than ₹1,00,000', 'Health coverage up to ₹5,00,000 per family', '#'),
        ('Housing Scheme', 'Affordable housing for rural families', 'Social Welfare', 'Families without own house', '₹2,00,000 subsidy for house construction', '#')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO services (category, name, contact_number, address, in_charge, city) 
        VALUES 
        ('Health', 'Primary Health Center', '9876543210', 'Main Road, Near Post Office', 'Dr. Sharma', 'Sample Village'),
        ('Education', 'Government High School', '9876543211', 'School Road, Center Point', 'Principal Verma', 'Sample Village'),
        ('Police', 'Police Station', '100', 'Station Road, West Side', 'Inspector Singh', 'Sample Village'),
        ('Bank', 'State Bank Branch', '9876543212', 'Market Road, Main Market', 'Manager Gupta', 'Sample Village')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO notices (title, description, valid_until) 
        VALUES 
        ('Monthly Gram Panchayat Meeting', 'Monthly village meeting on 15th August at 10:00 AM in Panchayat Office', '2024-08-20'),
        ('Water Supply Maintenance', 'Water supply will be interrupted on 10th August from 9 AM to 5 PM for pipeline maintenance', '2024-08-12'),
        ('Free Vaccination Camp', 'Free vaccination camp for children below 5 years on 20th August at Health Center', '2024-08-25'),
        ('Electricity Bill Payment', 'Last date for electricity bill payment extended to 25th August', '2024-08-25')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO beneficiaries (name, age, gender, scheme_id, mobile, status) 
        VALUES 
        ('Ramesh Kumar', 45, 'Male', 1, '9876543201', 'Approved'),
        ('Sita Devi', 35, 'Female', 2, '9876543202', 'Pending'),
        ('Amit Singh', 28, 'Male', 3, '9876543203', 'Approved')
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
init_db()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['name'], user['email'], user['role'])
    return None

# Routes
@app.route('/')
@login_required
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get counts for dashboard
    cursor.execute('SELECT COUNT(*) as count FROM schemes')
    schemes_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM beneficiaries')
    beneficiaries_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM notices')
    notices_count = cursor.fetchone()['count']
    
    # Get latest notices
    cursor.execute('SELECT * FROM notices ORDER BY publish_date DESC LIMIT 3')
    latest_notices = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         schemes_count=schemes_count,
                         beneficiaries_count=beneficiaries_count,
                         notices_count=notices_count,
                         latest_notices=latest_notices)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/acknowledgements')
def acknowledgements():
    return render_template('acknowledgements.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['name'], user['email'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')

            # Respect the 'next' parameter when present (and simple safety check)
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None

            # Redirect admin users to admin dashboard, others to index (or next)
            if user_obj.role == 'admin':
                return redirect(next_page or url_for('admin_dashboard'))
            else:
                return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if not name or not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email already registered. Please log in or use a different email', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (name, email, hashed_password, 'user')
            )
            conn.commit()
            conn.close()
            
            flash('Account created successfully! Please log in with your credentials', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.close()
            flash(f'An error occurred during registration: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Check if user is admin
    if current_user.role != 'admin':
        flash('You do not have permission to access the admin dashboard', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get counts for admin dashboard
    cursor.execute('SELECT COUNT(*) as count FROM schemes')
    schemes_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM beneficiaries')
    beneficiaries_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM notices')
    notices_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM services')
    services_count = cursor.fetchone()['count']
    
    # Get recent beneficiaries
    cursor.execute('''
        SELECT b.*, s.title as scheme_name 
        FROM beneficiaries b 
        LEFT JOIN schemes s ON b.scheme_id = s.id 
        ORDER BY b.registered_on DESC LIMIT 5
    ''')
    recent_beneficiaries = cursor.fetchall()
    
    cursor.execute('SELECT id, title FROM schemes')
    schemes = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         schemes_count=schemes_count,
                         beneficiaries_count=beneficiaries_count,
                         notices_count=notices_count,
                         services_count=services_count,
                         recent_beneficiaries=recent_beneficiaries,
                         schemes=schemes)

@app.route('/notices')
def notices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notices ORDER BY publish_date DESC')
    notices = cursor.fetchall()
    conn.close()
    
    return render_template('notices.html', notices=notices)

@app.route('/schemes')
def schemes():
    category = request.args.get('category', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM schemes WHERE department = ? ORDER BY published_on DESC', (category,))
    else:
        cursor.execute('SELECT * FROM schemes ORDER BY published_on DESC')
    
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('schemes.html', schemes=schemes, selected_category=category)

@app.route('/services')
def services():
    category = request.args.get('category', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if category:
        cursor.execute('SELECT * FROM services WHERE category = ?', (category,))
    else:
        cursor.execute('SELECT * FROM services')
    
    services = cursor.fetchall()
    conn.close()
    
    return render_template('services.html', services=services, selected_category=category)

@app.route('/beneficiaries')
@login_required
def beneficiaries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, s.title as scheme_name 
        FROM beneficiaries b 
        LEFT JOIN schemes s ON b.scheme_id = s.id 
        ORDER BY b.registered_on DESC
    ''')
    beneficiaries = cursor.fetchall()
    
    cursor.execute('SELECT id, title FROM schemes')
    schemes = cursor.fetchall()
    
    conn.close()
    
    return render_template('beneficiaries.html', 
                         beneficiaries=beneficiaries, 
                         schemes=schemes)

# API Routes
@app.route('/api/add_notice', methods=['POST'])
@login_required
def add_notice():
    try:
        title = request.form['title']
        description = request.form['description']
        valid_until = request.form['valid_until']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO notices (title, description, valid_until, created_by) VALUES (?, ?, ?, ?)',
            (title, description, valid_until, current_user.id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Notice added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/add_scheme', methods=['POST'])
@login_required
def add_scheme():
    try:
        title = request.form['title']
        description = request.form['description']
        department = request.form['department']
        eligibility = request.form['eligibility']
        benefits = request.form['benefits']
        apply_link = request.form['apply_link']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO schemes (title, description, department, eligibility, benefits, apply_link) VALUES (?, ?, ?, ?, ?, ?)',
            (title, description, department, eligibility, benefits, apply_link)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Scheme added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/add_beneficiary', methods=['POST'])
@login_required
def add_beneficiary():
    try:
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        scheme_id = request.form['scheme_id']
        mobile = request.form['mobile']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO beneficiaries (name, age, gender, scheme_id, mobile) VALUES (?, ?, ?, ?, ?)',
            (name, age, gender, scheme_id, mobile)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Beneficiary added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/search')
def search():
    try:
        query = request.args.get('q', '')
        
        if not query or len(query) < 2:
            return jsonify({
                'success': True,
                'results': {
                    'schemes': [],
                    'notices': [],
                    'services': []
                }
            })
        
        conn = get_db()
        cursor = conn.cursor()
        
        results = {}
        
        # Search in schemes
        cursor.execute('SELECT * FROM schemes WHERE title LIKE ? OR description LIKE ?', 
                      (f'%{query}%', f'%{query}%'))
        results['schemes'] = cursor.fetchall()
        
        # Search in notices
        cursor.execute('SELECT * FROM notices WHERE title LIKE ? OR description LIKE ?', 
                      (f'%{query}%', f'%{query}%'))
        results['notices'] = cursor.fetchall()
        
        # Search in services
        cursor.execute('SELECT * FROM services WHERE name LIKE ? OR category LIKE ?', 
                      (f'%{query}%', f'%{query}%'))
        results['services'] = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'results': {
                'schemes': [dict(row) for row in results['schemes']],
                'notices': [dict(row) for row in results['notices']],
                'services': [dict(row) for row in results['services']]
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Search error: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Starting Village Development Information Portal...")
    print("🌐 Open: http://localhost:5000")
    print("🔑 Admin Login: admin@villageportal.com / admin123")
    print("📊 Sample data loaded successfully")
    app.run(debug=True)
