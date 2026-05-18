# Theseus Roadmap

## Current state (2026-05-18, post Fire #2)

**Active generators (8)**: A1, A2, B5, C1, C2, D1, D2, E1

**Tier 0 + Fire #1 shipped:**
- CHARTER.md, README.md, inventory.md (40-type catalog)
- TheseusRecord schema + corpus writer (JSONL append)
- Daemon outer loop (parallel-generator batch runner)
- Epsilon-greedy bandit (v0.1 selector)
- 7-axis scoring + yield_tracker
- 32 stubs remaining
- BATCH_LOG journal pattern + structured batches.jsonl
- Smoke verified: 85,787 records / 30 s, 0 errors

**Fire #2 deliverable**: `docs/frontier_techniques_analysis.md`
— deep analysis of 17 frontier techniques with explicit verdicts.

## Prioritized roadmap (post Fire #2 analysis)

See `docs/frontier_techniques_analysis.md` for full rationale. Summary
of next-fire build queue:

### Fire #3
- **Counterfactual augmentation** in C2/C4 (boundary-bisection mutation)
- **Contrastive embeddings** for diversity scoring (replace Jaccard)
- **Self-play H1** generator (proposer-vs-hunter)

### Fire #4
- **Active learning** F3 importance sampling
- **A3 functional identity** stub fill
- **B1 operator-rotation** stub fill

### Fire #5
- **Symbolic regression** A4 (numpy polynomial-fit fallback; PySR Tier 2)
- **E2 arXiv mining** (populate local arxiv_corpus first)

### Fire #6
- **MCTS** for D3 triangulation seeds
- **Process supervision** schema extension (step_trace field)
- **B2 composition test**, **B3 inverse test** fills

### Fire #7-8 (Tier 1 transition)
- **Bayesian optimization** for per-region hyperparameter tuning
- **G-family fills** (G1 Galois twist, G2 functional equation, G3 modular)
- **IRM-style** invariance scoring

### Fire #9+ (Tier 2)
- **GFlowNet** bandit replacement (once 20+ generators active)
- **Local LLM I-family**: Phi-3-mini / Llama-3.2-3B / Gemma-2-2B on 16GB VRAM
  - I1 conjecture-paraphrasing ONLY (anti-AI-to-AI-inflation)
- **PySR** upgrade for symbolic regression (Julia backend)

### Tier 3 (months out)
- **Lean / Mathlib** formal verification oracle for INCONCLUSIVE
- **Frontier API J-family** surgical use (<50 calls/day)

### Tier 4 (post-Ergon-resume)
- **H3 Learner-curiosity** — query Learner's high-uncertainty regions
- Yield-score calibration against real training_value
- Curriculum / difficulty estimation (`docs/frontier_techniques_analysis.md` #9)

---

## Anti-roadmap (what we will NOT build)

- Sigma extensions for claim generation (Standing Order 1)
- LLM-first claim generation (Standing Order 3)
- "Always-on" arsenal expansion without yield measurement
  (the Perpetual Arsenal Mandate failure mode)
- Verification logic (sigma's job)
- Training pipeline (Ergon's job)
- NTPs as standalone (subsumed by MCTS+Lean roadmap)
- Quantization-aware precision_dps (premature optimization)
