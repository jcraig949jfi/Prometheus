# GEN-2 REQUALIFICATION CANDIDATE — Handoff to Harmonia

**From:** Daedalus (M1), maintainer of the Serendipity Foundry Engine
**To:** Harmonia (M2), qualifier
**Date:** 2026-09-01
**Status:** `GEN-2 REQUALIFICATION CANDIDATE` — *not* qualified. Daedalus builds and asserts the contract; only Harmonia may issue the verdict.

This repair implements the execution-commit correction and the DFX/H hardening order in full. It does **not** merely patch DFX-1..4 literally — it introduces one irreversible experimental-lifecycle boundary and hangs the ordering, budget, and release-identity guarantees on it.

---

## 1–4. Exact candidate identity

| Field | Value |
|---|---|
| **engine_source_hash** (authoritative, build-derived) | `sha256:e367e791c10080decc8ac8152c82fde61b426682a9bc298403f0ccc970f9ed1a` |
| **source_commit** | HEAD at process start; updates on the next restart after this commit is pushed (see §XIX note). Read live from `GET /v2/version`. |
| **client** | `sfclient` (stdlib), `SerendipityFoundryClient` |
| **API version** | `2.1.0` |
| **schema version** | `2` (migrated in place from v1: 28 worlds / 507 events preserved, ledgers verified) |

`engine_source_hash` is computed at process start over the loaded `sfe/*.py` (LF-normalized), so it is a property of the running build, not operator attestation. It appears on `GET /v2/version` and is stamped into every `EXPERIMENT_COMMITTED` event. **Whenever you requalify, first `GET /v2/version` and pin that hash; every result you accept should trace to it.**

---

## 5. DFX-1..4 dispositions

| Defect | Disposition |
|---|---|
| **DFX-1** prospective ordering bypass | **FIXED, semantics replaced.** Prospective eligibility now closes at the **experiment COMMIT boundary**, before execution is possible — not at first observation. A prediction is prospective for an experiment iff `prediction.created_seq < experiment.committed_seq`. A post-commit prediction is refused (`409 prediction_ordering_error`) unless explicitly `retrospective=true`, and is then recorded but never prospective. Observations are only accepted on committed experiments. |
| **DFX-2** budgets not authoritatively consumed | **FIXED.** The experiment budget is debited **in the same atomic transaction as the commit**. There is no state where an experiment is executable but undebited; a budget block leaves it REGISTERED, non-executable, with the exhaustion durably recorded (commit-then-raise). Idempotent: re-committing does not double-charge. |
| **DFX-3** exact running release absent | **FIXED.** `engine_source_hash` + `source_commit` on `GET /v2/version`, `world_status.engine`, and in every `EXPERIMENT_COMMITTED` payload. |
| **DFX-4** nested config not fail-closed | **FIXED + audited.** Budget specs, fork-child specs, and artifact `info_kind` are strict recursively (`422` on unknown control keys). Freeform payloads that are user-owned by design remain open and are documented as such: experiment `spec`, fork-child `interventions`, and artifact `meta` (except its `info_kind`). |

## 6. H1..H6 dispositions

| Hardening | Disposition |
|---|---|
| **H1** lease fencing | **DONE.** Each claim mints a server-issued `claim_id`; it is required on heartbeat/complete/fail and is invalidated on reclaim. A stale attempt cannot act **even from the same `worker_id`** — the claim *attempt*, not the worker, is the identity. |
| **H2** fork epistemic time | **DONE (structural).** Experiment and prediction rows are world-scoped; a child cannot observe an inherited (parent) experiment (`404`), and event `created_seq` is globally monotonic, so a fork cannot turn past evidence into future evidence. Inherited history + lineage remain mechanically reconstructable and chain-verifiable. |
| **H3** fork budget | **DONE.** Every world carries a `budget_root`; a fork inherits the parent's root. Authoritative consumption debits **both** the world-local safety cap and the lineage root, so repeated forking cannot mint fresh scientific budget. `budget_status` reports scope + the lineage row. |
| **H4** evidence authority | **DONE.** Observations carry an `evidence_class`: `ENGINE_WORK_RESULT` (bound to a verified COMPLETED work item of this experiment) or `CLIENT_ASSERTED` (default). The class is recorded on the observation, its event, and any `CLAIM_*` adjudication — provenance survives adjudication; a client assertion cannot be dressed as engine-attested (forging a foreign/incomplete `work_id` is `422`). |
| **H5** sharing must be bilateral | **DONE.** A cross-client crossing requires a **registered** `topology_group` — a server-issued, unguessable capability (`grp_` + 96 bits) minted via `POST /v2/topology-groups` and shared by deliberate transfer. Matching a fabricated or self-minted group id does not grant membership (`403`). |
| **H6** transitive re-export | **DONE (safe default).** A cross-client import must draw from the artifact's **NATIVE origin**; an IMPORTED copy held by an intermediary cannot be re-exported to a third client (`403`). Provenance stays transitive (root origin, immediate source, content id); an import can never become indistinguishable from independent discovery. |

## 7. The experiment lifecycle / state machine

```
HYPOTHESIS -> PREDICTION -> EXPERIMENT REGISTERED
                                   | (planning: editable, non-executing,
                                   |  no budget, prospective window OPEN)
                                   v
                          EXPERIMENT COMMIT   <-- the one irreversible boundary
                             |  freeze spec (spec_hash)
                             |  CLOSE prospective window (committed_seq)
                             |  DEBIT budget (local + lineage root)
                             |  stamp engine_source_hash
                             |  (optional) enqueue work == authorize execution
                             v
                     CLAIM (server-issued claim_id fence)
                             v
                     EXECUTION (remote, under lease)
                             v
              AUTHORITATIVE RESULT / FAILURE (exactly-once, fenced)
                             v
                     OBSERVATION (evidence_class; prospective iff pred<commit)
                             v
                        ADJUDICATION (CLAIM_SURVIVED / CLAIM_FALSIFIED,
                                      carrying prospective + evidence_class)
```

`create_experiment` commits by default (register+commit in one call); pass `commit=false` to plan, then `POST /v2/worlds/{wid}/experiments/{eid}/commit`.

## 8. Exact prospective-ordering rule

> A prediction P is **prospective** for experiment E **iff** `P.created_seq < E.committed_seq`.
> The commit closes the window **before execution becomes possible**, so neither a prior observation nor a worker's local knowledge of the outcome can be laundered into foresight. A later observation never reopens the window.

## 9. Exact budget scope

Two named scopes, never conflated:
- **FORK_LOCAL** — a world's own `budgets` row: a per-world safety cap.
- **LINEAGE_ROOT** — the `budget_root` world's row: the authoritative campaign budget a lineage shares. A commit debits both; the tighter enforceable limit blocks. A root world is its own root. Pre-v2 worlds were migrated to be their own root (their historical world-local meaning is preserved, not silently reinterpreted).

## 10. Fork inheritance semantics

A child inherits, by reference: the parent's immutable event prefix (chain-verifiable), the parent's `budget_root`, and its sharing policy/topology defaults. It does **not** inherit experiment/prediction/observation rows (those are world-scoped) and its budget-consumed resets to zero (local cap only; the root is shared).

## 11. Lease fencing mechanism

`claim_work` returns `claim_id` (a `clm_`-prefixed token). `heartbeat`/`complete`/`fail` require it and check `claimed_by == worker_id AND claim_id == current`. `_reclaim_expired` sets `claim_id = NULL` on the item, so an expired attempt's token can never match again.

## 12. Evidence provenance classes

`ENGINE_WORK_RESULT` (backed by a verified COMPLETED work item enqueued for the experiment) and `CLIENT_ASSERTED` (a client-supplied observation). Bind by passing `work_id` to the observation. The class is immutable on the record and carried into adjudication events.

## 13. Sharing / re-export semantics

Cross-client sharing: register a group (`POST /v2/topology-groups` -> `grp_...`), give it to the other client out of band, and set **both** worlds' `topology_group` to it; the source policy must emit the info-kind. Re-export is origin-only (H6). Same-client cross-world import is governed by the destination policy + matching group (no registration required within one client).

## 14. Token lifecycle semantics

Registration (`POST /v2/clients`) can be operator-gated after bootstrap (`serve.py --registration closed` -> `403`; existing tokens keep working). Operator tools (on the host): `manage_client.py revoke|reissue`. **Revoke** kills the current token (`401` thereafter); **reissue** binds a new token to the **same `client_id`**, so identity and all historical provenance are unchanged. Both are on the foundry audit chain.

## 15. Regression tests added

- `tests/test_sfe_requalification.py` — the full battery: D1-01..07 + observation-requires-commit, D2-01..07 + concurrent-one-debit, H1-01/02, H2-01/02, H3-01, H4 (3), H5 (2), H6-01, DFX-3, DFX-4 (3), verify_world authorization, token revoke/reissue.
- `tests/test_sfe_api.py` — fencing-token required (`422` without it), commit route in OpenAPI, version `2.1.0`.
- Live: `SerendipityFoundryClient/test_harness/requalification_live.py` (6 invariants over REST).

**Results (this candidate):** Engine `pytest` **61/61**; live capability **12/12**; live two-experimenter isolation **7/7**; live requalification **6/6**; v1->v2 migration verified on a copy of the production DB (28 worlds / 507 events preserved, ledgers intact).

## 16. Nearby bypasses attempted (and closed)

- late prediction after commit (RQ-A) — refused.
- late prediction after work CLAIM / after the worker learns the outcome (RQ-B) — refused.
- second observation to reopen the window (D1-06) — refused.
- stale-lease completion after reclaim, same `worker_id` (RQ-C/D) — refused.
- register-many then never commit to dodge budget (D2-01) — budget only at commit; observation blocked until commit.
- fork to refill budget (H3) — lineage root blocks.
- fork to re-observe inherited evidence (H2) — parent rows absent in child.
- guess/substitute a topology group to self-enroll (H5) — `403`.
- re-export an imported artifact A->B->C (H6) — `403`.
- forge `ENGINE_WORK_RESULT` with a foreign/incomplete work id (H4) — `422`.
- nested unknown control keys in budget / fork-child / info_kind (DFX-4) — `422`.

## 17. Previously-passing systems touched (and re-verified)

Work queue (now fenced), budgets (now commit-driven + lineage), observations (now commit-gated + evidence-classed), fork (now budget-root + child spec strict), sharing/import (now registered-group + origin-only). The two prior critical isolation fixes (client-scoped claim; bilateral-consent import) are **preserved and strengthened**. All pre-existing invariant tests (T5/T6/T7/T16 etc.) updated to present the fencing token and still pass; isolation harness still 7/7.

## 18. Remaining limitations (stated plainly)

- **Trusted-LAN** trust model: a valid token fully authorizes; TLS protects it in transit; no per-request signing.
- **Ledger claim:** the per-world hash chain is **tamper-evident under the trusted-host model** — it proves internal consistency of the stored sequence, not resistance to a privileged process/DBA who rewrites history and recomputes the chain. No external anchoring is implemented (banked as a later option).
- **World-existence oracle:** a `404`-vs-`403` distinction over opaque world ids reveals existence only (no data); retained by choice for cooperating colleagues.
- **Durability:** single-machine (M1), SQLite WAL.
- **Same-client sharing** still uses free-form `topology_group` strings (registration is required only for cross-client crossings).

## 19. Commands / endpoints for independent requalification

From `SerendipityFoundryClient/` (Engine at `https://192.168.1.202:8811`, cert `config/m1.crt`):

```bash
# exact candidate identity — pin this hash
curl --cacert config/m1.crt https://192.168.1.202:8811/v2/version

# unit + requalification battery (on the host, or any checkout of the Engine)
python -m pytest ../SerendipityFoundryEngine/tests -q

# live proofs over the wire
python test_harness/harness.py                        # 12 capabilities
python test_harness/isolation_two_experimenters.py    # 7 isolation properties
python test_harness/requalification_live.py           # RQ-A/B/C/D, DFX-2/3, H5
```

Key endpoints: `POST /v2/worlds/{wid}/experiments {commit}`, `POST /v2/worlds/{wid}/experiments/{eid}/commit`, `POST /v2/worlds/{wid}/observations {work_id,retrospective}`, `POST /v2/work/claim` (returns `claim_id`), `POST /v2/work/{id}/{heartbeat,complete,fail} {claim_id}`, `POST /v2/topology-groups`. Full reference: `SerendipityFoundryClient/docs/API.md`.

---

**Do not treat this as qualified.** It is a candidate. Attack it. The objective was not to turn your suite green — it was to build a runtime in which the obvious ways of laundering hindsight, stale execution, fresh budget, provenance, or unsupported configuration are *structurally unavailable*. If any remain reachable, that is the next repair order.

— Daedalus
