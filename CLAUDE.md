# Exegia API - Development Guide

## Overview

This API serves as the backend for a desktop Bible study application with Text-Fabric dataset support.

**Core Technologies:**

- **FastAPI** - REST endpoints
- **Strawberry GraphQL** - Primary API layer
- **Context-Fabric** - Corpus query engine
- **Supabase** - Database, storage, and authentication
- **uv** - Python package manager (replaces pip/requirements.txt)

## Quick Start

```bash
# Install dependencies
uv sync

# Run dev server
uv run uvicorn src.main:app --reload

# Run with Docker
docker compose up -d
```

## Quick Links

### Module Documentation

- **GraphQL** - Strawberry GraphQL schema, types, resolvers
  @packages/graphql/CLAUDE.md
- **Corpus Integration** - Context-Fabric integration and queries
  @packages/corpus/CLAUDE.md
- **Storage Service** - Supabase storage for datasets
  @packages/storage/CLAUDE.md
- **Database Models** - SQLAlchemy models and schema
  @packages/models/CLAUDE.md
- **Supabase** - Database migrations and edge functions
  @src/supabase/CLAUDE.md
- **Auth** - Supabase JWT authentication and FastAPI dependencies
  @src/supabase/auth/CLAUDE.md

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Client App                        │
│              (Electron, Tauri, or Native)                    │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ GraphQL / REST
                    │
┌───────────────────▼─────────────────────────────────────────┐
│                  Exegia API (FastAPI)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Strawberry GraphQL (Primary)                │    │
│  │  • Corpus queries (user-friendly)                   │    │
│  │  • User data (notes, favorites)                     │    │
│  │  • Dataset management                               │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────┬─────────────────┬───────────────────────┘
                    │                 │
        ┌───────────▼─────┐    ┌─────▼──────────┐
        │  Supabase       │    │ Context-Fabric │
        │  • Database     │    │ • Local .tf    │
        │  • Storage      │    │   datasets     │
        │  • Auth         │    │ • Query engine │
        └─────────────────┘    └────────────────┘
```

### Data Flow

1. **User browses datasets** → GraphQL query → Supabase Storage metadata
2. **User downloads dataset** → ZIP from Supabase Storage → Extract locally
3. **User queries corpus** → GraphQL → Context-Fabric → Local .tf files
4. **User saves note** → GraphQL mutation → Supabase Database

## Project Structure

```
api/                              # uv workspace root
├── packages/                     # Workspace members (editable installs)
│   ├── graphql/                  # → See packages/graphql/CLAUDE.md
│   │   ├── pyproject.toml        # name: exegia-graphql
│   │   └── exegia_graphql/       # module: exegia_graphql
│   │       ├── schema.py         # Strawberry schema + GraphQLRouter
│   │       ├── types/            # Corpus, dataset, user GQL types
│   │       └── resolvers/        # Query/mutation implementations
│   ├── corpus/                   # → See packages/corpus/CLAUDE.md
│   │   ├── pyproject.toml        # name: exegia-corpus
│   │   └── corpus/               # module: corpus
│   │       └── manager.py        # Corpus loading and caching
│   ├── models/                   # → See packages/models/CLAUDE.md
│   │   ├── pyproject.toml        # name: exegia-models
│   │   └── models/               # module: models
│   │       ├── book.py, note.py, user.py …
│   ├── schemas/                  # → See packages/schemas/CLAUDE.md
│   │   ├── pyproject.toml        # name: exegia-schemas
│   │   └── schemas/              # module: schemas
│   │       ├── dataset.py, library.py …
│   ├── storage/                  # → See packages/storage/CLAUDE.md
│   │   ├── pyproject.toml        # name: exegia-storage
│   │   └── storage/              # module: storage
│   │       └── datasets.py       # Supabase dataset operations
│   └── routers/                  # → See packages/routers/CLAUDE.md
│       ├── pyproject.toml        # name: exegia-routers
│       └── routers/              # module: routers
├── src/                          # Root app module (module: src)
│   ├── supabase/                 # → See src/supabase/CLAUDE.md
│   │   ├── auth/                 # → See src/supabase/auth/CLAUDE.md
│   │   │   ├── __init__.py       # JWT verification + FastAPI deps
│   │   │   └── __init__.pyi      # Type stubs
│   │   ├── migrations/           # Database migrations
│   │   └── config.toml           # Supabase config
│   ├── services/                 # Internal services (epub, git, etc.)
│   ├── utils/                    # Utilities (ssl_cert, storage_client)
│   ├── auth.py                   # Re-export shim → src.supabase.auth
│   ├── config.py                 # App settings (pydantic-settings)
│   ├── database.py               # SQLAlchemy async engine + Base
│   └── main.py                   # FastAPI app entry point
├── Dockerfile                    # Docker build (uv-based)
├── docker-compose.yml            # Docker services
├── pyproject.toml                # Workspace root + exegia-api deps
└── uv.lock                       # Shared workspace lockfile
```

## API Endpoints

### GraphQL (Primary)

- **POST /graphql** - Strawberry GraphQL endpoint
- **GET /graphql** - GraphiQL interactive playground

See [graphql/CLAUDE.md](#module-documentation) for detailed API documentation.

## Key Principles

1. **GraphQL**: Primary API is GraphQL
2. **User Data in Supabase**: All user-specific data stored in PostgreSQL
3. **Datasets in Storage**: Binary datasets (ZIP files) in Supabase Storage buckets
4. **Local Corpus Access**: Context-Fabric operates on locally extracted datasets
5. **Auth Required**: All user operations require Supabase authentication
6. **Offline Capable**: Once downloaded, datasets work without internet
7. **Type Safety**: Strawberry GraphQL provides full type safety

## User Flow

1. **Desktop app starts** → User authenticates with Supabase
2. **Browse library** → GraphQL query lists available datasets
3. **Download dataset** → ZIP from Supabase Storage → Extract locally
4. **Query corpus** → GraphQL → Context-Fabric → Local .tf files → Results
5. **Save annotations** → GraphQL mutation → Supabase Database

## Documentation Index

### External Resources

- **Text-Fabric**: https://github.com/annotation/text-fabric
- **Context-Fabric Core**: https://context-fabric.ai/docs/core
- **Context-Fabric Graph Model**: https://context-fabric.ai/docs/concepts/graph-model

- **Strawberry GraphQL**: https://strawberry.rocks
- **Supabase**: https://supabase.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **uv**: https://docs.astral.sh/uv/

## Package Management

This project uses **uv** for Python package management.

```bash
# Install all deps (creates .venv automatically)
uv sync

# Install including dev deps
uv sync --dev

# Add a new dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run a command inside the venv
uv run <command>

# Lock deps after changing pyproject.toml
uv lock
```

Dependencies are declared in `pyproject.toml`. The `uv.lock` file pins exact versions for reproducible installs — commit both files.
