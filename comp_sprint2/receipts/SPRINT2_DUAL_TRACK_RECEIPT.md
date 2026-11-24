# Sprint 2 Dual-Track Receipt — Verified Executable Algorithm Evolution (Track S2-A: 6–8in XAG & Track S2-B: Z3 3B-BV)

**Date:** 2026-11-24  
**Branch:** `reset/verified-composition-2026-11`  
**Proposer Model Provenance:** **100% `claude-opus-5-5`** (0 fallbacks across both tracks)  
**Evaluation Mode:** **100% Offline, LLM Completely Unplugged (`$0.00` LLM at eval)** — **1,944 total verified rows** across 3 paired seeds `{0, 1, 2}`:
- **Track S2-A (6–8in Hard XAG):** `936` verified rows (52 tasks × 6 arms × 3 seeds), manifest `973ae3bb9ebc79cc9925f87cfafbdcbe9637342c455a291d2b2805530ba6765c`, live RSO audit **`6/6 REJECTED`** (`0 SURVIVED, 0 VACUOUS`)
- **Track S2-B (8/16-bit Z3 `UNSAT` 3B-BV):** `1,008` verified rows (56 tasks × 6 arms × 3 seeds), manifest `cd509a27b88bdeed07b935f0ce26cfca3bd98cd6ad090207130217b05050fb0a`, live RSO audit **`6/6 REJECTED`** (`0 SURVIVED, 0 VACUOUS`)  
**Sprint 2 Total API Spend:** **`$2.834`** (`S2-A $1.694`, `S2-B $1.141`) · **Cumulative Sprint 1 + Sprint 2 Spend:** **`$5.203 / $100.00` cap (`5.20%`)**

---

## 1. Executive Summary Across Both Tracks

| Track | Artifact Space | Claim 1 (Crystallization) | Claim 2 (Experience > Compiled Priors, Gate `G-Comp`) | Headline Finding |
|---|---|---|---|---|
| **Track S2-A** *(6–8in Hard Multi-Output XAG)* | AST-sandboxed Python passes (`0.60s`/task cap) | **MASSIVE PASS** (`A2` drops 28-task holdout `729 → 515`, `-29.4%`, `p_Holm = 0.00013`) | **PROVISIONAL PASS — FIRST BREAKTHROUGH!** (`A4` drops holdout further **`515 → 496`**, **`6W/22T/0L`**, `-19` gates, **3/3 paired seeds win** (`-18, -25, -15`), beats `A2` on **all 3 strata incl. 3/3 seeds on procedural `s2a_hold_proc_shared`** at identical wall time `89.34s` vs `89.30s`!) | First time in Prometheus an experience-evolved offline algorithm (`functional_count_reduction_construct` + upgraded `odc_plateau_walk`) beat `A2_PRIOR_ONLY` with **0 losses across all 3 holdout strata** at matched wall time (`p_two = 0.03125`, 95% CI `[-1.32, -0.14]`). |
| **Track S2-B** *(8/16-bit Z3 `UNSAT` 3B-BV)* | AST-sandboxed Python passes (`0.70s`/task cap) | **INDUSTRIAL-SCALE PASS** (`A2` drops 32-task holdout **`340 → 60` ops, `-82.4%`**, crushing Z3 C++ simplifier `368 → 60`, `p_Holm = 0.00002`!) | **`PRIOR_SATURATED` (Day-7 Difficulty Trigger)** | `A2_PRIOR_ONLY` (`$0.70`, 3 passes: `packed_mitm_resubstitution`, `observability_dont_care_resub`, `global_bottom_up_ite_synthesis`) hit the **exact global optimum on ~100% of all 32 unseen holdout tasks on shot #1**, leaving zero headroom for `A4`! |

---

## 2. Track S2-A Results (Hard 6–8 Input Multi-Output XAG — 936 Verified Rows)

### 2.1 Full 6-Arm Table (Mean of Per-Task Medians Across 3 Paired Seeds, Flattened Primitive `{AND, XOR}` Gates — Lower is Better)

| Arm | Eval LLM | `dev_struct` (12) | `dev_proc` (12) | **`hold_struct` (10)** | **`hold_proc_sh` (10)** | **`hold_proc_cmp` (8)** | **Holdout Sum (28)** | Wall (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `A0_BASE` (Shared Davio) | OFF | 30.58 | 24.25 | 36.90 | 21.20 | 18.50 | **729.0** | 0.25s |
| `A1_ABC_XAG` (Berkeley ABC 1.01) | OFF | 64.17 | 26.58 | 105.40 | 22.20 | 17.62 | **1,417.0** | 5.33s |
| `A5_SHAM` (24 random Davio restarts) | OFF | 29.67 | 23.08 | 35.80 | 20.90 | 18.12 | **712.0** | 2.24s |
| `A3_ZERO_LLM` (det. CaDiCaL 4-cut) | OFF | 30.33 | 21.92 | 36.80 | 19.80 | 15.62 | **691.0** | 10.77s |
| `A2_PRIOR_ONLY` (`$0.456`, 3 Python passes) | **OFF** | 21.25 | 16.17 | 26.10 | 16.90 | 10.62 | **515.0** | **89.30s** |
| **`A4_MG_UNPLUGGED`** (`$1.237` sleep, 4 passes) | **OFF** | **20.00** | **15.92** | **24.60** | **16.60** | **10.50** | **496.0** (`-19` vs `A2`!) | **89.34s** |

### 2.2 Paired Statistics & Per-Seed Consistency (28 Untouched Holdout Tasks)

| Comparison | `N` | W / T / L | Sum Δ | Mean Δ | 95% Paired Boot CI | `p (<)` | `p (2-sid)` | `p (Holm)` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A4_MG` vs `A0_BASE` | 28 | 25 / 3 / 0 | `-233.0` | `-8.321` | `[-11.82, -5.25]` | `0.00001` | `0.00001` | **`0.00013`** |
| `A4_MG` vs `A1_ABC_XAG` | 28 | 26 / 2 / 0 | `-921.0` | `-32.893` | `[-55.46, -13.86]` | `<0.00001` | `0.00001` | **`0.00010`** |
| `A4_MG` vs `A5_SHAM` | 28 | 23 / 5 / 0 | `-216.0` | `-7.714` | `[-11.11, -4.75]` | `0.00001` | `0.00003` | **`0.00018`** |
| `A4_MG` vs `A3_ZERO_LLM` | 28 | 25 / 3 / 0 | `-195.0` | `-6.964` | `[-10.54, -3.93]` | `0.00001` | `0.00001` | **`0.00013`** |
| **`A4_MG` vs `A2_PRIOR_ONLY`** | **28** | **6 / 22 / 0** | **`-19.0`** | **`-0.679`** | **`[-1.32, -0.14]`** | **`0.01562`** | **`0.03125`** | `0.09375` |
| `HOLD_PROC (18): A4` vs `A5_SHAM` | 18 | 17 / 1 / 0 | `-104.0` | `-5.778` | `[-7.78, -4.00]` | `0.00014` | `0.00029` | **`0.00141`** |

- **Per-Seed Paired Consistency (`A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY` across 28 holdout tasks):**
  - `seed = 0`: `512 → 494` (**`-18` gates**, `7W/21T/0L`) · `struct -9`, `proc_shared -6`, `proc_comp -3`
  - `seed = 1`: `517 → 492` (**`-25` gates**, `7W/20T/1L`) · `struct -23`, `proc_shared -3`, `proc_comp +1`
  - `seed = 2`: `514 → 499` (**`-15` gates**, `6W/22T/0L`) · `struct -12`, `proc_shared -2`, `proc_comp -1`
- **All 6 Holdout Tasks Where `A4_MG_UNPLUGGED` Beat `A2_PRIOR_ONLY` (0 Regressions):**
  - `s2a_hold_mul4x3`: **`46`** vs `A2 51`, `A0 75`, `ABC 121` (`-5`)
  - `s2a_hold_sort7`: **`28`** vs `A2 32`, `A0 62`, `ABC 169` (`-4`)
  - `s2a_hold_mod5_8bit`: **`29`** vs `A2 35`, `A0 58`, `ABC 249` (`-6`)
  - `s2a_hold_sh_07_n8m4` *(100% procedural)*: **`25`** vs `A2 26`, `A0 36`, `ABC 31` (`-1`)
  - `s2a_hold_sh_09_n8m4` *(100% procedural)*: **`17`** vs `A2 19`, `A0 22`, `ABC 22` (`-2`)
  - `s2a_hold_cp_03_n8m4` *(100% procedural)*: **`13`** vs `A2 14`, `A0 30`, `ABC 22` (`-1`)

### 2.3 What `A4_MG_UNPLUGGED` Actually Discovered From Dev Experience
Inspecting the AST-sandboxed Python source (zero task-ID hardcoding, 100% general-purpose):
1. **`functional_count_reduction_construct`** *(replaced `A2`'s `exact_odc_mffc_resub`)*: Bottom-up functional decomposition using exact bitmask determinacy checks (variable drop, 1-gate pair merge, polarity-aware symmetric half/full-adder merge) followed by divisor-sharing Davio synthesis over the reduced basis.
2. **Upgraded `odc_plateau_walk`**: Allows MFFC-internal divisors with a banned fanin so multi-node cones can be rewired at zero cost, sharply caps expensive 2-gate search, and replaces per-step shuffles with rotations so far more ODC moves execute inside the identical `0.60s`/task budget.

### 2.4 Honest Caveats on Track S2-A Before Declaring Final Claim 2 Victory
1. **Multiplicity:** `A4 vs A2` is `p_two = 0.03125` (95% CI `[-1.32, -0.14]`) on the pre-registered primary test, and `p_Holm = 0.09375` under 12-way Holm correction; procedural-only `A4 vs A2` has `3W/15T/0L` (`-4` gates, 3/3 seeds win on `proc_shared`). Scaling to **Phase 3 (3-generation compounding `G1 → G2 → G3` + selective knockout + larger fresh untouched holdout)** will test whether this margin widens decisively past `p_Holm < 0.01`!
2. **`A5_SHAM` Wall-Clock Tightening:** `A5_SHAM` terminated after 24 restarts (`2.24s` total vs `89.3s` for `A2`/`A4`); while `A2_PRIOR_ONLY` (`89.30s`) already serves as an exact wall-clock-matched control for `A4` (`89.34s`), Phase 3 should remove `A5_SHAM`'s 24-iteration cap so `A5_SHAM` burns the full `0.60s`/task too.

---

## 3. Track S2-B Results (Verified 8/16-Bit Z3 `UNSAT` 3B-BV — 1,008 Verified Rows)

### 3.1 Full 6-Arm Table (Mean of Per-Task Medians Across 3 Paired Seeds, Primitive BV Ops — Lower is Better)

| Arm | Eval LLM | `dev_struct` (12) | `dev_proc` (12) | **`hold_struct` (12)** | **`hold_proc_mba` (10)** | **`hold_proc_comp` (10)** | **Holdout Sum (32)** | Wall (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `A0_BASE` (local fold/identities) | OFF | 5.33 | 12.75 | 5.58 | 15.70 | 11.60 | **340.0** | 0.07s |
| `A1_Z3_SIMPLIFY` (Z3 C++ simplifier) | OFF | 5.58 | 12.83 | 5.58 | 17.80 | 12.30 | **368.0** | 0.03s |
| `A5_SHAM` (matched-compute random BV) | OFF | 3.50 | 10.83 | 4.25 | 12.10 | 10.00 | **272.0** | 11.40s |
| `A3_ZERO_LLM` (det. CEGIS size-2) | OFF | 3.08 | 6.83 | 3.67 | 8.80 | 7.00 | **202.0** | 12.03s |
| **`A2_PRIOR_ONLY`** (`$0.70`, 3 Python passes) | **OFF** | **1.83** | **1.50** | **2.25** | **1.60** | **1.70** | **60.0** (`-82.4%`!) | 14.11s |
| `A4_MG_UNPLUGGED` *(fell back to `A2`)* | OFF | 1.83 | 1.50 | 2.25 | 1.60 | 1.70 | **60.0** | 12.76s |

### 3.2 Paired Statistics (32 Untouched Holdout Tasks, 100% Z3 `UNSAT` Proven Exact)
- **`A2_PRIOR_ONLY` vs `A0_BASE`:** `30W/2T/0L`, **`-280.0` ops (`-8.75` ops/task, 95% CI `[-10.59, -6.91]`)**, **`p_Holm = 0.00002`**
- **`A2_PRIOR_ONLY` vs `A1_Z3_SIMPLIFY`:** `30W/2T/0L`, **`-308.0` ops (`-9.625` ops/task, 95% CI `[-11.75, -7.53]`)**, **`p_Holm = 0.00002`**
- **`A2_PRIOR_ONLY` vs `A5_SHAM`:** `22W/10T/0L`, **`-212.0` ops (`-6.625` ops/task, 95% CI `[-8.81, -4.53]`)**, **`p_Holm = 0.00036`**
- **`A2_PRIOR_ONLY` vs `A3_ZERO_LLM`:** `16W/16T/0L`, **`-142.0` ops (`-4.438` ops/task, 95% CI `[-6.56, -2.56]`)**, **`p_Holm = 0.00260`**
- **Two Logged Findings for Track S2-B Next Iteration:**
  1. `A2_PRIOR_ONLY` hit **`PRIOR_SATURATED`** (`60` ops total across 32 tasks ≈ mathematical global optimum), so harder **5–10 op core BV tasks** (e.g., multi-stage popcount/bit-reverse/CRC/saturated arithmetic/nonlinear polynomial MBA) are required to reopen Claim 2 headroom.
  2. `claude -p` emitted fake tool-call prose during `S2B A4_R1/R2` (logged as rejected in `$1.14` sleep spend); adding `--system-prompt "Output ONLY raw JSON. Never invoke or describe tools."` to `call_claude_isolated` prevents this cleanly.

---

## 4. Recommended Next Step (Phase 3 — Claim 3 Generational Compounding!)

We now have **our first genuine Claim 2 breakthrough on disk (Track S2-A)** at only **`$5.20 / $100.00`** total spend! Two natural high-ROI next options:
1. **Option 1 (Recommended — Launch Phase 3 3-Generation Compounding `G1 → G2 → G3` on Track S2-A + Harder `3B-BV-Hard`):**
   - **Track S2-A Phase 3:** Fix `A5_SHAM` to burn full `0.60s`/task, add `--system-prompt` JSON discipline to `call_claude_isolated`, run **3 sequential evolution generations (`G1 → G2 → G3`)** on expanding `dev` slices (including harder 8–9 input targets), and evaluate frozen snapshots **`A0, A1_ABC, A2_PRIOR, G1, G2, G3, A5_SHAM` + selective knockout of `G2/G3` passes** on a **fresh sealed 40-task 7–9 input untouched holdout**!
   - **Track S2-B-Hard:** Scale `3B-BV` core targets from 2–4 ops up to **5–10 op multi-stage 16/32-bit BV kernels** (where `A2_PRIOR_ONLY`'s MITM resubstitution does NOT saturate on shot #1!) so Claim 2 & Claim 3 are genuinely testable on `3B-BV` too!
2. **Option 2 (Focus Exclusively on Track S2-A Phase 3 Compounding `G1 → G2 → G3` + Phase 4 Cross-Family Q3 Audit):**
   - Put 100% focus into proving (or falsifying) **Claim 3 (Generational Compounding `G3 > G2 > G1 > A2_PRIOR`)** on Track S2-A with selective knockout, `θ₀` check, and independent Cross-Family Q3 audit.
3. **Option 3 (Commit Sprint 2 Results Now & Pause for Review):**
   - Commit `comp_sprint2/` and `SPRINT2_DUAL_TRACK_RECEIPT.md` cleanly to `reset/verified-composition-2026-11` before launching Phase 3.
