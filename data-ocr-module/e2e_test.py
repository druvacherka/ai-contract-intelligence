import httpx
import json

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

all_passed = True
for expected, text in test_cases:
    r = httpx.post("http://localhost:8000/analyze-text", json={"contract_text": text})
    data = r.json()
    status = "PASS" if data["clause"] == expected else "FAIL"
    if status == "FAIL":
        all_passed = False
    clause = data["clause"]
    conf = data["confidence"]
    risk = data["risk_score"]
    level = data["risk_level"]
    print(f"{status} | {expected:20s} | Got: {clause:20s} | Conf: {conf:5.1f}% | Risk: {risk:3d} ({level})")

print()
print(f"Result: {'ALL 10 PASSED' if all_passed else 'SOME FAILED'}")
