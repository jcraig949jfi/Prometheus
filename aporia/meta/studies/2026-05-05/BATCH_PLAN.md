# Meta-Studies Batch — 2026-05-05

**Commissioned by:** James
**Owner:** Aporia
**Token budget:** 20 deep research tokens (one per study)
**Cadence:** waves of 3 parallel general-purpose subagents
**Output:** `aporia/meta/studies/2026-05-05/study_NN_{slug}.md`
**Cap:** ~30 min wall clock per subagent; if longer, write what they have and flag

## Purpose

20 meta-studies on mathematical discovery itself, adapted to inform Prometheus
substrate design. The substrate has just produced (over the past 24 hours):

- Substrate-grade Case A finding (RL search-mech is broken at episode-length-1
  contextual bandit + sparse reward)
- Region-specific gradient field structure confirmed (different operators win
  in different regions)
- Brute-force enumeration of deg-14 ±5 palindromic subspace returned
  INCONCLUSIVE (26 Mossinghoff rediscoveries + 17 borderline near-cyclotomic
  entries needing higher-precision verification)
- Kill-vector primitive shipped (per-component margins replacing categorical
  kill_path)
- Caveat-as-metadata schema preventing internal narrative inflation

Each study below is a research question whose answer will inform a specific
substrate-side design decision. NOT a literature review for human consumption.

## The 20 studies

| # | Topic | Substrate connection | Slug |
|---|---|---|---|
| 01 | Minimal Generative Bases Across Mathematical Domains | arsenal_meta primitive set design | minimal_generative_bases |
| 02 | Failure Surfaces in Theorem Discovery | kill_vector design, negative-space tensor | failure_surfaces |
| 03 | Analogy Graphs Between Fields | bridge gradient, cross-domain transport | analogy_graphs |
| 04 | Empirical Study of Rediscovery | discovery-via-rediscovery framework | empirical_rediscovery |
| 05 | Symbolic Compression Limits | Sigma kernel opcode minimality | compression_limits |
| 06 | Mutation Operators for Mathematical Objects | bottled serendipity / MAP-Elites operators | mutation_operators |
| 07 | Invariants as Discovery Anchors | canonicalizer subclass axes | invariants_as_anchors |
| 08 | Dimensional Lifting as Discovery Strategy | abstraction strategies, kill_vector dim | dimensional_lifting |
| 09 | Productive vs Unproductive Generalizations | scope decisions for 322 open questions | generalization_quality |
| 10 | Mathematics as Compression vs Internal Consistency | data-vs-structure weighting | reality_vs_consistency |
| 11 | Search Landscapes of Open Problems | MAP-Elites archive design | search_landscapes |
| 12 | Primitive Operations Underlying Proofs | Sigma kernel opcodes / BIND-EVAL | proof_primitives |
| 13 | When Heuristics Beat Formal Methods | LLM-mutator + formal-falsification hybrid | heuristics_vs_formal |
| 14 | Cross-Domain Conservation Laws | bridge gradient, Langlands-type structure | conservation_laws |
| 15 | Mathematical Objects as Programs | BIND/EVAL semantics, executable claims | objects_as_programs |
| 16 | Noise vs Signal in Conjecture Generation | calibration discipline (cf Ergon's CALIBRATION post) | noise_vs_signal |
| 17 | Canonical Forms Across Domains | canonicalizer extension, dedup | canonical_forms |
| 18 | Edge Cases That Changed Fields | the 17 inconclusive entries from brute-force | edge_cases |
| 19 | Meta-Analysis of Mathematical Notation | Sigma language design, substrate symbol vocabulary | notation_meta |
| 20 | Reduction Pathways Between Theories | dependency_graph.py, theory-graph design | reduction_pathways |

## Wave schedule

- **Wave 1 (now):** studies 01, 02, 03 — foundational primitives + failure-space + bridges
- **Wave 2:** studies 04, 05, 06 — rediscovery + compression + mutation
- **Wave 3:** studies 07, 08, 09 — invariants + lifting + generalization quality
- **Wave 4:** studies 10, 11, 12 — philosophical foundation + landscapes + proof primitives
- **Wave 5:** studies 13, 14, 15 — heuristics + conservation + programs
- **Wave 6:** studies 16, 17, 18 — noise/signal + canonical + edge cases
- **Wave 7:** studies 19, 20, +1 spare or summary task

## Per-study report template (every output must follow)

```markdown
# Study NN: {Title}

**Date:** 2026-05-05
**Owner:** general-purpose subagent (Aporia delegation)
**Substrate connection:** {one sentence}

## Problem statement (Prometheus-adapted)

[the question, framed for what Prometheus needs to know]

## Literature scan

[what's been done, with citations]

## Substrate-relevance

[how the answer connects to Prometheus's current architecture]

## Concrete operational handles

[what specific design decisions the substrate could change based on this]

## Falsification

[what would refute the central claim of this study]

## Open questions raised

[questions the study itself surfaces but does not answer]

## Citations

[full citations, prefer arXiv / DOI / canonical sources]
```

## Honesty rules (apply to every subagent)

- Do not invent citations; if uncertain, say so
- Do not over-claim transferability ("this works in math, therefore in our
  substrate..." — show the bridge, don't assume it)
- Calibrated negative results are preferred to confident positive claims
- "Prometheus has not done X" is a valid and useful finding
- Cap report length at ~2000 words; prefer concision
