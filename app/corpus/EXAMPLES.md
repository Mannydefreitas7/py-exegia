# Corpus Query Examples

User-friendly GraphQL API for querying biblical and linguistic corpora using Context-Fabric.

## Table of Contents

- [Introduction](#introduction)
- [Node Types](#node-types)
- [Simple Queries](#simple-queries)
- [Feature Filtering](#feature-filtering)
- [Hierarchical Queries](#hierarchical-queries)
- [Text Search](#text-search)
- [Navigation Queries](#navigation-queries)
- [Common Bible Study Patterns](#common-bible-study-patterns)
- [Advanced Queries](#advanced-queries)

## Introduction

The Context-Fabric GraphQL API provides an intuitive way to query annotated text corpora without needing to write raw search patterns. Instead of writing complex query syntax, you use simple parameters:

- **Node Types**: `WORD`, `PHRASE`, `CLAUSE`, `SENTENCE`, `VERSE`, `CHAPTER`, `BOOK`, `DOCUMENT`
- **Feature Filters**: Filter by grammatical, semantic, or structural properties
- **Hierarchical Patterns**: Define parent-child relationships
- **Order Constraints**: Specify ordering requirements

## Node Types

The corpus graph is organized hierarchically:

```
DOCUMENT (or BOOK)
  └── CHAPTER
      └── VERSE
          └── SENTENCE
              └── CLAUSE
                  └── PHRASE
                      └── WORD (SLOT)
```

Each node type represents a different level of text structure.

## Simple Queries

### Find All Verbs

```graphql
query FindVerbs {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{ name: "pos", value: "verb" }]
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

**What it finds**: All word nodes with part-of-speech = "verb"

### Find All Clauses

```graphql
query FindClauses {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: CLAUSE
      limit: 20
    ) {
      reference
      text
      matchCount
    }
  }
}
```

**What it finds**: All clause nodes in the corpus

### Find Specific Verses

```graphql
query FindVerses {
  corpus {
    searchSimple(
      datasetId: "KJV"
      nodeType: VERSE
      limit: 50
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: Individual verses with their references

## Feature Filtering

### Find Past Tense Verbs

```graphql
query PastTenseVerbs {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        { name: "pos", value: "verb" }
        { name: "tense", value: "past" }
      ]
      limit: 15
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

**What it finds**: Verbs in past tense

### Find Nouns with Specific Gender

```graphql
query MasculineNouns {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        { name: "pos", value: "noun" }
        { name: "gender", value: "masculine" }
      ]
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: Masculine nouns

### Case-Insensitive Text Matching

```graphql
query FindLove {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{ name: "lemma", value: "love", operator: "~" }]
      limit: 20
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

**What it finds**: Words with lemma matching "love" (case-insensitive with `~` operator)

### Exclude Values

```graphql
query NonVerbs {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{ name: "pos", value: "verb", operator: "!=" }]
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: All words that are NOT verbs

## Hierarchical Queries

### Clauses Containing Verbs

```graphql
query ClausesWithVerbs {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE }
        children: [{ root: { nodeType: WORD, features: [{ name: "pos", value: "verb" }] } }]
      }
      limit: 10
    ) {
      reference
      text
      nodes {
        nodeType
        text
      }
    }
  }
}
```

**What it finds**: Clauses that contain at least one verb

### Subject-Predicate Phrases

```graphql
query SubjectPredicate {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE }
        children: [
          {
            root: { nodeType: PHRASE, features: [{ name: "function", value: "subject" }] }
          }
          {
            root: { nodeType: PHRASE, features: [{ name: "function", value: "predicate" }] }
          }
        ]
      }
      limit: 15
    ) {
      reference
      text
      matchCount
    }
  }
}
```

**What it finds**: Clauses containing both a subject phrase and a predicate phrase

### Predicate Before Subject (Word Order)

```graphql
query PredicateBeforeSubject {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE }
        children: [
          {
            root: { nodeType: PHRASE, features: [{ name: "function", value: "predicate" }] }
          }
          {
            root: { nodeType: PHRASE, features: [{ name: "function", value: "subject" }] }
            orderConstraint: AFTER
          }
        ]
      }
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: Clauses where the predicate comes BEFORE the subject (VSO word order)

### Sentences with Multiple Clauses

```graphql
query MultiClauseSentences {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: SENTENCE }
        children: [
          { root: { nodeType: CLAUSE } }
          { root: { nodeType: CLAUSE } }
          { root: { nodeType: CLAUSE } }
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

**What it finds**: Sentences containing at least 3 clauses

### Nested Phrases

```graphql
query NestedPhrases {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: PHRASE }
        children: [
          {
            root: { nodeType: PHRASE }
            children: [{ root: { nodeType: WORD, features: [{ name: "pos", value: "noun" }] } }]
          }
        ]
      }
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: Phrases containing nested phrases which contain nouns

## Text Search

### Simple Text Search

```graphql
query SearchLove {
  corpus {
    searchText(datasetId: "KJV", text: "love", limit: 20) {
      reference
      text
      nodes {
        text
      }
    }
  }
}
```

**What it finds**: All occurrences of the word "love"

### Case-Sensitive Search

```graphql
query SearchGod {
  corpus {
    searchText(datasetId: "KJV", text: "God", caseSensitive: true, limit: 15) {
      reference
      text
    }
  }
}
```

**What it finds**: Exact matches for "God" (capital G)

### Search in Specific Node Type

```graphql
query SearchInVerses {
  corpus {
    searchText(datasetId: "KJV", text: "salvation", nodeType: VERSE, limit: 10) {
      reference
      text
    }
  }
}
```

**What it finds**: Verses containing "salvation"

## Navigation Queries

### Get Text of a Node

```graphql
query GetNodeText {
  corpus {
    getNodeText(datasetId: "BHSA", nodeId: 12345)
  }
}
```

**What it returns**: The text content of node 12345

### Get All Features of a Node

```graphql
query GetNodeFeatures {
  corpus {
    getNodeFeatures(datasetId: "BHSA", nodeId: 12345)
  }
}
```

**What it returns**: JSON object with all feature values for node 12345

### Get Containing Verse

```graphql
query GetContainingVerse {
  corpus {
    getContainingNodes(datasetId: "BHSA", nodeId: 12345, nodeType: VERSE) {
      nodeId
      text
      features
    }
  }
}
```

**What it finds**: The verse (or verses) containing word node 12345

### Get All Words in a Clause

```graphql
query GetWordsInClause {
  corpus {
    getContainedNodes(datasetId: "BHSA", nodeId: 67890, nodeType: WORD) {
      nodeId
      text
      features
    }
  }
}
```

**What it finds**: All word nodes contained within clause 67890

### Get Corpus Information

```graphql
query GetCorpusInfo {
  corpus {
    getCorpusInfo(datasetId: "BHSA") {
      datasetId
      nodeTypes
      features
      totalSlots
      description
    }
  }
}
```

**What it returns**: Metadata about the corpus (available node types, features, etc.)

## Common Bible Study Patterns

### Find All Occurrences of a Hebrew/Greek Word

```graphql
query HebrewWordStudy {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [{ name: "lemma", value: "אהב", operator: "=" }] # Hebrew: love
      limit: 50
    ) {
      reference
      text
      nodes {
        text
        feature(name: "lemma")
        feature(name: "pos")
        feature(name: "tense")
      }
    }
  }
}
```

**Use case**: Word study - find all forms of a specific lemma

### Find Questions

```graphql
query FindQuestions {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: SENTENCE
      features: [{ name: "type", value: "interrogative" }]
      limit: 20
    ) {
      reference
      text
    }
  }
}
```

**Use case**: Find interrogative sentences (questions)

### Find Direct Speech

```graphql
query DirectSpeech {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: CLAUSE
      features: [{ name: "domain", value: "Q" }] # Quotation
      limit: 15
    ) {
      reference
      text
    }
  }
}
```

**Use case**: Find quoted/direct speech

### Find Imperative Verbs (Commands)

```graphql
query FindCommands {
  corpus {
    searchSimple(
      datasetId: "BHSA"
      nodeType: WORD
      features: [
        { name: "pos", value: "verb" }
        { name: "mood", value: "imperative" }
      ]
      limit: 25
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

**Use case**: Find commands in the text

### Find Parallel Structures

```graphql
query ParallelClauses {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: SENTENCE }
        children: [
          {
            root: { nodeType: CLAUSE, features: [{ name: "function", value: "parallel" }] }
          }
          {
            root: { nodeType: CLAUSE, features: [{ name: "function", value: "parallel" }] }
          }
        ]
      }
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**Use case**: Find poetic parallelism

## Advanced Queries

### Quantifiers - Find Clauses with 3+ Words

```graphql
query LongClauses {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE }
        children: [
          { root: { nodeType: WORD, quantifier: "{3,}" } } # 3 or more words
        ]
      }
      limit: 10
    ) {
      reference
      text
      matchCount
    }
  }
}
```

**What it finds**: Clauses containing 3 or more words

### Optional Elements

```graphql
query ClauseWithOptionalObject {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE }
        children: [
          { root: { nodeType: PHRASE, features: [{ name: "function", value: "subject" }] } }
          { root: { nodeType: PHRASE, features: [{ name: "function", value: "predicate" }] } }
          {
            root: {
              nodeType: PHRASE
              features: [{ name: "function", value: "object" }]
              quantifier: "?"
            }
          } # Optional
        ]
      }
      limit: 10
    ) {
      reference
      text
    }
  }
}
```

**What it finds**: Clauses with subject and predicate, optionally with an object

### Labeled Results

```graphql
query LabeledQuery {
  corpus {
    searchHierarchical(
      datasetId: "BHSA"
      pattern: {
        root: { nodeType: CLAUSE, label: "mainClause" }
        children: [
          { root: { nodeType: WORD, features: [{ name: "pos", value: "verb" }], label: "verb" } }
          { root: { nodeType: WORD, features: [{ name: "pos", value: "noun" }], label: "noun" } }
        ]
      }
      limit: 5
    ) {
      reference
      text
      nodes {
        nodeType
        text
      }
    }
  }
}
```

**What it finds**: Clauses with labeled verb and noun nodes (useful for complex queries)

## Operator Reference

### Feature Filter Operators

- `=` - Exact match (case-sensitive)
- `!=` - Not equal
- `~` - Contains/matches (case-insensitive)
- `!~` - Does not contain/match (case-insensitive)

### Quantifiers

- `*` - Zero or more
- `+` - One or more
- `?` - Zero or one (optional)
- `{n}` - Exactly n
- `{n,}` - n or more
- `{n,m}` - Between n and m (inclusive)

### Order Constraints

- `BEFORE` (`<`) - First node must come before second
- `AFTER` (`>`) - First node must come after second
- `ADJACENT` (`..`) - Nodes must be directly adjacent

## Tips for Effective Queries

1. **Start Simple**: Begin with basic searches and add complexity gradually
2. **Check Corpus Info**: Use `getCorpusInfo` to see available node types and features
3. **Use Limits**: Always set reasonable limits to avoid overwhelming results
4. **Feature Discovery**: Use `getNodeFeatures` on sample nodes to discover available features
5. **Hierarchical Thinking**: Think in terms of containment (clauses contain phrases, phrases contain words)
6. **Test Incrementally**: Test each level of a hierarchical query before adding more nesting

## Related Resources

- [Context-Fabric Graph Model](https://context-fabric.ai/docs/concepts/graph-model)
- [Text-Fabric Search Documentation](https://annotation.github.io/text-fabric/tf/about/searchusage.html)
- [BHSA Corpus Features](https://github.com/ETCBC/bhsa)
