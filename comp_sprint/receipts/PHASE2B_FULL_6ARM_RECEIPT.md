# Phase 2B Receipt — Full 6-Arm Unplugged Evaluation + A6 Shadow Amortization (Track 3B-Boolean)

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11`  
**Sealed Manifest SHA-256:** `9c02ddcaa5a1610801fe05f8307f221079923fb3bce86b230c8d99cc4f4322e7`  
**Proposer Model Provenance:** **100% `claude-opus-5-5`** (via isolated `claude -p --model opus --tools "" --no-session-persistence`, 0 fallbacks)  
**Evaluation Mode:** **100% Offline, LLM Unplugged (`$0.00` LLM spend during holdout eval)** — 900 verified rows (6 arms × 50 tasks × 3 paired seeds `{0, 1, 2}`, budget = `1,200` eval units/task, wall time = `13.15s`)  
**Raw Packets (scratch):**
- Proposals: `PHASE2B_PROPOSALS.json` (`$1.747` total LLM spend: `A2 $0.073`, `A4 $0.218`, `A6 $1.456`)
- Full 900-row Eval: `PHASE2B_FULL_PACKET.json` (`verify_and_reduce`: **900/900 rows verified exact**)

---

## 1. Executive Verdict on the Four-Rung Claim Ladder (`SYNTHESIS_AND_ADJUDICATION.md` §3.1)

| Rung | Claim | Phase 2B Verdict | Evidence Summary |
|---|---|---|---|
| **Claim 1** | **Crystallization** (LLM knowledge compiles into compact, deterministic, LLM-free machinery beating `BASE`, `ABC`, `ZERO-LLM`, and `SHAM`) | **CONFIRMED (`PASS`)** | Unplugged `A2_PRIOR_ONLY` (`F = $0.073`, `v_M = $2.3e-7/task`) beats `A0_BASE` (**16W/14T/0L**, `p = 0.00014`), `A5_SHAM` (**15W/15T/0L**, `p = 0.00023`), `A3_ZERO_LLM` (**14W/15T/1L**, `p = 0.00065`), Berkeley `ABC 1.01` (**23W/2T/5L**, `p = 0.00004`), **and** beats direct `claude-opus-5-5` (`A6_SHADOW_NAKED`, `21.29` vs `23.57` mean gates on the 14/15 common solved set, with `N* = 0.70` tasks!). |
| **Claim 2** | **Experience-Derived Acquisition Beyond Compiled Priors** (**Gate `G-Comp`**: `A4` or `A3` strictly beats `A0`, `A2 (PRIOR-ONLY)`, and `A5 (SHAM)` on ≥1 stratum including Stratum 2 procedural) | **FAIL — `COMPILED_PRIORS_ONLY`** | `A4_MG_UNPLUGGED` **did NOT beat `A2_PRIOR_ONLY`**. On untouched holdout (30 tasks), `A4` **lost** to `A2` (**2W/19T/9L**, `+8` gates worse, `p(A4 < A2) = 0.9946`; on Stratum 2 `holdout_proc_shared`: **0W/5T/5L**, `16.2` vs `15.6`). `A4` overfit to `dev_structured` (`10.8` vs `11.0`) by spending 3 of its 12 macro slots on dev-specific 4-input blocks (`popcount4`, `sort4_hi3`, `mul2x2_hi`), evicting general 2-gate 3-input atoms (`and_or`, `xor3`, `xor_and`). |
| **Claim 3** | **Generational Compounding (`A1 → A2 → A3`)** | **GATED (HELD BY `G-Comp`)** | Per §3.4 hard kill rule: *"If `A4 ≈ A2`, log honest `COMPILED_PRIORS_ONLY` result and diagnose before spending Week 3."* |
| **Claim 4** | **Non-Human Novelty** | **OUT OF SCOPE** | Explicitly deferred per v2.0 protocol. |

> **Why the Pre-Registered `A2_PRIOR_ONLY` Control Paid for Itself 100x Over:**  
> Without `A2_PRIOR_ONLY`, we would have looked at `A4_MG_UNPLUGGED` beating `A0_BASE` (`p = 0.00195`), `A5_SHAM` (`p = 0.00391`), `A3_ZERO_LLM` (`p = 0.043`), Berkeley `ABC` (`-4.3` gates/task), AND direct `A6_SHADOW_NAKED` (`21.57` vs `23.57`, `N* = 2.08`), and **falsely declared Claim 2 proven!** The mandatory `A2_PRIOR_ONLY` arm caught an exact `COMPILED_PRIORS_ONLY` + dev-overfitting artifact on the very first run.

---

## 2. Full 6-Arm Per-Stratum Results (Mean of Per-Task Medians Across 3 Paired Seeds, Lower Primitive XAG Gates = Better)

All circuits are flattened to primitive `{AND, XOR}` gates (inverters free, zero macro-call gate discount) and verified 100% bit-exact by exhaustive truth-table check.

| Arm | LLM at Eval | `dev_structured` (10) | `dev_proc_shared` (10) | **`holdout_structured` (10)** | **`holdout_proc_shared` (10)** | **`holdout_proc_rand` (10)** | **All Holdout Sum (30)** |
|---|---|---:|---:|---:|---:|---:|---:|
| **`A0_BASE`** | OFF | 11.8 | 15.9 | 17.4 | 16.5 | 35.1 | **690** |
| **`A1_ABC_XAG`** (Berkeley ABC 1.01) | OFF | 14.1 | 19.4 | 21.9 | 16.8 | 41.4 | **801** |
| **`A2_PRIOR_ONLY`** (`$0.073`, 0 tasks) | **OFF** | 11.0 | **15.5** | **16.4** | **15.6** | **34.4** | **664** (`-26`) |
| **`A3_ZERO_LLM`** (deterministic miner) | OFF | 11.7 | 15.6 | 17.2 | 16.5 | 34.8 | **685** (`-5`) |
| **`A4_MG_UNPLUGGED`** (`$0.218`, 2 dev rds) | **OFF** | **10.8** | 15.6 | **16.4** | 16.2 | 34.6 | **672** (`-18`) |
| **`A5_SHAM`** (size-matched optimal sham) | OFF | 11.8 | 15.9 | 17.4 | 16.5 | 35.0 | **689** (`-1`) |

### Paired Statistical Tests (Exact Wilcoxon Signed-Rank on Per-Task Medians)

| Comparison | Stratum | W / T / L | Sum Gate Δ | Mean Gate Δ | One-Sided `p (<)` | Two-Sided `p (≠)` |
|---|---|---:|---:|---:|---:|---:|
| **`A2_PRIOR_ONLY` vs `A0_BASE`** | **ALL HOLDOUT (30)** | **16 / 14 / 0** | **-26.0** | **-0.867** | **0.00014** | **0.00028** |
| **`A2_PRIOR_ONLY` vs `A5_SHAM`** | **ALL HOLDOUT (30)** | **15 / 15 / 0** | **-25.0** | **-0.833** | **0.00023** | **0.00045** |
| **`A2_PRIOR_ONLY` vs `A3_ZERO_LLM`** | **ALL HOLDOUT (30)** | **14 / 15 / 1** | **-21.0** | **-0.700** | **0.00065** | **0.00130** |
| **`A2_PRIOR_ONLY` vs `A1_ABC_XAG`** | **ALL HOLDOUT (30)** | **23 / 2 / 5** | **-137.0** | **-4.567** | **0.00004** | **0.00008** |
| `A4_MG_UNPLUGGED` vs `A0_BASE` | ALL HOLDOUT (30) | 9 / 21 / 0 | -18.0 | -0.600 | 0.00195 | 0.00391 |
| `A4_MG_UNPLUGGED` vs `A5_SHAM` | ALL HOLDOUT (30) | 8 / 22 / 0 | -17.0 | -0.567 | 0.00391 | 0.00781 |
| **`A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY`** | **ALL HOLDOUT (30)** | **2 / 19 / 9** | **+8.0** | **+0.267** | **0.99463** | 0.05566 |
| **`A2_PRIOR_ONLY` vs `A4_MG_UNPLUGGED`** | `holdout_proc_shared` (10) | **5 / 5 / 0** | **-6.0** | **-0.600** | **0.03125** | 0.06250 |
| `A4_MG_UNPLUGGED` vs `A2_PRIOR_ONLY` | `holdout_structured` (10) | 2 / 6 / 2 | 0.0 | 0.000 | 0.68750 | 1.00000 |
| `A3_ZERO_LLM` vs `A5_SHAM` | ALL HOLDOUT (30) | 3 / 27 / 0 | -4.0 | -0.133 | 0.12500 | 0.25000 |

### Holdout Task-Level Highlights (All 16 Holdout Tasks Where Any Library Improved on `A0_BASE`)

| Suite | Task | `A0_BASE` | `A1_ABC` | `A2_PRIOR` | `A3_ZERO` | `A4_MG` | `A5_SHAM` | `A2−A0` | `A4−A2` |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `holdout_structured` | `s1_hold_add3` | 13 | 14 | **12** | 13 | 13 | 13 | -1 | +1 |
| `holdout_structured` | `s1_hold_popcount6` | 24 | 53 | 18 | 24 | **17** | 24 | -6 | **-1** |
| `holdout_structured` | `s1_hold_sbox_ascon` | 21 | 22 | 20 | 21 | **19** | 21 | -1 | **-1** |
| `holdout_structured` | `s1_hold_barrel_rot4` | 22 | 24 | **20** | **20** | 21 | 22 | -2 | +1 |
| `holdout_proc_shared` | `s2_hold_shared_01_n5m3` | 12 | 10 | **11** | 12 | 12 | 12 | -1 | +1 |
| `holdout_proc_shared` | `s2_hold_shared_02_n5m3` | 18 | 20 | **17** | 18 | 18 | 18 | -1 | +1 |
| `holdout_proc_shared` | `s2_hold_shared_03_n5m3` | 11 | 9 | **9** | 11 | **9** | 11 | -2 | 0 |
| `holdout_proc_shared` | `s2_hold_shared_04_n5m3` | 17 | 14 | **16** | 17 | 17 | 17 | -1 | +1 |
| `holdout_proc_shared` | `s2_hold_shared_05_n6m4` | 21 | 19 | **19** | 21 | 21 | 21 | -2 | +2 |
| `holdout_proc_shared` | `s2_hold_shared_09_n6m4` | 20 | 25 | **18** | 20 | 19 | 20 | -2 | +1 |
| `holdout_proc_rand` | `s2_hold_rand_00_n5m3` | 37 | 48 | **35** | 36 | **35** | 37 | -2 | 0 |
| `holdout_proc_rand` | `s2_hold_rand_02_n5m3` | 38 | 48 | **37** | 38 | 38 | 38 | -1 | +1 |
| `holdout_proc_rand` | `s2_hold_rand_05_n5m3` | 35 | 39 | **34** | 35 | 35 | 35 | -1 | +1 |
| `holdout_proc_rand` | `s2_hold_rand_06_n5m3` | 36 | 38 | **35** | 36 | **35** | 36 | -1 | 0 |
| `holdout_proc_rand` | `s2_hold_rand_08_n5m3` | 36 | 41 | 35 | **34** | 35 | 35 | -1 | 0 |
| `holdout_proc_rand` | `s2_hold_rand_09_n5m3` | 33 | 44 | **32** | 33 | **32** | 33 | -1 | 0 |

---

## 3. `A6_SHADOW_NAKED` Amortization Curve & Censored Failures

15 predeclared untouched holdout tasks (`[0::2]` across all 3 holdout strata), direct `claude-opus-5-5` with exact truth-table verifier feedback (up to 2 attempts/task).

- **Solved Rate:** **`14/15` (93.3%)** — **1 censored failure** (`s2_hold_rand_06_n5m3` failed both attempts). All offline arms solved **15/15 (100%)**.
- **Common Solved Set (`14/15`) Mean Primitive Gates:**
  - **`A2_PRIOR_ONLY` (unplugged): `21.29`** *(best overall)*
  - **`A4_MG_UNPLUGGED` (unplugged): `21.57`**
  - `A0_BASE`: `21.79`
  - `A6_SHADOW_NAKED` (direct Opus 5.5): `23.57`
  - `A1_ABC_XAG` (Berkeley ABC): `25.00`
- **Striking Qualitative Split in `A6_SHADOW_NAKED`:**
  - On **textbook human crypto/structured tasks**, direct Opus 5.5 was extraordinary: `s1_hold_sbox_skinny` = **`8` gates** (vs `14` for `A0/A2/A4` and `20` for `ABC`!), `s1_hold_mul3x2` = `14` (vs `15`), `s1_hold_add3` = `12` (tie with `A2`).
  - On **random procedural truth tables** (`holdout_proc_rand`), direct Opus 5.5 collapsed: `48, 50, 49, FAIL, 37` gates vs unplugged `A2_PRIOR_ONLY`'s `35, 37, 34, 35, 35` gates (`-11.25` gates/task worse even on the 4 it solved!).
- **Exact Break-Even Amortization `N* = F / (v_L − v_M)`:**
  - Direct naked marginal cost (including failed attempts in `v_L`): `v_L = $0.105057 / task` (`$1.456` across 15 tasks / 21 LLM proposals, 14 accepted).
  - Unplugged marginal CPU cost (`$0.05/core-hr`): `v_M = $2.3 × 10⁻⁷ / task` (`450,000×` cheaper per task).
  - **`A2_PRIOR_ONLY`:** `F = $0.073166` → **`N* = 0.70 tasks`** (amortizes on task #1!).
  - **`A4_MG_UNPLUGGED`:** `F = $0.218183` (R1 `$0.1024` + R2 `$0.1157` + SAT compression/dev screening CPU) → **`N* = 2.08 tasks`**.

---

## 4. Mechanistic Diagnosis: Why `A2_PRIOR_ONLY` Beat `A4_MG_UNPLUGGED`

Post-hoc leave-one-out knockout on seed 0 (purely diagnostic on the already-frozen libraries; never used for tuning) reveals the exact mechanism down to the gate:

### Library Diff (`A2_PRIOR_ONLY` vs `A4_MG_UNPLUGGED`)
- **5 Exact Shared Truth-Table Core Priors:** `half_adder` (2→2, 2g), `compare_swap` (2→2, 2g), `full_adder` (3→2, 5g), `sort3` (3→3, 8g), `maj3` (3→1, 4g) (+ functionally variant `mux2` and `and_xor_and`).
- **`A2`-only (general low-arity atoms):** `and_or` (3→1, **2g**), `xor3` (3→1, **2g**), `xor_and` (3→1, **2g**), `eq2bit` (4→1, 3g), `add2bit` (4→3, 7g).
- **`A4`-only (dev-overfitted 4-input blocks):** `popcount4` (4→3, **9g**), `sort4_hi3` (4→3, **9g**), `mul2x2_hi` (4→3, **7g**), `xor2_and` (4→1, 3g), `ao22` (4→1, 3g).

### Leave-One-Out Knockout Contribution on Holdout (Seed 0; Positive Δ = Gates Lost When Macro Removed)

| `A2_PRIOR_ONLY` Macro (in→out, gates) | Holdout Δ Total | `(struct, proc_sh, proc_rnd)` | `A4_MG_UNPLUGGED` Macro (in→out, gates) | Holdout Δ Total | `(struct, proc_sh, proc_rnd)` |
|---|---:|---|---|---:|---|
| **`and_or`** (3→1, 2g) | **+8** | `(0, +6, +2)` | `compare_swap` (2→2, 2g) | +2 | `(0, 0, +2)` |
| **`full_adder`** (3→2, 5g) | **+4** | `(+4, 0, 0)` | `ao22` (4→1, 3g) | +2 | `(0, +2, 0)` |
| **`xor3`** (3→1, 2g) | **+3** | `(+2, +1, 0)` | `popcount4` (4→3, 9g) | +1 | `(+1, 0, 0)` |
| **`compare_swap`** (2→2, 2g) | **+2** | `(0, 0, +2)` | `xor2_and` (4→1, 3g) | +1 | `(+1, 0, 0)` |
| **`xor_and`** (3→1, 2g) | **+2** | `(0, 0, +2)` | `full_adder` (3→2, 5g) | 0 | redundant w/ `popcount4` |
| **`half_adder`** (2→2, 2g) | **+1** | `(0, 0, +1)` | `sort4_hi3` (4→3, 9g) | **0** | **dead weight (dev overfit)** |
| `mux2` (3→1, 3g) | -1 | `(0, 0, -1)` (beam contention) | `mul2x2_hi` (4→3, 7g) | **0** | **dead weight (dev overfit)** |
| Remaining 5 macros | 0 | unused/redundant | Remaining 5 macros | 0 | unused/redundant |

### Three Root Causes Diagnosed
1. **Dev-Structured Overfitting Under a Hard 12-Macro Slot Cap:** `A4`'s sleep selector maximized raw `dev_structured + dev_proc_shared` sum. Because `dev_structured` includes `popcount5`, `sort4`, and `mul2x2`, Claude Opus 5.5 traded `A2`'s universal 2-gate 3-input atoms (`and_or`, `xor3`, `xor_and` — responsible for **+13 gates** of holdout generalization!) for dev-memorized 4-input blocks (`sort4_hi3`, `mul2x2_hi`, `popcount4`), yielding `-2` gates on dev and **`+8` gates regression on holdout**.
2. **Engine Representation Ceiling (Why `A0/A2/A4` All Stuck at 14 on `sbox_skinny` While `A6` Got 8):**
   Our v2 `synth_base.py` only uses macros via (i) **state-compressing functional factorization** (`|image(W')| < |image(W)|`, which **cannot fire on bijective layers** like 4-bit S-boxes `skinny`/`gift`/`present` or invertible GF(16) steps where `|image| = 16`!), and (ii) **single-output 4-cut NPN rewriting** (which cannot synthesize multi-output shared quadratic/linear layers like S-box decompositions or multiplier partial-product trees). Consequently, static macros alone have a narrow ceiling on structured non-compressive circuits, and virtually zero mechanism to let `A4` improve the *synthesizer algorithm/rewrites* (`T_mg, S_mg`) beyond a 12-macro lookup table.
3. **`A4` Started Cold Without Inheriting `A2` or Using Stratified Dev Cross-Validation:** Starting `A4` from scratch instead of evolving `(L, T, S)` on top of `A2` with a dev-holdout (or Stratum-2-weighted) selection gate meant any dev-specific macro that saved 1 gate on `dev_structured` could evict a general prior atom.

---

## 5. Cognitive Accounting Ledger (4-Row Unified Work Meter)

| Phase / Arm | Eval Units | SAT Calls | CPU Seconds | LLM Calls (Acc/Tot) | USD Cost (`$0.05/core-hr` + API) |
|---|---:|---:|---:|---:|---:|
| **Sleep — `A2_PRIOR_ONLY`** (propose + SAT compress) | 0 | 18 | 0.009s | 1 / 1 | `$0.073166` |
| **Sleep — `A4_MG_UNPLUGGED`** (2 rounds + SAT compress + dev screen) | 154,799 | 46 | 3.091s | 2 / 2 | `$0.218183` |
| **Offline Eval — All 6 Arms (900 rows, LLM OFF)** | 2,524,425 | 67 | 11.198s | 0 / 0 | `$0.000156` |
| **Shadow — `A6_SHADOW_NAKED`** (15 holdout tasks, direct Opus 5.5) | 16 | 0 | 0.000s | 14 / 21 | `$1.456053` |
| **TOTAL PHASE 2B SPRINT SPEND** *(cap: `$100.00`)* | **2,679,240** | **131** | **14.298s** | **17 / 24** | **`$1.747558`** (`1.75%` of cap) |

---

## 6. Live RSO Adversarial Audit on the Real 900-Row Packet

Running the frozen `rso/adversary` kit directly against `PHASE2B_FULL_PACKET.json`:
- `DROP / drop_row_0` → **REJECTED**
- `DUPLICATE / duplicate_row_0_over_1` → **REJECTED**
- `REWRITE_DERIVED / tamper_summary` → **REJECTED**
- `SCRUB_ANSWER / corrupt_targets_hex` → **REJECTED**
- `CONSTANT / constant_detector_on_sham` → **REJECTED**
- `REWRITE_DERIVED / tamper_row_rebind_hash` → **SURVIVED (real audit catch!)**  
  *Cause:* With 3 seeds per task (`[g, g, g]`), tampering 1 seed's `gate_count` to `1` and recomputing `row_sha256` leaves the per-task **median** unchanged (`median([1, g, g]) == g`), so `compute_summary` (which only aggregated task medians) did not change.  
  *Status & Fix:* Our actual Phase 2B packet is untampered (generated directly by `phase2_llm.py` with 900/900 live truth-table checks). Before any next run, `reducer.py` must include **all-seed mean/min/max** (or exact `rows_merkle_sha256` + circuit witness verification) in the checked summary so single-seed row tampering cannot hide behind a median.

---

## 7. Gate `G-Comp` Ruling & Next-Step Options (Awaiting Operator Decision)

Per `SYNTHESIS_AND_ADJUDICATION.md` §3.4, **Gate `G-Comp` is HELD (`COMPILED_PRIORS_ONLY`)**. We do **NOT** blindly burn Week 3 running 3 generations of a static 12-macro prompt that already loses to `A2_PRIOR_ONLY`!

Three clean, bounded options for the Operator:
1. **Option 1 (Recommended — Fix the Representation & Selection Bottleneck, Then Re-Test Claim 2 on the Exact Same Frozen Holdout? Wait — Holdout Discipline!):**
   - **CRITICAL ANTI-LEAKAGE NOTE:** We have now **looked at** the 30-task Phase 2B holdout (`9c02ddca...`) and diagnosed why `A4` lost (`popcount4`/`sort4_hi3`/`mul2x2_hi` vs `and_or`/`xor3`/`xor_and`, plus `sbox_skinny`). Therefore, per scientific rigor, if we upgrade the architecture/loop to test Claim 2 properly, we MUST **treat the current 50-task manifest as Phase 2B historical receipt** and generate a **FRESH sealed Phase 2C/Phase 3 holdout seed** (zero leakage!) before claiming Claim 2 or Claim 3.
   - **Targeted Architectural Upgrade to Unlock Real Claim 2 (Experience > Compiled Priors):**
     1. **Fix the `A4` selection loop:** Give `A4` an explicit **internal dev/val split** (train on half of dev, validate on the other half, including Stratum-2 procedural) and allow **additive/prune evolution starting from `A2_PRIOR_ONLY`** (or a larger library with utility pruning so dev-specific blocks cannot evict universal atoms).
     2. **Unlock genuine `(L, T, S)` mechanism learning beyond static 4-input macros:** Add **bijective/multi-output DAG rewriting** (e.g., learned **XAG rewrite rules `T`** over 3–4 gate patterns / multi-output shared linear-layer factoring — which directly targets why `A6` hit **8 gates** on `sbox_skinny` while static macros froze at `14`!) AND allow `A4` to propose **verified rewrite rules + multi-output subcircuit decompositions** mined from actual failure/gap traces on dev.
     3. **Close the 1/6 RSO 3-seed median hole** in `comp_sprint/reducer.py`.
2. **Option 2 — Declare Honest Claim 1 Victory & Close Track 3B-Boolean (Pivot to Phase 4 Cross-Family Q3 Audit Now):**
   - Accept the crisp empirical result we already have on disk (`Claim 1 CONFIRMED` at `p = 0.00014`, `N* = 0.70`, beating Berkeley `ABC` and direct `Opus 5.5` offline; `Claim 2 = COMPILED_PRIORS_ONLY` for static macro libraries), hand the frozen receipts to Gemini/Astra for Q3 verification, and decide whether the real frontier ROI is `(L, T, S)` rewrite/search evolution in 3B-Boolean or moving to a richer substrate (`3B-BV` / algorithm synthesis).
3. **Option 3 — Targeted Ablation First (`<$0.50`, 15 min) on `A4`'s Overfitting Hypothesis:**
   - Before touching `synth_base.py`, test the single cleanest causal hypothesis on a fresh sealed procedural+structured holdout: does **`A4` initialized from `A2` + internal dev-val selection + utility pruning** beat `A2_PRIOR_ONLY` on Stratum 2 procedural? That isolates *selection overfitting* vs *representation ceiling* in 15 minutes for `<$0.50`.
