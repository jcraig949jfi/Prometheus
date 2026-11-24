# Phase 0 Exit Receipt — Verified Composition Sprint (`D1-A`, `D2-A`)

**Date:** 2026-11-22  
**Branch:** `reset/verified-composition-2026-11` (branched from `origin/main` @ `9884ac934`)  
**Previous checkout preserved:** `vivarium/v0-2026-09-05` @ `859a1bcf7` intact in git history  
**Locked Decisions:** `D1-A` (skip `TFS-1`, straight to Track 3B), `D2-A` (Track `3B-Boolean`: exact minimum-size XAG/AIG Boolean circuits)

---

## 1. Phase 0 Checklist

| Check | Status | Evidence |
|---|---|---|
| Clean branch off `origin/main` (`9884ac934`) | **PASS** | `git rev-parse --abbrev-ref HEAD` -> `reset/verified-composition-2026-11`; base `9884ac934` |
| Auto-committer audit (`auto: portfolio update`, `Achilles[census]`) | **PASS (Audited)** | `auto: portfolio update` comes from `scripts/intelligence_loop.py` (M4/`pythonw`; 0 matching scheduled tasks on this Windows host). `Achilles[census]` comes from **ELSA** (`5633cc02a`). Last remote commits were `2026-11-12/13`. |
| Pinned `rso/adversary` + `rso/completeness` green (zero edits) | **PASS** | `67 passed in 5.45s` (`test_attacks.py`, `test_mutants.py`, `rso/completeness/tests`) |
| `comp_sprint/` kernel + meter + NPN4 + SAT-exact tests (RED → GREEN) | **PASS** | RED `5 failed (0.41s)` -> GREEN `5 passed (0.94s)` |
| 4-input NPN exact calibration (all 222 classes / 65,536 functions) | **PASS (100%)** | Exact match to Knuth TAOCP Vol. 4A §7.1.2 Table 1 / OEIS A056287 (see §2); `63/63` BFS vs SAT exact agreement for `k <= 4`; `222/222` truth-table verified; `23.77s` wall time, `$0.0003` CPU |
| Industry baseline (`A1 INDUSTRY`) status | **PARTIAL (Action for Phase 1 Step 1)** | SAT-exact (`pysat` / `cadical195` + `z3 5.0.0`) is live and verified. **Berkeley `ABC` (`abc.exe` / `yosys-abc.exe`)** is not yet installed on this Windows host (`gcc`/`clang` are available, WSL returned `E_ACCESSDENIED` inside sandbox). Needed before Phase 2 multi-output 6–8 input comparisons. |

---

## 2. Exact 4-Input NPN Calibration Table (`basis = XAG_free_inv == Knuth B_2`)

Full per-class receipt: `comp_sprint/receipts/PHASE0_NPN4_XAG_CALIBRATION.json`.

| Min XAG Gates (`k`) | NPN Classes | Total 4-Input Functions | Knuth TAOCP 4A / OEIS A056287 |
|---:|---:|---:|---|
| 0 | 2 | 10 | Exact match |
| 1 | 2 | 60 | Exact match |
| 2 | 5 | 456 | Exact match |
| 3 | 20 | 2,474 | Exact match |
| 4 | 34 | 10,624 | Exact match |
| 5 | 75 | 24,184 | Exact match |
| 6 | 72 | 25,008 | Exact match |
| 7 | 12 | 2,720 | Exact match |
| **Total** | **222** | **65,536** | **100.0% exact** |

- **Independent cross-check (`k <= 4`):** Exact DAG BFS vs CaDiCaL 1.9.5 SAT-exact agreed on **63 / 63** classes.
- **Anti-cheating macro contract verified:** `test_xag_circuit_eval_and_macro_flattening_no_discount` confirms every `Macro` flattens to primitive `{AND, XOR}` gates with structural-hashing (`strash`) deduplication and receives zero artificial gate-count discount.

---

## 3. Ready for Phase 1 (Days 3–7): Minimal Engine + Sealed Two-Stratum Holdout

Next concrete steps:
1. Acquire/build **Berkeley `ABC`** (`abc.exe` or `yosys-abc.exe`) so `A1 (INDUSTRY)` is wired alongside `cadical195` SAT-exact.
2. Build `comp_sprint/benchmarks.py` + `comp_sprint/qualify.py`: generate, mechanically qualify, and cryptographically seal:
   - **Stratum 1 (Structured multi-output):** 4–6-input arithmetic, popcount, comparators, small S-boxes, and bit-permutation networks.
   - **Stratum 2 (100% Procedural zero-LLM):** randomly sampled 6–8-input multi-output Boolean functions with compositional sharing.
3. Build `comp_sprint/synth_base.py` (**A0 `BASE`**) + `comp_sprint/industry_abc.py` (**A1 `INDUSTRY`**) + `comp_sprint/library.py` (**A2 `PRIOR-ONLY`**) and run the non-saturation gate before launching any learning arm.
