<<<<<<< HEAD
# DDIS Project — Lab 1

## Kubernetes Deployment, API Development & Load Testing

**Course:** Distributed Databases and Information Systems
**Semester:** Summer Term 2026
**Team:** Rakesh Reddy Kalamakuntla & Vikram Vupparapalli
**Professor:** Prof. Dr.-Ing. Jens Ehlers
**Namespace:** team8

---

#  Objective

The goal of this lab is to:

* Deploy a PostgreSQL database on Kubernetes
* Develop a stateless API on top of the database
* Perform load testing and analyze performance
* Ensure data consistency under concurrent access

---

#  System Architecture

```
Client → API (FastAPI, Stateless) → PostgreSQL (Stateful)
```

* API deployed as **stateless service (Deployment)**
* Database deployed as **stateful service (StatefulSet)**

---

#  1. Database Deployment (Kubernetes)

* PostgreSQL 16 deployed as **StatefulSet**
* CPU: 4 cores | Memory: 8GB | shared_buffers = 4GB
* Persistent storage: 20Gi
* Data survives restart

###  Kubernetes Nodes Connected

![K8s Nodes](01%20-%20Screenshot%202026-03-28%20at%2012.57.38%20PM.png)

###  PostgreSQL Pod Running

![Postgres Pod](02%20-%20Screenshot%202026-03-28%20at%2012.57.51%20PM.png)

---

#  2. Dataset

| Table | Rows       |
| ----- | ---------- |
| users | 540,357    |
| items | 44,446     |
| sales | 10,343,240 |

###  Data Successfully Loaded

![Data Loaded](03%20-%20screenshot.png)

---

#  3. API Development

### Technology:

* FastAPI
* PostgreSQL (psycopg2)
* JWT Authentication

###  API Pods Running

![API Pods](04%20-%20Screenshot%202026-03-28%20at%205.14.50%20PM.png)

---

##  Authentication

* Stateless JWT-based authentication
* No session storage

###  Login (JWT Token)

![Login](05%20-%20Screenshot%202026-03-28%20at%205.49.15%20PM.png)

---

#  4. Transactions & Consistency

```sql
SELECT ... FOR UPDATE
```

* Prevents race conditions
* Ensures no overselling

###  Stock Before Load Test

![Before](07%20-%20Screenshot%202026-03-28%20at%207.26.49%20PM.png)

###  Stock After Load Test

![After](08%20-%20Screenshot%202026-03-28%20at%207.28.37%20PM.png)

---

#  5. API Deployment

* Stateless deployment
* Replicas: 2
* Connection pooling enabled

---

#  6. Load Testing (Locust)

---

##  Scenario 1 — 100 Users

* Users: 100
* Spawn rate: 10/s
* Duration: 120s

###  Locust Result (100 Users)

![Locust 100](locust%20result%20-%20100%20users.jpeg)

* RPS: ~100
* Failures: 0%
* Median latency: 30–40 ms

---

##  Scenario 2 — 200 Users

* Users: 200
* Spawn rate: 20/s

###  Locust Result (200 Users)

![Locust 200](Locust%20result%20-%20200%20users.jpeg)

* RPS: ~175
* Failures: 0%
* Latency stable

---

##  Interpretation

* System scales with higher load
* Better resource utilization
* No failures under stress

---

# 7. Performance Optimization

---

##  Indexing

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sales_uid ON sales(uid);
CREATE INDEX idx_sales_item ON sales(item_id);
```

###  Query Plan (Index Scan)

![Query Plan](06%20-%20Screenshot%202026-03-28%20at%205.53.03%20PM.png)

---

##  Improvements

| Stage     | Throughput    |
| --------- | ------------- |
| Initial   | ~10 req/s     |
| Indexed   | ~100 req/s    |
| Optimized | **175 req/s** |

---

#  8. Query Performance

| Query       | Before | After    |
| ----------- | ------ | -------- |
| Sales query | 327 ms | 0.167 ms |

---

#  Key Concepts

* Stateless vs Stateful
* Indexing
* Transactions
* Kubernetes scaling

---

#  9. Evidence

All screenshots demonstrate:

* DB setup
* API working
* Query optimization
* Load testing
* Consistency validation

---

#  Conclusion

* Built scalable system on Kubernetes
* Achieved **~175 req/s**
* Ensured consistency
* Demonstrated performance optimization

---

# Key Takeaways

* Kubernetes enables scalability
* Indexing is critical for performance
* Transactions ensure correctness
* System scales with load

---
=======