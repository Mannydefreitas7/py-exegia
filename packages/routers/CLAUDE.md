# REST Routers Module

FastAPI REST endpoints for dataset management and user data operations (legacy/compatibility layer).

## Overview

REST endpoints complement the primary GraphQL API, providing compatibility for clients that prefer REST and handling file downloads/uploads.

## Architecture

```
HTTP Request (REST)
    ↓
FastAPI Router
    ↓
[Storage Service | Database Models]
    ↓
HTTP Response (JSON)
```

## Files

```
app/routers/
├── datasets.py      # Dataset management endpoints
└── user_data.py     # User notes/favorites endpoints
```

## Dataset Endpoints (`datasets.py`)

### List Datasets

```http
GET /api/datasets?category=bibles
```

**Response:**

```json
{
  "datasets": [
    {
      "id": "BHSA",
      "name": "Biblia Hebraica Stuttgartensia Amstelodamensis",
      "language": "Hebrew",
      "version": "2021",
      "size": 45678901,
      "category": "bibles",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Get Dataset Info

```http
GET /api/datasets/:id
```

**Response:**

```json
{
  "id": "BHSA",
  "name": "Biblia Hebraica Stuttgartensia Amstelodamensis",
  "description": "Hebrew Bible with morphological annotations",
  "language": "Hebrew",
  "version": "2021",
  "size": 45678901,
  "features": ["pos", "lemma", "tense", "gender", ...],
  "node_types": ["word", "phrase", "clause", "sentence", ...]
}
```

### Download Dataset

```http
GET /api/datasets/:id/download
```

**Response:** ZIP file (binary stream)

**Headers:**

```
Content-Type: application/zip
Content-Disposition: attachment; filename="BHSA.zip"
Content-Length: 45678901
```

### Mark Dataset as Downloaded

**Request:**

```json
{
  "local_path": "{user-home-path}/.exegia/datasets/BHSA",
  "version": "2021"
}
```

**Response:**

```json
{
  "id": "abc123",
  "dataset_id": "BHSA",
  "local_path": "{user-home-path}/.exegia/datasets/BHSA",
  "downloaded_at": "2024-01-15T10:30:00Z"
}
```

### Remove Dataset

```http
DELETE /api/datasets/:id
```

**Response:**

```json
{
  "success": true,
  "message": "Dataset removed from library"
}
```

## User Data Endpoints (`user_data.py`)

All endpoints require authentication (JWT token in `Authorization: Bearer <token>` header).

### Notes

#### List Notes

```http
GET /api/notes?dataset_id=BHSA&reference=Genesis 1:1
```

**Response:**

```json
{
  "notes": [
    {
      "id": "note-123",
      "dataset_id": "BHSA",
      "reference": "Genesis 1:1",
      "content": "This verse describes creation",
      "tags": ["creation", "beginning"],
      "created_at": "2024-01-10T12:00:00Z",
      "updated_at": "2024-01-10T12:00:00Z"
    }
  ],
  "total": 1
}
```

#### Create Note

```http
POST /api/notes
```

**Request:**

```json
{
  "dataset_id": "BHSA",
  "reference": "Genesis 1:1",
  "content": "This verse describes creation",
  "tags": ["creation", "beginning"]
}
```

**Response:**

```json
{
  "id": "note-123",
  "dataset_id": "BHSA",
  "reference": "Genesis 1:1",
  "content": "This verse describes creation",
  "tags": ["creation", "beginning"],
  "created_at": "2024-01-10T12:00:00Z"
}
```

#### Update Note

```http
PUT /api/notes/:id
```

**Request:**

```json
{
  "content": "Updated note content",
  "tags": ["creation"]
}
```

#### Delete Note

```http
DELETE /api/notes/:id
```

### Favorites

#### List Favorites

```http
GET /api/favorites?dataset_id=BHSA
```

**Response:**

```json
{
  "favorites": [
    {
      "id": "fav-123",
      "dataset_id": "BHSA",
      "reference": "John 3:16",
      "note": "For God so loved the world",
      "created_at": "2024-01-10T12:00:00Z"
    }
  ],
  "total": 1
}
```

#### Add Favorite

```http
POST /api/favorites
```

**Request:**

```json
{
  "dataset_id": "BHSA",
  "reference": "John 3:16",
  "note": "My favorite verse"
}
```

#### Remove Favorite

```http
DELETE /api/favorites/:id
```

## Authentication

All user-specific endpoints require Supabase JWT authentication:

```python
from app.auth import get_current_user
from fastapi import Depends

@router.get("/notes")
async def get_notes(user = Depends(get_current_user)):
    # user contains authenticated user info
    notes = db.query(Note).filter(Note.user_id == user.id).all()
    return {"notes": notes}
```

### Token Usage

```http
GET /api/notes
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid dataset_id",
  "details": "Dataset 'INVALID' not found"
}
```

### 401 Unauthorized

```json
{
  "error": "Authentication required",
  "details": "Missing or invalid authorization token"
}
```

## Router Implementation

```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.models import Note
from app.database import get_db

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/notes")
async def get_notes(
    dataset_id: Optional[str] = None,
    reference: Optional[str] = None,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    query = db.query(Note).filter(Note.user_id == user.id)

    if dataset_id:
        query = query.filter(Note.dataset_id == dataset_id)
    if reference:
        query = query.filter(Note.reference == reference)

    notes = query.all()
    return {"notes": notes, "total": len(notes)}

@router.post("/notes")
async def create_note(
    note_data: NoteCreate,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    note = Note(
        user_id=user.id,
        dataset_id=note_data.dataset_id,
        reference=note_data.reference,
        content=note_data.content,
        tags=note_data.tags
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    return note
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Desktop app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
