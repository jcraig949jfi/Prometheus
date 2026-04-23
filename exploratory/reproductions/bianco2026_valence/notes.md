# Bianco & Shiller 2026 — Beyond Behavioural Trade-Offs
## Mechanistic Tracing of Pain-Pleasure Decisions in an LLM

**arxiv:** 2602.19159
**Authors:** Francesca Bianco, Derek Shiller
**Code:** Not yet public (contact: francesca.bianco.lain@gmail.com)

---

## Why This Paper Matters to Us

This is our RPH twin. They're testing the same core hypothesis we are — that **linear directions in activation space causally drive behavioral regime shifts** — just in a different domain (valence/pain-pleasure vs reasoning/heuristic bypass). Their methodology is exactly what we need for Ignis Layer 3 (SAE mediation / causal interventions).

## Their Setup vs Ours

| Aspect | Bianco 2026 | Prometheus/Ignis |
|--------|-------------|------------------|
| **Model** | Gemma-2-9B-it (42 layers) | Qwen2.5-0.5B to 4B (24-36 layers) |
| **Tooling** | TransformerLens (same!) | TransformerLens (same!) |
| **Direction** | Data-derived: μ_pleasure - μ_pain | CMA-ES evolved steering vectors |
| **Intervention** | h ← h + εv̂ (steering) | h_L' = h_L + α·v (same!) |
| **Readout** | logit2 − logit3 margin | Multi-trap fitness score |
| **Probing** | Layer-wise logistic/ridge regression | Ghost trap cosine similarity |
| **Causal test** | Steering + swap/patching + ablation | Falsification pass (noise, ortho, flip) |
| **Dose-response** | ε grid from -200 to +200 | Not yet implemented |

## Key Methods to Adapt

### 1. Layer-wise Linear Probing
They probe EVERY (layer, position, stream) combination with logistic regression.
Stream families: resid_pre, attn_out, mlp_out, resid_post.
**We should do this:** probe our trap prompts across all layers/streams in Qwen 1.5B/3B/4B.

### 2. Dose-Response ε Sweep
They sweep ε from -200 to +200 and measure margin shift.
**Critical for us:** if our steering vectors show phase-transition-like jumps at specific ε values, that's precipitation. Smooth linear response = bypass.

### 3. Head-Level Patching
They do per-head interventions using `attn.hook_z`.
**We should do this:** find which attention heads mediate our steering effect.

### 4. Directional Ablation
h ← h − (h·v̂)v̂ — remove only the component along the steering direction.
**This is the necessity test we're missing.** If ablating the direction kills the fitness improvement, the vector is causal. If fitness survives, it's bypass.

### 5. BoW Lexical Baseline
They compare probe results against a bag-of-words baseline to rule out surface-level confounds.
**We need this:** compare our trap probes against a lexical baseline.

## Adaptation Plan

### Phase 1: Direct Reproduction (Gemma-2-2B)
- Load Gemma-2-2B via TransformerLens (fits 17GB card)
- Replicate their pain/pleasure task
- Run probing + steering + ablation
- Verify we get similar results at smaller scale

### Phase 2: Cross-Domain Transfer (Qwen + Our Traps)
- Use our existing trap prompts instead of pain/pleasure
- Apply their full probing pipeline to Qwen 1.5B
- Compare: do reasoning traps show the same layer-wise separability as valence?
- Run dose-response ε sweep on our best steering vectors
- Run directional ablation on our best vectors

### Phase 3: Synthesis
- If reasoning and valence directions share geometric properties → strong RPH support
- If they differ fundamentally → characterize the difference (this is a paper)
- Feed findings to Titan Council for interpretation

## VRAM Requirements
- Gemma-2-2B: ~4GB weights, ~8GB with TransformerLens → FITS
- Gemma-2-9B: ~18GB weights, ~36GB with TL → DOES NOT FIT
- All Qwen models already cached and tested

## What We Don't Have Yet
- Their code (not published)
- But their methods section is detailed enough to reproduce from scratch
- TransformerLens hooks are identical to what we already use in Ignis
