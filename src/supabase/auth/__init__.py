import logging
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from src.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None

bearer_scheme = HTTPBearer(auto_error=False)
bearer_scheme_required = HTTPBearer(auto_error=True)


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_anon_key)
    return _client


def verify_token(token: str) -> dict[str, Any]:
    """Verify a Supabase JWT and return user data. Raises HTTPException on failure."""
    try:
        response = get_client().auth.get_user(token)
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = response.user
        return {"sub": user.id, "email": user.email, **(user.user_metadata or {})}
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Token verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme_required),
) -> dict[str, Any]:
    """FastAPI dependency that requires a valid Supabase auth token."""
    return verify_token(credentials.credentials)


async def optional_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any] | None:
    """FastAPI dependency for optional auth. Returns user data or None."""
    if credentials is None:
        return None
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None
