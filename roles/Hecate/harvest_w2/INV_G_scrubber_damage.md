# INV-G -- What the v1 blinding scrubber did to the META V1 inputs

Analyst for Hecate, 2026-09-30. Read-only audit. Inputs: hecate/meta/scrub.py,
hecate/meta/arms/arms_v1.jsonl (40 unit-arms, 400 mechanisms),
hecate/meta/run_arms.py, hecate/meta/detector/detect_rows_v1.jsonl,
hecate/meta/matcher/match_rows_v1.jsonl, hecate/meta/REPORT_v1.md,
hecate/meta/RESULTS_v1.json. No model calls were made. New file:
hecate/meta/scrub_v2_proposal.py (a proposal; scrub.py is untouched).

## 0. Bottom line

1. The scrubber damage is real but light. It masked 1226 spans ([X]) across
   400 items, about 1-2% of words, and deleted 517 novelty words. It erased
   symbols, operators and rule notation in 34 items; in 30 items at least
   one sentence is >= 25% masks.
2. Masking differs by arm, so there IS a differential-blinding asymmetry:
   T 5.1 masks/item (1.9% of words), P 3.9 (1.4%), S 1.8 (0.6%),
   O 2.6 (0.9%), G 2.0 (0.7%). Kruskal-Wallis p = 1e-11.
3. That asymmetry does NOT explain the M1 FAMILIAR->COMPOSITE shift.
   Within an arm, masking does not predict FAMILIAR (stratified
   permutation p = 0.34). Controlling for arm type, the sign of the mask
   effect flips (z +1.5, n.s.). At ZERO masks the gap is unchanged: 4/22
   multi-concept items are FAMILIAR against 53/71 single-concept ones
   (Mantel-Haenszel OR 0.027 across mask strata).
4. Masking does not explain M2 saturation either, and here the cause runs
   the other way: the scrubber UNDER-blinds. All 22 matcher items with no
   masks were matched correctly. A crude bag-of-stems matcher that uses no
   model scores 149/160 on raw text, and still 145/160 after v1 scrubbing.
   The decoys are separable from vocabulary alone.
5. A fixed scrubber (v2) is proposed and tested. It removes the
   collateral damage and passes its own leak check on all 400 items. It
   cannot remove the arm asymmetry, which is inherent: multi-concept texts
   contain more concept names, so honest blinding masks them more. v2
   makes the T:S ratio larger (3.5x vs 2.1x), because it strips the
   collateral damage, which was spread evenly across arms.

## 1. scrub.py read as code: every pattern, intent, collateral damage

Order: COINAGE -> VOCAB -> ACRONYM -> NOVEL -> collapse spaces. detect()
re-scrubs mechanism_text()'s output; verified: every stored blind_text ==
scrub(scrub(raw)) and the second pass changed 0/400 items.

P1 VOCAB (case-INSENSITIVE, word-boundary; 95 concept names + 20 field
   names + 63 eponyms/stems, each with hyphen/space and +s / -s variants).
   Intended: concept names, fields, eponyms. 816 hits.
   Collateral:
   - Field "Statistics" -> masks generic "statistics" (191 hits: "avalanche
     statistics", "input statistics", "marginal statistics") and, via the
     automatic singular, "statistic" (36: "sufficient statistic").
     Together these are 227 of the 816 VOCAB hits (28%). None of them names
     a discipline.
   - Field "Logic" -> "logic gate", "temporal-logic goal spec" (7).
   - In scope but costly: generic-word concept names "topology" (64,
     "network topology"), "criticality" (30), "evolution" (13); stems
     "counterfactual" (26, "counterfactual rollout"), "Hamming", "functor".
P2 ACRONYM `(?<![A-Za-z])[A-Z][A-Z0-9]{1,}s?(?![A-Za-z])` (case-sensitive).
   Intended: "all-caps acronyms ... removes invented architecture
   acronyms". 410 hits, 81 distinct strings. In practice it masks EVERY
   token of 2+ capitals or a capital followed by a digit. Classified by hand:
     A concept alias (intended)   110  SAT 46, UNSAT 22, SOC 15, HJB 8, RG 6, RL 6, BTW 5, KC 2
     B tech acronym, no concept   231  CP 30, TT 27, DAG 17, MI 14, RLS 11, RD 10, KL 8, IFS 8,
                                       LDPC 7, PCA 6, SVD 6, TD 6, LP 6, IB 5, SMT 5, MDL 5,
                                       STDP 4, PDE 4, LTP/LTD 3+3, BCM, PID, LQR, MRAC ...
     C symbol/state/operator       66  L2 12, XOR 10, L1 8, AND 5, N0, N1, G1, G2, R1, R2,
                                       X1, X3, X4, X6, P1, P2, AB, BA, NOT, NAND, GF, HG, II, DO
     D English emphasis              3  ORDER, NEW, WITHOUT
   Class A is the only intended target (27%). Collateral therefore makes up
   73% of the rule's hits. The headline defect: "YZ -> XW" ->
   "[X] -> [X]" (reproduced: scrub("YZ -> XW") == "[X] -> [X]").
   Data examples: "pulses in either order AB or BA" -> "order [X] or [X]";
   "HG^T=0" -> "[X]^T=0"; "GF(q) symbols" -> "[X](q) symbols";
   "truncate to size N1 < N0" -> "[X] < [X]"; "X1->...->X6" -> "[X]->...->[X]";
   "Holling type-II" -> "type-[X]"; "kicks to f DO move s" -> "[X] move s".
P3 COINAGE `(?:[A-Z][\w-]+\s+){1,7}\(\s*[A-Z][A-Za-z0-9-]{1,}\s*\)` -> "[NAME]".
   0 hits on the 400 items. Latent bug: ACRONYM runs after it and turns
   "NAME" into "[X]", so a coinage always comes out "[[X]]" (reproduced,
   single pass). It also never checks that ACRO abbreviates the words
   before it ("Each Step (S1)" would be hit).
P4 NOVEL (case-insensitive deletion: novel, new, newly, unprecedented,
   groundbreaking, innovative, revolutionary, first-ever, unique, uniquely).
   Intended: hype. 517 deletions: new 354+5, novel 137, newly 12+3, unique 6.
   Collateral: almost every hit is literal, not hype: "transfers to novel
   tasks" -> "transfers to tasks" (changes a what_can_transfer claim);
   "to a unique attractor" -> "to a attractor". Deletion leaves no marker.
P5 whitespace collapse. Harmless.
check(): tests only that names/fields are absent; it cannot fail on
   over-masking, so collateral damage was invisible to the gate.

## 2. Damage per arm (400 items; unit = mechanism)

    metric                                  T      P      S      O      G
    [X] insertions (total)                 407    313    141    204    161
    [X] per item, mean / median           5.1/4  3.9/3  1.8/1  2.6/2  2.0/1.5
    items with >=1 [X]                      73     65     55     58     56
    % words masked (excl. novelty)         1.89   1.41   0.64   0.85   0.71
    % words masked + novelty deleted       2.28   1.71   1.01   1.27   1.33
    % chars removed                        2.01   1.55   0.87   1.12   1.07
    max % words masked in one item          7.2    5.7    2.9    3.5    3.4
    [NAME] insertions                        0      0      0      0      0
    VOCAB: concept-name hits                80     77     33     35     13
    VOCAB: field-name hits                  33     38     38     72     53
    VOCAB: eponym/stem hits                119     99     41     38     47
    ACRONYM A concept alias                 78     18      0      8      6
    ACRONYM B tech acronym (collateral)     89     68     18     27     29
    ACRONYM C symbol/operator (collateral)   8     11     11     24     12
    items with a class-C symbol destroyed    7      7      5      9      6
    non-concept masks in formula context    24     28     13     19     15
    items with a sentence >=25% masked      14      6      0      6      4
    "[X] op [X]" relations erased           14      7      0      5      1
    novelty words deleted                   92     71     91    108    155

Notes. "Formula context" means the mask touches = < > ( ) ^ _ * + / | { } [ ] ->,
a non-ASCII math character, or contains a digit. "[X] op [X]" means two
masks joined by -> = < > / * + , and, or, vs. The 25% threshold is a
heuristic. Worst item: u0-T-m5 (22 masks, 7.2% of words), where "SAT/UNSAT
threshold" becomes "[X]/[X] threshold" five times. The SAT/UNSAT masks are
intended (Satisfiability), yet they erase the one relation the mechanism
is about. Other examples: u5-T-m2 "refinement morphisms [X]->[X]" (from
P1->P2), u2-P-m2 "outcome ([X] vs [X])" (LTP vs LTD), and u3-T-m0
"[X]/Tucker-decomposed" with "[X] refits" (CP, ALS).

Differential: T >= P > O,G,S in most units; Kruskal-Wallis masks/item
H=50.6 p=3e-10, word rate H=57.2 p=1e-11. The concept part of the gap is
by construction (T/P prompts name 2-3 concepts, outputs reuse them); field
hits peak in O (prompt names a field); class C and novelty are even.

## 3. Could the masking explain the M1 shift? (detector rows, 399 scored)

Test 1: correlation of masking with FAMILIAR and with prior_fit.
  Pooled (all arms):  rho(mask%, FAMILIAR) = -0.19 (p=1e-4);
                      rho(mask%, prior_fit) = -0.24 (p=9e-7).
  Within arm (rho with FAMILIAR / with prior_fit):
     T -0.11 / -0.21(p=.06)   P +0.07 / +0.04   S +0.14 / +0.14
     O +0.19 / +0.08          G +0.17 / +0.11       (all p > 0.05)
  The pooled correlation is the arm effect (Simpson structure). Within
  arms it is null, and in S/O/G it leans POSITIVE: more masking goes with
  MORE FAMILIAR calls. Stratified permutation (labels shuffled within arm,
  5000 draws): p = 0.34 (mask%) and 0.33 (count). The one nominal
  within-arm signal (T, mask count vs prior_fit, rho -0.23, p=0.037) is 1
  of 15 tests and does not survive correction.

Test 2: logistic regression FAMILIAR ~ multi-concept(T,P) + mask.
  mask only:           coef -0.39 per % words, z = -4.1
  multi + mask:        multi -3.79 (se 0.35); mask +0.19 (se 0.13, z = +1.5)
  With [X] count in place of rate: multi -3.77, mask +0.065 (z = +1.5).
  Once arm type is in the model, masking adds nothing, and its sign flips.

Test 3: arm gap at matched masking ([X] count strata), FAMILIAR/scored:
     [X]=0    T 3/7   P 1/15   S 17/25  O 17/22  G 19/24
     1-2      T 0/15  P 4/23   S 26/33  O 22/27  G 27/32
     3-5      T 2/32  P 3/17   S 15/17  O 16/19  G 17/19
     6+       T 2/26  P 3/24   S 4/5    O 12/12  G 5/5
  Mantel-Haenszel OR (multi vs single, FAMILIAR) = 0.027. Items with no
  mask AND no novelty deletion: T+P 2/10 FAMILIAR vs S+O+G 15/20.
  The detector saw these texts with nothing removed. The heavily masked
  single-concept items (6+ masks) are 21/22 FAMILIAR.
INCOHERENT (2 items, both O; 1-2 field/eponym masks, no symbol damage)
and the failed call (u4-P-m8, 1 mask) are not attributable to masking.
Verdict: differential masking does not explain FAMILIAR->COMPOSITE. The
REPORT's own reading stands (multi-concept prompts produce descriptions
of several mechanisms, and the detector's FAMILIAR/COMPOSITE boundary
counts mechanisms).

## 4. Could the masking explain M2 saturation? (matcher rows, 160)

- Wrong: 2/160 (u1-P-m5, u7-P-m1, 3 masks each); 0-mask items 22/22.
- A no-model baseline: score each option by the share of its concepts'
  name and short_description word stems (6-char prefixes, >=5 letters)
  that appear in the text. Unique-argmax correct:
     raw text (no scrubbing)  149/160
     v1 scrubbed text         145/160
     v2 scrubbed text         145/160
  Scrubbing costs a bag-of-words matcher 4 items. Vocabulary alone
  separates the true set from distant decoys (REPORT section 3); the
  scrubber's role is near zero either way, and v2 cannot fix M2.
- [X] density (T 5.1 vs P 3.9/item) says nothing about WHICH of four
  same-k sets; it is a possible arm cue for the detector only.

## 5. Proposed fix: hecate/meta/scrub_v2_proposal.py

Changes, each answering one defect from section 1:
- ACRONYM: replaced by CONCEPT_ACRONYMS. These are the generated initialisms
  of length >= 3 (SOC, MCTS, ECC, GRN, FEP, ...), plus a curated list of
  2-letter and alias forms (RL, KC, GA, QM, CA, ToM, RG, SAT, UNSAT,
  MaxSAT, BTW, HJB, SAE, FFT, DWT, CWT, MaxEnt). Generated 2-letter
  initialisms are excluded because they collide with symbols (TT, AB,
  CS, IS, PT, SA, MC, AI). Indexed symbols, operators, state names and
  non-concept acronyms are never touched.
- COINAGE: fires only when the ACRO equals the initials of the preceding
  capitalised words. It masks the coined acronym's later uses in the same
  text, emits "[NAME]" (no "[[X]]"), and leaves "Data (N)" and
  "Each Step (S1)" alone.
- Fields: multi-word fields match in any case. Single-word fields
  (Statistics, Logic, Physics, ...) match only when Capitalised or
  ALL-CAPS. No automatic singular for -ics words.
- Novelty: deletes only hype words ("unprecedented", "groundbreaking", ...)
  and "novel/new" directly before mechanism/approach/method/framework/....
  "novel tasks", "new instances", "unique attractor" survive.
- Optional indexed=True: each distinct masked term gets a stable tag
  ([X1], [X2]) within a text, so "SAT/UNSAT threshold" becomes
  "[X1]/[X2] threshold" and the relation survives without naming the
  terms. Left for the PREREG to choose.
- Idempotent (tested). check_v2() is a fail-closed leak check matching
  this policy.
Tests (python -m hecate.meta.scrub_v2_proposal test): all pass. 12
preservation cases (YZ -> XW, AB/BA, L1/L2, X1, N1 < N0, GF(q), HG^T,
NOT/AND/XOR/NAND, KL/PCA/STDP/LTP, "statistics", novel/new/unique,
S1/WAIT/ORDER) come through byte-identical; all 12 FAIL under v1, so the
tests can fail. 10 masking cases pass with check_v2() clean; coinage,
indexed and idempotence tests pass.

Run on the 400 items (python -m hecate.meta.scrub_v2_proposal compare):

    arm   v1 masks  v2 masks   v1 %words lost  v2 %words lost  v2 leaves text untouched
    T       407       277          2.00            1.17              13/80
    P       313       215          1.56            0.93              19/80
    S       141        74          0.94            0.33              49/80
    O       204        80          1.18            0.32              45/80
    G       161        66          1.26            0.31              49/80
  check_v2 leaks: 0/400. v1's check() on v2 output flags 136 items, all
  lower-case "statistics" (133) / "logic" (5): the deliberate policy
  change, which weakens the old guard and needs PREREG approval. These
  words survive more in O (59 vs 33-37; unit 4's field is Statistics);
  under v1 they became [X], an equally visible cue.

What v2 does NOT fix: arm asymmetry. The T:S word-loss ratio is 2.1x under
v1 and 3.5x under v2. The extra masking in T/P is the intended blinding of
concept names that the outputs genuinely contain. If v2 should equalise
the detector's view across arms, it needs a design control, not a better
regex. Options: (a) report M1 within mask strata, as in Test 3, as a
standing check; (b) give the detector unscrubbed and scrubbed versions of
a random subset and test whether classification changes; (c) pad
lower-mask arms with neutral [X] tokens to a matched density. Option (c)
is invasive and needs its own validation.

## 6. Adversarial loop on the main conclusion

Claim under attack: "v1 masking is differential by arm but does not
explain the M1 FAMILIAR->COMPOSITE shift or the M2 saturation."

A1. "Counts are the wrong measure. One mask on 'Kalman' removes the
    anchor the detector would use to say FAMILIAR, while ten masks on
    'statistics' do nothing. T items lose their anchors."
    Reply: zero-mask items (anchors intact) should then look like S/O/G;
    they do not (T+P 4/22 FAMILIAR; 2/10 with nothing removed). S items
    lose their concept name too (33 hits) and stay 78% FAMILIAR.
    SURVIVES. Caveat: small n; zero-mask T/P items may be self-selected.
A2. "The detector infers arm from mask density (or residual vocabulary)
    and applies a prior: many masks -> 'composite'. That is an
    item-independent arm-level bias, so a within-arm correlation cannot
    detect it."
    Reply: partly conceded. Within-arm nulls rule out a per-item density
    heuristic. They cannot rule out the detector reading "this text was
    built from several concepts" from vocabulary, which no scrubber
    removes (Section 4: vocabulary identifies the concept set 145/160
    times). The [X]=0 stratum carries no density cue and still shows the
    gap, so density is not needed for the shift. Arm recognition from
    vocabulary is untested and is a confound of BLINDING ADEQUACY, not of
    scrubber DAMAGE. It can be tested only with model calls (option (b)
    above, or the detector run on S items rewritten to mention two extra
    concept names). The claim is NARROWED: masking is not the mechanism;
    whether the detector is arm-blind remains open.
A3. "Symbol destruction lowers coherence or recognisability where it
    matters, in formula-heavy T items."
    Reply: INCOHERENT calls are O items without symbol damage; class-C
    damage is spread (T7 P7 S5 O9 G6); the worst formula items are
    COMPOSITE like 91% of T anyway. SURVIVES, low power.
A4. "The 25% sentence threshold and formula-context rule are arbitrary."
    Reply: conceded; descriptive only. Tests 1-3 use only counts/rates.
A5. "M2: bag-of-stems hitting 145/160 shows separability, not that the
    model used vocabulary."
    Reply: correct. Its role here is narrower: a matcher with no access
    to causal structure already reaches 0.91 on the scrubbed text, so
    M2=1.0 cannot be read as evidence of label-shaped structure. Masking
    cannot be the cause: zero-mask items 22/22. SURVIVES.
A6. "Pooled masking DOES predict FAMILIAR (p=1e-4), and you explained it
    away."
    Reply: it is entirely between-arm; it reverses within arms and with
    arm type in the model (z -4.1 -> +1.5). SURVIVES.
Net: survives as "scrubber DAMAGE is not the explanation"; A2 leaves
open whether the detector is arm-blind at all (no regex can settle it).

## 7. Recommendations

R1. Do not reinterpret v1 M1/M2 on account of scrubber damage. Add one
    line to the REPORT's instrument problems: v1 masked 1-2% of words with
    ~73% acronym collateral; arm-differential (T 2.9x S per item);
    stratified tests show no effect on M1.
R2. Adopt scrub_v2_proposal.py (or a successor) for meta v2 only through
    the v2 PREREG. Freeze CONCEPT_ACRONYMS and the field-case policy
    there, and decide on indexed=True.
R3. Make "M1 within mask strata" a preregistered secondary analysis, and
    add an arm-blindness probe for the detector (A2).
R4. The scrubber cannot fix M2. Use the REPORT's v2 decoy change, and
    preregister the bag-of-stems baseline as the floor M2 must beat.

Reproduction: analysis scripts were scratch (not committed); all numbers
recompute from the four input files with scrub.py's regexes; class A-D
labels are by hand (Section 1 P2).
