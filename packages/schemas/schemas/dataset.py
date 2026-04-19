from typing import Any

from pydantic import BaseModel, ConfigDict


class Dataset(BaseModel):
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
	numberOfBooks: int = 0
	totalChapters: int = 0


class DatasetBook(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: str
	datasetId: str
	name: str
	commonName: str
	title: str | None = None
	order: int
	numberOfChapters: int
	firstChapterNumber: int
	lastChapterNumber: int
	isApocryphal: bool = False


class DatasetBooks(BaseModel):
	"""Response for GET /api/d/{dataset}/books.json"""

	dataset: Dataset
	books: list[DatasetBook]


class DatasetBookChapter(BaseModel):
	"""Response for GET /api/d/{dataset}/{book}/{chapter}.json"""

	model_config = ConfigDict(from_attributes=True)

	dataset: Dataset
	book: DatasetBook
	thisChapterLink: str
	nextChapterLink: str | None = None
	previousChapterLink: str | None = None
	content: list[Any]


class AvailableDatasets(BaseModel):
	"""Response for GET /api/available_datasets.json"""

	datasets: list[Dataset]
