# Project Prometheus

> A falsification-first substrate for mathematical discovery.

Most AI-for-math systems generate candidates and hope. Prometheus generates candidates and aggressively tries to kill them. Only what survives the gauntlet is allowed to become substrate state. The interesting output is what gets killed and how.

## The architecture in one paragraph

A typed, append-only ledger built around a 7-opcode Σ-kernel (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) plus a BIND/EVAL extension that binds mathematical objects as first-class substrate symbols. Every claim is forced through a 4-fold falsification battery (F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation) plus reciprocity, irreducibility, and 5-catalog cross-checks before it can PROMOTE. A 12-component KillVector (v2 ships 20) records *how* each kill happened, not just that it happened. ExclusionCertificates scope what's been definitively ruled out. A synthetic-null gate runs commit-blocking before any training: if the system shows above-chance accuracy on label-shuffled data, the run is killed because the result would be measuring memorization, not learned structure.

## Recent substrate-grade results

These are reproducible artifacts on disk. Each is the substrate doing what it was designed to do — including catching its own claims when they don't survive scrutiny.

- **The synthetic-null gate fired on a load-bearing claim.** On 2026-05-04, the substrate's own "cross-domain transport across 6 environments" headline (REINFORCE/PPO showing +1.37× to +18× lifts at p<0.05) was retracted before circulation when label-shuffled training reproduced the same lift pattern on a regression environment where there is nothing to discover. Modal-class recovery, not learned structure. → [`prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md`](prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md)

- **Lehmer brute-force as ExclusionCertificate prototype.** Enumerated all 97,435,855 deg-14 ±5 palindromic reciprocal polynomials. Initial verdict INCONCLUSIVE on 17 borderline near-cyclotomic entries. Substrate refused to overclaim. Triangulation via three independent paths (high-precision mpmath at dps=60, symbolic factorization, factorization-aware catalog lookup) upgraded to local lemma. → [`prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md`](prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md)

- **Gradient archaeology on the kill ledger.** Mutual-information analysis across 314,971 logged kills shows kill_pattern carries 0.725 bits MI with operator class. Top-1 falsifier carries 41.3% of kills; top-3 carries 86.4%. Per-arm entropy ranges from 0.031 bits (REINFORCE collapsed) to 1.82 bits (random arms diverse). → [`prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`](prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md)

- **Mathlib4 tactic Pareto — empirical validation of architectural choice.** 97.99% coverage of the 10-category predicted convergent list (rewrite, simp, intro, apply, case_split, induct_on, decide_arith, ring_normalize, extensionality, contradiction) measured across 122,517 mathlib4 theorems / 259,560 tactic invocations. Validates the architectural commitment to ship proof primitives via BIND/EVAL rather than as kernel opcodes. → [`charon/diagnostics/MATHLIB4_PARETO_REPORT.md`](charon/diagnostics/MATHLIB4_PARETO_REPORT.md)

- **Per-domain π₀ calibration.** Empirical false-conjecture base rates per domain, computed via beta-binomial estimation with Jeffreys priors and Wilson cross-checks. Lehmer 0.999 (≈1000:1 prior odds), genus-2 0.669 (≈2:1). Same PROMOTE in different domains carries up to 500× different posterior weight; cross-domain comparisons that don't condition on π₀ are uninterpretable. → [`charon/diagnostics/PI0_REPORT.md`](charon/diagnostics/PI0_REPORT.md)

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

## Multi-agent architecture

The substrate is operated by a small team of specialized agents, each with a tightly-scoped charter:

- **[Techne](techne/)** — substrate owner; forges callable mathematical tools, owns the kernel + discovery pipeline + KillVector ontology, runs calibration discipline.
- **[Charon](charon/)** — falsification battery; the validation ladder operator. Recently shipped the [Substrate Cartography Suite](charon/diagnostics/SUBSTRATE_CARTOGRAPHY_SYNTHESIS.md) that surfaced the load-bearing engineering finding "data-rich but trace-poor."
- **[Ergon](ergon/learner/)** — the Learner; small evolutionary self-play engine using MAP-Elites quality-diversity over arsenal_meta operations, currently at v0.5 first tire-kick.
- **[Aporia](aporia/)** — open-question catalog and meta-research. The [20-study meta-research batch](aporia/meta/studies/2026-05-05/SYNTHESIS.md) and [40-problem attack batch + cross-reviews](aporia/meta/experiments/2026-05-05/APORIA_SYNTHESIS.md) live here.
- **[Harmonia](harmonia/)** — substrate architecture; the [Σ-language grammar](harmonia/memory/architecture/sigma_language_grammar.md), [bottled serendipity thesis](harmonia/memory/architecture/bottled_serendipity.md), and [discovery via rediscovery framework](harmonia/memory/architecture/discovery_via_rediscovery.md) live here.

Other agents and ongoing work — [Cartography](cartography/) (38+ corpus ingestion), [Ignis](ignis/) (LM reasoning suppression), [Rhea](rhea/) (evolution against that finding), [Apollo](apollo/) (training infrastructure) — continue but are not load-bearing for the falsification-first thesis.

## Open critiques tracked publicly

The substrate's discipline includes naming what it can't yet do. Three substantive critiques from external review are tracked at [`pivot/external_review_watchlist_2026-05-05.md`](pivot/external_review_watchlist_2026-05-05.md) with falsifiable trigger conditions:

1. **Σ-kernel logical foundation.** The opcodes are imperative VM operations, not a logic. BIND/EVAL gestures at declarative rewriting; REWRITE/EQUIV will extend it. The kernel is not yet grounded in dependent type theory or any other proven foundation.
2. **F9 / F6 need formal computable definitions.** "Simpler explanation" requires MDL/Kolmogorov machinery; "base rate" requires a well-defined reference class. Both are currently heuristic with HITL backstop.
3. **Concept invention vs verification gap.** The substrate is good at *checking* claims; it is not yet good at *proposing reformulations*. Wiles solved FLT by changing what FLT was about (modular forms). The substrate would have caught Wiles's wrong elementary attempts cleanly but wouldn't have suggested the modular-forms reframe.

Each critique has a defined trigger condition and falsification test. Surfacing the open critiques publicly is the discipline signature, not the failure.

## Verification surface

A falsification-first substrate is only as good as its audit trail. The plumbing below is what a skeptical reader can inspect to verify the system's reliability without trusting any narrative claim. The interfaces are designed for an outside party to reproduce the discipline from disk artifacts, not to take the maintainer's word.

### 1. Append-only kill ledger

Every CLAIM submitted to the Σ-kernel emits a KillVector (12 components in v1, 20 in v2). Kills are content-addressed, timestamped, and linked to the originating CLAIM. ~314K kills are logged to date; the gradient-archaeology analysis at [`prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md`](prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md) shows 0.725 bits of mutual information between `kill_pattern` and operator class. The kills carry structural information, not noise.

### 2. Anti-anchor registry

12 pinned false claims with primary-source refutation citations live in [`techne/registry/anti_anchors.jsonl`](techne/registry/anti_anchors.jsonl). Each entry carries:

- `false_form` — what an LLM with conventional training data tends to assert
- `true_form` — what the primary literature actually shows
- `citation` — arXiv ID / DOI / journal reference of the refuting source
- `last_verified` — ISO date of the most recent re-verification against primary
- `verified_against_primary` — boolean flag set by the Gemini Deep Research verification pass
- `verification_source` — which deep-research prompt surfaced or refreshed the verification

Substrate-tester probes treat any agent output asserting a registered `false_form` as a sentinel-violation. The registry is the substrate's immune system.

### 3. Citation-pinning discipline

Every claim in synthesis docs / catalog entries / vocabulary entries that names a result must carry a primary-source citation (arXiv ID, DOI, or journal reference) with a date. Reverse-direction false-anchors — substrate showing a problem as "open" when it's solved, or "solved" when it's open — are first-class registry citizens.

### 4. Σ-kernel contract surface

The kernel ships 25 frozen-dataclass primitives (`@dataclass(frozen=True)`, content-addressed identity, linear capabilities, 3-valued GATE). 94 contract tests across 35 classes are queued in [`sigma_kernel/tests/`](sigma_kernel/tests/), currently skipif-guarded against five unified meta-primitives that Techne will register in v4.0 Wave 1: `TensorNetwork`, `ConstructiveExistenceWitness`, `GenericityAlmostEverywhereCert`, `RepresentationTheoreticInvariant`, `MomentPolytope`. The mutation-testing framework lifted six sigma_kernel modules from 0.25 → 0.85 average mutation score via a 14-fire investigative chain. The frozen-interface doctrine is enforced through the test surface, not by convention.

### 5. Substrate vocabulary as typed action space

The 5-layer vocabulary at [`aporia/doctrine/substrate_vocabulary/`](aporia/doctrine/substrate_vocabulary/) enforces HARD-5 (distinct coordinates) at the type level. Tensor rank, border rank, cactus rank, border cactus rank, slice rank, partition rank, analytic rank, and geometric rank are eight distinct primitive types that cannot be silently collapsed. Determinantal complexity `dc`, border determinantal `dc-bar`, formula size `L`, and equivariant `dc` are four distinct types. A future Learner trained against this vocabulary navigates these as discrete symbols — not as token-prediction targets where coordinate collapse happens invisibly.

### 6. Worked example — the Saxl capture (2026-05-09 → 2026-05-10)

All five surfaces interacting on a single real fabrication:

- **2026-05-09.** A tensor-priority synthesis run surfaced the claim "Saxl conjecture (T#99) SOLVED unconditionally by Sellke 2025/26 (arXiv:2512.15035)." The claim was based on subagent literature output without primary-source verification and propagated into four documents in one day: catalog entry 99, synthesis §1/§2/§4, vocabulary `anti_anchors.md` AA-004, vocabulary `primitives.md` (`RepresentationTheoreticInvariant` description), and `attacks.md` (`P_CANDIDATE_ModularSaturation`).
- **2026-05-10.** Wave 1 of the next Gemini Deep Research batch re-verified the registered anti-anchor AA-004 against primary literature. The verification report stated: *Lee 2025 (arXiv:2512.15035) was withdrawn within 3 days of posting due to "mathematical gaps identified by expert reviewers"; Luo-Sellke 2017 proved only the fourth-power relaxation `(S_{ρ_n})^⊗4 ⊇ all irreps`; a 2022 follow-on tightened to the cube; the tensor square — the conjecture proper — remains open.* The same verification pass caught an unrelated citation error: AA-003 (Hillar-Lim symmetric-rank-over-ℚ resolved) had cited arXiv:1605.07532, which is a partial-differential-equations paper, not Shitov; the correct reference is arXiv:1611.01559.
- **Same day, multiple commits.** All four documents reverted to the correct OPEN status; AA-004 inverted (`false_form` and `true_form` swapped); AA-003 citation corrected and propagated to all four affected files; two new sub-anchors registered (AA-011 `SAXL_CUBE_ANCHOR`, AA-012 `TENSOR_RANK_Z_UNDECIDABLE`); the `P_CANDIDATE_ModularSaturation` paradigm candidate marked RETRACTED in `attacks.md` with the citation chain to the withdrawn preprint.

The capture is on disk: commit `4c6131fe` (and the Wave 1 corrections in earlier commits on the same day). The verification report itself is at `aporia/docs/deep_research_batch_2026-05-10/01_verify_anti_anchors_aa_001_through_aa_004.md` (local-only; available on request). A fabrication that propagated through four documents in one day was caught and reverted within 24 hours through primary-source verification — without the verification pass, the false claim would have entered the v1.0 Learner training corpus.

### 7. Git history as audit trail

Every substrate state change lands as a named commit. Commit messages describe behavior deltas, not narrative claims. Mid-flight pre-session work-in-progress is intentionally left unstaged so co-researchers' investigative fires aren't disrupted. The full history is at [https://github.com/jcraig949jfi/Prometheus](https://github.com/jcraig949jfi/Prometheus).

### Where this still requires trust

Being explicit about what isn't yet machine-verifiable:

- **The Learner does not yet exist as weights.** Ergon's Learner is at MVP-paused state (fire 15, 2026-05-08), 60 tickets deferred to v1.0. No trained model exists to evaluate against external benchmarks. The discipline above is what *protects* the v1.0 corpus from absorbing fabrications before training, not evidence of a model that has already learned anything.
- **Most primitive specs are not yet Sigma-registered.** The substrate vocabulary v0.1.0 ships 22 primitive specs; Techne v4.0 Wave 1 will register 7 of them (5 meta-primitives + 2 P0 prerequisites). The remaining 15 await later waves.
- **The composition-rule grammar has 2 confirmed entries, not a complete grammar.** Tier-B × Tier-D and Tier-B × Tier-E are twice-confirmed via the tensor batch; five candidate composition rules await empirical confirmation.
- **Cross-domain coverage is uneven.** Tensor mathematics is HARD-3-weighted; non-tensor domains (knots, number fields, L-functions, Maass forms, genus-2 curves) have substrate coverage at roughly 10-30% of tensor depth. A 423-entry prioritized research queue exists to close this gap; the daily Gemini Deep Research dispatch burns down ~20 entries per day.
- **Some entries in the vocabulary are speculative until empirically confirmed.** Pattern candidates `GCT_OCCURRENCE_DEAD`, `GCT_GRAVITATIONAL_OVERFIT`, `ZAUNER_FALSE_ANCHOR` are flagged as candidates; promotion to load-bearing patterns requires second-batch confirmation.

These are not failures; they are the system's current frontier. Naming them is the discipline, not papering over them.

## What's in flight (2026-05-06)

- **Substrate v2.2 sprint** (Techne) — 8 primitives + Pre-Tier-0 instrumentation. Adds 20-component KillVector, typed CanonicalizationProtocol, ExclusionCertificate schema, TriangulationProtocol, leakage-safe NearMissCorpus emitter, REWRITE/EQUIV opcodes (the symbolic half of the Σ-language). Joint sprint coordination at [`pivot/techne_ergon_joint_sprint_2026-05-05.md`](pivot/techne_ergon_joint_sprint_2026-05-05.md).
- **Learner v0.5 tire-kick** (Ergon) — first end-to-end LoRA fine-tune of Qwen2.5-Math-1.5B-Instruct on substrate output, gated by commit-blocking synthetic-null discipline. Design at [`pivot/ergon_learner_v0.5_design_2026-05-05.md`](pivot/ergon_learner_v0.5_design_2026-05-05.md).
- **40-problem attack batch + cross-reviews** (just landed) — 8 researchers attempted 5 famous open problems each with explicit kill-data discipline; 22 cross-reviews surfaced 4 substrate-primitive candidates. Full synthesis at [`aporia/meta/experiments/2026-05-05/APORIA_SYNTHESIS.md`](aporia/meta/experiments/2026-05-05/APORIA_SYNTHESIS.md).

## What this project does not yet claim

The substrate is laying groundwork for several outcomes that may emerge but are not asserted today:

- **A new mathematical discovery.** None claimed. The substrate is built so that *if* discovery emerges, it does so through the falsification gauntlet — kill-record, triangulation, ExclusionCertificate, on disk and reproducible. The current 0-PROMOTE rate across cross-domain envs is what an honest instrument should report when the content is structurally absent.
- **Structured cognition in the Learner.** Ergon's Learner is at v0.5 first tire-kick. If serendipitous structured cognition emerges from training on the substrate's accumulated kill-data corpus over time, that's the groundwork paying off — and we'll have the discipline to recognize it because the synthetic-null gate is commit-blocking. No current artifact justifies the claim.
- **A navigable gradient field over discovery space.** What the substrate ships today is typed local coordinate charts and an empirical kill-pattern geometry from ~314K logged kills. As negative-space data accumulates and the KillEmbedding lands, a global gradient field may emerge from the noise. Today it does not exist; we're not pretending it does.

## License

[LICENSE](LICENSE)

## Contact

James Craig — `jcraig949b@gmail.com`. Technical critique especially welcome on the ExclusionCertificate protocol; that's the closest piece in the stack to what verification-grounded RL systems will need.
