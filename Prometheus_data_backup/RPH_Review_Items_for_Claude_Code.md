# RPH Pipeline: Review Items from Claude Conversation
## Suggestions, Warnings, Overstatement Risks, and Metric Tuning Notes
### For synthesis into project documentation by Claude Code

---

## Coherence Gaussian Calibration (HIGHEST PRIORITY)

- The Gaussian over log-perplexity is the highest-risk component of the fitness function (Section 11.1 of RPH)
- At 1.5B, the perplexity distribution shifts relative to 0.5B — baseline outputs are more fluent, so the "structured weirdness" window moves
- If the Gaussian was calibrated on 0.5B data, it may inadvertently filter out exactly the specimens we want at 1.5B
- ACTION: Pull the raw perplexity distribution from the first few hundred evaluations of the calibration run and verify the target window captures structured-but-unusual outputs rather than rewarding near-default fluency
- This recalibration is needed at every scale transition (0.5B → 1.5B → 3B → larger)

---

## MI_step Estimator Weakness (CRITICAL FOR PUBLICATION)

- The current MI_step implementation (correlation-based proxy after PCA to 64 components) is the weakest link in the measurement chain
- The gap between what MI_step is supposed to measure (genuine inter-step causal dependency) and what correlation on PCA-reduced hidden states actually captures is significant
- Risk: conflating any form of sequential structure with genuine reasoning dependency
- Reviewers at NeurIPS will push hard on this specific metric
- ACTION: Prioritize getting a k-NN estimator or MINE (Mutual Information Neural Estimation) working before the main experimental runs
- At minimum, document the limitation explicitly and show robustness across PCA dimensions (32, 64, 128) as a partial mitigation

---

## Secondary Gradient Existence (THEORETICAL RISK)

- Section 4.3's argument that structured novelty accidentally selects for reasoning is the theoretical linchpin and the most speculative claim
- The bet: the intersection of "novel" and "coherent" is small enough that reasoning dominates it
- Counterargument: if that intersection is crowded with other structured-but-non-reasoning modes (creative recombination, stylistic shifts, domain-transfer artifacts), the secondary gradient won't materialize
- The 5% threshold in Section 11.4 is the right falsification criterion — watch it carefully
- ACTION: Track the fraction of high-novelty specimens showing elevated Δ_cf or MI_step from the earliest runs and flag immediately if it's trending below 5%

---

## Pseudo-Formal Structure Detection (PRIMARY FAILURE MODE)

- The system could converge on outputs exhibiting stylized complexity — formal-looking language, mathematical notation, logical connectives — without genuine causal reasoning
- This "meta-linguistic mode" produces text that talks about reasoning without performing it
- At frontier scale, this failure mode gets much more convincing — the word salad becomes extremely polished
- Detection: pseudo-formal outputs show low Δ_cf and low MI_step despite high surface-level formality
- ACTION: Ensure the Prometheus dual-classifier architecture is operational and tested before main runs — one classifier for structural coherence, one for causal dependency

---

## Persona Collapse as Diagnostic at 1.5B

- If clean field-biologist-type attractor collapses are still visible at 1.5B, the heuristic basin is still dominant enough for stereotyped fallback — this is informative data for RPH
- If responses are more fragmented and mixed-mode, the landscape has more competing shallow basins
- Either outcome constrains basin geometry at that scale
- ACTION: Log and categorize persona collapse patterns during calibration run — this is free data about attractor structure

---

## α Sweep Shape Is the Key Scaling Diagnostic

- The shape of the α sweep curve at 1.5B relative to 0.5B is the single most informative early comparison
- Sharp phase transition at 1.5B = strong evidence for metastable regime hypothesis and green light for full pipeline
- Smooth/gradual curve = either the separatrix is wider (harder to cross cleanly) or there's a continuum rather than discrete boundary at this scale
- If it's already smoothing significantly at 1.5B, that's an early warning about the scaling wall
- ACTION: Capture raw α sweep data from the start of the calibration run — do not defer to a second pass

---

## Overstatement Risk: "Scientific Discovery" Framing

- The waste stream exploration should NOT be framed as "the model discovers new science"
- The defensible claim: the model's weights encode a compressed, structured map of relationships between scientific concepts, and probing the waste stream identifies where boundaries between fields are closest — where connections might exist but haven't been explored
- The model is a structured index, not a scientist — it points at intersections, it doesn't reason across them
- The text output bottleneck is what we're bypassing; the tensor structure in the weights is what we're probing
- ACTION: Review all documentation for language that implies the model is generating scientific insights rather than revealing proximity structure in its knowledge map

---

## Overstatement Risk: "Reasoning Circuits" and "Emergence"

- Calling internal model structures "reasoning manifolds" that exhibit "emergence" overstates what mechanistic interpretability has demonstrated
- What's actually documented: features, circuits, directions in activation space that correspond to meaningful concepts (negation detection, entity tracking, rudimentary logical consistency checking)
- Better framing: increasingly reliable heuristics that approximate reasoning in many common cases
- What looks like meta-reasoning in large models is often better described as learned rhetorical calibration — the model has learned that certain topics call for hedging, not that it's reasoning about its own limits
- ACTION: Audit documentation for claims about "emergence" or "reasoning circuits" and replace with more precise language about learned heuristics and internal structure

---

## Overstatement Risk: Large Model "Understanding"

- Large models haven't crossed into genuine reasoning — they've developed sophisticated pattern matching over argumentative structures
- They produce appropriate epistemic hedging because their training data packages those topics with caution, not because they're independently evaluating argument strength
- Failure modes revealing this: novel combinations of frontier concepts still trip up large models; subtle category errors get through (bridging mathematical and physical notions of "dimension" without flagging the analogy); long chains of reasoning under genuine uncertainty drift toward statistically likely conclusions rather than tracking logical structure
- ACTION: Where documentation describes model capabilities, distinguish between "learned to mimic the form of reasoning" and "actually reasoning"

---

## THOR Integration: TT-Rank Selection

- The TT-rank design is a make-or-break decision for whether the tensor train representation preserves cross-field proximity structure
- Do NOT decide TT-ranks theoretically — decide them by examining singular value spectra of actual residual captures and identifying where meaningful structure separates from noise floor
- Risk: naive truncation may throw away exactly the modes that are interesting for this application
- The interesting structure might live at ranks a standard physics-oriented decomposition would discard
- ACTION: Defer TT-rank decisions until real tensor shapes are in hand; build the pipeline to capture spectra first and parameterize rank selection

---

## THOR Adaptation Challenge

- THOR's tensor network integrators are designed for smooth, continuous functions on regular grids
- Residual stream activations are neither smooth nor regularly sampled
- The natural tensor index structure: specimen × layer × token_position × d_model_component
- The TT cores should capture how activation patterns factor across those axes
- ACTION: Design the adaptation layer carefully — structure tensor indices so decomposition captures meaningful modes rather than artifacts of dimension ordering

---

## NemoClaw: Early Alpha Stability

- NemoClaw is explicitly described by NVIDIA as early-stage Alpha software — expect rough edges
- Fine for research pipeline, but build with the assumption that APIs and interfaces will change
- ACTION: Abstract the NemoClaw integration behind clean interfaces so framework changes don't cascade through the pipeline

---

## Cross-Model Arcanum: Sample Size Caution

- Current sample of ~1,600 specimens with rigs only halfway through evaluation
- Very few score well across models — but this is expected at this stage and sample size
- We are in the "is there signal at all" phase, not the "characterize the signal" phase
- ACTION: Do not draw conclusions about cross-substrate persistence until the full batch completes; report the rarity honestly as a constraint on universality claims

---

## Scaling Concern: Scale Window Hypothesis

- Precipitation vectors might be a real phenomenon that only exists in a scale window — large enough to have reasoning circuitry, small enough that basins are shallow enough to cross
- This would still be a publishable and interesting finding, but it's a narrower claim than the strong RPH
- The 1.5B calibration run is the first real data point on whether this is the case
- ACTION: Frame the hypothesis to accommodate this outcome — present it as an informative constraint rather than a failure if scale-limited

---

## Brute Force vs. Precision at Scale

- At 30B+, brute-force MAP-Elites evolutionary search for precipitation vectors is likely intractable — search space too large, signal too subtle
- The viable approach: use tensor train decomposition to characterize separatrix geometry first, then design targeted perturbations that exploit thin points
- Timing matters: injection timed to moments when the trajectory is already near the separatrix (self-correction events, high-uncertainty processing) requires far less energy than injection from rest
- ACTION: Build the pipeline to support timed injection (per-token or per-step vector application/removal) from the start, not as an afterthought

---

## Base vs. Instruct Model Control

- The RPH attributes suppression to RLHF, but two distinct mechanisms may be at play: (1) alignment shaping outputs toward agreeableness, (2) next-token pretraining biasing toward short-horizon prediction
- If precipitation effect is present only in instruct model → RLHF is primary suppressor
- If present in both base and instruct → suppression is a deeper pretraining artifact
- ACTION: Ensure base model variants are available and tested alongside instruct models at each scale

---

## Data Capture Completeness

- Do not plan for second-pass data capture — capture everything from the start
- Raw α sweep data, perplexity distributions, persona collapse patterns, residual stream activations, logit distributions at each generation step
- Storage is cheaper than re-running experiments
- ACTION: Verify that the calibration run logging captures all raw data needed for every downstream analysis before it completes

---

## Publication Framing

- The strongest framing is NOT "we found a reasoning vector"
- The strongest framing IS: "reasoning emerges when trajectories enter a specific structured subspace of activation space, which can be reached via linear perturbations and is mediated by sparse feature circuits"
- If results hold, the four defensible claims are:
  1. There exist linear directions that increase counterfactual sensitivity and internal information flow (causal)
  2. These directions align with endogenous activation patterns during reasoning (endogeneity)
  3. Effects are mediated through sparse, identifiable feature subspaces (mechanism)
  4. Reasoning corresponds to a low-measure, structured region in activation space (structure)
- ACTION: All documentation should build toward these four specific claims and not overreach beyond what the data supports
