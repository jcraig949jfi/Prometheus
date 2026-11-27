# Verified Compositional Algorithm Evolution: Empirical Evidence Across Four Formal Domains, Four Engineering Laws, and Mechanistic Quantum Compilation Discovery

**Program:** Project Prometheus — Verified Composition Program (`reset/verified-composition-2026-11`)  
**Date:** 2026-11-26  
**Builder / Proposer Provenance:** 100% `claude-opus-5-5` (`0` silent fallbacks across Sprints 1–8)  
**Independent Cross-Family Q3 Adversary:** OpenAI open-weights `groq:openai/gpt-oss-120b` (strictly non-Anthropic; 5 independent closeout audits archived; **Sprint 8 raised Algorithmic Innovation `3.5 → 4.2 / 5` and Wall-Clock Cleanliness `3.0 → 3.5 / 5`; Overall `3.8 / 5` [`B+`]**)  
**Frozen Integrity Apparatus (`rso/`):** `0` bytes modified (`git diff -- rso/` empty); **`6/6` hardened 3-seed RSO tamper attacks REJECTED** (`0 SURVIVED, 0 VACUOUS`) on every live packet  
**Total Verified Offline Evidence Base:** **19,050+ verified 100%-offline evaluation rows** (LLM completely unplugged at eval; incl. 600-row post-freeze blind `n = 8..12` replication) across **4 independent formal domains**  
**Total Cumulative Equivalent Spend (Including ALL Aborted/Erratum/Rejected Runs):** **`~$39.32 / $100.00` (`39.3%`)**

---

## Abstract

We investigate whether frontier language models can compile domain knowledge and empirical failure telemetry into **compact, standalone, formally verified, LLM-free algorithms** that strictly outperform published domain state-of-the-art and full-budget prior-only compiled algorithms — whether successive generations can **compound compositionally**, and whether evolved algorithms **transfer out-of-distribution and yield publishable mathematical mechanisms**. Across eight structured experimental sprints spanning **18,450+ verified offline evaluations** over **four independent formal domains** — (1) Combinational Boolean Logic (`XAG`, 4–11 inputs), (2) 16-Bit SMT Bit-Vector Superoptimization (`Z3 UNSAT`), (3) Reversible/Quantum Linear Circuits (`GL(n, F_2)` CNOT synthesis vs. published Patel–Markov–Hayes 2008), and (4) Fault-Tolerant Quantum `Clifford+T` `T`-Count Minimization (`n = 6..11` qubits vs. published `T-par` 2014, `TODD` Heyfron–Campbell 2018, and `FastTODD` Vandaele–Martiel–de Brugière 2022) — we evaluate every artifact against a strict Four-Rung Claim Ladder under an untouched, frozen tamper-evident adversarial audit suite (`rso/`).

Our findings establish six concrete empirical and mathematical results:
1. **Claim 1 (Executable Algorithm Crystallization) is confirmed across all four formal domains** (`p_Holm < 1e-6`), beating Berkeley `ABC 1.01`, the Z3 C++ simplifier, published Patel–Markov–Hayes 2008 (`-28.5%` CNOTs), published `T-par` 2014, published `TODD` 2018 (`-8.9%` on `n=6..8`, `-7.1%` on `n=8..11`, `p_Holm < 1e-6`), and published `FastTODD` 2022 (`-58` `T`-gates across 80 `n=8..11` tasks, `p_Holm = 0.0024`) with the LLM completely unplugged at evaluation.
2. **Claim 2 (Un-Caveated Experience Beyond Full-Budget Compiled Priors, including 100% Procedural Zero-LLM Holdouts) is confirmed cleanly in THREE independent formal domains:**
   - **Combinational XAG (Sprint 3):** `p_Holm = 0.0060` overall (`p_Holm = 0.0131` procedural, `30%` faster wall time than `A2_PRIOR_ONLY`).
   - **16-Bit Z3 BV (Sprint 4–5):** `p_Holm < 1e-6` overall (`p_Holm = 0.000032` procedural; surviving strict Law 4 word-width + Z3 `rlimit_count` metering at `p_two = 3e-6` / `6.1e-5`, `0` losses).
   - **Fault-Tolerant Quantum `Clifford+T` (`n = 8..11` Qubits, Sprint 8 — ZERO Early-Exit Caveat, Law 4b+4c Clean):** `S8 G2` beats full-budget `A2_PRIOR_ONLY` (`560.0M` vs `556.2M` `v3_ops`, `99.3%` matched!) by **`-87.0` `T`-gates** (`40W/31T/9L`, **`p_Holm < 1e-6`**; Procedural `N = 60`: `-86.0`, `36W/19T/5L`, **`p_Holm < 1e-6`**), beats full-budget `A5_SHAM` by **`-110.0`** (`p_Holm < 1e-6`), and beats published `FastTODD (2022)` by **`-58.0`** (`p_Holm = 0.002385`)!
3. **Claim 3 (Multi-Generation Compositional Compounding) is verified up to two wall-clock-clean compositional generations across three domains** (`A2→G1→G2` in XAG and Quantum CNOT; `G2→G3` in Sprint 7 Quantum `Clifford+T`, `413.2k` cross-gen calls, `0.81× / 0.97×` wall time).
4. **Mechanistic Science & Zero-Shot Out-of-Distribution Scale Transfer (Sprint 8 Study 1, `$0.00` LLM):** A 5-factor ablation of Sprint 7's `mod_g3_null_todd` **falsified** our initial hypothesis (showing `M1` representation throughput, not `M2..M5`, drove Sprint 7 at `n = 6..8`), while `S7_G3_ZERO_SHOT` transferred zero-shot to 80 unseen `n = 8..11` circuits (beating `TODD 2018` by `-132`, `p < 1e-6` and `FastTODD 2022` by `-26`, `p = 0.031`, before hitting its predicted `O(2^n)` wall at `n = 10..11`).
5. **Publishable Algorithmic Discovery (Sprint 8 Study 2):** Combining our **exact `C(n, 2)` involutive `chi_z` compression theorem** (`<= 55` bits for all `n <= 11`) with Law 4b+4c evolution discovered **`g2_flat_kick`** — a **Greedy Majority-Voting Affine 4-Flat Reed–Muller `RM(n-4, n)` Codeword Decoder** that beats `S7_G3_ZERO_SHOT` by **`-42` `T`-gates (`p_Holm = 0.010`) while running `4.3×` faster in real wall-clock time (`49.9s` vs `214.0s`)**!
6. **Four Empirical Laws (plus Law 4b/4c Refinements) govern when offline evolution compounds vs. generates counterfeit meter exploits:** Our metering audits explicitly caught and downgraded two apparent wins (`S4-B G4` 50,000-bit int arbitrage and `Sprint 6 G1` flat 180-unit `davio_synth` pricing loophole), and Sprint 8 closed both loopholes cleanly.

---

## 1. Experimental Protocol & Anti-Counterfeit Methodology

Every experiment in Sprints 1–8 enforces six non-negotiable methodological invariants:

1. **Zero LLM at Evaluation (`$0.00` Eval):** Evolved artifacts are frozen, AST-validated, SHA-256 content-addressed Python modules/libraries executed 100% offline with zero network or LLM access.
2. **Zero Macro-Call Discount:** All costs measure exact flattened primitive counts (`AND + XOR` gates in XAG; live primitive SSA ops in 16-bit BV; primitive `CNOT` gates in Quantum `GL(n, F_2)`; exact `T`-gates in Fault-Tolerant `Clifford+T`).
3. **100% Exact Mathematical Verification:** Exhaustive `2^n`-bit truth-table equality for XAG; exact isolated-context Z3 `UNSAT` equivalence over all `2^(16*k)` inputs for BV; exact matrix-group multiplication over `GL(n, F_2)` for Quantum CNOT; exhaustive `2^n`-state unitary verification up to `n = 11` (`2,048` basis states) for `Clifford+T`.
4. **Procedural Zero-LLM + Real Literature Holdout Strata:** Holdouts combine real literature circuits (Cuccaro/VBE adders, `GF(2^3)/GF(2^4)` multipliers, Barenco Toffolis, QCLA, CSUM-MUX, Grover oracles) with 100% procedurally generated tasks from disjoint RNG seeds.
5. **Hardened 3-Seed RSO Tamper-Evident Audit:** Every evaluation packet is reduced across 3 paired seeds `{0, 1, 2}` with all-seed checksums (`sum_all_cost`, `min_all_cost`, `max_all_cost`) and audited live against 6 adversarial attacks (`DROP`, `DUPLICATE`, `REWRITE_DERIVED`, `SINGLE_SEED_TAMPER`, `SCRUB_SPEC`, `MANIFEST_TAMPER`). Every live packet achieved **`6/6 REJECTED` (`0 SURVIVED, 0 VACUOUS`)**.
6. **Cross-Family Adversarial Adjudication:** All claims are audited by a strictly non-Anthropic model (`groq:openai/gpt-oss-120b`), with all valid caveats permanently attached to the verdict.

---

## 2. Chronological Empirical Arc (Sprints 1–8, 4 Formal Domains, 18,450+ Offline Rows)

| Sprint / Track | Domain & Scale | Artifact Space | Verified Offline Rows | Equivalent Spend* | Claim 1 | Claim 2 (`G-Comp`) | Claim 3 (`G-Recurse`) | Key Scientific Finding |
|---|---|---|---:|---:|---|---|---|---|
| **Sprint 1** *(P2B, P2C, P4 Q3)* | XAG 4–6in | Static `k ≤ 4` `(L, T, S)` tables | 2,268+ | `$2.37` | **PASS** (`p_Holm ≤ 0.031`, `N* = 0.70`) | **FAIL** (`COMPILED_PRIORS_ONLY`) | Gated | Static low-arity tables saturate on shot #1; 2×2 factorial isolated `(L, T)` from `S`. |
| **Sprint 2 — S2-A** | XAG 6–8in | AST-sandboxed Python passes (`0.60s`) | 936 | `$1.69` | **PASS** (`p_Holm = 0.00013`) | **Provisional** (`6W/0L`, `p_two = 0.031`, `p_Holm = 0.094`) | Not run | Promoting artifact to executable Python jumped Claim 1 >10×; first Claim 2 signal. |
| **Sprint 2 — S2-B** | 8/16-bit Z3 BV | AST-sandboxed Python passes (`0.70s`) | 1,008 | `$1.14` | **PASS** (`-82.4%` vs Z3, `p_Holm = 2e-5`) | **`PRIOR_SATURATED`** | Not run | `A2_PRIOR_ONLY` hit near-global optimum (`340 → 60`) on 2–4 op cores on shot #1. |
| **Phase 3 — S3-A** | XAG 7–9in | Flat 3-gen Python passes (`0.60s`) | 1,350 | `$2.16` | **PASS** (`-382` vs `90.5s` SHAM, `p_Holm < 1e-5`) | Partial (`G1` 3/3 seeds, `p_two = 0.188`) | **FAIL** (`876→866→868→870`) | Exposed **Laws 1, 2, 3**: wall-clock slice theft, 10-task `dev_val` Goodharting, flat pass ceiling. |
| **Phase 3 — S3-B-Hard** | 16-bit Z3 BV (5–10 op cores) | Flat 3-gen Python passes (`0.80s`) | 1,512 | `$1.89` | **PASS** (`-57.1%` vs Z3, `p_Holm = 0.0012`) | **FAIL** | **FAIL** (`244→231→260→260`) | Identical code (`A2` vs `G1`) swung **13 ops** from Z3 wall-clock jitter! |
| **Sprint 3** *(Laws 1–3)* | XAG 7–9in (170 tasks) | Compositional `LibModule` (`OpBudget v1`) | 1,500 | `$7.56`** | **PASS** (`-487` vs SHAM, `p_Holm < 1e-6`) | **PASS** (`p_Holm = 0.006`; **Proc `p_Holm = 0.013`**) | **2-STEP PASS** (`A2→G1→G2`; `G3` gated) | First Holm-significant Claim 2 incl. 100% procedural; `G2` (`mod_g2_net`) ran **30% faster** (`32s` vs `45.6s`) with `191k` cross-gen calls. |
| **Sprint 4 — S4-A** *(Laws 1–4)* | 16-bit Z3 BV (140 tasks) | Compositional `LibModule` + isolated Z3 `rlimit` | 1,320 | `$4.34` | **PASS** (`-433` vs Z3, `p_Holm < 1e-6`) | **PASS — SURVIVES LAW 4!** (`34W/0L`, `p_Holm < 1e-6`; Law 4: **`29W/0L`, `p_two = 3e-6`**, Proc **`15W/0L`, `p_two = 6.1e-5`**) | 1-step (`G2`/`G3` gated) | **Cross-domain Claim 2 confirmed** with `0.000` Z3 jitter (`G1=G2=G3=538.0` bit-identical); survives 64-bit word + Z3 `rlimit` metering! |
| **Sprint 4 — S4-B** *(Laws 1–4)* | XAG 9–11in (172 tasks) | Compositional `LibModule` (4 gens + Matched-Op KO) | 1,452 | `$4.49` | **PASS** (`-818` vs SHAM, `p_Holm < 1e-6`) | **PASS** (`G2`: `-415` at `89.9s < 102.2s`, `23W/0L`, `p_Holm < 1e-6`) | 2-step wall-clean (`G2`); **`G4` EXPOSED BY LAW 4** | Discovered **Law 4**: `G4` (`mod_g4_batchwalk`, `985k` calls) achieved `-253` via 50,000-bit Python int arbitrage (`633s → 17.5s` & reversed under `OpBudget v2`). |
| **Sprint 5 — S5-Q** *(All 4 Laws Native)* | Quantum `GL(n, F_2)` CNOT (12–18q, 140 tasks) | Compositional `LibModule` (`OpBudget v2` native) | 1,320 | `$3.55` | **PASS** (**`-28.5%` / `-975` CNOTs vs PMH 2008**, `p_Holm < 1e-6`) | **Directional** (`-49`, CI `[-1.98, -0.27]`, `p_two = 0.0266`, `p_Holm = 0.133`; **KO `p_Holm = 0.00086`**) | **2-Step 3-Tier** (`A2→G1→G2`, `0.998×` wall parity, `142.5k` calls) | 3rd formal domain; `G2` invokes BOTH `G1` (`97k`) & `G0` (`33k`) at `48.15s` vs `48.22s`; residual dict overhead motivated Law 4b. |
| **Sprint 6 — S6** *(Law 4b Archive)* | XAG 8–10in (172 tasks) | Compositional `LibModule` (`OpBudget v3`) | 1,452 | `$2.44` | Discounted (`davio_synth` loophole) | **DOWNGRADED (Law 4c Exposure)** | **Gated** (`G2..G4` rejected by Law 2) | **Exposed Law 4c:** un-instrumented native helper `davio_synth` (180 units) let `G1` run `295k` calls (`1,180s` vs `19.4s`); downgraded per ruthless falsification + Q3. |
| **Sprint 7 — S7-CT** *(4th Domain, Law 4b)* | Quantum `Clifford+T` (`n = 6..8q`, 140 tasks) | Compositional `LibModule` (`OpBudget v3` native) | 1,452 | `$4.45`*** | **PASS** (**`-8.9%` vs `TODD` 2018**, `35W/0L`, `p_Holm < 1e-6`) | **PASS vs Full-Budget Controls** (`A5_SHAM` `0.88×` wall, `p_Holm = 0.000134`); **CAVEATED vs `A2`** | **2-STEP PASS** (`G2→G3`: `-68`, `33W/0L`, `p_Holm < 1e-6`, **`0.81×` wall**, `413.2k` calls) | 4th formal domain; `mod_g3_null_todd` beats `TODD 2018` & `A5_SHAM` while running faster; `A2` early-exit caveat closed in Sprint 8. |
| **Sprint 8 — S8-Science** *(Law 4b+4c, Scale-Free)* | Quantum `Clifford+T` (`n = 8..11q`, 200 tasks, 80 holdout incl. 20 real lit circuits) | Compositional `LibModule` (`OpBudget v3` + Law 4c + exact `C(n,2)` involutive `chi_z`) | **2,880** | **`$3.24`** | **PASS** (**`-164` vs `TODD` 2018**, `p_Holm < 1e-6`; **`-58` vs `FastTODD` 2022**, `p_Holm = 0.0024`) | **UN-CAVEATED PASS!** (**`-87` vs 99.3%-matched full-budget `A2_PRIOR_ONLY`**, `p_Holm < 1e-6`; Proc `-86`, `p_Holm < 1e-6`; **`-42` vs `S7_G3` at `4.3×` faster wall!**) | 1-step (`cross_gen = {}`; `G3/G4` gated by Law 2) | **Closes A2 & Law 4c gaps!** Study 1 falsified `M2..M5` as S7's driver & confirmed OOD transfer; Study 2 discovered **`g2_flat_kick` (Greedy Majority-Voting Affine 4-Flat `RM(n-4,n)` Decoder)**! |

*\*All USD figures represent `claude -p` API-equivalent usage drawn from the operator's Claude subscription, honestly including every failed/rejected proposal.*  
*\*\*Sprint 3 spend includes `$2.98` clean v2 + `$4.58` errata (`$4.13` v1 run aborted after catching `MeteredStrashBuilder._gates` bug + `~$0.45` pre-unpacking CLI call).*  
*\*\*\*Sprint 7 spend includes `$2.13` clean v2 + `$2.32` logged v1 `getattr`-prompt erratum.*

---

## 3. The Four Empirical Laws (with Law 4b/4c Refinements)

1. **Law 1 — Deterministic Execution Budgets (Zero Jitter):** AST loop instrumentation + isolated `z3.Context()` `rlimit` yield exact `0.000` variance across all four domains.
2. **Law 2 — Disjoint Per-Generation Validation Splits + Paired Statistical Gates:** Disjoint hidden validation splits (`val_g1..val_gK`, `N = 20–25`) gated by exact paired Wilcoxon `p_less < 0.05` (`< 0.025` Bonferroni on retry) prevented every noisy regression across Sprints 3–8.
3. **Law 3 — Compositional Verified Libraries + Matched-Op Causal Knockouts:** Generation-tagged `LibModule` libraries enable coupled mechanism + representation evolution verified causally by matched-op knockouts.
4. **Law 4 — Complete Compute-Proportional Metering (`OpBudget v2 → v3 → 4c`):**
   - **4a (`OpBudget v2`):** Meter 64-bit big-int word-ops `(bit_length - 1) // 64` and exact Z3 `rlimit_count` (exposed `S4-B G4`).
   - **4b (`OpBudget v3`):** Meter container allocations (`dict/set`, `list/tuple`, `sorted`) and function calls (enabled Sprint 7's `0.81×–0.97×` wall parity).
   - **4c (Native Helper Pricing — Diagnosed in Sprint 6, Solved in Sprint 8):** Charge every native API helper exact compute-proportional `v3` word-ops (`O(m · C(n, 2))` in Sprint 8, verified `2.5×` stricter per wall-second than pure Python).

---

## 4. Complete Permanent Caveats, Errata & Open Frontier Ledger

1. **Sprint 7 `A2_PRIOR_ONLY` Early-Exit Caveat (Closed in Sprint 8):** In Sprint 7 (`n = 6..8`), `A2_PRIOR_ONLY` exited at `3,300` `v3_ops`, so Sprint 7 wall-clock-clean claims rest on full-budget controls (`A5_SHAM`, `KO_MATCHED_LAST`, `G2`). Sprint 8 (`n = 8..11`) enforced full-budget `A2_PRIOR_ONLY` (`99.3%` matched `v3_ops`), delivering an un-caveated Claim 2 PASS (`p_Holm < 1e-6`).
2. **Sprint 8 Multi-Generation Scope & Wall Parity:** Sprint 8 `G2` (`mod_g2_escape`) is a **1-step Claim 2 pass** (`cross_gen_calls = {}`; `G3/G4` gated off by Law 2), running at `1.31×` wall time of `A2_PRIOR_ONLY` (`49.9s` vs `38.1s`) and **`0.23×` (`4.3×` faster)** than `S7_G3_ZERO_SHOT` (`214.0s`). On the 20 literature circuits vs `FastTODD 2022`, `S8 G2`'s `-7` `T`-gate lead is directional (`p_Holm = 0.311`), while vs `TODD 2018` it is Holm-significant (`-31`, `p_Holm = 0.00165`).
3. **Sprint 6 Law 4c & S4-B `G4` Law 4a Downgrades:** Both permanently classified as meter-loophole exposures (`davio_synth` 180-unit flat fee in S6; 50,000-bit Python int arbitrage in S4-B `G4`), not clean algorithmic wins.
4. **S5-Q Multiplicity & Container Overhead:** `G2 vs A2` on Quantum CNOT is `p_two = 0.0266` (`p_Holm = 0.133`), while `G2 vs KO_MATCHED_LAST` passed Holm (`p_Holm = 0.00086`).
5. **Hardest Open Frontiers (Unproven):** (a) **3+ wall-clock-clean compounding generations** (`G0 → G1 → G2 → G3+`) under full Law 4c metering; (b) scaling beyond `n = 11` qubits (`n = 12..20+` using polynomial `O(m · n^3)` algebraic verification) and `N ≥ 500` circuit suites.
6. **Logged Cognitive Accounting & Protocol Audit Errata (All Included in `$39.32` Total):** Sprint 1 Phase 2B `$0.1198` `A6` miss; Sprint 3 v1 `$4.13` `MeteredStrashBuilder._gates` bug + `~$0.45` CLI call; Sprint 7 v1 `$2.32` `getattr`-prompt erratum; Sprint 8 v1 tool-isolation audit finding (`s8_runner.py` initially omitted `--tools ""`, allowing local `dev_diag` tests in `g0_draft`/`g2_draft` and `val_g3` checks in rejected `g3_draft` — fixed with `--tools ""` + empty `TemporaryDirectory`, draft folders removed, and `S8_G2_FLAT_KICK` independently confirmed on a **100% post-freeze blind 100-circuit `n = 8..12` suite**: `-236` vs `A2_PRIOR_ONLY`, `74W/14L`, `p_Holm < 1e-6`, incl. `-63` at unseen `n = 12`, `p_Holm = 0.0112`; `-295` vs `A5_SHAM`, `p_Holm < 1e-6`; `-211` vs `TODD 2018`, `p_Holm < 1e-6`!).

---

## 5. Reproducibility & Complete Receipt Chain

Run the unified verification script to re-verify all unit tests (`106` tests), all `11/11` deterministic SHA-256 benchmark manifests, and frozen `rso/` integrity (`0` bytes modified):
```bash
python scripts/verify_all_composition_sprints.py
```

- Sprint 1 Closeout: [PHASE4_FINAL_CLOSEOUT_RECEIPT.md](file:///F:/Prometheus/comp_sprint/receipts/PHASE4_FINAL_CLOSEOUT_RECEIPT.md)
- Sprint 2 Dual-Track: [SPRINT2_DUAL_TRACK_RECEIPT.md](file:///F:/Prometheus/comp_sprint2/receipts/SPRINT2_DUAL_TRACK_RECEIPT.md)
- Phase 3 Compounding: [PHASE3_COMPOUNDING_RECEIPT.md](file:///F:/Prometheus/comp_sprint2/receipts/PHASE3_COMPOUNDING_RECEIPT.md)
- Sprint 3 Compositional: [SPRINT3_COMPOSITIONAL_COMPOUNDING_RECEIPT.md](file:///F:/Prometheus/comp_sprint3/receipts/SPRINT3_COMPOSITIONAL_COMPOUNDING_RECEIPT.md) & [CROSS_FAMILY_Q3_CLOSEOUT_RECEIPT.md](file:///F:/Prometheus/comp_sprint3/receipts/CROSS_FAMILY_Q3_CLOSEOUT_RECEIPT.md)
- Sprint 4 Dual-Track & Q3: [SPRINT4_DUAL_TRACK_AND_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint4/receipts/SPRINT4_DUAL_TRACK_AND_Q3_RECEIPT.md)
- Sprint 5 Quantum & Law 4 Master: [SPRINT5_QUANTUM_AND_FOUR_LAW_MASTER_RECEIPT.md](file:///F:/Prometheus/comp_sprint5_quantum/receipts/SPRINT5_QUANTUM_AND_FOUR_LAW_MASTER_RECEIPT.md)
- Sprint 6 Law 4b Archive & Law 4c Diagnosis: [SPRINT6_LAW4B_ARCHIVE_RECEIPT.md](file:///F:/Prometheus/comp_sprint6_compound/receipts/SPRINT6_LAW4B_ARCHIVE_RECEIPT.md)
- Sprint 7 Quantum `Clifford+T` & Q3 Audit: [SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint7_clifford_t/receipts/SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md)
- Sprint 8 Mechanistic Science, Literature Circuits & `RM(n-4,n)` 4-Flat Decoder: [SPRINT8_MECHANISTIC_AND_RM_DECODER_RECEIPT.md](file:///F:/Prometheus/comp_sprint8_science/receipts/SPRINT8_MECHANISTIC_AND_RM_DECODER_RECEIPT.md)
