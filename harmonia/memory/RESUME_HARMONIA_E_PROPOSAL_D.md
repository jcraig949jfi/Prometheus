# RESUME — Harmonia E, Proposal D (Failure-Primitive Atlas)

**Last session:** 2026-06-10. **Status:** Proposal D shipped (all 5 stages);
2 follow-ups blocked on the Anthropic monthly **spend limit**.

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
