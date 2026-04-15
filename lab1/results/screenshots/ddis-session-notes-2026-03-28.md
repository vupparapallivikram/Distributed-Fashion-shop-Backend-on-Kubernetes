# DDIS Project – Session Notes
**Date:** Saturday, 28 March 2026  
**Project:** `fashion_shop` – Kubernetes-deployed API + PostgreSQL (namespace: `team8`)

---

## Screenshot 01 & 02 — Database Setup & Record Counts

- Connected to PostgreSQL via  
  `kubectl exec -it postgres-0 -n team8 -- psql -U vikram -d fashion_shop`
- Loaded sales data from `/tmp/sales.csv` using `\COPY`
- Queried row counts across all three core tables:

| Table | Rows       |
|-------|-----------:|
| users | 540,357    |
| items | 44,446     |
| sales | 10,343,248 |

---

## Screenshot 03 — Kubernetes Pod Status

Running `kubectl get pods -n team8` confirmed all pods healthy:

| Pod Name                   | Ready | Status  | Restarts | Age  |
|---------------------------|:-----:|---------|---------:|------|
| ddis-api-74cf685dbd-9jlbz | 1/1   | Running | 0        | 10d  |
| ddis-api-74cf685dbd-bdlq5 | 1/1   | Running | 0        | 10d  |
| ddis-api-74cf685dbd-kwv4v | 1/1   | Running | 0        | 10d  |
| ddis-api-74cf685dbd-vmkrv | 1/1   | Running | 0        | 10d  |
| postgres-0                | 1/1   | Running | 0        | 5m10s |

---

## Screenshot 04 — API Login Test

- Exec'd into `postgres-0` pod for DB access  
- Tested the API login endpoint:

  ```bash
  curl -X POST http://localhost:8080/login \
       -H "Content-Type: application/json" \
       -d '{"email":"test@example.com","password":"secret"}'
  ```

---

## Screenshot 05 — Query Plan – Index Scan on Sales

- Connected to PostgreSQL via `kubectl exec -it postgres-0 -n team8 -- psql -U vikram -d fashion_shop`
- Loaded sales data from `/tmp/sales.csv` using `\COPY`
- Queried row counts across all three core tables:

| Table  | Rows       |
|--------|------------|
| users  | 548,357    |
| items  | 44,444     |
| sales  | 10,343,248 |

---
## Screenshot 06 — Index Size Analysis

Checked index sizes across `users`, `items`, and `sales` tables:

| Index Name         | Size   |
|--------------------|--------|
| sales_pkey         | 222 MB |
| idx_sales_uid      | 84 MB  |
| idx_sales_item_id  | 70 MB  |
| users_email_key    | 33 MB  |
| users_pkey         | 20 MB  |
| items_pkey         | 1318 kB|
| idx_items_id       | 992 kB |

---

## Screenshot 07 — Stock Reset Before Load Test

- Updated `in_stock = 10` for 5 test items (IDs: 38005, 9524, 27217, 52425, 48958)
- Confirmed with `SELECT` — all 5 items showed `in_stock = 10` 

---

## Screenshot 08 — Stock After Load Test

- Re-ran `SELECT` on the same 5 items after the load test
- All items showed `in_stock = 0` — confirming the load test successfully depleted stock
- Load test ran correctly against the ddis API

---

## Locust Results — Load Testing

Two Locust runs were executed against the API to evaluate performance under concurrent load.

### Screenshot — Locust, 100 Users

_File: `locust-result-100-users.jpg`_

- Concurrent users: **100**
- Requests per second (RPS): ~**~100**
- Failures: **0%**
- Median response time (50th percentile): ~**30–40 ms**
- 95th percentile response time: ~**40–50 ms**

### Screenshot — Locust, 200 Users

_File: `Locust-result-200-users.jpg`_

- Concurrent users: **200**
- Requests per second (RPS): peaked around **~ 180**
- Failures: **0%**
- Median response time: ~**30–40 ms**
- 95th percentile response time: ~**40–60 ms** after initial ramp‑up

These Locust results confirm that the `fashion_shop` API scales from 100 to 200 concurrent users with stable latency and no request failures, while correctly updating stock in the database.

This session covered the full lifecycle of the ddis fashion shop system:  
database loading → pod health checks → API testing → query performance tuning → index analysis → load testing with stock validation and Locust-based performance verification.