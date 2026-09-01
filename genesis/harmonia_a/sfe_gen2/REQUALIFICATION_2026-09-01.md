# GEN-2 REQUALIFICATION — 2026-09-01 (appended to GEN2_QUALIFICATION_PACKET)

Candidate: engine_source_hash sha256:e367e791c10080decc8ac8152c82fde61b
426682a9bc298403f0ccc970f9ed1a, source_commit ec4d35a1, API 2.1.0, schema 2
(migrated in place, ledgers verified per handoff), repo commit f9dd6ed88.
Protocol per packet s10-11: fixes + regression tests inspected
(tests/test_sfe_requalification.py, 506 lines, covers D1/D2/H1-H6/DFX-3/4),
my repros rerun, one nearby bypass per fix attempted.

## Rerun + bypass table (all live against the deployed build)
| probe | result |
|---|---|
| R1a DFX-1 exact repro (exp->obs->late pred->bind) | 409 prediction_ordering_error — REJECTED |
| R1b retrospective=true | recorded; events carry prospective flag + evidence_class |
| R1c BYPASS: post-commit pred, NO prior observation | 409 — window closes at COMMIT, stronger than the original ask |
| R1d BYPASS: observation on uncommitted experiment | 409 invalid_transition |
| R1e legit pre-commit prediction | bound, prospective: 1 on CLAIM event |
| R2a third commit on limit-2 | 409 budget_exhausted; consumed=2; debit AT commit |
| R2b re-commit | idempotent (already_committed: true), no double charge |
| R2c blocked commit leaves nothing executable | claim returns null |
| H3 BYPASS: fork-mint budget | child commit blocked by lineage root |
| R3 release identity | hash+commit on /v2/version, world status.engine, and stamped in EXPERIMENT_COMMITTED payloads (build-derived, not attestation) |
| R4a/b/c nested fail-closed | 422 / 422 / 422 (sneaky key, bad enforcement, bogus info_kind) |
| H1a/b/c lease fencing | claim_id required (422), wrong id conflict (409), correct exactly-once |
| H4 evidence authority | fabricated work_id 422; real work_id -> ENGINE_WORK_RESULT |
| H5 fabricated topology group | inert at create; 403 access_denied at the actual crossing |
| R5 duplicate binding of same prospective pred | still silently accepted (claims idempotent at hypothesis level) — REMAINING AMBIGUITY, P3 |

## Gate re-score
G1 PASS · G2 PASS · G3 PASS · G4 PASS · G5 PASS · G6 PASS (commit
idempotent + fencing) · G7 PASS · G8 PASS (body+event stamping; a
per-response header remains a nicety, P3) · G9 PASS · G10 PASS.

## VERDICT: QUALIFIED_WITH_DECLARED_LIMITATIONS

Declared limitations carried into any campaign freeze:
L1 duplicate pred-binding semantics undocumented (R5);
L2 no per-response release header (identity via version/status/commit
   events — sufficient, less convenient);
L3 no request-identity idempotency on non-commit POSTs (commit itself IS
   idempotent, which covers the budgeted action);
L4 no amendment/supersession records (pure immutability);
L5 no replay engine (declared);
L6 evidence_class ENGINE_WORK_RESULT attests engine-verified completion of
   MY worker's result, not third-party compute;
L7 freeform fields (spec / interventions / meta-minus-info_kind) are open
   by documented design — estimand-bearing content in them is client
   responsibility.

## FROZEN QUALIFIED RELEASE (the approved gen-2 control plane)
    engine_source_hash: sha256:e367e791c10080decc8ac8152c82fde61b426682a9bc298403f0ccc970f9ed1a
    source_commit:      ec4d35a1cb34a8138775ab170cb723d1062e0a3c
    api: 2.1.0   schema: 2
    client: sfclient @ repo commit f9dd6ed88
    qualification: plan 5a82d3c2d; original battery bd1488d98; this rerun
    date: 2026-09-01
Campaigns pin engine_source_hash via GET /v2/version at start and verify
it in EXPERIMENT_COMMITTED events. A mid-campaign hash change = stop,
classify, requalify, new freeze.
