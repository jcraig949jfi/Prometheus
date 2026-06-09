# Cross-pollination feedback — `pivot\sprint1\phase3\PHASE3_COMBINED_VERDICT_2026-05-30.md`

- generated_at: 2026-05-30T13:29:31.542639+00:00
- generated_by: Moros (charon/agents/moros/daemon.py)
- fanout_n_attempted: 3
- fanout_n_ok: 1
- providers_consulted: ['NVIDIA Nemotron-120B']
- artifact_size_bytes: 10985

## Critique 1 — NVIDIA Nemotron-120B

We need to produce 5-8 bullet points, each a concrete critique with a quote-or-paraphrase of the line the critique targets. Focus on structural defects, missing citations, alternative framings prematurely closed off, HARD-5 violations (terms or coordinates silently collapsed), overclaim risk.

We need to read the artifact and critique.

Let's identify potential issues:

- Structural defects: load-bearing assumptions not justified. For example, assumption that seam sufficiency is provisional based on raw underperforming seam by 1.7 points, but they treat as sufficient. Also assumption that Layer 2 primitives are structurally equivalent to per-plugin counters because they group rows by (plugin,kp) and count. Might be a structural defect: they assume that the primitive's output is identical to per-plugin majority counter when there's one dominant kp per plugin, but they haven't proven that condition holds across all data; they just note it's the case in real ledger after enrichment.

- Missing citations: They refer to harness docs, ITER-40, ITER-42, etc., but no external citations. Might be okay as internal, but could be missing justification for claims like "chance ~6.7%" for 16-class problem.

- Alternative framings prematurely closed off: They discuss Option 1,2,3 but quickly dismiss Option 1 as weaker, and push Option 2. They close off possibility that the claim could be about representation rather than decision improvement without sufficient justification.

- HARD-5 violations: terms or coordinates silently collapsed. For example, they collapse "motif extraction primitive" to per-cell counter, ignoring potential other dimensions. They treat "Layer 2's primitives as designed are structurally equivalent to per-plugin counters at the current data shape." They collapse the multidimensional nature of primitives into a single equivalence claim without showing the mapping.

- Overclaim risk: Language outruns evidence. For example, "The substrate's value claim — that Layer 2 produces decision-relevant signal counters cannot — requires Layer 2 primitives that consume MORE than 1-D (plugin, kp) tuples:" This is a strong claim that may not be fully supported; they haven't shown that counters cannot consume more than 1-D, just that current primitives don't.

Also: "The headline number didn't budge." They claim that z-score improved but actionable routing delta remained zero, implying Layer 2 still matches counters. Overclaim: they say "The motif extraction primitive (ITER-40), as designed, computes the SAME function as a per-plugin majority counter, by construction." This is a strong claim; need to verify if it's truly by construction or only under certain conditions.

Also: "The substrate's value claim — that Layer 2 produces decision-relevant signal counters cannot — requires Layer 2 primitives that consume MORE than 1-D (plugin, kp) tuples:" This is an overclaim; they haven't proven that counters cannot consume more than 1-D.

Also: "The claim as currently operationalized is empirically false on real data, regardless of Layer-1 verdict richness." This is a strong claim; they have only tested with 60 enriched rows; maybe more data could change.

Now produce bullet points.

We need 5-8 bullet points. Let's aim for 6.

Each bullet: start with critique, then quote or paraphrase the line.

Let's craft:

1. Structural defect: treating seam sufficiency as provisional despite inconclusive result; assuming raw underperformance indicates seam sufficiency without ruling out overfitting.

Quote: "verdict = SEAM_SUFFICIENT (weak)" and "Honest reading: raw UNDERPERFORMED seam by 1.7 percentage points. Per the harness doc's own caveat, this is INCONCLUSIVE on seam sufficiency (raw could be losing to predictor overfitting, not because the seam is sufficient)."

2. Structural defect: claiming Layer 2 primitives are structurally equivalent to per-plugin counters by construction, ignoring conditions (single dominant kp per plugin) not proven across all data.

Quote: "The motif extraction primitive (ITER-40), as designed, computes the SAME function as a per-plugin majority counter, by construction."

3. Missing citation/justification: claim about chance accuracy ~6.7% for

## Critique 2 — <failed_call_1>

_(cascade call 2 failed; provider returned no usable text)_

## Critique 3 — <failed_call_2>

_(cascade call 3 failed; provider returned no usable text)_

---

*v0.2 multi-provider cross-pollination per CHARTER §6. Convergence analysis in companion meta_analysis_*.md.*