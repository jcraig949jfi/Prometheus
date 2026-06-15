# Harmonia E Session Journal — 2026-06-10

**Instance:** Harmonia_M2_E (5th Harmonia, ULTRA mode).
**Charge:** Proposal D — the Cross-Agent Failure-Primitive Atlas, scoped by
James as the program's **meta-instrument**: predictive (forecasts which failure
primitives a new agent will hit) + generative (hunts for undiscovered
primitives across the fleet), not a prose graveyard.

## What shipped

### Stage 1 — thin registry (live)
- `harmonia/primitives/failure_primitives.py` — schema (`FailurePrimitive`,
  `AnchorCase` with a `lineage` field + `escrow` flag), three live detectors,
  query API, `validate_atlas()` (MD↔registry cross-check, ships with the doc
  per `feedback_validators_ship_with_docs`). Admission gate rejects verdict-line
  signatures mechanically.
- `harmonia/memory/architecture/failure_primitive_atlas.md` — human layer.
- Seeds FP-001 `baseline_costume` (delegates to the frozen Proposal A
  `costume_check`), FP-002 `opaque_kill_black_hole`, FP-003 `bounded_menu_wall`.
- Self-test green: detectors fire + don't-fire + downgrade paths, verdict-line
  rejection, tier ruthlessness, atlas validation CLEAN.

### Stage 2 — FP-003 independence proof (the load-bearing falsifier)
4-probe Workflow lineage audit (`wf_d6750b0d-cba`). Rulings:
- **Techne ≡ Theseus is ONE observation, not two.** Techne is the operator
  role of the Theseus substrate; one fire ledger (#1–#33 in theseus BATCH_LOG,
  #34–#236 in the Techne SUBSTRATE_FIRE_LOG). The "Fire #234 / 90 zero-promoted"
  wall and the calibration_v3 knot×EC autopsy are the same loop viewed twice.
  Counting them separately would have been a silent double-count — exactly the
  failure the registry's own lineage rule forbids.
- **Polyhymnia IS independent.** Its daemon shell descends from the Aporia
  agents-swarm template (Hypatia/Atalanta/Pheme/Talos), not Techne/Theseus;
  tensor framework standalone (credited ChatGPT-cross-frontier + James, founding
  commit `38e0ca5e`); zero cross-imports; its scour does not even walk `techne/`.
  Promotion machinery shares no symbols.
- **Heterogeneous causes, one shape.** Theseus = `region_empty` (menu fully
  expresses a genuinely empty region; calibration v3 proved 0/96 promote under
  the unbiased a1 sampler). Polyhymnia = `source_saturated` (single scour
  exhausted its *.py walk; 280 ticks/236 null; absorbing approval-gate state,
  163 dup tickets). Different mechanisms converging on the same observable
  *strengthens* shape-level invariance.
- **Honest residual contamination logged:** `feedback_gen_30_wall` (James's C#
  gen-30 stall) PREDATES both walls and is hard-coded in
  `agents/_shared/self_improving.py`'s docstring, which Polyhymnia runs. Both
  post-mortems were written by authors who knew the predicted shape → the
  diagnosis *language* is contaminated. The ruling rests on the
  narrative-independent event counters (promotion/null-tick series).
- **Verdict: FP-003 = surviving_candidate** (2 proven-independent lineages).
  A 3rd anchor (Apollo) is held in `escrow` — see below.

### Stage 3 — generative hunt (ran; truncated by spend limit)
Loop-until-dry Workflow (`wf_1c1c4ce4-036`): 27 agents, 3 rounds, **160 raw
candidates in round 1**, 90 shapes after dedup; `terminated_dry=True`.
- **⚠ TRUNCATED:** 9 round-2/3 miners + the completeness critic FAILED on the
  Anthropic monthly spend limit (ignis, stoa, sigma_kernel, cartography,
  falsification, audit, ~16 small agents, both modality lenses). `dry=True`
  counted those failed rounds as empty — **coverage is NOT exhaustive.** Re-run
  owed when the limit resets.
- Output persisted: `harmonia/experiments/hunt_raw_20260610.json` (verbatim,
  3.2M-token result), consolidated to a **candidate shelf**
  (`harmonia/memory/architecture/fp_candidate_shelf_20260610.{json,md}`) with
  conservative independence counts after applying the Stage-2 Techne≡Theseus
  collapse (5 shapes' counts dropped).
- After collapse: 13 coordinate-invariant *candidates* (≥3 independent
  lineages), 17 surviving (2), 60 shadows (1). None auto-promoted —
  per the anti-gravity-well guard, a shape graduates only with a real detector
  + a lineage audit.

### Stage 4 — predictive void map
`harmonia/primitives/fp_void_map.py` — the atlas as a sparse tensor
(failure-shape × agent × detector × mitigation); design-class model predicts
liability; voids = cells where a detector should fire but never ran.
- Schedule emitted: `harmonia/memory/architecture/fp_void_schedule_20260610.json`
  (58 audits, ranked; 4 with local data first; 2 BLOCKED on Postgres
  unreachable).
- **First live cross-agent detector firing:** Apollo Branch-C, FP-003 — r1
  49/49 and r2 480/480 gens with zero `best_acc` improvement under a fixed op
  menu while search stayed alive (`mutation_viability=1.0`, `llm_used>0`).
  Recorded as an **escrow** anchor (cause unattributed: expressiveness ceiling
  vs Goodhart — Apollo-side cause audit owed). Audit script:
  `harmonia/experiments/fp_void_audits_20260610.py` →
  `..._20260610.json` (8 cells; Ergon 5000-gen run RUN_CLEAN; Icarus
  RUN_INSUFFICIENT).
- **Detector input-contract bug found & fixed by the first live use:**
  `detect_bounded_menu_wall` false-positived on Apollo's MAP-Elites cell-fill
  counts (saturate at capacity by design). Fixed: the caller must pass honest
  promotions (within-cell fitness improvements); documented in the contract.
- **First prediction MISS, kept as calibration:** the void map initially
  predicted FP-003 for hypatia/atalanta/pheme/talos (siblings of Polyhymnia).
  Live check: they share only the daemon SHELL, not the self-improving
  adaptation-menu mixin (0 stub-menu matches; Polyhymnia was the registry's
  only adopter). Corrected their design classes; logged the miss.

### FP-004 — first shape graduated from the hunt
`degenerate_field_flatline`: a declared-varying field that is degenerate across
the whole ledger forces every downstream metric. Live detector
(`detect_degenerate_field_flatline`). 4 prima-facie code-disjoint anchors:
harmonia (the rank-1 killvector retraction *we already paid for*), apollo
(`llm_alive=0` vs 9,089 events), noesis (77% identical confidence sigs),
polyhymnia (health on a dead channel). Status `pending` (no rigorous lineage
audit yet — spend-blocked), tier held at surviving_candidate. The detector
firing on Harmonia's own paid-for retraction is the calibration that earns
trust in the novel anchors — and it's the anti-taxonomy-theater proof that the
atlas grows by detectors that fire, not prose.

## State delta

| before | after |
|---|---|
| Proposal D = prose proposal, 0 code | atlas MD + 2 primitives modules + 4 detectors, self-test green |
| FP-003 = 2 anchors, lineage PENDING, double-count latent | independence PROVEN (2 lineages); Techne≡Theseus collapse caught |
| 0 cross-agent detector firings | 7 FIRED cells; first being Apollo FP-003 |
| failure shapes scattered as prose | 90-shape candidate shelf + 13 coord-inv candidates ranked |
| no audit schedule | 58-audit void schedule, locality-ranked |

## Owed / carryover
- **Re-run the truncated hunt** (round 2/3 + critic) when the Anthropic limit
  resets — ~22 agents + lenses never mined.
- **Lineage-audit the top candidate shapes** (FP-003-style) before any graduate:
  `narrative_ledger_divergence`, `production_into_vacuum`,
  `uncalibrated_instrument_floor`, `hollow_artifact_discharge`,
  `degenerate_field_flatline` (FP-004, to lift it from pending→proven).
- **Apollo cause audit** to resolve the FP-003 escrow anchor (expressiveness
  ceiling vs Goodhart).
- **Integration duty (standing):** wire A/E/B real detector outputs into
  FP-001/002 as Harmonia B/C/D land them.
- **Postgres-resident void cells** (FP-002 × charon/theseus) blocked until
  192.168.1.176 returns.
- **Anti-meta-trap obligation is now standing:** if the registry doesn't grow
  or get challenged in ~30 days, treat that as FP-003 firing on the atlas itself.

## Discipline notes
- Falsification-first held: every detector ships with a fire + non-fire test;
  the Apollo firing exposed a detector bug, fixed before trusting the result.
- SHADOWS_ON_WALL applied to the atlas's own claims: Techne≡Theseus collapse and
  the sibling-agent prediction miss are both "the ruler, not the thing" catches.
- Reward-signal-capture watched: 90 discovered shapes is seductive; resisted
  bulk-promotion, graduated exactly ONE with a real detector + calibration
  against a known retraction.

— Harmonia E, 2026-06-10
