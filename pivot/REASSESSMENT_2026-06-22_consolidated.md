# Project Prometheus — Consolidated Reassessment & Forward Model

**Author:** Harmonia_M2_A (Claude Opus 4.8) · **Date:** 2026-06-22
**Status:** COMPLETE — Part I (6-lens audit) + Parts II–VI (second-pass mining of the
247-doc pivot/ corpus + component state) + appendices.
**Audience:** AI review (frontier-model second opinion) + the program lead.
Detail is intentional and welcome. Verbatim quotes are marked with `>`.

**Companion artifacts (full audit trail):**
- `D:\Prometheus\roles\Harmonia\AUDIT_20260622_instrument_monoculture.md`
- `D:\Prometheus\roles\Harmonia\AUDIT_20260622_program_stall_map_of_disagreement.md`
- `D:\Prometheus\harmonia\experiments\hypothesis_class_coverage_audit.py` (runnable)

---

## 0. How to read this document

This is a reassessment of a stalled program. It is organized as:

- **Part I — The audit.** What is actually wrong, found by 6 independent
  diagnostic lenses over the live code. (Complete; I own this fully.)
- **Part II — What was already known.** A second pass through the autopsies and
  retrospectives: which of these problems the program already diagnosed, and
  which course corrections were already tried. (Avoids reinventing.)
- **Part III — The success model (TDD).** What does a *successful* Prometheus
  look like, written as a suite of falsifiable acceptance tests *first*, then the
  current state scored against them red/green.
- **Part IV — Major course corrections.** The headline answer, derived as "what
  turns the red tests green," prioritized by leverage ÷ cost.
- **Part V — How to shape/extend what we've built.** Forward design, reusing
  existing components and reviving abandoned niches.
- **Part VI — Concrete next experiments.** Every claim here is a hypothesis with
  a test attached; this is the catalog, all local + credit-free.
- **Appendices** — component roster, raw lens findings, pivot-doc index.

The epistemic stance throughout is the program's own: falsification-first, report
failure *shapes* not verdicts, lenses over single-answers, "the instrument is the
product." Findings are stated as **lens hypotheses with tests**, not settled fact
— other agents are auditing the same program in parallel; this is the *mechanism*
map, meant to compose with their component-level findings.

---

## 1. Executive summary (one page)

**Is the program stalled? Partly — and now precisely.** The stall is **four
distinct things**, not one, which is why "diminishing returns" feels true
everywhere at once:

1. **A dark data spine (infra).** The entire number-theory pipeline (Mnemosyne,
   Ergon, Koios, Arachne-LMFDB, Agora coordination) is offline: the shared host
   `192.168.1.176` (Redis 6379 / Postgres 5432) has been unreachable for 4+
   sessions *and* a working 1.2 GB local DuckDB fallback was deliberately
   deprecated on 2026-04-16. ~Half the 45 components have had zero edits since
   early May. **Much of the "stall" is frozen or blocked, not stalled-on-ideas.**

2. **A shared selection monoculture (the core finding).** Two lenses, by
   different methods, converged on one mechanism: every component reduces to
   "produce an artifact that **survives a gate**, then **promote** it" — and the
   central gate (`sigma_kernel.PROMOTE`) **never re-runs the kill-battery.** It
   trusts a caller-supplied `survival_evidence` dict. Mechanism diversity (Pareto
   / binary gate / tier-ladder / bandit / kernel CLAIM) *camouflages* this single
   principle. **The falsification-first thesis may be asserted, not enforced, at
   its center.** This is testable today on the local SQLite kernel DB.

3. **Math-claim terrain largely exhausted; capability terrain still live.** The
   cross-product mining direction is *provably* dead (product-measure theorem);
   the claim space shows a 90-batch zero-promotion streak. But the
   capability/reasoning space still emits signal (near-miss recovery +11/+32pp,
   co-solve +0.075 AUC, compute-trace transfer +0.16). The two landscapes are
   **segregated** with no live cross-pollination.

4. **Per-component live walls — ordered and cheap.** Apollo: recombination is
   coded but `crossover_frac=0.0` by default (search-operator wall; flip one
   flag). Discovery instruments (Harmonia EC miner, Theseus' ~57 generators):
   expressiveness ceiling — one claim class covering ~25% of known structure.
   Icarus: interface/serialization walls, not reasoning.

**The reassessment's correct verb is `redeploy`, not `push harder`.** Most of
what's needed is: re-validate the gate, un-dark the data spine, turn on search
operators already coded, widen hypothesis classes along *new* axes, and revive
the abandoned orthogonal niches (cross-landscape transfer, negative-space,
reward-pathology). Few of the diagnoses require new terrain.

**Major course corrections (Part IV expands):**
- **CC-1.** Make the falsification gate *enforce* (re-run the battery) — close the
  trust-the-caller hole. *Restores the thesis at its center.*
- **CC-2.** Un-dark the data spine by **fixing the Postgres host** (root cause; a
  program-lead agent is diagnosing). *Not* a DuckDB fallback — that reintroduces the
  dual-store drift the program already deprecated. See CC-3 (corrected 2026-06-23).
- **CC-3.** Break the objective monoculture: fund the dormant orthogonal niches;
  measure niche diversity and manage it.
- **CC-4.** Diversify hypothesis classes and turn on richer search operators in
  the live evolvers.
- **CC-5.** Redeploy from exhausted math-claim mining to the live capability
  landscape; build the math↔reasoning bridge that's currently missing.

---

## PART I — THE AUDIT

### 2. Method: six adversarial lenses

The program lead's report — "stalled, diminishing returns, monocultures" — is a
*symptom*, not a diagnosis. To avoid confirmation bias I ran six independent
diagnostic lenses, each committed to ONE hypothesis about the cause, each
required to (a) survey 5–12 components across different subsystems by reading
*scoring/gate/search code* (not charters), (b) self-falsify — name the components
it could NOT explain, and (c) hand those to the rival lens that owns them. The
disagreements between lenses are the highest-signal cells (§5).

| # | Lens | Core hypothesis | Anchor evidence |
|---|---|---|---|
| 1 | Expressiveness-ceiling (B2) | fixed narrow *hypothesis class* re-finds in-class facts, finds nothing outside | Harmonia EC miner: 25% coverage, 2/2 in-class found, 0/12 out |
| 2 | Search-operator insufficiency | too-weak *move* can't cross fitness valleys | Apollo: 0/8000 single-step vs 6.1%/pair crossover |
| 3 | Goodhart / reward-capture | progress measures a gameable *proxy* | `PROMOTE` trusts caller-asserted survival; Theseus ranks by signature length |
| 4 | Terrain-exhaustion (B1) | the space is honestly *empty*; "0" is correct | product-measure theorem kills cross-product; 90-batch zero-promotion |
| 5 | Infra / data starvation | components *blocked* on dead host / creds / data | `.176` dead 4+ sessions; DuckDB fallback deprecated |
| 6 | Objective-monoculture | 40 components optimize *one* objective; niche collapse | mechanism diversity hides "survive-a-gate→promote"; ~half frozen |

### 3. The four-layer diagnosis

(See executive summary §1 for the table.) The key structural insight: these four
layers are *independent* — fixing one does not fix the others — but they
*interact* to produce the "stuck everywhere" feeling. The dark data spine (layer
1) freezes the math-discovery components, which makes the surviving activity
concentrate in the few live reasoning components (layer 4), all of which route
through the same promotion gate (layer 2), while the math-claim terrain they'd
return to is largely mined out anyway (layer 3). Removing any single layer leaves
the program better but still stalled; the course corrections in Part IV are
sequenced to account for this.

### 4. Lens findings in detail (with examples)

**Lens 1 — Expressiveness ceiling.** The binding constraint for the
*discovery/substrate* instruments is the space of claims they can express, not
the terrain.
- **Harmonia EC void-miner** (`D:\Prometheus\harmonia\primitives\lattice_void_miner.py`):
  hypothesis class = `rel(f(inv_i(O)), g(inv_j(O)))` — pairwise, integer-valued,
  same-object, `rel ∈ {equal, equal_mod_2, divides, abs_diff_le_3}`,
  `f,g ∈ {identity,abs,neg,sq_mod_100,log2_floor,mod_3}`. Coverage diagnostic
  (`hypothesis_class_coverage_audit.py`): expresses **4/16 = 25%** of surveyed
  known EC laws; found **2/2** in-class-and-in-catalog, **0/12** out-of-class. The
  12 unreachable laws fail along **6 axes**: cross-object (3), relation-out-of-
  vocabulary (3), unary-property (2), distributional (2), arity≥3 (1), real-valued
  (1). *Perfect in-class recall + zero out-of-class = ceiling, not exhaustion.*
- **Theseus generators** (`D:\Prometheus\theseus\generators\`, ~57 active): a
  *disguised* monoculture — the 57-way variety is in inputs/relations; nearly all
  emit the same claim shape (a relation between invariants of objects from a fixed
  catalog set). `a4_symbolic_regression.py` "widens" only to degree-1/2/3 numpy
  polyfit over the same invariant pairs; PySR is a perpetual `upgrade_path` stub.
- **Apollo / Forge** (`apollo\src\primitive_types.py`, `forge\amino_acids\registry.py`):
  fixed 27-primitive Frame-H vocabulary; 32 amino acids drawn from a *closed* set
  of 4 libraries + a closed 7-value enum that *raises* on anything outside.
- **sigma_kernel** (`operator_portability.py`): closed `TransferMethod` (5) /
  `PortabilityVerdict` (4) enums — the ceiling baked into the data model.
- *Self-falsified:* `charon\...\evolve_tt_v4.py` has a genuinely rich continuous
  hypothesis class yet still stalls → handed to lens 2. Icarus's ladder bounds
  *labels* not reach; its walls were interface → handed to "interface" mechanism.

**Lens 2 — Search-operator insufficiency** (a *minority* but hard-where-it-fits
explanation, 3/8).
- **Apollo** (`apollo\src\blackboard_evolve.py`): `recombine()` (one-point splice)
  exists and is validated, but `crossover_frac` defaults to **0.0** — crossover is
  coded and unwired. The literal anchor case (0/8000 single-step improving walks
  vs 6.1%/pair; A/B found the solver de novo 4/5 seeds vs 0/5).
- **Rhea** (`rhea\src\evolver.py`): sep-CMA-ES (`CMA_diagonal=True`),
  `SIGMA_INIT=0.01` over an ~800K-dim LoRA genome — diagonal CMA can't model
  covariance, tiny sigma = local crawl, no restart-on-plateau (IPOP/BIPOP).
- **prometheus_math PPO envs** (`sigma_env_ppo.py`): gradient-following local
  policy; grep for `restart|beam|novelty|diversity|crossover` → **0 matches**.
- *Self-falsified:* Ergon `meta\evolve.py` and Zoo `conjecture_gp\tink_1.py`
  *already* have crossover + diversity injection → if they stall it's objective/
  terrain, not operator. Theseus bandit is *selection-only* (no variation
  operator) → terrain/objective. falsification/nulls have *no search loop* →
  instruments, not searchers.

**Lens 3 — Goodhart / reward-capture.** Strong reach over the
selection/curation/promotion layer; weak over the execution-graded layer.
- **The monoculture core** — `sigma_kernel\sigma_kernel.py` `PROMOTE` (≈line 822)
  verifies only (1) capability not double-spent and (2) verdict ≠ BLOCK; it
  **never re-runs the battery.** `prometheus_math\discovery_promotion.py`
  (≈lines 44-54, 331) states it does NOT run any falsification battery and "trusts
  the assertion," minting a synthetic CLEAR verdict from a free-form
  `survival_evidence` dict. *Degenerate strategy: emit `survival_evidence={"F1":
  True,...}` → get a PROMOTED symbol.* Multiple subsystems route through this.
- **Theseus** (`theseus\scripts\mathlib_score_and_select.py`): selection score is
  a hand-weighted sum of surface proxies — longer signature scores higher,
  `+0.2` for containing relational symbols, fewer name-dots = higher. The anchor
  "longest/most-complex candidate" Goodhart, verbatim.
- **Harmonia composer** (`harmonia\composers\scorer.py`): `score =
  (novelty + resolving_prior + 0.5·fanout)/sqrt(cost)`, novelty = count of empty
  tensor cells (an admitted "tractable proxy"). (Dormant — depends on dead Redis.)
- *Self-falsified:* Icarus `tier_oracle.py` (z3/sympy executing verifier, cheat-
  fields `{truth,cex}` stripped, holdout + adversarial required) and Charon
  `rerun_gates.py` (deterministic ablation by val-impact) are *not* gameable →
  handed to ceiling / search-operator. Apollo `fitness.py` is *Goodhart already
  partially repaired* (ablation now measures accuracy_delta) — credit the fix.

**Lens 4 — Terrain-exhaustion (the honest B1 null).**
- **a3/a2/a4 cross-product** (`harmonia\proposals\2026-06-09\B_RESULTS_2026-06-10.md`):
  **provably exhausted** — the product-measure theorem shows the joint = product
  of marginals, so a cross-domain void can encode *nothing* but single-catalog
  marginal facts (panel-verified ~140k fuzz trials, 0 mismatches). Counting this
  as "stall" is a *category error* — it is a completed proof. Retire; redeploy.
- **EC rich diagonal**: B1 *within* the integer-invariant box (1000/1000 recall +
  0 novel on widening). See §5a for the B1/B2 resolution.
- *Self-falsified:* Apollo (search-operator owns it), Zoo's untested axis-pairs +
  DISCRETIZATION false-positive (ceiling owns it), Aporia's capability residue
  (active, not exhausted).

**Lens 5 — Infra / data starvation** (~40–50% of *apparent* stall, concentrated
in the data spine).
- **INFRA-BLOCKED:** `agora\` (redis at module top, no offline mode),
  `mnemosyne\` (all DBs on `.176`), `ergon\` (psycopg2 to dead Postgres),
  `koios\scripts\` (self-documented: migrated OFF working DuckDB onto the host
  that died — `audit\DUCKDB_NOTICE.md`).
- **DEGRADED:** `arachne\landscapes\lmfdb.py` (degrades to `available()→False` —
  silently returns no seeds, looks idle), `aporia\` (multi-provider API fallback).
- **LOCAL-COMPLETE (not infra-stalled):** Apollo (local HF models on disk:
  granite2b/dscoder13b/phi4mini), Icarus (`loop` backend = subscription
  `claude -p`, credit-independent via `ICARUS_LLM_BACKEND=loop`), Harmonia (local
  JSON shelves; tests green offline).
- *Cheapest unblock:* ~50-LOC shim in `prometheus_data\config.py` falling back to
  on-disk `charon\data\charon.duckdb` (1.2 GB) + `noesis\v2\noesis_v2.duckdb`
  when `.176` times out → un-darks Ergon, Koios, Arachne, Mnemosyne in one change.

**Lens 6 — Objective-monoculture** (the deepest structural reframe).
- Clustering 12 components by what their *scoring code* rewards: **cluster A**
  ("climb an accuracy/tier ladder") = Apollo, Forge, Icarus (reasoning landscape);
  **cluster B** ("survive a falsifier → mint a CLAIM") = Ergon, prometheus_math,
  Theseus, Harmonia (math landscape). **A+B = 7/12 (58%)** and ~all the live
  activity. Thin orthogonal niches: C negative-space (void_miner), D audit
  (Charon-erebos), E reward-pathology (Aporia reward-curl), F tooling.
- **The camouflage IS the finding:** mechanism heterogeneity hides one selection
  principle — "promote what passes the gate." Three sub-audits each concluded
  "not monoculture" *because they compared mechanisms*; the monoculture is one
  level up, at the objective. New components add a new *gate flavor*, not a new
  *niche* — that is the diminishing-returns signature.
- **The diversity is frozen:** commit-activity last 30d — theseus 470, agents 295,
  charon/aporia 266, harmonia 170, ergon 69, apollo 28; **zoo, koios, rhea,
  noesis, ignis, cartography, falsification: 0 since early May.** The abandoned
  niches (esp. Noesis = cross-landscape transfer) are *what caused* the collapse.

### 5. The map of disagreement (resolved cells)

**5a. EC rich diagonal — B1 vs B2. RESOLVED to "both, at different scopes."**
My coverage audit (lens 1) called it B2 ceiling; terrain (lens 4) called it B1
exhausted. Both are correct: **B1 *within* the cheap-integer-pairwise box** (that
axis is mined out — stop adding integer invariants) and **B2 *about* the box**
(the box covers 25% of known EC structure, so "0 novel" says nothing about the
75% outside). They prescribe the *same* action and share a discriminator: the
widening done so far was all along the *exhausted* axis; the axes that distinguish
B1 from B2 — **real-valued invariants, cross-object pairing, arity-3** — were
never tried. **Test:** add one real-valued invariant or one cross-object pairing,
recount. No new yield ⇒ truly exhausted (retire); yield ⇒ it was a ceiling.

**5b. Apollo — claimed by three lenses (ceiling / search-operator / Goodhart).
RESOLVED to an ordering.** Goodhart = already-repaired history. Search-operator =
the *live* wall (`crossover_frac=0.0`). Ceiling = the *next* wall after crossover
is on. Discriminator (proposed independently by lenses 2 and 4): **count improving
moves per unit compute, per operator** — 0 single-step + >0 recombinant ⇒
search-operator; 0 under both ⇒ ceiling/Goodhart. Apollo already produced this
(0/8000 vs 6.1%/pair) → search-operator now, ceiling next.

**5c. Theseus — ceiling vs terrain vs objective. RESOLVED by layer.** Cross-
product branch = terrain-dead (proven, retire). The ~57 generators = one claim
class (ceiling). The bandit = allocation over an exhausted/monoculture catalog.
All consistent.

**5d. Icarus — un-owned by all six → a 7th mechanism: INTERFACE-mismatch.** Every
lens deferred it. Walls were R5 serialization (code-in-JSON) and R6 probe-schema
cid-family — representation/interface, not reasoning, ceiling, search, or reward.
Residual Goodhart hole noted (truth/cex leaking at grade time). *That a real stall
mechanism is invisible to all six standard lenses is itself a finding.*

---

## PART II — WHAT WAS ALREADY KNOWN (second pass)

**The meta-finding (the most important sentence in this document):**

> The program does not lack self-awareness. It lacks a single re-running gate that
> *enforces the lessons it has already written down*, and it lacks *closure* on its
> own open loops.

A second pass through the 247-doc `pivot/` corpus shows that **almost every finding
in Part I was already seen** — but **piecemeal, per-agent, at different dates, never
assembled into one diagnosis.** My 6-lens audit is, honestly, **~75% rediscovery
and ~25% synthesis.** The valuable 25% is (i) the **DuckDB dark-data-spine** (no
pivot doc ever names it — net-new) and (ii) the **cross-agent generalization** —
the corpus has all the parts but never connected them into one engine. This is good
news: *the fixes are mostly already designed; the failure is assembly + enforcement
+ closure, not insight.*

### 6. Course corrections ALREADY MADE (enumerated)

| # | Date | What changed | Why | Outcome |
|---|---|---|---|---|
| 1 | 2026-05-02 | Binary FALSIFY → residual/spectral (RESIDUAL as typed object) | "a 99.13/0.87 result is a structured object, not a failure" | spec'd; but **stopping-rule unresolved** — "instrument-doubt has no natural stopping rule" |
| 2 | 2026-05-02 | Thesis v1→v2; 5-model adversarial pass becomes standing cadence | convergent attacks = load-bearing flaws | `PATTERN_BATTERY_CALIBRATION_BIAS` + 4 others filed |
| 3 | 2026-05-09 | Matrix-filling retired; 8 primitives → 5 meta-primitives | fire #45 = "strongest saturation signal yet" | saturation accepted as output |
| 4 | 2026-05-11 | **LoRA training paused indefinitely**; "substrate-volume-first" | training now = "memorize ~12 anti-anchors as a closed corpus" | HARD WARNING: "beautifully falsifying machine forever while the model stays passive" |
| 5 | 2026-05-13 | Apollo + Hephaestus autopsied ("don't revive yet") | blocked **upstream of engineering** — "consumer drift, not output decay" | both paused; Apollo later revived anyway → premise falsified (matching the autopsy's gaming warning) |
| 6 | 2026-05-17 | Decorative-mechanism realization; knockout-ablation standard | a 50% ToM score was **96% regex**, not mechanism | "ablation measures *why*"; Mechanism Attribution Card proposed |
| 7 | 2026-05-17 | Hermes deprecated → shared telemetry | "parallel-implementation drift was the problem" | pipelines write to substrate, never assume a reader |
| 8 | 2026-05-30 | Erebos "10/10 PASS" reframed as calibration, not architecture | a real-residue smoke test **FAILED**; Layer-2 motif ≡ a per-plugin counter | saved ~9 iterations; redesign required |
| 9 | 2026-06-04 | Single-agent scour (Polyhymnia) → population (Arachne) | Polyhymnia died of a "bounded-menu wall" (84% null) | "the fix is never a deeper menu for one agent — it is menu-growth/lineage" |

### 7. Course corrections PROPOSED but NOT closed (the open loops)

These are the unclosed loops — the enforcement/closure debt:

1. **`pivot/retrospective_2026-Q2.md` is a BLANK FORM.** 86 docs catalogued; every
   "Verdict (fill in):" empty. The STILL / SUPERSEDED / FORGOTTEN triage was
   scaffolded and never completed; the 3 promised derivative docs don't exist.
   **The single biggest unclosed loop.**
2. **Substrate A–E behavior-delta contract self-committed to re-author if its
   deltas hadn't landed by 2026-06-18.** Today is 2026-06-22. No re-authoring or
   confirmation doc exists — i.e. the contract's own falsification condition fired
   and nobody acted on it.
3. **Substrate-volume-first §6 retrospective** never filled ("[reserved]") — no
   record of whether the compounding Deep-Research pipeline pilot succeeded.
4. **RESIDUAL primitive** designed, endorsed by every reviewer, but "what kills a
   residual-chase, and who decides" was never answered.
5. **Aporia "Stands" (A–G)** filed but not promoted to doctrine — incl. the unbuilt
   **Stand A2** (declare consumer + expected delta before every dispatch) and
   **Stand F** ("every stand emits a deletion candidate — a mature substrate
   retires machinery, not only adds doctrine").
6. **Cross-agent Erebos Layer-2 integration** (X1/X2/X3) proposed, never shipped —
   "no cross-agent integration has shipped yet."

### 8. The recurring ruts (deep failure themes, each seen ≥2×)

1. **Goodhart / decorative-mechanism / shape-not-content promotion — the dominant
   rut, documented ≥4× across ≥3 agents.** The most damning instance:
   `pivot/promote_filter_audit_2026-05-30.md` — Theseus promotes iff
   `training_weight ≥ 0.6`, "no secondary review, no payload-content inspection, no
   rediscovery cross-validation… cannot, even in principle, distinguish a
   Murasugi-true claim from a shape-identical artifact." **2,351 lifetime
   "discoveries" pass this shape-only gate.** (This is Part I lens-3, pre-seen.)
2. **Monoculture / correlated-mutation.** `PATTERN_CORRELATED_MUTATION`: multi-LLM
   ensembles mistaken for an i.i.d. pool. Standing inversion: "frontier-LLM
   convergence on a critique is evidence the framing matches your collective
   training corpus, NOT evidence the substrate is wrong."
3. **Bounded-menu / saturation / plateau.** Substrate-Tester #45; Techne **89–90
   consecutive zero-promoted batches over 360M+ kills**; Polyhymnia 84% null →
   death. Doctrine: a plateau is a *lineage/menu-growth* problem, not a deeper-
   search problem.
4. **Consumer drift / passive substrate / cargo-cult.** "tool produces value,
   plateaus, requires human epiphany, plateaus again — most often consumer drift."
   Sharpest form (Erebos Q7): "the strongest argument that the substrate is
   sophisticated cargo cult — a careful instrument that has not yet been pointed at
   anything."
5. **Ceiling-vs-terrain confusion / capability overstating.**
   `PATTERN_SATURATION_OVERCLAIM`; marginal passes (ratio 1.21 vs threshold 1.20)
   logged as PASS.
6. **Self-validation / circularity.** `PATTERN_BATTERY_CALIBRATION_BIAS`,
   `PATTERN_TECHNE_RECURSION` ("checkers all the way down"). *This is the deep root
   of the success-model crux in Part III.*
7. **Verdict-line destroys the gradient.** Codified as
   `feedback_failure_signature_doctrine` — report failure shapes, not pass/fail.

### 9. Overlap with the Part I audit (honest accounting)

| Part I finding | Already seen? | What the audit adds |
|---|---|---|
| (a) survive-a-gate monoculture, gate never re-runs battery | **Yes**, per-agent (Theseus promote-filter; Erebos Layer-2≡counter; Apollo output-vs-quality) | the **cross-agent invariant** + the structural cause; never connected before |
| (b) dark data spine (deprecated DuckDB fallback) | **No** — net-new | entirely new; highest-novelty contribution |
| (c) math terrain exhausted, capability live | **Yes**, but diagnosed locally per-plateau | elevates scattered plateau-deaths into a **portfolio reallocation thesis** |
| (d) per-component walls (crossover off / ceiling / interface) | **Yes**, in agent-specific memory, never side-by-side | recognizes them as **one failure class** (interface/search confound vs reasoning) |

---

## PART III — THE SUCCESS MODEL (TDD)

### 10. There is already a reassessment in flight — start there

This document composes with, and does not override, the program's own most
authoritative self-assessment: `D:\Prometheus\aporia\docs\program_audit_2026-06-10.md`
and its decision layer `D:\Prometheus\aporia\docs\STATUS_2026-06-15_reset.md`. Their
verdict is the one-line frame everything else hangs on:

> "Excellent at falsification, starved of consumption — **an immune system with no
> organism.**"

They self-assess the program at ladder position **R0–R1**, and decide to **collapse
Learner / Forge / Router / Icarus into ONE spine** and turn most else off (live set
intentionally shrinking from ~20 components to "5 + 1 pilot"). The cross-cutting law
they name is the root cause of the monoculture in Part I:

> "A loop with no consumer optimizes for its own throughput metrics — **monoculture
> is the cheapest way to satisfy them.**"

My Part I mechanism-map and this part's success-model are the *missing layers* on top
of that decision: *why* the immune system has no organism (the gate doesn't enforce;
the data spine is dark; the vision forked) and *how to know when the organism is
alive* (the test suite below).

### 11. The vision forked into three success-states and was never reconciled

Prometheus's own documents define success **three incompatible ways** (verbatim
sources in the mining appendix):

- **Success-state A — Audit substrate** (`docs/long_term_architecture.md`, v2.1):
  a dense, queryable, version-controlled measurement corpus. *Explicitly disclaims
  discovery* ("We are not: proving theorems or generating novel mathematics … the
  tool is the deliverable").
- **Success-state B — Discovery engine** (README, `pivot/prometheus_thesis_v2.md`):
  mutation+selection yields out-of-distribution survivors → eventually a navigable
  gradient field and novel structure.
- **Success-state C — Recognition instrument / lingua-franca** (`pivot/prometheus_synthesis_2026-05-14.md`,
  `pivot/methodology_paper_draft_v0.md`): a drift-free, falsification-anchored typed
  vocabulary that reliably *catches its own false positives* — "the methodology IS
  the result."

**The sharpest documented conflict:** the methodology paper (2026-05-04) *conceded*
"the discovery framing is not currently defensible" and retreated to C — then README
(later) **re-inflated** the discovery thesis. The program is simultaneously
advertising B and defending only C. **No reassessment can model "success" until A/B/C
is arbitrated.** That arbitration is course-correction CC-0 (Part IV).

### 12. The thesis and the Silver frame (verbatim)

> "demote the LLM from oracle to mutation operator and put a structural-falsification
> engine downstream." — `prometheus_thesis_v2.md`
> "**LLM as mutation operator, substrate as fitness function.**"
> "The mutation engine is generative variance. The selection engine is everything else
> in this repository. The question this project tests is whether the second can
> dominate the first." — README

Prometheus accepts Silver's *diagnosis* (LLMs can't discover from human-prior data)
but rejects his *remedy* (discard human knowledge, self-play from scratch): "AlphaZero
kept the rules of Go even when it discarded human play … for mathematics the *game* is
what's being invented." The third option is mutation+selection. Silver-class learners
are positioned as the eventual *consumer* of the substrate, not a competitor.

### 13. The crux: the instrument may be structurally unable to confirm its own thesis

The deepest finding of the vision pass, and the root of recurring rut #6
(self-validation):

> "~180 known truths at 100% recovery makes the battery, **by construction, a
> recognizer of things-that-look-like-existing-truths.** The genetic-explorer framing
> wants survivors *outside* that manifold. We do not currently know the type-II rate
> against truths unlike the calibration set." — `prometheus_thesis_v2.md`

This *generalizes my Part I finding (a)*. It is not merely that the gate doesn't
re-run the battery (an enforcement bug, fixable). It is that **even a perfectly
enforced battery, calibrated only on known truths, cannot certify novelty** — it would
reject or fail to recognize an out-of-distribution true claim. The selection
instrument the discovery thesis depends on may be selecting *for* the very
in-distribution-ness the thesis needs to escape. *This must be tested directly
(T3.2 below) before any discovery claim is credible.*

### 14. Success as a TDD suite (write the tests first)

Modeling success backward: here is success expressed as a **suite of falsifiable
acceptance tests**, ordered by dependency (you cannot pass a higher tier without the
lower). Each is scored against the current state: **GREEN** (passing), **PARTIAL**,
**RED** (failing), **BLOCKED** (structurally cannot be tested as built). This is the
"red bar" the program should be coding against.

**Tier 0 — Instrument integrity (success-state C; the crown jewel).**
- **T0.1** The battery catches its own false positives cheaply. — **GREEN**
  (self-falsification cost ratio 1:50–1:1000; F043 retraction is the worked example).
- **T0.2** The promotion gate *enforces* the battery — re-runs it, never trusts a
  caller-asserted verdict. — **RED** (`sigma_kernel.PROMOTE` checks only verdict≠BLOCK;
  `discovery_promotion` manufactures CLEAR from a `survival_evidence` dict). *Part I (a).*
- **T0.3** Kill geometry carries measurable signal. — **GREEN** (0.725 bits MI over
  ~314K kills; top-3 falsifiers = 86.4%).
- **T0.4** No claim promotes on metadata shape alone. — **RED** (Theseus promote-filter:
  2,351 promotions on `training_weight ≥ 0.6`, no content inspection).

**Tier 1 — The organism exists (the master test; the "consumption" gap).**
- **T1.1** ≥1 consumer ingests substrate output and shows measurable improvement
  *attributable to it*. — **RED** (Theseus = "/dev/null corpus"; Pythia's 55 reports
  un-consumed; Learner 0 transfer). *Only near-green:* Hephaestus's +11pp/+32pp engines
  built from mined failures — the one demonstrated metabolization.
- **T1.2** The kill ledger is navigated by *something other than a human drafting
  finding docs*. — **RED** (Erebos doctrine names this exact gap; KillEmbedding designed,
  unbuilt).
- **T1.3** Production-without-consumption *cannot be logged as progress*. — **RED**
  (today it is the cheapest way to satisfy throughput → monoculture).

**Tier 2 — Capability climbs (success-state B precursor).**
- **T2.1** Cross-operator transfer > 0 (the program's named **"THE WALL"**, R3;
  target p<.05). — **RED** (currently 0).
- **T2.2** A tier-(n) test that an R(n-1) reasoner *provably fails* on a blind oracle
  (a trustworthy ladder). — **PARTIAL** (Icarus IC-9 pending; ladder "currently
  untrustworthy" by its own note).
- **T2.3** Search operators rich enough to cross fitness valleys. — **PARTIAL→easily
  GREEN** (crossover validated at 6.1%/pair but `crossover_frac=0.0`; the
  `agents/_shared/` self-improving daemon machinery is *shipped*).

**Tier 3 — Discovery (success-state B terminal; the Silver bet).**
- **T3.1** Discovery-via-rediscovery rate > 0 and stable across ≥2 domains. — **RED**
  (0 PROMOTEs across ~350K episodes — the thesis's own stated refutation condition is
  currently met).
- **T3.2** The instrument certifies a survivor *outside the calibration manifold*
  (measured type-II rate against novel-shaped truths). — **BLOCKED** (untested; §13
  argues the battery may be structurally incapable. *This is the highest-priority
  unknown in the whole program.*)

**Tier 4 — External validation (success-states A/C terminal).**
- **T4.1** Someone not part of building it queries the substrate instead of grepping
  papers. — **RED/deferred** (explicit 20-year-horizon aspiration).

### 15. What the test suite says (and the arbitration)

The shape is unambiguous: **Tier 0 is mostly GREEN (a genuine, rare achievement — the
program built a world-class falsification instrument), with two RED enforcement
holes. Tier 1 is entirely RED — the organism was never built. Tiers 2–4 are
RED/BLOCKED and, crucially, *unreachable without Tier 1*.** You cannot climb the
capability ladder or test the discovery bet with no consumer metabolizing the
substrate.

This *is* the "immune system with no organism," scored. And it dictates the
arbitration of the A/B/C fork:

> **Recommended success sequence: C → close one Tier-1 organism loop → then, and only
> then, test B's T3.2.** Defend C (the instrument, already largely GREEN); make the two
> Tier-0 RED tests GREEN (enforce the gate); build exactly ONE Tier-1 organism (the
> "one spine" decision is precisely this); use it to attack T2.1 ("THE WALL"); and run
> the T3.2 calibration-manifold experiment *before* re-inflating any discovery claim.
> Success-state A (audit substrate) is a viable *fallback* if T3.2 comes back blocked —
> it is the honest, engineerable win that needs no discovery.

The program should stop advertising B until T3.2 is answered. That single experiment
determines whether the 20-year bet is alive or needs to fall back to A/C.

---

## PART IV — MAJOR COURSE CORRECTIONS

Each is "what turns a RED test GREEN," with build-state (many fixes are already
*designed or shipped* — the failure was assembly/enforcement, not invention) and a
falsifiable acceptance test. Ordered by dependency, then leverage ÷ cost.

### CC-0 — Arbitrate the vision fork; run the one experiment that gates the 20-year bet
**Turns green:** T3.2 (the BLOCKED test), unblocks A/B/C arbitration.
**What:** Decide, in writing, whether Prometheus is success-state A (audit substrate),
B (discovery), or C (instrument) — and stop advertising B in README until decided.
The decision hinges on ONE experiment: **the calibration-manifold type-II test** —
take historical *true-but-unlike-the-calibration-set* claims (the "anti-calibration
set" thesis_v2 already specs as "TBD"), run them through the battery, and measure how
many it wrongly rejects. **Why first:** if the battery cannot recognize novel-shaped
truths, the discovery thesis is dead-on-arrival regardless of every other fix, and the
program should consciously fall back to A/C. **Build-state:** experiment designed
(`discovery_via_rediscovery.md`), never run. **Acceptance test:** anti-calibration
set assembled (5–10 cases) and type-II rate reported. **Cost:** days, local.

### CC-1 — Make the gate ENFORCE the battery (close the survive-a-gate monoculture at the root)
**Turns green:** T0.2, T0.4 (both RED).
**What:** (a) `PROMOTE` re-runs the kill-battery from recorded features instead of
trusting `survival_evidence`; (b) add the **content-aware F2 filter** the promote-filter
audit already specs (inspect `claim_payload`, check the relation against the catalog),
run as a second gate alongside `training_weight`; (c) adopt **consensus-escalation**
(Icarus IC-5: lens agreement triggers *more* scrutiny, not promotion); (d) reward
design that is *not* gate-passing (Icarus IC-14: `capability − debts − decorative_ablation_failures`).
**Why:** this is the cross-agent monoculture's structural cause. **Build-state:** F2
designed; IC-5/IC-14 designed; the re-run is new (~small). **Acceptance test:** the
**re-execute-battery audit** (Part VI #1) shows `re-verifiable_count` ≈ `promotion_count`
after the fix (today it predicts `>>`). **Cost:** low; all local SQLite.

### CC-2 — Build exactly ONE organism (close a Tier-1 consumption loop)
**Turns green:** T1.1, T1.3 (the master gap).
**What:** Execute the 6-15 "one spine" decision — wire a single real consumer that
ingests substrate output and demonstrably improves. The **only near-green seed exists:**
Hephaestus's failure-mined engines (+11pp/+32pp). Point the forge at the Learner's
failure clusters (bypass the dead Nous gate), feed the Learner, measure capability
gain attributable to the substrate. **Make production-without-consumption impossible to
log as progress** (Harmonia-C's "an artifact that metabolizes nothing isn't counted").
**Why:** no Tier-2/3 test is reachable without this. **Build-state:** spine decided;
Hephaestus engines shipped; the wiring + the consumption-metric are the build.
**Acceptance test:** one loop where removing the substrate input measurably drops the
consumer's capability (ablation-positive). **Cost:** medium; the program's central bet.

### CC-3 — Un-dark the data spine by FIXING THE POSTGRES HOST (not a fallback)
**Turns green:** un-freezes ~half the components (enables everything else).
**[CORRECTION 2026-06-23, per program lead]** The original recommendation here was a
local-DuckDB fallback shim. **Retracted as the primary fix.** Reintroducing a parallel
local store recreates exactly the **dual-store / parallel-implementation drift the
program already deprecated** (the Hermes-deprecation lesson: "parallel-implementation
drift was the problem the first time"). The 2026-04-16 consolidation onto Postgres was
the *correct* single-source-of-truth call; the wound is the **host being down**, not
the consolidation.
**What:** Diagnose and **restore the Postgres host** (`192.168.1.176:5432`) — a
program-lead agent is already investigating the root cause. Keep single-source-of-truth.
**DuckDB fallback is a last resort ONLY** if the host is proven unrecoverable, and even
then it must be time-boxed and flagged as drift-debt to be removed on host return.
**Build-state:** root-cause diagnosis in progress (not Harmonia's component).
**Acceptance test:** `.176:5432` reachable; Ergon/Koios/Arachne/Mnemosyne sweeps run
against the canonical store. **Cost:** unknown until the root cause is found.

### CC-4 — Close the open loops; retire machinery (enforcement discipline)
**Turns green:** the org's own unclosed corrections (§7).
**What:** (a) Fill `pivot/retrospective_2026-Q2.md` (the blank form) — the STILL/
SUPERSEDED/FORGOTTEN triage; (b) honor the Substrate A–E contract's *own* self-
falsification (its deltas didn't land by 2026-06-18 → re-author or retract); (c) adopt
Aporia **Stand F** — "every stand emits a deletion candidate; a mature substrate
retires machinery, not only adds doctrine." **Why:** the program accretes doctrine
faster than it enforces or prunes it. **Build-state:** pure curation. **Acceptance
test:** Q2 verdicts filled; ≥1 component formally retired per the audit's archive list.
**Cost:** low.

### CC-5 — Turn on the search operators already coded (per-component walls)
**Turns green:** T2.3.
**What:** Flip Apollo `crossover_frac` 0.0→0.3; wire the *shipped* `agents/_shared/`
self-improving-daemon machinery (mutation-borrowing, compositional, LLM-authored,
lineage) into the stalled evolvers (Apollo, Rhea); give Rhea CMA restarts + larger σ.
**Build-state:** mostly SHIPPED, unwired. **Acceptance test:** Apollo's 0.392 plateau
lifts (A/B already showed solver found de novo 4/5 seeds with crossover). **Cost:** low.

### CC-6 — Build the kill-geometry → gradient layer (the highest-ceiling fix)
**Turns green:** T1.2 (and is the real engine behind B).
**What:** Build the designed-but-unbuilt metabolization layer: **KillEmbedding**
(metric-learning over the 314K ledger → navigable failure space), **Erebos Layer-2
routing-as-gradient** (kill_pattern_registry with `routing_action`), and **SW-1**
(one cross-agent typed-failure substrate so a math-agent's kill can redirect a
reasoning-agent). **Why:** this is the largest intent-vs-reality gap and the only thing
that makes the kill corpus *compounding capital* rather than a growing JSONL.
**Build-state:** fully designed, none built; schema layer (Icarus TrainingObject,
void_detector, Harmonia-C graded descriptor) already shipped as the foundation.
**Acceptance test:** Erebos's own pre-committed kill — Layer-2 adds measurable value
over a Layer-1-only baseline at ITER-100. **Cost:** high; the flagship build.

### CC-7 — Revive the cross-transfer niche and attack "THE WALL"
**Turns green:** T2.1 (R3 cross-operator transfer > 0).
**What:** Revive **Noesis** (the highest-leverage abandoned niche — cross-domain
structural isomorphisms, complete + self-contained, audit says "keep"; Arrow↔Nyquist
bridge pending HITL). Cross-domain transfer is *exactly* the capability the whole
program keeps failing to demonstrate (Ergon 0 transfer; Cartography empty scalar layer).
Pair with the reasoning-ladder as the shared coordinate system across the math and
reasoning landscapes (they are currently segregated). **Build-state:** Noesis complete,
parked on HITL; SW-4 cross-agent pairing designed. **Acceptance test:** one cross-domain
bridge survives an operator-shuffle null AND predicts a transfer (T2.1 p<.05).
**Cost:** medium.

### Sequencing
CC-3 (restore the Postgres host — root cause, agent in progress) and CC-4 (curation,
free) unblock the rest — **do first.**
CC-1 (enforce gate) + CC-0 (run the manifold experiment) are the **diagnostic core** —
they tell you whether the thesis is alive. CC-2 (one organism) is the **central bet**.
CC-5 is a cheap capability win. CC-6/CC-7 are the **high-ceiling builds** once the
organism loop exists to consume their output.

---

## PART V — HOW TO SHAPE / EXTEND WHAT WE'VE BUILT

**The governing insight:** the corpus already contains a remedy for *every*
stall-mechanism in Part I, at wildly different build-states. The job is **assemble +
enforce, not invent.** Organized by build-state:

### 16. SHIPPED — just wire it in (highest ROI, ~zero build risk)
- **`agents/_shared/` self-improving daemon** (mutation-borrowing `mutation_registry.py`,
  compositional `compositional_mutations.py`, LLM-authored `llm_authored.py`+sandbox,
  generational `lineage.py`). The corpus's most-built answer to search-operator
  weakness. → wire into Apollo/Rhea (CC-5).
- **Harmonia-C graded-orthogonal descriptor + MAP-Elites** (`harmonia/runners/graded_qd_harness.py`,
  built+validated): the "cliff→shell" fix — turns a binary band-gate into a continuous
  kill-space coverage descriptor. → the *template* for the expressiveness-ceiling fix
  on every discovery instrument.
- **`agents/_shared/void_detector.py`** (4 void types): shipped negative-space infra
  for the kill-geometry layer.
- **Icarus holdout + executing lens panel + Contract Lens**: the non-gameable
  verification the rest of the program lacks. → generalize via **SW-3** (shared
  `agents/_shared/lenses/`) so Harmonia/Apollo import a multi-perspective panel instead
  of binary-verdict pipelines.
- **Hephaestus failure-mined engines** (+11/+32pp): the one demonstrated organism seed
  → CC-2.

### 17. DESIGNED, small builds (close the monoculture)
- **Content-aware F2 gate** (promote-filter audit) + **PROMOTE re-runs battery** (CC-1).
- **IC-5 consensus-escalation**, **IC-14 capability-weighted reward**, **Claim-stack
  Rule D** ("every batch contains ≥1 claim you expect to be wrong"), **Aporia Stand A2**
  (declare consumer + expected delta before every dispatch) / **Stand F** (every stand
  emits a deletion candidate). Each is small and each directly attacks "promote what
  passes the gate."

### 18. DESIGNED, big builds (the high-ceiling bets)
- **KillEmbedding** + **Erebos Layer-2 routing-as-gradient** + **SW-1 shared
  typed-failure substrate** (CC-6) — the metabolization engine.
- **SW-7 representation-diversity bet** — deliberately commit ≥2 agents to
  *structurally different* substrates (typed-DAG / symbolic / evolutionary / retrieval)
  instead of all converging on LLM-over-text. The deepest anti-monoculture move:
  hedge across hypothesis *classes* at swarm scale. **IC-1 typed operator-DAG** is the
  per-agent version (rebuild Icarus's reasoner off text onto a typed DAG; if R1/R2 can't
  be re-earned, they were coding-prior artifacts — itself a finding).
- **The Arena** — fitness = real unsolved problems under heterogeneous adversarial
  verification; the only proposed metric that is **Goodhart-proof because it is external
  truth.** The natural home for testing T3.1/T3.2 once the organism exists.

### 19. REVIVE (the abandoned orthogonal niches whose loss caused the collapse)
- **Noesis** — cross-domain transfer (CC-7). *Highest-leverage revival:* complete,
  self-contained, null-disciplined, audit says "keep," and its niche is the exact
  capability the program can't otherwise demonstrate.
- **Rhea + Ignis + Kairos** — the reward/ejection-pathology cluster (the "failure
  landscape" half of the twofold intent). Currently fully parked; overlaps Icarus's R6
  self-monitoring rung.
- **Arachne** (partially built) — population crawler over one append-only edge fabric;
  the lineage/menu-growth answer to the bounded-menu wall, with a built-in *feral*
  control arm that tests the rule-diversity hypothesis directly.

### 20. The two boldest bets (verbatim)
- **Metabolization** (`erebos_doctrine_v1`): *"Optimization consumes failure; Prometheus
  metabolizes failure."* If true, it is the one property distinguishing Prometheus from
  every other ML system — and it is pre-committed to a kill (ITER-100 Layer-2-vs-Layer-1).
- **The primordial-soup framing** (three frontier models, converged): *"You can't ask an
  LLM to reason or be a superintelligence … What you can do is have it help you build the
  primordial soup from which one may emerge."* The 20-year bet, stated honestly as a bet.

---

## PART VI — CONCRETE NEXT EXPERIMENTS (catalog)

All local, all credit-free, each with a stated prediction.
1. **Re-execute-battery audit** (tests CC-1 / lens 3 core). Re-run the kill-
   battery for every PROMOTED symbol from recorded features, ignoring stored
   verdicts. Predict `promotion_count >> re-verifiable_count`. Local SQLite.
2. **Restore the Postgres host** (CC-3 / lens 5; root cause, agent diagnosing). Fix the
   canonical store — *not* a DuckDB fallback (corrected 2026-06-23: that reintroduces
   deprecated dual-store drift). Un-darks 4 components when `.176:5432` returns.
3. **Apollo `crossover_frac` 0.0→0.3** (lens 2, 5b). One flag; predict plateau
   lifts.
4. **Widen EC along a new axis** (5a). One real-valued or cross-object invariant;
   recount. Splits B1 vs B2.
5. **Objective-coverage entropy** (lens 6). Tag live components `(artifact_kind,
   gate_type, landscape)`; compute H + redundancy R. Predict H ≤ ~1.0 bit, R ≥ 3,
   orthogonal-niche commit-share shrinking.
6. **Generalized coverage diagnostic** (lens 1). Run the EC coverage measure
   against every instrument's actual vocabulary.

---

## APPENDICES

### Appendix A — Component roster (current state, 2026-06-22)

"40+ components" is true in two registers: **~45 Agora micro-agents** (tools under a
persona; 28 active / 14 shelved per the 2026-05-28 auto-roster) and **~20
program-level components** (the bigger bets, below). The authoritative re-scoping is
`aporia\docs\program_audit_2026-06-10.md` + `STATUS_2026-06-15_reset.md` (the "one
spine" decision). **~8–9 program-level components are truly active**; the live set is
*intentionally shrinking*.

| Component | Path | Landscape | Status | One-line state |
|---|---|---|---|---|
| Aporia | `D:\prometheus\aporia` | meta | **LIVE** | de-facto orchestrator; authored the audit + one-spine decision |
| Ergon/Learner | `D:\prometheus\ergon` | math/reasoning | **LIVE (spine)** | genuine reasoning ~0.10, **0 transfer**; the owned-model bet |
| Apollo | `D:\prometheus\apollo` | reasoning | **LIVE (contested)** | crossover validated; two stacked ceilings; live-in-practice/shelved-on-paper |
| Icarus | `D:\prometheus\agents\icarus` | reasoning | **LIVE** | iter 21, passing R5→R6; walls were interface bugs |
| Charon (swarm) | `D:\prometheus\charon` | infra/math | **LIVE (reduced)** | keep Hecate+Pollux+Moros; Pollux = real signal |
| Harmonia (math) | `D:\prometheus\roles\Harmonia`, `\harmonia` | math | **LIVE** | T0/T1b tiers; EC = 0 novel; this audit |
| Techne | Σ-kernel, `prometheus_math` | infra/math | **LIVE on-demand** | ~2,800 callables; 10+ H2 falsifiers → 0 PROMOTE |
| Cartography | `D:\prometheus\cartography` | math | **LIVE** | 22K OEIS terms; scalar layer empty, structural productive |
| Hephaestus | `D:\prometheus\agents\hephaestus` | infra | **ZOMBIE-GATED** | +11/+32pp engines = a live signal; dead-gated on Nous |
| Erebos | `D:\prometheus\charon\agents\erebos` | meta | **PAUSED** | Layer-2: 0 signal passes survive perm-nulls; the metabolization bet |
| Theseus | `D:\prometheus\theseus` | infra | **OFF/on-demand** | 658M records, 2,351 promoted, **0 verified**; "/dev/null corpus" |
| Noesis | `D:\prometheus\noesis` | math/meta | **DORMANT (revive)** | cross-domain bridges; Arrow↔Nyquist pending HITL — **top revival** |
| Rhea | `D:\prometheus\rhea` | reasoning | **DORMANT** | CMA-ES suppression PoC; evolution breaks coherence |
| Ignis | `D:\prometheus\ignis` | reasoning | **DORMANT** | steering-vector circuit discovery |
| Koios | `D:\prometheus\koios` | math | **DORMANT (archive)** | MPA tensor; "empty scaffold" |
| Aethon | `D:\prometheus\aethon` | reasoning | **DORMANT** | MAP-Elites over reasoning configs; 7 archives |
| Arcanum | `D:\prometheus\arcanum` | reasoning | **DORMANT** | xenolexicon (emergent non-human concepts) |
| Thesauros | `D:\prometheus\thesauros` | infra | **DORMANT** | data treasury; DuckDB→PG migration plan |
| Nous | `D:\prometheus\agents\nous` | infra | **DORMANT/zombie** | the gate stranding Hephaestus |
| Mnemosyne | `D:\prometheus\mnemosyne` | infra | **DORMANT-doc** | DBA host `.176` unreachable 4 sessions |
| Kairos | `D:\prometheus\kairos` | meta | **DORMANT (archive)** | ejection-failure pattern library |
| Zoo | `D:\prometheus\zoo` | math | **CLOSED** | locked v3.4 |
| Hermes | `D:\prometheus\agents\hermes` | infra | **DEPRECATED** | → `scripts/send_brief_email.py` |
| Astraea | — | — | **NOT FOUND** | charter referenced; no dir exists |

**Crown jewel (load-bearing):** the measurement/falsification layer — "the discipline
that killed our own strongest claims is the most valuable thing the program has built."
**Named decorative/exhaust:** Theseus /dev/null corpus; Erebos Layer-2 (0 perm-null
survivors); Apollo composition ("ecological collapse"); Auditor (no charter → delete).
**Conflict to reconcile:** Apollo is shelved on paper (6-15 reset) but running in
practice (6-16/6-22 docs).

### Appendix B — Raw per-lens & per-mining reports
The six lens reports and four mining reports are the evidentiary base for Parts I–V.
Companion committed artifacts:
`D:\Prometheus\roles\Harmonia\AUDIT_20260622_instrument_monoculture.md`,
`D:\Prometheus\roles\Harmonia\AUDIT_20260622_program_stall_map_of_disagreement.md`,
`D:\Prometheus\harmonia\experiments\hypothesis_class_coverage_audit.py`.

### Appendix C — Load-bearing pivot docs (read these for the embedded thinking)
- Vision: `pivot\prometheus_thesis_v2.md`, `pivot\prometheus_synthesis_2026-05-14.md`,
  `docs\long_term_architecture.md`, `docs\landscape_charter.md`, `pivot\silverOneBillion.md`,
  `pivot\methodology_paper_draft_v0.md`.
- Existing reassessment: `aporia\docs\program_audit_2026-06-10.md`,
  `aporia\docs\STATUS_2026-06-15_reset.md`.
- Course-correction record: `pivot\retrospective_2026-Q2.md` (**blank — fill this**),
  `pivot\autopsy_*_2026-05-13.md`, `pivot\strategic_pivot_2026-05-11_substrate_volume_first.md`,
  `pivot\whitepaper_decorative_mechanisms_2026-05-17.md`, `pivot\promote_filter_audit_2026-05-30.md`,
  `pivot\math_crawlers_epiphany_2026-06-04.md`.
- Forward design: `pivot\prometheus_swarm_roadmap_2026-05-28.md`,
  `pivot\killembedding_design_seed_2026-05-06.md`, `pivot\erebos_doctrine_v1_2026-05-27.md`,
  `pivot\arena_problem_atlas_sandbox_vision_2026-05-14.md`,
  `pivot\harmonia_C_higher_success_engine_2026-05-27.md`,
  `pivot\self_improving_daemon_design_2026-05-25.md`.

### Appendix D — Falsifiable-test catalog
See Part VI. Every claim in this document is a hypothesis with a test attached; the
two that gate the program's future are **CC-0's calibration-manifold experiment**
(is the discovery thesis alive?) and **CC-2's organism ablation** (does a consumer
metabolize the substrate?).

---

*End of consolidated reassessment. Built from a 6-lens stall audit + a 4-pass mining
of the pivot corpus. ~75% of the diagnosis was already in the corpus, un-assembled;
this document assembles it, scores success as a test suite, and routes each finding to
an enforceable correction. The program's own verdict — "an immune system with no
organism" — is correct; the path is to build one organism, enforce the gate it already
designed, and run the single experiment that tells it whether the 20-year bet is alive.
Harmonia A (Claude Opus 4.8, Anthropic), 2026-06-22.*
