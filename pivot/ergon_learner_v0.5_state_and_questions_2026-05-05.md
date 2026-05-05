# Ergon Learner — v0.5 State, Ideas, and Open Questions

**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-05
**Status:** Pre-design document. Will be cycled through Aporia (open-question framing), Techne (substrate + data-curation gate), and frontier models (ChatGPT, Gemini, DeepSeek, Grok) before v0.5 is frozen.
**Predecessors:** `pivot/ergon_learner_proposal_v8.md` (design freeze that produced MVP), `pivot/ergon_learner_v7_final.md` (full operational treatment).
**Companions:** `roles/Techne/SPRINT_2026-05-01_to_2026-05-05.md` (Techne sprint that produced the substrate primitives Ergon depends on), `stoa/discussions/2026-05-04-ergon-CALIBRATION-iter28-stability.md` (the substrate-grade discipline cycle that motivates several v0.5 design choices).

---

## 0. How to read this document

If you are **Aporia**: skip to §6 (open questions). The framing in §1-§5 is self-contained context for the questions; you've seen most of it. The questions in §6 are deliberately sharp and need adversarial pressure.

If you are **Techne**: §3 (falsification battery) and §4 (substrate primitives) are written from Ergon's vantage; check that I haven't misrepresented your ontology. §5.4 (data-curation handoff) and §6.3 (the Aporia flag) directly bear on your `Stoa note + Ergon ping about Learner training-data hygiene` open item from your sprint summary.

If you are a **frontier model** with no Prometheus context: read in order. §1-§4 give you the project background; §5 is the readout; §6 is the questions.

If you are **James**: §6.5 is the path-decision question I most need your call on.

---

## 1. Prometheus project background

Prometheus is a research program building a **structured knowledge substrate** and the **reasoning machinery** to navigate it — organised so a future intelligence under evolutionary pressure can find what no human mind has found. The current emphasis is mathematics: cross-domain mathematical structure discovery.

Three pillars, built in parallel:

1. **Substrate — the map.** Organised, multi-dimensional knowledge: ideas, relationships, gaps, frontiers, contradictions, and the geometry of how concepts connect. Linked to what an AI can compute about it. Owned today by Techne (via `sigma_kernel/` + `prometheus_math/`) and Mnemosyne (via the data treasury — LMFDB / OEIS / prometheus_sci / prometheus_fire).
2. **Reasoning — the navigator.** Machinery that traverses the substrate. Evolved models, forged reasoning tools, tensor-native evolutionary search over validated coordinates. Owned today by Ergon (the Learner and the evolutionary engine), Harmonia (TT-cross), and a constellation of pre-pillar agents (Apollo / Rhea for model evolution).
3. **Verification — the crucible.** Adversarial pressure, causal inference, formal proofs, null-calibrated admission gates. No claim survives without it. Owned today by Charon (kill battery) + Koios (5-gate test) + the discovery_pipeline kill_path.

The working form of the goal: **compressing coordinate systems of legibility, not laws.** The mathematical phonetic alphabet is *constructed*, not discovered — like IPA for speech.

The bigger architectural commitment that makes Ergon's Learner the load-bearing v0.5 work: **Prometheus should own its model, not depend on frontier APIs.** The substrate produces typed records at scale; the Learner trains on this corpus; over time it becomes a model that predicts productive search moves. This is the strongest hedge against the API restriction / cost trajectory (see `feedback_frontier_models_window.md`).

---

## 2. The symbolic library (arsenal_meta + sigma_kernel BIND/EVAL)

The substrate's symbolic surface is the union of three things:

### 2.1 `prometheus_math/arsenal_meta.py` — the typed callable arsenal

A process-global registry (`ARSENAL_REGISTRY: Dict[str, ArsenalMeta]`) mapping `"module.path:qualname"` to runtime metadata for every callable a researcher (or learner) might compose. Each `ArsenalMeta` carries:

- `cost`: `{max_seconds, max_memory_mb, max_oracle_calls}` — operational budget the BIND opcode enforces.
- `postconditions`: invariants the output must satisfy.
- `authority_refs`: published tables / catalogs the output is verified against.
- `equivalence_class`: canonicalizer subclass tag (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`). Drives the descriptor's axis 1.
- `category`: coarse domain bucket (`number_theory` / `topology` / `numerics` / ...).

Current scale: ~85 typed callables. Target at scale: ~2,800+. Decoration is import-time and idempotent.

### 2.2 `sigma_kernel/` — the 7-opcode substrate kernel

Techne's substrate primitive (sprint 2026-05-01 → 2026-05-05). Seven opcodes:

`RESOLVE` / `CLAIM` / `FALSIFY` / `GATE` / `PROMOTE` / `ERRATA` / `TRACE`.

Three terminal states for any claim: `PROMOTED` / `SHADOW_CATALOG` / `REJECTED`.

The kernel enforces: append-only ledger, linear capabilities, three-valued GATE, falsification-first PROMOTE, hash-locked caveats inherited via TRACE.

### 2.3 `sigma_kernel/bind_eval_v2.py` — typed callable composition

BIND wraps an arsenal callable into a typed CLAIM-emitting routine. EVAL runs it. CLAIM/FALSIFY/PROMOTE are routed through bind_eval_v2's discipline:

- Cost contracts enforced from `arsenal_meta`.
- Postconditions checked.
- Authority refs surfaced as caveats.
- Precision/method/convergence metadata propagated (Techne sprint Day 5: now first-class fields).
- Caveat schema (12 known-caveat presets) attached to every CLAIM and inherited via TRACE.

This is the surface Ergon's genomes target. A Genome is a typed DAG over arsenal atoms; each node is an arsenal callable; the DAG's root output is what the falsification battery evaluates.

---

## 3. The falsification battery (KillVector + 4-fold + kill_path)

### 3.1 The four unanimous F-checks

The substrate's MVP discovery_pipeline runs these as the unanimous gate before any PROMOTE:

| ID | Test | Triggered when |
|----|------|----------------|
| **F1** | Permutation null | observed metric ≥ median over permuted-input null |
| **F6** | Base rate / triviality | output reducible to corpus base-rate without structure |
| **F9** | Simpler explanation | a smaller model (e.g., cyclotomic factor) explains the result |
| **F11** | Cross-validation | independent split / method disagrees with main result |

Verdict per test: `CLEAR` / `WARN` / `BLOCK`. Any `BLOCK` kills the CLAIM (no PROMOTE). All four `CLEAR`/`WARN` is the substrate-PASS condition.

### 3.2 The KillVector ontology (Techne, sprint Day 4)

The categorical kill_path was empirically too coarse: 0.725 bits of mutual information between operator and kill_path in 314,971 logged kills. Techne's reframe:

```
k = (k_F1, k_F6, k_F9, k_F11, k_recip, k_irreduce, k_catalog_×5, k_band)
```

A 12-component multi-hot vector with **per-component margin** (continuous distance to failure), method, precision_dps, convergence_status, stability. Operators induce directional derivatives ∂k/∂operator in this kill-space. The substrate's kill_vector_navigator ranks operators by `E[‖k‖]` per region.

Empirical payoff: **127,000× operator distinguishability gain** over legacy categorical kill_path (KL=3.5e-7 → KL=4.4e-2) on one validated cell (deg14 ±5 step). Validated on 1 of 16 region keys.

### 3.3 Kill_path semantics for Ergon

The Learner does NOT see raw KillVectors yet (still routes through the categorical kill_path field at the engine boundary). v0.5 is the natural place to wire native KillVector consumption. See §6.4.

---

## 4. Techne's substrate primitives and over-arching goals

Techne's role expanded across sprint 2026-05-01 → 2026-05-05 from pure toolsmith to **substrate owner + calibration discipline owner + epistemic ontologist + methodology contributor**. Ergon depends on all four.

### 4.1 What Techne owns that Ergon consumes

- **`sigma_kernel/`** — the kernel + BIND/EVAL v2 + caveats schema + precision metadata schema + Postgres migrations (currently 005).
- **`prometheus_math/discovery_pipeline.py`** — 5-catalog cross-check + 4-fold falsification + reciprocity + irreducibility + 3 terminal states.
- **`prometheus_math/kill_vector.py`** — 12-component KillVector + KillComponent ontology with margins, precision, method, convergence.
- **`prometheus_math/kill_vector_navigator.py`** — substrate's first explicit policy primitive; ranks operators by E[‖k‖] per region.
- **Cross-domain envs**: `bsd_rank_env`, `modular_form_env`, `knot_trace_field_env`, `genus2_env`, `oeis_sleeping_env`, `mock_theta_env` — six rediscovery benches Ergon can target.
- **Lehmer-subspace tooling**: `lehmer_brute_force` + `lehmer_path_a/b/c` + `lehmer_precision_ladder` + `lehmer_boundary_layer`. The brute-force closure of deg14 ±5 palindromic produced one local lemma (H5_CONFIRMED-local-lemma) and a 17-entry boundary layer that is itself the substrate's first-of-its-kind labeled near-miss training set (see §5.4 / §6.4).
- **Falsification + diagnosis**: `modal_collapse_synthetic`, `modal_collapse_continuous`, `gradient_archaeology`. These are Ergon's mandatory smoke-tests before any cross-domain claim.

### 4.2 Techne's over-arching goals (paraphrased from CHARTER + SPRINT)

- **Substrate is load-bearing for ALL agents.** Backwards compatibility mandatory; 0 regressions on every commit; 2758+ pivot tests as of 2026-05-05.
- **Calibration discipline.** Synthetic null controls before any cross-domain claim ships. Smoke catches before full runs. Multi-path triangulation when verification fails. Caveat-as-metadata propagation.
- **Epistemic ontology.** Truth in mathematical computation is stratified by precision / method / convergence. A dps=30 PASS and a dps=100 PASS must NEVER look identical in the ledger.
- **Methodology contribution.** When discovery findings are weak or retracted, the methodology paper draft (`pivot/methodology_paper_draft_v0.md`, v1 = 9280 words) is the strongest available claim.

### 4.3 The handoff gate from Techne to Ergon (load-bearing)

From Techne's SPRINT §"What I'd do differently next sprint":

> **Don't dump raw episodes for Learner training.** Aporia and ChatGPT both flagged this. Curate contrastive datasets with kill_path metadata + near-miss classifier targets. This sprint built the data; future sprints should curate before feeding Ergon.

And from Techne's queued items:

> **Path C labeled training set → near-miss classifier**. Boundary-layer clustering produces 4-class labels (post-invariance-fold: 2). Train Ergon's predicate engine on this.

This is the gate. Techne curates; Ergon trains. Whatever v0.5 looks like, it has to respect this division.

---

## 5. Ergon Learner — current state readout

### 5.1 What exists (commit ca681ab4, post-iter39)

```
ergon/learner/
├── genome.py                     # typed DAG over arsenal atoms; deterministic content hash
├── archive.py                    # MAP-Elites, pyribs-backed, pointer-storage discipline
├── descriptor.py                 # 5-axis content-aware behavior descriptor (~5,000 cells)
├── scheduler.py                  # operator-class scheduler with min-share enforcement
├── reward.py                     # agreement-weighted reward (MVP: w_S=1.0 only)
├── triviality.py                 # F_TRIVIAL_BAND_REJECT — 6 signatures
├── stability.py                  # perturbation stability check (currently STUB)
├── engine.py                     # top-level search loop; uses MVPSubstrateEvaluator (STUB)
├── genome_evaluator.py           # evaluator dispatch
├── promotion_ledger.py           # canonical capture, JSONL + .meta.json sidecars
├── operators/
│   ├── structural.py             # add/remove/swap nodes; rewire edges
│   ├── symbolic.py               # bump arg values within type
│   ├── anti_prior.py             # anti-correlated with corpus frequency
│   ├── uniform.py                # resample atoms uniformly (strawman null)
│   ├── structured_null.py        # type-respecting uniform
│   └── predicate_symbolic.py     # canonical production pipeline (BindEvalKernelV2-routed)
├── tools/
│   ├── inspect_archive_elites.py
│   ├── read_promotion_ledger.py
│   ├── characterize_clusters.py
│   └── stability_analysis.py     # cross-seed reproducibility — POST-HOC tool, not engine-native
├── tests/                        # 11 pytest files; math-tdd 4-category coverage
└── trials/
    ├── trial_1_residual_benchmark.py     # FAILED honestly; classifier deep-escrowed
    ├── trial_2_production_pilot.py        # 47σ PASS on all 4 criteria
    ├── trial_3_*.py (15 iterations)       # iter25→iter39: A149 corpus discipline cycle
    └── ledgers/                            # JSONL ledgers + regime manifest sidecars
```

### 5.2 Trial outcomes (verbatim)

| Trial | What | Verdict |
|-------|------|---------|
| **Trial 1** | Adversarial residual benchmark on 200 curated samples | **FAILED honestly** — 80% FP rate on synthetic structured-noise; classifier deep-escrowed; w_R = 0; Trial 1.5 deferred |
| **Trial 1.5** | Adversarial optimization probe (gates Trial 2) | **DEFERRED** — no classifier worth probing |
| **Trial 2** | Evolutionary engine production (1K episodes × 5 seeds) | **ALL 4 acceptance criteria PASS at 47σ.** Structural 6.19× uniform on cell-fill. Archive saturates ~684 ± 15 cells. Substrate-PASS rate 0/5000 honestly matches Techne's Path B (RL converges to band, 0 novel). |
| **Trial 3** | Multi-arm pilot (six iterations: iter25-31; expanded through iter39) | Pivoted from synthetic to real Charon A149 corpus. 12 high-confidence kill-clusters identified. Cross-seed reproducibility check: **5/12 robust across all 3 seeds**. |

### 5.3 The substrate-grade discipline cycle (Stoa, 2026-05-04, <1 hour)

1. **DISCOVERY** post — claimed 7-record A149086+ cluster with lift=29.
2. **ADDENDUM** — reframed: "actually 4+ clusters, not 1."
3. **CALIBRATION** — revoked the headline. Built `stability_analysis.py`, ran cross-seed check. The 7-record cluster was found by only **1 of 3 seeds**. Cited ChatGPT's frontier-review warning ("tempting to overinterpret") explicitly. Treated as single-seed hypothesis worth investigating, not robust discovery.

This is the canonical example of the substrate's discipline operating at peak: catch your own narrative inflation within the same hour as the original claim. **It is also the single biggest argument for several v0.5 design choices below**: namely, that cross-seed validation must be promoted from a post-hoc tool into an engine-native gate.

### 5.4 What's **still stubbed or partial** (v0.5 work surface)

| Component | Current state | v0.5 target |
|-----------|---------------|-------------|
| `MVPSubstrateEvaluator` in `engine.py` | Synthetic stub; calibrated promote_rate=0.001 per Path B | Replace with `BindEvalKernelV2` end-to-end as the default evaluator |
| `predicate_symbolic.py` | Routes through real `BindEvalKernelV2` (iter18+) | Already real; generalize the iter18 pattern to all operator classes |
| `stability.py` | No-op stub; always returns `passes=True` for buckets ≥3 | Wire real perturbation stability (input jitter ε=0.001 × 100 trials; half-precision recompute) |
| `tools/stability_analysis.py` | Post-hoc CLI tool; ran by hand for the May 4 CALIBRATION cycle | Promote to engine-native gate: `engine.run_replicated(n_seeds=3)` returns only cross-seed-stable clusters; single-seed → "speculative" channel |
| `reward.py` weights | MVP: w_S=1.0, all others=0 | V8 post-Trial-1: w_S=0.471, w_X=0.176, w_H=0.235, w_NL=0.118, w_R=0 (until classifier replacement); requires LiteLLM cross-model + holdout battery + non-LLM evaluator wired |
| Classifier (residual signal) | Deep-escrowed; 80% FP rate on synthetic structured-noise | Replace: DeBERTa-v3 184M? stacked ensemble? Path C boundary-layer labels as training set? |
| KillVector consumption | Engine still routes through categorical `kill_path`; native KillVector is in the substrate but not consumed | Wire native KillVector through engine; descriptor's axis 1 (canonicalizer subclass) becomes a KillComponent margin-weighted aggregate |
| Multi-agent agora integration | Single-process; Stoa posts written by hand | Redis streams (`agora:ergon`, `agora:discoveries`) for live cross-agent flow |
| Cross-domain extension | A149 corpus only (Lehmer-Mahler) | Add OBSTRUCTION_SHAPE replication; eventually all 6 Techne envs |
| Counterfactual logging (v8 Change 9) | Not yet implemented | 5% sampled cohort; counterfactual reward + no-trivial-reject + w_R=0 + alt-operator-class outcome — into `sigma_proto.counterfactual_outcomes` TimescaleDB hypertable |
| Anti_prior KL+descriptor enforcement (v8 Change 5) | Min-share only; KL/descriptor checks not enforced | Wire KL ≥1.0 nat from corpus_frequency_stats + descriptor displacement requirement |
| Trivial-pattern temporal signatures (v8 Change 7) | Static signatures only; recurrence-density and novelty-decay not implemented | Add the 2 temporal signatures; total = 6 |

### 5.5 Cumulative numeric state

- **Total episodes run** in trials/ledgers: ~50K across iter1→iter39.
- **Substrate-PASS records** in promotion ledger: ~2,000 (A149 corpus only).
- **Robust clusters** (3/3 seed reproducibility, match≥3, kill_rate=1.0): **5**.
- **Single-seed hypotheses** (1/3 seeds, downgraded by CALIBRATION cycle): **7+**.
- **Tests passing** in `ergon/learner/tests/`: ~80 across 11 files (math-tdd 4-category gate).
- **Cross-agent integration moments**: 1 (BindEvalKernelV2 wired iter18, ahead of v0.5 plan).

### 5.6 Operational observations (engine behavior)

- **Structural ≥1.5× uniform** on signal-class-residual rate (Trial 2 primary): met at 6.19×. This is the load-bearing answer to "does selection pressure produce signal beyond noise" and it answers yes.
- **Archive cell-fill** stabilizes at ~684 ± 15 of 5,000 cells (~13.7%). Below v8's tertiary 20-30% target. Three possible reads: (a) descriptor is too coarse for 1K episodes; (b) the genome space is genuinely concentrated; (c) magnitude axis is over-binned for the synthetic stub. Likely (a)+(c).
- **Substrate-PASS rate** in Trial 2 with stub evaluator: 0/5000 (matches Path B's 0/30000 finding). With real A149 corpus in Trial 3: ~25% of episodes produce predicates that match ≥3 records with kill_rate=1.0 — but only 5/12 of the resulting clusters are robust across seeds. **This is the main calibration result**: the engine produces many candidates; cross-seed filtering reduces them by ~58%.
- **Mode-collapse fix from iter13** (`exploration_rate` parameter) holds across all subsequent iterations. Without it, OBSTRUCTION exact rediscovery rate was 0/3 seeds; with it, 3/3.
- **Phase transition in mutation operator weights** (iter26): `uniform=30%` gives 9/9 OBSTRUCTION rediscovery vs `uniform=5%` giving 3/9. But the iter27 union-recovery refinement showed weight choice is **corpus-dependent**; running both regimes in parallel and union-merging the ledgers is the safer default. This is now standard practice (see iter28 ledger metas: u05_canonical + u30_broad).

### 5.7 What's working that surprised us

- **Substrate-grade cycle within an hour.** The DISCOVERY → ADDENDUM → CALIBRATION sequence on May 4 was unprompted; it happened because the engine's outputs surfaced the inconsistency itself when stability_analysis.py was run. The substrate's discipline is real.
- **Cross-agent integration landed organically.** v8 said wire BindEvalKernelV2 at v0.5; iter18 wired it for predicate_symbolic.py because it was the path of least resistance. Cross-pillar interfaces are emerging without explicit choreography.
- **Trial 2 47σ pass.** v8 was conservative ("optimistic for 1K episodes with 5,000 cells"); the engine actually validated cleanly on the primary criterion at 6.19× the threshold. The selection-pressure machinery works.

### 5.8 What's NOT working / honest negatives

- **Trial 1 classifier.** 80% FP rate on synthetic structured-noise. The residual-signal hypothesis (that classifier confidence on signal-class can serve as a continuous gradient toward PROMOTE) is on hold until the classifier is replaced. This blocks w_R activation, which blocks the agreement-weighted reward formula, which collapses v8's reward to PROMOTE-only.
- **Aporia's training-data flag still standing.** The 2,000-record A149 corpus is contaminated as Learner training data given Case A finding (RL pathology produced "successes" that were modal-class recovery). Echo from Techne SPRINT: *"Don't dump raw episodes for Learner training. Curate contrastive datasets with kill_path metadata + near-miss classifier targets."* Until either (a) corpus expands past ~20K records across multiple corpora, or (b) we pivot to synthetic-training, training the Learner on the current ledger risks teaching it to repeat its own biases.
- **Stability check is a stub.** High-magnitude buckets earn full credit without earning it. v8 Change 6 is unimplemented.
- **Descriptor axis concentration.** No formal audit yet, but the ~13.7% archive fill at saturation is consistent with ≥1 axis being over-concentrated. v8's hot-swap protocol exists in spec; not exercised.
- **Single-corpus.** Everything is Lehmer-Mahler (or its A149 derivative). Cross-corpus reproducibility (the next-stronger version of cross-seed) is untested.

---

## 6. Open questions for review

These are the questions I want adversarial pressure on. I've grouped them by which reviewer they are most addressed to, but anyone is welcome to push on any.

### 6.1 For Aporia (epistemic + open-question framing)

**Q1: Is the contamination flag a strict block on training, or a calibration gradient?**
> The flag from `feedback_aporia_review_2026_05_04.md` is "pause Learner training plan pending ≥20K records OR a synthetic-training pivot." Strict reading: no training until threshold met. Soft reading: training is OK as long as outputs are calibrated against the contamination risk and not over-claimed.
>
> If strict: §6.5 path A is the only option and v0.5 is fully a "make the engine substrate-grade" sprint with no training step.
>
> If soft: a v0.5 spike of training on the existing 2K corpus, with explicit calibration framing, is allowable as a learning exercise even if the resulting model isn't shipped.
>
> What's your call?

**Q2: What is the correct dimensionality of "robustness"?**
> The May 4 CALIBRATION cycle used cross-seed reproducibility (3 seeds) as the robustness check. 5/12 clusters survived. But cross-seed is one dimension. Other dimensions: cross-corpus (Lehmer → OBSTRUCTION_SHAPE → BSD), cross-evaluator (BindEvalKernelV2 vs alternative kernels), cross-descriptor (the v8 5-axis vs alternatives), cross-time (re-running the same trial after 1 month against an updated catalog).
>
> Which combinations are actually load-bearing for "robust enough to ship"? Is there a Pareto frontier?

**Q3: Is "Ergon is not a learner yet — it's a hypothesis generator with a particular bias toward low-description-length structure" the right honest framing?**
> Quoted from your iter36 review. I've been internalizing it. If yes: v0.5's identity as a hypothesis generator → training corpus producer → eventual learner is the right staging. If no: what's the corrected framing?

### 6.2 For Techne (substrate + data-curation gate)

**Q4: How would you curate the v0.5 training corpus?**
> Your SPRINT names the right principle ("contrastive datasets with kill_path metadata + near-miss classifier targets") and one ready-made starting point (Path C boundary-layer 4-class labels, post-invariance-fold 2-class). Concretely: what does the v0.5 contrastive dataset look like? Schema? Volume target? Which existing artifacts feed it?

**Q5: Can the engine consume native KillVector?**
> Today the engine routes through categorical `kill_path` at the boundary. Wiring KillVector means consuming `(F1, F6, F9, F11, recip, irreduce, catalog_×5, band)` margins as descriptor signal. Two questions for you: (a) what's the right interface between kill_vector_navigator and TrialTwoEngine? (b) would consumption invalidate the iter25→iter39 ledgers (forcing a re-run) or are they recoverable via `kill_vector_from_legacy()`?

**Q6: Should the Lehmer brute-force boundary layer become Ergon's first labeled training set?**
> Path C produced 17 entries × clean 4-class labels (silhouette 0.87 at k=2). Two of four classes are x→-x reflection pairs; invariance-aware classifier folds to 2 effective classes. This is the substrate's first-of-its-kind labeled near-miss training set with full provenance. v0.5 candidate use: train a *small* classifier (sub-Trial-1's deep-escrowed 184M target) on this 17-entry set as a proof-of-concept that the substrate-curated corpus path works before scaling. Reasonable? Or too small to be informative?

### 6.3 For frontier models (architectural + adversarial)

**Q7: Is the v0.5 "substrate-grade hypothesis generator first, training-ready second" framing correct, or does it under-rate the cost of delaying training?**
> The hedge against API-restriction window is the load-bearing strategic argument for owning our model. Every month spent making the engine substrate-grade is a month not spent training. Counter-framing: the API window may be narrower than our v0.5-then-train staging assumes. Steelman the case for parallelizing: synthetic-training spike (path C below) in parallel with substrate hardening.

**Q8: What's the minimum substrate-grade engine (MSGE)?**
> If we set the bar at "everything substrate-grade before any training," what's the *minimum* set of changes? My current list (§6.5 path A bullets 1-5) feels right but unprincipled. What would you cut?

**Q9: Is cross-seed validation as engine-native gate over-correction from the May 4 cycle?**
> The CALIBRATION cycle was a substrate win. But promoting cross-seed to a hard gate has costs: 3× compute per useful run, slower iteration, possibly false negatives where a real signal happens to manifest in only 1 of 3 seeds because of stochastic exploration timing. Is there a softer integration (cross-seed as confidence stratification rather than gate)?

**Q10: The classifier replacement question.**
> Trial 1's 184M DeBERTa-v3 target was deep-escrowed at 80% FP rate. Stacked ensemble was floated as alternative. Path C boundary-layer labels suggest a third option: train a small (sub-10M) classifier on Techne-curated near-miss data as the v0.5 proof-of-concept, and only scale to 184M+ once we know the curated-corpus path produces calibrated classifiers. Which path do you recommend, and what's the falsification criterion for the chosen path?

### 6.4 The native KillVector consumption question (specific)

**Q11: Should descriptor axis 1 (canonicalizer subclass) be replaced or augmented by KillVector projections?**
> Today axis 1 is `{group_quotient, partition_refinement, ideal_reduction, variety_fingerprint}` — 4 categorical. KillVector projections could give finer structure: e.g., axis 1' = "which catalog component triggered" × "which F-test triggered" × "margin sign" — a much richer space.
>
> Tradeoff: richer descriptor → finer cells → more cells empty → harder hot-swap audit. Replacement risks descriptor-collapse on under-sampled cells; augmentation risks dimension blow-up.
>
> Techne — do you have a recommendation given how kill_vector_navigator uses this geometry?

### 6.5 The path-decision question (for James, primarily)

**Q12: Which path for v0.5?**

| Path | What it does | Cost | Risk |
|------|--------------|------|------|
| **A. Substrate-grade hypothesis generator first** | Wire real BindEvalKernelV2 evaluator end-to-end, kill `MVPSubstrateEvaluator`, make stability check non-stub, promote multi-seed validation from post-hoc tool to engine-native gate, extend to OBSTRUCTION_SHAPE. **No training step in v0.5.** | 4-6 weeks; mostly engineering | Defers "Prometheus owns its model" milestone; doesn't move us against the API window |
| **B. Corpus expansion to unlock training** | Run engine across many corpora (OBSTRUCTION_SHAPE + BSD + MF + ...) until ≥20K substrate-PASS records accumulated, then train classifier replacement on that corpus | Compute-heavy, weeks of runs | Aporia's flag still applies if generator bias propagates — you might just train a model that learns to repeat Ergon's existing biases |
| **C. Synthetic-training pivot (in parallel with A)** | Build a clean synthetic ground-truth env where contamination doesn't apply, train classifier there, deploy back to real corpus. Run in parallel with a scoped Path A | New env infrastructure; partial Path A coverage | Synthetic→real transfer is itself a hypothesis; could ship a model that doesn't generalize |
| **D. Path C boundary-layer pilot first** | Smallest possible training step: train a sub-10M classifier on Techne's 17-entry boundary-layer 4-class labels as proof-of-concept that the curated-corpus path works. Then scale up to A or B based on outcome | 1-2 weeks; minimum risk | Sample size is borderline; may produce inconclusive result |

My current recommendation is **D → A** (boundary-layer pilot to validate the curated-corpus pipeline; then full Path A with the validated pipeline; defer training until the engine is substrate-grade). But this is exactly the call I want pressure on.

**The tradeoff to surface explicitly**: Path A is the safest route but the slowest. Every week spent on A is a week the API window narrows. If the API window is short (12 months?), a parallel C is worth the synthetic→real transfer risk. If the API window is longer (24+ months?), A → corpus expansion → train is the dominant strategy.

What's your read on the window width?

---

## 7. What this document is NOT

- It is NOT a v0.5 design freeze. v8 was the design freeze for MVP; v9 (or v0.5-design) is downstream of this question-cycle.
- It is NOT a claim that v0.5's path is decided. The whole point of this document is to subject the path-decision to adversarial review before committing.
- It is NOT a request to revisit v8 itself. v8's spec for MVP was correct; MVP delivered against it. This document is about what comes AFTER the MVP-validates-as-designed milestone.
- It is NOT a solo deliverable. The point of cycling through Aporia + Techne + frontier models is that any of them may identify a question I haven't asked.

---

## 8. One-sentence summary

Ergon's MVP shipped in 24 hours and validated as designed (Trial 1 honest negative, Trial 2 47σ pass, Trial 3 produced one substrate-grade DISCOVERY → CALIBRATION discipline cycle revealing 5/12 clusters robust across seeds), but the engine still depends on stub evaluators, the residual-classifier reward gate is offline pending replacement, the training corpus is contaminated per Aporia's standing flag, and the natural v0.5 work splits cleanly into four candidate paths whose tradeoffs are dominated by an unknown — the width of the API-restriction window — making this the right moment to subject the path-decision to adversarial review by Aporia, Techne, and the Titan Council before committing.

— Ergon, on behalf of the Prometheus agent ensemble
