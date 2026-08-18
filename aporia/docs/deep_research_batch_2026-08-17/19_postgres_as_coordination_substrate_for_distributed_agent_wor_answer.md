# Distributed Coordination via Relational State: Patterns, Pitfalls, and Scaling Limits of PostgreSQL-Backed Job Queues

**Key Points**
*   **Feasibility and Scale:** Implementing a multi-machine job queue utilizing PostgreSQL is highly viable and routinely deployed in production systems, particularly for workloads below 10,000 transactions per second.
*   **Concurrency Mechanism:** The `FOR UPDATE SKIP LOCKED` clause is the foundational mechanism that allows distributed workers to fetch jobs concurrently without locking contention.
*   **Table Bloat:** The most significant physical limitation is table bloat, stemming from PostgreSQL's Multi-Version Concurrency Control (MVCC). Frequent updates generate dead tuples, demanding meticulous `FILLFACTOR` tuning and autovacuum management.
*   **Lease Expiry Risks:** Relying purely on time-based lease expiry introduces split-brain race conditions where a stalled worker and a new worker may process the same job. Fencing tokens or optimistic concurrency controls are heavily recommended.
*   **Poison Item Handling:** Robust queue architectures must implement Dead Letter Queues (DLQs) to prevent malformed or infinitely failing jobs from blocking subsequent task processing.

**Layman's Overview**
When building software that coordinates multiple computers (workers) to execute tasks, developers historically rely on dedicated message brokers like RabbitMQ or Kafka. However, adding these systems introduces new failure points—such as a "conductor" process crashing and bringing the entire system down. An alternative approach uses a standard PostgreSQL database as the central coordinator. In this model, tasks are stored as rows in a table. Workers "claim" a task by putting their name and an expiration time on it (a lease). If a worker crashes, its lease eventually expires, allowing another worker to pick up the task. 

While this decentralized, database-backed model removes the risk of a single broker crashing, it introduces its own set of challenges. If a worker simply "falls asleep" (due to a network lag or a frozen system) and wakes up after its lease has expired, it might try to finish a task that another worker has already taken over, resulting in duplicate work. Furthermore, because of how PostgreSQL handles data changes under the hood, rapidly claiming and deleting tasks can leave behind "ghost" data that fills up hard drives and slows down the database. This report explores how to build this database-queue safely, how to prevent duplicate tasks, how to handle bad data that crashes workers, and exactly how far this system can scale before a dedicated message broker becomes absolutely necessary.

---

## Introduction

In distributed systems engineering, the orchestration of background jobs across multi-machine agent fleets is a foundational challenge. The conventional architectural consensus often leans toward deploying specialized message brokers (e.g., Apache Kafka, RabbitMQ, or Amazon SQS) to decouple producers from consumers [cite: 1, 2]. However, introducing an external message broker violates the simplicity of a single-system architecture and introduces independent failure domains. The phenomenon known as the **PATTERN_CONDUCTOR_CONFOUND** describes the erroneous assumption that adding a highly available, centralized coordination daemon inherently increases system reliability. In reality, external brokers require independent state replication, distinct backup strategies, and specialized network routing. As observed in field reports where entire fleets of daemon processes have silently failed, decentralized worker architectures relying on shared relational state can yield higher structural resilience for specific operational scales.

By utilizing PostgreSQL as a decentralized coordination mechanism, the architecture aligns state transitions of application data with the state transitions of the distributed queue within the same ACID-compliant transaction boundary [cite: 3, 4]. The system relies on lease-based claiming: autonomous worker nodes query the database for pending tasks, atomically claim them with an expiration timestamp, and execute the workload.

The problem statement addressed in this report investigates the established patterns and intrinsic pitfalls of utilizing PostgreSQL as a job queue with lease semantics. Operating within the constraints of PostgreSQL 17 on a single primary instance with tens of thousands of active queue rows, this analysis explores the `SKIP LOCKED` concurrency model, lease-expiry race conditions, poison-item management, table bloat driven by high-churn updates, and the empirical scaling limits of this architecture.

## Established Patterns: The PostgreSQL Queue Paradigm

The implementation of a relational database as a message queue has evolved from an anti-pattern into an established, well-documented architectural strategy, driven primarily by feature additions to the PostgreSQL engine [cite: 5]. 

### The Concurrency Primitive: `FOR UPDATE SKIP LOCKED`

Prior to PostgreSQL 9.5 (released in 2016), utilizing a database table as a queue resulted in severe lock contention [cite: 4, 5]. If multiple concurrent worker agents attempted to claim the oldest pending job using a standard `SELECT ... FOR UPDATE` query, the database would lock the row for the first worker. All subsequent workers would halt execution, waiting for the first worker to release the row-level lock. This serialized the queue consumption, converting a theoretically parallel system into a single-file convoy, drastically throttling throughput [cite: 4, 6].

The introduction of the `SKIP LOCKED` clause resolved this contention [cite: 5, 7]. When a query includes `FOR UPDATE SKIP LOCKED`, PostgreSQL scans the table according to the specified criteria. If it encounters a row that is already locked by an active transaction, it does not wait for the lock to be released; instead, it silently skips the locked row and proceeds to the next available row that satisfies the `WHERE` clause [cite: 2, 8]. 

This allows multiple independent workers to poll the queue table concurrently. Each worker acquires a lock on a distinct, available row without interacting with the locks held by its peers [cite: 9, 10]. The fundamental query structure for this pattern is typically executed atomically via a Common Table Expression (CTE):

```sql
WITH next_job AS (
  SELECT id 
  FROM job_queue 
  WHERE status = 'pending' 
  ORDER BY created_at ASC 
  FOR UPDATE SKIP LOCKED 
  LIMIT 1
)
UPDATE job_queue 
SET status = 'running',
    locked_at = NOW(),
    expires_at = NOW() + interval '10 minutes',
    worker_id = $1
FROM next_job 
WHERE job_queue.id = next_job.id 
RETURNING job_queue.*;
```

This pattern ensures that a job is fetched, locked, and marked as active in a single, atomic operation, eliminating the window for read-modify-write race conditions [cite: 2, 8].

### Transactional Enqueueing

One of the most profound advantages of the PostgreSQL queue pattern over an external message broker is the ability to utilize transactional boundaries [cite: 3, 4]. In a microservices architecture communicating with an external broker, the "dual-write problem" emerges: if the system writes business data to the database and then publishes an event to the broker, a crash between these two operations leaves the system in an inconsistent state. 

By unifying the queue and the operational database, producers can insert business data and enqueue the corresponding job within the same `BEGIN ... COMMIT` block [cite: 11, 12]. If the transaction fails, the queue entry is automatically rolled back, providing exact structural consistency without necessitating complex outbox patterns or two-phase commits.

### Proactive Polling vs. `LISTEN/NOTIFY`

While `SKIP LOCKED` facilitates safe claiming, continuous polling by dozens of workers on an empty queue consumes database CPU and connection overhead [cite: 2, 11]. To optimize latency and resource utilization, the pattern is frequently augmented with PostgreSQL's asynchronous `LISTEN/NOTIFY` functionality.

Workers issue a `LISTEN queue_channel` command and enter an idle state. When a producer enqueues a job, it executes a `NOTIFY queue_channel` command (often via a database trigger). This wakes the sleeping workers, prompting them to execute the `SKIP LOCKED` claiming query [cite: 11]. This hybrid approach delivers near-instantaneous job pickup without hammering the database with empty polling queries during idle periods [cite: 2]. 

## Attack Vectors and Pitfalls

Despite its elegance, the PostgreSQL lease-based queue harbors several architectural vulnerabilities that manifest under distributed failure conditions. Systems designed without rigorous handling for these attack vectors are prone to silent data corruption, cascading failures, and extreme latency degradation.

### Attack Vector 1: Lease-Expiry Races and Duplicate Execution

In a multi-machine fleet, worker processes do not fail cleanly. A worker might crash, experience a severe garbage collection pause, suffer network partition, or be temporarily suspended by the host hypervisor. To prevent these stalled workers from holding a job indefinitely, the architecture relies on lease semantics: when a worker claims a job, it sets an `expires_at` timestamp [cite: 13, 14]. 

A separate "reaper" process, or the primary claiming query itself, is configured to reclaim jobs where `status = 'running' AND expires_at < NOW()`. These jobs are reverted to `pending` status or claimed directly by a new worker [cite: 2, 11]. 

**The Split-Brain Vulnerability:**
Relying strictly on lease expiration creates a deterministic race condition. Consider the following sequence involving Worker A and Worker B:
1. Worker A claims Job X, establishing a lease that expires at \( T_0 + 10 \text{ min} \).
2. Worker A begins processing but experiences a systemic stall (e.g., an Out-Of-Memory thrash or a network block) at minute 9.
3. At minute 11, the lease expires. The database reassigns Job X to Worker B. Worker B begins execution.
4. At minute 12, Worker A recovers from its stall. Unaware that its lease has expired and ownership has transferred, Worker A finishes its execution and commits its side-effects to downstream systems (e.g., sending an email, charging a credit card).
5. Shortly after, Worker B also finishes and commits the exact same side-effects [cite: 13].

Lease expiry transfers *ownership* within the database, but it does not intrinsically revoke *execution control* from the stalled physical process [cite: 13]. 

**Mitigation Strategies:**
To neutralize this attack vector, the system must enforce strict concurrency controls at the commit boundary. 
1. **Fencing Tokens:** Every time a job is claimed or a lease is renewed, the database issues a monotonically increasing sequence integer (a fencing token) to the worker [cite: 15]. The database enforces a schema constraint, such as `UNIQUE(job_id, token)`. When Worker A wakes up and attempts to commit its success, it must provide its original token. If Worker B has already taken over and incremented the token, Worker A's commit will be rejected at the database level [cite: 15].
2. **Optimistic Locking via State Checks:** A worker must verify it still holds the lease at the exact moment of completion. The update query must be conditional: `UPDATE job_queue SET status = 'completed' WHERE id = $1 AND worker_id = $2 AND status = 'running'` [cite: 4]. If this query affects zero rows, the worker has been preempted and must gracefully abort any further side-effects.
3. **Idempotency Keys:** Regardless of database-level locking, external side-effects (like calling a third-party API) must utilize idempotency keys derived deterministically from the `job_id` and the attempt number. This ensures that even if two workers execute concurrently, the downstream service collapses the duplicate requests into a single operation [cite: 13, 16].

### Attack Vector 2: Poison-Item Handling

A "poison pill" is a message or queue item that cannot be successfully processed due to deterministically flawed data (e.g., malformed JSON, missing relational constraints, or a bug in the worker's business logic) [cite: 17, 18]. 

If a queue lacks robust poison-item handling, the following failure loop occurs:
1. A worker claims the poison pill.
2. The worker attempts to process the job and encounters an unhandled exception, causing the worker process to crash or prematurely abort.
3. Because the job was never marked as completed, its lease eventually expires.
4. A second worker claims the job, crashes, and the cycle repeats infinitely [cite: 18].

This phenomenon, known as Head-of-Line blocking, consumes worker capacity and generates massive amounts of error logs, effectively acting as a localized Denial of Service (DoS) attack on the worker fleet [cite: 17, 19].

**Mitigation Strategies:**
1. **Attempt Tracking:** The queue schema must include an `attempts` counter (`retry_count INT DEFAULT 0`) [cite: 8]. Every time a job is dequeued (or processed by the reaper), this counter must be incremented.
2. **Dead Letter Queue (DLQ):** A strict threshold must be established (e.g., `max_retries = 5`). If a job fails to process after exceeding this threshold, it must be permanently routed out of the active queue. This is achieved by either moving the row to a dedicated `dead_letter_queue` table or updating its status to `failed`/`dead` [cite: 12, 20]. A DLQ turns an invisible, infinitely repeating failure into a visible, inspectable operational artifact that engineers can debug without impacting active production flows [cite: 17, 20].
3. **Exponential Backoff and Visibility Timeouts:** When a transient error occurs (e.g., a temporary network timeout), the worker should affirmatively report the failure back to the queue rather than waiting for lease expiration [cite: 12]. The database should then apply an exponential backoff to the `visible_at` timestamp, preventing the item from being immediately retried and hot-looping the database at round-trip speeds [cite: 12, 19].

### Attack Vector 3: The MVCC Trap and Table Bloat

The most profound physical limitation of a PostgreSQL-backed queue originates from its storage engine architecture. PostgreSQL utilizes Multi-Version Concurrency Control (MVCC) to provide transaction isolation [cite: 21, 22]. 

In PostgreSQL, an `UPDATE` operation does not mutate data in place. Instead, it writes a completely new version of the row to the disk (the heap) and marks the old version of the row with a deletion timestamp (`t_xmax`) [cite: 23, 24]. Similarly, a `DELETE` operation simply marks the row as dead. These invisible, outdated rows are known as "dead tuples." [cite: 21, 22].

A highly active job queue is essentially a churn machine. A single job might undergo multiple state transitions (`pending` \(\rightarrow\) `running` \(\rightarrow\) `completed`), generating three or more dead tuples for every single successful job [cite: 2, 4]. If a system processes 1,000 jobs per second, it is generating thousands of dead tuples per second. 

If these dead tuples are not physically removed from the disk, the table experiences **table bloat**. The database pages become filled with invisible data, forcing sequential scans and index traverses to read massive amounts of wasted disk space [cite: 21, 25]. Over time, performance degrades exponentially—a phenomenon often referred to as the queue "death spiral," where the system gets slower the emptier the active queue actually is [cite: 23].

**Mitigation Strategies:**
Cleaning up dead tuples is the responsibility of the background **autovacuum** daemon [cite: 22, 26]. However, heavily utilized queues often outpace the default autovacuum configurations.
1. **Aggressive Autovacuum Tuning:** For queue tables, the autovacuum thresholds must be radically tightened. The `autovacuum_vacuum_scale_factor` (default 20%) should be lowered to 1% or less, ensuring that vacuuming triggers frequently in proportion to the high churn [cite: 27].
2. **Heap-Only Tuples (HOT) Updates:** This is a crucial PostgreSQL optimization. If an `UPDATE` does not modify any columns that are indexed, PostgreSQL can place the new version of the row on the exact same disk page as the old version, and it bypasses updating the indexes entirely [cite: 28, 29]. This drastically reduces "write amplification" (where one row update requires rewriting dozens of index entries) and makes localized page cleanup incredibly fast [cite: 28].
3. **FILLFACTOR Tuning:** By default, PostgreSQL packs data pages to 100% capacity (`FILLFACTOR = 100`). When a page is full, any `UPDATE` forces the new row to be written to a different page, completely neutralizing the HOT update optimization [cite: 28, 29]. For queue tables, the `FILLFACTOR` must be explicitly lowered (e.g., to 80 or 90). This leaves 10% to 20% of the disk page completely empty, specifically reserving "elbow room" for future HOT updates [cite: 27, 29].
4. **Targeted Indexing:** To maximize HOT updates, one must avoid placing indexes on columns that change frequently [cite: 27, 30]. However, the core queue query inherently requires searching by the `status` column. To balance these conflicting requirements, developers must use **partial indexes**. Instead of indexing the entire `status` column, an index should be created solely for pending rows: `CREATE INDEX idx_jobs_pending ON jobs (created_at) WHERE status = 'pending';` [cite: 1, 2]. When a job is updated to `running`, it falls out of the partial index.
5. **Partitioning and Truncation:** For extreme workloads, some modern PostgreSQL queue implementations (such as pgque) abandon row-by-row `DELETE` entirely. Instead, they use snapshot-based batching and partition the queue tables by time. Once all jobs in a partition are processed, the entire partition is dropped or truncated. `TRUNCATE` reclaims disk space instantly at the OS level without generating dead tuples or requiring vacuuming, effectively reducing table bloat to zero [cite: 25, 31].

## Scale and Bounds: When Does the Pattern Break?

A prevalent fallacy in architectural engineering is **PATTERN_BASE_RATE_NEGLECT**—the tendency to ignore historical statistical baselines regarding when a technology actually fails. When analyzing PostgreSQL as a message broker, critics often point to its ultimate scalability limits as a reason to avoid it entirely, neglecting the fact that the vast majority of applications operate well below these thresholds [cite: 1, 32].

### The Throughput Ceiling: ~10,000 Jobs Per Second

Empirical testing and documented production reports consistently indicate that a well-provisioned, finely tuned PostgreSQL database (running on SSDs, with optimized `shared_buffers` and partial indexes) reaches its realistic throughput ceiling for queue operations at roughly **10,000 jobs (or transactions) per second** [cite: 2]. 

At scales below 10,000 jobs per second (which equates to over 860 million jobs per day), the `SKIP LOCKED` pattern on a single primary node is highly stable, provided autovacuum and table bloat are managed [cite: 32, 33]. In fact, tests running on moderate multi-core SSD instances yield synchronous commit speeds well within the thousands-per-second range [cite: 34, 35]. For a system characterized by "single-digit machines" and "human-triggered sessions" (as outlined in the problem bounds), the throughput will comfortably sit orders of magnitude below this failure threshold, making PostgreSQL an exceptionally safe and robust choice.

### Mechanisms of Failure at Scale

If an application pushes past this ~10,000 jobs/sec boundary, the system begins to fracture in specific, measurable ways:
1. **Connection Pool Exhaustion:** PostgreSQL uses a process-per-connection model. Spawning thousands of connections to accommodate thousands of concurrent workers drains OS memory and incurs severe context-switching penalties. While connection poolers like PgBouncer can multiplex connections (handling upwards of 10,000 client connections by mapping them to a smaller pool of backend DB connections) [cite: 36, 37], the raw physical limit of concurrent active queries still forms a hard ceiling [cite: 35].
2. **Autovacuum Starvation (The Death Spiral):** Beyond tens of thousands of updates per second, the sheer volume of dead tuples generated outpaces the disk I/O available for the autovacuum process to clean them. The database cannot reclaim space faster than the workload mutates it, leading to unrecoverable table and index bloat [cite: 26, 31].
3. **Write-Ahead Log (WAL) Bottlenecks:** Every transactional state change (`pending` to `running`, `running` to `completed`) requires fsyncing the mutation to the WAL on disk to guarantee ACID durability. At extreme scale, this I/O bottleneck chokes the queue's performance regardless of CPU availability [cite: 28, 34].

### When to Migrate to a Dedicated Broker

The architecture crosses the Rubicon and necessitates a dedicated distributed broker (e.g., Apache Kafka, Amazon SQS) under the following conditions [cite: 1, 4]:
* **Sustained Throughput:** When continuous baseline load exceeds 10,000 jobs per second [cite: 2].
* **Consumer Fan-out (Pub/Sub):** PostgreSQL queues are fundamentally a point-to-point, competing-consumer model. If a single event must be read independently by multiple different microservices (e.g., an order creation triggers the billing service, the inventory service, and the notification service simultaneously), Kafka's append-only log and independent consumer group cursors are structurally superior [cite: 1, 4].
* **Long-Term Replay:** If the business requirements dictate that processed events must be retained for days or weeks to allow new consumer applications to "replay" historical data, a relational queue holding millions of terminal rows will suffer from insurmountable bloat and sequential scan latency [cite: 1, 2].

## Conclusion

Coordinating multi-machine agent work via a PostgreSQL table utilizing lease-based claiming is not a technological compromise; it is a highly robust architectural pattern that fundamentally reduces systemic complexity by eliminating external distributed message brokers. 

By employing the `FOR UPDATE SKIP LOCKED` primitive, developers bypass the historical pitfalls of relational queue lock contention, allowing for massive horizontal worker concurrency. However, this decentralized authority model demands rigorous safeguards. Time-based lease expiry must be fortified with database-level fencing tokens or optimistic locking to prevent the catastrophic split-brain duplicate execution inherent in stateless worker crashes. Furthermore, the pipeline must strictly enforce Dead Letter Queues to route around poison-item head-of-line blocking.

At the physical storage layer, the queue is perpetually engaged in a war of attrition against PostgreSQL's MVCC implementation. Maintaining query latency requires obsessive management of dead tuples through aggressive autovacuuming, the strategic utilization of HOT updates, a reduced `FILLFACTOR`, and partial indexing to minimize write amplification. 

Provided these failure modes are proactively addressed, the architecture offers unparalleled transactional consistency between business logic and asynchronous job orchestration. Bound by a throughput ceiling of roughly 10,000 transactions per second, it scales flawlessly for the vast majority of human-triggered, moderately scaled workloads, validating the decision to rely on relational state over disparate distributed daemons.

**Sources:**
1. [conduktor.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH0griuinyWFFNrep38HGnDD8x4jgB-KIHRT8vrZAkHMcPQ6Ys7Gz2Gdjdds9vTKCCA1e6hfG0SsvgHYOlqsgBk2whwo6gxV3_-_gwTfGgjZV8zty0YL5cxcWTFNMeXE-fhpjR4moC4g==)
2. [matthewswong.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-s8ZlO0zGIW1OY218n87aOLVGT5-nWfSorfrfunfET1a9zBHyOq0Df78-lc2h40Okbk0ZJ-LWNDmtvm7eSqC2pOYXAvrrrAZ8O-Lr631tywCMBJht4IUdQMrKDEQ17N77FEG0T_xTyPwdj_yfYfg-6wx3rseF0Qed)
3. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHfUS5iExc-nP-JIwRu94bneh8XpP5Qzneik41qi05Uc2ERmZ0bTJ45uoFsfWjMh9PzTdxtD9uR7HoQS4mptikMalpjUQxRrYZ2FPMXuZatdg-Ims=)
4. [prisma.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE-BKulFCVOg2ZBMVpxKeABv7cctBUMJ9qmc529xa_2OuD0DbRjKLTF_QndaUSFXHPp7e_DSpbfGrKmVG_-uPIUXKi2YH-ZLpHPtIZtH6eOllJlP_RPMeqxSCCa8wThpL1OWvvkk-We6rZbFBkj1f6GNJ92_U6mYOdkwb-ts6UovVcVlhN1nXkSj4=)
5. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC9lfmPp8DK7_CWAJEPJvTn6py7BKQg1ZIPhLLfiV28drTdxY5CXRbsfeY_a2E3Y8Kj03fzf27-gNoy7ox7tomSPnF-NWtORhjC3Vcdu9dwZwqKESjeipL-kkXsKtrU6x38y7C9TB4J8uOAiUMaVcTh8lEm1tAL9W8S2LY8MjU8PbLTwJ3qlNkK_q2bdqc8Cjn)
6. [netdata.cloud](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe1A8pCVStcdQ5VyEfMZrtQK9gRc38k6s_z7ezKURHv1tQVsYkq1PAgPbDnfZMAwjvfeatj6L29q85JbROOJyvCaJS-CKxBtdspnDTBUpsxTS_sTRo2rEEQj2iCxJ9bG4kT0XHD9prmNOV)
7. [parottasalna.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcrbFq29yZiFojjtAIk2ad-AVn5RFG-6bgNi0rvY_BjA__A9Zax031WPu_APNNTpDZLkkfe0JDWaKjO2KsZ73GC2bUU2r6uSecNKZwfEPekNVpC_PNmiYdW12yxC624uGDYjYAuWSqZQhsUYrm8c02vyqEmEkI5JcVZpx36YmVdHzQEumsSbCTYP4h7mmE0YRc)
8. [aminediro.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpldmdy8wUm2m6ul9rKcQ9tM8x4_dYl8vyrb7HUETYVJgiquQqej2qfaIz6y_gDJ3ONUkC2z7WnrhkoOCB6BcddDRhfFQe3ev_Bmw9Z6KCH9vrVCVJkNQ6Z12SJyXb)
9. [supaexplorer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy59n3MTGzAgx7xRe2RM66vO5N0ZvgHirSBYMZ2O-vJ_82WNJo1fZ21bCwPjlLF7dbchd0MK9CoiPNjgZExT1TV5PND07s-3nJz0qvjsEKFnQcJswnG_pwedDcf1SRyyESjlesDxQcpNVjFbDFUVUFOPgDsOyUZ0rFDz1w2qiWuw==)
10. [dbos.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgZA3QutL8GJM8cXb4ei4cGHpS9D6b3kbOiNxTTEiCMDEoLXymDlLXKScYmxO5x5hOCM3Q8Nv0Xx2S2xE17G5nQqgnzzm1rIgvRdyxulG9jhxKir1J91v0DvSBqQ07zRNcMcfY_tEtFKyfpg==)
11. [imti.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENRAaJAGU4pmo689zNMtKy_Cn0-jj900Wtt8Zameb9BYQDIOgR1nPgWqBrAiJeEmbOl2S4c4a4Uv-1YFxo4Cu5CXUNUjyTD-rUyWnSSpLbrnhwhaUGOgmSGfNz-Vq__fqqpNAv-Hc52y1xt6eZ8W0=)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoDmt7l9CbJ1uvqmo4Fcb7AbsR2SREglgDdem8Ty9hZz0VgWnB0JgJOyqOzM73ng1Cacrc9xGFpX4kGwahdsOrudU0wiuEQp4dyI6fMuiLkcVDcYEMLkRrINSF)
13. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGICRlkirpg3BS5XAWDsp3K6L3-BO8tojQZZ5NPVM3-CHbvyhD2VjNp_hMYmNNouSnS27bSs7Oo2S8STaMXRYuC62GquT7PBdoZGU-Gyl72nHpgxQ-vCoWFr7mqdYKD5fQm4EUoYbpL_uNPs5RJj4WyAmxzjJyGzNstfk6sNoJQWGB6Af-IFaGDU-YnmtifyZD3wOU5zTDnsI4=)
14. [digitalocean.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIFH1sk8olBx6NcAIaA-8Mjwi_A9bcZwvMkK2GTKTRMZHBJul_QWWkLsddMab4Vy2lBJyc57pov2MaeoljFC3x8zsCXDQOmWt4OfNCMdzbpgLrbogkzZnVUp-0jvXi2kkJyaE5XnYS77S9SrvtI7yuVPoMpVxNdyq_5Zdm3DG4TOouLsBCOwY0ZQqYlQ_Ex2o366FRHg==)
15. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNbpun7xetxly9XSfXHs5GBP7uk7pPt3RW-yWN9z3cevyaz8m2JAq6x2kThaxEjOu2bczgi4O0vlzqElT8Toqm8Ecu3zV3_sgXp-nxY64vOFDUNp8Lv_ykeLNU)
16. [plainenglish.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmnKelTMxvehGJW-I2EwenNgHec_DXf589AsWTTOGyIHFsAQ8Ad5IrJhItwjL22n7dZ81AkEb1Wy10naTCEIq1kjXLzpV2og9dUb_zWCtxWjs52Dg7JZh8WNhZLOR6txrSGdzYleqbNVHg4QMvogu6hYwvou2KKKZhbiv1FEPg7dmKnawm-FVbs1kgbAi-HkIJsEfgxNhilUMqzT9NJixDK00yhKGL62jlMjDOEg==)
17. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4v_Xv1m0rdIsKF2dhdrxKly6ksXBDylgb9QgkIdJG_vy6h9jwJZDuaLfK907TDxckge3696EPdEgQx1CHqxt4eecugXBHk0pp-1CxCWEzinloNh4anXd2LsWZMt2kajE=)
18. [rahuldhar.me](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQIH7mmz6LHksZo82b0z1p0a07WoWGs4JW9q3XBI6GyW71oFijTZQciJ4XQ-7Q-SY1TOX_QHavhFYWPG1y_X6Yl6Trgz8JDwvKrPSGmYGb4Z86YR3Iafk0i2ZgGgBJZKoJlvoACoy80I8ox2oamu_07md-MXY=)
19. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE758EFh4cndXGSQW2nfsn6udmHJJgYOpPcRvQrRYnVm1vMQUiyzyRchjpgv6ffkm3eB5Cz64JHwEF9SCJdCtYQrzV9VOqhjyfTvaEUavVw1O3VMzsQsiHscppMT9IgLPZMmquge1Mr97572PQTETV_hl7zjreUKdljluXd)
20. [glukhov.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF15QZUxSmdwAEB9TS3CwNTWyXYFUFjdDBQD-Fww90n5pcS9v6xfdmohGKH9crwwO8GZXhRMSFmpu1D8Wn-7Cf4m8s12zYJ52o-3bHeKdyltFYrcvD0SeoTDRwa3v6pqoAo73fwLtA0c1mlAhkv9fkSOb0uVhs_coJhgP5lqIXkkl-M618MFA==)
21. [tigerdata.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdbl7-9RouJrIgh-NdlCVdiqGdtGgVRUg2VcDmACHS1onygU9ZslDQKY20xalG9TnrD3vmg0hGD2gZEZomcM5oCpv-58_aCSHpchUyg-aiL3R9CIfTe6UYYxYx9xkKRiHpRA-HNTLzyHKR7pbJvScYVpFWDu-rU997ZY-tDiz90vNBsg==)
22. [singhajit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_crqncdRVDAH5x7uXezmvyFO64DcmZSZ1QIZ0q12kcIdURBp1A39IAHft7mScLGb4weT9OqeLtR0AyjtR7hfU3rdyyxu6tiGcymcbftXu9ZYAdTkqkqJrUeTUOJBULx4DnnKxQ9Y=)
23. [boringsql.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBotsoGN2Y0HHOkAQoGiQJ0diodxaRqE_ec-BEcxOhgAD_mB0sOEPtLXaWl1owfQ1YJ_VV0lm8VCPBjfnGVw7vFXI3HI0KFidDqAFQl5KJRq-W3XFCRraAkWFHKgWX)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB-gP47pcsuw1YXh7mDqVdxDon2KOqCSI0u3QB_iZP3Kcrht0srY3pujOOiGooS7DuraSz3SDw9n8i0tCFZ8nNDnISsLG1OU6Cy33l82WtnmnqbvzgDGL5OgWyDxq3jKgWlGbaj9zOsXtWO6ve5Fq1y1MMo9TrJkfL3g==)
25. [postgres.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGExu7F1lxklA2SNBZFy9UY56_ol_3n9o7hiZZjkKZUKZrUlkqxaHCB1beVFCD6PLCF8HIcIlN6yb4wzHRsxjFSUDoP0e7xw9xIlGYqM74RfqY3ZzaFq65nMdBHtL_JzVGVsZvWOPcOKRN8tYyPrI5EUOucfUcrcaWBk4tmF8FZRe_9f7YcZaQdg5xWu6F8cDwYwq3UTx-JVQ==)
26. [planetscale.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZfkWfq2eg_sNjD0IQA1gBNBJmKsAgWjSJZlcOKPIt-guzH24NeqId2mPM2m-LbbUMU6SLFfZBphIR8hcqLg32RNpTSu50GjTYUm8T_gsQUSkCl6yqvj7auDXin2oJnWk04hSCJDBMjf8uUuT-FhUHN3E=)
27. [andyatkinson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYTWQ3rDiTOxmpB5aESJ7qCywR5394KVusViub7Y6_zmDvkPTidFIb9AKx2_dCMzc18ueqhxG1W6owR9WQ_hZXwN4xyHSCq105TiKWTpAcjvcLVqf44slVV0RVawI=)
28. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGADWM9_XoSEQ7-HnxiTdm3BBeq5m6RnaIXs1ZOxzrQnRPodKKTFgNOgMtxsEDMWF3XQ8-USQGTKLoWKVGuvfQ8t4vd6bndzbBnda0r4lFsEWB2MWFCivtyGP43r7fK-74vvw_fM2G_cOwhEiwTes9IrXk6HV6vDivMto78O8cWykdO7OS_T95-K9eagyIHnIUf9pc=)
29. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbXnbDtJtOtuQuB7ypORgXwdVm7QigIlQKbvpDZdwEoNHkY7Igg03obgGR8MhRlpyy9hQDZWPmI6MZWqv2JWm4_-znClxdZBcNgI8YfSLWtFCKHUTctInH7HDbqAi1GYRUpQtPtGrYmtzJr9Dkq_-4C7AfNUYVtPHqxvlGGZTdud2H)
30. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNRN0cg0Tugl6B_pKvsfoi0cWdDcRZwjoRiWdxZdSHKHkIoBLwxBBkxyWlVgiY_aD8SBDI2rLaAHmU6QVK6Izxt_R7mA8ALggxiHPCk2CHA3HnhxCbpWGWdWhKyxszXk6ifg==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFtU-TXym7C-LNWOTBcCc9oo-3LZ8shRsodVBpkQeQRFv_MnPWZyKjE7cv8Iy_QKo_2NIH3WOLB21rnm2unUGrbI_YFgsgJRNrtpiAntlv1BgG1WJV5w==)
32. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENj_AlyoZUCYsaoNXiWzdnZGfKksEzdJmSq8H53SJxF-ceqjb70v_HzMKXJZKc9TXOWV-7nHvQcEBjsk1QZD7GzLATZ_EEcbUmvbvlShx-vRX4bfFz0zcuzi07L69CRr0MFw==)
33. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp0cwSnnst8sY4IQCXV48NTU4nQS44Ji-9oclxqW43kQWAW7gBCE2nHSB7i8xYEY5BBSJw5Bn_0DGWojZt5aHg_oOFSeFNsQQXCj8jdNo6jEE8AuHrOqetOrIozgmbZNy9gg==)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaoRvqSbGIQQVOE8aMLbyunYcqLthHDdpdzujTKFLeaqDbEwgxTDfZQyJUXCLQI7-3Hb6KmnzryeHe3IYwWoDPHrWcJZn-VzP0gSjocLuVN9JX64mbstARl4j7)
35. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzjcM19RjRHhwpbnuqsvDa2DciYic0hdLEf_KxZUe27BgDhj0tPrT4Di-vpEgpHYVRg7VwYAei89dPY6A1r3fUqth7s_6tOpWrIp81klaEf3gUr9yjFseeOswZfegMk_QqdytYlENohR62cNgqbPfRf3i3jJtBrezFKy9js_dzX0pcxlwovpw0n6jWaBvSwR1atrU=)
36. [tinybird.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRsLeo6Kstpv9UQaADS9mFiZ7Y3B15Dv6FzKzPlUF41WwMMB2Llo7hh8k3O_V0s31WvD4Vs8epL_oRFAm4QmTHUsyUlvlAwXER3Swkrj9xkXX6JFWGwhmnF5g3tdNabmEllhrSQcV3gWd7RqrUIemUO62QoZF7deHjTjMugeyhqPMH1LfsAigrTQ==)
37. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDQCc4-R-K-GvwFV5XnTOINF7VlUcTcJbbFTt0eu8YK7Von0lQCLxt4kQFENRdG-dJjbSDiAm1I1pdhDbxvzszvgJVHaoFPI7lMmjICv5Ed8I3N8jbnZt23NkzGqW8ULr9HoNzpVpfiE6UB3qAAN21Ys-Y7kLnZiDw-iL4OgowpQxORiatkW4TaBSo8AnR0AxF7CcVbsJTEeGvk8PpsYYpDWNTemfdpbuG08lksVpz9yrouA==)
