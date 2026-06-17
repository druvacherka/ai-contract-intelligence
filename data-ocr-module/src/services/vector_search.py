"""
Vector Search Service — Embedding Generation & Semantic Search.

Uses sentence-transformers for embeddings and MongoDB for storage.
Provides semantic search across contract documents.
"""

from typing import Any

from src.utils.config import Config
from src.utils.logger import logger

# ── Lazy-loaded model ─────────────────────────────────────────────
_model = None
_model_available = None  # None = not checked yet


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model, _model_available
    if _model_available is False:
        return None
    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer
        model_name = Config.EMBEDDING_MODEL
        logger.info("Loading embedding model: {} ...", model_name)
        _model = SentenceTransformer(model_name)
        _model_available = True
        logger.info("Embedding model loaded successfully")
        return _model
    except Exception as e:
        _model_available = False
        logger.warning("sentence-transformers not available: {}", e)
        return None


def _get_db():
    """Get MongoDB database for embeddings."""
    try:
        from src.services.database import _get_db as get_mongo_db
        return get_mongo_db()
    except Exception:
        return None


def generate_embedding(text: str) -> list[float] | None:
    """
    Generate a 384-dimensional embedding for the given text.

    Args:
        text: Input text to embed.

    Returns:
        List of 384 floats, or None if model unavailable.
    """
    model = _get_model()
    if model is None:
        return None

    try:
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    except Exception as e:
        logger.error("Embedding generation failed: {}", e)
        return None


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: Full document text.
        chunk_size: Target characters per chunk.
        overlap: Character overlap between chunks.

    Returns:
        List of text chunks.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks: list[str] = []
    sentences = text.replace("\n", " ").split(". ")
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}. {sentence}" if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Start new chunk with overlap from end of previous
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-overlap:]
                current_chunk = f"{overlap_text} {sentence}"
            else:
                current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def store_embeddings(contract_id: str, text: str, user_id: str = "") -> int:
    """
    Chunk text, generate embeddings, and store in MongoDB.

    Args:
        contract_id: Contract document ID.
        text: Full contract text.
        user_id: User ID for scoped search.

    Returns:
        Number of chunks stored, or 0 on failure.
    """
    model = _get_model()
    if model is None:
        logger.info("Embedding model not available — skipping vector storage")
        return 0

    db = _get_db()
    if db is None:
        logger.warning("MongoDB not available — skipping vector storage")
        return 0

    try:
        from datetime import datetime, timezone

        chunks = _chunk_text(text)
        if not chunks:
            return 0

        logger.info("Storing {} embedding chunks for contract {}", len(chunks), contract_id[:8])

        # Generate embeddings in batch
        embeddings = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)

        # Build documents for MongoDB
        documents = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            documents.append({
                "contract_id": contract_id,
                "user_id": user_id,
                "chunk_index": i,
                "chunk_text": chunk,
                "embedding": embedding.tolist(),
                "created_at": datetime.now(timezone.utc),
            })

        # Delete existing embeddings for this contract
        db.contract_embeddings.delete_many({"contract_id": contract_id})

        # Insert new embeddings
        db.contract_embeddings.insert_many(documents)

        logger.info("Stored {} embeddings for contract {}", len(documents), contract_id[:8])
        return len(documents)

    except Exception as e:
        logger.error("Failed to store embeddings: {}", e)
        return 0


def search(query: str, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Semantic search across contract embeddings.

    Generates embedding for the query, then computes cosine similarity
    against stored embeddings in MongoDB.

    Args:
        query: Search query text.
        user_id: User ID to scope search.
        limit: Maximum results to return.

    Returns:
        List of matching results with similarity scores.
    """
    model = _get_model()
    if model is None:
        logger.info("Embedding model not available — cannot search")
        return []

    db = _get_db()
    if db is None:
        return []

    try:
        import numpy as np

        # Generate query embedding
        query_embedding = model.encode(query, normalize_embeddings=True)

        # Get all embeddings for this user
        cursor = db.contract_embeddings.find(
            {"user_id": user_id},
            {"_id": 0, "contract_id": 1, "chunk_text": 1, "embedding": 1},
        )

        results = []
        for doc in cursor:
            stored_embedding = np.array(doc["embedding"])
            # Cosine similarity (embeddings are normalized, so dot product = cosine)
            similarity = float(np.dot(query_embedding, stored_embedding))
            if similarity > 0.3:  # threshold
                results.append({
                    "contract_id": doc["contract_id"],
                    "chunk_text": doc["chunk_text"],
                    "similarity": round(similarity, 4),
                })

        # Sort by similarity desc, take top N
        results.sort(key=lambda x: x["similarity"], reverse=True)
        results = results[:limit]

        # Enrich with contract metadata
        enriched = []
        seen_contracts = set()
        for r in results:
            cid = r["contract_id"]
            if cid in seen_contracts:
                continue
            seen_contracts.add(cid)

            contract = db.contracts.find_one(
                {"contract_id": cid, "user_id": user_id},
                {"_id": 0, "filename": 1, "document_type": 1, "primary_clause": 1,
                 "overall_risk_score": 1, "overall_risk_level": 1, "created_at": 1},
            )
            if contract:
                r.update(contract)
            enriched.append(r)

        logger.info("Vector search for '{}': {} results", query[:50], len(enriched))
        return enriched

    except Exception as e:
        logger.error("Vector search failed: {}", e)
        return []
