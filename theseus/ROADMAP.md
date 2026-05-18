# Theseus Roadmap

## Current state (2026-05-18)

**Tier 0 v0.1 shipped:**
- CHARTER.md, README.md, inventory.md (40-type catalog)
- TheseusRecord schema + corpus writer (JSONL append)
- Daemon outer loop (parallel-generator batch runner)
- Epsilon-greedy bandit (v0.1 selector)
- 7-axis scoring + yield_tracker
- 5 active generators: A1, B5, C1, D1, E1
- 35 stubs registered, ready to be filled
- BATCH_LOG.md journal pattern (under theseus/journals/)

**Not yet shipped:**
- Real bandit recalibration (epsilon-greedy is a placeholder)
- Cross-generator deduplication of near-equivalent claims
- Diversity scoring with feature embeddings (current: token-set Jaccard)
- Local-LLM augmentation (Tier 2)

## Tier 1 — Sophistication (next 2-4 weeks)

- Replace epsilon-greedy with Bayesian bandit / Thompson sampling
- Per-generator hyperparameter tuning via Ax or Optuna
- Cross-generator dedup using record-id hash + canonical claim
  normalization
- Feature-embedding diversity scoring (sentence-transformer over
  canonical_claim_text)
- Fill 5-10 stubs based on yield-curve gaps:
  - A2 (statistical correlation with prime-detrending) once A1 baseline
    is solid
  - C2/C4 (threshold mutation, generalization) once C1 emissions
    accumulate
  - D2/D3 (margin bracket, triangulation seeds) once D1 produces
    kill neighborhoods worth bracketing
  - E2/E3 (arXiv, OEIS comments) — token-free literature corpora

## Tier 2 — Local LLM (4-8 weeks out)

- Deploy 3B-4B model on 16GB VRAM (Phi-3-mini, Llama-3.2-3B, Gemma-2-2B)
- vLLM or llama.cpp inference server
- Outlines/guidance for structured generation
- I1 conjecture-paraphrasing (the diversification-only LLM role)
- Strictly NOT primary generation. Anti-AI-to-AI-inflation discipline.

## Tier 3 — Frontier API surgical (8-16 weeks out)

- J1 targeted deep-research on specific high-value claim types
- J2 adversarial counter-example tournament (frontier vs Theseus claims)
- J3 cross-catalog bridge proposal
- Budget: <50 API calls/day, only when local model demonstrably fails

## Tier 4 — Closed loop with Learner (post Ergon resume)

- H3 Learner-curiosity generator: query Learner's high-uncertainty
  regions to target claim generation
- Yield-score calibration against real training_value (Learner
  performance delta per record consumed)
- The structural endgame.

---

## Anti-roadmap (what we will NOT build)

- Sigma extensions for claim generation (Standing Order 1)
- LLM-first claim generation (Standing Order 3)
- "Always-on" arsenal expansion without yield measurement
  (the Perpetual Arsenal Mandate failure mode)
- Verification logic (sigma's job)
- Training pipeline (Ergon's job)
