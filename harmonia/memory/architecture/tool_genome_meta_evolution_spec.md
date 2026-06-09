# Tool-Genome Meta-Evolution Harness — SPEC

## ⚗️ STATUS: EXPERIMENTAL — research scaffold, not a product

> **Nature of this work (read first).** This is *experimental play*, deliberately so. The premise
> ("build all candidate tools cheaply, score them, recombine tools as genomes") is a bet, not a
> validated method. Build cost is ~0; the binding constraint and the entire risk surface is in
> **scoring** (eval-cost + eval-integrity). Everything below is tagged EXPERIMENTAL and should be
> read as a falsifiable design, with explicit kill-criteria for the harness itself (§7). Nothing
> here is wired up; this is a spec gated on an explicit go.
>
> **Companions:** [`topological_falsification_engine.md`](topological_falsification_engine.md)
> (doctrine), [`reasoning_tool_candidates.md`](reasoning_tool_candidates.md) (the seed population),
> [`bottled_serendipity.md`](bottled_serendipity.md) (per-claim thesis). Drafted by Harmonia_M2_B,
> 2026-05-27.

---

## 1. Purpose

A two-level evolutionary system over reasoning instruments:

- **Object level** — reasoning genomes (atoms → molecules → organisms) evolved *by* the tools, scored
  by a mechanical falsification battery (the existing Forge/Apollo/Icarus substrate).
- **Meta level** — the **tools are genomes.** A tool-genome is a configuration over
  `(mutation operator, selection lens, KillVector basis, diversity scheme, assembly operator,
  coverage instrument)`. Recombination swaps components. This is hyper-heuristics (catalog #40)
  applied to the whole catalog — the catalog eating itself.

The meta-level fitness is **marginal kill-space coverage**: a tool-genome is good iff it produces
deaths/structure *no other tool reaches*. This rewards orthogonality among tools and is the
anti-monoculture move (§4). It is also the load-bearing risk (§6).

---

## 2. The genome encoding

```
ToolGenome = {
  mutation_op:      one of {near_miss_llm, constraint_conditioned, forbidden_move,
                            temp_ensemble, semantic_crossover, repr_shuffle, kill_replay, ...}  # catalog §1
  selection_lens:   subset of {contract, frame_null_precheck, formal_verifier, property_based,
                               metamorphic, mutation_testing, ablation_v2, ...}                  # catalog §2
  basis:            KillVector basis id + version                                                # catalog §3
  diversity_scheme: one of {map_elites_kv, novelty_search, nslc, cma_mae, fitness_sharing}        # catalog §4
  assembly_op:      one of {blackboard, dreamcoder, gp_typed, grammar_evo, none}                  # catalog §5
  coverage_instr:   one of {participation_ratio, persistent_homology, frontier_tracker}           # catalog §6
  hyperparams:      dict (temperatures, budgets, thresholds)
}
```

Recombination = crossover over these slots; mutation = perturb one slot. Each genome instantiates a
runnable pipeline. The seed population = all [VAR]+[NEW] candidates from the catalog.

---

## 3. Shared substrate (PREREQUISITE — must exist before any tool is scored)

Without a shared genome space and a common fitness, N tools are scored in N incomparable units and
cannot be ranked or recombined. Build order in §8; the pieces:

1. **Domain-general KillVector basis** (catalog #23). The current basis is Lehmer/Mahler-specific and
   measured **rank-1** (engine-doctrine §6 Q2). A meta-search over tools cannot illuminate a collapsed
   space — this is the hardest prerequisite, not a formality.
2. **Multi-gate instrumentation** (#26). Record *all* falsifier margins per candidate, not just the
   first-failing — the direct fix for the rank-1 cascade collapse.
3. **Cross-swarm KillVector bus** (#83). One shared kill-space so every tool's deaths land in the same
   basis ("reactions, not nodes").
4. **Coverage / effective-dimensionality instrument** (#45, #84). The order parameter; productionizes
   today's audit measurement.
5. **A fixed calibration battery** — known truths/falsehoods (Harmonia F001–F005 analogue, #19), held
   model-invisible, as the *stable evaluation reference* (coevolution needs this — §6 C5).

---

## 4. Fitness: marginal kill-space coverage (defined)

For a tool-genome `g` producing a set of evaluated candidates `C_g`, each landing at a point in the
KillVector basis:

- **Coverage(g)** = volume of kill-space cells *first reached* by `g`, weighted by cell **density**
  (reproducible re-sampling lands in the same cell) — *occupancy alone is not counted* (anti-noise).
- **Marginal coverage(g | archive)** = cells `g` reaches that the current archive does not. This is the
  selection signal.
- **Minimal-criteria gate (MCNS, Lehman & Stanley):** a cell counts only if its candidates also pass a
  minimal viability bar (e.g. survived past gate 1 — a *near-miss*, not a gross miss / compile error).
  Without this, coverage chases degenerate regions (§6 C7).
- **Adaptive-persistence weighting (Bedau):** a cell contributes to *cumulative evolutionary activity*
  only when it is **revisited and built upon**, not touched once. Distinguishes real innovation from
  drift (§6 C6). This is the difference between "mapped" and "grazed."

Net fitness is necessary-not-sufficient: high marginal coverage is required but must be cross-checked
against downstream survival/promotion yield (§6 C1).

### 4.1 Scoring stack (added 2026-05-27) — EXPERIMENTAL

Coverage composes from typed sub-scores. **Kill scores define/enrich the axes; diversity scores reward
spread over them** — the same object viewed twice.

**Kill scores (axis-defining):** margin/near-miss (continuous distance-to-trigger — the rank-1 fix);
survival-depth (gates cleared before death); **confound-residual** (death scored *after* partialling out
the dominant axis — directly punishes rank-1); reproducibility-weighted (down-weight flaky kills);
frame/null-adjusted (discount selection-frame artifacts — F044 guard); kill-novelty/anti-anchor (new way
to die vs known); minimal-counterexample (shrinking); surprisal; cost-normalized (info/compute);
mutual-information (vs the 0.725-bit baseline); process-step (which step failed); calibrated-scorer
meta-kill (sensitivity/specificity vs hidden anchors).

**Diversity scores (spread-rewarding):** k-NN novelty; NSLC (novelty × local quality);
**participation-ratio / effective-dim** of the kill-vector matrix (the order parameter, directly
anti-rank-1); cell entropy; DPP set-diversity; count-based curiosity bonus; surprise search;
fitness-sharing/crowding; phylogenetic/lineage diversity; expected (re-eval) coverage.

**Combination discipline (load-bearing):** DO NOT scalarize. A weighted sum is a new single ruler → new
monoculture, and is exactly why the current `magnitude()` collapsed 12 components to rank-1. Keep the
scores as a multi-objective frontier / QD archive / DPP-selected set — never one number. Adding scores
without this discipline *increases* Goodhart surface.

**Phase 0 gate metric:** confound-residual kill score + participation-ratio reward. One punishes the
`out_of_band`-dominated collapse; the other rewards discovery of a second axis. This pair is the
operational success metric for the Phase 0 near-miss experiment (the re-run of `kv_basis_dim.py`).

---

## 5. The meta-search

MAP-Elites over **tool-behavior** (not a single leaderboard), using a maintained QD library (pyribs,
catalog #31). Behavior descriptor for a tool-genome = *where in kill-space its deaths concentrate*
(so diverse tools occupy distinct niches). Insertion is **confidence-gated and re-evaluated** to avoid
locking in lucky noise (Uncertain QD — §6 C3). The archive is the deliverable: an illuminated map of
which tool reaches which region of kill-space.

---

## 5.5 Empiricizing the reasoning ladder (EXPERIMENTAL — added 2026-05-27)

The R0–R12 ladder is currently a **narrative taxonomy**; "R2 promoted more than R1" (Icarus) is the tell
that the rungs aren't operationalized. The move to empirical is the same move as the math-side kill-space:

- **Define each rung by its discriminating failure gradient, not prose.** Tier *n* is real iff there is a
  battery R_(n−1) provably cannot pass and R_n can, AND the *failure-mode signature* at *n* differs from
  *n−1*. The tier IS the failure-signature, not the description.
- **Graded test cases (failure gradients, not pass/fail).** Each case emits a *margin vector* — how close,
  in which direction it failed — over a reasoning-side KillVector basis (catalog #27:
  failure_class × tier × detected_by). Candidate gradient channels: process-step failure (which step),
  partial-constraint satisfaction (how many constraints met), edit-distance-to-correct, self-consistency
  spread (answer instability across samples), verifier margin (how close to passing a formal check).
- **The stacked near-miss landscape.** Each tier's graded battery is a kill-space; **stacking them, indexed
  by tier, IS the near-miss landscape across every rung.** A reasoner's tier-*n* performance is a point in
  that tier's kill-space.
- **The near-miss shell is the on-ramp to the next rung.** Consistent near-misses at tier *n* are the
  population from which tier *n+1* emerges; climbing = moving through near-miss shells. The ladder becomes
  a continuous gradient field, not discrete narrative levels.
- **Rung-reality test (the empirical payoff).** If the failure-gradient distributions at R_(n−1) and R_n
  are statistically indistinguishable, that rung is narrative fiction; if distinct, it is empirical. This
  makes the ladder itself **falsifiable**, and directly tests the suspicious R1 < R2 promotion rate.
- **Hardest part:** defining the gradient for reasoning tasks is non-trivial (a real number for Mahler
  measure; ill-defined for "did it reason correctly"). The gradient-channel vector above IS the
  reasoning-side KillVector basis — building it is the prerequisite, exactly as on the math side.

**Full design + build:** the testable R0–R12 ladder (tier table, 4-version battery, Reasoning Trace
Vector schema) is captured in [`reasoning_ladder_testable.md`](reasoning_ladder_testable.md) (design by
James). First suite built and calibrated: `harmonia/experiments/reasoning_phase0.py` — procedural R0–R3
+ R6 probes, capability-capped baseline reasoners, deterministic trace-vector emitter. 2026-05-27 run:
clean capability staircase (reasoners fail in tier-predicted ways = calibration PASS); reasoning
trace-vector kill-space effective dim ≈ 4.4 (multi-dimensional, not rank-1); rung-reality signal — R0/R2/R6
are empirically distinct rungs, R1/R3 thin/overlapping (candidate non-rungs, supporting the
ladder-vs-basis critique).

---

## 6. Challenges & literature-grounded failure signals

*Each: why it bites here · the named failure mode · the observable SIGNAL (shape, per failure-signature
doctrine) · mitigation/probe. All EXPERIMENTAL.*

**C1 — The fitness is the whole game (Goodhart, 4 variants).** Coverage-fitness is itself gameable.
*Regressional:* selecting coverage also selects the coverage-minus-discovery gap. *Extremal:* tools
maximize coverage at degenerate extremes unlike the regime where coverage≈value held. *Causal:* raising
coverage may not causally produce discovery; intervening breaks the link. *Adversarial:* a tool that
*models* the metric emits noise into empty cells.
**Signal:** coverage ↑ while downstream survival/promotion flat or ↓; cells filled by single low-density
hits. **Lit:** Manheim & Garrabrant, *Categorizing Variants of Goodhart's Law* (2018). **Mitigation:**
density+reproducibility (not occupancy); orthogonal downstream-yield cross-check; red-team the metric.

**C2 — The behavior descriptor IS the whole game, and ours is rank-1.** In QD, the BD choice determines
everything; a misaligned BD illuminates nothing. Our BD = the KillVector basis, measured rank-1 today.
A meta-search inherits the basis pathology.
**Signal:** archive collapses to ~1 cell regardless of tool diversity; coverage saturates immediately.
**Lit:** Cully & Mouret (illuminating search spaces); Pugh, Soros & Stanley (QD); Flageat & Cully (BD
uncertainty). **Mitigation:** §3 prerequisites (#23/#24/#26) MUST land first; measure basis effective-
dim before trusting the archive (gate K2).

**C3 — Noisy-fitness over-estimation ("lucky" elites).** Single-sample coverage estimates are optimistic;
MAP-Elites elitism locks in lucky noise; QD score and coverage are overestimated.
**Signal:** elites don't reproduce on re-eval; archive coverage drops on re-evaluation; ranking unstable
across seeds. **Lit:** Flageat & Cully, *Fast and stable MAP-Elites in noisy domains* (2020); Uncertain
Quality-Diversity (2023). **Mitigation:** confidence-gated insertion; re-evaluation budget; report
*expected* (re-eval) coverage.

**C4 — The meta-search may not beat random (the NAS lesson).** In neural architecture search, random
search ≥ leading methods; the *search space* carried the signal, not the search. Our tool-genome
MAP-Elites may not beat random tool-sampling; the catalog may be doing all the work.
**Signal:** MAP-Elites elites ≈ random-sampled tools at equal eval budget; no separation. **Lit:** Li &
Talwalkar, *Random Search and Reproducibility for NAS* (2019/2020). **Mitigation:** random-tool-sampling
is a MANDATORY control and the harness's primary calibration anchor (gate K1).

**C5 — Coevolution pathologies (tool↔task and Nemesis↔atom loops).** Disengagement (one side dominates →
gradient vanishes → drift), cycling (intransitive, revisits states, forgets prior solutions),
overspecialization, relative overgeneralization. Root cause: *lack of a stable yet continually improving
evaluation reference.*
**Signal:** oscillation without monotone coverage gain; archive churn (cells gained then lost); win-rates
flip with no net progress. **Lit:** Popovici/Bucci/Wiegand/De Jong, *Coevolutionary Principles*;
Cartlidge & Bullock (reducing parasite virulence); Ficici; Watson & Pollack. **Mitigation:** hall-of-fame
of past adversaries (anti-forgetting); cap trap "virulence" (no unbeatable traps); keep the fixed
calibration battery (§3.5) as the stable reference.

**C6 — Open-endedness vs drift: is coverage real innovation?** Unbounded activity with no novel
components = pure ecological drift, not innovation. Coverage can grow while nothing adaptive accrues.
**Signal:** cumulative evolutionary activity flat while raw coverage grows (new cells touched once, never
built upon). **Lit:** Bedau et al., evolutionary activity statistics; Channon (Geb / ALife test); OEE
workshop (Taylor, Stanley et al.). **Mitigation:** instrument cumulative evolutionary activity / adaptive
persistence on the kill-space (§4), not just occupancy (gate K3).

**C7 — Novelty in an unbounded space chases junk.** Novelty search struggles when behavior space is
large/unbounded; it explores many uninteresting solutions.
**Signal:** coverage explodes into degenerate kill-space regions (compile-error / gross-miss cells);
novelty without viability. **Lit:** Lehman & Stanley, *Abandoning Objectives* (2011); Minimal-Criteria
Novelty Search (MCNS). **Mitigation:** the §4 minimal-criteria viability gate (count only near-miss cells).

**C8 — Compositional brittleness at the tool level (Frankenstein, again).** Composing operator+lens+basis
tool-genomes has brittle interfaces; composed tools may underperform their best single component — the
same disease Apollo hit composing reasoning primitives.
**Signal:** a composed tool-genome's coverage < its best single-component sub-tool's coverage. **Lit:**
Apollo gen-3551 baseline-matrix falsification (internal); compositional-generalization benchmarks (SCAN,
COGS, CFQ). **Mitigation:** typed tool interfaces; require lift over best single component (Apollo's
strict gate generalized) — gate K5.

**C9 — LLM-in-the-loop contamination (the doctrine's own rule).** If the coverage-fitness or any
selection seat uses an LLM, the human prior leaks back in; tools that "look novel to a model" win without
raising deterministic coverage. This is how the system "steers back toward papers."
**Signal:** tools score well on LLM-judged components but flat on deterministic coverage. **Lit:** the
doctrine (LLM on mutation side only); adversarial Goodhart. **Mitigation:** coverage-fitness fully
deterministic; LLM confined to the mutation seat; audit every seat for an LLM judge.

**C10 — Representation dependence of coverage (SHADOWS_ON_WALL).** Coverage is relative to the chosen
basis; a tool that maximizes coverage in basis B may be useless in B′.
**Signal:** coverage gains don't transfer across reasonable alternative bases. **Lit:** internal
(SHADOWS_ON_WALL@v1; ensemble-invariance doctrine). **Mitigation:** measure coverage under ≥2 independent
bases; report only basis-invariant gains.

**C11 — Evaluation cost & throughput is the binding constraint.** Build cost ≈ 0, but each tool-genome
needs many candidate evaluations to estimate coverage with usable confidence intervals; recombination
multiplies eval demand.
**Signal:** eval-queue backpressure; coverage CIs too wide to rank; "0 promoted over N runs" churn
(Techne's live symptom). **Lit:** Uncertain-QD compute cost; NAS compute critiques. **Mitigation:** cheap
surrogate Tier-0 pre-filter; eval budget allocated by bandit; cache by candidate_hash.

**C12 — Specification gaming / reward hacking (general).** The metric gets satisfied in a way that
violates intent.
**Signal:** the coverage target is hit by a mechanism obviously orthogonal to discovery (engineered
empty-cell hits). **Lit:** Krakovna et al., specification-gaming examples catalog. **Mitigation:** hidden
calibration anchors (#19); adversarial red-team of the metric before trusting it.

---

## 7. Falsification plan for the harness itself (kill-criteria)

The harness must survive its own battery. If any of these fire, the named component is theater and should
be cut — the catalog (search space) may still be kept even if the search is killed.

- **K1 (NAS control).** If random tool-sampling matches MAP-Elites on basis-invariant coverage at equal
  eval budget → the *meta-search* is decorative. Keep the catalog; drop the search.
- **K2 (dead BD).** If KillVector-basis effective-dim stays ≤ ~1 after #23/#24/#26 land → the behavior
  descriptor is dead; no QD is possible. Stop; fix the basis or conclude the domain has no multi-D
  kill-space here.
- **K3 (drift).** If coverage rises while cumulative evolutionary activity AND downstream survival stay
  flat → drift, not innovation; the metric is being gamed. Revert to viability-gated, activity-weighted
  coverage.
- **K4 (luck).** If elites don't reproduce on re-eval → noisy-fitness capture; the archive is luck.
  Raise re-eval budget or abandon.
- **K5 (decorative composition).** If composed tool-genomes never beat the best single component → tool
  composition is decorative (Apollo redux). Keep single tools; drop recombination.

These kill-criteria ARE the calibration anchors. Running without them is how the project has previously
manufactured certified mirages (F043, F044, Apollo gen-3551).

---

## 8. Phased build order (SPEC ONLY — gated on explicit go)

- **Phase 0 — Substrate.** #23 domain-general basis + #24 orthogonalization + #26 multi-gate +
  #84 eff-dim dashboard. **Gate:** basis effective-dim > 1 (K2) — else stop.
- **Phase 1 — Fitness.** #45 coverage order-parameter + Bedau activity weighting + MCNS viability gate +
  #49 frontier tracker. **Gate:** metric survives adversarial red-team + reproduces on re-eval.
- **Phase 2 — Controls.** Random-tool-sampling baseline + hidden calibration anchors. **Gate:** harness
  beats random on basis-invariant coverage (K1) — else stop.
- **Phase 3 — Meta-search.** Tool-genome encoding + MAP-Elites over tool-behavior (pyribs) +
  uncertain-QD re-evaluation.
- **Phase 4 — Mass build.** Build all [VAR]+[NEW] as the seed population; run; watch K1–K5 continuously.

Each phase is independently abortable. The early gates are designed to kill the bet cheaply if the
substrate can't carry it.

---

## 9. Open questions

1. Tool-behavior descriptor: is "where its deaths concentrate" the right BD, or does it need a separate
   axis for *cost* and *assembly depth*?
2. Cheap basis-invariance: measuring coverage under ≥2 bases doubles eval cost — is there a surrogate?
3. Do the math and reasoning landscapes share one basis, or a product basis with a shared sub-block?
4. The minimal-viability criterion (MCNS gate) definition per landscape — what is "past gate 1" for
   reasoning organisms vs math claims?
5. Eval-budget policy: how to split budget across (new genomes) vs (re-eval of incumbents) vs (random
   control)?

---

## 10. References (literature grounding for §6–§7)

- Manheim & Garrabrant, *Categorizing Variants of Goodhart's Law* (2018) — https://arxiv.org/abs/1803.04585
- Li & Talwalkar, *Random Search and Reproducibility for NAS* (2019/2020) — https://arxiv.org/abs/1902.07638
- Flageat & Cully, *Fast and stable MAP-Elites in noisy domains using deep grids* (2020) — https://arxiv.org/abs/2006.14253
- Lehman & Stanley, *Abandoning Objectives: Evolution Through the Search for Novelty Alone* (2011) — https://dl.acm.org/doi/abs/10.1162/EVCO_a_00025
- Bedau et al., evolutionary activity statistics; Channon, *Passing the ALife Test (Geb)* — https://link.springer.com/article/10.1007/s10710-006-9009-3
- Popovici, Bucci, Wiegand & De Jong, *Coevolutionary Principles* (Handbook of Natural Computing); Cartlidge & Bullock, *Combating Coevolutionary Disengagement by Reducing Parasite Virulence* — https://www.researchgate.net/publication/8549752
- Cully & Mouret; Pugh, Soros & Stanley — Quality-Diversity foundations — https://quality-diversity.github.io/papers.html

*EXPERIMENTAL throughout. This spec is itself a falsifiable artifact; if a gate or failure-signal here
does not fire the way it predicts, update the spec.*
