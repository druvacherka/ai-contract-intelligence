"""
E2E NLP Clause Classification Test Suite.

Tests all 10 supported clause types against the /analyze-text API endpoint.
Validates that the NLP engine correctly classifies each clause type and
returns the expected integration contract schema.

Usage:
    python e2e_test.py
"""
import sys
import httpx

# Fix Unicode output on Windows (cp1252 doesn't support special chars)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"

test_cases = [
    ("Termination", "Either party may terminate this agreement upon thirty days prior written notice. Right to terminate for cause applies."),
    ("Confidentiality", "The receiving party shall not disclose any confidential information or proprietary data without prior written consent."),
    ("Liability", "In no event shall either party be liable for indirect or consequential damages. Total aggregate liability shall not exceed amounts paid."),
    ("Arbitration", "Any dispute shall be settled by binding arbitration under the rules of the American Arbitration Association."),
    ("Governing Law", "This agreement shall be governed by and construed in accordance with the laws of the State of Delaware."),
    ("Payment Terms", "All invoices are payable within net 30 days of the invoice date. Late payments accrue interest at 1.5 percent per month."),
    ("Warranty", "The Provider represents and warrants that services shall be performed consistent with industry standards and free from defects."),
    ("Renewal", "This agreement shall automatically renew for successive one-year terms unless either party provides sixty days notice of non-renewal."),
    ("Indemnification", "Each party agrees to indemnify defend and hold harmless the other party from all losses damages and attorneys fees."),
    ("Non-Compete", "The contractor shall not directly or indirectly compete within a fifty mile radius for two years following termination."),
]

print("=" * 90)
print("  E2E NLP Clause Classification — 10 Clause Types")
print("=" * 90)

passed = 0
failed = 0
for expected, text in test_cases:
    r = httpx.post(f"{BASE_URL}/analyze-text", json={"contract_text": text})
    data = r.json()
    status = "PASS" if data["clause"] == expected else "FAIL"
    if status == "PASS":
        passed += 1
    else:
        failed += 1
    clause = data["clause"]
    conf = data["confidence"]
    risk = data["risk_score"]
    level = data["risk_level"]
    print(f"  {status} | {expected:20s} | Got: {clause:20s} | Conf: {conf:5.1f}% | Risk: {risk:3d} ({level})")

print("=" * 90)
print(f"  Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 90)

if failed > 0:
    sys.exit(1)

