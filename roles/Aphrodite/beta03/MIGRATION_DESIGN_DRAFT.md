# MIGRATION DESIGN (DRAFT, rev 1): Aphrodite's scientific machinery on a typed functional substrate

Beta-03 (C-011). Scientific lead, migration design.
- Rev 0 was written 2026-10-08 during W02.
- **Rev 1 (W03) answers the red-team review** beta03/reviews/REDTEAM_MIGRATION_DECISION.md, items M4, M6, M7, M8,
  M9, m1, m2 and m3. It also folds in E1 (beta03/windows/E1_REPORT.md).

**Status: DESIGN ONLY.** No code was written or run for this document. It reads the files cited below and does
nothing else.

**Not a disposition.** The Beta-03 recommendation is decided **only** by the frozen beta03/CLOSE_RULE.md (s5). Nothing
in this file amends that rule. W5 is not silently replaced during the campaign (directive s10).

Working name for the target substrate: **TFS-1** (typed functional substrate, version 1).

---

## 1. Evidence chain: why the current substrate stops

### 1.1 The program space has one control structure and one accumulator
- **One fold.** A program is `("fold", init, body, final)` or `("expr", final)`. `basis_v4.run_program` (l.153-176)
  hard-codes a single left fold with one integer accumulator. There is no branching, recursion, second accumulator,
  lambda, let, or higher-order use (Hestia dossier s1.1, s3c).
- **Fixed vocabulary.** Bodies are built from 7 binary primitives over the atoms `acc v first last 0 1`, to depth 3
  (W5/G5).
- **What an abstraction is.** It is a **one-hole, body-only** Plotkin-LGG schema (`tier3d.derive_schemas`). Hole
  fillers come from a fixed set of 258 (`fair.LEVEL1`).
- **Size.**
  - The whole derivable universe from pristine coverage is 554 one-hole schemas (K3).
  - Per donor, a median of 1.5 (I_0@O4) to 4.5 (g11@O10) candidates are derived (dossier O3).

### 1.2 A library can only reorder a fixed walk
- `fair.py` says so itself: "every library has identical expressive power". KLib walks the library's entries, then
  the full fallback grammar.
- **Capability means position.** Capability is a position in a keyed walk of 2.3e8 (G4) to 9.7e9 (G5) programs.
- **The budget covers almost none of it.** The 1M cap covers 0.44% / 0.010% of those spaces. The 30k escrow covers
  0.013% of G4.
- **What was learned on natural supply.** Beta-02 learned three schemas over 22 seeds: `(acc + {H})` 10×,
  `(acc - {H})` 7×, `({H} + v)` 3×, and no schema 2×.
- **Directive "level 1".** This is search ordering, which the operator rates "strong positive". Level 2 is "not
  established".

### 1.3 R8's deficit is unequal headroom, and most of the residual is out of reach (E1 now MEASURED)
- **Beta-02 R8 stays frozen as NO.** Under I_0 machinery the improvement was 10 / 39 / 56 (L_g11 / L_I0 / L_P).
- **W01 (frozen-data diagnostic).** About 93% / 72% of the deficit vanishes on the common residual (301/640). 88% of
  that residual was acquired by no arm.
- **E1, fresh supply, 22 pairs, disposition MEASURED** (E1_REPORT.md):
  - **SATURATION_SUPPORTED.**
    - Own-start deficit L_g11 - L_P = **-104** (1/20/1, one-sided p 2e-6).
    - **Headroom share 0.933.**
    - End-state L_g11 388 ≥ L_P 363.
  - **INTERFERENCE: not supported.** Common-residual contrast -7 (2/4/16, two-sided p 0.44). The test was attainable
    (k = 6, minimum p 0.031).
  - **REPRESENTATION_CEILING_CONSISTENT: not met.**
    - 2 extending pairs acquired 2 common families each.
    - Those acquisitions are **unattributed**, and on the same pairs the pristine recipient acquired 2 and 1.
    - E1 composition is OFF for recipients (A1.5), so this is not a test of H3.
  - **89% of the common residual (329 slots) stays unsolved by every arm** (best arm 35, 10.6%).
- **Reading.** R8's failure is mostly a property of the **opportunity set** (the W8 world, consumed by first-order
  inheritance). That is world evidence, not substrate evidence (red team M3).
- **Lesson carried into s4 as a hard requirement.** Next-generation learning is scored on a **common, pre-recipient
  residual**, on any substrate.

### 1.4 Promotion is technically sound, and the known-positive depth-two control fails
**W5P machinery is qualified** (W5P_DESIGN s7). All 11 tests pass:
- PROMOTION_SEMANTICS: 15,360 cases, 0 mismatches;
- conformance: 18,600 evaluations and 48 walks;
- no-op continuity;
- fresh-process transplant.

**W9-H contains attainable depth-two families** (W9H_DESIGN s5; E5H_DESIGN_NOTES s1):
- 44/47 certified by expansion (30 strict), and **28 by W5P's own builder**;
- PROMOTED_A reaches 94/94 cells at 1M, but **only 4/188 at the 30k escrow**.

**The learner does not reach them:**
- **Gen-1 (pristine start): 0 schemas derived at 30k and at 300k on 3/3 exposed seeds.** PRISTINE observes 1/60 L1
  families at 30k.
- **Gen-2 oracle control, frozen W5P (300k): fails.** Depth-2 candidates are derived, but none is a true
  composition, because L2 bodies lie outside G5 and observation does not walk them.
- **The one cheap repair, O1 (observation also walks promoted applications): O1_FAILS, 0/3.**
  - Source: O1_REPAIR.md on origin/aphrodite/b03-w5p. The criterion was frozen before the runs.
  - Cost: **1.13 core-h** total (its s3); the itemised s4 table sums to ≈1.12.
  - **CANDIDACY broke on seeds 0 and 2.** On seed 2 the O1 walk hit **once**, because 300k covers about 68% of the
    O1 entry. That is budget-confounded.
  - **SELECTION broke on seed 1 under g11.** True composition C1 (saving 5,524) lost to the bare re-expression
    `P_acbd({H})` (7,862).
  - **Alias bookkeeping defect:** a bare `P_x({H})` is recorded as depth 2.
- **Disposition:** E5-H = INSTRUMENT_UNVALIDATED, not launched (directive Outcome C).

### 1.5 What the failures do and do not show (scoped; red team M4)
On 3 **exposed** pilot seeds:
- **CANDIDACY.** One-hole LGG failed to propose a true composition on **1 clean seed** (seed 0: 7 L2 observations,
  no true composition) and on **1 budget-confounded seed** (seed 2).
- **SELECTION.** g11 acceptance preferred an inherited re-spelling on 1 seed (seed 1). **Whether g12 would also have
  done so is untested.**
  - g12 is already built on W5 (E2). It credits reach only where INHERITED is censored, and requires S > 0.
  - The winning alias has "the same numbers" as its inherited plain twin, so g12 plausibly rejects it.
  - The SELECTION break is therefore attributed to the **acceptance rule**, which directive objective 1 replaces on
    W5. It is **not** attributed to the substrate.
- **OBSERVATION.** Gen-1 observation is starved at 30k and 300k. That is a world × budget property. **TFS-1 does not
  fix it by construction** (s2.4, M0 probe in s4).

**What the evidence does support.** The one-hole, body-only, LGG-over-a-fixed-walk representation has, on this
evidence, **not been shown able** to form or select a depth-2 composition, even with oracle level-1 knowledge. The
directive's single cheap repair for it has been spent.

**That is the Outcome C basis** recorded in CLOSE_RULE.md. It is not a proof that W5 *cannot* cross the boundary.
**s4 M1 adds the W5 comparator arm that could falsify the migration rationale** (red team M8).

### 1.6 Still open; outcomes are NOT predicted here
| Pending | What it is | Use in this design |
|---|---|---|
| **E2** (g12; E2_PREREG + A1) | does an acceptance rule that does not name MEMORISE generalise on W5? | calibrates s2.6; decides whether g12 is the established comparator in M1 / M2 (CLOSE_RULE "Separation") |
| **E5-N** (R8 under promotion, natural W8; E5N_PREREG + A1) | does W5P inheritance enable attributed depth-2 acquisition on the common residual? | the sole input to CLOSE_RULE |

---

## 2. Target substrate specification (TFS-1)

### 2.1 Terms and types
- **Terms:** a simply typed λ-calculus with rank-1 polymorphic primitive schemes, de Bruijn indices, and canonical
  (β-normal, η-long) storage form.
- **Types:**

  ```
  t ::= int | bool | list t | t -> t | alpha
  ```

  Enumeration is **type-directed**, so ill-typed terms are never proposed or charged.
- **Base primitives:**
  - **Arithmetic, byte-compatible with the engine:** `add sub mul fdiv mod gcd powr`, with exactly `basis_v4`'s guards:
    - `pow = 0` if b < 0 or b > 32;
    - fdiv/mod by 0 is FAIL;
    - FAIL if `|acc|` or `|out|` exceeds `CEIL` = 10^40.
  - **Control:** `if eq lt`.
  - **Lists:** `nil cons head last length`.
  - **Higher-order:** `foldl map filter`, and `unfold` (bounded to L steps).
  - **Constants:** `0 1`.
- **FAIL semantics:** an absorbing `Fail` value, which reproduces `run_program`'s `None`.
- **The W5 embedding E (the continuity anchor).** `("fold", i, b, f)` becomes

  ```
  λxs. let vs = (trailing ? init xs : xs); acc = foldl (λacc v. b) i vs in f
  ```

  - `first = head xs` and `last = last xs`.
  - The FAIL check runs after each step.
  - **`v` in `f` is bound to the last folded element, or 0 if there is none,** as `run_program`'s env does.

### 2.2 Learned primitives are first-class typed terms
- **What a library entry is.** A closed term `A = λx1..xk. e`, with arity 0 ≤ k ≤ 3 (frozen) and an inferred type.
  `e` may reference **earlier library entries**.
- **Record format.** The W5P `Promoted` record is generalised field for field:
  - `id = "A_" + sha256(canonical{substrate_version, term, deps})`, content-addressed and arm-blind;
  - `term` and `expansion`, `type`, `deps`, `lineage`;
  - `depth = 1 + max(dep depth)`;
  - `contract`, `source_artifact_sha256`, `hash`.
- **Loading.** `from_json` re-derives every field and requires byte equality.
- **Alias rule (fixes the O1 defect).** An entry α/η-equivalent to an existing entry, or to an existing entry applied
  only to bound variables, IS that entry: same id, same depth.

### 2.3 Explicit library retrieval
- **Retrieval is a logged step.** `retrieve(library, dev_examples) -> top-k R`, with k frozen.
  - Type compatibility comes first.
  - Then a frozen I/O-signature score.
- **The proposal distribution is conditioned on R.**
- **Ablation.** "Retrieve all" is the ablation and reproduces W5 behaviour.
- **Retrieval is identical across arms.**

### 2.4 Guided proposal distribution; cost in nats
- **The prior.** A library carries a probabilistic type-directed grammar. Its weights are fit by inside-outside counts
  on the library's solved corpus (DreamCoder-style unigram).
- **Search order.** Best-first enumeration in decreasing prior, so `DL = -ln p(program | grammar, R)`.
- **Escrow.** The escrow is B nats, plus a candidate cap. A 1-per-candidate meter is kept for continuity.
- **Common random numbers.** Ties within a frozen ε are ordered by `fair.key(seed, slot, canonical_term)`, which is
  arm-independent.
- **"Guided" means only library weights plus retrieval.** There is no neural recognition model (CPU-only, no live
  models).
- **Three ledgers:** candidates, nats, and expanded execution units. A library entry is never billed as one free
  operation.
- **Limitation (M6).** The pristine TFS-1 grammar strictly contains E(W5), so a pristine learner's DL for a W9-H
  level-1 witness can only grow relative to its W5 rank.
  - **TFS-1 cannot rescue gen-1 observation starvation by representation.**
  - Whether gen-1 is feasible at all is decided by the outcome-free M0 probe (s4) before any M1 freeze.

### 2.5 Measurable abstraction-dependency DAG
- **The DAG.** An edge runs A -> B iff B's term references A. `depth(B)` is the longest path, and it is recorded on
  every artifact and receipt.
- **Attributed depth d for an acquisition.** All three must hold:
  - (a) the first tribunal-qualified program references an entry B of depth d;
  - (b) B's chain contains an INHERITED entry;
  - (c) **ablation** loses the acquisition: B's dependency is removed as a reusable term, while its expansion stays
    enumerable from base primitives.
- **Base higher-order primitives are depth 0.** Using `map` is not a rung.

### 2.6 Compression-based acceptance with a transfer guard (restated per red team M9)
**Candidate generation: corpus compression.** Stitch-style top-down anti-unification over the donor's solved,
behaviour-classed corpus.
- Arity ≤ 3; multi-use variables.
- **The corpus is first refactored modulo the current library** (rewrite with the inherited entries). Without that
  step, expanded observations never expose `S_b(A_Sa(x))`. KAT in s3 (m3).

**MDL gain, in nats, under the library's own grammar:**

    MDL_gain(ΔA) = Σ_t L(ρ_t | Lib) − [ L(ΔA) + Σ_t L(ρ_t | Lib ∪ ΔA) ]

**Acceptance requires BOTH:**
- (i) `MDL_gain > 0`;
- (ii) **the g12 fold-minimum reach guard.** ≥ 1 tribunal-qualified, inherited-censored VALIDATE family in each of 2
  seeded folds (E4_DESIGN s3).

**What each part does, and does not, do:**
- **MDL rejects aliases.** After alias collapse their gain is 0 and L(ΔA) > 0.
- **MDL rejects single-use stored programs** (k = 1 gives no saving).
- **MDL does NOT in general reject memorisation.**
  - An arity-0 abstraction (a whole stored program) reused by k ≥ 2 tasks has positive gain.
  - W8 supply recurs exactly such programs: E1 A1.5 records 427 identical programs across seed blocks.
  - I_0 selected MEMORISE in 11/22 Beta-02 seeds and 11/24 E1 donor seeds.
- **Rejecting memorisation therefore rests on the reach guard (ii),** not on MDL. Whether it succeeds is an M1 Q4 / M2
  measurement, and is not predicted here.

**Relation to g12.**
- g12 is DL in entries (λ = 0.25) plus fold-minimum reach.
- TFS-1 replaces the DL term with nats and keeps reach as the guard.
- **E2's λ = 0 rescore shows which g12 term does the rejecting on W5.** If g12 rejects everything, the guard width
  (VALIDATE 12) is reviewed before any TFS-1 freeze.

### 2.7 Inspirations (named honestly; no benchmarks claimed)
Sources are those in science/frontier/PRIOR_ART_B_LIBRARY_LEARNING.md.

| Source | What TFS-1 takes from it |
|---|---|
| **DreamCoder / EC2** | typed λ library, MDL compression, probability-ordered enumeration. Its compute (about a day on 20-100 CPUs per domain) is far above our cap |
| **Stitch** | top-down compression with arity ≤ 3 |
| **babble** | compression modulo equations. Deferred: behaviour classing plays that role |
| **AbstractBeam** | the closest cousin of our observational-equivalence search |

- **The gap we fill.** No surveyed work runs a controlled transplant test of abstraction-on-abstraction.
- **The reporting standard.** "Library Learning Doesn't" sets it: compute-matched baselines plus behavioural reuse
  counts.
- **External dependency.** `stitch_core` is UNVERIFIED on Windows. It is decided at M0, with in-house compression as
  the fallback.

---

## 3. Transplant plan per preserved component
Every port passes its known-answer test (KAT) before any TFS-1 science.

| Component (current) | On TFS-1 | Interface | KAT |
|---|---|---|---|
| **Causal membrane** (engine.py `Lineage.extract` / `Recipient.load`; README guarantees) | the Artifact becomes the canonical JSON of {substrate_version, records, grammar weights, retrieval config} | `extract(gen)`; ONE loader for scratch / transplant / sham / positive; receipt of donor reads | port the **12 test_membrane.py cases**, including the NEGATIVE fixture and reset; **no-donor-state receipt check** (TH-021 open defect, now mandatory) |
| **Artifact hashing** | generalised Promoted record (s2.2) | `to_json` / `from_json` (re-derive) / `load_records` | port W5P SERIALIZATION + TRANSPLANT (31 records, fresh process). **Alias KAT:** the O1 `P_x({H})` case maps to P_x at depth 1 |
| **Escrow** | B nats plus a candidate cap, beneath the improver, equal across arms | `Escrow(nats, cap)` | the improver cannot raise it; identical exhaustion for identical libraries |
| **Paired fair search** (fair.py) | best-first by DL, CRN tie-break | `walk(lib, cell, budget) -> (first_qualified, charges, nats, exec_units)` | **(a) Invariance:** identical libraries give identical sequences; entry permutation, name scramble and corpus reorder have no effect. **(b) Index-identity (M7a):** on a frozen sample of E12 cells (2 seeds × all cells), E(KLib) walked in KLib order **with the TFS-1 evaluator** gives the identical first qualified program and walk index. The E12 totals (162 vs 63, 16/0/6) are then **derived from the frozen E12 walk records**, and stated as derived, not re-walked |
| **Behaviour classing + certification** (identity.py, a17 `certified_classes`) | per-type batteries. For `list int -> int`, B1/B2 are reused unchanged | `behavior_id(term, type)`, `certified_classes` | `behavior_id(E(p)) == identity.behavior_id(p)` on all 10,842 G4 sources; the `classes` field of 8 frozen E12 donor rows reproduced |
| **Hostile tribunal** (T4 v1a, path BOTH) | unchanged on the embedded `list int -> int` fragment. Every first-campaign endpoint is of that type | `qualifier(...)` | T01's 0/330 admission flips; the W9-H endpoint audit (FP 1/727, FN 0) on re-walked endpoints |
| **Exact paired statistics** | copied as is | `signflip`, `attainable_min_p` | recompute p 1.5e-5 (E12), p 0.31 / 0.25 (W01) and p 2e-6 / 0.44 (E1) from the receipts' d vectors |
| **Common-residual endpoint** (b03; **mandatory on any substrate**, per E1) | unchanged: built from START walks, hashed before any recipient | `common_residual(starts, families, cells)` | the reducer reproduces 301/640 (W01) and 329/704 (E1) from the frozen start-walk records |
| **Compression / refactoring** (new; m3) | corpus rewrite modulo the library, then anti-unification | `refactor(corpus, lib)`, `propose(corpus, lib)` | **Planted corpus:** 4 expanded programs `S_b(S_a(x_i))` with library {S_a}. The candidate `λx. S_b(A_Sa(x))` must be proposed at depth 2 with MDL gain > 0. The same corpus with an empty library proposes it only at depth 1. A planted alias is collapsed and rejected |
| **Selection rules g11 / g12** | comparators, run over TFS-1 candidates | `select(cands, start, cells)` | g12's 16 tests ported; MEMO / NULL / NEAR-MISS traps behave as in E2 |
| **W9-H + `certify_family`** | the composition grammar re-expressed as typed terms | `certify_family(f, builder)` | the TFS-1 builder certifies ⊇ the 28 W5P-certified pilot families, and nothing that expansion rejects |
| **Prereg / amendment / red team** | unchanged (FREEZE_*.json with sha, pre-data amendments, mechanical attacks) | process | first TFS-1 prereg passes a red-team pre-freeze review with 0 open BLOCKERs |
| **Failure fossils** (calibration/LEDGER.md, defect ledger) | carried forward | rows | **gate-liveness:** every gate FAILs on a negative fixture (the D55 constant-True class); import-order assertion (a18.TAG) |

---

## 4. First campaign on TFS-1 (minimal, pre-registrable)

**Envelope and hard requirements.**
- CPU only, M4. At most 48 core-h per rolling 24 h; target ≤ 40.
- $0 cloud. No live models. One inheritance step.
- Strictly ordered stages. **A failed gate stops the campaign.**
- One pre-registered neutral repair per stage.
- **Every next-generation endpoint is acquisition on a COMMON, pre-recipient residual**, hashed before recipients run
  (E1 lesson). Own-start measures are secondary only.

### M0: build, conformance, feasibility probe (DEV)
- **Build** TFS-1 and every s3 KAT. The gate is that all pass.
- **Throughput:** nats/s and candidates/s per core on a frozen probe set. **All later budgets are re-derived from it
  and frozen.**
- **Feasibility probe (M6; outcome-free; static; reads generator truth exactly as `certify_family` does):**
  1. For every L1 and L2 witness of the W9-H' qualification seeds, compute its DL in nats under (a) the pristine
     TFS-1 grammar and (b) the oracle-level-1 library grammar.
  2. Compare it with B_max = ln(candidates affordable per observation walk at the frozen budget).
  3. **Rule, frozen before the probe:** if the median L1 witness DL under (a) exceeds B_max, Q1 is **infeasible by
     construction**.
     - The world or the budget is fixed **before** the M1 freeze. For example, the observable L1 tier (E5H_DESIGN_NOTES
       option O2), applied equally to the W5 comparator.
     - It is recorded as SEARCH_BUDGET, not discovered at M1.
  4. The same check under (b) for L2 witnesses gates Q2.
  5. The W5 keyed rank of each witness is reported beside it.
- **Kill:** KATs not passing within 3 DEV windows gives SUBSTRATE_BUILD_FAILED. **This is the likeliest binding risk
  of the whole migration** (M7d).

### M1: instrument qualification, KNOWN-POSITIVE depth-two control FIRST
- **World and seeds.** W9-H CONFIG re-expressed in TFS-1, sha frozen.
  - Exposed dev seeds W9H:200-202.
  - Fresh qualification seeds W9H:203-210.
  - Positive set: TFS-1-certified families.
- **Q1, gen-1.** From PRISTINE, ≥ 1 true level-1 mechanism is accepted on ≥ 5/8 seeds. This is only run if the M0
  probe says it is feasible.
- **Q2, oracle gen-2 control.** Start = the true level-1 mechanisms; acceptance = s2.6. All three on ≥ 5/8 seeds:
  - (a) a true `S_b ∘ S_a` is a candidate;
  - (b) it is accepted as non-alias depth 2;
  - (c) ≥ 1 attributed EXTEND acquisition on an L2 family that PRISTINE reaches in 0 cells.
- **Q2-W5, the frozen W5 comparator arm (M8).**
  - Same 8 seeds and the same oracle start.
  - Machinery: **W5P + O1 + g12 acceptance + the alias fix (alias → P_x, depth 1)**, as a separately versioned branch
    frozen before M1, with no change to the E5-N-frozen W5P.
  - Escrow 300k, as O1.
  - Same Q2 criteria, with W5P's attributed EXTEND definition.
  - Cost: O1 ran 3 seeds in 1.13 core-h including diagnostics, so about **3-4 core-h for 8 seeds**.
  - **Interpretation, frozen:** if Q2-W5 passes on ≥ 5/8 seeds, the report states "**the migration was not necessary
    for crossing the boundary**", whatever TFS-1 does. The s1.5 rationale is then withdrawn.
- **Q3, specificity.** A SHAM_C start gives attributed depth-2 acquisition on ≤ 1/8 seeds.
- **Q4, traps.**
  - Planted MEMO (programs recurring k ≥ 2), alias and junk libraries are each rejected in ≥ 7/8 seeds.
  - Acceptance is non-empty in ≥ 6/8.
- **Kill.** Q2 fails, then one pre-registered repair on the exposed seeds, then 8 new fresh seeds. A second failure
  gives INSTRUMENT_UNVALIDATED_ON_TFS1, and the campaign stops.

### M2: first-order replication of memorisation exclusion
- **Supply.** Fresh W8 LIN 128-151 (24 seeds), embedded via E, O10 roles. LIN 120-127 stays reserved for E5-N E6(d).
- **Arms:**
  - **MDL+GUARD** (s2.6);
  - **SAVINGS** (the I_0 analogue);
  - **SAVINGS−MEM** (the g11 analogue);
  - NULL;
  - MEMO-PLANT;
  - **G12 (conditional, m2):** g12 over TFS-1 candidates.
    - If E2 returns G12_GENERAL_RULE = YES, G12 is the established comparator for the secondary contrast.
    - Otherwise it is reported descriptively.
- **Primary.** MDL+GUARD - SAVINGS on held-out families reached beyond PRISTINE. Exact one-sided sign-flip, ≥ 20
  usable seeds, attainable p reported.
- **Secondary.** MDL+GUARD vs (G12 if E2 YES, else SAVINGS−MEM), two-sided.
- **Replication** means the direction of the Beta-02 finding, not its magnitude.
- **Kill.** If the sum is ≤ 0, or MEMO-PLANT is accepted in > 2 seeds, MDL+GUARD does not replace the exclusion. The
  established comparator is carried to M3, declared.

### M3: R8 under promotion on TFS-1 (primary)
**Two worlds, separate claims, no pooling:**
- **Structured:** W9-H', **≥ 20 pairs = 40 seeds** (W9H:211-250; donor d → recipient d + 20) (M7c).
- **Natural:** W8. The donors are M2's MDL+GUARD libraries on LIN 128-151, frozen and hashed **before any M3 recipient
  runs**. The recipients are fresh **LIN 152-175** (pair d → d + 24), the Beta-02 E1 → R8 pattern. This reuses M2
  supply.

**Arms:**
- PRISTINE;
- **L_gen1**;
- L_SHAM (same size, from a disjoint grammar stream);
- L_ORACLE (structured only; a control).

Budgets, evaluator, retrieval, cells and tribunal are equal across arms.

**Endpoint.** Acquisition on the **common residual**, split into REORDER and EXTEND, with attributed depth (s2.5).

**Tests:**
- **P1 (sole confirmatory, per world):** L_gen1 - PRISTINE, exact one-sided sign-flip, ≥ 20 pairs.
- **SHAM:** L_gen1 - L_SHAM, p < 0.05 and sum > 0.
- **SECOND-LEVEL:** ≥ 3 pairs with an attributed depth-2 acquisition.

**Attacks, chosen now:**
- (a) inline the inherited dependency;
- (b) sham-swap it;
- (c) a name scramble, which must be invariant;
- (d) 8 further unseen lineages (LIN 176-183 / W9H:251-258).

**A demonstrated second compositional rung** (`R8_UNDER_PROMOTION_TFS1 = YES`, per world) requires ALL of:
1. M1 qualified.
2. P1 significant with sum > 0.
3. SHAM holds.
4. SECOND-LEVEL holds, with an endogenous, non-alias depth-2 entry whose dependency was learned by the donor and
   crossed the membrane as the only state.
5. (a) and (b) each drop acquisition in ≥ 2/3 of the SECOND-LEVEL pairs; (c) is invariant; (d) gives sum > 0 with
   ≤ 1 pair worse.
6. The gain holds on the expanded-execution ledger.

A structured-world YES alone means "second rung under designed stepping stones". It is not a natural-W8 replication.

**Substrate kill.** If M1 qualified, P1 is not positive in both worlds, and the attributed depth-2 fraction is < 10%,
the disposition is TFS1_NO_SECOND_RUNG, recorded. There is no grammar widening.

### Compute (honest re-budget; M7)
The rates come from:
- the Beta-03 W8 foundry: 26.3 core-h / 48 seeds ≈ 0.55 core-h per seed;
- W9-H at 96 families: about 0.5 core-h per seed including certification (E5H_DESIGN_NOTES s4);
- W5P / O1 donor timings.

**TFS-1 run costs are guesses until M0 measures throughput.** They are multiplied by the M0 slowdown factor relative to
`fasteval` before any freeze.

| Stage | Supply / foundry | Runs | Subtotal |
|---|---|---|---|
| M0 | none | KATs including index-identity (2 seeds) and the static probe | ~6-7 |
| M1 | W9-H' 11 seeds ≈ 5.5 | TFS-1 arms ~8; W5 comparator ~3-4 | ~17 |
| M2 | LIN 128-151 ≈ 13 | ~15 | ~28 |
| M3 structured | W9-H' 40 (+8 attack) seeds ≈ 24 | ~15-20 | ~42 |
| M3 natural | LIN 152-175 (+8 attack) ≈ 18 | ~15 | ~33 |
| **Total** | | | **≈ 125 core-h** |

- **That is at least 4 rolling-24h windows at ≤ 40 core-h/24h**, plus about 3 DEV windows of build. The campaign is
  multi-day, not one 48-hour block.
- **Fallback, if it must fit in one 48-hour block:** run M0 + M1 only (about 24 core-h). That is still decisive for
  the question that matters first: can any substrate pass the known-positive depth-two control? M2 and M3 are then
  scheduled in a later campaign.
- Per-job cap: 15 CPU-min, with checkpointed shards.

---

## 5. Recommendation rule: SUPERSEDED here
**The Beta-03 recommendation is governed solely by beta03/CLOSE_RULE.md** (frozen; its own sha). This design does not
restate or modify it. E1 and E2 enter only as qualifiers and TFS-1 design obligations, as that file specifies.

### 5.1 Risks and costs of migrating
- **Build risk (the most likely binding risk).** M0 covers:
  - a type-directed best-first enumerator;
  - type inference;
  - a refactoring compressor (or `stitch_core`, unverified on Windows);
  - the classing port;
  - 14 KAT families.

  SUBSTRATE_BUILD_FAILED is a realistic outcome, with a hard 3-window kill.
- **Gen-1 starvation is not addressed by representation (M6).** If the M0 probe fails, the fix is to the world or the
  budget, and it applies equally to W5. The migration then buys only the CANDIDACY and SELECTION links.
- **Necessity is not yet shown.** The SELECTION link may be fixable on W5 by g12. The M1 W5 comparator decides this,
  and the report must state its result whatever it is.
- **Compute.** About 125 core-h planned (s4), before the λ-interpreter slowdown factor is applied. If the cap binds,
  power drops. The attainable p is always reported.
- **Planting.** Base higher-order primitives make some behaviour reachable at depth 0. Depth is counted on learned
  entries with ablation, and the W9-H CONFIG is re-expressed, not re-tuned.
- **Compression ≠ transfer, and MDL ≠ anti-memorisation (s2.6).** The reach guard carries memorisation rejection and is
  tested in M1 Q4 and M2.
- **Comparability.** TFS-1 is a new evidence line. Every W5 label stays frozen.
- **Opportunity cost.** About 3 DEV windows and about 4 compute windows before any second-rung answer.

---

## 6. Uncertainties (unverified by this design)
- **E2 and E5-N had no outcome on record** when rev 1 was written. E1 is taken from E1_REPORT.md as the coordinator
  stated it. The receipts (E1_RESULT.json) were not re-opened here.
- **Index-identity KAT.** It assumes the E12 walk records hold, per cell, the first qualified program and its walk
  index. Not checked row by row.
- **Embedding edge cases.** `v` in `final`, empty lists, and the trailing query are read from `run_program` but not
  exercised.
- **Budgets.** Every TFS-1 run figure is a planning guess. The foundry figures use measured Beta-03 / W9-H rates on a
  contended host.
- **The g12-rejects-alias argument (s1.5)** is plausible from the O1 receipt ("same numbers" as the inherited twin) but
  untested. The M1 W5 comparator tests it.
