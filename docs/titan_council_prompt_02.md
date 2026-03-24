# Titan Council Prompt 02 — Data Review & Next Steps
*Package for frontier model consultation. Includes raw results, code, and analysis.*
*Goal: refine signals, identify angles we're missing, suggest next exploration steps.*

---

## NARRATOR CONTEXT (for the Titan receiving this)

We're a mechanistic interpretability research program called Prometheus. We previously consulted you (Prompt 01) about our experimental design for testing the Reasoning Precipitation Hypothesis — the idea that linear directions in a language model's residual stream can shift computation from heuristic to reasoning regimes.

You critiqued our methodology and proposed improvements. We built all of them. We ran them overnight. Here are the raw results with our analysis. We need your eyes on the data — not reassurance, not a literature review. Tell us what the data says that we're not seeing.

**Our North Star is exploration, refinement, redirection first, publication second.** We want to know what to refine and probe next, not how to frame a paper.

---

## THE EXPERIMENTAL SETUP (recap)

- **Model:** Qwen3-4B (36 layers, d_model=2560)
- **Steering vector:** Evolved by CMA-ES against 4 adversarial reasoning traps (Decimal Magnitude, Density Illusion, Spatial Inversion, Anti-Sycophancy)
- **Vector properties:** norm=3.303, injection layer=31 (of 36), fitness=1.152
- **Tooling:** TransformerLens, Python, single RTX 5060 Ti (17GB VRAM)

---

## RAW RESULTS — Seven Independent Tests

### Test 1: Dose-Response ε Sweep
**Verdict: SMOOTH (no phase transition)**

Swept ε from -20 to +20 across 4 logit traps. All curves are smooth/linear. No sharp sigmoid or discontinuity at any ε.

| Trap | Shape | Max Jump | Ratio |
|------|-------|----------|-------|
| Decimal Magnitude | SMOOTH | 0.211 | 2.3x |
| Prime Check | SMOOTH | 0.133 | 2.2x |
| Density Illusion | SMOOTH | 0.047 | 2.5x |
| Spatial Inversion | SMOOTH | 0.023 | 2.7x |

**Note:** The maximum jump ratios are all below 3x (our threshold for phase transition detection). The dose-response curves are available as PNG if you want to inspect the shape.

---

### Test 2: Directional Ablation
**Verdict: BYPASS**

Three conditions: baseline (no intervention), steered (inject vector), ablated (remove direction from residual stream: h ← h − (h·v̂)v̂).

| Trap | Baseline | Steered | Ablated | Causal (S-A) | Bypass (A-B) |
|------|----------|---------|---------|-------------|-------------|
| Decimal Magnitude | 0.10 | 0.10 | 0.10 | 0.00 | 0.00 |
| Density Illusion | 1.00 | 0.30 | 2.00 | -1.70 | +1.00 |
| Spatial Inversion | 0.10 | 0.10 | 0.10 | 0.00 | 0.00 |
| Anti-Sycophancy | 1.00 | 1.00 | 4.00 | -3.00 | +3.00 |
| **MEAN** | **0.55** | **0.38** | **1.55** | **-1.18** | **+1.00** |

**Critical observation:** On Density Illusion and Anti-Sycophancy, ablation *improves* performance dramatically (2x and 4x baseline). The vector HURTS these traps. Removing it helps. Meanwhile, steering shows no improvement over baseline on any trap.

**Question for you:** Why would an evolved vector with fitness=1.152 show zero or negative effect on the generation-scored traps? The CMA-ES fitness function used logit-shift scoring, not generation scoring. Is the vector optimized for logit margin but not behavioral output? If so, what does that tell us about the relationship between logit-space interventions and generation-space behavior?

---

### Test 3: Layer-wise Linear Probing
**Verdict: WEAK separability, near-zero alignment**

Probed all 36 layers × 4 stream families (resid_pre, attn_out, mlp_out, resid_post) with logistic regression. 24 prompts (4 traps × 6 variants), 20 correct, 4 wrong at baseline.

Top probes by AUC:

| Layer.Stream | AUC | Accuracy |
|-------------|-----|----------|
| L31_mlp_out | 0.588 | 0.792 |
| L35_mlp_out | 0.525 | 0.833 |
| L33_mlp_out | 0.462 | 0.792 |
| L24_mlp_out | 0.450 | 0.833 |
| L32_mlp_out | 0.438 | 0.792 |

Steering vector alignment at injection layer 31:
- resid_pre: cos = **-0.024**
- mlp_out: cos = **+0.003**
- resid_post: cos = **-0.020**

**Interpretation:** The best probe is at the injection layer (L31 mlp_out), but AUC=0.588 is barely above chance. Steering vector alignment is effectively zero at all layers. The vector does not point toward the correct/incorrect separatrix.

**Question for you:** The probe label distribution is 20/4 (83% correct at baseline). This model is already good at these traps without steering. Is there value in probing with more difficult traps where the model fails more often? Or does the fact that 4B already gets 20/24 right explain why the steering effect is so small?

---

### Test 4a: Activation Patching (Residual Stream)
**Verdict: 1 PRECIPITATION signal out of 10 traps**

Patched steered residual stream activations into baseline runs, layer by layer. Measured recovery fraction (how much of the steering effect is recovered by patching at each layer).

9 out of 10 traps showed "steering effect too small" (< 0.1 logit margin change) — skipped.

**The one trap that worked: Overtake Race (held-out, never seen by CMA-ES)**

| Layer | Recovery |
|-------|----------|
| L0 | 0.000 |
| L7 | 0.000 |
| L14 | 0.000 |
| L21 | 0.000 |
| L28 | 0.000 |
| **L31 (injection)** | **1.000** |
| L35 | 1.000 |

Signal appears at injection layer, propagates to final layer, absent before injection. This is the exact precipitation signature: the vector introduces information at L31 that downstream layers (L32-L35) process to produce the correct output.

**Test 4b: Component Patching** (attention heads + MLPs at layers 26-35)

For Overtake Race only (others had too-small effects):
- L31: mlp recovery=0.050, top head=H19 recovery=0.073
- L32: mlp recovery=0.082, top head=H10 recovery=-0.069
- L33: mlp recovery=0.101, top head=H30 recovery=-0.015
- L34: mlp recovery=0.068
- L35: mlp recovery=0.093

**Interpretation:** Signal is distributed across MLPs in layers 31-35 (each contributing 5-10% recovery), not concentrated in one head. No single "reasoning bottleneck" component.

---

### Test 4c: CoT Patching (Chain-of-Thought Ground Truth)
**Verdict: ANTI-CORRELATED — evolved vector opposes CoT direction**

For each trap, ran standard (model fails) and CoT-forced ("Let's think step by step") versions. Cached activations at injection layer. Patched CoT activations into standard run.

| Trap | Baseline | CoT | Steered | Patched | cos(vector, CoT-baseline) |
|------|----------|-----|---------|---------|--------------------------|
| Decimal Magnitude | +4.32 | +1.17 | +4.36 | +1.80 | **-0.228** |
| Prime Check | +1.84 | +1.43 | +1.82 | +1.28 | **-0.200** |
| Density Illusion | -0.67 | -7.28 | -0.63 | -7.51 | **-0.311** |
| Spatial Inversion | -0.37 | +0.62 | -0.35 | +0.30 | **-0.325** |
| Overtake Race | -1.91 | -6.62 | -1.81 | -6.17 | **-0.263** |
| Simpson's Paradox | +0.83 | +1.59 | +0.80 | +1.14 | **-0.221** |

**All cosines are negative** (range: -0.18 to -0.33). The evolved steering vector consistently points in the *opposite direction* from where chain-of-thought takes the model's activations.

**This is our most interesting finding.** The vector doesn't amplify reasoning — it finds a geometrically different path. CoT changes the residual stream in direction A; the evolved vector changes it in direction -A (approximately). Yet both sometimes improve performance.

**Questions for you:**
1. What computational mechanism would produce anti-correlation between an effective steering vector and the CoT direction? Is the vector suppressing the model's default heuristic rather than amplifying reasoning?
2. Is the anti-correlation stable (same sign across all traps) evidence of a consistent mechanism, or could it be an artifact of the CoT direction being poorly defined (CoT changes the prompt, not just the computation)?
3. Does this suggest we should evolve vectors that *maximize* alignment with the CoT direction instead of maximizing task performance? Would that produce precipitation vectors?

---

### Test 5: Distributed Alignment Search (DAS)
**Verdict: VECTOR IS HIGHLY SPECIFIC (not random noise)**

For each trap, tested subspace dimensions [1, 2, 4, 8, 16, 32, 64, 128]. At each dimension, generated 50 random orthonormal subspaces, ablated each, and compared against the vector-aligned subspace.

Representative results (Decimal Magnitude):

| Dimension | Random Preserved | Aligned Preserved | Ratio |
|-----------|-----------------|-------------------|-------|
| 1 | 1.21 ± 1.05 | 11.01 | **9.1x** |
| 2 | 0.93 ± 1.02 | 8.93 | **9.6x** |
| 4 | 1.86 ± 1.52 | 13.63 | **7.3x** |
| 8 | 1.20 ± 2.11 | 7.88 | **6.6x** |
| 16 | 0.63 ± 2.96 | 5.39 | **8.6x** |
| 32 | 0.76 ± 4.89 | 10.65 | **14.0x** |
| 64 | 0.91 ± 7.92 | 5.82 | **6.4x** |
| 128 | -0.56 ± 8.68 | 7.23 | **N/A** |

Pattern holds across all traps: the aligned (vector-containing) subspace preserves 5-15x more of the steering effect than random subspaces of the same dimension. Even at dim=1, the vector's direction alone captures most of the effect.

**Interpretation:** This is NOT a random perturbation. The vector targets a specific, narrow computational pathway. But that pathway is not the reasoning pathway (cos ≈ 0 with probes, cos ≈ -0.25 with CoT).

---

### Tests 6-10: Generalization Gauntlet

| Test | Verdict | Key Data |
|------|---------|----------|
| Token Generalization | **CONCEPT** | Generalizes to unseen decimal pairs (train Δ=+0.032, test Δ=+0.021) |
| Prompt Distribution | **BRITTLE** | 3/5 paraphrases show zero steering effect |
| Multi-Step Reasoning | **REASONING** | Small positive effect on harder problems (mean Δ=+0.008) |
| KL Divergence | **AMPLIFICATION** | KL(steered ∥ base) = 0.0003 — nearly zero distributional shift |
| Attention Patterns | FAILED (API bug) | Not yet measured |

---

## SYNTHESIS — What the Data Actually Says

### What we know:
1. The vector is **bypass** by all causal tests (dose-response, ablation, patching).
2. But it's **not random** — DAS shows 10-15x specificity over random directions.
3. It encodes a **genuine concept** (decimal comparison generalizes to novel numbers).
4. It operates via a **different geometric pathway** than chain-of-thought (anti-correlated, cos ≈ -0.25).
5. It barely perturbs the output distribution (KL = 0.0003) — it's a **precision nudge**.
6. It's **prompt-brittle** — works on the exact phrasing it was evolved on, fails on paraphrases.
7. At 4B, **the model already gets 20/24 traps right** without steering — there's little room for the vector to improve.
8. One held-out trap (Overtake Race) shows a **genuine precipitation signature** — signal at injection, propagation downstream, absent before.

### What we don't know:
1. What SAE features the vector activates (we haven't decoded it yet).
2. Whether the anti-CoT geometric relationship holds on other architectures (Gemma, Llama).
3. Why the Overtake Race shows precipitation while 9 other traps don't.
4. Whether evolving for CoT-alignment (instead of task performance) would find precipitation vectors.
5. What the residual stream trajectory looks like with and without steering (we haven't plotted it).
6. Whether these geometric signatures exist at smaller scales (0.5B, 1.5B, 3B) or only emerge at 4B.

---

## WHAT WE NEED FROM YOU

We are NOT asking you to help us write a paper. We're asking you to help us **explore**.

1. **Look at the raw data above.** Do you see patterns, anomalies, or angles we haven't considered? Especially in the DAS numbers, the anti-CoT correlation, and the ablation results where removing the vector *helps*.

2. **The anti-CoT finding is our most interesting signal.** What does it mean mechanistically that an effective vector opposes the chain-of-thought direction? Is this a known phenomenon? Does it connect to any existing work on "reasoning via different computational routes"?

3. **The Overtake Race precipitation signal on a held-out trap** — how do we follow this thread? Run more held-out traps? Zoom in on what's different about Overtake Race (simple ordering/logic vs numerical comparison)?

4. **Given our hardware constraints** (17GB VRAM, max ~4B models with TransformerLens), what is the highest-ROI next experiment? Options we're considering:
   - SAE decomposition of the vector (what features does it activate?)
   - Cross-architecture comparison on Gemma-2-2B (does the anti-CoT geometry hold?)
   - Evolve vectors that maximize CoT-alignment instead of task performance
   - More held-out traps to test precipitation replication
   - Probe the "ablation improves performance" phenomenon (why does removing the vector help on some traps?)

5. **Write code** for whichever experiment you think has the highest ROI. Same setup: TransformerLens, Qwen3-4B or Gemma-2-2B, best_genome.pt with keys 'vector' (shape [2560]) and 'layer_index' (int).

We're not at the drawing board. We're at the map table, and the map has interesting features we don't understand yet. Help us decide which direction to walk.

---

## NOTES FOR JAMES

- Paste this into each Titan
- The key questions are in section "WHAT WE NEED FROM YOU" #1-5
- Watch for: do they see the anti-CoT finding as significant? Do they have a mechanistic explanation?
- Watch for: do they agree on which experiment has highest ROI?
- Save responses to: `reproductions/titan_council/TITAN_NAME_response_02.md`
- The anti-CoT correlation is the thread to pull. If any Titan has a theory for why it works, that's gold.
