# INV-S -- Does a surface property of the text explain the FAMILIAR/COMPOSITE arm gap?

Analyst for Hecate, 2026-10-01 01:24Z. Read-only, no model/API calls. Inputs:
hecate/meta/detector/detect_rows_v1.jsonl, arms/arms_v1.jsonl, units.py,
hecate/gravity/detector_v1.md. Scripts in scratch only (S/inv_s*.py).

## 0. Bottom line

1. NO. None of the surface properties tested explains the gap. Matched or
   stratified on length, on hand-lexicon domain count, on coverage of the
   unit's own concept vocabularies, or on a bag-of-words "looks
   multi-concept" score that separates the arms with AUC 0.946, the gap
   stays the same size. Multi-concept items are 10-15% FAMILIAR and
   single-concept items are 75-93% FAMILIAR. Mantel-Haenszel OR is
   0.03-0.05 in every surface stratification; raw it is 0.027.
2. "COMPOSITE is a count of named priors" cannot be the explanation. The
   detector listed exactly 3 nearest_priors on 399/400 rows (the 400th
   failed to parse). The count is constant, so stratifying on it leaves the
   raw table unchanged (OR 0.027).
3. Within an arm group, surface features do not predict the call.
   Surface-only logistic, leave-one-unit-out: AUC 0.49 (multi) and
   0.50 (single). The BoW multi-ness score gives AUC 0.55 and 0.58.
4. The blind texts are NOT trivially separable by arm across units: BoW
   leave-one-unit-out accuracy is 0.60-0.68 against a 0.60 base rate. Within
   a unit they are separable (0.85-0.905), through the unit's B/C concept
   vocabulary. Without training, the detector's call alone recovers the
   arm group at 0.85, using all 8 units at once.
5. What remains is consistent with the detector reading composition in the
   mechanism content: T/P generators were told to make mechanisms "visible
   only when combined". This analysis cannot certify that reading. It only
   rules out the cheap surface explanations listed here (see 6, Limits).

## 1. Predictions (written 2026-10-01T01:16Z, before any fit; copied verbatim)

    Already seen during data inspection (NOT a prediction): 399/400 rows list
    exactly 3 nearest_priors (1 row has 0, parse failure). The detector schema
    asks for the nearest priors and the classification rule is "FAMILIAR = one
    known mechanism; COMPOSITE = two or three combined". So the count of priors
    listed is constant and cannot carry the arm gap.
    P1 BoW logistic, leave-one-unit-out CV, multi (T,P) vs single (S,O,G):
       accuracy >= 0.80 (chance 0.60).
    P2 Within arm group, surface features predict COMPOSITE weakly:
       distinct-concept-vocabulary count has OR > 1 per extra domain in both
       groups; word count near null. Stratified permutation p in 0.01-0.2.
    P3 Matched on word count + distinct-domain count, the multi-single
       FAMILIAR gap shrinks but does not vanish: >= 30 points remain
       (raw gap about 75 points).
    P4 Detector-side proxy (distinct prior fields among the 3 priors) tracks
       COMPOSITE strongly; it is circular and will be reported as such.

Scorecard: P1 WRONG across units (0.667), RIGHT within units (0.85).
P2 PARTLY RIGHT: the signs are as predicted but the effects are smaller,
and only one test reaches p < 0.05 (multi group, field count, p = 0.034).
P3 WRONG in direction: the gap did not shrink at all (about 70 points
matched). P4 WRONG: the distinct-prior-field count barely differs by class
(section 5).

## 2. Data and definitions

FAMILIAR/COMPOSITE subset: 397 items. Excluded: 2 O-arm INCOHERENT and 1
P-arm parse failure.

    arm  FAM  COMP   FAM%      multi = T,P (159 items, FAM 18 = 11%)
    T      7    73    9        single = S,O,G (238 items, FAM 197 = 83%)
    P     11    68   14
    S     62    18   78
    O     67    11   84 (+2 INCOHERENT)
    G     68    12   85

Surface features computed from blind_text only:
words (whitespace tokens); masks ([X] count, the concept-name residue left
by the scrubber); sents (sentences in the statement line); n_exist (items
in "what exists"); semis (semicolons, a clause proxy); couple (coupl-,
combin-, joint, interact-, both, together, hybrid, bridg-, interplay,
unif-); ndom/nfield (distinct hits among 27 hand regex vocabularies: one
per each of the 24 unit concepts, built from its name, short_description
and standard terms, plus evolution, ML and economics; nfield collapses
them to 15 fields); cov3 (how many of the item's own unit's 3 concept
vocabularies hit); covBC (the same for concepts B and C only; S sees only
A, P sees A and B, T sees A, B and C).

Arm means:

    arm  words  ndom  masks  couple  sents  n_exist  cov3=0/1/2/3
    T     289   4.96  5.09   1.48    1.79   3.14     0/12/41/27
    P     290   4.34  3.91   2.14    1.99   3.45     0/25/45/10
    S     303   3.31  1.76   1.45    1.82   3.40     13/52/14/1
    O     307   3.52  2.55   1.16    2.09   3.94     46/32/2/0
    G     299   3.79  2.01   1.25    2.22   3.91     56/23/1/0

Length does not track arm; domain count, masks, concept coverage do.
## 3. Test 1 -- can the blind text alone predict the arm group?

Binary BoW, min_df 2:

    model                      leave-one-unit-out   10-fold (within-unit)
    logistic C=1   counts          0.667                0.853
    logistic C=10  tfidf 1-2gram   0.627                0.905
    multinomial NB counts          0.647                 --
    statement line only (C=1)      0.663                 --
    base rate                      0.600                0.600
    detector call (no training)    0.850 (COMPOSITE -> multi)

5-arm LOUO accuracy is 0.38 (chance 0.20). G is the most distinct arm
(62/80 correct). T, P and S are confused with each other.
Top words: multi = species, hypothesis, maxent, entropy, intervention;
single = training, network, accuracy, input. Concept words, not style:
"multi" vocabulary changes per triplicate, so cross-unit BoW gets little,
while within a unit the B/C concept vocabulary marks T/P almost perfectly.

## 4. Test 2 -- do surface features predict COMPOSITE within arm group?

Univariate logistic with arm dummies, coefficient per SD. p values come
from a permutation that shuffles labels within each arm, 5000 draws.

    feature  multi(b, p)       single(b, p)      pooled(b, p)
    words    -0.18  0.44       -0.05  0.84       -0.09  0.51
    ndom     +0.57  0.070      +0.17  0.44       +0.32  0.066
    nfield   +0.62  0.034      +0.20  0.33       +0.35  0.028
    masks    +0.02  0.78       -0.57  0.014      -0.23  0.34
    couple   -0.08  0.86       -0.14  0.60       -0.11  0.61
    sents    -0.18  0.53       +0.04  0.72       -0.05  0.75
    n_exist  -0.13  0.62       -0.06  0.68       -0.09  0.49
    semis    +0.12  0.74       -0.01  0.84       +0.03  0.92

18 tests; 1-2 nominal hits are chance-level. The single-group masks hit
has the anti-leakage sign (more residue, fewer COMPOSITE; cf. INV-G). All 8 features together, logistic,
leave-one-unit-out: AUC 0.492 (multi) and 0.504 (single). BoW predicting
COMPOSITE within a group does not beat the base rate: 0.887 vs 0.887
(multi), 0.832 vs 0.828 (single).

## 5. Test 3 (key) -- matched comparison

Stratified, FAMILIAR rate multi vs single in strata that contain both groups:

    stratified on                        multi FAM   single FAM   MH OR
    none (raw)                           18/159 .11  197/238 .83  0.027
    # nearest_priors (constant 3)        18/159 .11  197/238 .83  0.027
    ndom                                 18/159 .11  195/236 .83  0.032
    words/50 x ndom (17 strata)          18/154 .12  189/228 .83  0.035
    words/50 x ndom x couple (45)        18/127 .14  158/191 .83  0.031
    unit x ndom (36)                     17/133 .13  163/200 .81  0.038
    cov3 x covBC (own concept coverage)       --          --      0.048
    BoW multi-ness score, 5 bins         --          --           0.047

1:1 nearest-neighbour matching without replacement, caliper in SD units:

    matched on                    pairs  multi FAM  single FAM  discordant  McNemar p
    words                          147    .10        .86        1 vs 113    1e-32
    ndom                           129    .12        .82        5 vs 96     7e-23
    words + ndom                   109    .14        .82        4 vs 78     8e-19
    words+ndom+couple+masks         41    .10        .93        0 vs 34     1e-10

The sharpest cells are where a single-concept text looks multi-concept:

    own-concept coverage cov3 = 2:   multi 8/86 FAM    single 14/17 FAM
    covBC = 1 (B or C vocab seen):   multi 10/81 FAM   single 33/41 FAM
    BoW score [0.8,1.0]:             multi 7/86 FAM    single 3/3 FAM
    25 most multi-looking singles:   18/25 FAMILIAR
    25 most single-looking multis:   3/25 FAMILIAR

Single items that look multi stay FAMILIAR; multi items that look single
stay COMPOSITE. The gap does NOT vanish under any surface match (small
cells, 17 and 3, but all one direction).

## 6. Circularity, and what was not tested

- nearest_priors is detector output, written in the same response as
  the classification. Its COUNT turned out to be degenerate (always 3), so
  the hypothesis "COMPOSITE = number of priors named" is not just
  unsupported: this design cannot test it at all.
- Detector-side proxies are post-treatment, because they are produced
  jointly with the call. Distinct field tokens among the 3 priors: multi
  FAM 5.94, multi COMP 5.79, single FAM 5.20, single COMP 5.66. These
  barely separate the classes, and matching on them leaves the gap
  (.11 vs .81). prior_fit is lower for COMPOSITE by construction (multi
  .83/.63, single .91/.77, FAM/COMP). Stratifying on fields x prior_fit
  moves the OR to 0.395. That is conditioning on a co-output of the
  decision, and it says only that COMPOSITE calls come with lower
  single-prior fit, which the rule already implies. It is NOT evidence
  that the call is surface-driven. Detector-side quantities were used for
  no conclusion above.
- Lexicon limits: the 27 vocabularies are hand regexes with imperfect
  recall and some cross-hits (e.g. "selection", "filter", "solver"). A
  better domain tagger might find a surface variable that the detector
  tracks. The BoW multi-ness score was added as a lexicon-free check, and
  it gives the same answer.
- Not tested: higher-order style (how the clauses are linked, whether the
  statement names two interacting subsystems), which is close to mechanism
  structure itself. A causal test needs the detector, run on paraphrases
  that keep the mechanism and change the surface (or the reverse). That
  needs model calls and was out of scope here.

## 7. Implication for Hecate

The split survives every cheap surface control (length, concept residue,
domain-vocabulary count, priors named). Left: (a) real composition, which
the T/P seeds demanded, or (b) higher-order cues not captured here.
REPORT_v1's "composites of known mechanisms, close to by construction"
stays the simplest account; no grounds to call COMPOSITE an artifact.
