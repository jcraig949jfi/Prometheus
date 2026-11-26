# Sprint 6 Receipt — Law 4b (`OpBudget v3`) & Multi-Lineage 4-Gen XAG Archive Evolution

**Date:** 2026-11-26  
**Track:** `S6_LAW4B_ARCHIVE_XAG` (`comp_sprint6_compound/`)  
**Proposer Provenance:** 100% `claude-opus-5-5` (`0` silent fallbacks)  
**Independent Cross-Family Q3 Referee:** `groq:openai/gpt-oss-120b` (strictly non-Anthropic)  
**Manifest SHA-256:** `9087a648278fa108993160605234212edc9fb6218e454ba8fdde3048bdd61f52` (172 fresh 8–10in XAG tasks; 4 disjoint `val_g1..g4` splits of 20 tasks each + 44 untouched holdout: 16 struct + 14 `proc_shared` + 14 `proc_comp`)  
**Total Verified Offline Rows:** **1,452 rows** (11 arms × 44 holdout tasks × 3 paired seeds `{0, 1, 2}`, LLM completely unplugged at eval)  
**Equivalent Spend:** **`$2.44`** (`fixed_llm_usd = $2.4253`, `cpu_usd = $0.0121`, 8 proposals, 2 accepted)  
**Frozen Integrity Apparatus (`rso/`):** `0` bytes modified; **`6/6` hardened 3-seed RSO attacks REJECTED** (`DROP`, `DUPLICATE`, `REWRITE_DERIVED`, `SINGLE_SEED_TAMPER`, `SCRUB_SPEC`, `MANIFEST_TAMPER`); determinism audit **`6/6` tasks, `0` mismatches**; `0` `fn_errors`; `0` anti-hardcoding hits.

---

## 1. Honest Executive Verdict (Including Q3 Downgrade to Law 4c Loophole Exposure)

- **Self-Disclosed & Q3-Confirmed Verdict:** **NO WALL-CLOCK-CLEAN CLAIM 2 OR CLAIM 3 WIN — EXPOSED LAW 4c (API-PRIMITIVE PRICING ARBITRAGE).**
- **What Happened:** Under Law 4b (`OpBudget v3`: loops=`1`, calls=`3`, big-int >64b=`(bits-1)//64`, dict/set=`4+2*len`, list/tuple=`2+len`, sorted=`4+n*log2(n)`, cap `2,400,000` units/task):
  - `G0` (`A2_PRIOR_ONLY`, 2 modules: `mod_g0_struct` [68L], `mod_g0_davio` [52L]) ran ~24 fixed Davio order heuristics and exited early after only `905,878` `v3_ops` (`19.44s`).
  - `G1` (`mod_g1_ordersearch`, 103L) passed `val_g1` (`810 → 746`, `-64`, `11W/9T/0L`, `p_less = 0.000488`) and beat `A2_PRIOR_ONLY`, `A5_SHAM`, and `KO_MATCHED_LAST` on the untouched holdout with `0` losses (`2,432.0` vs `2,652.0` / `2,555.0` / `2,634.0`, `p_Holm <= 0.000427`).
  - `G2`, `G3`, and `G4` were all **honestly gated off by Law 2** (`p >= 0.25`; promoted generations = `[1]`).
  - **HOWEVER — THE CRITICAL METER LOOPHOLE:** `G1` burned **`94,492,653` `v3_ops` (`104×` `A2`)** and **`1,179.96s` wall time (`60.7×` `A2`'s `19.44s`; `5.5×` `A5_SHAM`'s `213.68s`)** by invoking `g1->g0:davio_try` **`295,454` times** (~2,238 times per task)! Why? Because the un-instrumented native API helper `davio_synth` was still charged a flat `180` units against a `2,400,000` `OpBudget v3` cap (`0.0075%` of budget per call) even though a full 10-input Davio decomposition executes ~15,000+ internal word-ops!
- **Independent Q3 Verdict (`groq:openai/gpt-oss-120b`):** Concurred completely: *"Sprint 6 does not constitute a clean wall-clock win. The improvement over A2/A5/KO is attributable to the pricing loophole... Sprint 6 is downgraded to 'Loophole exposure – no claim of wall-clock superiority.'"*

---

## 2. Exact Holdout Results (44 Untouched 8–10in XAG Tasks × 3 Seeds = 1,452 Rows)

| Arm | Struct (16) | Proc Shared (14) | Proc Comp (14) | Proc Total (28) | **All-44 Total** | Wall (s) | Ratio vs A2 | Total `v3_ops` | Cross-Gen Calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `A0_BASE` | 111.06 | 61.21 | 18.64 | 1,118.0 | **2,895.0** | 1.53s | 0.08× | 0 | 0 |
| `A1_ABC_XAG` *(AIG→XAG caveat)* | 438.81 | 75.93 | 17.71 | 1,311.0 | **8,332.0** | 12.64s | 0.65× | 0 | 0 |
| `A3_ZERO_LLM` | 109.81 | 56.29 | 15.00 | 998.0 | **2,755.0** | 61.70s | 3.17× | 1,477,208 | 0 |
| `A5_SHAM` *(500 random Davio restarts)* | 97.19 | 54.57 | 16.86 | 1,000.0 | **2,555.0** | 213.68s | 10.99× | 12,687,771 | 0 |
| `A2_PRIOR_ONLY` *(early exit)* | 101.81 | 55.57 | 17.50 | 1,023.0 | **2,652.0** | 19.44s | 1.00× | 905,878 | 0 |
| **`G1` (`= G2 = G3 = G4`)** | **90.62** | **53.43** | **16.71** | **982.0** | **2,432.0** | **1,179.96s** | **60.70×** | **94,492,653** | **591,172** |
| `KO_MATCHED_LAST` | 101.06 | 55.50 | 17.14 | 1,017.0 | **2,634.0** | 52.37s | 2.69× | 2,631,533 | 0 |

### Paired Wilcoxon + Holm–Bonferroni (Logged Transparently — Discounted by Law 4c Metering Disparity)

| Comparison | W / T / L | Sum Δ | 95% Boot CI (mean/task) | `p_two` | `p_Holm` | Honest Audit Interpretation |
|---|---:|---:|---|---:|---:|---|
| `G1 (=G4)` vs `A0_BASE` (44) | 30W / 14T / 0L | -463.0 | [-20.159, -4.318] | 0.000002 | 0.000022 | Metric lower, but `60×` wall / `104×` ops via `davio_synth` pricing gap |
| `G1 (=G4)` vs `A5_SHAM` (44) | 15W / 29T / 0L | -123.0 | [-5.545, -0.864] | 0.000061 | 0.000427 | `5.5×` slower wall time (`1,180s` vs `213.7s`); `A5_SHAM` capped at 500 restarts |
| `G1 (=G4)` vs `A2_PRIOR_ONLY` (All 44) | 19W / 25T / 0L | -220.0 | [-9.864, -1.614] | 0.000004 | 0.000040 | **DISCOUNTED**: `A2` early-exited (`0.91M` ops); `G1` burned `94.5M` ops (`295k` `davio_try` calls) |
| `G1 (=G4)` vs `A2_PRIOR_ONLY` (Proc 28) | 11W / 17T / 0L | -41.0 | [-2.571, -0.607] | 0.000977 | 0.005862 | **DISCOUNTED**: same Law 4c pricing loophole |
| `G1 (=G4)` vs `KO_MATCHED_LAST` (44) | 19W / 25T / 0L | -202.0 | [-9.409, -1.386] | 0.000004 | 0.000040 | **DISCOUNTED**: `G0` had no search loop to absorb `G1`'s donated budget (`2.63M` vs `94.5M` ops) |

---

## 3. Law 4c Engineering Lesson (Required Fix for Future XAG Evolution)

Sprint 6 proves that instrumenting Python loops, big-ints, and containers (`OpBudget v3`) is **necessary** (and worked cleanly in Sprint 7, achieving `0.81×–0.97×` wall-clock parity!) **but insufficient whenever un-instrumented native C/Python API helpers remain underpriced**:
1. Every native API helper (such as `davio_synth`) **must be metered in exact `OpBudget v3` units** proportional to its actual internal word-operations (e.g., `~15,000` units for 10-input Davio synthesis, or internally instrumented with the same `v3` counter), not a flat `180`-unit stub.
2. Any future XAG re-run under corrected Law 4c pricing must also enforce matched-budget consumption on `A5_SHAM` and `A2_PRIOR_ONLY` before claiming wall-clock-clean Claim 2 or 3+ generation compounding.
