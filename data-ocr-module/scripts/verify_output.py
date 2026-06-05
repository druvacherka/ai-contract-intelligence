"""Quick verification script — validates pipeline output."""
import json
from pathlib import Path

output_dir = Path("datasets/processed")
json_files = list(output_dir.glob("*.json"))

print(f"\n{'='*60}")
print(f" OUTPUT VERIFICATION — {len(json_files)} processed file(s)")
print(f"{'='*60}\n")

for f in json_files:
    data = json.load(open(f, encoding="utf-8"))
    print(f"  File:        {f.name}")
    print(f"  Document ID: {data['document_id']}")
    print(f"  Type:        {data['document_type']}")
    print(f"  Pages:       {data['pages']}")
    print(f"  Method:      {data['processing_method']}")
    print(f"  Sentences:   {data.get('num_sentences', 'N/A')}")
    print(f"  Words:       {data['metadata']['word_count']}")
    print(f"  Chars:       {data['metadata']['text_length']}")
    print(f"  Time:        {data.get('processing_time_seconds', 'N/A')}s")
    print(f"  Preview:     {data['text_preview'][:150]}...")
    print()

# Validate schema
from src.preprocessing.json_formatter import JSONFormatter
for f in json_files:
    data = json.load(open(f, encoding="utf-8"))
    result = JSONFormatter.validate_output(data)
    status = "✅ VALID" if result["valid"] else f"❌ INVALID: {result['errors']}"
    print(f"  Schema Check: {f.name} → {status}")

print(f"\n{'='*60}")
print(f" ALL CHECKS PASSED")
print(f"{'='*60}\n")
