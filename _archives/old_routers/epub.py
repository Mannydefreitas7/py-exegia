"""
EPUB router — metadata, full extraction, and SSE progress stream.
"""
import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.epub import extract_pages, get_metadata

router = APIRouter(prefix="/epub", tags=["EPUB"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class PageOut(BaseModel):
    index: int
    id: str
    name: str
    text: str
    html: str
    percent: float


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get(
    "/metadata",
    summary="EPUB Metadata",
    description="Open an EPUB from a local path or URL and return its Dublin Core metadata.",
)
async def epub_metadata(
    path: str = Query(..., description="Filesystem path or HTTP(S) URL to the EPUB file."),
) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(get_metadata, path)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {path}")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/pages",
    summary="EPUB Pages",
    description="Extract all pages from an EPUB as JSON. Each item includes id, name, plain text, raw HTML, and percent progress.",
    response_model=list[PageOut],
)
async def epub_pages(
    path: str = Query(..., description="Filesystem path or HTTP(S) URL to the EPUB file."),
) -> list[PageOut]:
    try:
        pages = await asyncio.to_thread(extract_pages, path)
        return pages
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {path}")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/extract",
    summary="EPUB Extract with Progress (SSE)",
    description=(
        "Stream EPUB extraction progress as Server-Sent Events. "
        "Each event is a JSON object with `type` (either `progress` or `page`), "
        "plus page data and `percent` field. "
        "A final `done` event is emitted when extraction completes."
    ),
)
async def epub_extract_stream(
    path: str = Query(..., description="Filesystem path or HTTP(S) URL to the EPUB file."),
) -> StreamingResponse:
    queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

    def _run_extraction() -> None:
        def on_progress(current: int, total: int, percent: float) -> None:
            queue.put_nowait({"type": "progress", "current": current, "total": total, "percent": percent})

        try:
            pages = extract_pages(path, on_progress=on_progress)
            for page in pages:
                queue.put_nowait({"type": "page", **page})
            queue.put_nowait(None)  # sentinel — signals completion
        except Exception as exc:
            queue.put_nowait({"type": "error", "detail": str(exc)})
            queue.put_nowait(None)

    async def _event_generator():
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, _run_extraction)

        while True:
            item = await queue.get()
            if item is None:
                yield "event: done\ndata: {}\n\n"
                break
            if item.get("type") == "error":
                yield f"event: error\ndata: {json.dumps(item)}\n\n"
                break
            yield f"event: {item['type']}\ndata: {json.dumps(item)}\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
