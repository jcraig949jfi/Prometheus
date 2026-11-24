# Synthesis & Adjudication — Prometheus Strategic Reset (v2.0)

**Date:** 2026-11-22  
**Status:** ADJUDICATED TRIAL PROTOCOL — Awaiting Operator Sign-Off on D1 & D2 before Phase 0 execution  
**Inputs adjudicated (preserved verbatim in this directory):**
- Proposal v1: `STRATEGY_AND_EXECUTION_PLAN.md` & `REVIEW_PACKET_FOR_FABLE_AND_ASTRA.md` (Gemini 4 Neon)
- Review 1: `fable_5_2_review.md` (Claude Fable 5.2 — **MODIFY**, audited with repo access)
- Review 2: `astra_review.txt` (ChatGPT Astra — **REJECT AS WRITTEN**, audited packet-only)

---

## 0. Errata on Proposal v1 & Review Packet (Corrections Accepted)

Per Prometheus discipline, three omissions and two inaccuracies caught by Fable 5.2 in `REVIEW_PACKET_FOR_FABLE_AND_ASTRA.md` are recorded on the ledger rather than silently edited away:

1. **Hecate's frozen verdict omitted:** The packet cited Opus 5.5's `0.98` AUC and `0/32` false noise on standard aliens, but omitted Hecate's frozen ruling `NOVELTY_DETECTOR_NOT_VALIDATED` (`19/30` incompressible nulls called `RULE`, `24/30` called `COHERENT`, concluding novelty *"must rest on behavioural and predictive tests ... never on LLM classification alone"*). That directly undercuts Phase 1's LLM-only Gravity Detector.
2. **Beta-04's frozen failure labels omitted:** The packet omitted `TFS1_INSTRUMENT_QUALIFIED = NO`, `WORLD_DEMAND_QUALIFIED = NO` (`5/12` worlds), and fallback-off acquisition (`0/15` frozen, `9/15` with both repairs *and supplied decomposition*).
3. **Bake-off & path inaccuracies:** Fable 5.2's `M0` is unbuilt design text (~1,800 LOC) that yields a rewrite theory `T` (not `(L, T)`), and its own probabilities were `40%` M0 gain / `40%` M1 self-modification / `20%` 2-gen recursion / `8%` transfer (not a flat `8–20%`). Also `CONSTITUTION.md` exists on the local `vivarium` branch, not on `origin/main` (`CHARTER_AND_CONTINUITY.md` is canonical on `origin/main`).

---

## 1. Unanimous Convergences (All 8 Adopted Into v2.0)

Both Fable 5.2 and ChatGPT Astra independently converged on **eight major corrections** to Proposal v1. Every one is adopted cleanly:

| # | Area | Convergent Finding (Fable 5.2 + Astra) | Adopted Change in v2.0 |
|---|---|---|---|
| **1** | **Core Inversion & Operating Reset** | **AGREE:** Kill the 75-seat fleet, freeze flat-genome ALife engines, enforce 3-role cross-family separation, and test LLM-guided abstraction with **LLM unplugged at held-out eval**. | Retained as the backbone of v2.0. Recorded as a **falsifiable trial protocol**, not a premature "governing charter." |
| **2** | **Phase 1 (Gravity Pilot)** | **KILL off critical path:** Gates nothing (both branches advanced), LLM classification cannot certify non-human novelty (asymmetric classification + Hecate `NOVELTY_DETECTOR_NOT_VALIDATED`), 50–64 sample thresholds (`≥5%`) are noise, prose knockouts are unexecuted. | **Removed from critical path.** Hecate behavioural completion (`<$5`) is optional background work only; Gravity Detector deferred until evolved executable artifacts exist to audit. |
| **3** | **Compiled-Priors Control (`PRIOR-ONLY`)** | **ADD IMMEDIATELY:** Without comparing against a frozen LLM-supplied library generated from the language spec *alone* (zero tasks, zero traces, zero evolution), `MG-UNPLUGGED` cannot separate experience-derived learning from textbook priors. | **Mandatory arm from Day 1:** `PRIOR-ONLY` (LLM proposes library/laws from grammar spec alone, zero experience). Only `MG-UNPLUGGED > PRIOR-ONLY` counts as evidence of experience-derived acquisition. |
| **4** | **Domain Choice (Track 3B)** | **UNANIMOUS: Pick Track 3B, kill 3A & 3C.** Symbolic algebra/e-graphs (3A) is maximally prior-saturated and risks unsound bounded verifiers; Lean 4 (3C) carries heavy toolchain friction. | **Commit now to Track 3B** (exact bit-level / circuit synthesis with an independent, exact deterministic verifier and mandatory industry baseline). |
| **5** | **Cut Fable's M0 Engine from Phase 2** | **CUT:** Building M0 (~1,800 LOC, 2 weeks) recreates Wall W3 plumbing drag, confounds `T`-only vs `(L, T)`, and omits schemas/inverse rules. | **Removed.** Use lightweight deterministic library/search learning as the zero-LLM comparator; reserve schemas/inverse rules as a bounded extension only if forward rewriting stalls. |
| **6** | **Honest Amortization (`N*` Curve)** | **FIX:** Single-point `MG-UNPLUGGED` vs `SHADOW-NAKED` is gameable via suite size `N`. Must include failed proposals in fixed cost `F`, match success rates, give direct prompting fair verifier tool access, and report censored failures (never solved-only medians). | Report full **amortization curve & break-even count** `N* = F / (v_L − v_M)` on the common solved set + success-vs-cost Pareto curve. **Demote from toy-world gate to reported metric**; gate only on real-domain hard targets. |
| **7** | **Patch Counterfeit Positives & Gate Math** | **FIX THREE DEFECTS:** (a) Cross-family models share human training priors → counterfeit "prior-matching"; (b) naive knockout is tautological; (c) comparing `G3` on harder tasks than `G1` confounds generation with difficulty. | (a) Require **≥2 distinct task generators, including a 100% procedural/random no-LLM stratum**; (b) replace naive knockout with **size-matched, sound-but-irrelevant `SHAM`** + **cached conventional baseline**; (c) evaluate **all frozen checkpoints (`A1, A2, A3`) on the SAME untouched final holdout** at matched compute (plus Opus 5.5's `θ₀` blank-state acceptance). |
| **8** | **Kill Phase 4 Spec & 70/30 Slogan** | **CUT:** Phase 4 packages 4 unproven hypotheses at once; 70/30 is unmeasured ceremony. | **Delete Phase 4** from current scope (retain only shadow-run/knockout principles). Replace 70/30 with **hard timeboxes, dollar caps, and validity-gap justification** per component. Add Phase-0 task to locate and stop whatever is still committing `auto: portfolio update` and Achilles censuses to `origin/main`. |

---

## 2. Explicit Disagreements Adjudicated (Not Smoothed Over)

Fable 5.2 and ChatGPT Astra disagreed sharply on **two concrete engineering forks**:

### Disagreement A: Role of `TFS-1` (48h Non-Blocking Probe vs. 1-Week Phase 2 vs. Skip Straight to 3B)

| Seat | Position | Core Argument |
|---|---|---|
| **ChatGPT Astra** | **48–72h non-blocking probe, or start 3B in Week 1** | Making a toy substrate (`TFS-1`, whose own frozen labels are `INSTRUMENT_QUALIFIED = NO`, `WORLD_DEMAND_QUALIFIED = NO`, fallback-off `0/15`) a veto gate before entering a real domain is **circular**. Start Track 3B immediately; never let a `TFS-1` failure block 3B. |
| **Claude Fable 5.2** | **Day 1–2 headroom gate → 5-day `TFS-1` dry-run → 3B** | `TFS-1` already has a pinned kernel, cost meter, compress/promote path, and sham arms (`e3/organism.py`). Testing the 5-arm protocol (`BASE-OE`, `ZERO-LLM-LIB`, `MG-UNPLUGGED`, `PRIOR-ONLY`, `SHAM`) for 5 days validates the harness cheaply — *only* if a Day 1–2 depth-2 vs depth-1 headroom check passes first. |

**Adjudication:** **Astra wins on the veto logic; Fable's 48h headroom check is optional, strictly non-blocking.**
- A `TFS-1` failure **must never veto Track 3B** (Astra is 100% right that G2 was circular).
- Running a 5-day `TFS-1` campaign risks spending a full week in an integer-list DSL where Fable itself notes *"model priors are most saturated"* (every frontier model knows `map`/`fold`).
- **Recommended default:** Go **straight to Track 3B on Day 2** (Astra's 28-Day Verified Composition Sprint), optionally running a **≤1-day read-only TFS-1 depth-2 headroom check** in parallel only if we want to close the open Beta-05 question on disk. *(Marked as Operator Decision **D1** below.)*

---

### Disagreement B: Exact Track 3B Starter Domain — Boolean Circuits (Fable) vs. Bit-Vector Superoptimization (Astra)

| Criterion | **Option 3B-Boolean** (Fable 5.2: Min-Size Boolean Circuits) | **Option 3B-BV** (Astra: Verified Bit-Vector Superoptimization) |
|---|---|---|
| **Target** | Minimum-gate circuits over `{AND, XOR, NOT}` (or `{AND, OR, XOR, NOT}`) for 4–8 input single & multi-output Boolean functions | Shorter equivalent fixed-width (8/16/32-bit) SMT-LIB bit-vector programs over `{AND, OR, XOR, NOT, SHL, SHR, ADD, SUB, ITE}` |
| **Exact Verifier** | **Exhaustive bitmask truth table** — microsecond exact, 0 timeouts, 0 external solver instability | **Z3 `UNSAT`** on `∃x: f(x) ≠ g(x)` — exact when `UNSAT`, can hit `UNKNOWN`/timeout on complex 16–32-bit expressions |
| **Zero-Prior Procedural Holdout** | **Native & effortless:** sample random 6–8 input truth tables + multi-output arithmetic/S-boxes — zero pretraining contamination possible | Harder: public SyGuS benchmarks are in LLM pretraining; procedural BV targets still draw from familiar bitwise idioms |
| **Natural Multi-Generation Compounding** | **Direct structural sharing:** multi-output targets (adders, multipliers, popcount, S-boxes, random multi-output cones) reward reusable shared sub-circuits (`L`) directly | Strong: reusable peephole rewrite rules + macro-instructions; closely tracks compiler optimization |
| **Mandatory Industry Baseline** | **`ABC`** (Berkeley logic synthesis) + SAT-based exact synthesis (where it terminates) | **`cvc5`** (SyGuS) + Z3 + Souper-style superoptimizer comparator |
| **Bridge to Non-Human Mechanisms** | **Very high:** exact/evolutionary circuit search routinely finds alien gate topologies humans never write | Moderate: closer to known Hacker's Delight / compiler peephole identities |

**Adjudication:** **Recommend Option 3B-Boolean (Fable 5.2) as the Day-1 Track 3B starter slice, with Z3 equivalence (Astra) as the clean scaling bridge beyond 8 inputs.**
- **Why 3B-Boolean wins on Day-1 ROI:**
  1. **Speed & determinism:** Exhaustive 64-bit/256-bit truth-table bitmask verification in Python/NumPy runs in microseconds — completely eliminating the slow verification loops that crippled SFE and Aether.
  2. **Unfakeable held-out stratum:** Random multi-output 6–8 input Boolean functions are mathematically immune to LLM training-corpus memorization and eliminate the "World-Demand Foundry" problem completely.
  3. **Tabulated calibration + brutal baseline:** Exact 4-input NPN optima verify the harness on Day 1, while `ABC` (and SAT-exact synthesis) guarantees we cannot celebrate beating naive enumeration.
- **Note:** If you prefer compiler-level bit-vector superoptimization (`3B-BV` with Z3 + `cvc5`), the exact same 28-day experimental architecture and 6 arms apply unchanged. *(Marked as Operator Decision **D2** below.)*

---

## 3. The Revised Plan: 28-Day Verified Composition Sprint (v2.0)

### 3.1 The Explicit Four-Rung Claim Ladder (Adopted from Astra)
Every experiment receipt must state **exactly which rung** it tests and never overclaim into a higher rung:
1. **Claim 1 — Crystallization:** Useful model-derived knowledge compiles into compact, deterministic, LLM-free machinery (`PRIOR-ONLY` or `MG-UNPLUGGED` > `BASE`).
2. **Claim 2 — Autonomous / Experience-Derived Composition:** Learned intermediate structures acquired from experience beat a frozen `PRIOR-ONLY` library and a `SHAM` library, and causally enable solving held-out Order-2 targets (`MG-UNPLUGGED` or `ZERO-LLM-LEARN` > `PRIOR-ONLY` & `SHAM`).
3. **Claim 3 — Generational Compounding:** Frozen checkpoints `A1 → A2 → A3` monotonically improve on the **same untouched final holdout distribution** under matched evaluation compute, with knockout removing the gain and `θ₀` blank-state checks confirming genuine inherited leverage.
4. **Claim 4 — Low-Prior / Non-Human Novelty:** *Explicitly out of scope for this 28-day sprint.* Deferred until Claims 2–3 are empirically established on disk.

### 3.2 Mandatory Six-Arm Design + Industry Baseline (Fixed Pre-Run)

| Arm | Sleep / Evolution Input | Held-Out Eval (LLM OFF) | What It Isolates |
|---|---|---|---|
| **A0: `BASE`** | None | Base deterministic synthesizer | Floor capability |
| **A1: `INDUSTRY`** | None | **`ABC`** + SAT-exact (3B-Boolean) or **`cvc5`** (3B-BV) at matched wall time | Prevents celebrating wins over weak search |
| **A2: `PRIOR-ONLY`** | Frontier LLM proposes library/macros/rewrites from **language spec alone** (0 tasks, 0 traces) | Frozen `(L_prior, T_prior)` offline | **Compiled human priors** ceiling |
| **A3: `ZERO-LLM-LEARN`** | Pure deterministic subcircuit/abstraction mining (no LLM) | Frozen `(L_det, T_det)` offline | Autonomous non-LLM acquisition |
| **A4: `MG-UNPLUGGED`** | Frontier LLM inspects dev failure traces + search bottlenecks, proposes verified subcircuits/macros/rules/search weights | Frozen `(L_mg, T_mg, S_mg)` offline | **Primary Claim 2/3 test** |
| **A5: `SHAM-MATCHED`** | Size-matched, verified-valid but task-irrelevant library (random valid subcircuits or wrong-domain LLM library) | Frozen sham library offline | Rules out vocabulary-size / search-bias artifacts |
| **A6: `SHADOW-NAKED`** *(reported, not a toy gate)* | None | Direct frontier LLM + same exact verifier tool on held-out tasks | Full amortization curve `N* = F / (v_L − v_M)` |

### 3.3 Mandatory Two-Stratum Untouched Holdout (Anti-Prior-Matching Defense)
To kill the single highest-probability counterfeit positive identified by both reviewers (shared-corpus motif matching):
- **Stratum 1 (Structured Real Targets):** Multi-output arithmetic / cryptographic / combinational targets (e.g., adders, small multipliers, popcount, 4–6-bit S-boxes, bit-permutation networks — 3B-Boolean; or non-public composite BV kernels — 3B-BV), benchmarked against published best-known gate/op counts.
- **Stratum 2 (100% Procedural / Zero-Author-Bias Targets):** Randomly sampled 6–8 input multi-output Boolean functions with bounded compositional sharing (zero LLM in target generation).
- **Qualification check (4 mechanical rules, no tribunal):** (1) Verified valid target, (2) `BASE` fails to reach optimum/target cost at eval budget, (3) Order-2 sharing check (multi-output / 2-stage sharing beats independent per-output synthesis), (4) Frozen and sealed before any treatment arm runs; **all 3 generational checkpoints (`A1, A2, A3`) evaluated on this exact same untouched holdout**.

### 3.4 Concrete 28-Day Schedule & Hard Kill Points

| Window | Milestone | Concrete Deliverables | Hard Stop / Pivot Gate |
|---|---|---|---|
| **Days 1–2** *(Phase 0)* | **Clean Slate & Environment** | 1. Tag `vivarium` snapshot; create ONE clean branch/worktree `reset/verified-composition-2026-11` off `origin/main` (`9884ac934`).<br>2. Locate & disable whatever process is still pushing `auto: portfolio update` and Achilles census commits to `origin/main`.<br>3. Verify `rso/adversary` green; install/verify verifier (`ABC` + truth-table kernel for 3B-Boolean, or Z3 + `cvc5` for 3B-BV).<br>4. *(Optional per D1)* Run ≤1-day read-only `TFS-1` depth-2 headroom probe. | Clean git tree, 0 background census commits, exact verifier + industry baseline working on 4-input calibration table (100% agreement with tabulated NPN optima). |
| **Days 3–7** *(Phase 1 — Build & Qualify)* | **Minimal Engine + Sealed Holdout** | 1. Build lean package `comp_sprint/` (≤1,200 LOC, unified work meter from line 1, zero edits to frozen `rso/`).<br>2. Generate, qualify, and **cryptographically freeze** Stratum-1 (structured) and Stratum-2 (procedural) held-out suites + dev split.<br>3. Run **A0 (`BASE`)**, **A1 (`INDUSTRY`)**, and **A2 (`PRIOR-ONLY`)** first to verify non-saturation (`BASE` neither 0% nor 100%, measurable headroom against `INDUSTRY` or exact optima). | **KILL / ADJUST TARGET DIFFICULTY** if `BASE` saturates (≥90%) or flatlines at 0% on dev, or if `PRIOR-ONLY` already saturates the holdout (means targets are too textbook). |
| **Days 8–14** *(Phase 2 — Claim 1 & 2 Test)* | **Single-Generation 6-Arm Run** | 1. Run **A3 (`ZERO-LLM-LEARN`)**, **A4 (`MG-UNPLUGGED`)**, **A5 (`SHAM-MATCHED`)**, and **A6 (`SHADOW-NAKED` with verifier tool)** across ≥3 paired seeds.<br>2. Emit full 4-row Cognitive Accounting Ledger + `N*` amortization curve + censored failure counts + per-stratum breakdown.<br>3. Register reducer as an `rso/adversary/` target (`0 SURVIVED`, `0 VACUOUS`). | **Gate G-Comp (Claim 2):** Proceed to multi-generation compounding ONLY if `A4` (or `A3`) beats **both** `A0`, `A2 (PRIOR-ONLY)`, and `A5 (SHAM)` on **at least one stratum including Stratum 2 (procedural)** with paired-seed consistency. If `A4 ≈ A2`, log honest `COMPILED_PRIORS_ONLY` result and diagnose before spending Week 3. |
| **Days 15–22** *(Phase 3 — Claim 3 Compounding)* | **3-Generation Compounding (`A1 → A2 → A3`)** | 1. Run 3 sequential evolution generations on progressively expanding dev slices, freezing artifact snapshots `A1 = (L1, T1, S1)`, `A2`, `A3`.<br>2. Evaluate **`A1`, `A2`, `A3` on the SAME untouched final holdout** at identical eval budgets (plus matched-size library controls & selective knockouts removing G2/G3-acquired structures).<br>3. Run Opus-style blank-state (`θ₀`) check + Weaker-Model/Offline-Solver transfer check against `A1 (INDUSTRY)` and `A6 (SHADOW-NAKED)`. | **Gate G-Recurse (Claim 3):** Confirmed ONLY if `A3 > A2 > A1` (or `A3 > A1` with statistical separation across seeds) on the shared untouched holdout, **survives Stratum 2**, **disappears under selective knockout**, and **is not reproduced by matched-size `SHAM`**. |
| **Days 23–28** *(Phase 4 — Independent Falsification)* | **Cross-Family Q3 Attack & Closeout** | 1. Hand frozen receipts, code, and holdout results to the **Cross-Family Adversary** (different model family than Builder).<br>2. Attack: unseen target-family shift, `rso/adversary/` suite, semantic-equivalence audit, cost-accounting audit, re-expression check.<br>3. Publish final honest verdict (`CLAIM_1` / `CLAIM_2` / `CLAIM_3` / `NEGATIVE` / `INCONCLUSIVE`) with full reproducibility receipt. | Hard stop at Day 28 regardless of outcome. Zero scope extension without a fresh operator decision. |

### 3.5 Hard Budget Ceiling (Entire 28-Day Sprint)
- **API Spend Cap:** `≤ $100` total across all sleep-phase proposals, `PRIOR-ONLY`, `SHADOW-NAKED`, and Cross-Family Q3 review (tracked in `F` including all failed proposals).
- **Compute:** Local CPU / single local GPU only (`$0` cloud).
- **Operating Roles:** 3 roles max (Builder / Cross-Family Adversary / Operator). Zero fleet seats, zero background daemons.

---

## 4. Two Operator Decisions Required Before Day 1 Starts

Everything above is aligned and ready to execute. Only **two explicit choices** need your call to lock the protocol and begin Phase 0:

1. **Decision D1 — `TFS-1` Dry-Run vs. Straight to Track 3B:**
   - **Option D1-A (Recommended — Pure Astra Sprint):** Skip `TFS-1` completely; start **Track 3B** on Day 2 after Phase 0 cleanup. Zero toy-world time risk.
   - **Option D1-B (Hybrid):** Run a strictly capped **≤1-day read-only `TFS-1` depth-2 headroom check** in parallel on Day 2 (never blocks Track 3B).

2. **Decision D2 — Exact Track 3B Starter Domain:**
   - **Option D2-A (Recommended — Fable's `3B-Boolean`):** Minimum-size Boolean circuits (`{AND, XOR, NOT}` / `{AND, OR, XOR, NOT}`), microsecond exhaustive truth-table verifier, 4–8 input single & multi-output targets (structured arithmetic/S-boxes + 100% random procedural stratum), mandatory `ABC` + SAT-exact baseline. *(Clean Z3 bridge later for 16-bit.)*
   - **Option D2-B (Astra's `3B-BV`):** Verified 8/16-bit SMT-LIB bit-vector superoptimization, Z3 `UNSAT` exact verifier, `cvc5` SyGuS baseline + custom procedural BV expressions.

---

## 5. Operator Sign-Off (2026-11-22)

- **D1:** `D1-A` selected (skip `TFS-1`; go straight to Track 3B after Phase 0).
- **D2:** `D2-A` selected (Track `3B-Boolean`: minimum-size Boolean circuits over fixed basis `{AND, XOR, NOT}`, exhaustive bitmask truth-table verifier, 4-input NPN exact calibration, 4–8 input single & multi-output structured + 100% procedural holdout strata, mandatory industry/exact synthesis baseline).
- **Branch:** `reset/verified-composition-2026-11` branched from `origin/main` @ `9884ac934`.
- **Auto-committer audit (Phase 0):**
  - `auto: portfolio update` (`9884ac934`) originates from `scripts/intelligence_loop.py` (configured for M4 / `pythonw`); **0** matching Windows scheduled tasks exist on this host.
  - `Achilles[census]` (`5633cc02a`) originates from **ELSA** (`Built from origin/main ... by ELSA`), not this host. Both last pushed `2026-11-12/13`. Any remaining cron/daemon on ELSA or M4 must be quiesced there if still active.
