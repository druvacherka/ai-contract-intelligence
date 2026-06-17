"""
FastAPI Backend Server — Contract Intelligence OCR Pipeline.

Serves the data-ocr-module as REST API endpoints for the frontend.
Includes Supabase auth, contract CRUD, vector search, and PDF reports.
All optional dependencies degrade gracefully when missing.
"""

import sys
import time
import json
import shutil
import uuid
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional

# Add data-ocr-module to path
MODULE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_ROOT))

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# ── Core pipeline imports (always available) ──────────────────────
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

# ── Optional: AgentPipeline ───────────────────────────────────────
try:
    from src.agents.pipeline import AgentPipeline
    _AGENT_PIPELINE_AVAILABLE = True
    logger.info("AgentPipeline loaded successfully")
except Exception as _agent_err:
    _AGENT_PIPELINE_AVAILABLE = False
    logger.warning("AgentPipeline not available ({}), using inline pipeline", _agent_err)

# ── Optional: backend services ────────────────────────────────────
try:
    from src.services import database
    from src.services import vector_search
    from src.services import pdf_report
    from src.services.supabase_client import get_supabase_client
    _SERVICES_AVAILABLE = True
except Exception as _svc_err:
    database = None  # type: ignore[assignment]
    vector_search = None  # type: ignore[assignment]
    pdf_report = None  # type: ignore[assignment]
    get_supabase_client = None  # type: ignore[assignment]
    _SERVICES_AVAILABLE = False
    logger.warning("Backend services not available ({})", _svc_err)

# Ensure directories exist
Config.ensure_directories()

# ──────────────────────────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="IntelliAnalyze AI OCR Pipeline API",
    description="Enterprise document ingestion, OCR, NLP analysis, and contract intelligence platform",
    version="2.0.0",
)

# CORS — allow all origins for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize pipeline components ────────────────────────────────
document_loader = DocumentLoader()
pdf_parser = PDFParser()
docx_parser = DOCXParser()
scan_detector = ScanDetector()
ocr_engine = OCREngine()
text_cleaner = TextCleaner()
json_formatter = JSONFormatter()
nlp_engine = NLPEngine()
risk_engine = RiskEngine(nlp_engine=nlp_engine)

UPLOAD_DIR = MODULE_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────
# Request / response models
# ──────────────────────────────────────────────────────────────────

class AnalyzeTextRequest(BaseModel):
    """Request body for /analyze-text."""
    contract_text: str


class SearchRequest(BaseModel):
    """Request body for /api/search."""
    query: str
    limit: int = 10


# ──────────────────────────────────────────────────────────────────
# In-memory document store (backward compatibility)
# ──────────────────────────────────────────────────────────────────
processed_docs: dict[str, dict[str, Any]] = {}


def load_processed_documents():
    processed_dir = Config.PROCESSED_DIR
    if processed_dir.exists():
        for file_path in processed_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    if "document_id" in doc:
                        processed_docs[doc["document_id"]] = doc
            except Exception as e:
                logger.error(f"Failed to load processed doc {file_path}: {e}")
    logger.info(f"Loaded {len(processed_docs)} processed documents from disk.")


load_processed_documents()


# ──────────────────────────────────────────────────────────────────
# Authentication — Supabase JWT verification
# ──────────────────────────────────────────────────────────────────

async def get_current_user(authorization: str = Header(None)) -> str:
    """
    Extract and verify the Supabase JWT from the Authorization header.

    Returns the user's UUID (``sub`` claim).
    Raises ``HTTPException(401)`` on failure.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    # Strip "Bearer " prefix
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")

    token = parts[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Token is empty")

    # Strategy: use Supabase client to verify the token
    if _SERVICES_AVAILABLE and get_supabase_client is not None:
        supabase = get_supabase_client()
        if supabase is not None:
            try:
                user_response = supabase.auth.get_user(token)
                if user_response and user_response.user:
                    return str(user_response.user.id)
            except Exception as exc:
                logger.warning("Supabase auth.get_user failed: {}", exc)
                raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fallback: decode JWT manually (python-jose)
    try:
        from jose import jwt as jose_jwt

        # Supabase JWTs are signed with the JWT secret (not the anon/service key).
        # The JWT secret is available as SUPABASE_JWT_SECRET env var, or we try
        # the service role key as a last resort.
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "") or Config.SUPABASE_SERVICE_ROLE_KEY
        if not jwt_secret:
            raise HTTPException(status_code=401, detail="JWT verification not configured")

        payload = jose_jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing 'sub' claim")
        return str(user_id)

    except HTTPException:
        raise
    except ImportError:
        logger.warning("python-jose not installed — cannot decode JWT manually")
        raise HTTPException(status_code=401, detail="Auth verification unavailable")
    except Exception as exc:
        logger.warning("JWT decode failed: {}", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_optional_user(authorization: str = Header(None)) -> Optional[str]:
    """
    Like ``get_current_user`` but returns ``None`` instead of raising
    when no valid token is provided.  Used for endpoints that work
    both with and without auth.
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


# ──────────────────────────────────────────────────────────────────
# NLP Integration Helpers
# ──────────────────────────────────────────────────────────────────

def classify_clauses_in_text(text: str) -> list[dict[str, Any]]:
    """Classify each paragraph into clause types with risk analysis."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    detected_clauses = []

    current_idx = 0
    for p in paragraphs:
        start_idx = text.find(p, current_idx)
        if start_idx == -1:
            start_idx = current_idx
        end_idx = start_idx + len(p)
        current_idx = end_idx

        if len(p) < 15:
            continue

        classification = nlp_engine.classify(p)
        clause_type = classification["clause"]
        confidence = classification["confidence"]

        if clause_type != "Unknown" and confidence >= 40.0:
            risk = risk_engine.analyze(p, clause_type)
            detected_clauses.append({
                "type": clause_type,
                "text": p,
                "confidence": confidence,
                "risk_score": risk["risk_score"],
                "risk_level": risk["risk_level"],
                "risk_factors": risk["risk_factors"],
                "startIndex": start_idx,
                "endIndex": end_idx,
            })

    return detected_clauses


def generate_contract_summary(
    detected_clauses: list[dict[str, Any]],
    primary_analysis: dict[str, Any],
) -> list[str]:
    """Generate a bulleted summary from detected clauses."""
    summary = []
    primary_clause = primary_analysis.get("clause", "Unknown")
    primary_risk = primary_analysis.get("risk_level", "Low")

    if primary_clause != "Unknown":
        summary.append(
            f"Identified primarily as a {primary_clause} clause/document "
            f"with {primary_risk.lower()} risk."
        )

    types_found = set(c["type"] for c in detected_clauses)
    if "Confidentiality" in types_found:
        summary.append("Contains confidentiality/non-disclosure obligations.")
    if "Termination" in types_found:
        summary.append("Specifies conditions for contract termination.")
    if "Liability" in types_found:
        liability_clauses = [c for c in detected_clauses if c["type"] == "Liability"]
        has_high = any(c["risk_level"] == "High" for c in liability_clauses)
        if has_high:
            summary.append(
                "Warning: High liability exposure detected "
                "(broad or uncapped liability language)."
            )
        else:
            summary.append("Contains limitation of liability provisions.")
    if "Arbitration" in types_found:
        summary.append("Includes binding arbitration for dispute resolution.")
    if "Governing Law" in types_found:
        summary.append("Governing law and jurisdiction terms are defined.")
    if "Renewal" in types_found:
        summary.append("Renewal terms or auto-extension provisions detected.")
    if "Indemnification" in types_found:
        summary.append("Contains mutual or unilateral indemnification protection.")
    if "Non-Compete" in types_found:
        summary.append("Includes non-compete or non-solicitation restrictions.")

    if not summary:
        summary.append(
            "No specific high-risk or standard legal clauses were "
            "identified in the text."
        )

    return summary


# ──────────────────────────────────────────────────────────────────
# Endpoints — Health & Pipeline Status
# ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "IntelliAnalyze AI OCR Pipeline",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "document_loader": "ready",
            "pdf_parser": "ready",
            "docx_parser": "ready",
            "ocr_engine": "ready",
            "scan_detector": "ready",
            "text_cleaner": "ready",
            "json_formatter": "ready",
            "nlp_engine": "ready",
            "risk_engine": "ready",
            "agent_pipeline": "ready" if _AGENT_PIPELINE_AVAILABLE else "unavailable",
            "supabase": "ready" if (_SERVICES_AVAILABLE and get_supabase_client and get_supabase_client() is not None) else "unavailable",
            "vector_search": "ready" if _SERVICES_AVAILABLE else "unavailable",
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
        "agent_pipeline_available": _AGENT_PIPELINE_AVAILABLE,
        "services_available": _SERVICES_AVAILABLE,
    }


# ──────────────────────────────────────────────────────────────────
# Endpoints — Legacy Upload (OCR only)
# ──────────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_and_process(file: UploadFile = File(...)):
    """
    Upload a document and process through the OCR pipeline.
    (Legacy endpoint — no auth required, no Supabase storage.)
    """
    start_time = time.time()
    file_id = str(uuid.uuid4())[:12]

    try:
        safe_name = file.filename.replace(" ", "_")
        save_path = UPLOAD_DIR / f"{file_id}_{safe_name}"

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        file_size_mb = len(content) / (1024 * 1024)

        try:
            doc_info = document_loader.load(save_path)
        except DocumentLoadError as e:
            raise HTTPException(status_code=400, detail=str(e))

        metadata = doc_info.get("metadata", {})
        category = metadata.get("category", "unknown")

        extracted_text = ""
        pages = 0
        processing_method = "native"
        ocr_confidence = None

        if category == "pdf":
            try:
                result = pdf_parser.extract(save_path)
                pages = len(result.get("pages", []))

                if result.get("needs_ocr", False):
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

        is_ocr = processing_method == "ocr"
        clean_result = text_cleaner.clean(extracted_text, is_ocr=is_ocr)
        clean_text = clean_result["clean_text"]
        sentences = clean_result.get("sentences", [])

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

        output_path = json_formatter.save(document)

        document["file_id"] = file_id
        document["original_size_mb"] = round(file_size_mb, 3)
        processed_docs[document["document_id"]] = document

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


# ──────────────────────────────────────────────────────────────────
# Endpoints — In-Memory Document List (backward compatibility)
# ──────────────────────────────────────────────────────────────────

@app.get("/api/documents")
async def list_documents():
    """List all in-memory processed documents."""
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
    """Get a specific in-memory processed document by ID."""
    if doc_id not in processed_docs:
        raise HTTPException(status_code=404, detail="Document not found")
    return processed_docs[doc_id]


# ──────────────────────────────────────────────────────────────────
# Endpoint — /upload-contract (Full NLP pipeline + optional Supabase)
# ──────────────────────────────────────────────────────────────────

@app.post("/upload-contract")
async def upload_contract_nlp(
    file: UploadFile = File(...),
    user_id: Optional[str] = Depends(get_optional_user),
):
    """
    Full pipeline: Upload → OCR → Clean → NLP → Risk → Response.

    Supports: PDF, DOCX, DOC, TXT, JPG, PNG, TIFF, BMP.
    If the user is authenticated the results are saved to MongoDB and
    vector embeddings are generated.

    When AgentPipeline is available, it runs the 7-agent chain. Otherwise
    the inline (legacy) pipeline logic is used.
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

        file_size_mb = round(len(content) / (1024 * 1024), 3)

        # ------------------------------------------------------------------
        # Try the AgentPipeline first
        # ------------------------------------------------------------------
        if _AGENT_PIPELINE_AVAILABLE:
            try:
                pipeline = AgentPipeline()
                result = pipeline.run(str(save_path), file.filename or safe_name)

                elapsed = time.time() - start_time
                result["processing_time_seconds"] = round(elapsed, 2)
                result["file_size_mb"] = file_size_mb

                # Persist to Supabase if authenticated
                contract_id = None
                if user_id and _SERVICES_AVAILABLE and database is not None:
                    result["filename"] = file.filename or safe_name
                    saved = database.save_contract(user_id, result)
                    contract_id = saved.get("contract_id") if saved else None
                    result["contract_id"] = contract_id

                # Store vector embeddings
                if user_id and contract_id and _SERVICES_AVAILABLE and vector_search is not None:
                    clean_text = result.get("contract_text") or result.get("clean_text", "")
                    if clean_text:
                        try:
                            vector_search.store_embeddings(contract_id, clean_text, user_id)
                        except Exception as ve:
                            logger.warning("Embedding storage failed: {}", ve)

                # Also save in-memory for legacy endpoints
                doc_id = result.get("document_id", file_id)
                processed_docs[doc_id] = result

                # Cleanup
                try:
                    save_path.unlink()
                except Exception:
                    pass

                logger.info(
                    "upload-contract (AgentPipeline) complete | file={} | time={:.2f}s",
                    safe_name, elapsed,
                )
                return result

            except Exception as agent_exc:
                logger.warning(
                    "AgentPipeline failed ({}), falling back to inline pipeline",
                    agent_exc,
                )
                # Fall through to inline pipeline

        # ------------------------------------------------------------------
        # Inline (legacy) pipeline fallback
        # ------------------------------------------------------------------
        file_ext = save_path.suffix.lower()
        extracted_text = ""

        # ── Image files ──
        if file_ext in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"):
            from PIL import Image as PILImage
            try:
                img = PILImage.open(save_path)
                ocr_result = ocr_engine.ocr_image(img, preprocess=True, preset="standard")
                extracted_text = ocr_result.get("text", "")
                used_ocr = True
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Image OCR failed: {e}")

        # ── PDF files ──
        elif file_ext == ".pdf":
            try:
                result = pdf_parser.extract(save_path)
                extracted_text = result.get("full_text", "")

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

            except (PDFParseError, Exception) as e:
                logger.warning("PDF extraction failed ({}), attempting OCR fallback", e)
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

        # ── Plain text ──
        elif file_ext == ".txt":
            try:
                doc_info = document_loader.load(save_path)
                extracted_text = doc_info.get("text", "")
            except Exception:
                with open(save_path, "r", encoding="utf-8", errors="ignore") as tf:
                    extracted_text = tf.read()

        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type: {file_ext}. "
                    "Supported: PDF, DOCX, TXT, JPG, PNG, TIFF, BMP"
                ),
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted. For handwritten documents, ensure the image is clear and well-lit.",
            )

        # Step 3: Clean text
        clean_result = text_cleaner.clean(extracted_text, is_ocr=used_ocr)
        clean_text = clean_result["clean_text"]

        # Step 4: NLP + Risk
        analysis = risk_engine.full_analysis(clean_text)
        detected_clauses = classify_clauses_in_text(clean_text)
        risk_details = risk_engine.analyze(clean_text, analysis["clause"])
        risk_factors = risk_details.get("risk_factors", [])
        summary = generate_contract_summary(detected_clauses, analysis)

        # Page count
        pages = 1
        if file_ext == ".pdf":
            try:
                pages = pdf_parser.extract_metadata(save_path).get("num_pages", 1)
            except Exception:
                pages = 1

        elapsed = time.time() - start_time
        logger.info(
            "upload-contract complete | file={} | ocr={} | clause={} | time={:.2f}s",
            safe_name, used_ocr, analysis["clause"], elapsed,
        )

        # Format and save document
        document = json_formatter.format_document(
            filename=file.filename or "uploaded_contract",
            clean_text=clean_text,
            pages=pages,
            processing_method="ocr" if used_ocr else "native",
            metadata={"file_size_mb": file_size_mb},
            sentences=clean_result.get("sentences", []),
            confidence=analysis["confidence"] if used_ocr else None,
            processing_time=elapsed,
        )

        document["clause"] = analysis["clause"]
        document["confidence"] = analysis["confidence"]
        document["risk_score"] = analysis["risk_score"]
        document["risk_level"] = analysis["risk_level"]
        document["risk_factors"] = risk_factors
        document["summary"] = summary
        document["clauses"] = detected_clauses

        # Save to disk
        output_path = json_formatter.save(document)

        # Store in memory
        document["file_id"] = file_id
        document["original_size_mb"] = file_size_mb
        processed_docs[document["document_id"]] = document

        # ── Persist to MongoDB if authenticated ──
        contract_id = None
        if user_id and _SERVICES_AVAILABLE and database is not None:
            result_data = {
                **document,
                "contract_text": clean_text,
                "processing_time_seconds": round(elapsed, 2),
                "file_size_mb": file_size_mb,
            }
            saved = database.save_contract(user_id, result_data)
            contract_id = saved.get("contract_id") if saved else None

        # Store vector embeddings
        if user_id and contract_id and _SERVICES_AVAILABLE and vector_search is not None:
            try:
                vector_search.store_embeddings(contract_id, clean_text, user_id)
            except Exception as ve:
                logger.warning("Embedding storage failed: {}", ve)

        # Cleanup
        try:
            save_path.unlink()
        except Exception:
            pass

        response_payload = {
            "clause": analysis["clause"],
            "confidence": analysis["confidence"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "contract_text": clean_text,
            "summary": summary,
            "risk_factors": risk_factors,
            "clauses": detected_clauses,
            "document_id": document["document_id"],
        }
        if contract_id:
            response_payload["contract_id"] = contract_id

        return response_payload

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Processing failed: {str(e)}"},
        )


# ──────────────────────────────────────────────────────────────────
# Endpoint — /analyze-text (no auth required)
# ──────────────────────────────────────────────────────────────────

@app.post("/analyze-text")
async def analyze_text(
    request: AnalyzeTextRequest,
    user_id: Optional[str] = Depends(get_optional_user),
):
    """
    Text-only pipeline: Accept contract text → NLP → Risk → Response.
    """
    contract_text = request.contract_text

    if not contract_text or not contract_text.strip():
        raise HTTPException(status_code=400, detail="contract_text must not be empty.")

    try:
        contract_text = contract_text.strip()
        analysis = risk_engine.full_analysis(contract_text)
        detected_clauses = classify_clauses_in_text(contract_text)
        risk_details = risk_engine.analyze(contract_text, analysis["clause"])
        risk_factors = risk_details.get("risk_factors", [])
        summary = generate_contract_summary(detected_clauses, analysis)

        # Save to processed_docs
        document_id = json_formatter.generate_document_id("pasted_text.txt", contract_text)
        document = {
            "document_id": document_id,
            "filename": "Pasted Text",
            "pages": 1,
            "document_type": json_formatter.determine_document_type("pasted_text.txt", contract_text),
            "metadata": {
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "pipeline_version": "2.0.0",
                "text_length": len(contract_text),
                "word_count": len(contract_text.split()),
            },
            "clean_text": contract_text,
            "text_preview": contract_text[:500],
            "processing_method": "native",
            "clause": analysis["clause"],
            "confidence": analysis["confidence"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "risk_factors": risk_factors,
            "summary": summary,
            "clauses": detected_clauses,
        }

        processed_docs[document_id] = document

        # Persist to Supabase if authenticated
        contract_id = None
        if user_id and _SERVICES_AVAILABLE and database is not None:
            saved = database.save_contract(user_id, {
                **document,
                "contract_text": contract_text,
            })
            contract_id = saved.get("id")

        response = {
            "clause": analysis["clause"],
            "confidence": analysis["confidence"],
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "contract_text": contract_text,
            "summary": summary,
            "risk_factors": risk_factors,
            "clauses": detected_clauses,
            "document_id": document_id,
        }
        if contract_id:
            response["contract_id"] = contract_id

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Analysis failed: {str(e)}"},
        )


# ──────────────────────────────────────────────────────────────────
# Endpoints — MongoDB Contract CRUD (auth required)
# ──────────────────────────────────────────────────────────────────

@app.get("/api/contracts")
async def list_contracts(user_id: str = Depends(get_current_user)):
    """Return all contracts for the authenticated user."""
    if not _SERVICES_AVAILABLE or database is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")

    contracts = database.get_contracts(user_id)
    return {"contracts": contracts, "total": len(contracts)}


@app.get("/api/contracts/{contract_id}")
async def get_contract(contract_id: str, user_id: str = Depends(get_current_user)):
    """Return a single contract by ID for the authenticated user."""
    if not _SERVICES_AVAILABLE or database is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")

    contract = database.get_contract(contract_id, user_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    return contract


@app.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: str, user_id: str = Depends(get_current_user)):
    """Delete a contract owned by the authenticated user."""
    if not _SERVICES_AVAILABLE or database is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")

    deleted = database.delete_contract(contract_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contract not found or already deleted")

    return {"status": "deleted", "contract_id": contract_id}


# ──────────────────────────────────────────────────────────────────
# Endpoint — Semantic Search (auth required)
# ──────────────────────────────────────────────────────────────────

@app.post("/api/search")
async def semantic_search(
    request: SearchRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Semantic search across a user's contracts using vector embeddings.
    """
    if not _SERVICES_AVAILABLE or vector_search is None:
        raise HTTPException(status_code=503, detail="Vector search service unavailable")

    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    results = vector_search.search(
        query=request.query.strip(),
        user_id=user_id,
        limit=request.limit,
    )

    return {
        "query": request.query,
        "results": results,
        "total": len(results),
    }


# ──────────────────────────────────────────────────────────────────
# Endpoint — PDF Report Download (auth required)
# ──────────────────────────────────────────────────────────────────

@app.get("/api/report/{contract_id}/pdf")
async def download_report_pdf(
    contract_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Generate and download a professional PDF report for a contract.
    """
    if not _SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Services unavailable")

    if database is None:
        raise HTTPException(status_code=503, detail="Database service unavailable")

    if pdf_report is None:
        raise HTTPException(status_code=503, detail="PDF report service unavailable")

    # Fetch contract from MongoDB
    contract = database.get_contract(contract_id, user_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    try:
        filepath = pdf_report.generate_report(contract)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.error("PDF report generation failed: {}", exc)
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    filename = Path(filepath).name
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/pdf",
    )


# ──────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
