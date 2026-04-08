# DDIS Project — Team 8

**Course:** Distributed Databases and Information Systems  
**Semester:** Summer Term 2026  
**Team:** Rakesh Reddy Kalamakuntla & Vikram  
**Namespace:** team8  
**Professor:** Prof. Dr.-Ing. Jens Ehlers

---

## Lab 1 — Kubernetes Deployment, API & Load Testing

### Database Setup
- PostgreSQL 16 deployed as **StatefulSet** on HAW Kiel Kubernetes cluster
- Namespace: `team8`
- Resources: 8GB RAM, 4 CPU, `shared_buffers=4GB`
- Storage: 20Gi persistent volume (ceph-hdd)

### Dataset Loaded

| Table | Rows |
|---|---|
| users | 540,357 |
| items | 44,446 |
| sales | 10,343,240 |

### API
- Framework: FastAPI (Python)
- Authentication: JWT tokens (stateless)
- Replicas: 4

### API Routes

| Route | Method | Auth |
|---|---|---|
| `/token` | POST | No |
| `/items` | GET | Yes |
| `/items/{id}` | GET | Yes |
| `/users` | GET | Yes |
| `/users/{id}` | GET | Yes |
| `/sales` | GET | Yes |
| `/purchase` | POST | Yes |

### Performance Optimization Journey

| Stage | req/s | Change |
|---|---|---|
| No indexes | ~10 req/s | Full table scans |
| After indexes | ~89 req/s | Direct index lookup |
| After pooling + optimized queries | **169–175 req/s** | Reuse connections, pre-computed columns |

### Load Test Results

| Test | Users | RPS | Failures | Avg Response |
|---|---|---|---|---|
| Baseline | 100 | **89.7** | 0% | ~38ms (50th) |
| Peak | 200 | **175.2** | 0% | ~34ms |
| Extended (120s) | 200 | **169** | <0.1% | 34ms |

See screenshots 10–11 for Locust charts.

### Database Indexes

| Index | Size | Purpose |
|---|---|---|
| sales_pkey | 222 MB | Primary key |
| idx_sales_uid | 84 MB | Sales by user |
| idx_sales_item_id | 70 MB | Sales by item |
| users_email_key | 22 MB | Login query |

### Consistency Check
- No overselling detected ✅
- Purchase endpoint uses transactions with row-level locking

---

## Evidence & Screenshots

### 01 — Namespace & pods
![Namespace](lab1/results/screenshots/01%20-%20%20Screenshot%202026-03-28%20at%205.06.47%20PM.png)

### 02 — StatefulSet running
![StatefulSet](lab1/results/screenshots/02%20-%20%20Screenshot%202026-03-28%20at%205.06.47%20PM.png)

### 03 — Data loaded (540k users, 44k items, 10M sales)
![Data loaded](lab1/results/screenshots/03%20-%20%20Screenshot%202026-03-28%20at%205.06.47%20PM.png)

### 04 — API pods running (4 replicas)
![API running](lab1/results/screenshots/04%20-%20%20Screenshot%202026-03-28%20at%205.14.50%20PM.png)

### 05 — Login route working (JWT token)
![Login JWT](lab1/results/screenshots/05%20-%20%20Screenshot%202026-03-28%20at%205.49.15%20PM.png)

### 06 — Index performance (327ms → 0.167ms)
![Index performance](lab1/results/screenshots/06%20-%20%20Screenshot%202026-03-28%20at%205.53.03%20PM.png)

### 07 — Load test results (169 req/s)
![Load test](lab1/results/screenshots/07%20-%20%20Screenshot%202026-03-28%20at%205.53.03%20PM.png)

### 08 — Consistency check (no overselling)
![Consistency](lab1/results/screenshots/08%20-%20%20Screenshot%202026-03-28%20at%207.28.37%20PM.png)

### 09 — All pods running (5/5 Ready)
kubectl get pods shows 5 rows: 4 API replicas + postgres-0, all Running, 0 restarts.
![kubectl pods](lab1/results/screenshots/09-kubectl-pods-running.png)

### 10 — Locust result — 100 users (89.7 req/s)
100 concurrent users, 0% failures. RPS stable ~89–90. 50th percentile ~34ms.
![Locust 100 users](lab1/results/screenshots/10-locust-100-users.png)

### 11 — Locust result — 200 users (175.2 req/s)
200 concurrent users, 0% failures. RPS peaked at 175.2. Near-linear scaling confirmed.
![Locust 200 users](lab1/results/screenshots/11-locust-200-users.png)
