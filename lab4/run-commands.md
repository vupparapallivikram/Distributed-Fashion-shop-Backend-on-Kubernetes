# YCSB Run Commands — Copy-Paste Ready

## Connection string (same for all runs)
```
pg.host=cockroachdb-public pg.port=26257 pg.user=root pg.db=ycsb pg.sslmode=disable
```

---

## BEFORE RUNNING — Verify data loaded
```bash
PGCLIENTENCODING=utf-8 psql "postgresql://root@cockroachdb-public:26257/ycsb?sslmode=disable" -c "SELECT count(*) FROM usertable;"
# Must show 4000000 before running any R1-R7
```

---

## R1 — Workload A, uniform, 50 threads (run TWICE)
**What it tests:** 50% read + 50% update, equal key distribution, baseline performance

### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
### Run 2 (repeat immediately):
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R1_run1.png`, `task2_R1_run2.png`

---

## R2 — Workload B, uniform, 50 threads (run TWICE) ⭐ LIVE DEMO
**What it tests:** 95% read + 5% update — read-heavy workload. Higher OPS expected than R1.

### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloadb -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloadb -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R2_run1.png`, `task2_R2_run2.png`

---

## R3 — Workload A, uniform, 250 threads (run TWICE)
**What it tests:** Same as R1 but 5x more threads — tests high concurrency performance

### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=250 -p requestdistribution=uniform
```
### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=250 -p requestdistribution=uniform
```
📸 Screenshot both outputs → `task2_R3_run1.png`, `task2_R3_run2.png`

---

## R4 — Workload A, zipfian, 250 threads (run TWICE)
**What it tests:** Same as R3 but with zipfian distribution — hot keys stress leaseholders

### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=250 -p requestdistribution=zipfian -p recordcount=4000000
```
### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=250 -p requestdistribution=zipfian -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R4_run1.png`, `task2_R4_run2.png`

---

## R5 — Workload E, uniform, 50 threads (run TWICE)
**What it tests:** 95% range scans + 5% inserts — tests scan performance

### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloade -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloade -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R5_run1.png`, `task2_R5_run2.png`

---

## R6 — CPU=2, Workload A, uniform, 50 threads (run TWICE)
**What it tests:** Same as R1 but CPU halved — tests impact of CPU on throughput

### STEP 1 — Patch CPU to 2 (run in NEW terminal, NOT inside ycsb pod):
```powershell
'{"spec":{"template":{"spec":{"containers":[{"name":"cockroachdb","image":"cockroachdb/cockroach:v23.1.11","resources":{"requests":{"cpu":"2","memory":"8Gi"},"limits":{"cpu":"2","memory":"8Gi"}}}]}}}}' | Out-File -FilePath patch-r6.json -Encoding ascii
kubectl patch statefulset cockroachdb -n team8 --type=merge --patch-file patch-r6.json
kubectl delete pod cockroachdb-0 cockroachdb-1 cockroachdb-2 cockroachdb-3 -n team8
kubectl get pods -n team8 -w
# Wait until all 4 Running again
```

### STEP 2 — Verify CPU is 2:
```powershell
kubectl get statefulset cockroachdb -n team8 -o jsonpath='{.spec.template.spec.containers[0].resources}'
```

### STEP 3 — Run benchmark (inside ycsb pod):
#### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
#### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R6_run1.png`, `task2_R6_run2.png`

### STEP 4 — Patch CPU back to 4 after R6:
```powershell
kubectl patch statefulset cockroachdb -n team8 --type=merge --patch-file patch.json
kubectl delete pod cockroachdb-0 cockroachdb-1 cockroachdb-2 cockroachdb-3 -n team8
kubectl get pods -n team8 -w
```

---

## R7 — RF=1, Workload A, uniform, 50 threads (run TWICE)
**What it tests:** Same as R1 but no replication — removes Raft overhead, should be faster

### STEP 1 — Change RF to 1 (new terminal):
```powershell
kubectl exec -it cockroachdb-0 -n team8 -- /cockroach/cockroach sql --insecure --host=cockroachdb-0.cockroachdb --database=ycsb
```
Inside SQL shell:
```sql
ALTER DATABASE ycsb CONFIGURE ZONE USING num_replicas = 1;
SHOW ZONE CONFIGURATION FOR DATABASE ycsb;
\q
```
📸 Screenshot zone config → `task2_R7_rf1_config.png`

Wait 2-3 minutes for rebalancing, then:

### STEP 2 — Run benchmark (inside ycsb pod):
#### Run 1:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
#### Run 2:
```bash
./bin/go-ycsb run pg -P workloads/workloada -p pg.host=cockroachdb-public -p pg.port=26257 -p pg.user=root -p pg.db=ycsb -p pg.sslmode=disable -p operationcount=1000000 -p threadcount=50 -p requestdistribution=uniform -p recordcount=4000000
```
📸 Screenshot both outputs → `task2_R7_run1.png`, `task2_R7_run2.png`

### STEP 3 — Reset RF back to 3 after R7:
```powershell
kubectl exec -it cockroachdb-0 -n team8 -- /cockroach/cockroach sql --insecure --host=cockroachdb-0.cockroachdb --database=ycsb
```
```sql
ALTER DATABASE ycsb CONFIGURE ZONE USING num_replicas = 3;
\q
```

---

## How to Read the Output

```
Run finished, takes 45.2s
READ   - Takes(s): 45.2, Count: 950000, OPS: 21017.7, Avg(us): 1189
UPDATE - Takes(s): 45.2, Count: 50000,  OPS: 1106.7,  Avg(us): 5823
```

| Field | Formula | Results Table Column |
|---|---|---|
| Runtime | `Takes(s)` value | Runtime in s |
| Total OPS | READ OPS + UPDATE OPS | Operations/s |
| Total Avg (ms) | `Avg(us)` of TOTAL ÷ 1000 | Avg Total |
| Read Avg (ms) | `Avg(us)` of READ ÷ 1000 | Avg Read |
| Update Avg (ms) | `Avg(us)` of UPDATE ÷ 1000 | Avg Update |
| Scan Avg (ms) | `Avg(us)` of SCAN ÷ 1000 | Avg Scan |
| Insert Avg (ms) | `Avg(us)` of INSERT ÷ 1000 | Avg Insert |

---

## Monitor CPU During Each Run (separate terminal)
```powershell
kubectl top pods -n team8
```
📸 Take a screenshot during each run.

---

## Order of Execution
```
L1 (load) → R1 → R2 → R3 → R4 → R5 → R6 (patch CPU=2) → R7 (RF=1)
```
Each run phase takes ~5-15 minutes depending on OPS.
