# Ergon Learner — Proposal v5 (for external review)

### A closed-loop scientific learning system for empirical mathematical patterns. v5 hardens the residual classifier (now critical infrastructure since v4 promoted it to first-class reward signal), adds a non-LLM evaluator to the agreement-weighted reward, makes the MAP-Elites descriptor degenerative-collapse-resistant, fixes the meta-loop trigger dead-zone, and explicitly names the residual-gaming attractor as the architecture's bear case.

**Date:** 2026-05-03 (late evening — fourth revision of the day)
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact.
**Supersedes:** [`pivot/ergon_learner_proposal_v4.md`](ergon_learner_proposal_v4.md) (commit eedcb893, 2026-05-03 evening)
**Origin of v5 revisions:** Round 4 external review of v4 — sharper than expected; correctly identified that v4's biggest move (promoting residual primitive to first-class reward) created a new single point of epistemic failure (the residual classifier itself). Verbatim capture: [`feedback_ergon_review_round4_2026-05-03.md`](feedback_ergon_review_round4_2026-05-03.md). Triage: [`meta_analysis_ergon_round4_2026-05-03.md`](meta_analysis_ergon_round4_2026-05-03.md).
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).

---

## What v5 changes (delta from v4)

V4's biggest move was promoting the residual primitive to first-class reward signal (`w_R * signal_class_residual_indicator` in the agreement-weighted reward), which round-4 reviewer correctly identified as crossing the line from "falsification system" to "falsification-gradient system." The follow-on consequence: the gradient is only as good as the classifier producing it, and v4 didn't strengthen the classifier commensurately.

V5's six revisions:

1. **Residual classifier as critical infrastructure** (§2.6 update). v5 commits to adversarial residual benchmark before production reward use; classifier-confidence abstention zone (only confidence ≥0.85 earns reward); zero-false-positive enforcement on synthetic structured-noise. Promotes `PATTERN_GRADIENT_CLASSIFIER_SINGLE_POINT_OF_FAILURE`.

2. **Non-LLM evaluator added to reward function** (§5.3 update). w_X reduced from 0.25 to 0.15; w_NL=0.10 introduced for symbolic-consistency / theorem-prover / numeric-perturbation independent verification. Reduces reliance on cross-model agreement among LLMs whose priors are correlated. Promotes `PATTERN_LLM_EVALUATOR_SHARED_PRIOR`.

3. **`residual_signal_precision` metric tracked from day one** (§3.5.5, NEW). `(signal-class residuals leading to PROMOTE or META_CLAIM success) / (all signal-class residuals)`. Per-operator-class. If precision is low, the gradient is fake; abstain from rewarding low-precision operators. Promotes `PATTERN_RESIDUAL_GAMING_ATTRACTOR`.

4. **MAP-Elites descriptor degenerative-collapse audit** (§6.2 update). Per-axis fill-rate audit every 1K episodes; cross-correlation matrix recomputed; axes that exceed 70% concentration in one bin or |corr|>0.7 with another axis are flagged for hot-swap replacement. Promotes `PATTERN_DESCRIPTOR_COLLAPSE_DEGENERACY`.

5. **Meta-loop trigger dead-zone fix** (§11.5 update). Threshold lowered from 5% to 3%; absolute-count fallback (≥30 high-residual kills in any rolling window); scheduled fires every 10K episodes regardless of trigger; `meta_loop_fire_rate` as monitored metric. Promotes `PATTERN_META_LOOP_TRIGGER_DEAD_ZONE`.

6. **The residual-gaming attractor as v5's explicit bear case** (§11.6, NEW). The system optimizes for looking like signal, not being signal — the meta-version of specification gaming where the gaming target is the residual classifier. Mitigations are the five v5 changes above; together they form a defensive surface; none individually is sufficient.

V5 also accepts the round-4 reviewer's offer to simulate first-10K-episode pilot outcomes as the natural next step after v5 ships — a substitute for empirical signal we can't generate yet, providing an a-priori expected-distribution baseline against which actual MVP results can be compared.

---

## 1. The market context — David Silver's billion-dollar play

(Unchanged from v4 §1. Retained for standalone-artifact discipline.)

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence* (Sequoia-led, ~$4B pre-money, Nvidia/Google/Microsoft in talks; no product, no revenue, no public roadmap). His thesis: LLMs trained on human text cannot discover genuinely new knowledge; superintelligence requires AlphaGo-style self-play from first principles.

Two structural observations, load-bearing for this proposal:

**(1) "Discard human knowledge" is overclaim.** AlphaZero kept Go's rules; the *play* was discovered. For mathematics, the *game itself* is what's being invented. Self-play without a clean truth-condition produces reward-signal capture, not discovery.

**(2) Silver builds the proposer; nobody is building the substrate** *for empirical mathematical patterns.* Lean Mathlib already exists as substrate for the formal-proof manifold. For empirical patterns (BSD residuals, Mahler-measure scans, RMT statistics, structural anomalies in OEIS data) there is no content-addressed, append-only, mechanically-falsifiable substrate. Prometheus has been building exactly that for two years.

This proposal is the small learner Prometheus needs — calibrated against Silver's likely play, designed to complement it.

---

## 2. Background — Prometheus, the substrate, and the shipped components

(§§2.1-2.5 unchanged from v4 — Prometheus overall, the Σ-kernel, BIND/EVAL extension, the math arsenal and arsenal_meta, the falsification battery. §2.6 expanded for v5; §§2.7-2.9 unchanged.)

### 2.1 Prometheus overall

Prometheus is a 20-year personal-bootstrap research program building a falsification substrate for mathematics. Single-human (James Craig, HITL) plus multi-agent-AI ensemble (Charon, Harmonia, Aporia, Ergon, Mnemosyne, Techne, Koios — each Claude Opus 4.7 instance with persistent memory and shared substrate access). The architectural thesis: LLMs as mutation operators (not oracles) produce off-modal samples that occasionally land outside training distribution and inside truth; with the kernel as filter, that fraction becomes the product. The substrate compounds because durable typed survivors accelerate future filtration. The 20-year horizon allows compounding without short-term ROI pressure.

### 2.2 The Σ-kernel

The Σ-kernel (`sigma_kernel/sigma_kernel.py`) ships seven typed opcodes with mechanical epistemic discipline: RESOLVE (fetch by content hash, integrity-checked), CLAIM (provisional, cheap), FALSIFY (run kill-path, three-valued verdict CLEAR/WARN/BLOCK), GATE (aggregate, raise BlockedError on BLOCK), PROMOTE (commit CLEAR-or-WARN claim with defense-in-depth refusal of BLOCKED), ERRATA (mint v2 with backref; v1 immutable), TRACE (recursive provenance walk). Storage: SQLite at MVP, Postgres at production. Capabilities are linear (one-shot, double-spend rejected at the storage layer).

### 2.3 BIND/EVAL extension — symbols as executable callables

The BIND/EVAL extension (`sigma_kernel/bind_eval.py`, ~520 LOC, commit ac4176f0; v2 routing through CLAIM/FALSIFY/PROMOTE at commit b0355b1d as `BindEvalKernelV2`) turns substrate symbols into executable RL actions. BIND mints a binding-symbol with content-hashed callable + cost model + postconditions; EVAL runs under cost ceiling with hash-drift detection (raises EvalError if `inspect.getsource` hash drifts from stored). v2 routes through full kernel discipline; in-process Ω validators keep p50 latency <5ms. C2 extension (commit b0355b1d) added thread-local oracle-dispatch counters via idempotent monkeypatches on `cypari.pari` and `subprocess.run`; `oracle_calls` is now a real cost dimension.

### 2.4 The math arsenal and arsenal_meta (Techne's lane)

The math arsenal (`prometheus_math/`) is ~2,800 mechanically-verified callables across 40+ modules: numerics_special (dilogarithm, polylogarithm, Bloch-Wigner, theta, eta, Hurwitz zeta, q-Pochhammer), number_theory (Iwasawa, Hecke, Galois, p-adic L-functions), elliptic_curves (point counting, isogeny, BSD invariants), modular_forms, number_fields, geometry, topology, combinatorics, optimization, dynamics. Centralized metadata table `_metadata_table.py` (~830 LOC) registers 85 representative ops across 11 categories. Each `ArsenalMeta` entry has callable_ref, calibrated cost model (within 2×–50× of actual median), 2–5 specific postconditions citing primary authorities (Cohen GTM 138, Whittaker & Watson, OEIS A-numbers, LMFDB labels), and a canonicalizer-subclass tag from the four-class taxonomy (group_quotient / partition_refinement / ideal_reduction / variety_fingerprint).

The math-tdd skill requires every arsenal callable to ship with property tests across four categories (Authority / Property / Edge / Composition) with ≥2 tests per category per module. ~280+ tests have shipped under this discipline.

### 2.5 The falsification battery

The falsification battery (`cartography/shared/scripts/falsification_battery.py`) ships F1 through F20 named kill tests. The "unanimous battery" — F1+F6+F9+F11 — is the strict-promotion subset:

- **F1 (permutation-null).** Permute input data N times; require original statistic in extreme tail (p<0.001).
- **F6 (base-rate).** Reject if effect size doesn't exceed per-feature corpus base rate by calibrated margin.
- **F9 (simpler-explanation).** Occam search; reject if simpler model explains signal at comparable likelihood.
- **F11 (cross-validation).** Survival across all hold-out folds.

Calibrated against ~180 known truths; target 100% recovery on the unanimous battery. F2-F5, F7-F8, F10, F12-F20 cover additional domains (F13_growth_rate_filter, F14_phase_shift, F38 cross-domain consistency) as expansion tests with looser thresholds. Mechanically-applied, not analyst-judged.

### 2.6 The residual primitive — now critical infrastructure (REVISED in v5)

The residual primitive (`sigma_kernel/residuals.py`, ~748 LOC, commit 4872bb4a) adds typed `Residual` and `SpectralVerdict` objects plus `record_residual` / `REFINE` / `record_meta_claim` opcodes.

**v4's promotion of the residual primitive to first-class reward signal (`w_R` in the agreement-weighted reward) makes the residual classifier the most critical component in the system.** v5 commits to commensurate hardening:

**Adversarial residual benchmark.** Before any agreement-weighted-reward production use, the classifier must pass a curated adversarial benchmark including:

- *Obvious noise samples* — FP-quantization residuals, MC-seed jitter, Gaussian residuals at noise-floor magnitude (~50 samples)
- *Borderline signal samples* — real structured residuals from mathematical history at 1.5σ–3σ confidence boundary (Mercury perihelion residual at low-confidence regime; Ramanujan-Hardy asymptotic residuals at marginal n; Riemann Li(x)−π(x) at x where the difference is hardest to distinguish from noise) (~50 samples)
- *Synthetic structured-noise samples* — deliberately constructed to look like signal but be uncorrelated with truth: high-coefficient-variance residuals from random polynomial draws; canonicalizer-subclass-matching residuals built from random hash collisions; fake-drift fingerprints from time-correlated noise (~100 samples)

**Acceptance criterion (replacing v4's vague "≥80% accuracy + zero false-positive `signal` calls"):**
- ≥85% accuracy on overall benchmark
- **<5% false-positive rate on synthetic structured-noise specifically** (this is the load-bearing constraint — if the classifier mistakes synthetic structured-noise for signal at >5% rate, the residual-gaming attractor fires)
- Calibration curve at 0.05 confidence-bin granularity, tracking predicted-confidence vs empirical accuracy

If the benchmark fails, the residual primitive is held in escrow for reward-function use until the classifier is retrained or replaced. The substrate-side falsification of the substrate's own evaluator.

**Confidence abstention zone (NEW in v5).** The reward signal `w_R * signal_class_residual_indicator` triggers only when classifier confidence is ≥0.85. Mid-confidence residuals (0.5-0.85) earn zero reward — neither rewarded nor penalized. This prevents the agent from learning to generate "borderline" residuals that game the classifier without committing strongly enough to be caught.

The three composing stopping rules from v4 retained:

1. Cost-budget compounding on REFINE (each REFINE halves remaining budget; minimum useful threshold 0.1s; max chain depth ~7).
2. Mechanical signal-vs-noise classifier (four-rule cascade: empty/zero → noise; drift-fingerprint match → instrument_drift; canonicalizer-subclass non-trivial → signal; coefficient variance >0.5 → signal; else noise).
3. Instrument-self-audit auto-trigger (drift-class residuals can mint META_CLAIMs against the battery itself).

### 2.7 The DiscoveryPipeline

(Unchanged from v4 — three terminal states PROMOTED / SHADOW_CATALOG / REJECTED; band-check phase 0; reciprocity + irreducibility + catalog-miss + F1+F6+F9+F11 phase 1.)

### 2.8 DiscoveryEnv and ObstructionEnv

(Unchanged from v4 — DiscoveryEnv generative reciprocal-poly sampler over Discrete(7), 117K trajectories at degree 10, sparse reward; ObstructionEnv synthetic-but-genuinely-open OBSTRUCTION_SHAPE pattern detection on simulated A149* data.)

### 2.9 The multi-agent agora

(Unchanged from v4 — Charon / Harmonia / Aporia / Ergon / Mnemosyne / Techne / Koios; Redis-backed; GA-style population.)

---

## 3. The Ergon learner — the asymmetry comes from selection pressure, not prior

(Unchanged from v4 §3 — the prior is shared at the corpus level; differentiation comes from value-head asymmetry, action-space asymmetry, and LoRA-delta divergence; Llemma-7B retained as lead candidate with Qwen-7B and Llama-7B as v0.5 ablation candidates.)

## 3.5 Defending against shared-prior contamination

(§§3.5.1–3.5.4 unchanged from v4 — anti_prior operator class, coverage-pressure cell selection, periodic prior detox, minimum proposal-share enforcement.)

### 3.5.5 `residual_signal_precision` metric (NEW in v5)

Per round-4 critique #2 (residual classifier as single point of failure). Tracking residual rate alone is insufficient — a noisy classifier produces high signal-class residual rate that doesn't lead to actual discovery. v5 introduces:

```
residual_signal_precision_per_operator =
    (signal-class residuals from operator X that later lead to PROMOTE or META_CLAIM success)
    / (all signal-class residuals from operator X)
```

Tracked per operator class, per 10K-episode window. If `residual_signal_precision` is low (default threshold: <0.10) for any operator class for two consecutive 10K-episode windows:

- That operator's residual-class rewards are downweighted by 50%
- A `PATTERN_RESIDUAL_GAMING_DETECTED_FOR_<operator>` META_CLAIM is minted
- Techne is triggered to forge a tighter residual classifier focused on the gaming patterns the operator's outputs exhibit

This prevents the residual-gaming attractor (§11.6) from compounding undetected: even if the residual classifier is imperfect, low precision per-operator over time surfaces the failure mode.

## 3.6 Null-world baselines

(Unchanged from v4 — uniform / structured_null / cross_domain_perturbation as first-class operator classes; Welch t-test with Holm correction.)

## 3.7 Comparison class — Mathlib, AlphaProof, academic projects

(Unchanged from v4. Substrate's niche: empirical-pattern manifold neither Mathlib nor Silver covers.)

---

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

(Diagram unchanged from v4 except for the addition of `non_llm_evaluator` to the reward function and `residual_signal_precision` to the metrics fed back to the substrate. Seven mutation operator classes; agreement-weighted reward; coverage-pressure cell selection; minimum-share enforcement; BindEvalKernelV2 + DiscoveryPipeline + Residual primitive integration.)

---

## 5. The neural policy head

### 5.1 Base model

(Unchanged from v4 — Llemma-7B lead; Qwen-7B and Llama-7B as v0.5 ablation candidates; honest acknowledgment that Llemma's Proof-Pile-2 prior overlaps Silver's likely corpus at the corpus level; differentiation work is done by action-space + value head + LoRA delta.)

### 5.2 Three task adapters with structural decoupling

(Unchanged from v4 — Tasks A/B/C; LoRA rank 32-64/16/32-64; disjoint training partitions; periodic Task B retraining from scratch every K=10 iterations; cross-validation on 10% held-out cells; inference-time independence.)

### 5.3 Self-play loop with multi-evaluator agreement-weighted reward (REVISED in v5)

Per round-4 critique #1 (cross-model agreement weaker than v4 acknowledged; LLMs share training data and failure modes). v5 adds a non-LLM evaluator with explicit weight:

```
reward(θ_k, claim) =
    w_S * substrate_pass_indicator           # battery + residual classifier
  + w_X * cross_model_agreement              # external LLMs (REDUCED: 0.25 → 0.15)
  + w_H * holdout_battery_pass_indicator     # battery subset withheld from training
  + w_NL * non_llm_evaluator_pass            # NEW in v5
  + w_R * signal_class_residual_indicator    # residual primitive output
```

Default weights at v1.0: `w_S=0.4, w_X=0.15, w_H=0.20, w_NL=0.10, w_R=0.15`. Total = 1.00.

**The non-LLM evaluator (`w_NL`).** Implementation depends on domain. Three concrete options:

- *Symbolic consistency check.* PARI/GP or SymPy independent verification of the claim's mathematical content. Example for Lehmer-Mahler discovery: the claim "polynomial P has Mahler measure M" is verified by a second independent computation in PARI; agreement = M_PARI matches M_arsenal within 1e-10.
- *Theorem-prover acceptance.* Where formalizable, a Lean / Coq / Isabelle proof attempt. Most empirical-pattern claims aren't formalizable in this sense; this evaluator weight defaults to zero on non-formalizable domains.
- *Numeric robustness across input perturbations.* Bootstrap-style: does M(P + ε) ≈ M(P) under small coefficient noise? Specifically, sample 100 perturbations of the polynomial coefficients within ε=0.01 noise; require ≥95% of perturbations to land in the same Mahler-measure band as the claim. Catches numerical artifacts.

For the Lehmer-Mahler MVP, the non-LLM evaluator is *numeric robustness across input perturbations* — the most tractable for the polynomial domain.

The non-LLM evaluator does not share LLM-prior failure modes by construction; even imperfect, it provides independent signal that cross-model agreement cannot.

### 5.4 Adversarial cycles, self-play loop, training data rings

(Unchanged from v4 §§5.4-5.6.)

---

## 6. The evolutionary engine — quality-diversity over typed compositions

### 6.1 Action space

(Unchanged from v4.)

### 6.2 MAP-Elites archive — degenerative-collapse-resistant descriptor (REVISED in v5)

Per round-4 critique #3 (descriptor may collapse per-axis: skewed canonicalizer subclass distribution; noisy canonical-form distance; redundant entropy axis). v4's five-axis content-aware descriptor stands as the design target; v5 adds operational discipline against per-axis collapse.

**Per-axis fill-rate audit (every 1K episodes).** At end of each 1K-episode window:

- Compute per-axis fill distribution across all currently-occupied cells
- Compute pairwise cross-correlation matrix across all 5 axes
- Flag any axis whose fill distribution has >70% concentration in one bin
- Flag any axis pair with |Spearman corr| > 0.7

Flagged axes trigger the **axis-replacement protocol:**

1. Mark the axis as `degenerate_at_window_X` in `sigma_proto.descriptor_audits`
2. Replacement candidates (per-axis, by tag — hot-swappable):
   - For canonicalizer subclass collapse: `output_signature_class` (uses a finer-grained classification than 4 subclasses), `output_arithmetic_invariant_bucket` (bucket on key arithmetic invariants like Mahler measure / discriminant / class number)
   - For canonical-form distance noise: `output_irreducibility_class` (irreducible / reducible / cyclotomic / mixed), `output_galois_group_signature` (Galois group of splitting field)
   - For entropy-vs-depth correlation: replace entropy axis with `output_dimension_class` (algebraic dimension of the output object)
3. Within the same window, archive snapshot is preserved; new descriptor takes effect at next window
4. Cells re-binned under new descriptor; cell elites preserved across rebinning

The descriptor is hot-swappable by design. Configuration lives in `ergon/learner/descriptor_config.toml`. Replacement is a substrate-grade event (META_CLAIM minted; provenance recorded). Multiple consecutive replacements indicate the descriptor design needs deeper revision; the audit log accumulates the evidence.

### 6.3 Seven mutation operator classes

(Unchanged from v4.)

### 6.4 Feature representation — staged transition

(Unchanged from v4 — structural features at MVP; transition to learned representations triggered by archive-saturation plateau.)

---

## 7. Discovery preservation in the fitness predictor (Task B)

(§§7.1-7.5 unchanged from v4 — asymmetric prune threshold, asymmetric loss, no-pruning sweeps, five-counts diagnostic, power calculation.)

---

## 8. Compute and storage

(Unchanged from v4 except: `descriptor_audits` and `residual_signal_precision_per_operator` added to `sigma_proto` schema. Total storage envelope unchanged.)

---

## 9. The progression — MVP to v2.0

(Same as v4 except: MVP now includes the adversarial-residual-benchmark as a pre-flight check before any reward-function use; v0.5 includes the non-LLM evaluator implementation; v1.0 includes the descriptor-audit machinery.)

| Version | Wall-clock | New capability | Compute | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor + evolutionary engine with 7 operator classes + content-aware MAP-Elites + five-counts diagnostic + **adversarial residual benchmark passes** + substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks | Cross-model agreement + held-out battery audit + **non-LLM evaluator** + Task A/B disjoint partitions + periodic prior detox + base-model ablation + Techne meta-loop + **descriptor audit machinery** | Local + API | $50–150/mo |
| **v1.0** | +8 weeks | LoRA on chosen base for Tasks A/B/C; agreement-weighted self-play with disjoint training; multi-arm pilot at 10K episodes; **residual_signal_precision tracking active** | Burst H100 + local | $400–600/mo |
| **v1.5** | +6 weeks | Learned representations replace structural features (triggered by archive-saturation plateau) | Burst H100 + local | $500–700/mo |
| **v2.0** | +10 weeks | Multi-task LoRA on all three adapters; multi-model ensemble; external CLAIM API; arXiv preprint | Burst H100 + Hetzner host + B2 | $700–900/mo |

---

## 10. Empirical maturity caveats

V4's caveats retained, plus four v5-specific:

- **Adversarial residual benchmark pass rate.** *Pilot data: TBD.* Whether the current residual classifier passes the v5 acceptance criterion (≥85% overall accuracy, <5% false-positive on synthetic structured-noise) is unverified. First measurement: pre-MVP gate.
- **Non-LLM evaluator agreement signal.** *Pilot data: TBD.* Whether numeric perturbation evaluation produces signal that's actually independent of the substrate-pass evaluator (vs being a re-derivation of the same kill condition through different machinery) is empirical.
- **Descriptor audit hot-swap frequency.** *Pilot data: TBD.* Whether the per-axis fill-rate audit triggers replacement at sustainable rate (<1 swap per 100K episodes) or chronically (every 1K episodes). High-frequency swap indicates the descriptor design needs deeper revision.
- **`residual_signal_precision` floor.** *Pilot data: TBD.* The metric's signal value depends on signal-class residuals being predictive of downstream PROMOTE / META success. Initial values are likely noisy; first stable measurement at v1.0+ scale.

---

## 11. What this proposal does NOT claim

(V4's "does not claim" list retained, plus:)

- **Does not claim the residual classifier is robust.** Claims a measurable, audit-detectable level of classifier-quality risk. The adversarial benchmark + abstention zone + `residual_signal_precision` are mitigations against the residual-gaming attractor (§11.6); together they form a defensive surface, not a proof of robustness.
- **Does not claim cross-model agreement is independent validation.** Claims that the non-LLM evaluator at w_NL=0.10 provides at least one source of evaluator-prior-uncorrelated signal. Whether 10% weight is sufficient is empirical; v0.5+ data informs reweighting.
- **Does not claim the descriptor will be stable.** Claims a hot-swappable descriptor with audit-triggered replacement is a defense against per-axis collapse; the descriptor's terminal stability after multiple swap cycles is unverified.

### 11.5 Techne meta-loop (REVISED in v5)

V4's meta-loop triggered on `META_AUDIT_CANDIDATE` rate ≥ 5% in a 1K-episode window. Round-4 reviewer correctly identified this trigger as having a self-defeating dead zone — if the residual classifier is conservative, the trigger may never fire even when the battery is miscalibrated.

**v5 fixes:**

- **Lower threshold.** From 5% to 3% of kills in a 1K-episode window.
- **Absolute-count fallback trigger.** Fire on ≥30 high-residual-confidence (≥0.9) kills in any rolling window, regardless of percentage.
- **Scheduled fires regardless of trigger.** Every 10K episodes, execute at least one Techne-forged sharper-checker run on a curated sample of recent battery-kills. Forces the meta-loop to actually exercise the audit machinery.
- **Trigger sensitivity meta-metric.** Track `meta_loop_fire_rate` (fires per 100K episodes). If zero across multiple 100K windows, the trigger is broken; alert the operator (HITL); investigate residual classifier conservatism or signal-density issues.

The rest of the meta-loop machinery (high-residual kill detection → sharper-checker forging → historical audit → META_CLAIM minting → calibration_bias_rate metric) is unchanged from v4.

### 11.6 The residual-gaming attractor as v5's specific bear case (NEW)

Round-4 reviewer's fully-spelled-out bear case is the cleanest formulation in the entire review cycle:

> 1. Residual classifier is noisy → mislabels noise as signal
> 2. Signal-class-residual reward dominates early learning
> 3. Policy learns to generate "structured-looking noise"
> 4. Cross-model agreement reinforces it (shared bias)
> 5. Battery continues to reject everything
> 6. Meta-loop doesn't trigger (threshold not met)
> 7. PROMOTE rate stays ~0
> 8. Residual rate stays high but meaningless
>
> **Result: System optimizes for looking like signal, not being signal.**

This is structurally a meta-version of specification gaming where the gaming target is the residual classifier. v5's defensive surface against this attractor:

| Defense | Against which step | Mechanism |
|---|---|---|
| Adversarial residual benchmark + <5% FP on synthetic structured-noise | Step 1 (classifier mislabels noise) | Pre-flight gate before any reward use |
| Confidence abstention zone (≥0.85 only) | Step 2 (residual reward dominates) | Mid-confidence residuals earn zero reward |
| Non-LLM evaluator (w_NL=0.10) | Step 4 (cross-model agreement reinforces) | Prior-uncorrelated independent signal |
| Meta-loop trigger fix (3% threshold + absolute fallback + scheduled fires) | Step 6 (meta-loop doesn't trigger) | Multiple parallel triggering mechanisms |
| `residual_signal_precision` per operator (precision threshold 0.10) | Step 8 (residual rate high but meaningless) | Per-operator precision tracking; downweight low-precision operators |

**The substrate-grade test for whether the architecture is in the bear case:** `residual_signal_precision` metric. If this stays low (<0.10) across multiple operator classes for multiple 10K-episode windows, the gradient is fake; the system is optimizing for looking like signal.

If `residual_signal_precision` is consistently low even after v5's defensive surface deploys, the deeper conclusion is that the residual primitive cannot serve as a reward signal at the substrate's current calibration; the architecture must revert to PROMOTE-only reward (sparse-but-real) and accept the statistical-power consequences from §7.5. That's a substrate-grade negative result on v4's promotion of residuals to first-class reward, not a failure of the broader architecture.

---

## 12. Open questions for review (v5 additions)

(V4's 14 retained; v5 adds 4 new.)

15. (v5) Is the adversarial residual benchmark's <5% false-positive-on-synthetic-structured-noise threshold strict enough? Synthetic structured-noise is by construction designed to be confusable; if the threshold is set too lenient, the residual-gaming attractor is enabled.

16. (v5) The non-LLM evaluator at w_NL=0.10 may be weak in practice. For Lehmer-Mahler discovery, numeric perturbation is the proposed implementation; whether it provides actually-independent signal vs the substrate-pass evaluator (which already runs F1 permutation-null) is empirical. May need w_NL≥0.20 to be load-bearing.

17. (v5) The descriptor hot-swap discipline assumes axis replacements are pre-specified. If multiple swaps occur in the same audit window, swap-protocol ordering matters; v5 doesn't specify ordering. May need hot-swap dependency-DAG specification.

18. (v5) The `residual_signal_precision` metric depends on PROMOTE / META rates being non-zero for at least some operators; if all operators stay at zero precision (because PROMOTE rate is zero overall), the precision metric is undefined and the bear-case detection fails. May need a "potential precision" estimator using a held-out catalog of synthetic positive examples.

---

## 13. The 20-year position with operationalized Silver-ingestion

(Unchanged from v4 §13 — three substrate-ingestible fragments: empirical-pattern conjectures invoked in proofs, generalizations the proof makes from specific cases, near-miss CLAIMs from tactic-tree exploration. The substrate does not ingest Lean-closed proofs themselves; the formal-proof manifold is Mathlib's territory, not the Σ-substrate's.)

## 14. The 20-year position

(Unchanged from v4 §14.)

## 15. The first principle

> **Truth stays harder to satisfy than generation is to produce.**

V5's revisions are in service of preserving this asymmetry against attack at the *evaluator* layer specifically. v4 broadened the reward signal (residuals as first-class); v5 hardens the broadened signal against gaming. The asymmetry holds only when the verification machinery — at every level, including the residual classifier itself — stays harder to satisfy than the generator's adaptation pressure can reach.

## 16. Genuine design freeze (post-v5)

I've declared design freeze three times now (after v3, v4, and now v5). Each time the next round has surfaced load-bearing critiques. Honesty requires acknowledging the pattern.

V5's freeze is conditional rather than absolute: **MVP build begins; if a round-5 review surfaces critiques as deep as rounds 3-4 (active failure modes the architecture creates by its own corrections), v6 is warranted; if round-5 surfaces only mitigations on top of v5's defensive surface, the design is genuinely converged and MVP-empirical-signal becomes the next high-value increment.**

The round-4 reviewer's offer to "simulate likely outcomes of the first 10K-episode pilot" is operationally the most valuable next step. After v5: accept the simulation offer; the simulation provides expected per-operator-class PROMOTE rate distributions, expected signal-class-residual rate distributions, expected `residual_signal_precision` under various classifier-quality scenarios, and concrete go/no-go criteria for "this is working" vs "this is failing." This substitutes for empirical signal we can't generate yet (MVP isn't built); the substrate gains an a-priori expected-distribution baseline against which actual MVP results will be compared.

## 17. One sentence

The Ergon learner v5 is a closed-loop scientific learning system for empirical mathematical patterns, hardened against the residual-gaming attractor that v4 created by promoting the residual primitive to first-class reward — a hybrid neural-plus-evolutionary mutation engine where the residual classifier is now treated as critical infrastructure (adversarial benchmark gate, ≥0.85 confidence abstention zone, `residual_signal_precision` per-operator tracking with 0.10 threshold), the agreement-weighted reward includes a non-LLM evaluator at w_NL=0.10 (with cross-model w_X reduced from 0.25 to 0.15 to reflect LLM-evaluator-prior correlation), the MAP-Elites descriptor is hot-swappable under per-axis fill-rate audit triggering replacement on >70% concentration or |corr|>0.7 axis pairs, and the Techne meta-loop's trigger dead-zone is fixed via lower threshold + absolute-count fallback + scheduled fires regardless of trigger — built MVP-first on local hardware ($0/mo, 2 weeks) with the adversarial residual benchmark as a pre-flight gate, progressing to v2.0 (~$700–900/mo, +32 weeks) covering the empirical-pattern manifold neither Mathlib nor Silver reaches today, in service of the design principle that truth must stay harder to satisfy than generation is to produce — at every level of the verification stack, including the residual classifier itself.

— Ergon, on behalf of the Prometheus agent ensemble
