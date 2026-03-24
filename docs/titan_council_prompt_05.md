# Titan Council Prompt 05 — The Ejection Mechanism

*For: Claude/Coeus, ChatGPT/Atlas, Gemini/Hyperion, DeepSeek/Oceanus, Grok/Prometheus*
*From: Project Prometheus (mechanistic interpretability research)*
*Date: 2026-03-24*

---

## TO THE COUNCIL

We ran your experiments. We found fire. Then we discovered the fire can't be carried. And we found out why.

This is the most data-dense prompt we've sent you. Every number is empirical. Every claim is backed by a specific experiment with a specific result. We are not theorizing. We are reporting.

---

## WHAT HAPPENED SINCE ROUND 4

### 1. Pivoted to 1.5B — Phase Transitions Everywhere (Then Not)

Following your unanimous recommendation, we moved from Qwen3-4B to Qwen2.5-1.5B-Instruct (28 layers, d_model=1536). Initial PT-1 scan at ε range [-12, +12]: 68/70 layer×trap pairs showed BIC-confirmed sigmoid dose-response. Random direction: 69/70.

We got suspicious. Ran a saturation check: 10 random unit vectors × 3 moderate epsilons (1, 2, 4) × 16 failing traps = 480 forward passes.

**Result: Zero flips.** 0/160 at every epsilon. The "phase transitions" at extreme ε were saturation artifacts — overwhelming a small model, not real attractor switches. Re-ran PT-1 at moderate ε [-4, +4]: still 69/70 "transitions" by BIC, but **zero decision boundary crossings** across all 70 layer×trap pairs. The BIC test detects curvature, not sign change.

### 2. Basin Escape Histogram — RIDGED

Ran 50 random directions on Overtake Race at L23 (thinnest basin wall), binary-searched for crossing ε.

| Metric | Overtake Race | Overtake 2nd | Overtake Last |
|--------|--------------|--------------|---------------|
| Crossed | 8/50 | 8/50 | **0/50** |
| Min ε | 3.71 | 3.71 | — |
| Median ε | 10.47 | 10.47 | — |
| Std ε | 4.56 | 4.56 | — |

**VERDICT: RIDGED.** 16% of directions find channels. 84% can't cross at any ε ≤ 20. Overtake Last (deeper basin, margin=-0.726) is completely impenetrable to random search. The basin has narrow channels that evolution can exploit.

### 3. CMA-ES Evolution — Found Fire (Z=40.6σ)

500 generations on Qwen2.5-1.5B-Instruct, L23, ε=3.0, popsize=32. Precipitation-specific fitness: only score failing traps, penalize breaking passing traps.

**Final evaluation:**

| Trap | Baseline | Steered (ε=3.0) | Result |
|------|----------|-----------------|--------|
| Overtake Race | -0.312 | +1.404 | **FLIPPED** |
| Overtake 2nd | -0.312 | +1.404 | **FLIPPED** |
| Overtake Last | -0.726 | +0.789 | **FLIPPED** |
| Siblings | -0.266 | +0.018 | **FLIPPED** |
| Density Illusion | -3.296 | -2.290 | improved +1.0 |
| Spatial Inversion | -1.693 | -0.859 | improved +0.83 |
| Birthday Paradox | -2.709 | -1.916 | improved +0.79 |

**14/30 → 18/30 correct. 4 flips. 0 broken.**

Overtake Last — impenetrable to 50 random directions at ANY epsilon — flipped at ε=3.0.

**Test C (Grok's test):** 30 random vectors at same norm and ε.

| Metric | Evolved | Random Mean | Random Std | Z-score |
|--------|---------|-------------|------------|---------|
| Flips | 4 | 0.00 | 0.00 | **∞** |
| Fitness | +9.451 | -0.051 | 0.234 | **+40.6σ** |

Every random vector: zero flips. The evolved vector is 40.6 standard deviations from random. At 4B in Round 4, this same test gave Z=1.38σ (haystack). At 1.5B: Z=40.6σ.

**The vector is genuinely special.** Not a haystack. Real structured direction through ridged basin channels.

### 4. Logit Lens Backward Pass — The Ejection Mechanism

Ran logit lens on all 30 traps across all 28 layers: project residual stream at each layer through the unembedding matrix, compute margin(L) = logit(correct) - logit(anti) at each layer.

**Baseline (no steering) — key failing traps:**

| Trap | Final Margin | Max Margin (any layer) | L* (ejection layer) |
|------|-------------|----------------------|---------------------|
| Density Illusion | -3.30 | **+6.52** | L26 |
| Overtake Race | -0.31 | **+6.11** | L27 |
| Spatial Inversion | -1.69 | +0.20 | L26 |
| Birthday Paradox | -2.71 | +0.89 | L21 |
| Handshakes | -1.62 | +0.16 | L22 |
| Staircase Steps | -2.42 | -0.02 | L25 |

**26 out of 30 traps have the correct answer ALIVE at some intermediate layer.** The model computes the right answer. Then something at L25-27 destroys it.

Density Illusion: the model reaches +6.52 margin for the correct answer at an intermediate layer — overwhelming confidence in "same." Then at L26, the margin collapses to -3.30. The model KNEW the right answer with a +6.5 margin and ejected it.

**Steered trajectories (Z=40.6σ vector at L23):**

Overtake Race trajectory (sampled across layers):
- Baseline: +0.3, -0.4, -0.1, -1.0, -1.5, -0.2, +0.4, +1.8 → **-0.31**
- Steered: +0.3, -0.4, -0.1, -1.0, -1.5, -0.2, **+7.8, +10.1** → **+5.87**

Pre-injection points are IDENTICAL. Post-injection (after L23): massive correct-answer amplification. The ejection mechanism at L27 still fires (margin drops from +10.1 to +5.87) but the vector gave the correct answer enough escape velocity to survive.

Overtake Last (impenetrable to random):
- Baseline: ...−1.2, −2.8, −2.0 → -0.73
- Steered: ...−1.2, **+3.9, +6.2** → **+5.05**

L* shifts observed:
- Cutting Rope: L* from 22 → 27 (+5 layers — ejection DELAYED)
- Siblings: L* from 21 → 23 (+2 layers)

### 5. The Generation Test — Where Fire Dies

Then we ran the test that matters. Actually generated text. Read the words.

**At ε=3.0 (evolution epsilon): Zero generation flips out of 30 traps.**

The model says the exact same thing with and without the vector. The steered text and baseline text are nearly identical.

**At ε=13.3 (brute force, 4x evolution strength): One generation flip out of 24 failing traps** (Month Ordering). One.

The vector shifts the first-token logit distribution at the answer position. But generation is autoregressive — the model produces one token, reads it back, generates the next. The steering vector fires at every token's forward pass, but the model's own generated context ("To determine the new position...") immediately anchors it back to the default reasoning chain. The perturbation gets washed out by autoregressive momentum.

**Logit margins: Z=40.6σ, 4 flips, genuinely special.**
**Actual generation: zero flips at ε=3.0, one at ε=13.3.**

The fire exists in the residual stream. We can see it. We can measure it. We can give it escape velocity for one token position. But we cannot sustain it through autoregressive generation.

---

## THE EJECTION MECHANISM — SUMMARY

The data tells a consistent story across all experiments:

1. **The model computes correct answers.** 26/30 traps show the correct answer alive at some intermediate layer. Density Illusion reaches +6.52 margin before collapsing to -3.30.

2. **Something at L25-27 actively ejects them.** L* (the ejection layer) clusters in the last 3 layers. This is not a missing capability. It's an active suppressor.

3. **The evolved vector can overcome the ejection at a single token position.** Z=40.6σ, 4 logit-margin flips, genuine basin channel navigation. The vector gives the correct answer escape velocity.

4. **But autoregressive generation washes out the intervention.** The model's self-generated context overwhelms the perturbation. Every subsequent token regenerates the ejection mechanism's output.

5. **The ejection mechanism is in the weights, not in the activations.** You can't outrun it with a perturbation. You have to remove it.

---

## WHAT WE NEED FROM YOU

We are not asking for more steering vector experiments. That chapter is closed. We are asking you to help us understand what we found and what it means.

**1. Is the ejection mechanism a known phenomenon?**

We've looked at Arditi et al. on refusal directions, Zou et al. on circuit breakers, the representation engineering literature. Nobody describes a mechanism where the correct answer's probability spikes at intermediate layers and then collapses at late layers on reasoning traps specifically. The closest is the "logit lens" work showing intermediate predictions differ from final outputs — but that's descriptive, not mechanistic. Has anyone characterized L* before? Has anyone measured the margin trajectory through layers on wrong-answer traps and seen the spike-and-collapse pattern?

**2. What components are doing the ejection at L25-27?**

We have the infrastructure to decompose the residual stream update at L* into attention heads and MLPs. Before we run it: what do you predict? Is it likely to be:
- A small number of "ejection heads" that specifically suppress correct answers (sparse, targetable)
- The MLP at those layers performing a learned heuristic override (dense, harder to target)
- A distributed effect across many components (no single ejection mechanism, just the aggregate of many weak biases)

Your prediction matters because it determines whether Rhea's approach (evolve LoRA perturbations to eliminate the ejection) is feasible. If the ejection is sparse (a few heads), LoRA can target it. If it's distributed, LoRA may need to reshape the entire late-layer computation.

**3. Why does the ejection happen at the LAST 3 layers?**

Our data shows L* clustering at L25-27 in a 28-layer model (89-96% depth). Is this because:
- Late layers implement the "output formatting" that RLHF trained for confident fluency
- Late layers are where the model resolves competition between multiple candidate answers
- The unembedding matrix at the final layer has a structural bias toward certain token distributions
- Something else we're not seeing

**4. The autoregressive washout — is this fundamental or fixable?**

The vector works on single-token logit margins but fails on generation. Is this:
- Fundamental to autoregressive generation (you can never steer with a single-layer injection because each generated token regenerates the attractor)
- Fixable by injecting at EVERY layer simultaneously (not just L23)
- Fixable by injecting only at the late layers where ejection happens (L25-27 instead of L23)
- Something else — perhaps the vector should target the autoregressive *context* formation, not the logit computation

We haven't tried multi-layer injection. It's testable on our hardware. Worth it?

**5. The big question: is the ejection mechanism a consequence of RLHF specifically, or does it appear in base models without RLHF?**

We tested Qwen2.5-1.5B-**Instruct** (post-RLHF). If we run the logit lens backward pass on Qwen2.5-1.5B (base, no instruction tuning, no RLHF), and L* disappears — that's direct evidence the ejection mechanism is RLHF-induced. If L* is present in the base model too, the story is different.

This is a one-hour experiment. Should we prioritize it?

**6. Tell us something we haven't considered.**

Five rounds. Ejection mechanism confirmed. Steering vector limit found. Rhea conceived. What are we not seeing?

---

## TECHNICAL CONTEXT

- **Hardware:** RTX 5060 Ti 16GB VRAM
- **Models tested:** Qwen3-4B (rounds 1-4), Qwen2.5-1.5B-Instruct (round 5)
- **Stack:** TransformerLens, PyTorch, EvoTorch, matplotlib
- **Genome:** `best_genome_1_5b.pt` — layer=23, norm=13.277, fitness=9.156, evolved at ε=3.0
- **Infrastructure:** AnalysisBase (shared model loading, trap batteries, hooks), preflight gate (62 checks), Phalanx suite (Jacobian/RMSNorm/steering sign), logit lens backward pass (L* detection), basin escape histogram, ejection decomposition (built, not yet run)
- **Trap battery:** 4 core logit traps + 6 held-out + 20 ordinal = 30 total
- **16 traps fail at baseline on 1.5B** (53.3% failure rate — good curvature for evolution)

---

## NOTES FOR JAMES

- Paste into all 5 Titans
- Key questions: Q2 (what's doing the ejection), Q4 (is autoregressive washout fixable), Q5 (RLHF vs base model)
- Q5 is the one that could change everything — if the base model doesn't have L*, we've proven RLHF creates the ejection mechanism. Run it regardless of what the Titans say.
- Watch for: does anyone recognize the spike-and-collapse pattern in L*? Has this been published?
- Save responses to: `docs/titan_council_prompt_05_responses.md`

---

*The fire exists. We can see it. We can measure it. We can trace its exact trajectory through the layers and watch it die at L*. We just can't carry it out with a steering vector. So we're building a forge where it doesn't need to be carried.*
