import uuid
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User  
from dotenv import load_dotenv
import os

load_dotenv()

# Creating a Test Database for mocking
database_url = os.getenv('database_url')  
engine = create_engine(database_url)
session_testing = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = session_testing()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_create_user(client, db_session):
    user_data = {
        "email": f"testuser_{uuid.uuid4()}@example.com",
        "password": "testpassword"
    }

    # Test: Create the user
    response = client.post("/users/", json=user_data)

    # Assert: User created successfully
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

    # Deleting after successful creation
    db_session.query(User).filter_by(email=user_data["email"]).delete()
    db_session.commit()

def test_login_for_access_token(client, db_session):
    # Arrange: Create a user
    user_data = {
        "email": f"testuser_{uuid.uuid4()}@example.com",
        "password": "testpassword"
    }
    client.post("/users/", json=user_data)

    # Act: Login to get the token
    response = client.post("/token", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })

    # Assert: Token generation
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Clean up: Delete the user after test
    db_session.query(User).filter_by(email=user_data["email"]).delete()
    db_session.commit()

def test_create_book(client, db_session):
    # Arrange: Create a unique user and login
    user_data = {
        "email": f"testuser_{uuid.uuid4()}@example.com",
        "password": "testpassword"
    }

    # First, create the user
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200

    # Login to get the token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create headers with the authorization token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Arrange: Create a book
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "published_date": "2024-01-01"
    }

    # Act: Create the book with the authorization headers
    response = client.post("/books/", json=book_data, headers=headers)

    # Assert: Check if the book was created successfully
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"

    # Clean up: Delete the user after test
    db_session.query(User).filter_by(email=user_data["email"]).delete()
    db_session.commit()
