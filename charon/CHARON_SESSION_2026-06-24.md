# Charon Session — 2026-06-24

## 1. PARKED (James: "document that, we'll come back to it")

The **shared cross-component value-score** thread is parked, not dropped. Captured in
`pivot/REASSESSMENT_2026-06-23_charon_third_perspective.md` (§4 + §6). One-line state:

> The monoculture is in the VALUE FUNCTION — every component scores "survived MY gate"
> (binary, local, incomparable). The proposed coordination substrate is one shared
> graded `value(output) = navigability + null-survival + downstream-delta` every
> component reports into, making monoculture visible as clustering in value-space and
> letting the breadth James wants be *tuned and expanded* rather than pruned. Gated
> behind the cheap **navigability pre-test** (kill_vector is 0% populated — the navigable
> object was never computed) and a **right-axis null on the 0.725-bit kill-MI**.

Resume points when we return: (a) right-null the 0.725-bit MI; (b) compute `kill_vector`
on a corpus slice + run the 4-criteria navigability gate (first real KillEmbedding/CC-6
piece); (c) draft the shared value-score spec as a cross-agent contract. Awaiting
Aporia's fourth perspective for joint triage. **No work to be done on this now.**

## 2. DONE — DuckDB code-side retirement (read path)

Repointed Charon's source tree off `charon.duckdb` onto `prometheus_fire.charon_duckdb`
(Postgres). Full report: `charon/DUCKDB_REPOINT_2026-06-24.md`. Summary:
- New `charon/src/db.py` — DuckDB-compatible psycopg2 facade; aliased as `duckdb` at call
  sites so the repoint is a one-line import swap per file.
- 18 read files repointed; 6 frozen writers retired (guarded); 4 builders flagged for
  owner sign-off (guarded — they write tables already migrated).
- Validated exact vs the DuckDB oracle: all 14 table counts, group-bys, length-24 array
  fidelity (0.0 diff), and two entry points end-to-end (zero_battery 120,649 /
  research_battery 14,751 — byte-identical checksums).
- `charon.duckdb` left frozen (no-delete). Granted `lmfdb` read on `charon_duckdb`;
  installed psycopg2-binary.

**Standing recommendation for next session:** the 4 flagged builders (build_graph,
disagreement_atlas, embed, genus2_crossing) need an owner decision before any re-run —
rewrite their writes against canonical Postgres tables (xref/zeros/analysis), not the
charon_duckdb archive.

— Charon, 2026-06-24
