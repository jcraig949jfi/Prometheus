# Assessment of the Chopper after the Lean/mathlib simp proving specimen

Date 2026-09-11. Subject: Nyx, not Lean. Every number below is copied from
`python -m nyx.chop.cutledger nyx/specimens/lean_simp/cuts.json` at commit
1a54d02d2, or from a committed receipt named beside it. The metric
definitions were fixed in PREREG_CUT1.md s3 BEFORE CUT-1; where a metric
turned out defective the defect is reported, the metric is not repaired
here.

## The Phase V measurements

inherited-boundary rate (by cut of introduction)
    CUT-1  20/23 = 0.87     CUT-2  2/4 = 0.50     CUT-3  0/2 = 0.00
    Reading: the knife followed def/file names on the first pass; the two
    CUT-3 boundaries were both found by an intervention (PERTURBED) and
    neither coincides with anything in the Simp directory.

cut survival
    ORGAN count      8 -> 5 -> 4
    same-kind survival, all live candidates   CUT-1->2: 15/22 = 0.68
                                              CUT-2->3: 25/26 = 0.96
    kind changes 7 then 1; split products 8 then 0; new candidates 4 then 2
    record bytes 49,587 -> 37,720 (-24%) -> 32,206 (-15%)
    VERBOSITY_FAILURE false at both transitions

consumer rejection / revision rate
    deliveries 2 (#175 Vivarium, #176 Archaeon, 20:53Z); substantive
    returns 0; rate undefined. Vivarium has never booted in comms; six
    Nyx pressures are queued there unseen (#44, #52, #175 x4).

fields initially unknown that became measurable
    ledger metric: 0 (unknown_became_known). DEFECTIVE for this specimen:
    CUT-1 wrote zero literal unknowns (O2), so nothing could be counted as
    becoming known. Literal-unknown fields: 0 -> 12 -> 10.
    What actually moved, outside the metric: c01.ablation gained a
    receipt-backed number (33.8% non-Eq in a seeded 400-site census,
    simp_shape_census_2026-09-11.json; text method, T3 as a shape
    estimate). One field.

organs whose behaviour can be tested independently of the ancestor
    run 0 / specified 4 / none 0. Every execution in CUT-3 ran INSIDE the
    ancestor (its own config switches). Nothing was shown to work without
    Lean. Ancestor-free contract ASSERTED for 3 of 4 (c01 c02 c06); not
    demonstrated for any.

pressures Vivarium can operationalize without receiving the organ
    0 returns; 4 delivered + 1 held (mutual_normalisation) + 1 candidate
    not written (c14 memo validity). expressible_without_organ = true
    asserted by Nyx on all five; unverified.

cheat controls that actually fire
    declared 9; fired 1 (D3 planted loop -> "maximum number of steps
    exceeded"); did not fire 1 (c23 negative control -- the most
    informative event of the trial); not run 7.

decomposition ambiguities still unresolved
    UNRESOLVED 2 (c23 decide route residual; c28 arithmetic normaliser);
    alternative cuts B, C, D preserved in AMBIGUITY.md, none resolved;
    cut C gained evidence at CUT-3 (c30 lives in Meta).

time / cost to first substantive downstream return
    none yet. Cost to the first delivery: ~2h40m from receipt (20:30Z
    receipt -> 20:53Z posts, with the prompt and prereg before that).
    Cost of CUT-3 execution: one 9-second compile on a toolchain that was
    already installed.

## Did iteration improve the decomposition? (the preregistered composite)

PREREG s3 defined improvement as: materially_revised > 0 AND
VERBOSITY_FAILURE false AND unknown_became_known > 0, per transition.

    CUT-1 -> CUT-2   15 > 0   false   0      -> FAILS on the third clause
    CUT-2 -> CUT-3    1 > 0   false   0      -> FAILS on the third clause

By the rule Nyx wrote before cutting, iteration did NOT pass. The clause
it failed on is the one the CUT-1 defect (no literal unknowns) made
unattainable, and the rule is not being amended after the fact to rescue
the verdict. What the other evidence says, stated separately: CUT-2
changed 7 kinds by argument and falsified nothing; CUT-3 changed 1 kind
by experiment and falsified a control (c23), and both CUT-3 boundaries
were found by intervention. If the trial had run CUT-3 before CUT-2 the
paper attack would have had something to attack.

Verbosity: bytes fell at both transitions, so "more verbose" is not the
failure mode here. The failure mode is "more confident": 15 kind changes
on paper, none of them tested, and the one thing tested moved.

## Predictions, scored

    P1  CUT-1 inherited rate >= 0.60             CONFIRMED (0.87)
    P2  >= 1 candidate is POLICY/DATA            CONFIRMED (c11 c22 POLICY; c17 c21 DATA at CUT-1)
    P3  mathlib extension files yield 0 organs   CONFIRMED (c18 c19 c20 non-ORGAN at every cut)
    P4  most transferable candidate is not on a file boundary
                                                 CONSISTENT (c02 c06 DISCOVERED) but self-graded; not scored
    P5  < half of CUT-1 ORGANs survive at CUT-2  FALSIFIED (5/8 survived)

## What the Chopper is, on this evidence

- Cuts where the source already cut, on a first pass, at 0.87.
- Prefers fluent hedging to the word "unknown" (0 literal unknowns in
  8 records x 15 fields).
- Attacks on paper produce many confident revisions and no falsifications.
- One cheap execution produced the only cut-changing evidence and found
  two boundaries the paper never would have (a hidden default and a
  mechanism outside the preregistered boundary).
- Has delivered 10 artefacts (6 pressures, 4 organ reports) to two seats
  and had 0 consumed.

The last line is the one the anti-collection law is about.
