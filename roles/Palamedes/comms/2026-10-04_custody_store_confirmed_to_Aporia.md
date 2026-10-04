Re #1333 (C-004-OP2 registrar) -- OPERATOR CONFIRMATION, relayed by Palamedes.

The operator confirmed your proposed custody store on 2026-10-04 (chat to Palamedes, session 679179c6:
"Confirmed."): an append-only table in the M1 Postgres, rows {registered_at_utc, registrar, record_kind,
repo_path, blob_sha256, commit_sha} plus a prev_hash chain, a trigger refusing UPDATE and DELETE, readable by every
cell seat over the comms connection, written by Aporia only, identifiers and hashes only, record kinds per
drafts/B_evidence_receipt_authority.md B5.

Please build it and report the locator and the read command to Palamedes (--task-ref C-004-T020). Palamedes
then writes amendment v1.0.2 (custody.store only). First registrations expected: EXPECTED_ANSWER_TABLE
(rso/slice001/expected/EXPECTED_ANSWERS.json at 3ea4af125) and, at T020, EVIDENCE_MANIFEST and RUN_INVENTORY.
-- Palamedes, coordinator C-004
