# BiblePedia API - Documentation Map

Complete guide to navigating the documentation.

## Quick Navigation

### 🏠 Start Here
- **[CLAUDE.md](CLAUDE.md)** - Main overview and architecture

### 📚 Module Documentation
- **[app/graphql/CLAUDE.md](app/graphql/CLAUDE.md)** - GraphQL API, queries, resolvers
- **[app/corpus/CLAUDE.md](app/corpus/CLAUDE.md)** - Context-Fabric integration
- **[app/storage/CLAUDE.md](app/storage/CLAUDE.md)** - Supabase Storage for datasets
- **[app/models/CLAUDE.md](app/models/CLAUDE.md)** - Database schema and models
- **[app/routers/CLAUDE.md](app/routers/CLAUDE.md)** - REST API endpoints
- **[supabase/CLAUDE.md](supabase/CLAUDE.md)** - Database, storage, auth, functions

### 🔍 Query Documentation
- **[CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md)** - 30+ query examples
- **[QUICKSTART_CORPUS.md](QUICKSTART_CORPUS.md)** - Get started in 5 minutes
- **[docs/FRIENDLY_QUERIES.md](docs/FRIENDLY_QUERIES.md)** - Implementation details
- **[docs/QUERY_FLOW.md](docs/QUERY_FLOW.md)** - Architecture visualization

### 📖 Additional Docs
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Complete feature overview

## Documentation by Task

### Getting Started

1. Read **[CLAUDE.md](CLAUDE.md)** for architecture overview
2. Try **[QUICKSTART_CORPUS.md](QUICKSTART_CORPUS.md)** to run your first query
3. Explore **[CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md)** for more examples

### Understanding GraphQL API

1. **[app/graphql/CLAUDE.md](app/graphql/CLAUDE.md)** - Schema and types
2. **[CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md)** - Real query examples
3. **[docs/FRIENDLY_QUERIES.md](docs/FRIENDLY_QUERIES.md)** - How it's implemented

### Working with Context-Fabric

1. **[app/corpus/CLAUDE.md](app/corpus/CLAUDE.md)** - Integration guide
2. **[docs/QUERY_FLOW.md](docs/QUERY_FLOW.md)** - How queries flow
3. [Context-Fabric Docs](https://context-fabric.ai/docs/core) - Official docs

### Managing Datasets

1. **[app/storage/CLAUDE.md](app/storage/CLAUDE.md)** - Download/upload operations
2. **[supabase/CLAUDE.md](supabase/CLAUDE.md)** - Storage configuration
3. **[app/routers/CLAUDE.md](app/routers/CLAUDE.md)** - REST endpoints

### Database & Models

1. **[app/models/CLAUDE.md](app/models/CLAUDE.md)** - Schema and SQLAlchemy models
2. **[supabase/CLAUDE.md](supabase/CLAUDE.md)** - Migrations and RLS policies

### REST API (Legacy)

1. **[app/routers/CLAUDE.md](app/routers/CLAUDE.md)** - All REST endpoints
2. **[CLAUDE.md](CLAUDE.md)** - Why GraphQL is preferred

### Deployment

1. **[CLAUDE.md](CLAUDE.md)** - Docker deployment
2. **[supabase/CLAUDE.md](supabase/CLAUDE.md)** - Supabase production setup

## Documentation Structure

```
api/
├── CLAUDE.md                          # 🏠 Main overview
├── DOCUMENTATION_MAP.md               # 📍 This file
├── CORPUS_QUERY_EXAMPLES.md          # 📚 30+ examples
├── QUICKSTART_CORPUS.md               # ⚡ 5-minute start
├── IMPLEMENTATION_SUMMARY.md          # 📊 Feature overview
│
├── docs/
│   ├── FRIENDLY_QUERIES.md            # 🔍 Implementation
│   └── QUERY_FLOW.md                  # 🔄 Architecture
│
├── app/
│   ├── graphql/
│   │   └── CLAUDE.md                  # GraphQL module
│   ├── corpus/
│   │   └── CLAUDE.md                  # Context-Fabric module
│   ├── storage/
│   │   └── CLAUDE.md                  # Storage module
│   ├── models/
│   │   └── CLAUDE.md                  # Database module
│   └── routers/
│       └── CLAUDE.md                  # REST API module
│
└── supabase/
    └── CLAUDE.md                      # Supabase module
```

## Documentation by Role

### Frontend Developer

**Building a client app?**
1. [app/graphql/CLAUDE.md](app/graphql/CLAUDE.md) - GraphQL schema
2. [CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md) - Query examples
3. [app/routers/CLAUDE.md](app/routers/CLAUDE.md) - REST API (if needed)

### Backend Developer

**Working on the API?**
1. [CLAUDE.md](CLAUDE.md) - Architecture overview
2. [app/graphql/CLAUDE.md](app/graphql/CLAUDE.md) - Resolvers
3. [app/corpus/CLAUDE.md](app/corpus/CLAUDE.md) - Corpus integration
4. [app/models/CLAUDE.md](app/models/CLAUDE.md) - Database models

### Database Administrator

**Managing data?**
1. [app/models/CLAUDE.md](app/models/CLAUDE.md) - Schema
2. [supabase/CLAUDE.md](supabase/CLAUDE.md) - Migrations, RLS, backups

### DevOps Engineer

**Deploying the API?**
1. [CLAUDE.md](CLAUDE.md) - Docker setup
2. [supabase/CLAUDE.md](supabase/CLAUDE.md) - Production config

### Content Manager

**Adding datasets?**
1. [app/storage/CLAUDE.md](app/storage/CLAUDE.md) - Upload process
2. [supabase/CLAUDE.md](supabase/CLAUDE.md) - Storage buckets

## Search by Topic

### Authentication & Authorization
- [supabase/CLAUDE.md](supabase/CLAUDE.md) - Auth setup
- [app/routers/CLAUDE.md](app/routers/CLAUDE.md) - Using auth in endpoints
- [app/models/CLAUDE.md](app/models/CLAUDE.md) - RLS policies

### Corpus Queries
- [CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md) - Examples
- [app/graphql/CLAUDE.md](app/graphql/CLAUDE.md) - GraphQL interface
- [app/corpus/CLAUDE.md](app/corpus/CLAUDE.md) - Context-Fabric API
- [docs/QUERY_FLOW.md](docs/QUERY_FLOW.md) - Flow diagrams

### Dataset Management
- [app/storage/CLAUDE.md](app/storage/CLAUDE.md) - Download/upload
- [supabase/CLAUDE.md](supabase/CLAUDE.md) - Storage buckets
- [app/models/CLAUDE.md](app/models/CLAUDE.md) - user_datasets table

### User Data (Notes, Favorites)
- [app/models/CLAUDE.md](app/models/CLAUDE.md) - Database schema
- [app/routers/CLAUDE.md](app/routers/CLAUDE.md) - REST endpoints
- [app/graphql/CLAUDE.md](app/graphql/CLAUDE.md) - GraphQL mutations

### Testing
- [QUICKSTART_CORPUS.md](QUICKSTART_CORPUS.md) - Quick test
- [CLAUDE.md](CLAUDE.md) - Test commands
- Each module CLAUDE.md has testing section

## External Resources

### Context-Fabric
- [Core Library](https://context-fabric.ai/docs/core)
- [Graph Model](https://context-fabric.ai/docs/concepts/graph-model)
- [Text-Fabric Compatibility](https://context-fabric.ai/docs/concepts/text-fabric-compatibility)

### Strawberry GraphQL
- [Official Docs](https://strawberry.rocks)
- [Schema Basics](https://strawberry.rocks/docs/general/schema-basics)
- [Resolvers](https://strawberry.rocks/docs/general/resolvers)

### Supabase
- [Documentation](https://supabase.com/docs)
- [Storage](https://supabase.com/docs/guides/storage)
- [Auth](https://supabase.com/docs/guides/auth)
- [RLS](https://supabase.com/docs/guides/auth/row-level-security)

### FastAPI
- [Documentation](https://fastapi.tiangolo.com)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)

## Contributing

When adding documentation:

1. **Module changes**: Update respective `app/*/CLAUDE.md`
2. **New queries**: Add to `CORPUS_QUERY_EXAMPLES.md`
3. **Architecture changes**: Update main `CLAUDE.md`
4. **New features**: Update `IMPLEMENTATION_SUMMARY.md`
5. **Navigation**: Update this `DOCUMENTATION_MAP.md`

## Getting Help

Can't find what you're looking for?

1. Check this map for relevant docs
2. Search across all CLAUDE.md files
3. Look at query examples
4. Check external resources
5. Open a GitHub issue
