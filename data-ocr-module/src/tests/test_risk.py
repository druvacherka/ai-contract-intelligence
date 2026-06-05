"""
Tests for the Risk Scoring Engine (RiskEngine).

Tests cover:
- Risk score range validation (0–100)
- Risk level mapping (Low / Medium / High)
- High-risk text detection
- Low-risk text detection
- full_analysis() integration schema
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from src.nlp.risk_engine import RiskEngine
from src.nlp.nlp_engine import NLPEngine


@pytest.fixture(scope="module")
def engine():
    nlp = NLPEngine(use_transformer=False)
    return RiskEngine(nlp_engine=nlp)


# ── Score range ──────────────────────────────────────────

def test_risk_score_range(engine):
    """Risk score must be an int between 0 and 100."""
    result = engine.analyze("The agreement shall terminate upon notice.", "Termination")
    assert isinstance(result["risk_score"], int)
    assert 0 <= result["risk_score"] <= 100


def test_risk_level_present(engine):
    """Risk level must be Low, Medium, or High."""
    result = engine.analyze("Payment is due within 30 days.", "Payment Terms")
    assert result["risk_level"] in ("Low", "Medium", "High")


def test_risk_factors_list(engine):
    """Risk factors must be a list of strings."""
    result = engine.analyze("This clause limits liability.", "Liability")
    assert isinstance(result["risk_factors"], list)
    for factor in result["risk_factors"]:
        assert isinstance(factor, str)


# ── High-risk detection ──────────────────────────────────

def test_high_risk_text(engine):
    """Text with many risk indicators should score high."""
    high_risk_text = (
        "The Provider shall have unlimited liability for all consequential damages "
        "and indirect damages. The Provider waives all rights and irrevocably agrees "
        "to joint and several liability. No cap on liability shall apply. The agreement "
        "auto-renews perpetually at the Provider's sole discretion without notice. "
        "All terms are non-negotiable and binding without prior consent."
    )
    result = engine.analyze(high_risk_text, "Liability")
    assert result["risk_score"] >= 40, f"Expected high risk, got {result['risk_score']}"
    assert len(result["risk_factors"]) > 0


def test_high_risk_level(engine):
    """Very risky text should return 'High' or 'Medium' risk level."""
    text = (
        "Unlimited liability with no cap. Sole discretion to terminate without notice. "
        "Waiver of all rights. Irrevocable. Auto-renewal. Perpetual term. "
        "Joint and several liability. No warranty. As-is basis."
    )
    result = engine.analyze(text, "Liability")
    assert result["risk_level"] in ("High", "Medium")


# ── Low-risk detection ──────────────────────────────────

def test_low_risk_text(engine):
    """Neutral text with no risk indicators should score low."""
    low_risk_text = (
        "The parties agree to cooperate in good faith. This agreement "
        "represents the entire understanding between the parties."
    )
    result = engine.analyze(low_risk_text, "Governing Law")
    assert result["risk_score"] <= 40, f"Expected low risk, got {result['risk_score']}"


# ── Edge cases ──────────────────────────────────────────

def test_empty_input(engine):
    """Empty input should return score 0 and Low."""
    result = engine.analyze("", "Unknown")
    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["risk_factors"] == []


def test_short_input(engine):
    """Very short input should return safe defaults."""
    result = engine.analyze("hello", "Unknown")
    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"


# ── full_analysis integration ────────────────────────────

def test_full_analysis_schema(engine):
    """full_analysis() must return the integration contract schema."""
    result = engine.full_analysis(
        "Either party may terminate this agreement upon thirty days written notice."
    )
    assert "clause" in result
    assert "confidence" in result
    assert "risk_score" in result
    assert "risk_level" in result
    assert isinstance(result["clause"], str)
    assert isinstance(result["confidence"], (int, float))
    assert isinstance(result["risk_score"], int)
    assert result["risk_level"] in ("Low", "Medium", "High")
    assert 0.0 <= result["confidence"] <= 100.0
    assert 0 <= result["risk_score"] <= 100


def test_full_analysis_clause_detection(engine):
    """full_analysis() should correctly classify the clause type."""
    result = engine.full_analysis(
        "The receiving party shall not disclose any confidential information "
        "to any third party without prior written consent of the disclosing party."
    )
    assert result["clause"] == "Confidentiality"
    assert result["confidence"] > 20.0


def test_full_analysis_risk_scoring(engine):
    """full_analysis() should produce reasonable risk scores."""
    result = engine.full_analysis(
        "The Provider shall have unlimited liability for all damages. "
        "No cap on liability. Joint and several liability applies. "
        "The Provider waives all rights and defenses irrevocably."
    )
    assert result["risk_score"] > 20
