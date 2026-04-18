import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.translation import Book, Chapter, Translation
from app.storage_client import get_object
from app.schemas.translation import (
	AvailableTranslations,
	TranslationBooks,
	TranslationComplete,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Translations"])


def _map_translation(t: Translation) -> dict[str, Any]:
	return {
		"id": t.id,
		"name": t.name,
		"englishName": t.english_name,
		"website": t.website,
		"licenseUrl": t.license_url,
		"shortName": t.short_name,
		"language": t.language,
		"languageName": t.language_name,
		"languageEnglishName": t.language_english_name,
		"textDirection": t.text_direction,
		"availableFormats": t.available_formats,
		"numberOfBooks": t.number_of_books,
		"totalChapters": t.total_chapters,
		"totalVerses": t.total_verses,
	}


def _map_book(b: Book) -> dict[str, Any]:
	return {
		"id": b.id,
		"translationId": b.translation_id,
		"name": b.name,
		"commonName": b.common_name,
		"title": b.title,
		"order": b.order,
		"numberOfChapters": b.number_of_chapters,
		"firstChapterNumber": b.first_chapter_number,
		"lastChapterNumber": b.last_chapter_number,
		"totalVerses": b.total_verses,
		"isApocryphal": b.is_apocryphal,
	}


@router.get(
	"/available_translations.json",
	response_model=AvailableTranslations,
	summary="List all available translations",
)
async def get_available_translations(
	db: AsyncSession = Depends(get_db),
) -> AvailableTranslations:
	result = await db.execute(select(Translation).order_by(Translation.language, Translation.id))
	translations = result.scalars().all()
	return AvailableTranslations(translations=[_map_translation(t) for t in translations])


@router.get(
	"/{translation}/books.json",
	response_model=TranslationBooks,
	summary="List books for a translation",
)
async def get_translation_books(
	translation: str,
	db: AsyncSession = Depends(get_db),
) -> TranslationBooks:
	result = await db.execute(
		select(Translation)
		.where(Translation.id == translation)
		.options(selectinload(Translation.books))
	)
	t = result.scalar_one_or_none()
	if t is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")

	books_sorted = sorted(t.books, key=lambda b: b.order)
	return TranslationBooks(
		translation=_map_translation(t),
		books=[_map_book(b) for b in books_sorted],
	)


@router.get(
	"/{translation}/{book}/{chapter}.json",
	summary="Get a specific chapter with verse content",
)
async def get_chapter(
	translation: str,
	book: str,
	chapter: int,
	db: AsyncSession = Depends(get_db),
) -> Any:
	# Prefer S3 for chapter content (pre-generated JSON)
	s3_key = f"{translation}/{book}/{chapter}.json"
	data = get_object(s3_key)
	if data is not None:
		return data

	# Fallback: build response from DB
	result = await db.execute(
		select(Chapter)
		.join(Book, Chapter.book_id == Book.id)
		.join(Translation, Chapter.translation_id == Translation.id)
		.where(
			Translation.id == translation,
			Book.common_name == book,
			Chapter.chapter_number == chapter,
		)
		.options(
			selectinload(Chapter.book).selectinload(Book.translation),
		)
	)
	ch = result.scalar_one_or_none()
	if ch is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

	t = ch.translation
	b = ch.book
	base_path = f"/api/{translation}/{book}"

	prev_link = f"{base_path}/{chapter - 1}.json" if chapter > b.first_chapter_number else None
	next_link = f"{base_path}/{chapter + 1}.json" if chapter < b.last_chapter_number else None

	return {
		"translation": _map_translation(t),
		"book": _map_book(b),
		"thisChapterLink": f"{base_path}/{chapter}.json",
		"thisChapterAudioLinks": ch.audio_links,
		"nextChapterLink": next_link,
		"previousChapterLink": prev_link,
		"numberOfVerses": ch.number_of_verses,
		"content": ch.content or [],
		"footnotes": [],
	}


@router.get(
	"/{translation}/complete.json",
	summary="Get complete translation data (all books and chapters)",
)
async def get_complete_translation(
	translation: str,
	db: AsyncSession = Depends(get_db),
) -> Any:
	# Prefer pre-generated S3 artifact
	s3_key = f"{translation}/complete.json"
	data = get_object(s3_key)
	if data is not None:
		return data

	# Fallback: build from DB
	result = await db.execute(
		select(Translation)
		.where(Translation.id == translation)
		.options(
			selectinload(Translation.books),
			selectinload(Translation.chapters).selectinload(Chapter.book),
		)
	)
	t = result.scalar_one_or_none()
	if t is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")

	books_sorted = sorted(t.books, key=lambda b: b.order)
	chapters_sorted = sorted(t.chapters, key=lambda c: (c.book.order, c.chapter_number))

	return TranslationComplete(
		translation=_map_translation(t),
		books=[_map_book(b) for b in books_sorted],
		chapters=[
			{
				"bookId": c.book_id,
				"chapterNumber": c.chapter_number,
				"numberOfVerses": c.number_of_verses,
				"content": c.content or [],
			}
			for c in chapters_sorted
		],
	)
