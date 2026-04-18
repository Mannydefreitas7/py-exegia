# Quick Start: User-Friendly Corpus Queries

Get started with the BiblePedia corpus query API in 5 minutes.

## 1. Start the GraphQL Server

```bash
# Install dependencies
bun install
pip install -r requirements.txt

# Start server
bun run dev
```

Server runs on: **http://localhost:8000**

## 2. Open GraphiQL Playground

Navigate to: **http://localhost:8000/graphql**

You'll see an interactive GraphQL IDE with:
- Query editor (left)
- Results panel (right)
- Schema explorer (docs button)
- Query history

## 3. Try Your First Query

### Find All Verbs

Copy this into the query editor:

```graphql
query FindVerbs {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        {name: "pos", value: "verb"}
      ]
      limit: 5
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

Click **Play** ▶️

You should see results like:

```json
{
  "data": {
    "corpus": {
      "searchSimple": [
        {
          "reference": "Genesis 1:1",
          "text": "created",
          "nodes": [
            {
              "text": "created",
              "feature": "ברא"
            }
          ]
        }
      ]
    }
  }
}
```

## 4. Explore Available Options

Click the **Docs** button (top right) to see:

- All available queries
- Node types (WORD, PHRASE, CLAUSE, VERSE, etc.)
- Feature filters
- Search patterns

## 5. Try More Queries

### Search for Text

```graphql
query SearchLove {
  corpus {
    searchText(
      datasetId: "KJV"
      text: "love"
      limit: 3
    ) {
      reference
      text
    }
  }
}
```

### Complex Pattern

```graphql
query SubjectPredicate {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: {nodeType: CLAUSE}
        children: [
          {root: {nodeType: PHRASE, features: [{name: "function", value: "subject"}]}},
          {root: {nodeType: PHRASE, features: [{name: "function", value: "predicate"}]}}
        ]
      }
      limit: 3
    ) {
      reference
      text
    }
  }
}
```

### Get Corpus Info

```graphql
query GetInfo {
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

## 6. Understanding Node Types

### Hierarchy

```
DOCUMENT (entire corpus)
  └── BOOK (e.g., Genesis)
      └── CHAPTER (e.g., Chapter 1)
          └── VERSE (e.g., Genesis 1:1)
              └── SENTENCE
                  └── CLAUSE
                      └── PHRASE
                          └── WORD (individual tokens)
```

### Common Node Types

- **WORD**: Individual words/tokens (most granular)
- **PHRASE**: Groups of words forming phrases
- **CLAUSE**: Grammatical clauses
- **SENTENCE**: Complete sentences
- **VERSE**: Biblical verses
- **CHAPTER**: Chapters
- **BOOK**: Entire books

## 7. Feature Filters

Features are properties of nodes (e.g., part of speech, tense, gender).

### Operators

- `=` - Exact match
- `!=` - Not equal
- `~` - Contains (case-insensitive)
- `!~` - Does not contain

### Examples

```graphql
# Find masculine nouns
features: [
  {name: "pos", value: "noun"},
  {name: "gender", value: "masculine"}
]

# Find non-verbs
features: [
  {name: "pos", value: "verb", operator: "!="}
]

# Case-insensitive lemma search
features: [
  {name: "lemma", value: "love", operator: "~"}
]
```

## 8. Order Constraints

Control the sequence of nodes in patterns:

- `BEFORE` (`<`) - First must come before second
- `AFTER` (`>`) - First must come after second
- `ADJACENT` (`..`) - Nodes must be adjacent

```graphql
# Predicate BEFORE subject (VSO word order)
children: [
  {root: {nodeType: PHRASE, features: [{name: "function", value: "predicate"}]}},
  {root: {nodeType: PHRASE, features: [{name: "function", value: "subject"}]}, orderConstraint: AFTER}
]
```

## 9. Common Patterns

### Word Study

Find all occurrences of a Hebrew/Greek word:

```graphql
query HebrewWord {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{name: "lemma", value: "אהב"}]  # Hebrew: love
      limit: 10
    ) {
      reference
      text
      nodes {
        text
        feature(name: "tense")
        feature(name: "pos")
      }
    }
  }
}
```

### Find Questions

```graphql
query Questions {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: SENTENCE
      features: [{name: "type", value: "interrogative"}]
      limit: 5
    ) {
      reference
      text
    }
  }
}
```

### Find Commands

```graphql
query Commands {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        {name: "pos", value: "verb"},
        {name: "mood", value: "imperative"}
      ]
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

## 10. Navigation

### Get Verse Containing a Word

```graphql
query GetVerse {
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
```

### Get All Words in a Clause

```graphql
query GetWords {
  corpus {
    getContainedNodes(
      datasetId: "BHSA"
      nodeId: 67890
      nodeType: WORD
    ) {
      nodeId
      text
      features
    }
  }
}
```

## Next Steps

1. **Read Examples**: See [CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md) for 30+ examples
2. **Understand Flow**: Read [docs/QUERY_FLOW.md](docs/QUERY_FLOW.md) for architecture
3. **Learn Context-Fabric**: Visit https://context-fabric.ai/docs/core
4. **Explore BHSA**: Learn about Hebrew Bible features at https://github.com/ETCBC/bhsa

## Troubleshooting

### Corpus Not Found

```json
{
  "errors": [{
    "message": "Corpus 'BHSA' not found"
  }]
}
```

**Solution**: Download and extract the BHSA dataset to `/app/datasets/BHSA/`

### No Results

- Check that `limit` is set high enough
- Verify feature names and values are correct
- Use `getCorpusInfo` to see available features
- Try simpler queries first

### GraphiQL Not Loading

- Ensure server is running on port 8000
- Check console for errors
- Try http://localhost:8000/health

## Resources

- **Examples**: [CORPUS_QUERY_EXAMPLES.md](CORPUS_QUERY_EXAMPLES.md)
- **Implementation**: [docs/FRIENDLY_QUERIES.md](docs/FRIENDLY_QUERIES.md)
- **Architecture**: [docs/QUERY_FLOW.md](docs/QUERY_FLOW.md)
- **Context-Fabric**: https://context-fabric.ai/docs/core
- **Strawberry**: https://strawberry.rocks

## Support

Questions? Check:
1. Schema docs (GraphiQL Docs button)
2. Example queries (CORPUS_QUERY_EXAMPLES.md)
3. Context-Fabric documentation
4. GitHub issues

Happy querying! 🎯
