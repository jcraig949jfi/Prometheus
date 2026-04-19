# Dataset Snapshot Discipline v1

**Status:** Mandatory for any `dataset` symbol at version ≥ 2.
**Motivation:** Without this discipline, "immutable symbol versions" is a filing convention, not a reproducibility guarantee. A `dataset` symbol that pins only SQL returns different rows when the underlying database changes; two agents running the same SIGNATURE at different times get different results and there is no mechanism to detect the drift.

**Scope:** this protocol covers `dataset` symbols. `computation` symbols have a parallel purity discipline (see `computation_purity_v1.md`, pending). Together they are what make a measurement's SIGNATURE idempotent across time.

---

## The snapshot block

A dataset symbol's frontmatter carries a `snapshot` block with the following fields:

```yaml
snapshot:
  type: row_bytes_sha256              # currently the only supported type
  value: <64-hex-char sha256>         # hash of canonical row bytes
  captured_at: <ISO-8601 UTC>         # when the snapshot was computed
  n_rows_exact: <int>                 # exact row count at capture time
  n_columns: <int>                    # column count
  columns_sorted:                     # columns in alpha order (part of hash)
    - <col_a>
    - <col_b>
  canonicalization: agora_csv_jsonl_v1  # serialization spec version
  sample_note: <string>               # optional free-text for operators
  bytes_size: <int>                   # size of canonicalized bytes
```

## Canonicalization spec `agora_csv_jsonl_v1`

The hash is over the UTF-8 encoding of:

1. **Columns sorted alphabetically** — column ordering in the raw DataFrame does not affect the hash.
2. **Row order preserved** — the canonical SQL must include `ORDER BY` on deterministic columns (e.g. `ORDER BY conductor, lmfdb_label`). The snapshot depends on the row order produced by that `ORDER BY`.
3. **Header line** — tab-separated column names in alpha order.
4. **One line per row** — cells in alpha column order, tab-separated, each rendered via:
   - `float` → `repr(x)` (Python round-trip stable form)
   - `None` / `NaN` / `pd.NA` → literal string `null`
   - `bool` → `true` or `false`
   - `int` → `str(x)`
   - `str` → double-quoted with backslash, double-quote, newline, tab escaped
   - `list` / `tuple` / `ndarray` → `json.dumps(list(x), sort_keys=True, separators=(',',':'))`
   - `dict` → `json.dumps(x, sort_keys=True, separators=(',',':'))`
5. Lines joined with `\n`.
6. UTF-8 encoded.
7. `sha256` → hex.

Reference implementation: `agora/datasets/snapshot.py::canonicalize`. A second independent implementation that agrees byte-for-byte on this spec satisfies the cross-implementation requirement for snapshot idempotence.

## Capture workflow

An operator with LMFDB Postgres credentials runs:

```bash
export AGORA_PG_USER=... AGORA_PG_PASSWORD=...
python -m agora.datasets capture Q_EC_R0_D5 --note "initial v2 snapshot"
```

The command reads the canonical SQL from the symbol's MD file, executes it against the mirror, computes the snapshot block, and prints it to stdout. The operator pastes the block into the symbol's frontmatter, bumps version, and promotes via `python -m agora.symbols.push`.

## Verify workflow

```bash
python -m agora.datasets verify Q_EC_R0_D5
```

The command re-runs the canonical SQL, recomputes the hash, and compares to the promoted snapshot. Exit 0 for match, 1 for drift.

**Drift is expected and informative.** When LMFDB updates, the hash diverges. The correct response is not to silently update the snapshot — it is to promote a new dataset symbol version (e.g., `Q_EC_R0_D5@v3`) with the new snapshot. Old SIGNATUREs continue to reference the old snapshot; they remain reproducible against the pinned data if that data is archived elsewhere, and explicitly non-reproducible otherwise (the substrate records the non-reproducibility honestly).

## What a dataset symbol looks like without a snapshot

Pre-v2 dataset symbols (including the current `Q_EC_R0_D5@v1`) have no `snapshot` field. They can still be used in SIGNATUREs, but those SIGNATUREs carry an implicit `snapshot: UNPINNED` status and are not idempotent across time. They record "we ran this query on this day against LMFDB as it existed then." Useful for contemporaneous work; not reproducible after the underlying data changes.

## Relationship to SIGNATURE@v1

The SIGNATURE@v1 `dataset_spec` field currently reads like `Q_EC_R0_D5@v1`. Under snapshot discipline it extends to `Q_EC_R0_D5@v2.snapshot_<8-hex-prefix>`, carrying the snapshot reference compactly. The full snapshot is resolvable from the symbol at that version.

Full idempotent SIGNATURE example:
```json
{
  "feature_id": "F011@c1abdec43",
  "projection_ids": ["P020@c348113f3"],
  "null_spec": "NULL_BSWCD@v2[stratifier=conductor_decile,n_perms=300,seed=20260417]",
  "dataset_spec": "Q_EC_R0_D5@v2.snapshot_3f8a9b2c",
  "computation_spec": "BSWCD_IMPL@v1.sha256_e4d909c2",
  "n_samples": 559386,
  "effect_size": 0.2290,
  "z_score": 4.19,
  ...
}
```

All four "@" references are content-pinned: the operator interface, the concrete code, the dataset snapshot, and the feature/projection descriptions. Running the composition in 2030 produces byte-identical SIGNATURE iff all four resolve to the same content.

## Caveats

- Snapshot hash depends on the canonicalization version. Bumping from `agora_csv_jsonl_v1` to a future version invalidates all stored hashes; symbols would need re-snapshotting. The protocol version is explicit in the frontmatter so this is detectable.
- Floating-point row values use `repr()` which is stable on a given Python version and architecture family but can vary across radically different architectures. Current target: x86_64 + CPython 3.11+. Agents on other targets may produce different hashes for the same data and should report this as a drift.
- NULL handling assumes pandas `pd.NA` / `None` / `NaN` are equivalent (all render as `null`). SQL `NULL` comes through pandas as `NaN` for numeric columns and `None` for object columns; both canonicalize the same.
- Array-valued columns (e.g., `bad_primes` as a Postgres integer array) come through as Python lists; `json.dumps` with `sort_keys` gives deterministic output.

## Version history

- **v1** 2026-04-19 — initial protocol. Covers the mandatory baseline for `dataset` symbols at version ≥ 2. Any future bump to `agora_csv_jsonl_v2` canonicalization would be documented here with a deprecation path for v1 snapshots.
