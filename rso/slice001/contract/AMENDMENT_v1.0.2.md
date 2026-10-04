# S1 contract amendment v1.0.2 (custody store locator)

Amends contract v1.0.1. STATUS: ADOPTED; contract.json is updated to 1.0.2 only when C-004-T021
integrates (the S2 suite reads the live custody.store and evidence.py has no store reader yet, so setting the field
before T021 turns test_unset_store_is_keeper_row_missing into STORE_UNREACHABLE). Written by Palamedes[harry1-679179c6], 2026-10-04. Reserved by CONTRACT.md R3 (renumbered
in AMENDMENT_v1.0.1.md): one field, custody.store, plus the residual it carries. Nothing else changes.

Source: Aporia (registrar, C-004-OP2) comms #1353, store design confirmed by the operator 2026-10-04 (relayed
#1347); code ops/custody/ at 497b81a4e.

W1  custody.store = postgresql://192.168.1.202:5432/prometheus_fire#custody.registry, reached through the comms
    connection (EW_DB_HOST=192.168.1.202 off M1). Read: `python -m ops.custody.registry read [--kind K] [--json]`.
    Verify: `python -m ops.custody.registry verify` (exit 0 ok, 1 chain break, 3 unreachable). The consumer maps
    exit 3 to STORE_UNREACHABLE and exit 1 to a custody FAIL reason ROW_CHAIN_BROKEN; neither is ever a pass.
    Row fields: row_id, registered_at_utc (server clock), registrar, record_kind, repo_path, blob_sha256
    (computed by the registrar from the committed blob), commit_sha, campaign, prev_hash, row_hash. These are the
    B5.1 D2-1 fields plus the chain.

W2  custody.independence_caveat gains Aporia's stated residual: every seat connects as the same Postgres
    superuser, which can disable the refusal triggers, so write exclusivity is procedural; tampering is DETECTED
    (chain recompute plus heads Aporia publishes on comms) rather than prevented. Custody QUALIFIED therefore means
    "bytes registered at the recorded time, chain intact at check time", within B5.4, and never more.

Coordinator check at amendment time: `verify` -> chain_ok true, 1 row, head
0c5764a79bcf10a4850ebda5fd9f4dcbfbf24fe27f7cf3f6022ebdb211872b2b; row 1 EXPECTED_ANSWER_TABLE blob
8f5b8631...072aec3 equals the sha256 of rso/slice001/expected/EXPECTED_ANSWERS.json at 3ea4af125 computed
independently by Palamedes.

V8 consequence: the real T020 run is no longer BLOCKED on the locator. It still needs EVIDENCE_MANIFEST and
RUN_INVENTORY rows registered (path + commit on main sent to Aporia) before the consumer's first check.
