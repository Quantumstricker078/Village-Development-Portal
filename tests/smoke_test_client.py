import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

with app.test_client() as c:
    r = c.get('/')
    print('GET / ->', r.status_code, 'len(body)=', len(r.data))

    r2 = c.get('/api/search?q=Health')
    print('GET /api/search?q=Health ->', r2.status_code)
    print('  JSON keys:', list(r2.get_json().keys()))

    # Login
    r3 = c.post('/login', data={'email':'admin@villageportal.com','password':'admin123'}, follow_redirects=True)
    print('POST /login ->', r3.status_code, 'admin dashboard present:', b'Admin Dashboard' in r3.data)

    # Add a notice (authenticated)
    r4 = c.post('/api/add_notice', data={'title':'SmokeTest Notice','description':'Smoke test','valid_until':'2099-12-31'})
    print('POST /api/add_notice ->', r4.status_code, r4.get_json())

    # Search for the new notice
    r5 = c.get('/api/search?q=SmokeTest')
    print('GET /api/search?q=SmokeTest ->', r5.status_code, r5.get_json())

    # Check notices page contains the added notice
    r6 = c.get('/notices')
    print('GET /notices ->', r6.status_code, 'contains SmokeTest Notice:', b'SmokeTest Notice' in r6.data)
