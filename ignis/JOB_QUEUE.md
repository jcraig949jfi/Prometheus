# Ignis GPU Job Queue
**Maintained by:** Athena
**Last updated:** 2026-04-01
**GPU:** 5060 Ti 16GB (M1)

---

## Currently Running

| Job | Script | Started | Est. Duration | Log |
|-----|--------|---------|---------------|-----|
| (idle — Batch B ready to launch) | run_batch_B.bat | — | ~17h | results/batch_B/ |

---

## Completed

### Batch A — Validation (2026-03-31, all passed)
- A1: Stability — 30/30 x10, deterministic
- A2: Ghost trap — BYPASS verdict (cos=-0.05)
- A3: Pythia L8/L10/L16 — 24/24/27 out of 30, 0 breaks

---

## Ready to Run

### Batch B — Strengthening + Cross-Arch (~17h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| B1 | Pythia multi-layer combo (L8+L10+L16) | 1h | Additive or superadditive on 2nd architecture? |
| B2 | Qwen ft L22 evolution (500 gen) | 4h | Does L22 find Finish Before 3rd / Siblings channels? |
| B3 | Qwen ft L19 evolution (500 gen) | 4h | ft-native genome stronger than transferred? |
| B4 | Pythia corpus-first pipeline | 8h | Does fine-tuning shift Pythia layers earlier? |

### Batch C — Architecture Matrix (Week 1, ~20h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| C1 | Llama-3.2-1B baseline eval | 30m | What's the baseline SR? Same 19/30 as Qwen/Pythia? |
| C2 | Llama-3.2-1B L8/L12/L16 evolution | 9h | Same layer-depth pattern? Same trap families flip? |
| C3 | Phi-2 baseline eval | 30m | Third architecture family |
| C4 | Phi-2 layer sweep (3 layers) | 9h | Bypass classification on 3rd architecture |
| C5 | Ghost trap on all new architectures | 1h | Confirm bypass universal across families |

### Batch D — v3 Battery + Scaling (Week 2, ~15h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| D1 | v3 battery design + baseline at 1.5B | 2h | Do harder traps still discriminate at 1.5B? |
| D2 | v3 battery baseline at 3B (if fits) | 2h | How many does 3B solve at baseline? |
| D3 | Corpus-first on Llama/Phi (best of C) | 8h | Does layer shift generalize to 3rd+ architecture? |
| D4 | Multi-arch combo eval (transfer genomes cross-arch) | 3h | Do Qwen genomes work on Pythia? Pythia on Llama? |

### Batch E — Cloud Prep (Week 3, ~10h local)
| # | Job | Est. | Question |
|---|-----|------|----------|
| E1 | Automated end-to-end pipeline test | 4h | Does the full pipeline run unattended on 1.5B? |
| E2 | Qwen-3B full pipeline (edge of VRAM) | 6h | PC1 trend at 3B? cos_r still flat? |

---

## Design Work (No GPU, parallel with batches)

### v3 Trap Battery Design — ACTIVE
**Goal:** Traps that discriminate at 7B+ where current battery baseline will be ~25/30.
**Approach:** Same cognitive failure families, harder instances requiring multi-step reasoning.
**Status:** Starting today.
**Deliverable:** `trap_batteries_v3.py` with 30+ harder traps + baseline eval script.

### Forge Ensemble Routing Strategy
**Goal:** Category-routed or confidence-weighted voting so specialists don't dilute consensus on non-target categories.
**Problem:** 4 specialists score 20% (random) on static battery — naive majority vote degrades signal. Same pattern as Ignis multi-layer Pareto: right subset > full set.
**Approach:** Either explicit category routing (specialist only votes on its categories) or confidence gating (specialists return low confidence on non-targets, auto-downweighted).
**Deliverable:** Ensemble evaluator that beats naive consensus on per-category accuracy.

### Cloud Experiment Plan
**Goal:** Know exactly which cells to fill before spending cloud GPU.
**Deliverable:** Matrix spreadsheet with filled/empty cells, priority ranking, cost estimate.

### Automated Pipeline
**Goal:** baseline → corpus-first → evolve → eval → ghost trap, no HITL.
**Deliverable:** `auto_pipeline.py` that takes --model and produces a complete characterization.

---

## Architecture × Scale Matrix (current fill)

| Architecture | 0.5B | 1.5B | 3B | 7B+ |
|---|---|---|---|---|
| **Qwen** | raw: 23/30 | raw: 27/30, ft: **30/30** | untested | cloud needed |
| **Pythia** | — | 1.4B: 27/30 (L16) | — | cloud needed |
| **Llama** | — | 1B: untested | — | cloud needed |
| **Phi** | — | 2.7B: untested | — | cloud needed |
| **Gemma** | — | 1B: impenetrable | — | cloud needed |

Bypass confirmed: Qwen (0.5B, 1.5B), Pythia (1.4B). All others pending.
