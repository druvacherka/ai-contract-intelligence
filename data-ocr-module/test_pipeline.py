"""Quick test: create a text file and upload it to the /upload-contract endpoint."""
import requests
import tempfile
import json
import os

# Create a test contract text file
contract_text = """
PROFESSIONAL SERVICES AGREEMENT

This Professional Services Agreement ("Agreement") is entered into as of January 1, 2025,
by and between ABC Corporation, a Delaware corporation ("Company"), and XYZ Consulting LLC,
a California limited liability company ("Consultant").

SECTION 1 - TERMINATION
Either party may terminate this Agreement upon thirty (30) days' prior written notice to the
other party. The Company may terminate immediately for cause.

SECTION 2 - CONFIDENTIALITY
All proprietary information shared between the parties shall remain strictly confidential
for a period of five (5) years following termination of this Agreement.

SECTION 3 - INDEMNIFICATION
Consultant shall indemnify and hold harmless the Company, its officers, directors, and employees
from and against any and all claims, damages, losses, costs, and expenses arising from
Consultant's breach of this Agreement or negligent performance of services.

SECTION 4 - LIABILITY
The total aggregate liability of either party under this Agreement shall not exceed the total
fees paid or payable during the twelve (12) month period preceding the claim. IN NO EVENT SHALL
EITHER PARTY BE LIABLE FOR INDIRECT, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES.

SECTION 5 - PAYMENT TERMS
Payment shall be made within thirty (30) days of receipt of invoice. Late payments shall accrue
interest at a rate of 1.5% per month. Total contract value: $250,000.

SECTION 6 - GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of
California, without regard to conflicts of law principles.

SECTION 7 - ARBITRATION
Any and all disputes arising under or relating to this Agreement shall be resolved through
binding arbitration administered by the American Arbitration Association in San Francisco, California.

SECTION 8 - WARRANTY
Consultant warrants that all services shall be performed in a professional manner consistent
with generally accepted industry standards.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.
"""

# Write to temp file
test_file = os.path.join(tempfile.gettempdir(), "test_contract.txt")
with open(test_file, "w") as f:
    f.write(contract_text)

print("Uploading test contract...")
try:
    with open(test_file, "rb") as f:
        resp = requests.post(
            "http://localhost:8000/upload-contract",
            files={"file": ("test_contract.txt", f, "text/plain")},
            timeout=120,
        )
    
    if resp.status_code == 200:
        data = resp.json()
        print("\n=== PIPELINE RESULT ===")
        print(f"Status: SUCCESS")
        print(f"Clause: {data.get('clause', 'N/A')} (conf: {data.get('confidence', 0):.1f}%)")
        print(f"Risk: {data.get('risk_score', 0)}/100 ({data.get('risk_level', 'N/A')})")
        print(f"Pages: {data.get('pages', 'N/A')}")
        print(f"Contract text length: {len(data.get('contract_text', ''))}")
        print(f"Clauses detected: {len(data.get('clauses', []))}")
        print(f"Risk factors: {len(data.get('risk_factors', []))}")
        print(f"Missing clauses: {data.get('missing_clauses', [])}")
        print(f"Completeness: {data.get('completeness_score', 'N/A')}%")
        
        print(f"\n=== AI SUMMARY ===")
        print(data.get('ai_summary', 'NONE')[:500])
        
        print(f"\n=== KEY FINDINGS ===")
        for f in data.get('key_findings', []):
            print(f"  - {f}")
        
        print(f"\n=== RECOMMENDATIONS ===")
        for r in data.get('recommendations', []):
            print(f"  - {r}")
        
        print(f"\n=== ENTITIES ===")
        entities = data.get('entities', {})
        for cat, vals in entities.items():
            if vals:
                print(f"  {cat}: {vals}")
        
        print(f"\n=== CLAUSES ===")
        for c in data.get('clauses', []):
            print(f"  {c.get('type', '?')}: {c.get('confidence', 0):.1f}% (risk: {c.get('risk_score', 0)})")
    else:
        print(f"ERROR {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"Request failed: {e}")
finally:
    os.unlink(test_file)
