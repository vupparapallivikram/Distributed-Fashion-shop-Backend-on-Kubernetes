# DDIS Project — Team 8

**Course:** Distributed Databases and Information Systems  
**Semester:** Summer Term 2026  
**Team:** Rakesh Reddy Kalamakuntla & Vikram  
**Professor:** Prof. Dr.-Ing. Jens Ehlers

## Lab 1 — Kubernetes Deployment, API & Load Testing

### Results
| Metric | Result |
|---|---|
| Users loaded | 540,357 |
| Items loaded | 44,446 |
| Sales loaded | 10,343,240 |
| API replicas | 2 |
| Load test | ~89 req/s |
| Sales query before index | 327ms |
| Sales query after index | 0.167ms |
| Consistency check | No overselling |

### Structure
- `lab1/api/` — FastAPI application (7 routes, JWT auth)
- `lab1/k8s/` — Kubernetes YAML files
- `lab1/loadtest/` — Locust load test + CSV results
- `lab1/results/` — Screenshots and evidence
