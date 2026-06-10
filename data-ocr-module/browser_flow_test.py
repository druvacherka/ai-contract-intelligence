"""
Full browser-flow simulation: Tests exactly what the frontend JavaScript does.
Simulates: Page load -> health check -> pipeline status -> paste text -> analyze -> navigate to results.
"""
import httpx
import json
import sys

# Fix Unicode output on Windows (cp1252 doesn't support arrows/checkmarks)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

BASE = "http://localhost:8000"
client = httpx.Client(timeout=30)
errors = []


print("=" * 70)
print("LIVE BROWSER FLOW TEST — Simulating Frontend JavaScript")
print("=" * 70)

# ─── Step 1: What Upload.jsx does on mount ───────────────────────
print("\n[1] Upload page mount → healthCheck()")
try:
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    print(f"    ✅ Backend healthy: {data['status']}")
    print(f"    Modules: {list(data['modules'].keys())}")
except Exception as e:
    errors.append(f"Health check: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 2: What Upload.jsx does on mount ───────────────────────
print("\n[2] Upload page mount → getPipelineStatus()")
try:
    r = client.get(f"{BASE}/api/pipeline/status")
    assert r.status_code == 200
    data = r.json()
    print(f"    ✅ Pipeline status OK")
    print(f"    processed_count: {data.get('processed_count')}")
    print(f"    ocr_dpi: {data.get('ocr_dpi')}")
    print(f"    max_file_size_mb: {data.get('max_file_size_mb')}")
    print(f"    supported_formats: {data.get('supported_formats')}")
except Exception as e:
    errors.append(f"Pipeline status: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 3: Paste Text → analyzeText() ─────────────────────────
print("\n[3] Paste Text tab → api.analyzeText(contractText)")
contract_text = """
This Agreement may be terminated by either party upon thirty (30) days
prior written notice to the other party. In the event of a material breach
that remains uncured for fifteen (15) days after written notice thereof,
the non-breaching party shall have the right to terminate this Agreement
immediately. Upon termination, all rights and obligations shall cease
except for those provisions that by their nature survive termination.
"""

try:
    r = client.post(f"{BASE}/analyze-text",
                    json={"contract_text": contract_text},
                    headers={"Content-Type": "application/json"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()

    # Validate schema matches what ContractResults.jsx expects
    assert "clause" in data, "Missing 'clause' field"
    assert "confidence" in data, "Missing 'confidence' field"
    assert "risk_score" in data, "Missing 'risk_score' field"
    assert "risk_level" in data, "Missing 'risk_level' field"
    assert isinstance(data["clause"], str), f"clause should be str, got {type(data['clause'])}"
    assert isinstance(data["confidence"], (int, float)), f"confidence should be number, got {type(data['confidence'])}"
    assert isinstance(data["risk_score"], int), f"risk_score should be int, got {type(data['risk_score'])}"
    assert data["risk_level"] in ("Low", "Medium", "High"), f"Invalid risk_level: {data['risk_level']}"
    assert 0 <= data["confidence"] <= 100, f"confidence out of range: {data['confidence']}"
    assert 0 <= data["risk_score"] <= 100, f"risk_score out of range: {data['risk_score']}"

    print(f"    ✅ Analysis succeeded!")
    print(f"    Clause:     {data['clause']}")
    print(f"    Confidence: {data['confidence']}%")
    print(f"    Risk Score: {data['risk_score']}/100")
    print(f"    Risk Level: {data['risk_level']}")
except Exception as e:
    errors.append(f"Analyze text: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 4: Test CORS headers (what the browser enforces) ──────
print("\n[4] CORS check → OPTIONS /analyze-text")
try:
    r = client.options(f"{BASE}/analyze-text",
                       headers={
                           "Origin": "http://localhost:5173",
                           "Access-Control-Request-Method": "POST",
                           "Access-Control-Request-Headers": "content-type",
                       })
    # CORS should return 200
    cors_origin = r.headers.get("access-control-allow-origin", "MISSING")
    cors_methods = r.headers.get("access-control-allow-methods", "MISSING")
    print(f"    Status: {r.status_code}")
    print(f"    Allow-Origin: {cors_origin}")
    print(f"    Allow-Methods: {cors_methods}")
    if cors_origin == "*" or cors_origin == "http://localhost:5173":
        print(f"    ✅ CORS configured correctly")
    else:
        errors.append(f"CORS: Origin={cors_origin}")
        print(f"    ❌ CORS may block frontend requests!")
except Exception as e:
    errors.append(f"CORS: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 5: Test file upload (FormData like the browser sends) ──
print("\n[5] File upload → api.uploadForAnalysis(file)")
try:
    # Create a temporary .txt file simulating a contract
    txt_content = b"""CONFIDENTIALITY AGREEMENT

The Receiving Party agrees to hold and maintain all Confidential Information
of the Disclosing Party in strict confidence for the sole and exclusive
benefit of the Disclosing Party. Without limiting the foregoing, the Receiving
Party shall not, without the prior written approval of the Disclosing Party,
use or disclose any Confidential Information to any third party.

The Receiving Party shall carefully restrict access to Confidential Information
to employees, contractors and third parties as is reasonably required and shall
require those persons to sign nondisclosure restrictions at least as protective
as those in this Agreement.
"""
    files = {"file": ("test_contract.txt", txt_content, "text/plain")}
    r = client.post(f"{BASE}/upload-contract", files=files)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()

    assert "clause" in data, "Missing 'clause' in upload response"
    assert "confidence" in data, "Missing 'confidence'"
    assert "risk_score" in data, "Missing 'risk_score'"
    assert "risk_level" in data, "Missing 'risk_level'"

    print(f"    ✅ File upload + OCR + NLP pipeline succeeded!")
    print(f"    Clause:     {data['clause']}")
    print(f"    Confidence: {data['confidence']}%")
    print(f"    Risk Score: {data['risk_score']}/100")
    print(f"    Risk Level: {data['risk_level']}")
except Exception as e:
    errors.append(f"Upload contract: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 6: Test edge cases the user might trigger ──────────────
print("\n[6] Edge case: empty text submission")
try:
    r = client.post(f"{BASE}/analyze-text", json={"contract_text": ""})
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print(f"    ✅ Empty text correctly rejected (400)")
except Exception as e:
    errors.append(f"Empty text: {e}")
    print(f"    ❌ FAILED: {e}")

print("\n[7] Edge case: very short text")
try:
    r = client.post(f"{BASE}/analyze-text", json={"contract_text": "Hello world, short text."})
    assert r.status_code == 200
    data = r.json()
    print(f"    ✅ Short text handled: clause={data['clause']}, conf={data['confidence']}%")
except Exception as e:
    errors.append(f"Short text: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Step 7: Verify frontend is serving ─────────────────────────
print("\n[8] Frontend serving check")
try:
    r = client.get("http://localhost:5173/")
    assert r.status_code == 200
    assert "AI Contract Intelligence" in r.text
    print(f"    ✅ Frontend serving at http://localhost:5173")
except Exception as e:
    errors.append(f"Frontend: {e}")
    print(f"    ❌ FAILED: {e}")

try:
    r = client.get("http://localhost:5173/upload")
    assert r.status_code == 200
    print(f"    ✅ /upload route accessible")
except Exception as e:
    errors.append(f"Upload route: {e}")
    print(f"    ❌ FAILED: {e}")

try:
    r = client.get("http://localhost:5173/dashboard")
    assert r.status_code == 200
    print(f"    ✅ /dashboard route accessible")
except Exception as e:
    errors.append(f"Dashboard route: {e}")
    print(f"    ❌ FAILED: {e}")

try:
    r = client.get("http://localhost:5173/results")
    assert r.status_code == 200
    print(f"    ✅ /results route accessible")
except Exception as e:
    errors.append(f"Results route: {e}")
    print(f"    ❌ FAILED: {e}")

# ─── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 70)
if errors:
    print(f"❌ {len(errors)} ERROR(S) FOUND:")
    for err in errors:
        print(f"   • {err}")
    sys.exit(1)
else:
    print("✅ ALL 8 CHECKS PASSED — Full browser flow verified!")
    print("   Backend API: healthy, CORS OK, all endpoints working")
    print("   Frontend: all routes serving correctly")
    print("   NLP Pipeline: clause classification + risk scoring operational")
    print("   File Upload: OCR + NLP + Risk pipeline end-to-end OK")
print("=" * 70)
