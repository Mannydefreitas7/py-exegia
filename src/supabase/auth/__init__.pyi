from typing import Any

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

bearer_scheme: HTTPBearer
bearer_scheme_required: HTTPBearer

def get_client() -> Client: ...
def verify_token(token: str) -> dict[str, Any]: ...
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = ...,
) -> dict[str, Any]: ...
async def optional_auth(
    credentials: HTTPAuthorizationCredentials | None = ...,
) -> dict[str, Any] | None: ...
