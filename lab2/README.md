# DDIS Lab 2 — Derived Data for Search and Analytical Queries

## Student Information

| Field | Value |
|---|---|
| Student | Vikram Vupparapalli |
| Student | Rakesh Kalamakuntla |
| Course | Distributed Data Intensive Systems (DDIS) |
| Lab | Lab 2 |
| Namespace | team8 |

***

## Introduction

In this lab, the Fashion Shop application from Lab 1 was extended with advanced filtering, PostgreSQL full-text keyword search, OpenSearch integration, semantic vector search, and analytical queries using DuckDB.

The goal was to compare the strengths of PostgreSQL as a row-store transactional database, OpenSearch as a search engine, and DuckDB as a column-store analytical database.

***

## System Architecture

### Components

| Component | Purpose |
|---|---|
| PostgreSQL | Main transactional database |
| FastAPI | Backend REST API |
| OpenSearch | Keyword and vector search |
| DuckDB | Analytical processing |
| Web App | Frontend interface |

***

# 1. Task 1 — Filter Item Catalog

## 1.1 Goal

Extend the `/items` API route to support:

- Color filtering
- Type filtering
- Category filtering
- Price ranges
- Multiple filter values

## 1.2 API Filters

### Example API Calls

#### Multiple Filters

```bash
curl "http://localhost:8080/items?color=pink,green&type=socks"
```

#### Price Range

```bash
curl "http://localhost:8080/items?price_min=100&price_max=500"
```

#### Combined Filters

```bash
curl "http://localhost:8080/items?color=blue&type=shoes&price_max=1000"
```

## 1.3 SQL Query

```sql
WHERE color = ANY(%s)
  AND type = ANY(%s)
  AND category = ANY(%s)
  AND discounted_price >= %s
  AND discounted_price <= %s
```

## 1.4 Web Application

The web application was implemented using:

- HTML
- CSS
- JavaScript

### Features

- Filter inputs
- Keyword search
- Vector search toggle
- Pagination
- Response time display
- Result count display

### Screenshot — Web App Filters

**Command Used**

```bash
kubectl port-forward service/ddis-api-service 8080:80 -n team8
```

**Screenshot placeholder:** [Add screenshot here](screenshots/01-filter-webapp.png)

## 1.5 Results

The API successfully supported:

- Multiple filter values
- Combinations of filters
- Pagination
- Good response times during filtering

***

# 2. Task 2 — Keyword Search

Two approaches were implemented:

- PostgreSQL Full-Text Search
- OpenSearch

## 2.1 PostgreSQL Full-Text Search

### API Example

```bash
curl "http://localhost:8080/items?search=superman"
```

## 2.2 PostgreSQL Search Query

```sql
to_tsvector(
    'english',
    COALESCE(display_name,'') || ' ' ||
    COALESCE(data->>'description','')
)
@@ websearch_to_tsquery('english', %s)
```

## 2.3 GIN Index

### Index Creation

```sql
CREATE INDEX idx_items_search
ON items
USING GIN (
    to_tsvector(
        'english',
        COALESCE(display_name,'') || ' ' ||
        COALESCE(data->>'description','')
    )
);
```

## 2.4 PostgreSQL Search Features

| Feature | Supported |
|---|---|
| Basic search | Yes |
| OR search | Yes |
| Stemming | Yes |
| Typo tolerance | No |

### PostgreSQL Search Examples

#### OR Search

```bash
curl "http://localhost:8080/items?search=superman OR batman"
```

#### Stemming

```bash
curl "http://localhost:8080/items?search=dancing shoes"
```

### Screenshot — PostgreSQL Search

**Screenshot placeholder:** [Add screenshot here](screenshots/02-postgres-search.png)

## 2.5 OpenSearch Deployment

OpenSearch 2.11.0 was deployed as a StatefulSet in the `team8` namespace.

### Deployment Command

```bash
kubectl apply -f k8s/opensearch-statefulset.yaml -n team8
```

### Check StatefulSet

```bash
kubectl get pods -n team8
```

### Screenshot — OpenSearch Pods

**Screenshot placeholder:** [Add screenshot here](screenshots/03-opensearch-pods.png)

## 2.6 OpenSearch Index Creation

### Create Index

```bash
curl -X PUT "http://localhost:9200/items" \
  -H "Content-Type: application/json" \
  -d @index.json
```

### Port Forward OpenSearch

```bash
kubectl port-forward opensearch-0 9200:9200 -n team8
```

## 2.7 Synchronization Script

The script `sync_to_opensearch.py` was used to synchronize items from PostgreSQL into OpenSearch.

### Run Synchronization

```bash
python sync_to_opensearch.py
```

### Example Output

```text
Fetching page 1
Fetching page 2...
Total items fetched: 44446
Progress: 44446/44446 success: 44446 errors: 0
```

### Screenshot — Synchronization

**Screenshot placeholder:** [Add screenshot here](screenshots/04-sync-opensearch.png)

## 2.8 OpenSearch Query

### API Example

```bash
curl "http://localhost:8080/search?q=superman&size=3"
```

### Example OpenSearch Query

```json
{
  "query": {
    "multi_match": {
      "query": "superman",
      "fields": ["title^2", "description"],
      "fuzziness": "AUTO"
    }
  }
}
```

## 2.9 Typo Tolerance

### Example

```bash
curl "http://localhost:8080/search?q=supermax"
```

**Result:** OpenSearch still returned Superman-related products.

### Screenshot — Typo Tolerance

**Screenshot placeholder:** [Add screenshot here](screenshots/05-opensearch-typo.png)

## 2.10 PostgreSQL vs OpenSearch

| Feature | PostgreSQL | OpenSearch |
|---|---|---|
| Basic search | Yes | Yes |
| OR queries | Yes | Yes |
| Stemming | Yes | Yes |
| Typo tolerance | No | Yes(fuzzy) |
| Relevance scoring | Limited | Advanced |
| Title boosting | No | Yes |

***

# 3. Task 3 — Vector Search

## 3.1 Goal

Implement semantic vector search using embeddings.

## 3.2 Embedding Model

- Embedding model: `nomic-embed-text-v2-moe`
- Embedding dimension: `768`

## 3.3 Vector Index

### Create Vector Index

```bash
curl -X PUT "http://localhost:9200/items_vector" \
  -H "Content-Type: application/json" \
  --data-binary "@vector-index.json"
```

### Example Mapping

```json
{
  "embedding": {
    "type": "knn_vector",
    "dimension": 768
  }
}
```

## 3.4 Generate Query Embeddings

### API Call

```bash
curl -X POST "https://db.iue.haw-kiel.de/ollama/api/embeddings" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 42" \
  -d '{"model":"nomic-embed-text-v2-moe:latest","prompt":"running shoes"}'
```

## 3.5 Vector Search Endpoint

### API Example

```bash
curl "http://localhost:8080/vector-search?q=running shoes"
```

## 3.6 kNN Query

```json
{
  "query": {
    "knn": {
      "embedding": {
        "vector": [...],
        "k": 20
      }
    }
  }
}
```

## 3.7 Web App Integration

The frontend contains a checkbox:

`🤖 Vector Search (AI)`

### Behavior

| Checkbox | Search Type |
|---|---|
| Unchecked | Keyword Search |
| Checked | Vector Search |

### Screenshot — Vector Search

**Screenshot placeholder:** [Add screenshot here](screenshots/06-vector-search.png)

## 3.8 Semantic Similarity

| Query | Possible Match |
|---|---|
| soccer jersey | football shirt |
| running shoes | sports footwear |

## 3.9 Embedding Storage Estimation

Each embedding contains 768 floating-point values. Embedding millions of reviews would require several gigabytes of additional storage.

***

# 4. Task 4 — Analytical Queries

## 4.1 Goal

Compare analytical query performance between PostgreSQL and DuckDB.

## 4.2 Analytical Query

```sql
SELECT
    type,
    COUNT(*) AS sales,
    SUM(sale_price) AS revenue,
    COUNT(review_date) AS reviews,
    COUNT(return_date) AS returns
FROM items i
JOIN sales s ON i.id = s.item_id
GROUP BY type
ORDER BY revenue DESC
LIMIT 10;
```

## 4.3 PostgreSQL Query

### Open PostgreSQL

```bash
kubectl exec -it postgres-0 -n team8 -- psql -U vikram -d fashion_shop
```

### Run Query

```sql
EXPLAIN ANALYZE
SELECT
    type,
    COUNT(*) AS sales,
    SUM(sale_price) AS revenue,
    COUNT(review_date) AS reviews,
    COUNT(return_date) AS returns
FROM items i
JOIN sales s ON i.id = s.item_id
GROUP BY type
ORDER BY revenue DESC
LIMIT 10;
```

### PostgreSQL Result

Execution time: **2140.339 ms**

### Screenshot — PostgreSQL Explain Analyze

**Screenshot placeholder:** ![postgres-explain](lab2/screenshots/07-postgres-explain.png)

## 4.4 DuckDB Analytical Query

### Run Script

```bash
python duckdb_test.py
```

### DuckDB Result

DuckDB Execution Time: **118.02 ms**

### Screenshot — DuckDB Result

**Screenshot placeholder:** ![duckdb-results](lab2/screenshots/duckdb-results.png)

## 4.5 PostgreSQL vs DuckDB

| Database | Storage Model | Execution Time |
|---|---|---|
| PostgreSQL | Row-store | 2140.339 ms |
| DuckDB | Column-store | 118.02 ms |

## 4.6 Why DuckDB Was Faster

### PostgreSQL

- Stores complete rows together
- Optimized for transactions
- Scans unnecessary columns for analytical workloads

### DuckDB

- Stores columns separately
- Optimized for analytics
- Reads only required columns
- Better cache efficiency

***

## Kubernetes Commands

### OpenSearch Port Forward

```bash
kubectl port-forward opensearch-0 9200:9200 -n team8
```

### PostgreSQL Port Forward

```bash
kubectl port-forward postgres-0 5432:5432 -n team8
```

### API Port Forward

```bash
kubectl port-forward service/ddis-api-service 8080:80 -n team8
```

***

## Files Added

| File | Purpose |
|---|---|
| `webapp.html` | Frontend |
| `sync_to_opensearch.py` | Synchronization |
| `vector-index.json` | Vector index |
| `duckdb_test.py` | Analytical benchmark |
| `opensearch-statefulset.yaml` | OpenSearch deployment |

***

## Conclusion

In this lab, advanced filtering was implemented, PostgreSQL full-text search was added, OpenSearch integration was completed, semantic vector search was implemented, and DuckDB analytical benchmarking was performed.

The lab demonstrated the differences between transactional databases, search systems, and analytical databases. DuckDB achieved the best analytical performance, while OpenSearch provided the most advanced search capabilities.