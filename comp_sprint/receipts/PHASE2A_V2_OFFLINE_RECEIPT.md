# Phase 2A (v2) Offline Baseline Receipt — Qualified Monotonic Engine

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11`  
**Sealed Manifest SHA-256:** `9c02ddcaa5a1610801fe05f8307f221079923fb3bce86b230c8d99cc4f4322e7`  
**Rows Verified:** `600 / 600` (`50 tasks × 4 arms × 3 paired seeds`, `100%` exact truth-table verified, `verify_and_reduce` PASS)  
**Wall Time:** `8.63s` | **API Spend:** `$0.00` | **CPU Cost:** `$0.00009` (`6.57s` CPU, `85` SAT calls in sleep/sham compression)

---

## 1. Per-Suite Results (Mean of Per-Task Medians Across 3 Paired Seeds, Lower = Better)

| Suite | Split | `A0_BASE` | `A1_ABC_XAG` | `A3_ZERO_LLM` (12 dev-mined) | `A5_SHAM` (12 optimal random) | `A3 − BASE` | `A3 − SHAM` |
|---|---|---:|---:|---:|---:|---:|---:|
| `dev_structured` | dev | 11.8 | 14.1 | 11.7 | 11.7 | −0.1 | 0.0 |
| `dev_proc_shared` | dev | 15.9 | 19.4 | 15.6 | 15.6 | −0.3 | 0.0 |
| `holdout_structured` | **untouched holdout** | 17.4 | 21.9 | 17.2 | 17.3 | −0.2 | −0.1 |
| `holdout_proc_shared` | **untouched holdout** | 16.5 | 16.8 | 16.5 | 16.2 | 0.0 | +0.3 |
| `holdout_proc_rand` | **untouched holdout** | 35.1 | 41.4 | 34.8 | 34.9 | −0.3 | −0.1 |

---

## 2. Scientific Readout (Zero-Cost Offline Baseline Complete)

1. **Zero regressions across all 600 runs:** Monotonicity holds strictly on every task and seed (`A3 <= A0_BASE` and `A5_SHAM <= A0_BASE` everywhere).
2. **`A0_BASE` (v2) beats Berkeley `ABC 1.01` (AIG+XOR folding) on all 5 suites:** by `0.3` to `6.3` gates/task (native XAG Positive/Negative Davio + shared strash vs ABC's AIG-native `resyn2; dc2`).
3. **Clean null for naive zero-LLM bottom-up mining (`A3_ZERO_LLM ≈ A5_SHAM`):**
   - `A3_ZERO_LLM` is statistically indistinguishable from size-matched optimal `A5_SHAM` on every single suite (`Δ = 0.0` on dev, `−0.1` on `holdout_structured`, `+0.3` worse than SHAM on `holdout_proc_shared`).
   - **Why (contrast with Dev Planted-Positive):** Our Dev Planted-Positive check (`PHASE2A_INSTRUMENT_QUALIFIED.md`) proved that the exact same synthesizer drops `dev_structured` by **`−7` gates** (`119 → 112`, e.g., `popcount5` `17 → 12`) with **just 3 state-compressing multi-output macros** (`HA, FA, CAS`), while `SHAM` got `0` gain.
   - Pure bottom-up cut-mining over `A0_BASE`'s own Davio DAGs extracts local Davio fragments rather than **state-compressing multi-output functional abstractions** (`|image(W')| < |image(W)|`).

---

## 3. Ready for Step 3 — LLM Proposer Arms (`A2 PRIOR-ONLY`, `A4 MG-UNPLUGGED`, `A6 SHADOW-NAKED`)

The offline baseline cleanly isolates the exact hypotheses for Step 3:
- **Claim 1 (`A2 PRIOR-ONLY` vs `A0_BASE` / `A1_ABC_XAG` / `A5_SHAM`):** Can a frontier model given *only* the XAG spec (zero tasks) crystallize reusable multi-output abstractions that beat all offline baselines with **LLM OFF at holdout eval**?
- **Claim 2 (`A4 MG-UNPLUGGED` vs `A2 PRIOR-ONLY`):** Does inspecting **dev-split traces/circuits** (`dev_structured` + `dev_proc_shared`, holdout untouched) enable discovering abstractions that beat `A2 PRIOR-ONLY` on the untouched holdout strata?
- **Amortization (`A6 SHADOW-NAKED`):** Exact break-even curve `N* = F / (v_L − v_M)` including all failed LLM proposals in `F`.
