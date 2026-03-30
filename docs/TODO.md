# Prometheus — Master TODO List

*Living document. Updated 2026-03-29. For priority ordering, see [PRIORITIES.md](PRIORITIES.md).*

---

## Ignis (Reasoning Circuit Discovery)

### Stage D — Corpus-First Evolution (RUNNING)
- [x] Stage D gen 0-100: fitness 6.87→8.61, 17/30, 3 Overtake flips, zero breaks <!-- 2026-03-28 -->
- [x] Stage D gen 100-125: fitness 9.255, margins widening, no 4th flip <!-- 2026-03-29 -->
- [ ] Stage D gen 125-200 — **RUNNING ON M1 GPU**
- [ ] If no 4th flip by gen 200: ceiling confirmed, design layer sweep
- [ ] If hung: 20-gen burst workaround

### Layer Sweep (next after Stage D)
- [ ] Test L19, L21, L22 with corpus-trained model
- [ ] Or: multi-vector injection (two layers simultaneously)
- [ ] Target: the 13 impenetrable traps

### SAE Decomposition
- [ ] Install SAELens, train on Qwen 2.5-3B residual stream
- [ ] Decode best_genome.pt through SAE → human-readable features
- [ ] Compare to supervised probe directions from paper 2603.16335v1

### Scale Gradient
- [ ] 7B Qwen2.5 cloud run (Lambda/RunPod A100, ~$25-40)
- [ ] Update scale gradient table, determine if 14B warranted

### RPH Paper
- [ ] Reframe around bypass finding + scale threshold
- [ ] Add Stage D corpus-first results when gen 200 complete
- [ ] Add SAE decomposition when available

---

## Forge Pipeline (Hephaestus)

### COMPLETED — Session 2026-03-29
- [x] 89/89 Tier 1 coverage (gap closers for causal_intervention, tom_perspective_shift) <!-- 2026-03-29 -->
- [x] Tier 2 battery: 24 categories requiring computation <!-- 2026-03-29 -->
- [x] Difficulty-weighted scoring in test_harness.py <!-- 2026-03-29 -->
- [x] Frame E/F/G forge prompts in prompts.py <!-- 2026-03-29 -->
- [x] Deep reasoning engine: 74.8% on hard categories <!-- 2026-03-29 -->
- [x] Ensemble evaluator: 0.734 weighted, library #1 <!-- 2026-03-29 -->
- [x] RLVF integration design doc (Athena-reviewed) <!-- 2026-03-29 -->
- [x] Computation-first architecture validated and default <!-- 2026-03-29 -->

### Remaining
- [ ] Tier 3 battery design (HITL — narrative complexity, MUSR/BoardgameQA/FOLIO-style)
- [ ] Harden remaining Tier 2 gaps (6 categories still at 0% for best tool)
- [ ] RLVF Phase 1: capture combined baseline on Rhea

---

## Noesis (Tensor Exploration)

### Round 1 — COMPLETE
- [x] M1: 266K chains, strategy succession finding <!-- 2026-03-28 -->
- [x] M2: scoring fix confirmed dominant effect (+0.055) <!-- 2026-03-28 -->
- [x] M3: BB monoculture identified (97.2% ising, artifact of bb_bonus) <!-- 2026-03-28 -->
- [x] M5: 0.8288 quality with length-5 chains <!-- 2026-03-28 -->

### Round 2 — DESIGNED, WAITING FOR CPU
- [ ] M2: integrated package (entropy compression + diminishing depth + no bb_bonus + promoted BBs)
- [ ] M4: no-BB control (identical to M2 minus building blocks)
- [ ] M5: depth forcing (minimum chain length 3)
- [ ] Kill M1 Noesis when done to free CPU

---

## Intelligence Pipeline (Eos → Metis → Hermes)

- [x] PRIORITIES.md and TODO.md updated (fixes stale Metis briefs) <!-- 2026-03-29 -->
- [ ] Metis staleness detection (detect when brief hasn't changed in 3+ cycles)
- [ ] Eos semantic dedup (cluster same-story items across sources)
- [ ] Hermes forge section update (reflect Tier 2, ensemble, computation-first)
- [ ] HTML email formatting for Gmail readability
- [ ] Structured logging for both pipelines

### Scanners — To Wire
- [ ] Semantic Scholar bulk dataset (local mirror, zero rate limits)
- [ ] Cerebras for deep analysis (Qwen 3-235B FREE)
- [ ] Serper for targeted web searches (2500 lifetime budget)

---

## Infrastructure

- [ ] Archive old repos (bitfrost-mech, ArcanumInfinity) as read-only
- [ ] Helios (GPU scheduler) — auto-queue experiments
- [ ] Evaluate Claude Code Agent SDK for persistent research agents
