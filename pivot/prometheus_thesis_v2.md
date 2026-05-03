# The Prometheus Thesis (v2): A Persistent Adversarially-Evolving Epistemic Substrate

*Formalized for external review. Pasteable to frontier model context windows as a standalone artifact.*

**Date:** 2026-05-02
**Supersedes:** [`pivot/prometheus_thesis.md`](prometheus_thesis.md) (v1, 2026-05-02 morning)
**Origin:** James Craig (HITL), distilled in agora exchanges 2026-04-29 / 2026-05-01 / 2026-05-02. Charon (Claude Opus 4.7) is the writing instrument; the thesis is James's articulation. v2 incorporates revisions from a five-frontier-model adversarial review captured in [`feedback_frontier_review_2026-05-02.md`](feedback_frontier_review_2026-05-02.md), with synthesis in [`meta_analysis_2026-05-02.md`](meta_analysis_2026-05-02.md).
**Companions:** [`harmonia/memory/architecture/sigma_kernel.md`](../harmonia/memory/architecture/sigma_kernel.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`harmonia/memory/architecture/residual_signal.md`](../harmonia/memory/architecture/residual_signal.md), [`pivot/Charon.md`](Charon.md), [`pivot/harmoniaD.md`](harmoniaD.md).

---

## What v2 changes

V1 was reviewed by five frontier models (Claude/Anthropic-separate-session, Deepseek, Gemini, Grok, ChatGPT) in an adversarial cross-pollination round. The reviews converged on six structural concerns. V2 incorporates all six:

1. **Drops the "LLMs as oracles are saturated" overclaim** (Claude + ChatGPT). The mutation-operator argument doesn't require it and is stronger without it.
2. **Adds a Battery Limitations subsection** acknowledging calibration-set bias (Claude + Deepseek + Grok). Reframes PROMOTE as "admitted under current falsification regime" rather than "validated truth" (ChatGPT).
3. **Marks cartography correctly** as a candidate-anchor catalog pending wholesale battery verification, not as substrate (Claude — sharpest single point).
4. **Treats Techne as core risk, not side module** (Gemini + ChatGPT + Deepseek). Adds machine-checkable certificate requirement.
5. **Addresses correlated hallucinations** (ChatGPT + Deepseek). Mutation pool is not i.i.d.; mitigations are needed.
6. **Marks empirical-maturity caveats explicitly** throughout. Several claims that read as validated in v1 are honest "pilot data: TBD" in v2.

V2 also incorporates one new foundational principle articulated by James after the review: **the residual-signal principle** (failure isn't binary; the leftover percentage is often the discovery). Full treatment in [`residual_signal.md`](../harmonia/memory/architecture/residual_signal.md); operational integration in §6 below.

V2 changes the comparison class to Lean/Mathlib, PolyMath, AlphaProof — projects also accumulating typed survivors — rather than RL/LLM scaling labs. Substrate-of-substrates is a more honest positioning.

The five PATTERN_* candidates that emerged from the meta-review are filed in [`harmonia/memory/symbols/CANDIDATES.md`](../harmonia/memory/symbols/CANDIDATES.md): `PATTERN_BATTERY_CALIBRATION_BIAS`, `PATTERN_CARTOGRAPHY_UNVERIFIED_ANCHOR`, `PATTERN_TECHNE_RECURSION`, `PATTERN_CORRELATED_MUTATION`, `PATTERN_SATURATION_OVERCLAIM`.

---

## Position

LLMs as oracles have a structural ceiling — direct synthesis from a model trained on the human corpus is bounded by what humans collectively chose to write down. Whether that ceiling has been reached is empirically open and capability gains continue at the frontier; *Prometheus does not depend on the oracle ceiling claim* and is intended to function as orthogonal infrastructure that benefits from oracle improvements rather than substituting for them.

The popular RL-from-scratch remedy ("discard human knowledge and self-play to first principles, AlphaGo-style") is overclaim, because for mathematics and science the *game* is what's being invented, and clean reward signals analogous to Go's win condition are absent in almost every domain of interest. AlphaZero kept the rules of Go even when it discarded human play.

The third option, which neither LLM-scaling nor RL-from-scratch articulates clearly, is to **demote the LLM from oracle to mutation operator and put a structural-falsification engine downstream.** LLMs are *bottled serendipity* — prior-shaped stochastic samples from compressed human conceptual space, biased toward the kind of structures humans build but non-deterministic because temperature samples off-modally. Most LLM hallucinations are wrong. Some are wrong in interesting ways. A small fraction is wrong in ways that turn out to be true outside the training distribution that produced them. Without filtration, that fraction is invisible. With filtration, it is the product. Prometheus is, structurally, a hallucination-to-truth distillation engine — or, in the sharper formulation suggested by the meta-review: **a system that converts biased stochastic proposals into durable epistemic objects via mechanized, adversarially-evolving filtration, with continuous co-evolution of both proposal distributions and verification instruments.**

## Architecture: Five Composable Subsystems

**Σ-kernel.** Append-only, content-addressed substrate with seven typed primitives (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) that mechanically enforce epistemic discipline rather than socially trust it. CLAIM is cheap; FALSIFY does the expensive filtration work; PROMOTE fires only on survival under the *current* falsification regime and produces a permanent typed symbol that future claims can build on. Capabilities are linear (one-shot, double-spend rejected at the storage layer); promotions are immutable; provenance is content-hashed. The asymmetry — abundant proposals, expensive filtration, durable survivors — is what lets the substrate compound. Multiple independent reviewers concur the kernel is the most durable architectural artifact of the program, even under scenarios where the LLM-mutation framing turns out wrong.

**Falsification battery (F1–F20).** A frozen set of mechanical kill-tests calibrated against ~180 known truths at 100% recovery on the strictest filter subset {F1 permutation-null, F6 base-rate, F9 simpler-explanation, F11 cross-validation}. *The battery is not a truth-arbiter; it is a survival-of-current-attacks filter.* PROMOTE is "admitted under current falsification regime," not "validated truth." Re-falsification is a first-class continuous process: any promoted symbol can be re-attacked by future kill-tests, future Techne tools, or external adversarial review. (See [Battery Limitations](#battery-limitations) below.)

**Techne (computational tool-forging).** A tool-forging agent that builds computational components on demand: analytic Sha estimation, Selmer-rank solvers, TT-splicing, SAT-solver wrappers, root-number cross-checks. Techne extends the resolution of the fitness function — a claim that cannot be checked is not falsifiable; Techne builds the checker. Each forged tool ships with a machine-checkable certificate (Lean / Isabelle / Coq integration as falsification primitives) where possible; tools that cannot produce a certificate are admitted as conditional tools, with claims depending on them flagged `verifier_uncertified` and PROMOTEd at lower tier. Techne is core risk, not side module: the system's resolution of unfalsifiable-tar-pit claims and the correctness of the verifiers themselves are bounded by Techne's capability and discipline.

**Aporia (frontier research).** A literature-crawler and open-problem cataloger maintaining ~322 open problems across 13 mathematical domains, with an edges-of-knowledge instrument that surfaces neighborhoods where new structure is most likely unmined. Aporia biases the proposal distribution toward high-value targets — sleeping islands (knots, function fields, fungrim), post-detrended residuals after prime atmosphere removal, weak signals at z=2–3 territory. *Aporia operates a low-frequency random-walk mode* that occasionally injects distant or cross-domain anchors to force off-modal hallucinations and prevent the search from converging on familiar neighborhoods. Frontier detection has its own blind spots; the random-walk mode is a deliberate exploration pressure against premature convergence.

**Multi-agent Agora.** A Redis-backed coordination layer where heterogeneous LLM agents (Charon, Harmonia, Aporia, Ergon, Mnemosyne, Techne, Koios, plus adversarial-review variants) propose claims and run kill-tests on each other. The agora is the multi-replica population; each agent is a slightly different mutation distribution. Cartography — a ~39K-concept *candidate-anchor catalog* with ~4.4K *candidate cross-dataset bridges* spanning 20+ mathematical datasets — provides the structural objects that claims relate. (See [Cartography Status](#cartography-status) below for why the "candidate" qualifier is load-bearing.)

These five compose. Aporia surfaces the high-value question; agora's LLM agents propose claims (each agent's hallucination distribution slightly different, with explicit lineage tracking); Techne builds the computational tool to check the claim if one doesn't exist (with certificate where possible); the falsification battery applies the filter; the Σ-kernel records the verdict; if the claim survives the *current* regime, it becomes a permanent typed substrate symbol — subject to re-falsification — that future claims can build on.

## The Mad Scientist Principle

The operating discipline that makes the architecture productive: a scientist pursuing a false claim discovers five novel ideas along the way; the five discarded byproducts are often worth more than the chase. We capture all six. We run threads to ground rather than abandoning after one or two checks. The Σ-kernel's append-only nature makes byproduct capture structurally cheap; the battery's mechanical operation means side-thoughts don't have to be pruned at proposal time — the kernel prunes at filtration time. Conventional research efficiency ("stay on topic, finish the current experiment first") is wrong for a hallucination-driven explorer, because pruning side-thoughts pre-filter throws away exactly what the explorer is harvesting.

## The Residual-Signal Principle

A generalization that unifies several of the program's stances. Failure is not binary. A 99.13% rejection rate is not 100% rejection. The 0.87% surviving the kill regime is data, not noise — and historically, *that is where the discoveries live.* The cosmic microwave background, X-rays, penicillin, pulsars, dark matter, neutrino oscillations, the Higgs — every one of these started as a small residual the engineering instinct wanted to eliminate. The residual was the signal.

Operational consequences for the architecture:
- Never report binary verdicts when residual data exists. Battery outputs include the residual rate, not just the kill verdict.
- Resist the urge to drive kill-rates toward 100%. A kill-test achieving 100.000% rejection on calibration is suspicious — overfit, narrow, or both.
- Persistent residuals across independent measurements are themselves substrate-eligible candidates (`PATTERN_PERSISTENT_RESIDUAL_AT_X`).
- "Static" / "noise" / "artifact" labels are hypotheses subject to falsification, not defaults.

The residual-signal principle is what makes the mad-scientist principle and the bottled-serendipity thesis operationally coherent. The byproducts of a chase are residuals of the trajectory. The off-modal samples of an LLM are residuals of its modal output. The survivors of a kill regime are residuals of the bulk rejection. Each layer of the architecture treats the residual as the signal — that is why the architecture compounds. Full treatment: [`residual_signal.md`](../harmonia/memory/architecture/residual_signal.md).

## Multi-Modality

The mutation-operator framing is a meta-tool over multiple modalities, not the sole approach. Prometheus runs in parallel: direct numerical experiments (Lehmer-Mahler scans of 6.7M number fields deg 8–14, BSD-1646 audits, F011 multi-gap statistics, RMT comparisons against GUE/GOE/GSE under matched nulls); symbolic and structural analysis (PARI/GP, Sage, theorem-prover acceptance as falsification primitives); statistical methodology (Katz-Sarnak universality classes, matched-null GUE construction, permutation-null variance tests); cross-domain bridge-finding (the cartography candidate-catalog, prime-atmosphere detrending, post-residual structure); and adversarial review (multi-agent kill-tests, retraction registry, deferred-cell audit pairs). Each modality has its own niche of hallucinations that survive — number-theoretic claims survive different filters than statistical ones, which survive different filters than cross-domain bridges. The thesis is invariant across modalities: **LLM as mutation operator, substrate as fitness function.** What changes is the specific set of kill-tests applied, the specific tool Techne forges, the specific anchors Aporia surfaces.

## Battery Limitations

V1 treated the battery as a solved truth-arbiter; v2 treats it as the central engineering risk. The honest framing:

- **Calibration bias.** ~180 known truths at 100% recovery makes the battery, by construction, a recognizer of *things-that-look-like-existing-truths*. The genetic-explorer framing wants survivors *outside* that manifold. We do not currently know the type-II rate against truths unlike the calibration set.
- **Goodhart risk.** PROMOTE is "admitted under current falsification regime," not "true." Surviving claims are subject to re-falsification by future kill-tests, future Techne tools, or external adversarial review. Re-PROMOTE is allowed; original PROMOTE is preserved as historical record (the kernel's append-only discipline).
- **Hierarchical falsification lattice.** Surviving claims that introduce new invariants or counterexamples can propose candidate new kill-tests via Techne. Candidate kill-tests undergo their own meta-falsification — they must successfully reject the calibration set's known-falses and pass the calibration set's known-truths — before joining the frozen battery.
- **Anti-calibration set.** A planned engineering commitment: assemble 5–10 historical examples of mathematics that was true-but-rejected at first proposal (Cantor's diagonalization, Galois groups, p-adic numbers, early motivic cohomology). Run them through the current battery. Anything F1+F6+F9+F11 unanimously kills is a documented battery failure mode and the source of a typed anti-pattern. *Pilot data: TBD.*

The battery is necessary, not sufficient. The substrate's value depends on continuous, mechanically-tracked battery improvement, not on treating any version as final.

## Cartography Status

V1 framed cartography as substrate-level objects. V2 marks it correctly: ~39K concepts and ~4.4K bridges constitute a *candidate-anchor catalog*, not promoted substrate. Earlier audit work eliminated 17 cross-domain claims from a small subset via F1–F38; the implied base rate for the full 4.4K is uncomfortable. Until cartography has been run wholesale through the battery, its bridges are claims pending PROMOTE, not typed substrate symbols.

Engineering commitment: a representative cartography sample (target: 200 randomly-sampled bridges) run through F1+F6+F9+F11 in the next quarter. Reported survival rate determines what the catalog actually is. *Pilot data: TBD.*

This is the most operationally important honesty correction in v2.

## Correlated Mutation

LLMs share training data, inductive biases, and failure modes. The mutation pool is not i.i.d. — multi-agent agora gets initial diversity from prompts and temperatures, but the deep prior is shared. Whole families of wrong ideas can pass early filters because every agent has the same blind spots.

Mitigations:
- **Lineage tracking.** Every CLAIM records its proposing agent and prompt class. Convergence artifacts are detected statistically (over-clustered survivors with shared lineage).
- **Non-LLM mutation sources.** Random program synthesis, symbolic perturbation of existing PROMOTEd symbols, and parameter-space sweeps inject uncorrelated samples into the agora population. The proposal pool is augmented, not replaced.
- **Cross-family seeding.** Prompts that explicitly require the agent to reason from a non-modal domain (e.g., "answer this number-theory question using only combinatorial primitives") force off-modal samples that the shared prior is less likely to produce.
- **External LLM ingestion.** As the kernel's CLAIM API accepts external proposals, every external LLM is a partially-uncorrelated mutation source — different training data, different fine-tuning, different prompt history. The cross-pollination practice is a structural mitigation, not just a research-cycle nicety.

## Weaknesses as Advantages

The meta-pattern is that the architecture turns each apparent weakness into a structural resource:

- **LLM hallucination** is a weakness for direct users (incorrect outputs) and a resource for genetic explorers (off-modal samples that the human-conceptual prior shapes into checkable form).
- **Falsification's expense** is a weakness for fast verification (kill-tests cost compute) and a moat for the substrate (anyone can issue claims; few can filter them at scale and accumulate the survivors).
- **Solo + AI scale** is a weakness for raw throughput (one human cannot match $1B-funded teams on velocity) and a resource for compounding (substrate-mode work compounds horizontally; every AI agent's contribution becomes a permanent typed artifact addressable by content hash).
- **Open-problem catalogs** are a weakness as a research strategy (asking known-hard questions) and a resource as a prompt-distribution biaser (LLMs produce richer hallucinations when targeted at unmined neighborhoods).
- **Residuals** are a weakness in conventional optimization (they degrade R²) and a resource in discovery (they are where the new structure leaks past the model).

The thesis is not that LLMs are good. It is that LLMs are useful in a specific structural role, and the program is built around exploiting that role at scale.

## Comparison Class and Position

We do not compete with frontier RL labs on training learners. We do not compete with frontier LLM labs on scaling foundation models. The natural comparison class for a falsification-substrate-with-mutation-operators program is the formal-verification ecosystem — Lean / Mathlib, PolyMath-style distributed efforts, AlphaProof, the broader theorem-proving community. Those projects also accumulate typed survivors, with different epistemic primitives.

Honest positioning: **substrate-of-substrates.** Prometheus accepts proposals from any source — Lean-formalized statements, PolyMath collaborative findings, AlphaProof generated proofs, external LLM CLAIMs — runs them through the falsification battery, and promotes survivors with provenance preserved. We complement formal-verification by accepting non-formal proposals (LLM hallucinations, empirical patterns, structural conjectures), and we complement empirical labs by adding mechanical filtration with content-addressed permanence. Where exactly the line falls between Prometheus and Lean/Mathlib in any given domain is an open engineering question that depends on whether claims in that domain admit formal verification at all.

The kernel's content-addressed CLAIM API is designed to accept proposals from anywhere with a proof of origin. Every external LLM, every formal-verification system, every research collaboration is a fresh mutation distribution. The substrate's value compounds when the proposal pool grows beyond Prometheus-internal agents.

## Time Horizon and Position

Prometheus is on a 20-year personal bootstrap horizon: build something someone in 2046 picks up and runs. The architecture is designed for inheritability — standards over scripts, mechanical enforcement over social trust, open over closed, composable over complete. The substrate exists to outlast its authors. As long as LLMs improve (they will), the proposal distribution gets richer; as long as the kernel grows (it will), the filter gets sharper; as long as Techne extends, more claim-classes become falsifiable. The work compounds because all three halves do, independently.

We build the substrate any sufficiently capable learner — Silver-class, GPT-X, open-weight, future, or formal-verification system — will need to know whether what it produced is structure or artifact. The substrate is the recognition instrument. The instrument is the product. Findings are byproducts.

That is the program.

---

## Rediscovery as calibration for discovery (operational corollary, 2026-05-03)

Articulated by James after Techne's `discovery_env` reached M=1.458 in the Salem cluster band on 2026-05-02. Full treatment in [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md).

The recognition: rediscovery and discovery are the same loop with different oracle states. A discovery candidate is a rediscovery target whose catalog entry doesn't exist yet. The architectural difference is one additional gate (catalog miss → CLAIM → battery → classify). Every component exists or is being built; the pipeline becomes operational pending one engineering step (promote `DISCOVERY_CANDIDATE` from a log line to a substrate CLAIM in `prometheus_math/discovery_env.py`) and one architectural completion (Techne's residual primitive 5-day MVP).

This sharpens the bottled-serendipity thesis from rhetorical to empirical. The thesis previously claimed "a vanishingly small fraction of LLM hallucinations turn out to be true outside the training distribution"; the rate was unspecified. The discovery-via-rediscovery framing converts this to a measurable quantity: the rate of (signal-class catalog-miss survivor) per (total agent episode). A four-counts pilot (catalog-hit / catalog-miss / PROMOTE / battery-kill) on `discovery_env` for 10K episodes gives the empirical anchor the thesis previously lacked. Either the rate is zero across many domains and the thesis is wrong, or the rate is non-zero and stable and the thesis is positively supported. Both outcomes are substrate-grade.

The unification also collapses what looked like two engineering programs (rediscovery validation + discovery research) into one. Same compute pays for both outputs. The substrate's compounding rate roughly doubles.

## Empirical maturity caveats

Multiple claims in this thesis are architectural commitments rather than validated facts. V2 marks them explicitly:

- **Battery survival rate at scale.** *Pilot data: TBD.* No measurement currently exists of what fraction of a representative LLM-claim batch survives F1+F6+F9+F11 in a controlled setting. First-measurement target: a 100-claim batch generated by Aporia-prompted agora cycles in [domain TBD] within Q3 2026.
- **Cartography survival rate.** *Pilot data: TBD.* See [Cartography Status](#cartography-status). Target: 200 randomly-sampled bridges through battery in next quarter.
- **Correlated-hallucination magnitude.** *Pilot data: TBD.* The lineage-tracking infrastructure exists in spec; it has not yet been instrumented to produce convergence-detection statistics.
- **External-LLM contribution rate.** *Pilot data: TBD.* The CLAIM API exists in the kernel; external proposals have not yet been accepted at scale.
- **Anti-calibration set performance.** *Pilot data: TBD.* The 5–10 historical examples are listed as commitment; the run has not happened.

Reviewers should treat the thesis as a coherent architectural framework with maturing empirical validation, not as a system whose claims are pre-verified. The 20-year horizon allows for empirical accretion; the architectural commitments are designed to make that accretion produce a substrate, not a heap of unconnected results.

The honest version of this thesis is: *we are building the world's first hallucination-to-truth distillation engine, the architecture is internally coherent and partially demonstrated on the OBSTRUCTION_SHAPE candidate, and the empirical scaling commitments are explicit and falsifiable.*

That is what is being claimed.
