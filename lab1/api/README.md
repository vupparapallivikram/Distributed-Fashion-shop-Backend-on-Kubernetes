# DDIS Project — Team 8

**Course:** Distributed Databases and Information Systems  
**Semester:** Summer Term 2026  
**Team:** Rakesh Reddy Kalamakuntla & Vikram  
**Professor:** Prof. Dr.-Ing. Jens Ehlers

---

## Lab 1 — Kubernetes Deployment, API & Load Testing

### What we built
- PostgreSQL deployed on HAW Kiel Kubernetes cluster (namespace: team8)
- Fashion shop dataset loaded: 540,357 users, 44,446 items, 10,343,240 sales
- REST API with 7 routes and JWT authentication
- Load tested with Locust: ~89 req/s, 100 concurrent users

### Key results
| Metric | Result |
|---|---|
| Users loaded | 540,357 |
| Items loaded | 44,446 |
| Sales loaded | 10,343,240 |
| API replicas | 2 |
| Load test req/s | ~89 req/s |
| Login query (before index) | 4ms (already indexed) |
| Sales query (before index) | 327ms |
| Sales query (after index) | 0.167ms |
| Consistency check | ✅ No overselling |

### Structure
```
lab1/
  api/          → FastAPI application (7 routes)
  k8s/          → Kubernetes YAML files
  loadtest/     → Locust load test + results
  results/      → Screenshots and evidence
```

### How to run
```bash
# Connect to cluster
kubectl config use-context ddis-context

# Check everything running
kubectl get all -n team8

# Test API
kubectl port-forward service/ddis-api-service 8080:80 -n team8
curl http://localhost:8080/items
```