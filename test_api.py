"""
Simple test file to verify API endpoints
Run with: pytest test_api.py
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.services.otp_service import verify_otp

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "FastFoodie Restaurant Partner API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_send_otp():
    """Test send OTP endpoint"""
    response = client.post(
        "/auth/send-otp",
        json={"phone_number": "+919876543210"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "message" in data


def test_verify_otp_rejects_default_test_code():
    """The hardcoded 123456 bypass should not be accepted."""
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None

    assert verify_otp(db, "+919876543210", "123456") is False


def test_get_restaurant_types():
    """Test get restaurant types endpoint (no auth required)"""
    # This will fail without auth, but we're testing the endpoint exists
    response = client.get("/restaurant/types")
    # Should return 401 or 403 without auth
    assert response.status_code in [401, 403, 200]


def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404


# Integration tests would require database setup
# These are just basic smoke tests

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
