"""
Library router — browse and filter the generic book catalog (library_books).

GET /api/library
  Query params:
    category  — one or more BookCategory values (repeatable: ?category=bible&category=quran)
    limit     — max items to return (default: 100, max: 500)
    display   — "list" (default) | "sections"
    sort      — "alphabet" (default) | "date" | "authors"
                Only applies when display=list.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, cast, func, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.database import get_db
from app.models.book import BookCategory, LibraryBook
from app.schemas.library import (
	LibraryBookOut,
	LibraryListResponse,
	LibrarySectionOut,
	LibrarySectionsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["Library"])

_MAX_LIMIT = 500
_DEFAULT_LIMIT = 100


def _to_out(book: LibraryBook) -> LibraryBookOut:
	return LibraryBookOut(
		uuid=book.uuid,
		slug=book.slug,
		title=book.title,
		subtitle=book.subtitle,
		authors=book.authors if isinstance(book.authors, list) else None,
		publisher=book.publisher,
		published_date=book.published_date,
		language=book.language,
		text_direction=book.text_direction,
		category=book.category,
		subjects=book.subjects if isinstance(book.subjects, list) else None,
		cover_url=book.cover_url,
		description=book.description,
		total_sections=book.total_sections,
		total_pages=book.total_pages,
		created_at=book.created_at.isoformat(),
		updated_at=book.updated_at.isoformat(),
	)


def _apply_sort(query: Any, sort: str) -> Any:
	if sort == "date":
		return query.order_by(LibraryBook.published_date.asc().nulls_last(), LibraryBook.created_at.asc())
	if sort == "authors":
		# authors is a JSONB array; sort by the first element cast to text
		first_author = func.jsonb_array_element_text(LibraryBook.authors, 0)
		return query.order_by(first_author.asc().nulls_last(), LibraryBook.title.asc())
	# default: alphabet
	return query.order_by(LibraryBook.title.asc())


@router.get(
	"",
	summary="Browse the library",
	description=(
		"Returns books from the library catalog with optional filtering and sorting. "
		"Use `display=sections` to group results by category."
	),
	response_model=LibraryListResponse | LibrarySectionsResponse,
)
async def get_library(
	category: Annotated[
		list[BookCategory] | None,
		Query(description="Filter by one or more categories (repeatable)."),
	] = None,
	limit: Annotated[
		int,
		Query(ge=1, le=_MAX_LIMIT, description="Maximum number of results."),
	] = _DEFAULT_LIMIT,
	display: Annotated[
		str,
		Query(pattern="^(list|sections)$", description='"list" or "sections".'),
	] = "list",
	sort: Annotated[
		str,
		Query(
			pattern="^(alphabet|date|authors)$",
			description='"alphabet", "date", or "authors". Only used when display=list.',
		),
	] = "alphabet",
	db: AsyncSession = Depends(get_db),
) -> LibraryListResponse | LibrarySectionsResponse:
	base = select(LibraryBook)

	if category:
		base = base.where(LibraryBook.category.in_(category))

	if display == "sections":
		return await _sections_response(db, base, limit, category)

	return await _list_response(db, base, limit, sort)


async def _list_response(
	db: AsyncSession,
	base: Any,
	limit: int,
	sort: str,
) -> LibraryListResponse:
	# Total count (without limit)
	count_q = select(func.count()).select_from(base.subquery())
	total: int = (await db.execute(count_q)).scalar_one()

	q = _apply_sort(base, sort).limit(limit)
	rows = (await db.execute(q)).scalars().all()

	return LibraryListResponse(
		sort=sort,
		total=total,
		items=[_to_out(b) for b in rows],
	)


async def _sections_response(
	db: AsyncSession,
	base: Any,
	limit: int,
	categories: list[BookCategory] | None,
) -> LibrarySectionsResponse:
	# Determine which categories to include
	if categories:
		cats = categories
	else:
		# All categories that actually have books
		cat_q = select(LibraryBook.category).distinct().order_by(LibraryBook.category)
		cats = list((await db.execute(cat_q)).scalars().all())

	sections: list[LibrarySectionOut] = []
	total = 0

	for cat in cats:
		q = (
			base.where(LibraryBook.category == cat)
			.order_by(LibraryBook.title.asc())
			.limit(limit)
		)
		rows = (await db.execute(q)).scalars().all()

		# Count for this category
		count_q = select(func.count()).select_from(
			select(LibraryBook).where(LibraryBook.category == cat).subquery()
		)
		count: int = (await db.execute(count_q)).scalar_one()

		sections.append(LibrarySectionOut(category=cat, count=count, items=[_to_out(b) for b in rows]))
		total += count

	return LibrarySectionsResponse(total=total, sections=sections)
