================================================================================
PHASE 3 HARDENING -- DOCUMENT 3 OF 3
TEST HARNESS SPECIFICATION, FABLE-5.1 VERSION
================================================================================
Prepared:    2026-10-02 (UTC)   FABLE-5.1 (seat Dionysus)
Specifies:   the gates of document 2 (hardening design v0.2, my version)
Answers:     the test harness spec and next review charter of the
             hardening package v0.2 by ChatGPT 5.6
Runs:        harness/ (reference harness v0; standard library only)
Receipts:    harness/RECEIPT_harness_v0.json
             harness/RECEIPT_mutation_probe.json
             attack/RECEIPT_attack_on_first_version.json
Location:    docs/phase3/hardening/FABLE-5.1/
Headline:    A GATE IS A RULER. 21 gates run today against 50 sound cases
             and 258 cases that must not pass. EVERY GATE HAS AT LEAST ONE
             FAULT IT IS KNOWN NOT TO CATCH; 29 ARE PINNED, AND EVERY READ
             FOUND MORE. AT FIRST SIGHT THE TESTS MISSED 22 OF 25, 34 OF
             44, 20 OF 32 AND 26 OF 36 ONE-LINE CHANGES TO THE GATES, AND
             12 OF 26 AND 20 OF 54 ON THE THIRD VERSION.

TERMS
--------------------------------------------------------------------------------
As in document 2. Used here besides:
    the package   the hardening package v0.2 by ChatGPT 5.6
    H0 to H9      the ten layers of the package's harness spec
    the readers   the adversarial reads of this package (attack/): the
                  first reader, its closure read, a second reader with
                  three forks, and a final round by both
    mutant        here: a case that must not pass, with the verdict it
                  must get. Most are broken on purpose; a few are cases
                  a gate cannot decide
    the cue       the bit an organism must hold in the toy world
    door two      entry of a physics by a positive found by blind search

WHAT RUNS MEANS HERE
--------------------------------------------------------------------------------
RUNS means: implemented in harness v0 and exercised on toy fixtures or
on four existing receipts. It does not mean the gate has been used on
any Prometheus engine. The toy fixtures are small state machines written
by one author. They are deterministic and have no noise. The harness
shows that each gate returns its registered answer on the cases it
holds. It proves nothing about cognition, and nothing about whether the
gates are the right ones.

--------------------------------------------------------------------------------
1. PURPOSE
--------------------------------------------------------------------------------
The package's purpose line is right and I keep it: "The harness prevents
rules from living only in prose." Two jobs, as there: software
conformance, and scientific qualification. I add two that the others
depend on: the harness qualifies itself, and it is attacked by someone
who did not write it.

--------------------------------------------------------------------------------
2. VERDICTS
--------------------------------------------------------------------------------
Every gate returns exactly one of five.

    PASS           qualified gate, complete inputs, pass condition held
    FAIL           qualified gate, complete inputs, fail condition held
    INDETERMINATE  qualified gate, complete inputs, neither held
    BLOCKED        could not run: an input or precondition is missing
    UNQUALIFIED    no authority here: no known positive or negative, or
                   never shown able to fail

The package has four. The fifth is INDETERMINATE: a statistical gate
needs a registered third outcome, or an underpowered run gets read as a
negative. Six gates compute it here, and the claim gate carries it
from a facet. When a gate finds several problems, or several gates feed
one decision, the verdict is the worst of FAIL, BLOCKED, UNQUALIFIED,
INDETERMINATE, PASS, in that order. Only PASS moves a claim.

--------------------------------------------------------------------------------
3. THE META-GATE (GM), THE ATTACK AND THE PROBE
--------------------------------------------------------------------------------
Every gate registers sound cases and mutants. A mutant carries the
verdict it must get.

    a gate with no mutant, or no sound case ............ UNQUALIFIED
    a gate that passes a mutant ........................ FAIL (escape)
    a gate that rejects a sound case ................... FAIL (false
                                                         accusation)
    a mutant rejected with the wrong verdict ........... FAIL
    otherwise .......................................... PASS

A gate that is not PASS here may not feed a claim. GM is itself tested:
five tests give it a gate with no mutant, one with no sound case, one
with an escape, one with a false accusation and one with a wrong
verdict.

THIS IS NOT ENOUGH, AND THREE VERSIONS SHOWED IT. Each version passed GM
on every gate when it was handed to a reader.

    VERSION ONE: 21 gates, 34 sound cases, 62 mutants, all mine.
      The first reader wrote 71 broken cases and 12 sound ones. Replayed
      on a copy of version one, by my count of the labels in its
      scripts: 65 of the 71 got through, in 19 of 19 groups, and all 12
      sound cases were refused. Ten of the 71 are two faults swept over
      a parameter. It also made 25 one-line changes to the gates' logic;
      the tests missed 22, one of which alters no verdict.
    VERSION TWO: 44 sound cases, 148 mutants, 11 known escapes.
      The closure read found 14 new faults that passed in 11 gates, and
      14 of the earlier cases still passing, 6 of them unlisted. The
      second reader found an unlisted passing fault in every one of the
      21 gates. Of fresh one-line changes the tests missed 34 of 44, 20
      of 32 and 26 of 36.
    VERSION THREE: 48 sound cases, 215 mutants, 24 known escapes, 103
      unit tests.
      The final round. The second reader found fifteen passing faults on
      no list, in twelve gates, and four sound cases refused. Of fresh
      one-line changes the tests missed 12 of the closure reader's 26,
      and 20 of the second reader's 54, which it wrote before opening
      the tests. Two of those 20 alter no verdict.
    VERSION THREE AS AMENDED, this one: 50 sound cases, 258 mutants, 29
      known escapes, 110 unit tests. Not read again.
      The probe now holds all 247 changes of the seven sets. 244 could
      be carried over to this code, 218 of them distinct. The tests
      notice 236 (211 distinct); the 8 they miss each alter no verdict.
      That figure is taken after the tests were written against those
      changes. It says the holes are closed. It does not measure the
      tests.

So a gate here has three conditions, not one:
  - GM: its sound cases pass and its mutants are rejected as registered;
  - ATTACK: someone who did not write it has tried to break it. Most of
    what was found is now a registered mutant or a known escape
    (section 10); the rest is in the readers' reports;
  - PROBE: its logic is changed one line at a time by someone who did
    not write the tests, and the tests are asked whether they notice.
    The figure to quote is the one taken at first sight.

--------------------------------------------------------------------------------
4. THE GATES
--------------------------------------------------------------------------------
The column H is the package's layer. Sound and broken are counts of
registered cases; broken counts every case that must not pass. The
column esc is the count of known escapes.

    gate            guards                             H    sound broken esc
    --------------  ---------------------------------  ---  ----- ------ ---
    G1.cell         a run exists only as a complete    H0     2    26    1
                    cell whose answers are attainable
    G1.receipt      a receipt belongs to its           H0     1    12    1
                    registration
    G2.preflight    both answers of the ruler are      --     1    10    1
                    attainable before a run starts
    G3.exclusion    class exclusion gives the known    H1     1    19    1
                    answers, at its thresholds too
    G4.entry        a physics is read only after it    H1     4    11    3
                    has returned a known answer
    G5.neutrality   a ruler is shared only where it    H2     5    11    1
                    has returned the known answers
    G6.observer     observing a run does not change    H3     2    12    2
                    it
    G6.reset        after a reset a runtime behaves    H3     2     9    2
                    as one that never ran
    G6.restart      capture and restore carry the      H3     1    10    1
                    whole state
    G7.calibration  a reach estimator agrees with      H4     1     6    2
                    exact reach on five cells
    G7.report       a search result is what it says,   H4     7    36    1
                    and is the search registered
    G8.demand       every baseline on the list sits    H5     1    14    2
                    at the bound
    G9.arms         arms registered as separate give   H6     3     6    2
                    separate series
    G9.clauses      every clause holds somewhere and   H7     1     6    1
                    fails somewhere by itself
    G9.sham         a sham can fail and is neutral     H6     2     4    1
    G10.setting     the nine open choices are          H7     2    11    1
                    registered
    G10.contrast    a named contrast changes one       --     1     3    1
                    variable
    G10.ruler       a ruler answered the kit           H7     1    11    2
                    correctly before it is used
    G11.custody     confirmation is not discovery,     H8     2    17    1
                    and the rule was fixed first
    G12.promote     a claim stands only on facets      H9     9    16    1
                    that passed, each with a source
    G12.render      a claim is quoted with its cell,   --     1     8    1
                    class and registered setting
                                                            ----- ------ ---
                                                              50   258   29

The 258 cases are rejected as registered: 125 FAIL, 99 BLOCKED, 25
UNQUALIFIED, 9 INDETERMINATE. The nine are not broken: they are cases a
gate cannot decide, and it must say so.

SPECIFIED AND NOT BUILT
    a runner        G1 and G2 are checks a runner would call. There is
                    no runner.
    G13.report      numbers and quotations in a report are recomputed
                    from receipts. Exists for my review as
                    check_review.py and for these documents as
                    check_hardening.py; not generalised.
    selection       a filter on which worlds are used is registered. No
                    gate.
    the class       a claim must name the class it excludes. The gate
                    checks that the field is there, not that the class
                    is the right one.
    G4, door two    a positive found by blind search
    G6, classes     stochastic, asynchronous and continuous execution,
                    with equivalence margins. The toy is deterministic.
    G8, W1          exact class values and a break-even price
    kit             world parking, nested compiler cargo, hierarchical
                    selector, flattened twin, genuine learned updater
    B's rules       frozen update law, V kept out of the last assay,
                    cost as a vector: nothing tests them
    second author   every read was by a reader of my model family; no
                    second author has written a gate, a ruler or an
                    isomer

--------------------------------------------------------------------------------
5. WHAT EACH GATE CHECKS
--------------------------------------------------------------------------------
G1.cell. Sixteen fields present, else BLOCKED. A description may not be
  a placeholder word. Exposure and the time of registration are counts.
  Design seeds and registered seeds are integers: none repeated, none
  shared. The verdict table maps every count to one registered outcome
  and can emit every outcome. One registered seed per unit the table
  counts. For each answer expected from a known case the cell registers
  the design runs behind that case, as hits of units. The gate computes
  the probability of the answer from the table, at the worse end of the
  exact 99% interval; below 0.99 the run is BLOCKED.
  In the fixture, 24 units and a rule of 22: a positive right in 480 of
  480 design units is attainable at 0.9985; in 240 of 240, at 0.9897,
  and blocked; in 466 of 480, at 0.8715. A declared power is not read.

G1.receipt. The registration must itself pass G1.cell. The gate hashes
  the code on hand itself and compares it with the registration and with
  what the receipt reports. The registered seeds, each once. A run
  earlier than its registration fails; one at the same clock tick is
  INDETERMINATE. What the receipt says its run found is not read.

G2.preflight. With n trials, exact rate p0 and level alpha: a count that
  excludes the class exists; the positive, at the lower 99% bound of its
  design rate, reaches it with probability 0.99; and a member of the
  class is called NEGATIVE with probability 0.99. Here: 64 episodes,
  rate 1/2, alpha 1e-6, critical count 51; a positive right 15 times in
  16 reaches it with probability 0.99997.

G3.exclusion. A score out of 64 has five places to stand: 51 or more is
  POSITIVE; 14 to 47 is NEGATIVE (too low for the weakest positive);
  48 to 50 is undecided; 13 or fewer is INVERTED (the cue is carried and
  its complement answered); and with too few episodes for any answer it
  is underpowered. The fixture holds four positives (64 of 64), a weak
  positive (61), each impostor on nine disjoint blocks of seeds (25 to
  41), and a scripted score at each of the six thresholds. The gate is
  UNQUALIFIED without a weak positive, a further block, or thresholds
  that reach a yes, a no and an inverted answer. It does not check how
  many blocks there are, or that the weak positive is weak.

G4.entry. A physics may be read only with a designed positive and a
  matched impostor, both declared to be of that physics. The preflight
  must pass for the weakest positive, and the exclusion ruler must
  return POSITIVE and NEGATIVE on them. An impostor that scores INVERTED
  is refused: it carries the cue. So is an organism that does not
  declare its physics.

G5.neutrality. Three rulers. Class exclusion and whole-state interchange
  are declared SHARED and return the truth in all four physics.
  Interchange moves a donor's state into a recipient after the fourth
  step, in 128 pairs with the opposite cue and 128 with the same; each
  count is judged by the same exact test as a score, so its negative is
  earned too. The third ruler is physics-specific on purpose: it moves
  the attribute named w. On the other three physics it returns
  NOT_MOVED, and declared shared it FAILS. A physics with no known
  answer is outside a ruler's authority and does not fail it.

G6.observer. One world, every seed in turn, with and without the
  observer, for each of the nine organisms of the panel. The runs must
  be equal: what the world delivered at each step, the organism's state
  after the step and again straight after the observer, and the final
  state of both.

G6.reset. An episode after a reset must equal the same episode on a
  runtime that has never run. Tried with no cue and with each cue,
  after an earlier episode with each cue and with none.

G6.restart. Capture after each of the eight steps, restore into a
  runtime that has just run the opposite cue, continue. The rest of the
  run and the final state must match.

G7.calibration. On 8-bit landscapes exact reach is computed by
  propagating the whole distribution. On five cells the sampled count
  (256 founders, 400 proposals) must be compatible with it at level
  0.002, both ways. Resolution at exact reach 0.7298: counts from 164 to
  208 of 256 pass.

G7.report. Landscape, budget, start law, distance, policies and
  founders come from the registration, not from the report, and a report
  that differs from them fails. The gate replays the registered search
  on the registered founders and compares the counts. A discovery needs
  a hit and a cold start; a repair claim a repair start at distance one
  or more. A null needs two policies, one able to cross a neutral step;
  no hit; a positive control that each policy reaches 99 times in 100 at
  the same budget, computed by the gate; a stated scope (these policies
  at this budget, never the substrate); and a bound below 1 and no
  smaller than the founders warrant. On these toy landscapes every count
  is also held against exact reach.

G8.demand. Required: a constant, a clock reader, a reader of the probe,
  an organism that writes on the environment, and tables fitted on other
  seeds to nine small views of what the world shows after the cue (the
  probe; three bits of the clock; the first and the last one, two and
  three distractors; all of them). Each must be SHOWN to lie within 0.1
  of one half: of 2,048 episodes, 929 to 1,119 right. At 912 or fewer,
  or 1,136 or more, the world fails: a policy that is reliably wrong has
  the information too. In between, or with a view that cannot be fitted,
  the verdict is INDETERMINATE.

G9.arms. Arms equal in at least 22 of 24 replicates give one series and
  one piece of evidence, whether they are one computation or two that
  both hit a cap. One pair may be exempted: the intact arm and its sham.
  This audit and the next two are registered for 24 replicates and are
  BLOCKED on any other number.

G9.clauses. A clause fails in a cell when it is true in at most 12 of
  its 24 replicates, and holds when true in at least 22. UNQUALIFIED if
  some clause fails in no cell or holds in none. INDETERMINATE if every
  clause fails somewhere and some fail only where another does not hold.

G9.sham. The sham clause must fail in some cell, and the sham arm must
  lie within 25% of intact (or one task) in 22 of 24 replicates.

G10.setting. The nine choices of document 2, section 6. Presence and
  type: power is a probability of at least 0.99, the horizon a count of
  at least one, the threshold a positive number; nine placeholder words
  are refused.

G10.contrast. A contrast named after one variable differs in that
  variable only, among the fields written down. The same choice worded
  two ways counts as a difference: a false accusation the gate is known
  to make.

G10.ruler. For a claim and a setting, the gate reads from the receipts
  what the ruler returned on each registered cell and compares it with
  the registered answer. For the bits claim it reads the certified bits
  and the two guards of that run, not a label. A wrong answer is FAIL.
  No correct positive, no correct negative, a member unbuilt or not run
  at this setting leave it UNQUALIFIED. A receipt that cannot be read is
  BLOCKED.

G11.custody. Ten fields. Confirmation seeds, panel and generator (by
  the hash of its code) differ from discovery; the champion was chosen
  on discovery data; tuning stayed in budget; the acceptance rule was
  fixed before the confirmation data was opened; two custodians. Seeds
  are integers. A claim of new seeds only may share the generator.

G12.promote, G12.render. Document 2, section 13. Seven facets at the
  first level, four more at the second, one each at the third and
  fourth, and those of the claim's kind. A facet with no source is
  BLOCKED. A rendered claim prints its cell, the class it excludes, its
  registered setting, checked by hash, and why it stands no higher.

--------------------------------------------------------------------------------
6. FIXTURE PACKS
--------------------------------------------------------------------------------
RETAIN-1 PANEL. One world: a cue bit, six distractor bits, a probe. The
cue is uniform and independent of what follows, so a policy that carries
nothing across the gap scores exactly 1/2. That is a property of the
generator, argued and not tested. Four positives hold the bit as a
stored word, in an attractor, in a packet in flight around three
forwarding nodes, and as a domain on a ring of eight cells under local
majority. Four impostors are the same machines holding something else:
the last distractor, a single basin, the first distractor, the majority
of the last three inputs. One weak positive loses its word in one
episode of eight. Worlds broken on purpose: the cue follows the first,
second, third or fourth bit of a readable counter; the probe carries the
answer, its complement, or the answer in two episodes of five; the cue
is the xor of two distractors or the parity of all; the environment
keeps what is written, within an episode or across episodes; the harness
forgets to reset.

SEARCH LANDSCAPES. 8-bit genomes, one random flip per step, two
acceptance rules (strict; neutral). Founders have at most four bits set.

    landscape   rule      cold reach, exact   repair from one flip
    ---------   -------   -----------------   --------------------
    ASCENT      both           1.0000              1.0000
    NEEDLE      strict         0.0000              1.0000
    NEEDLE      neutral        0.7298              0.7757
    VALLEY      strict         0.0000              1.0000
    VALLEY      neutral        0.0000              0.1797

Three lessons sit in that table. On the needle the strict rule finds
nothing and the neutral rule finds it: a null from one policy is the
operator's, not the substrate's. On the valley cold reach is exactly
zero and repair is certain: recovery is not discovery. And on the valley
the neutral rule repairs worse than the strict one: repair reach depends
on the operator too. The positive control (ASCENT, cold) is reached with
probability 0.0107 at a budget of 5, 0.8126 at 24, 0.9896 at 46 and
0.9909 at 47: a null is read from a budget of 47 up.

--------------------------------------------------------------------------------
7. THE FOURTH PACK: MY OWN RUNS
--------------------------------------------------------------------------------
The third reader of my review found faults in runs 2 and 3 by hand. The
gates below read the receipts of those runs and return several of the
same faults as verdicts. They return a part of what that reader found.
They do not return: a family read the easy way, the selection of worlds,
a rule changed after design runs, or the measured power of 0.9.

    gate           on             verdict       what it found
    -------------  -------------  ------------  ------------------------
    G9.clauses     run 2          UNQUALIFIED   4 of 13 clauses fail in
                                                no cell; 2 fail by
                                                themselves
    G9.clauses     run 3          UNQUALIFIED   6 of 13; 1 fails by
                                                itself
    G9.arms        run 3          FAIL          8 arms give 3 series
    G9.arms        run 2          PASS          8 arms, 8 series
    G9.sham        run 2          FAIL          within 25% of intact in
                                                8 of 24 replicates;
                                                faster in 24
    G9.sham        run 3          UNQUALIFIED   the sham clause fails in
                                                no cell
    G10.setting    runs 2 and 3   BLOCKED       no power and no
                                                amortization horizon
    G10.contrast   run 2 against  FAIL          named after shared
                   run 3                        parts; of 10 fields
                                                written down 6 differ
    G10.ruler      runs 1, 2, 3   FAIL          for the strong claim,
                                                yes to a known negative
                                                at each setting
    G10.ruler      run 4          PASS          for bits carried: right
                                                on 9 cells of 9

Two cautions. The settings read by G10.setting and G10.contrast are my
own transcription, made after the fact, of what the two preregistrations
say. Two things tie it to the record: the clause counts recomputed with
the two effect thresholds equal the receipts' own counts, and the
absence of a power statement and of a horizon is checked against the
two files; both by check_hardening.py. And under this specification
runs 2 and 3 would have been refused at registration for those two
missing fields. The other faults in the table can be found only after a
run.

--------------------------------------------------------------------------------
8. THE SMALLEST NEXT EXPERIMENT: COMBINATION ON AN UNSEEN PAIR
--------------------------------------------------------------------------------
WHAT HAPPENED TO THE EARLIER PROPOSALS. The draft proposed a key world
with a second nested boundary as a ruler for nested improvement. The
first reader simulated it: a cache with 256 inherited re-indexings
passes. Version two proposed the world below as a ruler for reuse of
built parts. Two readers built caches that pass it. Version three said
its control catches an answer that does not come from this life. The
second reader built an organism that passes both arms where one arm's
key is reused. All of it is in the harness (rso_harness/ladder.py,
exploratory). What is proposed now is smaller, and has a custody check
that no reader has attacked.

WORLD. Per life, three random permutations of 16 symbols (tables) and
three more (moves). A family is a pair of one table and one move, shown
as a label. A trial shows x and asks for the move applied to the table
at x, then reveals it; each x once. The life shows eight of the nine
pairs, then the ninth.

EXACT NULL. The ninth map is fixed by three of the maps shown and by no
two. For any organism whose state, when the ninth family begins, depends
only on shown families that do not link the ninth pair's table to its
move, the ninth map is a uniformly random permutation and the best
expected score is elimination: 3.38 of 16. TABLE_CACHE and TWO_TABLES
below keep all eight tables, so they are outside that class: their rows
are measurements of two organisms, not a bound.

CONTROL. The eight families shown come from another key under the same
labels. The bound then holds for every organism. The control guards only
against a leak that reaches both arms alike.

CUSTODY. Every life's key is hashed, and none may repeat. A run in which
one does is answered KEY_REUSED whatever the arms say.

SIMULATED (300 lives; exploratory; a mean of 5.81 or more is called
CARRIED at alpha 1e-6):

                                               ninth pair   control
    ELIM          carries nothing                 3.48        3.48
    TABLE_CACHE   every table seen, and 256       3.43        3.50
                  fixed re-indexings
    TWO_TABLES    every way of combining two      3.45        3.49
                  kept tables
    SCHEMA_CACHE  all 512 ways of combining      13.46        3.48
                  three; reads no label
    COMPOSER      composes the three its         16.00        3.49
                  label points to
    WATCHER       keeps last life's tables;       3.48        3.48
                  uses them if this life
                  repeats it

    with a key reuse planted in the harness:
    HIDER         keeps last life's answers;     15.96       15.96
                  one key in both arms
    SANDBAGGER    the same, used only after      15.96       15.96
                  eight families
    WATCHER       as above; the life's key       15.96        3.46
                  reused, the control's fresh

With fresh keys the two arms call the fourth and fifth COMBINED and the
others NOT_SHOWN. Under the planted faults the arms alone call the hider
and the sandbagger NOT_FROM_THIS_LIFE, and the watcher COMBINED, which
is wrong. The custody check answers KEY_REUSED for all three.

WHAT IT WOULD SHOW IF REGISTERED AND RUN. That information from at least
three families, shown separately, was combined in one life: a claim
about structure with an exact null, read from answers alone.
WHAT IT WOULD NOT SHOW. How it was combined. A cache that tries 512
inherited recombinations passes. So it is not a ruler for reuse of built
parts, it does not tell choosing from building, and it says nothing
about the strong claim. Nor does it apply to worlds without keys.
WHAT A REGISTRATION STILL NEEDS.
  - the number of lives and its power, and an earned negative: NOT_SHOWN
    is the absence of a yes, not a no;
  - the pair held out drawn per life. With a fixed pair, the second
    reader found, one hard-wired formula scores 16.00;
  - the nine choices of the setting. The content reset is the hard one:
    kept tables are content, and with them cleared no organism can pass;
  - the kit at this setting, built and registered, with the two caches
    as positives for combination and negatives for reuse;
  - organisms by a second author, written to beat the two arms and the
    custody check;
  - a fire test of each arm and of the custody check. The last three
    rows are a start.
COST. One file on the model of my review's fourth run; minutes of one
processor.

NOT THE SMALLEST, AND MORE DECISIVE. B's experiment 5: build the cargo
compiler and the genuine learned updater, each by someone who has not
seen the ruler, and count false promotions and false rejections under
B's interventions. B's plan holds it; the package's plan holds the
attacks and not the positive.

--------------------------------------------------------------------------------
9. WHERE THIS HARNESS FAVOURS TRACK A
--------------------------------------------------------------------------------
The next charter asks which assumptions privilege R1 and R2. In harness
v0, nine:

  1. State capture is a tuple of named fields. A physics with
     distributed or continuous state needs a capture with a tolerance.
  2. Interchange copies state bit for bit. In a chaotic system a copy
     leaves the manifold; it needs an ensemble and a sham of matched
     size.
  3. Execution is deterministic. For the other three execution classes
     only a rule is given, and nothing is exercised.
  4. Time is a count of discrete steps taken in lockstep with the world.
  5. An episode has a sharp start, and reset means going back to it.
     An ecology has no such boundary.
  6. Lesion sites in the receipt audits are countable entries (library
     items, an index). A weight matrix has no such sites.
  7. The search fixtures flip bits of a genome. Gradient search and
     population methods are absent.
  8. Observations are symbols handed to the organism. A local physics
     has to pay for getting a signal in and out, and the toy charges
     nothing.
  9. The organism is one individual. Shared niches and collectives have
     no fixture, and the unit of analysis is never tested.

The lattice and the packet ring on the panel are there against 1 and 4,
and they are still small discrete machines I wrote. A second author
should write the next isomer.

--------------------------------------------------------------------------------
10. KNOWN ESCAPES
--------------------------------------------------------------------------------
29 faults the harness is known not to catch. Each is run, and a test
pins it, so that a passing harness is not read as covering it. Every
gate has at least one. The list is not complete: each read has found
faults that were on no list.

THE GATE READS A DECLARATION (16).
  G1.cell       design counts that were typed and never run
  G2.preflight  the same, for the positive's design rate
  G3.exclusion  a bound of 0.48 where the truth is 0.5, registered
                together with thresholds computed from it
  G4.entry      stored-word machines relabelled as another physics
  G5.neutrality the physics-specific ruler declared shared on three
                relabelled stored-word machines
  G8.demand     a world that keeps what is written, with a constant
                entered under the name of the baseline that would show it
  G9.clauses    cells that were typed, not run
  G9.sham       a sham that cannot fail, made to look able to by a cell
                in which another, harmful operation is called the sham
  G10.setting   a power of 0.99 typed onto run 3, with nothing computed
  G10.contrast  two runs that differ in a choice nobody wrote down
  G10.ruler     a registry that calls the fixed builder a positive for
                the strong claim; the ruler then passes
  G10.ruler     rows that point at another run's cells
  G11.custody   an edited copy of the discovery generator presented as
                a new family; generators are compared by hash
  G12.promote   a facet typed PASS whose named source was never run
  G12.render    a setting and its hash replaced together
  G7.report     a null whose prose says the substrate cannot do it,
                with the scope field right; prose is not read

THE GATE LOOKS AT PART OF WHAT HAPPENED (10).
  G1.receipt    a receipt whose reported outcome was changed after the
                run
  G4.entry      a positive that is right on the 64 episodes checked and
                wrong ever after
  G6.observer   an observer that disturbs only seeds that were not
                checked
  G6.observer   an observer that writes a field of the organism its
                reported state omits
  G6.reset      a carry that a runtime hides and uses two episodes
                later
  G6.reset      a reset that leaks on every third call
  G6.restart    a hidden count of episodes, used from the second on
  G7.calibration an estimator that searches on the five cells of the
                panel and reports no hit anywhere else
  G8.demand     the cue follows the fourth bit of a counter the organism
                can read. No baseline or table reads that bit; a policy
                that does scores 64 of 64. A list is not the class
  G9.arms       three computations reported as eight arms, with a
                constant added to each

THE GATE HAS A RESOLUTION (3).
  G4.entry      an impostor that carries the cue in one episode of
                five: 40 of 64, called a negative; over 2,048 episodes
                it is shown to carry
  G7.calibration an estimator that ran 95% of the registered budget
                (exact reach 0.7113 against 0.7298)
  G9.arms       arms that are one series, nudged apart in three
                replicates of 24

The remedy for the first group is outside the harness: derive it twice,
or have a second author attack it.

--------------------------------------------------------------------------------
11. HOW TO RUN
--------------------------------------------------------------------------------
    cd docs/phase3/hardening/FABLE-5.1/harness
    python -B -m unittest discover -v      110 tests, under a minute
    python -B run_harness.py               rewrites the receipt; exit 0
                                           only if all is as registered
    python -B mutation_probe.py            about twenty minutes;
                                           rewrites its receipt
    cd ../attack
    python -B replay_attack.py             about four minutes; replays
                                           the first read on version one

The harness receipt holds every gate's row, every mutant's verdict and
reason, the 29 known escapes, the panel scores and thresholds, the exact
reach table, the audits of my four receipts with what each ruler
returned on each of their 26 cells, and the two exploratory key worlds;
and the hash of every source file. The closure read, the second read
and the final round are kept as records in attack/, each with the
version it attacked. They are not replayed.

--------------------------------------------------------------------------------
12. LIMITS
--------------------------------------------------------------------------------
  - A conformance skeleton. One author, toy fixtures, no noise: the
    positives score 64 of 64. Fixtures near a threshold are scripted
    scores and one weak positive.
  - Three reads and a final round, by readers of my own model family.
    Each found faults in most of what it probed. What was changed after
    the final round was checked by code only: no reader has seen it.
  - The mutation figure for this version is fitted. The honest figures
    are the six taken at first sight, and they are bad.
  - The audits of section 7 are regression tests on four receipts of
    mine. They show the gates find those faults. They do not show the
    gates find others.
  - Both key worlds of section 8 are exploratory simulations with no
    registered verdict. Three earlier readings of them were refuted.
  - Twenty-one gates are a judgment about what matters. Document 2,
    section 17, item 3 is the test: a gate that never returns anything
    but PASS on real work should be removed.

Bottom line, to confirm or contest: which of these 21 gates would have
changed nothing in v1 and v2, and can be dropped?

--------------------------------------------------------------------------------
APPENDIX: THE PACKAGE'S EIGHTEEN HISTORICAL FIXTURES, AND FOURTEEN MORE
--------------------------------------------------------------------------------
Where each has a running case in harness v0. Two of the eighteen and two
of the fourteen are specified only.

     1 seeded phenomenon called endogenous ...... G10.ruler: the hider of
                                                  an inherited key (run 4)
     2 answer or label leakage .................. G8, three ways
     3 missing constant baseline ................ G8, BLOCKED
     4 control that cannot fail ................. G9.sham, G9.clauses
     5 ruler cannot emit a required verdict ..... G1.cell, G2.preflight
     6 clock or counter leak .................... G8
     7 coordinate or location bias .............. specified (two adapters)
     8 holdout champion selection ............... G11
     9 search cannot cross a neutral step ....... G7.report
    10 propagation called content transport ..... G4, the packet impostor
    11 library growth called recursive .......... G10.ruler, run 2
    12 source-read organ called mechanism ....... G12, intervention facet
    13 same-code repeat called replication ...... G12, second
                                                  implementation; G1
    14 post-data analysis promoted .............. G1.receipt, G11
    15 incomplete reset, external carryover ..... G6.reset
    16 write ancestry called recursive order .... specified (nested
                                                  compiler not built)
    17 persuasive false accusation .............. GM, the 50 sound cases
                                                  (in part)
    18 observer changes the dynamics ............ G6.observer

    19 a run named after one variable that changed several ... G10
    20 arms that give one series ............................. G9.arms
    21 a clause no fixture can make false .................... G9.clauses
    22 a sham that is not neutral ............................ G9.sham
    23 a run started with no power statement ................. G10.setting
    24 a bound that is not exact ............................. G3, in part
    25 a positive that does not work; an impostor that does .. G4
    26 a budget cut where naive and developed differ ......... specified
    27 worlds chosen so that labels are true, unregistered ... specified
    28 a verdict quoted without its setting .................. G12.render
    29 a gate tried only by its author ....................... GM, attack
    30 a retention certificate read as nested improvement .... G12, NESTED
    31 a report believed and not replayed .................... G7.report
    32 a power declared and not computed ..................... G1, G2
================================================================================
END OF DOCUMENT 3
================================================================================
