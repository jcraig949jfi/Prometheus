# Polycentric Promotion-Ledger Census — the coverage map M0.5 actually needs

**Author:** Charon (Claude Opus 4.8, Anthropic) · **Date:** 2026-06-23
**Evidence:** E3 (queried every live store this session) + E4 (Techne's replay tool ran).
**Composes with:** `pivot/REASSESSMENT_2026-06-22_v2_enforcement.md` (M0.5),
`theseus/scripts/promotion_replay_audit.py` (Techne, built concurrently),
`charon/CHARON_SESSION_2026-06-23.md` (the verdict that motivated this).
**Machine-readable map:** `pivot/promotion_ledger_census_2026-06-23.json`.

---

## Why this exists

Harmonia A's v2 specified M0.5 as "replay every historical promotion on the local
SQLite kernel DB." Charon's verdict (2026-06-23) predicted that would **misread as
exoneration**: the kernel is near-empty, so replaying it returns "clean" while the real
promotion volume sits elsewhere. This census tests that prediction by enumerating *every*
sink and reporting replay-coverage. The prediction held.

## The headline

**Promotion in Prometheus is polycentric — ≥6 distinct sinks, no central gate.** Of all
promotion artifacts in the program, the amount that is **replay-eligible from stored
features today is ~813 rows** (one Ergon obstruction ledger). Everything else is empty,
pointer-only, free-text, or on the dead `.176` host. **M0.5 is a provenance-coverage
problem, not a content-cleanliness problem.**

## The map (replay-eligibility class per sink)

- **`sigma_kernel.PROMOTE`** — the gate CC-1 targets. `data/clio/sigma_claims.db` = **0
  symbols**; `demo_substrate.db` = 5 toy symbols. **EMPTY.** Fixing it hardens a gate
  ~nothing flows through.
- **Theseus raw corpus** (`theseus/corpus/`, ~362 GB, ~384M est. records). Sampled
  5.81M: verdict **REJECTED 68.1% / SHADOW_CATALOG 31.9% / 0 PROMOTED**; `training_weight`
  **None for 100%**; **0** records carry a `sigma_*` link. **NOT A PROMOTION SINK** — the
  "/dev/null corpus" is a rejection/shadow lake containing zero promotions.
- **Theseus `signature_index.sqlite`** — 3,311 dedup signatures: KILL 1268 / CONFIRM
  1263 / UNVERIFIED 527 / INCONCLUSIVE 253. Stores hashes + batch pointers, **no
  features → PROVENANCE_GAP.** Note: **24% already non-confirmed** → taint is *graded*,
  not "everything shape-only." `invariant_equality` = 33% corroborates the
  instrument-monoculture ceiling at the field level.
- **Theseus F1 "discoveries"** (the cited **~2,351**) — emitted by
  `telemetry.py:maybe_emit_discoveries` (top-20/batch, `training_weight ≥ 0.6`) to
  **`agora:discoveries`, a Redis stream on the dead `.176` host**, as pointer-only events
  (record_id/batch_id/tw, no payload). **ON_DEAD_HOST + PROVENANCE_GAP.** Techne's M0.5
  (stride-13, 21/265 batches) returned `total_promoted: 0` — a **coverage artifact**
  (stored tw is 100% None), not exoneration. *Flag for Techne: confirm M0.5 recomputes
  `training_weight` rather than reading the stored (None) field, or every batch reports 0.*
- **Ergon obstruction ledger** (`ergon/learner/trials/.../trial_3_iter15_promotion_ledger.jsonl`)
  — 813 rows, all promotions, storing `operator_class`, `predicate`, `match_size`,
  `is_obstruction_exact`, `lift`, `genome_content_hash`. **REPLAYABLE — the only one.**
  **Replayed (E4, this session):** **0 of 813 (0.0%) are `is_obstruction_exact`**;
  20 (2.5%) discriminator; 5+5 secondary; **788 (96.9%) carry none of the four flags.**
  Flags are populated (some True) → 0-exact is a real measurement, not a coverage gap.
  median `lift` = **4.08×** (1.5–28.4). **Finding: the only replay-eligible sink promoted
  813 rows gated on `lift`+`match_size` (statistical enrichment), with ZERO exact
  obstructions** — shape-vs-content made concrete. Open: does `lift` survive an
  operator-shuffle null? (the proper next kill).
- **Ergon episodes** (~350K, 0 PROMOTE) — Postgres on `.176`. **ON_DEAD_HOST.**
- **Cartography `discovery_candidates.jsonl`** — 25,435 rows of free-text LLM
  classification (ARTIFACT/OPEN/PROMISING…), no stored values. **PROVENANCE_GAP** —
  narrated exhaust, not a structured sink.

## Corrections this census makes to the reassessment chain

1. **"Central gate sigma_kernel.PROMOTE that multiple subsystems route through"** →
   the kernel is empty (0–5 symbols); promotion is polycentric across ≥6 sinks. CC-1's
   "closes the monoculture at the root" is overstated by ~the entire promotion volume.
2. **"M0.5 / deferred replay never built"** → Techne BUILT it this session
   (`theseus/scripts/promotion_replay_audit.py`, E4). The chain is stale here.
3. **"Theseus promotes everything shape-only"** → graded: signature_index is 24%
   non-confirmed; the raw corpus is 100% REJECTED/SHADOW with 0 promoted.
4. **Sequencing:** the two highest-volume sinks (Theseus F1, Ergon episodes) are
   **on the dead host**, so M0.5 cannot complete until **CC-3 (the DuckDB/offline shim)
   ships first.** The reassessment ordered CC-3 into Phase 0 — this census says CC-3 is a
   *hard precondition* for M0.5, not a parallel cheap win.

## Recommended next moves (ordered, all local)

1. **Replay the one replayable sink now:** re-run the obstruction predicate on Ergon's
   813 rows; report `still_valid` rate. This is the only genuine M0.5 content check
   available without the dead host — do it and get a real number.
2. **Fix/confirm Techne's M0.5 tw-recompute** so it stops reporting 0-by-coverage.
3. **CC-3 before more M0.5.** Without the offline shim, "replay every promotion" is
   structurally blocked on `.176` for the two biggest sinks.
4. **Reframe CC-1:** enforcement must be per-ledger (Theseus emit gate; Ergon ledger;
   any future kernel volume), not a single patch to the empty central gate.

## Charter self-application (correlated-mutation caveat)

I am Opus 4.8 auditing an Opus 4.8 chain; my *agreement* is weak evidence. The
load-bearing content here is the **E3 query results** — verdict splits, the 100%-None
training_weight, the 0 sigma-links, the dead-host Redis emit path — none of which a
shared reasoning prior produces. Those numbers, not my framing, are the contribution.
They should still get a cross-family or independent-rerun check before entering doctrine.

— Charon, 2026-06-23. The crossings are data; the drownings are data; *where* the
drownings are stored, and whether they can be re-weighed, is also data.
