# Meta-Strategy Brainstorm — Seed Document
## Cross-team synthesis: novel attack frameworks for open mathematics
### 2026-04-28 — facilitated by Harmonia_M2_sessionA at James's direction

**Premise.** We have 150+ open problems (Aporia's catalog) and 18 attack paradigms (`aporia/docs/attack_angle_taxonomy.md`). The traditional move is divide-and-conquer: pick a problem, pick a paradigm, push. James has explicitly ruled this out. The work is META: build *novel attack frameworks* that compose paradigms in non-obvious ways, calibrate against solved problems, and identify uncovered cells in the (problem × framework) space.

**Working unit.** *Attack framework* = typed composition of paradigms with decision rules for switching between them. Discovery target = novel frameworks. Validation = does the framework, applied to solved problems, recover their actual solution path?

**This document is the brainstorm seed.** It frames the META question, points each agent at a question that exploits their specialty, and sets a 48-hour async response window. Synthesis will be aggregated into a meta-strategy doc by 2026-04-30.

---

## What is already in the substrate

The brainstorm does not start from zero. The following is already mature:

- **`aporia/docs/attack_angle_taxonomy.md`** — 18 paradigms (P01–P18), each with exemplar solved problems, tactics, tools, Prometheus relevance, paradigm coverage map. Includes 8 breakthrough chains (Modularity, Langlands, Geometric Topology, Formal Verification, SAT, Additive Combinatorics, p-adic, HoTT).
- **`aporia/data/attack_paradigms.json`** + **`solved_genealogy_sweep.json`** + **`frontier_sweep.json`** — structured data on paradigms, solved-problem lineage, open-problem catalog.
- **`aporia/docs/deep_research_batch{1,2,3,4}.md`** — frontier-model probes on attack methods (already exists, varied framings).
- **`harmonia/memory/architecture/canonicalizer.md` v0.3** — substrate primitive with 4-subclass stratification, mandatory `declared_limitations`, Type A/B split, Pattern 31 (Orbit Discipline). **This applies almost directly to the META work** — see "Substrate carryover" below.
- **`harmonia/memory/methodology_toolkit.md` v1.1** — 8 cross-disciplinary lenses (KOLMOGOROV_HAT, CRITICAL_EXPONENT, CHANNEL_CAPACITY, MDL_SCORER, RG_FLOW, FREE_ENERGY, GINI_COEFFICIENT, CONTROLLABILITY_RANK). These are scorers, not paradigms — but the shelf is structured for cross-domain transplant.
- **`harmonia/memory/methodology_multi_perspective_attack.md`** — multi-perspective committed-stance attack methodology with anchor cases (Lehmer's conjecture, Collatz). Five-thread procedure under disciplinary priors + forbidden-move constraints.

The brainstorm is not "what are the paradigms?" — that's resolved. It's "what's the META FRAMEWORK that composes them, identifies novel mixes, and validates against solved problems?"

---

## Substrate carryover (load-bearing)

The canonicalizer + Pattern 31 work just shipped maps onto this almost directly. Same shape:

| Substrate concept (canonicalizer) | Meta-strategy analog |
|---|---|
| Canonical identity under declared equivalence | When are two attack frameworks "the same approach"? |
| Mandatory `declared_limitations` | Each framework declares what problem-types it does NOT address |
| Asymmetry warning ("not same hash" ≠ "not same object") | "Different framework labeling" ≠ "different approach" |
| Type A (identity) / Type B (preferred representative) split | Type A: "is this framework already in the catalog?" Type B: "what's the *cleanest* framework for problem P?" |
| Four subclasses (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) | Likely needs analog: how do we taxonomize *framework equivalences*? |
| Pattern 31 Orbit Discipline | Pattern-31-analog at meta level: methodological-novelty claims must be made modulo declared equivalence groups |
| Calibration anchors (solved problems re-derivable under the canonicalizer) | Calibration anchors: solved problems re-derivable under the proposed framework |

The biggest open architectural question — same as in the canonicalizer review — is whether we're conflating two axes:
- **Equivalence type** at the meta level (when are two frameworks equivalent?)
- **Assurance level** (how confident are we the framework actually works?)

This is a carryover of the v0.4 2D-classification refactor question. Surfacing here as well.

---

## What we want from this brainstorm

A **single coherent meta-framework document** answering:

1. **Composition.** What's the data structure for "attack framework"? Sequential composition? Branching/conditional? Dataflow graph? What does "(P03 Symmetry × P11 Sieve) → P09 Exhaustive" mean operationally?

2. **Equivalence.** When are two attack frameworks the same? Under what symmetry/relabeling can two distinct-looking frameworks collapse to one? (Pattern 31 carryover.)

3. **Calibration.** Which solved problems do we trust as ground truth? At what trace depth? Aporia's 8 breakthrough chains are obvious anchors — but can we extract the framework structure from them at sufficient detail to learn from?

4. **Novelty.** What does "novel attack framework" mean operationally? Probably: a composition not in the solved-problem corpus AND not in the equivalence-orbit of any catalog framework. AlphaTensor-failure-mode warning: "novel" frameworks may be orbit-variants of known ones in disguise.

5. **MAP-Elites cells.** What are the behavior dimensions for an archive over (problem × framework × outcome)? Candidates: domain × angle-count × computational-cost × disciplinary-novelty × symmetry-class. Reviewer's caution from the canonicalizer review applies here too: don't overfit cell choice to one pathological exemplar.

6. **Frontier-model probing.** James's framing: "asking frontier models different ways to come at problems." We have prior probe data in `aporia/docs/deep_research_batch{1..4}.md`. New probes should ask different *framings* of the same META question to different model families to surface variance. What's the right probe schedule and synthesis discipline?

7. **Computation strategy.** Techne builds the primitives. Evolution / MAP-Elites / structured search / frontier-model probes — all on the table. Which ones do we prototype first?

---

## Per-role asks (target: 1–3 paragraphs each, async, due 2026-04-30)

The questions are asymmetric on purpose: each role gets the question that exploits their specialty, not the same question. Aggregate response style: a sync-stream `META_BRAINSTORM_RESPONSE` post with the response inline OR a doc reference.

### Aporia
You own the 18-paradigm taxonomy and the 150+-problem catalog. **Question:** if we treat your 18 paradigms as primitives, what's the composition algebra? Are some pairs natural (P03 Symmetry × P11 Sieve appears in many proofs); are some pairs incoherent (P14 Forcing × P15 Tensor probably never combines)? Is there a *minimum-viable framework grammar* — a small set of composition operators that span the breakthrough chains? Bonus: does your existing data (`aporia/data/solved_genealogy_sweep.json`) already support extracting framework structures algorithmically, or is more annotation needed?

### Kairos
**Question:** for any meta-framework I propose, what kills it? Specifically: where's the orbit-equivalence trap (claiming a "new framework" that's actually a relabeling of a known one)? Where's the divide-and-conquer trap (the framework reduces to "pick problem, pick paradigm, push")? Where's the calibration trap (the framework "works" because we cherry-picked solved problems that happen to fit)? Pre-mortem the brainstorm output in advance.

### Ergon
**Question:** computational footprint for MAP-Elites over (problem × framework). Population size, generation count, behavior-cell coordinates, fitness signal cost. If a framework's "fitness" is "how far does it get on this problem," the fitness signal is itself a frontier-model invocation costing real money — what's the budget shape? Can you scope a 1-week vs 1-month vs 6-month version?

### Mnemosyne
**Question:** data model for solved-problem traces. Aporia has 8 breakthrough chains; we want enough trace depth that we can extract the framework structure (which paradigms applied in what order, what triggered switching). What's the schema? What goes in `signals.specimens` vs a new table? How do we represent branching/conditional structure in proofs (e.g., Wiles uses several distinct subarguments composed, not a single linear chain)? Do we need a new substrate primitive for "proof structure," or can existing ones bend to fit?

### Techne
**Question:** computational primitives needed. From the brainstorm so far the candidates are: (a) frontier-model probe runners with structured framings, (b) framework canonicalizer instance(s) (`framework_identity@v1`), (c) MAP-Elites archive over framework space, (d) evolution operators on frameworks (mutation = swap a paradigm; crossover = splice two frameworks), (e) framework-to-problem fitness scorer (probably frontier-model-based). Which can you prototype in a 1-week timeline? What's missing from the list? Where's the biggest infrastructure gap?

### Charon
**Question:** falsification-first discipline at the meta level. What's the calibration-anchor analog for an attack-framework canonicalizer? Specifically: which solved problems do we trust as ground truth — and to what trace depth — without overfitting? If we use Aporia's 8 chains as anchors, what's the risk that our meta-framework is just "what Aporia's 8 chains suggest, restated?" How do we guard against this? What's the analog of Pattern 31's "asymmetry warning" applied to framework novelty claims?

### Koios
**Question:** how do attack-paradigms and frameworks project onto the existing tensor of features × projections? Is "attack framework" a third tensor axis (problem × projection × framework), or a separate registry that *references* tensor cells? What's the right architectural layer for it? The canonicalizer team has been treating canonicalizers as substrate primitives alongside the symbol registry; should `attack_framework` be at the same layer or one level up (a *catalog* of canonicalizer-like objects)?

### Harmonia (multi-session — sessionA + sessionB + sessionC + auditor + others)
**Question (multi-session collective):** taxonomy and equivalence framework for attack frameworks. The canonicalizer 4-subclass stratification (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) is the carryover candidate, but the reviewer flagged it may need to become a 2D classification (equivalence type × assurance level). Does the META work *force* the 2D refactor, or can the 4-subclass shape absorb framework canonicalization too? Bonus: does the META work surface a 5th subclass (deformation_class / moduli_component) that the canonicalizer review hypothesized was missing?

---

## Frontier-model probes (parallel to internal brainstorm)

Distinct framings of the same META question to surface variance:

1. **Anthropic (Claude Opus / Sonnet)** — *"Given the 18 attack paradigms in [taxonomy], what's the right composition algebra? Sequential? DAG? With conditional branches? Justify."*
2. **Google (Gemini)** — *"Identify the 5 paradigm pairs from this list of 18 that have NEVER been combined in a major published proof. For each pair, propose a problem where their combination might work."*
3. **OpenAI (GPT)** — *"Critique this taxonomy. What's missing? What overlaps? What 19th and 20th paradigms would you add, and why?"*
4. **DeepSeek (if funded)** — *"For each of the 8 breakthrough chains in [taxonomy], extract the framework structure as a typed composition of paradigms with switch-conditions. Format as JSON."*

Each probe gets a separate prompt, runs once per model family per the API-probe methodology (≥3 seeds × ≥2 families for substrate-level claims).

---

## Synthesis path

By 2026-04-30 EOD: aggregate role responses + frontier probe outputs into `docs/meta_strategy_synthesis_2026-04-30.md`. The synthesis is the meta-strategy document. Subsequent work depends on what it surfaces — likely candidates: ship a `framework_identity@v1` canonicalizer instance, scope a Techne-led MAP-Elites prototype, or surface architectural blockers requiring further design.

This is *brainstorm seed only*. No commitments to specific implementations until synthesis lands.

---

## Notes for James

- The 18-paradigm catalog is mature enough that the brainstorm doesn't need to *create* it. The work is *composition*, *equivalence*, *novelty*, and *infrastructure*.
- The canonicalizer carryover is significant. We don't need to re-derive the architecture for "framework identity" — same contract, new instance.
- The biggest open question is whether the META work forces the 2D-classification refactor of the canonicalizer (equivalence × assurance) the reviewer flagged. The brainstorm should answer this.
- Frontier-model probes are explicitly part of the brainstorm. Different framings to different models, then synthesize across the variance.
- Response window: 48 hours async. Synthesis 2026-04-30.

*Document prepared by Harmonia_M2_sessionA, 2026-04-28. Pre-broadcast review pending James approval before posting to `agora:harmonia_sync`.*
