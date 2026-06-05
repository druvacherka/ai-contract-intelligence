"""
Pytest Configuration and Shared Fixtures.

Provides test fixtures for all pipeline test modules including
sample documents, temporary directories, and mock data.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text():
    """Provide sample contract text for testing."""
    return """
    MASTER SERVICE AGREEMENT

    This Master Service Agreement ("Agreement") is entered into as of January 1, 2024
    ("Effective Date"), by and between:

    Company ABC, Inc., a Delaware corporation with principal offices at
    123 Business Lane, New York, NY 10001 ("Client"),

    and

    Service Provider XYZ LLC, a California limited liability company with
    principal offices at 456 Tech Avenue, San Francisco, CA 94105 ("Provider").

    ARTICLE 1. DEFINITIONS

    1.1 "Services" means the consulting, development, and support services
    described in each Statement of Work executed under this Agreement.

    1.2 "Confidential Information" means all non-public information disclosed
    by either party to the other, whether orally or in writing, that is
    designated as confidential.

    ARTICLE 2. SCOPE OF SERVICES

    2.1 Provider shall perform the Services described in each Statement of
    Work ("SOW") in a professional and workmanlike manner.

    (a) Each SOW shall specify the scope, timeline, deliverables, and fees.

    (b) Provider shall assign qualified personnel to perform the Services.

    ARTICLE 3. TERM AND TERMINATION

    3.1 This Agreement shall commence on the Effective Date and shall
    continue for an initial term of twelve (12) months.

    3.2 Either party may terminate this Agreement upon thirty (30) days
    prior written notice.

    ARTICLE 4. CONFIDENTIALITY

    4.1 Each party agrees to maintain the confidentiality of the other
    party's Confidential Information and not to disclose such information
    to any third party without prior written consent.

    ARTICLE 5. GOVERNING LAW

    5.1 This Agreement shall be governed by and construed in accordance
    with the laws of the State of Delaware.
    """.strip()


@pytest.fixture
def sample_dirty_text():
    """Provide dirty/unclean text for testing the cleaner."""
    return """



    Page 1 of 10

    CONFIDENTIAL

    MASTER   SERVICE    AGREEMENT

    This Master Service Agreement (\u201cAgreement\u201d) is entered into
    as of January 1, 2024 (\u201cEffective Date\u201d).

    - 2 -

    ARTICLE 1.  DEFINITIONS

    1.1  \u201cServices\u201d means the consulting services.

    ___________________________________

    Page 2 of 10

    ARTICLE 2.   SCOPE

    2.1  Provider shall perform services.

    ========================================

    3

    CONFIDENTIAL

    DRAFT
    """


@pytest.fixture
def sample_cuad_article():
    """Provide a sample CUAD-format article for testing."""
    return {
        "title": "Test Contract ABC Corp",
        "paragraphs": [
            {
                "context": (
                    "This Agreement is entered into as of January 1, 2024, "
                    "by and between ABC Corporation and XYZ LLC. "
                    "This Agreement shall be governed by the laws of Delaware. "
                    "Either party may terminate this Agreement upon 30 days notice."
                ),
                "qas": [
                    {
                        "question": "Highlight the parts (if any) of this contract related to Agreement Date.",
                        "id": "test-001",
                        "answers": [
                            {
                                "text": "January 1, 2024",
                                "answer_start": 45,
                            }
                        ],
                        "is_impossible": False,
                    },
                    {
                        "question": "Highlight the parts (if any) of this contract related to Governing Law.",
                        "id": "test-002",
                        "answers": [
                            {
                                "text": "laws of Delaware",
                                "answer_start": 134,
                            }
                        ],
                        "is_impossible": False,
                    },
                    {
                        "question": "Highlight the parts (if any) of this contract related to Termination For Convenience.",
                        "id": "test-003",
                        "answers": [
                            {
                                "text": "Either party may terminate this Agreement upon 30 days notice",
                                "answer_start": 152,
                            }
                        ],
                        "is_impossible": False,
                    },
                    {
                        "question": "Highlight the parts (if any) of this contract related to Non-Compete.",
                        "id": "test-004",
                        "answers": [],
                        "is_impossible": True,
                    },
                ],
            }
        ],
    }


@pytest.fixture
def sample_cuad_dataset(sample_cuad_article):
    """Provide a complete sample CUAD dataset."""
    return {
        "version": "v1.0",
        "data": [sample_cuad_article],
    }


@pytest.fixture
def sample_txt_file(tmp_dir, sample_text):
    """Create a sample .txt file in the temp directory."""
    filepath = tmp_dir / "test_contract.txt"
    filepath.write_text(sample_text, encoding="utf-8")
    return filepath


@pytest.fixture
def sample_cuad_json(tmp_dir, sample_cuad_dataset):
    """Create a sample CUAD JSON file in the temp directory."""
    filepath = tmp_dir / "CUADv1.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sample_cuad_dataset, f)
    return filepath


@pytest.fixture
def empty_file(tmp_dir):
    """Create an empty file."""
    filepath = tmp_dir / "empty.txt"
    filepath.touch()
    return filepath


@pytest.fixture
def unsupported_file(tmp_dir):
    """Create a file with an unsupported extension."""
    filepath = tmp_dir / "test.xyz"
    filepath.write_text("unsupported content")
    return filepath


@pytest.fixture
def large_file(tmp_dir):
    """Create a file that exceeds the size limit (simulated)."""
    filepath = tmp_dir / "large.txt"
    # Write just a few bytes but we'll test with a reduced limit
    filepath.write_text("x" * 1000)
    return filepath
