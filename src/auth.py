# Re-exports for backward compatibility — auth logic lives in src.supabase.auth
from src.supabase.auth import (
    bearer_scheme,
    bearer_scheme_required,
    get_client,
    get_current_user,
    optional_auth,
    verify_token,
)

__all__ = [
    "bearer_scheme",
    "bearer_scheme_required",
    "get_client",
    "get_current_user",
    "optional_auth",
    "verify_token",
]
