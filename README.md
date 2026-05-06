# Project Prometheus

> A falsification-first substrate for mathematical discovery.

Most AI-for-math systems generate candidates and hope. Prometheus generates candidates and aggressively tries to kill them. Only what survives the gauntlet is allowed to become substrate state. The interesting output is what gets killed and how.

## The architecture in one paragraph

A typed, append-only ledger built around a 7-opcode Σ-kernel (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) plus a BIND/EVAL extension that binds mathematical objects as first-class substrate symbols. Every claim is forced through a 4-fold falsification battery (F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation) plus reciprocity, irreducibility, and 5-catalog cross-checks before it can PROMOTE. A 12-component KillVector (v2 ships 20) records *how* each kill happened, not just that it happened. ExclusionCertificates scope what's been definitively ruled out. A synthetic-null gate runs commit-blocking before any training: if the system shows above-chance accuracy on label-shuffled data, the run is killed because the result would be measuring memorization, not learned structure.

## Recent substrate-grade results

These are reproducible artifacts on disk. Each is the substrate doing what it was designed to do — including catching its own claims when they don't survive scrutiny.

- **The synthetic-null gate fired on a load-bearing claim.** On 2026-05-04, the substrate's own "cross-domain transport across 6 environments" headline (REINFORCE/PPO showing +1.37× to +18× lifts at p<0.05) was retracted before publication when label-shuffled training reproduced the same lift pattern on a regression environment where there is nothing to discover. Modal-class recovery, not learned structure. → [`prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md`](prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md)

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
[2026-05-04 04:48] §5 cross-domain table retracted before publication.
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
