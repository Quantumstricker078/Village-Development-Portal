"""
Manual testing script for comprehensive web portal testing
Tests all features including:
- Navigation and UI
- Authentication
- Admin dashboard
- CRUD operations
- Search functionality
- Form submissions
"""

import urllib.request
import urllib.parse
import http.cookiejar
import json
from time import sleep

BASE_URL = "http://127.0.0.1:5000"

# Setup cookie handling
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"✓ {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"✗ {test_name}: {error}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{'='*60}")
        print(f"Test Summary: {len(self.passed)}/{total} passed")
        print(f"{'='*60}")
        if self.failed:
            print("\nFailed Tests:")
            for test, error in self.failed:
                print(f"  - {test}: {error}")
        return len(self.failed) == 0

results = TestResults()

def test_homepage():
    """Test if homepage loads"""
    try:
        resp = opener.open(f"{BASE_URL}/")
        if resp.status == 200:
            results.add_pass("Homepage loads")
        else:
            results.add_fail("Homepage loads", f"Status code {resp.status}")
    except Exception as e:
        results.add_fail("Homepage loads", str(e))

def test_navigation():
    """Test all navigation links"""
    links = [
        ("/", "Home"),
        ("/about", "About"),
        ("/contact", "Contact"),
        ("/documentation", "Documentation"),
        ("/acknowledgements", "Acknowledgements"),
        ("/notices", "Notices"),
        ("/schemes", "Schemes"),
        ("/services", "Services"),
    ]
    
    for url, name in links:
        try:
            resp = opener.open(f"{BASE_URL}{url}")
            if resp.status == 200:
                results.add_pass(f"Navigation: {name} page")
            else:
                results.add_fail(f"Navigation: {name} page", f"Status {resp.status}")
        except Exception as e:
            results.add_fail(f"Navigation: {name} page", str(e))

def test_login_page():
    """Test if login page loads"""
    try:
        resp = opener.open(f"{BASE_URL}/login")
        content = resp.read().decode('utf-8')
        if resp.status == 200 and 'login' in content.lower():
            results.add_pass("Login page loads")
        else:
            results.add_fail("Login page loads", "Page not found or incorrect content")
    except Exception as e:
        results.add_fail("Login page loads", str(e))

def test_invalid_login():
    """Test login with wrong credentials"""
    try:
        data = urllib.parse.urlencode({'email': 'wrong@test.com', 'password': 'wrongpass'}).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/login", data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Invalid login rejected")
        else:
            results.add_fail("Invalid login rejected", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Invalid login rejected", str(e))

def test_admin_login():
    """Test admin login"""
    try:
        data = urllib.parse.urlencode({'email': 'admin@villageportal.com', 'password': 'admin123'}).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/login", data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Admin login successful")
            return True
        else:
            results.add_fail("Admin login successful", f"Status {resp.status}")
            return False
    except Exception as e:
        results.add_fail("Admin login successful", str(e))
        return False

def test_admin_dashboard():
    """Test admin dashboard access"""
    try:
        resp = opener.open(f"{BASE_URL}/admin/dashboard")
        content = resp.read().decode('utf-8')
        if resp.status == 200 and 'dashboard' in content.lower():
            results.add_pass("Admin dashboard accessible")
        else:
            results.add_fail("Admin dashboard accessible", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Admin dashboard accessible", str(e))

def test_dashboard_link_in_navbar():
    """Test if dashboard link appears in navbar after login"""
    try:
        resp = opener.open(f"{BASE_URL}/")
        content = resp.read().decode('utf-8')
        if 'dashboard' in content.lower() and '/admin/dashboard' in content:
            results.add_pass("Dashboard link in navbar")
        else:
            results.add_fail("Dashboard link in navbar", "Link not found in navbar")
    except Exception as e:
        results.add_fail("Dashboard link in navbar", str(e))

def test_add_notice():
    """Test adding a new notice"""
    try:
        notice_data = urllib.parse.urlencode({
            'title': 'Test Notice',
            'description': 'This is a test notice',
            'valid_until': '2026-12-31'
        }).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/api/add_notice", notice_data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Add notice successfully")
        else:
            results.add_fail("Add notice successfully", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Add notice successfully", str(e))

def test_add_scheme():
    """Test adding a new scheme"""
    try:
        scheme_data = urllib.parse.urlencode({
            'title': 'Test Scheme',
            'description': 'Test scheme description',
            'department': 'Test Dept',
            'eligibility': 'Test Eligibility',
            'benefits': 'Test Benefits',
            'apply_link': '#'
        }).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/api/add_scheme", scheme_data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Add scheme successfully")
        else:
            results.add_fail("Add scheme successfully", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Add scheme successfully", str(e))

def test_add_beneficiary():
    """Test adding a beneficiary"""
    try:
        beneficiary_data = urllib.parse.urlencode({
            'name': 'Test Beneficiary',
            'age': '30',
            'gender': 'Male',
            'scheme_id': '1',
            'mobile': '9876543210'
        }).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/api/add_beneficiary", beneficiary_data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Add beneficiary successfully")
        else:
            results.add_fail("Add beneficiary successfully", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Add beneficiary successfully", str(e))

def test_search():
    """Test search functionality"""
    try:
        resp = opener.open(f"{BASE_URL}/api/search?q=health")
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Search functionality works")
        else:
            results.add_fail("Search functionality works", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Search functionality works", str(e))

def test_contact_form():
    """Test contact form submission"""
    try:
        form_data = urllib.parse.urlencode({
            'name': 'Test User',
            'contact': '9876543210',
            'message': 'This is a test message'
        }).encode('utf-8')
        resp = opener.open(f"{BASE_URL}/api/submit_feedback", form_data)
        content = resp.read().decode('utf-8')
        if resp.status == 200:
            results.add_pass("Contact form submission")
        else:
            results.add_fail("Contact form submission", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Contact form submission", str(e))

def test_logout():
    """Test logout functionality"""
    try:
        resp = opener.open(f"{BASE_URL}/logout")
        if resp.status == 200 or resp.status == 302:
            results.add_pass("Logout successfully")
        else:
            results.add_fail("Logout successfully", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Logout successfully", str(e))

def test_unauthenticated_dashboard_access():
    """Test that unauthenticated users can't access admin dashboard"""
    try:
        resp = opener.open(f"{BASE_URL}/admin/dashboard")
        if resp.status == 302 or resp.status == 301:
            results.add_pass("Unauthenticated dashboard access blocked")
        else:
            results.add_fail("Unauthenticated dashboard access blocked", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Unauthenticated dashboard access blocked", str(e))

def test_register_page():
    """Test if register page loads"""
    try:
        resp = opener.open(f"{BASE_URL}/register")
        if resp.status == 200:
            results.add_pass("Register page loads")
        else:
            results.add_fail("Register page loads", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Register page loads", str(e))

def test_beneficiaries_page():
    """Test beneficiaries page after admin login"""
    try:
        resp = opener.open(f"{BASE_URL}/beneficiaries")
        if resp.status == 200:
            results.add_pass("Beneficiaries page loads")
        else:
            results.add_fail("Beneficiaries page loads", f"Status {resp.status}")
    except Exception as e:
        results.add_fail("Beneficiaries page loads", str(e))

if __name__ == '__main__':
    print("🧪 Starting Comprehensive Web Portal Tests...\n")
    
    # Public pages
    print("Testing Public Pages:")
    test_homepage()
    test_navigation()
    test_login_page()
    test_register_page()
    
    print("\nTesting Authentication:")
    test_invalid_login()
    is_logged_in = test_admin_login()
    
    if is_logged_in:
        print("\nTesting Admin Features:")
        test_admin_dashboard()
        test_dashboard_link_in_navbar()
        test_beneficiaries_page()
        
        print("\nTesting Admin Operations:")
        test_add_notice()
        test_add_scheme()
        test_add_beneficiary()
        
    print("\nTesting General Features:")
    test_search()
    test_contact_form()
    test_unauthenticated_dashboard_access()
    
    if is_logged_in:
        print("\nTesting Logout:")
        test_logout()
    
    # Print summary
    success = results.summary()
    exit(0 if success else 1)
