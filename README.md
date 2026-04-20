# Exegia API

> Backend API for a desktop Bible study application with Text-Fabric dataset support

## Overview

This API serves as the backend for a desktop Bible study application with Text-Fabric dataset support.

**Core Technologies:**

- **FastAPI** - REST endpoints
- **Strawberry GraphQL** - Primary API layer
- **Context-Fabric** - Corpus query engine
- **Supabase** - Database, storage, and authentication
- **uv** - Python package manager (workspace-based)

## Quick Links

### Module Documentation

- **[GraphQL API](packages/graphql/CLAUDE.md)** - Strawberry GraphQL schema, types, resolvers
- **[Corpus Integration](packages/corpus/CLAUDE.md)** - Context-Fabric integration and queries
- **[Storage Service](packages/storage/CLAUDE.md)** - Supabase storage for datasets
- **[Database Models](packages/models/CLAUDE.md)** - SQLAlchemy models and schema
- **[REST Routers](packages/routers/CLAUDE.md)** - FastAPI REST endpoints
- **[Supabase](src/supabase/CLAUDE.md)** - Database migrations and edge functions
- **[Auth](src/supabase/auth/CLAUDE.md)** - Supabase JWT authentication and FastAPI dependencies

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
│                  Exegia API (FastAPI)                        │
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

## Development Stack

### Python (Backend)

Python 3.13+ with a uv workspace:

- **FastAPI** - Web framework
- **Strawberry GraphQL** - GraphQL schema and resolvers
- **Context-Fabric** - Text-Fabric corpus analysis
- **Supabase Python Client** - Database and storage operations
- **SQLAlchemy** - ORM for database models

### uv (Package & Script Management)

Default to using uv for all Python tooling:

- Use `uv run <script>` instead of `python <script>`
- Use `uv run pytest` instead of `pytest` directly
- Use `uv add <package>` instead of `pip install`
- Use `uv add --dev <package>` for dev-only dependencies
- Use `uv sync` to install all workspace dependencies
- Use `uv lock` after changing `pyproject.toml`

## Project Structure

```
api/                              # uv workspace root
├── packages/                     # Workspace members (editable installs)
│   ├── graphql/                  # → See packages/graphql/CLAUDE.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       ├── schema.py         # Strawberry schema + GraphQLRouter
│   │       ├── types/            # Corpus, dataset, user GQL types
│   │       └── resolvers/        # Query/mutation implementations
│   ├── corpus/                   # → See packages/corpus/CLAUDE.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── manager.py        # Corpus loading and caching
│   ├── models/                   # → See packages/models/CLAUDE.md
│   │   ├── pyproject.toml
│   │   └── src/                  # book.py, note.py, user.py …
│   ├── schemas/
│   │   ├── pyproject.toml
│   │   └── src/                  # dataset.py, library.py …
│   ├── storage/                  # → See packages/storage/CLAUDE.md
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── datasets.py       # Supabase dataset operations
│   └── routers/                  # → See packages/routers/CLAUDE.md
│       ├── pyproject.toml
│       └── src/
├── src/                          # Root app module
│   ├── supabase/                 # → See src/supabase/CLAUDE.md
│   │   ├── auth/                 # → See src/supabase/auth/CLAUDE.md
│   │   ├── migrations/           # Supabase migrations
│   │   └── config.toml           # Supabase config
│   ├── alembic/                  # Alembic migrations
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

## Quick Start

### Local Development

```bash
# Install all workspace dependencies
uv sync

# Start development server
uv run uvicorn src.main:app --reload

# Run migrations
uv run alembic upgrade head
```

Server runs on: **http://localhost:8000**

GraphiQL playground: **http://localhost:8000/graphql**

### Docker Deployment

```bash
# Build image
docker build -t exegia-api .

# Run with docker-compose
docker compose up -d
```

## API Endpoints

### GraphQL (Primary)

- **POST /graphql** - Strawberry GraphQL endpoint
- **GET /graphql** - GraphiQL interactive playground

See **[packages/graphql/CLAUDE.md](packages/graphql/CLAUDE.md)** for detailed API documentation.

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

## Testing

```bash
# Run tests
uv run pytest

# Test GraphQL queries
# Open http://localhost:8000/graphql and try example queries
```

## Documentation Index

### Module-Specific

- **[GraphQL API](packages/graphql/CLAUDE.md)** - Schema, types, resolvers, user-friendly queries
- **[Corpus Integration](packages/corpus/CLAUDE.md)** - Context-Fabric API, corpus management
- **[Storage Service](packages/storage/CLAUDE.md)** - Dataset downloads, Supabase Storage
- **[Database Models](packages/models/CLAUDE.md)** - Schema, migrations, models
- **[REST Routers](packages/routers/CLAUDE.md)** - REST endpoints, authentication
- **[Supabase](src/supabase/CLAUDE.md)** - Migrations, functions, configuration

### External Resources

- **Text-Fabric**: https://github.com/annotation/text-fabric
- **Context-Fabric Core**: https://context-fabric.ai/docs/core
- **Context-Fabric Graph Model**: https://context-fabric.ai/docs/concepts/graph-model
- **Strawberry GraphQL**: https://strawberry.rocks
- **Supabase**: https://supabase.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **uv**: https://docs.astral.sh/uv/

## Contributing

When adding new features:

1. Update relevant module `CLAUDE.md` file
2. Add GraphQL types/resolvers for new queries
3. Update `packages/corpus/EXAMPLES.md` if adding query features
4. Add tests for new functionality
5. Update this `README.md` if architecture changes
