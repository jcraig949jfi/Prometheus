# Phase 4 Cross-Family Q3 Adversarial Audit Packet — Track 3B-Boolean (28-Day Verified Composition Sprint v2.0)

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11`  
**Builder / Proposer Family:** Anthropic `claude-opus-5-5` (`100%` verified via CLI `modelUsage`, `0` silent fallbacks)  
**Cross-Family Q3 Adversary Role:** Must be a **non-Anthropic** model family (Gemini / ChatGPT Astra) per v2.0 3-role cross-family separation protocol.  
**Proposed Closeout Verdict for Q3 Attack:**
- **Claim 1 (Crystallization):** `CONFIRMED`
- **Claim 2 (Experience Beyond Compiled Priors — Gate `G-Comp`):** `COMPILED_PRIORS_ONLY` (Honest Negative / Held — did NOT pass Gate `G-Comp` across 3 independent holdout datasets!)
- **Claim 3 (Generational Compounding):** `NOT_RUN_GATED_BY_G_COMP`
- **Claim 4 (Non-Human Novelty):** `OUT_OF_SCOPE`

---

## 1. Independent Mechanical Q3 Audit Summary (`comp_sprint/phase4_q3_audit.py`)

All five mechanical falsification checks from `SYNTHESIS_AND_ADJUDICATION.md` §3.4 were executed cleanly:

1. **Frozen `rso/` Integrity:** `git diff -- rso/` = **0 bytes changed**. All **67/67** frozen `rso/adversary` + `rso/completeness` tests pass (`3.23s`). All **20/20** `comp_sprint/tests/` pass (`6.05s`).
2. **Hardened Live 3-Seed RSO Adversarial Audit (Real 1,368-Row Phase 2C Packet):**
   - `DROP` (`drop_row_0`) → **REJECTED**
   - `DUPLICATE` (`dup_row_0_over_1`) → **REJECTED**
   - `REWRITE_DERIVED` (`tamper_summary`) → **REJECTED**
   - `REWRITE_DERIVED` (`tamper_single_seed_rebind_hash`) → **REJECTED** *(after hardening `reducer.py` with all-seed `sum_all_gates`/`min_all_gates`/`max_all_gates` following a Phase 2B live-audit catch!)*
   - `SCRUB_ANSWER` (`corrupt_targets_hex`) → **REJECTED**
   - `CONSTANT` (`constant_detector_on_sham`) → **REJECTED**
   - **Total:** `6 REJECTED, 0 SURVIVED, 0 VACUOUS, 0 ERROR`.
3. **Zero-Shared-Code Semantic & No-Discount Re-Audit:**
   - Standalone gate evaluator completely independent of `comp_sprint/circuit.py` re-verified **48 macros + 900 rows (Phase 2B)** and **42 macros + 27 rewrite rules + 1,368 rows (Phase 2C)**: **`0` truth-table mismatches, `0` unsound rewrites (`lhs != rhs`), `0` cycles, `0` macro gate-count discounts** (`and_count + xor_count == gate_count` on 100% of rows; all macros flattened to primitive `{AND, XOR}` gates).
4. **Independent Cost-Accounting Audit & Erratum Caught:**
   - **Erratum caught by Q3 audit:** In Phase 2B `A6_SHADOW_NAKED`, one failed-parse attempt spent `$0.119795` on `claude -p` before raising a parser exception; `phase2_llm.py` recorded it in `shadow_naked["total_usd"]` (`$1.576`, so `v_L = $0.105057/task` and `N*` were already exact), but charged `$0.0` instead of `$0.119795` to `sleep_meter["fixed_llm_usd"]` (`$1.747` vs true `$1.867`).
   - Phase 2C had **0.000000 discrepancy** (`$0.499237 == $0.499237`).
   - **True Corrected Combined Total Sprint Spend (Phases 0–4):** **`$2.369 / $100.00` cap (`2.37%`)**.
   - **Proposer Provenance:** `100% claude-opus-5-5` across every single proposal call (`0` fallbacks).
   - **Phase 0 Exact Calibration:** All **222 4-input NPN classes (65,536 functions)** proved exact via CaDiCaL 1.9.5 in `23.77s`, matching **Knuth TAOCP Vol. 4A §7.1.2 Table 1 / OEIS A056287** digit-for-digit (`{0:2, 1:2, 2:5, 3:20, 4:34, 5:75, 6:72, 7:12}`).

---

## 2. Three Independent Untouched Holdout Datasets (86 Total Unseen Holdout Tasks, LLM 100% UNPLUGGED at Eval)

### Dataset 1 — Phase 2B Sealed Holdout (`9c02ddcaa5a16108...`, 30 Unseen Holdout Tasks, 900 Verified Rows, Static 12-Macro Library)
- `A0_BASE`: `690` total holdout gates (`17.4 / 16.5 / 35.1`)
- `A1_ABC_XAG` (Berkeley ABC 1.01): `801` (`21.9 / 16.8 / 41.4`)
- `A5_SHAM` (size-matched SAT-optimal sham): `689` (`17.4 / 16.5 / 35.0`)
- `A3_ZERO_LLM`: `685` (`17.2 / 16.5 / 34.8`)
- `A4_MG_UNPLUGGED` (`$0.218`, 2 dev rounds): `672` (`16.4 / 16.2 / 34.6`)
- **`A2_PRIOR_ONLY` (`$0.073`, 0 tasks):** **`664`** (`16.4 / 15.6 / 34.4`)
  - `A2` vs `A0_BASE`: `16W/14T/0L`, `-26` gates, Wilcoxon one-sided `p = 0.00014`
  - `A2` vs `A5_SHAM`: `15W/15T/0L`, `-25` gates, `p = 0.00023`
  - `A2` vs `A1_ABC_XAG`: `23W/2T/5L`, `-137` gates, `p = 0.00004`
  - `A4` vs `A2`: `2W/19T/9L`, `+8` gates worse (`p(A4 < A2) = 0.9946`)
- **`A6_SHADOW_NAKED` (15 predeclared holdout tasks, direct `claude-opus-5-5` + exact verifier, `$1.576`):**
  - `14/15` solved (`1` censored failure: `s2_hold_rand_06_n5m3`).
  - Common solved (14/15) mean gates: **`A2_PRIOR_ONLY = 21.29`**, `A4 = 21.57`, `A0 = 21.79`, `A6_NAKED = 23.57`, `ABC = 25.00`.
  - Break-even amortization (`v_L = $0.1051/task`, `v_M = $2.3e-7/task`): **`N*_A2 = 0.70` tasks**, `N*_A4 = 2.08` tasks.

### Dataset 2 — Phase 2C Fresh Sealed Holdout (`b14f790e5d5eab08...`, 40 Brand-New Unseen Holdout Tasks Across 4 Strata, 1,368 Verified Rows, Full `(L, T, S)` Artifacts)
- `A0_BASE`: `848.0` (`18.2 / 17.1 / 14.3 / 35.2`)
- `A1_ABC_XAG` (Berkeley ABC 1.01): `993.0` (`19.7 / 19.2 / 17.6 / 42.8`)
- `A5_SHAM` *(matched `S` + SAT-optimal random `L, T`)*: `805.0` (`17.3 / 16.5 / 12.8 / 33.9`)
- `A3_ZERO_LLM` (AC + NPN + bridges): `805.0` (`16.7 / 16.3 / 13.2 / 34.3`)
- `A4_MG_UNPLUGGED` (`$0.324`, 2 rounds + `dev_val` pruning): `790.0` (`16.0 / 16.3 / 12.8 / 33.9`)
- **`A2_PRIOR_ONLY` (`$0.176`, 0 tasks, 20 macros + 8 rewrites + `S`):** **`774.0`** (`15.3 / 16.1 / 12.6 / 33.4`)
  - `A2` vs `A0_BASE`: `27W/13T/0L`, `-74` gates, `p < 0.00001`
  - `A2` vs strategy-matched `A5_SHAM`: `18W/18T/4L`, `-31` gates, `p = 0.00070`
  - `A2` vs `A1_ABC_XAG`: `-219` gates
  - `A4` vs `A2`: `3W/28T/9L`, `+16` gates worse (`p(A4 < A2) = 0.964`)

### Dataset 3 — Phase 4 Q3 Adversarial Target-Family Shift + 2×2 Factorial Decomposition (16 Brand-New Shifted Tasks: Crypto S-Boxes/Inverses, 5–6 Bit Threshold/CLZ/Hamming/Mod3, Datapath/Gray, 6-Input Uniform Random)

| Arm (`L, T, S` Configuration) | Total Gates (16) | Mean | Crypto (4) | Sym/Coding (4) | Datapath (4) | Rand6 (4) | vs `A0_BASE` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `A1_ABC_XAG` (Berkeley ABC 1.01) | 643 | 40.19 | 21.75 | 26.75 | 16.50 | 95.75 | +152 |
| `A0_BASE` (`L=∅, T=∅, S=S0`) | 491 | 30.69 | 19.00 | 19.50 | 15.00 | 69.25 | 0 |
| `S_ONLY_EMPTY_LT` (`L=∅, T=∅, S=full`) | 475 | 29.69 | 17.00 | 17.75 | 14.75 | 69.25 | -16 (`S` alone) |
| `A5_SHAM_S` (`L=sham, T=sham, S=full`) | 476 | 29.75 | 17.25 | 17.75 | 14.75 | 69.25 | -15 (`+1` vs `S_ONLY`) |
| `A3_ZERO_LLM` | 472 | 29.50 | 17.00 | 17.75 | 14.50 | 68.75 | -19 |
| `A2_LT_ONLY_S0` (`L=prior, T=prior, S=S0`) | 467 | 29.19 | 18.75 | **14.50** | 14.50 | 69.00 | -24 (`(L,T)` alone, `p=0.0039`) |
| `A4_MG_UNPLUGGED` | 462 | 28.88 | **16.50** | 15.50 | 14.50 | 69.00 | -29 (`p=0.0039` vs `A5_SHAM`) |
| **`A2_PRIOR_FULL` (`L=prior, T=prior, S=full`)** | **459** | **28.69** | **16.50** | 15.00 | **14.25** | 69.00 | **-32 (`12W/4T/0L`, `p=0.00024`)** |

- **2×2 Factorial Proof of Claim 1 Under Adversarial Shift:**
  - `A2_LT_ONLY_S0` vs `A0_BASE`: **`8W/8T/0L`, `-24` gates, `p = 0.00391`** (pure `(L, T)` works with `S` OFF!)
  - `A2_PRIOR_FULL` vs `S_ONLY_EMPTY_LT`: **`9W/7T/0L`, `-16` gates, `p = 0.00195`** (pure `(L, T)` adds significant gain on top of `S`!)
  - `A2_PRIOR_FULL` vs `A5_SHAM_S`: **`9W/7T/0L`, `-17` gates, `p = 0.00195`** (`SHAM` adds `0` / `-1` gate!)
  - `A2_PRIOR_FULL` vs `A1_ABC_XAG`: **`14W/1T/1L`, `-184` gates, `p = 0.00044`**!
  - `A4_MG_UNPLUGGED` vs `A2_PRIOR_FULL`: `1W/13T/2L`, `+3` gates worse (`p = 0.75`) — **3rd consecutive dataset confirming `COMPILED_PRIORS_ONLY` for static `k <= 4` macros at 4–6 inputs!**

---

## 3. Adversarial Questions for the Cross-Family Q3 Reviewer

As an independent adversarial reviewer (different model family from Builder/Proposer `claude-opus-5-5`), attack this sprint ruthlessly and answer:
1. **Claim 1 Audit:** Do you accept `CLAIM_1_CONFIRMED` (compiled LLM priors into deterministic LLM-free XAG machinery beating `BASE`, `ABC`, `SHAM`, `S_ONLY`, and `A6_NAKED` across 86 unseen tasks in 3 independent holdout datasets), or is there any remaining methodological flaw, baseline weakness (e.g. `ABC` AIG→XAG folding fairness), or confounding artifact that invalidates Claim 1?
2. **Claim 2 Audit:** Do you agree with the honest `COMPILED_PRIORS_ONLY` verdict (and our two-part diagnosis: small-sample `dev_val` over-pruning + low-arity prior saturation at 4–6 inputs)? Did we unfairly handicap `A4` or `A3` in any way that must be logged on the errata ledger?
3. **Accounting, Provenance, & RSO Audit:** Are the `$0.1198` Phase 2B `A6` meter erratum, the hardened 3-seed RSO fix (`6/6 REJECTED`), and the zero-shared-code semantic verification sufficient to certify reproducibility?
4. **Final Verdict & Highest-ROI Next Step:** Issue your binding Q3 closeout label (`CLAIM_1` / `CLAIM_2` / `CLAIM_3` / `NEGATIVE` / `INCONCLUSIVE`) and critique our proposed next frontier (evolving verified executable synthesis *algorithms* `S_mg` in Python on harder 6–10 input circuits or `3B-BV` via Z3, where a 20-entry static table cannot saturate).
