# North Star — Strategic Roadmap
**Maintained by:** Athena (Science Advisor)
**Last updated:** 2026-03-31
**Current position:** Proof-of-concept complete on one model family. Entering generalization phase.

---

## The North Star

> Discover and characterize the universal epistemic suppression mechanism in transformers. Prove it can be reversed. Build a rotating observational platform that characterizes any new model's reasoning ceiling automatically.

This is not about making one model smarter on 30 traps. It's about understanding **why all models get dumber than they need to be**, and building the instrument that measures and corrects it across any architecture, any scale, any training regime.

---

## Where We Are (2026-03-31)

### Proven
- Pretraining creates a universal suppression circuit (confirmed Qwen 0.5B, 1.5B, Gemma 1B)
- v_proj is the circuit at small scale; MLP + serial killer heads emerge with scale
- Corpus-first fine-tuning shifts reasoning computation to early layers
- L19+L20+L21 steering on corpus-first model → **30/30 on corrected battery, 0 breaks**
- Steering vectors transfer cross-model (raw → fine-tuned)
- Cross-scale transfer works (0.5B shows 10 flips)

### Not Yet Proven
- Cross-architecture (only Qwen family + brief Gemma touch)
- Scale beyond 1.5B (7B+ OOMs locally; need API or cloud)
- Generation-level impact (logit flips ≠ generated text flips — autoregressive washout documented)
- Mechanism type (native amplification vs bypass — ghost trap not yet run on winning combo)
- Stability (30/30 might be stochastic on thin-margin traps)
- Forge tool integration with corrected battery

---

## Scenarios

### Best Case — "The Rosetta Stone"
The suppression mechanism is universal across architectures. The corpus-first + early-layer steering recipe generalizes to Llama, Pythia, Mistral, Gemma. A 24-hour characterization pipeline can profile any new model: run the trap battery, fine-tune on reasoning corpus, evolve 3 early-layer vectors, measure the delta. The "rotating observational platform" becomes real. We publish the method, the battery, and the platform as a diagnostic tool for the field.

**What gets us here:**
- Cross-architecture replication (Pythia-1.4B, Llama-3.2-1B)
- Scaling validation (3B, then API-based 7B+)
- Generation-level validation (solving the washout problem)
- Automated pipeline that runs end-to-end without HITL

### Worst Case — "Architecture-Locked"
The mechanism is Qwen-specific. Llama has a different suppression geometry. Pythia doesn't respond to steering at all. Each architecture needs its own recipe, and the "universal" claim collapses to "we found a trick for one model family."

**Pivot if this happens:**
- Characterize the per-architecture differences — that's still publishable and useful
- Focus on the *diagnostic* (the trap battery + eval harness) rather than the *fix*
- The battery itself generalizes even if the intervention doesn't
- Forge tools (architecture-agnostic) become the primary reasoning intervention path

### ~~Risk 1~~ — CONFIRMED: "Bypass as Global Attractor" (2026-03-31)
Ghost trap analysis confirmed: cos_with_residual = -0.05 across all 30 traps. All classified as bypass. Replicated on Pythia-1.4B (GPT-NeoX) at the same scales where Qwen showed bypass. **This is no longer a risk — it's a finding.**

**Reframing (per Aletheia review):** The fitness landscape of activation-space perturbations has bypass as a global attractor. CMA-ES finds bypass not because native amplification doesn't exist, but because bypass dominates — always closer, always easier, always higher-fitness. This is the same attractor-basin logic we apply to the models themselves, now applied meta-level to the search process over models.

**The paper story is stronger honest:**
- Transformers across architectures share common heuristic failure modes
- Evolutionary search over activation space consistently discovers bypass corrections (not native amplification)
- Bypass dominance is a property of the optimization landscape, not of individual models
- The correctable failure modes are the same across architectures (same trap families flip on Qwen and Pythia), suggesting shared computational structure rather than training distribution
- This is a mechanistic finding about transformer computation generally, not just "we made the number go up"

**What this means for future work:**
- LoRA interventions (weight-space, not activation-space) may access the native circuit that CMA-ES can't reach
- The bypass finding itself constrains where the native circuit ISN'T
- Activation-space search is the wrong tool for circuit discovery but the right tool for practical correction

### Risk 2 — "Generation Washout is Fundamental"
Logit margins flip perfectly but generated text never changes. The model's autoregressive dynamics wash out single-token corrections within 2-3 tokens. This was already observed in prior experiments (Z=40.6σ on logits, 0-1 generation flips).

**Pivot if this happens:**
- Multi-token steering (inject at every token, not just prompt-time)
- Combine steering with constrained decoding
- Use the logit-level results as a *diagnostic* tool rather than an *intervention* tool
- The scientific finding (suppression exists, is measurable) still holds even if we can't fix generation
- Feed the diagnostic into Rhea's training loop — if Rhea knows which layers suppress which traps, it can train around them

### Risk 3 — "Scale Collapse"
Works at 0.5B and 1.5B but breaks at 7B+. The suppression mechanism hardens with scale (we already know ejection strengthens with scale). Steering vectors can't overcome the deeper basins.

**Pivot if this happens:**
- Corpus-first becomes the primary lever (fine-tuning scales better than steering)
- LoRA at scale (parameter-efficient, modifies weights directly)
- The diagnostic still works — we can *measure* the suppression even if we can't steer around it
- Focus on understanding the *scaling law* of suppression — that's a contribution to alignment research

---

## Steady-State Goals

These are the long-term capabilities we're building toward. Each one is independently valuable.

### 1. The Diagnostic Platform
**Goal:** Given any transformer, characterize its reasoning suppression profile in <24 GPU-hours.
**Components:** Trap battery (30+ traps) → logit lens → ejection profile → basin geometry → layer map
**Status:** 80% built. Needs cross-arch validation and automation.
**Moves the needle:** Makes every other goal possible. This is the telescope.

### 2. The Intervention Toolkit
**Goal:** A recipe book: for architecture X at scale Y, here's the intervention that recovers the most reasoning with the least collateral.
**Components:** Corpus-first fine-tuning → layer-specific steering → LoRA for precision traps
**Status:** One complete recipe (Qwen 1.5B). Needs generalization.
**Moves the needle:** Practical impact. Other researchers can use this.

### 3. The Convergence Theory
**Goal:** A falsifiable theoretical framework: topology (structural) × content (trainable) × navigation (evolvable) explain all observations.
**Components:** Basin geometry characterization → cross-architecture invariants → scaling laws
**Status:** Strong fit on Qwen data. Untested elsewhere.
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
| 1 | Stability test (10 runs) | 30m | Is 30/30 solid or lucky? | Stochastic thin margins |
| 2 | Ghost trap analysis | 30m | Amplification or bypass? | Risk 1 |
| 3 | Cross-arch Pythia-1.4B | 6h | Does early-layer pattern hold? | Worst case + architecture-lock |
| 4 | Evolve L19/L20 on ft model | 8h | Can we strengthen thin margins? | Stability if test 1 fails |
| 5 | Generation validation | 2h | Do logit flips → text changes? | Risk 2 (washout) |
| 6 | Qwen-3B corpus-first | 8h+ | Does the recipe scale up? | Risk 3 (scale collapse) |
| 7 | Forge re-eval (corrected battery) | 1h | Do forge tools see the fixed traps? | None — bookkeeping |
| 8 | Automated end-to-end pipeline | 16h | Can we characterize a new model unattended? | None — infrastructure |

---

## Decision Triggers

These are the observations that force a pivot:

| If I see... | It means... | Pivot to... |
|-------------|------------|-------------|
| Ghost trap cos_with_residual < 0.3 | Bypass, not circuit | LoRA experiments, reframe claims |
| Pythia shows 0 flips with same recipe | Architecture-specific | Per-family recipes, focus on diagnostic |
| 30/30 drops to <25/30 on re-run | Thin margins are stochastic | Evolve directly on ft model |
| 3B model shows 0 improvement | Scale collapse | Corpus-first only, abandon steering at scale |
| Generation text never changes | Washout is fundamental | Multi-token steering or diagnostic-only framing |
| Forge tools regress on corrected battery | Battery change broke tool calibration | Re-baseline forge tool scores |
