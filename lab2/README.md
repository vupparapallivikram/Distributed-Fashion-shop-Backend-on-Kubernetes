# Lab 2 - Derived Data for Search and Analytical Queries

## Task 1 - Filter Item Catalog (COMPLETE):

- Extended `/items` API route with filters: `color`, `type`, `category`, `price_min`, `price_max`
- Multiple values supported: `/items?color=pink,green&type=socks`
- Built web app (`webapp.html`) showing items with images, prices, response time, result count
- Images loaded from https://db.iue.haw-kiel.de/ddis/fashion-shop/item_images/

## Task 2 - Keyword Search (COMPLETE):

### Approach A - PostgreSQL `tsvector`:

- Added `search` parameter: `/items?search=superman`
- Used `websearch_to_tsquery` for OR/AND support
- Created GIN index on title and description
- Results: OR works, stemming works, typos NOT supported

### Approach B - OpenSearch:

- Deployed OpenSearch 2.11.0 as StatefulSet on Kubernetes (namespace `team8`)
- Created `items` index with `title`, `description`, `reviews` fields
- Synced all 44,446 items from PostgreSQL using Python script
- New API route: `/search?q=superman`
- Uses `multi_match` with `fuzziness: AUTO` and `title` boosted 2x
- Results: typos work (e.g. `supermax` finds `superman`), relevance scores, title boosting

## Comparison table:

Feature | PostgreSQL | OpenSearch
---|---:|---:
Basic search | yes | yes
OR search | yes | yes
Stemming | yes | yes
Typos | no | yes (fuzzy)
Relevance score | no | yes
Title boosting | no | yes

## Web app updated:

- Unchecked checkbox = PostgreSQL search
- Checked checkbox = OpenSearch search
- Both show response time and result count

## API & testing commands

Port-forward (Kubernetes) used during testing:

```bash
# Forward OpenSearch (namespace team8)
kubectl port-forward opensearch-0 9200:9200 -n team8

# Forward Postgres (namespace team8)
kubectl port-forward postgres-0 5432:5432 -n team8

# Forward API service to local port 8080
kubectl port-forward service/ddis-api-service 8080:80 -n team8
```

Direct OpenSearch API test (example):

```bash
curl -X GET "http://localhost:9200/items/_search" \
  -H "Content-Type: application/json" \
  -d '{"query": {"multi_match": {"query": "soccer jersey", "fields": ["title", "description"]}}, "size": 3}' | python3 -m json.tool | grep "title"
```

OpenSearch via our API:

```bash
curl "http://localhost:8080/search?q=superman&size=3" | python3 -m json.tool
```

PostgreSQL `/items` examples:

```bash
# Basic search by keyword
curl "http://localhost:8080/items?page=1&page_size=20&search=superman" | python3 -m json.tool

# Filter by multiple colors and a type
curl "http://localhost:8080/items?color=pink,green&type=socks" | python3 -m json.tool
```

Notes:

- The API routes are hosted by the `ddis-api-service` in the `team8` namespace during testing; port-forwarding exposes them locally on `http://localhost:8080`.
- OpenSearch runs on `http://localhost:9200` when port-forwarded.