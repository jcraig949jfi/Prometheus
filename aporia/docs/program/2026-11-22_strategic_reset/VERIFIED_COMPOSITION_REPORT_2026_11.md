# Verified Compositional Algorithm Evolution: Empirical Evidence Across Four Formal Domains and Four Engineering Laws

**Program:** Project Prometheus — Verified Composition Program (`reset/verified-composition-2026-11`)  
**Date:** 2026-11-26  
**Builder / Proposer Provenance:** 100% `claude-opus-5-5` (`0` silent fallbacks across Sprints 1–7)  
**Independent Cross-Family Q3 Adversary:** OpenAI open-weights `groq:openai/gpt-oss-120b` (strictly non-Anthropic; 4 independent closeout audits archived; **Final Independent Program Grade: `3.8 / 5` [`B+`], Scientific Rigor `4.5 / 5`, Cross-Domain Impact `4.0 / 5`**)  
**Frozen Integrity Apparatus (`rso/`):** `0` bytes modified (`git diff -- rso/` empty); **`6/6` hardened 3-seed RSO tamper attacks REJECTED** (`0 SURVIVED, 0 VACUOUS`) on every live packet  
**Total Verified Offline Evidence Base:** **15,570+ verified 100%-offline evaluation rows** (LLM completely unplugged at eval) across **4 independent formal domains**  
**Total Cumulative Equivalent Spend (Including ALL Aborted/Erratum/Rejected Runs):** **`~$36.08 / $100.00` (`36.1%`)**

---

## Abstract

We investigate whether frontier language models can compile domain knowledge and empirical failure telemetry into **compact, standalone, formally verified, LLM-free algorithms** that strictly outperform both published domain baselines and prior-only compiled algorithms — and whether successive generations can **compound compositionally** without human intervention. Across seven structured experimental sprints spanning **15,570+ verified offline evaluations** over **four independent formal domains** — (1) Combinational Boolean Logic (`XAG`, 4–11 inputs), (2) 16-Bit SMT Bit-Vector Superoptimization (`Z3 UNSAT`), (3) Reversible/Quantum Linear Circuits (`GL(n, F_2)` CNOT synthesis vs. published Patel–Markov–Hayes 2008), and (4) Fault-Tolerant Quantum `Clifford+T` `T`-Count Minimization (`n = 6..8` qubits vs. published `T-par` 2014 & `TODD` Heyfron–Campbell 2018) — we evaluate every artifact against a strict Four-Rung Claim Ladder under an untouched, frozen tamper-evident adversarial audit suite (`rso/`).

Our findings establish five concrete empirical results:
1. **Claim 1 (Executable Algorithm Crystallization) is confirmed across all four formal domains** (`p_Holm < 1e-6`), beating Berkeley `ABC 1.01`, the Z3 C++ simplifier, published Patel–Markov–Hayes 2008 (`-28.5%` CNOTs), published `T-par` 2014 (`-28.5%` `T`-gates), published `TODD` 2018 (`-8.9%` overall / `-11.2%` procedural, `35W/0L`, `p_Holm < 1e-6`), and full-budget matched random baselines with the LLM completely unplugged at evaluation.
2. **Claim 2 (Experience Beyond Compiled Priors, including 100% Procedural Zero-LLM Holdouts) is cleanly confirmed in two independent formal domains** — Combinational XAG (`p_Holm = 0.0060` overall; `p_Holm = 0.0131` procedural, `30%` faster wall time than `A2_PRIOR_ONLY`) and 16-Bit Z3 BV (`p_Holm < 1e-6` overall; `p_Holm = 0.000032` procedural; surviving Law 4 64-bit word + Z3 `rlimit_count` metering at `p_two = 3e-6` / `6.1e-5` with 0 losses) — plus directional 3-seed replication in Quantum CNOT (`p_two = 0.0266`, `p_Holm = 0.133`; matched-op knockout `p_Holm = 0.00086`) and **wall-clock-faster superiority over full-budget random TODD (`A5_SHAM`, `0.88×` wall, `p_Holm = 0.000134`) and `G2`/`KO_MATCHED_LAST` (`0.81× / 0.97×` wall, `33W/0L`, `p_Holm < 1e-6`)** in Quantum `Clifford+T` (with `A2_PRIOR_ONLY` explicitly caveated due to early exit).
3. **Claim 3 (Multi-Generation Compositional Compounding) is verified up to two wall-clock-clean compositional generations across three domains** (`A2→G1→G2` in XAG and Quantum CNOT; `G2→G3` in Quantum `Clifford+T`), demonstrating genuine coupled **mechanism + representation** discovery (`mod_g1_peel → mod_g2_net` [`191k` calls], `mod_g1_beam_reduce → mod_g2_fast_bidir` [`142.5k` calls], `mod_g2_todd_search → mod_g3_null_todd` [`413.2k` calls, running faster than both `G2` and `A5_SHAM`]).
4. **Four Empirical Laws (plus Law 4b/4c Refinements) govern when offline evolution compounds vs. generates counterfeit meter exploits:** (1) deterministic execution budgets, (2) disjoint per-generation validation splits with paired statistical promotion gates, (3) compositional module libraries with matched-op causal knockouts, and (4) word-width + container + solver-decision + native-helper metering (`OpBudget v2/v3` → Law 4c).
5. **Ruthless Empirical Self-Falsification Works:** Our metering audits explicitly caught and downgraded **two** apparent wins — `S4-B G4` (50,000-bit Python int arbitrage under `OpBudget v1`) and `Sprint 6 G1` (`davio_synth` flat 180-unit API-primitive pricing loophole under `OpBudget v3`) — keeping the verified positive frontier strictly free of counterfeit speedups.

---

## 1. Experimental Protocol & Anti-Counterfeit Methodology

Every experiment in Sprints 1–7 enforces six non-negotiable methodological invariants:

1. **Zero LLM at Evaluation (`$0.00` Eval):** Evolved artifacts are frozen, AST-validated, SHA-256 content-addressed Python modules/libraries executed 100% offline with zero network or LLM access.
2. **Zero Macro-Call Discount:** All costs measure exact flattened primitive counts (`AND + XOR` gates in XAG; live primitive SSA ops in 16-bit BV; primitive `CNOT` gates in Quantum `GL(n, F_2)`; exact `T`-gates in Fault-Tolerant `Clifford+T`).
3. **100% Exact Mathematical Verification:** Exhaustive `2^n`-bit truth-table equality for XAG; exact isolated-context Z3 `UNSAT` equivalence over all `2^(16*k)` inputs for BV; exact matrix-group multiplication over `GL(n, F_2)` for Quantum CNOT; exhaustive `2^n`-state unitary phase-polynomial verification for `Clifford+T`. Unsound candidates are rejected monotonically.
4. **Procedural Zero-LLM Holdout Strata:** Every holdout combines structured benchmarks with 100% procedurally generated tasks from disjoint RNG seeds, eliminating human-textbook memorization as an explanation for gains.
5. **Hardened 3-Seed RSO Tamper-Evident Audit:** Every evaluation packet is reduced across 3 paired seeds `{0, 1, 2}` with all-seed checksums (`sum_all_cost`, `min_all_cost`, `max_all_cost`) and audited live against 6 adversarial attacks (`DROP`, `DUPLICATE`, `REWRITE_DERIVED`, `SINGLE_SEED_TAMPER`, `SCRUB_SPEC`, `MANIFEST_TAMPER`). Every live packet achieved **`6/6 REJECTED` (`0 SURVIVED, 0 VACUOUS`)**.
6. **Cross-Family Adversarial Adjudication:** All claims are audited by a strictly non-Anthropic model (`groq:openai/gpt-oss-120b`), with all valid caveats permanently attached to the verdict.

---

## 2. Chronological Empirical Arc (Sprints 1–7, 4 Formal Domains)

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
| **Sprint 5 — S5-Q** *(All 4 Laws Native)* | Quantum `GL(n, F_2)` CNOT (12–18q, 140 tasks) | Compositional `LibModule` (`OpBudget v2` native) | 1,320 | `$3.55` | **PASS** (**`-28.5%` / `-975` CNOTs vs PMH 2008**, `p_Holm < 1e-6`) | **Directional** (`-49`, CI `[-1.98, -0.27]`, `p_two = 0.0266`, `p_Holm = 0.133`; **KO `p_Holm = 0.00086`**) | **2-Step 3-Tier** (`A2→G1→G2`, `0.998×` wall parity, `142.5k` calls) | 3rd formal domain; `G2` invokes BOTH `G1` (`97k`) & `G0` (`33k`) at `48.15s` vs `48.22s`; residual Python dict overhead (`48s` vs `A2` `16s`) motivated Law 4b. |
| **Sprint 6 — S6** *(Law 4b Archive)* | XAG 8–10in (172 tasks) | Compositional `LibModule` (`OpBudget v3`) | 1,452 | `$2.44` | Discounted (`davio_synth` loophole) | **DOWNGRADED (Law 4c Exposure)** | **Gated** (`G2..G4` rejected by Law 2) | **Exposed Law 4c:** un-instrumented native helper `davio_synth` (priced at 180 units) let `G1` run `295k` calls (`1,180s` vs `19.4s`); downgraded per ruthless falsification + Q3. |
| **Sprint 7 — S7-CT** *(4th Domain, Law 4b)* | Fault-Tolerant Quantum `Clifford+T` (`n = 6..8q`, 140 tasks) | Compositional `LibModule` (`OpBudget v3` native) | 1,452 | `$4.45`*** | **PASS** (**`-8.9%` / `-70` `T`-gates vs `TODD` 2018**, `35W/0L`, `p_Holm < 1e-6`; Proc **`-11.2%`**, `23W/0L`, `p_Holm < 1e-6`) | **PASS vs Full-Budget Controls** (`A5_SHAM`: `0.88×` wall, `p_Holm = 0.000134`; `KO`: `0.97×` wall, `p_Holm < 1e-6`); **CAVEATED vs `A2`** | **2-STEP PASS** (`G2→G3`: `-68` `T`-gates, `33W/0L`, `p_Holm < 1e-6`, **`0.81×` wall**, `413.2k` calls) | **4th formal domain breakthrough:** pure-Python `mod_g3_null_todd` beats published `TODD (2018)`, full-budget `A5_SHAM`, and `G2`/`KO` while running **faster in wall time** than `A5_SHAM`, `G2`, and `KO`! |

*\*All USD figures represent `claude -p` API-equivalent usage drawn from the operator's Claude subscription, honestly including every failed/rejected proposal.*  
*\*\*Sprint 3 spend includes `$2.98` clean v2 + `$4.58` errata (`$4.13` v1 run aborted after catching `MeteredStrashBuilder._gates` bug + `~$0.45` pre-unpacking CLI call).*  
*\*\*\*Sprint 7 spend includes `$2.13` clean v2 + `$2.32` logged v1 erratum (prompt omitted listing `getattr`/`hasattr` as AST-forbidden).*

---

## 3. The Four Empirical Laws (with Law 4b/4c Refinements)

The central methodological contribution of this program is the empirical isolation of **four necessary engineering laws** for falsifiable offline algorithm compounding:

1. **Law 1 — Deterministic Execution Budgets (Zero Jitter):** Wall-clock caps inject non-reproducible noise that destroys generational selection (Phase 3's 13-op Z3 swing on identical code). AST loop instrumentation + isolated `z3.Context()` `rlimit` counters yield exact `0.000` variance across all four domains.
2. **Law 2 — Disjoint Per-Generation Validation Splits + Paired Statistical Gates:** Reusing a small validation set produces monotonic `dev_val` Goodharting while holdout degrades (Phase 3). Disjoint hidden validation splits (`val_g1..val_gK`, `N ≥ 20–25`) gated by exact paired Wilcoxon `p_less < 0.05` (`< 0.025` Bonferroni on retry) prevented every noisy regression across Sprints 3–7.
3. **Law 3 — Compositional Verified Libraries + Matched-Op Causal Knockouts:** Flat pass lists force redundant rewrites; generation-tagged `LibModule` libraries enable **coupled mechanism + representation evolution** (`mod_g1_peel → mod_g2_net` in XAG; `mod_g1_beam_reduce → mod_g2_fast_bidir` in Quantum CNOT; `mod_g2_todd_search → mod_g3_null_todd` in Quantum `Clifford+T`), verified causally by matched-op knockouts.
4. **Law 4 — Complete Compute-Proportional Metering (`OpBudget v2 → v3 → 4c`):**
   - **4a (`OpBudget v2`):** Meter 64-bit big-int word-ops `(bit_length - 1) // 64` and exact Z3 `rlimit_count` (exposed `S4-B G4` 50,000-bit int arbitrage).
   - **4b (`OpBudget v3`):** Meter container allocations (`dict/set = 4 + 2*len`, `list/tuple = 2 + len`, `sorted = 4 + n*log2(n)`) and function calls (`3` units) — directly enabling Sprint 7's **`0.81×–0.97×` wall-clock parity** across pure-Python search engines!
   - **4c (Native Helper Pricing — Diagnosed in Sprint 6):** Every un-instrumented native API helper (e.g., `davio_synth`) MUST also be charged in exact `OpBudget v3` word-op equivalents rather than flat stubs (`180` units), otherwise evolution rationally spams the underpriced native helper.

---

## 4. Complete Permanent Caveats, Errata & Open Frontier Ledger

1. **Mandatory Sprint 7 Q3 Caveat (Attached Verbatim per `groq:openai/gpt-oss-120b`):** *All wall-clock-clean claims in Sprint 7 are conditioned on the full-budget metering regime defined by Law 4b. The `A2_PRIOR_ONLY` baseline in Sprint 7 exits after only `3,300` `v3_ops`, far below the allotted `1,600,000` units, and therefore cannot be used as a wall-clock-clean comparator. All reported wall-clock speed-up ratios are computed against full-budget baselines (`A5_SHAM`, `KO_MATCHED_LAST`, `G2`) that consume comparable op-budget and are subject to the same metering costs.*
2. **Sprint 6 Law 4c Downgrade:** Sprint 6 `G1` (`mod_g1_ordersearch`) achieved `-220` XAG gates (`p_Holm = 0.00004`) by calling underpriced `davio_synth` `295,454` times (`1,180s` vs `A2`'s `19.4s`). Permanently classified as a Law 4c loophole exposure, not a clean algorithmic win.
3. **S4-B `G4` Law 4a Arbitrage Exposure:** Under `OpBudget v1`, S4-B `G4` achieved `-253` gates (`p_Holm < 1e-6`), but `OpBudget v2` exposed 50,000-bit Python int arbitrage (`633.5s` vs `89.9s`) and reversed the gain.
4. **S5-Q Multiplicity & Container Overhead:** `G2 vs A2_PRIOR_ONLY` on Quantum CNOT is `p_two = 0.0266` (`p_Holm = 0.133` under 11-way Holm) with `3.0×` dict overhead (`48.15s` vs `15.96s`), while `G2 vs G1` matched wall time (`0.998×`) and `G2 vs KO_MATCHED_LAST` passed Holm (`p_Holm = 0.00086`).
5. **Berkeley `ABC 1.01` AIG→XAG Caveat:** `A1_ABC_XAG` folds AIG output to XAG post-hoc; Claim 1 & 2 on XAG rest primarily on native XAG controls (`A0`, `A3`, `A5_SHAM`, `A2_PRIOR_ONLY`).
6. **Hardest Open Frontiers (Unproven):** (a) **3+ wall-clock-clean compounding generations** (`G0 → G1 → G2 → G3+`) under full Law 4c metering; (b) scaling holdouts (`N ≥ 200`) and problem dimensions (`> 10` XAG inputs, `≥ 10` `Clifford+T` qubits).
7. **Logged Cognitive Accounting Errata (All Included in `$36.08` Total):** Sprint 1 Phase 2B `$0.1198` `A6` exception-handler miss; Sprint 3 v1 `$4.13` `MeteredStrashBuilder._gates` bug + `~$0.45` pre-unpacking CLI error; Sprint 7 v1 `$2.32` `getattr`/`hasattr` prompt-omission erratum.

---

## 5. Reproducibility & Complete Receipt Chain

Run the unified verification script to re-verify all unit tests (`104` tests), all `10/10` deterministic SHA-256 benchmark manifests, and frozen `rso/` integrity (`0` bytes modified):
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
- Sprint 7 Quantum `Clifford+T` & Final Q3 Audit: [SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md](file:///F:/Prometheus/comp_sprint7_clifford_t/receipts/SPRINT7_CLIFFORD_T_AND_Q3_RECEIPT.md)
