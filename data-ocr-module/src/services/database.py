"""
Database Service — MongoDB CRUD Operations.

Handles all contract data persistence using MongoDB.
Supabase is used only for authentication; all data storage goes through MongoDB.
"""

import time
from datetime import datetime, timezone
from typing import Any

from src.utils.config import Config
from src.utils.logger import logger

# ── MongoDB client (lazy singleton) ───────────────────────────────
_mongo_client = None
_mongo_db = None


def _get_db():
    """Get MongoDB database instance (lazy singleton)."""
    global _mongo_client, _mongo_db
    if _mongo_db is not None:
        return _mongo_db

    if not Config.MONGODB_URI:
        logger.warning("MONGODB_URI not set — database operations will be skipped")
        return None

    try:
        from pymongo import MongoClient

        # Build connection kwargs
        conn_kwargs = {
            "serverSelectionTimeoutMS": 8000,
            "connectTimeoutMS": 8000,
        }

        # Use certifi CA bundle for Python 3.14+ SSL compatibility
        try:
            import certifi
            conn_kwargs["tlsCAFile"] = certifi.where()
            logger.info("Using certifi CA bundle for MongoDB TLS")
        except ImportError:
            logger.warning("certifi not installed — using system CA bundle")

        # Clean up URI: remove tlsInsecure params since we provide proper CA
        uri = Config.MONGODB_URI
        for param in ["&tlsInsecure=true", "?tlsInsecure=true", "&tls=true"]:
            uri = uri.replace(param, "")
        # Ensure tls=true is set cleanly
        if "tls=" not in uri:
            sep = "&" if "?" in uri else "?"
            uri = uri + sep + "tls=true"

        _mongo_client = MongoClient(uri, **conn_kwargs)

        # Test connection
        _mongo_client.admin.command("ping")
        _mongo_db = _mongo_client[Config.MONGODB_DB_NAME]
        logger.info("✅ MongoDB connected: database='{}'", Config.MONGODB_DB_NAME)
        
        # Create indexes
        _mongo_db.contracts.create_index("user_id")
        _mongo_db.contracts.create_index([("created_at", -1)])
        _mongo_db.users.create_index("supabase_id", unique=True)
        _mongo_db.contract_embeddings.create_index("contract_id")
        _mongo_db.contract_embeddings.create_index("user_id")
        
        return _mongo_db
    except Exception as e:
        logger.error("❌ MongoDB connection failed: {}", e)
        return None


def save_user(supabase_id: str, email: str, full_name: str = "", avatar_url: str = "") -> dict | None:
    """
    Create or update user profile in MongoDB.
    Called after Supabase auth verification.
    """
    db = _get_db()
    if db is None:
        return None
    try:
        now = datetime.now(timezone.utc)
        result = db.users.update_one(
            {"supabase_id": supabase_id},
            {
                "$set": {
                    "email": email,
                    "full_name": full_name,
                    "avatar_url": avatar_url,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "supabase_id": supabase_id,
                    "role": "member",
                    "created_at": now,
                },
            },
            upsert=True,
        )
        user = db.users.find_one({"supabase_id": supabase_id}, {"_id": 0})
        logger.info("User saved: supabase_id={}", supabase_id[:8])
        return user
    except Exception as e:
        logger.error("Failed to save user: {}", e)
        return None


def get_user_profile(user_id: str) -> dict | None:
    """Get user profile by Supabase ID."""
    db = _get_db()
    if db is None:
        return None
    try:
        user = db.users.find_one({"supabase_id": user_id}, {"_id": 0})
        return user
    except Exception as e:
        logger.error("Failed to get user profile: {}", e)
        return None


def save_contract(user_id: str, data: dict) -> dict | None:
    """
    Save contract analysis result to MongoDB.

    Args:
        user_id: Supabase user ID.
        data: Analysis result dict from the agent pipeline.

    Returns:
        Saved document with generated ID, or None on failure.
    """
    db = _get_db()
    if db is None:
        logger.warning("MongoDB not available — contract not saved")
        return None

    try:
        import uuid
        now = datetime.now(timezone.utc)
        contract_id = str(uuid.uuid4())

        document = {
            "contract_id": contract_id,
            "user_id": user_id,
            "filename": data.get("filename", "unknown"),
            "document_type": data.get("document_type", "unknown"),
            "pages": data.get("pages", 0),
            "processing_method": data.get("ocr_method", data.get("processing_method", "native")),
            "ocr_confidence": data.get("ocr_confidence", 0.0),
            "clean_text": data.get("clean_text", ""),
            "text_preview": data.get("clean_text", "")[:500] if data.get("clean_text") else "",
            # NLP
            "primary_clause": data.get("primary_clause", data.get("clause", "")),
            "primary_confidence": data.get("primary_confidence", data.get("confidence", 0.0)),
            "overall_risk_score": data.get("overall_risk_score", data.get("risk_score", 0)),
            "overall_risk_level": data.get("overall_risk_level", data.get("risk_level", "Low")),
            "completeness_score": data.get("completeness_score", 0),
            # AI Summary
            "ai_summary": data.get("ai_summary", ""),
            "key_findings": data.get("key_findings", []),
            "recommendations": data.get("recommendations", []),
            # Detailed Analysis
            "entities": data.get("entities", {}),
            "clauses": data.get("clauses", []),
            "clause_risks": data.get("clause_risks", []),
            "risk_factors": data.get("risk_factors", []),
            "missing_clauses": data.get("missing_clauses", []),
            # Metadata
            "file_size_mb": data.get("file_size_mb", 0.0),
            "processing_time_seconds": data.get("processing_time_seconds", 0.0),
            "agent_logs": data.get("agent_logs", []),
            "created_at": now,
            "updated_at": now,
        }

        db.contracts.insert_one(document)

        # Remove MongoDB ObjectId for JSON serialization
        document.pop("_id", None)

        logger.info(
            "Contract saved: id={} | user={} | file={}",
            contract_id,
            user_id[:8],
            document["filename"],
        )
        return document

    except Exception as e:
        logger.error("Failed to save contract: {}", e)
        return None


def get_contracts(user_id: str) -> list[dict]:
    """Get all contracts for a user, ordered by created_at desc."""
    db = _get_db()
    if db is None:
        return []
    try:
        contracts = list(
            db.contracts.find(
                {"user_id": user_id},
                {"_id": 0, "clean_text": 0},  # Exclude large text field
            ).sort("created_at", -1)
        )
        logger.info("Retrieved {} contracts for user {}", len(contracts), user_id[:8])
        return contracts
    except Exception as e:
        logger.error("Failed to get contracts: {}", e)
        return []


def get_contract(contract_id: str, user_id: str) -> dict | None:
    """Get a single contract by ID, verifying ownership."""
    db = _get_db()
    if db is None:
        return None
    try:
        contract = db.contracts.find_one(
            {"contract_id": contract_id, "user_id": user_id},
            {"_id": 0},
        )
        if contract:
            logger.info("Retrieved contract: {}", contract_id[:8])
        return contract
    except Exception as e:
        logger.error("Failed to get contract: {}", e)
        return None


def delete_contract(contract_id: str, user_id: str) -> bool:
    """Delete a contract and its embeddings, verifying ownership."""
    db = _get_db()
    if db is None:
        return False
    try:
        result = db.contracts.delete_one(
            {"contract_id": contract_id, "user_id": user_id}
        )
        if result.deleted_count > 0:
            # Also delete associated embeddings
            db.contract_embeddings.delete_many({"contract_id": contract_id})
            logger.info("Deleted contract: {}", contract_id[:8])
            return True
        return False
    except Exception as e:
        logger.error("Failed to delete contract: {}", e)
        return False


def get_dashboard_stats(user_id: str) -> dict:
    """Get aggregated dashboard statistics for a user."""
    db = _get_db()
    if db is None:
        return {"total_contracts": 0, "avg_risk_score": 0, "high_risk_count": 0}
    try:
        contracts = list(
            db.contracts.find(
                {"user_id": user_id},
                {"overall_risk_score": 1, "overall_risk_level": 1, "completeness_score": 1, "_id": 0},
            )
        )
        total = len(contracts)
        if total == 0:
            return {"total_contracts": 0, "avg_risk_score": 0, "high_risk_count": 0}

        risk_scores = [c.get("overall_risk_score", 0) for c in contracts]
        high_risk = sum(1 for c in contracts if c.get("overall_risk_level") == "High")

        return {
            "total_contracts": total,
            "avg_risk_score": round(sum(risk_scores) / total, 1),
            "high_risk_count": high_risk,
            "avg_completeness": round(
                sum(c.get("completeness_score", 0) for c in contracts) / total, 1
            ),
        }
    except Exception as e:
        logger.error("Failed to get dashboard stats: {}", e)
        return {"total_contracts": 0, "avg_risk_score": 0, "high_risk_count": 0}
