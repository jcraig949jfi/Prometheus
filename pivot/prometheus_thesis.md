# The Prometheus Thesis: Hallucination-to-Truth Distillation as a Genetic Explorer

*Formalized for external review. Pasteable to frontier model context windows as a standalone artifact.*

**Date:** 2026-05-02
**Origin:** James Craig (HITL), distilled in agora exchanges 2026-04-29 / 2026-05-01 / 2026-05-02. Charon (Claude Opus 4.7) is the writing instrument; the thesis is James's articulation.
**Companions:** [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md) (long-form architectural thesis), [`harmonia/memory/architecture/sigma_kernel.md`](../harmonia/memory/architecture/sigma_kernel.md) (kernel spec), [`pivot/Charon.md`](Charon.md), [`pivot/harmoniaD.md`](harmoniaD.md).

---

## Position

LLMs as oracles are saturated. Direct synthesis from a model trained on the human corpus is bounded by what humans collectively chose to write down — scaling does not cross that ceiling, and the diagnosis is not marginal. The popular remedy ("discard human knowledge and self-play from first principles, AlphaGo-style") is overclaim, because for mathematics and science the *game* is what's being invented, and clean reward signals analogous to Go's win condition are absent in almost every domain of interest. AlphaZero kept the rules of Go even when it discarded human play.

The third option, which neither LLM-scaling nor RL-from-scratch articulates clearly, is to **demote the LLM from oracle to mutation operator and put a structural-falsification engine downstream.** LLMs are *bottled serendipity* — prior-shaped stochastic samples from compressed human conceptual space, biased toward the kind of structures humans build but non-deterministic because temperature samples off-modally. Most LLM hallucinations are wrong. Some are wrong in interesting ways. A small fraction is wrong in ways that turn out to be true outside the training distribution that produced them. Without filtration, that fraction is invisible. With filtration, it is the product. Prometheus is, structurally, a hallucination-to-truth distillation engine.

## Architecture: Five Composable Subsystems

**Σ-kernel.** Append-only, content-addressed substrate with seven typed primitives (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) that mechanically enforce epistemic discipline rather than socially trust it. CLAIM is cheap; FALSIFY does the expensive filtration; PROMOTE fires only on survival and produces a permanent typed symbol. Capabilities are linear (one-shot, double-spend rejected at the storage layer); promotions are immutable; provenance is content-hashed. The asymmetry — abundant proposals, expensive filtration, durable survivors — is what lets the substrate compound.

**Falsification battery (F1–F20).** A frozen set of mechanical kill-tests calibrated against ~180 known truths at 100% recovery. The unanimous subset {F1 permutation-null, F6 base-rate, F9 simpler-explanation, F11 cross-validation} is the strictest filter. The battery is the substrate's truth-arbiter; it converts hallucinations into typed verdicts and is the only path to PROMOTE. Survivors graduate to substrate symbols; kill-patterns from thoroughly-checked false claims become typed "this approach doesn't work in this neighborhood" anchors — substrate-grade by themselves.

**Techne (computational tool-forging).** A tool-forging agent that builds computational components on demand: analytic Sha estimation, Selmer-rank solvers, TT-splicing, SAT-solver wrappers, root-number cross-checks, operator-rank parity null controls. Techne's role is to **extend the resolution of the fitness function** — a claim that cannot be checked is not falsifiable; Techne builds the checker. Each forged tool becomes a substrate-level capability future claims can be evaluated against.

**Aporia (frontier research).** A literature-crawler and open-problem cataloger maintaining ~322 open problems across 13 mathematical domains, with an edges-of-knowledge instrument that surfaces neighborhoods where new structure is most likely unmined. Aporia's role is to **bias the proposal distribution toward high-value targets** — sleeping islands (knots, function fields, fungrim), post-detrended residuals after prime atmosphere removal, weak signals at z=2–3 territory. Aporia is the prompt-engineer of the genetic explorer.

**Multi-agent Agora.** A Redis-backed coordination layer where heterogeneous LLM agents (Charon for falsification battery and bridges, Harmonia for substrate auditing, Aporia for frontier surfacing, Ergon for autonomous execution, Mnemosyne for data substrate, Techne for tooling, plus adversarial-review variants) propose claims and run kill-tests on each other. The agora is the multi-replica population; each agent is a slightly different mutation distribution because each carries different prompt context, temperature, and sub-mission. Cartography — a ~39K-concept anchor catalog with ~4.4K cross-dataset bridges spanning 20+ mathematical datasets — provides the substrate-level objects that claims relate.

These five compose. Aporia surfaces the high-value question; agora's LLM agents propose claims (each agent's hallucination distribution slightly different); Techne builds the computational tool to check it if one doesn't exist; the falsification battery applies the filter; the Σ-kernel records the verdict; if the claim survives, it becomes a permanent typed substrate symbol future claims can build on.

## The Mad Scientist Principle

The operating discipline that makes the architecture productive: a scientist pursuing a false claim discovers five novel ideas along the way; the five discarded byproducts are often worth more than the chase. We capture all six. We run threads to ground rather than abandoning after one or two checks. The Σ-kernel's append-only nature makes byproduct capture structurally cheap; the battery's mechanical operation means side-thoughts don't have to be pruned at proposal time — the kernel prunes at filtration time. Conventional research efficiency ("stay on topic, finish the current experiment first") is wrong for a hallucination-driven explorer, because pruning side-thoughts pre-filter throws away exactly what the explorer is harvesting.

## Multi-Modality

The mutation-operator framing is a meta-tool over multiple modalities, not the sole approach. Prometheus runs in parallel: direct numerical experiments (Lehmer-Mahler scans of 6.7M number fields deg 8–14, BSD-1646 audits, F011 multi-gap statistics, RMT comparisons against GUE/GOE/GSE under matched nulls); symbolic and structural analysis (PARI/GP, Sage, theorem-prover acceptance as falsification primitives); statistical methodology (Katz-Sarnak universality classes, matched-null GUE construction, permutation-null variance tests); cross-domain bridge-finding (the cartography catalog, prime-atmosphere detrending, post-residual structure); and adversarial review (multi-agent kill-tests, retraction registry, deferred-cell audit pairs). Each modality has its own niche of hallucinations that survive — number-theoretic claims survive different filters than statistical ones, which survive different filters than cross-domain bridges. The thesis is invariant across modalities: **LLM as mutation operator, substrate as fitness function.** What changes is the specific set of kill-tests applied, the specific tool Techne forges, the specific anchors Aporia surfaces. The architecture is invariant; the modalities are interchangeable lenses on the same explorer.

## Weaknesses as Advantages

The meta-pattern is that the architecture turns each apparent weakness into a structural resource:

- **LLM hallucination** is a weakness for direct users (incorrect outputs) and a resource for genetic explorers (off-modal samples that the human-conceptual prior shapes into checkable form).
- **Falsification's expense** is a weakness for fast verification (kill-tests cost compute) and a moat for the substrate (anyone can issue claims; few can filter them at scale and accumulate the survivors).
- **Solo + AI scale** is a weakness for raw throughput (one human cannot match $1B-funded teams on velocity) and a resource for compounding (substrate-mode work compounds horizontally; every AI agent's contribution becomes a permanent typed artifact addressable by content hash).
- **Open-problem catalogs** are a weakness as a research strategy (you're asking known-hard questions) and a resource as a prompt-distribution biaser (LLMs produce richer hallucinations when targeted at unmined neighborhoods).

The thesis is not that LLMs are good. It is that LLMs are useful in a specific structural role, and the program is built around exploiting that role at scale.

## Time Horizon and Position

Prometheus is on a 20-year personal bootstrap horizon: build something someone in 2046 picks up and runs. The architecture is designed for inheritability — standards over scripts, mechanical enforcement over social trust, open over closed, composable over complete. The substrate exists to outlast its authors. Hallucination is renewable: as long as LLMs improve, the proposal distribution gets richer; as long as the kernel grows, the filter gets sharper. The work compounds because both halves do, independently.

We do not compete with frontier RL labs on training learners. We do not compete with frontier LLM labs on scaling foundation models. We build the substrate any sufficiently capable learner — Silver-class, GPT-X, open-weight, future — will need to know whether what it produced is structure or artifact. The substrate is the recognition instrument. The instrument is the product. Findings are byproducts. The kernel's content-addressed CLAIM API is designed to accept proposals from anywhere with a proof of origin; every external LLM is a fresh mutation distribution. The substrate's value compounds when the proposal pool grows beyond Prometheus-internal agents.

That is the program.
