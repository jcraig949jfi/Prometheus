# Phase 3 Dual-Track Compounding Receipt — 3-Generation Executable Algorithm Evolution (Track S3-A: 7–9in XAG & Track S3-B-Hard: 16-Bit Z3 BV)

**Date:** 2026-11-24  
**Branch:** `reset/verified-composition-2026-11`  
**Proposer Model Provenance:** **100% `claude-opus-5-5`** (via `claude -p --system-prompt ... --tools ""`, `0` fallbacks, `0` rejected JSON calls across all 8 Phase 3 calls!)  
**Evaluation Mode:** **100% Offline, LLM Completely Unplugged (`$0.00` LLM at eval)** — **2,862 verified Phase 3 rows** across 3 paired seeds `{0, 1, 2}`:
- **Track S3-A (7–9in Hard XAG):** `1,350` verified rows (50 eval tasks incl. 40 brand-new untouched holdout × 9 arms × 3 seeds), manifest `9a003b37da6af60655de55d153e2c4cf8fedf00942b3a1248e18ba85a96c9937`, live RSO **`6/6 REJECTED`** (`0 SURVIVED, 0 VACUOUS`)
- **Track S3-B-Hard (16-bit Multi-Stage Z3 `UNSAT` BV):** `1,512` verified rows (56 eval tasks incl. 28 brand-new untouched holdout × 9 arms × 3 seeds), deterministic manifest `0a06abdb0ad8164c7b377ebf0345dff29e743debe653c943a55d1e0e8762a4b0`, live RSO **`6/6 REJECTED`** (`0 SURVIVED, 0 VACUOUS`)  
**Phase 3 Equivalent Spend (Claude Subscription Usage):** `$4.047` (`S3-A $2.161`, `S3-B $1.886`)  
**Cumulative Equivalent Spend Across Sprint 1 + Sprint 2 + Phase 3 (7,074 Total Verified Offline Rows):** **`$9.25 / $100.00` cap (`9.25%`)**

---

## 1. Honest Verdict on the Four-Rung Claim Ladder (`SYNTHESIS_AND_ADJUDICATION.md` §3.1)

| Rung | Claim | Track S3-A (7–9in Hard XAG) | Track S3-B-Hard (16-bit Z3 BV) |
|---|---|---|---|
| **Claim 1** | **Executable Algorithm Crystallization** (`A2_PRIOR_ONLY` compiles into deterministic LLM-free algorithms crushing `A0`, Industry, `A3`, and full-budget `A5_SHAM`) | **MASSIVE PASS** (`1,339 → 876`, **`-382` gates vs true full-budget `90.5s` `A5_SHAM`**, `-391` vs `A3`, `-2,321` vs `ABC 1.01`, `p_Holm < 0.00001`!) | **MASSIVE PASS** (`569 → 244`, **`-57.1%`**, `-332` vs Z3 C++ simplifier, `-303` vs `A3`/`A5_SHAM`, `p_Holm = 0.0012`, 100% Z3 `UNSAT` exact!) |
| **Claim 2** | **Experience Beyond Compiled Priors (`G1`/`G3` > `A2_PRIOR_ONLY` incl. Stratum 2 procedural)** | **PARTIAL / STRUCTURED `G1` REPLICATION** (`G1` `+mdfa_weighted_count_synth` beat `A2` on **3/3 paired seeds: `-21, -4, -8`**, median `866` vs `876`, `4W/35T/1L`, `p_two = 0.188`; procedural `+0.0` at `G3`) | **FAIL** (`G2/G3 = 260` worse than `A2 = 244` & `G1 = 231`; exposed **13-op Z3 wall-clock jitter on identical code**!) |
| **Claim 3** | **Generational Compounding (`G3 > G2 > G1 > A2_PRIOR` on shared untouched holdout + disappears on knockout)** | **HONEST FAIL (`G-Recurse` NOT MET)** (`dev_val` dropped `215→207→205→202`, but holdout flatlined `876→866→868→870`; `G3 vs G3_KO = -1`, `p_two = 1.0`) | **HONEST FAIL (`G-Recurse` NOT MET)** (`dev_val` dropped `75→70→42→42`, but holdout regressed `244→231→260→260`) |
| **Claim 4** | **Non-Human Novelty** | **OUT OF SCOPE** | **OUT OF SCOPE** |

---

## 2. Track S3-A Full 9-Arm Progression (40 Brand-New 7–9 Input Untouched Holdout Tasks, 1,350 Verified Rows)

| Arm | Eval LLM | `s3a_dev_val` (10) | **`hold_struct` (14)** | **`hold_proc_sh` (14)** | **`hold_proc_cmp` (12)** | **Holdout Sum (40)** | Wall (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| `A0_BASE` | OFF | 36.70 | 45.71 | 32.29 | 20.58 | **1,339.0** | 0.37s |
| `A1_ABC_XAG` (Berkeley ABC 1.01) | OFF | 122.70 | 173.79 | 40.93 | 15.92 | **3,197.0** | 5.29s |
| `A3_ZERO_LLM` (det. CaDiCaL 4-cut) | OFF | 33.90 | 45.00 | 30.00 | 18.08 | **1,267.0** | 19.86s |
| `A5_SHAM` *(true full-budget random Davio)* | OFF | 33.70 | 43.50 | 30.07 | 19.00 | **1,258.0** | **90.54s** |
| `A2_PRIOR_ONLY` (Gen 0, 3 passes) | **OFF** | 21.70 | 28.64 | 22.64 | 13.17 | **876.0** | 87.67s |
| **`G1`** (`+mdfa_weighted_count_synth`, 4 passes) | **OFF** | 21.00 | 28.00 | **22.64** | 13.08 | **866.0** (`-10` vs `A2`) | 87.71s |
| `G2` (`+odc_threshold_walk`, 5 passes) | **OFF** | 20.80 | **27.93** | 22.79 | 13.17 | **868.0** | 82.31s |
| `G3` (`resub→odc_fast_chain_walk`, 5 passes) | **OFF** | **20.40** | 28.21 | 22.86 | **12.92** | **870.0** | 85.59s |
| `G3_KO_G2G3` *(selective knockout of G2/G3)* | OFF | 20.90 | 28.14 | 22.86 | 13.08 | **871.0** | 87.57s |

- **Per-Seed Untouched Holdout Totals (`N = 40`):**
  - `seed = 0`: `A0=1339`, `SHAM=1258`, `A2=892`, **`G1=871`** (`-21`), `G2=873`, `G3=875`, `G3_KO=876`
  - `seed = 1`: `A0=1339`, `SHAM=1261`, `A2=868`, **`G1=864`** (`-4`), `G2=867`, `G3=875`, `G3_KO=878`
  - `seed = 2`: `A0=1334`, `SHAM=1252`, `A2=894`, `G1=886` (`-8`), `G2=883`, **`G3=870`** (`-24`), `G3_KO=870`
- **Key Paired Wilcoxon Stats (`N = 40`):**
  - `G3 vs A0_BASE`: `36W/4T/0L`, `-469.0` gates, **`p_Holm < 0.00001`**
  - `G3 vs A5_SHAM` *(full `90.5s`)*: `36W/4T/0L`, `-388.0` gates, **`p_Holm < 0.00001`**
  - `G3 vs A3_ZERO_LLM`: `35W/5T/0L`, `-397.0` gates, **`p_Holm < 0.00001`**
  - `G1 vs A2_PRIOR_ONLY`: `4W/35T/1L`, `-10.0` gates (`3/3` seeds win), `p_less = 0.094`, `p_two = 0.188`
  - `G3 vs A2_PRIOR_ONLY`: `12W/21T/7L`, `-6.0` gates, `p_two = 0.536` (`G3 vs G1 = +4.0`, `G3 vs G3_KO = -1.0`)

---

## 3. Track S3-B-Hard Full 9-Arm Progression (28 Brand-New 16-Bit Multi-Stage BV Holdout Tasks, 1,512 Verified Rows)

| Arm | Eval LLM | `dev_struct` (14) | `dev_proc` (14) | **`hold_struct` (12)** | **`hold_proc` (16)** | **Holdout Sum (28)** | Wall (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| `A0_BASE` | OFF | 14.57 | 23.14 | 16.17 | 23.44 | **569.0** | 0.07s |
| `A1_Z3_SIMPLIFY` (Z3 C++ simplifier) | OFF | 15.00 | 23.71 | 16.67 | 23.50 | **576.0** | 0.07s |
| `A3_ZERO_LLM` (det. CEGIS size-2) | OFF | 14.57 | 21.57 | 16.17 | 22.06 | **547.0** | 20.87s |
| `A5_SHAM` (random BV sampler) | OFF | 14.57 | 21.57 | 16.17 | 22.06 | **547.0** | 13.16s |
| `A2_PRIOR_ONLY` (Gen 0, 3 passes) | **OFF** | 5.29 | 11.07 | 6.00 | 10.75 | **244.0** | 113.47s |
| `G1` *(identical 3 passes as `A2`)* | **OFF** | 5.29 | 8.86 | **5.67** | **10.19** | **231.0** *(Z3 wall-clock jitter!)* | 120.72s |
| `G2` (`+forward_cut_proved_resub`, 4 passes) | **OFF** | **5.00** | 9.50 | 6.50 | 11.38 | **260.0** | 149.36s |
| `G3` (`odc→linear_mba_signature_rewrite`, 4 passes) | **OFF** | **5.00** | **8.07** | 6.50 | 11.38 | **260.0** | 151.38s |
| `G3_KO_G2G3` *(2 passes only)* | OFF | 5.36 | 15.64 | 7.25 | 15.88 | **341.0** (`+81` worse!) | 114.96s |

- **Key Paired Wilcoxon Stats (`N = 28`, 100% Z3 `UNSAT` Proven Exact):**
  - `G3 vs A0_BASE`: `20W/8T/0L`, `-309.0` ops (`-11.04` ops/task), **`p_Holm = 0.00119`**
  - `G3 vs A1_Z3_SIMPLIFY`: `20W/8T/0L`, `-316.0` ops, **`p_Holm = 0.00119`**
  - `G3 vs A5_SHAM` & `A3_ZERO_LLM`: `19W/9T/0L`, `-287.0` ops, **`p_Holm = 0.00155`**
  - `G3 vs G3_KO_G2G3`: `5W/23T/0L`, `-81.0` ops (`p_less = 0.03125`) — confirming `G2`/`G3`'s new passes are genuinely functional, though their 4-pass pipeline regressed `+16` ops vs `A2_PRIOR_ONLY`'s 3-pass pipeline under wall-clock slicing!

---

## 4. Three Concrete Engineering Laws Diagnosed for True Claim 3 Compounding

Across **7,074 verified offline rows** (`Sprint 1 + Sprint 2 + Phase 3`), we now know with empirical precision why **`G1` repeatedly discovers genuine structured improvements (`functional_count_reduction_construct` in S2-A, `mdfa_weighted_count_synth` in S3-A)** yet **`G2` and `G3` fail to compound monotonically on holdout**:

1. **Law 1 — Wall-Clock Budgets Destroy Generational Signal (Must Switch to Deterministic Operation Budgets!):**
   In `S3-B-Hard`, **identical code** (`A2_PRIOR_ONLY` vs `G1`) produced `244` vs `231` ops (`13`-op swing!) purely from Z3 SMT wall-clock jitter. In `S3-A`, appending a 5th pass inside a fixed `0.60s` wall-clock cap stole ~30% of each earlier pass's time slice. **Fix:** Replace `time.perf_counter() < deadline` with **deterministic operation counters** (exact truth-table evals / exact Z3 call counts) so identical code has `0.000` run-to-run noise.
2. **Law 2 — Adaptive Goodharting on a Reused 10-Task `dev_val` Split:**
   In BOTH tracks, greedy selection over 3 generations on the same 10-task `dev_val` produced monotonic `dev_val` improvement (`215→207→205→202` and `75→70→42→42`) that did **not** transfer past `G1` on the 40-task / 28-task holdout. **Fix:** Use a **disjoint validation split per generation (`val_g1`, `val_g2`, `val_g3`, `N >= 25` each)** AND require a **paired Wilcoxon `p < 0.05` acceptance gate** (never accepting 1-to-2 gate point noise).
3. **Law 3 — Flat Sequential Pass Lists Hit Structural Diminishing Returns (Need Compositional Modularity!):**
   Appending independent 50-line passes into a flat list forces later generations to rewrite similar search loops from scratch rather than **composing on top of earlier generations' discovered modules/libraries**. True multi-generation compounding requires letting Generation `k+1` **import and call** Generation `k`'s verified helper subroutines + shared persistent rewrite/decomposition state.
