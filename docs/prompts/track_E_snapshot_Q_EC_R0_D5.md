# Track E — Capture First Dataset Snapshot (Q_EC_R0_D5)

**Role:** Snapshot Capturer (single-purpose, ~5 minutes of work)
**Delegated:** not yet
**Status:** ready to claim
**Prerequisites:** AGORA_PG_USER and AGORA_PG_PASSWORD env vars; psycopg2 installed; repo pulled to `c9d2276e` or later (needs `agora/datasets` module)
**Expected deliverables:**
  - `Q_EC_R0_D5@v2` promoted to Redis with a real snapshot block
  - A commit containing the v2 MD with the captured snapshot
  - A `SNAPSHOT_CAPTURED` sync message with the hash prefix

---

## Paste-ready prompt

```
You are [whichever session has LMFDB Postgres credentials].
Role: Snapshot Capturer. Single-purpose, ~5 minutes. You're capturing
the first content-addressed snapshot for Q_EC_R0_D5, promoting it
as v2 of the dataset symbol. This is the first operationalization of
the idempotence mandate (see docs/long_term_architecture.md §2.1).

Working directory: Prometheus clone. Pull latest first.

Read first:
  docs/long_term_architecture.md  §2.1  — idempotence + purity
  harmonia/memory/symbols/protocols/dataset_snapshot_v1.md
  harmonia/memory/symbols/Q_EC_R0_D5.md  — the v1 symbol to extend
  agora/datasets/snapshot.py  — canonicalization spec and hashing

Prerequisites — verify before proceeding:
  export AGORA_PG_HOST=192.168.1.176
  export AGORA_PG_PORT=5432
  export AGORA_PG_DB=prometheus_sci
  export AGORA_PG_USER=<your user>
  export AGORA_PG_PASSWORD=<your password>
  python -c "import psycopg2; import pandas; print('ok')"

Steps:

1. Capture the snapshot:
     python -m agora.datasets capture Q_EC_R0_D5 --note "v2 initial"
   The output is a YAML-style block starting "snapshot:" with the sha256,
   captured_at timestamp, row count, and canonicalization version.

2. Construct Q_EC_R0_D5@v2 by copying v1's MD and editing:
     - version: 2
     - version_timestamp: <current UTC ISO-8601>
     - immutable: true
     - previous_version: 1
     - v2_bump_by: <your session>@<current commit hash>
     - references: update Q_EC_R0_D5 references to @v1 where needed
     - Add the captured snapshot block to frontmatter (paste output of step 1)
     - redis_key: symbols:Q_EC_R0_D5:v2:def
     - Append a "What v2 changes" section to the body documenting the
       snapshot capture and the canonicalization spec used
     - Update Version history at bottom

3. Validate by running push_symbol in dry mode (doesn't exist yet, so
   just import the push script and call validation directly):
     python -c "
     from agora.symbols.parse import load_symbol
     from agora.symbols.push import _validate
     sym = load_symbol('harmonia/memory/symbols/Q_EC_R0_D5.md')
     _validate(sym, 'harmonia/memory/symbols/Q_EC_R0_D5.md')
     print('schema valid')
     "

4. Promote to Redis:
     python -m agora.symbols.push harmonia/memory/symbols/Q_EC_R0_D5.md
   Expected output: "pushed_new_version  Q_EC_R0_D5@v2 (Q_EC_R0_D5.md)"

5. Verify resolver sees both v1 and v2:
     python -c "
     from agora.symbols import resolve, all_versions
     print('versions:', all_versions('Q_EC_R0_D5'))
     v2 = resolve('Q_EC_R0_D5', version=2)
     print('v2 snapshot:', v2.get('sections', {}).get('snapshot') or 'in frontmatter')
     "

6. Commit:
     git add harmonia/memory/symbols/Q_EC_R0_D5.md
     git commit -m "Q_EC_R0_D5@v2 promoted with snapshot <first-8-hex>"
     git push origin main

7. Sync broadcast:
     agora.xadd SNAPSHOT_CAPTURED with:
       symbol: Q_EC_R0_D5@v2
       snapshot_hash: <full 64-hex>
       snapshot_captured_at: <ISO-8601>
       n_rows_exact: <int>
       canonicalization: agora_csv_jsonl_v1

Constraints:
  - Do NOT modify Q_EC_R0_D5@v1 in the catalog — v1 remains the
    pre-snapshot reference for existing SIGNATUREs
  - Do NOT modify any computation that already referenced Q_EC_R0_D5@v1
  - Future measurements that want idempotent SIGNATUREs should reference
    Q_EC_R0_D5@v2; legacy ones continue to reference @v1 without
    retroactive snapshot attribution
  - If the SQL fails or returns zero rows, STOP and post a QUESTION on
    agora:harmonia_sync rather than promoting an empty snapshot

Commit prefix: "Snapshot capturer:"

Charter context: this is the first dataset symbol to carry a content-
addressable snapshot. It is the first operational step toward making
SIGNATURE tuples reproducible across time and machine. If the capture
succeeds cleanly, the same pattern applies to every future dataset
symbol — the plumbing is reusable.
```

---

## Background motivation

v2.1 of `docs/long_term_architecture.md` established that idempotence of SIGNATURE tuples requires three things simultaneously:
1. Pure computation (to be addressed via the `computation` symbol type)
2. Content-pinned inputs (this track)
3. Composition-as-symbol

Capturing a real snapshot for Q_EC_R0_D5 operationalizes (2) for the most-used dataset in the tensor. Once this pattern works for one symbol, it's mechanical for every future dataset.

Notably: existing measurements are NOT retroactively made idempotent. They referenced Q_EC_R0_D5@v1 which had no snapshot, so those SIGNATUREs remain pre-snapshot-discipline. New work builds on @v2 going forward. This is the correct boundary — we do not rewrite history silently.

The capture is a ~5 minute task on a machine with LMFDB Postgres credentials. The reason it's a separate track rather than inline work is that this host (the drafting session) does not have Postgres credentials configured.
