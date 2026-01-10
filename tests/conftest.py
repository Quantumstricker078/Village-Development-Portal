import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path):
    # Use a temporary file-based DB so multiple connections share the same data
    app.config['TESTING'] = True
    db_file = tmp_path / "test.db"
    app.config['DATABASE'] = str(db_file)

    # Initialize the file-based DB with sample data
    init_db(app.config['DATABASE'])

    with app.test_client() as client:
        yield client
