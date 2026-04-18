# User-Friendly Corpus Queries

## Overview

The BiblePedia GraphQL API provides an intuitive, parameter-based interface for querying biblical and linguistic corpora powered by Context-Fabric. Instead of writing raw search syntax, users interact with structured types and enums.

## Architecture

```
GraphQL Request (User-Friendly Parameters)
    ↓
Strawberry GraphQL Schema (app/graphql/schema.py)
    ↓
Query Resolvers (app/graphql/resolvers/corpus_query.py)
    ↓
Query Builder (Converts parameters → Context-Fabric syntax)
    ↓
Context-Fabric API (app/corpus/)
    ↓
Corpus Data (Local .tf files)
```

## Key Features

### 1. Node Type Enum

```graphql
enum NodeType {
  DOCUMENT
  BOOK
  CHAPTER
  VERSE
  SENTENCE
  CLAUSE
  PHRASE
  WORD
  SLOT
}
```

**Instead of writing**: `"word pos=verb"`
**Users write**: `{nodeType: WORD, features: [{name: "pos", value: "verb"}]}`

### 2. Feature Filters

```graphql
input FeatureFilter {
  name: String!
  value: String!
  operator: String = "="  # =, !=, ~, !~
}
```

**Example**: Find past tense verbs
```graphql
features: [
  {name: "pos", value: "verb"},
  {name: "tense", value: "past"}
]
```

### 3. Hierarchical Patterns

```graphql
input SearchPattern {
  root: NodeQuery!
  children: [SearchPattern!]
  orderConstraint: OrderConstraint
}
```

**Example**: Clauses with subject before predicate
```graphql
pattern: {
  root: {nodeType: CLAUSE},
  children: [
    {root: {nodeType: PHRASE, features: [{name: "function", value: "subject"}]}},
    {root: {nodeType: PHRASE, features: [{name: "function", value: "predicate"}]}, orderConstraint: AFTER}
  ]
}
```

## Available Queries

### `searchSimple`

For single-node searches with feature filters.

```graphql
query {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{name: "pos", value: "verb"}]
      limit: 10
    ) {
      reference
      text
      nodes {
        nodeId
        nodeType
        text
        features
      }
    }
  }
}
```

### `searchHierarchical`

For complex patterns with parent-child relationships.

```graphql
query {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: {nodeType: SENTENCE}
        children: [
          {root: {nodeType: CLAUSE}},
          {root: {nodeType: CLAUSE}}
        ]
      }
      limit: 5
    ) {
      reference
      text
      matchCount
    }
  }
}
```

### `searchText`

For simple text-based searches.

```graphql
query {
  corpus {
    searchText(
      datasetId: "KJV"
      text: "love"
      nodeType: VERSE
      limit: 20
    ) {
      reference
      text
    }
  }
}
```

### Navigation Queries

```graphql
# Get node text
query {
  corpus {
    getNodeText(datasetId: "BHSA", nodeId: 12345)
  }
}

# Get node features
query {
  corpus {
    getNodeFeatures(datasetId: "BHSA", nodeId: 12345)
  }
}

# Get containing nodes (e.g., which verse contains this word?)
query {
  corpus {
    getContainingNodes(
      datasetId: "BHSA"
      nodeId: 12345
      nodeType: VERSE
    ) {
      nodeId
      text
    }
  }
}

# Get contained nodes (e.g., what words are in this clause?)
query {
  corpus {
    getContainedNodes(
      datasetId: "BHSA"
      nodeId: 67890
      nodeType: WORD
    ) {
      nodeId
      text
    }
  }
}
```

### Corpus Metadata

```graphql
query {
  corpus {
    getCorpusInfo(datasetId: "BHSA") {
      datasetId
      nodeTypes
      features
      totalSlots
    }
  }
}
```

## Query Builder Implementation

The `CorpusQueryBuilder` class translates user-friendly parameters into Context-Fabric search syntax:

```python
# User provides:
{
  nodeType: WORD,
  features: [
    {name: "pos", value: "verb"},
    {name: "tense", value: "past"}
  ]
}

# Builder generates:
"word pos=verb tense=past"

# Context-Fabric executes:
results = S.search("word pos=verb tense=past")
```

## Hierarchical Query Translation

```python
# User provides:
{
  root: {nodeType: CLAUSE},
  children: [
    {root: {nodeType: PHRASE, features: [{name: "function", value: "subject"}]}},
    {root: {nodeType: PHRASE, features: [{name: "function", value: "predicate"}]}, orderConstraint: AFTER}
  ]
}

# Builder generates:
"""
clause
  phrase function=subject
  > phrase function=predicate
"""

# Context-Fabric executes with proper ordering constraint
```

## Benefits

1. **Type Safety**: Enum-based node types prevent typos
2. **Discoverability**: GraphQL introspection shows all options
3. **Validation**: Invalid queries caught at GraphQL layer
4. **Documentation**: Self-documenting with GraphQL schema
5. **IDE Support**: Autocomplete and inline docs
6. **Gradual Complexity**: Start simple, add complexity as needed
7. **No Syntax Knowledge**: Users don't need to learn Context-Fabric query language

## Code Organization

```
api/app/graphql/
├── schema.py                      # Main Strawberry schema
├── types/
│   └── corpus.py                  # GraphQL types (NodeType, FeatureFilter, etc.)
└── resolvers/
    └── corpus_query.py            # Query resolvers & query builder
```

## Example Use Cases

### Bible Study App

```graphql
# Find all commands in a book
query FindCommands {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        {name: "pos", value: "verb"},
        {name: "mood", value: "imperative"}
      ]
      limit: 50
    ) {
      reference
      text
    }
  }
}
```

### Linguistic Research

```graphql
# Find VSO word order patterns
query VSOPatterns {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: {nodeType: CLAUSE}
        children: [
          {root: {nodeType: WORD, features: [{name: "pos", value: "verb"}]}},
          {root: {nodeType: PHRASE, features: [{name: "function", value: "subject"}]}, orderConstraint: AFTER},
          {root: {nodeType: PHRASE, features: [{name: "function", value: "object"}]}, orderConstraint: AFTER}
        ]
      }
      limit: 20
    ) {
      reference
      text
    }
  }
}
```

### Text Comparison

```graphql
# Find poetic parallelism
query Parallelism {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: {nodeType: SENTENCE}
        children: [
          {root: {nodeType: CLAUSE, features: [{name: "function", value: "parallel"}]}},
          {root: {nodeType: CLAUSE, features: [{name: "function", value: "parallel"}]}}
        ]
      }
      limit: 15
    ) {
      reference
      text
    }
  }
}
```

## Testing

```bash
# Start GraphQL playground
bun run dev

# Navigate to http://localhost:8000/graphql
# Try the example queries from CORPUS_QUERY_EXAMPLES.md
```

## Related Documentation

- [CORPUS_QUERY_EXAMPLES.md](../CORPUS_QUERY_EXAMPLES.md) - Comprehensive examples
- [Context-Fabric Graph Model](https://context-fabric.ai/docs/concepts/graph-model)
- [CLAUDE.md](../CLAUDE.md) - Architecture overview
