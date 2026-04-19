"""
Corpus Query Resolvers

User-friendly GraphQL resolvers that abstract Context-Fabric's search syntax
into intuitive parameters for querying biblical and linguistic corpora.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

import strawberry

from src.corpus.manager import CorpusManager


@strawberry.enum
class NodeType(Enum):
    """Available node types in a corpus graph"""

    DOCUMENT = "document"
    BOOK = "book"
    CHAPTER = "chapter"
    VERSE = "verse"
    SENTENCE = "sentence"
    CLAUSE = "clause"
    PHRASE = "phrase"
    WORD = "word"
    SLOT = "slot"


@strawberry.enum
class OrderConstraint(Enum):
    """Ordering constraints for node relationships"""

    BEFORE = "<"  # First node comes before second
    AFTER = ">"  # First node comes after second
    ADJACENT = ".."  # Nodes are adjacent


@strawberry.input
class FeatureFilter:
    """Filter nodes by feature values"""

    name: str
    value: str
    operator: Optional[str] = "="  # =, !=, ~, !~


@strawberry.input
class NodeQuery:
    """Query parameters for a single node in the search pattern"""

    node_type: NodeType
    features: Optional[List[FeatureFilter]] = None
    quantifier: Optional[str] = None  # *, +, ?, {n}, {n,m}
    label: Optional[str] = None  # For referencing in results


@strawberry.input
class SearchPattern:
    """Hierarchical search pattern for corpus queries"""

    root: NodeQuery
    children: Optional[List["SearchPattern"]] = None
    order_constraint: Optional[OrderConstraint] = None


@strawberry.type
class NodeResult:
    """A single node in search results"""

    node_id: int
    node_type: str
    text: str
    features: strawberry.scalars.JSON

    @strawberry.field
    def feature(self, name: str) -> Optional[str]:
        """Get a specific feature value"""
        return self.features.get(name)


@strawberry.type
class SearchResult:
    """Result from a corpus search"""

    reference: str  # e.g., "Genesis 1:1" or node range
    text: str
    nodes: List[NodeResult]
    match_count: int

    @classmethod
    def from_cf_result(cls, cf_result: tuple, api: Any) -> "SearchResult":
        """Convert Context-Fabric result to GraphQL type"""
        nodes = []
        texts = []

        for node in cf_result:
            node_type = api.F.otype.v(node)
            text = api.T.text(node)

            # Gather all features for this node
            features = {}
            for feature_name in api.Fall():
                value = api.F.otype.v(node) if feature_name == "otype" else None
                if value is not None:
                    features[feature_name] = value

            nodes.append(
                NodeResult(
                    node_id=node, node_type=node_type, text=text, features=features
                )
            )
            texts.append(text)

        # Try to get reference (verse, chapter, etc.)
        reference = cls._get_reference(cf_result[0], api)

        return cls(
            reference=reference,
            text=" ".join(texts),
            nodes=nodes,
            match_count=len(nodes),
        )

    @staticmethod
    def _get_reference(node: int, api: Any) -> str:
        """Extract human-readable reference from node"""
        try:
            # Try to get containing verse
            verses = api.L.u(node, otype="verse")
            if verses:
                verse_node = verses[0]
                book = api.F.book.v(verse_node) if hasattr(api.F, "book") else None
                chapter = (
                    api.F.chapter.v(verse_node) if hasattr(api.F, "chapter") else None
                )
                verse = api.F.verse.v(verse_node) if hasattr(api.F, "verse") else None

                if all([book, chapter, verse]):
                    return f"{book} {chapter}:{verse}"

            # Fallback to node ID
            return f"Node {node}"
        except:
            return f"Node {node}"


@strawberry.type
class CorpusInfo:
    """Information about a loaded corpus"""

    dataset_id: str
    node_types: List[str]
    features: List[str]
    total_slots: int
    description: Optional[str] = None


class CorpusQueryBuilder:
    """Builds Context-Fabric query strings from user-friendly parameters"""

    @staticmethod
    def build_simple_query(
        node_type: NodeType, features: Optional[List[FeatureFilter]] = None
    ) -> str:
        """Build a simple single-node query"""
        query = node_type.value

        if features:
            feature_strs = []
            for f in features:
                if f.operator == "=":
                    feature_strs.append(f"{f.name}={f.value}")
                elif f.operator == "!=":
                    feature_strs.append(f"{f.name}!={f.value}")
                elif f.operator == "~":
                    feature_strs.append(f"{f.name}~{f.value}")
                elif f.operator == "!~":
                    feature_strs.append(f"{f.name}!~{f.value}")

            if feature_strs:
                query += " " + " ".join(feature_strs)

        return query

    @staticmethod
    def build_hierarchical_query(pattern: SearchPattern, indent: int = 0) -> str:
        """Build a hierarchical query from a search pattern"""
        lines = []
        prefix = "  " * indent

        # Build root node query
        root_query = CorpusQueryBuilder.build_simple_query(
            pattern.root.node_type, pattern.root.features
        )

        # Add quantifier if specified
        if pattern.root.quantifier:
            root_query += pattern.root.quantifier

        # Add label if specified
        if pattern.root.label:
            root_query += f" :{pattern.root.label}"

        lines.append(prefix + root_query)

        # Add children recursively
        if pattern.children:
            for i, child in enumerate(pattern.children):
                # Add order constraint if specified
                if child.order_constraint:
                    lines.append(prefix + "  " + child.order_constraint.value)

                child_query = CorpusQueryBuilder.build_hierarchical_query(
                    child, indent + 1
                )
                lines.append(child_query)

        return "\n".join(lines)


@strawberry.type
class CorpusQuery:
    """Root query type for corpus operations"""

    @strawberry.field
    def search_simple(
        self,
        dataset_id: str,
        node_type: NodeType,
        features: Optional[List[FeatureFilter]] = None,
        limit: int = 100,
    ) -> List[SearchResult]:
        """
        Simple search for a single node type with optional feature filters.

        Example: Find all verbs in past tense
        - node_type: WORD
        - features: [{"name": "pos", "value": "verb"}, {"name": "tense", "value": "past"}]
        """
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        # Build query
        query = CorpusQueryBuilder.build_simple_query(node_type, features)

        # Execute search
        results = corpus.S.search(query)

        # Convert to GraphQL results
        graphql_results = []
        for i, result in enumerate(results):
            if i >= limit:
                break
            graphql_results.append(SearchResult.from_cf_result(result, corpus.api))

        return graphql_results

    @strawberry.field
    def search_hierarchical(
        self, dataset_id: str, pattern: SearchPattern, limit: int = 100
    ) -> List[SearchResult]:
        """
        Hierarchical search with nested node patterns.

        Example: Find clauses containing a subject phrase followed by a predicate phrase
        - root: {node_type: CLAUSE}
        - children: [
            {node_type: PHRASE, features: [{name: "function", value: "subject"}]},
            {node_type: PHRASE, features: [{name: "function", value: "predicate"}], order_constraint: AFTER}
          ]
        """
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        # Build query
        query = CorpusQueryBuilder.build_hierarchical_query(pattern)

        # Execute search
        results = corpus.S.search(query)

        # Convert to GraphQL results
        graphql_results = []
        for i, result in enumerate(results):
            if i >= limit:
                break
            graphql_results.append(SearchResult.from_cf_result(result, corpus.api))

        return graphql_results

    @strawberry.field
    def search_text(
        self,
        dataset_id: str,
        text: str,
        node_type: Optional[NodeType] = None,
        case_sensitive: bool = False,
        limit: int = 100,
    ) -> List[SearchResult]:
        """
        Search for nodes containing specific text.

        Example: Find all verses containing the word "love"
        - text: "love"
        - node_type: VERSE
        """
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        # Build text search query
        operator = "=" if case_sensitive else "~"
        target_type = node_type.value if node_type else "word"
        query = f"{target_type} text{operator}{text}"

        # Execute search
        results = corpus.S.search(query)

        # Convert to GraphQL results
        graphql_results = []
        for i, result in enumerate(results):
            if i >= limit:
                break
            graphql_results.append(SearchResult.from_cf_result(result, corpus.api))

        return graphql_results

    @strawberry.field
    def get_node_text(self, dataset_id: str, node_id: int) -> Optional[str]:
        """Get the text of a specific node by ID"""
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        try:
            return corpus.T.text(node_id)
        except:
            return None

    @strawberry.field
    def get_node_features(
        self, dataset_id: str, node_id: int
    ) -> strawberry.scalars.JSON:
        """Get all features of a specific node"""
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        features = {}
        try:
            # Get all available features
            for feature_name in corpus.api.Fall():
                try:
                    value = getattr(corpus.F, feature_name).v(node_id)
                    if value is not None:
                        features[feature_name] = value
                except:
                    pass
        except:
            pass

        return features

    @strawberry.field
    def get_containing_nodes(
        self, dataset_id: str, node_id: int, node_type: NodeType
    ) -> List[NodeResult]:
        """Get all ancestor nodes of a specific type containing this node"""
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        try:
            ancestors = corpus.L.u(node_id, otype=node_type.value)
            return [
                NodeResult(
                    node_id=n,
                    node_type=node_type.value,
                    text=corpus.T.text(n),
                    features={},
                )
                for n in ancestors
            ]
        except:
            return []

    @strawberry.field
    def get_contained_nodes(
        self, dataset_id: str, node_id: int, node_type: NodeType
    ) -> List[NodeResult]:
        """Get all descendant nodes of a specific type within this node"""
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        try:
            descendants = corpus.L.d(node_id, otype=node_type.value)
            return [
                NodeResult(
                    node_id=n,
                    node_type=node_type.value,
                    text=corpus.T.text(n),
                    features={},
                )
                for n in descendants
            ]
        except:
            return []

    @strawberry.field
    def get_corpus_info(self, dataset_id: str) -> CorpusInfo:
        """Get metadata about a loaded corpus"""
        corpus_manager = CorpusManager()
        corpus = corpus_manager.load(dataset_id)

        # Get node types
        node_types = (
            list(corpus.F.otype.s("").keys()) if hasattr(corpus.F, "otype") else []
        )

        # Get features
        features = corpus.api.Fall() if hasattr(corpus.api, "Fall") else []

        # Get total slots
        total_slots = len(corpus.F.otype.s("word")) if hasattr(corpus.F, "otype") else 0

        return CorpusInfo(
            dataset_id=dataset_id,
            node_types=node_types,
            features=list(features),
            total_slots=total_slots,
        )


@strawberry.type
class Query:
    """Root Query"""

    corpus: CorpusQuery = strawberry.field(resolver=lambda: CorpusQuery())
