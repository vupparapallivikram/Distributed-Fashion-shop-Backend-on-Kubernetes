# Lab 2 - Task 2: Keyword Search Results

## PostgreSQL Full-Text Search (tsvector)

| Check | Query | Result | Status |
|---|---|---|---|
| Basic search | superman | 29 items found | ✅ |
| OR search | superman or batman | 58 items found | ✅ |
| Stemming | dance | 7 items found | ✅ |
| Typo | supermax | 0 items found | ❌ |
| Synonyms | soccer jersey | 2 items found | ✅ partial |

## OpenSearch Full-Text Search

| Check | Query | Result | Status |
|---|---|---|---|
| Basic search | superman | 29 items with scores | ✅ |
| OR search | superman or batman | works | ✅ |
| Stemming | dancing | finds dance items | ✅ |
| Typo | supermax | finds superman! | ✅ fuzzy |
| Synonyms | German soccer jersey | finds football items | ✅ |
| Field boost | title^2 | title matches ranked higher | ✅ |

## Comparison: PostgreSQL vs OpenSearch

| Feature | PostgreSQL | OpenSearch |
|---|---|---|
| Basic search | ✅ | ✅ |
| OR/AND | ✅ | ✅ |
| Stemming | ✅ | ✅ |
| Typos | ❌ | ✅ fuzzy matching |
| Relevance score | ❌ | ✅ |
| Title boosting | ❌ | ✅ title^2 |

## Key Finding
OpenSearch handles typos via fuzzy matching.
PostgreSQL tsvector requires exact word matches.
OpenSearch ranks results by relevance score — better UX.

## Synchronization
Items synced from PostgreSQL to OpenSearch using Python script.
44,446 items synced with: id, title, description, reviews array.
Zero errors during sync.

## GIN Index (PostgreSQL)
Created for fast full-text search:
CREATE INDEX idx_items_fts ON items 
USING GIN(to_tsvector('english', 
  COALESCE(display_name,'') || ' ' || 
  COALESCE(data->>'description','')));
