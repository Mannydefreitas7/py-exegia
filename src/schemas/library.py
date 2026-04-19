from typing import Any

from pydantic import BaseModel

from src.models.book import BookCategory


class LibraryBookOut(BaseModel):
	uuid: str
	slug: str
	title: str
	subtitle: str | None
	authors: list[str] | None
	publisher: str | None
	published_date: str | None
	language: str
	text_direction: str
	category: BookCategory
	subjects: list[str] | None
	cover_url: str | None
	description: str | None
	total_sections: int
	total_pages: int
	created_at: str
	updated_at: str

	model_config = {"from_attributes": True}


class LibraryListResponse(BaseModel):
	display: str = "list"
	sort: str
	total: int
	items: list[LibraryBookOut]


class LibrarySectionOut(BaseModel):
	category: BookCategory
	count: int
	items: list[LibraryBookOut]


class LibrarySectionsResponse(BaseModel):
	display: str = "sections"
	total: int
	sections: list[LibrarySectionOut]
