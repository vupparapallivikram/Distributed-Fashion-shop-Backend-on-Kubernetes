cat > ~/ddis-project/README.md << 'EOF'
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
- Namespace: team8
- Resources: 8GB RAM, 4 CPU, shared_buffers=4GB
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
- Workers per pod: 4 (uvicorn)
- Connection pooling: 50 connections
- Image: rakeshreddykalamakuntla/ddis-api:v5 (linux/amd64)

### API Routes
| Route | Method | Auth |
|---|---|---|
| /items | GET | No |
| /item/id | GET | No |
| /login | POST | No |
| /user/id | GET | Yes |
| /user/id/sales | GET | Yes |
| /sales/ | POST | Yes |
| /sales/id | PATCH | Yes |

### Performance Optimization Journey
| Stage | req/s | Change |
|---|---|---|
| No indexes | ~10 req/s | Full table scans |
| After indexes | ~89 req/s | Direct index lookup |
| After pooling + optimized queries | 169 req/s | Reuse connections, pre-computed columns |

### Final Load Test Results
| Metric | Value |
|---|---|
| Users | 200 |
| Spawn rate | 20/s |
| Duration | 120s |
| Total requests | 20,154 |
| Failures | 8 |
| Average response time | 34ms |
| **Throughput** | **169 req/s** |

### Database Indexes
| Index | Size | Purpose |
|---|---|---|
| sales_pkey | 222 MB | Primary key |
| idx_sales_uid | 84 MB | Sales by user |
| idx_sales_item_id | 70 MB | Sales by item |
| users_email_key | 33 MB | Login query |
| users_pkey | 20 MB | Primary key |
| idx_items_id | 992 kB | Item lookup |

### Query Performance
| Query | Before Index | After Index |
|---|---|---|
| Sales by user | 327ms | 0.167ms |
| Login by email | 4ms (already indexed) | 4ms |

### Consistency Check
- 5 items preset with in_stock=10
- 100 users buying simultaneously for 5 seconds
- Result: No overselling — all items ended at exactly 0
- Mechanism: PostgreSQL FOR UPDATE row locking in transaction

### Project Structure

## Evidence & Screenshots

### 01 — Kubernetes nodes connected
![Kubernetes nodes](lab1/results/screenshots/01%20-%20Screenshot%202026-03-28%20at%2012.57.38%20PM.png)

### 02 — PostgreSQL pod running
![PostgreSQL running](lab1/results/screenshots/02%20-%20Screenshot%202026-03-28%20at%2012.57.51%20PM.png)

### 03 — Data loaded (540k users, 44k items, 10M sales)
![Data loaded](lab1/results/screenshots/03%20-%20Screenshot%202026-03-28%20at%205.06.47%20PM.png)

### 04 — API pods running (2 replicas)
![API running](lab1/results/screenshots/04%20-%20Screenshot%202026-03-28%20at%205.14.50%20PM.png)

### 05 — Login route working (JWT token)
![Login JWT](lab1/results/screenshots/05%20-%20Screenshot%202026-03-28%20at%205.49.15%20PM.png)

### 06 — Index performance (327ms → 0.167ms)
![Index performance](lab1/results/screenshots/06%20-%20Screenshot%202026-03-28%20at%205.53.03%20PM.png)

### 07 — Load test results (169 req/s)
![Load test](lab1/results/screenshots/07%20-%20Screenshot%202026-03-28%20at%207.26.49%20PM.png)

### 08 — Consistency check (no overselling)
![Consistency](lab1/results/screenshots/08%20-%20Screenshot%202026-03-28%20at%207.28.37%20PM.png)