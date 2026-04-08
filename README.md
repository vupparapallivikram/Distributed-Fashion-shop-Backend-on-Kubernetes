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