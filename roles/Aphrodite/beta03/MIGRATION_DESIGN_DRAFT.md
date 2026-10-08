# MIGRATION DESIGN (DRAFT): Aphrodite's scientific machinery on a typed functional substrate

Beta-03 (C-011). Scientific lead, migration design. Written 2026-10-08, during W02.

**Status: DESIGN ONLY.** No code was written or run for this document. It reads the files cited below and does
nothing else.
- **What it is:** the concrete migration design that directive s10 asks for "if the evidence supports retirement".
- **What it is NOT:** a disposition. Whether Aphrodite migrates is decided at the Beta-03 close (BETA03_48H_CLOSE_SYNTHESIS, s13 recommendation), and E1, E2 and E5-N were still pending when this was written (s1.5).
- **Rule:** W5 is not silently replaced during the campaign (directive s10). Nothing here changes any frozen Beta-03 experiment.

Working name for the target substrate: **TFS-1** (typed functional substrate, version 1).

---

## 1. Evidence chain: why the current substrate stops

### 1.1 The program space has one control structure and one accumulator
- **One fold.** A program is `("fold", init, body, final)` or `("expr", final)`. `basis_v4.run_program` (l.153-176)
  hard-codes a single left fold with one integer accumulator. There is no branching, recursion, second accumulator,
  lambda, let, or higher-order use (Hestia dossier s1.1, s3c).
- **Fixed vocabulary.** Bodies are built from 7 binary primitives over the atoms `acc v first last 0 1`, to depth 3
  (W5/G5).
- **What an abstraction is.** It is a **one-hole, body-only** Plotkin-LGG schema (`tier3d.derive_schemas`: "exactly
  one hole, non-root"). Inits and finals are never abstracted.
- **Filler set.** The hole is filled from a fixed 258-element LEVEL1 set (`fair.LEVEL1`).
- **Size.**
  - The whole derivable universe from pristine coverage is **554 one-hole schemas** (K3_DERIVABLE_UNIVERSE).
  - Per donor, a median of **1.5 (I_0@O4) to 4.5 (g11@O10)** candidate schemas are derived (dossier O3).

### 1.2 A library can only reorder a fixed walk
- `fair.py` says so itself: "every library has identical expressive power". `KLib.candidates` walks the library's
  entries and then the complete fallback grammar.
- **Capability means position.** Capability is the position of the first consistent program inside a keyed
  enumeration of 2.3e8 (G4) to 9.7e9 (G5) fold programs.
- **The budget covers almost none of it.** The 1M transfer cap covers 0.44% of G4 and 0.010% of G5. The 30k escrow
  covers 0.013% of G4 (dossier s3a).
- **What was learned on natural supply.** Beta-02 learned exactly three schemas across 22 seeds: `(acc + {H})` 10×,
  `(acc - {H})` 7×, `({H} + v)` 3×, and no schema 2× (dossier O3, cross-checked against R8_LIBRARIES.json).
- **Directive "level 1".** This is search ordering, the level the operator's closing notes rate "strong positive".
  Level 2 (search representation) is "not established".

### 1.3 R8's deficit is mostly unequal headroom, and most of the remaining headroom is out of reach
Beta-02 R8, which stays frozen as **NO**: next-generation improvement under I_0 machinery was 10 / 39 / 56
(L_g11 / L_I0 / L_P).

The W01 autopsy (beta03/runs/W01_R8_COMMON_RESIDUAL_DIAG.json; diagnostic only):
- **Common residual.** 301 of 640 slots are unreached by every start library.
- **About 93% (g11 machinery) and about 72% (I_0 machinery) of the own-start deficit disappears** when all arms are
  scored on that common set. Check of the arithmetic:
  - g11 machinery: own-start deficit 37 - 134 = -97, against a residual -7;
  - I_0 machinery: 10 - 56 = -46, against -13.
- **The residual deficit is not significant:** -7 (1/4/15, p = 0.31) and -13 (0/3/17, p = 0.25).
- **88% of the common residual is acquired by no arm** (the best arm takes 37/301).
- **Reading:** this is consistent with H1 (saturation) for the deficit, and with H3 (representation ceiling) for the
  unreachable remainder. Because the same data generated these hypotheses, E1 is the test (s1.5).

### 1.4 Promotion is technically sound, and the known-positive depth-two control still fails
**W5P is qualified as machinery** (engine/w5p/W5P_DESIGN.md s7). All 11 tests pass:
- PROMOTION_SEMANTICS: 15,360 cases, 0 mismatches;
- conformance: 18,600 evaluations and 48 walks, 0 mismatches;
- no-op continuity: reproduces T12 seed 17 exactly;
- fresh-process transplant.

**The structured world W9-H does contain attainable depth-two mechanisms** (science/b03_ecology/W9H_DESIGN.md s5).
- **CERTIFIED_DEPTH2 = 44/47** (30 strict).
- PROMOTED_A reaches **94/94** transfer cells at 1M; PRISTINE reaches 6/94.
- **Under W5P's own builder, 28 families are certified** (E5H_DESIGN_NOTES s1). All 16 mismatches come from the W5P
  instantiation rule `g5p_admissible`.

**The learner cannot reach them**, at any affordable escrow:
- **Gen-1 (pristine start), the observation channel is starved.** W5P donors derive **0 schemas at 30k and at 300k**
  on 3/3 seeds (E5H_DESIGN_NOTES s3a-b). PRISTINE observes 1/60 L1 families at 30k.
- **Gen-2 known-positive control (oracle level-1 start, rule g11), frozen W5P: FAILS.** At 300k it derives depth-2
  candidates, but **none is a true composition** S_b∘P_a. They are `P_outer(base-inner)` forms that G5 happened to
  fold. The cause is that L2 bodies lie outside G5, and observation cannot see them (W5P limitation 1, frozen as
  E5-N D1).
- **The one cheap arm-neutral repair, O1 (observation also walks promoted applications): O1_FAILS, 0/3 seeds**
  (O1_REPAIR.md on origin/aphrodite/b03-w5p; criterion frozen before the runs; 1.12 core-h).
  - O1 does make L2 families observable: 7 / 8 / 1 L2 observations.
  - **CANDIDACY breaks on seeds 0 and 2.** One-hole LGG over the observed classes does not produce the true
    composition.
  - **SELECTION breaks on seed 1.** The true composition C1 was eligible (mean paired saving 5,524). It lost to the
    bare re-expression `P_acbd({H})` (7,862).
  - **Alias defect.** A bare `P_x({H})` is recorded as depth 2.
- **Disposition (ledger, 11:42Z):** structured-world R8 (E5-H) = **INSTRUMENT_UNVALIDATED**, and it was not
  launched. This is directive Outcome C: "if not [repairable cheaply], stop".

### 1.5 The pattern behind these failures
Three links fail, and each is a property of the substrate rather than of a tunable parameter.

1. **Observation sees only what the fixed walk reaches.** A promoted primitive does not change what is CHEAP to
   observe. It only changes what is derivable after observation.
2. **Candidate generation is one-hole syntactic LGG.** It cannot express `S_b ∘ S_a` as a generalisation of the
   observed bodies unless the hole pattern happens to line up. Arity > 1 and multi-use variables are absent.
3. **Acceptance is paired charge saving.** This statistic rewards whatever is cheapest to walk first:
   - in Beta-02, the lookup table (MEMORISE, 11/22 fresh seeds);
   - in O1, a re-spelling of an inherited mechanism.

   The second is the same pathology as the first, appearing again. g11 fixed the first by deleting a candidate type
   (`b02.py:139-142`). Nothing comparable is available for the second without another hand-coded exclusion.

### 1.6 Still open; outcomes are NOT predicted here
| Pending | What it decides | Where this design uses it |
|---|---|---|
| **E1** (saturation / interference / ceiling; fresh LIN 72-119; E1_PREREG + A1) | whether R8's deficit was headroom (H1), interference (H2) or consistent with a ceiling (H3) | s5 decision table |
| **E2** (g12: fold-minimum reach - 0.25·DL; E2_PREREG) | whether an acceptance rule that does not name MEMORISE generalises | s2.6 inherits g12's fold-minimum guard. A g12 failure mode is diagnostic for MDL |
| **E5-N** (R8 under promotion, natural W8; E5N_PREREG + A1; KILL_CRITERION_HESTIA mechanical) | whether W5P yields an attributed depth-2 acquisition on natural supply | s5 decision table |

Status when written: `beta03/runs/` holds the known-answer receipts for E2 and E5N, SUPPLY, the W01 diagnostic, and
an in-progress `runs/E1/E1_DONORS.jsonl` (donor stage only, not read by this design).
- E1, E2 and E5-N have **no outcome on record**.
- E5N A1 item 3 caveat: "a natural-world NO does not by itself trigger retirement without the structured-world
  known-positive control". **That control is now INSTRUMENT_UNVALIDATED (1.4), which is itself evidence about the
  instrument, not about recursion.**

---

## 2. Target substrate specification (TFS-1)

### 2.1 Terms and types
- **Terms:** a simply typed lambda calculus with let-polymorphic primitives, de Bruijn-indexed, in canonical
  (β-normal, η-long) storage form.
- **Types:**

  ```
  t ::= int | bool | list t | t -> t | alpha
  ```

  Type inference uses Hindley-Milner restricted to rank-1 primitive schemes. Enumeration is **type-directed**, so
  ill-typed candidates are never proposed or charged.
- **Base primitives:**
  - **Arithmetic, kept byte-compatible with the engine:** `add sub mul fdiv mod gcd powr`, with **exactly
    `basis_v4`'s guards**:
    - `pow(a,b) = 0` if b < 0 or b > 32;
    - fdiv/mod by 0 is FAIL;
    - FAIL if `|acc|` or `|out|` exceeds `basis_v4.CEIL` = 10^40.
  - **Control:** `if`, `eq`, `lt`.
  - **Lists:** `nil cons head last length`.
  - **Higher-order:** `foldl : (b->a->b)->b->list a->b`, `map`, `filter`, and `unfold` (bounded: at most L steps, the
    same ceiling).
  - **Constants:** `0 1`.
- **FAIL semantics:** an absorbing `Fail` value, which reproduces `run_program`'s `None`.
- **The W5 embedding E: W5 -> TFS-1 (a total, checked translation).** It is the design's continuity anchor.
  - `("fold", i, b, f)` becomes
    `λxs. let vs = (trailing ? init xs : xs); acc = foldl (λacc v. b) i vs in f`,
    with `first = head xs`, `last = last xs`.
  - **The FAIL check runs after each step**, as `run_program` does.
  - **`v` in `final` is bound to the last folded element** (0 if there is none), as `run_program`'s env does after
    its loop. The conformance test (s3) must pin this edge case.
  - `("expr", f)` becomes `λxs. f`.

### 2.2 Learned primitives are first-class typed terms
- **What a library entry is.** A closed term `A = λx1..xk. e`, with k ≥ 0 (multi-hole, arbitrary arity) and an
  inferred type scheme.
- **Entries can build on entries.** `e` may reference base primitives and **earlier library entries**.
- **Record format.** The W5P `Promoted` record is generalised field for field (W5P_DESIGN s2):
  - `id` = `"A_" + sha256(canonical{substrate_version, term, deps})`, content-addressed and arm-blind;
  - `term` (with library references) and `expansion` (fully inlined base term);
  - `type`, `deps`, `lineage`, `depth` = 1 + max(dep depth);
  - `contract`: totality, FAIL behaviour, and arity;
  - `source_artifact_sha256`;
  - `hash`.
- **Loading.** `from_json` re-derives every field and requires byte equality. This is unchanged from W5P.
- **Alias rule (fixes the O1 defect).** An entry whose expansion is α/η-equivalent to an existing entry, or to an
  existing entry applied to bound variables only, is the SAME entry: it gets the same id and depth. Aliases cannot
  carry depth.

### 2.3 Explicit library retrieval
- **Retrieval is a logged, ablatable step.** For each task, `retrieve(library, dev_examples) -> ranked subset R`
  (top-k, k frozen) is computed from the development examples only.
  - Type compatibility comes first.
  - Then a frozen I/O-signature score: the entry's behaviour on the dev inputs, compared with outputs where the type
    allows.
- **The proposal distribution is conditioned on R, not on the whole library.**
- **Retrieval is part of the artifact's machinery, not of the donor.** It is identical across arms. It can be
  replaced by "retrieve all" as an ablation, which is the W5 behaviour.

### 2.4 Guided proposal distribution; cost in nats
- **The prior.** A library carries a probabilistic type-directed grammar: production weights over base primitives,
  library entries and variables. The weights are fit by inside-outside counts on the library's own solved corpus,
  in the style of DreamCoder's unigram grammar.
- **Search order.** Search enumerates in **decreasing prior probability** (best-first / heap enumeration), so
  description length is `-ln p(program | grammar, R)` in nats.
- **The search budget is in nats.** The donor enumerates every program with DL ≤ B nats, and B is the escrow. A
  candidate-count meter (1 charge per candidate) is kept beside it for continuity with Beta-02.
- **Common random numbers (fair.py, preserved).** Programs of equal DL (within a frozen quantisation ε) are ordered
  by `fair.key(seed, slot, canonical_term)`, which is arm-independent. As a result:
  - byte-identical libraries walk identical sequences;
  - entry order and entry names do not matter.
- **What "guided" means in TFS-1:** library weights plus retrieval. **There is no neural recognition model in the
  first campaign** (CPU-only; no live models). A task-conditioned model is a later, separately authorised step.
- **Billing ledgers, as in W5P s5:**
  - (i) candidates;
  - (ii) nats spent;
  - (iii) expanded execution units (inlined node count × examples).

  A library entry is never billed as one free operation on the execution ledger.

### 2.5 Measurable abstraction-dependency DAG
- **The DAG.** Nodes are library entries; an edge runs A -> B iff B's term references A.
- **Structural depth.** `depth(B)` = the longest path. It is recorded on every artifact and every receipt.
- **Attributed depth of an acquisition** (generalising E5N A1.1). An acquired family counts at depth d iff:
  - (a) its first tribunal-qualified program references an entry B of depth d;
  - (b) B's chain contains an INHERITED entry;
  - (c) **ablation:** removing B's dependency from the learner, while keeping the same base expressivity (the
    expansion is still enumerable from base primitives), loses the acquisition.
- **Depth is counted on learned entries only.** Base higher-order primitives (`map`, `foldl`) are depth 0. Using
  `map` is not a rung.

### 2.6 Compression-based (MDL) acceptance replaces the hand-coded exclusion
**Candidate generation: corpus compression.** Stitch-style top-down anti-unification over the donor's corpus of
solved, behaviour-classed programs.
- Arity ≤ 3 (frozen).
- Multi-use variables.
- Abstractions may contain library references. **This is where depth 2 can arise without a designer move.**

This replaces one-hole LGG. It attacks the CANDIDACY link that broke in O1.

**Acceptance (MDL, in nats, under the library's own grammar).** Accept a candidate set ΔA iff

    MDL_gain(ΔA) = Σ_t L(ρ_t | Lib) − [ L(ΔA) + Σ_t L(ρ_t | Lib ∪ ΔA) ]  > 0

where:
- ρ_t is the shortest rewrite of task t's solution (refactoring);
- `L(ΔA)` is the abstraction's own description length;
- the corpus is OBSERVE.

What this does to the two known traps:
- **MEMORISE** stores each solution verbatim. It compresses nothing (L(ΔA) ≈ Σ L(ρ_t)), so it is rejected **without
  being named**.
- **A bare alias** adds L(ΔA) > 0 and saves 0 nats, so it is rejected. This attacks the SELECTION link that broke in
  O1.

**Transfer guard: g12's fold-minimum, kept as a necessary condition.** An accepted ΔA must also reach ≥ 1
tribunal-qualified, inherited-censored VALIDATE family in each of the 2 seeded folds (E4_DESIGN s3 / g12).

**How this relates to g12.** g12 is a coarse MDL:
- its DL is counted in **entries** at λ = 0.25 (G12_IMPLEMENTATION.md);
- its benefit is **reach**, not code length.

TFS-1 measures both terms in nats. It keeps g12's reach term as a guard, because compression ≠ transfer.

**E2 outcomes are read as calibration for this design:**
- If g12's λ = 0 rescore shows the DL term doing the rejecting, that supports MDL-as-exclusion.
- If g12 rejects everything (`S ≤ 0`), that warns that the fold-minimum guard is too strict at VALIDATE width 12, and
  the guard's width must be fixed before any TFS-1 freeze.

### 2.7 Inspirations (named honestly; no benchmarks claimed)
Sources are those catalogued in science/frontier/PRIOR_ART_B_LIBRARY_LEARNING.md. Nothing here claims their numbers
for TFS-1.

| Source | What TFS-1 takes from it |
|---|---|
| **DreamCoder / EC2** (Ellis et al.) | typed λ-calculus library, MDL/Bayesian compression, enumeration in probability order. Its compute (about a day on 20-100 CPUs per domain) is far above our cap, so TFS-1 is deliberately smaller |
| **Stitch** (Bowers et al., POPL 2023) | top-down corpus compression with arity ≤ 3, as the candidate generator |
| **babble** (Cao et al., POPL 2023) | compression modulo an equational theory. Deferred: behaviour classing (s3) plays that role first |
| **AbstractBeam** | the closest architecture to our enumerative, observational-equivalence search |

The prior-art note's key gap is ours to fill: **no surveyed work runs the controlled transplant test for
abstraction-on-abstraction.** The "Library Learning Doesn't" critiques set the reporting standard: compute-matched
baselines plus behavioural reuse counts.

**Whether to vendor `stitch_core` or implement compression in-house** is decided at M0. It is UNVERIFIED that a
pinned Python/Windows build exists and conforms. In-house is the fallback, and either option is conformance-tested
against hand-computed toy corpora.

---

## 3. Transplant plan per preserved component

Every port must pass its known-answer test (KAT) **before any TFS-1 science**. "Reproduce" means byte-equal or
count-equal on the receipts named.

| Component (current) | On TFS-1 | Interface | KAT that proves the transplant |
|---|---|---|---|
| **Causal membrane** (engine.py `Lineage.extract` / `Recipient.load` / Artifact; README "What the membrane guarantees") | unchanged semantics. The Artifact becomes the canonical JSON of {substrate_version, library records, grammar weights, retrieval config} | `extract(gen) -> Artifact`; `Recipient.load(artifact)` as the ONE loader for scratch / transplant / sham / positive; receipt listing every donor read | port all **12 tests/test_membrane.py cases** against the TFS-1 Artifact, including the NEGATIVE fixture (an extra payload is caught) and reset-destroys-markers. Plus a **receipt check that no donor state crossed** (Beta-01 open defect TH-021, now mandatory) |
| **Artifact hashing** | the W5P Promoted record generalised (s2.2) | `to_json`, `from_json` (re-derive, then compare bytes), `load_records` (any order) | port W5P SERIALIZATION + TRANSPLANT (31 records, fresh process, 0 mismatches). Add an alias-collapse test: the O1 bare `P_x({H})` case must map to P_x at depth 1 |
| **Escrow** | budget in nats (B) plus a candidate cap, enforced beneath the improver and equal across arms | `Escrow(nats, cap)` with `charge()` raising `EscrowExhausted` | the improver cannot raise it; identical exhaustion point for byte-identical libraries; the README "escrow beneath the improver" test |
| **Same-loader controls** | unchanged | as the membrane | sham / positive fixtures load through the same path (membrane tests) |
| **Paired fair search** (fair.py CRN keys) | best-first enumeration by DL, ties broken by `fair.key(seed, slot, canonical_term)` | `walk(lib, cell, budget) -> (first_qualified, charges, nats, exec_units)` | **(a) Invariance:** identical libraries give identical sequences; permuting entries, scrambling names (E5N A1 6c) and reordering the corpus change nothing. **(b) COMPAT MODE:** E(KLib) is walked with the KLib order instead of the DL order. It must reproduce `fair.search_collect` charge counts on a frozen sample of Beta-02 E12 cells, then the **E12 receipt totals g11@O10 162 vs I_0@O4 63, 16/0/6** from the frozen E12 donor libraries (transfer walks only) |
| **Behaviour classing + certification** (identity.py `behavior_id` / `audit_id`, B1/B2 batteries; a17 `certified_classes` with CT.certify) | per-type batteries. For `list int -> int`, the B1/B2 batteries are reused unchanged. Other types get new frozen batteries with a declared out-of-support share (calibration LEDGER row 2026-09-17, E3 verifier) | `behavior_id(term, type)`, `certified_classes(observed, cov)` | (a) `behavior_id(E(p)) == identity.behavior_id(p)` on all **10,842 G4 sources** (the W5P PARSE_NORMALISE_CONTINUITY scope); (b) reproduce the `classes` field of E12_DONORS rows for a frozen sample of 8 donors |
| **Hostile tribunal** (T4 v1a; v2b/instruments `qualifier` path BOTH) | T4 v1a runs unchanged on the embedded `list int -> int` fragment. New types need a tribunal extension, and that extension is its own qualification (out of scope for the first campaign: s4 restricts endpoints to `list int -> int`) | `qualifier(prov, name, version, path)` | reproduce T01's **0/330 admission flips** and the W9-H endpoint audit (**FP 1/727, FN 0**) on re-walked endpoints |
| **Exact paired statistics** (b02/b03 sign-flip, Holm, attainable-p reporting) | the pure functions are copied as they are | `signflip(d, side)`, `attainable_min_p(k)` | recompute **p = 1.5e-5** from E12's per-seed d vector, and **p = 0.31 / 0.25** from the W01 residual contrasts |
| **Common-residual endpoint** (b03 E1) | unchanged definition: built mechanically from START walks, hashed before any recipient | `common_residual(starts, families, cells) -> frozen set` | reproduce the W01 count **301/640** from the frozen Beta-02 start walks via COMPAT MODE |
| **Selection rules g11 / g12** | kept as comparators. g11 = savings minus the MEMORISE type, g12 = fold-minimum reach - λ·DL, both run over TFS-1 candidates | pluggable `select(cands, start, cells)` (W5P harness API) | g12's 16 unit tests ported; MEMO / NULL / NEAR-MISS traps behave as in E2 |
| **W9-H ecology + `certify_family`** | the composition grammar is re-expressed in typed terms; known-positive control libraries PROMOTED_A / ORACLE / SHAM_C become typed entries | `certify_family(f, builder)` | **D5-style agreement:** the TFS-1 builder certifies ≥ the 28 W5P-certified pilot families, and never certifies one that expansion rejects |
| **Prereg / amendment / red-team discipline** | unchanged: FREEZE_*.json carrying the spec sha, pre-data amendments, red-team pre-freeze review, mechanically chosen E6-style attacks | process | first TFS-1 prereg passes a red-team pre-freeze review with 0 open BLOCKERs |
| **Failure fossils** (calibration/LEDGER.md; defect ledger) | carried forward; new rows for known code-level failure classes | ledger rows | **gate-liveness test:** every gate must FAIL on a negative fixture. This guards the D55 constant-True gate class. Also an import-order assertion, as in the a18.TAG defect |

**COMPAT MODE is the bridge, not a product.** Its only purpose is to prove that the instruments did not change
meaning in transplant. Native TFS-1 science never runs in COMPAT MODE.

---

## 4. First campaign on TFS-1 (minimal, pre-registrable)

**Envelope.**
- CPU only, on M4. At most 48 core-h per rolling 24 h, checked before each stage; target ≤ 40 core-h/24 h to leave
  headroom for other seats.
- Cloud spend $0 unless separately authorised. No live models.
- One generation of inheritance, with no third generation.
- The stages are strictly ordered. **A stage that fails its gate stops the campaign at that stage.**
- One pre-registered, scientifically neutral repair is allowed per stage. There is no second repair.

### M0: substrate build and conformance (DEV; ≤ 6 core-h)
- **Work:** build TFS-1 (s2) and all s3 KATs.
- **Gate M0:** every s3 KAT passes, including COMPAT-MODE reproduction of E12 (162 vs 63, 16/0/6) and W01 (301).
- **Throughput measurement:** nats/s and candidates/s per core on a frozen probe set. **Every later budget below is
  re-derived from this measurement and frozen.** The numbers here are planning guesses.
- **Kill:** if the KATs do not pass within 3 DEV windows, the disposition is SUBSTRATE_BUILD_FAILED. Report it and
  stop. No science.

### M1: instrument qualification, KNOWN-POSITIVE depth-two control FIRST (≤ 8 core-h)
The lesson of W9-H and O1: **no confirmatory R8 runs until the assay can detect a planted depth-2 positive.**

- **World.** W9-H CONFIG re-expressed in TFS-1, with its sha frozen.
  - Exposed dev seeds: W9H:200-202.
  - Fresh qualification seeds: W9H:203-210.
  - The pilot seeds 0-2 stay excluded.
- **Positive set.** Families certified by the TFS-1 builder (s3).
- **Q1, gen-1 learnability.** From a PRISTINE start at the frozen budget B, the donor accepts ≥ 1 TRUE level-1
  mechanism (behaviour-equal to S_a on B1) on ≥ 5/8 fresh seeds.
  - This is the link that starved W5P (0 derived at 30k and 300k).
  - If Q1 fails, B is not raised after the fact. Report CANDIDACY or SEARCH_BUDGET and stop.
- **Q2, known-positive gen-2 control.** Start = the seed's true level-1 mechanisms; machinery = MDL acceptance. All
  three must hold on ≥ 5/8 fresh seeds:
  - (a) a TRUE composition `S_b ∘ S_a` is among the candidates (CANDIDACY);
  - (b) it is accepted as a non-alias depth-2 entry (SELECTION);
  - (c) it gives ≥ 1 attributed EXTEND acquisition on an L2 family that PRISTINE reaches in 0 cells (TRANSFER).
- **Q3, specificity.** A SHAM_C start (wrong level-1 mechanisms, same screens) yields attributed depth-2 acquisitions
  on ≤ 1/8 seeds.
- **Q4, traps.**
  - A planted MEMO library, a planted alias library and planted junk are each rejected by MDL acceptance in ≥ 7/8
    seeds.
  - Acceptance is non-empty: something is accepted in ≥ 6/8 seeds.
- **Kill:**
  - If Q2 fails, the disposition is **INSTRUMENT_UNVALIDATED_ON_TFS1**. Record the first broken link (CANDIDACY /
    SELECTION / TRANSFER / SEARCH_BUDGET), allow one pre-registered repair on the exposed seeds, then re-run on 8 new
    fresh seeds.
  - If Q2 fails a second time, stop. **TFS-1 has not crossed the boundary W5P could not cross.**

### M2: first-order replication of memorisation exclusion via MDL (≤ 15 core-h)
- **Supply.** Fresh W8 LIN seeds 128-151, embedded via E, with Beta-02 roles at O10. LIN 120-127 stays reserved for
  E5-N's E6(d).
- **Arms (same machinery otherwise):**
  - **MDL** (s2.6 with the fold guard);
  - **SAVINGS** (the I_0 analogue: paired savings);
  - **SAVINGS−MEM** (the g11 analogue);
  - NULL (planted OFF);
  - MEMO-PLANT.
- **Primary.** MDL - SAVINGS on held-out families reached beyond PRISTINE. Exact one-sided sign-flip over seeds;
  usable seeds ≥ 20; attainable p reported.
- **Secondary.** MDL vs SAVINGS−MEM, two-sided (does the general rule match the type rule?).
- **What counts as replication.** The DIRECTION of the Beta-02 finding (acceptance by savings admits non-generalising
  knowledge; a rule that does not name the type removes it), not its magnitude. Magnitude is COMPAT MODE's job, done
  in M0.
- **Kill.** MDL - SAVINGS sum ≤ 0, or MEMO-PLANT accepted in > 2 seeds: MDL acceptance does not replace the exclusion.
  Fall back to SAVINGS−MEM as the established comparator and continue to M3 with it, declared. This follows the
  directive's g12 rule: the acceptance outcome does not decide which representation experiment runs.

### M3: R8 under promotion on TFS-1 (primary; ≤ 15 core-h)
Run in two worlds, with separate claims: structured W9-H' (fresh seeds 211-226) and natural W8 (LIN 152-199, donor
→ recipient pairs d ↔ d + 24).

- **Arms:**
  - PRISTINE;
  - **L_gen1** (the MDL donor's library from a pristine start);
  - L_SHAM (the same number of entries, drawn from a disjoint grammar stream and screened identically);
  - L_ORACLE (structured world only; a control, never a treatment).
- **Equal across arms:** budgets, evaluator, retrieval rule, cell seeds and tribunal.
- **Endpoint.** Acquisition on the **common residual**, built from START walks and hashed before any recipient. Every
  acquisition is split into REORDER (the first qualified program needs no inherited entry) and EXTEND, both carrying
  attributed depth (s2.5).
- **P1 (sole confirmatory).** L_gen1 - PRISTINE on common-residual acquisition. Exact one-sided sign-flip; ≥ 20 pairs
  per world. **The natural world and the structured world are separate tests, with no pooling.**
- **SHAM.** L_gen1 - L_SHAM, one-sided p < 0.05 and sum > 0.
- **SECOND-LEVEL.** ≥ 3 pairs with an attributed depth-2 acquisition.
- **Attack, chosen now (the E5N A1 item 6 pattern):**
  - (a) inline-expand the inherited dependency, keeping it enumerable but not a reusable term;
  - (b) a sham swap of the inherited entry;
  - (c) a name scramble, which must be invariant;
  - (d) 8 further unseen lineages.

**A demonstrated second compositional rung** (the label `R8_UNDER_PROMOTION_TFS1 = YES`, per world) requires ALL of:
1. M1 qualified (the known-positive control passed on fresh seeds).
2. P1 is significant, with sum > 0, on ≥ 20 pairs.
3. SHAM holds.
4. SECOND-LEVEL holds. The depth-2 entry B was accepted by the endogenous rule, not planted, and is not an alias; its
   dependency A was learned by the donor and crossed the membrane as the only state.
5. Attacks (a) and (b) each drop acquisition in ≥ 2/3 of the SECOND-LEVEL pairs; (c) is invariant; (d) gives
   sum(gen1 - PRISTINE) > 0 with ≤ 1 pair worse.
6. The gain holds on the expanded-execution ledger as well as on candidates and nats (no cheaper-billing artefact).

A structured-world YES alone is reported as "second rung under designed stepping stones". It is NOT a natural-W8
replication (directive s7).

**Kill for the substrate.** The disposition **TFS1_NO_SECOND_RUNG** is recorded, and stays recorded, if both:
- M1 qualified, and M3 P1 is not positive in both worlds;
- the attributed depth-2 fraction is < 10% of pairs.

That is the Hestia criterion transplanted. The grammar is then NOT widened to rescue it.

**Compute total.** About 44 core-h, planned (M0 6 + M1 8 + M2 15 + M3 15), spread over ≥ 2 rolling-24h windows.
Every number is re-frozen after the M0 throughput measurement. Per-job cap: 15 CPU-min, with checkpointed shards.

---

## 5. Risks, costs, and when CONTINUE_CURRENT_ENGINE is the right call

### 5.1 Risks and costs of migrating
- **Engineering risk.** TFS-1 is the largest build in this seat's history. The type-directed best-first enumerator,
  the compressor and the classing port are each nontrivial.
  - M0 has a hard 3-window kill.
  - COMPAT MODE keeps every Beta-02 receipt checkable, so a migration bug cannot masquerade as a scientific result.
- **Compute risk.** Interpreting λ-terms in Python is slower per candidate than `fasteval` on fold bodies.
  DreamCoder-class compression is expensive (prior-art note: a day on 20-100 CPUs per domain). Mitigations:
  - arity ≤ 3;
  - corpora of tens to hundreds of programs;
  - budgets in nats.
  - Residual risk: M1/M3 may need more than 48 core-h/24 h, which forces smaller seed counts and lower power. The
    attainable p is reported in either case.
- **Planting risk.** Base `map/filter/fold/unfold/if` make some "depth-2" behaviour reachable at depth 0.
  - Depth is counted on learned entries only, with ablation (s2.5).
  - The W9-H generator must not be re-tuned toward TFS-1's primitives. Its CONFIG is re-expressed, not redesigned.
- **Compression ≠ transfer.** MDL can accept abstractions that compress OBSERVE but do not transfer. That is why the
  g12 fold guard is kept, and why M2 tests MDL against SAVINGS on held-out reach.
- **Comparability loss.** TFS-1 results are a new evidence line (tier 2, new substrate). They do not relabel any W5
  result, and every W5 label stays frozen.
- **Opportunity cost.** About 3 DEV windows of build before any science. During that time no W5 experiment runs on
  the new substrate.

### 5.2 Decision table: when to prefer CONTINUE_CURRENT_ENGINE instead
These conditions are fixed now, before any E1, E2 or E5-N outcome, and are read mechanically at the Beta-03 close.

| Pending outcome | Recommendation | Why |
|---|---|---|
| **E5-N `R8_UNDER_PROMOTION = YES`** (after E6: DEPENDENCY_CONFIRMED, invariance, unseen lineages pass) | **CONTINUE_CURRENT_ENGINE** (with W5P) | A clean second rung exists on the current substrate. Migration would trade a demonstrated instrument for an unproven one |
| E5-N YES_PENDING_E6 but NO_AFTER_ATTACK | MIGRATE_SUBSTRATE | the depth-2 acquisition did not depend on the inherited abstraction |
| E5-N NO with channel **CLOSED_CANDIDACY or CLOSED_SELECTION**, and KILL_CRITERION_HESTIA FIRES | **MIGRATE_SUBSTRATE** | the same two links O1 broke, now on natural supply. Both are substrate properties (s1.5) |
| E5-N NO with channel **OPEN_NO_EXTEND_ACQUISITION / OPEN** | MIGRATE_SUBSTRATE, weaker form | promotion works but extends nothing useful. This is consistent with a world/representation ceiling, so W5 has nothing left to test cheaply |
| E5-N gate fails (no-op mismatch → MEASUREMENT_FAILED) or PC fails (INSTRUMENT_UNVALIDATED) | **INSTRUMENT_REPAIR_REQUIRED** | no substrate decision from a broken instrument. With E5-H also unvalidated, though, the repair would be a second repair of the promotion instrument, which the directive discourages |
| **E1 INTERFERENCE_SUPPORTED** (and not ceiling-consistent) | CONTINUE_CURRENT_ENGINE **for the interference question only** | interference is a property of search ordering (fair.py / KLib priority), which TFS-1 inherits through its CRN tie-break and priority. A cheaper W5 experiment on ordering (e.g. interleaved inherited/fallback walks) comes before migration |
| E1 SATURATION_SUPPORTED and/or REPRESENTATION_CEILING_CONSISTENT | supports MIGRATE | the W8 / one-hole opportunity set is consumed by first-order inheritance. More W5 engineering cannot create headroom |
| E1 INCONCLUSIVE / NO_POSITIVE_CONTROL | neutral | the decision rests on E5-N and on the E5-H status |
| E2 (g12) any outcome | **does not decide the substrate** (directive s5) | it calibrates s2.6 only |

**Combined rule (proposed for the close).**
- **MIGRATE_SUBSTRATE iff** E5-N is not YES, AND E5-N's failure is not MEASUREMENT, AND E1 does not return
  interference-only.
- **CONTINUE_CURRENT_ENGINE** iff E5-N = YES, or E1 = interference-only with E5-N not decisive.
- **INSTRUMENT_REPAIR_REQUIRED** otherwise.

E5-H (INSTRUMENT_UNVALIDATED after O1) counts toward MIGRATE whenever E5-N is not YES. The directive's Outcome C
names exactly this case: "Don't spend days trying to coerce a one-hole grammar into behaving like a higher-order
language."

---

## 6. Uncertainties (unverified by this design)
- **Pending experiments.** E1, E2 and E5-N had no outcome on record in `beta03/runs/` when this was written. A newer
  commit on another branch was not checked beyond the coordinator branch head (99e74c368).
- **COMPAT-MODE feasibility.** It assumes the frozen E12 donor libraries and walk cells are fully recoverable from
  E12_DONORS / E12_WALKS. Not checked row by row.
- **Embedding edge cases.** `v` binding inside `final`, empty lists, and the `trailing` query convention are read
  from `basis_v4.run_program` but not exercised.
- **Budgets.** Every core-h figure in s4 is a planning guess, scaled from W5P / W9-H pilot timings. None is
  measured for TFS-1.
- **External dependency.** Availability and Windows conformance of a Stitch implementation (`stitch_core`) is
  UNVERIFIED.
