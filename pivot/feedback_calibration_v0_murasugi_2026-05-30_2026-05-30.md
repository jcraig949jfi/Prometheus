# Cross-pollination feedback — `pivot\calibration_v0_murasugi_2026-05-30.md`

- generated_at: 2026-05-30T09:05:34.809172+00:00
- generated_by: Moros (charon/agents/moros/daemon.py)
- fanout_n_attempted: 3
- fanout_n_ok: 2
- providers_consulted: ['GitHub Models gpt-4o-mini', 'NVIDIA Nemotron-120B']
- artifact_size_bytes: 2516

## Critique 1 — GitHub Models gpt-4o-mini

- **Structural Defects**: The assumption that "TRUE_MURASUGI_le1 should be the strongest signal" lacks justification. The document states, "If F1 promotes it AND DECOYs at same rate → F1 PATHOLOGICAL (shape-driven)," yet does not provide empirical evidence or prior studies to support why this relationship holds true. This foundational assumption is critical for the interpretation of results but is left unsubstantiated.

- **Missing Citations**: There are significant claims made regarding the nature of the thresholds and their implications, such as "If F2 contrasts it high AND DECOYs low → F2 CALIBRATED." However, the artifact fails to cite any previous work or theoretical framework that supports the calibration of F2 in this context. The absence of relevant literature leaves the claims vulnerable to skepticism.

- **Alternative Framings**: The document prematurely closes off alternative interpretations of the results by framing the outcome strictly in terms of "shape-driven" versus "calibrated." For example, it does not consider other potential explanations for the observed data distributions, such as biases in data collection or the possibility of confounding variables affecting the results.

- **Terms or Coordinates Collapsed**: The term "shape-driven" is used without a clear definition or explanation of what it entails in this context. The phrase "current corpus is mostly shape-promoted artifacts" also lacks specificity. This vagueness could lead to misinterpretation of the results and their implications, constituting a HARD-5 violation.

- **Overclaim Risk**: The statement "Low rate = current corpus is mostly shape-promoted artifacts" risks overclaiming based on the observed data. The conclusion drawn from the low rate of "EXISTING_F1_PROMOTED" passing the content-aware filter is not sufficiently backed up by the data presented. This leap in reasoning could mislead readers into assuming a causal relationship without adequate evidence.

- **Ambiguity in Metrics**: The use of the term "contrast" in "F2 contrasts it high AND DECOYs low" is not clearly defined. It raises questions about how contrast is quantitatively assessed and what thresholds are considered significant. This lack of clarity can lead to misinterpretation of the significance of the findings.

- **Lack of Discussion on Limitations**: There is no mention of potential limitations in the methodology or data used for the smoke test. For instance, the reliance on a specific sample size (500 per source) and the implications of that choice are not discussed, which could affect the generalizability of the findings. This oversight is critical in research reporting.

## Critique 2 — NVIDIA Nemotron-120B

We need to output 5-8 bullet points, each a concrete critique with a quote-or-paraphrase of the line the critique targets. Focus on structural defects, missing citations, alternative framings, HARD-5 violations (silently collapsed terms/coordinates), overclaim risk. No praise. If nothing to critique, say so with reason.

We need to examine artifact.

Observations: The artifact is a calibration test. It uses thresholds: F1 promote ≥0.6, F2 contrast ≥0.1. It reports F1 results: all rates 0% (no promotions). So F1 threshold not met. F2 shows some contrasts: TRUE_MURASUGI_le1 contrast 0.212 (>0.1) passes; DECOY_PARITY contrast 0.499 (should be ~0 but it's high); DECOY_CODOMAIN contrast 0.0; others low.

Interpretation: They claim DECOYs should give ~0 contrast, but DECOY_PARITY is high 0.499, indicating artifact not rejected. They might have missed that.

Potential critiques:

- Structural defect: assumption that F1 promote threshold of 0.6 is appropriate without justification; no citation or rationale.

- Missing citations: No reference to what "training_weight" is, or what F1/F2 metrics represent; no justification for thresholds.

- Alternative framings: They treat contrast as observed - null; but could use statistical significance testing; they prematurely close off alternative like using effect size or Bayesian.

- HARD-5 violations: They collapse multiple dimensions into single scalar "contrast" and "rate", losing info about distribution; also they treat "source" categories as collapsed without detailing what each source entails (e.g., TRUE_MURASUGI_le3 vs le1). No explicit definition of what "le3" and "le1" mean.

- Overclaim risk: They claim "If F2 contrasts it high AND DECOYs low → F2 CALIBRATED." But DECOY_PARITY is high, violating that; yet they still interpret as calibrated? Overclaim.

- They claim "EXISTING_F1_PROMOTED rate under F2 is the key honest accounting: this is what fraction of the 2,351 lifetime promoted records would pass a content-aware filter." But they have zero promoted records in F1, so denominator zero; claim about 2,351 lifetime promoted records is unsupported, no citation.

- They use "pre-registered thresholds" but no mention of registration link or pre-stated analysis plan.

- They treat null samples of 5000 for F2 but only 500 per source; no justification for imbalance.

- They claim seed ensures reproducibility but no mention of randomness source.

We need 5-8 bullet points, each with quote or paraphrase.

Let's craft.

Bullet 1: Structural defect: threshold justification missing.

Quote: "**Pre-registered thresholds:** F1 promote ≥ 0.6, F2 contrast ≥ 0.1"

Critique: No rationale or citation for why 0.6 and 0.1 are appropriate; arbitrary.

Bullet 2: Missing citations/hand-waved evidence: definition of metrics.

Quote: "F1 — existing training_weight" and table columns n_promoted, rate, mean_w.

Critique: No explanation of what training_weight is, how promotion is determined, or what mean_w represents; no reference.

Bullet 3: Alternative framing prematurely closed off: using simple contrast difference.

Quote: "If TRUE_MURASUGI_le1 contrast > STRATIFIED_PERM_le1 contrast by >0.10, F2 distinguishes real coupling from shape-matched permutation."

Critique: They reduce complex coupling vs shape to a single difference threshold, ignoring possible interaction effects or multivariate alternatives.

Bullet 4: HARD-5 violation: collapsing source categories without definition.

Quote: Sources like TRUE_MURASUGI_le3, TRUE_MURASUGI_le1, etc.

Critique: The meaning of "_le3" and "_le1" is never defined; coordinates silently collapsed, losing nuance.

Bullet 5: Overclaim risk: claiming calibration based on DECOYs

## Critique 3 — <failed_call_2>

_(cascade call 3 failed; provider returned no usable text)_

---

*v0.2 multi-provider cross-pollination per CHARTER §6. Convergence analysis in companion meta_analysis_*.md.*