import pytest
from conftest import test_db

# We need a fixture to get an authenticated client token
@pytest.fixture
def auth_token(client):
    # Register a user
    client.post(
        "/api/auth/register",
        json={"username": "routeuser", "email": "route@example.com", "password": "password"}
    )
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"email": "route@example.com", "password": "password"}
    )
    return response.json()["access_token"]

def test_get_history_empty(client, auth_token):
    # Fetch history for new user
    response = client.get(
        "/api/history",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 0

def test_get_history_unauthenticated(client):
    response = client.get("/api/history")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# We cannot easily test the WebSocket endpoint purely over the TestClient 
# in a synchronous test without an async loop, but we can verify that 
# normal HTTP endpoints are protected.
