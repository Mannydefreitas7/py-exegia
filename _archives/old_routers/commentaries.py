import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.commentary import Commentary, CommentaryBook, CommentaryChapter, CommentaryProfile
from app.storage_client import get_object
from app.schemas.commentary import (
	AvailableCommentaries,
	CommentaryBooks,
	CommentaryProfileContent,
	CommentaryProfiles,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/c", tags=["Commentaries"])


def _map_commentary(c: Commentary) -> dict[str, Any]:
	return {
		"id": c.id,
		"name": c.name,
		"englishName": c.english_name,
		"website": c.website,
		"licenseUrl": c.license_url,
		"shortName": c.short_name,
		"language": c.language,
		"languageName": c.language_name,
		"languageEnglishName": c.language_english_name,
		"textDirection": c.text_direction,
		"introduction": c.introduction,
		"numberOfBooks": c.number_of_books,
		"totalChapters": c.total_chapters,
	}


def _map_commentary_book(b: CommentaryBook) -> dict[str, Any]:
	return {
		"id": b.id,
		"commentaryId": b.commentary_id,
		"name": b.name,
		"commonName": b.common_name,
		"title": b.title,
		"order": b.order,
		"numberOfChapters": b.number_of_chapters,
		"firstChapterNumber": b.first_chapter_number,
		"lastChapterNumber": b.last_chapter_number,
		"isApocryphal": b.is_apocryphal,
	}


def _map_profile(p: CommentaryProfile) -> dict[str, Any]:
	return {
		"id": p.id,
		"commentaryId": p.commentary_id,
		"name": p.name,
		"introduction": p.introduction,
	}


# This route must NOT be under the /c prefix — register separately via main.py
available_commentaries_router = APIRouter(tags=["Commentaries"])


@available_commentaries_router.get(
	"/available_commentaries.json",
	response_model=AvailableCommentaries,
	summary="List all available commentaries",
)
async def get_available_commentaries(
	db: AsyncSession = Depends(get_db),
) -> AvailableCommentaries:
	result = await db.execute(
		select(Commentary).order_by(Commentary.language, Commentary.id)
	)
	commentaries = result.scalars().all()
	return AvailableCommentaries(commentaries=[_map_commentary(c) for c in commentaries])


@router.get(
	"/{commentary}/books.json",
	response_model=CommentaryBooks,
	summary="List books for a commentary",
)
async def get_commentary_books(
	commentary: str,
	db: AsyncSession = Depends(get_db),
) -> CommentaryBooks:
	result = await db.execute(
		select(Commentary)
		.where(Commentary.id == commentary)
		.options(selectinload(Commentary.books))
	)
	c = result.scalar_one_or_none()
	if c is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commentary not found")

	books_sorted = sorted(c.books, key=lambda b: b.order)
	return CommentaryBooks(
		commentary=_map_commentary(c),
		books=[_map_commentary_book(b) for b in books_sorted],
	)


@router.get(
	"/{commentary}/{book}/{chapter}.json",
	summary="Get a specific commentary chapter",
)
async def get_commentary_chapter(
	commentary: str,
	book: str,
	chapter: int,
	db: AsyncSession = Depends(get_db),
) -> Any:
	s3_key = f"c/{commentary}/{book}/{chapter}.json"
	data = get_object(s3_key)
	if data is not None:
		return data

	result = await db.execute(
		select(CommentaryChapter)
		.join(CommentaryBook, CommentaryChapter.book_id == CommentaryBook.id)
		.join(Commentary, CommentaryChapter.commentary_id == Commentary.id)
		.where(
			Commentary.id == commentary,
			CommentaryBook.common_name == book,
			CommentaryChapter.chapter_number == chapter,
		)
		.options(
			selectinload(CommentaryChapter.book).selectinload(CommentaryBook.commentary),
		)
	)
	ch = result.scalar_one_or_none()
	if ch is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="Commentary chapter not found"
		)

	c = ch.commentary
	b = ch.book
	base_path = f"/api/c/{commentary}/{book}"

	prev_link = f"{base_path}/{chapter - 1}.json" if chapter > b.first_chapter_number else None
	next_link = f"{base_path}/{chapter + 1}.json" if chapter < b.last_chapter_number else None

	return {
		"commentary": _map_commentary(c),
		"book": _map_commentary_book(b),
		"thisChapterLink": f"{base_path}/{chapter}.json",
		"nextChapterLink": next_link,
		"previousChapterLink": prev_link,
		"content": ch.content or [],
	}


@router.get(
	"/{commentary}/profiles.json",
	response_model=CommentaryProfiles,
	summary="List profiles for a commentary",
)
async def get_commentary_profiles(
	commentary: str,
	db: AsyncSession = Depends(get_db),
) -> CommentaryProfiles:
	result = await db.execute(
		select(Commentary)
		.where(Commentary.id == commentary)
		.options(selectinload(Commentary.profiles))
	)
	c = result.scalar_one_or_none()
	if c is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commentary not found")

	return CommentaryProfiles(
		commentary=_map_commentary(c),
		profiles=[_map_profile(p) for p in c.profiles],
	)


@router.get(
	"/{commentary}/profiles/{profile}.json",
	response_model=CommentaryProfileContent,
	summary="Get a specific commentary profile",
)
async def get_commentary_profile(
	commentary: str,
	profile: str,
	db: AsyncSession = Depends(get_db),
) -> CommentaryProfileContent:
	# Try S3 first
	s3_key = f"c/{commentary}/profiles/{profile}.json"
	data = get_object(s3_key)
	if data is not None:
		return data

	result = await db.execute(
		select(CommentaryProfile)
		.join(Commentary, CommentaryProfile.commentary_id == Commentary.id)
		.where(Commentary.id == commentary, CommentaryProfile.id == profile)
		.options(selectinload(CommentaryProfile.commentary))
	)
	p = result.scalar_one_or_none()
	if p is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

	return CommentaryProfileContent(
		commentary=_map_commentary(p.commentary),
		profile=_map_profile(p),
		content=p.content or [],
	)
