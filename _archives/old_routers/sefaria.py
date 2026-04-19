"""
Proxy router for the Sefaria API.
All requests are forwarded to https://www.sefaria.org, preserving query params and bodies.
See: https://github.com/Sefaria/Sefaria-Project/blob/master/docs/openAPI.json
"""

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger(__name__)

SEFARIA_BASE = "https://www.sefaria.org"

# ── Routers by tag ────────────────────────────────────────────────────────────
text_router = APIRouter(tags=["Sefaria · Text"])
index_router = APIRouter(tags=["Sefaria · Index"])
related_router = APIRouter(tags=["Sefaria · Related"])
calendar_router = APIRouter(tags=["Sefaria · Calendars"])
lexicon_router = APIRouter(tags=["Sefaria · Lexicon"])
topic_router = APIRouter(tags=["Sefaria · Topics"])
term_router = APIRouter(tags=["Sefaria · Terms"])
misc_router = APIRouter(tags=["Sefaria · Misc"])

# Shared async client (lazily initialised)
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=SEFARIA_BASE,
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "Exegia/1.0"},
        )
    return _client


async def _get(path: str, params: dict[str, Any]) -> Any:
    """Forward a GET request to Sefaria and return the JSON response."""
    clean = {k: v for k, v in params.items() if v is not None}
    try:
        resp = await _get_client().get(path, params=clean)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.text
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Sefaria proxy error %s: %s", path, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc


async def _post(path: str, body: Any) -> Any:
    """Forward a POST request to Sefaria and return the JSON response."""
    try:
        resp = await _get_client().post(path, json=body)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.text
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Sefaria proxy error %s: %s", path, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc


# ═════════════════════════════════════════════════════════════════════════════
# TEXT
# ═════════════════════════════════════════════════════════════════════════════


@text_router.get(
    "/v3/texts/{tref:path}",
    summary="Texts (v3)",
    description=(
        "The most up-to-date way to retrieve Sefaria texts. "
        "Query params: `version`, `fill_in_missing_segments`, `return_format`."
    ),
)
async def get_v3_texts(tref: str, request: Request) -> Any:
    return await _get(f"/api/v3/texts/{tref}", dict(request.query_params))


@text_router.get(
    "/texts/versions/{index}",
    summary="Versions",
    description="Returns all versions of a given Sefaria index title.",
)
async def get_text_versions(index: str, request: Request) -> Any:
    return await _get(f"/api/texts/versions/{index}", dict(request.query_params))


_ALLOWED_LANGS = {"en", "he"}


@text_router.get(
    "/texts/translations",
    summary="Languages",
    description="Returns translation languages available in Sefaria, restricted to English (`en`) and Hebrew (`he`).",
)
async def get_translations(request: Request) -> Any:
    data = await _get("/api/texts/translations", dict(request.query_params))
    if isinstance(data, list):
        return [
            item
            for item in data
            if item.get("iso_code", item.get("language", "")) in _ALLOWED_LANGS
        ]
    return data


@text_router.get(
    "/texts/translations/{lang}",
    summary="Translations",
    description="Returns all translations for a language. Only `en` (English) and `he` (Hebrew) are supported.",
)
async def get_translations_by_lang(lang: str, request: Request) -> Any:
    if lang not in _ALLOWED_LANGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang}' is not available. Supported languages: en, he.",
        )
    return await _get(f"/api/texts/translations/{lang}", dict(request.query_params))


@text_router.get(
    "/texts/{tref:path}",
    summary="Texts (v1)",
    description=(
        "Retrieve text for a given Sefaria `Ref`. "
        "Query params: `context`, `commentary`, `pad`, `ven`, `vhe`, `alts`, `wrapLinks`, "
        "`stripItags`, `multiple`, `transLangPref`, `fallbackOnDefaultVersion`, `sheets`."
    ),
)
async def get_texts(tref: str, request: Request) -> Any:
    return await _get(f"/api/texts/{tref}", dict(request.query_params))


@text_router.get(
    "/manuscripts/{tref:path}",
    summary="Manuscripts",
    description="Returns manuscript data for a given Sefaria `Ref`.",
)
async def get_manuscripts(tref: str, request: Request) -> Any:
    return await _get(f"/api/manuscripts/{tref}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# INDEX
# ═════════════════════════════════════════════════════════════════════════════


@index_router.get(
    "/v2/raw/index/{index_title:path}",
    summary="Index (v2)",
    description="Returns the raw index data for a given Sefaria title.",
)
async def get_index_v2(index_title: str, request: Request) -> Any:
    return await _get(f"/api/v2/raw/index/{index_title}", dict(request.query_params))


@index_router.get(
    "/index",
    summary="Table of Contents",
    description="Returns the full Sefaria table of contents. Optional `include_authors=1`.",
)
async def get_toc(request: Request) -> Any:
    return await _get("/api/index", dict(request.query_params))


@index_router.get(
    "/shape/{title:path}",
    summary="Shape",
    description=(
        "Returns the shape (structure) of a text or category. "
        "Query params: `depth`, `dependents`."
    ),
)
async def get_shape(title: str, request: Request) -> Any:
    return await _get(f"/api/shape/{title}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# RELATED
# ═════════════════════════════════════════════════════════════════════════════

# Register /websites variant BEFORE the generic /{tref:path} route to avoid shadowing.


@related_router.get(
    "/related/{tref:path}/websites",
    summary="Related Web Pages",
    description="Returns related web pages for a segment-level Sefaria `Ref`.",
)
async def get_related_websites(tref: str, request: Request) -> Any:
    return await _get(f"/api/related/{tref}/websites", dict(request.query_params))


@related_router.get(
    "/related/{tref:path}",
    summary="Related",
    description="Returns all related content (links, sheets, notes) for a Sefaria `Ref`.",
)
async def get_related(tref: str, request: Request) -> Any:
    return await _get(f"/api/related/{tref}", dict(request.query_params))


@related_router.get(
    "/links/{tref:path}",
    summary="Links",
    description=(
        "Returns links for a Sefaria `Ref`. "
        "Query params: `with_text`, `with_sheet_links`, `category`, `categories`."
    ),
)
async def get_links(tref: str, request: Request) -> Any:
    return await _get(f"/api/links/{tref}", dict(request.query_params))


@related_router.get(
    "/ref-topic-links/{tref:path}",
    summary="Ref-Topic Links",
    description="Returns topic links for a Sefaria `Ref`.",
)
async def get_ref_topic_links(tref: str, request: Request) -> Any:
    return await _get(f"/api/ref-topic-links/{tref}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# CALENDARS
# ═════════════════════════════════════════════════════════════════════════════


@calendar_router.get(
    "/calendars",
    summary="Calendars",
    description=(
        "Returns Jewish calendar data for a given date. "
        "Query params: `diaspora`, `custom`, `year`, `month`, `day`, `timezone`."
    ),
)
async def get_calendars(request: Request) -> Any:
    return await _get("/api/calendars", dict(request.query_params))


@calendar_router.get(
    "/calendars/next-read/{parasha}",
    summary="Next Read",
    description="Returns the next date on which a given Parasha will be read.",
)
async def get_next_read(parasha: str, request: Request) -> Any:
    return await _get(f"/api/calendars/next-read/{parasha}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# LEXICON
# ═════════════════════════════════════════════════════════════════════════════


@lexicon_router.get(
    "/words/{word:path}",
    summary="Lexicon",
    description=(
        "Returns lexicon (dictionary) data for a given Hebrew word or phrase. "
        "Query params: `lookup_ref`, `never_split`, `always_split`, `always_consonants`."
    ),
)
async def get_words(word: str, request: Request) -> Any:
    return await _get(f"/api/words/{word}", dict(request.query_params))


@lexicon_router.get(
    "/words/completion/{word}/{lexicon}",
    summary="Word Completion",
    description="Returns word completions from a Sefaria lexicon. Query params: `limit`.",
)
async def get_word_completion(word: str, lexicon: str, request: Request) -> Any:
    return await _get(
        f"/api/words/completion/{word}/{lexicon}", dict(request.query_params)
    )


# ═════════════════════════════════════════════════════════════════════════════
# TOPICS
# ═════════════════════════════════════════════════════════════════════════════


@topic_router.get(
    "/v2/topics/{topic_slug}",
    summary="Topic (v2)",
    description=(
        "Returns topic data for a given slug (v2). "
        "Query params: `with_links`, `annotate_links`, `annotate_time_period`, `group_related`, `with_refs`."
    ),
)
async def get_topic_v2(topic_slug: str, request: Request) -> Any:
    return await _get(f"/api/v2/topics/{topic_slug}", dict(request.query_params))


@topic_router.get(
    "/topics-graph/{topic_slug}",
    summary="Topic Graph",
    description="Returns topic graph data for a given slug. Query params: `link_type`.",
)
async def get_topic_graph(topic_slug: str, request: Request) -> Any:
    return await _get(f"/api/topics-graph/{topic_slug}", dict(request.query_params))


@topic_router.get(
    "/recommend/topics/{ref_list:path}",
    summary="Recommended Topics",
    description="Returns recommended topics for a `+`-separated list of Sefaria `Ref`s.",
)
async def get_recommended_topics(ref_list: str, request: Request) -> Any:
    return await _get(f"/api/recommend/topics/{ref_list}", dict(request.query_params))


@topic_router.get(
    "/topics",
    summary="All Topics",
    description="Returns all topics in Sefaria. Query params: `limit` (default 1000, 0 = no limit).",
)
async def get_all_topics(request: Request) -> Any:
    return await _get("/api/topics", dict(request.query_params))


@topic_router.get(
    "/topics/{topic_slug}",
    summary="Topic (v1)",
    description=(
        "Returns topic data for a given slug (v1). "
        "Query params: `with_links`, `annotate_links`, `group_related`, `with_refs`, `annotate_time_period`."
    ),
)
async def get_topic_v1(topic_slug: str, request: Request) -> Any:
    return await _get(f"/api/topics/{topic_slug}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# TERMS
# ═════════════════════════════════════════════════════════════════════════════


@term_router.get(
    "/terms/{name}",
    summary="Terms",
    description="Returns a Sefaria Term (shared title node) by its English name.",
)
async def get_term(name: str, request: Request) -> Any:
    return await _get(f"/api/terms/{name}", dict(request.query_params))


@term_router.get(
    "/name/{name:path}",
    summary="Name",
    description=(
        "Resolves an arbitrary string against Sefaria's data collections. "
        "Query params: `limit`, `type` (ref | Collection | Topic | TocCategory | Term | User)."
    ),
)
async def get_name(name: str, request: Request) -> Any:
    return await _get(f"/api/name/{name}", dict(request.query_params))


# ═════════════════════════════════════════════════════════════════════════════
# MISC
# ═════════════════════════════════════════════════════════════════════════════


@misc_router.post(
    "/find-refs",
    summary="Find Refs",
    description="Finds Sefaria references in a given body of text.",
)
async def find_refs(request: Request) -> Any:
    body = await request.json()
    return await _post("/api/find-refs", body)


@misc_router.post(
    "/search-wrapper",
    summary="Search",
    description="Full-text search across the Sefaria library.",
)
async def search_wrapper(request: Request) -> Any:
    body = await request.json()
    return await _post("/api/search-wrapper", body)


@misc_router.get(
    "/img-gen/{tref:path}",
    summary="Social Media Image",
    description=(
        "Generates a social media image for a Sefaria `Ref`. "
        "Query params: `lang`, `platform`, `ven`, `vhe`."
    ),
)
async def get_img_gen(tref: str, request: Request) -> Any:
    return await _get(f"/api/img-gen/{tref}", dict(request.query_params))


@misc_router.get(
    "/category/{category_path:path}",
    summary="Category",
    description="Returns metadata for a Sefaria category path (e.g. `Tanakh/Torah`).",
)
async def get_category(category_path: str, request: Request) -> Any:
    return await _get(f"/api/category/{category_path}", dict(request.query_params))
