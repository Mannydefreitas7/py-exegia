import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graphql.schema import graphql_router
from app.routers.commentaries import available_commentaries_router
from app.routers.commentaries import router as commentaries_router
from app.routers.datasets import available_datasets_router
from app.routers.datasets import router as datasets_router
from app.routers.epub import router as epub_router
from app.routers.graphql_supabase import router as graphql_supabase_router
from app.routers.library import router as library_router
from app.routers.mcp import router as mcp_router
from app.routers.sefaria import (
    calendar_router,
    index_router,
    lexicon_router,
    misc_router,
    related_router,
    term_router,
    text_router,
    topic_router,
)
from app.routers.translations import router as translations_router
from app.ssl_cert import CERT_FILE, KEY_FILE, generate_ssl_cert

logging.basicConfig(
    level=logging.DEBUG if settings.is_development else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# Generate certs at import time so they exist before the server binds.
if settings.is_development:
    generate_ssl_cert()

app = FastAPI(
    title="BiblePedia API",
    description="Bible API compatible with bible.helloao.org",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Sefaria proxy routers ─────────────────────────────────────────────────────
# Registered first so their specific paths take precedence over generic ones.
app.include_router(text_router, prefix="/api")
app.include_router(index_router, prefix="/api")
app.include_router(related_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(lexicon_router, prefix="/api")
app.include_router(topic_router, prefix="/api")
app.include_router(term_router, prefix="/api")
app.include_router(misc_router, prefix="/api")

# ── BiblePedia (helloao.org compatible) routers ───────────────────────────────
# Register specific prefixes before the generic /{translation}/... catch-all.
app.include_router(available_commentaries_router, prefix="/api")
app.include_router(available_datasets_router, prefix="/api")
app.include_router(commentaries_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(translations_router, prefix="/api")
app.include_router(epub_router, prefix="/api")
app.include_router(library_router, prefix="/api")

# ── Context-Fabric MCP routers ────────────────────────────────────────────────
app.include_router(mcp_router, prefix="/api/mcp")

# ── GraphQL routers ────────────────────────────────────────────────────────────
# Strawberry GraphQL (Context-Fabric data) at /corpus/graphql
app.include_router(graphql_router, prefix="/corpus/graphql")
# Supabase GraphQL (pg_graphql proxy) at /api/graphql
app.include_router(graphql_supabase_router, prefix="/api/graphql")


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", tags=["Health"], include_in_schema=False)
async def root() -> dict[str, str]:
    return {"message": "BiblePedia API — see /docs for API reference"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        port=8000,
        reload=True,
        use_colors=True,
        ssl_certfile=str(CERT_FILE),
        ssl_keyfile=str(KEY_FILE),
    )
