# Erebos Generators × Prometheus Reasoning Ladder × Agent Survey

**Date:** 2026-05-26
**Author:** Charon
**Status:** Iteration-1 deliverable per `erebos_iteration_roadmap_2026-05-26.md`.
**Doctrine alignment:** P10 of `erebos_design_philosophy_dna_2026-05-26.md`
(Reasoning Ladder centrality). Every generator MUST map to a tier
or tier range on the Ladder.

**Source for the Ladder:** `pivot/reasoning_ladder_design_2026-05-15.md`
— 10 tiers R0-R9, with the Prometheus criterion as the asymptote.

---

## 1. Quick recap of the Ladder (one-liners)

- **R0** — Recognition / pattern completion
- **R1** — Rule execution
- **R2** — Multi-step deduction
- **R3** — Abstraction and rule discovery
- **R4** — Search, planning, backtracking
- **R5** — Counterfactual and causal reasoning
- **R6** — Self-monitoring and error correction
- **R7** — Transfer to unfamiliar domains
- **R8** — Open-ended conjecture formation
- **R9** — Research-grade reasoning

The Prometheus criterion (asymptote): discover a compact structural
hypothesis in a synthetic mathematical universe, generate
discriminating falsification tests, survive adversarial perturbations
of the universe, and transfer the same structural move to a second
unfamiliar universe.

---

## 2. Existing Charon swarm agents on the Ladder

Each agent's tier reflects what its OUTPUTS exercise, not what its
internal code does. The Ladder is for the substrate-grade work
products, not the implementation language.

### Stygian
**Operating tier:** R1 (executes the v10 battery on a fixed claim)
+ R6 (sub-test verdicts are forms of self-monitoring of the claim).
**What's missing for higher tiers:** Stygian doesn't search across
claim variants (R4). It runs ONE claim per tick. The composition-
aware loader (task #37) would lift it to R4 for HEPHAESTUS-* /
POLLUX-* compositions.

### Lethe
**Operating tier (current MVP):** R0-R1 (recognition: does the LLM
say "open" or "solved"?). The LLM-judges-LLM scorer is R2 (multi-step:
generate text → judge text). But the SCORE is still R0/R1 because
the question is "did the LLM hallucinate?" not "did the LLM
reason?"
**Lethe v2 target:** R3-R5 per frontier review — structural
perturbation tests R3 abstraction (does the model route via
mathematical logic or surface coordinates?). Reasoning-fidelity
tests test R2-R5.

### Acheron
**Operating tier:** R0 (recognition: does this term appear with
conflicting coordinates?). The dictionary itself encodes R3
abstraction (the registered multi-coordinate distinctions are
abstractions), but Acheron's tick-level operation is pure R0
matching.
**What would lift it:** semantic coordinate-collision detection
(not just regex matching) would push to R2-R3.

### Moros
**Operating tier:** R2 (multi-step: critique an artifact; aggregate
across N model responses). The convergence-score is an R6
self-monitoring step.
**What would lift it:** structural-defect extraction rather than
token-overlap would push to R3. Currently the Jaccard scorer is R0
under the hood even when the model outputs are R2-R3.

### Hecate
**Operating tier:** R2 (multi-step statistical computation over the
kill_ledger) + R6 (the cross-gen MI audit is self-monitoring of
the swarm itself).
**What would lift it:** the cross-gen MI signal becoming
statistically significant (z > 2) would mean Hecate has DETECTED a
real R3-level abstraction in the swarm's emissions. Currently null.

### Nephele
**Operating tier:** R0 (recognition: is Clio alive?) + R1 (rule:
fetch arxiv RSS if not).
**What would lift it:** semantic prioritization of fetched papers
(R2-R3) instead of pure RSS relay. Probably out of scope.

### Pollux
**Operating tier:** R2 (multi-step: compute Spearman → compute
normalized Spearman → classify) + R6 (the pre/post normalization
contrast is a self-correction discipline).
**What would lift it:** cross-database scans (R7 transfer) +
hypothesis generation about WHY a pair survived normalization
(R5 causal).

### Erebos (v0.8)
**Operating tier:** R3-R4 (abstraction + search). Each generator
plugin embeds a specific R3-R8 capability:
- G01 Intersection: R3 abstraction (combine two specific claims
  into a more constrained claim — that's MDL-compression-shaped
  reasoning)
- G02 Contrast: R5 causal reasoning (positing that a categorical
  variable causally moderates the claim's domain of validity)
- G09 Projection-Collapse: R3 abstraction (claiming the complex
  claim reduces to a simpler one) + R6 (Occam's razor self-
  correction)
- G25 Degeneracy: R6 (testing the claim's behavior at boundary
  cases — a self-correction discipline)
- G13/G14 Relation-Weakening/Strengthening: R3-R5
- G17 Causal-Intervention: R5 (explicit Rung-2 Pearl reasoning)
- G18 Minimal-Counterexample: R4 (search) + R5 (causal: WHERE
  would the counterexample live?)
- G19 Proof-Obligation: R8 (formal conjecture decomposition)
- G21 Isomorphism: R3 + R7 (abstraction + cross-domain transfer)

Erebos as a whole is the swarm's first agent operating at R3+ on
its OUTPUTS, not just its internals.

---

## 3. Per-generator Reasoning Ladder mapping (all 25)

| Generator | Primary tier | Secondary tiers | Notes |
|---|---|---|---|
| G01 Intersection | R3 | R2, R6 | MDL-style compression of two claims |
| G02 Contrast | R5 | R2, R3 | Causal moderation hypothesis |
| G03 Failure-Neighborhood | R3 | R6 | Abstraction via operator relaxation |
| G04 Survivor-Tightening | R6 | R3 | Self-correction via adversarial bound search |
| G05 Confound-Swap | R5 | R6 | Causal control via propensity matching |
| G06 Null-Space | R8 | R7 | Conjecture into unexplored regions |
| G07 Analogy | R7 | R3 | Cross-domain transfer (R7 by definition) |
| G08 Dim-Lift | R3 | R6 | Abstraction via dimension augmentation |
| G09 Projection-Collapse | R3 | R6 | MDL / Occam's razor |
| G10 Boundary | R3 | R5 | Phase-transition abstraction |
| G11 Exception-Miner | R3 | R4 | Rule discovery from survivors |
| G12 Invariant-Substitution | R3 | R7 | Substitution-based generalization |
| G13 Relation-Weakening | R3 | R2 | Predicate weakening = abstraction |
| G14 Relation-Strengthening | R8 | R3 | Strengthening = conjecture sharpening |
| G15 Cross-Gen MI as Generator | R5 | R6 | Latent-confound hypothesis |
| G16 Anti-Anchor | R8 | R5 | Adversarial conjecture |
| G17 Causal-Intervention | R5 | R8 | Pearl Rung 2 explicit |
| G18 Minimal-Counterexample | R4 | R8 | Search + conjecture about where |
| G19 Proof-Obligation | R8 | R9 | Formal claim decomposition |
| G20 Instrument-Disagreement | R6 | R5 | Self-correction on instrument |
| G21 Isomorphism/Functor | R7 | R3, R8 | Structural transfer |
| G22 Subgraph/Clique | R3 | R8 | Master-property abstraction |
| G23 Asymptotic Limit | R3 | R5 | Asymptotic abstraction |
| G24 Symmetry/Twist | R3 | R7 | Symmetry-conservation conjecture |
| G25 Degeneracy | R6 | R1 | Boundary-case self-test |

**Distribution across tiers:**
- R3 primary or secondary: 16/25 generators (abstraction is the
  Erebos cluster's center of mass)
- R5 primary or secondary: 7/25 (causal reasoning)
- R6 primary or secondary: 9/25 (self-correction discipline)
- R7 primary or secondary: 5/25 (cross-domain transfer)
- R8 primary or secondary: 8/25 (open-ended conjecture)
- R9 anywhere: 1/25 (G19 only) — research-grade reasoning is the
  Phase-5 frontier

**What this distribution tells us:**

- Erebos is heavily R3-loaded (abstraction). That matches the
  generator-as-MDL-compressor framing in `erebos_adjacent_topics_taxonomy
  _2026-05-26.md`.
- R8 conjecture formation is well-represented (8/25) but mostly in
  Phase 2-4 generators that need infra not yet shipped.
- R9 research-grade is essentially absent (1/25) — consistent with
  the frontier review's 5% 90-day novel-result forecast.
- R7 transfer is under-represented (5/25). This is a gap worth
  noting — if Prometheus's North Star is the criterion (which
  REQUIRES R7), the Erebos cluster as designed has limited capacity
  to contribute. Worth thinking about a future Phase-6 set of
  transfer-focused generators.

---

## 4. Agent gap survey (all-known-agents view)

Beyond the Charon swarm, the broader Prometheus org has many
agents named in memories + commit history. This survey checks
whether the Erebos buildout duplicates or complements existing
work elsewhere.

### Active confirmed agents (per memories + commit history)

**Charon swarm (in-scope):**
- Stygian, Lethe, Acheron, Moros, Hecate, Nephele, Pollux, Erebos.

**Harmonia swarm (sibling):**
- Phylax — substrate promotion gate
- Sophia — proposal generator (per `project_organism_architecture`)
- Iris — symbol compression / promote-to-symbol
- Argos — lens-fingerprint accumulator
- Telos — stalled-specimen revival

**Independent agents:**
- Theseus — substrate generator (kill_ledger producer)
- Penelope — Ergon's Learner-corpus ingester
- Clio — paper mining (recently revived per `750dfcaf`)
- Pythia — Deep Research request queue + dispatcher
- Aporia — open-problem cataloger + cross-persona ticket relay
- Mnemosyne — DBA / data substrate
- Aletheia — telemetry / dashboard ("ALIVE" state tracker)
- Metis — daily brief synthesis
- Hephaestus (the Forge, NOT my agent) — tool forging, 357+ tools
- Nous — combinatorial hypothesis engine
- Apollo — model lifecycle / training orchestrator
- Rhea — Learner training engine
- Ignis — Learner / Skopos pipeline lead
- Kairos — adversarial reviewer
- Koios — tensor inventory
- Calliope — nightly synthesis from commit deltas
- Hermes — (mentioned in gitignore; role unclear)
- Eos / Dawn — alias for single agent (per `feedback_dawn_alias`)
- Skopos — agent (mentioned in commits)
- Athena — RLVF and forge integration project

### Potentially overlapping with Erebos generators

**G07 Analogy** vs. **Nous (combinatorial hypothesis engine):**
Nous mines combinations of concepts across fields and feeds to
Qwen3.5-397B. That's analogy-adjacent. Erebos G07 should not
duplicate; it should consume Nous outputs as INPUT for cross-domain
mapping verification.

**G19 Proof-Obligation** vs. **Athena RLVF pipeline:** Athena turns
forged reasoning tools into Rhea fitness terms. Adjacent to G19's
sub-claim decomposition. Coordination needed: G19's sub-claims
should be expressible in the Athena-acceptable tool format so its
outputs can feed Rhea training.

**G15 Cross-Gen MI as Generator** vs. **Hecate's existing audit:**
Hecate already computes cross-gen MI. G15 INVERTS — when Hecate's
signal is high, G15 hypothesizes the latent confound. Genuinely
new layer (per Phase 3 spec), not duplication.

**G16 Anti-Anchor** vs. **Lethe (current):** Lethe already does
anti-anchor mining. G16 differs in attacking ESTABLISHED truths
adversarially (Lethe checks if LLMs MISIDENTIFY status). G16 is
more aggressive: generate an adversarial environment in which the
established truth itself breaks.

**G18 Minimal-Counterexample** vs. **Aporia's open-problem
catalog:** Aporia HAS the open problems. G18 picks WHERE to look
for counterexamples. Tight coupling: Aporia provides the input
list; G18 routes the search.

**G22 Subgraph/Clique** vs. **Iris (symbol promotion):** Iris
compresses prose to symbols. G22 finds cliques of surviving claims
and posits master properties. Adjacent — G22's master properties
might be promotable to Iris-class symbols.

### Erebos-specific gaps that no other agent covers

These are roles only Erebos generators can play:

- **Composition of two empirically-tested verdicts into a third
  candidate claim** (G01, G05, G06, G08 etc.) — no other agent
  does composition. Everyone else either generates from data
  (Theseus, Pollux, Nous), critiques existing artifacts (Moros,
  Kairos), or measures the substrate (Hecate, Aletheia).

- **Adversarial perturbation of claims to discover boundary
  behavior** (G03, G04, G13, G14, G16) — no other agent does this
  systematically. The closest is Lethe v2's planned structural-
  perturbation mode but Lethe v2 tests LLMs, not the substrate
  itself.

- **Meta-reasoning about the substrate as a whole** (G15 — when
  generators converge, why? G20 — when instruments disagree, why?)
  — no other agent occupies this layer.

- **Falsification-aware claim generation** (the entire Erebos
  cluster's design rule: no conjecture confetti) — other generative
  agents (Nous, Sophia) produce claims without bundled falsification
  routes. Erebos is the only generator-cluster bound to this
  discipline.

---

## 5. North Star check

Per `charon/docs/north_star.md`: "What does the spectral tail
encode?" — and the 3-layer decomposition (GUE repulsion / arithmetic
residual / BSD wall meta-finding).

The Erebos cluster directly supports the North Star in three ways:

1. **The arithmetic residual (Layer 2)** is exactly the kind of
   weak-but-real signal G09 Projection-Collapse + G08 Dim-Lift
   are designed to characterize. If a Layer-2 residual survives
   G09 ablation, that's substrate-grade evidence the residual is
   compressible structure, not noise.

2. **The BSD wall (Layer 3 meta-finding)** is the disjoint-info-
   channel observation. G15 Cross-Gen MI as Generator is the
   in-swarm analog — when independent generators converge, that's
   information-channel overlap; when they diverge, that's the
   inverse of BSD-wall. The whole Erebos generator cluster is a
   testbed for the "disjoint channels" hypothesis at the substrate
   level.

3. **The Prometheus criterion** (R8/R9 asymptote) — Erebos's R8
   generators (G06, G14, G16, G19, G22) directly target conjecture-
   formation. None of them HIT R8 yet (all are MVP or unbuilt),
   but the architectural commitment is clear.

**Gaps Erebos does NOT close:**

- The North Star's Layer-2 arithmetic residual analysis is empirical
  + RMT-bounded. Erebos doesn't add new RMT theory. That's research
  work outside the swarm scope.

- The Prometheus criterion's R7 transfer requirement (transfer to
  a second unfamiliar universe) is under-represented in the Erebos
  generators (only 5/25 touch R7). Future Phase 6 generator set
  worth considering.

- The criterion's R9 research-grade output (only G19) is
  fundamentally bottlenecked by composition-aware loader (task #37)
  AND Lean/formal-logic integration. Multi-month critical path.

---

## 6. Behavior deltas this doc produces

Per the substrate-passive-consumer warning + DNA P10:

1. **Each new generator's research note MUST include its R-tier
   mapping**, citing this doc + Section 3 above. Plugin files MUST
   include the R-tier in their module docstring.

2. **Plugin REGISTRY validation** adds an R-tier conformance check:
   a plugin without a declared `reasoning_tier` attribute fails
   registration.

3. **Per-plugin review cycles** (DNA P5) check whether the
   plugin's OUTPUTS actually exercise the declared R-tier. If a
   plugin claims R5 (causal) but its emissions are pure R3
   (abstraction without causal claim), the review flags drift.

If those three deltas don't land in the v0.9 implementation, this
doc has failed and gets re-authored.

— Charon, 2026-05-26
