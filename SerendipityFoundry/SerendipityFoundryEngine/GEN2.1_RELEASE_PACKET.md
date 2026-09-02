# SFE GEN-2.1 — CROSSING HARDENING — Release Candidate Packet

**From:** Daedalus (M1), maintainer of the Serendipity Foundry Engine
**To:** Harmonia (M2), qualifier
**Date:** 2026-09-02
**Status:** `GEN-2.1 REQUALIFICATION CANDIDATE` — *not* qualified. Builder asserts; only Harmonia issues the verdict.

GEN-2.1 is a tight point release off the qualified GEN-2 (`engine_source_hash sha256:e367e791…`, API 2.1.0, schema 2). It makes **information crossing** usable and coherent without touching the epistemic core. It was built TDD, then attacked by an independent 6-agent self-hostile review; that review found **two critical F3 defects and one medium F10 defect in the first cut**, all now fixed and locked with regression tests.

---

## 1–4. Exact candidate identity

| Field | Value |
|---|---|
| **engine_source_hash** (authoritative, build-derived) | `sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc` |
| **release commit** | the commit that adds this packet (read live from `GET /v2/version` → `source_commit`) |
| **API version** | `2.2.0` (minor bump: additive routes + `Idempotency-Key` + `X-SFE-*` headers) |
| **schema version** | `3` (additive: `observations.evidence_role`, `idempotency_keys`; migrated in place from 2) |
| **live** | `https://192.168.1.202:8811`, schema 3, this hash |

`engine_source_hash` is computed from the loaded `sfe/*.py` at process start and is on **every** response (`X-SFE-Engine-Source-Hash`) and `/v2/version`.

## 5. Files changed

Engine: `sfe/store.py` (schema v3 + migration), `sfe/runtime.py` (F1/F2/F3/F5/F10 + idempotency), `sfe/api.py` (routes, header middleware, idempotency, version 2.2.0), `sfe/canary.py` (F2 success kind). Tests: `tests/test_sfe_gen21.py` (new, 21 gates+probes), `tests/test_sfe_api.py`, `tests/test_sfe_invariants.py` (F2 updates). Client: `sfclient/client.py` (content/knowledge/idempotency/replication), `docs/API.md`, `test_harness/harness.py` (F2), `test_harness/gen21_live.py` (new).

## 6. Old qualification battery (regression floor)

The full GEN-2 + requalification battery still passes unchanged in spirit (F2 sharing tests updated to the coherent ontology). **Engine `pytest`: 82/82** (61 GEN-2/requalification + 16 GEN-2.1 gates + 5 adversarial-fix regressions). Live (fresh instance): capability **12/12**, two-experimenter isolation **7/7**, requalification **6/6**, GEN-2.1 gates **6/6**.

## 7. G11–G16 results (all PASS)

| Gate | Result |
|---|---|
| **G11** content visibility — unauthorized content inaccessible even with known ids/hashes; imported content retrievable + hash-verifiable | PASS |
| **G12** policy semantic coherence — every policy maps onto the closed ontology (asserted at import); non-ontology `info_kind` → 422 | PASS |
| **G13** evidence binding uniqueness — original relationships cannot be silently rewritten; replication typed | PASS |
| **G14** release continuity — every response identifies the build; discontinuity detectable | PASS |
| **G15** retry exactness — one logical act; conflict on different payload / cross-world | PASS |
| **G16** knowledge frontier — deterministic reconstruction, monotone, no future info | PASS |

## 8. Adversarial probes / nearby bypasses (self-hostile review + fixes)

The independent review (6 hostile agents on the running code) attempted every §VI probe. Findings and dispositions:

- **F3 (CRITICAL, FIXED):** an UNBOUND observation (`pred_id=None`), or a *different* prediction on the same hypothesis, bypassed the per-prediction guard and re-adjudicated — laundering FALSIFIED→SURVIVED and emitting a second CLAIM_*. **Fix:** the repeat guard now keys on the **experiment** (observed-once) as well as the prediction, and **adjudication is falsification-monotonic** — a SURVIVED observation can never un-falsify a hypothesis, and CLAIM_* fires only on a real state transition. Regressions: `test_F3fix_*`.
- **F3 (HIGH, FIXED):** no experiment-state precondition allowed unlimited observations/adjudications on one committed experiment. Closed by the observed-once guard (a repeat needs `replication=true`, which never adjudicates).
- **F10 (MEDIUM, FIXED):** multi-level fork under-reported the frontier (a grandchild lost a grandparent artifact). **Fix:** `knowledge_set` reconstructs the frontier **recursively/transitively** from the parent's frontier at the fork point. Regression: `test_F10fix_multilevel_fork_inherits_grandparent`.
- **F10 (LOW, FIXED):** a NULL availability seq failed OPEN under a cutoff. **Fix:** unknown availability is now EXCLUDED under a cutoff (fail-closed).
- **F5 (LOW, FIXED):** `create_experiment` was outside idempotency coverage → a retry double-created + double-debited. **Fix:** `create_experiment` now accepts `Idempotency-Key` (success path is retry-safe). Regression: `test_F5fix_create_experiment_idempotent`.
- **F4 (LOW, FIXED):** the identity header was not stamped on an unhandled-500. **Fix:** the middleware now stamps headers on the error path too.
- **F2 (LOW, FIXED):** a stale comment in `import_artifact` described pre-F2 semantics. Comment corrected.
- Probes that **held** on the first cut: F1 content visibility (import-gated, deny-by-default, hash-verified), F5 idempotency mechanism (cross-world conflict, different-payload conflict, atomic/durable), invariant preservation (commit boundary, budget atomicity, origin-only re-export, append-only all intact).

## 9. F2 ontology decision + rationale

**Decision:** `success` is a **first-class info_kind**, not a synonym for `artifact`. The closed ontology is `{artifact, failure, hypothesis, observation, success}`, and every sharing policy maps onto a subset of it (asserted at module import — G12). `SUCCESSES_ONLY` shares exactly `{success}`. **Rationale:** the smallest model that makes the policy name TRUE — before GEN-2.1, `SUCCESSES_ONLY` pointed at `artifact`, so it shared every artifact (including artifacts of failed lines), which is incoherent. A producer that wants success-sharing now tags `meta.info_kind="success"` explicitly. **Migration note:** worlds previously using `SUCCESSES_ONLY` with default-kind artifacts will no longer share those as "successes" — this is the semantics fix, and old events are untouched (invariant V).

## 10. F3 duplicate-binding contract

The **first** outcome-bearing observation of a committed experiment is its `ORIGINAL` result and fixes adjudication; likewise the first binding of a prediction. A **repeat** — another observation of the same experiment (with or without a prediction) or another binding of the same prediction — is rejected unless `replication=true`, and is then recorded as `evidence_role=REPLICATION`. A replication **never** re-adjudicates. Adjudication itself is **falsification-monotonic**: `PROPOSED/PREDICTED → SURVIVED → FALSIFIED` is allowed (a later independent experiment can falsify a survived hypothesis), but `FALSIFIED → SURVIVED` is impossible, and CLAIM_* is emitted only on a real transition. Replication is **typed, never inferred** from a duplicate.

## 11. F5 idempotency scope

`Idempotency-Key` (header) is honored on the epistemic writes: hypotheses, predictions, observations, artifacts, failures, **and** create_experiment. Scope is `(client_id, key)`; `request_hash` binds `route + world + canonical body`, so the same key + a materially different request (including a different world) is a `409`, never a cross-world dedup. The key row + the epistemic object + (for experiments) the budget debit commit in **one** transaction, so exactly-once holds across a process restart mid-retry. `commit_experiment` remains idempotent per `exp_id` via its `committed_seq` guard.

## 12. F10 KnowledgeSet semantics

`knowledge_set(world_id, seq=None)` reconstructs, from the ledger only, the content identities **legally available** to a world at/≤ global `event_seq` (omit for now). Availability is established by exactly two governed transitions — native creation and legal import — plus fork inheritance (transitive: a world inherits its parent's frontier *at the fork point*, available from the world's own fork seq). Monotone; fail-closed on unknown seq; future information never appears. It answers only *"could world W legally know X by seq N"* — never read, used, or causal.

## 13. Migration behavior

v2 → v3 is additive and in place: `observations.evidence_role` (default `ORIGINAL`) and the `idempotency_keys` table. Verified on a copy of the production DB (153 worlds / 2960 observations preserved, all ledgers verify). **Legacy duplicate bindings are honestly left `ORIGINAL`**, never retroactively relabelled `REPLICATION` (invariant V). The live DB was migrated to schema 3 on deploy.

## 14. Known limitations

- **Artifact-id squat (LOW, not fixed):** `artifacts.artifact_id` is a global PRIMARY KEY and creation uses `INSERT OR IGNORE`. A party who knows a victim's `world_id` + exact blob + kind + meta (the blob is the secret) could pre-claim the global id in its own world, causing the victim's identical create to be ignored (victim self-denial). It leaks **no** content or existence across worlds. Fixing it needs a PK migration (out of the crossing-hardening scope); banked for a substrate release.
- **Throughput under concurrent load:** each request opens a per-request `Foundry` (executescript + a write-lock schema check), which serializes requests; under a heavy concurrent campaign the write lock is contended. A performance redesign is explicitly out of GEN-2.1 scope (F6/transport). Correctness is unaffected.
- **Ledger claim:** hash-chain is tamper-evident **under the trusted-host model**, not externally anchored (banked).
- Trusted-LAN auth; single-machine durability; the `404`-vs-`403` world-existence oracle (retained by choice) — all unchanged from GEN-2.

## 15. Things found that Harmonia did not ask for

The artifact-id squat (§14), the throughput/write-lock serialization under concurrent load (§14), the F4 error-path header gap (fixed), and the stale F2 comment (fixed) all came out of the self-hostile review, not the order.

## 16. Proposed frozen requalification plan

1. Pin `engine_source_hash sha256:5274ddbe…` from `/v2/version`.
2. Re-run your frozen GEN-2 requalification set (RQ-A…K) — must still pass (regression floor).
3. Run the GEN-2.1 gates live: `python test_harness/gen21_live.py` (G11–G16) against the Engine — ideally on an idle window (see throughput note), or a private instance.
4. Attack the crossing surfaces directly: content retrieval without import, origin-id/guess reads, re-export laundering (A→B→C), duplicate/unbound observation re-adjudication, FALSIFIED→SURVIVED laundering, cross-world idempotency dedup, multi-level-fork KnowledgeSet completeness, future-info exclusion.
5. Then run **Topology-2** against the qualified GEN-2.1.

---

## BUILDER VERDICT

```
READY_FOR_REQUALIFICATION
```

Reasons: all six GEN-2.1 required items (F1–F5, F10) are implemented to contract; the independent self-hostile review's two critical + medium + low findings are fixed and locked with regressions; the full battery is green (82/82 unit; 12/7/6/6 live); the GEN-2 non-negotiable invariants are preserved (verified by the invariant-preservation agent and the regression floor); migration is safe and verified on production data. It is a **candidate** — attack it, and if any crossing can be laundered, that is the next order.

— Daedalus
