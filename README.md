# Exegia API

> Backend API for a desktop Bible study application with Text-Fabric dataset support

## Overview

This API serves as the backend for a desktop Bible study application with Text-Fabric dataset support.

**Core Technologies:**

- **FastAPI** - REST endpoints
- **Strawberry GraphQL** - Primary API layer
- **Context-Fabric** - Corpus query engine
- **Supabase** - Database, storage, and authentication

## Quick Links

### Module Documentation

- **[GraphQL API](app/graphql/CLAUDE.md)** - Strawberry GraphQL schema, types, resolvers
- **[Corpus Integration](app/corpus/CLAUDE.md)** - Context-Fabric integration and queries
- **[Storage Service](app/storage/CLAUDE.md)** - Supabase storage for datasets
- **[Database Models](app/models/CLAUDE.md)** - SQLAlchemy models and schema
- **[REST Routers](app/routers/CLAUDE.md)** - FastAPI REST endpoints
- **[Supabase](supabase/CLAUDE.md)** - Database migrations and edge functions

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Client App                       │
│              (Electrobun, Tauri, or Native)                 │
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

## Development Stack

### Python (Backend)

Python 3.12+ for the FastAPI backend:

- **FastAPI** - Web framework
- **Strawberry GraphQL** - GraphQL schema and resolvers
- **Context-Fabric** - Text-Fabric corpus analysis
- **Supabase Python Client** - Database and storage operations
- **SQLAlchemy** - ORM for database models

### Bun (Tooling & Scripts)

Default to using Bun for Node.js scripts and tooling:

- Use `bun <file>` instead of `node <file>` or `ts-node <file>`
- Use `bun test` instead of `jest` or `vitest`
- Use `bun install` instead of `npm install`
- Use `bun run <script>` instead of `npm run <script>`
- Use `bunx <package>` instead of `npx <package>`
- Bun automatically loads .env, so don't use dotenv

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

## Quick Start

### Local Development

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

Server runs on: **http://localhost:8000**

GraphiQL playground: **http://localhost:8000/graphql**

### Docker Deployment

```bash
# Build image
docker build -t exegia-api .

# Run with docker-compose
docker-compose up -d
```

### Environment Variables

Required in `.env`:

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Database
DATABASE_URL=postgresql://...

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# Dataset Storage
DATASETS_BASE_PATH=/app/datasets
```

## API Endpoints

### GraphQL (Primary)

- **POST /graphql** - Strawberry GraphQL endpoint
- **GET /graphql** - GraphiQL interactive playground

See **[app/graphql/CLAUDE.md](app/graphql/CLAUDE.md)** for detailed API documentation.

## Key Principles

1. **GraphQL First**: Primary API is GraphQL, REST for legacy support
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
# Python tests
pytest

# Bun tests (if applicable)
bun test

# Test GraphQL queries
# Open http://localhost:8000/graphql and try example queries
```

## Documentation Index

### Module-Specific

- **[GraphQL API](app/graphql/CLAUDE.md)** - Schema, types, resolvers, user-friendly queries
- **[Corpus Integration](app/corpus/CLAUDE.md)** - Context-Fabric API, corpus management
- **[Storage Service](app/storage/CLAUDE.md)** - Dataset downloads, Supabase Storage
- **[Database Models](app/models/CLAUDE.md)** - Schema, migrations, models
- **[REST Routers](app/routers/CLAUDE.md)** - REST endpoints, authentication
- **[Supabase](supabase/CLAUDE.md)** - Migrations, functions, configuration

### External Resources

- **Context-Fabric Core**: https://context-fabric.ai/docs/core
- **Context-Fabric Graph Model**: https://context-fabric.ai/docs/concepts/graph-model
- **Strawberry GraphQL**: https://strawberry.rocks
- **Supabase**: https://supabase.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Text-Fabric**: https://github.com/annotation/text-fabric

## Contributing

When adding new features:

1. Update relevant module `CLAUDE.md` file
2. Add GraphQL types/resolvers for new queries
3. Update `app/corpus/EXAMPLES.md` if adding query features
4. Add tests for new functionality
5. Update this main `CLAUDE.md` if architecture changes

## License

[Add your license here]
