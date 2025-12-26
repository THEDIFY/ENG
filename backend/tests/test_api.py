"""Tests for the API endpoints."""

import os
import pytest

# Set environment variable to use SQLite for testing before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


class TestRootEndpoints:
    """Tests for root endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_info(self, client):
        """Test API info endpoint."""
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "optimization" in data["features"]


class TestRulesAPI:
    """Tests for rules API."""

    def test_get_rules(self, client):
        """Test getting all rules."""
        response = client.get("/api/v1/rules/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "categories" in data

    def test_list_categories(self, client):
        """Test listing rule categories."""
        response = client.get("/api/v1/rules/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_category(self, client):
        """Test getting a specific category."""
        response = client.get("/api/v1/rules/categories/Safety%20Equipment")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Safety Equipment"
        assert "rules" in data

    def test_parse_rules(self, client):
        """Test parsing rules into constraints."""
        response = client.post(
            "/api/v1/rules/parse",
            json={"rule_set_version": "2024", "custom_constraints": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "constraints" in data
        assert "dimensional_constraints" in data
        assert "safety_requirements" in data

    def test_dimensional_defaults(self, client):
        """Test getting dimensional defaults."""
        response = client.get("/api/v1/rules/dimensional-defaults")
        assert response.status_code == 200
        data = response.json()
        assert "max_width_mm" in data
        assert data["max_width_mm"] == 2438
