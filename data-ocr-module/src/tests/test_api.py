"""
Tests for FastAPI endpoints.

Tests cover:
- GET /health
- POST /analyze-text with valid text
- POST /analyze-text with empty text
- Response schema validation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ── Health check ───────────────────────────────────────────

def test_health(client):
    """GET /health should return status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ── Analyze text endpoint ─────────────────────────────────

def test_analyze_text_termination(client):
    """POST /analyze-text with termination clause text."""
    response = client.post("/analyze-text", json={
        "contract_text": (
            "Either party may terminate this agreement upon thirty days prior "
            "written notice to the other party. In the event of a material breach, "
            "the non-breaching party may terminate this agreement immediately."
        )
    })
    assert response.status_code == 200
    data = response.json()

    # Schema validation
    assert "clause" in data
    assert "confidence" in data
    assert "risk_score" in data
    assert "risk_level" in data
    assert isinstance(data["clause"], str)
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["risk_score"], int)
    assert data["risk_level"] in ("Low", "Medium", "High")
    assert 0.0 <= data["confidence"] <= 100.0
    assert 0 <= data["risk_score"] <= 100


def test_analyze_text_confidentiality(client):
    """POST /analyze-text with confidentiality clause text."""
    response = client.post("/analyze-text", json={
        "contract_text": (
            "The receiving party shall not disclose any confidential information "
            "to any third party without the prior written consent of the disclosing "
            "party. All proprietary data shall remain strictly confidential."
        )
    })
    assert response.status_code == 200
    data = response.json()
    assert data["clause"] == "Confidentiality"
    assert data["confidence"] > 20.0


def test_analyze_text_high_risk(client):
    """POST /analyze-text with high-risk text should return elevated score."""
    response = client.post("/analyze-text", json={
        "contract_text": (
            "The Provider shall have unlimited liability for all consequential "
            "damages without any cap. The Provider irrevocably waives all rights "
            "and agrees to sole discretion of the other party."
        )
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] > 10


def test_analyze_text_empty(client):
    """POST /analyze-text with empty text should return 400."""
    response = client.post("/analyze-text", json={"contract_text": ""})
    assert response.status_code == 400


def test_analyze_text_missing_field(client):
    """POST /analyze-text with missing field should return 422."""
    response = client.post("/analyze-text", json={})
    assert response.status_code == 422
