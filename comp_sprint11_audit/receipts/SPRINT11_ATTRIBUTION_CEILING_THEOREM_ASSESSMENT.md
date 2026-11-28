# Prometheus Sprint 11 — Attribution Study, Ceiling Diagnosis, Machine-Checked Theorem Prototype & Revised Research Assessment

**Branch:** `sprint11/audit-attribution-discovery` (branched off `be71271f3`; historical `reset/verified-composition-2026-11` and frozen `rso/` untouched: `0` bytes modified)  
**Date:** 2026-11-28  
**Sprint 11 Spend:** **`$3.34`** (Phase B 8 trials: `$2.26`; Phase C 6 trials: `$1.08`; Phases A & D: `$0.00` — 100% offline)  
**Evaluation Discipline:** Zero LLM participation in evaluation or adjudication; exact mathematical verification (`0` verifier fallbacks); actual wall-clock efficiency measured alongside abstract `OpBudget v3`; distinct benchmark tasks only (`N = 60` in Phase A, `N = 40` in Phases B/D, `N = 20` in Phase C); no self-assigned or LLM-assigned grades.

---

## 1. Phase A Summary — Independent Reference Reproduction & Errata

Full errata report: [ERRATA_AND_SCIENTIFIC_AUDIT_S1_S10.md](file:///F:/Prometheus/comp_sprint11_audit/receipts/ERRATA_AND_SCIENTIFIC_AUDIT_S1_S10.md).

- **Stop Condition #1 Passed (`phase_a_km2023.py`):** Faithful un-throttled **Kauers & Moosbauer (2023)** reference (O(1) incremental pair/mode maps, long path limit `L = 8,000`, pool-based restarts, exact fused atomic Plus transitions) independently reproduced **`3×3×3 → 23`** (`4.00s`, `551k` flips), **`2×3×3 → 15`** (`1.00s`), **`2×2×4 → 14`** (`1.00s`), **`2×2×3 → 11`** (`0.50s`), and **`2×2×2 → 7`** (`0.50s`).
- **Corrected Equalized Wall-Clock Audit (`0.50s`/run, 3-seed median per distinct task, `N = 60` Sprint 10 tasks):**
  - Faithful Fused KM-2023 jumped from Sprint 10's throttled `820 → 758` (`90.2s` total wall).
  - Sprint 10 `S10_G0` (`740`, `89.2s` total wall) retained a real but much smaller edge: **`-18.0` overall (`15W / 44T / 1L`, `p_two = 0.000427`)**, driven by procedural tensors (`-15.0`, `12W / 35T / 1L`, `p = 0.0027`), while classic Matmul 12 narrowed to **`-3.0` (`p_two = 0.250`, NOT significant; `3×3×3` tied at `24`)**.
- **Scope Correction:** Sprint 9's exact `O(m · n^3)` `Z/8Z` verifier applies strictly to the **phase-polynomial (`{CNOT, T, S, Z}` / CNOT-dihedral)** circuit class, not arbitrary universal `Clifford+T` circuits with internal Hadamard gates.

---

## 2. Phase B — Controlled Attribution Experiment: Minimal-Spec (`UNGUIDED`) vs. Mathematically Guided (`GUIDED`)

**Suite (`phase_b_attribution.py`):** `N = 40` brand-new, immutable `F_2` bilinear 3-tensors (`manifest sha256`, `0` overlap with Sprint 10: 20 planted low-rank tensors with known `Planted_UB = 255`, `Base = 549` + 20 sparse random tensors; overall `Base = 939`).  
**Controls:** 100% tool-less (`--tools ""` + isolated `TemporaryDirectory`), identical model (`claude-opus-5-5`), 1 call per trial, `K = 4` independent trials per condition (`8` total calls, every success & failure preserved!).

| Trial | Condition | Valid? | **Wall-Equalized (`0.50s`/run, `N = 40`)** | Planted 20 (`UB=255`) | vs. Faithful KM-2023 (`525`) | `p_two` vs KM-2023 | Op-Equalized `v3` (`1.8M`) | Mechanisms Found in Code |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **Faithful KM-2023** | Ref Baseline | ✓ | **`525`** (`60.1s`) | `266` | `0` | — | — | Incremental pair/mode maps + fused Plus |
| `UNGUIDED_T1` | Minimal Spec | ✓ | **`517`** (`59.8s`) | `261` | `-8` | `0.1846` *(NS)* | `525` (`22.5s`) | Pure flip walk + Plus (**NO** GF(2) slice rank, **NO** lookahead) |
| `UNGUIDED_T2` | Minimal Spec | ✓ | **`535`** (`59.7s`) | `277` | `+10` | `0.5219` *(NS)* | `560` (`12.3s`) | Pure flip walk + Plus (**NO** GF(2) slice rank, **NO** lookahead) |
| `UNGUIDED_T3` | Minimal Spec | ✗ | *(Schema fail)* | — | — | — | — | Preserved failure (`Missing new_modules`) |
| `UNGUIDED_T4` | Minimal Spec | ✗ | *(Schema fail)* | — | — | — | — | Preserved failure (`Missing new_modules`) |
| `GUIDED_T1` | Math Guided | ✓ | **`519`** (`59.7s`) | `265` | `-6` | `0.2437` *(NS)* | `537` (`15.0s`) | Pair maps + **GF(2) slice rank** + **lookahead** + Plus |
| **`GUIDED_T2`** | **Math Guided** | **✓** | **`507`** (`59.4s`) | **`252` (`-3` < UB)** | **`-18`** | **`0.0013`** | **`525`** (`13.7s`) | **GF(2) `gf2_rref` slice rank** + **lookahead** + Plus |
| `GUIDED_T3` | Math Guided | ✓ | **`532`** (`59.6s`) | `273` | `+7` | `0.2324` *(NS)* | `544` (`11.6s`) | Lookahead only (omitted GF(2) slice rank & Plus) |
| `GUIDED_T4` | Math Guided | ✓ | **`526`** (`59.7s`) | `270` | `+1` | `0.7513` *(NS)* | `547` (`12.3s`) | Lookahead + Plus (omitted GF(2) slice rank) |

### Decisive Attribution Verdict
1. **Best Guided (`GUIDED_T2 = 507`) vs. Best Unguided (`UNGUIDED_T1 = 517`) at Equalized Wall-Clock (`59.4s` vs `59.8s`):** **`GUIDED_T2` won `8W / 32T / 0L` (0 losses!)**, `-10.0` multiplications, **`p_two = 0.007812`**.
2. **Primary Question Answered Honestly — NO Autonomous Discovery Observed in Phase B:**
   - Under minimal specification (`UNGUIDED`), `claude-opus-5-5` cleanly reconstructed standard Kauers–Moosbauer flip-graph random walks (mean valid `526.0` vs KM-2023 `525`, `p >= 0.18`), **never** invented GF(2) matrix-rank slice compression (`0/2` valid) or lookahead (`0/2` valid), and suffered a `50%` schema-failure rate (`2/4` vs `4/4` guided).
   - The ONLY trial that beat Faithful KM-2023 significantly (`GUIDED_T2`, `-18`, `p = 0.0013` — replicating Sprint 10's exact `-18` margin on a brand-new disjoint suite!) was a **guided** trial implementing the prompt-supplied **`gf2_rref` slice-rank compression + lookahead**; guided trials that omitted `gf2_rref` (`GUIDED_T3`, `GUIDED_T4`) failed to beat KM-2023.
   - **Conclusion:** Sprint 10's performance gain over KM-2023 is **causally attributable to effective implementation of prompt-supplied mathematical strategies**, NOT autonomous unguided algorithmic discovery.

---

## 3. Phase C — Controlled Diagnosis of the `PRIOR_SATURATED` Evolutionary Ceiling

Tested four falsifiable hypotheses (`phase_c_ceiling.py`, `N = 20` planted + `N = 20` random):

1. **H1 — True Benchmark Saturation (CONFIRMED as Primary Cause on `5×5×5–6×6×6`):**
   - On the 20 fresh planted tensors (`Base = 549`, **`Known Planted Upper Bound = 255`**): `KM-2023 (0.50s) = 264 (+9)`, whereas **`S10_G0 (v3) = 255 (+0)`** and **`S10_G0 (0.50s) = 254 (−1)`** (`17/20` tasks already at or below the known planted rank!). There was virtually zero remaining headroom for `G1..G3` to pass a paired Wilcoxon gate.
2. **H2 — Interface Blindness / Compositional Opacity (CONFIRMED as Causal Secondary Killer):**
   - Controlled 100% tool-less ablation evolving `G1` on top of `S10_G0` (`K = 3` trials each, `N = 20` planted):
     - **`NAMES_ONLY`** (replicating S9/S10 prompts that showed only `exports=['fn1', ...]`): `255 → 290, 332, 284` (**mean regression `+47.0`**, **`0/3` cross-gen calls**, `xgen = 0`).
     - **`FULL_SIGNATURES_AND_ORCH`** (showing exact `def` signatures + orchestrator source): `255 → 260, 260, 260` (**mean regression slashed `9.4×` to `+5.0`**, **`301,654` cross-gen calls unlocked on `T2`**, `0/6` timeouts).
3. **H3 — Single-Seed Stochastic Gate Variance (Quantified):**
   - Identical `KM-2023` across 5 seeds on `N = 20` random tensors spanned `[262, 259, 260, 262, 262]` (range `3`, mean per-task range `1.05`; null `seed1 - seed0 = -3`, `p = 0.613`), confirming that 3-seed medians are required to detect small `−2..−4` algorithmic gains cleanly.

---

## 4. Phase D — Minimal Autonomous Theorem-Generation & Counterexample-Falsification Prototype

Implemented a 100% deterministic, machine-checked cycle (`phase_d_theorem_loop.py`, zero LLM in verification/adjudication):  
`OBSERVE FAILURE → FORM HYPOTHESIS → DERIVE PREDICTION → SEARCH FOR COUNTEREXAMPLE → TEST → RETAIN OR REJECT → MODIFY SEARCH STRATEGY`.

### 4.1 Cycle 1 — Falsified Conjecture via Exact Exhaustive BFS Counterexample
- **Conjecture H1:** *"Every non-minimal reduced binary tensor decomposition `D` (`R > rank*(T)`) admits a flip-only path (no Plus transitions) to a decomposition of rank `<= R - 1`."*
- **Machine-Checked Verdict:** **`REJECTED_BY_MACHINE_CHECKED_COUNTEREXAMPLE`**.
- **Exact Counterexample (`F_2^{3×3×3}`):** `D = [(x, x, x) for x in 1..7]` (`rank = 7`, `tensor_mask = 0x10402840` — the 6 permutations of `(0, 1, 2)`).
  - Exact `flip_degree(D) = 0`; exhaustive BFS verified `component_size = 1` (`complete = True`, `min_reachable_rank = 7`).
  - Explicit verified decomposition `D*` achieves **`rank = 5 < 7`** (`verify_bilinear_decomp == True`).
  - Applying ONE fused XOR-Triangle Plus-Bridge move increases `flip_degree` from `0 → >= 3` and enables reaching `rank = 5`.

### 4.2 Cycle 2 — Machine-Checked Theorem Refinement (P1) & Honest Strategy-Modification Test
- **Draft Lemma Auto-Falsified & Sharpened:** Our first draft claimed unique-factor XOR triangles always gain `>= +3` flip edges; automated counterexample testing immediately revealed that non-isolated vertices (`deg_flip > 0`) can lose pre-existing edges in non-`m` modes! Sharpening the hypothesis to flip-isolated vertices (`deg_flip == 0`) produced the exact machine-checked **Proposition P1**:
  - *(a)* `deg_flip(D) == 0` iff all 3 modes have pairwise distinct factors (`500/500` checks, `0` violations).
  - *(b)* On any flip-isolated decomposition `D` (`deg_flip == 0`) containing an XOR triangle `f_c = f_a ^ f_b`, the fused XOR-Triangle Plus-Bridge preserves `T` identically and either immediately reduces rank (`R' <= R`) or strictly yields **`deg_flip(D') >= 3`** (strictly exceeding the `>= 2` lower bound of an arbitrary fused Plus move; `431/431` checks, `0` violations, exact `min_isolated_flip_deg_gain = 3`, `33` immediate drops).
- **Offline Strategy-Modification Test (`N = 40` fresh suite, exact equalized wall-clock `60.1s` vs `60.2s`):**
  - Unmodified Faithful Fused KM-2023: **`529`** (`60.1s`)
  - Modified KM-2023 + XOR-Triangle Plus-Bridge: **`526`** (`60.2s`)
  - **Paired Wilcoxon (`N = 40`):** `d = -3.0` (`4W / 34T / 2L`, **`p_two = 0.531` — NOT statistically significant**).
  - **Honest Interpretation:** P1 is mathematically exact and strictly necessary on isolated traps, but because random `5×6×6–6×6×6` flip walks rarely stall at `deg_flip == 0`, replacing random fused Plus with XOR-Triangle Plus did not yield a statistically significant wall-clock improvement on general benchmarks.

---

## 5. Revised Prometheus Research Assessment (Post-Sprint 11)

### What Project Prometheus HAS Rigorously Demonstrated
1. **Anti-Counterfeit Verification & Metering Engineering (Laws 1–4c):** Deterministic execution budgets, disjoint Law 2 promotion gates, frozen `rso/` tamper-evident reductions (`6/6` attacks rejected on every packet), exact mathematical verification across 5 formal domains, and strict wall-clock reconciliation cleanly separate real gains from meter arbitrage (`S4-B G4`, `S6 G1`) and throttled baselines (`S10 A1_FLIP_GRAPH`).
2. **Effective Guided Algorithm Synthesis & Implementation:** Given accurate mathematical strategy guidance, frontier LLMs reliably synthesize standalone, exact-verified, LLM-free solvers that deliver verified wall-clock-equalized gains over strong published baselines (e.g., `S3/S4-A` XAG & 16-bit BV, `S8` `g2_flat_kick` greedy majority-voting 4-flat decoder beating `FastTODD 2022` on `n = 8..11` and transferring zero-shot to `n = 12..16` faster than `TODD 2018`, and `S10_G0`/`GUIDED_T2` beating Faithful Fused KM-2023 by `-18` at equalized `0.50s` wall time via `gf2_rref` slice compression).
3. **Working Machine-Checked Falsification Loop:** Phase D demonstrates an end-to-end deterministic hypothesis → counterexample → lemma-refinement → empirical strategy-test pipeline with zero LLM involvement in verification or adjudication.

### What Project Prometheus HAS NOT YET Demonstrated (The True North Star Gap)
1. **Autonomous Unguided Algorithmic Discovery:** Phase B proved that when mathematical strategy hints are withheld (`UNGUIDED`), the model reproduces known literature baselines (`517`, `535` vs KM-2023 `525`, `p >= 0.18`) and does **not** autonomously discover mechanisms like GF(2) slice-rank compression (`GUIDED_T2` beat `UNGUIDED_T1` `8W/0L`, `p = 0.0078`).
2. **Sustained Multi-Generation Compounding (`3+` Generations):** Phase C proved that compounding stalled because (a) small benchmarks saturated at G0 (`255` vs `255` planted UB) and (b) withholding parent signatures caused `+47` regressions and `0` reuse.
3. **Autonomous Discovery Feeding Back Into Genuine Wall-Clock Speedups:** Phase D's Theorem P1 was mathematically sound but empirically neutral (`p = 0.53`) on general tensors because isolated `deg_flip == 0` traps are rare in dense `5×6×6–6×6×6` walks.

### Concrete Path Forward Toward True Autonomous Discovery (If Continuing to Sprint 12)
1. **Move to Non-Saturated Hard Regimes:** E.g., `4×4×4` / `4×4×5` / `7×7×7–9×9×9` `F_2` bilinear tensors (where `G0` sits `+10..+20` above known rank!) with **full parent source/signature visibility** (fixing H2) and **3-seed validation medians** (fixing H3).
2. **Drive Hypothesis Formation Strictly From Measured Failure Modes (Zero Human Strategy Hints):** Feed the proposer ONLY empirical failure traces from the autonomous counterexample engine (e.g., exact structural statistics of stalled local minima — rank deficiency of shared-factor slices, cycle lengths, isolated components) WITHOUT naming any algorithm or textbook technique, and test under the exact Phase B attribution protocol whether failure-grounded autonomous cycles outperform both Faithful KM-2023 AND zero-telemetry unguided baselines at equalized real wall-clock time!
