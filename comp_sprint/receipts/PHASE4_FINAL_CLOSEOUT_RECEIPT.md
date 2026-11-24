# Phase 4 Final Closeout Receipt — 28-Day Verified Composition Sprint (Track 3B-Boolean)

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11` (branched cleanly from `origin/main` @ `9884ac934`)  
**Builder / Proposer Model Family:** Anthropic `claude-opus-5-5` (`100%` verified via CLI `modelUsage`, `0` silent fallbacks)  
**Cross-Family Q3 Adversary:** OpenAI open-weights `groq:openai/gpt-oss-120b` (strictly non-Anthropic; verbatim review archived in scratch `PHASE4_Q3_CLEAN_groq.md`; mechanical audit in [phase4_q3_audit.py](file:///F:/Prometheus/comp_sprint/phase4_q3_audit.py))  
**Total Verified Sprint API + CPU Spend:** **`$2.369 / $100.00` cap (`2.37%`)** *(corrected for `$0.1198` Phase 2B `A6` exception-handler erratum)*  
**Frozen `rso/` Integrity:** `0` bytes modified (`git diff -- rso/` empty; **67/67** frozen `rso` tests passing; **20/20** `comp_sprint` tests passing; **6/6** live hardened 3-seed RSO attacks REJECTED on the real 1,368-row packet)

---

## 1. Binding Final Closeout Verdict (Four-Rung Claim Ladder)

| Rung | Claim | Binding Closeout Label | Scope & Evidence |
|---|---|---|---|
| **Claim 1** | **Crystallization** (LLM knowledge compiles into compact, deterministic, LLM-free machinery) | **`CLAIM_1` — CONFIRMED** *(Cross-Family Q3 Adversary label: **`CLAIM_1`**)* | Confirmed across **3 independent untouched holdout datasets (86 total unseen tasks, 2,268+ verified rows, LLM 100% UNPLUGGED at eval)** after strict two-sided **Holm–Bonferroni** family-wise error correction (`p_Holm <= 0.031` on all 10 primary Claim-1 comparisons; zero 95% bootstrap CIs cross zero) and a **2×2 factorial** isolating `(L, T)` from `S`. Amortizes vs direct `claude-opus-5-5` (`A6_SHADOW_NAKED`, 14/15 solved) at **`N* = 0.70` tasks** while achieving lower mean gates (`21.29` vs `23.57`). |
| **Claim 2** | **Experience Beyond Compiled Priors** (**Gate `G-Comp`**: `A4` or `A3` > `A0`, `A2`, `A5` incl. Stratum 2 procedural) | **`COMPILED_PRIORS_ONLY`** *(Honest Negative / Gate Held)* | Failed Gate **`G-Comp`** across **all 3 independent holdout datasets** (`A4_MG_UNPLUGGED` worse than `A2_PRIOR_ONLY` by `+8` gates in Phase 2B, `+16` in Phase 2C, `+3` in Phase 4 shift; all `p_Holm >= 0.167`). Scoped strictly to **static `k <= 4` macro/rewrite libraries on 4–6 input Boolean circuits** (with Phase 2C 12-task `dev_val` over-pruning logged as a documented confounder). |
| **Claim 3** | **Generational Compounding (`A1 → A2 → A3`)** | **`NOT_RUN_GATED_BY_G_COMP`** | Properly halted per v2.0 §3.4 hard kill rule without wasting Week 3 compute. |
| **Claim 4** | **Non-Human Novelty** | **`OUT_OF_SCOPE`** | Explicitly deferred per v2.0 protocol. |

---

## 2. Complete Statistical Evidence (Two-Sided Wilcoxon + Holm–Bonferroni Across All 13 Primary Tests + 95% Paired Bootstrap CIs)

| Dataset & Comparison | `N` Unseen Tasks | Mean Δ Gates (Negative = Better) | 95% Paired Bootstrap CI | Exact Two-Sided `p` | **Holm–Bonferroni `p_Holm`** | Outcome |
|---|---:|---:|---:|---:|---:|---|
| **P2B (30): `A2_PRIOR` vs `A0_BASE`** | 30 | `-0.867` | `[-1.333, -0.500]` | `0.00028` | **`0.00340`** | Claim 1 PASS |
| **P2B (30): `A2_PRIOR` vs `A5_SHAM`** | 30 | `-0.833` | `[-1.300, -0.467]` | `0.00045` | **`0.00496`** | Claim 1 PASS |
| **P2B (30): `A2_PRIOR` vs `A3_ZERO`** | 30 | `-0.700` | `[-1.167, -0.333]` | `0.00130` | **`0.01041`** | Claim 1 PASS |
| P2B (30): `A4_MG` vs `A2_PRIOR` | 30 | `+0.267` | `[+0.033, +0.500]` | `0.05566` | `0.16699` | Claim 2 FAIL |
| **P2C (40): `A2_PRIOR` vs `A0_BASE`** | 40 | `-1.850` | `[-2.450, -1.300]` | `<0.00001` | **`0.00006`** | Claim 1 PASS |
| **P2C (40): `A2_PRIOR` vs `A5_SHAM`** | 40 | `-0.775` | `[-1.325, -0.325]` | `0.00141` | **`0.01041`** | Claim 1 PASS |
| **P2C (40): `A2_PRIOR` vs `A3_ZERO`** | 40 | `-0.775` | `[-1.300, -0.350]` | `0.00099` | **`0.00895`** | Claim 1 PASS |
| P2C (40): `A4_MG` vs `A2_PRIOR` | 40 | `+0.400` | `[+0.000, +0.875]` | `0.07910` | `0.16699` | Claim 2 FAIL |
| **P4 Shift (16): `A2_FULL` vs `A0_BASE`** | 16 | `-2.000` | `[-3.062, -1.125]` | `0.00049` | **`0.00496`** | Shift PASS |
| **P4 Shift (16): `A2_FULL` vs `S_ONLY`** | 16 | `-1.000` | `[-1.812, -0.438]` | `0.00391` | **`0.02344`** | `(L,T)` > `S` |
| **P4 Shift (16): `A2_FULL` vs `A5_SHAM_S`** | 16 | `-1.062` | `[-1.875, -0.438]` | `0.00391` | **`0.02344`** | `(L,T)` > SHAM |
| **P4 Shift (16): `A2_LT_S0` vs `A0_BASE`** | 16 | `-1.500` | `[-2.688, -0.500]` | `0.00781` | **`0.03125`** | `(L,T)` alone |
| P4 Shift (16): `A4_MG` vs `A2_FULL` | 16 | `+0.188` | `[-0.312, +0.812]` | `0.75000` | `0.75000` | Claim 2 FAIL |

### Phase 4 Adversarial Shift 2×2 Factorial Decomposition (16 Brand-New Shifted Tasks: NOEKEON/KLEIN/TWINE/SKINNY-inv/PRESENT-inv, Threshold/CLZ/Hamming/Mod3, Priority/Barrel/Gray, 6-Input Uniform Random)

| Factor Configuration | Total Gates (16) | Mean | Δ vs `A0_BASE` | Isolates |
|---|---:|---:|---:|---|
| `A1_ABC_XAG` (Berkeley ABC 1.01 + AIG→XAG fold) | 643 | 40.19 | `+152` | Conventional AIG baseline |
| `A0_BASE` (`L=∅, T=∅, S=S0`) | 491 | 30.69 | `0` | Floor |
| `S_ONLY_EMPTY_LT` (`L=∅, T=∅, S=full`) | 475 | 29.69 | `-16` | Pure strategy `S` (linear precond) |
| `A5_SHAM_S` (`L=sham, T=sham, S=full`) | 476 | 29.75 | `-15` | `S` + optimal random `(L,T)` = `+1` (null!) |
| `A2_LT_ONLY_S0` (`L=prior, T=prior, S=S0`) | 467 | 29.19 | **`-24`** | Pure compiled `(L,T)` with `S` OFF |
| `A4_MG_UNPLUGGED` (`L=mg, T=mg, S=full`) | 462 | 28.88 | `-29` | Experience-refined (over-pruned) |
| **`A2_PRIOR_FULL` (`L=prior, T=prior, S=full`)** | **459** | **28.69** | **`-32`** | Full compiled priors `(L, T, S)` |

---

## 3. Permanent Caveats & Errata Ledger (From Cross-Family Q3 Audit)

1. **`A1_ABC_XAG` Baseline Fairness Caveat:** Berkeley `ABC 1.01` is an **AIG-native** synthesizer (`{AND, NOT}`), and `industry_abc.py` folds its AIG output to XAG (`{AND, XOR, NOT}`) post-hoc. That makes `A1_ABC_XAG` weaker than a native XAG optimizer (e.g., Mockturtle). Claim 1 therefore rests primarily on the apples-to-apples comparisons within our identical XAG engine (`A2_PRIOR_ONLY` vs `A0_BASE`, `S_ONLY_EMPTY_LT`, `A3_ZERO_LLM`, and `A5_SHAM`, all `p_Holm <= 0.023`).
2. **Modest Effect Size & 4–6 Input Scope:** Compiled-prior savings over `S_ONLY` / `A5_SHAM` average `0.8–1.1` gates/task (`1.5–2.0` gates over `A0_BASE`) on 4–6 input circuits. This sprint certifies Claim 1 strictly within this verified regime; extrapolation to 8–16 input circuits is untested.
3. **Phase 2C `dev_val` Over-Pruning Confounder on Claim 2:** `prune_artifact_on_val` pruned `13/20` of `A4`'s macros on a 12-task `dev_val` split lacking adders/sorters, handicapping `A4` on `sort5` (`+5`), `add3_sat` (`+6`), and `holdout_proc_rand` (`+5`). Claim 2's `COMPILED_PRIORS_ONLY` verdict is therefore scoped honestly to the tested Phase 2B/2C static `k <= 4` protocols — NOT a universal impossibility proof.
4. **Cost-Accounting Erratum (`$0.1198`):** In Phase 2B `A6_SHADOW_NAKED`, one failed-parse attempt spent `$0.119795` on `claude -p` before throwing a parser exception; `shadow_naked["total_usd"]` (`$1.576`) and `N*` (`0.70` / `2.08`) captured it accurately, but `sleep_meter` logged `$0.0` instead of `$0.119795`. Fixed in both `phase2_llm.py` and `phase2c_lts.py`; true corrected sprint total = **`$2.369 / $100.00`**.
5. **Phase 2B Live RSO Audit Catch & Phase 2C Fix:** Phase 2B's live RSO audit revealed a single-seed tamper hole behind 3-seed medians; `reducer.py` was hardened with all-seed `sum_all_gates`/`min_all_gates`/`max_all_gates`, achieving **`6/6 REJECTED, 0 SURVIVED, 0 VACUOUS`** on the real 1,368-row Phase 2C packet.

---

## 4. Reproducibility Receipts & Next High-ROI Frontier

### Complete Receipt Chain (`comp_sprint/receipts/`)
- [PHASE0_EXIT_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE0_EXIT_RECEIPT.md) — Clean branch, auto-committer audit, 222-class NPN4 exact calibration matching Knuth TAOCP Vol. 4A (`23.77s`, `0` mismatches)
- [PHASE1_QUALIFICATION_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE1_QUALIFICATION_RECEIPT.md) — Berkeley `ABC 1.01` build + sealed Phase 1/2B manifest (`9c02ddca...`)
- [PHASE2A_OFFLINE_DIAGNOSTIC.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE2A_OFFLINE_DIAGNOSTIC.md), [PHASE2A_INSTRUMENT_QUALIFIED.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE2A_INSTRUMENT_QUALIFIED.md), [PHASE2A_V2_OFFLINE_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE2A_V2_OFFLINE_RECEIPT.md) — Monotonic v2 engine upgrade + dev-only planted-positive qualification + `$0` 600-row baseline
- [PHASE2B_FULL_6ARM_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE2B_FULL_6ARM_RECEIPT.md) — 900-row 6-arm + `A6_SHADOW_NAKED` (`N* = 0.70` tasks, `Claim 1 PASS`, `Claim 2 = COMPILED_PRIORS_ONLY`)
- [PHASE2C_LTS_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE2C_LTS_RECEIPT.md) — 1,368-row full `(L, T, S)` on fresh sealed manifest (`b14f790e...`), `6/6` hardened RSO audit
- [PHASE4_Q3_AUDIT_PACKET.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE4_Q3_AUDIT_PACKET.md) & this closeout receipt

### Recommended Next Frontier (Post-Sprint Roadmap)
The single highest-ROI insight of this sprint is **why** `A2_PRIOR_ONLY` saturated Track 3B-Boolean at 4–6 inputs: a 20-entry static `k <= 4` library covers nearly the entire low-arity Boolean primitive space on shot #1. To genuinely unlock **Claim 2 (Experience > Compiled Priors)** and **Claim 3 (Generational Compounding)** next:
1. **Promote the evolvable artifact from static lookup tables to verified executable synthesis/rewriting *algorithms* (Python code `S_mg`, run 100% offline with LLM unplugged)** on **harder 6–10 input multi-output circuits** (where native XAG Mockturtle/SAT-window search has 30–100+ gates of headroom) or **8/16-bit Z3 bit-vector superoptimization (`3B-BV`)**.
2. **Pre-block the #1 counterfeit positive flagged by the Q3 Adversary:** Enforce primitive-level zero-discount flattening (`and_count + xor_count == gate_count` / primitive SMT-LIB op count), matched wall-clock/eval budgets across `A2_PRIOR_ONLY` and `A4_MG_UNPLUGGED`, strict additive preservation of prior baselines (no small-sample over-pruning), and 100% procedural zero-LLM holdouts.
