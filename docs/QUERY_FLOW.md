# Query Flow: From User to Context-Fabric

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                           │
│  (Desktop App, Web Browser, Mobile App)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ GraphQL Query
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STRAWBERRY GRAPHQL API                        │
│                   (app/graphql/schema.py)                        │
│                                                                  │
│  User-Friendly Query:                                           │
│  {                                                               │
│    nodeType: WORD                                                │
│    features: [{name: "pos", value: "verb"}]                      │
│  }                                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Python Objects
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       QUERY RESOLVER                             │
│            (app/graphql/resolvers/corpus_query.py)               │
│                                                                  │
│  Validates input, calls CorpusQueryBuilder                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Structured Parameters
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY BUILDER                               │
│                  (CorpusQueryBuilder)                            │
│                                                                  │
│  Translates:                                                     │
│  {nodeType: WORD, features: [{name: "pos", value: "verb"}]}      │
│  →                                                               │
│  "word pos=verb"                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Context-Fabric Query String
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CORPUS MANAGER                               │
│                  (app/corpus/manager.py)                         │
│                                                                  │
│  Loads corpus from local filesystem                              │
│  Manages corpus instances                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Loaded Corpus API
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT-FABRIC API                            │
│                    (cfabric library)                             │
│                                                                  │
│  S.search("word pos=verb")                                       │
│  → Returns: [(node1), (node2), ...]                              │
│                                                                  │
│  T.text(node)                                                    │
│  F.lemma.v(node)                                                 │
│  L.u(node, otype='verse')                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Node Results
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULT CONVERTER                              │
│              (SearchResult.from_cf_result)                       │
│                                                                  │
│  Converts Context-Fabric tuples to GraphQL types                 │
│  Enriches with text, features, references                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ GraphQL Response
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT RESPONSE                             │
│                                                                  │
│  {                                                               │
│    reference: "Genesis 1:1",                                     │
│    text: "In the beginning",                                     │
│    nodes: [                                                      │
│      {nodeId: 1, nodeType: "word", text: "created", ...}         │
│    ]                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Step 1: User Query

```graphql
query {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        {name: "pos", value: "verb"},
        {name: "tense", value: "past"}
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

### Step 2: GraphQL Schema Routing

```python
# schema.py
@strawberry.type
class Query:
    corpus: CorpusQuery = strawberry.field(resolver=lambda: CorpusQuery())
```

Routes to `CorpusQuery.searchSimple()`

### Step 3: Resolver Processing

```python
# corpus_query.py
@strawberry.field
def search_simple(
    self,
    dataset_id: str,
    node_type: NodeType,
    features: Optional[List[FeatureFilter]] = None,
    limit: int = 100,
) -> List[SearchResult]:
    # Get corpus instance
    corpus_manager = CorpusManager()
    corpus = corpus_manager.load(dataset_id)
    
    # Build query string
    query = CorpusQueryBuilder.build_simple_query(node_type, features)
    # Result: "word pos=verb tense=past"
    
    # Execute
    results = corpus.S.search(query)
    
    # Convert to GraphQL types
    return [SearchResult.from_cf_result(r, corpus.api) for r in results]
```

### Step 4: Query Builder Translation

```python
@staticmethod
def build_simple_query(node_type: NodeType, features: Optional[List[FeatureFilter]]):
    query = node_type.value  # "word"
    
    if features:
        for f in features:
            query += f" {f.name}={f.value}"  # " pos=verb tense=past"
    
    return query  # "word pos=verb tense=past"
```

### Step 5: Context-Fabric Execution

```python
# Context-Fabric API (cfabric)
results = corpus.S.search("word pos=verb tense=past")
# Returns: [(node_12345,), (node_12346,), (node_12347,), ...]

# For each node, extract data:
for (node,) in results:
    text = corpus.T.text(node)           # "created"
    lemma = corpus.F.lemma.v(node)       # "ברא"
    verse = corpus.L.u(node, otype='verse')[0]  # node_67890
    reference = get_reference(verse)     # "Genesis 1:1"
```

### Step 6: Result Conversion

```python
@classmethod
def from_cf_result(cls, cf_result: tuple, api: Any) -> "SearchResult":
    nodes = []
    for node in cf_result:
        node_type = api.F.otype.v(node)
        text = api.T.text(node)
        
        # Gather features
        features = {}
        for feature_name in api.Fall():
            value = getattr(api.F, feature_name).v(node)
            if value:
                features[feature_name] = value
        
        nodes.append(NodeResult(
            node_id=node,
            node_type=node_type,
            text=text,
            features=features
        ))
    
    reference = _get_reference(cf_result[0], api)
    
    return SearchResult(
        reference=reference,
        text=" ".join([n.text for n in nodes]),
        nodes=nodes,
        match_count=len(nodes)
    )
```

### Step 7: GraphQL Response

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
        },
        {
          "reference": "Genesis 1:21",
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

## Key Benefits of This Architecture

### 1. Type Safety
- GraphQL validates all inputs before execution
- Enums prevent invalid node types
- Required fields enforced

### 2. Abstraction
- Users don't need to learn Context-Fabric query syntax
- Intuitive parameter-based interface
- Progressive complexity (simple → hierarchical)

### 3. Flexibility
- Simple queries for common cases
- Hierarchical queries for complex patterns
- Raw query support for advanced users (if needed)

### 4. Performance
- Query builder is fast (string manipulation)
- Context-Fabric handles heavy lifting efficiently
- Results cached at corpus level

### 5. Discoverability
- GraphQL introspection shows all options
- Documentation built into schema
- IDE autocomplete support

## Comparison: Before vs After

### Before (Raw Context-Fabric)

```python
# User needs to know syntax
query = """
clause
  phrase function=Pred
    word sp=verb
"""
results = corpus.S.search(query)

# Manual result processing
for clause, phrase, word in results:
    print(T.text(clause))
```

### After (User-Friendly GraphQL)

```graphql
# Intuitive, structured parameters
query {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: {nodeType: CLAUSE}
        children: [
          {
            root: {nodeType: PHRASE, features: [{name: "function", value: "Pred"}]}
            children: [
              {root: {nodeType: WORD, features: [{name: "sp", value: "verb"}]}}
            ]
          }
        ]
      }
    ) {
      reference
      text
    }
  }
}
```

## Performance Considerations

1. **Query Building**: O(n) where n = number of parameters (very fast)
2. **Corpus Loading**: One-time cost per dataset (cached)
3. **Search Execution**: Depends on corpus size and query complexity
4. **Result Conversion**: O(m) where m = number of results

## Error Handling

```
User Query Error
    → GraphQL validation error (400)
    → User-friendly error message

Query Builder Error
    → Invalid parameters detected early
    → Helpful error message

Context-Fabric Error
    → Caught and wrapped
    → Returned as structured GraphQL error

Result Conversion Error
    → Graceful degradation
    → Partial results returned with warning
```

## Next Steps

1. **Test with Real Corpora**: Download BHSA and test queries
2. **Add More Node Types**: Extend NodeType enum as needed
3. **Feature Discovery**: Implement dynamic feature listing
4. **Query Templates**: Pre-built queries for common patterns
5. **Performance Optimization**: Caching, pagination, streaming
