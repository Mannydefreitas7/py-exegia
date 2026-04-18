# BiblePedia API with Context-Fabric MCP Integration

A comprehensive Bible API that combines compatibility with bible.helloao.org endpoints and powerful Context-Fabric MCP (Model Context Protocol) integration for advanced biblical text corpus analysis.

## Features

### Bible API

- ✅ **bible.helloao.org compatible** - Drop-in replacement for existing Bible API clients
- 📖 **Multiple translations** - KJV, ESV, ASV, NET, and many more
- 🌍 **Original languages** - Hebrew (OHG) and Greek (SBLGNT) texts
- 📚 **Commentaries & lexicons** - Rich theological resources
- 🔍 **Sefaria.org proxy** - Access Jewish texts and Torah study materials

### Context-Fabric MCP Integration (New!)

- 🤖 **AI-powered queries** - Natural language search with Claude and other AI assistants
- 🔎 **Advanced search** - Pattern-based queries with linguistic features
- 📊 **Corpus analysis** - Morphology, syntax, and semantic annotations
- 🔗 **Cross-references** - Discover related passages and themes
- 💾 **Supabase storage** - Fast, scalable PostgreSQL backend
- ⚡ **Performance** - Cached queries and optimized indexes

## Quick Start

### Prerequisites

- [Bun](https://bun.sh) (already configured)
- Python 3.12+
- Docker Desktop (for Supabase)
- External drive with Bible data at `/Volumes/External HD/biblemate/`

### 5-Minute Setup

```bash
cd api

# 1. Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Install Bun dependencies
bun install

# 3. Start Supabase
bun run db:start

# 4. Run migrations
bun run db:reset

# 5. Start the API
bun run dev
```

**API is now running at:** https://localhost:8000

### Import Bible Data

```bash
# Quick: Import just the KJV (~30 seconds)
bun run mcp:import:bibles

# Full: Import all corpora (~20-30 minutes)
bun run mcp:setup:import
```

## Documentation

📚 **[Quick Start Guide](./QUICKSTART.md)** - Get up and running in 5 minutes

🔧 **[MCP Setup Guide](./MCP_SETUP.md)** - Complete Context-Fabric MCP documentation:

- Architecture and data flow
- API endpoints reference
- Claude Desktop integration
- Performance optimization
- Troubleshooting

🌐 **[API Documentation](https://localhost:8000/docs)** - Interactive Swagger UI (when server is running)

🎨 **[GraphQL Guide](./GRAPHQL_GUIDE.md)** - Complete GraphQL API guide:

- Two GraphQL endpoints
- Example queries and mutations
- Client integration examples
- Schema introspection

## API Endpoints

### Bible API (bible.helloao.org compatible)

```
GET  /api/{translation}/books
GET  /api/{translation}/{book}/chapters
GET  /api/{translation}/{book}/{chapter}
GET  /api/available_commentaries
GET  /api/available_datasets
```

### Context-Fabric MCP API

```
GET  /api/mcp/corpora                          # List available corpora
GET  /api/mcp/corpora/{name}                   # Get corpus details
POST /api/mcp/corpora/{name}/search            # Search corpus
POST /api/mcp/corpora/{name}/passages          # Get passages
GET  /api/mcp/corpora/{name}/cross-references  # Get cross-references
```

### GraphQL API

```
GET/POST  /corpus/graphql       # Context-Fabric GraphQL (Strawberry)
GET/POST  /api/graphql          # Supabase GraphQL (pg_graphql)
GET       /api/graphql/schema   # Supabase schema introspection
```

### Sefaria Proxy

```
GET  /api/texts/*
GET  /api/index/*
GET  /api/related/*
```

## Usage Examples

### Get a Bible Verse

```bash
curl https://localhost:8000/api/KJV/John/3
```

### Search for "love" in KJV

```bash
curl -X POST https://localhost:8000/api/mcp/corpora/KJV/search \
  -H "Content-Type: application/json" \
  -d '{"query": "love", "limit": 10}'
```

### Get Multiple Passages

```bash
curl -X POST https://localhost:8000/api/mcp/corpora/KJV/passages \
  -H "Content-Type: application/json" \
  -d '{"references": ["John 3:16", "Romans 8:28"]}'
```

### GraphQL: Query Corpora (Context-Fabric)

```bash
curl -X POST https://localhost:8000/corpus/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ corpora(first: 10) { edges { node { name corpusType language } } totalCount } }"
  }'
```

### GraphQL: Search Verses (Strawberry)

```bash
curl -X POST https://localhost:8000/corpus/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { search(corpusName: \"KJV\", searchInput: { query: \"love\", limit: 10 }) { edges { node { reference textContent } } totalCount } }"
  }'
```

### GraphQL: Direct Database Query (Supabase)

```bash
curl -X POST https://localhost:8000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ corporaCollection(first: 10, filter: { corpusType: { eq: \"bible\" } }) { edges { node { name language } } } }"
  }'
```

## Development

### Available Scripts

```bash
# API Development
bun run dev              # Start development server
bun run build           # Build Docker image

# Database
bun run db:start        # Start Supabase
bun run db:stop         # Stop Supabase
bun run db:reset        # Reset database with migrations
bun run db:migrate      # Run pending migrations
bun run db:new          # Create new migration

# MCP Integration
bun run mcp:setup       # Setup MCP integration
bun run mcp:import      # Import all corpus data
bun run mcp:test        # Run integration tests

# Utilities
bun run clean           # Remove cache and build files
```

### Project Structure

```
api/
├── app/
│   ├── mcp/                  # Context-Fabric MCP service
│   ├── routers/              # API route handlers
│   │   ├── mcp.py           # MCP API endpoints
│   │   ├── graphql_supabase.py  # Supabase GraphQL proxy
│   │   ├── translations.py   # Bible API endpoints
│   │   └── sefaria.py       # Sefaria proxy
│   ├── graphql/              # GraphQL schema and resolvers
│   │   ├── schema.py        # Strawberry GraphQL schema
│   │   ├── types.py         # GraphQL type definitions
│   │   ├── resolvers.py     # Query/Mutation resolvers
│   │   └── supabase_proxy.py # Supabase GraphQL client
│   ├── scripts/
│   │   └── import_corpus/   # Data import scripts
│   ├── config.py            # Configuration
│   ├── database.py          # Database connections
│   └── main.py              # FastAPI application
├── supabase/
│   ├── migrations/          # Database schema
│   └── config.toml          # Supabase configuration
├── setup_mcp.py             # MCP setup script
├── test_mcp_integration.py  # Integration tests
├── QUICKSTART.md            # Quick start guide
└── MCP_SETUP.md             # Full MCP documentation
```

## Tech Stack

- **Runtime**: [Bun](https://bun.sh) - Fast JavaScript runtime
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- **Database**: [Supabase](https://supabase.com) - PostgreSQL with real-time features
- **Corpus Analysis**: [Context-Fabric](https://context-fabric.ai) - Biblical text corpus framework
- **GraphQL**: [Strawberry](https://strawberry.rocks) - Python GraphQL library with type annotations
- **ORM**: SQLAlchemy with async support
- **MCP**: [Model Context Protocol](https://modelcontextprotocol.io/) - AI integration standard

## Data Sources

The project uses biblical text data from:

- **Bible translations** (KJV, ESV, ASV, NET, etc.) - SQLite `.bible` files
- **Original language texts** - Hebrew (OHG) and Greek (SBLGNT)
- **Commentaries** - Various theological commentaries
- **Lexicons** - Hebrew and Greek lexicons
- **Cross-references** - Biblical cross-reference data

Data location: `/Volumes/External HD/biblemate/data/`

## Configuration

### Environment Variables

Create `.env` file:

```env
# Supabase
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres

# App
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Get Supabase keys with: `bunx supabase status`

## Testing

```bash
# Run integration tests
bun run mcp:test

# Test Supabase connection
bunx supabase status

# Check import logs
# Open http://127.0.0.1:54323 (Supabase Studio)
```

## Claude Desktop Integration

Use Context-Fabric MCP with Claude Desktop for natural language queries:

1. Install: `pip install context-fabric[mcp]`
2. Configure `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "context-fabric": {
      "command": "python",
      "args": ["-m", "context_fabric.mcp"],
      "env": {
        "CORPUS_PATH": "/Volumes/External HD/biblemate/data"
      }
    }
  }
}
```

3. Ask Claude: "Search for 'love' in the KJV Bible"

## Database Schema

Key tables:

- `corpora` - Corpus metadata
- `sections` - Biblical verses and passages
- `nodes` - Text graph nodes
- `features` - Linguistic annotations
- `passages` - Cached passage text
- `search_queries` - Cached search results (24hr TTL)

See [MCP_SETUP.md](./MCP_SETUP.md) for complete schema documentation.

## Troubleshooting

**Supabase won't start:**

```bash
docker ps  # Ensure Docker is running
bun run db:stop && bun run db:start
```

**Port conflicts:**
Edit `supabase/config.toml` to change ports

**Import fails:**

- Check external drive is mounted
- View logs in Supabase Studio (http://127.0.0.1:54323)
- Check `import_logs` table for errors

**SSL warnings:**
Use HTTP: `http://localhost:8000/docs` (without 's')

## Performance

- **Caching**: Search queries cached for 24 hours
- **Indexes**: Full-text search on verses, GIN indexes on JSONB
- **Pooling**: Connection pooling for database efficiency
- **Batch imports**: 1000 records per batch

## Contributing

1. Create feature branch
2. Make changes
3. Create migration: `bun run db:new feature_name`
4. Test: `bun run mcp:test`
5. Submit PR

## License

See project LICENSE file for details.

## Resources

- [Context-Fabric Documentation](https://context-fabric.ai/docs/mcp)
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase GraphQL Guide](https://supabase.com/docs/guides/graphql)
- [Strawberry GraphQL Documentation](https://strawberry.rocks/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Bun Documentation](https://bun.sh/docs)

## Support

For issues:

1. Check [MCP_SETUP.md](./MCP_SETUP.md) troubleshooting section
2. Review Supabase logs: `bunx supabase db logs`
3. Check import logs in Supabase Studio
4. Review API logs in terminal

---

Built with ❤️ using Bun, FastAPI, Supabase, and Context-Fabric
