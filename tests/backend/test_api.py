"""
Comprehensive backend API tests.

Tests all endpoints, services, and integration points.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "src" / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestInterviewerFlow:
    """Test Interviewer flow endpoints."""
    
    def test_step1_missing_consents(self):
        """Test Step 1 fails without all consents."""
        payload = {
            "name": "Test Interviewer",
            "email": "test@example.com",
            "consent_terms": True,
            "consent_privacy": True,
            "consent_store_data": False,  # Missing this
            "consent_future_contact": True,
            "language": "en"
        }
        response = client.post("/api/interviewer/step1", json=payload)
        assert response.status_code == 400
        assert "consents" in response.json()["detail"].lower()
    
    def test_step1_success(self):
        """Test Step 1 with all consents succeeds."""
        payload = {
            "name": "Test Interviewer",
            "email": "test_interviewer@example.com",
            "phone": "+1234567890",
            "country": "Portugal",
            "company_name": "Test Company",
            "consent_terms": True,
            "consent_privacy": True,
            "consent_store_data": True,
            "consent_future_contact": True,
            "language": "en"
        }
        response = client.post("/api/interviewer/step1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "interviewer_id" in data
        assert "session_id" in data
        assert "message" in data


class TestCandidateFlow:
    """Test Candidate flow endpoints."""
    
    def test_step1_invalid_email(self):
        """Test Step 1 fails with invalid email."""
        payload = {
            "name": "Test Candidate",
            "email": "invalid-email",  # Invalid format
            "consent_terms": True,
            "consent_privacy": True,
            "consent_store_data": True,
            "consent_future_contact": True,
            "language": "en"
        }
        response = client.post("/api/candidate/step1", json=payload)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_step1_success(self):
        """Test Step 1 with valid data succeeds."""
        payload = {
            "name": "Test Candidate",
            "email": "test_candidate@example.com",
            "phone": "+1234567890",
            "country": "France",
            "consent_terms": True,
            "consent_privacy": True,
            "consent_store_data": True,
            "consent_future_contact": True,
            "language": "fr"
        }
        response = client.post("/api/candidate/step1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "candidate_id" in data
        assert "session_id" in data


class TestAdminEndpoints:
    """Test Admin endpoints."""
    
    def test_login_invalid_credentials(self):
        """Test login fails with wrong credentials."""
        payload = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = client.post("/api/admin/login", json=payload)
        assert response.status_code == 401
    
    def test_login_success(self):
        """Test login succeeds with correct credentials."""
        payload = {
            "username": "admin",
            "password": "admin123"
        }
        response = client.post("/api/admin/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint fails without token."""
        response = client.get("/api/admin/me")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_auth(self):
        """Test protected endpoint succeeds with valid token."""
        # First login
        login_response = client.post("/api/admin/login", json={
            "username": "admin",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        
        # Then access protected endpoint
        response = client.get(
            "/api/admin/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

