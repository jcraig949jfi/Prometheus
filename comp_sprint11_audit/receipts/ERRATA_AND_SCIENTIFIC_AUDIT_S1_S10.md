# Prometheus Sprint 11 — Phase A Errata, Independent Reference Reproduction & Scientific Audit (Sprints 1–10)

**Branch:** `sprint11/audit-attribution-discovery` (branched off `reset/verified-composition-2026-11` @ `be71271f3`; historical results and frozen `rso/` preserved untouched: `0` bytes modified)  
**Date:** 2026-11-28  
**Audit Standard:** Zero LLM participation in evaluation or adjudication; exact mathematical verification; equalized real wall-clock measurements alongside abstract operation budgets; distinct benchmark tasks only (repeated seeds never counted as independent tasks); no self-assigned scientific grades.

---

## 1. Mandatory Scientific Corrections (Sprints 9 & 10)

### 1.1 Correction #1 — Sprint 10 Kauers–Moosbauer (2023) Baseline Discrepancy (RESOLVED)
- **What Went Wrong in Sprint 10 (`comp_sprint10_alphatensor/s10_core.py`):** Our Sprint 10 baseline `A1_FLIP_GRAPH` remained stuck at rank **`27`** on `3×3×3` matrix multiplication over `F_2` and scored `820` across the 60 holdout tensors, whereas Kauers & Moosbauer (ISSAC 2023, *"Flip Graphs for Matrix Multiplication"*, official repo `github.com/jakobmoosbauer/flips`) famously reach rank **`23`** on `3×3×3` over `F_2`.
- **Root Cause Identified:** Sprint 10's `A1_FLIP_GRAPH` rebuilt `buckets` and called full `O(R)` `api["reduce_terms"]` on every single flip inside `OpBudget v3` (limiting it to ~2,500 flips total) and reset to `best` after only 120 stale flips, preventing it from traversing long flip-graph components.
- **Independent Reference Reproduction (`phase_a_km2023.py`, Stop Condition #1 — PASSED):** Our faithful, un-throttled pure-Python reference reproduction of Kauers & Moosbauer (2023) (O(1) incremental pair/mode hash maps, long path limit `L = 8,000`, pool-based restarts, and exact fused atomic Plus transitions `(u1^u2,v1,w1) + (u2,v1,w1^w2) + (u2,v1^v2,w2)`) independently reproduced EVERY published rank over `F_2`:
  - `matmul_2x2x2`: **7** (`0.50s`, `617k` flips)
  - `matmul_2x2x3`: **11** (`0.50s`, `77k` flips)
  - `matmul_2x3x3`: **15** (`1.00s`, `1.02M` flips)
  - `matmul_2x2x4`: **14** (`1.00s`, `149k` flips)
  - **`matmul_3x3x3`: 23** (`4.00s`, `551k` flips)
- **Wall-Clock-Equalized Re-Evaluation (`0.50s`/run, 3-seed median per distinct task, `N = 60` distinct Sprint 10 tasks):**

| Arm (Un-Throttled Python, Exact `0.50s`/run) | Matmul / Alg (12) | Planted (24) | Sparse Rand (24) | **All-60 Total** | Total Wall (180 runs) |
|---|---:|---:|---:|---:|---:|
| Sprint 10 Throttled `A1_FLIP_GRAPH` *(deprecated)* | 172 | 342 | 306 | 820 | 49.4s *(throttled)* |
| **Faithful Fused KM-2023 Reference (`0.50s`)** | **160** | **300** | **298** | **758** | **90.2s** |
| **Sprint 10 `S10_G0` (`mod_g0_flip`, `0.50s`)** | **157** | **292** | **291** | **740** | **89.2s** |

- **Corrected Statistical Verdict (`S10_G0` vs. Faithful Fused KM-2023 at Exact Matched Wall Time):**
  - **All 60 Distinct Tasks:** **`-18.0` multiplications** (`15W / 44T / 1L`, `p_two = 0.000427`) — down from Sprint 10's inflated `-75.0`!
  - **100% Procedural (48 Tasks):** **`-15.0` multiplications** (`12W / 35T / 1L`, `p_two = 0.002686`).
  - **Classic Matmul / Algebraic (12 Tasks):** **`-3.0` multiplications** (`3W / 9T / 0L`, **`p_two = 0.250` — NOT statistically significant**; `3×3×3` tied at median `24`, `2×2×2` tied at `7`, `2×2×3` tied at `11`, `poly_mul_4x4` tied at `14`, with `S10_G0` winning by 1 on `2×3×3`, `3×3×2`, `poly_mul_3x3`).
- **Retraction / Revision:** The Sprint 10 claim of "-75 multiplications (-9.1%) and -13 on classic matmul over published Kauers–Moosbauer (2023)" is **formally retracted and replaced** by the corrected wall-clock-equalized margin **`-18` overall (`p = 0.00043`)** and **no significant difference on classic matmul (`-3`, `p = 0.25`)**.

### 1.2 Correction #2 — Sprint 9 Polynomial Verifier Scope Clarification
- Sprint 9's exact `O(m · n^3)` `Z/8Z` verifier (`verify_poly_exact`) and `O(m · n^2)` Clifford completion (`synthesize_poly_clifford_t`) apply strictly to the **phase-polynomial / CNOT-dihedral (`{CNOT, T, Tdg, S, Sdg, Z}`) sub-class** (circuits without internal Hadamard `H` gates).
- They do **NOT** verify arbitrary universal `Clifford+T` circuits containing internal Hadamard `H` gates (where phase-polynomial linearity breaks across `H` boundaries and full unitary equivalence is QMA-complete in general). All Sprint 7–9 claims are strictly scoped to phase-polynomial `{CNOT, T, S, Z}` sub-circuits (the exact domain of published `T-par` 2014, `TODD` 2018, and `FastTODD` 2022).

### 1.3 Correction #3 — Distinct Task Counting & Self-Assigned Grades
- Across all future evaluations and this audit, repeated seeds (`{0, 1, 2}`) are used strictly to reduce per-task estimator variance (per-task median) and are **never** counted as independent benchmark tasks (e.g., Sprint 9 evaluated `N = 200` distinct circuits, Sprint 10 evaluated `N = 60` distinct tensors, Sprint 11 Phase B evaluates `N = 40` distinct tensors).
- Cross-family LLM reviews (`groq:openai/gpt-oss-120b`) are explicitly demoted to supplementary commentary; **no self-assigned or LLM-assigned grade** is used as a scientific success criterion.

---

## 2. Four-Bucket Taxonomy Audit Across Sprints 1–10 (Ruthless Separation of Novelty vs. Known Math)

| Program Element | Bucket 1: Previously Known Mathematics | Bucket 2: Implementation / Engineering Innovation | Bucket 3: Verified Empirical Performance Gain | Bucket 4: Genuinely Novel Algorithmic Discovery? |
|---|---|---|---|---|
| **Sprints 1–4 XAG (`mod_g1_peel → mod_g2_net`)** | Ashenhurst–Curtis decomposition, Davio expansion, XOR-AND graph rewriting (classical logic synthesis). | Incremental TFO-only mutable-netlist engine (`mod_g2_net`), deterministic `OpBudget` + `rso/` audit harness. | **YES:** Beats `A2_PRIOR_ONLY` (`p_Holm = 0.006`, Proc `0.013`) while running 30% faster in wall time. | **NO** — effective compositional implementation & coupling of known logic-synthesis techniques. |
| **Sprint 4–5 16-Bit Z3 BV (`S4-A`)** | Algebraic bit-vector identities, SMT-verified peephole superoptimization. | Isolated `z3.Context()` `rlimit` deterministic metering (`0.000` jitter), Law 4 word-width + `rlimit` accounting. | **YES:** Survives strict Law 4 metering (`29W/0L`, `p_two = 3e-6`; Proc `15W/0L`, `p_two = 6.1e-5`). | **NO** — verified engineering law + experience-driven heuristic synthesis. |
| **Sprint 5 Quantum CNOT (`S5-Q`)** | `GL(n, F_2)` Gaussian elimination, Patel–Markov–Hayes (2008) block synthesis, bidirectional beam search. | Transposition-deduplicated bidirectional incremental beam invoking G1+G0 (`142.5k` calls, `0.998×` wall parity vs G1). | **YES vs PMH 2008 (`-28.5%`, `p_Holm < 1e-6`)**; directional vs `A2` (`p_two = 0.0266`, `p_Holm = 0.133`, `3×` wall overhead vs `A2`). | **NO** — beam-search engineering over known `GL(n, F_2)` CNOT synthesis. |
| **Sprint 7 `Clifford+T` (`mod_g3_null_todd`)** | Heyfron–Campbell (2018) `TODD`, Amy–Mosca (2019) cubic tensor invariance, `RM(n-4, n)` weight-15 subspaces. | O(1) bilinear `sig[a^z]^sig[a]^sig[z]` table + Gray-code nullspace traversal + `2c+2` branch-and-bound. | **YES vs `TODD 2018` (`35W/0L`) & full-budget `A5_SHAM` (`0.88×` wall, `p_Holm = 0.00013`)**; Sprint 8 Study 1A proved `M1` throughput drove the win. | **NO** — high-throughput representation/engineering optimization of `TODD` (with `O(2^n)` scaling limit). |
| **Sprint 8 `C(n, 2)` `chi_z` + `g2_flat_kick`** | Heyfron–Campbell (2018) / Vandaele (2022) `chi_z` reduction; Reed–Muller `RM(n-4, n)` weight-15/16 codewords (affine 4-flats). | Involutive change-of-basis `M(z) = e_h` compressing `chi_z` to `C(n, 2)` bits; **greedy iterative doubling majority-voting 4-flat expansion (`g2_flat_kick`)**. | **YES:** Un-caveated `-87` vs full-budget `A2` (`p_Holm < 1e-6`), `-58` vs `FastTODD 2022` (`p_Holm = 0.0024`), confirmed on blind `N=100` (`n=8..12`: `-236` vs `A2`, `p_Holm < 1e-6`). | **PARTIAL (Algorithmic Heuristic Refinement, Prompt-Seeded):** The `RM(n-4, n)` 4-flat family was supplied in the prompt, **but** the 3-step greedy majority-voting flat-doubling heuristic (`g2_flat_kick`) was autonomously synthesized by the model and generalizes OOD to `n = 12..16`. |
| **Sprint 9 `Z/8Z` Polynomial Verifier** | Exact `Z/8Z` expansion `(y.x) = sum y_i x_i - 2 sum y_i y_j x_i x_j + 4 sum y_i y_j y_k x_i x_j x_k (mod 8)` — **previously known mathematics** (Amy–Mosca 2016/2019)! | Polynomial `O(m·n^3)` verifier & `O(m·n^2)` Clifford completion for phase-polynomial sub-class (`n = 12..16`). | Confirmed OOD transfer of `S8_G2` over `TODD 2018` (`-298`, `1.57×` faster); **lost to uncapped `FastTODD 2022` (`2.5×` wall)**. | **NO** — faithful implementation of known Amy–Mosca algebra. |
| **Sprint 10 AlphaTensor `F_2` (`mod_g0_flip`)** | Kauers–Moosbauer (2023) flip graphs & Plus transitions; GF(2) matrix rank; Strassen (1969) & Laderman (1976) ranks. | Incremental pair maps + 1-step lookahead + GF(2) slice-rank bucket compression — **all 3 explicitly prompted in `S10_API_DOC`!** | **Corrected (Phase A):** `-18` (`15W/1L`, `p = 0.00043`) vs faithful fused KM-2023 at equalized `0.50s` wall time (tied on classic Matmul 12, `p = 0.25`). | **NO** — prompt-guided implementation of supplied mathematical techniques (attribution tested directly in Phase B!). |

---

## 3. Honest Interim Verdict After Phase A

1. **What Is Solidly Verified:** The Prometheus engineering framework (Laws 1–4c, frozen `rso/` tamper-evident audit, exact offline verification) reliably produces **verified empirical performance gains** and **clean self-falsifications**. Even after fixing Sprint 10's throttled baseline to faithful fused Kauers–Moosbauer (2023) at equalized real wall-clock time (`89.2s` vs `90.2s`), `S10_G0` retains a statistically significant `-18` rank edge on procedural tensors (`p = 0.00043`), though classic matmul is tied (`p = 0.25`).
2. **What Was Overclaimed and Is Now Corrected:** (a) Sprint 10's `-75` / `-13 matmul` margin over KM-2023 was an artifact of a throttled baseline; (b) Sprint 9's `Z/8Z` verifier is previously known Amy–Mosca mathematics scoped strictly to phase-polynomial `{CNOT, T, S, Z}` circuits; (c) Sprint 10's algorithm was **prompt-guided implementation**, NOT autonomous discovery.
3. **Why Phase B (Attribution) Is Decisive:** Only a controlled minimal-spec (`UNGUIDED`) vs. mathematically guided (`GUIDED`) experiment can determine what mechanisms the model produces **without** prompt recipes.
