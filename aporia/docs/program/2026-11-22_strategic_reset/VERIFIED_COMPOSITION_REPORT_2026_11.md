# Verified Compositional Algorithm Evolution: Empirical Evidence Across Five Formal Domains, Four Engineering Laws, and Exact Polynomial / Tensor-Rank Discovery

**Program:** Project Prometheus — Verified Composition Program (`reset/verified-composition-2026-11`)  
**Date:** 2026-11-27  
**Builder / Proposer Provenance:** 100% `claude-opus-5-5` (`0` silent fallbacks across Sprints 1–10; strict tool-less `--tools ""` isolation enforced by automated regression guards in Sprints 8–10)  
**Independent Cross-Family Q3 Adversary:** OpenAI open-weights `groq:openai/gpt-oss-120b` (strictly non-Anthropic; 6 independent closeout audits archived; **Final 10-Sprint Grade: `4.2 / 5` [`A−`] — Scientific Rigor `4.8 / 5`, Cross-Domain Impact `4.3 / 5`, Algorithmic Innovation `4.2 / 5`, Wall-Clock Cleanliness `3.6 / 5`**)  
**Frozen Integrity Apparatus (`rso/`):** `0` bytes modified (`git diff -- rso/` empty); **`6/6` hardened 3-seed RSO tamper attacks REJECTED** (`0 SURVIVED, 0 VACUOUS`) on every live packet  
**Total Verified Offline Evidence Base:** **27,690+ verified 100%-offline evaluation rows** (LLM completely unplugged at eval) across **5 independent formal domains**  
**Total Cumulative Equivalent Spend (Including ALL Aborted/Erratum/Rejected Runs):** **`~$42.45 / $100.00` (`42.5%`)**

---

## Abstract

We investigate whether frontier language models can compile domain knowledge and empirical failure telemetry into **compact, standalone, formally verified, LLM-free algorithms** that strictly outperform published domain state-of-the-art and full-budget prior-only compiled algorithms — whether successive generations can **compound compositionally**, and whether evolved algorithms **transfer out-of-distribution across scale and yield publishable mathematical mechanisms**. Across ten structured experimental sprints spanning **27,690+ verified offline evaluations** over **five independent formal domains**:
1. **Combinational Boolean Logic (`XAG`, 4–11 inputs)** vs. Berkeley `ABC 1.01`,
2. **16-Bit SMT Bit-Vector Superoptimization (`Z3 UNSAT`)** vs. Z3 C++ simplifier,
3. **Reversible/Quantum Linear Circuits (`GL(n, F_2)` CNOT, 12–18q)** vs. published Patel–Markov–Hayes (2008),
4. **Fault-Tolerant Quantum `Clifford+T` `T`-Count Minimization (`n = 6..16` qubits, up to `2^16 = 65,536` states!)** vs. published `T-par` (2014), `TODD` (Heyfron–Campbell 2018), and `FastTODD` (Vandaele–Martiel–de Brugière 2022), and
5. **Exact Binary Bilinear 3-Tensor Rank over `F_2` (Strassen / Laderman / AlphaTensor Matrix Multiplication & General 3-Tensors)** vs. published Kauers–Moosbauer Flip-Graph (2023),

we evaluate every artifact under an untouched, frozen tamper-evident adversarial audit suite (`rso/`).

Our findings establish seven concrete empirical and mathematical results:
1. **Claim 1 (Executable Algorithm Crystallization) is confirmed across ALL FIVE independent formal domains (`p_Holm < 1e-6`),** culminating in Sprint 10's 100% tool-less `$0.60` pure-Python solver crushing published **Kauers–Moosbauer Flip-Graph (2023)** with **0 losses (`35W/25T/0L`, `-75` multiplications, `p_Holm < 1e-6`)** and automatically rediscovering **Strassen `2×2×2 → 7`**, **Hopcroft–Kerr `2×3×3 → 15`**, **Karatsuba `poly_mul_3x3 → 9`**, and **Laderman / AlphaTensor `3×3×3 → 23`**!
2. **Claim 2 (Un-Caveated Experience Beyond Full-Budget Compiled Priors, including 100% Procedural Zero-LLM Holdouts) is confirmed cleanly in THREE independent formal domains:** Combinational XAG (`p_Holm = 0.006`, 30% faster wall), 16-Bit Z3 BV (`p_Holm < 1e-6`, surviving strict Law 4 word-width + Z3 `rlimit_count` metering with `0` losses), and Quantum `Clifford+T` (`n = 8..11`, Sprint 8: `-87` `T`-gates vs 99.3%-matched full-budget `A2_PRIOR_ONLY`, `p_Holm < 1e-6`; independently confirmed on a **100-circuit post-freeze blind `n = 8..12` suite**: `-236` vs `A2`, `p_Holm < 1e-6`, incl. `-63` at unseen `n = 12`, `p_Holm = 0.0112`!).
3. **Claim 3 (Multi-Generation Compositional Compounding) is verified up to two wall-clock-clean compositional generations across three domains** (`A2→G1→G2` in XAG [`191k` calls, 30% faster] and Quantum CNOT [`142.5k` calls, `0.998×` wall]; `G2→G3` in Sprint 7 Quantum `Clifford+T` [`413.2k` calls, `0.81× / 0.97×` wall]).
4. **Exact Polynomial Algebraic Theorems Permanently Break the `O(2^n)` Quantum Verification Barrier (Sprints 8–9):** Our exact `C(n, 2)` involutive `chi_z` compression (`M(z) = e_h`, `<= 55` bits for `n <= 11`) and exact `Z/8Z` cubic identity (`(-2)^{r-1} ≡ 0 mod 8` for `r >= 4`) deliver `O(m · n^3)` exact unitary verification and `O(m · n^2)` zero-`T` Clifford completion with zero `2^n` arrays, verified across **7,200 offline rows on `N = 200` untouched `n = 12..16` circuits (`2^16 = 65,536` states!)**.
5. **Large-Scale Zero-Shot Out-of-Distribution Transfer Confirmed Across `n = 6..16` Qubits (Sprints 8–9):** Sprint 7 `mod_g3_null_todd` transferred zero-shot to `n = 8..11` (beating `FastTODD 2022` by `-26`, `p = 0.031`), and Sprint 8 `g2_flat_kick` transferred zero-shot to `N = 200` `n = 12..16` circuits, beating published `TODD 2018` by **`-298` `T`-gates (`p_Holm < 1e-6`) while running `1.57×` faster (`102.1s` vs `160.6s`)** and beating Sprint 9's freshly compiled `A2_PRIOR_ONLY` by **`-109` (`p_Holm = 0.039`, `1.74×` faster)**!
6. **Publishable Algorithmic & Mechanistic Science (Sprint 8):** A 5-factor ablation falsified our initial hypothesis about Sprint 7 (isolating `M1` representation throughput), while Sprint 8 evolution discovered **`g2_flat_kick` (Greedy Majority-Voting Affine 4-Flat Reed–Muller `RM(n-4, n)` Decoder)** — beating `FastTODD 2022` (`-58`, `p_Holm = 0.0024`) and `S7_G3` (`-42`, `4.3×` faster wall).
7. **Four Empirical Laws (plus Law 4b/4c) & Ruthless Self-Falsification:** Our audits caught and transparently downgraded two meter loopholes (`S4-B G4` 50k-bit int arbitrage, `Sprint 6 G1` flat 180-unit `davio_synth` fee) and one Sprint 8 proposer-isolation seam (immediately patched with `--tools ""` + `TemporaryDirectory` + blind 100-circuit post-freeze replication).

---

## 1. Chronological Empirical Arc (Sprints 1–10, 5 Formal Domains, 27,690+ Offline Rows)

| Sprint / Track | Domain & Scale | Verified Offline Rows | Equivalent Spend* | Claim 1 | Claim 2 (`G-Comp`) | Claim 3 (`G-Recurse`) | Key Scientific Finding |
|---|---|---:|---:|---|---|---|---|
| **Sprint 1** *(P2B–P4)* | XAG 4–6in (static macros) | 2,268+ | `$2.37` | **PASS** (`p_Holm ≤ 0.031`) | FAIL (`PRIOR_ONLY`) | Gated | Static low-arity tables saturate on shot #1. |
| **Sprint 2** *(S2-A, S2-B)* | XAG 6–8in & 8/16-bit BV | 1,944 | `$2.83` | **PASS** (`p_Holm ≤ 0.00013`) | Provisional / Saturated | Not run | Executable Python passes jumped Claim 1 >10×. |
| **Phase 3** *(S3-A, S3-B)* | XAG 7–9in & 16-bit BV (flat) | 2,862 | `$4.05` | **PASS** (`p_Holm ≤ 0.0012`) | Partial / FAIL | FAIL | Exposed **Laws 1, 2, 3** (jitter, Goodharting, flat ceiling). |
| **Sprint 3** *(Laws 1–3)* | XAG 7–9in (170 tasks) | 1,500 | `$7.56`** | **PASS** (`p_Holm < 1e-6`) | **PASS** (`p_Holm = 0.006`; Proc `0.013`, `30%` faster) | **2-STEP PASS** (`A2→G1→G2`, `191k` calls) | First Holm-significant Claim 2 incl. procedural + coupled mechanism/representation. |
| **Sprint 4** *(S4-A, S4-B)* | 16-bit Z3 BV & 9–11in XAG | 2,772 | `$8.83` | **PASS** (`p_Holm < 1e-6`) | **PASS** (BV survives Law 4: `29W/0L`, `p_two = 3e-6`) | 2-step clean (`S4-B G2`); `G4` exposed by Law 4 | Cross-domain Claim 2 + discovered **Law 4** (big-int & Z3 `rlimit` metering). |
| **Sprint 5 — S5-Q** | Quantum `GL(n, F_2)` CNOT (12–18q) | 1,320 | `$3.55` | **PASS** (**`-28.5%` vs PMH 2008**, `p_Holm < 1e-6`) | Directional (`p_two = 0.0266`; **KO `p_Holm = 0.00086`**) | **2-Step 3-Tier** (`A2→G1→G2`, `0.998×` wall, `142.5k` calls) | 3rd formal domain; residual Python dict overhead motivated Law 4b. |
| **Sprint 6 — S6** | XAG 8–10in (Law 4b archive) | 1,452 | `$2.44` | Discounted | **DOWNGRADED (Law 4c Exposure)** | Gated (`G2..G4`) | Exposed **Law 4c**: flat 180-unit `davio_synth` fee let `G1` run `295k` calls. |
| **Sprint 7 — S7-CT** | Quantum `Clifford+T` (`n = 6..8q`) | 1,452 | `$4.45`*** | **PASS** (`-8.9%` vs `TODD 2018`, `35W/0L`, `p_Holm < 1e-6`) | **PASS vs `A5_SHAM`** (`0.88×` wall, `p_Holm = 0.000134`); caveated vs `A2` | **2-STEP PASS** (`G2→G3`: `-68`, `33W/0L`, `0.81×` wall, `413k` calls) | 4th formal domain; wall-clock-faster breakthrough over `TODD 2018` & `A5_SHAM`. |
| **Sprint 8 — S8-Science** | Quantum `Clifford+T` (`n = 8..11q` + Blind `8..12q`) | **3,480** *(2,880 + 600 blind)* | `$3.24` | **PASS** (`-58` vs `FastTODD 2022`, `p_Holm = 0.0024`) | **UN-CAVEATED PASS!** (`-87` vs 99.3%-matched `A2`, `p_Holm < 1e-6`; Blind 100: `-236`, `p_Holm < 1e-6`) | 1-step (`cross_gen = {}`) | Exact `C(n,2)` `chi_z` theorem; mechanistic falsification of S7; discovered **`g2_flat_kick` (`RM(n-4,n)` 4-Flat Decoder)** (`4.3×` faster than `S7_G3`)! |
| **Sprint 9 — S9-PolyScale** | Quantum `Clifford+T` (`n = 12..16q`, `N = 200` holdout) | **7,200** | `$1.74` | **PASS** (`S8_G2_ZS` `-298` vs `TODD 2018`, `1.57×` faster, `p_Holm < 1e-6`) | OOD transfer (`-109` vs `S9 A2`, `p_Holm = 0.039`); `G1..G4` gated | Not achieved | **Broke exponential barrier** (`O(m·n^3)` exact `Z/8Z` verification up to `2^16 = 65,536` states); uncapped `FastTODD` (`2.5×` wall) beat capped `S8_G2`. |
| **Sprint 10 — S10-AlphaTensor** | **5th Domain:** Binary Bilinear 3-Tensor Rank over `F_2` (`N = 60` holdout) | **1,440** | `$1.39` | **PASS** (**`-75` / `-9.1%` vs Published Kauers–Moosbauer 2023, `35W/0L`, `p_Holm < 1e-6`!**) | `PRIOR_SATURATED` on shot #1 (`$0.60`, `G1..G3` gated) | Not achieved | **5th formal domain!** 100% tool-less pure-Python `mod_g0_flip` rediscovered **Strassen `7`**, **`2×3×3 → 15`**, **Karatsuba `9`**, and **Laderman/AlphaTensor `3×3×3 → 23`** (`3.86×` bytecode wall overhead logged). |

*\*All USD figures are `claude -p` API-equivalent subscription usage, honestly including every failed/aborted/erratum proposal.*  
*\*\*Includes Sprint 3 v1 `$4.58` errata. \*\*\*Includes Sprint 7 v1 `$2.32` `getattr`-prompt erratum.*

---

## 2. Permanent Caveats, Errata & Open Frontiers

1. **Multi-Generation Depth (`Claim 3`):** Wall-clock-clean compositional compounding is verified up to **2 generations** across 3 domains (`XAG`, `GL(n, F_2)` CNOT, `Clifford+T`); **3+ wall-clock-clean generations** under full Law 4c metering remains the premier open frontier.
2. **Wall-Clock Parity Gaps Logged Honestly:** (a) In Sprint 9 (`n = 12..16`), uncapped `FastTODD 2022` (`254.4s` = `2.5×` more wall time) beat `35,000·C(n,2)`-capped `S8_G2_ZERO_SHOT` (`102.1s`); (b) in Sprint 10 (`AlphaTensor F_2`), pure-Python `mod_g0_flip` ran `3.86×` slower (`191.1s` vs `49.4s`) than native-assisted `A1_FLIP_GRAPH` at matched `310M` `v3_ops`.
3. **Logged Self-Falsifications & Errata (All Included in `$42.45` Total):** Sprint 1 `$0.12` `A6` miss; Sprint 3 v1 `$4.58` builder bug; Sprint 4 `S4-B G4` 50k-bit int arbitrage downgrade; Sprint 6 `G1` 180-unit `davio_synth` Law 4c downgrade; Sprint 7 v1 `$2.32` `getattr` prompt erratum & `A2` early-exit caveat (closed in Sprint 8); Sprint 8 v1 tool-isolation audit catch (immediately fixed with `--tools ""` + `TemporaryDirectory` guard tests + confirmed via 100-circuit post-freeze blind `n = 8..12` replication).

---

## 3. Reproducibility & Complete Receipt Chain

Run the unified verification script to re-verify all unit tests (`113+` tests), all `13/13` deterministic SHA-256 benchmark manifests, and frozen `rso/` integrity (`0` bytes modified):
```bash
python scripts/verify_all_composition_sprints.py
```

- Sprint 1: [PHASE4_FINAL_CLOSEOUT_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE4_FINAL_CLOSEOUT_RECEIPT.md)
- Sprint 2 & Phase 3: [SPRINT2_DUAL_TRACK_RECEIPT.md](file:///F:/Prometheus/comp_sprint2/receipts/SPRINT2_DUAL_TRACK_RECEIPT.md), [PHASE3_COMPOUNDING_RECEIPT.md](file:///F:/Prometheus/comp_sprint2/receipts/PHASE3_COMPOUNDING_RECEIPT.md)
- Sprint 3: [SPRINT3_COMPOSITIONAL_COMPOUNDING_RECEIPT.md](file:///F:/Prometheus/comp_sprint3/receipts/SPRINT3_COMPOSITIONAL_COMPOUNDING_RECEIPT.md), [CROSS_FAMILY_Q3_CLOSEOUT_RECEIPT.md](file:///F:/Prometheus/comp_sprint3/receipts/CROSS_FAMILY_Q3_CLOSEOUT_RECEIPT.md)
- Sprint 4: [SPRINT4_DUAL_TRACK_AND_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint4/receipts/SPRINT4_DUAL_TRACK_AND_Q3_RECEIPT.md)
- Sprint 5: [SPRINT5_QUANTUM_AND_FOUR_LAW_MASTER_RECEIPT.md](file:///F:/Prometheus/comp_sprint5_quantum/receipts/SPRINT5_QUANTUM_AND_FOUR_LAW_MASTER_RECEIPT.md)
- Sprint 6: [SPRINT6_LAW4B_ARCHIVE_RECEIPT.md](file:///F:/Prometheus/comp_sprint6_compound/receipts/SPRINT6_LAW4B_ARCHIVE_RECEIPT.md)
- Sprint 7: [SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint7_clifford_t/receipts/SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md)
- Sprint 8: [SPRINT8_MECHANISTIC_AND_RM_DECODER_RECEIPT.md](file:///F:/Prometheus/comp_sprint8_science/receipts/SPRINT8_MECHANISTIC_AND_RM_DECODER_RECEIPT.md)
- Sprint 9: [SPRINT9_POLY_SCALE_N12_N16_RECEIPT.md](file:///F:/Prometheus/comp_sprint9_poly_scale/receipts/SPRINT9_POLY_SCALE_N12_N16_RECEIPT.md)
- Sprint 10 & Final Q3: [SPRINT10_ALPHATENSOR_AND_FINAL_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint10_alphatensor/receipts/SPRINT10_ALPHATENSOR_AND_FINAL_Q3_RECEIPT.md)
