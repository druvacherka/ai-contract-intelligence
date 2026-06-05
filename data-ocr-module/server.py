"""
FastAPI Backend Server — Contract Intelligence OCR Pipeline.

Serves the data-ocr-module as REST API endpoints for the frontend.
"""

import sys
import time
import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# Add data-ocr-module to path
MODULE_ROOT = Path(__file__).resolve().parent.parent / "data-ocr-module"
sys.path.insert(0, str(MODULE_ROOT))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import OCR pipeline modules
from src.utils.config import Config
from src.ingestion.document_loader import DocumentLoader, DocumentLoadError
from src.ocr.pdf_parser import PDFParser, PDFParseError
from src.ocr.ocr_engine import OCREngine
from src.ocr.scan_detector import ScanDetector
from src.ocr.image_preprocessor import ImagePreprocessor
from src.ingestion.docx_parser import DOCXParser
from src.preprocessing.clean_text import TextCleaner
from src.preprocessing.json_formatter import JSONFormatter
from src.nlp.nlp_engine import NLPEngine
from src.nlp.risk_engine import RiskEngine
from src.utils.logger import logger

# Ensure directories exist
Config.ensure_directories()

app = FastAPI(
    title="ContractIQ OCR Pipeline API",
    description="Enterprise document ingestion, OCR, and text extraction pipeline",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline components
document_loader = DocumentLoader()
pdf_parser = PDFParser()
docx_parser = DOCXParser()
scan_detector = ScanDetector()
ocr_engine = OCREngine()
text_cleaner = TextCleaner()
json_formatter = JSONFormatter()
nlp_engine = NLPEngine()
risk_engine = RiskEngine(nlp_engine=nlp_engine)


class AnalyzeTextRequest(BaseModel):
    """Request body for /analyze-text."""
    contract_text: str

# In-memory store for processed documents
processed_docs: dict[str, dict[str, Any]] = {}

UPLOAD_DIR = MODULE_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ContractIQ OCR Pipeline",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "document_loader": "ready",
            "pdf_parser": "ready",
            "docx_parser": "ready",
            "ocr_engine": "ready",
            "scan_detector": "ready",
            "text_cleaner": "ready",
            "json_formatter": "ready",
        },
    }


@app.get("/api/pipeline/status")
async def pipeline_status():
    """Get pipeline status and stats."""
    return {
        "status": "operational",
        "processed_count": len(processed_docs),
        "supported_formats": [".pdf", ".docx", ".doc", ".txt"],
        "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
        "ocr_available": True,
        "ocr_dpi": Config.OCR_DPI,
        "ocr_language": Config.OCR_LANGUAGE,
    }


@app.post("/api/upload")
async def upload_and_process(file: UploadFile = File(...)):
    """
    Upload a document and process it through the full OCR pipeline.

    Steps:
    1. Save uploaded file
    2. Validate file type/size
    3. Extract text (native or OCR)
    4. Clean text
    5. Format to structured JSON
    6. Return result
    """
    start_time = time.time()
    file_id = str(uuid.uuid4())[:12]

    try:
        # Step 1: Save uploaded file
        safe_name = file.filename.replace(" ", "_")
        save_path = UPLOAD_DIR / f"{file_id}_{safe_name}"

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_size_mb = len(content) / (1024 * 1024)

        # Step 2: Validate
        try:
            doc_info = document_loader.load(save_path)
        except DocumentLoadError as e:
            raise HTTPException(status_code=400, detail=str(e))

        metadata = doc_info.get("metadata", {})
        category = metadata.get("category", "unknown")

        # Step 3: Extract text
        extracted_text = ""
        pages = 0
        processing_method = "native"
        ocr_confidence = None

        if category == "pdf":
            try:
                result = pdf_parser.extract(save_path)
                pages = len(result.get("pages", []))

                if result.get("needs_ocr", False):
                    # Try OCR
                    try:
                        scan_result = scan_detector.detect(save_path)
                        if scan_result.get("is_scanned", True):
                            ocr_result = ocr_engine.ocr_pdf(save_path)
                            extracted_text = ocr_result["full_text"]
                            pages = ocr_result["metadata"]["num_pages"]
                            processing_method = "ocr"
                            ocr_confidence = ocr_result["metadata"].get("avg_confidence")
                        else:
                            extracted_text = result["full_text"]
                    except Exception:
                        extracted_text = result["full_text"]
                else:
                    extracted_text = result["full_text"]
            except PDFParseError as e:
                raise HTTPException(status_code=422, detail=f"PDF parsing failed: {e}")

        elif category == "docx":
            try:
                result = docx_parser.extract(save_path)
                extracted_text = result["full_text"]
                pages = max(1, len(extracted_text) // 3000)
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"DOCX parsing failed: {e}")

        elif category == "text":
            extracted_text = doc_info.get("text", "")
            pages = 1

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {category}")

        if not extracted_text.strip():
            extracted_text = "[NO TEXT EXTRACTED]"

        # Step 4: Clean text
        is_ocr = processing_method == "ocr"
        clean_result = text_cleaner.clean(extracted_text, is_ocr=is_ocr)
        clean_text = clean_result["clean_text"]
        sentences = clean_result.get("sentences", [])

        # Step 5: Format output
        elapsed = time.time() - start_time

        document = json_formatter.format_document(
            filename=file.filename,
            clean_text=clean_text,
            pages=pages,
            processing_method=processing_method,
            metadata=metadata,
            sentences=sentences,
            confidence=ocr_confidence,
            processing_time=elapsed,
        )

        # Save to disk
        output_path = json_formatter.save(document)

        # Store in memory
        document["file_id"] = file_id
        document["original_size_mb"] = round(file_size_mb, 3)
        processed_docs[document["document_id"]] = document

        # Cleanup upload file
        try:
            save_path.unlink()
        except Exception:
            pass

        return {
            "status": "success",
            "document": document,
            "output_path": str(output_path),
            "processing_time_seconds": round(elapsed, 3),
        }

    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "processing_time_seconds": round(elapsed, 3),
            },
        )


@app.get("/api/documents")
async def list_documents():
    """List all processed documents."""
    docs = []
    for doc_id, doc in processed_docs.items():
        docs.append({
            "document_id": doc["document_id"],
            "filename": doc["filename"],
            "document_type": doc["document_type"],
            "pages": doc["pages"],
            "processing_method": doc["processing_method"],
            "word_count": doc["metadata"].get("word_count", 0),
            "text_length": doc["metadata"].get("text_length", 0),
            "num_sentences": doc.get("num_sentences", 0),
            "processing_time": doc.get("processing_time_seconds", 0),
            "processed_at": doc["metadata"].get("processed_at", ""),
        })
    return {"documents": docs, "total": len(docs)}


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific processed document by ID."""
    if doc_id not in processed_docs:
        raise HTTPException(status_code=404, detail="Document not found")
    return processed_docs[doc_id]


# ──────────────────────────────────────────────────────────────
# NLP Integration Endpoints
# ──────────────────────────────────────────────────────────────


@app.post("/upload-contract")
async def upload_contract_nlp(file: UploadFile = File(...)):
    """
    Full pipeline: Upload → OCR → Clean → NLP → Risk → Response.

    Supports: PDF, DOCX, DOC, TXT, JPG, PNG, TIFF, BMP
    Handles: native digital text, scanned documents, handwritten documents.

    Returns the integration contract schema:
    {"clause": "...", "confidence": ..., "risk_score": ..., "risk_level": "..."}
    """
    start_time = time.time()
    file_id = str(uuid.uuid4())[:12]
    used_ocr = False

    try:
        # Step 1: Save uploaded file
        safe_name = file.filename.replace(" ", "_") if file.filename else "upload"
        save_path = UPLOAD_DIR / f"{file_id}_{safe_name}"

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_ext = save_path.suffix.lower()

        # Step 2: Extract text based on file type
        extracted_text = ""

        # ── Image files (handwritten / scanned) ──
        if file_ext in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"):
            from PIL import Image as PILImage
            try:
                img = PILImage.open(save_path)
                # Call ocr_image with self-healing fallback preset support
                ocr_result = ocr_engine.ocr_image(img, preprocess=True, preset="standard")
                extracted_text = ocr_result.get("text", "")
                used_ocr = True
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Image OCR failed: {e}")

        # ── PDF files ──
        elif file_ext == ".pdf":
            try:
                # Try native text extraction first
                doc_info = document_loader.load(save_path)
                result = pdf_parser.extract(save_path)
                extracted_text = result.get("full_text", "")

                # If native text is too short or needs OCR, run OCR
                needs_ocr = result.get("needs_ocr", False)
                if needs_ocr or len(extracted_text.strip()) < 30:
                    try:
                        ocr_result = ocr_engine.ocr_pdf(save_path)
                        ocr_text = ocr_result.get("full_text", "")
                        if len(ocr_text.strip()) > len(extracted_text.strip()):
                            extracted_text = ocr_text
                            used_ocr = True
                    except Exception as ocr_err:
                        logger.warning("OCR fallback failed for PDF: {}", ocr_err)
                        # Keep whatever native text we got

            except PDFParseError as e:
                # PDF parse failed entirely, try pure OCR
                try:
                    ocr_result = ocr_engine.ocr_pdf(save_path)
                    extracted_text = ocr_result.get("full_text", "")
                    used_ocr = True
                except Exception:
                    raise HTTPException(status_code=422, detail=f"PDF parsing failed: {e}")

        # ── DOCX files ──
        elif file_ext in (".docx", ".doc"):
            try:
                result = docx_parser.extract(save_path)
                extracted_text = result.get("full_text", "")
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"DOCX parsing failed: {e}")

        # ── Plain text files ──
        elif file_ext == ".txt":
            try:
                doc_info = document_loader.load(save_path)
                extracted_text = doc_info.get("text", "")
            except Exception as e:
                # Direct read fallback
                with open(save_path, "r", encoding="utf-8", errors="ignore") as tf:
                    extracted_text = tf.read()

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: PDF, DOCX, TXT, JPG, PNG, TIFF, BMP"
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted. For handwritten documents, ensure the image is clear and well-lit."
            )

        # Step 3: Clean text
        clean_result = text_cleaner.clean(extracted_text, is_ocr=used_ocr)
        clean_text = clean_result["clean_text"]

        # Step 4: NLP + Risk analysis
        analysis = risk_engine.full_analysis(clean_text)

        elapsed = time.time() - start_time
        logger.info(
            "upload-contract complete | file={} | ocr={} | clause={} | time={:.2f}s",
            safe_name, used_ocr, analysis["clause"], elapsed,
        )

        # Cleanup uploaded file
        try:
            save_path.unlink()
        except Exception:
            pass

        return {
            "clause": analysis["clause"],
            "confidence": analysis["confidence"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
        }

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Processing failed: {str(e)}"},
        )


@app.post("/analyze-text")
async def analyze_text(request: AnalyzeTextRequest):
    """
    Text-only pipeline: Accept contract text → NLP → Risk → Response.

    Returns the integration contract schema:
    {"clause": "...", "confidence": ..., "risk_score": ..., "risk_level": "..."}
    """
    contract_text = request.contract_text

    if not contract_text or not contract_text.strip():
        raise HTTPException(status_code=400, detail="contract_text must not be empty.")

    try:
        analysis = risk_engine.full_analysis(contract_text.strip())

        return {
            "clause": analysis["clause"],
            "confidence": analysis["confidence"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Analysis failed: {str(e)}"},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
