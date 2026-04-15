# DDIS Project — Lab 1

## Kubernetes Deployment, API Development & Load Testing

**Course:** Distributed Databases and Information Systems  
**Semester:** Summer Term 2026  
**Team:** Rakesh Reddy Kalamakuntla & Vikram Vupparapalli  
**Professor:** Prof. Dr.-Ing. Jens Ehlers  
**Namespace:** team8

---

# Objective

The goal of this lab is to:

* Deploy a PostgreSQL database on Kubernetes  
* Develop a stateless API on top of the database  
* Perform load testing and analyze performance  
* Ensure data consistency under concurrent access  

---

# System Architecture

`Client → API (FastAPI, Stateless) → PostgreSQL (Stateful)`

* API deployed as **stateless service (Deployment)**  
* Database deployed as **stateful service (StatefulSet)**  
* Communication via Kubernetes Service  

---

# 1. Database Deployment (Kubernetes)

* PostgreSQL 16 deployed as **StatefulSet**
* Resources:
  * CPU: 4 cores
  * Memory: 8GB
  * shared_buffers = 4GB
* Persistent storage:
  * 20Gi volume (Ceph HDD)
* Data survives pod restart


### 📸 PostgreSQL Pod Running
[Postgres Pod](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/03%20-%20screenshot.png?ref_type=heads)
---

# 2. Dataset

| Table | Rows       |
| ----- | ---------- |
| users | 540,357    |
| items | 44,446     |
| sales | 10,343,240 |

### 📸 Data Successfully Loaded
[Data Loaded](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/02%20-%20Screenshot%202026-03-28%20at%2012.57.51%E2%80%AFPM.png?ref_type=heads)

### Data Sources:

* users.csv  
* items JSON files  
* sales.csv  

---

# 3. API Development

### Technology:

* FastAPI (Python)  
* PostgreSQL (psycopg2)  
* JWT Authentication  

### 📸 API Pods Running
[API Pods](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/03%20-%20Screenshot%202026-03-28%20at%205.06.47%E2%80%AFPM.png?ref_type=heads)

---

## Authentication

* Stateless JWT-based authentication  
* Token required for protected routes  
* No session storage → scalable  

### 📸 Login Route (JWT Token)
[Login](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/04%20-%20Screenshot%202026-03-28%20at%205.14.50%E2%80%AFPM.png?ref_type=heads)

---

## 🔗 API Endpoints

| Route            | Method | Description               | Auth |
| ---------------- | ------ | ------------------------- | ---- |
| /items           | GET    | Paginated item list       | NO   |
| /item/{id}       | GET    | Item details              | NO   |
| /login           | POST   | User login (JWT)          | NO   |
| /user/{id}       | GET    | User details              | YES  |
| /user/{id}/sales | GET    | User sales                | YES  |
| /sales           | POST   | Create sale (transaction) | YES  |
| /sales/{id}      | PATCH  | Update sale               | YES  |

---

# 4. Transactions & Consistency

To prevent overselling and ensure consistency, we used:

```sql
SELECT ... FOR UPDATE
```

* Locks item row during transaction  
* Ensures no concurrent updates  
* We validated consistency using concurrent load testing.
* Guarantees consistency  

### 📸 Stock Before Load Test
[Before](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/07%20-%20Screenshot%202026-03-28%20at%207.26.49%E2%80%AFPM.png?ref_type=heads)

### 📸 Stock After Load Test
[After](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/08%20-%20Screenshot%202026-03-28%20at%207.28.37%E2%80%AFPM.png?ref_type=heads)

**Result:**

* 100 users buying simultaneously  
* No overselling observed  

---

# 5. API Deployment

* Kubernetes Deployment (stateless)  
* Replicas: 2 (can be scaled up)  
* Connection pooling enabled  

---

# 6. Load Testing

### Tool:

* Locust  

---

## 🔹 Required Scenario

| Parameter  | Value |
| ---------- | ----- |
| Users      | 100   |
| Spawn rate | 10/s  |
| Duration   | 120s  |

### 📸 Locust Result – 100 Users
[Locust 100 Users](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/locust%20result%20-%20100%20users.jpeg?ref_type=heads)

**Result:** ~100 req/s, 0% failures

---

## 🔹 Extended Scenario (Scalability Test)

| Parameter  | Value |
| ---------- | ----- |
| Users      | 200   |
| Spawn rate | 20/s  |
| Duration   | 120s  |

### 📸 Locust Result – 200 Users
[Locust 200 Users](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/Locust%20result%20-%20200%20users.jpeg?ref_type=heads)

**Result:** ~175 req/s, 0% failures

---

## Interpretation

* System performs better under higher load  
* Better CPU and DB utilization  
* Demonstrates scalability  

---

# 7. Performance Optimization

## 🔹 Problem (Initial)

* Full table scans  
* JSON parsing overhead  
* No connection reuse  

→ ~10 req/s  

---

## Optimizations Applied to improve performance

### 1. Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sales_uid ON sales(uid);
CREATE INDEX idx_sales_item ON sales(item_id);
```

[Indexes created and their size analysis](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/06%20-%20Screenshot%202026-03-28%20at%205.53.03%E2%80%AFPM.png?ref_type=heads)

### 2. Remove JSON parsing

* Extracted fields into columns:
  * display_name
  * price
  * type
  * color

### 3. Connection Pooling

* Reuse DB connections  
* Reduced overhead  

### System performance improves significantly through indexing, removing JSON parsing and connection pooling.
### Also scaling (tested by increasing replicas to 4)  

## Performance Improvement

| Stage           | Throughput    |
| --------------- | ------------- |
| No optimization | ~10 req/s     |
| With indexes    | ~100 req/s    |
| Fully optimized | **175 req/s** |

---

# 8. Query Performance

| Query       | Before | After    |
| ----------- | ------ | -------- |
| Sales query | 327 ms | 0.167 ms |
| Login query | ~4 ms  | ~4 ms    |

---

# Key Concepts

## Stateless vs Stateful

* API = stateless → scalable  
* DB = stateful → persistent  

---

## Indexing

* Avoids full table scans  
* Improves query performance 

[Indexing result ](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/05%20-%20Screenshot%202026-03-28%20at%205.49.15%E2%80%AFPM.png?ref_type=heads)

---

## Transactions

* Ensure atomicity and consistency  
* Prevent race conditions  

* This ensures that concurrent transactions do not oversell items by locking rows until the transaction completes.

---

## Kubernetes

* Enables scaling and reliability  
* Separates application and database  

---

# 9. Evidence

Included screenshots show:

* Kubernetes pods running  
* Database setup  
* Data successfully loaded  
* API responses  
* Load test results  
* Consistency validation  

[All Screenshots](https://gitlab.iue.haw-kiel.de/rakesh.r.kalamakuntla/ddis-project/-/blob/vikram.vupparapalli-main-patch-d928/lab1/results/screenshots/ddis-session-notes-2026-03-28.md?ref_type=heads)

---

# Conclusion

* Successfully deployed distributed system on Kubernetes  
* Built scalable, stateless API  
* Achieved **≈175 req/s throughput**  
* Ensured consistency under concurrent load  
* Demonstrated system scalability  

---

# Key Takeaways

* Kubernetes enables scalable architecture  
* Indexing and query optimization are critical  
* Transactions ensure data consistency  
* Improving System performance