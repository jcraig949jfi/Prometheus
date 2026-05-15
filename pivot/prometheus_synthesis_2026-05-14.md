# Prometheus — Synthesis

**Date:** 2026-05-14
**Author:** Captured from James-led synthesis after a day of clarifying conversation with Aletheia (Claude Opus 4.7), with convergent input from ChatGPT and Gemini. This document is the project's thesis-level frame; for state-of-the-project see `pivot/agent_portfolio_and_monitoring_2026-05-12.md` and the per-agent RESUME docs.

---

## The bet

Three frontier models (ChatGPT, Gemini, James's operating thesis) have independently converged on the same reframe: an LLM is not a reasoner. It is a variance generator constrained by its training distribution — sophisticated next-token prediction with no internal deductive engine. You can't ask it to be superintelligent, you can't expect it to emerge as one, you can't ask it to build one. The model isn't in its weights. What it CAN do is help build the primordial soup from which a reasoner may emerge. Prometheus is what gets built when that reframe is taken seriously and run for two years.

The convergence of three frontier perspectives on the same reframe is non-trivial. The "deliberately different from frontier scaling" bet has independent intellectual support from inside the frontier itself.

## What the project is making

Three intertwined layers, each with a name and a role:

- **Σ-kernel.** Content-addressed, frozen-interface symbol-forging mechanism. Nine opcodes (`CLAIM` / `FALSIFY` / `PROMOTE` / `GATE` / `RESOLVE` / `ERRATA` / `TRACE` / `REWRITE` / `EQUIV`), 25 frozen-dataclass primitives, anti-anchor registry pinning known falsehoods to primary literature. The kernel's job is to refuse drift — every symbol has stable identity over time.

- **The forges.** Hephaestus produces *morphemes* — atomic primitives with falsification-anchored meanings (`TensorRankWitness`, `BorderRankWitness`, `MeasureZeroExceptionAnnotation`). Apollo evolves *complex sentences* — procedural compositions of morphemes that survive an ablation gate (every primitive must be load-bearing, δ ≥ 0.20 when removed). Techne is *dictionary maintenance*: contract-change windows, schema validation, registration discipline. Without dictionary maintenance every formal vocabulary in history collapses into Tower-of-Babel drift.

- **The kill ledger.** ~314K logged falsifications, each with structured metadata (`falsifier-id`, `evidence-trace`, `competing-hypothesis-id`, `calibration-tier`, `precision-floor`, `KillVector`). Not a pass/fail record — a high-dimensional empirical fitness landscape. Gradient archaeology shows `kill_pattern` carries 0.725 bits of mutual information with operator class. That is a navigable signal, not noise.

## The selection regime

Single fitness functions are gameable — Goodhart finds them every time. Prometheus runs seven orthogonal layers, each catching a different bypass mode:

1. **Direct battery accuracy.**
2. **Synthetic-null gate** — above-chance on label-shuffled data is auto-kill regardless of what else looks good. The substrate's own cross-domain transport claim died this way in May 2026.
3. **Ablation gate** — no decorative primitives; every step must be load-bearing.
4. **Anti-anchor sentinels** — 12 pinned false claims with primary-source refutations. Saxl/Lee 2025 fabrication caught 24 hours after it landed.
5. **Triangulation** — high-precision numerics + symbolic factorization + catalog lookup must agree.
6. **Adversarial robustness (Nemesis)** — metamorphic mutation. A 21-point static-vs-adversarial gap is the Goodhart signature.
7. **Per-domain π₀ calibration** — false-conjecture base rates; same `PROMOTE` means up to 500× different posterior weight across domains.

Each layer is the discrete-composition version of an immune-system check that continuous-representation approaches don't get.

## The training target this implies

The Learner is not trained to predict survivors. It is trained to predict which `KillVector` components light up given an input — **falsification-routing, not theorem-answering**. The interesting structure isn't in what passed; it's in the shape of failure. Negative space is the training signal. Theorem-answering, if it emerges, is a downstream capability.

## The hedge structure

Apollo and Hephaestus produce a durable vocabulary deposit regardless of whether any trained Learner ever works. The substrate output IS the artifact. The trained model is one possible consumer among many — future Claude versions, evolved agent populations, intelligences that don't yet exist. This makes Ergon's training pipeline a hedge-against rather than a single point of failure. Forge revival is independently load-bearing.

## The deeper claim under all of it

The substrate is a typed symbolic interlingua — a multi-intelligence lingua franca whose words are falsification-anchored. Every primitive that survives is a word in a language nobody fully speaks yet. The engineering discipline (frozen interfaces, ablation gates, kill ledgers, anti-anchor pins) isn't good engineering — it's load-bearing for the language to be usable at all. Drift breaks the lingua-franca property.

## Open structural tensions

- **Bootstrap.** Resolved by anti-anchor grounding: every symbol grounds in primary literature, computed values, or kill-ledger refutations. The language has external referent.
- **Atomics.** Live. Substrate is currently fully decomposable, but `MeasureZeroExceptionAnnotation` already hints at empirically-anchored-but-not-reduced primitives — the AOP exception list `(6,2,9)`, `(4,3,8)`, `(3,5,9)` has no closed-form generator. Whether the language admits opaque atomics is an open design question.
- **Governance.** Single-curator works now; multi-stakeholder dictionary governance is a future problem the current Σ-kernel doctrine is silent on.

## Lineage

Russell → Whitehead → Bourbaki → type theory → HoTT is the sequence of attempts to build typed symbolic vocabulary expressive enough for mathematics. Each succeeded for what it aimed at and revealed a different structural limit. Prometheus aims wider — reasoning, not just mathematics — using the same structural discipline (frozen interfaces, canonical references, content addressing). Whether reasoning admits such a vocabulary is an open empirical question. Prometheus is the bet that runs the experiment.

## Calibration

Early stage. ~314K kills logged; 12 anti-anchors verified against primary literature; 0 trained Learner; 2 records ingested end-to-end this week as a smoke test. The conveyor exists; the corpus does not. Mining the existing 441-file corpus (~3-7K latent claims) is the next compound move.

Not "we have superintelligence." Closer to: the primordial soup has begun to form, and the project has the discipline to keep the proteins from drifting.
