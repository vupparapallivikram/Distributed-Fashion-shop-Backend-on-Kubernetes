# Lab 4 — YCSB Benchmark Results

## System Info
| Field | Value |
|---|---|
| DBS | CockroachDB v23.1.11 |
| CPU info | AMD EPYC 7763 64-Core Processor |
| YCSB recordcount | 4,000,000 |
| YCSB operationcount | 1,000,000 |

---

## Column Guide

| Column | Fill when |
|---|---|
| OPS | Always |
| Runtime (s) | Always |
| Avg Total (ms) | Always |
| Avg Read (ms) | Workloads A, B (has READ operations) |
| Avg Update (ms) | Workloads A, B (has UPDATE operations) |
| Avg Scan (ms) | Workload E only (95% scans) |
| Avg Insert (ms) | L1 load phase + Workload E (5% inserts) |

Grey in table = N/A (that operation does not exist in that workload)

---

## CockroachDB Results

| Run | CPU | RF | Phase | Workload | Distribution | Threads | OPS (run1) | OPS (run2) | Runtime run1 (s) | Runtime run2 (s) | Avg Total (ms) | Avg Read (ms) | Avg Update (ms) | Avg Scan (ms) | Avg Insert (ms) |
|-----|-----|----|-------|----------|-------------|---------|------------|------------|-----------------|-----------------|----------------|---------------|-----------------|---------------|-----------------|
| L1 | 4 | 3 | load | - | - | 50→200 | | N/A | | N/A | N/A | N/A | N/A | | |
| R1 | 4 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R1 | 4 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R2 | 4 | 3 | run | B | uniform | 50 | | | | | | | | N/A | N/A |
| R2 | 4 | 3 | run | B | uniform | 50 | | | | | | | | N/A | N/A |
| R3 | 4 | 3 | run | A | uniform | 250 | | | | | | | | N/A | N/A |
| R3 | 4 | 3 | run | A | uniform | 250 | | | | | | | | N/A | N/A |
| R4 | 4 | 3 | run | A | zipfian | 250 | | | | | | | | N/A | N/A |
| R4 | 4 | 3 | run | A | zipfian | 250 | | | | | | | | N/A | N/A |
| R5 | 4 | 3 | run | E | uniform | 50 | | | | | | N/A | N/A | | |
| R5 | 4 | 3 | run | E | uniform | 50 | | | | | | N/A | N/A | | |
| R6 | 2 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R6 | 2 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R7 | 4 | 1 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R7 | 4 | 1 | run | A | uniform | 50 | | | | | | | | N/A | N/A |

---

## YugabyteDB Results (minimum: L1, R1, R2)

| Run | CPU | RF | Phase | Workload | Distribution | Threads | OPS (run1) | OPS (run2) | Runtime run1 (s) | Runtime run2 (s) | Avg Total (ms) | Avg Read (ms) | Avg Update (ms) | Avg Scan (ms) | Avg Insert (ms) |
|-----|-----|----|-------|----------|-------------|---------|------------|------------|-----------------|-----------------|----------------|---------------|-----------------|---------------|-----------------|
| L1 | 4 | 3 | load | - | - | 200 | | N/A | | N/A | N/A | N/A | N/A | | |
| R1 | 4 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R1 | 4 | 3 | run | A | uniform | 50 | | | | | | | | N/A | N/A |
| R2 | 4 | 3 | run | B | uniform | 50 | | | | | | | | N/A | N/A |
| R2 | 4 | 3 | run | B | uniform | 50 | | | | | | | | N/A | N/A |
