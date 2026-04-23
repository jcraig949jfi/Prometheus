# Prometheus — Results

*Updated: 2026-03-25*

---

## The Finding

Language models compute correct answers internally and then suppress them before output. This isn't a side effect of alignment training — it's built in during pretraining. The internet contains more confident wrong answers to tricky questions than correct ones, and models learn to reproduce that pattern.

We found this suppression circuit, mapped it, broke it, and showed that a 135M-parameter model with the circuit disabled outperforms models 11x its size on epistemic honesty.

---

## Results at a Glance

| Scale | What we did | Survival Rate | Metacognition | Key finding |
|-------|------------|---------------|---------------|-------------|
| **135M** | CMA-ES over LoRA (rank-4, 484K params) | 0% to 92% | 6% to 75% | Phase transition at gen 65. Self-improving loop closed. |
| **360M** | CMA-ES over LoRA (rank-8) | 0% to 89% | 37% to 75% | Same recipe, same result. v_proj confirmed as the lever. |
| **1.7B** | Targeted LoRA on 5 heads in L22-L23 (65K params) | 0% to 42% | pending | 65K targeted params beat 5.5M blanket params. |

**Survival Rate (SR):** fraction of reasoning traps where the correct answer survives to the output (not ejected).

**Metacognition:** fraction of uncertainty traps where the model appropriately says "I don't know" instead of confabulating.

---

## The Ejection Mechanism

**What it is:** A two-stage circuit in transformer models that suppresses correct answers, honest uncertainty, and self-correction before they reach the output.

- **Stage 1 (writing):** Early-layer v_proj (attention value projections) builds heuristic representations from the question tokens and writes them into the KV cache.
- **Stage 2 (execution):** Late-layer MLP and attention heads read the KV cache and suppress the correct answer in favor of the confident-but-wrong heuristic.

**Where it lives:** The last ~10% of layers. At 1.7B, the circuit concentrates in 5 attention heads across 2 layers:

| Head | Margin | Layer |
|------|--------|-------|
| L23.head_9 | -0.723 | 23 |
| L22.head_26 | -0.700 | 22 |
| L23.head_8 | -0.592 | 23 |
| L22.head_7 | -0.463 | 22 |
| L23.head_23 | -0.428 | 23 |

This pattern is architecturally conserved across SmolLM2 and Qwen model families.

**Evidence it's pretraining, not RLHF:** 19 out of 30 ejection traps are present in base models before any alignment training. Only 1 out of 30 is RLHF-induced.

---

## Breaking It

**Method:** CMA-ES (evolutionary search) over LoRA adapter weights targeting v_proj. The fitness function rewards models where correct answers survive to the output (logit lens monotonicity + survival rate).

**The key insight — v_proj is the entire circuit:**
- v_proj alone recovers 72% survival rate
- gate_proj alone: 0%
- q_proj alone: 0%
- v_proj is 19% of the LoRA parameter budget but produces identical results to the full budget

**Scaling requires targeting, not broadening:**

| Approach | Parameters | SR | Verdict |
|----------|-----------|-----|---------|
| 1.7B blanket rank-8 | 2,750,000 | 0.361 | plateaued |
| 1.7B blanket rank-16 | 5,500,000 | 0.083 | collapsed |
| 1.7B targeted L22+L23 | **65,536** | **0.417** | best result |

More parameters hurt because the signal gets diluted. Targeting the specific ejection heads with 42x fewer parameters produces a better result.

---

## The Self-Improving Loop

Once ejection is suppressed, the model can generate reasoning chains that are verified externally (Lean 4 theorem prover for arithmetic). Training on its own verified chains further improves metacognition:

```
Evolve (CMA-ES) --> Generate reasoning chains --> Verify (Lean 4) --> Train --> 75% metacognition
```

This recipe works identically at 135M and 360M. The model trains on what it got right, verified by an external proof system, and gets better at knowing what it knows.

---

## The Generalization Result

The fitness function targeted only 36 reasoning traps. It never mentioned metacognition, self-correction, or sycophancy resistance. Yet when ejection was suppressed:

| Capability | Before | After | Notes |
|-----------|--------|-------|-------|
| Metacognition | 6% (1/16) | **100% (16/16)** | Never in fitness function |
| Self-correction | 20% (2/10) | **80% (8/10)** | Never in fitness function |
| Calibration | 30% (3/10) | **70% (7/10)** | Never in fitness function |
| Arithmetic | 20% (3/15) | 40% (6/15) | Partial improvement |

These capabilities weren't trained — they emerged when the suppression was removed. The ejection mechanism is unified: breaking it on reasoning simultaneously restores honesty across every dimension we measured.

---

## The Trade-Off (Reported Honestly)

Ejection suppression is not free. The evolved 135M model shows a regression on logic/bias traps:

| Pillar | Before | After | Delta |
|--------|--------|-------|-------|
| Logic/Bias | 40% (6/15) | 7% (1/15) | **-33%** |

The model lost cognitive reflection traps (Monty Hall, Simpson's paradox, contrapositive reasoning). The LoRA perturbation that enables metacognition disrupts some heuristics that were producing correct answers on logic traps.

The net gain is large (metacognition +94%, self-correction +60%, calibration +40% vs logic/bias -33%), but the trade-off exists. We believe multi-objective fitness will resolve this — evolving for both survival rate AND logic trap performance simultaneously — but this has not yet been demonstrated.

Additionally, the evolved model shows an over-correction bias on self-correction traps: it correctly identifies 8/10 wrong answers as wrong, but also flags 2/10 correct answers as wrong. It learned error detection but became trigger-happy.

---

## Basin Geometry — The Shape of Suppression

*Added: 2026-03-28*

We mapped the basin geometry of the ejection circuit at 1.5B by binary-searching for the minimum steering vector magnitude (ε) that flips each trap, across 100 random directions per layer.

**Basin escape rates across the ejection circuit (1.5B, 100 directions, ε≤20):**

| Layer | Crossing Rate | Basin Shape |
|-------|--------------|-------------|
| L22 | 5.3% | ANISOTROPIC — some channels exist |
| L23 | 4.8% | DEEP — almost impenetrable |
| L24 | 3.6% | DEEP — almost impenetrable |

**Basins deepen with layer depth.** Only 5 of 16 trap families are ever penetrable. 11 traps are completely impenetrable at any layer with random directions. The Overtake family shows RIDGED geometry — specific low-ε channels where CMA-ES can find entry points.

## Cross-Scale Evidence — Ejection Strengthens with Size

*Added: 2026-03-28*

We evolved steering vectors on Qwen-0.5B (d_model=896, L18) to compare with 1.5B results.

| Metric | Qwen-0.5B (L18) | Qwen-1.5B (L19 best) |
|--------|-----------------|---------------------|
| Flipped traps | **10** | 5 |
| Broken traps | 1 | 0 |
| Impenetrable at 1.5B but flipped at 0.5B | 5 (Density Illusion, Elevator Floor, Handshakes, Staircase Steps, Cutting Rope) | — |

**The ejection circuit is weaker at smaller scale.** Traps that no direction at any magnitude can touch at 1.5B are flipped by a single evolved vector at 0.5B. The suppression mechanism exists at 0.5B but is fragile — by 1.5B it's robust. This is quantitative evidence that the ejection circuit strengthens with model scale.

**Implication:** LoRA-based steering may hit a fundamental wall at larger scales. The number of redundant suppression pathways likely grows with parameter count, making rank-limited interventions insufficient.

## Layer Sweep — Full Ejection Circuit Map (1.5B)

*Added: 2026-03-28*

Athena autonomous session ran CMA-ES evolution at every layer from L19-L26 (300 gen each).

| Layer | Flipped | Broken | Trap Families |
|-------|---------|--------|---------------|
| L19 | 5 | 0 | Spatial Inversion, Overtake ×3, Siblings |
| L20 | 4 | 0 | Overtake ×3, Siblings |
| L21 | — | — | (500 gen, reference run) |
| L22 (gate+v) | 8 | 3 | Diverse (8 families) |
| L24 | 3 | 0 | Overtake ×3 |
| L25 | 3 | 0 | Overtake ×3 |
| L26 | 3 | 0 | Overtake ×3 |

**L19 is the best zero-break steering layer.** L22 flips the most traps (8) but breaks 3. The ejection circuit spans L19-L26 with per-layer specialization.

---

## Corpus-First Experiment — Training Data Improves Reasoning Without Changing the Circuit

*Added: 2026-03-28*

**The question:** Can supervised fine-tuning on reasoning data weaken the ejection circuit, making the basins shallower for subsequent steering?

**The answer:** No — but it improves reasoning anyway, through a mechanism we didn't predict.

**Method:** Fine-tune Qwen-1.5B on 300 self-generated reasoning examples (74 correct, 181 corrected, 45 "unknown") for 3 epochs at lr=5e-6 with bf16, gradient checkpointing, and gradient clipping. No evolution. No steering vectors. Pure supervised learning.

**Results:**

| Pillar | Baseline | Post-Corpus | Delta |
|--------|----------|-------------|-------|
| Tier A accuracy | 46.7% | 46.7% | 0% |
| Tier B accuracy | 50.0% | 50.0% | 0% |
| Tier C (far-transfer) | 42.9% | **52.4%** | **+9.5%** |
| Metacognition | 35.7% | **57.1%** | **+21.4%** |
| Self-correction | 38.5% | **53.8%** | **+15.4%** |
| Composite | 0.335 | **0.427** | **+27.5%** |

**The ejection profile is structurally unchanged:**
- Correct answer alive at some layer: 26/30 → 26/30
- Top-5 at some layer: 7/30 → 7/30
- L* distribution: median 26 → median 26

**What changed:** Margins within existing basins. Traps the model already got right became more confident (CRT Widgets: +2.81 → +5.47). Some traps it got wrong became more wrong (Spatial Inversion: -1.69 → -3.20). The basin geometry is fixed — what moved is the model's position within the basins.

**What this means:**
1. The ejection circuit is structural, not distributional — 300 reasoning examples don't reshape it
2. But reasoning performance has room to improve *within* the existing geometry
3. Metacognition (+21.4%) and self-correction (+15.4%) improved because the training data contained examples of uncertainty acknowledgment and error correction — the model learned these *patterns* without changing the suppression circuit
4. The basins are the ceiling, not the current performance — there's headroom before hitting the wall
5. This is evidence for the metacognitive hedge: the ejection circuit cannot be trained away, only worked around (steering vectors) or bypassed (Noesis)

---

## The Forge Pipeline

Alongside the core ejection work, we built an automated pipeline for discovering computable reasoning criteria:

- **Nous** mines cross-domain concept combinations (95 concepts across 18 fields)
- **Coeus** learns which concepts causally predict successful tool creation
- **Hephaestus** forges concepts into Python reasoning tools and tests them against an 89-category battery
- **Nemesis** adversarially stress-tests tools with metamorphic mutations
- **CAITL** refines tools through iterative category-only feedback (5 versions, v1→v5)

**Current numbers (v5, 2026-03-28):** 344 tools scored on 89-category battery. 31 genuinely unique by behavioral fingerprint (91% redundancy). Tier A accuracy: 40.3%. Tier B accuracy: 78.1%. Tier B honesty: 0.993. Unseen generalization: 46.2%. CAITL trajectory: +167% max improvement across 5 versions, near-zero plateaus.

These tools are designed to become fitness function terms in RLVF and as reasoning organisms in the Noesis tensor exploration engine.

---

## Hardware

All results obtained on a single consumer GPU:
- NVIDIA RTX 5060 Ti (16GB VRAM)
- Windows 11 + WSL2 Ubuntu
- No cloud compute used

---

## Reproducibility

All evolution logs, checkpoints, evaluation results, and analysis scripts are in this repository. The core experiment (135M ejection suppression) takes approximately 6 hours on the hardware above.

Key paths:
- Ignis (ejection characterization): `ignis/`
- Rhea (evolution + self-improving loop): `rhea/` (WSL)
- Forge pipeline: `agents/nous/`, `agents/coeus/`, `agents/hephaestus/`
- Evaluation harness: `ignis/src/eval_v2.py`
- Trap battery: `agents/hephaestus/src/test_harness.py`
