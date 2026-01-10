import pytest
from app import app, init_db

# The test client fixture has been moved to tests/conftest.py for reuse across tests.


def test_search_endpoint_returns_results(client):
    resp = client.get('/api/search?q=Health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'results' in data
    # Expect to find the sample 'Health Insurance' scheme
    schemes = data['results'].get('schemes', [])
    assert any(s.get('title') == 'Health Insurance' for s in schemes)


def test_admin_login_flow(client):
    # Login as default admin user
    resp = client.post('/login', data={'email': 'admin@villageportal.com', 'password': 'admin123'}, follow_redirects=True)
    assert resp.status_code == 200
    # Should reach admin dashboard which contains 'Admin Dashboard'
    assert b'Admin Dashboard' in resp.data
    # Flash message should contain success
    assert b'Login successful!' in resp.data
