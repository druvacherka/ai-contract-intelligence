"""
Accuracy + OCR integration test.
Tests all NLP/Risk improvements and verifies Tesseract is working.
"""
import httpx, json, sys, os, tempfile
from PIL import Image, ImageDraw, ImageFont

BASE = "http://localhost:8000"
client = httpx.Client(timeout=60)
errors = []
results = []

print("=" * 70)
print("ACCURACY + OCR TEST")
print("=" * 70)

# ---- Test 1: NLP Accuracy (10 clause types) ----
CLAUSE_TESTS = {
    "Termination": """
        Either party may terminate this agreement upon thirty (30) days written
        notice. In the event of material breach that remains uncured for fifteen
        days after written notice, the non-breaching party may terminate immediately.
        Upon termination or expiration, all rights granted shall cease.
    """,
    "Confidentiality": """
        The Receiving Party agrees to hold all Confidential Information in strict
        confidence and not disclose any proprietary data to third parties without
        prior written consent. Non-disclosure obligations survive termination for
        five years. Trade secrets shall remain protected indefinitely.
    """,
    "Liability": """
        In no event shall either party be liable for indirect, incidental,
        consequential, or punitive damages. The total aggregate liability shall
        not exceed the amounts paid under this agreement in the preceding twelve
        months. Neither party shall bear unlimited liability.
    """,
    "Arbitration": """
        Any dispute arising out of this agreement shall be settled by binding
        arbitration in accordance with the rules of the American Arbitration
        Association. The arbitrator's decision shall be final and binding. The
        parties waive their right to a jury trial.
    """,
    "Governing Law": """
        This agreement shall be governed by and construed in accordance with
        the laws of the State of Delaware, without regard to its conflict of
        laws provisions. The parties submit to the exclusive jurisdiction of
        the federal and state courts located in Delaware.
    """,
    "Payment Terms": """
        All invoices are due and payable within net thirty (30) days of the
        invoice date. Late payments shall accrue interest at 1.5% per month.
        The Client shall reimburse all reasonable expenses with proper receipts.
    """,
    "Warranty": """
        The Provider represents and warrants that all deliverables shall be
        free from material defects and conform to the agreed specifications.
        This warranty shall remain in effect for twelve (12) months from
        delivery. The warranty is void if the product is misused.
    """,
    "Renewal": """
        This agreement shall automatically renew for successive one-year terms
        unless either party provides sixty (60) days written notice of
        non-renewal prior to expiration. Auto-renewal continues indefinitely
        unless terminated per this provision.
    """,
    "Indemnification": """
        Each party agrees to indemnify, defend, and hold harmless the other
        party from and against all losses, damages, liabilities, and expenses,
        including reasonable attorneys' fees, arising from any third-party claim
        related to the indemnifying party's breach of this agreement.
    """,
    "Non-Compete": """
        During the term and for two years following termination, the Contractor
        shall not directly or indirectly compete with the Company, solicit any
        employees or customers, or engage in any competing business within a
        fifty-mile radius of the Company's principal office.
    """,
}

print("\n[1] NLP Clause Classification Accuracy")
print("-" * 50)
correct = 0
for expected_clause, text in CLAUSE_TESTS.items():
    r = client.post(f"{BASE}/analyze-text", json={"contract_text": text})
    if r.status_code != 200:
        errors.append(f"Clause {expected_clause}: HTTP {r.status_code}")
        print(f"  FAIL {expected_clause}: HTTP {r.status_code}")
        continue
    data = r.json()
    actual = data["clause"]
    conf = data["confidence"]
    risk = data["risk_score"]
    level = data["risk_level"]
    match = actual == expected_clause
    if match:
        correct += 1
    status = "OK" if match else "WRONG"
    conf_status = "OK" if conf >= 70 else "LOW"
    print(f"  {status:5s} | {expected_clause:20s} -> {actual:20s} | conf={conf:5.1f}% ({conf_status}) | risk={risk:2d} ({level})")
    results.append({"expected": expected_clause, "actual": actual, "confidence": conf, "match": match})

accuracy = correct / len(CLAUSE_TESTS) * 100
print(f"\n  Accuracy: {correct}/{len(CLAUSE_TESTS)} = {accuracy:.0f}%")
low_conf = sum(1 for r in results if r["confidence"] < 70)
print(f"  Low confidence (<70%): {low_conf}/{len(CLAUSE_TESTS)}")

if accuracy < 80:
    errors.append(f"Classification accuracy too low: {accuracy:.0f}%")
if low_conf > 3:
    errors.append(f"Too many low-confidence results: {low_conf}/{len(CLAUSE_TESTS)}")

# ---- Test 2: Risk Scoring Accuracy ----
print("\n\n[2] Risk Scoring Accuracy")
print("-" * 50)

HIGH_RISK_TEXT = """
This agreement grants the Provider sole and absolute discretion to modify
terms at any time without notice. The Client assumes unlimited liability for
all damages, including consequential damages, with no cap on liability.
The Client irrevocably waives all rights to dispute resolution and waives
all claims and defenses. This is provided as-is without warranty. The
contract automatically renews indefinitely with no right to opt out and
includes a substantial early termination penalty.
"""

LOW_RISK_TEXT = """
This agreement sets forth the terms under which the parties will collaborate
on the project. Each party shall maintain reasonable care in performing their
obligations. Either party may terminate with 30 days notice. Standard
limitation of liability caps apply. Disputes will be resolved through
good-faith negotiation.
"""

r = client.post(f"{BASE}/analyze-text", json={"contract_text": HIGH_RISK_TEXT})
high_data = r.json()
print(f"  High-risk text: score={high_data['risk_score']}, level={high_data['risk_level']}")
if high_data["risk_score"] < 40:
    errors.append(f"High-risk text scored too low: {high_data['risk_score']}")
    print(f"    FAIL: Score should be >= 40")
else:
    print(f"    OK: Properly identified as risky")

r = client.post(f"{BASE}/analyze-text", json={"contract_text": LOW_RISK_TEXT})
low_data = r.json()
print(f"  Low-risk text:  score={low_data['risk_score']}, level={low_data['risk_level']}")
if low_data["risk_score"] > 50:
    errors.append(f"Low-risk text scored too high: {low_data['risk_score']}")
    print(f"    FAIL: Score should be <= 50")
else:
    print(f"    OK: Properly identified as low-risk")

# ---- Test 3: Tesseract OCR working ----
print("\n\n[3] Tesseract OCR Integration")
print("-" * 50)

# Create a test image with typed text
try:
    img = Image.new("RGB", (800, 200), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 30), "CONFIDENTIALITY AGREEMENT", fill="black", font=font)
    draw.text((20, 80), "All information shall remain strictly confidential", fill="black", font=font)
    draw.text((20, 130), "and shall not be disclosed to any third party.", fill="black", font=font)

    # Save to temp file and upload
    tmp_path = os.path.join(tempfile.gettempdir(), "ocr_test.png")
    img.save(tmp_path)

    with open(tmp_path, "rb") as f:
        files = {"file": ("test_contract.png", f, "image/png")}
        r = client.post(f"{BASE}/upload-contract", files=files)

    if r.status_code == 200:
        data = r.json()
        print(f"  OCR Result: clause={data['clause']}, conf={data['confidence']:.1f}%")
        print(f"  Risk: score={data['risk_score']}, level={data['risk_level']}")
        print(f"    OK: Tesseract OCR pipeline working!")
    else:
        errors.append(f"OCR upload failed: {r.status_code} - {r.text}")
        print(f"    FAIL: HTTP {r.status_code} - {r.text[:200]}")

    os.unlink(tmp_path)
except Exception as e:
    errors.append(f"OCR test failed: {e}")
    print(f"    FAIL: {e}")

# ---- Test 4: File upload with text file ----
print("\n\n[4] Text file upload")
print("-" * 50)

try:
    txt = b"""INDEMNIFICATION CLAUSE
    
Each party hereby agrees to indemnify, defend, and hold harmless the other 
party and its officers, directors, employees, and agents from and against 
all losses, damages, liabilities, costs, and expenses, including reasonable 
attorneys' fees, arising from or relating to any breach of this Agreement 
by the indemnifying party or any negligent or wrongful act or omission of 
the indemnifying party."""

    files = {"file": ("indemnity_contract.txt", txt, "text/plain")}
    r = client.post(f"{BASE}/upload-contract", files=files)
    if r.status_code == 200:
        data = r.json()
        print(f"  Result: clause={data['clause']}, conf={data['confidence']:.1f}%, risk={data['risk_score']}")
        if data["clause"] == "Indemnification":
            print(f"    OK: Correctly identified Indemnification clause!")
        else:
            print(f"    WARNING: Expected Indemnification, got {data['clause']}")
    else:
        errors.append(f"TXT upload failed: {r.status_code}")
        print(f"    FAIL: {r.status_code}")
except Exception as e:
    errors.append(f"TXT upload: {e}")
    print(f"    FAIL: {e}")

# ---- Summary ----
print("\n" + "=" * 70)
if errors:
    print(f"ISSUES ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("ALL TESTS PASSED!")
print(f"\nClassification accuracy: {accuracy:.0f}% ({correct}/{len(CLAUSE_TESTS)})")
print(f"High-risk detection: score={high_data['risk_score']} ({high_data['risk_level']})")
print(f"Low-risk detection:  score={low_data['risk_score']} ({low_data['risk_level']})")
print("=" * 70)

sys.exit(1 if errors else 0)
