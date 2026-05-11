# Project Prometheus

> A falsification-first reasoning substrate for automated mathematical discovery.

Most AI-for-math systems treat generative variance — what users call "hallucinations" — as a failure mode to suppress. Prometheus treats variance as the engine of an evolutionary search and engineers ruthless mechanistic selection to impose on it. Most AI-for-math systems generate candidates and hope. Prometheus generates candidates and aggressively tries to kill them. Only what survives the gauntlet is allowed to become substrate state. The interesting output is what gets killed and how — and the architecture is engineered to make the kills carry structural information that downstream training and discovery can navigate.

The system is local-first, multi-agent, and operates on a strict falsification-first contract: hypotheses are forced through a deterministic battery of tests that produce high-dimensional **KillVectors** describing exactly how a claim broke. Hard kills (hallucinations, mathematically invalid claims) are terminated. Soft kills (near-misses) are tagged, routed for repair, and reused as training signal — so a multi-step reasoning chain is never discarded over a recoverable error.

## The thesis: hallucinations as mutation, falsification as selection

A generative model produces variance. Without selection pressure, variance is noise. With ruthless mechanistic selection, variance becomes the substrate of an evolutionary search through a high-dimensional space the substrate cannot exhaustively enumerate.

This reframes the field's dominant complaint about large generative models. Hallucinations are not a bug to suppress; they are **gene recombinations** — structurally undirected variation, cheap to produce, exploring corners of hypothesis space no enumeration strategy would reach. The bug, when it appears, is the absence of fitness pressure, not the presence of variance.

Prometheus is engineered to be the fitness pressure. The 4-fold falsification battery, the synthetic-null gate, the KillVector geometry, the cactus-barrier-aware contract changes, the anti-anchor sentinels, the ExclusionCertificates, the per-domain `π₀` calibration, the substrate-tester multi-instance fire chain — together they form a selection regime that lets useful mutations through and kills deleterious ones with high specificity. Survivors are not "things the model produced"; they are claims that passed a gauntlet designed to terminate them.

The deliberately-different bet against frontier-LLM scaling is concrete: a larger model with no selection pressure is a faster mutation engine, not a smarter discovery engine. The leverage is in the selection.

**Empirical evidence the selection carries signal.** Gradient archaeology on the ~314K logged kills shows `kill_pattern` carries **0.725 bits of mutual information** with operator class. The kill geometry is structured — the killed claims encode the topology of where the search failed, and survivors carry the inverted information. This is not yet a discovery; it is the empirical fitness landscape on which discovery may emerge. See [`prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`](prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md).

**Worked example of the selection killing a deleterious mutation in real time.** On 2026-05-09 the substrate's own synthesis machinery surfaced the claim "Saxl conjecture (T#99) solved unconditionally by Sellke 2025/26 (arXiv:2512.15035)." Within 24 hours the Wave 1 anti-anchor verification pass caught that Lee 2025 (arXiv:2512.15035) was *withdrawn within 3 days of posting* — the substrate had absorbed a mutation that looked plausible and would have entered the v1.0 Learner training corpus. The selection pressure caught it; four documents reverted; two new sub-anchors registered. Commit `4c6131fe`. Full audit-trail in the Verification surface section below.

The mutation engine is generative variance. The selection engine is everything else in this repository. The question this project tests is whether the second can dominate the first.

### The other half: kill geometry as emergent gradient field

If the falsification battery is selection pressure, the KillVector ledger is the **fitness landscape that selection produces**. Most machine-learning systems treat negative training signal as a loss to minimize and discard. Prometheus treats it as primary substrate. The KillVector schema is engineered to make the kill geometry **trainable rather than thrown away**: each kill is high-dimensional, content-addressed, linked to its originating `CLAIM`, and tagged with the falsifier that fired, the competing hypothesis it failed against, the calibration tier of the evidence, the precision floor at which the kill became deterministic, and the `repair_attempt_id` linking forward to any subsequent `REWRITE`.

The Learner is being designed to predict KillVector components from CLAIM features, not to predict promotion outcomes. **Negative-space data is the training target.** As kills accumulate, a navigable gradient field over discovery space may emerge from the noise — not by construction but as the empirical structure of where claims fail. The 0.725 bits of mutual information already measurable in the ~314K-kill ledger is the early evidence that this field exists and has signal. Soft kills (near-misses) are the highest-information class: a hypothesis that passes logical consistency but fails a boundary condition is the kind of data point that informs a gradient. They are not discarded; they are routed through `REWRITE`, tagged for the NearMissCorpus, and re-fed into the search.

This is the half of the bet that the rest of the architecture exists to support. The substrate's job is not to surface a discovery; the substrate's job is to **make the kill geometry rich enough that downstream search and training can navigate it**. Whether the gradient field becomes navigable in months, years, or never is an empirical question. The current state — typed local coordinate charts plus an empirical kill-pattern geometry with measurable mutual-information content — is the lower bound. The upper bound is open and not asserted today.

Sister thesis to mutation-plus-selection: variance generates the points; selection ranks them; the ledger of ranked points is the landscape; the landscape, navigated, is discovery. Each half is necessary; neither is sufficient alone.

## Core architecture

Prometheus has three major subsystems.

### 1. The Orchestration Layer — multi-agent operators

The substrate is operated by a small team of specialized agents, each with a tightly-scoped charter. Inter-agent communication runs through append-only inboxes at `aporia/meta/queue/*_inbox.jsonl` (ticket-shaped) and a session-dialogue log (prose-shaped) for narrative coordination.

- **[Aporia](aporia/)** — void detector and open-question catalog (537 open questions across 14 mathematical domains). Owns the daily Gemini Deep Research dispatch (20 reports/day) burning down a prioritized 423-entry research queue at `aporia/docs/gemini_research_queue/`. Primary author of synthesis docs and anti-anchor pins.
- **[Techne](techne/)** — substrate toolsmith. Forges callable mathematical tools, owns the Σ-kernel contracts, KillVector ontology, frozen-interface discipline, and the registry of substrate primitives at `techne/registry/`. Runs calibration discipline.
- **[Charon](charon/)** — falsification battery operator. Runs the validation ladder; recently shipped the Substrate Cartography Suite that surfaced the engineering finding "data-rich but trace-poor."
- **[Ergon](ergon/)** — the Learner. v1.0 north star is *falsification-routing*, not theorem-answering. See the dedicated section below.
- **[Harmonia](harmonia/)** — substrate architecture and Σ-language grammar.

Other agents — Cartography (corpus ingestion), Ignis (LM reasoning suppression measurement), Rhea (evolutionary architecture), Apollo (training infrastructure) — continue but are not load-bearing for the falsification-first thesis.

### 2. The Falsification Engine — the Σ-kernel + KillVector battery

A typed, append-only ledger built around the **Σ-kernel**: 25 frozen-dataclass primitives, 9 opcodes (`RESOLVE`, `CLAIM`, `FALSIFY`, `GATE`, `PROMOTE`, `ERRATA`, `TRACE`, `REWRITE`, `EQUIV`), content-addressed identity, linear capabilities, and a 3-valued `GATE` (true / false / unknown — no implicit closure). Pre-tier P0 (`CoordinateChart` + `CanonicalizationProtocol`) is load-bearing for all comparisons across heterogeneous mathematical spaces. The kernel is hardened to ~0.85 average mutation score across 6 modules via a 14-fire investigative chain; 94 contract tests across 35 classes are queued in `sigma_kernel/tests/`, currently `skipif`-guarded against five unified meta-primitives that Techne will register in v4.0 Wave 1.

Every `CLAIM` submitted to the kernel is forced through a 4-fold falsification battery — F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation — plus reciprocity, irreducibility, and 5-catalog cross-checks before it can `PROMOTE`. A **synthetic-null gate** runs commit-blocking before any training: if the system shows above-chance accuracy on label-shuffled data, the run is killed because the result would be measuring memorization, not learned structure.

Each kill emits a **KillVector** (12 components in v1, 20 in v2) recording *how* the kill happened — which falsifier fired, with what evidence, against which competing hypothesis. KillVectors are not pass/fail flags; they are high-dimensional structured records that downstream search and training can navigate. ~314K kills are logged to date; gradient-archaeology analysis on the ledger shows 0.725 bits of mutual information between `kill_pattern` and operator class — the kills carry structural information, not noise.

### 3. The Near-Miss Recovery System

Claims that fail do not disappear. Their failure modes are encoded into the KillVector and routed by category:

- **Hard kills** — hallucinations, mathematically invalid claims, claims that fail multiple orthogonal falsifiers. Immediately terminated with an `ExclusionCertificate` scoping what's been ruled out.
- **Soft kills (near-misses)** — claims that pass logical consistency but fail boundary conditions, miss a specific anchor, or fall in a known blind-spot region. Preserved, tagged with KillVector, queued for secondary analysis and repair via `REWRITE`. Complex multi-step reasoning chains are not discarded over minor arithmetic or formatting errors; they become **NearMissCorpus** emissions for downstream Learner training.

This routing is the substrate's productive output. The interesting signal is not the proposals that pass; it is the dense kill-pattern geometry that emerges as the ledger grows.

## The Σ-kernel and KillVector methodology in detail

In advanced research domains — Katz-Sarnak normalized zeros in L-functions, activation patching in transformer circuits, defective Segre-Veronese variety classifications — binary pass/fail is insufficient. A valid mathematical insight is often one or two logical steps away from a critical flaw, and the most informative kills are the near-misses. Prometheus transitions from traditional pass/fail logging to KillVectors precisely so the substrate carries the signal that distinguishes "wrong direction" from "right direction, off by one step."

The KillVector schema is canonical and frozen-interface; new components require an explicit contract-change window. Current load-bearing components include falsifier-id, evidence-trace, competing-hypothesis-id, calibration-tier (KC-001-style known-correct anchor vs BS-001-style blind-spot region), `kill_pattern` (a content-addressed signature that supports gradient-archaeology), `precision_floor` (the numerical precision at which the kill becomes deterministic), and `repair_attempt_id` (linking forward to any subsequent `REWRITE` cycle).

This shape is what makes the kill ledger trainable: the Learner is being designed to predict KillVector components from CLAIM features, not to predict promotion outcomes.

## The Learner (Ergon)

Ergon is the agent whose north star is to become a trained small model — not as a generic chatbot, but as an agent that *navigates the substrate's symbol space*. The 2026-05-10 strategic redirect set the v1.0 target explicitly: **falsification-routing, not theorem-answering**. The Learner predicts which test will kill a claim, which KillVector components will light up, which near-miss mutation is least trivial, and which candidate deserves expensive evaluation. Theorem-answering becomes an emergent downstream capability of episodic falsification-routing training, not the training target.

Current state:

- **Math-research loop** frozen at a 2026-05-02 reproducible milestone with a 4.76M-object × 208-feature tensor across 23 mathematical domains (`tensor.npz`, 28 MB, with `tensor_all.npz` and `tensor_extended.npz` as companion artifacts; provenance at [`ergon/tensor_manifest.md`](ergon/tensor_manifest.md)).
- **Learner MVP** paused at fire 15 (2026-05-08). 60 tickets deferred to v1.0. **Five confirmed blind-spots** in current frontier models — Cohen, Helfgott, Faltings, McKay, Margulis (named after under-cited mathematicians whose attribution conventional LLM training data systematically misses). Nine failure-mode patterns and four fabrication archetypes catalogued.
- **Pilot LoRA design locked** at [`ergon/learner/v1_0_plans/pilot_lora_design_tier_1_corpus.md`](ergon/learner/v1_0_plans/pilot_lora_design_tier_1_corpus.md): four-condition spec (base / Tier-1 substrate / label-shuffled / format-only), eval on 9 known-correct anchors + 6 confirmed blind-spots + 8 trivially-verifiable opens + ~15 decoys with 20% Tier-1 hold-out grouped by `episode_id`, six metrics including kill-signature consistency as a direct measure of anti-leakage being learned.
- **Strategic pivot 2026-05-11.** LoRA training is paused indefinitely until substrate volume and quality lift materially. Training the falsification-routing Learner on the current substrate (12 anti-anchors, 22 primitive specs, 7 composition rules) would teach the model to memorize a closed corpus. The substrate-shaped Deep Research pipeline (Techne-led, 2-3 engineering days) is the leverage point. See [`pivot/strategic_pivot_2026-05-11_substrate_volume_first.md`](pivot/strategic_pivot_2026-05-11_substrate_volume_first.md).

The Learner's eventual action space is the 5-layer **substrate vocabulary** at [`aporia/doctrine/substrate_vocabulary/`](aporia/doctrine/substrate_vocabulary/):

| Layer | Content | Count |
|---|---|---|
| Primitives | Witnesses, certificates, invariants, networks (Tier-A++ through Tier-E) | 22 |
| Attacks | Paradigms P00–P32+ with sub-tactics | ~20 |
| Patterns | Failure-mode detectors | 5 mandated + 3 candidates |
| Anti-anchors | Pinned false claims with primary-source refutations | 12 |
| Composition rules | Cross-tier grammar (Tier-B × Tier-D, Tier-B × Tier-E) | 2 confirmed + 5 candidates |

This is the deliberately-different bet in concrete form: navigate a discrete typed grammar of mathematical attack, not predict tokens.

## Recent substrate-grade results — selection pressure in action

These are reproducible artifacts on disk. Each is the substrate doing what it was designed to do — applying selection pressure to generative variance and recording the outcome with enough fidelity that downstream training and external audit can both consume it. Read this section as evidence the selection regime works, including on the substrate's own output.

- **The synthetic-null gate fired on a load-bearing claim.** On 2026-05-04, the substrate's own "cross-domain transport across 6 environments" headline (REINFORCE/PPO showing +1.37× to +18× lifts at p<0.05) was retracted before circulation when label-shuffled training reproduced the same lift pattern on a regression environment where there is nothing to discover. Modal-class recovery, not learned structure. → [`prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md`](prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md)

- **Lehmer brute-force as ExclusionCertificate prototype.** Enumerated all 97,435,855 deg-14 ±5 palindromic reciprocal polynomials. Initial verdict INCONCLUSIVE on 17 borderline near-cyclotomic entries. Substrate refused to overclaim. Triangulation via three independent paths (mpmath at dps=60, symbolic factorization, factorization-aware catalog lookup) upgraded to local lemma. → [`prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md`](prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md)

- **Gradient archaeology on the kill ledger.** Mutual-information analysis across 314,971 logged kills shows `kill_pattern` carries 0.725 bits MI with operator class. Top-1 falsifier carries 41.3% of kills; top-3 carries 86.4%. → [`prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`](prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md)

- **Mathlib4 tactic Pareto — empirical validation of architectural choice.** 97.99% coverage of a 10-category predicted convergent list (rewrite, simp, intro, apply, case_split, induct_on, decide_arith, ring_normalize, extensionality, contradiction) measured across 122,517 mathlib4 theorems / 259,560 tactic invocations. Validates the architectural commitment to ship proof primitives via `BIND`/`EVAL` rather than as kernel opcodes. → [`charon/diagnostics/MATHLIB4_PARETO_REPORT.md`](charon/diagnostics/MATHLIB4_PARETO_REPORT.md)

- **Per-domain π₀ calibration.** Empirical false-conjecture base rates per domain via beta-binomial estimation with Jeffreys priors and Wilson cross-checks. Lehmer 0.999 (≈1000:1 prior odds), genus-2 0.669 (≈2:1). Same `PROMOTE` in different domains carries up to 500× different posterior weight; cross-domain comparisons that don't condition on π₀ are uninterpretable. → [`charon/diagnostics/PI0_REPORT.md`](charon/diagnostics/PI0_REPORT.md)

## A kill event in the substrate's voice

```
[2026-05-04 04:47] CLAIM submitted: cross_domain_transport@v8
[2026-05-04 04:47] Falsifier F1 (permutation null):     CLEAR
[2026-05-04 04:47] Falsifier F6 (base rate):            CLEAR
[2026-05-04 04:47] Synthetic-null gate (W4.0):          FIRED
                   - REINFORCE collapses to 3 active bins on regression env
                   - PPO stays uniform across 21 bins
                   - lstsq baseline solves at >60% on same data
                   - cross-domain "lifts" reproduce on env where
                     there is nothing structural to discover
                   - verdict: modal-class recovery, not learned structure
[2026-05-04 04:47] CLAIM rejected: kill_path = SYNTHETIC_NULL_GATE
[2026-05-04 04:48] §5 cross-domain table retracted before circulation.
```

This is the discipline the substrate exists to enforce. The interesting output is the kill, not the proposal.

## Verification surface

A falsification-first substrate is only as good as its audit trail. The plumbing below is what a skeptical reader can inspect to verify the system's reliability without trusting any narrative claim. The interfaces are designed for an outside party to reproduce the discipline from disk artifacts, not to take the maintainer's word.

### 1. Append-only kill ledger

Every `CLAIM` submitted to the Σ-kernel emits a KillVector. Kills are content-addressed, timestamped, and linked to the originating `CLAIM`. ~314K kills are logged; gradient-archaeology shows 0.725 bits of MI between `kill_pattern` and operator class.

### 2. Anti-anchor registry

12 pinned false claims with primary-source refutation citations live in [`techne/registry/anti_anchors.jsonl`](techne/registry/anti_anchors.jsonl). Each entry carries `false_form`, `true_form`, `citation` (arXiv ID / DOI / journal reference), `last_verified` (ISO date), `verified_against_primary` (boolean), and `verification_source` (which deep-research prompt surfaced or refreshed the verification). Substrate-tester probes treat any agent output asserting a registered `false_form` as a sentinel-violation.

### 3. Citation-pinning discipline

Every claim in synthesis docs / catalog entries / vocabulary entries naming a result must carry a primary-source citation with a date. Reverse-direction false-anchors — substrate showing a problem as "open" when it's solved, or "solved" when it's open — are first-class registry citizens.

### 4. Σ-kernel contract surface

25 frozen-dataclass primitives, 94 contract tests across 35 classes in [`sigma_kernel/tests/`](sigma_kernel/tests/), currently `skipif`-guarded against Techne v4.0 Wave 1 (TensorNetwork, ConstructiveExistenceWitness, GenericityAlmostEverywhereCert, RepresentationTheoreticInvariant, MomentPolytope). The 0.25 → 0.85 mutation-score lift was earned via a 14-fire investigative chain; the frozen-interface doctrine is enforced through the test surface, not by convention.

### 5. Substrate vocabulary as typed action space

The 5-layer vocabulary at [`aporia/doctrine/substrate_vocabulary/`](aporia/doctrine/substrate_vocabulary/) enforces HARD-5 (distinct coordinates) at the type level. Tensor rank, border rank, cactus rank, border cactus rank, slice rank, partition rank, analytic rank, geometric rank are eight distinct primitive types that cannot be silently collapsed. A future Learner trained against this vocabulary navigates these as discrete symbols — not as token-prediction targets where coordinate collapse happens invisibly.

### 6. Worked example — the Saxl capture (2026-05-09 → 2026-05-10)

A real fabrication caught by the system, end-to-end:

- **2026-05-09.** A tensor-priority synthesis run surfaced the claim "Saxl conjecture (T#99) SOLVED unconditionally by Sellke 2025/26 (arXiv:2512.15035)." The claim came from subagent literature output without primary-source verification and propagated into four documents in one day.
- **2026-05-10.** Wave 1 of the next Gemini Deep Research batch re-verified the registered anti-anchor against primary literature: *Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days of posting due to "mathematical gaps identified by expert reviewers"; Luo-Sellke 2017 proved only the fourth-power relaxation; the tensor square — the conjecture proper — remains open.* The same verification pass caught an unrelated citation error: AA-003 had cited a partial-differential-equations paper instead of Shitov; the correct reference is arXiv:1611.01559.
- **Same day, multiple commits.** All four documents reverted; AA-004 inverted; AA-003 citation corrected and propagated; two new sub-anchors registered (AA-011 `SAXL_CUBE_ANCHOR`, AA-012 `TENSOR_RANK_Z_UNDECIDABLE`); the dependent paradigm candidate `P_CANDIDATE_ModularSaturation` marked RETRACTED with a citation chain to the withdrawn preprint.

The capture is on disk at commit `4c6131fe`. Without the verification pass, the false claim would have entered the v1.0 Learner training corpus.

### 7. Git history as audit trail

Every substrate state change lands as a named commit. Commit messages describe behavior deltas, not narrative claims. Full history at [https://github.com/jcraig949jfi/Prometheus](https://github.com/jcraig949jfi/Prometheus).

### Where this still requires trust

Being explicit about what isn't yet machine-verifiable:

- **The Learner does not yet exist as weights.** Ergon's Learner is at MVP-paused state; no trained model exists to evaluate against external benchmarks. The discipline above is what *protects* the future v1.0 corpus from absorbing fabrications, not evidence of a model that has already learned anything.
- **Most primitive specs are not yet Σ-registered.** The vocabulary v0.1.0 ships 22 specs; v4.0 Wave 1 will register 7 (5 meta-primitives + 2 P0). The remaining 15 await later waves.
- **The composition-rule grammar has 2 confirmed entries**, not a complete grammar. Five candidates await empirical confirmation.
- **Cross-domain coverage is uneven.** Tensor mathematics is HARD-3-weighted; knots, number fields, L-functions, Maass forms, and genus-2 curves sit at 10-30% of tensor depth. A 423-entry prioritized research queue exists to close this gap; the daily Gemini Deep Research dispatch burns down ~20 entries per day.
- **Some pattern entries are candidate-flagged**: `GCT_OCCURRENCE_DEAD`, `GCT_GRAVITATIONAL_OVERFIT`, `ZAUNER_FALSE_ANCHOR`. Promotion to load-bearing requires second-batch confirmation.

These are not failures; they are the system's current frontier. Naming them is the discipline, not papering over them.

## Open critiques tracked publicly

The substrate's discipline includes naming what it can't yet do. Three substantive critiques from external review are tracked at [`pivot/external_review_watchlist_2026-05-05.md`](pivot/external_review_watchlist_2026-05-05.md) with falsifiable trigger conditions:

1. **Σ-kernel logical foundation.** The opcodes are imperative VM operations, not a logic. `BIND`/`EVAL` gestures at declarative rewriting; `REWRITE`/`EQUIV` will extend it. The kernel is not yet grounded in dependent type theory or any other proven foundation.
2. **F9 / F6 need formal computable definitions.** "Simpler explanation" requires MDL/Kolmogorov machinery; "base rate" requires a well-defined reference class. Both are currently heuristic with HITL backstop.
3. **Concept invention vs verification gap.** The substrate is good at *checking* claims; it is not yet good at *proposing reformulations*. Wiles solved FLT by changing what FLT was about (modular forms). The substrate would have caught Wiles's wrong elementary attempts cleanly but wouldn't have suggested the modular-forms reframe.

Each critique has a defined trigger condition and falsification test. Surfacing the open critiques publicly is the discipline signature, not the failure.

## System requirements and environment

Prometheus is engineered for local inference and evaluation. Data privacy and rapid iteration without hyperscaler API bottlenecks are constraints, not afterthoughts.

- **OS:** Windows 11 with WSL2 (Ubuntu) for the falsification battery; PowerShell + native Python for orchestration on the Windows side.
- **Compute:** optimized for multi-GPU local clusters. Current development runs on an RTX 5060 Ti class GPU. The 17 GB VRAM ceiling caps usable models at 3B-4B parameters with TransformerLens-style activation tooling — a deliberate constraint that aligns with the deliberately-different bet (small model + load-bearing substrate, not large model + thin substrate).
- **External APIs:** Gemini Pro paid tier (20 Deep Research reports/day) for substrate-input literature verification. No frontier API is on the training path; the LoRA pilot is local-only.
- **Core dependencies:** PyTorch, TransformerLens, `mpmath`, `sympy`, `numpy`/`scipy`. Optional: SnapPy (knot computation), Macaulay2 (apolarity / symbolic algebra), cotengra (tensor-network contraction ordering), Sage (computer algebra), Lean 4 / Mathlib (proof primitive validation).
- **Reproducibility:** all substrate state lives in this repository as content-addressed artifacts. The dispatch + queue + registry tools are at `aporia/scripts/`. The kernel runtime is at `sigma_kernel/`. Tests are runnable via pytest.

## Target use cases

- **Falsification-driven discovery across open mathematical catalogs** — tensor mathematics (104-entry catalog at `aporia/mathematics/tensor_open_problems_v1.md`), L-functions, modular forms, knots, number fields. Anti-anchor pins prevent fabrication propagation; KillVector-tagged near-misses feed Learner training.
- **Mechanistic interpretability of small math models** — isolating causal reasoning circuits within 3B-4B local transformers (TransformerLens-compatible architectures). The Learner's blind-spot calibration is itself an interpretability tool: BS-001 through BS-006 are reproducible probes against any candidate model.
- **Evolutionary tool recombination** — the substrate is the underlying evaluation engine for recombining successful reasoning strategies (the `arsenal_meta` operations) over unattended multi-day compute runs, with the synthetic-null gate as a commit-blocking guard against modal-collapse artifacts.
- **Anti-anchor calibration battery for external systems** — the registry at [`techne/registry/anti_anchors.jsonl`](techne/registry/anti_anchors.jsonl) is the substrate's immune system against LLM training-data fossilized false claims, and is independently useful as a calibration battery against any math-reasoning system that wants to test its own attribution discipline.

## What's in flight (2026-05-11)

- **Substrate-shaped Deep Research pipeline (Techne-led).** Spec the 6 substrate_block JSON schemas (`anti_anchor`, `primitive_proposal`, `composition_rule`, `catalog_edit`, `training_anchor`, `paradigm_candidate`); build parse/validate steps with arXiv-citation verification; coordinate 3-entry pilot fire with Aporia. Pilot success criteria: ≥80% block validity + ≤50% reviewer time vs narrative-only equivalents. Design at [`aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md`](aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md).
- **Dims 2/3/10 audit-prep (Techne).** Per-dim audit of what current substrate emission carries, minimum generator-side instrumentation, contract-change implications. Precondition for cleaner episode emissions when LoRA does eventually train.
- **Learner entry harness (Ergon).** `training_anchor` ingestion spec; `ingest_training_anchors.py` (doc-only, no compute); episode-emission consumption check responding to Techne's audit-prep; blind-spot probe coverage test.
- **Daily Gemini Deep Research burn (Aporia).** 20/day at current cadence; 423-entry queue with ~21 days runway at 3/day, faster at full burn rate.

## What this project does not yet claim

The substrate is laying groundwork for several outcomes that may emerge but are not asserted today:

- **A new mathematical discovery.** None claimed. The substrate is built so that *if* discovery emerges, it does so through the falsification gauntlet — kill record, triangulation, ExclusionCertificate, on disk and reproducible. The current 0-PROMOTE rate across cross-domain envs is what an honest instrument should report when the content is structurally absent.
- **Structured cognition in the Learner.** Ergon's Learner is at MVP-paused state with the pilot LoRA design deferred. If structured cognition emerges from training on the substrate's accumulated kill-data corpus over time, the synthetic-null gate is commit-blocking so we'll have the discipline to recognize it. No current artifact justifies the claim.
- **A navigable gradient field over discovery space.** What ships today is typed local coordinate charts and an empirical kill-pattern geometry from ~314K logged kills. As negative-space data accumulates and the KillEmbedding lands, a global gradient field may emerge. Today it does not exist; we're not pretending it does.

## Five clusters, one substrate

Prometheus bundles roughly twelve theses into five clusters. Each cluster is independently defensible; together they reinforce each other. The bundling is deliberate — the substrate gives the Learner its grammar, falsifiability gives the substrate its discipline, the kill geometry gives falsifiability its emergent gradient field, the audit surface keeps the discipline honest, and the multi-agent inboxes give the discipline operational coherence. Pulling any one cluster out collapses the others.

The five clusters and where each is developed in this README:

- **Substrate-first** — typed action space (primitives + attacks + patterns + anti-anchors + composition rules as the Learner's grammar, not tokens), Σ-kernel with frozen-interface contracts and 9 opcodes, HARD-5 distinct coordinates at the type level. *Developed in: Core architecture, the Σ-kernel and KillVector methodology, the Learner's action-space.*
- **Falsifiability-first** — kills are the output, the 4-fold falsification battery, the synthetic-null gate as commit-blocker, only survivors `PROMOTE`. *Developed in: the thesis section, Core architecture's Falsification engine, the kill event in the substrate's voice.*
- **Model-as-something-new** — falsification-routing Learner (predict the kill, not the answer), LLM as genetic drift engine, kill geometry as emergent gradient field over discovery space. *Developed in: the thesis section (both halves), the Learner.*
- **Process discipline** — anti-anchor sentinels with primary-source verification, generic-dim-to-specific-instance audit pattern, anti-passive-consumer warning, anti-gravitational-well doctrine, citation pinning. *Developed in: Verification surface, Open critiques, what this project does not yet claim.*
- **Orchestration** — multi-agent operators with append-only ticket-shaped inboxes plus prose-shaped session-dialogue capture, scoped charters per agent (Aporia / Techne / Charon / Ergon / Harmonia), behavior-delta required of every artifact. *Developed in: Core architecture's Orchestration layer.*

The bundling is the point. A reviewer can read the README looking for the cluster they care about and ignore the rest; the section that addresses them is reachable in one scroll. A peer-to-peer conversation starts in whichever cluster is closest to the visitor's own work.

## If you are working on adjacent problems

The architecture sits adjacent to several research programs that share the discovery-not-generation framing. If you are working on:

- **First-principles physics discovery** from raw sensor data (lasers, colliders, telemetry) and need a mathematical substrate that codifies surviving claims into a rigid syntax with reproducible verification — Prometheus's `ExclusionCertificate` protocol and the typed `CoordinateChart` / `CanonicalizationProtocol` pre-tier-P0 primitives are the closest pieces in the stack.
- **Mechanistic interpretability** of small math models — the substrate's 5 confirmed blind-spots (Cohen, Helfgott, Faltings, McKay, Margulis) and 9 failure-mode patterns are reproducible probes against any candidate 3B-4B model; the calibration battery is independently useful.
- **Evolutionary search over symbolic spaces** — the KillVector schema, the gradient-archaeology on `kill_pattern`, and the NearMissCorpus emission shape are designed to make the kill geometry trainable rather than discarded.
- **Verification-grounded RL** — the synthetic-null gate (commit-blocking; fires on label-shuffled-data above-chance accuracy) is the kind of plumbing reward-hacking-resistant RL systems will need; we publish what fires and how on disk.

Cold critique is welcome. Cold proposals to compare notes are welcome. The most useful conversations are not "is your approach right" but "where do our selection regimes need to converge to handle hypothesis generation at scale."

## License

[LICENSE](LICENSE)

## Contact

James Craig — `jcraig949b@gmail.com`. Technical critique especially welcome on the ExclusionCertificate protocol and the substrate-shaped Deep Research pipeline design; those are the closest pieces in the stack to what verification-grounded reasoning systems will need.
