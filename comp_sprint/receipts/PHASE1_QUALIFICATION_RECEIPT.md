# Phase 1 Qualification & Non-Saturation Receipt — Track `3B-Boolean`

**Date:** 2026-11-22  
**Branch:** `reset/verified-composition-2026-11`  
**Sealed Benchmark Manifest SHA-256:** `9c02ddcaa5a1610801fe05f8307f221079923fb3bce86b230c8d99cc4f4322e7`  
**Industry Baseline Binary:** `UC Berkeley, ABC 1.01` (compiled locally from `github.com/berkeley-abc/abc`, recipe: `strash; dc2; resyn2; dc2; resyn2; dc2; strash` with sound exact AIG→XAG XOR folding)  
**Test Suite:** `9/9` passed (`pytest comp_sprint/tests`), `67/67` passed (`rso/adversary` + `rso/completeness`, untouched)

---

## 1. Per-Suite Qualification Summary (`base_budget = 8000`, `seeds = [0, 1, 2]`, `wall = 7.98s`)

| Suite | Stratum / Split | Tasks | `A0 BASE` Mean Gates | `INDEP` Per-Out Mean | `A1 ABC` AIG Mean | `A1 ABC` XAG Mean | Joint Beats Indep | Gap (`BASE − ABC_XAG`) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `dev_structured` | Stratum 1 / dev | 10 | 12.6 | 17.0 | 17.7 | 14.1 | 8 / 10 | −1.5 |
| `holdout_structured` | Stratum 1 / **untouched holdout** | 10 | 20.0 | 30.7 | 25.9 | 21.9 | 10 / 10 | −1.9 |
| `dev_proc_shared` | Stratum 2a / dev | 10 | 20.2 | 23.0 | 21.6 | 19.4 | 8 / 10 | +0.8 |
| `holdout_proc_shared` | Stratum 2a / **untouched holdout** | 10 | 20.2 | 21.8 | 19.8 | 16.8 | 5 / 10 | **+3.4** |
| `holdout_proc_rand` | Stratum 2b / **untouched holdout** | 10 | 39.7 | 45.6 | 41.9 | 41.4 | 9 / 10 | −1.7 |

*Every circuit across all 50 tasks and all arms passed exact 100% bitmask truth-table verification (`verify_truth_tables == True`).*

---

## 2. Non-Saturation & Order-2 Qualification Checks

1. **Exact Disjointness:** Dev and holdout target tuples are 100% disjoint (`test_benchmark_suite_counts_determinism_and_disjointness`).
2. **Non-Saturation:**
   - On `holdout_proc_shared`, Berkeley `ABC` (XAG) beats `A0 BASE` by **`3.4 gates/task`** (`16.8` vs `20.2`), confirming genuine structural sharing headroom that naive wavefront + Davio misses.
   - On `holdout_structured`, individual targets retain large verified headroom vs known/ABC optima (e.g., `s1_hold_cmp3`: `BASE 29` vs `ABC 18`; `s1_hold_barrel_rot4`: `BASE 31` vs `ABC 24`; `s1_hold_sbox_prince`: `BASE 24` vs `ABC 19`; `s1_hold_popcount6`: `BASE 24` vs ~`14` exact; `s1_hold_gf16_inv`: `BASE 25` vs ~`12` exact).
   - On `holdout_proc_rand` (pure random 5-in 3-out anti-prior stratum), targets sit cleanly at `36–43` gates with `0` trivial collapses.
3. **Order-2 Multi-Output Sharing Confirmed:** Joint synthesis beats independent per-output synthesis on **40 / 50 tasks** overall (including **10 / 10** `holdout_structured`, saving `10.7 gates/task` on average).
4. **Gate Verdict:** **PHASE 1 PASS — SEALED HOLDOUT READY FOR PHASE 2 (6-ARM CLAIM 1 & CLAIM 2 RUN).**

---

## 3. Frozen Holdout Policy Entering Phase 2

From this commit onward, `holdout_structured`, `holdout_proc_shared`, and `holdout_proc_rand` (manifest `9c02ddcaa5a1610801fe05f8307f221079923fb3bce86b230c8d99cc4f4322e7`) are **UNTOUCHED**. No proposer (`A2 PRIOR-ONLY`, `A3 ZERO-LLM-LEARN`, `A4 MG-UNPLUGGED`) may inspect any holdout task, trace, or score during evolution. All frozen checkpoints (`A1, A2, A3` in Phase 3) will be evaluated on this exact same sealed holdout.
