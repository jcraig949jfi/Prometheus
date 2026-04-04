# North Star — Strategic Roadmap
**Maintained by:** Athena (Science Advisor)
**Last updated:** 2026-04-03
**Current position:** Cross-architecture bypass confirmed on 5/6 families. v3 evolution running. Entering generation validation phase.

---

## The North Star

> Discover and characterize the universal epistemic suppression mechanism in transformers. Prove it can be reversed. Build a rotating observational platform that characterizes any new model's reasoning ceiling automatically.

This is not about making one model smarter on 30 traps. It's about understanding **why all models get dumber than they need to be**, and building the instrument that measures and corrects it across any architecture, any scale, any training regime.

---

## Where We Are (2026-04-03)

### Proven
- Pretraining creates a universal suppression circuit (confirmed across 5 architecture families)
- v_proj is the circuit at small scale; MLP + serial killer heads emerge with scale
- Corpus-first fine-tuning shifts reasoning computation to early layers
- L19+L20+L21 steering on corpus-first model → **30/30 on corrected battery, 0 breaks**
- Steering vectors transfer cross-model (raw → fine-tuned)
- **Cross-architecture bypass — confirmed on 5/6 architecture families:**
  - Qwen 0.5B: 28/30, L10 best (42% depth), bypass confirmed
  - Qwen 1.5B: 30/30 (corpus-first), bypass confirmed
  - Pythia 1.4B: 29/30, L16 best (67% depth), bypass confirmed
  - Llama 1B: 29/30, L8 best (50% depth), bypass confirmed
  - Phi-2 2.7B: 30/30 (L12+L20, eps×2.0), bypass confirmed, 0 breaks
  - Gemma 2B: IMPENETRABLE — 0 flips, sole outlier across all experiments
- **Cross-scale coverage:** 0.5B through 2.7B all respond. Smaller models are MORE responsive (shallower suppression basins).
- **Ghost trap (bypass):** cos_with_residual ≈ 0 on ALL architectures tested. Bypass is a global attractor, not a per-model quirk.
- **Cross-architecture transfer: DEAD.** Pythia genomes on Llama = +1 net. Llama genomes on Pythia = +2 net. Correction direction is topology-specific — you cannot import coordinates from a different topology.

### Not Yet Proven
- Scale beyond 2.7B (7B+ OOMs locally; need API or cloud)
- Generation-level impact (logit flips ≠ generated text flips — autoregressive washout documented)
- v3 battery steering (harder traps — overnight runs in progress)
- Corpus-first on non-Qwen architectures (does fine-tuning shift layers on Pythia/Llama?)
- Stability (30/30 might be stochastic on thin-margin traps)
- Forge tool integration with corrected battery

---

## Architecture × Scale Matrix

| | Qwen 0.5B | Qwen 1.5B | Pythia 1.4B | Llama 1B | Gemma 2B | Phi-2 2.7B |
|---|---|---|---|---|---|---|
| v2 Baseline | 23/30 | ~18/30 | ~19/30 | 21/30 | ~21/30 | 24/30 |
| v2 Best steered | 28/30 | 30/30 (ft) | 29/30 | 29/30 | 21/30 | 30/30 |
| v3 Baseline | 17/30 | 16/30 | 19/30 | 25/30 | — | 19/30 |
| v3 Steered | — | RUNNING (M1) | — | — | — | RUNNING (M2) |
| Bypass? | Yes | Yes | Yes | Yes | 0 flips | Yes |
| Best layer | L10 (42%) | Early (ft) / Late (raw) | L16 (67%) | L8 (50%) | — | L12+L20 |
| Cross-arch transfer | — | — | No | No | — | — |

---

## Scenarios

### Best Case — "The Rosetta Stone"
The suppression mechanism is universal across architectures. The corpus-first + early-layer steering recipe generalizes to Llama, Pythia, Mistral, Gemma. A 24-hour characterization pipeline can profile any new model: run the trap battery, fine-tune on reasoning corpus, evolve 3 early-layer vectors, measure the delta. The "rotating observational platform" becomes real. We publish the method, the battery, and the platform as a diagnostic tool for the field.

**What gets us here:**
- ~~Cross-architecture replication~~ — DONE (5/6 families, Gemma outlier understood)
- Scaling validation (7B+ via API or cloud)
- Generation-level validation (solving the washout problem)
- Automated pipeline that runs end-to-end without HITL
- v3 battery steering (harder traps also bypassable)

### Worst Case — "Architecture-Locked"
~~The mechanism is Qwen-specific.~~ This scenario is largely retired. 5/6 architectures respond. Gemma's resistance suggests *some* architectures have harder suppression geometry, but the pattern is clearly cross-architectural. The residual worst case is that each architecture needs a *different optimal layer recipe* — which is true (L10 vs L16 vs L8 vs L12+L20), but the diagnostic + evolve pipeline handles this automatically.

**Residual pivot if generalization stalls:**
- Characterize the per-architecture layer differences — already publishable
- Focus on the *diagnostic* (the trap battery + eval harness) rather than the *fix*
- The battery itself generalizes even if the intervention details vary per family
- Forge tools (architecture-agnostic) become the primary reasoning intervention path

### ~~Risk 1~~ — RETIRED: "Bypass as Global Attractor" (confirmed 2026-03-31, replicated 2026-04-03)
Ghost trap analysis confirmed: cos_with_residual ≈ 0 across all architectures and all 30 traps. All classified as bypass. Replicated on Qwen 0.5B, Qwen 1.5B, Pythia 1.4B, Llama 1B, and Phi-2 2.7B. **This is no longer a risk — it's a core finding.**

**Reframing (per Aletheia review):** The fitness landscape of activation-space perturbations has bypass as a global attractor. CMA-ES finds bypass not because native amplification doesn't exist, but because bypass dominates — always closer, always easier, always higher-fitness. This is the same attractor-basin logic we apply to the models themselves, now applied meta-level to the search process over models.

**The paper story is stronger honest:**
- Transformers across architectures share common heuristic failure modes
- Evolutionary search over activation space consistently discovers bypass corrections (not native amplification)
- Bypass dominance is a property of the optimization landscape, not of individual models
- The correctable failure modes are the same across architectures (same trap families flip on Qwen, Pythia, Llama, Phi-2), suggesting shared computational structure rather than training distribution
- This is a mechanistic finding about transformer computation generally, not just "we made the number go up"

**What this means for future work:**
- LoRA interventions (weight-space, not activation-space) may access the native circuit that CMA-ES can't reach
- The bypass finding itself constrains where the native circuit ISN'T
- Activation-space search is the wrong tool for circuit discovery but the right tool for practical correction

### Risk 2 — "Generation Washout is Fundamental" — HIGHEST PRIORITY
Logit margins flip perfectly but generated text never changes. The model's autoregressive dynamics wash out single-token corrections within 2-3 tokens. This was already observed in prior experiments (Z=40.6σ on logits, 0-1 generation flips). **This is now the single biggest unknown.** We have 5 architectures showing logit-level correction. If none of them produce generation-level changes, the intervention framing shifts to diagnostic-only.

**Pivot if this happens:**
- Multi-token steering (inject at every token, not just prompt-time)
- Combine steering with constrained decoding
- Use the logit-level results as a *diagnostic* tool rather than an *intervention* tool
- The scientific finding (suppression exists, is measurable) still holds even if we can't fix generation
- Feed the diagnostic into Rhea's training loop — if Rhea knows which layers suppress which traps, it can train around them

### Risk 3 — "Scale Collapse" — Partially Addressed
Works at 0.5B through 2.7B. Smaller models are more responsive, not less, which is encouraging. But 7B+ remains untested — and we already know ejection strengthens with scale. The suppression basins may be too deep for activation-space intervention at frontier scale.

**Pivot if this happens:**
- Corpus-first becomes the primary lever (fine-tuning scales better than steering)
- LoRA at scale (parameter-efficient, modifies weights directly)
- The diagnostic still works — we can *measure* the suppression even if we can't steer around it
- Focus on understanding the *scaling law* of suppression — that's a contribution to alignment research

---

## Convergence Theory Update

The cross-architecture results sharpen the theory: **topology × content × navigation**.

- **Topology** (architecture-specific): Determines WHERE suppression basins live. L10 in Qwen 0.5B, L16 in Pythia, L8 in Llama, L12+L20 in Phi-2. Each architecture has its own geometry.
- **Content** (training-specific): Determines WHAT gets suppressed. Same trap families flip across architectures, suggesting shared failure modes from shared training distributions.
- **Navigation** (evolvable): CMA-ES finds bypass basins in each specific topology. The search works everywhere because bypass is a global attractor in every topology tested.

The cross-architecture transfer failure **strengthens** this framework. You can't import coordinates from a different topology — Pythia genomes mean nothing in Llama space — because the basin geometry is architecture-specific. But the *existence* of bypassable basins is universal. The theory predicts: for any new architecture, run the diagnostic, evolve in that topology's space, find the basins. Don't try to transfer from somewhere else.

Gemma's resistance is the most interesting test case. Either (a) Gemma's topology genuinely lacks accessible bypass basins, or (b) the search hyperparameters need architecture-specific tuning. If (a), it constrains the "universal" claim to "near-universal" — which is still a strong finding.

---

## Steady-State Goals

These are the long-term capabilities we're building toward. Each one is independently valuable.

### 1. The Diagnostic Platform
**Goal:** Given any transformer, characterize its reasoning suppression profile in <24 GPU-hours.
**Components:** Trap battery (30+ traps) → logit lens → ejection profile → basin geometry → layer map
**Status:** 90% built. Validated on 6 architectures. Needs automation and v3 battery integration.
**Moves the needle:** Makes every other goal possible. This is the telescope.

### 2. The Intervention Toolkit
**Goal:** A recipe book: for architecture X at scale Y, here's the intervention that recovers the most reasoning with the least collateral.
**Components:** Corpus-first fine-tuning → layer-specific steering → LoRA for precision traps
**Status:** Five complete recipes (Qwen 0.5B, Qwen 1.5B, Pythia 1.4B, Llama 1B, Phi-2 2.7B). One confirmed failure (Gemma 2B). Needs generation validation and scale testing.
**Moves the needle:** Practical impact. Other researchers can use this.

### 3. The Convergence Theory
**Goal:** A falsifiable theoretical framework: topology (structural) × content (trainable) × navigation (evolvable) explain all observations.
**Components:** Basin geometry characterization → cross-architecture invariants → scaling laws
**Status:** Strong fit across 5 architectures. Cross-transfer failure confirms topology-specificity prediction. Gemma outlier needs explanation.
**Moves the needle:** This is the *understanding*. The theory predicts what should work on a new architecture before we try it.

### 4. The Forge Bridge
**Goal:** Connect Hephaestus forge tools (pure algorithmic reasoning) with neural model diagnostics. Use forge tool performance as an upper bound for what the model *could* achieve.
**Components:** forge_eval.py → trap-tool matrix → consensus-weighted evolution
**Status:** 357 tools forged, top tool hits 100% on traps. Integration with corrected battery pending.
**Moves the needle:** Establishes the ceiling. If a forge tool solves a trap with pure logic, the model has no excuse.

### 5. The Rhea Loop
**Goal:** Feed Ignis diagnostics into Rhea's self-improving training loop. Rhea uses ejection profiles to know which layers to target with LoRA.
**Status:** v_proj identified as the lever. Rhea at 75% metacognition at 360M. Scaling to 1.7B.
**Moves the needle:** Closes the loop from diagnosis to automated self-improvement.

---

## What Moves the Needle RIGHT NOW

Ranked by information-per-GPU-hour:

| Priority | Experiment | Time | What It Proves | Risk It Retires |
|----------|-----------|------|----------------|-----------------|
| 1 | v3 evolution (RUNNING M1+M2) | overnight | Are harder traps also bypassable? | v3 ceiling question |
| 2 | Generation validation (5 architectures) | 4h | Do logit flips → text changes? | Risk 2 (washout) — biggest unknown |
| 3 | Corpus-first on Pythia or Llama | 8h | Does fine-tuning shift layers on non-Qwen? | Recipe generalization |
| 4 | Automated end-to-end pipeline | 16h | Can we characterize a new model unattended? | None — infrastructure prerequisite for cloud |
| 5 | Cloud 7B+ experiments | cloud $ | Does steering survive at frontier scale? | Risk 3 (scale collapse) |
| 6 | Gemma deep dive | 4h | Is Gemma impenetrable or just mis-configured? | Convergence theory edge case |
| 7 | Forge re-eval (corrected battery) | 1h | Do forge tools see the fixed traps? | None — bookkeeping |

---

## Decision Triggers

These are the observations that force a pivot:

| If I see... | It means... | Pivot to... |
|-------------|------------|-------------|
| v3 evolution shows 0 improvement on M1+M2 | v3 traps may need weight-space intervention | LoRA experiments; activation-space may be insufficient for harder traps |
| Generation text never changes across 5 architectures | Washout is fundamental | Reframe as diagnostic-only tool; multi-token steering as last attempt |
| 30/30 drops to <25/30 on re-run | Thin margins are stochastic | Evolve directly on ft model |
| 7B+ model shows 0 improvement | Scale collapse | Corpus-first only, abandon steering at scale |
| Forge tools regress on corrected battery | Battery change broke tool calibration | Re-baseline forge tool scores |
| Gemma responds after hyperparameter tuning | Impenetrability was search failure, not architecture | Expand search budget for resistant architectures |
