"""Security tests."""
import pytest
from fastapi import status


def test_security_headers(client):
    """Test that security headers are present."""
    response = client.get("/health")
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"


def test_cors_headers(client):
    """Test CORS headers."""
    response = client.options(
        "/api/v1/ships",
        headers={"Origin": "http://localhost:5173"}
    )
    # CORS middleware should handle this
    assert response.status_code in [200, 204]


def test_rate_limiting(client):
    """Test rate limiting."""
    # Make many requests quickly
    responses = []
    for _ in range(150):  # More than the limit
        response = client.get("/api/v1/ships")
        responses.append(response.status_code)
    
    # Should have some 429 responses
    assert status.HTTP_429_TOO_MANY_REQUESTS in responses


def test_input_sanitization(client):
    """Test input sanitization."""
    # Try XSS attempt
    response = client.get("/api/v1/ships?limit=<script>alert('xss')</script>")
    # Should not crash, should handle gracefully
    assert response.status_code in [200, 400, 422]


def test_sql_injection_protection(client):
    """Test SQL injection protection."""
    # Try SQL injection in query param
    response = client.get("/api/v1/ships?limit=1; DROP TABLE ships;--")
    # Should be handled by Pydantic validation or sanitization
    assert response.status_code in [200, 400, 422]
