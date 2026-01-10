import sqlite3
import pytest
from app import app, init_db


def login(client):
    return client.post('/login', data={'email': 'admin@villageportal.com', 'password': 'admin123'}, follow_redirects=True)


def test_add_notice_requires_login(client):
    resp = client.post('/api/add_notice', data={'title': 'T1', 'description': 'D', 'valid_until': '2026-01-01'})
    # Unauthenticated should be redirected to login
    assert resp.status_code == 302
    assert '/login' in resp.headers.get('Location', '')


def test_add_notice_authenticated(client):
    login(client)
    resp = client.post('/api/add_notice', data={'title': 'T2', 'description': 'Desc', 'valid_until': '2026-01-01'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    # Verify DB contains the new notice
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM notices WHERE title = ?", ('T2',))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 1


def test_add_scheme_authenticated(client):
    login(client)
    resp = client.post('/api/add_scheme', data={
        'title': 'Test Scheme',
        'description': 'Sample',
        'department': 'Testing',
        'eligibility': 'All',
        'benefits': 'None',
        'apply_link': '#'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    # Verify DB contains the scheme
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM schemes WHERE title = ?", ('Test Scheme',))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 1


def test_add_beneficiary_authenticated_and_validation(client):
    login(client)
    # Valid beneficiary
    resp = client.post('/api/add_beneficiary', data={
        'name': 'Tester', 'age': '30', 'gender': 'Other', 'scheme_id': '1', 'mobile': '9999999999'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    # Missing required field (name)
    resp2 = client.post('/api/add_beneficiary', data={'age': '25', 'gender': 'Male', 'scheme_id': '1', 'mobile': '8888888888'})
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    # The endpoint should return success: False for missing fields
    assert data2['success'] is False


def test_search_short_query_and_no_match(client):
    # Short query (<2) returns empty results
    resp = client.get('/api/search?q=a')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['results']['schemes'] == []

    # Query with no matches
    resp2 = client.get('/api/search?q=NoSuchTermHere')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['success'] is True
    assert all(len(v) == 0 for v in data2['results'].values())
