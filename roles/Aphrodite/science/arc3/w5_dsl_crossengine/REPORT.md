# ARC3 / W5 -- DSL-EXTENSION COST/BENEFIT MAP + CROSS-ENGINE MINING
(Deposited verbatim by the principal from worker W5's final message; the harness
blocked the worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W5.)

Worker W5 for the Aphrodite seat. Label APHRODITE/ARC3/W5/v1. Date 2026-09-28.

This report is forensic, not a disposition. No engine file was modified, and nothing
here is Campaign 1 evidence. The DSL extension is PARKED by the operator: this report
characterises the candidates and does not adopt any.

## Files in this directory
- `xdsl.py`: a MODIFIED COPY of the fold evaluator. It adds:
  - lag registers p (previous v) and q (previous acc);
  - an index atom i, where i = n in the final;
  - integer literals 2..9;
  - max/min operators;
  - symmetric templates.

  It carries T4's family_profile logic verbatim. On G4 witnesses it agrees with
  `tribunal_t4.family_profile` 60/60, and it reproduces the G4 grammar exactly.
- `probes.py`: probes P1-P4.
- Outputs: `W5_PROBES_p1_p4.json`, `W5_PROBES_p2.json`, `W5_PROBES_p3.json`, `P2.log`,
  `P3.log`.

## PART 1 -- DSL EXTENSION MAP

### P1. Search-space sizes

PRISTINE = 2 x H2 x finals. The escrow is 250,000.

| Variant | Bodies | Inits | Finals | G1 fillers | H2 | PRISTINE | Fits escrow |
|---|---|---|---|---|---|---|---|
| G4 | 10,842 | 116 | 180 | 258 | 422 | 151,920 | yes |
| Literals 2..9 | 135,842 | 1,020 | 1,196 | 1,386 | 49,710 | 118.9M | no (476x) |
| Lag p (previous v) | 17,157 | 116 | 258 | 350 | 1,389 | 716,724 | no |
| Lag q (previous acc) | 17,157 | 116 | 258 | 350 | 1,389 | 716,724 | no |
| Index i | 17,157 | 116 | 258 | 350 | 1,389 | 716,724 | no |
| Symmetric depth 2 | 465,954 | 116 | 180 | 258 | 6,302 | 2.27M | no |
| max/min | 17,826 | 148 | 230 | 330 | 686 | 315,560 | no |

The G1 fillers column counts raw fillers.

### P2. Degeneracy census

Method:
- For each variant, up to 600 new bodies that mention acc and v were each given an H1
  init and a G4 final mentioning acc.
- Each resulting program was profiled with the T4 logic.
- "Extensionally new" means the accumulator behaviour (final = acc) differs from every
  G4 body with the same init.
- "Affine" means the family equals c x (a G4 family) + g(length, first, m).

| Variant | n | T4-admissible | Perm-invariant (admissible) | Ext-new (all) | Admissible & ext-new | Of which affine | Net novel admissible |
|---|---|---|---|---|---|---|---|
| G4 (control) | 600 | 10.7% | 0.61 | 0% | 0 | 0 | 0 |
| Literals | 600 | 14.2% | 0.47 | 58% | 76 | 16 | 60 (10.0%) |
| Lag p | 294* | 12.2% | 0.00 | 45% | 36 | 0 | 36 (12.2%) |
| Lag q | 294* | 9.2% | 0.00 | 31% | 27 | 0 | 27 (9.2%) |
| Index i | 294* | 12.6% | 0.16 | 63% | 37 | 9 | 28 (9.5%) |
| Symmetric | 600 | 6.7% | 0.45 | 25% | 18 | 6 | 12 (2.0%) |
| max/min | 600 | 7.5% | 0.76 | 34% | 29 | 3 | 26 (4.3%) |

\* This is the whole pool: at depth 2 with left-atom templates, only 294 new bodies
mention acc and v.

The rejection reasons rank the same way in every variant: MIDDLE_INSENSITIVE, then
LAST_INSENSITIVE, then CONSTANT.

Targeted cases:
- **Rejected:** the telescoping sum of (v - p), and the length-only acc + i.
- **Admitted:**
  - the sum of v*p;
  - the sum of i*v;
  - (v + 7*acc) % m;
  - the sum of 3v, which is a G1 instance.

T4 does not catch affine copies, and it does not catch growth of G1's coverage.

Lag registers make every admissible family order-sensitive (0/63 are
permutation-invariant). The old MetaTribunal therefore becomes unusable for them.

### P3. EC polynomial ladder (symbolic)

Each cell gives QUAD_COMPLEX / QUAD_COEF_GT1 counts, out of 729 / 512.

| Template | SUM | ORBIT | SUM QUAD (of 900) | SUM LINEAR (of 90) |
|---|---|---|---|---|
| Left-atom depth 2 (G4) | 0/0 | 0/0 | 2 | 5 |
| Left-atom depth 3 (G5/W5) | 0/0 | 0/0 | 7 | 11 |
| Symmetric depth 2 | 0/0 | 0/0 | 6 | 11 |
| Symmetric depth 3 | 50/27 | 26/3 | 107 | 41 |
| Left-atom + literals, depth 2 | 0/0 | 0/0 | 9 | 32 |
| Left-atom + literals, depth 3 | 0/0 | 0/0 | 55 | 90 |
| Symmetric + literals, depth 2 | 0/0 | 0/0 | 41 | 90 |
| Symmetric + literals, depth 3 | 729/512 | 729/512 | 900 | 90 |

The effect is strongly super-additive; Aether's "one change at a time hides
interactions" lesson applies. An example witness: ((acc + 7) + (8*v)) + (9*(v*v)).

### P4. OEIS LINREC with a lag register

- The canonical witness is init 0, body v, and a final that applies the recurrence to v,
  p and literals.
- It is verified on all listed terms for 102/102 order-1 and order-2 sequences, but T4
  admits 0/102.
- Only 11/102 fit in a depth-1 final.
- The 48 order-3 sequences need two lag registers.

### Assessment by extension

**(i) Literals / constant hole**
- **(a) Families gained:** EC CONST and LINEAR become complete at depth 3, but QUAD
  reaches only 55/900 without symmetric templates. OEIS gains nothing. The natural world
  gains affine and Horner families.
- **(b) Degeneracies:** about 21% of novel admissible families are affine copies of G4
  families. G1's fillers grow 5.4x. There is no detectable trivial-family excess
  (admissibility 14.2% vs 10.7%).
- **(c) Comparability:** this is the worst break of the five. In H2 or the finals,
  PRISTINE grows 780x, so charges, savings, Q2 (whose reachable set is PRISTINE), T31,
  the 16% base rate and every gate must be re-derived. Only a single declared
  constant-hole slot keeps PRISTINE intact.
- **(d) Science:** coverage and parameterisation. There is no new state and no new kind
  of abstraction.
- **Trigger:** both conditions must hold:
  1. a reuse-controlled positive;
  2. a census showing at least 25% of unsolved transfer and validation families have a
     witness within one composition move only once a literal is added.

  Then adopt it as a declared hole, never as free atoms.

**(ii) Lag register / second accumulator**
- **(a) Families gained:** OEIS order-2 becomes 81/81 expressible but 0 admissible. The
  real gain is input-driven order-2 dynamics; 9-12% of new bodies are novel and
  admissible.
- **(b) Degeneracies:** telescoping, which T4 catches. Every admissible family is
  order-sensitive.
- **(c) Comparability:**
  - The evaluator signature changes (T4.run, fasteval, the 288k-pair and 400-pair
    gates).
  - The ruler v2 grid covers only (acc, v, first, last), so fclass, conjugates and
    re-expressions are undefined for p and q.
  - K7 and cert.py need redefining.
  - PRISTINE grows 4.7x.
- **(d) Science:** this changes the science. It adds a second state dimension and
  schemas such as (acc + (q + {H})), and raises a new question: compounding from order 1
  to order 2.
- **Trigger:** only as a separately preregistered question, after an order-1 mechanism
  positive. Never because of OEIS.

**(iii-a) Index atom**
- **(a) Families gained:** position-weighted folds. In the final, i = n supplies the c*n
  constant term.
- **(b) Degeneracies:** length-only families are caught. Length offsets are not (24% of
  novel admissible families).
- **(c) Comparability:** the same breaks as the lag register.
- **(d) Science:** modest; it is a register with fixed dynamics.
- **Trigger:** never alone. Include it with (ii) only if an affine screen is added to the
  ruler.

**(iii-b) Symmetric templates**
- **(a) Families gained:** the biggest EC lever (100% with literals). In the natural world
  it is the weakest: 2.0% net novel admissible.
- **(b) Degeneracies:** 75% of new bodies are extensional duplicates.
- **(c) Comparability:** the fallback grows 43x, and the templates overlap the
  composition move.
- **(d) Science:** it moves the line between "primitive" and "composition", which
  changes the A18/A19 treatment.
- **Trigger:** only if a static census of A19 supply files shows that witnesses fail
  specifically for lack of compound left operands. Even then, prefer extending the
  composition move.

**(iv) max/min**
- **(a) Families gained:** mostly more commutative-monoid families (76%
  permutation-invariant).
- **(b) Degeneracies:** fixed-point dynamics rise (272/600 vs 220/600).
- **(c) Comparability:** PRISTINE grows 2.1x.
- **(d) Science:** coverage only.
- **Trigger:** none.

**Placement rule.** If anything is ever adopted, give it its own declared slot and keep
H1, H2 and FINAL as in G4. `fair.keyed` sorts by a per-item hash, so the relative order
of G4 items is preserved. PRISTINE-solved charges then stay bit-identical, and only
fallback-derived results (including CON1's ">= 190x") are re-based.

## PART 2 -- CROSS-ENGINE MINING

ARC3 Block A (`arc3/con1/con1_forensics.py`) already runs the direct CON1 controls, so
they are not repeated here: an alias library (G2_ONLY), SHAM0, and (v - {H}). The paths
below are under `C:\Prometheus\` and were read without modification.

**NESTOR**
- **Sources:** `roles/Nestor/FINDINGS.md` E-8 (13/40 vs 0/40, p = 3.8e-5);
  `roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md` (1/64 to 39/64;
  the capability was present in 87/96 populations; "discoverability is set by encoding
  length").
- **Hypothesis:** "reuse" is a one-move composition horizon; transfer families sit two
  wraps from G1.
- **Test (static):** compute the minimum wrap distance from G1 and from each sham to an
  extensionally equivalent schema, for every A19 transfer and validation family.
  - Mostly distance 2, with shared ancestors: a horizon.
  - Distance 3 or more: the reuse scarcity is real.

**ANANKE**
- **Sources:** `roles/Ananke/research/SYNTHESIS_2026-09-28_ARC2.md` ("14/14 JOINT cells
  are per-trial PHASE MIXTURES"); `roles/Ananke/research/workers/W-F/REPORT.md` ("at a
  fixed physics point the carrier is NOT fixed").
- **Hypothesis:** CON1's "reused composition" is a mixture of different (init, H, final)
  choices per cell, matched extensionally.
- **Test:** log the fillers of the 16 solves, then rerun with the entry restricted to the
  most frequent filler.
  - Solves survive: one abstraction.
  - Solves collapse: a mixture.

**ARCHAEON**
- **Sources:** `archaeon/causal_lens/FALSE_FRIENDS.md` FF-1 (the parent-chain view
  credits hosts 8-42x more than the genetic view); `archaeon/campaign3/CAMPAIGN_REPORT.md`
  (permuted imports took over 12/12 vs 12/12).
- **Hypothesis:** G1's credit is provenance; any broad inner schema wrapped by
  (v - ...) works.
- **Test (static):** apply the same wrap to the size-matched schemas in the A19 candidate
  pool and count how many cover CON1's two transfer families.
  - Many do: CON1 is not G1-specific.
  - Only G1 and its re-expressions do: the credit is causal.

**AETHER**
- **Sources:** `Aether/AETH-03/RCV_REINTERPRETATION_2026-09-27.md` ("executes a frozen
  map", Jaccard 1.0 in 24/24); `Aether/pivot/AETHER_REVIEW_2026-09-27.md` ("lacks
  PROPAGATION"); `Aether/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md` (the one-change
  rule hid interactions).
- **Hypothesis:** the library is executed but never reorganised, so the G1 footprint does
  not grow past generation 1.
- **Test:** twin G1-present/absent lineages over 2-3 donor generations, measuring per
  generation the difference in selected schemas and solved cells.
  - The footprint grows: reuse is the limit.
  - It stays flat: there is no propagation, and a reuse-controlled supply would not fix
    it.
- The interaction half of Aether's lesson is already confirmed by P3.

**CRIUS**
- **Source:** `crius/CRIUS_C2_TERMINAL_REVIEW.md`:
  - existence: 46.1 vs 20.7; transplant 6/6/6;
  - access: 0/36 searches reached the capability;
  - priced partials: -0.001 / -0.002 / +1.138 / +15.974;
  - selection kept "generic scaffolding, never their typed links".
- **Hypothesis:** a reusable composition exists, but paired validation selection prefers
  a family-specific one. That would be a valley in selection, not scarcity in the world.
- **Test:** find the composition covering the most transfer families in each replicate,
  and price it on the frozen validation cells with `a18.fast_cost`.
  - It exists but loses: fix the selection objective.
  - It is absent: the bottleneck stands.

**Not supported:** "everything is accessibility". Aether's deficit is physics. Nestor's
next barrier was carried state ("self-poisoning"). Archaeon C5 changed the representation
and gained 0/96.

## EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION

1. **The recorded ordering of extensions is refuted.** The new-lens ordering (literals
   first; "with (i) alone the EC ladder becomes a graded supply") is contradicted: with
   literals alone, W5 gets 0/729 and 0/512 on EC's hard tiers. Symmetric templates alone
   do more, and only the combination reaches 100%.
2. **"Extend the DSL = cleanest non-smuggled route" (synthesis s6) is overstated.**
   - SUM-EC is G1's span by construction.
   - ORBIT is our own mapping.
   - OEIS is 0/102 admissible even with a lag register.
3. **"Reuse is the bottleneck" has three unexcluded rivals:** a composition horizon,
   selection preferring family-specific compositions, and a non-specific inner schema.
   Each has a static or cheap test, and each should run before the reuse-controlled
   assay.
4. **CON1's ">= 190x" and "10M" are properties of the escrow structure.** PRISTINE fills
   61% of the escrow. Beyond it, the search walks only a hash-ordered slice of a fallback
   of at least 226M programs. Any extension re-bases these numbers.
5. **The feared degeneracies are handled by T4; the unhandled problem is affine copies.**
   They make up 21-24% of novel admissible literal and index families, which compounds
   the existing 16% chance-novelty problem.

## CAVEATS

- P3 is exact only for the polynomial fragment and is a lower bound otherwise.
  - The SUM counts match RB-5 exactly.
  - The ORBIT counts differ from RB-5 by +/-1, because RB-5 used holdout/CEIL checks and
    all inits and finals.
- P2's "extensionally new" is measured against G4 only, at the accumulator level.
- Q2 and solvability were not measured for the extended families.
- The lag semantics are one choice among several: registers start at 0, and the final
  sees p as the second-to-last element.
- None of the Part 2 tests was run; each is only proposed.
