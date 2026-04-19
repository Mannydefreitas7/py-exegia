from typing import Any

from pydantic import BaseModel, ConfigDict


class Commentary(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	name: str
	englishName: str
	website: str | None = None
	licenseUrl: str | None = None
	shortName: str | None = None
	language: str
	languageName: str
	languageEnglishName: str
	textDirection: str = "ltr"
	introduction: str | None = None
	numberOfBooks: int = 0
	totalChapters: int = 0


class CommentaryBook(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	commentaryId: str
	name: str
	commonName: str
	title: str | None = None
	order: int
	numberOfChapters: int
	firstChapterNumber: int
	lastChapterNumber: int
	isApocryphal: bool = False


class CommentaryBooks(BaseModel):
	"""Response for GET /api/c/{commentary}/books.json"""

	commentary: Commentary
	books: list[CommentaryBook]


class CommentaryBookChapter(BaseModel):
	"""Response for GET /api/c/{commentary}/{book}/{chapter}.json"""

	model_config = ConfigDict(from_attributes=True)

	commentary: Commentary
	book: CommentaryBook
	thisChapterLink: str
	nextChapterLink: str | None = None
	previousChapterLink: str | None = None
	content: list[Any]


class CommentaryProfile(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	commentaryId: str
	name: str
	introduction: str | None = None


class CommentaryProfileContent(BaseModel):
	"""Response for GET /api/c/{commentary}/profiles/{profile}.json"""

	model_config = ConfigDict(from_attributes=True)

	commentary: Commentary
	profile: CommentaryProfile
	content: list[Any]


class CommentaryProfiles(BaseModel):
	"""Response for GET /api/c/{commentary}/profiles.json"""

	commentary: Commentary
	profiles: list[CommentaryProfile]


class AvailableCommentaries(BaseModel):
	"""Response for GET /api/available_commentaries.json"""

	commentaries: list[Commentary]
