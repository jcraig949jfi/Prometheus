# RB-6 DELIVERABLE 1 -- IMPROVER PARAMETER INVENTORY

Seat: Aphrodite (RB-6 worker). Written 2026-09-27. Plain ASCII.
Status: research background for a SEPARATE FUTURE PROGRAM ("improvement of the improver",
V5). Per the operator's ruling it is NOT part of the current abstraction-compounding
experiments. Nothing here is a disposition, and no frozen or engine file was modified.

Source of truth read for this inventory:
  engine/a17.py      donor(), certified_classes(), members_in(), coverage(), select(),
                     candidates_from(), schema_entry(), constants R_OBS/R_VAL/ESCROW/MAX_HITS
  engine/tier3d.py   lgg(), derive_schemas(), schema_src(), instantiate(), in_space_body()
  engine/fair.py     KLib (keyed walk order + full G4 fallback), search_collect(), Cell,
                     paired_summary(), LEVEL1, expand_schema()
  engine/cert.py / identity.py (behavior_id, normalise R2-R4, B1 battery) by reference.

## 0. The fixed improver, as a pipeline of decisions

    start library S (PRISTINE or L1)
      |  OBSERVE: for each OBSERVE family, R_OBS=3 cells, search S with escrow 250k,
      |           keep the FIRST dev-consistent hit (max_hits=1)
      v
    observed programs --(behavior_id bucketing; members_in(coverage(S)); cert.certify;
      |                  split failed buckets by value vector on B1+b_cert+adversarial)
      v
    certified classes, each with member_bodies
      |  DERIVE: tier3d.derive_schemas -- LGG of every body pair from DISTINCT classes,
      |          keep exactly-1-hole, non-root; dedupe by source string
      v
    candidate schemas --(instantiate: LEVEL1 fillers, in-space rule)--> bodies
      |  CANDIDATE LIBRARIES: INHERITED, MEMORISE, SCHEMA_k (one per schema, prepended
      |  to S), SCHEMA_ALL (union, if >1 schema)
      v
    SELECT: cost of each library on R_VAL=8 cells x each VALIDATE family (first-hit
      charges, censored at escrow); paired saving vs INHERITED; eligible iff one-sided
      95% lower bound > 0; argmax mean saving; ties -> smaller size -> sha256
      v
    selected library (the donor's product, inherited by recipients)

Every box above hides decisions that are CODE today but could be DATA. The table below
lists them. "Endogenous?" asks whether a donor's own products (its trace: observed
classes, candidate schemas, selection table, selected library, charges) could plausibly
set the parameter for the NEXT donor, i.e. whether the parameter is a candidate site for
L2 improvement. "Expected effect" is a HYPOTHESIS with its reasoning, not a measurement,
unless it cites the RB-6 lever check (rb6_lever_check.py, RB6_LEVER_CHECK_*.json).

Legend for effect size: NONE / SMALL / MEDIUM / LARGE on (a) WHICH schema is selected
and (b) downstream V1-V4. "Degenerate" = the parameter has a setting that trivially
wins on the selection metric while destroying the program's meaning (a smuggling or
hacking channel).

## 1. Observation stage

P1  Observe cells per family (R_OBS = 3)
    Controls: how many independent solutions per family enter classing; with max_hits=1
      each cell contributes one program, usually the FIRST in keyed walk order, so
      replicate cells often return the same body.
    Alternatives: 1..8; or adaptive (stop a family when two cells agree on a class).
    Endogenous: YES, weakly -- "observe more cells for families whose classes failed
      certification last generation" is computable from the trace (class_certificates).
    Effect: SMALL on selection. The class set is a function of families, not cells, for
      bounded folds; more cells mostly re-find the same class. Cost is linear.

P2  Hits kept per observe cell (max_hits = 1)
    Controls: the diversity of observed programs within a behaviour class. Because
      member enumeration (members_in) later recovers ALL class members inside coverage,
      extra hits add information only if they lie OUTSIDE coverage (in the G4 fallback).
    Alternatives: 1, 2, 5 (MAX_HITS=5 is used by recipients already).
    Endogenous: YES -- "raise max_hits when the last selected schema came from a fallback
      hit" is trace-computable.
    Effect: SMALL-MEDIUM. The main channel by which fallback bodies (outside S's span)
      enter the LGG corpus. This is one of few ways to see beyond the library.

P3  Observe escrow (ESCROW = 250,000, shared constant with recipients and selection)
    Controls: which families get ANY observed program. K4: PRISTINE needs 8x-3,527x more
      charges for G1-span families, so the escrow is exactly the gate that turns
      "budget-infeasible" into "unobserved".
    Alternatives: 50k .. 12M. Separating observe escrow from selection escrow.
    Endogenous: YES -- set the observe budget from the charge distribution of last
      generation's solutions (e.g. 2x the 90th percentile).
    Effect: MEDIUM-LARGE on which classes exist, therefore on candidates. Degenerate
      direction: a huge escrow makes the library irrelevant (the fallback finds all),
      which is the V1/V2 confound K4 already documents. Must be held fixed in any V5 test
      or charged to the improver's cost.

P4  Which families are OBSERVE vs VALIDATE (role split; catalog-level)
    Controls: the supply seen by derivation vs the supply that judges it.
    Alternatives: random split; curriculum (observe families the current library FAILS,
      STP "push toward unsolved"); observe-all + cross-validation.
    Endogenous: YES in principle (task choice = the field's endogenous curriculum), but
      this is TASK SUPPLY, not the improver. In a V5 program it must be FIXED by the
      protocol, otherwise V5 is confounded with curriculum learning (see program doc s5).
    Effect: LARGE (K5: supply regime moved compounding from 0/6 to 5/6). Excluded from the
      improver's editable set by design.

## 2. Classing / certification stage

P5  Semantic equivalence key (identity.behavior_id on B1, trailing convention)
    Controls: which observed programs are "the same" whole-program class. E4 showed whole-
      program classing is NECESSARY for derivation under compensating factorisations.
    Alternatives: body-only key (structural), extensional key on the task domain (RB-1's
      domain-grounded ruler), coarser keys (value on fewer probes), babble-style
      rewrite-modulo-theory keys.
    Endogenous: PARTLY -- the probe battery could be extended by adversarial inputs that
      split last generation's failed certificates (cert.adversarial already does this per
      bucket). A persistent, accumulated adversarial probe set is a genuine L2 object
      (the improver's evaluator improves), analogous to RQGM.
    Effect: MEDIUM. Coarser keys merge classes -> fewer distinct-class pairs -> fewer
      LGGs; finer keys split -> more pairs, more candidates, more selection cost.
      Degenerate direction: a key so coarse all programs are one class yields ZERO pairs
      (derive_schemas only pairs DISTINCT classes).

P6  Certification battery (cert.certify + B1 + b_cert + adversarial; split on failure)
    Controls: whether a bucket stays one class or is split by value vectors.
    Alternatives: stricter/looser battery; skip certification (trust behavior_id).
    Endogenous: YES (as P5: accumulate splitting probes from traces).
    Effect: SMALL in the current world (K-spikes: few certificate failures on the
      commutative bounded-fold world); could matter in RB-2/RB-5 worlds.

P7  Member space for class enumeration (coverage(S): every init x body x final in the
    library entries; NOT the fallback)
    Controls: the bodies each class contributes to LGG. This is THE mechanism by which an
      inherited library changes derivation (K3: 467 = 467 NEW -> inheritance adds no new
      derivable novel schema; K8: composition adds 77).
    Alternatives: coverage(S) (now); coverage(PRISTINE) fixed; coverage(S) + composition
      closure (RB-3 wrap(S, op, atom)); a bounded sample of the G4 fallback.
    Endogenous: YES -- this is the natural L1->L2 coupling: "enumerate members in the
      span of the last selected schema plus its one-step compositions". Note: under the
      current code it is ALREADY endogenous (coverage of the inherited library), which is
      why K5 donors compound; what is not endogenous is the RULE (coverage only, no
      composition, no fallback).
    Effect: LARGE (K8 is the evidence: composition changes the derivable universe; K3:
      coverage alone does not add novelty). Most promising lever; overlaps RB-3, which
      must run first (the operator ruled that composition belongs to the compounding
      program, not to V5).

## 3. Derivation stage (LGG)

P8  Hole count (exactly 1 hole)
    Controls: schema generality. 1-hole schemas are "acc + {H}"-like; 2-hole schemas
      ("(acc + gcd({H0}, {H1}))", "({H0} + {H1})") are strictly more general
      anti-unifiers; the in-space filler rule (LEVEL1 fillers; depth-2 bodies) limits a
      hole at depth 2 to atoms.
    Alternatives: 1, <=2, exactly 2, <=k with an MDL penalty; Stitch/babble-style
      "abstraction with arity k".
    Endogenous: YES -- "use the hole count that produced the last selected schema" or a
      bandit over hole counts rewarded by selection savings (the parameter is a small
      discrete arm; trace records which arity won).
    Effect: HYPOTHESIS MEDIUM on candidates, SMALL on selection. More holes -> larger
      instantiation sets -> larger library entries walked before the fallback -> higher
      first-hit cost unless the extra bodies are the ones needed. Paired-saving
      selection should usually reject over-general schemas (they approach "PRISTINE
      again"). See the lever check for the measured spread.

P9  Root-hole exclusion ("non-root") and exactly-one-hole-TABLE semantics
    Controls: excludes the trivial "{H}" schema; the same differing subterm pair maps to
    the same hole (first-order LGG with shared variables).
    Alternatives: allow distinct holes for repeated differing pairs; allow root-level
      schemas with a guard.
    Endogenous: NO plausible product-driven setting; a design invariant.
    Effect: SMALL; keep fixed.

P10 Class pairing rule (every pair of DISTINCT classes; every member-body pair)
    Controls: which LGGs are computed. Same-class pairs are excluded (they would yield
      schemas describing ONE behaviour, i.e. compression of a class, not
      generalisation across classes).
    Alternatives: (a) include same-class pairs; (b) only pairs of classes from DIFFERENT
      families; (c) only pairs whose LGG is supported by >= m pairs (support threshold);
      (d) weight pairs by class charges (pair expensive classes first -- the classes the
      current library solves worst).
    Endogenous: YES for (c)/(d): support threshold and charge weighting are set by trace
      statistics (n_pairs; observed charges).
    Effect: HYPOTHESIS SMALL-MEDIUM. (a) adds many near-duplicate schemas; (c) prunes
      candidates cheaply (selection cost is dominated by the number of candidate
      libraries x validation cells); (d) is the most "improver-like": it redirects
      derivation to where the library is weakest (STP push-toward-unsolved, inside the
      improver rather than the curriculum).

P11 Normalisation before LGG (identity.normalise R2-R4: commutative sort, neutral,
    absorbing)
    Controls: which syntactic variants anti-unify. babble shows LGG modulo an equational
      theory finds abstractions that syntactic LGG misses.
    Alternatives: no normalisation; R2 only; richer theory (distributivity, associativity
      flattening, e-graph anti-unification).
    Endogenous: YES in principle -- a learned set of rewrite rules certified by the
      tribunal (DreamCoder/babble analogue). This is the strongest "improver object" that
      is not a scalar knob, and the one the prior-art raid (C1) singles out.
    Effect: HYPOTHESIS MEDIUM, but LARGE engineering cost (a certified rewrite must
      preserve value AND failure disposition on every input; identity.py already carries
      that discipline for R2-R4).

P12 Instantiation rule (LEVEL1 fillers, in-space structural match via in_space_body)
    Controls: which bodies a schema contributes. A schema's value depends only on its
      in-space instantiations; a schema with < 2 in-space instantiations is useless.
    Alternatives: fillers from coverage bodies' subterms (data-driven fillers); fillers
      weighted by frequency in observed programs; bounded-depth fillers.
    Endogenous: YES -- "filler vocabulary = subterms of last generation's solutions" is a
      DreamCoder-style learned proposal distribution restricted to this DSL.
    Effect: HYPOTHESIS MEDIUM on V1 (entry size and order), NONE on the derivable set.

## 4. Candidate-library construction

P13 Candidate set: INHERITED, MEMORISE, SCHEMA_k, SCHEMA_ALL
    Controls: the menu the selector chooses from. MEMORISE is a control candidate (union of
      member bodies) that wins often in K5 (it is an unabstracted cache).
    Alternatives: drop MEMORISE; add pairwise unions SCHEMA_{i,j}; add
      SCHEMA_k + MEMORISE; top-m by support.
    Endogenous: YES -- e.g. "include SCHEMA_ALL only if the last selection was an ALL".
    Effect: MEDIUM on which product is selected (K5: MEMORISE selected in 17/36 donors);
      small on V3/V4 because MEMORISE carries no schema.

P14 Insertion position of the new entry (prepended: [new] + S)
    Controls: the new entry is walked FIRST; the old library is kept behind it.
    Alternatives: append; replace the entry that the schema generalises; interleave;
      drop entries whose coverage is subsumed.
    Endogenous: YES -- "insert before the entry that produced the witnesses" is
      trace-computable.
    Effect: MEDIUM on V1. Order is everything in a first-hit charge metric: K4 showed G1's
      whole benefit is ordering. A replace-vs-prepend policy decides whether libraries
      grow monotonically (bloat, the "architectural bloat" failure) or refine.

P15 Entry shape (inits = H1 {0,1}; finals = all 180)
    Controls: a schema entry costs 2 x |inst| x 180 before anything else is walked.
    Alternatives: finals restricted to those observed with the schema's witnesses;
      inits restricted likewise.
    Endogenous: YES -- "finals = finals seen in observed programs of the witness classes".
    Effect: HYPOTHESIS LARGE on V1 (a factor up to 180 in entry size), NONE on the
      derivable set. The most obvious cheap efficiency lever; also the most obvious
      OVERFITTING lever (finals are family-specific; a finals-restricted entry transfers
      worse). Must be judged on transfer, not on selection cells.

## 5. Library walk order (search)

P16 Within-entry order (fair.keyed: sha256 of (cell seed, slot, item); library-blind)
    Controls: the order inits/bodies/finals are tried; deliberately a function of the
      cell only (AMENDMENT 13 fairness: byte-identical libraries walk identically).
    Alternatives: learned order (by frequency of use in past solutions -- a DreamCoder
      recognition-model analogue), size-first, MDL order.
    Endogenous: YES, and it is the most natural L2 object for a search-based improver
      (prior-art C2: "a learned ordering over inits x bodies x finals").
      CAUTION: changing it breaks the common-random-numbers fairness of paired
      comparisons unless the order is a fixed function frozen BEFORE the paired cells
      (freeze-then-evaluate).
    Effect: HYPOTHESIS LARGE on V1 (G1's measured value is essentially an order effect,
      median ~300x). NONE on V2 at unlimited budget. Therefore a V5 claim resting on this
      parameter would be a pure efficiency (V1) claim one level up.

P17 Between-entry order (list order of entries) and fallback order (keyed G4, finals-only
    'expr' programs first)
    Controls: as P14/P16. The fallback guarantees identical expressive power.
    Alternatives: interleaving library and fallback (P18).
    Endogenous: YES (as P14).
    Effect: as P14.

## 6. Escrow split

P18 Escrow split between library and fallback (today: none -- the library is walked to
    exhaustion, then the fallback, under one 250k escrow)
    Controls: how much of the budget a large library can consume before the fallback
      starts. A big schema entry can starve the fallback (K2: L1 slightly WORSE than
      PRISTINE on gcd families = "escrow overhead").
    Alternatives: fixed fraction (e.g. library <= 50%); interleaving (dovetailing: k
      library candidates per fallback candidate); Levin-search-style allocation by
      description length.
    Endogenous: YES -- set the fraction from the last generation's share of solutions
      found in library vs fallback (trace: coordinate of each hit).
    Effect: HYPOTHESIS MEDIUM on V1 for out-of-span families (removes the overhead), SMALL
      in-span. It converts the library from a hard prefix into a prior, which is what
      the literature's successful systems do.

## 7. Selection stage

P19 Selection statistic (mean paired saving vs INHERITED on R_VAL x |VALIDATE| cells)
    Controls: what counts as "better". Censoring at escrow makes it a truncated mean.
    Alternatives: median; win-rate; log-charge mean (scale-free, less dominated by one
      censored cell); CMP-like 2-generation score (how productive the candidate's
      descendants are); transfer-proxy (saving on an extra held-out family).
    Endogenous: PARTLY -- a statistic cannot be chosen by the product it judges without a
      regress; but a bandit over statistics rewarded by NEXT-generation outcomes is an
      L2 mechanism (it is how HGM's CMP improves on DGM's performance selector).
    Effect: HYPOTHESIS SMALL-MEDIUM on which candidate wins among eligible ones; HGM
      reports selector choice changes descendant productivity materially (correlations
      0.285-0.444 vs 0.778, PARTIAL), but Aphrodite's candidate menus are small (2-9),
      which bounds the effect. See lever check V2_LOOK / V3_MEDIAN.

P20 Eligibility gate (one-sided 95% lower bound > 0; se from n cells)
    Controls: the default to INHERITED when evidence is weak.
    Alternatives: 80%/99% gates; Bonferroni over candidates (currently NO multiplicity
      correction: with 9 candidates the family-wise false-eligibility rate is well above
      5%); sequential testing.
    Endogenous: NO (a statistical-hygiene constant; must be fixed by preregistration).
    Effect: MEDIUM on the frequency of "no change" outcomes.

P21 Validation cells (R_VAL = 8 per VALIDATE family; labels; seeds)
    Controls: selection noise (prior-art C11 / "Simple Baselines": small validation sets
      pick wrong candidates).
    Alternatives: 4-32.
    Endogenous: NO (a sample-size constant).
    Effect: MEDIUM on selection STABILITY (not on the expected choice).

P22 Tie-break (size, then sha256)
    Controls: prefers smaller libraries on equal saving.
    Endogenous: NO. Effect: NONE-SMALL.

## 8. Composition move (not in a17; RB-3 / K8)

P23 Composition operator wrap(S, op, atom) applied to the inherited schema before
    member enumeration / derivation
    Controls: whether G1-dependent schemas (G1 used as a SUBTERM) are accessible.
    Alternatives: OFF (today); wrap with LEVEL1 atoms; wrap with the last selected schema
      only; DreamCoder-style promotion of a schema to a primitive.
    Endogenous: YES by construction (it composes the donor's own products).
    Effect: LARGE on the derivable universe (K8: +77 G1-composing schemas, 134 fresh).
    Ownership: per the operator's ruling this belongs to the COMPOUNDING program (RB-3).
    In a V5 program it would be a candidate "improver edit" only AFTER RB-3 has measured
    it as a fixed option; otherwise V5 would re-discover RB-3's result and call it L2.

## 9. Summary table

| id  | parameter                         | endogenous? | hypothesised effect | V5 status              |
|-----|-----------------------------------|-------------|---------------------|------------------------|
| P1  | observe cells R_OBS               | weak        | SMALL               | editable, low value    |
| P2  | hits per observe cell             | yes         | SMALL-MED           | editable               |
| P3  | observe escrow                    | yes         | MED-LARGE, degen.   | FIX (confound w/ budget)|
| P4  | observe/validate role split       | yes         | LARGE               | FIX (task supply)      |
| P5  | equivalence key                   | partly      | MEDIUM, degen.      | editable (probe set)   |
| P6  | certification battery             | yes         | SMALL now           | editable               |
| P7  | member space for classing         | yes         | LARGE               | after RB-3             |
| P8  | LGG hole count                    | yes         | MED cand / SMALL sel| editable (lever check) |
| P9  | root/shared-hole semantics        | no          | SMALL               | FIX                    |
| P10 | class pairing rule                | yes (c,d)   | SMALL-MED           | editable               |
| P11 | normalisation theory before LGG   | yes         | MEDIUM, costly      | editable (rewrite set) |
| P12 | filler vocabulary                 | yes         | MED on V1           | editable               |
| P13 | candidate menu                    | yes         | MEDIUM              | editable               |
| P14 | insertion position                | yes         | MED on V1           | editable               |
| P15 | entry shape (finals/inits)        | yes         | LARGE on V1, overfit| editable, transfer-judged|
| P16 | within-entry walk order           | yes         | LARGE on V1         | editable, freeze first |
| P17 | between-entry / fallback order    | yes         | as P14              | editable               |
| P18 | escrow split lib/fallback         | yes         | MED on V1           | editable               |
| P19 | selection statistic               | partly      | SMALL-MED           | editable (bandit)      |
| P20 | eligibility gate                  | no          | MEDIUM              | FIX (prereg)           |
| P21 | validation cells                  | no          | MED (stability)     | FIX                    |
| P22 | tie-break                         | no          | NONE                | FIX                    |
| P23 | composition move                  | yes         | LARGE               | RB-3 first             |

## 10. Reading of the inventory

1. The improver has ~15 genuinely editable, trace-settable parameters. A V5 program is
   therefore not blocked by the absence of levers in the CODE. Whether the levers matter
   in THIS DSL is an empirical question (the lever check).
2. The levers with the largest hypothesised effects split into two groups:
   (a) efficiency levers (P14-P18: order, entry shape, escrow split). These can only
       produce a V1 improvement one level up. A V5 positive built on them would be
       "the improver learned to order its search better", which is real but is exactly
       the sharpening signature (K4) moved up a level.
   (b) access levers (P7, P11, P23: member space, rewrite theory, composition). These can
       change the DERIVABLE UNIVERSE and are the only route to a V5 effect on V3/V4.
       P7/P23 are owned by RB-3 (compounding program) and must be settled there first.
3. Three parameters must be FIXED by protocol because editing them is either a confound
   or a hacking channel: P3 (observe escrow: buys capability with budget), P4 (task
   split: turns V5 into curriculum learning), P20/P21 (statistical gate and sample
   size: a self-edited gate can always lower itself).
