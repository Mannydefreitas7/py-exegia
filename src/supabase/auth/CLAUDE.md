# Auth Module — `src.supabase.auth`

Handles Supabase JWT verification and provides FastAPI dependency injection for authenticated routes.

## Location

```
src/supabase/auth/
  __init__.py    # Implementation
  __init__.pyi   # Type stubs (uv build backend stub package)
```

`src/auth.py` is a re-export shim for backward compatibility.

## Public API

```python
from src.supabase.auth import get_current_user, optional_auth, verify_token, get_client
```

| Symbol                   | Type         | Description                               |
| ------------------------ | ------------ | ----------------------------------------- |
| `bearer_scheme`          | `HTTPBearer` | Optional auth scheme (`auto_error=False`) |
| `bearer_scheme_required` | `HTTPBearer` | Required auth scheme (`auto_error=True`)  |
| `get_client()`           | `-> Client`  | Lazy singleton Supabase client            |
| `verify_token(token)`    | `-> dict`    | Verify JWT, return user payload           |
| `get_current_user`       | FastAPI dep  | Require auth; raises 401 on failure       |
| `optional_auth`          | FastAPI dep  | Optional auth; returns `None` if missing  |

## Usage

### Require authentication

```python
from fastapi import Depends
from src.supabase.auth import get_current_user

@router.get("/notes")
async def get_notes(user: dict = Depends(get_current_user)):
    user_id = user["sub"]  # Supabase user UUID
```

### Optional authentication

```python
from src.supabase.auth import optional_auth

@router.get("/public")
async def public_route(user: dict | None = Depends(optional_auth)):
    if user:
        # authenticated path
    else:
        # anonymous path
```

### Direct token verification

```python
from src.supabase.auth import verify_token

payload = verify_token(raw_jwt_string)
# {"sub": "uuid", "email": "user@example.com", ...user_metadata}
```

## User Payload Shape

`verify_token` returns the Supabase user metadata flattened into a dict:

```python
{
    "sub": str,       # Supabase user UUID
    "email": str,     # User email
    # ...any fields from user.user_metadata
}
```

## Error Handling

All auth failures raise `HTTPException(401)` with `WWW-Authenticate: Bearer`.  
Unexpected errors from the Supabase client are caught, logged as warnings, and re-raised as 401.

## Build Backend

The `__init__.pyi` file provides inline type stubs as supported by the uv build backend stub packages feature.  
The parent `src/supabase/__init__.py` re-exports all public symbols so `from src.supabase import get_current_user` also works.

## Authentication

### User Registration

```python
# Sign up
response = supabase.auth.sign_up({
    "email": "user@example.com",
    "password": "securepassword"
})

# Creates user in auth.users
# Triggers profile creation in profiles table
```

### User Login

```python
# Sign in
response = supabase.auth.sign_in_with_password({
    "email": "user@example.com",
    "password": "securepassword"
})

# Returns JWT token
access_token = response.session.access_token
```

### Token Usage

```python
# Set auth token
supabase.auth.set_session(access_token, refresh_token)

# All subsequent queries use this user's context
# RLS policies automatically filter data
notes = supabase.table('notes').select('*').execute()
```

### Auth in FastAPI

```python
from app.auth import get_current_user

@router.get("/notes")
async def get_notes(user = Depends(get_current_user)):
    # user is authenticated
    # RLS ensures they only see their notes
    pass
```
