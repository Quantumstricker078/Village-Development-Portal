# app.py - Village Development Information Portal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'village_portal_secret_key_2024'

# Database setup
def init_db(db_path=None):
    if db_path is None:
        db_path = app.config.get('DATABASE', 'database.db')
    conn = sqlite3.connect(db_path)
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

    cursor.execute('PRAGMA table_info(users)')
    user_columns = [row[1] for row in cursor.fetchall()]
    if 'location' not in user_columns:
        cursor.execute('ALTER TABLE users ADD COLUMN location TEXT')

    cursor.execute('PRAGMA table_info(users)')
    user_columns = [row[1] for row in cursor.fetchall()]
    
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
    cursor.execute('''
        DELETE FROM notices
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM notices
            GROUP BY title
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_notices_title ON notices(title)')
    
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
            published_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT DEFAULT 'All'
        )
    ''')
    cursor.execute('PRAGMA table_info(schemes)')
    scheme_columns = [row[1] for row in cursor.fetchall()]
    if 'location' not in scheme_columns:
        cursor.execute('ALTER TABLE schemes ADD COLUMN location TEXT DEFAULT "All"')
    cursor.execute('''
        DELETE FROM schemes
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM schemes
            GROUP BY title
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_schemes_title ON schemes(title)')
    
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
    cursor.execute('''
        DELETE FROM services
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM services
            GROUP BY category, name
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_services_category_name ON services(category, name)')
    
    # Create beneficiaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            dob TEXT,
            aadhaar TEXT,
            scheme_id INTEGER,
            mobile TEXT,
            status TEXT DEFAULT 'Pending',
            registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('PRAGMA table_info(beneficiaries)')
    beneficiary_columns = [row[1] for row in cursor.fetchall()]
    if 'user_id' not in beneficiary_columns:
        cursor.execute('ALTER TABLE beneficiaries ADD COLUMN user_id INTEGER')
    if 'dob' not in beneficiary_columns:
        cursor.execute('ALTER TABLE beneficiaries ADD COLUMN dob TEXT')
    if 'aadhaar' not in beneficiary_columns:
        cursor.execute('ALTER TABLE beneficiaries ADD COLUMN aadhaar TEXT')
    cursor.execute('''
        DELETE FROM beneficiaries
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM beneficiaries
            GROUP BY name, mobile, scheme_id
        )
    ''')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_beneficiaries_unique ON beneficiaries(name, mobile, scheme_id)')
    
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

    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            related_id INTEGER,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure notices can link to a specific scheme when needed
    cursor.execute('PRAGMA table_info(notices)')
    notice_columns = [row[1] for row in cursor.fetchall()]
    if 'scheme_id' not in notice_columns:
        cursor.execute('ALTER TABLE notices ADD COLUMN scheme_id INTEGER')
    
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
    # Clean up old test data if present in the database
    cursor.execute("DELETE FROM services WHERE city = 'Sample Village'")
    cursor.execute("DELETE FROM schemes WHERE title IN ('Farmers Loan Scheme', 'Student Scholarship', 'Health Insurance', 'Housing Scheme', 'Sillod Solar Subsidy', 'Vaijapur Tractor Scheme', 'Kannad Irrigation Project', 'Soegaon Women Entrepreneurship')")
    cursor.execute("DELETE FROM notices WHERE title IN ('Monthly Gram Panchayat Meeting', 'Water Supply Maintenance', 'Free Vaccination Camp', 'Electricity Bill Payment')")

    cursor.execute('''
        INSERT OR IGNORE INTO schemes (title, description, department, eligibility, benefits, apply_link, location) 
        VALUES 
        ('Paithan Godavari Irrigation Grant', 'Funding for drip and sprinkler irrigation near Godavari basin', 'Agriculture', 'Farmers in Paithan taluka with <5 acres', '90% subsidy on irrigation equipment', '#', 'Paithan'),
        ('Paithani Saree Weavers Subsidy', 'Financial aid for traditional Paithani weavers', 'Social Welfare', 'Registered weavers in Paithan', '₹50,000 grant for loom upgrade', '#', 'Paithan'),
        ('Gangapur Sugar Cane Harvester Aid', 'Assistance for purchasing mechanized harvesters', 'Agriculture', 'Sugar cane farmers in Gangapur', '₹5,00,000 subsidy on harvesters', '#', 'Gangapur'),
        ('Vaijapur Onion Storage Subsidy', 'Grants for building onion storage structures (Kanda Chawl)', 'Agriculture', 'Farmers in Vaijapur', '₹1,00,000 per storage structure', '#', 'Vaijapur'),
        ('Vaijapur Rural Tech Education', 'Scholarships for IT and technical diploma students', 'Education', 'Students from Vaijapur scoring >70%', 'Full tuition fee waiver', '#', 'Vaijapur'),
        ('Sillod Maize Crop Insurance', 'Premium-free crop insurance for maize cultivators', 'Agriculture', 'Maize farmers in Sillod', 'Coverage up to ₹40,000 per acre', '#', 'Sillod'),
        ('Phulambri Dairy Development Grant', 'Support for purchasing high-yield milch animals', 'Agriculture', 'Marginal farmers in Phulambri', '50% subsidy on purchase of 2 cows/buffaloes', '#', 'Phulambri'),
        ('Phulambri Women SHG Fund', 'Seed capital for Women Self-Help Groups', 'Social Welfare', 'Registered active SHGs in Phulambri', '₹1,00,000 revolving fund', '#', 'Phulambri'),
        ('Kannad Tribal Education Scholarship', 'Special education grant for tribal students', 'Education', 'Tribal students residing in Kannad', '₹10,000 annual scholarship + free hostel', '#', 'Kannad'),
        ('Kannad Solar Pump Yojana', 'Subsidized solar water pumps for remote farms', 'Agriculture', 'Farmers in Kannad without grid electricity', '95% subsidy on 3HP/5HP solar pumps', '#', 'Kannad'),
        ('Khuldabad Heritage Tourism Grant', 'Funding for locals starting homestays or guide services', 'Social Welfare', 'Residents of Khuldabad', '₹2,00,000 low-interest loan', '#', 'Khuldabad'),
        ('Khuldabad Fruit Orchard Subsidy', 'Support for planting custard apple and mango orchards', 'Agriculture', 'Farmers in Khuldabad', '100% subsidy on saplings and fertilizers', '#', 'Khuldabad'),
        ('Soegaon Cotton Seed Aid', 'Subsidized high-quality BT cotton seeds', 'Agriculture', 'Cotton farmers in Soegaon', 'Up to 10 packets at 50% cost', '#', 'Soegaon'),
        ('Soegaon Girl Child Education', 'Financial support for girls completing higher secondary', 'Education', 'Girl students in Soegaon', '₹15,000 fixed deposit upon passing 12th', '#', 'Soegaon'),
        ('Marathwada Universal Health Cover', 'Comprehensive health insurance for rural families', 'Health', 'All rural families in the district', 'Health cover up to ₹5,00,000 per family', '#', 'All')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO services (category, name, contact_number, address, in_charge, city) 
        VALUES 
        ('Health', 'Paithan Civil Hospital', '9876543220', 'Main Road, Paithan', 'Dr. Patil', 'Paithan'),
        ('Bank', 'Godavari Rural Bank', '9876543221', 'Market Yard, Paithan', 'Manager Kulkarni', 'Paithan'),
        ('Agriculture', 'Gangapur Krishi Kendra', '9876543222', 'Krishi Utpanna Bazar Samiti, Gangapur', 'Mr. Jadhav', 'Gangapur'),
        ('Police', 'Gangapur Taluka Police Station', '100', 'Station Road, Gangapur', 'Inspector Pawar', 'Gangapur'),
        ('Education', 'Vaijapur Technical Institute', '9876543223', 'College Road, Vaijapur', 'Principal Joshi', 'Vaijapur'),
        ('Bank', 'State Bank of Vaijapur', '9876543224', 'Main Branch, Vaijapur', 'Manager Deshmukh', 'Vaijapur'),
        ('Health', 'Sillod Rural Health Clinic', '9876543225', 'Panchayat Road, Sillod', 'Dr. Sharma', 'Sillod'),
        ('Agriculture', 'Sillod Fertilizer Depot', '9876543226', 'Market Area, Sillod', 'Mr. Kale', 'Sillod'),
        ('Education', 'Phulambri Zila Parishad School', '9876543227', 'Center Block, Phulambri', 'Headmaster Wagh', 'Phulambri'),
        ('Police', 'Phulambri Security Post', '100', 'West Highway, Phulambri', 'Sub-Inspector Singh', 'Phulambri'),
        ('Bank', 'Kannad Cooperative Bank', '9876543228', 'Shivaji Chowk, Kannad', 'Manager Rathi', 'Kannad'),
        ('Health', 'Kannad Maternity Hospital', '9876543229', 'Civil Road, Kannad', 'Dr. Chavan', 'Kannad'),
        ('Education', 'Khuldabad Heritage School', '9876543230', 'Dargah Road, Khuldabad', 'Principal Begum', 'Khuldabad'),
        ('Police', 'Khuldabad Tourist Police', '100', 'Tourism Center, Khuldabad', 'Inspector Khan', 'Khuldabad'),
        ('Agriculture', 'Soegaon Cotton Development Office', '9876543231', 'Agri Block, Soegaon', 'Mr. Munde', 'Soegaon'),
        ('Bank', 'Maharashtra Gramin Bank', '9876543232', 'Main Street, Soegaon', 'Manager Joshi', 'Soegaon')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO notices (title, description, valid_until, scheme_id) 
        VALUES 
        ('Paithan Canal Water Release Schedule', 'Godavari left bank canal water will be released for Rabi crops starting 1st November.', '2026-11-15', NULL),
        ('Sillod Market Committee Elections', 'Nominations are open for the Sillod Krishi Utpanna Bazar Samiti elections.', '2026-09-30', NULL),
        ('Khuldabad Tourism Festival Preparations', 'Local homestay owners are invited to a preparation meeting at the Panchayat office.', '2026-12-10', 11),
        ('Vaijapur Crop Damage Survey Final List', 'The final list of beneficiaries for the recent unseasonal rain damage is published at the Tehsil office.', '2026-08-25', 4),
        ('Mega Health Camp in Gangapur', 'Free health checkup and medicine distribution for senior citizens at Gangapur Krishi Kendra ground.', '2026-10-05', 15)
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO beneficiaries (name, age, gender, scheme_id, mobile, status) 
        VALUES 
        ('Tukaram Patil', 52, 'Male', 1, '9876543201', 'Approved'),
        ('Sujata Kulkarni', 38, 'Female', 2, '9876543202', 'Pending'),
        ('Namdev Jadhav', 45, 'Male', 3, '9876543203', 'Approved'),
        ('Anjali Deshmukh', 19, 'Female', 5, '9876543204', 'Approved'),
        ('Babanrao Kale', 60, 'Male', 6, '9876543205', 'Pending')
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    db_path = app.config.get('DATABASE', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
init_db()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, email, role, location=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.location = location

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['name'], user['email'], user['role'], dict(user).get('location'))
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
            user_obj = User(user['id'], user['name'], user['email'], user['role'], dict(user).get('location'))
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

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return render_template('forgot_password.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('forgot_password.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('forgot_password.html')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            flash('No account found with that email address.', 'error')
            return render_template('forgot_password.html')

        hashed_password = generate_password_hash(password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (hashed_password, email))
        conn.commit()
        conn.close()

        flash('Your password has been reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

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
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get counts for admin dashboard
        cursor.execute('SELECT COUNT(*) as count FROM schemes')
        schemes_count_result = cursor.fetchone()
        schemes_count = schemes_count_result['count'] if schemes_count_result else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM beneficiaries')
        beneficiaries_count_result = cursor.fetchone()
        beneficiaries_count = beneficiaries_count_result['count'] if beneficiaries_count_result else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM notices')
        notices_count_result = cursor.fetchone()
        notices_count = notices_count_result['count'] if notices_count_result else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM services')
        services_count_result = cursor.fetchone()
        services_count = services_count_result['count'] if services_count_result else 0
        
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
        
        # Admin notifications
        notifications = []
        
        # New beneficiary requests
        cursor.execute('SELECT COUNT(*) as count FROM beneficiaries WHERE status = "Pending"')
        pending_count = cursor.fetchone()['count']
        if pending_count > 0:
            notifications.append(f"{pending_count} new beneficiary request(s) pending approval")
        
        # Expiring notices (within 7 days)
        cursor.execute('SELECT COUNT(*) as count FROM notices WHERE valid_until IS NOT NULL AND DATE(valid_until) <= DATE("now", "+7 days")')
        expiring_count = cursor.fetchone()['count']
        if expiring_count > 0:
            notifications.append(f"{expiring_count} notice(s) expiring within 7 days")
        
        conn.close()
        
        return render_template('admin_dashboard.html',
                             schemes_count=schemes_count,
                             beneficiaries_count=beneficiaries_count,
                             notices_count=notices_count,
                             services_count=services_count,
                             recent_beneficiaries=recent_beneficiaries,
                             schemes=schemes,
                             notifications=notifications)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

# Admin CRUD Routes

@app.route('/admin/schemes')
@login_required
def admin_schemes():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schemes ORDER BY published_on DESC')
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('admin_schemes.html', schemes=schemes)

@app.route('/admin/schemes/add', methods=['GET', 'POST'])
@login_required
def admin_add_scheme():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        department = request.form['department']
        eligibility = request.form['eligibility']
        benefits = request.form['benefits']
        apply_link = request.form['apply_link']
        location = request.form.get('location', 'All')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO schemes (title, description, department, eligibility, benefits, apply_link, location) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, department, eligibility, benefits, apply_link, location)
        )
        conn.commit()
        conn.close()
        
        flash('Scheme added successfully', 'success')
        return redirect(url_for('admin_schemes'))
    
    return render_template('admin_scheme_form.html', scheme=None)

@app.route('/admin/schemes/edit/<int:scheme_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_scheme(scheme_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        department = request.form['department']
        eligibility = request.form['eligibility']
        benefits = request.form['benefits']
        apply_link = request.form['apply_link']
        location = request.form.get('location', 'All')
        
        cursor.execute(
            'UPDATE schemes SET title=?, description=?, department=?, eligibility=?, benefits=?, apply_link=?, location=? WHERE id=?',
            (title, description, department, eligibility, benefits, apply_link, location, scheme_id)
        )
        conn.commit()
        conn.close()
        
        flash('Scheme updated successfully', 'success')
        return redirect(url_for('admin_schemes'))
    
    cursor.execute('SELECT * FROM schemes WHERE id = ?', (scheme_id,))
    scheme = cursor.fetchone()
    conn.close()
    
    if not scheme:
        flash('Scheme not found', 'error')
        return redirect(url_for('admin_schemes'))
    
    return render_template('admin_scheme_form.html', scheme=scheme)

@app.route('/admin/schemes/delete/<int:scheme_id>')
@login_required
def admin_delete_scheme(scheme_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM schemes WHERE id = ?', (scheme_id,))
    conn.commit()
    conn.close()
    
    flash('Scheme deleted successfully', 'success')
    return redirect(url_for('admin_schemes'))

@app.route('/admin/notices')
@login_required
def admin_notices():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT n.*, s.title as scheme_title FROM notices n LEFT JOIN schemes s ON n.scheme_id = s.id ORDER BY n.publish_date DESC')
    notices = cursor.fetchall()
    cursor.execute('SELECT id, title FROM schemes')
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('admin_notices.html', notices=notices, schemes=schemes)

@app.route('/admin/notices/add', methods=['GET', 'POST'])
@login_required
def admin_add_notice():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        valid_until = request.form.get('valid_until')
        scheme_id = request.form.get('scheme_id') or None
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO notices (title, description, valid_until, scheme_id, created_by) VALUES (?, ?, ?, ?, ?)',
            (title, description, valid_until, scheme_id, current_user.id)
        )
        conn.commit()
        conn.close()
        
        flash('Notice added successfully', 'success')
        return redirect(url_for('admin_notices'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM schemes')
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('admin_notice_form.html', notice=None, schemes=schemes)

@app.route('/admin/notices/edit/<int:notice_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_notice(notice_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        valid_until = request.form.get('valid_until')
        scheme_id = request.form.get('scheme_id') or None
        
        cursor.execute(
            'UPDATE notices SET title=?, description=?, valid_until=?, scheme_id=? WHERE id=?',
            (title, description, valid_until, scheme_id, notice_id)
        )
        conn.commit()
        conn.close()
        
        flash('Notice updated successfully', 'success')
        return redirect(url_for('admin_notices'))
    
    cursor.execute('SELECT * FROM notices WHERE id = ?', (notice_id,))
    notice = cursor.fetchone()
    cursor.execute('SELECT id, title FROM schemes')
    schemes = cursor.fetchall()
    conn.close()
    
    if not notice:
        flash('Notice not found', 'error')
        return redirect(url_for('admin_notices'))
    
    return render_template('admin_notice_form.html', notice=notice, schemes=schemes)

@app.route('/admin/notices/delete/<int:notice_id>')
@login_required
def admin_delete_notice(notice_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notices WHERE id = ?', (notice_id,))
    conn.commit()
    conn.close()
    
    flash('Notice deleted successfully', 'success')
    return redirect(url_for('admin_notices'))

@app.route('/admin/services')
@login_required
def admin_services():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services ORDER BY name ASC')
    services = cursor.fetchall()
    conn.close()
    
    return render_template('admin_services.html', services=services)

@app.route('/admin/services/add', methods=['GET', 'POST'])
@login_required
def admin_add_service():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        in_charge = request.form['in_charge']
        city = request.form['city']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO services (category, name, contact_number, address, in_charge, city) VALUES (?, ?, ?, ?, ?, ?)',
            (category, name, contact_number, address, in_charge, city)
        )
        conn.commit()
        conn.close()
        
        flash('Service added successfully', 'success')
        return redirect(url_for('admin_services'))
    
    return render_template('admin_service_form.html', service=None)

@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_service(service_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        contact_number = request.form['contact_number']
        address = request.form['address']
        in_charge = request.form['in_charge']
        city = request.form['city']
        
        cursor.execute(
            'UPDATE services SET category=?, name=?, contact_number=?, address=?, in_charge=?, city=? WHERE id=?',
            (category, name, contact_number, address, in_charge, city, service_id)
        )
        conn.commit()
        conn.close()
        
        flash('Service updated successfully', 'success')
        return redirect(url_for('admin_services'))
    
    cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = cursor.fetchone()
    conn.close()
    
    if not service:
        flash('Service not found', 'error')
        return redirect(url_for('admin_services'))
    
    return render_template('admin_service_form.html', service=service)

@app.route('/admin/services/delete/<int:service_id>')
@login_required
def admin_delete_service(service_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    conn.close()
    
    flash('Service deleted successfully', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/beneficiaries')
@login_required
def admin_beneficiaries():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.*, s.title as scheme_name, u.name as user_name, u.email as user_email
        FROM beneficiaries b 
        LEFT JOIN schemes s ON b.scheme_id = s.id 
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.registered_on DESC
    ''')
    beneficiaries = cursor.fetchall()
    conn.close()
    
    return render_template('admin_beneficiaries.html', beneficiaries=beneficiaries)

@app.route('/admin/beneficiaries/approve/<int:beneficiary_id>')
@login_required
def admin_approve_beneficiary(beneficiary_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE beneficiaries SET status = "Approved" WHERE id = ?', (beneficiary_id,))
    conn.commit()
    conn.close()
    
    flash('Beneficiary approved successfully', 'success')
    return redirect(url_for('admin_beneficiaries'))

@app.route('/admin/beneficiaries/reject/<int:beneficiary_id>')
@login_required
def admin_reject_beneficiary(beneficiary_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE beneficiaries SET status = "Rejected" WHERE id = ?', (beneficiary_id,))
    conn.commit()
    conn.close()
    
    flash('Beneficiary rejected', 'success')
    return redirect(url_for('admin_beneficiaries'))

@app.route('/admin/beneficiaries/delete/<int:beneficiary_id>')
@login_required
def admin_delete_beneficiary(beneficiary_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM beneficiaries WHERE id = ?', (beneficiary_id,))
    conn.commit()
    conn.close()
    
    flash('Beneficiary deleted successfully', 'success')
    return redirect(url_for('admin_beneficiaries'))

@app.route('/admin/beneficiaries/add', methods=['GET', 'POST'])
@login_required
def admin_add_beneficiary():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        scheme_id = request.form['scheme_id']
        status = request.form['status']
        notes = request.form['notes']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO beneficiaries (name, contact, address, scheme_id, status, notes, application_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, contact, address, scheme_id, status, notes, datetime.now()))
        conn.commit()
        conn.close()
        
        flash('Beneficiary added successfully', 'success')
        return redirect(url_for('admin_beneficiaries'))
    
    # Get schemes for dropdown
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM schemes ORDER BY title')
    schemes = cursor.fetchall()
    conn.close()
    
    return render_template('admin_beneficiary_form.html', beneficiary=None, schemes=schemes)

@app.route('/admin/beneficiaries/edit/<int:beneficiary_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_beneficiary(beneficiary_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        scheme_id = request.form['scheme_id']
        status = request.form['status']
        notes = request.form['notes']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE beneficiaries 
            SET name = ?, contact = ?, address = ?, scheme_id = ?, status = ?, notes = ?
            WHERE id = ?
        ''', (name, contact, address, scheme_id, status, notes, beneficiary_id))
        conn.commit()
        conn.close()
        
        flash('Beneficiary updated successfully', 'success')
        return redirect(url_for('admin_beneficiaries'))
    
    # Get beneficiary and schemes
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM beneficiaries WHERE id = ?', (beneficiary_id,))
    beneficiary = cursor.fetchone()
    cursor.execute('SELECT id, title FROM schemes ORDER BY title')
    schemes = cursor.fetchall()
    conn.close()
    
    if not beneficiary:
        flash('Beneficiary not found', 'error')
        return redirect(url_for('admin_beneficiaries'))
    
    return render_template('admin_beneficiary_form.html', beneficiary=beneficiary, schemes=schemes)

@app.route('/notices')
def notices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notices ORDER BY publish_date DESC')
    notices = cursor.fetchall()
    conn.close()
    
    return render_template('notices.html', notices=notices)

@app.route('/notices/<int:notice_id>')
def notice_detail(notice_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT n.*, s.title AS scheme_title FROM notices n LEFT JOIN schemes s ON n.scheme_id = s.id WHERE n.id = ?', (notice_id,))
    notice = cursor.fetchone()
    conn.close()

    if not notice:
        flash('Notice not found.', 'error')
        return redirect(url_for('notices'))

    return render_template('notice_detail.html', notice=notice)

@app.route('/search')
def search_page():
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'latest')

    conn = get_db()
    cursor = conn.cursor()

    scheme_categories = [row['department'] for row in cursor.execute('SELECT DISTINCT department FROM schemes').fetchall()]
    service_categories = [row['category'] for row in cursor.execute('SELECT DISTINCT category FROM services').fetchall()]

    scheme_results = []
    notice_results = []
    service_results = []

    if query or category:
        if search_type in ['all', 'schemes']:
            scheme_filters = []
            scheme_params = []

            if category:
                scheme_filters.append('department = ?')
                scheme_params.append(category)
            if query:
                scheme_filters.append('(title LIKE ? OR description LIKE ? OR eligibility LIKE ? OR benefits LIKE ?)')
                q_param = f'%{query}%'
                scheme_params.extend([q_param] * 4)

            scheme_sql = 'SELECT * FROM schemes'
            if scheme_filters:
                scheme_sql += ' WHERE ' + ' AND '.join(scheme_filters)

            if sort == 'relevance' and query:
                scheme_sql += ' ORDER BY (CASE WHEN title LIKE ? THEN 3 WHEN department LIKE ? THEN 2 WHEN description LIKE ? THEN 1 ELSE 0 END) DESC, published_on DESC'
                scheme_params.extend([q_param, q_param, q_param])
            else:
                scheme_sql += ' ORDER BY published_on DESC'

            cursor.execute(scheme_sql, tuple(scheme_params))
            scheme_results = cursor.fetchall()

        if search_type in ['all', 'notices']:
            notice_filters = []
            notice_params = []
            if query:
                notice_filters.append('(title LIKE ? OR description LIKE ?)')
                notice_params.extend([f'%{query}%', f'%{query}%'])

            notice_sql = 'SELECT * FROM notices'
            if notice_filters:
                notice_sql += ' WHERE ' + ' AND '.join(notice_filters)

            if sort == 'relevance' and query:
                notice_sql += ' ORDER BY (CASE WHEN title LIKE ? THEN 2 WHEN description LIKE ? THEN 1 ELSE 0 END) DESC, publish_date DESC'
                notice_params.extend([f'%{query}%', f'%{query}%'])
            else:
                notice_sql += ' ORDER BY publish_date DESC'

            cursor.execute(notice_sql, tuple(notice_params))
            notice_results = cursor.fetchall()

        if search_type in ['all', 'services']:
            service_filters = []
            service_params = []
            if category:
                service_filters.append('category = ?')
                service_params.append(category)
            if query:
                service_filters.append('(name LIKE ? OR category LIKE ? OR address LIKE ? OR in_charge LIKE ? OR city LIKE ?)')
                q_param = f'%{query}%'
                service_params.extend([q_param] * 5)

            service_sql = 'SELECT * FROM services'
            if service_filters:
                service_sql += ' WHERE ' + ' AND '.join(service_filters)

            if sort == 'relevance' and query:
                service_sql += ' ORDER BY (CASE WHEN name LIKE ? THEN 2 WHEN category LIKE ? THEN 1 ELSE 0 END) DESC'
                service_params.extend([f'%{query}%', f'%{query}%'])
            else:
                service_sql += ' ORDER BY name ASC'

            cursor.execute(service_sql, tuple(service_params))
            service_results = cursor.fetchall()

    conn.close()

    return render_template('search.html',
                           query=query,
                           search_type=search_type,
                           category=category,
                           sort=sort,
                           scheme_categories=scheme_categories,
                           service_categories=service_categories,
                           scheme_results=scheme_results,
                           notice_results=notice_results,
                           service_results=service_results)

@app.route('/schemes')
def schemes():
    category = request.args.get('category', '')
    
    location = request.args.get('location', None)
    if location is None:
        location = current_user.location if current_user.is_authenticated and current_user.location else ''
        
    sort = request.args.get('sort', 'latest')
    query = request.args.get('q', '').strip()
    
    conn = get_db()
    cursor = conn.cursor()
    
    filters = []
    params = []
    if category:
        filters.append('department = ?')
        params.append(category)
    if location:
        filters.append('(location = ? OR location = "All")')
        params.append(location)
    if query:
        filters.append('(title LIKE ? OR description LIKE ? OR eligibility LIKE ? OR benefits LIKE ?)')
        query_param = f'%{query}%'
        params.extend([query_param] * 4)

    sql = 'SELECT * FROM schemes'
    if filters:
        sql += ' WHERE ' + ' AND '.join(filters)

    if sort == 'relevance' and query:
        sql += ' ORDER BY (CASE WHEN title LIKE ? THEN 3 WHEN department LIKE ? THEN 2 WHEN description LIKE ? THEN 1 ELSE 0 END) DESC, published_on DESC'
        params.extend([query_param, query_param, query_param])
    else:
        sql += ' ORDER BY published_on DESC'

    cursor.execute(sql, tuple(params))
    schemes = cursor.fetchall()

    cursor.execute('SELECT DISTINCT location FROM schemes WHERE location IS NOT NULL AND location != "All"')
    locations = [row['location'] for row in cursor.fetchall()]

    default_locations = ['Paithan', 'Gangapur', 'Vaijapur', 'Sillod', 'Phulambri', 'Kannad', 'Khuldabad', 'Soegaon']
    all_locations = sorted(list(set(locations + default_locations)))
    conn.close()
    
    return render_template('schemes.html', schemes=schemes, selected_category=category, selected_location=location, locations=all_locations, selected_sort=sort, search_query=query, selected_scheme_default=None)

@app.route('/schemes/<int:scheme_id>')
def scheme_detail(scheme_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schemes WHERE id = ?', (scheme_id,))
    scheme = cursor.fetchone()
    conn.close()

    if not scheme:
        flash('Scheme not found.', 'error')
        return redirect(url_for('schemes'))

    return render_template('scheme_detail.html', scheme=scheme)

@app.route('/schemes/request/<int:scheme_id>', methods=['GET'])
@login_required
def request_scheme(scheme_id):
    progress = None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schemes WHERE id = ?', (scheme_id,))
    scheme = cursor.fetchone()

    if scheme:
        cursor.execute(
            'SELECT b.*, s.title as scheme_name FROM beneficiaries b LEFT JOIN schemes s ON b.scheme_id = s.id WHERE b.user_id = ? AND b.scheme_id = ?',
            (current_user.id, scheme_id)
        )
        progress = cursor.fetchone()

    conn.close()

    if not scheme:
        flash('Scheme not found.', 'error')
        return redirect(url_for('schemes'))

    return render_template('scheme_request.html', scheme=scheme, progress=progress)

@app.route('/schemes/submit', methods=['POST'])
@login_required
def submit_scheme_request():
    selected_scheme = request.form.get('selected_scheme', '').strip()
    full_name = request.form.get('full_name', '').strip()
    age = request.form.get('age', '').strip()
    dob = request.form.get('dob', '').strip()
    aadhaar = request.form.get('aadhaar', '').strip()
    email = request.form.get('email', '').strip()
    mobile = request.form.get('mobile', '').strip()
    comments = request.form.get('comments', '').strip()
    scheme_id = request.form.get('scheme_id')

    if not selected_scheme or not full_name or not mobile or not age or not dob or not aadhaar:
        flash('Please fill in all required fields (name, age, DOB, Aadhaar, mobile number).', 'error')
        return redirect(request.referrer or url_for('schemes'))

    conn = get_db()
    cursor = conn.cursor()

    actual_scheme_id = None
    if scheme_id:
        try:
            actual_scheme_id = int(scheme_id)
        except ValueError:
            actual_scheme_id = None

    if actual_scheme_id is None:
        cursor.execute('SELECT id FROM schemes WHERE title = ?', (selected_scheme,))
        found = cursor.fetchone()
        actual_scheme_id = found['id'] if found else None

    if actual_scheme_id is None:
        flash('Selected scheme was not found. Please request an existing scheme from its detail page.', 'error')
        conn.close()
        return redirect(url_for('schemes'))

    cursor.execute(
        'SELECT * FROM beneficiaries WHERE user_id = ? AND scheme_id = ?',
        (current_user.id, actual_scheme_id)
    )
    existing = cursor.fetchone()

    if existing:
        status = existing['status']
        flash(f'You already have a request for "{selected_scheme}". Current status: {status}.', 'info')
        conn.close()
        return redirect(url_for('user_dashboard'))
    else:
        cursor.execute(
            'INSERT INTO beneficiaries (user_id, name, age, scheme_id, dob, aadhaar, mobile, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (current_user.id, full_name, age, actual_scheme_id, dob, aadhaar, mobile, 'Pending')
        )
        conn.commit()
        beneficiary_id = cursor.lastrowid
        conn.close()
        
        # Redirect to confirmation page
        return redirect(url_for('scheme_confirmation', beneficiary_id=beneficiary_id))

@app.route('/schemes/confirmation/<int:beneficiary_id>')
@login_required
def scheme_confirmation(beneficiary_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch beneficiary details
    cursor.execute(
        '''SELECT b.*, s.title as scheme_name, s.benefits, s.description, s.eligibility, s.department
           FROM beneficiaries b 
           LEFT JOIN schemes s ON b.scheme_id = s.id 
           WHERE b.id = ? AND b.user_id = ?''',
        (beneficiary_id, current_user.id)
    )
    beneficiary = cursor.fetchone()
    conn.close()
    
    if not beneficiary:
        flash('Beneficiary record not found.', 'error')
        return redirect(url_for('user_dashboard'))
    
    return render_template('scheme_confirmation.html', beneficiary=beneficiary)

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user.id,))
    user = cursor.fetchone()

    # Build query for history with filters
    query = '''
        SELECT b.*, s.title AS scheme_name
        FROM beneficiaries b
        LEFT JOIN schemes s ON b.scheme_id = s.id
        WHERE b.user_id = ?
    '''
    params = [current_user.id]

    if status_filter:
        query += ' AND b.status = ?'
        params.append(status_filter)

    if date_filter:
        # Assuming date_filter is YYYY-MM-DD
        query += ' AND DATE(b.registered_on) = ?'
        params.append(date_filter)

    query += ' ORDER BY b.registered_on DESC'

    cursor.execute(query, tuple(params))
    history = cursor.fetchall()

    status_counts = {'Pending': 0, 'Approved': 0, 'Rejected': 0}
    for row in history:
        status = row['status'] or 'Pending'
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

    conn.close()
    return render_template('user_dashboard.html', user=user, history=history, status_counts=status_counts, status_filter=status_filter, date_filter=date_filter)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Settings handling can be extended here for other preferences
        location = request.form.get('location', '')
        cursor.execute('UPDATE users SET location = ? WHERE id = ?', (location, current_user.id))
        conn.commit()
        
        current_user.location = location
        flash('Preferences saved successfully!', 'success')
        return redirect(url_for('settings'))

    cursor.execute('SELECT * FROM users WHERE id = ?', (current_user.id,))
    user = cursor.fetchone()
    
    cursor.execute('SELECT DISTINCT location FROM schemes WHERE location IS NOT NULL AND location != "All"')
    locations = [row['location'] for row in cursor.fetchall()]
    default_locations = ['Paithan', 'Gangapur', 'Vaijapur', 'Sillod', 'Phulambri', 'Kannad', 'Khuldabad', 'Soegaon']
    all_locations = sorted(list(set(locations + default_locations)))
    
    conn.close()

    return render_template('settings.html', user=user, locations=all_locations)

@app.route('/services')
def services():
    category = request.args.get('category', '')
    
    location = request.args.get('location', None)
    if location is None:
        location = current_user.location if current_user.is_authenticated and current_user.location else ''
    
    conn = get_db()
    cursor = conn.cursor()
    
    filters = []
    params = []
    
    if category:
        filters.append('category = ?')
        params.append(category)
        
    if location:
        filters.append('(city = ? OR city = "All" OR city = "Sample Village")')
        params.append(location)
        
    sql = 'SELECT * FROM services'
    if filters:
        sql += ' WHERE ' + ' AND '.join(filters)
    sql += ' ORDER BY name ASC'
        
    cursor.execute(sql, tuple(params))
    services = cursor.fetchall()
    
    cursor.execute('SELECT DISTINCT city FROM services WHERE city IS NOT NULL AND city != "" AND city != "All"')
    locations = [row['city'] for row in cursor.fetchall()]
    default_locations = ['Paithan', 'Gangapur', 'Vaijapur', 'Sillod', 'Phulambri', 'Kannad', 'Khuldabad', 'Soegaon']
    all_locations = sorted(list(set(locations + default_locations)))
    
    conn.close()
    
    return render_template('services.html', services=services, selected_category=category, selected_location=location, locations=all_locations)

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
        location = request.form.get('location', 'All')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO schemes (title, description, department, eligibility, benefits, apply_link, location) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, department, eligibility, benefits, apply_link, location)
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

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        name = request.form.get('name', '')
        contact = request.form.get('contact', '')
        message = request.form.get('message', '')
        
        if not name or not message:
            return jsonify({'success': False, 'message': 'Name and message are required'})
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO feedback (name, contact, message) VALUES (?, ?, ?)',
            (name, contact, message)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Feedback submitted successfully'})
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
