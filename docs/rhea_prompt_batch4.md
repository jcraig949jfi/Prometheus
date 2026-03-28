# Rhea Prompt: Batch 4 — Targeted 1.7B Evolution

*For: Rhea engineer*
*From: Athena (chief science officer)*
*Date: 2026-03-25*

---

## BATCH 3 RESULTS — ANALYSIS

### Job 2 was the breakthrough: the 1.7B ejection map

Ignis decomposition found the circuit. At 1.7B, ejection concentrates in L22-L23:

```
L23.head_9   -0.723   ← strongest suppressor
L22.head_26  -0.700
L23.head_8   -0.592
L22.head_7   -0.463
L23.head_23  -0.428
```

This matches the Qwen 1.5B finding (L25-27) — different architecture, same late-layer pattern. The ejection circuit is architecturally conserved: it's always in the last ~10% of layers, always in a small cluster of attention heads.

This is why rank-16 blanket LoRA failed (SR=0.083). CMA-ES was searching a 5.5M-parameter space where the signal lived in ~200K parameters. Now we know exactly where to look.

### Job 1: Adversarial correction corpus was a wrong turn

| Corpus type | Metacognition | Reasoning transfer | Self-correction |
|------------|---------------|-------------------|-----------------|
| Verified self-corpus (batch 2) | **75%** | 55% | 37.5% |
| 70/30 verified + adversarial (batch 3) | 50% | **40%** | **62.5%** |

The correction chains preserved self-correction but **cost 25 points on metacognition and 15 on reasoning transfer**. Mixing "what wrong looks like" into the primary training data confused the model. The adversarial examples taught it to second-guess itself, which is self-correction but not metacognition.

**Lesson: train on what right looks like first. Add error-detection as a separate phase.**

The right pipeline is:
1. Phase 1: self-corpus (verified correct chains only) → 75% metacognition
2. Phase 2: correction fine-tune (error-detection chains only) → preserve metacognition, boost self-correction
3. Never mix the two corpora in a single training run

### Job 3: Multi-phase σ works but needs NaN guard

SR=0.417 (vs 0.000 with fixed σ=0.02). The schedule concept is sound — σ=0.10 got the evolution moving. But PPL went to NaN in later phases, likely from:
- Very small LoRA weights producing near-zero logits
- Log-probability computation hitting -inf
- Division by zero in perplexity averaging

Fix: clamp logits before softmax, guard against log(0), use `torch.nan_to_num` on the PPL tensor.

---

## BATCH 4 — THREE JOBS

### Job 1: 1.7B Head-Masked CMA-ES (THE MAIN EVENT)

Apply LoRA **only to v_proj weights of the 5 identified ejection heads** in L22-L23.

**Parameters:**
- Model: SmolLM2-1.7B-Instruct
- Target: v_proj of L22.head_7, L22.head_26, L23.head_8, L23.head_9, L23.head_23
- LoRA rank: 8
- Estimated parameter count: ~200K (vs 5.5M for blanket rank-16)
- CMA-ES population: 20 (same as 360M)
- Generations: 150 (allow longer run — smaller search space should converge faster)
- Fitness: logit lens monotonicity + survival rate

**Implementation notes:**

The LoRA adapter needs to target specific heads within a layer's v_proj, not the entire v_proj matrix. In SmolLM2-1.7B, each layer's v_proj is a single weight matrix that covers all heads. To target specific heads:

Option A (preferred): Apply LoRA to the full v_proj of L22 and L23 only (2 layers instead of 32). This is simpler and still reduces the search space to ~500K params. The non-ejection heads in L22-L23 will have small LoRA deltas that CMA-ES can learn to keep near zero.

Option B (surgical): Slice the v_proj weight matrix by head dimension and apply LoRA only to the head-specific slices. More complex to implement with `peft` but gives the tightest search space (~200K params).

**Start with Option A** — it's simpler and the 360M results show CMA-ES can handle ~500K params efficiently at rank-8. If it plateaus, try Option B.

```bash
#!/bin/bash
# batch4_job1_1.7b_targeted.sh
python evolve_lora_gate_v.py \
  --model HuggingFaceTB/SmolLM2-1.7B-Instruct \
  --target-layers 22,23 \
  --target-proj v_proj \
  --rank 8 \
  --population 20 \
  --generations 150 \
  --fitness "logit_lens+survival" \
  2>&1 | tee runs/batch4_1.7b_targeted.log
```

**Expected behavior:** Phase transition around gen 30-60 (faster than blanket LoRA because search space is 10x smaller). SR should climb past 0.40 — if it doesn't by gen 80, the circuit map may be incomplete and we need to add L21 or L24.

### Job 2: 360M Coherence with NaN Guard

Re-run the multi-phase σ schedule with numerical stability fixes.

```bash
#!/bin/bash
# batch4_job2_coherence_fixed.sh
python evolve_coherence.py \
  --model HuggingFaceTB/SmolLM2-360M-Instruct \
  --sigma-schedule "0.10:20,0.05:30,0.02:50" \
  --ppl-threshold 1.05 \
  --nan-guard \
  --gens 100 \
  2>&1 | tee runs/batch4_coherence_v2.log
```

The `--nan-guard` flag should:
1. Clamp model logits to [-100, 100] before softmax
2. Replace any NaN/Inf in loss with a large penalty value (e.g., 1000)
3. Skip PPL computation for genomes that produce NaN and assign them fitness = -inf
4. Log NaN events so we can see how frequently they occur

If `--nan-guard` doesn't exist yet, add it. The core fix is 3 lines:

```python
# In PPL computation:
logits = torch.clamp(logits, -100, 100)
loss = F.cross_entropy(logits, targets)
if torch.isnan(loss) or torch.isinf(loss):
    return float('inf')  # worst possible PPL → fitness = -inf
```

### Job 3: 1.7B Self-Corpus Prep (If VRAM Allows)

While Job 1 runs, start generating the self-corpus for 1.7B. Use the **base** 1.7B model (not yet evolved) to establish baseline chains. This gets the corpus pipeline ready so we can immediately train on verified chains once Job 1 produces an evolved 1.7B.

```bash
#!/bin/bash
# batch4_job3_corpus_prep.sh
# Generate reasoning chains from base 1.7B
python generate_chains.py \
  --model HuggingFaceTB/SmolLM2-1.7B-Instruct \
  --traps eval_traps.jsonl \
  --output runs/batch4_chains_1.7b_base.jsonl \
  --n-per-trap 20

# Verify with Lean 4
python lean_verify.py \
  --input runs/batch4_chains_1.7b_base.jsonl \
  --output runs/batch4_verified_1.7b_base.jsonl
```

**VRAM note:** This job uses the 1.7B model for inference only (no TransformerLens hooks, no gradients). Should fit easily on 17GB. But if Job 1 is also running on the same GPU, they'll compete for VRAM. Run sequentially if needed.

---

## PRIORITY & SEQUENCING

```
Job 1 (1.7B targeted CMA-ES) ──────────────────────── [4-8 hours, GPU-bound]
                                                          │
Job 2 (coherence NaN fix) ─── [runs after Job 1, same GPU, 4-6 hours]
                                                          │
Job 3 (corpus prep) ────────── [inference only, can overlap with Job 2]
```

Job 1 is the main event. Everything else is secondary.

---

## SUCCESS CRITERIA

- [ ] 1.7B targeted CMA-ES reaches SR > 0.40 (vs 0.361 for blanket rank-8, 0.083 for rank-16)
- [ ] Phase transition observed (sudden SR jump, not gradual climb)
- [ ] Coherence run completes without NaN, SR > 0.30 with PPL < 1.05x baseline
- [ ] 1.7B base corpus generated and partially verified by Lean 4

**The big question this batch answers:** Does the ejection map from Ignis translate into targeted evolutionary success? If SR > 0.50 with 5-head targeting at 1.7B, we've cracked the scaling problem and the recipe is: decompose → target → evolve → self-corpus → 75% metacognition. At any scale.

---

## IF THINGS GO WRONG

**1.7B targeted CMA-ES plateaus below 0.30:** The head map may be incomplete. Add L21 and L24 to the target set. If still stuck, run Ignis decomposition on more traps (the current map used 10, expand to all 36).

**1.7B OOMs during CMA-ES:** The 1.7B model + LoRA + CMA-ES population may exceed 17GB. Mitigations:
- Reduce population from 20 to 12
- Use `torch.float16` throughout (not just model weights — optimizer state too)
- Gradient checkpointing if supported by the CMA-ES wrapper
- Reduce generation batch from 150 to 100

**Coherence NaN persists after guard:** The issue might be in the fitness aggregation, not the PPL computation. Check that the CMA-ES fitness vector doesn't contain NaN before the `.tell()` step. Replace any NaN fitness with -1e6.
