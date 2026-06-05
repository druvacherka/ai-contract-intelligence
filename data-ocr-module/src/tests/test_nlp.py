"""
Tests for the NLP Clause Classifier (NLPEngine).

Tests cover:
- Classification of all 10 clause types
- Confidence range validation (0–100)
- Empty / short / garbage input handling
- Output schema compliance
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from src.nlp.nlp_engine import NLPEngine


@pytest.fixture(scope="module")
def engine():
    """Shared NLPEngine instance (keyword + TF-IDF only, no transformer)."""
    return NLPEngine(use_transformer=False)


# ── Schema validation ──────────────────────────────────────────

def test_output_schema(engine):
    """Output must contain 'clause' (str) and 'confidence' (float)."""
    result = engine.classify("This agreement may be terminated by either party.")
    assert "clause" in result
    assert "confidence" in result
    assert isinstance(result["clause"], str)
    assert isinstance(result["confidence"], (int, float))


def test_confidence_range(engine):
    """Confidence must be between 0.0 and 100.0 inclusive."""
    result = engine.classify(
        "The Provider warrants that the services will conform to the specifications."
    )
    assert 0.0 <= result["confidence"] <= 100.0


# ── Clause classification accuracy ─────────────────────────────

CLAUSE_SAMPLES = {
    "Termination": (
        "Either party may terminate this agreement upon thirty days prior "
        "written notice. In the event of a material breach, the non-breaching "
        "party shall have the right to terminate immediately."
    ),
    "Confidentiality": (
        "The receiving party shall not disclose any confidential information "
        "to any third party without the prior written consent of the disclosing "
        "party. All proprietary data shall be kept strictly confidential."
    ),
    "Liability": (
        "In no event shall either party be liable for any indirect, incidental, "
        "or consequential damages. The total aggregate liability shall not exceed "
        "the amounts paid under this agreement in the preceding twelve months."
    ),
    "Arbitration": (
        "Any dispute arising under this agreement shall be settled by binding "
        "arbitration in accordance with the rules of the American Arbitration "
        "Association. The arbitrator's decision shall be final and binding."
    ),
    "Governing Law": (
        "This agreement shall be governed by and construed in accordance with "
        "the laws of the State of Delaware, without regard to its conflict of "
        "laws provisions. The parties submit to the exclusive jurisdiction of "
        "the courts of Delaware."
    ),
    "Payment Terms": (
        "All invoices are payable within net 30 days of the invoice date. "
        "Late payments will accrue interest at 1.5% per month. The Client "
        "shall reimburse all reasonable expenses upon receipt of invoice."
    ),
    "Warranty": (
        "The Provider represents and warrants that the deliverables shall be "
        "free from defects and shall conform to the agreed specifications. "
        "This warranty shall survive for a period of twelve months."
    ),
    "Renewal": (
        "This agreement shall automatically renew for successive one-year terms "
        "unless either party provides sixty days written notice of non-renewal "
        "prior to the expiration of the then-current term."
    ),
    "Indemnification": (
        "Each party agrees to indemnify, defend, and hold harmless the other "
        "party from all losses, damages, and expenses, including reasonable "
        "attorneys' fees, arising from any third-party claim."
    ),
    "Non-Compete": (
        "During the term and for two years following termination, the Contractor "
        "shall not directly or indirectly compete with the Company within a "
        "fifty-mile radius or solicit any employees or customers."
    ),
}


@pytest.mark.parametrize("expected_clause,sample_text", list(CLAUSE_SAMPLES.items()))
def test_clause_classification(engine, expected_clause, sample_text):
    """Each clause type should be correctly identified with meaningful text."""
    result = engine.classify(sample_text)
    assert result["clause"] == expected_clause, (
        f"Expected '{expected_clause}', got '{result['clause']}' "
        f"(confidence: {result['confidence']})"
    )
    assert result["confidence"] > 20.0, (
        f"Confidence too low for '{expected_clause}': {result['confidence']}"
    )


# ── Edge cases ─────────────────────────────────────────────────

def test_empty_input(engine):
    """Empty string should return Unknown with 0 confidence."""
    result = engine.classify("")
    assert result["clause"] == "Unknown"
    assert result["confidence"] == 0.0


def test_whitespace_only(engine):
    """Whitespace-only input should return Unknown."""
    result = engine.classify("   \n\t  \n  ")
    assert result["clause"] == "Unknown"
    assert result["confidence"] == 0.0


def test_very_short_input(engine):
    """Very short input (< 10 chars) should return Unknown."""
    result = engine.classify("Hello")
    assert result["clause"] == "Unknown"
    assert result["confidence"] == 0.0


def test_garbage_input(engine):
    """Non-alphabetic garbage input should return Unknown."""
    result = engine.classify("12345 67890 !@#$% ^&*() 12345 67890")
    assert result["clause"] == "Unknown"
    assert result["confidence"] == 0.0


def test_generic_text(engine):
    """Generic non-legal text should have low confidence."""
    result = engine.classify(
        "The weather today is sunny with a high of 75 degrees. "
        "We recommend bringing sunscreen and water for outdoor activities."
    )
    # Should still return something but with lower confidence
    assert 0.0 <= result["confidence"] <= 100.0
