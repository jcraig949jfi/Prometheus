# Prometheus — Active Priorities

*Living document. Updated 2026-03-29. Feeds Metis briefs — keep current or briefs go stale.*

---

## IMMEDIATE (do next)

### 1. Stage D gen 150-200 — watch for ceiling
- Running on M1 GPU. Check terminal for `[eval]` lines.
- Gen 125: fitness 9.255, 17/30, 3 flips, zero breaks, margins still widening.
- If gen 150 shows no 4th flip: ceiling confirmed at 17/30. Next: layer sweep or multi-vector.
- If hung: switch to 20-gen burst workaround.

### 2. Noesis round 2 — launch when CPU frees
- Design complete (journal 2026-03-29): entropy compression, no bb_bonus, diminishing depth bonus.
- M2: integrated package (all fixes). M4: no-BB control. M5: depth forcing (min length 3).
- Waiting on M1 Noesis to finish or be killed to free CPU.

### 3. RLVF first cycle — capture baseline
- Design doc complete and Athena-reviewed (`docs/rlvf_integration.md`).
- Before Gen 0: capture BOTH behavioral AND geometric baselines in `agents/hephaestus/baselines/rhea_pre_rlvf.json`.
- Use mixed-difficulty curriculum (all 113 categories from start, weights shift over time).
- Ensemble evaluator at 0.734 weighted is the RLVF candidate.

---

## HIGH PRIORITY (this week)

### 4. Tier 3 battery design — HITL
- Tier 2 is solved (24 categories, ensemble at 0.734). Battery is the bottleneck again.
- Need narrative-complexity challenges: MUSR-style multi-paragraph evidence chains, BoardgameQA-style rule conflicts, FOLIO-style NL-to-FOL.
- Parametric generators can't produce these — needs human-designed templates.
- Titans proposed ~80 categories; ~20 unique computational primitives with massive overlap on top 4.

### 5. Ignis layer sweep
- Stage D confirms ceiling at 17/30 with single vector at L23/ε=3.0.
- Next experiment: L19, L21, L22 with corpus-trained model.
- Or: multi-vector injection (evolve at two layers simultaneously).
- The 13 impenetrable traps are the target.

### 6. SAE decomposition of Ignis vectors
- Train SAE on Qwen 2.5-3B residual stream using SAELens.
- Decode archived best_genome.pt through SAE → human-readable features.
- Transforms "we found something" into "here is what it is."

---

## MEDIUM PRIORITY (this month)

### 7. Semantic Scholar bulk dataset
- S2 Datasets API for local CS paper mirror. Zero rate limits.
- Eliminates API dependency for Eos paper scanning.

### 8. Scale gradient completion
- 7B Qwen2.5 cloud run (Lambda/RunPod A100, ~$25-40).
- Required to complete the Qwen 2.5 scale gradient.

### 9. RPH paper update
- Reframe around bypass finding + scale threshold.
- Add Stage D corpus-first results.
- Add SAE decomposition when available.

---

## COMPLETED (archive)

- [x] Qwen3-4B overnight run — archived, RPH eval complete (2026-03-24)
- [x] Prometheus repo — git init, GitHub push (2026-03-25)
- [x] Eos basic wiring — arxiv, GitHub, OpenAlex, web search working (2026-03-24)
- [x] Forge pipeline 89/89 Tier 1 coverage (2026-03-29)
- [x] Tier 2 battery — 24 categories, computation-first tools (2026-03-29)
- [x] Frame E/F/G forge prompts, difficulty-weighted scoring (2026-03-29)
- [x] Ensemble evaluator at 0.734 weighted (2026-03-29)
- [x] RLVF design doc — Athena-reviewed (2026-03-29)
- [x] Apollo mothballed — forge + Noesis replaced it (2026-03-29)
