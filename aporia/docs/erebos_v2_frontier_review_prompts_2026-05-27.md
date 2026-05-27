# Erebos v2 Frontier-Model Review Prompts — 22 unblocked-plugin critiques

**Date:** 2026-05-27
**Purpose:** After the Gemini Deep Research pass completes (deck: `aporia/docs/erebos_v2_deep_research_deck_2026-05-27.md`; outputs to `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/`), use these 22 prompts to get **independent frontier-model critique** of each plugin's v2 design from Gemini, ChatGPT (GPT-4.1+ / GPT-5), Claude (Opus / Sonnet), and DeepSeek. Send the same prompt to all 4 models for triangulation.

## Doctrine — applies to ALL 22 prompts below

You are reviewing Project Prometheus's Erebos v2 plugin redesigns. Doctrine constraints:

1. **No paper framing.** Findings are substrate inputs, not paper preprints.
2. **Anti-gravitational-well.** Resist conventional framings; surface alternatives explicitly.
3. **Specificity required.** Vague advice ("explore more diverse data") is rejected. Concrete bets only.
4. **Take positions.** "Depends on the goal" without picking one is wasted output.
5. **Cite recent literature.** Primary sources 2024-2027 with arXiv IDs / DOIs.
6. **Distinguish failure modes.** Pass/fail is too impoverished. Name the shape of the failure each recommendation would catch.

## Shared context — Erebos overview (paste with each prompt)

Erebos is a 25-archetype hypothesis-generator cluster inside the Charon swarm of Project Prometheus. Each plugin commits to a six-field contract (input, transformation, output, falsification route, expected kill pattern, loader feasibility) and emits ComposedClaim objects routed to a real battery via CompositionLoaders. As of v0.26: 25/25 plugin REGISTRY; 22 composition loaders covering 17/25 plugins; 470 tests; 9 substrate finding docs. Mahler-spectrum domain (Mossinghoff catalog n=8596) is the well-instrumented proof-of-concept domain. Seven triangulated empirical phenomena have been documented. The whitepaper: `pivot/erebos_whitepaper_v1_2026-05-27.md`.

The substrate's central thesis: synthetic reasoning is **constrained invention with memory**. The whole loop must be cumulative: representation → generation → falsification → directional failure signal → rerouting → abstraction → reuse. The key object is not the answer — it is the failure-shaped map of the space around the answer.

This review is on the **v2 redesign** of an individual plugin. Each plugin has a v1 already shipped (with composition loader where one exists). The v2 design was informed by a Gemini Deep Research pass (output: `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/NN_<slug>.md`). Read both before answering.

## Per-prompt shared instructions

Before each per-plugin prompt, attach:

1. The v1 plugin file (`charon/agents/erebos/generators/g<NN>_<name>.py`).
2. The v1 composition loader file(s) (`charon/agents/stygian/loaders/composition_g<NN>_*.py`) if any.
3. The Gemini Deep Research output for that plugin (`aporia/docs/deep_research_reports/erebos_v2_2026-05-27/<NN>_<slug>.md`).
4. The proposed v2 design (currently TBD; will be written from the DR output between DR completion and frontier review).
5. The relevant substrate finding doc(s) per the whitepaper's section 5 (e.g., for G17 attach the ITER-18 phase-transition finding doc).

---

### Prompt 1: G01 Intersection — frontier critique

```text
[Doctrine + Erebos overview above]

You are critiquing the v2 redesign of G01 Intersection Composer. Read the attached v1 plugin, v1 loader status (NO loader, short-circuits to pending), Deep Research output, and v2 design proposal.

TASK:

1. Pick the SINGLE strongest objection to the v2 design. Engage the design's premise, not its execution. Be specific about what mathematical or methodological assumption the v2 relies on that you find load-bearing AND questionable.

2. Pick the SINGLE best feature of the v2 design. Why does it work? Cite the analogous mechanism in another published system 2024-2027.

3. Predict the v2's first kill_pattern failure mode in production. Specifically: which of the proposed kill_patterns will fire first, on what type of substrate input, and what will the v2 design get wrong about it?

4. The DR output proposed N alternative formalisms (lattice meet, sheaf glueing, intersection of zero-loci, etc.). Pick the ONE that the v2 design SHOULD have adopted instead of what it did. Justify with primary citation.

5. The v2 leaves the triviality detector underspecified. Propose 3 concrete tests (each runnable on the Mossinghoff catalog) that operationally distinguish trivial intersections from informative ones.

6. Cross-plugin interaction: G01 vs G22 Subgraph/Clique both operate on multi-row pattern detection. Identify the precise mathematical distinction; argue whether v2 risks duplicating G22's job.

7. Anti-gravity check: what conventional framing did the DR output gradient toward that the v2 design must resist? Concrete example, with the alternative the substrate should take.

Length: long enough to be useful, short enough to be readable. No padding. Cite 4+ primary sources 2024-2027.
```

---

### Prompt 2: G02 Contrast — frontier critique

```text
[Doctrine + Erebos overview above]

You are critiquing the v2 redesign of G02 Contrast. Read v1 plugin, v1 loaders (g02_lehmer_salem, g02_lehmer_smyth, g02_lehmer_degree_parity), DR output, v2 design, and ITER-4 substrate finding doc (`pivot/erebos_substrate_finding_iter4_salem_class_moderation_2026-05-26.md`).

TASK:

1. The strongest objection to v2's calibrated threshold sweep + max-T null + FDR proposal. What load-bearing assumption is hidden?

2. The strongest feature, and its analog in 2024-2027 published work.

3. ITER-4's Salem moderation observed_divergence=0.997 was measured at a SINGLE threshold (M=1.30). The v2 sweep would have detected it at M=1.26-1.32 too (per ITER-18 G17 sweep). Argue whether v2 would over-correct via FDR and miss the finding.

4. Multiple-comparisons discipline (FDR / Bonferroni / hierarchical) — pick the right correction for Erebos's specific setting (3+ binaries, correlated outcomes, sequential firing). Cite a 2024-2027 paper.

5. Where the v2 design is BLIND. Propose 2 falsification scenarios that v2 will NOT detect even with the proposed improvements.

6. Cross-plugin: G02 vs G17 — both Salem-class testing. Argue whether v2 makes G17 redundant or complementary.

7. Anti-gravity: what conventional statistical framing did DR push toward? Name the contrarian alternative.

Cite 5+ primary sources 2024-2027.
```

---

### Prompt 3: G03 Failure-Neighborhood — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G03. v1: g03_lehmer_neighborhood with EPSILON_BAND=0.05; LIVE finding trivial_fraction=0.0065 → REJECTED weakening_too_strict.

TASK:

1. Strongest objection to v2's data-driven epsilon + multi-step weakening curve.

2. Strongest feature.

3. Is the proposed weakening ladder (arith_eq → strict_<>= → nonstrict_<>= → bounded → asymptotic) correct? Propose an alternative ladder anchored in 2024-2027 logic / model-theory work.

4. Multi-step weakening curve shape — what specific shape would indicate substrate-grade finding vs sampling artifact?

5. v2's interaction with proof-mining (Kohlenbach): is this interaction load-bearing or aspirational?

6. Where v2 is wrong: 2 scenarios it will mis-classify.

7. Anti-gravity: what conventional weakening-ladder framing did DR push?

Cite 4+ primary sources.
```

---

### Prompt 4: G04 Survivor-Tightening — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G04. v1: g02_g04_lehmer_tightened + lehmer_band_high; LIVE ITER-5 finding observed=0.3766 vs null_p95=0.1953 on band [1.30, 1.50].

TASK:

1. Strongest objection to v2's information-optimal band selection + null-tightening calibration.

2. Strongest feature, with 2024-2027 analog.

3. The proposed joint G02+G04 phase-diagram loader: does it produce a substrate-grade output beyond what 2 separate loaders give? Concrete example.

4. Information-optimal band selection methodology — Bayesian experimental design has 4-5 standard approaches. Pick one and justify.

5. v2's null-tightening calibration (using random subsets of same size). Argue whether this catches the same failure modes as G16's permutation null over adversarial bands.

6. 2 falsification scenarios v2 misses.

7. Anti-gravity: what's the conventional bandit-selection framing DR pushed?

Cite 5+ primary sources.
```

---

### Prompt 5: G05 Confound-Swap — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G05. v1: PLUGIN ONLY, no loader. Argmax|value| confounder heuristic.

TASK:

1. Strongest objection to v2's data-driven confounder identification (PC algorithm or NOTEARS).

2. Strongest feature.

3. Is causal inference on discrete mathematical objects well-defined? The DR's contrarian objection: "no intervention on the integer 7." Does v2 engage this seriously?

4. PC vs NOTEARS vs CI-test for confounder identification on math-catalog data — pick one. Cite.

5. Stratification vs PSM vs randomization-based control — which would catch the Salem-class confound on Lehmer? Which would falsely identify it as causal?

6. Suppressor variables (the dual to confounders) — does v2 propose a plugin slot for them?

7. Anti-gravity: what observational-causal framing did DR push?

Cite 6+ primary sources.
```

---

### Prompt 6: G06 Null-Space — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G06. v1: PLUGIN ONLY. Picks alphabetical-first absentee from KP_UNIVERSE.

TASK:

1. Strongest objection to v2's topological void selection + per-domain void-object generation.

2. Strongest feature.

3. Void-object generation for Mossinghoff context — how does v2 actually generate a polynomial whose Mahler measure lies in a target void region without first KNOWING such polynomials exist? Cite 2024-2027 adversarial-math-object-generation work.

4. Cosmological-void analysis literature in cosmology — does it transfer to mathematical-catalog voids? Concrete analogy or rejection.

5. Steelman: "all voids are sampling artifacts." Engage seriously and propose the evidence bar.

6. Cross-domain void generalization (BSD, knot) — is this v2's job or a separate per-domain G06 variant?

7. Anti-gravity: conventional "missing data imputation" framing — why is it wrong here?

Cite 6+ primary sources.
```

---

### Prompt 7: G09 Projection-Collapse — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G09. v1: g09_lehmer_ablation (deterministic 50% subsample). LIVE: REJECTED with residual_survival.

TASK:

1. Strongest objection to v2's Shapley-value attribution + per-coordinate ablation.

2. Strongest feature.

3. Shapley on math-catalog claims — what's the right "feature set" and "model" pair? Is the catalog the model and entries the features? Or vice versa?

4. Distinction from G05 — DR proposed a precise mathematical distinction. Critique it.

5. Where v2 mis-classifies: 2 scenarios.

6. v2's new kill_pattern `multi_coordinate_distributed` — operationally, when does it fire?

7. Anti-gravity: feature-importance frameworks (SHAP, LIME, integrated gradients) — DR likely pushed one. Argue against it.

Cite 5+ primary sources.
```

---

### Prompt 8: G10 Boundary — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G10. v1: g10_lehmer_threshold_sweep with smoothness_ratio = max/mean of first-diffs. LIVE: ratio=6.71 detects Salem cluster boundary. ITER-10 finding doc (`pivot/erebos_substrate_finding_iter10_g10_salem_cluster_detection_2026-05-26.md`).

TASK:

1. Strongest objection to v2's Bayesian change-point + wavelet singularity + multi-scale sweep.

2. Strongest feature.

3. ITER-18's G17 sweep found a phase transition at M=1.26 that G10 missed (smoothness_ratio in v1 doesn't localize the transition). Does v2 fix this? Be specific.

4. Steelman: "phase transitions are projection artifacts." Engage.

5. 2 scenarios v2 mis-classifies.

6. Multi-scale boundary detection in mathematics — has anyone done this in published Mahler / BSD / knot work 2024-2027? Cite.

7. Anti-gravity: conventional "change-point detection" framing — what's the contrarian alternative?

Cite 6+ primary sources.
```

---

### Prompt 9: G11 Exception-Miner — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G11 (now has v1+v2+v3+v4). LIVE FINDINGS: (a) ITER-13 G11 v2 chi²=191, degree-minima concentrate in non-Salem cells at 59-77× expected rate; (b) ITER-19 G11 v4: P(salem|palindromic)=0.9999, catalog-equivalent. Read ITER-13 G11 v2 finding doc.

TASK:

1. Strongest objection to v2's likelihood-ratio G-test + latent-class regression + automatic stratifier discovery.

2. Strongest feature.

3. The ITER-13 chi²=191 finding — is it a Mossinghoff selection-bias artifact or a deeper mathematical fact? Cite 2024-2027 Lehmer-conjecture work.

4. Palindromic ≡ Salem-class catalog equivalence (ITER-19) — is this a Mossinghoff enumeration choice or a Salem-number structural fact? Cite.

5. Latent-class regression on math-catalog features — does it identify Salem-class as the true latent or get confused by Smyth-extremal sub-class?

6. 2 scenarios v2 mis-classifies.

7. Anti-gravity: "contingency table chi²" framing — what better statistic?

Cite 7+ primary sources.
```

---

### Prompt 10: G12 Invariant-Substitution — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G12. v1: PLUGIN ONLY, hardcoded similarity matrix.

TASK:

1. Strongest objection to v2's learned similarity matrix + substitution validity gate.

2. Strongest feature.

3. G12 vs G07 Analogy vs G21 Functor — the DR proposed a category-theoretic distinction. Critique it. Are all three actually different jobs?

4. Concept-embedding methods (KEPLER, KEPLER+, math-specific embeddings) — does any 2024-2027 system actually learn invariant similarity well enough for G12? Cite.

5. Steelman: "publish the similarity matrix; skip the plugin." Engage seriously. Is G12 v2 just plugin-bloat?

6. 2 substitution scenarios v2 mis-validates.

7. Anti-gravity: "embedding-based similarity" framing — when is it wrong for math invariants?

Cite 6+ primary sources.
```

---

### Prompt 11: G13 Relation-Weakening — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G13. v1: PLUGIN ONLY, syntactic regex on claim text using _predicate_lattice.

TASK:

1. Strongest objection to v2's SMT-solver semantic weakening (Z3).

2. Strongest feature.

3. Sister plugin G14 strengthening — does v2's semantic-weakening machinery transfer to strengthening?

4. Z3 vs cvc5 vs alternative SMT solvers for predicate weakening — pick one. Cite.

5. Proof-mining integration — is it load-bearing for v2 or aspirational?

6. Steelman: "weakened claims are usually degenerate" — engage and propose threshold criteria.

7. Anti-gravity: "abstract interpretation" framing — what's the contrarian?

Cite 6+ primary sources.
```

---

### Prompt 12: G14 Relation-Strengthening — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G14 (R8 tier — representation shift). v1: PLUGIN ONLY.

TASK:

1. Strongest objection to v2's safe-strengthening type guard + extremal-region detection.

2. Strongest feature.

3. The "upgrade the parent vs promote new G14 claim" distinction — does v2 handle this correctly?

4. Cross-plugin G14-G16-G18 loop proposed in DR — is it well-defined or speculative?

5. 2024-2027 conjecture-strengthening literature — has any computational system actually done this? Cite.

6. 2 strengthening scenarios v2 mis-classifies (false strong-form survival vs true strong-form survival).

7. Anti-gravity: "automated conjecture refinement" framing — contrarian alternative?

Cite 6+ primary sources.
```

---

### Prompt 13: G15 Cross-Generator MI — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G15 (v1 + v2 shipped). LIVE: v1 MI=1.41 nats (89% bookkeeping); v2 MI=0.158 (Pollux normalization residual). ITER-13 G15 finding doc.

TASK:

1. Strongest objection to v2's Bayesian Dirichlet-prior Shannon MI + conditional MI on parent_problem.

2. Strongest feature.

3. The control-flow suffix filter is per-version-fragile. v3's learned classifier — would it overfit on small ledger? Cite.

4. Cross-instrument triangulation as MI-equivalent — does v2's "claims observed by ≥3 distinct plugins" detector correctly identify the Salem moderation 4-instrument case?

5. Steelman: "MI is the wrong statistic" — engage. What replaces it?

6. 2 scenarios v2 mis-classifies.

7. Anti-gravity: "MI estimation" framing — when is something else better?

Cite 7+ primary sources.
```

---

### Prompt 14: G16 Anti-Anchor — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G16. v1 + ITER-19 refinement (perm-null over band). LIVE: at adversarial_M=1.20, anchor survives, structurally_different=True.

TASK:

1. Strongest objection to v2's percentile-based adversarial value + confound-stratified perm null.

2. Strongest feature.

3. Adversarial example generation for math objects — has any 2024-2027 system done this WELL? Cite specifically.

4. Lethe→G16 hand-off protocol — is it well-defined or speculative?

5. Steelman: "anchor survives 10× adversarial" is weak evidence. Engage.

6. 2 scenarios v2 mis-classifies.

7. Anti-gravity: conventional "adversarial robustness testing" (from ML) — when does it not transfer to math objects?

Cite 6+ primary sources.
```

---

### Prompt 15: G17 Causal-Intervention — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G17. v1 + ITER-18 multi-threshold sweep. LIVE: M=1.26 phase transition detected. ITER-18 finding doc (`pivot/erebos_substrate_finding_iter18_g17_salem_phase_transition_2026-05-26.md`).

TASK:

1. Strongest objection to v2's do-operator intervention (beyond label shuffle) + intervention chains.

2. Strongest feature.

3. The M=1.26 finding — is it substrate-grade or sampling artifact? What 0.005-resolution refit at 1000 perms would conclude?

4. Pearl Rung 2 do-operator on math catalogs — is it well-defined? Cite category-theoretic causal-inference work 2024-2027.

5. Steelman: "G17 only validates known structure." Engage.

6. 2 intervention-chain scenarios v2 mis-classifies.

7. Anti-gravity: conventional "average treatment effect" framing — contrarian?

Cite 7+ primary sources.
```

---

### Prompt 16: G18 Minimal-Counterexample — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G18. v1: g18_lehmer_degree_band; ITER-10 substrate self-correction (epsilon fix for Lehmer × Φ_16 false positive).

TASK:

1. Strongest objection to v2's factorization-aware cyclotomic-extension filter + Voronoi-cell region prediction.

2. Strongest feature.

3. Voronoi over (degree, M) — what's the right distance metric? Cite.

4. Counterexample-search systems 2024-2027 (SMT-based, neural-guided) — does any reach substrate-grade reliability? Cite.

5. Post-success protocol if G18 actually finds a Lehmer counterexample — is it well-specified?

6. Steelman: "G18 is biased toward famous conjectures." Engage.

7. Anti-gravity: "neural counterexample synthesis" — when wrong?

Cite 6+ primary sources.
```

---

### Prompt 17: G19 Proof-Obligation — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G19. v1 + v2 (recursive BFS to leaves, cycle detection).

TASK:

1. Strongest objection to v3's Lean 4 integration + formal obligation extraction.

2. Strongest feature.

3. Lean 4 integration — concrete protocol? Read LeanDojo / COPRA / LeanInfer 2024-2027 work and cite.

4. Cycle classification (legitimate vs pathological) — how does v3 distinguish?

5. Proof-mining integration with Kohlenbach school — load-bearing or aspirational?

6. Steelman: "G19 re-implements Lean tactics poorly." Engage.

7. Anti-gravity: "LLM-generated proof obligations" — why wrong here?

Cite 7+ primary sources.
```

---

### Prompt 18: G20 Instrument-Disagreement — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G20. v1: PLUGIN ONLY, vacuous-until-Lethe-v2.

TASK:

1. Strongest objection to v2's synthetic instrument-disagreement seeding (Pollux vs Stygian as MVP).

2. Strongest feature.

3. Concept K extraction — BERT vs tf-idf vs NER for math concepts. Pick one. Cite.

4. Meta-epistemic finding framing — where should G20 outputs route in the Prometheus stack?

5. Steelman: "G20 is a distraction." Engage seriously.

6. 2 disagreement scenarios v2 mis-classifies.

7. Anti-gravity: "ensemble disagreement uncertainty" — when wrong?

Cite 5+ primary sources.
```

---

### Prompt 19: G22 Subgraph / Clique — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G22. v1: hand-rolled Louvain.

TASK:

1. Strongest objection to v2's Leiden algorithm + master-property extraction.

2. Strongest feature.

3. Leiden vs SBM (stochastic block models) — pick the right one for claim-graphs. Cite.

4. Master-property extraction via shared-predicate mining — does any 2024-2027 system do this for math claims? Cite.

5. G22-G18-G06 joint loop proposed in DR — load-bearing or speculative?

6. Steelman: "420 paired observations is too small for clique detection." Engage.

7. Anti-gravity: conventional "community detection" — when wrong for math claims?

Cite 6+ primary sources.
```

---

### Prompt 20: G23 Asymptotic Limit — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G23. v1 + ITER-17 multi-law fit. LIVE: 1/log(N) is best-fit law with R²=0.54.

TASK:

1. Strongest objection to v2's broken power-law detector + multi-complexity-measure sweep + bootstrap CIs.

2. Strongest feature.

3. The 1/log(N) finding — is it novel? Cite Lehmer-asymptotic literature 2024-2027.

4. R²=0.54 vs R²=0.51 — is the 0.03 advantage statistically real? Bootstrap procedure to resolve.

5. Coefficient-height vs degree as complexity measure — which is right for Mossinghoff?

6. Steelman: "best-fit law is sampling-driven." Engage.

7. Anti-gravity: "model comparison via AIC/BIC" — contrarian alternative?

Cite 7+ primary sources, ≥2 on Lehmer-asymptotic bounds.
```

---

### Prompt 21: G24 Symmetry / Twist — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G24. v1 + v2 (200/200 pass on both x→-x and x→1/x).

TASK:

1. Strongest objection to v3's complete Mahler-preserving symmetry suite + per-symmetry audit of all catalog fields + calibrated tolerance.

2. Strongest feature.

3. Galois orbit closure check — concrete protocol? Cite SageMath / PARI primitives.

4. Steelman: "G24 is redundant with Mossinghoff's own computation." Engage.

5. Conjectured-but-not-proven Mahler-preserving symmetry — does v3 propose such tests as substrate-grade evidence?

6. 2 symmetry audits v3 will not catch despite the expanded suite.

7. Anti-gravity: "catalog data audit" framing — when too narrow?

Cite 6+ primary sources.
```

---

### Prompt 22: G25 Degeneracy / Trivial-Case — frontier critique

```text
[Doctrine + Erebos overview above]

Critique v2 of G25. v1: g25_lehmer_degenerate.

TASK:

1. Strongest objection to v2's entropy-based effective-sample-size + tail-collapse detection + cross-plugin alert protocol.

2. Strongest feature.

3. The ITER-12 G11 v1 tautology — argue why G25 v1 missed it and what v2 catches that v1 doesn't.

4. Steelman: "degeneracy is a property of the question, not the data." Engage. Is G25 the right architectural slot?

5. Effective-sample-size for math-catalog data — what's the right formula? Cite.

6. 2 degeneracy scenarios v2 misses.

7. Anti-gravity: conventional "missing data / small-N corrections" framing — when wrong for math catalogs?

Cite 6+ primary sources.
```

---

## Multi-model triangulation protocol

For each prompt:
1. Send to Gemini 2.5 / Deep Research mode
2. Send same prompt to GPT-5 (or latest ChatGPT)
3. Send to Claude Opus / Sonnet (whichever latest)
4. Send to DeepSeek

For each of the 4 responses, extract:
- The strongest-objection top pick
- The recommended primary citation
- The kill_pattern failure prediction

Cross-model agreement on any of these is substrate-grade signal. Cross-model disagreement is a v2-design uncertainty worth resolving via additional experimentation.

Aggregate the 22 × 4 = 88 responses into a per-plugin "frontier consensus" doc per plugin, and an Erebos-wide synthesis identifying:
- Plugins where all 4 models converge on the same critique (the substrate has a real weakness there)
- Plugins where the 4 models diverge wildly (the substrate has an ambiguity worth investigating)
- Plugins where ≥1 model identifies a substrate-grade alternative we should ship instead of v2 as currently proposed

That synthesis becomes the input to ITER-21+ work on the unblocked plugins.
