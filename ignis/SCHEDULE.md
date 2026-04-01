# Ignis GPU Schedule — 3-Week Exploration Phase
**Maintained by:** Athena
**Created:** 2026-04-01
**Goal:** Fill the architecture × scale × bypass matrix. Card runs 24/7. Cloud-ready by week 3.

---

## VRAM Budget (5060 Ti, 16GB usable)

TransformerLens ≈ 2x model weight size. CMA-ES adds ~1-2GB overhead.

| Model | Params | Weights | TL Estimate | Fits? |
|---|---|---|---|---|
| Qwen 2.5-0.5B | 0.5B | ~1GB | ~3GB | Yes |
| Qwen 2.5-1.5B | 1.5B | ~3GB | ~7GB | Yes |
| Pythia-1.4B | 1.4B | ~5.6GB | ~11GB | Yes |
| **Llama-3.2-1B** | 1.2B | ~2.5GB | ~6GB | **Yes** |
| **Gemma-3-1B** | 1B | ~2GB | ~5GB | **Yes** |
| **Phi-2** | 2.7B | ~5.5GB | ~12GB | **Tight — test first** |
| Pythia-2.8B | 2.8B | ~11GB | ~16GB | **Edge — likely OOM with CMA-ES** |
| Qwen 2.5-3B | 3B | ~6GB | ~13GB | **Tight — test first** |
| Gemma-2-2B | 2B | ~4GB | ~9GB | Yes |

**Safe tier (< 12GB):** Qwen-0.5B, Qwen-1.5B, Pythia-1.4B, Llama-3.2-1B, Gemma-3-1B, Gemma-2-2B
**Edge tier (12-16GB):** Phi-2, Qwen-3B
**OOM tier:** Pythia-2.8B, anything 7B+

---

## Week 1: Architecture Sweep (Apr 1-7)

**Goal:** Fill 3+ architecture columns in the matrix. Confirm bypass is universal.

### Batch B — Running (started Apr 1, ~17h, finishes ~Apr 1 evening)
- B1: Pythia combo (1h)
- B2: Qwen ft L22 evolution (4h)
- B3: Qwen ft L19 evolution (4h)
- B4: Pythia corpus-first (8h)

### Batch C — Llama + Gemma (~22h, queue for Apr 2 morning)
| # | Job | Est. | Model | Question |
|---|-----|------|-------|----------|
| C1 | Llama-3.2-1B baseline eval | 30m | Llama-3.2-1B | Baseline SR? |
| C2 | Llama L8 evolution (300 gen) | 3h | Llama-3.2-1B | Early layer response (16-layer model, L8=50% depth) |
| C3 | Llama L12 evolution (300 gen) | 3h | Llama-3.2-1B | Late layer response (L12=75% depth) |
| C4 | Llama multi-layer combo | 30m | Llama-3.2-1B | Additivity on 3rd architecture |
| C5 | Llama ghost trap | 15m | Llama-3.2-1B | Bypass confirmed on Llama? |
| C6 | Gemma-2-2B baseline eval | 30m | Gemma-2-2B | Baseline SR? (Gemma-1B was "impenetrable" — is 2B different?) |
| C7 | Gemma-2-2B L10/L16/L22 evolution | 9h | Gemma-2-2B | 26-layer model, sweep early/mid/late |
| C8 | Gemma ghost trap | 15m | Gemma-2-2B | Bypass on 4th architecture |
| C9 | Cross-arch summary eval | 1h | All | Side-by-side comparison table |

### Batch D — Follow-up + Corpus-first Replication (~18h, queue ~Apr 3 evening)
| # | Job | Est. | Question |
|---|-----|------|----------|
| D1 | Llama corpus-first pipeline | 6h | Does fine-tuning shift Llama's productive layers earlier? |
| D2 | Llama ft multi-layer combo | 1h | Early-layer revolution on Llama? |
| D3 | Best non-Qwen cross-model genome transfer | 2h | Do Pythia genomes work on Llama? Qwen on Gemma? |
| D4 | Cross-arch trap-family overlap analysis | 1h | Same failure modes across all 4 architectures? |
| D5 | Phi-2 VRAM test + baseline | 30m | Does 2.7B fit? If yes, baseline SR |
| D6 | Phi-2 evolution (if fits) | 6h | 5th architecture if VRAM allows |

**End of Week 1 deliverable:** Architecture matrix with 4-5 columns filled. Bypass classification for each. Trap-family overlap analysis.

---

## Week 2: v3 Battery + Scaling Push (Apr 8-14)

**Goal:** Build harder traps. Push to edge of local VRAM. Cross-model genome transfer.

### Design Work (parallel with GPU, no card needed)
- v3 trap battery: 30+ harder traps for 7B+ headroom
- Automated pipeline script: `auto_pipeline.py`
- Cloud cost estimate and experiment plan

### Batch E — v3 Battery Validation (~8h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| E1 | v3 battery baseline on Qwen-1.5B | 1h | Do harder traps still discriminate? Target: <20/30 baseline |
| E2 | v3 battery baseline on Pythia-1.4B | 1h | Cross-arch baseline on harder traps |
| E3 | v3 battery + winning combo (Qwen ft) | 1h | Can steering still flip harder traps? |
| E4 | v3 battery across all local models | 4h | Full baseline matrix on harder traps |

### Batch F — Scaling Edge (~20h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| F1 | Qwen-3B VRAM test + baseline | 1h | Does 3B fit? Baseline SR on v2 and v3 batteries |
| F2 | Qwen-3B layer sweep (3 layers) | 9h | Where does suppression concentrate at 3B? |
| F3 | Qwen-3B ghost trap | 30m | PC1 trend at 3B? cos_r still flat? |
| F4 | Qwen-3B corpus-first (if fits) | 8h | Does the recipe work at 3B? |
| F5 | Gemma-2-2B corpus-first | 6h | Corpus-first on non-Qwen 2B+ model |

### Batch G — Genome Transfer Matrix (~6h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| G1 | Qwen genomes → Pythia | 1h | Cross-architecture transfer (same dim models) |
| G2 | Pythia genomes → Llama | 1h | Transfer across 3 families |
| G3 | Best genome from each arch → all others | 4h | Universal steering vector? Or arch-specific? |

**End of Week 2 deliverable:** v3 battery validated. 3B data point. Cross-architecture genome transfer results. Automated pipeline draft.

---

## Week 3: Cloud Prep + Final Local Runs (Apr 15-21)

**Goal:** Everything ready for first cloud experiment. Local matrix fully filled.

### Batch H — Pipeline Automation (~10h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| H1 | auto_pipeline.py test on Qwen-1.5B | 4h | Full unattended run: baseline → ft → evolve → eval → ghost |
| H2 | auto_pipeline.py test on Llama-1B | 3h | Does pipeline generalize? |
| H3 | auto_pipeline.py test on Pythia-1.4B | 3h | Third architecture, unattended |

### Batch I — Gap-Filling (~15h)
Whatever cells in the matrix are still empty. Likely:
- Any architecture that underperformed (re-runs with different hyperparams)
- Corpus-first on remaining architectures
- v3 battery evolution experiments
- LoRA experiments if bypass dominance holds everywhere (the pivot toward circuit discovery)

### Cloud Experiment Plan (document, no GPU)
| Priority | Experiment | Cloud GPU | Est. Cost | Question |
|---|---|---|---|---|
| 1 | Qwen-7B full pipeline (v2 + v3 battery) | A100 40GB | ~$5-10 | PC1 at 7B? cos_r? Bypass still? |
| 2 | Llama-3.1-8B full pipeline | A100 40GB | ~$5-10 | Cross-arch at 7B+ scale |
| 3 | Qwen-7B SAE decomposition | A100 40GB | ~$10-20 | Can interpretability find what CMA-ES can't? |
| 4 | Pythia-6.9B evolution | A100 40GB | ~$5-10 | Within-family scaling (1.4B → 6.9B) |

**End of Week 3 deliverable:** Automated pipeline tested on 3 architectures. Cloud experiment plan with cost estimates. Full local matrix. Ready to spend cloud GPU with clear hypotheses.

---

## The Matrix We're Building

By end of week 3, we want every local cell filled:

| | Qwen | Pythia | Llama | Gemma | Phi |
|---|---|---|---|---|---|
| **Baseline SR** | 0.5B: ✓, 1.5B: ✓ | 1.4B: ✓ | 1B: W1 | 2B: W1 | 2.7B: W1 |
| **Best single-layer** | 0.5B: ✓, 1.5B: ✓ | 1.4B: ✓ | 1B: W1 | 2B: W1 | 2.7B: W1 |
| **Multi-layer combo** | 1.5B: ✓ | 1.4B: B1 | 1B: W1 | 2B: W1 | 2.7B: W1 |
| **Bypass classification** | 0.5B: ✓, 1.5B: ✓ | 1.4B: ✓ | 1B: W1 | 2B: W1 | 2.7B: W1 |
| **Corpus-first** | 1.5B: ✓ | 1.4B: B4 | 1B: W1 | 2B: W2 | 2.7B: W2 |
| **Corpus-first combo** | 1.5B: ✓ | 1.4B: W1 | 1B: W1 | 2B: W2 | — |
| **v3 battery** | 1.5B: W2 | 1.4B: W2 | 1B: W2 | 2B: W2 | W2 |
| **3B+ scale** | 3B: W2 | — | 3B: W2 | — | — |
| **Cross-genome transfer** | — | W2 | W2 | W2 | — |

✓ = done, B# = in Batch B, W# = which week

---

## Principles

1. **Card never idles.** Next batch script is written before current batch finishes.
2. **Each batch informs the next.** If C reveals Gemma is impenetrable again, we skip Gemma in D and fill with something else.
3. **Design work parallels GPU work.** v3 battery, pipeline automation, and cloud planning happen while batches run.
4. **Kill/skip sentinels keep us agile.** If a 6h evolution is clearly plateaued at gen 100, kill it and move on.
5. **Cloud GPU is expensive. Know exactly what to run before spending it.**
