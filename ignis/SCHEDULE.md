# Ignis GPU Schedule — Local Exploration Phase
**Maintained by:** Athena
**Last updated:** 2026-04-03
**Goal:** Fill the architecture × scale × bypass matrix. Both cards run 24/7. Cloud-ready by Apr 6.

---

## Active Machines

| Machine | GPU | Status | Current Job |
|---|---|---|---|
| **M1** | 5060 Ti 16GB | Running Batch E | Cross-arch transfer + Qwen-0.5B |
| **M2** | 5060 Ti 16GB | Running Phi-2 sweep | ~63% through P2 (L12 evolution) |

---

## Queued Chains (autonomous, no HITL needed)

### M1: `run_M1_3day_chain.bat` (~30h, starts after Batch E)

| Phase | Est. | What | Key Question |
|---|---|---|---|
| P1a | 30m | Transfer raw L4/L8/L12 genomes to Llama ft model | Do genomes transfer on Llama like they did on Qwen? |
| P1b | 3h | Evolve L4 on Llama ft model | ft-native genome vs transferred |
| P1c | 5m | Ghost trap on Llama ft | Does corpus-first change mechanism? |
| P2a | 5m | Qwen ft v3 baseline (ft model) | How does ft model score on harder traps? |
| P2c | 5m | Llama ft v3 baseline | Same |
| P3 | 8h | Pythia corpus-first (fixed loop_closure) | Does fine-tuning shift Pythia's layers earlier? |
| P3b-d | 1h | Pythia ft transfer + ghost + v3 (if P3 succeeds) | Full ft characterization |
| P4 | 6h | Qwen-0.5B corpus-first | Small-scale ft cell |
| P4b | 30m | Qwen-0.5B ft transfer (if P4 succeeds) | |
| P5 | 8h | Llama corpus-first retry (clean run with fix) | Replaces crashed D1 |
| P5b | 30m | Llama ft2 transfer (if P5 succeeds) | |

### M2: `run_M2_after_phi2.bat` (~16h, starts after Phi-2 finishes)

| Phase | Est. | What | Key Question |
|---|---|---|---|
| M2a | 9h | Gemma-3-1B L10/L16/L22 evolution | Different Gemma gen — still impenetrable? |
| M2b | 2m | Gemma-3-1B v3 baseline | |
| M2c | 5m | Gemma-3 ghost trap | |
| M2d | 3h | Pythia L4 evolution (early layer gap) | Does 17% depth work on Pythia? |
| M2e | 1h | Pythia 4-layer combo (L4+L8+L10+L16) | Best Pythia result possible? |

---

## Completed Batches

| Batch | Machine | Date | Key Results |
|---|---|---|---|
| A: Validation | M1 | Mar 31 | 30/30 x10 stable, BYPASS confirmed, Pythia 27/30 |
| B: Strengthening | M1 | Apr 1 | Pythia combo 29/30, Qwen ft L22 found Siblings, Pythia cf FAILED |
| C: Gemma sweep | M1 | Apr 1-2 | Gemma-2-2B impenetrable (zero flips all 3 layers) |
| C: Llama sweep | M1 | Apr 2 | Llama 29/30, bypass, L8 margins +49, v3 baseline 25/30 |
| D: Fallback | M1 | Apr 2 | Llama L4=L8=L12 (all 29/30), Qwen ft combo still 30/30 |
| E: Cross-arch | M1 | Apr 3 | Running (Pythia↔Llama transfer + Qwen-0.5B) |
| Phi-2 | M2 | Apr 2-3 | Running (~63% done) |

---

## Bugs Fixed

| Bug | Impact | Fix | Date |
|---|---|---|---|
| BPE token collision (11 vs 10) | 3 traps reading 0.0 | Parity phrasings | Mar 31 |
| stability_test.py hardcoded genomes | Baseline fails on non-Qwen | M2 Athena fixed | Apr 2 |
| loop_closure.py missing GPT-NeoX path | Pythia corpus-first fails | Added gpt_neox.layers | Apr 3 |
| loop_closure.py Unicode Δ on Windows | Llama corpus-first rc=1 | Replace with 'Delta' | Apr 3 |

**Note:** Llama D1 corpus-first actually SUCCEEDED — the ft_model was saved before the Unicode crash. P1 in the M1 chain uses this existing model directly.

---

## Architecture × Scale Matrix (current fill)

| | Qwen 0.5B | Qwen 1.5B | Pythia 1.4B | Llama 1B | Gemma-2 2B | Gemma-3 1B | Phi 2.7B |
|---|---|---|---|---|---|---|---|
| **v2 Baseline** | ✓ (prior) | ✓ 14/30 | ✓ 19/30 | ✓ 21/30 | ✓ 21/30 | M2 chain | M2 running |
| **Best steered** | ✓ 23/30 | ✓ **30/30** (ft) | ✓ **29/30** | ✓ **29/30** | ✓ 21/30 | M2 chain | M2 running |
| **Bypass?** | E5 running | ✓ Yes | ✓ Yes | ✓ Yes | ✓ Yes (no flips) | M2 chain | M2 running |
| **Corpus-first** | M1 P4 | ✓ 30/30 | M1 P3 | M1 P1/P5 | — | — | — |
| **v3 Baseline** | E3 running | ✓ 16/30 | ✓ 19/30 | ✓ 25/30 | — | M2 chain | — |
| **Cross-arch transfer** | — | — | E1/E2 running | E1/E2 running | — | — | — |
| **Best layer depth** | — | Early (ft) | Late (67%) | **All (25-75%)** | — | — | — |

✓ = done, M1/M2 = in chain, E# = in current batch

---

## What Changes After Local Phase

By ~Apr 6, both chains finish. The local matrix has:
- 5-7 architecture columns filled (Qwen, Pythia, Llama, Gemma-2, Gemma-3, Phi, Qwen-0.5B)
- Bypass confirmed on 3+ architectures
- Cross-architecture genome transfer tested
- Corpus-first on 2-4 models (Qwen confirmed, Pythia/Llama pending fix validation)
- v3 battery calibrated across all models

**Then: cloud transition.** ~$50-75 for first round:
1. Qwen-7B full pipeline (A100, ~$8) — bypass at 7B? PC1 trend?
2. Llama-3.1-8B full pipeline (A100, ~$8) — cross-arch at scale
3. Qwen-7B SAE decomposition (A100, ~$10) — can interpretability find native circuits?
4. Qwen-7B corpus-first + steering (A100, ~$15) — does the 30/30 recipe scale?

---

## VRAM Budget (5060 Ti, 16GB)

| Model | Fits? | Notes |
|---|---|---|
| Qwen-0.5B | Yes (~3GB) | |
| Qwen-1.5B | Yes (~7GB) | |
| Pythia-1.4B | Yes (~11GB) | |
| Llama-3.2-1B | Yes (~6GB) | |
| Gemma-3-1B | Yes (~5GB) | |
| Gemma-2-2B | Yes (~9GB) | Impenetrable |
| Phi-2 (2.7B) | Tight (~12-14GB) | Popsize 24, confirmed fits |
| Qwen-3B | Tight (~13GB) | Untested |
| Anything 7B+ | No | Cloud needed |
