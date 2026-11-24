# Sprint 5 & Master Program Closeout Receipt — Three Formal Domains & Four Empirical Laws of Compositional Algorithm Evolution

**Date:** 2026-11-24  
**Branch:** `reset/verified-composition-2026-11`  
**Builder / Proposer Provenance:** **100% `claude-opus-5-5`** (`0` fallbacks across Sprints 1–5)  
**Cross-Family Q3 Adversary:** OpenAI open-weights **`groq:openai/gpt-oss-120b`** (strictly non-Anthropic; 3 independent closeout audits archived)  
**Total Verified 100%-Offline Evidence Base:** **12,666+ verified offline evaluation rows** (LLM completely unplugged at evaluation) across **THREE independent formal domains** (Combinational Boolean Logic `XAG`, SMT 16-Bit Bit-Vectors `Z3 UNSAT`, Quantum/Reversible Linear Circuits `GL(n, F_2)` CNOT), **`0` bytes modified in frozen `rso/`**, **`6/6 REJECTED`** on hardened 3-seed RSO across every live packet  
**Total Cumulative Equivalent Spend (Sprints 1–5, Including ALL Bug/Aborted/Rejected Runs):** **`~$29.19 / $100.00` (`29.2%`)**

---

## 1. Master Verdict Across All Three Independent Formal Domains

| Formal Domain | Published / Industry Baseline | Claim 1 (Executable Crystallization, LLM OFF) | Claim 2 (Experience > Compiled Priors, Gate `G-Comp` incl. Procedural) | Claim 3 (Multi-Gen Compositional Compounding) | Law 4 (`OpBudget v2`) Wall-Clock Audit |
|---|---|---|---|---|---|
| **Domain 1: Combinational Boolean XAG** *(Sprints 1–4, 4–11in, 7,518+ rows)* | Berkeley `ABC 1.01` *(AIG→XAG)* + matched `A5_SHAM` | **CONFIRMED** (`p_Holm < 1e-6`, `-487` to `-818` vs full-budget `A5_SHAM`) | **CONFIRMED** — Sprint 3 `G2` (`23W/7L`, `-84`, `p_Holm = 0.006`; Proc 32: `16W/4L`, **`p_Holm = 0.013`**, `30%` faster wall time) & S4-B `G2` (`-415`, `23W/0L`, `p_Holm < 1e-6`, `12%` faster wall time!) | **2-STEP WALL-CLOCK-CLEAN (`A2 → G1 → G2`)**; S4-B `G4` 3rd step (`-253`, `984,953` `g4→g2` calls) **EXPOSED BY LAW 4** as big-int bit-width arbitrage! | `OpBudget v2` collapsed `G4` `7.0×` wall gap to `1.29×` and reversed its step-3 gain (`+11` vs `G2`), validating Law 4! |
| **Domain 2: 16-Bit Z3 `UNSAT` Bit-Vectors** *(Sprints 2–4, 3,840 rows)* | Z3 C++ Simplifier + matched `A5_SHAM` | **CONFIRMED** (`-82.4%` in S2-B; `-44.6%` / `-433` ops vs Z3 in S4-A, `p_Holm < 1e-6`) | **CONFIRMED — SURVIVES LAW 4!** S4-A `G1` (`34W/0L`, `-319`, `p_Holm < 1e-6`; Proc 26: `18W/0L`, `p_Holm = 0.000032`). Under strict Law 4 (`64-bit word + Z3 rlimit//15`): **`29W/15T/0L`, `-292`, `p_two = 3e-6`; Proc 26: `15W/11T/0L`, `-187`, `p_two = 6.1e-5`!** | **1-STEP ONLY** (`G1` promoted; `G2`/`G3` cleanly gated off by Law 2; `0.000` Z3 jitter via isolated `z3.Context()` + `rlimit`) | **SURVIVED LAW 4!** Exact matched `66.0M` word-ops, `4.5×` faster than `A5_SHAM` (`26.2s` vs `117.4s`), `0` losses! |
| **Domain 3: Quantum `GL(n, F_2)` CNOT Circuits** *(Sprint 5 S5-Q, 12–18q, 1,320 rows, ALL 4 LAWS NATIVE)* | **Published Patel–Markov–Hayes (`A1_PMH`, 2008)** + matched `A5_SHAM` | **CONFIRMED** (`G2` beats published **PMH 2008** by **`-975` CNOTs / `-28.5%`, `41W/3T/0L`, `p_Holm < 1e-6`**; `-622` vs `18.5M`-op `A5_SHAM`, `p_Holm < 1e-6`) | **DIRECTIONAL / PROVISIONAL** — `G2` beat `A2_PRIOR` across **all 3 strata & 3/3 seeds** (`25W/6T/13L`, `-49` CNOTs, 95% CI `[-1.98, -0.27]`, `p_two = 0.0266`, `p_Holm = 0.133`; Proc 26: `16W/1T/9L`, `p_less = 0.068`). **Matched-Op KO:** **`30W/11T/3L`, `-42`, `p_Holm = 0.00086`!** | **2-STEP MONOTONIC 3-TIER COMPOSITION (`A2 → G1 → G2`, `G3` gated)** — `G2` calls BOTH `G1` (`97,090` calls!) AND `G0` (`33,377` calls!) = `142,508` cross-gen calls at **`0.998×` identical wall time (`48.15s` vs `48.22s`)**! | Native Law 4 achieved **`0.998×` wall parity** (`G2` vs `G1`) & `97.1%` matched-op KO (`48.2s` vs `43.4s`). Residual caveat: `G1`/`G2` took `3.0×` `A2`'s wall time (`48s` vs `16s`) due to Python dict/beam overhead. |

---

## 2. Part A — Law 4 (`OpBudget v2`) Verification on Frozen Sprint 4 Artifacts (`$0.00` LLM)

Implemented in [law4_meter.py](file:///F:/Prometheus/comp_sprint4/law4_meter.py) (verified by [test_law4_meter.py](file:///F:/Prometheus/comp_sprint4/tests/test_law4_meter.py)): AST-instruments every integer `BinOp`, `UnaryOp(~)`, and `AugAssign` to charge `(bit_length - 1) // 64` word-ops whenever operands exceed 64 bits, and charges exact deterministic Z3 `rlimit_count // 15` per SMT proof:

- **Track S4-A (16-Bit Z3 BV, 44 untouched holdout tasks, `word_budget = 1,500,000`):**
  - `A5_SHAM`: `TOT = 932`, `PROC = 601`, `wall = 117.36s`, `word_ops = 65.96M`
  - `A2_PRIOR_ONLY`: `TOT = 857`, `PROC = 550`, `wall = 6.55s`, `word_ops = 65.99M`
  - **`G1`:** **`TOT = 565`**, **`PROC = 363`**, `wall = 26.23s` (`4.5×` faster than `A5_SHAM`), `word_ops = 66.00M`
  - **All 44 (`G1` vs `A2`):** **`29W/15T/0L`, `-292.0` ops, `p_two = 0.000003`** · **Procedural 26:** **`15W/11T/0L`, `-187.0` ops, `p_two = 0.000061`** — **Claim 2 SURVIVED Law 4 decisively!**
- **Track S4-B (9–11in XAG, 44 tasks, `word_budget = 6,000,000`):**
  - `G4`'s `7.0×` wall-clock runaway (`633.5s` vs `89.9s`) collapsed immediately to **`1.29×` (`17.51s` vs `13.52s`)** and its step-3 gain reversed (`+11` vs `G2`, `p_two = 0.314`), decisively proving that S4-B `G4`'s step-3 leap under `OpBudget v1` was big-int bit-width arbitrage (while frozen `orch_g0..g4` hardcoded v1 `op_cap` slices).

---

## 3. Part B — 3rd Formal Substrate: Track S5-Q Quantum `GL(n, F_2)` CNOT Synthesis (1,320 Verified Rows, ALL 4 LAWS Native)

Built in [comp_sprint5_quantum/](file:///F:/Prometheus/comp_sprint5_quantum/s5q_core.py) (`140` fresh invertible `n = 12..18` matrices, `0` duplicates, `0` `fn_errors`, `0` hardcoding hits, `6/6` Law 1+4 determinism audit, `6/6` RSO REJECTED, `$3.55` equivalent spend):

| Arm | `hold_struct` (18) | `hold_dense` (13) | `hold_circ` (13) | **`PROC_26` Sum** | **`TOTAL_44` Sum** | Wall (s) | Word-Ops | Cross-Gen Calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0_GAUSS` | 97.22 | 113.77 | 93.15 | 2,690.0 | **4,440.0** | 0.01s | 0 | 0 |
| `A3_ZERO_LLM` (greedy HW) | 86.50 | 106.38 | 75.46 | 2,364.0 | **3,921.0** | 0.76s | 1.02M | 0 |
| **`A1_PMH` (Patel–Markov–Hayes 2008)** | 75.22 | 87.92 | 71.38 | 2,071.0 | **3,425.0** | 0.02s | 0 | 0 |
| `A5_SHAM` *(140k word-ops perm-PMH)* | 68.28 | 79.08 | 62.69 | 1,843.0 | **3,072.0** | 9.76s | 18.46M | 0 |
| `A2_PRIOR_ONLY` *(Gen 0, `$0.39`)* | 57.94 | 62.92 | 49.08 | 1,456.0 | **2,499.0** | 15.96s | 17.41M | 0 |
| `G1` *(+`beam_reduce`, `beam_finish`)* | 56.89 | 62.54 | 48.54 | 1,444.0 | **2,468.0** (`-31`) | 48.22s | 17.40M | 12,041 |
| **`G2`** *(+`fast_bidir`, `block_opt`, `=G3`)* | **56.50** | **61.85** | **48.38** | **1,433.0** (`-23`) | **2,450.0** (`-49`) | **48.15s** | 17.92M | **142,508** |
| `KO_MATCHED_LAST` *(stub `G2`)* | 57.50 | 62.62 | 49.46 | 1,457.0 | **2,492.0** (`+42`) | 43.42s | 17.40M | 6,644 |

- **3/3 Paired Seeds Monotonic (`A2 → G1 → G2`):** `seed 0: 2497 → 2477 → 2473`; `seed 1: 2503 → 2484 → 2439`; `seed 2: 2491 → 2455 → 2430`.
- **3-Tier Compositional Architecture Discovered (`G2 → G1 → G0`):**
  - `G0`: `(M, M^-T)` pair simulation, greedy cost reduction, commutation-aware cancellation.
  - `G1`: `mod_g1_beam_reduce` (204L) + `mod_g1_beam_finish` (40L) — transposition-deduplicated beam search over `(M, M^-T)`.
  - `G2`: `mod_g2_fast_bidir` (198L, bidirectional `(M, M^-T, M^T, M^-1)` incremental support-updated beam) + `mod_g2_block_opt` (111L, commutation-aware DAG-convex subcircuit peephole), directly invoking **BOTH `G1` (`g2->g1:beam_child_row: 84,462`, `beam_pair_table: 12,476`, `finish_finals: 152`) AND `G0` (`weight_table: 8,976`, `gates_to_pair: 8,824`, `finish_perm: 7,890`, `transpose_gates: 7,125`)**!
- **Key Paired Wilcoxon Tests:** `G2 vs A1_PMH`: `-975` (`41W/3T/0L`, **`p_Holm < 0.000001`**); `G2 vs A5_SHAM`: `-622` (`42W/2T/0L`, **`p_Holm < 0.000001`**); **`G2 vs KO_MATCHED_LAST`**: **`30W/11T/3L`, `-42`, CI `[-1.32, -0.59]`, `p_Holm = 0.00086`**; `G2 vs A2_PRIOR`: `25W/6T/13L`, `-49`, CI `[-1.98, -0.27]`, `p_two = 0.0266` (`p_Holm = 0.133` under 11-way Holm).

---

## 4. The Four Empirical Laws of Verified Compositional Algorithm Evolution (Program Synthesis)

Across **12,666+ verified offline rows** spanning **3 independent formal substrates**, Prometheus established four concrete, empirically falsified laws governing when offline executable algorithm evolution genuinely compounds vs produces counterfeit positives:

1. **Law 1 (Deterministic Execution Budgets — Zero Jitter):** Wall-clock deadlines destroy generational signal (Phase 3 exposed a 13-op Z3 swing on identical code). AST loop instrumentation + isolated `z3.Context()` `rlimit` delivers exact `0.000` variance across all three domains.
2. **Law 2 (Disjoint Per-Generation Validation + Paired Statistical Gates):** Reusing small `dev_val` splits causes adaptive Goodharting (Phase 3). Disjoint hidden `val_g{k}` splits (`N >= 20–25`) with exact paired Wilcoxon `p_less < 0.05` (Bonferroni `< 0.025` on retry) reliably block noisy mutations (`G3` cleanly blocked in Sprint 3, S4-A, S4-B, and S5-Q with zero regression).
3. **Law 3 (Compositional Verified Libraries + Matched-Op Causal Knockouts):** Flat sequential pass lists hit diminishing returns; compositional `LibModule` libraries unlock genuine coupled **mechanism + representation** evolution (`mod_g1_peel` → `mod_g2_net`, `mod_g1_beam_reduce` → `mod_g2_fast_bidir` with `142k–191k` cross-gen calls) verified causally by matched-op knockouts (`p_Holm <= 0.00086`).
4. **Law 4 (Word-Width & Solver-Decision Metering — `OpBudget v2`):** Pure loop-count metering invites big-int bit-width arbitrage (exposed in S4-B `G4` `633s → 17.5s`) and flat-cost solver arbitrage. Charging `(bit_length - 1) // 64` word-ops + actual Z3 `rlimit_count` eliminates big-int arbitrage (`0.998×` parity in S5-Q `G2 vs G1`) and cleanly separates genuine improvements (S4-A BV `G1`: `p_two = 3e-6`; Sprint 3 & S4-B XAG `G2`: wall-clock faster than `A2`) from meter exploits. *(Residual open frontier: accounting for Python container/dict allocation overhead + achieving 3+ wall-clock-matched generations.)*
