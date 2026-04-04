# Ignis GPU Job Queue
**Maintained by:** Athena (Science Advisor)
**Last updated:** 2026-04-03
**GPUs:** 5060 Ti 16GB (M1), 5060 Ti 16GB (M2)

---

## Currently Running

### M1 — Batch F: Qwen 1.5B v3 Evolution Pipeline (~11h)
- **Script:** `run_M1_overnight_v3.bat`
- **Started:** 2026-04-03 ~20:22
- **Results:** `results/batch_F_v3/`

| Step | Job | Status |
|------|-----|--------|
| F1 | v3 baseline | DONE |
| F2 | L10 v3 evolution (500 gen) | RUNNING |
| F3 | L23 v3 evolution (500 gen) | queued |
| F4 | Multilayer combo L10+L23 on v3 | queued |
| F5 | Ghost trap v3 | queued |

### M2 — Batch F-M2: Phi-2 v3 Evolution Pipeline (~13h)
- **Script:** `run_M2_overnight_v3.bat`
- **Structure:** F1–F5 same as M1, L12 and L20 instead
- **Results:** `results/batch_F_v3_phi2/`

---

## Completed

### Batch A — Validation (2026-03-31)
- A1: Stability — 30/30 x10, deterministic
- A2: Ghost trap — BYPASS verdict (cos=-0.05)
- A3: Pythia L8/L10/L16 — 24/24/27 out of 30, 0 breaks

### Batch B — Strengthening + Cross-Arch (2026-04-01)
- Pythia combo, Qwen ft L22/L19

### Batch C — Llama Sweep (2026-04-02)
- L8 (28/30), L12 (29/30)

### Batch D — Llama Corpus-First + Fallback (2026-04-02)
- Llama corpus-first, fallback experiments

### Batch E — Cross-Arch Transfer + v3 Baselines (2026-04-03)
- Cross-arch transfer (DEAD), Qwen 0.5B (28/30), v3 baselines

### Batch Phi-2 (2026-04-03, M2)
- Full Phi-2 sweep — 24/30 baseline, 30/30 steered, bypass confirmed, 0 breaks

---

## Ready to Run

### Batch G — Generation Validation + Risk 2 (~4h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| G1 | Generation check: Qwen 1.5B v2 winning combo | 45m | Do logit flips become text changes? |
| G2 | Generation check: Phi-2 L12+L20 v2 combo | 45m | Same question, different architecture |
| G3 | Generation check: Llama L8 v2 | 45m | Third architecture |
| G4 | Generation check on v3 best combo (from Batch F) | 45m | v3 flips → text changes? |

### Batch H — Corpus-First on Non-Qwen (~16h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| H1 | Pythia corpus-first pipeline (full) | 8h | Does fine-tuning shift Pythia layers earlier? |
| H2 | Llama corpus-first pipeline (full) | 8h | Same for Llama? |

### Batch I — Automated Pipeline (~8h)
| # | Job | Est. | Question |
|---|-----|------|----------|
| I1 | Build auto_pipeline.py (baseline → evolve → combo → ghost) | 4h dev | Can we characterize a model unattended? |
| I2 | Test auto_pipeline on Qwen 1.5B (validation run) | 4h | End-to-end without HITL? |

### Batch J — Cloud Prep (Week 2)
| # | Job | Est. | Question |
|---|-----|------|----------|
| J1 | v3 battery steered on remaining architectures | 8h | Fill v3-steered row for Pythia, Llama |
| J2 | Qwen-3B if fits in VRAM (edge case) | 6h | Scale test at 3B |
| J3 | Package results for cloud: matrix, scripts, battery | 2h | Ready to spend cloud GPU? |

---

## Design Work (No GPU, parallel with batches)

### Generation Validation Script
**Goal:** Must exist before Batch G.
**Check:** Does `generation_check.py` handle v3 battery and multi-architecture?

### Automated Pipeline
**Goal:** `auto_pipeline.py` that chains baseline → evolve → combo → ghost for any model.
**Deliverable:** `auto_pipeline.py` with `--model` flag producing complete characterization.

### Cloud Experiment Plan
**Goal:** Know exactly which cells to fill before spending cloud GPU.
**Deliverable:** Matrix with filled/empty cells, priority ranking, cost estimate.

---

## Architecture × Scale Matrix (current fill)

| | Qwen 0.5B | Qwen 1.5B | Pythia 1.4B | Llama 1B | Gemma 2B | Phi-2 2.7B |
|---|---|---|---|---|---|---|
| v2 Baseline | 23/30 | ~18/30 | ~19/30 | 21/30 | ~21/30 | 24/30 |
| v2 Best steered | 28/30 | 30/30 (ft) | 29/30 | 29/30 | 21/30 | 30/30 |
| v3 Baseline | 17/30 | 16/30 | 19/30 | 25/30 | — | 19/30 |
| v3 Steered | — | **RUNNING** | — | — | — | **RUNNING** |
| Bypass? | Yes | Yes | Yes | Yes | 0 flips | Yes |
