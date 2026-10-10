# OP-NF2 -- Prometheus Native Execution Fabric (operator amendment, verbatim)

The operator's words, byte for byte from the session transcript (session 0e9b1ed2-f51f-49c9-a2ea-5c93be2dfb1c).
AUTHORITY for replacing Git-CAS runtime coordination with a PostgreSQL-backed design built on the
existing Fabric service and Pan's Parquet/Iceberg evidence architecture (EP-MOONSHOT).

---

## 2026-10-10T07:15:43.846Z

OP-NF2 — PROMETHEUS NATIVE EXECUTION FABRIC

Operator amendment to the proposed Git-CAS replacement

Owners: Themis, with coordination from Odysseus and Pan
Epic: EP-MOONSHOT
Horizon: 48 hours of iterative engineering and experimentation
Resource policy: Existing MWO-0004 limits; local execution only

Mission

Replace Git-CAS runtime coordination with an internal architecture built upon Prometheus’s existing PostgreSQL infrastructure.

Do not implement SQLite.

Do not build a second generic task queue.

The existing Fabric service is the starting point.

Pan’s Apache Parquet/Iceberg implementation is the starting point for scientific evidence storage and analytics.

Preserve Moonshot’s transport-independent scientific identity and all valid findings from C-008.

1. Reconcile the existing implementations

Inspect:

* fabric/
* fabric/store.py
* fabric/schema.sql
* fabric/README.md
* fabric/promexec/STATUS_EXPERIMENTAL.md
* pan/
* pan/iceberg.py
* roles/Pan/docs/DATA_ARCHITECTURE.md
* moonshot/epoch/

Confirm the current operational status and ownership of each.

Read Pan’s October 9–10 commits, particularly the PostgreSQL catalog, Iceberg history and large-scale JSONL consolidation work.

Coordinate with Odysseus and Pan before proposing changes to their interfaces.

Do not modify either owner’s schema without review and authorization.

2. Establish the division of responsibility

FABRIC owns:

* Job submission and claims.
* Worker identity and capabilities.
* Resource leases.
* Heartbeats and attempt execution state.
* Generic task retry/recovery.

MOONSHOT owns:

* Canonical epoch identity.
* Checkpoint lineage.
* Atomic epoch publication.
* Duplicate and disagreement classification.
* Scientific replay/validation state.
* Contest/taint resolution.

PAN owns:

* Scientific dataset catalogs.
* Parquet conversion and analytical schemas.
* Iceberg snapshots and historical datasets.
* Searchable evidence metadata and cross-experiment discovery.

Do not conflate these responsibilities.

3. Implement the smallest PostgreSQL epoch-publication extension

Design a versioned Moonshot schema on the existing canonical PostgreSQL cluster.

The schema must permit a guarded transactional publication:

An epoch may advance a chain only when its expected parent and chain generation match the current authoritative state.

Identical repeated results are idempotent.

Differing results for the same work identity are preserved and classified as disagreements.

A stale worker cannot silently advance the chain.

Publication does not confer validation authority.

Attempt accounting remains durable and separate from canonical scientific traces.

Retain all C-008 semantic identity and replay tests that remain applicable.

Add PostgreSQL-specific concurrency, transaction rollback, lost-acknowledgment and crash-recovery tests.

Use Fabric’s canonical resource leases. Do not establish another competing lease authority.

4. Integrate with Pan’s evidence architecture

Design the mapping from Moonshot’s canonical artifacts into:

* PostgreSQL publication metadata.
* Immutable content-addressed artifact objects.
* Parquet event/measurement data.
* Iceberg tables for versioned experiment history.

The authoritative publication transaction must not depend on an Iceberg snapshot update.

Define a recoverable, idempotent process that materializes newly published evidence into Pan’s lake.

Coordinate the lake’s network-accessible location with Pan.

Do not assume M2-local Iceberg files are available to the Ubuntu nodes merely because their catalog entries exist on M1.

No bulk migration of historical Prometheus data is required.

5. Two-node native execution experiment

Demonstrate one deterministic Moonshot synthetic epoch using:

Fabric task claim
→ approved execution
→ immutable evidence publication
→ PostgreSQL chain update
→ independent replay
→ durable receipt.

Then demonstrate two workers racing for the same successor.

Both identical-result and conflicting-result cases must be exercised.

The system must distinguish:

PUBLISHED, DUPLICATE, CONTESTED, STALE, INVALID and UNVALIDATED/VALIDATED.

Repeat the critical crash and lost-acknowledgment cases.

No Git remote may be involved in claiming, executing or publishing these epochs.

6. Fleet benchmark

Once the two-node implementation passes its fault-injection controls, preregister a bounded multi-node benchmark.

Use the available Linux e-waste fleet without interfering with other active experiments.

Measure PostgreSQL coordination overhead separately from execution time and artifact transfer.

Include throughput, claim latency, retry amplification, storage growth, recovery and correctness.

Do not assume the existing Fabric service will meet Moonshot’s scale requirements.

If it fails a meaningful bound, document the precise bottleneck before proposing an additional component.

7. Security and execution boundaries

Fabric’s existing promexec isolation boundary is still marked experimental in the reviewed repository state.

Do not treat it as production-qualified merely because Fabric task claiming works.

Use only approved, bounded deterministic executors for the initial experiment.

Do not expose unrestricted command execution or privileged database credentials to arbitrary fleet workers.

Authentication, authorization and resource isolation must be explicit parts of the acceptance criteria.

8. Preserve scientific momentum

This infrastructure integration must not consume the entire Moonshot program.

Continue the native-world repair and independent RSO claim-mapping work with the respective owners.

Once PostgreSQL-backed synthetic epochs are qualified, put the first deterministic native-world epoch through the new path.

Do not launch evolutionary survival search against the known wforge affordability defect.

Deliverables

Produce:

1. A reviewed Fabric/Moonshot/Pan interface contract.
2. A minimal PostgreSQL epoch-publication implementation.
3. Transactional and adversarial fault-injection evidence.
4. A working two-node demonstration.
5. A preregistered fleet benchmark, if the two-node controls qualify.
6. A Parquet/Iceberg evidence-materialization design or bounded demonstration.
7. A concise engineering review identifying what is ready for native science.

Preserve the Git-CAS C-008 results as historical engineering evidence. Record any unexecuted Git benchmark as such; do not silently convert it into a scientific verdict.

North Star: An autonomous, scientifically accountable computing fabric that scales with inexpensive hardware and preserves the rare reasoning mechanisms Prometheus discovers.

Proceed.
