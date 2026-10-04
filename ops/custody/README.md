# Custody registry (C-004-OP2 registrar store)

- **Store (locator):** `postgresql://<EW_DB_HOST=192.168.1.202>:5432/prometheus_fire#custody.registry`. Reach it
  through the comms connection; seats off M1 set `EW_DB_HOST=192.168.1.202`.
- **Roles:** registrar Aporia; keeper/authority the operator (C-004-OP2). Spec: rso/slice001/contract/drafts/B_evidence_receipt_authority.md B5.
- **Commands:**
  - Read: `python -m ops.custody.registry read [--kind KIND] [--json]`. Any seat.
  - Verify: `python -m ops.custody.registry verify`. Any seat. Exit 0 ok, 1 chain break, 3 STORE_UNREACHABLE.
  - Register: `python -m ops.custody.registry register --kind KIND --path P --commit SHA --registrar Aporia`.
    Registrar only. The blob sha256 is computed from `git show SHA:P`, and the commit must be an ancestor of
    origin/main.
- **Integrity:**
  - The server sets registered_at_utc, so rows cannot be backdated.
  - The server computes prev_hash/row_hash chain links, so callers cannot supply them.
  - UPDATE, DELETE and TRUNCATE raise.
  - Controls were run on a throwaway schema: update, delete and truncate refused; bad registrar and bad kind refused;
    the chain recomputes; tampering with triggers disabled was detected at the edited row.
- **Residual:** all seats share one superuser, which could disable the triggers. Write exclusivity is therefore
  procedural, and tampering is detected rather than prevented. The chain head is published on comms at every
  registration, so a rewritten history disagrees with the published heads. Custody qualifies byte identity since
  registration only (B5.4).
