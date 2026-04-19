# GraphQL API Module

Strawberry GraphQL layer that provides user-friendly, type-safe access to Context-Fabric corpus queries and user data operations.

## Overview

This module exposes the Exegia API through a modern GraphQL interface, abstracting the technical Context-Fabric query syntax into intuitive, parameter-based queries.

## Architecture

```
Client Request (GraphQL)
    ↓
schema.py (Main Schema)
    ↓
resolvers/ (Query/Mutation Handlers)
    ↓
types/ (GraphQL Types & Inputs)
    ↓
[Context-Fabric API | Supabase]
    ↓
Response (Typed GraphQL Data)
```

## Files Structure

```
app/graphql/
├── schema.py                   # Main Strawberry schema
├── types/
│   ├── corpus.py               # Corpus query types
│   ├── user.py                 # User data types
│   └── dataset.py              # Dataset types
└── resolvers/
    ├── corpus_query.py         # Corpus query resolvers
    ├── user_data.py            # User data resolvers
    └── dataset.py              # Dataset resolvers
```

## Main Schema (`schema.py`)

Entry point for all GraphQL operations.

```python
import strawberry
from app.graphql.resolvers.corpus_query import CorpusQuery

@strawberry.type
class Query:
    @strawberry.field
    def corpus(self) -> CorpusQuery:
        """Access corpus query operations"""
        return CorpusQuery()

@strawberry.type
class Mutation:
    # User data mutations

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

## User-Friendly Query Interface

### Key Features

- **Node Type Enum**: WORD, PHRASE, CLAUSE, SENTENCE, VERSE, CHAPTER, BOOK, DOCUMENT
- **Feature Filters**: Filter by grammatical, semantic, or structural properties
- **Hierarchical Patterns**: Define parent-child relationships with order constraints
- **Text Search**: Simple text-based searches across node types

## GraphQL Types (`types/corpus.py`)

### Enums

```python
@strawberry.enum
class NodeType(Enum):
    """Available node types in corpus graph"""
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
    BEFORE = "<"
    AFTER = ">"
    ADJACENT = ".."
```

### Input Types

```python
@strawberry.input
class FeatureFilter:
    """Filter nodes by feature values"""
    name: str
    value: str
    operator: str = "="  # =, !=, ~, !~

@strawberry.input
class NodeQuery:
    """Query parameters for a single node"""
    node_type: NodeType
    features: Optional[List[FeatureFilter]] = None
    quantifier: Optional[str] = None
    label: Optional[str] = None

@strawberry.input
class SearchPattern:
    """Hierarchical search pattern"""
    root: NodeQuery
    children: Optional[List["SearchPattern"]] = None
    order_constraint: Optional[OrderConstraint] = None
```

### Output Types

```python
@strawberry.type
class NodeResult:
    """A single node in search results"""
    node_id: int
    node_type: str
    text: str
    features: strawberry.scalars.JSON

    @strawberry.field
    def feature(self, name: str) -> Optional[str]:
        return self.features.get(name)

@strawberry.type
class SearchResult:
    """Result from a corpus search"""
    reference: str
    text: str
    nodes: List[NodeResult]
    match_count: int

@strawberry.type
class CorpusInfo:
    """Information about a loaded corpus"""
    dataset_id: str
    node_types: List[str]
    features: List[str]
    total_slots: int
```

## Resolvers (`resolvers/corpus_query.py`)

### Query Builder

Translates user-friendly parameters into Context-Fabric syntax:

```python
class CorpusQueryBuilder:
    @staticmethod
    def build_simple_query(
        node_type: NodeType,
        features: Optional[List[FeatureFilter]] = None
    ) -> str:
        """Build simple query: {nodeType: WORD, features: [...]} → "word pos=verb" """
        query = node_type.value

        if features:
            for f in features:
                if f.operator == "=":
                    query += f" {f.name}={f.value}"
                # ... other operators

        return query
```

### Resolver Methods

```python
@strawberry.type
class CorpusQuery:
    @strawberry.field
    def search_simple(...) -> List[SearchResult]:
        """Simple search for single node type"""

    @strawberry.field
    def search_hierarchical(...) -> List[SearchResult]:
        """Hierarchical search with nested patterns"""

    @strawberry.field
    def search_text(...) -> List[SearchResult]:
        """Text-based search"""

    @strawberry.field
    def get_containing_nodes(...) -> List[NodeResult]:
        """Get ancestor nodes"""

    @strawberry.field
    def get_contained_nodes(...) -> List[NodeResult]:
        """Get descendant nodes"""
```

## Integration with Context-Fabric

```python
# In resolver
corpus_manager = CorpusManager()
corpus = corpus_manager.load(dataset_id)

# Build query
query = CorpusQueryBuilder.build_simple_query(node_type, features)

# Execute with Context-Fabric
results = corpus.S.search(query)

# Convert to GraphQL types
graphql_results = [SearchResult.from_cf_result(r, corpus.api) for r in results]
```

## Endpoints

- **POST /graphql** - GraphQL endpoint (production)
- **GET /graphql** - GraphiQL playground (development)

## Testing Queries

Open GraphiQL at **http://localhost:8000/graphql**

Try example queries from:

- @./app/corpus/EXAMPLES.md

## Benefits

✅ **Type Safety** - Strawberry enforces types at compile time
✅ **Discoverability** - GraphQL introspection shows all options
✅ **Validation** - Invalid queries caught before execution
✅ **Documentation** - Self-documenting through schema
✅ **IDE Support** - Autocomplete and inline docs

## Common Patterns

See **QUERY_EXAMPLES** for:

- Word studies
- Finding questions
- Finding commands
- Parallel structures
- VSO word order
- And 25+ more examples
