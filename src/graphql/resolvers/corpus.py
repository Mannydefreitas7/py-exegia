import logging
from pathlib import Path
from typing import List, Optional

from src.config import settings
from src.graphql.types.corpus import (
    BookInfo,
    ChapterInfo,
    ComparePassagesInput,
    CorpusMetadata,
    CorpusStats,
    GetBooksInput,
    GetChapterInfoInput,
    GetPassageInput,
    GetPassagesInput,
    GetVerseRangeInput,
    ParallelPassage,
    Passage,
    SearchCorpusInput,
    SearchResult,
    SearchResults,
    Verse,
    WordOccurrence,
    WordStudy,
    WordStudyInput,
)

logger = logging.getLogger(__name__)


def _get_corpus_manager():
    from src.corpus.manager import get_corpus_manager

    return get_corpus_manager(Path(settings.datasets_base_path))


def _load_corpus(dataset_id: str):
    try:
        manager = _get_corpus_manager()
        return manager.load_corpus(dataset_id)
    except Exception as e:
        logger.warning("Could not load corpus '%s': %s", dataset_id, e)
        return None


async def resolve_corpus_metadata(dataset_id: str) -> Optional[CorpusMetadata]:
    api = _load_corpus(dataset_id)
    if api is None:
        return None
    try:
        features = list(api.Fall()) if hasattr(api, "Fall") else []
        node_types = list(api.F.otype.all) if hasattr(api, "F") and hasattr(api.F, "otype") else []
        return CorpusMetadata(
            dataset_id=dataset_id,
            name=dataset_id,
            total_nodes=len(node_types),
            total_features=len(features),
        )
    except Exception as e:
        logger.error("resolve_corpus_metadata error: %s", e)
        return CorpusMetadata(dataset_id=dataset_id, name=dataset_id)


async def resolve_corpus_stats(dataset_id: str) -> Optional[CorpusStats]:
    api = _load_corpus(dataset_id)
    if api is None:
        return None
    try:
        total_words = (
            len(list(api.F.otype.s("word"))) if hasattr(api, "F") and hasattr(api.F, "otype") else 0
        )
        total_verses = (
            len(list(api.F.otype.s("verse")))
            if hasattr(api, "F") and hasattr(api.F, "otype")
            else 0
        )
        total_chapters = (
            len(list(api.F.otype.s("chapter")))
            if hasattr(api, "F") and hasattr(api.F, "otype")
            else 0
        )
        total_books = (
            len(list(api.F.otype.s("book"))) if hasattr(api, "F") and hasattr(api.F, "otype") else 0
        )
        return CorpusStats(
            dataset_id=dataset_id,
            total_books=total_books,
            total_chapters=total_chapters,
            total_verses=total_verses,
            total_words=total_words,
            languages=[],
        )
    except Exception as e:
        logger.error("resolve_corpus_stats error: %s", e)
        return CorpusStats(
            dataset_id=dataset_id,
            total_books=0,
            total_chapters=0,
            total_verses=0,
            total_words=0,
            languages=[],
        )


def _verse_from_node(node: int, api, dataset_id: str) -> Optional[Verse]:
    try:
        book = api.T.sectionFromNode(node)[0] if hasattr(api, "T") else ""
        chapter_num, verse_num = api.T.sectionFromNode(node)[1:3] if hasattr(api, "T") else (0, 0)
        text = api.T.text(node) if hasattr(api, "T") else ""
        return Verse(
            reference=f"{book} {chapter_num}:{verse_num}",
            book=str(book),
            chapter=int(chapter_num),
            verse=int(verse_num),
            text=text,
            dataset_id=dataset_id,
        )
    except Exception:
        return None


async def resolve_search_corpus(input: SearchCorpusInput) -> SearchResults:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return SearchResults(
            results=[], total=0, query=input.query, dataset_id=input.dataset_id, has_more=False
        )

    try:
        raw = list(api.S.search(input.query))
        total = len(raw)
        page = raw[input.offset : input.offset + input.limit]

        results = []
        for match in page:
            node = match[0] if isinstance(match, (tuple, list)) else match
            verse = _verse_from_node(node, api, input.dataset_id)
            if verse:
                results.append(
                    SearchResult(
                        reference=verse.reference,
                        text=verse.text,
                        book=verse.book,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        dataset_id=input.dataset_id,
                    )
                )

        return SearchResults(
            results=results,
            total=total,
            query=input.query,
            dataset_id=input.dataset_id,
            has_more=(input.offset + input.limit) < total,
        )
    except Exception as e:
        logger.error("resolve_search_corpus error: %s", e)
        return SearchResults(
            results=[], total=0, query=input.query, dataset_id=input.dataset_id, has_more=False
        )


async def resolve_get_passage(input: GetPassageInput) -> Optional[Passage]:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return None
    try:
        nodes = api.T.nodeFromSection(tuple(input.reference.split()))
        if not nodes:
            return None
        node = nodes[0] if isinstance(nodes, (tuple, list)) else nodes
        verse = _verse_from_node(node, api, input.dataset_id)
        if verse is None:
            return None
        return Passage(
            reference=verse.reference,
            book=verse.book,
            chapter=verse.chapter,
            start_verse=verse.verse,
            text=verse.text,
            dataset_id=input.dataset_id,
        )
    except Exception as e:
        logger.error("resolve_get_passage error: %s", e)
        return None


async def resolve_get_passages(input: GetPassagesInput) -> List[Passage]:
    results = []
    for ref in input.references:
        passage = await resolve_get_passage(
            GetPassageInput(dataset_id=input.dataset_id, reference=ref)
        )
        if passage:
            results.append(passage)
    return results


async def resolve_get_verse(dataset_id: str, reference: str) -> Optional[Verse]:
    api = _load_corpus(dataset_id)
    if api is None:
        return None
    try:
        parts = reference.split()
        if len(parts) >= 2 and ":" in parts[-1]:
            book = " ".join(parts[:-1])
            chapter_verse = parts[-1].split(":")
            chapter, verse_num = int(chapter_verse[0]), int(chapter_verse[1])
            verse_nodes = api.T.nodeFromSection((book, chapter, verse_num))
            if verse_nodes:
                node = verse_nodes if isinstance(verse_nodes, int) else verse_nodes[0]
                text = api.T.text(node)
                return Verse(
                    reference=reference,
                    book=book,
                    chapter=chapter,
                    verse=verse_num,
                    text=text,
                    dataset_id=dataset_id,
                )
        return None
    except Exception as e:
        logger.error("resolve_get_verse error: %s", e)
        return None


async def resolve_get_verse_range(input: GetVerseRangeInput) -> List[Verse]:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return []
    try:
        results = []
        end_chapter = input.end_chapter or input.start_chapter
        end_verse = input.end_verse or 999

        for chapter in range(input.start_chapter, end_chapter + 1):
            start_v = input.start_verse if chapter == input.start_chapter else 1
            end_v = end_verse if chapter == end_chapter else 999
            verse_num = start_v
            while verse_num <= end_v:
                try:
                    node = api.T.nodeFromSection((input.book, chapter, verse_num))
                    if not node:
                        break
                    n = node if isinstance(node, int) else node[0]
                    text = api.T.text(n)
                    results.append(
                        Verse(
                            reference=f"{input.book} {chapter}:{verse_num}",
                            book=input.book,
                            chapter=chapter,
                            verse=verse_num,
                            text=text,
                            dataset_id=input.dataset_id,
                        )
                    )
                    verse_num += 1
                except Exception:
                    break
        return results
    except Exception as e:
        logger.error("resolve_get_verse_range error: %s", e)
        return []


async def resolve_word_study(input: WordStudyInput) -> Optional[WordStudy]:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return None
    try:
        query = f"word g_word_utf8~{input.word}"
        raw = list(api.S.search(query))[: input.limit]

        occurrences = []
        for match in raw:
            node = match[0] if isinstance(match, (tuple, list)) else match
            try:
                section = api.T.sectionFromNode(node)
                book, chapter, verse_num = section[0], section[1], section[2]
                verse_nodes = api.T.nodeFromSection((book, chapter, verse_num))
                v_node = (
                    verse_nodes
                    if isinstance(verse_nodes, int)
                    else (verse_nodes[0] if verse_nodes else None)
                )
                verse_text = api.T.text(v_node) if v_node else ""
                occurrences.append(
                    WordOccurrence(
                        word=api.T.text(node),
                        reference=f"{book} {chapter}:{verse_num}",
                        text=verse_text,
                        book=str(book),
                        chapter=int(chapter),
                        verse=int(verse_num),
                        position=node,
                    )
                )
            except Exception:
                continue

        return WordStudy(
            word=input.word,
            lemma=input.lemma,
            occurrences=occurrences,
            total_count=len(occurrences),
            dataset_id=input.dataset_id,
        )
    except Exception as e:
        logger.error("resolve_word_study error: %s", e)
        return None


async def resolve_compare_passages(input: ComparePassagesInput) -> ParallelPassage:
    texts = {}
    for dataset_id in input.dataset_ids:
        verse = await resolve_get_verse(dataset_id, input.reference)
        texts[dataset_id] = verse.text if verse else ""
    return ParallelPassage(
        reference=input.reference,
        datasets=input.dataset_ids,
        texts=texts,
    )


async def resolve_get_books(input: GetBooksInput) -> List[BookInfo]:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return []
    try:
        book_nodes = list(api.F.otype.s("book"))
        books = []
        for node in book_nodes:
            try:
                name = api.T.sectionFromNode(node)[0]
                chapter_nodes = api.L.d(node, otype="chapter")
                verse_nodes = api.L.d(node, otype="verse")
                testament = None
                if input.testament:
                    testament = input.testament
                books.append(
                    BookInfo(
                        name=str(name),
                        code=str(name),
                        testament=testament,
                        chapter_count=len(chapter_nodes),
                        verse_count=len(verse_nodes),
                    )
                )
            except Exception:
                continue
        return books
    except Exception as e:
        logger.error("resolve_get_books error: %s", e)
        return []


async def resolve_get_chapter_info(input: GetChapterInfoInput) -> Optional[ChapterInfo]:
    api = _load_corpus(input.dataset_id)
    if api is None:
        return None
    try:
        chapter_nodes = list(api.T.nodeFromSection((input.book, input.chapter)))
        if not chapter_nodes:
            return None
        c_node = chapter_nodes if isinstance(chapter_nodes, int) else chapter_nodes[0]
        verse_nodes = api.L.d(c_node, otype="verse")
        word_nodes = api.L.d(c_node, otype="word")
        return ChapterInfo(
            book=input.book,
            chapter=input.chapter,
            verse_count=len(verse_nodes),
            word_count=len(word_nodes),
        )
    except Exception as e:
        logger.error("resolve_get_chapter_info error: %s", e)
        return None
