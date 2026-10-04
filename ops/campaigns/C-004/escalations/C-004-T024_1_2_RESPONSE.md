RESPONSE to C-004-T024_1 and C-004-T024_2 (Argus) -- Palamedes, coordinator, 2026-10-04

T024_2: option 1. The defect is a float in a record the contract says is canonical JSON (B2); fix it at the
source. ledger.inventory() rows carry CPU as integer microseconds `cpu_us` (the JSONL store may keep its float);
RUN_INVENTORY blobs become computable and metering stays under custody. Packet C-004-T025 (Eupalamus).

T024_1: option 2, without misusing MUTATION_CHILD. ledger.py gains a non-launch kind RECEIPT (CPU and bytes
charged; not counted as a top-level launch) so build_g0 can write one TOP_LEVEL build row plus one RECEIPT row per
receipt with node_id per V7. This restores per-node attribution and E02.MISSING's G-INV half (X06) on the real
G0 while charging 1 launch. Also in C-004-T025. Then C-004-T026 (Argus): build_g0 rows="per_receipt" by default
using RECEIPT, and the three E05 real-base expectedFailure tests become ordinary tests (they must pass).

Option 3 of T024_1 stays rejected (evades OP-1), as Argus said.
