# BiblePedia API - Architecture Documentation

## Overview

BiblePedia API is a backend service for a desktop Bible study application that provides access to biblical text datasets using Text-Fabric corpus analysis, with GraphQL and REST interfaces.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Desktop Client Application                    │
│              (Windows, macOS, Linux)                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ GraphQL / REST API
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    FastAPI Backend                               │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Strawberry      │         │  Context-Fabric  │             │
│  │  GraphQL Layer   │◄────────┤  Corpus Manager  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                  │
│  ┌──────────────────────────────────────────────┐              │
│  │         Storage Service                       │              │
│  │  (Dataset Download/Upload/Sync)              │              │
│  └──────────────────────────────────────────────┘              │
└──────────────┬──────────────────────────┬────────────────────┘
               │                          │
               │                          │
       ┌───────▼────────┐        ┌───────▼────────┐
       │   Supabase     │        │  Local File    │
       │                │        │  System        │
       │  - Database    │        │                │
       │  - Storage     │        │  /datasets/    │
       │  - Auth        │        │  ├─ bibles/    │
       │  - Functions   │        │  ├─ books/     │
       └────────────────┘        │  ├─ lexicons/  │
                                 │  └─ dicts/     │
                                 └────────────────┘
```

## Design Principles

### 1. Supabase Components

**Database** - PostgreSQL
- User profiles and authentication
- User-generated content (notes, favorites, comments)
- Dataset metadata (which datasets user has downloaded)
- Download history and preferences

**Storage** - Object Storage
- Corpus datasets as zip files
- Organized by category (buckets/folders):
  - `bibles/` - Bible translations (KJV.zip, ESV.zip, etc.)
  - `books/` - Biblical reference books
  - `lexicons/` - Hebrew/Greek lexicons
  - `dictionaries/` - Bible dictionaries

**Functions** - Edge Functions
- Fetch Text-Fabric datasets from Git repositories
- Automated dataset conversion and upload
- Dataset validation and processing

**Auth** - Authentication & Authorization
- User login/signup
- Row Level Security (RLS) for user data
- API key management
- JWT token generation

### 2. Backend Services

**Strawberry GraphQL**
- Primary API layer
- Type-safe schema with Python type hints
- Exposes Context-Fabric operations
- User data CRUD operations
- Dataset discovery and management

**Context-Fabric Integration**
- Text-Fabric corpus analysis engine
- Query downloaded datasets locally
- Advanced search capabilities
- Linguistic feature analysis
- AI-assisted study tools

**FastAPI REST**
- Legacy API compatibility
- Health checks and monitoring
- Alternative to GraphQL for simple operations

## User Flow

```
1. User Opens Desktop App
        ↓
2. User Browses Available Datasets
   - App queries: GET /graphql (datasets query)
   - Backend lists datasets from Supabase Storage
        ↓
3. User Selects Dataset to Download
   - App requests: mutation { downloadDataset(...) }
   - Backend downloads from Supabase Storage
   - Backend extracts to local filesystem
        ↓
4. Dataset Ready for Use
   - Context-Fabric loads dataset from local path
   - User can now query the dataset
        ↓
5. User Performs Operations
   - Search verses: query { searchCorpus(...) }
   - Get passages: query { getPassage(...) }
   - Create notes: mutation { createNote(...) }
   - Add favorites: mutation { addFavorite(...) }
        ↓
6. User Data Synced to Supabase
   - Notes, favorites stored in PostgreSQL
   - Available across devices
```

## Technology Stack

### Backend
- **Python 3.12+** - Core language
- **FastAPI** - Web framework
- **Strawberry GraphQL** - GraphQL library
- **Context-Fabric** - Text-Fabric corpus analysis
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Supabase Python Client** - Supabase integration
- **Uvicorn** - ASGI server

### Development Tools
- **Bun** - JavaScript runtime and package manager
- **Docker** - Containerization
- **PostgreSQL** - Database
- **Redis** - Caching (optional)
- **Nginx** - Reverse proxy (production)

## Project Structure

```
api/
├── app/
│   ├── graphql/                    # GraphQL Layer
│   │   ├── schema.py               # Main Strawberry schema
│   │   ├── types/                  # GraphQL type definitions
│   │   │   ├── dataset.py
│   │   │   ├── user.py
│   │   │   └── corpus.py
│   │   └── resolvers/              # Query/Mutation resolvers
│   │       ├── datasets.py
│   │       ├── users.py
│   │       └── corpus.py
│   │
│   ├── corpus/                     # Context-Fabric Integration
│   │   ├── manager.py              # Corpus lifecycle management
│   │   ├── query.py                # Query interface
│   │   └── search.py               # Search operations
│   │
│   ├── storage/                    # Supabase Storage Service
│   │   ├── datasets.py             # Dataset download/upload
│   │   └── git_fetch.py            # Git repo fetching
│   │
│   ├── models/                     # SQLAlchemy Models
│   │   ├── user.py                 # User profile
│   │   ├── note.py                 # User notes
│   │   ├── favorite.py             # User favorites
│   │   └── user_dataset.py         # Downloaded datasets tracking
│   │
│   ├── routers/                    # FastAPI Routers
│   │   ├── datasets.py             # Dataset management endpoints
│   │   └── user_data.py            # User notes/favorites endpoints
│   │
│   ├── services/                   # Business Logic
│   │   ├── auth_service.py         # Authentication logic
│   │   └── dataset_service.py      # Dataset operations
│   │
│   ├── auth.py                     # Supabase Auth integration
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database connections
│   └── main.py                     # FastAPI application
│
├── supabase/
│   ├── migrations/                 # Database migrations
│   │   └── 001_initial_schema.sql
│   ├── functions/                  # Edge functions
│   │   └── fetch_git_dataset/
│   └── config.toml                 # Supabase configuration
│
├── docker/
│   ├── nginx/
│   │   └── nginx.conf
│   └── pgadmin/
│       └── servers.json
│
├── _archives/                      # Old/deprecated code
│   └── old_routers/                # Previous implementation
│
├── Dockerfile                      # Container build
├── docker-compose.yml              # Service orchestration
├── requirements.txt                # Python dependencies
├── alembic.ini                     # Alembic config
├── pyproject.toml                  # Python project config
└── CLAUDE.md                       # Development guide
```

## API Endpoints

### GraphQL Endpoint

**URL:** `POST /graphql`

**Queries:**
```graphql
# List available datasets
query {
  datasets(category: "bibles") {
    id
    name
    version
    language
    size
  }
}

# Search corpus
query {
  searchCorpus(datasetId: "KJV", query: "love", limit: 10) {
    reference
    text
    context
  }
}

# Get user notes
query {
  myNotes(datasetId: "KJV", reference: "John 3:16") {
    id
    content
    createdAt
  }
}
```

**Mutations:**
```graphql
# Download dataset
mutation {
  downloadDataset(datasetId: "KJV", category: "bibles") {
    success
    localPath
  }
}

# Create note
mutation {
  createNote(datasetId: "KJV", reference: "John 3:16", content: "Great verse!") {
    id
    content
  }
}

# Add favorite
mutation {
  addFavorite(datasetId: "KJV", reference: "Romans 8:28") {
    id
    reference
  }
}
```

### REST Endpoints (Legacy)

```
GET    /api/datasets                    # List datasets
GET    /api/datasets/:id/download       # Download dataset
POST   /api/datasets/:id/install        # Mark as installed
DELETE /api/datasets/:id                # Remove from library

GET    /api/notes                       # Get user notes
POST   /api/notes                       # Create note
PUT    /api/notes/:id                   # Update note
DELETE /api/notes/:id                   # Delete note

GET    /api/favorites                   # Get favorites
POST   /api/favorites                   # Add favorite
DELETE /api/favorites/:id               # Remove favorite

GET    /health                          # Health check
```

## Database Schema

### Core Tables

```sql
-- User Profiles (extends Supabase auth.users)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    display_name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Notes
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id TEXT NOT NULL,
    reference TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Favorites
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id TEXT NOT NULL,
    reference TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, dataset_id, reference)
);

-- User Downloaded Datasets
CREATE TABLE user_datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id TEXT NOT NULL,
    category TEXT NOT NULL,
    local_path TEXT,
    downloaded_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ,
    UNIQUE(user_id, dataset_id)
);

-- Comments (optional)
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    dataset_id TEXT NOT NULL,
    reference TEXT NOT NULL,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Security

### Authentication Flow

1. User signs up/logs in via Supabase Auth
2. Client receives JWT token
3. Client includes token in GraphQL/REST requests
4. Backend validates token with Supabase
5. User ID extracted for database queries

### Row Level Security (RLS)

```sql
-- Users can only access their own notes
CREATE POLICY "Users can view own notes"
    ON notes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own notes"
    ON notes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Similar policies for favorites, comments, user_datasets
```

### API Security

- All endpoints require authentication (except /health)
- Rate limiting on public endpoints
- CORS configured for allowed origins
- Environment variables for secrets
- Service role key never exposed to client

## Deployment

### Docker Compose Stack

Services:
- `postgres` - PostgreSQL database
- `api` - FastAPI backend
- `redis` - Caching layer
- `nginx` - Reverse proxy
- `pgadmin` - Database management UI

### Environment Variables

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_STORAGE_BUCKET=biblepedia-data

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://app.biblepedia.com
DATASETS_BASE_PATH=/app/datasets

# Context-Fabric
TEXT_FABRIC_DATA=/app/datasets
```

### Production Deployment

1. Build Docker image: `docker build -t biblepedia-api .`
2. Push to registry: `docker push biblepedia-api:latest`
3. Deploy with docker-compose: `docker-compose up -d`
4. Run migrations: `docker exec api alembic upgrade head`
5. Verify health: `curl https://api.biblepedia.com/health`

## Development Workflow

### Setup

```bash
# Install Python dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install Bun dependencies
bun install

# Start Supabase (local)
bun run db:start

# Run migrations
bun run db:migrate

# Start development server
bun run dev
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Lint
ruff check app/
black app/

# Type checking
mypy app/
```

## Migration from Old Architecture

### Archived Components

The following files have been moved to `_archives/old_routers/`:
- `commentaries.py` - Old commentary endpoints
- `datasets.py` - Old dataset management
- `epub.py` - EPUB processing
- `library.py` - Old library endpoints
- `sefaria.py` - Sefaria proxy
- `translations.py` - Old translation endpoints

### New Implementation

These old endpoints will be reimplemented as:
- GraphQL queries/mutations in `app/graphql/`
- REST endpoints in `app/routers/` (compatibility layer)
- Core logic in `app/services/`

## Next Steps

### Phase 1: Core Infrastructure ✅
- [x] Updated architecture documentation
- [x] Reorganized file structure
- [x] Updated Docker configuration
- [x] Created corpus manager skeleton
- [x] Created storage service skeleton

### Phase 2: Database & Models
- [ ] Create database migrations
- [ ] Implement SQLAlchemy models
- [ ] Set up Supabase auth integration
- [ ] Configure RLS policies

### Phase 3: GraphQL Layer
- [ ] Define GraphQL schema
- [ ] Implement resolvers
- [ ] Add authentication middleware
- [ ] Create GraphiQL interface

### Phase 4: Context-Fabric Integration
- [ ] Implement corpus query interface
- [ ] Add search functionality
- [ ] Integrate with GraphQL resolvers
- [ ] Add AI-assisted tools

### Phase 5: Storage Integration
- [ ] Implement dataset download
- [ ] Add upload functionality
- [ ] Create sync mechanism
- [ ] Add progress tracking

### Phase 6: Testing & Documentation
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create API documentation
- [ ] Write user guides

### Phase 7: Deployment
- [ ] Set up CI/CD pipeline
- [ ] Configure production environment
- [ ] Deploy to staging
- [ ] Production release

## Resources

- [Text-Fabric Documentation](https://annotation.github.io/text-fabric/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Context-Fabric](https://github.com/annotation/text-fabric)

---

**Last Updated:** 2024
**Status:** Phase 1 Complete - Ready for Phase 2 Implementation
