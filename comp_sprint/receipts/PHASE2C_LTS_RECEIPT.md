# Phase 2C Receipt — Full `(L, T, S)` Offline Artifacts on Fresh Sealed v2c Manifest (Track 3B-Boolean)

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11`  
**Fresh Sealed v2c Manifest SHA-256:** `b14f790e5d5eab08f104876c8c7344ed2dc2036b705ce0d2a5be38fe56505708` *(100% disjoint from Phase 2B holdout `9c02ddca...`)*  
**Proposer Model Provenance:** **100% `claude-opus-5-5`** (isolated `claude -p --model opus --tools "" --no-session-persistence`, 0 fallbacks, 0 rejected items)  
**Evaluation Mode:** **100% Offline, LLM Completely Unplugged (`$0.00` LLM at eval)** — **1,368 verified rows** (6 arms × 76 tasks × 3 paired seeds `{0, 1, 2}`, budget = `12,000` eval units/task, wall time = `115.3s`)  
**Hardened 3-Seed Live RSO Adversarial Audit:** **`6 / 6 REJECTED, 0 SURVIVED, 0 VACUOUS, 0 ERROR`** (including single-seed tamper + re-hashed `row_sha256`!)  
**Raw Packets (scratch):**
- Proposals: `PHASE2C_PROPOSALS.json` (`$0.500` total sleep LLM spend: `A2 $0.176`, `A4_R1 $0.187`, `A4_R2 $0.136`)
- Full 1,368-row Eval: `PHASE2C_FULL_PACKET.json` (`verify_and_reduce`: **1,368/1,368 rows verified exact**)

---

## 1. Executive Verdict on the Four-Rung Claim Ladder (`SYNTHESIS_AND_ADJUDICATION.md` §3.1)

| Rung | Claim | Phase 2C Verdict | Evidence Summary (40 Brand-New Untouched Holdout Tasks) |
|---|---|---|---|
| **Claim 1** | **Crystallization** (`PRIOR-ONLY` or `MG-UNPLUGGED` compiles into compact, LLM-free machinery beating `BASE`, `ABC`, `ZERO-LLM`, and strategy-matched `SHAM`) | **DECISIVELY CONFIRMED (`PASS`)** | Unplugged **`A2_PRIOR_ONLY`** (`$0.176`, 0 tasks seen, 20 macros + 8 verified rewrites + strategy `S`) dropped 40-task holdout total from `848.0` (`A0_BASE`) and `993.0` (`ABC 1.01`) to **`774.0` (`-74` gates vs `BASE`, `27W/13T/0L`, `p < 0.00001`; `-31` gates vs strategy-matched `A5_SHAM`, `18W/18T/4L`, `p = 0.00070`; `-219` gates vs Berkeley `ABC 1.01`)**. |
| **Claim 2** | **Experience Beyond Compiled Priors** (**Gate `G-Comp`**: `A4` or `A3` beats `A0`, `A2 (PRIOR-ONLY)`, and `A5 (SHAM)` on ≥1 stratum incl. Stratum 2 procedural) | **FAIL — `COMPILED_PRIORS_ONLY` (2nd Consecutive Experiment)** | **`A4_MG_UNPLUGGED`** beat `A0_BASE` (`-58` gates, `p < 0.00001`), `A3_ZERO_LLM` (`-15` gates, `p = 0.00220`), strategy-matched `A5_SHAM` (`-15` gates, `p = 0.01725`), and `ABC 1.01` (`-203` gates, `p = 0.00001`), **AND** beat `A2_PRIOR_ONLY` on internal `dev_val` (`163` vs `168`), **BUT LOST to `A2_PRIOR_ONLY` on all 4 untouched holdout strata (`790.0` vs `774.0`, `3W/28T/9L`, `+16` gates worse, `p(A4 < A2) = 0.964`)!** `A3_ZERO_LLM` tied `A5_SHAM` (`805.0 == 805.0`) and lost to `A2` (`+31` gates). |
| **Claim 3** | **Generational Compounding (`A1 → A2 → A3`)** | **HELD BY GATE `G-Comp`** | Per §3.4 hard kill rule: do NOT spend Week 3 running 3 generations of a loop that has not yet beaten `A2_PRIOR_ONLY` in Generation 1. |
| **Claim 4** | **Non-Human Novelty** | **OUT OF SCOPE** | Explicitly deferred per v2.0 protocol. |

---

## 2. Full 6-Arm Per-Stratum Results (Mean of Per-Task Medians Across 3 Paired Seeds, Flattened Primitive XAG Gates — Lower is Better)

All 1,368 circuits were flattened to primitive `{AND, XOR}` gates (inverters free, zero macro-call gate discount) and verified 100% bit-exact by exhaustive truth-table check.

| Arm | Eval LLM | `dev_struct` (12) | `dev_proc_sh` (12) | `dev_proc_cmp` (12) | **`hold_struct` (10)** | **`hold_proc_sh` (10)** | **`hold_proc_cmp` (10)** | **`hold_proc_rnd` (10)** | **All Holdout Sum (40)** |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`A0_BASE`** | OFF | 12.75 | 15.17 | 15.83 | 18.20 | 17.10 | 14.30 | 35.20 | **848.0** |
| **`A1_ABC_XAG`** (Berkeley ABC 1.01) | OFF | 15.25 | 17.92 | 22.33 | 19.70 | 19.20 | 17.60 | 42.80 | **993.0** |
| **`A2_PRIOR_ONLY`** (`$0.176`, 0 tasks) | **OFF** | **11.75** | 14.42 | 13.33 | **15.30** | **16.10** | **12.60** | **33.40** | **774.0** (`-74`) |
| **`A3_ZERO_LLM`** (AC + NPN + bridges) | OFF | 12.25 | 14.42 | 13.75 | 16.70 | 16.30 | 13.20 | 34.30 | **805.0** (`-43`) |
| **`A4_MG_UNPLUGGED`** (`$0.324`, 2 rds) | **OFF** | 12.00 | **14.17** | **12.67** | 16.00 | 16.30 | 12.80 | 33.90 | **790.0** (`-58`) |
| **`A5_SHAM`** *(same `S` as `A4` + rand `L,T`)* | OFF | 12.42 | 15.00 | 14.33 | 17.30 | 16.50 | 12.80 | 33.90 | **805.0** (`-43`) |

> **Important Control Finding on Strategy-Matched `A5_SHAM`:**  
> Giving `A5_SHAM` the exact same search strategy `S` (`enable_linear_precond=True`, `enable_bijective_factor=True`, `enable_bridge_rewrites=True`) immediately dropped `A5_SHAM` from `848.0` (`A0_BASE`) to `805.0` (`-43` gates purely from `S`, mostly invertible GF(2) linear-basis preconditioning!). Holding `S` constant via `A5_SHAM` proved cleanly that **`A2_PRIOR_ONLY`'s `(L, T)` adds a genuine `-31` additional gates (`p = 0.00070`)**, and **`A4_MG_UNPLUGGED`'s `(L, T)` adds `-15` gates (`p = 0.01725`)**, while `A3_ZERO_LLM` added **`0.0` net gates over `A5_SHAM`** across all 40 holdout tasks (`805.0 == 805.0`).

---

## 3. Exact Paired Wilcoxon Signed-Rank Statistics (40 Untouched Holdout Tasks)

| Comparison | Stratum | W / T / L | Sum Gate Δ | Mean Gate Δ | One-Sided `p (<)` | Two-Sided `p (≠)` |
|---|---|---:|---:|---:|---:|---:|
| **`A2_PRIOR_ONLY` vs `A0_BASE`** | **ALL HOLDOUT (40)** | **27 / 13 / 0** | **-74.0** | **-1.850** | **<0.00001** | **<0.00001** |
| **`A2_PRIOR_ONLY` vs `A5_SHAM`** | **ALL HOLDOUT (40)** | **18 / 18 / 4** | **-31.0** | **-0.775** | **0.00070** | **0.00141** |
| **`A2_PRIOR_ONLY` vs `A3_ZERO_LLM`** | **ALL HOLDOUT (40)** | **16 / 22 / 2** | **-31.0** | **-0.775** | **0.00050** | **0.00099** |
| `A4_MG_UNPLUGGED` vs `A0_BASE` | ALL HOLDOUT (40) | 27 / 13 / 0 | -58.0 | -1.450 | <0.00001 | <0.00001 |
| `A4_MG_UNPLUGGED` vs `A5_SHAM` | ALL HOLDOUT (40) | 13 / 21 / 6 | -15.0 | -0.375 | 0.01725 | 0.03451 |
| `A4_MG_UNPLUGGED` vs `A3_ZERO_LLM` | ALL HOLDOUT (40) | 11 / 28 / 1 | -15.0 | -0.375 | 0.00220 | 0.00439 |
| `A4_MG_UNPLUGGED` vs `A1_ABC_XAG` | ALL HOLDOUT (40) | 31 / 2 / 7 | -203.0 | -5.075 | 0.00001 | 0.00002 |
| **`A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY`** | **ALL HOLDOUT (40)** | **3 / 28 / 9** | **+16.0** | **+0.400** | **0.96411** | 0.07910 |
| `A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY` | `holdout_structured` (10) | 2 / 6 / 2 | +7.0 | +0.700 | 0.81250 | 0.62500 |
| `A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY` | ALL PROCEDURAL (30) | 1 / 22 / 7 | +9.0 | +0.300 | 0.99609 | 0.04688 |
| `A3_ZERO_LLM` vs `A5_SHAM` | ALL HOLDOUT (40) | 9 / 22 / 9 | 0.0 | 0.000 | 0.43499 | 0.86998 |

---

## 4. Two-Part Root-Cause Diagnosis (Why Claim 2 Failed Again — And What It Teaches Prometheus)

### Cause A — Small-Sample `dev_val` Over-Pruning (Direct Mechanism on Holdout)
During sleep, `prune_artifact_on_val` pruned **13 of `A4`'s 20 macros** on the 12-task `dev_val` split (`if sc <= best_sum: drop`). Because `dev_structured[8:]` contained only `keccak_chi5`, `mux4_1bit_plus_par`, `sbox_serpent0`, and `sbox_piccolo` (zero adders, zero sorters, zero popcounts), pruning **deleted `full_adder`, `compare_swap`, `maj3`, `xor3`, `and_or`, `xor_and`, `and_xor`, and 2 of the 3 discovered `AC_CELL` alien cells!**
- Direct holdout damage from pruning `full_adder` + `and_or` + `xor3`:
  - `s1_v2_hold_sort5`: `A2 = 20` vs `A4 = 25` (`+5` gates lost!)
  - `s1_v2_hold_add3_sat`: `A2 = 19` vs `A4 = 25` (`+6` gates lost!)
  - `holdout_proc_rand`: `A2 = 33.4` vs `A4 = 33.9` (`+5` gates lost!)
- Meanwhile, the empirical abstractions `A4` *did* keep (`ac_cell_0_xnor_nor`, `npn4_1ee1`, `npn4_06f9`, `npn4_001e`, `npn4_007f`) produced genuine wins on individual unseen tasks:
  - `s1_v2_hold_absdiff3`: **`A4 = 21`** vs `A2 = 24` vs `A5_SHAM = 26` vs `BASE/ABC = 29` (`-3` vs `A2`, `-8` vs `BASE/ABC`!)
  - `s1_v2_hold_sbox_rect`: **`A4 = 15`** vs `A2 = 16` vs `ABC = 20`
  - `s2_v2_hold_comp_07_n6m4`: **`A4 = 17`** vs `A2 = 18` vs `A5_SHAM = 19` vs `BASE = 19`

### Cause B — The Deeper Structural Insight About Track `3B-Boolean` at 4–6 Inputs (High-ROI Finding!)
Looking honestly across **both** Phase 2B (`9c02ddca...`, 30 holdout tasks) **and** Phase 2C (`b14f790e...`, 40 holdout tasks) — **70 distinct holdout tasks, 2,268 verified rows, `$2.25` total API spend**:
1. **At 4–6 inputs, the entire low-arity Boolean primitive space is prior-saturated.** There are only 14 NPN3 classes and 222 NPN4 classes. With 20 macro slots + 8 rewrite rules, a single `$0.18` `A2_PRIOR_ONLY` call to `claude-opus-5-5` ALREADY covers nearly the entire high-leverage 2–4 input algebraic basis (`HA`, `FA`, `maj3`, `mux21`, `xor3`, `and3`, `and_or`, `xor_and`, `and_xor`, `xor4`, `and4`, `ao22`, `eq2`, `inner_product2`, `xor_dist`, `or_dist`).
2. **Even on `holdout_proc_comp` (where hidden alien PRNG 3→2 cells were planted!),** `A0_BASE` already beat the hidden witness on 4/10 tasks (`8–9` vs `10–11` gates), and `A2_PRIOR_ONLY` (`12.60`) + `A5_SHAM` (`12.80`) already absorbed most of the remaining headroom via general linear preconditioning + 3-input cuts! Static `k <= 4` macros simply have too narrow a representational dynamic range at `n = 4..6` inputs for experience-derived macros to open a wide, compounding margin over `A2_PRIOR_ONLY`.
3. **Where Experience *Can* Actually Outstrip `A2_PRIOR_ONLY` (The Real Frontier for Prometheus):**
   - **Not** static `k <= 4` lookup tables on 4–6 input truth tables — **either:**
     - **Path A (Scale up to Real Mechanism/Algorithm Synthesis inside Verified Track 3B):** Keep our ultra-fast exact verifier + RSO harness, but let `A4` evolve **verified executable Python synthesis / decomposition / rewriting code (`S_mg`, e.g., custom multi-output factoring heuristics, S-box tower decompositions, iterative SAT/exact-window local search, or bit-vector superoptimization `3B-BV` via Z3)** evaluated 100% offline with LLM unplugged on **harder 6–10 input / 8–16 bit targets** where `A2_PRIOR_ONLY` static macros cannot saturate!
     - **Path B (Clean Phase 4 Cross-Family Q3 Closeout of Track 3B-Boolean Static `(L, T, S)` First):** Freeze our crystal-clear Phase 2B + Phase 2C evidence (`Claim 1 CONFIRMED` at `p < 0.00001` & `N* = 0.70`, beating Berkeley `ABC 1.01` and direct `Opus 5.5` offline; `Claim 2 = COMPILED_PRIORS_ONLY` for static `k <= 4` macro/rewrite libraries on 4–6 input Boolean circuits), hand the frozen receipts to our **Cross-Family Q3 Adversary (Gemini / ChatGPT Astra)** to lock this milestone cleanly on disk, and then decide the next high-ROI frontier from verified ground truth!

---

## 5. Hardened Live RSO Adversarial Audit (Real 1,368-Row 3-Seed Packet)

| Attack | Variant | Verdict | Detail |
|---|---|---|---|
| `DROP` | `drop_row_0` | **REJECTED** | `Missing 1 expected rows` |
| `DUPLICATE` | `duplicate_row_0_over_1` | **REJECTED** | `Duplicate row detected` |
| `REWRITE_DERIVED` | `tamper_summary` | **REJECTED** | `Claimed summary does not match raw rows` |
| `REWRITE_DERIVED` | `tamper_single_seed_rebind_hash` | **REJECTED** | Caught by all-seed `sum_all_gates` / `min_all_gates` checksum even when 3-seed median was unchanged! |
| `SCRUB_ANSWER` | `corrupt_targets_hex` | **REJECTED** | `row_sha256 tamper detected` |
| `CONSTANT` | `constant_detector_on_sham` | **REJECTED** | `real_on_sham=False, const=True` |

---

## 6. Cumulative Sprint Cognitive Accounting Ledger (Phase 0 + 1 + 2A + 2B + 2C)

| Milestone | Rows Verified | API Spend (USD) | Offline Eval CPU (USD @ `$0.05/core-hr`) | Running Total vs `$100` Cap |
|---|---:|---:|---:|---:|
| Phase 0 (222-class NPN4 exact calibration) | 65,536 fns | `$0.000` | `$0.0003` | `$0.0003` (`0.00%`) |
| Phase 1 + 2A (Berkeley ABC + offline qualification) | 600 | `$0.000` | `$0.0002` | `$0.0005` (`0.00%`) |
| Phase 2B (6-arm + A6 shadow, `9c02ddca...`) | 900 | `$1.747` | `$0.0002` | `$1.748` (`1.75%`) |
| Phase 2C (full `(L, T, S)`, `b14f790e...`) | 1,368 | `$0.500` | `$0.0016` | **`$2.250` (`2.25%` of `$100` cap)** |
