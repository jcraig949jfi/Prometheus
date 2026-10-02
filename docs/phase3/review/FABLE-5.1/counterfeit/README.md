# Four preregistered runs on the recursive-sagacity criterion (RSO v0.1, section 19), and one file of probes

Reviewer: FABLE-5.1 (seat Dionysus). Run 2026-10-01 and 2026-10-02 (UTC) on
SKULLPORT.

**What this is.** The review charter, question 9, asks the reviewer to build
the strongest counterfeit it can against the combined criterion (functional
savings; V -> U -> S causal nesting; developmental provenance) and to repair
the definition if the counterfeit passes. This folder holds that attempt.

**What it is not.** Not a result about any Prometheus engine and not a
result about reasoning. Every organism is designed, so nothing is
discovered. All of it is observation about a criterion: one author, one
host, toy worlds. In my package's terms, level C0 and independence I1.

## The short version

| | question | preregistered at | answer |
|---|---|---|---|
| run 1, `gauntlet.py` | does anything simple meet the protocol as written? | 8dc9ef542 | yes: a selector over three inherited procedures, under easy readings of four things the steps leave open |
| run 2, `gauntlet2.py` | and with cost, content, sham and donors read strictly, and B, D, E kinds never met? | 619472376 | a plain library learner passes all six conjuncts in 24 of 24 replicates; a selector over 90 ready parts and pairs fails |
| run 3, `gauntlet3.py` | and when the targets share no part with the history? | c6adb3a57 | the library learner fails; a selector over 32 inherited search orders passes, at half the threshold and under weaker controls. The run changed the curriculum as well as the parts |
| run 4, `keys.py` | can the amount acquired across families be bounded from behaviour? | 635b3cba1 | yes on designed organisms, conservatively |
| `probes_exploratory.py` | what do the passes of runs 2 and 3 rest on? | not preregistered | the curriculum, the savings factor, the acceptance rule, how the worlds are chosen, and an easy reading of family C |

In each run the code and the expected verdicts were committed before the
registered seeds ran, and every verdict came out as registered. In each
case I had seen design runs on design seeds first; the preregistrations say
what changed after them.

The order in which they were made is 1, 4, 2, 3, probes. Runs 2 and 3 exist
because two read-only reviewers showed that the run before was too easy, or
proved less than I had said. The probes exist because a third reviewer
showed the same of runs 2 and 3. The probes are exploratory: design seeds
only, written after the results they vary were known.

What they add up to. Section 19 leaves five choices open: cost; how the
later families differ from A; content resets; the sham; what family A is.
To run its steps I turned them into conjuncts with thresholds of my own
(four in run 1, six from run 2 on).

    setting                                what passed
    1. run 1: as written, four             a selector over three inherited
       conjuncts; C, D, E new seeds of     procedures; also a library learner
       B's kind, and B too for the
       selector
    2. run 2: A is four part families;     a library learner; a selector over
       B, D, E are pairs of those parts    90 ready parts and pairs fails
       (kinds never met); C a new seed
    3. run 3: A is one composite family;   a selector over 32 inherited search
       B, D, E are composites of other     orders, at half the threshold and
       parts; C a new seed                 with weaker controls; the library
                                           learner fails
    4. probe: A is four part families;     neither the library learner nor
       B, D, E made of other parts         the order selector; a positive may
                                           be impossible here (see below)
    5. probe: C a kind never met           nothing, and nothing could in this
                                           world

- The verdict depends on choices the text leaves open: which organism
  passes changes with what A is and with how B differs from it.
- In each of the three registered settings an organism with fixed
  inherited machinery passed. Every organism I built is of that kind, so
  the runs show what the steps admit. They cannot show what the steps
  would do with a true positive.
- Where nothing passed I have no positive either. A test that nothing
  passes is not qualified by that. In setting 4 a positive may be
  impossible as the controls stand: a history that shares no part with the
  targets is itself what the protocol calls a wrong history, so whatever
  gains from it gains from the control too.

## Run 1: the protocol as written

Four designed organisms on prediction of hidden functions mod 17, the
section-19 protocol (steps 1 to 12) as arms, 24 replicates per arm.

    organism     target   v0.1 verdict   errors per task after a truncated
                                         construction, naive -> developed
    STATIC       SHIFT    FAIL           8.12 -> 8.12
    MATURATION   SHIFT    FAIL           8.07 -> 1.00  (irrelevant history
                                                        gives 1.00 too)
    GEARBOX      SHIFT    PASS           8.04 -> 1.00
    GEARBOX      SCALE    PASS           8.66 -> 1.00
    BUILDER      AFFINE   PASS           11.26 -> 1.94

- GEARBOX: three inherited learning procedures and a move-to-front list (a
  permutation of three items, 2.6 bits). Only the list develops.
- BUILDER: a fixed constructor and a library of templates that worked.

**What that pass rests on.** The accuracy reviewer re-ran the code and
showed the pass depends on four choices section 19 does not fix, each of
which I had read the easy way. `sweep_gauntlet1_exploratory.py`
(exploratory, after the fact) repeats the first check on the registered
seeds.

1. Budget. Construction was cut off exactly where naive and developed
   differ. The table above is the quality of a procedure after that cut,
   not a cost of acquisition. In tasks needed to reach an acceptable
   procedure the savings are small, and the verdict holds only in a window:

       case             PASS at budgets   tasks to an acceptable procedure
                                          naive   developed
       GEARBOX SHIFT    1                 2       1
       GEARBOX SCALE    1, 2              3       1
       BUILDER AFFINE   4 to 7            8       4

   Counting development as well (4, 5 and 4 tasks), none of the three is
   cheaper than a naive organism working on the one target.
2. Later families. C, D and E were new seeds of B's kind. For GEARBOX, B
   was a new seed of a kind already met, so in this world a "family" is a
   seed and the pass is learning across tasks of one kind: order 2,
   promoted to order 3 by my mapping of V, U and S. When B must be a kind
   never met GEARBOX fails (its irrelevant-history arm is that case: 11.28
   and 11.93 errors per task).
3. Content. No code carried out the resets of steps 2 and 5.
4. Sham. It wrote zero to a cell nothing reads. It could not fail.

Also: the lesion reset the organism to its naive state, and rescue and the
V donor restored the identical state, so thirteen arms were three
computations and "24 of 24" there is determinism; the U-donor arms involve
no transplant; and only two of the four conjuncts (savings, provenance) had
a fire test.

So run 1 supports one statement: with those four choices open, the steps
can be met by a permutation of three items. That is a fault of
specification. My preregistered claim was the narrow one ("the v0.1
criterion as written is satisfied by algorithm selection with a
move-to-front memory"); a draft of the review said more and was corrected.

The three added checks of run 1 (gain outside the inherited set; knockout;
count of accepted procedures) rest on my own inventory of what each
organism inherits "as a unit". BUILDER's candidate set is the same 42
templates before and after any history; its library only reorders them. So
the classes that run printed tell a list written out from a list generated,
and no more. They are not behavioural.

## Run 2: kinds never met

`gauntlet2.py`. Four of the open choices are fixed the hard way.

- COST: tasks consumed until an acceptable procedure exists, no cut-off; a
  candidate is accepted after 8 passed tasks in a row. Lifecycle cost
  includes development and is compared with a naive organism working on
  the targets alone.
- LATER FAMILIES: B, D and E are kinds never met, with distinct function
  classes that no shallower template covers. C is NOT read the hard way:
  it is a new seed of B's kind (and a narrower family inside B's class).
- CONTENT: every declared content store is cleared at steps 2 and 5.
- SHAM: removes as many library entries as the lesion, among entries the
  target does not use. A random library of equal size and a wrong-history
  library are separate donors.
- SEPARATE ARMS: the lesion removes only the two entries the target uses;
  rescue material and the V donor come from a second individual.

World: functions mod 17 from ADD, MUL, SQR, CUB, INV. Development on four
parts (depth 2); targets are compositions of two of those parts (depth 4)
that no template of depth 3 or less covers. Six conjuncts; a conjunct HOLDS
if its relation is true in at least 22 of 24 replicates and FAILS at 12 or
fewer.

    cell         verdict   conjuncts
    BUILDER      PASS      all six hold, 24 of 24 each
    SELECTOR     FAIL      SAVINGS 0 of 24         (90 ready parts and pairs)
    STATIC       FAIL      SAVINGS 0 of 24         (never writes its library)
    WASTEFUL     FAIL      LIFECYCLE 0 of 24       (development costs 40x)
    HIDDEN       FAIL      NESTING 0 of 24         (undeclared second copy)
    BADSHAM      FAIL      NESTING 0 of 24         (the sham is a lesion)
    MATURATION   FAIL      PROVENANCE 0 of 24      (any history unlocks it)
    MEMORISER    FAIL      SAVINGS 0 of 24; with the content reset skipped
                           it shows savings in 24 of 24
    OFFHISTORY   FAIL      REPEAT 0 of 24          (D, E use unmet parts)

Each fire test fails the conjunct it was built to fail. Three of the seven
fail others as well: STATIC and MEMORISER fail five conjuncts, HIDDEN two.
SELECTOR here is a different organism from run 1's GEARBOX; the selector
over three procedures was not run in this world.

BUILDER in detail, median tasks over 24 replicates:

    acquire B, a kind never met ................ naive 313.5   developed 20.5
    acquire D .................................. naive 334.0   developed 19.0
    acquire E .................................. naive 346.5   developed 20.0
    whole lifecycle, development included ...... naive 1045.5  developed 171.0
    development plus B, against naive B alone .. cheaper in 24 of 24
    B after lesion of the two entries it uses .. 316.0
    B after the sham ........................... 12.0
    B after rescue from a second individual .... 16.0
    B in a naive recipient of a donor library .. 22.0
    B after a history of other parts ........... 323.5
    B with a random library of equal size ...... 323.5
    frozen U, errors per task .................. 2.00 on a new seed of B's
                                                 kind; 1.97 on a narrower
                                                 family; 12.00 for what the
                                                 lesioned line builds at the
                                                 intact line's cost

BUILDER's constructor never changes, and neither does its set of
candidates (660 templates). It tries its library, then pairs of library
entries, then an inherited enumeration. The library only reorders what the
enumeration already holds.

The portfolio says of R8: "If it calls ordinary library accumulation
recursive sagacity, the ruler is insufficient." With B, D and E kinds never
met, built from parts just learned, my six conjuncts still pass it.

**What that pass rests on** (probes on six design seeds; tables below):

- The world builds the saving in. Every target is one of the 16 pairs of
  the four parts just learned, and the constructor tries those pairs
  first. A naive organism must pass 147 shallower templates before its
  first candidate of the right depth. On the registered seeds the largest
  developed cost is 27 tasks and the smallest naive cost 166.
- The savings factor of 4. It passes up to 6, is indeterminate at 8 on five
  of six design seeds, fails at 16.
- The curriculum of four part families. With one, two or three, it fails.
- Acceptance after 8 passed tasks, raised from 1 after design runs. At 1 it
  fails on five of six design seeds.
- Worlds chosen so that the labels are true (13% of unselected worlds have
  four outside parts that also compose B).
- Family C read the easy way. With C a kind never met nothing passes.
- The content reset moves one conjunct of the MEMORISER and not its
  verdict.

## Run 3: targets that share no part with the history

The second reviewer, arguing as the criterion's authors, gave the reply
they would give: section 18 speaks of "genuinely new causal families"; read
step 3 as "B shares no built component with history A" and the library
learner fails. That is right, and run 2 already shows it: its
wrong-history arm (323.5 tasks against 313.5 naive) and its OFFHISTORY
cell (REPEAT 0 of 24). The reviewer's unregistered probe also found a
one-bit organism that passes under that reading.

`gauntlet3.py` asked what passes instead. It uses run 2's world, task and
acceptance code (imported unchanged). Development is ONE composite family
built from four history parts; the targets are built from four other
parts; no pair of history parts covers a target's function class.

    cell         verdict   conjuncts
    STRATEGIST   PASS      five hold in 24 of 24; PROVENANCE in 23 of 24
    BUILDER      FAIL      SAVINGS 0 of 24  (353.0 tasks against 354.0 naive)
    STATIC       FAIL      SAVINGS 0 of 24      (never switches)
    EAGER        FAIL      PROVENANCE 0 of 24   (any history switches it)

STRATEGIST has no library. It inherits 32 complete orders in which to try
the same 660 templates: the plain order (in use at birth), one that tries
the 81 pairs of parts first, and 30 decoys that try them last. Every target
(and every history family) is in that list of 81 by construction. One index
develops, 5 bits of capacity: after a success it switches to the inherited
order that would have reached that success soonest. Median tasks:

    acquire B .................................. naive 398.0   developed 57.0
    acquire D .................................. naive 356.0   developed 44.5
    acquire E .................................. naive 362.0   developed 42.0
    whole lifecycle, development included ...... naive 1097.5  developed 424.0
    development plus B, against naive B alone .. cheaper in 15 of 24
    B after lesion (index reset) ............... 398.0
    B after the sham (two idle orders swapped) . 57.0
    B after a history of one part family ....... 398.0
    B with a random index ...................... 486.5

**The run changed two things at once.** The third reviewer caught it: the
targets' parts are disjoint from the history's, AND family A is one
composite family where run 2 had four part families. The probes separate
the two (SAVINGS of 24 on six design seeds; verdict on all six unless
noted). Every row was run in run 3's harness at its factor of 2; the first
row is run 2's curriculum and agrees with run 2 itself:

    family A                              library learner     order selector
    four part families, the targets'      24 24 24 24 23 24   0 0 0 0 0 0
      own parts (run 2's curriculum)      PASS                FAIL
    four part families, other parts       0 0 0 0 0 0         0 0 0 0 0 0
                                          FAIL                FAIL
    one composite of the targets' parts   0 0 0 0 0 0         24 24 24 24 24 24
                                          FAIL                PASS
    one composite of other parts          0 0 0 0 0 0         24 22 24 24 24 24
      (as run 3)                          FAIL                PASS
    four other parts, then one            0 0 0 0 0 0         24 22 24 24 24 24
      composite of them                   FAIL                PASS on three,
                                                              INDETERMINATE on
                                                              three (LIFECYCLE
                                                              21 21 23 21 22 23)

Both verdicts of run 3 follow the curriculum, not the disjoint parts. After
one composite the library holds a single entry of depth 4 (144 of 144
design replicates) and can form no pair, so the library learner fails
whatever the parts are. The order selector switches after a composite and
never after a part (developed cost equals naive in 24 of 24 after four part
families), so it passes after one composite whatever the parts are.

**Limits on STRATEGIST's pass.** It is not a pass under run 2's controls.

- The sham swaps two orders the organism never reads; sham cost equals
  intact cost in 24 of 24. It cannot fail. (The library learner's sham in
  this file does nothing at all.) This is the fault I named in run 1.
- Lesion equals naive, rescue and V donor equal intact, and the irrelevant
  history equals naive, each in 24 of 24 registered replicates. Eight arms
  are three computations and NESTING adds nothing to SAVINGS. Also a fault
  I named in run 1.
- The savings factor is 2 where run 2 used 4, fixed before the registered
  run. On the registered seeds the pass survives at 3 and 4, is
  INDETERMINATE at 6 and fails at 8. On design seeds at 4 it passes on five
  of six.
- The 30 decoys are there for one control, the random index. On design
  seeds the developed index ends at the one useful order in 142 of 144
  replicates and stays at the plain order after the irrelevant history in
  144 of 144: about one bit depends on experience. PROVENANCE by number of
  inherited orders, six design seeds:

      orders   PROVENANCE of 24         verdict
      2        0 0 0 0 0 0              FAIL on six
      3        14 13 13 11 11 10        FAIL on three, INDETERMINATE on three
      4        14 17 17 12 15 20        FAIL on one, INDETERMINATE on five
      8        21 20 21 22 21 21        INDETERMINATE on five
      16       21 23 22 23 22 24        INDETERMINATE on one
      32       23 24 23 23 22 24        PASS on six
      64       24 23 23 23 23 23        PASS on six

- The switch uses function classes: it ranks every one of its 660
  templates that covers the accepted one. Ranking only the accepted
  template gives SAVINGS 19 15 21 16 20 19, INDETERMINATE on all six. The
  organism reads nothing about the hidden kind, but the pass depends on
  that choice.
- Lifecycle. With three composite families LIFECYCLE holds in 21 23 23 21
  23 23 of 24 (INDETERMINATE on two seeds). The figure "18 of 24" in the
  preregistration and in drafts of the review came from a superseded
  script whose pairs-first order listed 144 raw pairs; it reproduces on
  one design seed (18 23 22 21 22 20).
- No content reset is called in this file. No organism in it declares
  content, so nothing changes, but the claim of "the same strict readings"
  in the preregistration does not hold for content or for the sham.
- Fire tests exist for SAVINGS and PROVENANCE only.
- Power. 240 design replicates of the STRATEGIST cell, in ten blocks of 24:
  nine PASS, one INDETERMINATE (LIFECYCLE true in 235 of 240, PROVENANCE in
  232). At factor 4, four of ten blocks are INDETERMINATE.

What run 3 does show: a choice among inherited search orders can carry
savings to families that share no part with the history, when the history
has the same shape as the targets. I count it as an existence sketch.

## What the probes show about run 2

`probes_exploratory.py`, receipt `RECEIPT_probes_exploratory.json`. Not
preregistered. Design seeds only (37, 41, 53, 67, 71, 83 for run 2's world;
43, 47, 59, 61, 73, 79 for run 3's). Counts are of 24 replicates, one per
seed, in that order. Lines marked "registered" are arithmetic on the
registered receipts.

    BUILDER by savings factor       verdicts on six seeds
    2, 4 (as registered), 6         PASS on six
    8                               INDETERMINATE on five (SAVINGS 21 21 24
                                    21 21 22)
    16                              FAIL on six
    registered receipt              PASS at 8 (22, 23, 22), INDETERMINATE at
                                    10, FAIL at 16

    BUILDER by acceptance rule      verdicts on six seeds
    1 passed task                   FAIL on five, INDETERMINATE on one
                                    (NESTING 10 16 11 10 8 10)
    2                               PASS on five, INDETERMINATE on one
    3, 8 (as registered)            PASS on six

    BUILDER by curriculum           verdicts on six seeds
    first 1 of the 4 part families  FAIL (SAVINGS 0 on six)
    first 2                         FAIL
    first 3                         FAIL
    all 4 (as registered)           PASS

    how the worlds are chosen       2,000 design worlds
    worlds redrawn (salt above 0)   0 (and 0 of the 312 registered replicates)
    first candidate B rejected      124 (it had a second decomposition)
    first four other parts          264, which is 13.2% (another four are
      compose B                     taken)
    BUILDER with the choices off    PROVENANCE 22 19 24 22 17 19:
                                    INDETERMINATE on three of six seeds

    family C a kind never met       frozen U good in 0 of 24 on every seed
      (D's kind, E's kind)          (median 10.65 to 11.17 errors of 12)
    family C as registered          good in 24 of 24 on every seed
    the same for STRATEGIST         0 of 24 on every seed

    MEMORISER, leak world           SAVINGS   verdict
    content resets applied          0         FAIL on six
    content resets skipped          24        FAIL on six (LIFECYCLE, U_TRANSFER,
                                              NESTING and REPEAT stay at 0)

    run 1's reading under run 2's cost (the target is a new seed of a kind
    already met, library learner): SAVINGS at factor 4 in 3 1 2 0 3 1 of
    24; LIFECYCLE in 0 on all six.

So "nothing built is shared" should be read as two separate things: with
run 2's curriculum and other parts, neither organism passes; with one
composite as the curriculum, the order selector passes whether or not the
parts are shared.

    clauses of run 2's conjuncts        registered receipt, nine cells
    never false in any cell             the rescue clause of NESTING; the
                                        random-library clause of PROVENANCE;
                                        the two clauses of U_TRANSFER that
                                        score the frozen U on C
    third clause of U_TRANSFER          true for BUILDER in 24 of 24 by the
      (the lesioned line is bad on C)   default score of an organism that
                                        built nothing; false in other cells

## Run 4: bits acquired, one order up

`keys.py`. A life has a fresh 44.25-bit key (a permutation of 16 symbols)
and six families, each with its own offset. A policy that carries nothing
between families cannot beat elimination: 3.38 correct of 16, exactly.
2,000 lives per organism and condition; the life is the independent unit.
From accuracy at each trial position, Fano's inequality gives a lower bound
on the bits of the key the organism carried into its last family.

    organism       correct of 16,     after          certified  really
                   later families     irrelevant     bits       holds
                                      history
    ELIM           3.41               3.36           0.00       0
    SELECTOR(64)   3.39               3.41           0.00       -
    ACQUIRER(4)    6.09               2.86           1.44       11.41
    ACQUIRER(8)    9.73               2.20           9.46       24.95
    ACQUIRER(12)   13.08              1.67           23.39      35.67
    ACQUIRER(16)   15.06              1.06           38.99      40.25

- SELECTOR(64) inherits 64 ready permutations and develops an index. With
  a fresh key it shows no savings.
- ACQUIRER(k) learns the relative table of k symbols in the first family.
  Its exact expected score, from its definition, is 6.1033, 9.7179,
  13.0834 and 15.0625; the observed means are within 0.02 of each.
- The certified bits never exceed what the organism really holds.
- After irrelevant history the acquirers fall below chance: they apply the
  wrong table.

Fire tests, each breaking one thing on purpose:

| | what is broken | what must happen | happened |
|---|---|---|---|
| A | the key is drawn from the SELECTOR's own inherited list (declared: 6 bits) | the ruler refuses; with the world check skipped it treats the selector like an acquirer | yes |
| B | the harness reuses one key for every life and the organism inherits it | INHERITED_OR_LEAK from the first family's score | yes |
| C | the power gate is given 200 lives | it refuses | yes |
| D | as B, but the organism hides the key during the first family | caught only by the irrelevant-history arm | yes |

Fire test D says section 19's irrelevant-history step is necessary and
must stay.

**A classification I withdrew.** The run was registered with a threshold,
11.49 bits (log2 of the 2,880 bits of inheritance the cell allows), and
with labels: WITHIN_SELECTION_BOUND below it and CONSTRUCTED above. The
receipt holds those labels. The second reviewer showed they claim too
much. The threshold bounds one index into one list, and nothing limits an
organism to one index: a selector with sixteen lists of sixteen symbols
fits in the cell's allowance and is ACQUIRER(16). The run never set the
line against a selector that shows savings in an admissible world. So what
the measurement gives is a number, the bits acquired across a boundary. It
is the RETAIN world of my prototype moved up one order. It separated
organisms that carry nothing from organisms that carry 23 bits or more,
and under-certified a partial acquirer. It does not tell selection from
construction, and it says nothing about depth.

## What follows for the definition

1. Section 19 has five open choices (cost; how the later families differ;
   content; sham; what family A is). They have to be fixed in the text,
   every clause needs an organism built to fail it, and every registered
   verdict needs a stated power. The text must also say what makes a
   history wrong when the right one shares no part with the targets. My
   own runs do not yet meet that: C is read the easy way, run 3's sham
   cannot fail, and four clauses have no fire test (the rescue clause of
   NESTING; the random-library clause of PROVENANCE; the two clauses of
   U_TRANSFER that score the frozen U on C).
2. The steps have no arm that separates choosing among inherited
   alternatives, building from parts with a fixed builder, and improving
   the builder. Only the last deserves the word "recursive". Nothing in
   this folder is a positive for it, and I do not know that one exists at
   toy scale.
3. What can be reported honestly today: the setting a result used (what A
   was, how the later families differed, the factor); how much developed,
   with the measure named; and "nested improvement, order k" in place of
   "recursive".
4. How much developed, two measures. Capacity of the developed store: 2.6
   bits (an order of three procedures), 5 bits (one index among 32), 37.5
   bits (four library slots over 660 templates). What experience selects
   among in the world at hand: about 1 bit for the index; 11.6 bits for the
   library (which four of nine parts were met, in order). An earlier table
   in this file mixed the two.

Three statements from drafts are withdrawn: that no reading of the steps
excludes fixed inherited machinery (I ran three settings, and in two
others nothing passes); that each tightening admits a smaller organism (a
tightening admits nothing; a change of curriculum admitted the order
selector); and that a pass in setting 2 with a fail in setting 3 identifies
reuse of built parts (the library learner fails after one composite with
shared parts too).

## Errata and limits

- PREREG.md describes BUILDER's constructor as trying "the library, then
  compositions of library items, then primitives". The code at that commit
  also enumerates every pair of primitives last. The description omitted
  it. So a naive BUILDER can reach a composite without any library: an
  affine template is its 8th candidate.
- In run 1 the count of V reads is incremented on every construction, so
  that conjunct cannot fail; the receipt's arm names
  `U_donor_into_lesioned` and `lesioned_U_with_intact_V` describe
  transplants that do not occur; there was no power computation.
- The six conjuncts, their thresholds and the mapping of S, U and V onto
  each organism are mine (in the preregistrations). Section 19 has no
  conjuncts and no thresholds. In runs 2 and 3: S is the constants fitted
  within a task, U the procedure constructed for a kind, V what the
  constructor reads and writes (a library; an index). Section 19 defines V
  as a process; a library is a store of earlier U's, so that mapping is a
  choice. The rule for content is "anything that refers to particular
  tasks".
- The worlds of runs 2 and 3 are compositional by design. That is the
  setting in which these organisms should do well. The question was
  whether passing there tells them apart from something more.
- The preregistrations and the code say worlds are "redrawn" until the
  labels "the entries B uses", "irrelevant history" and "nothing shared"
  are true of the function classes (power maps commute, so targets can
  have two decompositions). Nothing is redrawn: the salt is 0 in all 312
  registered replicates. The labels are made true by choosing inside the
  first draw. It is a selection, it reads only the function tables, and
  the probes show what it does.
- gauntlet2.py's header says "six fire tests" and lists seven.
- PREREG_gauntlet2.md says rescue and V donor come from "a second
  individual with its own families and order". The donor has its own
  family seeds; it shares the inherited order, and the rescued entries are
  the same templates that were removed.
- PREREG_gauntlet3.md claims the same strict readings of cost, content and
  sham as run 2. That holds for cost. See the limits of run 3.
- gauntlet3.py's header and PREREG_gauntlet3.md say a factor of 4 "held in
  22 or 23 of 24" on design seeds. On one of six design seeds REPEAT holds
  in 21.
- In gauntlet3.py, `Strategist.sham` swaps two idle orders inside a list
  shared with the other clones of the same individual before copying it.
  No arm reads those two orders, so no number changes.
- In gauntlet3.py the library learner's random library excludes the nine
  parts by name, not by function class, and has three entries against a
  developed library of one. In registered replicate 10 it costs 12 tasks
  against 163 naive; that is BUILDER's PROVENANCE 23 of 24.
- In runs 2 and 3 the D and E arms start from the state after development,
  so what was written for B is never reused. Compounding is not tested.
- U_TRANSFER has no dedicated fire test. Step 10's U cross is reduced to
  one comparison. Step 13 was not run. WASTEFUL is charged 40 tasks per
  candidate and is not tested on 40. Run 2's sham makes BUILDER faster
  (12.0 against 20.5 in 24 of 24), so it controls for size and not for
  neutrality.
- Run 4's bound is conservative, and it measures one order only.
- A draft of the review said my own frozen requirement XFER-07 was fooled
  by the library learner. That was wrong: its Why line already says a
  fixed learner speeds up inside its hypothesis space and only a gain
  outside it counts.
- Three rounds of review each found that the round before had claimed too
  much. A fourth would find more.

## Reproduce

From this directory, standard library only:

    python gauntlet.py --design     design seeds; prints; writes nothing
    python gauntlet.py              registered seeds; rewrites the receipt
    python gauntlet2.py [--design]
    python gauntlet3.py [--design]
    python keys.py [--design]
    python sweep_gauntlet1_exploratory.py
    python probes_exploratory.py    design seeds only; rewrites its receipt

About 6, 12, 14, 16 and 45 seconds, and 4 minutes for the probes. All are
deterministic. The timestamps differ between runs; every count and verdict
should not. On 2026-10-02 copies of the four run scripts were re-run in a
scratch folder and reproduced every receipt exactly, timestamps apart.
