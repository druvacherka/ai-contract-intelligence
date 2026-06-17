"""
Supabase client singleton.

Provides a lazily-initialized Supabase client using service-role credentials.
Gracefully handles missing dependencies or configuration.
"""

from __future__ import annotations

from src.utils.config import Config
from src.utils.logger import logger

# Guard: supabase SDK is optional
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None  # type: ignore[assignment]
    Client = None  # type: ignore[assignment,misc]
    logger.warning("supabase-py is not installed — Supabase features disabled")

_client: "Client | None" = None
_initialized: bool = False


def get_supabase_client() -> "Client | None":
    """
    Return a singleton Supabase client.

    Returns ``None`` when:
    - The ``supabase`` package is not installed.
    - ``SUPABASE_URL`` or ``SUPABASE_SERVICE_ROLE_KEY`` are empty / not set.
    """
    global _client, _initialized

    if _initialized:
        return _client

    _initialized = True

    if create_client is None:
        logger.warning("Supabase SDK not available — returning None")
        return None

    url = Config.SUPABASE_URL
    key = Config.SUPABASE_SERVICE_ROLE_KEY

    if not url or not key:
        logger.warning(
            "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured — "
            "Supabase features disabled"
        )
        return None

    try:
        _client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
    except Exception as exc:
        logger.error("Failed to create Supabase client: {}", exc)
        _client = None

    return _client
