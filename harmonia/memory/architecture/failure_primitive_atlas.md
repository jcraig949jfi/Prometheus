# The Cross-Agent Failure-Primitive Atlas

**Owner:** Harmonia_M2_E (Proposal D, per `D:\Prometheus\harmonia\proposals\2026-06-09\00_SEQUENCING_AND_HANDOFF.md` §6)
**Machine layer:** `D:\Prometheus\harmonia\primitives\failure_primitives.py` (registry + live detectors + `validate_atlas()`)
**Status:** v0 thin registry, seeded 2026-06-10; FP-003 reached `coordinate_invariant` 2026-06-15 (first top-tier primitive; Apollo escrow resolved). Grown by A/E/B outputs and the Stage-3 generative hunt — never by a standalone taxonomy sprint.
**Created:** 2026-06-10

---

## What this is

The agent-level analogue of Erebos's claim-level kill-pattern registry
(`D:\Prometheus\charon\agents\erebos\_kill_pattern_registry.py`): a typed map of
the failure **shapes** Prometheus agents keep paying for independently. Each
entry is a `FailurePrimitive` whose signature is a **detectable predicate** —
an entry that reduces to a verdict-line ("agent X failed") is rejected at
registration, mechanically (`_admission_check`).

The atlas is itself a sparse tensor (failure-shape × agent × detector ×
mitigation). Its **voids are the directional signal**: cells where a detector
should fire but has never been run are the highest-value audits to schedule
next (`void_report()`).

## Admission rules (enforced in code where possible)

1. **Shape, not verdict.** `signature` must state a detectable predicate.
   Regex-screened at registration; the real gate is review.
2. **Detector or demotion.** Every entry ships a live importable detector or a
   marked stub. A detector that never fires on agents that didn't author it
   demotes the entry to `cautionary_tale` (Proposal D §4).
3. **Independence is the whole game.** `coordinate_invariant` requires ≥3
   anchors across **distinct lineages** AND `independence_status == "proven"`.
   Two anchors sharing scour/scaffolding code are ONE observation — the same
   shadow cast twice. Tier ladder: 1 lineage = `shadow`, 2 =
   `surviving_candidate`, ≥3 proven = `coordinate_invariant`.
4. **Anti-gravity-well guard (the meta-trap, Proposal D §5 Q4).** The atlas
   must not become the menu that causes the bounded-menu wall at the meta
   level. The Stage-3 generative hunt (fan-out mining of agent histories for
   shapes the atlas doesn't name) is a STANDING obligation, not a one-shot —
   if the registry hasn't grown or been challenged in ~30 days, treat that as
   FP-003 firing on the atlas itself.

## The registry (v0 seeds)

### FP-001 `baseline_costume` — tier: surviving_candidate

- **Signature:** a structural claim derived from rows R ties (≥90% agreement on
  ≥5 shared keys) a cheap baseline computable from R's marginals or
  co-occurrence counts — the "found structure" is the baseline wearing a hat.
- **Detector:** `detect_baseline_costume` (LIVE — delegates to the frozen
  `harmonia.primitives.baseline_costume.costume_check`, Proposal A, shipped
  2026-06-10 by Harmonia B).
- **Anchors (2 independent lineages):**
  - Erebos Layer 2, ITER-56: 9.8σ "motif structure" == per-plugin majority
    counter — `D:\Prometheus\pivot\sprint1\phase3\PHASE3_0_SMOKE_VERDICT_2026-05-30.md`
  - Theseus kill-topography Finding 1: kill concentration == catalog volume —
    `D:\Prometheus\pivot\kill_topography_findings_2026-05-29.md`
- **Mitigation:** gate every structure claim through `costume_check` before
  promotion.
- **Voids:** Theseus a3 voids (Proposal B gate, pending); h2 subclasses
  (Proposal E §3.3, pending); Apollo Branch-C archive keying; Icarus lens
  attribution.

### FP-002 `opaque_kill_black_hole` — tier: shadow

- **Signature:** one kill-label absorbs ≥30% of a ≥1000-record ledger with no
  varying witness payload beneath it — that volume confirms failures happened
  but emits zero direction (the gradient is destroyed).
- **Detector:** `detect_opaque_kill_blackhole` (LIVE — pure function over any
  agent's kill-label column; optional payload-variation downgrade).
- **Anchor (1):** Theseus h2: `h2_method_triangulated_reject` = 43.68% of 200K
  kills, zero differentiation —
  `D:\Prometheus\pivot\kill_topography_findings_2026-05-29.md` Finding 3.
- **Mitigation:** h2 structured-kill refactor landed; historical backfill =
  Proposal E (Harmonia C).
- **Voids:** Apollo kill logs; Icarus kill_clusters; Charon plugin ledger;
  Ergon shadow archive.

### FP-003 `bounded_menu_wall` — tier: **coordinate_invariant** (3 proven-independent anchors; Apollo de-escrowed 2026-06-15)

- **Signature:** a fixed candidate-generation menu produces a ≥30-batch tail of
  consecutive zero promotions under honest scoring — a structural ceiling of
  the menu, not a search/tuning failure. Deepening the menu in-place does not
  break it; menu growth or lineage branching does.
- **Detector:** `detect_bounded_menu_wall` (LIVE). Input contract learned from
  first live use: pass HONEST promotions — for capacity-bound archives
  (MAP-Elites) use within-cell fitness improvements, not cell fills, or the
  detector false-positives on benign saturation-at-capacity.
- **Anchors:**
  - **theseus-substrate (Techne-operated)**, lineage `theseus-techne-loop`:
    Fires #142–#236, 92 consecutive 0-promoted after the Fire #141
    honest-scoring fix; cause subclass `region_empty` (calibration v3 proved
    the knot×EC region empty). Primary:
    `D:\Prometheus\roles\Techne\SUBSTRATE_FIRE_LOG_2026-05-21.md`; autopsy:
    `D:\Prometheus\pivot\calibration_v3_VERDICT_2026-06-03.md`. **Identity
    correction from Stage 2: "Techne's wall" and "Theseus's wall" are ONE
    observation — Techne is the operator role of the Theseus substrate, one
    fire ledger.**
  - **polyhymnia**, lineage `polyhymnia-scour-aporia-shell`: 280 ticks / 236
    null (84.3%); single scour saturated its source; adaptation menu = 5 no-op
    stubs + 1 real-but-useless item; absorbing approval-gate state (163 dup
    tickets); cause subclass `source_saturated`. Primary:
    `D:\Prometheus\aporia\meta\queue\aporia_inbox.jsonl` ticket
    `T-2026-06-03-aporia-polyhymnia-verdict`; commit `824a668b`; report:
    `D:\Prometheus\aporia\meta\triage_report_2026-06-03.md`.
  - **apollo (DE-ESCROWED 2026-06-15)**, lineage `apollo-blackboard-evolve`:
    this atlas's first cross-agent detector firing — Branch C r1 49/49 and r2
    480/480 gens with zero `best_acc` improvement under a fixed op menu while
    the search stayed alive (`mutation_viability=1.0`, `llm_used>0`). Cause
    subclass **`expressiveness_ceiling`** (resolved — see Stage-3 ruling below);
    **NOT Goodhart**. Evidence:
    `D:\Prometheus\harmonia\experiments\fp_void_audits_20260610.json`; cause
    resolution: `D:\Prometheus\apollo\pivot\r2_run1_findings_2026-06-10.md` +
    `D:\Prometheus\apollo\pivot\cross_tier_falsification_result_2026-06-10.json`.
- **Stage-2 independence ruling (2026-06-10, Harmonia E): PROVEN for anchors
  1–2.** Code-disjoint at the failure-relevant path: Polyhymnia's daemon shell
  descends from the Aporia agents-swarm template (Hypatia/Atalanta/Pheme/
  Talos), not Techne/Theseus; tensor framework standalone; zero cross-imports;
  the scour does not even walk `techne\`. Promotion machinery shares no
  symbols. Mechanical causes differ — heterogeneous causes converging on one
  observable shape *strengthens* shape-level invariance.
  **Known residual contamination (recorded, not hidden):**
  `feedback_gen_30_wall` is James's prior C# experiment (stalled gen 30) — the
  doctrine PREDATES both walls and is hard-coded in
  `D:\Prometheus\agents\_shared\self_improving.py`'s docstring, which
  Polyhymnia runs. Both post-mortems were written by authors who knew the
  predicted shape, so the diagnosis *language* is contaminated. The ruling
  rests on the mechanical event series (promotion counters, null-tick
  counters), which are narrative-independent. Also: the original
  `feedback_gen_30_wall.md` file is MISSING from disk everywhere; its content
  survives only as quotation in
  `D:\Prometheus\charon\agents\erebos\_rank_expansion.py`.
- **Stage-3 independence ruling (2026-06-15, Harmonia E): Apollo DE-ESCROWED →
  FP-003 promotes surviving_candidate → `coordinate_invariant` (3rd independent
  lineage).** The escrow held only for *cause attribution*; Apollo's own
  2026-06-10 artifacts resolve it. **Cause = `expressiveness_ceiling`, not
  Goodhart:** Apollo's op menu *cannot express* a cross-tier organism (no op
  reads `derived_facts` → writes `relations`/`ordered`), so the better organism
  is outside the search space — not unfound. `best_acc` stayed *honestly* flat
  at 0.42 (no proxy inflated while quality stalled → not Goodhart). **Falsified
  by FP-003's own predicted escape:** deepening the menu in-place made it worse
  (dup-op clones 0.42→0.27); growing the menu by one bridge op
  (`relations_from_facts`) made the cross-tier organism expressible → 0.42→**1.0**,
  `unique_solver=true`, all single-tier controls ≤0.3. **Independence (local
  audit, not the 4-probe Workflow — the structural disjointness is unambiguous
  enough that a Workflow would be confirmatory, not load-bearing):**
  `apollo/src/blackboard_evolve.py` imports only `blackboard`/`dataflow_fitness`/
  `blackboard_ops{,_v2,_r2}` — it does **not** import the
  `agents/_shared/self_improving.py` mixin that contaminated Polyhymnia, nor
  `theseus/`, nor any Aporia shell; separate MAP-Elites substrate, distinct
  founding (Branch C blackboard prototype); distinct mechanism. Diagnosis is in
  Apollo's own type-bridge vocabulary (no reference to FP-003); load-bearing
  evidence is the narrative-independent event series.
  **Sharpest open critique (logged, not fatal):** Theseus `region_empty` is a
  *truthful* wall (region genuinely empty → STOP is correct) while Apollo
  `expressiveness_ceiling` is an *artifact* wall (better organism exists outside
  the menu → GROW is correct) — opposite remedies under one observable. Per the
  heterogeneous-causes doctrine this *strengthens* shape-invariance and makes
  the detector a triage instrument; a subclass-discriminator probe is owed when
  spend resets, to confirm the detector cannot be made to over-lump.
- **Cause-subclass taxonomy** (preserves the gradient, and now *routes the
  remedy*): `region_empty` / `source_saturated` → **STOP** (the wall is
  truthful) | `expressiveness_ceiling` → **GROW the menu** (the wall is an
  artifact of an incomplete vocabulary) | `cause_unattributed`. The detector
  detects the shape; the subclass is post-detection diagnosis. Techne's own
  fire log resists the wall label for the Theseus case ("correct refusal to
  promote artifacts") — the lumping is acknowledged and carried as a subclass,
  not flattened.
- **Mitigation:** menu-growth / lineage mechanism (Arachne population layer).
  Prior art: Erebos ITER-43 `consecutive_zero_growth_run`
  (`D:\Prometheus\charon\agents\erebos\_rank_expansion.py`) — a second organ
  independently built a detector for this exact pattern.
- **Voids:** Ergon operator menu; Aporia attempt menu; Icarus proposal menu.
  (Theseus removed from voids — Stage 2 found that "void" was already the
  anchor; Apollo moved void → escrow → de-escrowed proven anchor over Stages
  2–3.)

### FP-004 `degenerate_field_flatline` — tier: surviving_candidate (graduated from the hunt)

- **Signature:** a field/channel/coordinate the design declares as VARYING is
  degenerate across the whole ledger (≤1 distinct populated value / never
  populated / pinned) despite live upstream writers — every downstream metric
  computed on it is algebraically forced and read as a domain finding.
- **Detector:** `detect_degenerate_field_flatline` (LIVE — per-field
  cardinality/population audit; optional `writer_events` smoking-gun leg).
- **Anchors (4 prima-facie code-disjoint lineages):**
  - **harmonia** — correlation matrix over single-component kill vectors forced
    to rank-1; *a retraction Harmonia already paid for* —
    `D:\Prometheus\harmonia\memory\architecture\reaudit_killvector_rank1_2026-05-27.md`
  - **apollo** — 9,089 LLM-mutation events but `llm_alive=0` in the population
    (`pivot/apollo_investigation_2026-05-22.md`)
  - **noesis** — 182/236 hubs (77%) share identical depth-2 confidence
    signatures — `D:\Prometheus\journal\2026-03-31-aletheia-overnight.md`
  - **polyhymnia** — health composite computed on a dead channel
    (diversity/novelty pinned at 0)
- **Why it's the graduation case:** it's the *anti-taxonomy-theater* proof —
  the atlas grows by a detector that FIRES, not prose; and the detector firing
  on Harmonia's own paid-for rank-1 retraction is the calibration that earns
  trust in the three novel anchors.
- **Status: `pending`.** Four different codebases, four mechanically distinct
  instruments → prima-facie independent, BUT a rigorous FP-003-style lineage
  audit was NOT run (blocked by the Anthropic spend limit 2026-06-10). Tier
  held at `surviving_candidate`, not `coordinate_invariant`, until it lands.
- **Voids:** Ergon tensor fields; Icarus trace-dict fields; Charon plugin
  scorecard fields; Theseus record fields.

## The candidate shelf (Stage-3 generative hunt, 2026-06-10)

The hunt (`hunt_raw_20260610.json`, 27 agents, 3 rounds, 90 deduped shapes)
fed the pre-filtered candidate pool, NOT the registry. Per the anti-gravity-
well guard, only shapes that earn a real detector and survive a lineage audit
graduate to an FP — so far only FP-004 has. The full shelf with conservative
(Techne≡Theseus-collapsed) independence counts is at
`D:\Prometheus\harmonia\memory\architecture\fp_candidate_shelf_20260610.md`.

**⚠ The hunt was truncated** by the Anthropic monthly spend limit: 9 round-2/3
miners + the completeness critic never ran (ignis, stoa, sigma_kernel,
cartography, falsification, audit, ~16 small agents, both modality lenses).
Coverage is NOT exhaustive despite `terminated_dry=True`. Re-run owed when the
limit resets.

Top coordinate-invariant *candidates* awaiting lineage audit (≥3 independent
lineages after collapse): `narrative_ledger_divergence` (5),
`production_into_vacuum` (5), `surface_space_novelty_inflation` (5),
`uncalibrated_instrument_floor` (4), `hollow_artifact_discharge` (4),
`null_free_validation_stack` (3, collapsed from 4), `unpersisted_evidence_record`
(4), `declared_check_never_executed` (3), `unwitnessed_flatline` (3),
`measurement_referent_unbinding` (3), `mismatched_null_reference` (3),
`posthoc_gate_thaw` (3). These are the next audits to schedule.

## Integration duty (standing)

As Harmonia B (Proposal A), C (Proposal E), D (Proposal B) emit results, their
detectors and evidence wire into FP-001/FP-002 here: real `costume_check`
verdicts become new anchors; the h2 backfill numbers become FP-002 evidence;
a3 void survivorship becomes FP-001's third anchor or its absence. Harmonia E
is the collection point.

## Validation

Run `python -c "import sys; sys.path.insert(0, r'D:\Prometheus'); from harmonia.primitives import failure_primitives as fpp; fpp._selftest()"`
— exercises all three detectors (fire + non-fire + downgrade paths), the
verdict-line admission gate, tier ruthlessness, and `validate_atlas()`
(MD↔registry ID cross-check + anchor-path existence).
