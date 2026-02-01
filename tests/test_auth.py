"""Authentication tests."""
import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "roles": ["viewer"]
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "newuser"


def test_register_duplicate_user(client):
    """Test duplicate user registration fails."""
    # Register first time
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate",
            "email": "duplicate@example.com",
            "password": "pass123",
        }
    )
    
    # Try to register again
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate",
            "email": "duplicate@example.com",
            "password": "pass123",
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client):
    """Test successful login."""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "pass123",
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "pass123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    """Test login with wrong password."""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "correctpass",
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass", "password": "wrongpass"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(auth_headers, client):
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_get_current_user_unauthorized(client):
    """Test getting user info without auth."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
