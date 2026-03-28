# DDIS Project – Session Notes
**Date:** Saturday, 28 March 2026
**Project:** `fashion_shop` – Kubernetes-deployed API + PostgreSQL (namespace: `team8`)

---

## Screenshot 01 & 02 — 12:57 PM · Database Setup & Record Counts

- Connected to PostgreSQL via `kubectl exec -it postgres-0 -n team8 -- psql -U vikram -d fashion_shop`
- Loaded sales data from `/tmp/sales.csv` using `\COPY`
- Queried row counts across all three core tables:

| Table  | Rows       |
|--------|------------|
| users  | 548,357    |
| items  | 44,444     |
| sales  | 10,343,248 |

---

## Screenshot 03 — 5:06 PM · Kubernetes Pod Status

Running `kubectl get pods -n team8` confirmed all pods healthy:

| Pod Name                    | Ready | Status  | Restarts | Age   |
|-----------------------------|-------|---------|----------|-------|
| ddis-api-795947f55-6hgbx    | 1/1   | Running | 0        | 5m27s |
| ddis-api-795947f55-l49cx    | 1/1   | Running | 0        | 5m34s |
| postgres-0                  | 1/1   | Running | 0        | 4d22h |

---

## Screenshot 04 — 5:14 PM · API Login Test

- Exec'd into `postgres-0` pod for DB access
- Tested the API login endpoint:
  ```
  curl -X POST http://localhost:8080/login
  ```
  with JSON credentials (Content-Type: application/json)

---

## Screenshot 05 — 5:49 PM · Query Plan – Index Scan on Sales

- Ran `EXPLAIN ANALYZE` on a sales query filtering by `uid`
- PostgreSQL used **Index Scan** via `idx_sales_uid` — good performance:
  - Planning Time: **0.082 ms**
  - Execution Time: **0.387 ms**
  - Rows returned: 24 (estimated 88)

---

## Screenshot 06 — 5:53 PM · Index Size Analysis

Checked index sizes across `users`, `items`, and `sales` tables:

| Index Name        | Size    |
|-------------------|---------|
| sales_pkey        | 222 MB  |
| idx_sales_uid     | 84 MB   |
| idx_sales_item_id | 70 MB   |
| users_email_key   | 33 MB   |
| users_pkey        | 20 MB   |
| items_pkey        | 1318 kB |
| idx_items_id      | 992 kB  |

---

## Screenshot 07 — 7:26 PM · Stock Reset Before Load Test

- Updated `in_stock = 10` for 5 test items (IDs: 38005, 9524, 27217, 52425, 48958)
- Confirmed with SELECT — all 5 items showed `in_stock = 10` ✅

---

## Screenshot 08 — 7:28 PM · Stock After Load Test

- Re-ran SELECT on same 5 items after load test
- All items showed `in_stock = 0` — confirming the load test successfully depleted stock
- Load test ran correctly against the ddis API 🎯

---

## Summary

Today's session covered the full lifecycle of the ddis fashion shop system:
database loading → pod health checks → API testing → query performance tuning → index analysis → load testing with stock validation.
