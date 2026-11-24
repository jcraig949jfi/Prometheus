# Phase 2A Instrument Qualification Receipt (`synth_base.py` v2 — Dev Only)

**Date:** 2026-11-23  
**Branch:** `reset/verified-composition-2026-11`  
**Holdout Access:** **ZERO** (all design, calibration, and planted-positive checks ran strictly on `dev_structured`)  
**Test Suite:** `12/12` `comp_sprint/tests` passing (including `6/6` RSO Adversarial Kit rejections + exact NPN4 wire-map verification + dev-only planted positive)

---

## 1. Mechanism Upgrade (`comp_sprint/synth_base.py` v2)

Replaced the non-monotonic Hamming wavefront with a **100% monotonic, zero-discount, shared three-stage engine** (identical across `A0`, `A2`, `A3`, `A4`, `A5`):

1. **Multi-Order Shared Positive/Negative Davio Initialization** (`A0_BASE`): deterministic multi-order decomposition with shared structural hashing (`StrashBuilder`).
2. **Exact Macro Functional Factorization (Selective Irreversibility over `library L`)**:
   - Applies verified multi-output macros `M(subset) -> Z` that **strictly compress reachable input states (`|image(W')| < |image(W)|`)** while **preserving 100% of target output distinctions** (exact lossless factorization).
   - Composes up to 6 macro layers via a macro-diverse beam, finishes residuals via don't-care-aware Davio, flattens to primitive `{AND, XOR}` gates (zero discount), and accepts ONLY when `new_gates < best.gate_count()`.
3. **Exact NPN4 Leaf Mapping + Monotonic `k`-Cut (`k <= 4`) Single- & Multi-Output DAG Rewriting**:
   - Indexes single-output macros by exact NPN4 class (`compose_npn4_wire_map`, verified across 40 random NPN4 pairs) and multi-output macros by output-pair NPN classes.
   - Accepts rewrites strictly monotonically (`new_gates < best.gate_count()`).

---

## 2. Dev-Only Planted-Positive Instrument Check (`dev_structured`, 10 tasks, seed 0)

Planted artifact = 3 verified 2-output macros (`half_adder` 2g, `full_adder` 5g, `compare_swap` 2g).  
`SHAM` = size-matched optimal random 2-output macros (`seed=77777`, exact-compressed via CaDiCaL).

| Task (`dev_structured`) | `A0_BASE` | `PLANTED` (3 macros) | `A5_SHAM` (3 optimal random) | `A1_ABC_XAG` |
|---|---:|---:|---:|---:|
| `s1_dev_add2` | 8 | **7** | 8 | 8 |
| `s1_dev_add2_cin` | 10 | 10 | 10 | 14 |
| `s1_dev_mul2x2` | 8 | 8 | 8 | 7 |
| `s1_dev_popcount5` | 17 | **12** | 17 | 31 |
| `s1_dev_sort4` | 14 | **13** | 14 | 10 |
| `s1_dev_cmp2` | 8 | 8 | 8 | 9 |
| `s1_dev_sbox_present` | 17 | 17 | 17 | 22 |
| `s1_dev_sbox_gift` | 15 | 15 | 15 | 18 |
| `s1_dev_keccak_chi5` | 10 | 10 | 10 | 10 |
| `s1_dev_mux4_1bit_plus_par` | 12 | 12 | 12 | 12 |
| **TOTAL (10 dev tasks)** | **119** | **112 (−7)** | **119 (0)** | **141** |

### Qualification Criteria Met
- **Zero regressions:** `0/10` regressions for both `PLANTED` and `SHAM`.
- **Zero sham leakage:** Size-matched optimal `SHAM` yields **0** false gate savings (`119 == 119`).
- **Genuine multi-layer composition demonstrated:** On `s1_dev_popcount5`, the domain-blind engine automatically composed `FA ∘ FA ∘ HA` to drop from `17 → 12` flattened primitive gates (beating Berkeley `ABC` `31` by **19 gates**).
- **Instrument Verdict:** **QUALIFIED** — ready for Step 2 (re-run `$0` Phase 2A offline arms `A0`, `A1`, `A3`, `A5` across all 50 tasks) and Step 3 (LLM Proposer arms `A2 PRIOR-ONLY`, `A4 MG-UNPLUGGED`, `A6 SHADOW-NAKED`).
