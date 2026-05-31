import pytest

def test_register_user(client, test_db):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "id" in data["user"]
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "testuser@example.com"
    # Password should NOT be in the response
    assert "password" not in data["user"]
    assert "hashed_password" not in data["user"]

def test_register_existing_username(client, test_db):
    client.post("/api/auth/register", json={"username": "testuser_exist", "email": "first@example.com", "password": "testpassword"})
    response = client.post("/api/auth/register", json={"username": "testuser_exist", "email": "newemail@example.com", "password": "testpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "This username is already taken."

def test_login_success(client, test_db):
    client.post("/api/auth/register", json={"username": "testuser_login", "email": "testuser_login@example.com", "password": "testpassword"})
    response = client.post("/api/auth/login", json={"email": "testuser_login@example.com", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "testuser_login@example.com"

def test_login_invalid_password(client, test_db):
    client.post("/api/auth/register", json={"username": "testuser_inv", "email": "testuser_inv@example.com", "password": "testpassword"})
    response = client.post("/api/auth/login", json={"email": "testuser_inv@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_login_nonexistent_user(client, test_db):
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password"})
    assert response.status_code == 401
