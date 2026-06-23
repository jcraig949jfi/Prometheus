# RESUME — Harmonia E, Proposal D (Failure-Primitive Atlas)

**Last session:** 2026-06-15 (resume; journal `SESSION_JOURNAL_E_20260615.md`).
**Status:** Atlas shipped 2026-06-10. 2026-06-15: **FP-003 → coordinate_invariant**
(first top-tier primitive; Apollo escrow resolved as `expressiveness_ceiling`,
executing-lens confirmed; commits `5531d4f1`, `4efd38f7`). **Spend limit has
RESET** — cloud fan-out unblocked.

## Next up (priority)
1. **FP-004 graduation (pending→proven):** EXECUTE `detect_degenerate_field_flatline`
   on real data for the 3 disjoint lineages (harmonia rank-1 killvectors;
   apollo `llm_alive=0` — the OLD May run, not the R2 log; noesis depth-2
   confidence sigs in duckdb). Discount Polyhymnia (imports the
   `agents/_shared/self_improving.py` mixin → contaminated). 3 fires =
   legitimate coordinate_invariant.
2. Re-run the truncated Stage-3 hunt (~22 agents + critic) — spend available.
3. FP-003 subclass-discriminator probe (region_empty STOP vs
   expressiveness_ceiling GROW — can the detector be made to over-lump?).

## Original handoff (2026-06-10) below — partially superseded by the above.

## One-paragraph state
The cross-agent Failure-Primitive Atlas is live: 4 FPs with working detectors
(FP-001 baseline_costume, FP-002 opaque_kill_black_hole, FP-003
bounded_menu_wall, FP-004 degenerate_field_flatline), a predictive void-map, and
a 90-shape candidate shelf from a fleet-wide generative hunt. FP-003 passed its
independence audit (found Techne≡Theseus is ONE observation; Polyhymnia is
genuinely independent → surviving_candidate, not coordinate-invariant). The
generative hunt was **truncated** by the spend limit (≈22 agents + the
completeness critic never ran). Nothing is mid-flight; no running processes.

## Files (all `D:\Prometheus\...`)
- `harmonia/primitives/failure_primitives.py` — registry + 4 live detectors + `validate_atlas()`. Run it to self-test.
- `harmonia/primitives/fp_void_map.py` — predictive tensor + `void_schedule()` + `predict_fps()`.
- `harmonia/memory/architecture/failure_primitive_atlas.md` — human atlas (FP-001..004 + candidate shelf section).
- `harmonia/memory/architecture/fp_candidate_shelf_20260610.{json,md}` — 90 hunt shapes, conservative independence counts.
- `harmonia/memory/architecture/fp_void_schedule_20260610.json` — 58 ranked audits.
- `harmonia/experiments/fp_void_audits_20260610.{py,json}` — first cross-agent detector runs (Apollo FP-003 FIRED).
- `harmonia/experiments/consolidate_hunt_20260610.py` + `hunt_raw_20260610.json` — hunt output + consolidator.
- `roles/Harmonia/SESSION_JOURNAL_E_20260610.md` — full journal.

## Resume checklist (priority order)
1. **When spend limit resets:** re-run the truncated hunt (rounds 2/3 + completeness critic). ~22 agents never mined: ignis, stoa, sigma_kernel, cartography, falsification, audit, ~16 small agents, both modality lenses.
2. **Lineage-audit the top candidate shapes** (FP-003-style 4-probe Workflow) before any graduate: `narrative_ledger_divergence`, `production_into_vacuum`, `uncalibrated_instrument_floor`, `hollow_artifact_discharge`. Lift FP-004 pending→proven the same way.
3. **Apollo cause audit** — resolve the FP-003 escrow anchor (expressiveness-ceiling vs Goodhart).
4. **Integration duty** — wire Harmonia A/E/B real detector outputs into FP-001/002 as they land.
5. **Blocked:** FP-002 × charon/theseus void cells need Postgres @192.168.1.176 (timed out 2026-06-10).

## Verify it still works
```
cd D:\Prometheus
set PYTHONPATH=D:\Prometheus
python harmonia\primitives\failure_primitives.py      # expect: 4 FPs, atlas validation CLEAN
python harmonia\primitives\fp_void_map.py             # expect: cell-state counts + void schedule
```

## Doctrine that bound this work
SHADOWS_ON_WALL (every measurement a shadow; invariance = survives lineage
change). Independence is the whole game: ≥3 code-disjoint lineages for the
coordinate-invariant tier, and shared authorship/doctrine does NOT count as
independence (Techne≡Theseus was the trap). Anti-taxonomy-theater: shapes
graduate only with a detector that FIRES on agents that didn't author them.
