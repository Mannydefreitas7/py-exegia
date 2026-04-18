from typing import Any, Literal, Union

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Chapter content types — match helloao.org structure exactly
# ---------------------------------------------------------------------------


class ChapterVerse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	type: Literal["verse"] = "verse"
	number: int
	content: list[Any]
	"""
	Content items can be:
	- str (plain text)
	- {"text": str, "poem": int} — poetry line
	- {"noteId": str} — footnote reference
	- {"heading": str} — inline heading
	"""


class ChapterHeading(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	type: Literal["heading"] = "heading"
	content: list[str]


class ChapterLineBreak(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	type: Literal["line_break"] = "line_break"


ChapterContent = Union[ChapterVerse, ChapterHeading, ChapterLineBreak]


class ChapterData(BaseModel):
	"""Shape of a single chapter's content object."""

	model_config = ConfigDict(from_attributes=True)

	translation: "Translation"
	book: "TranslationBook"
	thisChapterLink: str
	thisChapterAudioLinks: dict[str, str] | None = None
	nextChapterLink: str | None = None
	previousChapterLink: str | None = None
	numberOfVerses: int
	content: list[Any]
	footnotes: list[Any] | None = None


# ---------------------------------------------------------------------------
# Translation schemas
# ---------------------------------------------------------------------------


class Translation(BaseModel):
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
	availableFormats: list[str] | None = None
	numberOfBooks: int = 0
	totalChapters: int = 0
	totalVerses: int = 0


class TranslationBook(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	translationId: str
	name: str
	commonName: str
	title: str | None = None
	order: int
	numberOfChapters: int
	firstChapterNumber: int
	lastChapterNumber: int
	totalVerses: int
	isApocryphal: bool = False


class TranslationBookChapter(BaseModel):
	"""Summary of a chapter within a book listing."""

	model_config = ConfigDict(from_attributes=True)

	number: int
	id: str
	bookId: str
	translationId: str
	numberOfVerses: int


class TranslationBooks(BaseModel):
	"""Response for GET /api/{translation}/books.json"""

	translation: Translation
	books: list[TranslationBook]


class TranslationComplete(BaseModel):
	"""Response for GET /api/{translation}/complete.json"""

	translation: Translation
	books: list[TranslationBook]
	chapters: list[Any]


class AvailableTranslations(BaseModel):
	"""Response for GET /api/available_translations.json"""

	translations: list[Translation]
