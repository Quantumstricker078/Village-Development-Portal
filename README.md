# 🌱 Village Development Information Portal

> A comprehensive web-based information system designed to **digitize village-level governance and services**, featuring complete CRUD operations for government schemes, local services, beneficiary management, and community notices. Built as part of the **BCA curriculum**.

---

## 📌 Project Snapshot

🎓 **Course:** Bachelor of Computer Applications (BCA)  
🛠️ **Type:** Full-Stack Academic Web Application  
🌍 **Domain:** E-Governance / Rural Development  
⚙️ **Stack:** Flask • SQLite • HTML5 • CSS3 • Bootstrap 5 • JavaScript  
📊 **Region Focus:** Marathwada Region (Multiple Talukas - Paithan, Gangapur, Vaijapur, Sillod, Phulambri, Kannad, Khuldabad, Soegaon)  

---

## 🌟 Why This Project?

Many villages still rely on **manual notice boards, paper records, and word-of-mouth communication**, which leads to:
- ❌ Poor awareness of government schemes  
- ❌ Inefficient and scattered service access  
- ❌ Manual errors, delays, and inconsistencies  
- ❌ Lack of beneficiary tracking  

✅ This portal solves that by providing a **unified digital platform** for:
- Transparent scheme information
- Real-time notices & announcements
- Service location discovery
- Beneficiary registration & approval tracking

---

## 🎯 Core Objectives

1. **Centralize** village-level governance information  
2. **Improve** transparency and accessibility for all citizens  
3. **Digitally manage** beneficiary registrations with status tracking  
4. **Reduce** manual workload on administrators  
5. **Enable** data-driven decision making at village level  
6. **Promote** digital inclusion in rural communities  

---

## 👥 System Users & Roles

### 🧑 Regular Users (Villagers)
- **Browse & Explore:** View all government schemes with full details
- **Search:** Find schemes by keywords, departments, location
- **Apply:** Submit beneficiary registration requests for schemes
- **Track:** Monitor application status (Pending/Approved/Rejected)
- **Discover:** Find local services with contact information
- **Stay Informed:** Read village notices and announcements
- **Provide Feedback:** Submit suggestions and contact messages

### 👨‍💼 Admin Users
- **Authenticate:** Secure login with hashed passwords
- **Manage Schemes:** Create, edit, delete government schemes
- **Manage Notices:** Post, update, remove village announcements
- **Manage Services:** Maintain database of local services and contacts
- **Manage Beneficiaries:** Review, approve, or reject applications
- **View Dashboard:** Monitor portal statistics and metrics
- **Settings:** Update profile information

---

## ⭐ Key Features & Functionality

### 📋 **Government Schemes Management**
- Browse 15+ active schemes across departments (Agriculture, Education, Health, Social Welfare)
- Location-specific schemes by taluka (Paithan, Gangapur, Vaijapur, Sillod, Phulambri, Kannad, Khuldabad, Soegaon)
- Detailed information: Title, Description, Eligibility, Benefits, Department, Apply Link
- Scheme request/application submission
- Search by keywords and departments

### 🏛️ **Local Services Directory**
- 16+ services across categories: Health, Education, Banking, Police, Agriculture
- Complete contact information: Phone, Address, In-Charge Officer
- Services organized by location/city
- Easy browsing and discovery
- Admin management with add/edit/delete capabilities

### 📢 **Village Notices & Announcements**
- Real-time notice postings with validity dates
- Important announcements for water supply, health camps, meetings
- Notice linking to related schemes
- Search and filter by date
- Admin publishing and management

### 👥 **Beneficiary Management System**
- User registration and scheme application tracking
- Beneficiary data: Name, Age, Gender, DOB, Aadhaar, Mobile, Status
- Application status workflow: Pending → Approved/Rejected
- Admin review and approval interface
- Confirmation page after registration
- View registered beneficiaries

### 🔍 **Advanced Search & Discovery**
- Unified search across schemes, services, and notices
- Filter by keywords, departments, locations
- Real-time search results
- Search history and suggestions

### 📊 **Admin Dashboard**
- Statistics cards showing counts of schemes, beneficiaries, notices
- Quick access to management sections
- Notifications panel
- User-friendly management interface
- All admin operations (CRUD) in one place

### 🔐 **Authentication & Security**
- User registration with email and password
- Admin login with secure authentication
- Password hashing using werkzeug
- Forgot password recovery functionality
- Session-based user tracking
- Role-based access control (Admin vs User)

### 👤 **User Dashboard**
- Personal dashboard for each user
- View submitted applications and their status
- Beneficiary information summary
- Profile settings and updates
- Application history

### 🎨 **User Interface & Experience**
- Responsive Bootstrap 5 design (mobile, tablet, desktop)
- Clean, modern navigation
- Color-coded statistics cards
- Icon-enhanced UI with Font Awesome
- Smooth transitions and hover effects
- Accessible form validation
- Alert notifications for user actions

### 📱 **Additional Features**
- About page with project overview
- Contact form with feedback submission
- Documentation & help section
- Acknowledgements page
- Settings page for user profile updates
- Confirmation pages after successful submissions

---

## 🗄️ Database Design

### **Entities & Tables**

#### **Users Table**
- `id` - Primary Key
- `name` - Full Name
- `email` - Email (Unique)
- `password_hash` - Hashed Password
- `role` - User Role (admin/user)
- `location` - User Location/City
- `created_at` - Registration Timestamp

#### **Schemes Table**
- `id` - Primary Key
- `title` - Scheme Name
- `description` - Full Description
- `department` - Government Department
- `eligibility` - Eligibility Criteria
- `benefits` - Scheme Benefits
- `apply_link` - External Application Link
- `location` - Taluka/Region Specific
- `published_on` - Publication Date

#### **Services Table**
- `id` - Primary Key
- `category` - Service Category (Health, Banking, etc.)
- `name` - Service Name
- `contact_number` - Phone Number
- `address` - Physical Address
- `in_charge` - Officer Name
- `city` - Location/City

#### **Notices Table**
- `id` - Primary Key
- `title` - Notice Title
- `description` - Notice Content
- `scheme_id` - Related Scheme (Foreign Key)
- `publish_date` - Publication Date
- `valid_until` - Validity Date
- `attachment_url` - Document Link
- `created_by` - Admin User ID

#### **Beneficiaries Table**
- `id` - Primary Key
- `user_id` - Related User (Foreign Key)
- `name` - Full Name
- `age` - Age
- `gender` - Gender
- `dob` - Date of Birth
- `aadhaar` - Aadhaar Number
- `scheme_id` - Applied Scheme (Foreign Key)
- `mobile` - Contact Number
- `status` - Status (Pending/Approved/Rejected)
- `registered_on` - Registration Date

#### **Feedback Table**
- `id` - Primary Key
- `name` - Submitter Name
- `contact` - Contact Information
- `message` - Feedback Message
- `submitted_on` - Submission Date
- `status` - Status (New/Read)

#### **Notifications Table**
- `id` - Primary Key
- `user_id` - Related User
- `type` - Notification Type
- `title` - Notification Title
- `message` - Notification Message
- `related_id` - Related Entity ID
- `is_read` - Read Status
- `created_at` - Creation Date

---

## 🛠️ Technology Stack

### 🎨 **Frontend Technologies**
- **HTML5** - Semantic markup
- **CSS3** - Styling and animations
- **Bootstrap 5** - Responsive grid system and components
- **JavaScript** - Client-side interactivity
- **Font Awesome 6** - Icon library
- **jQuery** - DOM manipulation (via Bootstrap)

### ⚙️ **Backend Technologies**
- **Python 3.x** - Core programming language
- **Flask** - Web framework (routing, templates, sessions)
- **Flask-Login** - User authentication and session management
- **Werkzeug** - Security utilities (password hashing, WSGI)
- **SQLite3** - Lightweight database
- **Jinja2** - Template engine

### 🗄️ **Database**
- **SQLite3** - File-based relational database
- **PRAGMA statements** - Database optimization
- **Unique Indexes** - Data integrity and deduplication

### 🧰 **Development Tools**
- **VS Code** - Code editor
- **Git** - Version control
- **GitHub** - Repository hosting
- **Python Virtual Environment** - Dependency isolation

---

## 🔄 Application Flow & Architecture

### **System Architecture**
```
┌─────────────────────────────────────────────┐
│           Web Browser / Client              │
│  (HTML5, CSS3, JavaScript, Bootstrap)       │
└──────────────────┬──────────────────────────┘
                   │ HTTP/HTTPS
                   ▼
┌─────────────────────────────────────────────┐
│        Flask Web Server (Python)            │
│ • Route Handlers (@app.route decorators)   │
│ • Authentication (Flask-Login)              │
│ • Template Rendering (Jinja2)              │
│ • Request/Response Processing               │
└──────────────────┬──────────────────────────┘
                   │ SQL Queries
                   ▼
┌─────────────────────────────────────────────┐
│         SQLite3 Database                    │
│ • Users, Schemes, Services                  │
│ • Notices, Beneficiaries, Feedback          │
│ • Notifications (persistent storage)        │
└─────────────────────────────────────────────┘
```

### **User Flow - Regular User**
1. **Register** → Create account
2. **Login** → Authenticate user
3. **Browse** → View schemes/services/notices
4. **Search** → Find relevant information
5. **Apply** → Submit beneficiary request for scheme
6. **Receive Confirmation** → Application submitted
7. **Track Status** → View application status in dashboard
8. **Logout** → End session

### **User Flow - Admin**
1. **Login** → Admin authentication
2. **Dashboard** → View statistics and notifications
3. **Manage Schemes** → Create/Edit/Delete schemes
4. **Manage Notices** → Post/Update/Remove announcements
5. **Manage Services** → Maintain service directory
6. **Manage Beneficiaries** → Review and approve applications
7. **Logout** → End session

---

## 📂 File Structure

```
Field Project/Codes/
├── app.py                          # Main Flask application (45+ routes)
├── database.db                     # SQLite database file
├── README.md                       # This file
├── requirements.txt                # Python dependencies
│
├── templates/                      # HTML Templates (Jinja2)
│   ├── base.html                   # Base template with navigation
│   ├── index.html                  # Home/Dashboard page
│   ├── login.html                  # Login form
│   ├── register.html               # User registration
│   ├── forgot_password.html        # Password recovery
│   ├── profile/settings.html       # User settings/profile
│   ├── user_dashboard.html         # User dashboard
│   │
│   ├── schemes.html                # Schemes listing page
│   ├── scheme_detail.html          # Scheme details page
│   ├── scheme_request.html         # Apply for scheme form
│   ├── scheme_confirmation.html    # Application confirmation
│   │
│   ├── services.html               # Services directory
│   ├── notices.html                # Notices listing
│   ├── notice_detail.html          # Notice detail page
│   ├── search.html                 # Search results page
│   │
│   ├── beneficiaries.html          # Beneficiaries list (user view)
│   ├── admin_dashboard.html        # Admin dashboard
│   │
│   ├── admin_schemes.html          # Schemes management
│   ├── admin_scheme_form.html      # Add/Edit scheme form
│   │
│   ├── admin_notices.html          # Notices management
│   ├── admin_notice_form.html      # Add/Edit notice form
│   │
│   ├── admin_services.html         # Services management
│   ├── admin_service_form.html     # Add/Edit service form
│   │
│   ├── admin_beneficiaries.html    # Beneficiaries approval
│   ├── admin_beneficiary_form.html # Add/Edit beneficiary form
│   │
│   ├── about.html                  # About page
│   ├── contact.html                # Contact/Feedback form
│   ├── acknowledgements.html       # Credits and acknowledgements
│   ├── documentation.html          # Help & documentation
│   └── style.css                   # Custom CSS styles
│
├── tests/                          # Testing files
│   ├── test_app.py                 # Application tests
│   ├── test_api_endpoints.py       # API endpoint tests
│   ├── smoke_test_client.py        # Smoke tests
│   ├── manual_test.py              # Manual testing scripts
│   └── conftest.py                 # Pytest configuration
│
└── Documentation files/             # Project documentation
    ├── START_HERE.md
    ├── DOCUMENTATION_INDEX.md
    ├── DOCUMENTATION_QUICKSTART.md
    ├── TECHNICAL_DOCUMENTATION.md
    └── [Various completion reports]
```

---

## 🔐 Security Features

### **Authentication & Authorization**
- ✅ User registration with validation
- ✅ Secure password hashing (werkzeug.security)
- ✅ Session-based authentication (Flask-Login)
- ✅ Role-based access control (Admin/User)
- ✅ Admin-only dashboard routes
- ✅ Protected form submissions

### **Data Protection**
- ✅ Parameterized SQL queries (prevents SQL injection)
- ✅ Input validation on forms
- ✅ CSRF protection via Flask sessions
- ✅ Unique indexes on critical fields
- ✅ Password recovery mechanism
- ✅ Hashed password storage

### **Best Practices**
- ✅ Flask secret key configuration
- ✅ No hardcoded credentials in frontend
- ✅ Secure cookie handling
- ✅ Database connection pooling
- ✅ Error handling without exposing internals

---

## ⚙️ Installation & Setup

### 📋 **Prerequisites**
- Python 3.7 or higher
- pip (Python package manager)
- Git
- A text editor or IDE (VS Code recommended)

### 📥 **Step 1: Clone the Repository**
```bash
git clone https://github.com/your-username/Village-Development-Portal.git
cd "Field Project/Codes"
```

### 📦 **Step 2: Create Virtual Environment**
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 📥 **Step 3: Install Dependencies**
```bash
pip install Flask Flask-Login werkzeug
```

### ▶️ **Step 4: Run the Application**
```bash
python app.py
```

### 🌐 **Step 5: Access in Browser**
```
http://localhost:5000
```

### 🔑 **Default Admin Credentials**
- **Email:** `admin@villageportal.com`
- **Password:** `admin123`

⚠️ **Security Tip:** Change admin password immediately after first login!

---

## 📖 API Endpoints & Routes

### **Public Routes (No Login Required)**
- `GET /` - Home page (redirects to login if not authenticated)
- `GET /about` - About page
- `GET /contact` - Contact form
- `GET /acknowledgements` - Credits page
- `GET /documentation` - Help documentation
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Create new user
- `GET /forgot-password` - Password recovery
- `POST /forgot-password` - Process password reset

### **User Routes (Login Required)**
- `GET /` - Dashboard
- `GET /schemes` - View all schemes
- `GET /schemes/<id>` - Scheme details
- `GET /schemes/request/<id>` - Apply for scheme
- `POST /schemes/submit` - Submit beneficiary registration
- `GET /schemes/confirmation/<id>` - Confirmation page
- `GET /services` - View local services
- `GET /notices` - View notices
- `GET /notices/<id>` - Notice details
- `GET /beneficiaries` - View beneficiaries
- `GET /user/dashboard` - User dashboard
- `GET /settings` - User settings
- `POST /settings` - Update profile
- `GET /search` - Search functionality
- `GET /logout` - Logout user

### **Admin Routes (Admin Login Required)**
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/schemes` - Manage schemes
- `GET /admin/schemes/add` - Add scheme form
- `POST /admin/schemes/add` - Create scheme
- `GET /admin/schemes/edit/<id>` - Edit scheme
- `POST /admin/schemes/edit/<id>` - Update scheme
- `GET /admin/schemes/delete/<id>` - Delete scheme
- `GET /admin/notices` - Manage notices
- `GET /admin/notices/add` - Add notice form
- `POST /admin/notices/add` - Create notice
- `GET /admin/notices/edit/<id>` - Edit notice
- `POST /admin/notices/edit/<id>` - Update notice
- `GET /admin/notices/delete/<id>` - Delete notice
- `GET /admin/services` - Manage services
- `GET /admin/services/add` - Add service form
- `POST /admin/services/add` - Create service
- `GET /admin/services/edit/<id>` - Edit service
- `POST /admin/services/edit/<id>` - Update service
- `GET /admin/services/delete/<id>` - Delete service
- `GET /admin/beneficiaries` - Manage beneficiaries
- `GET /admin/beneficiaries/add` - Add beneficiary
- `POST /admin/beneficiaries/add` - Create beneficiary
- `GET /admin/beneficiaries/edit/<id>` - Edit beneficiary
- `POST /admin/beneficiaries/edit/<id>` - Update beneficiary
- `GET /admin/beneficiaries/approve/<id>` - Approve application
- `GET /admin/beneficiaries/reject/<id>` - Reject application
- `GET /admin/beneficiaries/delete/<id>` - Delete beneficiary

### **API Endpoints (AJAX/JSON)**
- `POST /api/search` - Search across content
- `POST /api/add_notice` - Add notice (AJAX)
- `POST /api/add_scheme` - Add scheme (AJAX)
- `POST /api/add_beneficiary` - Add beneficiary (AJAX)
- `POST /api/submit_feedback` - Submit feedback

---

## 🧪 Testing

### **Manual Testing Covered**
✅ User Registration and Login
✅ Scheme Browsing and Search
✅ Beneficiary Application Process
✅ Admin CRUD Operations (Schemes, Services, Notices)
✅ Beneficiary Approval Workflow
✅ Form Validation
✅ Responsive Design (Mobile, Tablet, Desktop)
✅ Navigation and UI Interactions

### **Test Files Available**
- `tests/test_app.py` - Main application tests
- `tests/test_api_endpoints.py` - API endpoint validation
- `tests/smoke_test_client.py` - Quick smoke tests
- `tests/manual_test.py` - Manual testing scripts
- `tests/conftest.py` - Pytest configuration

### **Running Tests**
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v tests/
```

---

## ⚠️ Known Limitations

1. **Database:** SQLite (file-based, not suitable for production)
2. **Real-time:** No real-time notifications or updates
3. **Scalability:** Limited to single-server deployment
4. **Roles:** Single admin role (no role hierarchy)
5. **Media:** Limited file upload capabilities
6. **Internationalization:** English language only
7. **Analytics:** No built-in analytics or reporting
8. **Performance:** No caching or optimization for large datasets

---

## 🚀 Future Enhancement Roadmap

### **Phase 1: Mobile & Accessibility**
- 📱 Native mobile app (iOS/Android)
- ♿ WCAG accessibility compliance
- 🌐 Multi-language support (Hindi, Marathi, etc.)

### **Phase 2: Communication & Notifications**
- 📧 Email notifications for scheme updates
- 📱 SMS alerts for beneficiary status changes
- 🔔 Push notifications
- 📮 In-app messaging system

### **Phase 3: Advanced Features**
- 📊 Analytics dashboard with charts
- 📈 Beneficiary statistics and reports
- 🎯 Scheme performance metrics
- 📑 Document management system
- 🗺️ Geo-location based services
- 💬 Community forum/comments

### **Phase 4: Infrastructure & Scale**
- ☁️ Cloud deployment (AWS/Azure/GCP)
- 🗄️ PostgreSQL/MySQL migration
- 🔄 Load balancing
- 🔐 OAuth/SSO integration
- 🌐 Multi-instance deployment
- 📊 Advanced caching (Redis)

### **Phase 5: Enterprise Features**
- 👥 Multiple admin roles with permissions
- 📋 Workflow automation
- 🔍 Advanced search with filters
- 📅 Event scheduling
- 💼 Budget tracking
- 🎓 Training modules
- 📱 Offline mode capability

---

## 📊 Sample Data Included

### **Pre-loaded Schemes (15+)**
- Paithan Godavari Irrigation Grant
- Paithani Saree Weavers Subsidy
- Gangapur Sugar Cane Harvester Aid
- Vaijapur Onion Storage Subsidy
- Vaijapur Rural Tech Education
- Sillod Maize Crop Insurance
- Phulambri Dairy Development Grant
- Phulambri Women SHG Fund
- Kannad Tribal Education Scholarship
- Kannad Solar Pump Yojana
- Khuldabad Heritage Tourism Grant
- Khuldabad Fruit Orchard Subsidy
- Soegaon Cotton Seed Aid
- Soegaon Girl Child Education
- Marathwada Universal Health Cover

### **Pre-loaded Services (16+)**
Services across categories: Health, Banking, Agriculture, Education, Police
Locations: Paithan, Gangapur, Vaijapur, Sillod, Phulambri, Kannad, Khuldabad, Soegaon

### **Sample Beneficiaries (5+)**
Pre-registered with various approval statuses (Pending/Approved)

---

## 🔁 Version Control

- **Repository:** GitHub
- **Branch Strategy:** Main branch for stable code
- **Commit History:** Tracked with descriptive messages
- **Documentation:** Updated with code changes

---

## 👨‍💻 Development Notes

### **Code Organization**
- Single-file Flask application (app.py) for simplicity
- Modular HTML templates with Jinja2 inheritance
- Separation of concerns: Routes, Templates, Database
- Clean CSS with Bootstrap framework

### **Database Queries**
- Parameterized queries for security
- Connection pooling in development
- Unique constraints to prevent duplicates
- PRAGMA statements for optimization

### **Frontend**
- Responsive Bootstrap 5 grid
- Icon-enhanced UI with Font Awesome
- Form validation with HTML5 attributes
- Client-side and server-side validation

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap 5 Guide](https://getbootstrap.com/docs/5.0/)
- [SQLite Tutorial](https://www.sqlite.org/docs.html)
- [Flask-Login Guide](https://flask-login.readthedocs.io/)

---

## 📝 License

This project is created as part of the Bachelor of Computer Applications curriculum. Use for educational purposes.

---

## ✨ Contributors

- **Developer:** [Your Name/Team]
- **Institution:** [College Name]
- **Year:** 2024-2026

---

## 📧 Contact & Support

For questions, feedback, or issues:
- **Contact Form:** Available at `/contact` route
- **Email:** [Your Email]
- **Repository:** [GitHub Link]

---

**Last Updated:** April 28, 2026
**Status:** ✅ Feature Complete & Tested

    GitHub for code hosting

    Commit-based change tracking

🎓 Academic Declaration

This project is developed strictly for academic purposes as part of the BCA curriculum, demonstrating practical application of web development concepts.
✅ Conclusion

The Village Development Information Portal is a step toward digital village governance, offering a simple, scalable, and transparent solution for rural information management.

⭐ If you find this project useful, consider starring the repository!