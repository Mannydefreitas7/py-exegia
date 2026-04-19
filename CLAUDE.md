# BiblePedia API - Development Guide

## Overview

This API serves as the backend for a desktop Bible study application with Text-Fabric dataset support.

**Core Technologies:**

- **FastAPI** - REST endpoints
- **Strawberry GraphQL** - Primary API layer
- **Context-Fabric** - Corpus query engine
- **Supabase** - Database, storage, and authentication

## Quick Links

### Module Documentation

- **GraphQL** - Strawberry GraphQL schema, types, resolvers
  @app/GraphQL/CLAUDE.md
- **Corpus Integration** - Context-Fabric integration and queries
  @app/corpus/CLAUDE.md
- **Storage Service** - Supabase storage for datasets
  @app/storage/CLAUDE.md
- **Database Models** - SQLAlchemy models and schema
  @app/models/CLAUDE.md
- **REST Routers** - FastAPI REST endpoints
  @app/routers/CLAUDE.md
- **Supabase** - Database migrations and edge functions
  @supabase/CLAUDE.md

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
│                  BiblePedia API (FastAPI)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Strawberry GraphQL (Primary)                │    │
│  │  • Corpus queries (user-friendly)                   │    │
│  │  • User data (notes, favorites)                     │    │
│  │  • Dataset management                               │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         REST Endpoints (Legacy/Compat)              │    │
│  │  • Dataset downloads                                │    │
│  │  • Health checks                                    │    │
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
api/
├── app/
│   ├── graphql/              # → See app/graphql/CLAUDE.md
│   │   ├── schema.py         # Main Strawberry schema
│   │   ├── types/            # GraphQL types
│   │   └── resolvers/        # Query/Mutation resolvers
│   ├── corpus/               # → See app/corpus/CLAUDE.md
│   │   ├── manager.py        # Corpus loading and caching
│   │   └── query.py          # Query utilities
│   ├── storage/              # → See app/storage/CLAUDE.md
│   │   ├── datasets.py       # Dataset download/upload
│   │   └── git_fetch.py      # Git repo fetching
│   ├── models/               # → See app/models/CLAUDE.md
│   │   ├── user.py           # User model
│   │   ├── note.py           # Notes model
│   │   └── favorite.py       # Favorites model
│   ├── routers/              # → See app/routers/CLAUDE.md
│   │   ├── datasets.py       # Dataset management
│   │   └── user_data.py      # User notes/favorites
│   ├── auth.py               # Supabase auth integration
│   ├── config.py             # Configuration
│   ├── database.py           # Database connections
│   └── main.py               # FastAPI app entry point
├── supabase/                 # → See supabase/CLAUDE.md
│   ├── migrations/           # Database migrations
│   ├── functions/            # Edge functions
│   └── config.toml           # Supabase config
├── docs/                     # Additional documentation
│   ├── FRIENDLY_QUERIES.md   # Query implementation details
│   └── QUERY_FLOW.md         # Architecture diagrams
├── Dockerfile                # Docker build
├── docker-compose.yml        # Docker services
└── requirements.txt          # Python dependencies
```

## API Endpoints

### GraphQL (Primary)

- **POST /graphql** - Strawberry GraphQL endpoint
- **GET /graphql** - GraphiQL interactive playground

See @app/graphql/CLAUDE.md for detailed API documentation.

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

- **Context-Fabric Core**: https://context-fabric.ai/docs/core
- **Context-Fabric Graph Model**: https://context-fabric.ai/docs/concepts/graph-model
- **Strawberry GraphQL**: https://strawberry.rocks
- **Supabase**: https://supabase.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Text-Fabric**: https://github.com/annotation/text-fabric
