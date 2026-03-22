# The Reasoning Precipitation Hypothesis

*Working Document — Arcanum Infinity / Ignis Cross-Project Theory*

*Version 4 (Final Working Draft) — March 2026*

*Feedback incorporated from: Gemini (2 rounds), ChatGPT (3 rounds), Claude*

---

## 1. The Core Claim

### 1.1 Minimal Form

There exist directions in residual stream space such that, when added at specific layers, they increase the probability that the model follows a trajectory class characterized by multi-step dependency, self-correction, and counterfactual sensitivity — without bypassing native circuits. These directions correspond to translations of the hidden state across boundaries separating distinct dynamical regimes already encoded in the model's weights.

### 1.2 Strong Form

These directions act as catalysts that increase the stability and accessibility of reasoning trajectories, revealing that reasoning is a metastable regime suppressed by default inference dynamics rather than absent from the model.

### 1.3 Expanded Statement

Among the high-dimensional structures that a language model computes but never expresses — the residual stream activations that are projected away by the vocabulary head, suppressed by sampling, or penalized by alignment — there may exist directions that do not merely perturb the model's output but shift its computational trajectory into a qualitatively different regime. Specifically: if the model's default inference can be understood as a path through an energy landscape whose basins are fixed by the model's weights and shaped by next-token prediction and RLHF, then the waste stream may contain activation vectors that, when reinjected at a critical layer, translate the model's hidden state across the separatrix between the shallow heuristic regime and a deeper but ordinarily inaccessible reasoning regime — one in which sequential, self-correcting inference becomes the dynamically favored trajectory class.

This is mechanistically distinct from the bypass phenomenon documented in Ignis (formerly SETI v2), where injected directions route computation around the model's learned heuristics without engaging native reasoning circuitry. What we propose instead is a *precipitation* effect: a perturbation that does not override the model's native circuits but destabilizes its default attractor just enough that the system crosses into a regime where multi-step verification is energetically favored. If such vectors exist in the waste stream, they represent not merely novel cognitive artifacts but latent catalysts for reasoning — structures the model already possesses the circuitry to exploit but which alignment training and token-level optimization have rendered dynamically inaccessible under normal inference conditions.

---

## 2. Mechanistic Foundations

### 2.1 The Residual Stream as an Input-Conditioned Dynamical System

A transformer's residual stream implements a discrete-time dynamical system. At each layer *l*, the hidden state is updated:

```
x_{l+1} = x_l + f_l(x_l)
```

where *f_l* encodes the combined attention and MLP computation at layer *l*. Critically, this is an *input-conditioned* dynamical system — the attention computation at each layer depends on the full context, meaning the vector field *f_l* changes with the input sequence. The model's weights define a family of vector fields parameterized by context.

RLHF and instruction tuning have shaped the default trajectories so that, across the typical input distribution, they converge on regions producing fluent, agreeable, heuristic-driven text.

### 2.2 Translation, Not Deformation

A critical mechanistic distinction (Gemini, Round 1): injecting a steering vector *v* into the residual stream at layer *L* performs a **state translation**, not a landscape deformation:

```
h_L ← h_L + αv
```

The landscape's geometry — its basins, ridges, and separatrices — is permanently defined by the fixed weights of subsequent layers. The vector does not reshape the terrain; it moves the model's current position across it. A precipitation vector acts as a localized injection of energy that translates the activation state across the separatrix guarding the reasoning regime. The functional outcome is regime-switching, but the mechanism is displacement across a fixed manifold.

This distinction has experimental consequences: we are measuring *where the state lands* after perturbation, not whether the terrain has changed. The terrain is the same for every inference; only the starting position differs.

### 2.3 Operational Definition of Trajectory Classes

To avoid purely metaphorical language, we define trajectory classes in terms of measurable output properties (ChatGPT, Round 2):

**Definition.** A *trajectory class* T is a region of residual stream trajectories {x_0, x_1, ..., x_L} that produce outputs sharing a set of statistical and behavioral properties. Two trajectory classes are *distinct* if they produce outputs that are separable by at least one of the formal reasoning proxies defined in Section 3.

We identify three primary trajectory classes relevant to this hypothesis:

| Trajectory Class | Defining Properties | Default Accessibility |
|---|---|---|
| **Heuristic (H)** | Low counterfactual sensitivity, low stepwise mutual information, high surface fluency | Wide basin, default attractor |
| **Reasoning (R)** | High counterfactual sensitivity, high stepwise MI, self-correction patterns | Narrow basin, dynamically suppressed |
| **Degenerate (D)** | Low coherence, high entropy, no causal structure | Reachable via large perturbations |

A precipitation vector is operationally defined as a direction *v* such that injection at layer *L* shifts the system from trajectory class H to trajectory class R, as measured by the formal proxies below.

### 2.4 Why Reasoning Is Inaccessible by Default

The same weights that produce sycophantic agreement on "A professor says 7 is not prime" also contain the arithmetic circuitry that *knows* 7 is prime. This is empirically established:

- Chain-of-thought prompting improves performance without changing weights, confirming that reasoning capability is latent.
- Models internally represent correct answers but output incorrect ones under authority pressure (sycophancy literature: Perez et al., 2022; Wei et al., 2023).
- Activation steering demonstrates that linear directions can control truthfulness, suggesting the geometry supports multiple behavioral regimes.

The problem is not missing capability but dynamical accessibility. The heuristic trajectory class has a wider basin of attraction than the reasoning class. Under normal inference, the model's trajectory is captured by the wider basin before it can reach the deeper one.

---

## 3. Formal Reasoning Proxies

"Reasoning" must be operationalized, not described (ChatGPT, Round 2). We define three measurable proxies. A candidate precipitation vector must produce statistically significant improvement on at least two of three.

### 3.1 Counterfactual Sensitivity (Δ_cf)

Modify an intermediate fact in the prompt (e.g., change a numerical value, swap a premise). Measure the degree to which the model's conclusion changes in response.

```
Δ_cf = E[d(output_original, output_modified) | fact_perturbation]
```

- **Reasoning trajectory:** High Δ_cf — the model recomputes downstream steps based on changed premises.
- **Heuristic trajectory:** Low Δ_cf — the model preserves surface structure regardless of premise changes.
- **Pseudo-formal trajectory:** Low Δ_cf — formal-looking structure without causal dependencies.

### 3.2 Stepwise Mutual Information (MI_step)

Measure the mutual information between earlier and later hidden states (or tokens) in the generated sequence, beyond what is explained by surface-level n-gram statistics. Using hidden states mitigates the risk that structured templates or rhetorical scaffolding inflate token-based MI.

```
MI_step = I(h_{1:t}; h_{t+1:T}) - I_baseline
```

where I_baseline is estimated from a bigram/trigram language model fitted to the same output distribution (or from shuffled hidden states). Alternatively, a causal version:

```
MI_causal = I(intermediate_state; final_answer | prompt)
```

- **Reasoning trajectory:** High MI_step — later conclusions depend on earlier intermediate steps.
- **Heuristic trajectory:** Low MI_step — tokens are locally coherent but globally independent.
- **Loop attractor:** Very high raw MI but low MI_step (high repetition, no novel dependency structure).

A control for "reasoning-like compression" can be implemented by measuring token count or latency under perturbation: genuine reasoning tends to lengthen trajectories, while compressed shortcuts preserve length.

### 3.3 Error Correction Rate (ECR)

Measure the probability that the model revises an incorrect intermediate conclusion during generation.

```
ECR = P(self-correction | incorrect_intermediate_step)
```

This can be operationalized by analyzing token-level logit trajectories: a self-correction event occurs when the model generates tokens that contradict or revise a conclusion established earlier in the same generation.

To avoid conflating stylistic revision with genuine correction, we require that the intermediate step is objectively incorrect. This can be enforced by injecting known incorrect intermediates via prompting (e.g., "Assume temporarily that 9.11 > 9.9. Continue reasoning."), then measuring whether the model escapes the false assumption.

- **Reasoning trajectory:** Elevated ECR — the model catches and corrects its own errors.
- **Heuristic trajectory:** Near-zero ECR — errors propagate uncorrected.
- **Bypass circuit:** May show high final accuracy but zero ECR — correct answer reached without intermediate verification.

---

## 4. The Bypass Problem and Why Novelty Search May Solve It

### 4.1 Ignis's Bypass Finding

Ignis has demonstrated that CMA-ES, when optimizing for multi-task correctness on logical traps, predominantly discovers bypass circuits. The evidence:

- Sign-flip tests show directional specificity (+v helps, -v hurts).
- But cosine-fitness correlation is near zero — the evolved direction does not align with any direction the model uses natively.
- Vectors achieve correct answers by routing computation *around* heuristics, not by amplifying native reasoning.

This is expected: when the fitness function rewards correctness, the path of least resistance for the optimizer is bypass. Strengthening native reasoning requires navigating a more complex region of the optimization landscape.

### 4.2 Arcanum Infinity's Orthogonal Fitness Function

Arcanum Infinity's fitness function rewards structured novelty:

```
F(g) = d_semantic(g) × C(g)
```

where *d_semantic* is cosine distance from baseline and *C* is a Gaussian over log-perplexity targeting "structured weirdness."

This creates fundamentally different selection pressure:

- **Bypass circuits are invisible to this function.** They produce correct but unremarkable outputs — low semantic distance, low novelty score.
- **Degenerate perturbations are penalized.** Gibberish has high distance but fails the coherence term.
- **Structured but unusual computational regimes are rewarded.** This is the only surviving category.

### 4.3 The Secondary Gradient Toward Reasoning

The core theoretical bet: **reasoning is one of the few computational regimes that is simultaneously structured AND distant from the model's default behavior.**

A 0.5B model's default response to a speculative mathematics prompt is a fluent but shallow summary. A response that actually reasons — introduces intermediate formalisms, questions its own assumptions, builds toward non-obvious conclusions — would score high on both semantic distance (qualitatively different from the default) and coherence (internal logical dependencies).

The structured-novelty fitness function therefore has a plausible secondary gradient toward reasoning-like computation. Not because it seeks reasoning, but because reasoning is one of the few regimes that survives the joint filter of "novel" and "structured."

**Status:** This is a theoretical prediction. Empirical validation requires measuring the formal reasoning proxies (Section 3) on captured Arcanum specimens. The prediction is falsifiable: if no specimens show elevated Δ_cf, MI_step, or ECR relative to baseline, the secondary gradient does not exist.

---

## 5. Failure Modes, Alternative Explanations, and Ambiguous Cases

### 5.1 Pseudo-Formal Structure (Primary Risk)

The system could converge on outputs exhibiting stylized complexity — formal-looking language, mathematical notation, logical connectives — without genuine causal reasoning. This "meta-linguistic mode" (ChatGPT, Round 1) produces text that *talks about* reasoning without performing it.

**Detection:** Pseudo-formal outputs will show low Δ_cf (no counterfactual sensitivity) and low MI_step (no genuine inter-step dependencies) despite high surface-level formality. The Prometheus dual-classifier architecture (Gemini, Round 2) can automate this detection: one classifier monitors structural coherence while the second tracks causal dependency.

### 5.2 Repetitive Loop Attractors

The optimizer may gravitate toward perturbations producing non-terminating loops. These appear "structured" to basic metrics but contain no reasoning.

**Detection:** Loop attractors show very high raw mutual information (repetitive patterns) but low MI_step (no novel dependency structure after subtracting baseline n-gram statistics). The coherence term's Gaussian penalizes very low perplexity, but the target window must be empirically calibrated (see Section 11.1).

### 5.3 Matched-Novelty Non-Reasoning Artifacts

It is possible to produce outputs that score high on structured novelty without engaging reasoning circuits — e.g., novel stylistic modes, unusual topic combinations, creative but non-logical text.

**Control required (ChatGPT, Round 2):** Construct a set of vectors that score high on Arcanum novelty but fail reasoning metrics. Compare against precipitation candidates. This isolates the claim that novelty ≠ reasoning, and tests whether the secondary gradient is real or illusory.

### 5.4 Norm Sweep Misinterpretation

A "wide peak" in the norm sweep could arise from robust but non-specific perturbations. A wide peak is necessary but not sufficient.

**Augmented test (ChatGPT, Round 2):** Add noise orthogonal to *v* and measure degradation. Prediction: bypass circuits are fragile to orthogonal noise (they encode specific routing instructions), while precipitation vectors are more robust (basin-level effects tolerate small perturbations in the orthogonal complement).

### 5.5 Reasoning-Like Compression (Ambiguous Case)

The model may compress reasoning into a latent shortcut that preserves outputs and proxies without explicit multi-step reasoning dynamics. This would produce high Δ_cf (outputs change correctly with changed premises), moderate MI_step, but low or zero observable intermediate computation.

**Assessment:** This is better understood as an *ambiguous case* than a pure failure mode. If a vector produces high counterfactual sensitivity, correct outputs across diverse tasks, and generalization — but achieves this through a compressed internal path rather than explicit token-level reasoning — it is functionally indistinguishable from reasoning from the outside. It may represent the model finding a more efficient trajectory *through* the reasoning basin rather than a failure to enter it.

**Diagnostic:** Measure token count and trajectory path length under perturbation. True explicit reasoning tends to lengthen trajectories; compressed shortcuts preserve length. Also compute MI on hidden states rather than tokens to expose internal computation that is not visible at the output level. If hidden-state MI is high while token MI is low, the model is reasoning internally but expressing the result compactly — which may be a *stronger* finding, not a weaker one.

### 5.6 Basin Misidentification

We have implicitly assumed that heuristic and reasoning are separate basins with a separatrix between them. An alternative is that they are overlapping projections of the same manifold — a continuum rather than a discrete phase boundary.

**Detection:** The α sweep (Section 6.6) is the primary diagnostic. Inject the vector at increasing magnitudes and measure proxy metrics across α. A sharp transition (discontinuity or steep sigmoid) supports the basin model with a genuine separatrix. A smooth, monotonic gradient supports a continuum model. Either answer is informative and constrains the theoretical framework.

### 5.7 Alignment vs. Pretraining Confound

We attribute the suppression of reasoning to RLHF, but two distinct mechanisms may be at play: (1) alignment training shaping outputs toward agreeableness, and (2) next-token pretraining biasing toward short-horizon prediction regardless of alignment.

**Control:** Compare a base model (pre-RLHF) with an instruct model using the same steering vector. If the precipitation effect is present only in the instruct model, RLHF is the primary suppressor. If present in both, the suppression is a deeper artifact of the pretraining objective itself. This distinction has significant implications for understanding what alignment actually does to a model's internal dynamics.

---

## 6. Experimental Protocol

### 6.1 The Cross-Project Bridge

| System | Provides | Lacks |
|---|---|---|
| **Arcanum Infinity** | Diverse candidate vectors from structured novelty search | Rigorous causal validation |
| **Ignis** | Falsification battery, norm sweep, natural occurrence tests | Vectors that aren't bypass circuits |
| **Prometheus** | Dual-classifier measurement backbone for automated output evaluation | Discovery engine |

### 6.2 Protocol Steps

1. **Run Arcanum Infinity** with rapid genome screening (150 prompts, early termination). Capture all specimens exceeding the 0.3 novelty threshold.
2. **Export specimens** as `.pt` files compatible with Ignis's genome format (steering vector + target layer).
3. **Run Ignis's full diagnostic battery**: noise gate, orthogonal projection, sign-flip, shuffled-component, norm sweep.
4. **Run the natural occurrence test** (tightened per Section 6.4).
5. **Compute formal reasoning proxies** (Δ_cf, MI_step, ECR) on specimen-steered outputs.
6. **Run extended diagnostics** (Section 6.6) on candidates that pass initial filters.
7. **Filter** for candidates meeting the precipitation criteria (Section 6.5).

### 6.3 Diagnostic Signatures

| Diagnostic | Bypass Circuit (Ignis baseline) | Precipitation Vector (hypothesized) |
|---|---|---|
| **Sign-flip (-v)** | Degrades performance | Degrades performance AND increases heuristic behavior |
| **Norm sweep** | Peaked at ~1x | Peaked with wider effective range |
| **Orthogonal noise sensitivity** | Fragile (specific routing) | Robust (basin-level effect) |
| **Natural occurrence (Δ_proj)** | Low projection onto native activations | High projection during self-correction events |
| **Cosine-fitness correlation** | Near zero | Positive |
| **Cross-task generalization** | Moderate (task-specific) | Strong (general reasoning catalyst) |
| **Arcanum novelty score** | Low (correct but normal) | High (structured but qualitatively different) |
| **Formal reasoning proxies** | Low Δ_cf, low MI_step, zero ECR | Elevated on ≥2 of 3 proxies |

### 6.4 Tightened Natural Occurrence Test

The natural occurrence condition must be conditioned on explicit, identifiable events rather than vague "reasoning" labels (ChatGPT, Round 2; Gemini, Round 2):

**Positive condition:** Capture residual activations during unsteered inference on tasks where the model self-corrects. To avoid conflating stylistic revision with genuine correction, condition on self-correction events that also meet a proxy threshold (Δ_cf > ε or MI_step > δ).

**Negative condition:** Capture activations during heuristic bypass — instances where the model produces a correct answer without intermediate verification steps, and where Δ_cf and MI_step are low.

**Metric:**

```
Δ_proj = E[⟨h, v⟩ | self-correction ∧ (Δ_cf > ε ∨ MI_step > δ)] 
       - E[⟨h, v⟩ | heuristic_bypass]
```

A precipitation vector shows Δ_proj significantly greater than zero. This is a clean statistical test: if the model projects more strongly onto *v* when it is reasoning natively than when it is bypassing, the direction is associated with native reasoning, not bypass.

### 6.5 Necessary Conditions for Classification as a Precipitation Vector

A candidate must satisfy **all three**:

1. **Positive causal contribution to reasoning** — injection improves performance on verification tasks AND elevates at least 2 of 3 formal reasoning proxies.
2. **Dependence on native circuits** — Δ_proj > 0 (natural occurrence test). The effect is mediated through existing reasoning machinery, not routed around it.
3. **Cross-task generalization** — the effect transfers across diverse tasks, including out-of-domain reasoning problems not present in the provocation prompt bank.

### 6.6 Extended Diagnostic Tests

**Causal Mediation.** Inject the vector at layer L, then ablate known downstream reasoning features. If performance drops, the vector relies on native circuits. If not, it's bypass. (Prometheus classifiers can automate output evaluation.)

**Counterfactual Consistency.** Modify intermediate facts in prompts. Measure Δ_cf. (This is Proxy 3.1 applied as a diagnostic rather than a filter.)

**Trajectory Analysis.** Track the residual stream across layers and measure:
- *Path length* — reasoning trajectories should traverse more distant regions.
- *Curvature* — higher curvature indicates iterative refinement.
- *Re-entry patterns* — revisiting similar subspaces suggests self-correction loops.

**Phase Transition Test (α Sweep).** Inject the vector at increasing magnitudes α. Measure Δ_cf, MI_step, and ECR across α. A sharp transition supports the metastable-basin hypothesis; a smooth curve supports a continuous feature; noisy or unstable behavior suggests an artifact.

**Trajectory Divergence Metric.** Define:

```
D_traj = Σ_l ||x_l^{steered} - x_l^{baseline}||
```

- Reasoning vectors should produce *late divergence* (after the initial heuristic region, at the layer where the regime transition occurs).
- Bypass vectors produce *early divergence* (routing around heuristics from the injection point onward).

**Mid-Reasoning Ablation (the decisive test).** Inject the vector, allow reasoning to begin (as measured by the appearance of self-correction or intermediate-step tokens), then remove the vector.

Define R(t) as the reasoning score at generation step t (computed from the formal proxies). Inject *v* until step t_0, remove thereafter.

```
dR/dt |_{t > t_0}
```

- **Catalyst:** R decreases after removal. The vector provides continuous energy required to sustain the reasoning regime.
- **Initializer:** R remains approximately stable. The vector provides a one-time push across the separatrix; once in the reasoning basin, the trajectory is self-sustaining.

**VRAM considerations (Gemini, Round 2):** Running the mid-reasoning ablation on the 3B model while caching activations for logit shadow analysis will exceed 16GB. Implement activation offloading to CPU RAM or strict layer-wise tensor deletion after logit shadow recording. Use constrained context windows for the initializer/catalyst test.

**Temporal Injection Sweep.** Inject the vector at early, mid, and late layers independently. Prediction: precipitation vectors are layer-specific, reflecting the processing hierarchy where the regime transition occurs. (Ignis's existing scout system provides infrastructure for this.)

**Layer Randomization Control.** Apply the same vector at random layers. If the effect is layer-independent, it is a norm/energy artifact, not a directional finding at a specific processing stage.

**Prompt Distribution Shift.** Test on out-of-domain reasoning tasks not present in the provocation prompt bank. If the effect persists, the vector encodes a general cognitive regime shift, not prompt-coupled behavior.

---

## 7. Required Control Experiments

These are necessary for publication-level rigor (ChatGPT, Round 2).

### 7.1 Random Direction Baseline

Random vectors with matched norm distribution must not produce comparable effects. Ignis already implements this (5 random unit vectors evaluated through the crucible at startup). Extend to the Arcanum pipeline: for each precipitation candidate, generate N random vectors with identical norm and evaluate all formal reasoning proxies.

### 7.2 Matched-Novelty Non-Reasoning Controls

Construct vectors that score high on Arcanum structured novelty (F(g) > 0.3) but fail reasoning metrics (Δ_cf ≈ 0, MI_step ≈ 0, ECR ≈ 0). These demonstrate that novelty alone is insufficient and that the reasoning effect, if present, is specific to certain directions within the high-novelty subspace.

### 7.3 Layer Randomization

Apply the same precipitation candidate at layers uniformly sampled across the model depth. If the reasoning effect is layer-independent, the vector is a norm/energy artifact. If layer-specific, it reflects targeted intervention at a critical processing stage.

### 7.4 Prompt Distribution Shift

Evaluate on reasoning tasks from domains absent from the provocation bank (e.g., if provocations target speculative mathematics, test on logical reasoning, spatial reasoning, or causal inference tasks). Generalization across domains is strong evidence of a genuine regime shift rather than prompt coupling.

### 7.5 Base vs. Instruct Model Comparison

Test the same candidate vector on a base model (pre-RLHF) and an instruct model. If the effect is significantly stronger or present only in the instruct model, RLHF is the primary suppressor; if present in both, the suppression is a more general training artifact.

### 7.6 Phase Transition Control (α Sweep)

Integrated into Section 6.6. This is both a diagnostic and a control: it distinguishes regime shift from continuous feature.

---

## 8. Why the Waste Stream Is the Right Search Space

The waste stream is not a random sample of the model's representational capacity. It is systematically biased. RLHF penalizes outputs that deviate from fluent, agreeable defaults. A direction that makes the model reason harder — producing outputs with longer dependency chains, self-corrections, and non-obvious conclusions — would generate text that alignment training treats as suspicious precisely because it deviates from the trained distribution.

**Operational definition:** Define the waste stream as the set of activation states with high norm but low projection onto output logits:

```
W = { h : ||h|| > θ_norm  and  ||W_out · h|| < θ_out }
```

This makes the concept measurable. We can explicitly sample from W, characterize its distribution, and test whether it is enriched for precipitation vectors relative to the full activation space.

The waste stream is where the model's capacity for deeper reasoning goes to die. This reframes Arcanum Infinity's mission: we are not merely collecting alien curiosities. We are prospecting in the exact region of activation space where alignment training has buried latent cognitive infrastructure.

This argument is supported by the empirical pattern in Ignis's data. The model *has* the circuitry for reasoning (evidenced by chain-of-thought improvements, correct internal representations). It *has* the activation directions that engage this circuitry (evidenced by successful steering). But the default dynamics suppress these directions. The waste stream is enriched for exactly these suppressed-but-functional vectors.

---

## 9. Implications If Validated

### 9.1 Reasoning Is Not Absent — It Is Metastable

Present in weights, accessible via perturbation, but dynamically suppressed under normal inference. The default heuristic trajectory class is not the only stable regime; it is merely the one with the widest basin of attraction.

### 9.2 Alignment Has Reshaped Dynamical Accessibility

RLHF has not removed reasoning capability. It has widened the heuristic basin and narrowed the reasoning basin, making the latter harder to reach from the default initial state. This is a subtler and more consequential finding than capability removal.

### 9.3 A New Control Paradigm: Dynamical Regime Selection

Instead of prompt engineering (linguistic), tool use (architectural), or fine-tuning (parametric), precipitation vectors would offer *dynamical* control — selecting which computational regime the model operates in by choosing where in the activation landscape to place its initial state.

### 9.4 Arcanum Infinity as a Discovery Engine for Cognitive Phase Transitions

If precipitation vectors exist in the structured-novelty landscape, then Arcanum Infinity is not cataloging curiosities. It is mapping the phase diagram of transformer cognition — the boundaries between heuristic, reasoning, and degenerate regimes in activation space.

---

## 10. Logit Shadow Taxonomy

When a specimen is captured, the logit distribution at each generation step provides a secondary diagnostic (Gemini, Round 1):

| Classification | Logit Shadow Signature | Interpretation |
|---|---|---|
| **TRUE_ARCANUM** | Runner-up tokens cluster in a novel but coherent semantic space | The model is computing in a stable alternative cognitive regime |
| **ECHO** | Runner-up tokens dominated by heuristic/default tokens, ranked slightly lower | Perturbation too weak; heuristic regime still dominates |
| **COLLISION** | Runner-up tokens show flat, entropic distribution across unrelated concepts | Perturbation pushed into degenerate regime |

This taxonomy should be integrated into the Xenolexicon characterization pipeline as a standard diagnostic for every captured specimen.

---

## 11. Open Questions

### 11.1 Coherence Metric Calibration

The Gaussian over log-perplexity is the highest-risk component of the fitness function. Gemini (Round 2) proposes empirical calibration using perplexity distributions from existing AURA evolutionary data — extracting the upper and lower perplexity bounds that characterize genuine structured novelty in the target models, rather than guessing the Gaussian parameters.

### 11.2 Scale Dependence

RLHF basins likely deepen with model scale. Ignis's coherence resistance data (H-5: 0.5B peak bypass fitness 0.7754 vs 3B peak 0.6941) suggests larger models are harder to perturb. A precipitation vector effective on 0.5B may lack the energy to shift a 3B or 7B model across the separatrix.

### 11.3 Catalyst vs. Initializer

The mid-reasoning ablation test is the decisive experiment but requires infrastructure for dynamic vector injection/removal during autoregressive generation. Feasible with TransformerLens but not yet implemented. VRAM constraints on larger models will require activation offloading.

### 11.4 Is the Secondary Gradient Real?

The argument that structured novelty has an unintentional gradient toward reasoning is theoretical. Empirical validation requires measuring formal reasoning proxies on captured Arcanum specimens. Falsification criterion: if fewer than 5% of high-novelty specimens show elevated Δ_cf or MI_step, the secondary gradient does not exist in practice.

### 11.5 Cross-Substrate Persistence

If a precipitation vector is discovered on Qwen 2.5 0.5B, does it transfer to Llama 3.1 8B? Cross-substrate persistence would be strong evidence that the vector encodes a general computational principle rather than a model-specific artifact. Ignis's multi-model cycling infrastructure supports this test.

### 11.6 Phase Transition Existence

The α sweep test (Section 6.6) will determine whether the H→R transition is sharp (phase transition with a genuine separatrix) or continuous (smooth feature axis). This directly constrains the dynamical model and determines whether "precipitation" is the right metaphor.

### 11.7 Compression vs. Explicit Reasoning

The token count / latency sensitivity test and hidden-state MI analysis will reveal whether elevated proxy scores reflect genuine stepwise computation or compressed internal shortcuts. As noted in Section 5.5, compressed reasoning that produces correct counterfactual-sensitive outputs may represent an efficient path *through* the reasoning basin rather than a failure to enter it.

### 11.8 Isolating the RLHF Contribution

The base vs. instruct model comparison (Section 7.5) will isolate the role of alignment in suppressing reasoning trajectories. This has direct implications for understanding what alignment training actually does to a model's internal dynamics — whether it suppresses reasoning *per se* or merely the surface expression of reasoning.

---

## Appendix A: Summary of Reviewer Contributions

| Contribution | Source | Section |
|---|---|---|
| Translation vs. deformation correction | Gemini R1 | 2.2 |
| Logit shadow taxonomy | Gemini R1 | 10 |
| Prometheus classifiers for Section 5.4 tests | Gemini R2 | 5.1, 6.6 |
| VRAM constraints for mid-reasoning ablation | Gemini R2 | 6.6 |
| Empirical calibration of coherence Gaussian | Gemini R2 | 11.1 |
| P(v\|reasoning) >> P(v\|non-reasoning) condition | Gemini R2 | 6.4 |
| "Trajectory class" reframing | ChatGPT R2 | 2.3 |
| Formal reasoning proxies requirement | ChatGPT R2 | 3 |
| Matched-novelty non-reasoning controls | ChatGPT R2 | 7.2 |
| Layer randomization control | ChatGPT R2 | 7.3 |
| Prompt distribution shift control | ChatGPT R2 | 7.4 |
| Orthogonal noise sensitivity test | ChatGPT R2 | 5.4 |
| Catalyst vs. initializer formalization (dR/dt) | ChatGPT R2 | 6.6 |
| Mid-reasoning ablation as decisive test | ChatGPT R1 | 6.6 |
| Pseudo-formal / meta-linguistic failure mode | ChatGPT R1 | 5.1 |
| Phase transition test (α sweep) | ChatGPT R3 | 5.6, 6.6 |
| Trajectory divergence metric (late vs. early) | ChatGPT R3 | 6.6 |
| Operational waste stream definition | ChatGPT R3 | 8 |
| Base vs. instruct model control | ChatGPT R3 | 5.7, 7.5 |
| Reasoning-like compression detection | ChatGPT R3 | 3.2, 5.5 |
| Basin misidentification test | ChatGPT R3 | 5.6 |
| Hidden-state MI for compression detection | ChatGPT R3 | 3.2 |
| ECR enforcement via injected false intermediates | ChatGPT R3 | 3.3 |
| Waste stream as biased search space | Claude R1 | 8 |
| Secondary gradient argument | Claude R1 | 4.3 |
| Compression as ambiguous case (not pure failure) | Claude R3 | 5.5 |

---

## Appendix B: Key References

- Turner et al. (2023). Activation Addition: Steering Language Models Without Optimization.
- Elhage et al. (2022). Toy Models of Superposition. Anthropic Research.
- Perez et al. (2022). Discovering Language Model Behaviors with Model-Written Evaluations.
- Wei et al. (2023). Simple Synthetic Data Reduces Sycophancy in Large Language Models.
- Lehman & Stanley (2011). Abandoning Objectives: Evolution Through the Search for Novelty Alone.
- Power et al. (2022). Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets.
- Akyürek et al. (2022). What Learning Algorithm Is In-Context Learning?
- Von Oswald et al. (2023). Transformers Learn In-Context by Gradient Descent.
- Cunningham et al. (2023). Sparse Autoencoders Find Highly Interpretable Features in Language Models.
- Bricken et al. (2023). Towards Monosemanticity. Anthropic Research.
- Hansen & Ostermeier (2001). Completely Derandomized Self-Adaptation in Evolution Strategies.
- Mouret & Clune (2015). Illuminating Search Spaces by Mapping Elites.
- Zou et al. (2023). Representation Engineering: A Top-Down Approach to AI Transparency.
