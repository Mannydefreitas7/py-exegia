import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.dataset import Dataset, DatasetBook, DatasetChapter
from app.storage_client import get_object
from app.schemas.dataset import AvailableDatasets, DatasetBooks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/d", tags=["Datasets"])

# Separate router for the /available_datasets.json endpoint (no /d prefix)
available_datasets_router = APIRouter(tags=["Datasets"])


def _map_dataset(d: Dataset) -> dict[str, Any]:
	return {
		"id": d.id,
		"name": d.name,
		"englishName": d.english_name,
		"website": d.website,
		"licenseUrl": d.license_url,
		"shortName": d.short_name,
		"language": d.language,
		"languageName": d.language_name,
		"languageEnglishName": d.language_english_name,
		"textDirection": d.text_direction,
		"numberOfBooks": d.number_of_books,
		"totalChapters": d.total_chapters,
	}


def _map_dataset_book(b: DatasetBook) -> dict[str, Any]:
	return {
		"id": b.id,
		"datasetId": b.dataset_id,
		"name": b.name,
		"commonName": b.common_name,
		"title": b.title,
		"order": b.order,
		"numberOfChapters": b.number_of_chapters,
		"firstChapterNumber": b.first_chapter_number,
		"lastChapterNumber": b.last_chapter_number,
		"isApocryphal": b.is_apocryphal,
	}


@available_datasets_router.get(
	"/available_datasets.json",
	response_model=AvailableDatasets,
	summary="List all available datasets",
)
async def get_available_datasets(
	db: AsyncSession = Depends(get_db),
) -> AvailableDatasets:
	result = await db.execute(
		select(Dataset).order_by(Dataset.language, Dataset.id)
	)
	datasets = result.scalars().all()
	return AvailableDatasets(datasets=[_map_dataset(d) for d in datasets])


@router.get(
	"/{dataset}/books.json",
	response_model=DatasetBooks,
	summary="List books for a dataset",
)
async def get_dataset_books(
	dataset: str,
	db: AsyncSession = Depends(get_db),
) -> DatasetBooks:
	result = await db.execute(
		select(Dataset)
		.where(Dataset.id == dataset)
		.options(selectinload(Dataset.books))
	)
	d = result.scalar_one_or_none()
	if d is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

	books_sorted = sorted(d.books, key=lambda b: b.order)
	return DatasetBooks(
		dataset=_map_dataset(d),
		books=[_map_dataset_book(b) for b in books_sorted],
	)


@router.get(
	"/{dataset}/{book}/{chapter}.json",
	summary="Get a specific dataset chapter",
)
async def get_dataset_chapter(
	dataset: str,
	book: str,
	chapter: int,
	db: AsyncSession = Depends(get_db),
) -> Any:
	s3_key = f"d/{dataset}/{book}/{chapter}.json"
	data = get_object(s3_key)
	if data is not None:
		return data

	result = await db.execute(
		select(DatasetChapter)
		.join(DatasetBook, DatasetChapter.book_id == DatasetBook.id)
		.join(Dataset, DatasetChapter.dataset_id == Dataset.id)
		.where(
			Dataset.id == dataset,
			DatasetBook.common_name == book,
			DatasetChapter.chapter_number == chapter,
		)
		.options(
			selectinload(DatasetChapter.book).selectinload(DatasetBook.dataset),
		)
	)
	ch = result.scalar_one_or_none()
	if ch is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND, detail="Dataset chapter not found"
		)

	d = ch.dataset
	b = ch.book
	base_path = f"/api/d/{dataset}/{book}"

	prev_link = f"{base_path}/{chapter - 1}.json" if chapter > b.first_chapter_number else None
	next_link = f"{base_path}/{chapter + 1}.json" if chapter < b.last_chapter_number else None

	return {
		"dataset": _map_dataset(d),
		"book": _map_dataset_book(b),
		"thisChapterLink": f"{base_path}/{chapter}.json",
		"nextChapterLink": next_link,
		"previousChapterLink": prev_link,
		"content": ch.content or [],
	}
