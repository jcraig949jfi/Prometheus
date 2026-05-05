# Deep Research Report #170: Data Snapshot Ledger Design

**Target Agent:** Mnemosyne
**Date:** 2026-04-26
**Front:** Replay capsule prerequisites (Batch 9 Tier 1)
**Upstream of:** Stoa proposal `2026-04-25-aporia-replay-capsule-primitive.md`, kill-ledger v1.2 schema field `data_snapshot_id`

## 1. Problem Statement

A **data snapshot** is an immutable, point-in-time, byte-identical state of a single data source, addressable by a stable ID and verifiable by checksum. Every battery execution under two-track epistemics v1.2 must reference one or more `data_snapshot_id`s so that re-running the battery against the same IDs produces bit-identical inputs and (modulo intentional stochasticity) identical outputs.

Sources that must be snapshotted:

- **LMFDB Postgres mirror** (`ec_curves`, `ec_nfcurves`, `nf_fields`, `hmf_hecke`, `hmf_forms`, `g2c_curves`, `mf_newforms`, ~200 more tables — the `reference_lmfdb_postgres.md` inventory).
- **OEIS local mirror** (`stripped` flat file + B-files).
- **Bloom–Erdős corpus** once REQ-001 ingests it.
- **Knot tables** (HFK, Khovanov, Alexander, signature; the 12,965-knot pull).
- **Modular form tables** beyond what LMFDB exposes (Sage-computed).
- **Fungrim, A123648 anchor file, sleeping-beauty OEIS subset** (68,770 sequences).
- Any future ingest registered through `mnemosyne/ingest_priority1.py`.

**Required guarantees:** (i) immutable — once registered, content cannot mutate; (ii) checksummed — SHA-256 over a canonical serialization; (iii) replayable — `mirror_path` + `snapshot_id` recover bit-identical state on either machine; (iv) append-only ledger — entries are never deleted, only superseded; (v) GC policy — orphaned snapshots (referenced by no live candidate) eligible for cold-storage eviction after a retention window.

## 2. Literature / precedent

- **Git** content-addressed object store (commit/tree/blob hashes) — the canonical immutable-by-hash design.
- **Nix store paths** (`/nix/store/<hash>-<name>`) — immutable inputs, hash-identified, garbage-collected against live root set; nearly the model we want.
- **DataLad / DVC** — data versioning with content addressing layered on Git; precedent for ledger + mirror split.
- **LMFDB release tags** (e.g. `lmfdb-2024.x`) — coarse upstream versioning we wrap, not replace.
- **Mnemosyne `data_audit_20260415.md`** — current static inventory; the snapshot ledger is the dynamic, append-only successor.
- **Charon Lehmer-NF incident** — `charon/scripts/lehmer_spectrum_audit.py` operated on a ~0.35% sample subset whose identity was implicit; with a snapshot ID the omission would have been an explicit `snapshot_id = lehmer_subset_v0` recorded in the kill ledger and instantly diffable against the full pull.
- **`feedback_assume_wrong`** — without snapshots every kill is potentially non-replayable; the kill ledger silently corrupts as upstream data evolves.

## 3. Schema

Append-only JSONL at `mnemosyne/data_snapshots/snapshots.jsonl`. One record per snapshot:

```json
{
  "snapshot_id": "lmfdb_ec_curves_20260425_a3f1c9",
  "source": "lmfdb_ec_curves",
  "pull_timestamp": "2026-04-25T14:02:11Z",
  "checksum_sha256": "a3f1c9...e8",
  "row_count": 3824372,
  "version_tag": "lmfdb-2026.04",
  "mirror_path": "Z:/mirrors/lmfdb/ec_curves/20260425_a3f1c9.parquet",
  "byte_size": 4118293822,
  "machine_origin": "skullport",
  "superseded_by": null,
  "notes": null
}
```

`snapshot_id` = `<source>_<UTCdate>_<first6 of checksum>`. `mirror_path` is per-machine (Skullport = `Z:/mirrors/...`, SpectreX5 = `D:/mirrors/...`); `snapshot_id` is universal. Mirror data lives at `mirror_path` and is bit-identical at the snapshot moment; immutability is enforced by filesystem read-only bit + checksum verification, not by trust.

## 4. API design

`mnemosyne/data_snapshots/api.py` exposes:

- `register_snapshot(source: str, pull_timestamp: datetime, mirror_path: Path, version_tag: str | None = None) -> str` — computes checksum, row count (where defined), appends ledger entry, sets `mirror_path` read-only, returns `snapshot_id`.
- `get_snapshot(snapshot_id: str) -> SnapshotMetadata` — O(log n) via lazy index sidecar `snapshots.idx`.
- `verify_snapshot(snapshot_id: str) -> Literal["ok", "corrupt", "missing"]` — re-hashes `mirror_path` and compares.
- `latest_for(source: str) -> str` — most recent non-superseded snapshot.
- `list_for(source: str, since: datetime | None = None, until: datetime | None = None) -> list[str]`.
- `supersede(old_id: str, new_id: str) -> None` — appends a superseding record; does not mutate the old one.

The replay-capsule primitive (`stoa/proposals/2026-04-25-aporia-replay-capsule-primitive.md`) consumes `get_snapshot` + `verify_snapshot`; refusal to replay on `corrupt` or `missing` is mandatory.

## 5. Operational policy

- **When to snapshot:** every full pull; every checksum-changing partial update; on-demand at the start of any battery run that lacks a same-day snapshot.
- **Retention:** any snapshot referenced by a non-`re_killed` candidate in `aporia/kill_ledger/*.jsonl` is immutable forever. Orphaned snapshots may be cold-archived (mirror moved to `Z:\archive\`, ledger entry retained) after a 90-day retention window — TBD by Mnemosyne.
- **Cross-machine coordination:** Skullport (M1) and SpectreX5 (M2) share `snapshots.jsonl` via git (`mnemosyne/data_snapshots/snapshots.jsonl` is committed; mirror payloads are not). On first reference of a foreign `snapshot_id`, the local machine pulls the payload from `Z:\` (shared) and verifies checksum before use. Per `feedback_two_machine_sync`: push often, pull before work.

## 6. Falsification / acceptance tests

- Pull LMFDB EC twice 24h apart; assert two distinct `snapshot_id`s and distinct `checksum_sha256` (assuming any upstream change) — and equal IDs/checksums if upstream is byte-stable.
- Replay an archived battery (e.g. the H15 run in `aporia/mathematics/h15_results.json`) against its recorded `snapshot_id`; assert deterministic re-execution at the result-hash level.
- Flip one byte in a mirror file; assert `verify_snapshot` returns `corrupt`.
- Reference a non-existent `snapshot_id` from a fake replay capsule; assert refusal.

## 7. Budget

~1 day Mnemosyne. Schema design ~2h, ledger initialization + first snapshots of existing mirrors (LMFDB EC, LMFDB NF, OEIS, knot tables) ~3h, API implementation ~3h, write-up ~1h. Backfill targets: LMFDB EC mirror, LMFDB NF mirror, OEIS pull, knot tables, plus REQ-001 (Bloom–Erdős) on ingestion. Once landed, the kill-ledger `data_snapshot_id` field becomes enforceable and the replay-capsule primitive is unblocked.

**Word count: 798**
