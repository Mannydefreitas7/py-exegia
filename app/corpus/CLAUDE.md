# Context-Fabric Corpus Integration

This module integrates the Context-Fabric Python API with the Exegia backend, enabling powerful corpus queries through a user-friendly GraphQL interface.

## Overview

Context-Fabric provides a Python API for querying annotated text corpora represented as directed graphs. This module wraps that API and exposes it through Strawberry GraphQL resolvers.

## Components

### `manager.py` - Corpus Management

Handles loading, caching, and managing Text-Fabric corpus instances.

```python
from app.corpus.manager import CorpusManager

manager = CorpusManager(base_path="/app/datasets")
corpus = manager.load("BHSA")

# Corpus object provides Context-Fabric API:
# - corpus.F (Features)
# - corpus.L (Locality)
# - corpus.T (Text)
# - corpus.S (Search)
# - corpus.N (Nodes)
```

### `query.py` - Query Interface (Future)

Higher-level query interface and utilities.

## Context-Fabric API

The loaded corpus provides these APIs:

### `F` - Features

Access node feature values:

```python
# Get part of speech for a word node
pos = corpus.F.pos.v(node_id)

# Get lemma
lemma = corpus.F.lemma.v(node_id)

# Find all nodes with a specific feature value
verbs = corpus.F.pos.s("verb")
```

### `L` - Locality (Navigation)

Navigate the graph hierarchy:

```python
# Get all words in a clause (down)
words = corpus.L.d(clause_node, otype="word")

# Get containing verse for a word (up)
verse = corpus.L.u(word_node, otype="verse")[0]

# Get next word (next)
next_word = corpus.L.n(word_node, otype="word")[0]

# Get previous clause (previous)
prev_clause = corpus.L.p(clause_node, otype="clause")[0]
```

### `T` - Text

Extract text content:

```python
# Get text of a node
text = corpus.T.text(node_id)

# Get text with custom separators
text = corpus.T.text(node_id, fmt="text-phono-full")
```

### `S` - Search

Execute search patterns:

```python
# Simple search
results = corpus.S.search("word pos=verb")

# Hierarchical search
results = corpus.S.search("""
clause
  phrase function=Pred
    word sp=verb
""")

# Iterate results
for clause, phrase, word in results:
    print(corpus.T.text(clause))
```

### `N` - Nodes

Iterate through nodes:

```python
# Get all nodes
for node in corpus.N.walk():
    print(node)

# Get nodes of a specific type
for verse in corpus.N.walk(otype="verse"):
    print(corpus.T.text(verse))
```

## GraphQL Integration

The Strawberry GraphQL API provides a user-friendly wrapper around these low-level APIs.

See:

- `app/graphql/resolvers/corpus_query.py` - GraphQL resolvers
- `app/graphql/types/corpus.py` - GraphQL types
- `CORPUS_QUERY_EXAMPLES.md` - Usage examples

## Corpus Storage

Corpora are stored as Text-Fabric datasets:

```
/app/datasets/
├── BHSA/                    # Hebrew Bible (ETCBC)
│   ├── .tf/                 # Text-Fabric files
│   │   ├── otype.tf
│   │   ├── pos.tf
│   │   ├── lemma.tf
│   │   └── ...
│   └── tfconfig.yaml        # Corpus metadata
├── KJV/                     # King James Version
└── ...
```

## Loading Process

1. **User downloads dataset** (from Supabase Storage)
2. **Extract to local path** (`/app/datasets/{dataset_id}/`)
3. **Load via CorpusManager** (`manager.load(dataset_id)`)
4. **Query via GraphQL** (user-friendly interface)

## Example Usage

### Direct API (Advanced)

```python
from app.corpus import CorpusManager

# Load corpus
manager = CorpusManager()
corpus = manager.load("BHSA")

# Execute search
results = corpus.S.search("word pos=verb tense=past")

# Process results
for (word_node,) in results:
    lemma = corpus.F.lemma.v(word_node)
    text = corpus.T.text(word_node)
    verse_nodes = corpus.L.u(word_node, otype="verse")

    if verse_nodes:
        verse_text = corpus.T.text(verse_nodes[0])
        print(f"{lemma}: {text} in {verse_text}")
```

### GraphQL API (User-Friendly)

```graphql
query FindPastTenseVerbs {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{ name: "pos", value: "verb" }, { name: "tense", value: "past" }]
      limit: 10
    ) {
      reference
      text
      nodes {
        text
        feature(name: "lemma")
      }
    }
  }
}
```

## Performance Considerations

- **Corpus loading**: One-time cost per dataset (cached in memory)
- **Feature access**: Memory-mapped, very fast (O(1))
- **Search**: Depends on query complexity and corpus size
- **Text extraction**: Fast for individual nodes, slower for large ranges

## Resources

- [Context-Fabric Documentation](https://context-fabric.ai/docs/core)
- [Graph Data Model](https://context-fabric.ai/docs/concepts/graph-model)
- [Text-Fabric Compatibility](https://context-fabric.ai/docs/concepts/text-fabric-compatibility)
