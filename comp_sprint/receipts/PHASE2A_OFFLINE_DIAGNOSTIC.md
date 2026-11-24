# Phase 2A Offline Diagnostic Receipt (Zero-Cost Arms + RSO Adversarial Kit)

**Date:** 2026-11-22  
**Branch:** `reset/verified-composition-2026-11`  
**Sealed Manifest SHA-256:** `9c02ddcaa5a1610801fe05f8307f221079923fb3bce86b230c8d99cc4f4322e7`  
**API Spend:** `$0.00` | **CPU Cost:** `$0.00009` (`6.31s` CPU, `8.09s` wall, `600` exact-verified runs)

---

## 1. RSO Adversarial Kit Verification (`comp_sprint_phase2` target)

Exercised `comp_sprint/reducer.py` directly through `rso.adversary.attacks` + `rso.adversary.core.run_variants` (zero edits to frozen `rso/`):

| Attack | Variant | Verdict |
|---|---|---|
| `DROP` | `drop_row_0` | **REJECTED** |
| `DUPLICATE` | `duplicate_row_0_over_1` | **REJECTED** |
| `REWRITE_DERIVED` | `tamper_summary` | **REJECTED** |
| `REWRITE_DERIVED` | `tamper_row_rebind_hash` | **REJECTED** |
| `SCRUB_ANSWER` | `corrupt_targets_hex` | **REJECTED** |
| `CONSTANT` | `constant_claim2_detector_on_null` | **REJECTED** |

**Result:** `6 REJECTED, 0 SURVIVED, 0 VACUOUS, 0 ERROR` (`10/10` tests pass in `1.67s`).

---

## 2. Phase 2A Zero-Cost Arm Results (Mean of Per-Task Medians Across 3 Paired Seeds)

| Suite | Split | `A0_BASE` | `A1_ABC_XAG` | `A3_ZERO_LLM` | `A5_SHAM` |
|---|---|---:|---:|---:|---:|
| `dev_structured` | dev | **12.6** | 14.1 | 14.5 | 13.1 |
| `dev_proc_shared` | dev | 20.2 | **19.4** | 20.5 | 20.2 |
| `holdout_structured` | untouched holdout | **20.0** | 21.9 | 22.0 | 20.6 |
| `holdout_proc_shared` | untouched holdout | 20.2 | **16.8** | 20.2 | 20.3 |
| `holdout_proc_rand` | untouched holdout | **39.7** | 41.4 | 40.2 | 39.7 |

*All 600 rows verified 100% truth-table exact and passed `verify_and_reduce`.*

---

## 3. Critical Scientific Diagnosis (Why Running Offline First Saved API Budget)

**Finding:** `A3_ZERO_LLM` scored **worse** than `A0_BASE` even on the **dev split** (`14.5` vs `12.6`), and `A5_SHAM` also slightly degraded `dev_structured` (`13.1` vs `12.6`).

**Root cause in `synth_base.py` (diagnosed strictly on `dev_structured`):**
1. **Non-monotonic greedy wavefront pollution:** `synth_base.py` Stage 1 commits any macro binding with positive Hamming-distance reduction (`ΔD > 0`) into the shared pool *before* Stage 2 Davio decomposition runs. Even a good macro adds 3–5 intermediate nodes that greedily steer Stage 1 away from optimal Davio splits, increasing final gate count rather than decreasing it!
2. **Missing structural cut-rewriting / library substitution:** Real logic synthesis (like Berkeley `ABC`) exploits a library `L` via **monotonic k-cut rewriting & shared subcircuit substitution**: enumerate `k`-input cuts (and shared multi-output cones) of the current verified DAG, match them against compact verified macros in `L` (modulo input permutation/polarity), and **accept a substitution ONLY when flattened strashed primitive gate count strictly decreases (`new_gates < old_gates`)**.

**Required Engineering Patch Before Spending Any LLM Dollars (`A2`, `A4`, `A6`):**
1. Upgrade the shared synthesizer (`synth_base.py`) to **Monotonic Cut-Rewriting + Library-Aware Substitution** (still 100% identical across `A0`, `A2`, `A3`, `A4`, `A5`, zero gate-count discount, exact budget charging).
2. Run a **Dev-Only Planted-Positive Instrument Check** (hand-built known good arithmetic/XAG macros on `dev_structured` ONLY — holdout untouched!): verify that a genuinely useful library produces a **clean, monotonic, repeatable gate-count drop over both `A0_BASE` and `A5_SHAM`** on dev *before* invoking any LLM API (`A2 PRIOR-ONLY`, `A4 MG-UNPLUGGED`, `A6 SHADOW-NAKED`).
