================================================================================
PHASE 3 HARDENING -- DOCUMENT 2 OF 3
HARDENING DESIGN v0.2, FABLE-5.1 VERSION
================================================================================
Prepared:    2026-10-02 (UTC)   FABLE-5.1 (seat Dionysus)
Built from:  A  my review of the wind-tunnel design v0.1
             B  the review by Enceladus (ASTRA-6.0)
             C  the hardening package v0.2 by ChatGPT 5.6
             O  the original design v0.1 and its portfolio R0 to R9
             Document 1 says what came from where.
Companions:  01 comparison and synthesis; 03 test harness specification;
             harness/ (runs); attack/ (the adversarial reads)
Location:    docs/phase3/hardening/FABLE-5.1/
Status:      a design. Nothing in it is a scientific result.
Headline:    A RULER, A GATE AND A REPORT ARE EACH BELIEVED ONLY AFTER
             PASSING A SOUND CASE AND REJECTING A BROKEN ONE, AND NOT ON
             THEIR AUTHOR'S WORD. A NESTED CLAIM NAMES THE CLASS IT
             EXCLUDES.

HOW THIS DIFFERS FROM THE PACKAGE'S v0.2
--------------------------------------------------------------------------------
I keep the package's shape: a thin federation of native runtimes, two
axes read from the world, two ways for a physics to enter, a panel of
the same capability in unlike physics, claims as records of evidence,
three statuses for a candidate. Where a section below says AS THE
PACKAGE, I have nothing to add. Ten changes.

  1. Gates are rulers. Each registers sound cases and mutants, or it is
     UNQUALIFIED. Its author's mutants are not enough: an attack by a
     second author is part of qualifying it (section 2).
  2. Five verdicts, not four, and a rule for combining them (section 2).
  3. Attainability is computed by the gate from design counts, and
     refuses a run on day 1 (section 6).
  4. The kit's answers are per claim, every cell of every receipt is
     registered, and the genuine positive is a member (section 12).
  5. No single ruler for nested improvement. A certificate says what
     crossed a boundary. A nested claim names the class it excludes
     (section 5).
  6. The package's nine frozen choices become a registered setting
     that a gate checks, and a contrast changes one thing (section 6).
  7. Whole runs are compared: what the world delivered and the
     organism's state at every step, the state straight after the
     observer, and the final state (section 9).
  8. Reports are replayed on the registered seeds, not believed, and a
     verdict travels with its registered setting (sections 10 and 13).
  9. Organisms get 40% of effort and the first gates are smaller
     (section 15).
 10. Every gate lists faults it is known not to catch, the test suite
     is scored by someone who did not write it, and the design has
     falsifiers that can fire (sections 2 and 17).

TERMS
--------------------------------------------------------------------------------
    physics          the rules a kind of organism runs on
    isomer           the same capability built in another physics
    ruler            a measurement with a registered verdict
    gate             a check that admits or refuses a run or a claim
    receipt          the file a run writes: its numbers and the hash of
                     its code
    cell             the registered combination a claim is conditional on
    setting          the nine registered choices of section 6
    positive         an organism known to have the capability
    impostor         an organism built to look like one and not be one
    kit              organisms with a registered answer per claim
    mutant           a case broken on purpose, which a gate must reject
    sound case       a case with no fault, which a gate must not accuse
    known escape     a fault a gate is known not to catch, kept on record
    key              a hidden object drawn at random, so that no
                     inherited state can contain it
    boundary         a point in the world's nesting that information may
                     or may not be carried across: between tasks,
                     families, epochs, lives
    class exclusion  a score too high for every member of a named class
                     of organisms, whose best score is computed exactly
    certificate      a class exclusion at a boundary, stated in bits
    facet            one line of evidence in a claim, with its verdict
                     and its source
    section 19       O's test of the recursive claim, on three stores: S
                     solves a task, U builds S, V builds U
    strong claim     O's recursive extension: what was built improves the
                     process that builds later learning machinery
    cargo            task content carried from one learner to the next
    clamp, swap      B's interventions: hold a learner fixed, or exchange
                     it between organisms with different histories
    W0, W1, W2       O's tiers of worlds: exact, economic, open-ended
    R0 to R10        the candidate architectures of the portfolio
    Track A          the candidates that are programs with addresses

--------------------------------------------------------------------------------
1. DECISION
--------------------------------------------------------------------------------
Keep the observatory. Build it as a thin federation of native runtimes
joined by shared contracts. In the package's words: "The tunnel
standardizes accountability, not ontology."

    shared                               native to each physics
    -----------------------------------  -------------------------------
    registered cells and settings        dynamics and state
    custody and exposure records         interventions and their shams
    resource vectors, native and host    search operators
    receipts and verdicts                capture, restore and replay
    known-answer panels                  what counts as a step
    claim records

No universal runtime, simulator, scorer or event store. A physics that
cannot support an operation has its claims capped. It is not shut out
(B: "Missing capabilities cap claims").

--------------------------------------------------------------------------------
2. ONE RULE AT THREE LEVELS
--------------------------------------------------------------------------------
Nothing has authority until it has passed a sound case and rejected a
broken one.

    level    what it is                sound case        broken case
    -------  ------------------------  ----------------  ---------------
    RULER    measures an organism      designed or       matched
                                       found positive    impostor
    GATE     admits a run or a claim   sound case        mutant
    REPORT   states a result           numbers           a planted wrong
                                       recomputed from   number or quote
                                       receipts

A thing with no sound case or no broken case is UNQUALIFIED at its
level, and nothing above it may raise a claim.

O has this rule for organisms and, in one sentence, for critics: "A good
audit system must be able to reject persuasive false accusations." The
package extends it to claims, and its charter asks reviewers for
mutants. Neither makes it a condition on every gate or on the write-up.

WHO WRITES THE BROKEN CASES. Not only the author. The trials so far
(RUN; attack/):

    version of    broken cases   what readers then found
    my harness    registered
    -----------   ------------   ---------------------------------------
    one           62, all mine   by my count of the reader's scripts,
                                 65 of its 71 broken cases got through;
                                 22 of 25 one-line changes to the gates'
                                 logic went unnoticed by the tests
    two           148            a passing fault outside the list of
                                 known escapes in every one of 21 gates;
                                 34 of 44, 20 of 32 and 26 of 36 changes
                                 unnoticed
    three         215            by the second reader alone, fifteen
                                 passing faults on no list, in twelve
                                 gates, and one in the next experiment;
                                 12 of 26 and 20 of 54 changes unnoticed
    three, as     258            not read again
    amended

So:
  - a gate is qualified by its sound cases, its mutants, AND an attack
    by someone who did not write it;
  - what the attack finds is to become a registered mutant, or, if the
    gate cannot catch it, a KNOWN ESCAPE: run, pinned by a test, and
    listed. Here most of it has; the rest is in the readers' reports.
    The list is never complete, and says so;
  - the tests of a gate are probed: change its logic one line at a
    time and count what they notice. The figure that counts is the one
    taken at first sight, on changes written by someone else after the
    tests. A figure taken after the tests were extended to those same
    changes says only that those holes are closed.

FIVE VERDICTS
    PASS           a qualified gate ran on complete inputs and its
                   registered pass condition held
    FAIL           the same, and its registered fail condition held: a
                   defect is shown
    INDETERMINATE  the same, and neither held: the evidence is
                   insufficient. A registered outcome, not an error
    BLOCKED        the gate could not run: an input or a precondition is
                   missing. It says nothing about the object
    UNQUALIFIED    the gate has no authority here: it lacks a known
                   positive or negative for this physics or claim, or
                   has never been shown able to fail

Only PASS moves a claim up. When several gates feed one decision the
combined verdict is the worst reason for not passing: FAIL, then
BLOCKED, then UNQUALIFIED, then INDETERMINATE. Reports keep the four
apart. BLOCKED and UNQUALIFIED are not evidence of absence. FAIL is.

A NEGATIVE IS EARNED LIKE A POSITIVE. A ruler says no only when the
score is too low for the weakest positive it is registered to detect. A
score between its yes and its no is undecided, and the gate returns
INDETERMINATE. Not finding something is not a no.

--------------------------------------------------------------------------------
3. WHAT MAY BE CLAIMED, AND WHAT STANDS BEHIND IT TODAY
--------------------------------------------------------------------------------
    claim                                  its ruler today
    -------------------------------------  -----------------------------
    retention across a named boundary,     answered nine designed cells
    in bits, where the world has a key     of my run 4 correctly; one
                                           world, one author
    combination of parts acquired          UNQUALIFIED: simulated only
    separately, where the world has keys   (section 5)
    an economic advantage of development   no W1 world exists
    in a stated W1 cell, or its absence
    nested improvement relative to a       no ruler; B's interventions
    named class, at a tested depth and     are untested
    boundary
    the strong claim                       FAIL at all three settings
                                           tried

B's wording for the scope of a nested claim: "at the tested depth,
boundary and task population". Not recursive sagacity. The package's
line stands:
"RECURSIVE_SAGACITY_RULER = DETECTION_UNQUALIFIED". The form of a report
is the package's: "nested improvement, order k, setting S,
acquired-information estimate I, lifecycle cost C". I add one field: the
class that was excluded. A claim record without it is not rendered.

--------------------------------------------------------------------------------
4. AXES
--------------------------------------------------------------------------------
AS THE PACKAGE, in my words:

    ORDER      which regularity is used, defined by how the WORLD is
               nested. Read from behaviour.
    RETENTION  what information survives a named boundary or
               perturbation and is used afterwards. A curve; and, where
               the world has a key, a lower bound in bits.

A registration names the boundary. The numbers 1 to 4 are a labelling:
the first reader argued that my own run with keys can be called order 2
or order 3, depending on what one calls a task.

ORIGIN (chosen among inherited alternatives, built by a fixed builder,
or built by a changed builder) stays an open measurement problem. The
package: "Do not infer this from write ancestry or memory size alone."

NEUTRALITY is a property of a ruler, measured on the panel of section 8.
It is not an axis of organisms.

--------------------------------------------------------------------------------
5. NESTED IMPROVEMENT: WHAT A CERTIFICATE CAN SAY
--------------------------------------------------------------------------------
WHAT EXISTS (RUN, preregistered, in my review). A fresh 44-bit key per
life, six families per life, an exact bound of 3.38 correct of 16 for
any organism that carries nothing across families, 2,000 lives per
organism. Six designed organisms were certified at 0, 0, 1.44, 9.46,
23.39 and 38.99 bits, in the order of what they hold. The ruler looks at
answers only, so it works in a physics that cannot be cut apart. It
needs a history of other keys as a control. Without it an organism that
hides an inherited key is certified.

WHAT WENT WRONG IN MY FIRST DRAFT. It called the same certificate, taken
at a second boundary of a deeper world, a ruler for nested improvement.
The first reader simulated that world and refuted it. The world: per
life a key, per epoch a rotation of the input, per family an offset of
the output. Scores of 16 in the first family of a later epoch, where the
bound for carrying nothing across epochs is 3.38 (my re-run, 300 lives;
RUN, exploratory; harness/rso_harness/ladder.py):

    carries nothing ................................... 3.42
    one cached table, 256 inherited re-indexings ...... 13.80
    one cached table, 16 inherited offsets ............ 4.16
    the same, when the epoch adds an offset instead ... 15.07

The second organism has no notion of an epoch and learns nothing about
the key after its first family. It finds each family's 8 bits by trying
its 256 re-indexings against feedback. The reader's own run, at 3,000
lives, gave 13.79 for it.

WHAT A CERTIFICATE SAYS. Information acquired in this life crossed this
boundary, at least so many bits. Nothing more. In particular:
  - it does not say that anything was acquired at the level of the
    boundary: the cache above crosses the epoch boundary with one table;
  - it does not tell choosing from building. An organism that picks
    among many inherited alternatives by feedback acquires bits by
    picking, and my review withdrew its attempt to draw that line: "a
    selector with many indices is an acquirer";
  - NOT_SHOWN is the absence of a yes. The third organism is NOT_SHOWN
    at 300 lives, and the reader found it CARRIED at 4,000.

THE GENERAL POINT (ARGUED; it may be wrong). A rule for acquiring things
at one level is content at the next level up. With no limit on what is
inherited, a fixed rule with enough carried content produces any
behaviour. So a claim from behaviour needs two things registered before
the run: a limit on inheritance, and the class of organisms it excludes,
with that class's best score computed. Then the claim is as wide as the
class and no wider. Three consequences.

  - There is no behavioural ruler for the strong claim as O words it,
    and I do not expect one. I withdraw my draft's suggestion that an
    organism found in shallow worlds and tested in deeper ones would
    earn it: that decides by pedigree, which is the fault B found in
    the portfolio's rule about libraries.
  - B's tests (clamp and swap the learner across histories; ask whether
    the same state and evidence give a different update) are relative
    to the interventions a physics allows, and B says so. Where the
    split cannot be made it caps the claim.
  - MY READING, NOT B'S: both repairs give a claim relative to something
    registered. I write that as one rule: NAME THE CLASS YOU EXCLUDE AND
    COMPUTE OR MEASURE ITS BEST SCORE. B's nearest sentences are "A
    clean fixture result qualifies only the tested attack classes." and
    "Equivalent behavior under relabeling must not gain a claim rung."

WHAT THIS BUYS: COMBINATION ON AN UNSEEN PAIR (RUN, exploratory; same
file). Per life, three random tables and three random moves, each a
permutation of 16 symbols. A family is a pair, shown as a label; its map
is the move applied to the table. The life shows eight of the nine pairs
and then the ninth. The ninth map is fixed by three of the maps shown:

    map(2,2) = map(1,2) o inverse of map(1,1) o map(2,1)

and by no two of them. Given any set of shown families that does not
link table 2 to move 2, the ninth map is exactly uniform. The second
reader proved this and checked it by enumeration at three symbols.

THE CLASS EXCLUDED: organisms whose state, when the ninth family begins,
depends only on shown families that do not link its table to its move:
on any two of them, for instance. Their best expected score is 3.38 of
16, exactly. An organism that keeps all eight tables is outside the
class even if it never combines them. Rows two and three below are two
such organisms. Their scores are measurements, not a bound.

THE CONTROL: the eight families shown come from another key under the
same labels. Within a life the organism cannot tell the two arms apart
before the ninth family. In the control the bound holds for every
organism, so one that beats it there got its answer from outside this
life.

WHAT THE CONTROL DOES NOT DO. It guards only against a leak that reaches
both arms alike. The second reader built an organism that keeps last
life's nine tables and uses the ninth only when this life's eight repeat
them. Where the life's own key is reused and the control's is drawn
afresh, the two arms call it COMBINED, and it combines nothing (last
row). So the world also keeps custody of its keys: every life's key is
hashed, and a run in which one repeats is refused whatever the arms say.

Scores of 16 on the ninth pair (300 lives):

                                                  ninth pair   control
    carries nothing                                  3.48        3.48
    every table seen, 256 fixed re-indexings         3.43        3.50
    every way of combining two tables                3.45        3.49
    all 512 ways of combining three, no label read  13.46        3.48
    composes the three its label points to          16.00        3.49
    hides last life's answer; one key in both arms  15.96       15.96
    watches for a repeated life; own key reused     15.96        3.46

WHAT A SCORE ABOVE THE BOUND SAYS, where the keys were fresh.
Information from at least three families, shown separately, was combined
in this life. It says nothing about how. The fourth organism reads no
label and tries every inherited way of combining three kept tables
against feedback. It is a selector over inherited procedures working on
memorised tables, and the kit table of section 12 has both of those as
negatives for reuse of built parts. So this certificate is not a ruler
for reuse. It does not tell choosing from building, and it does not
tell an inherited composing step from one acquired in the first eight
families. The first reader built that organism against my second draft,
which had claimed more.

WHAT A CERTIFICATE CANNOT DO. It certifies bits acquired in a life, at a
boundary, against a named class. It does not say how they are stored or
found. It needs a key, so it does not apply to worlds without one. Both
simulations here are exploratory: no registered verdict, one author,
designed organisms. Document 3, section 8 says what a registration
still needs.

--------------------------------------------------------------------------------
6. THE CELL, THE SETTING AND FOUR RULES
--------------------------------------------------------------------------------
THE CELL. The package's eight coordinates: physics, search, world,
development, boundary, resources, measurement, exposure. O's eight had a
selection pressure where the package has exposure. I follow the package
and require the search field to state its pressure; nothing checks that.
To these a gate adds what it needs in order to refuse: the adapter; the
independent unit (a life, a world, an ecology; B: "For shared niches the
independent unit is the world/ecology"); design seeds and registered
seeds, as integers, disjoint, none repeated, one registered seed per
unit; descriptions that are not placeholder words; a verdict table that
is total and whose every outcome is reachable; for each answer expected
from a known case, the design runs behind that case, as counts; the hash
of the code; the time of registration.

THE SETTING. Any claim that history lowers a later cost registers nine
choices before the run (the package's list). My review found the first
five open in section 19 and added the sixth; which organism passed
changed with what family A was and with how the later families differed
from it.

    1. cost                what is counted; no budget cut-off
    2. later families      how B, C, D, E differ from A and each other
    3. content reset       what is cleared, and that it is cleared
    4. sham                what it removes; shown able to fail
    5. family A            one family or a curriculum
    6. wrong history       what makes a history wrong in this setting
    7. effect threshold    the factor or margin
    8. power               probability of each registered answer
    9. amortization        how many later families pay for development

FOUR RULES.
  ATTAINABILITY   no run starts unless every registered answer has
                  probability at least 0.99. The gate computes it from
                  the verdict table and from design counts, taken at the
                  worse end of their exact 99% interval. A power that is
                  only declared is not read. The design counts are still
                  a declaration: the gate cannot see whether those runs
                  were made. (Gates G1, G2.)
  ONE VARIABLE    a contrast named after a variable differs in that
                  variable only. Otherwise the claim names every
                  difference, or the 2x2 is run first. (Gate G10.)
  CONDITIONS      a verdict is quoted with its cell, its registered
                  setting and the class it excludes, or not at all.
                  (Gate G12.)
  SELECTION       any filter on which worlds are used is registered, and
                  one unfiltered run is reported beside it. (No gate
                  yet.)

--------------------------------------------------------------------------------
7. THE RUNTIME CONTRACT
--------------------------------------------------------------------------------
AS THE PACKAGE: eight declarations (adapters, inheritance channel and its
dial, perturbations, capture and restore, cost in a native unit with
host cost beside it, interventions with shams, a tracer, search
regimes), and its rule that a runtime need not expose pointers, modules,
a split into fast and persistent state, V, U and S, or a lineage graph.
Three additions.
  - A ninth declaration, from B: a capability profile saying which of
    the eight the runtime supports. A missing one caps claims.
  - No single score for cost (B).
  - What a run is: what the world delivered at each step, the native
    state after the step and again straight after any observer, and the
    final state of both.

--------------------------------------------------------------------------------
8. ENTRY, PANEL, NEUTRALITY
--------------------------------------------------------------------------------
TWO DOORS, AS THE PACKAGE. Any physics may be explored. Before a null is
read in it, a ruler that looks inside it is trusted, or a search
campaign is funded, it needs a known answer. Door one: a designed
positive and a matched impostor. Door two: a positive found by blind
search and certified by class exclusion.

THE PANEL. One bounded capability, first one bit across a gap and then a
mapping, in four unlike forms: a stored word (thin Track-A machine), an
attractor (plastic or recurrent network), a packet in flight (message
ring), a spatial pattern (lattice). Each with a matched impostor: the
same kind of machine holding something other than the cue. Four things
the first version of my panel lacked:

  - REGISTERED THRESHOLDS. Perfect positives and impostors at chance are
    answered alike by any threshold between them, so a wrong bound
    passes. On the toy panel the organisms alone admit any bound from
    0.342 to 0.686 where the truth is 0.5. The lower end is set by the
    best block of impostor trials (41 of 64), the upper end by the worst
    (25 of 64). So the panel also holds scripted scores at each edge of
    each answer. They hold the ruler's arithmetic to the registered
    bound within 0.001. They cannot show that the registered bound is
    the true one: a wrong bound registered with matching thresholds
    passes. The bound is derived, and derived again by a second author.
  - A WEAK POSITIVE, right 15 times in 16, which the ruler must still
    call a positive. It fixes what a negative means (section 2).
  - ONE RULER BUILT TO BE PHYSICS-SPECIFIC, which the neutrality gate
    must flag. Without it the gate has no known negative.
  - A SECOND AUTHOR'S ISOMERS by day 45, written without sight of the
    rulers. Whether two physics are unlike, and whether an organism is
    of the physics it is entered under, are declarations. The gates
    read names. The first reader passed a physics-specific ruler as
    shared by giving three stored-word machines three names.

NEUTRALITY. A ruler is SHARED only if it returns the known answer on
every positive and every impostor of at least three physics. Otherwise
it is PHYSICS_SPECIFIC, with the list of physics it is valid in. That is
allowed. It supports no claim across physics.

--------------------------------------------------------------------------------
9. OBSERVATION, RESET, RESTART
--------------------------------------------------------------------------------
AS THE PACKAGE: observer equivalence is qualified inside each physics.
From O: four execution classes (deterministic, stochastic, asynchronous,
continuous). From B: a contract for each class, and a margin registered
from the smallest effect that would matter: "failure to reject a
difference is not enough". Build the first two classes now. What I add
is what is compared, learned one mistake at a time:

  - OBSERVER. One world, every seed in turn, with and without the
    observer, on every organism the observer will watch. Compared:
    what the world delivered at each step, the organism's state after
    the step and again straight after the observer, and the final
    state of both. Scores are not enough, the organism's state is not
    enough, and neither is the state before the next step.
  - RESET. An episode after a reset equals the same episode on a
    runtime that has never run: with no cue and with each cue, after
    each kind of earlier episode. B's list of channels to close:
    messages in flight, optimiser state, marks on the environment,
    clocks and counters, random streams, allocator ids, host caches.
  - RESTART. Capture after every step, the last included, restore into
    a runtime that has just been used, continue. The rest of the run
    must match the uncut run.

WHAT THESE CHECKS DO NOT SEE. State that a runtime hides from what it
reports, when it is used more than one episode later or changed only
every third reset. An observer that misbehaves on seeds that were not
checked.

The package's rule stands beside these: ruler outputs never reach a
search unless registered as a scaffold.

--------------------------------------------------------------------------------
10. SEARCH
--------------------------------------------------------------------------------
AS THE PACKAGE: two quantities, never one, "R_repair(distance, budget)"
and "R_cold(budget)"; cold founders; several unlike targets; at least
two search operators; finite fixtures; intervals on hit rates; tuning
counted as cost. What I add:

  - a null is a bound on reach for the policies run at the budget run,
    with its number: zero hits in n founders bounds the hit rate at
    1 - 0.05^(1/n). It is never a statement about the substrate;
  - of the two operators a null needs, one must be able to cross a
    neutral step;
  - every policy has a positive control at the same budget: a planted
    target on a smooth slope that it reaches 99 times in 100;
  - a report is held to its registration and replayed: landscape,
    budget, start law, policies and founders are those registered
    before the search ran, and the gate reruns that search. A report
    chooses neither its founders nor its budget;
  - estimators are scored against exact reach on a space small enough to
    count, before they are trusted on one that is not. The score has a
    resolution, and it is stated;
  - lifetime learning on and off at equal evaluations. Whether
    development makes a target easier to find is the reach question that
    matters most.

--------------------------------------------------------------------------------
11. WORLDS
--------------------------------------------------------------------------------
W0. Exact calibration. Two things are needed and they are different. The
bound is DERIVED from the generator, twice. And a list of policies that
carry nothing is RUN, and each is shown by an equivalence test to sit at
the bound: a constant, a clock reader, a reader of the probe, an
organism that parks its memory on the environment, and tables fitted to
small views of what the world shows after the cue. The list catches the
leaks it was written for. It is not the class, and it says so when a
view cannot be fitted.

W1. Where development pays, including nowhere (B, and the package).
First one keyed family with exact class values at every dial setting,
the break-even price as the thing measured, and a mandatory inheritance
budget (A). Then B's renewal hidden-law family, which the package puts
first. Comparators are chosen and tuned on discovery data and frozen.
One fresh confirmation in the 90 days. Pilot winners are not
confirmations.

W2. On paper only: its custody split and nothing else.

THE BOUNDARY. Now: every world certifies what the environment lets an
organism write, zero unless declared, and the kit holds the impostor
that parks memory there. After day 30: B's 2x2 of internal and external
retention, as a pilot. As science: only after W1 has exact values, since
a price sweep with no computed optimum finds what it was built to find.

--------------------------------------------------------------------------------
12. THE KIT
--------------------------------------------------------------------------------
V, U and S are a mapping the experimenter registers. They are not an
anatomy every physics must have.

AN ANSWER PER CLAIM. The package's nine members and the positive that
both B and the package ask for. Two claims: reuse (parts built in a life
lower the cost of a later family) and the strong claim. The table says
what a ruler would have to return.

    member                     reuse         strong     built
    ------------------------   -----------   --------   ---------
    procedure selector         negative      negative   runs 1, 2
    library, fixed builder     POSITIVE      negative   runs 1, 2, 3
    search-order selector      negative      negative   run 3
    maturation                 negative      negative   runs 1, 2
    memoriser                  negative      negative   run 2
    world parking              negative      negative   no
    nested compiler cargo      negative      negative   no
    hierarchical selector      negative      negative   no
    flattened twin             as source     as source  no
    genuine learned updater    none          POSITIVE   no

WHAT THE RULERS RETURNED (read from all 26 cells of my four receipts by
gate G10.ruler; the answer for the strong claim is NEGATIVE on every
organism of runs 1 to 3, since each has fixed inherited machinery).

    claim                    setting   verdict       why
    ----------------------   -------   -----------   -------------------
    strong                   run 1     FAIL          yes to a selector
                                                     and a fixed builder
    strong                   run 2     FAIL          yes to a fixed
                                                     builder
    strong                   run 3     FAIL          yes to a selector
                                                     of search orders
    bits across families     run 4     PASS          right on 9 cells:
                                                     4 yes, 5 no
    bits, two boundaries     none      UNQUALIFIED   nothing registered
                                                     has been built
    combination              none      UNQUALIFIED   nothing registered
                                                     has been built

FOR REUSE NO RULER HAS BEEN CHECKED. My runs do not settle a registered
answer per cell. At run 2 the steps said yes to the library builder and
no to four variants of it that fail for other reasons: cost, a hidden
copy, a harmful sham, a history off its targets. The result of run 3
follows its curriculum, as my review found. An earlier version of this
table gave verdicts for reuse. They changed with which cells I had typed
in, and the second reader showed it.

A ruler has to reject the negatives and accept the positives. B's
wording for the second half: reject a ruler that "vetoes a valid
conventional mechanism by pedigree".

RULES. The first five are B's. Only the last of the seven is tested by
something that runs (gate G9.clauses).
  - Freeze the update law of U, not a snapshot of it. Its declared
    runtime dynamics and the learning of S go on.
  - Keep V out of the C assay when the mediated path is the claim.
  - Control cargo with fixed-updater controls that carry equivalent
    priors, where that can be done.
  - A flattened twin gets the same behavioural verdict as its source.
  - Rebuilding a mechanism in another substrate tests for artefacts of
    the first substrate. It is not evidence of origin or of order.
  - Define the wrong history for the setting. Where the right history
    shares no part with the targets it is a wrong history too, and no
    organism can gain from one and not the other.
  - Every clause of every conjunct has a cell in which it holds and a
    cell in which it fails while the other clauses hold. In my run 2,
    4 of 13 clauses fail in no cell and only 2 fail by themselves.

--------------------------------------------------------------------------------
13. CLAIMS
--------------------------------------------------------------------------------
A claim is a record of facets. Each facet holds a verdict and names
where it came from. The level is computed and can go down. The levels,
four of the kinds and the ceiling without an exact null are the
package's. Added here: the rule that computes the level, three kinds
(ORIGIN, ECONOMY, NESTED), a source on every facet, and the excluded
class.

    L1 qualified    registration, power, detection, demand,
                    independence, exposure, resources
    L2 robust       L1 and: exact null, attack round, custody, second
                    implementation
    L3 reproduced   L2 and: reproduced by another author in another
                    physics or world family
    L4 predicted    L3 and: a quantitative relation stated in advance
                    for a new cell, then confirmed

Beside the level, the KIND, and what each kind needs at every level:

    EFFECT       nothing more
    TRANSFER     a new family: another generator, not new seeds
    MECHANISM    an intervention with a matched sham
    ORIGIN       a cold start, and a bound for the class that only
                 chooses among inherited alternatives
    ECONOMY      lifecycle cost, and comparators frozen before the data
    NESTED       retention at the boundary, mediation, a cargo control
                 and a flattened twin. Retention alone is not enough
    LAW          a prediction registered before the data

A claim with no exact null stops at L1: the exact-null facet is needed
at L2. An absent facet blocks. Among several reasons for not standing,
the worst is reported. When a facet is withdrawn the level is
recomputed. A claim is rendered with its cell, its registered setting,
the class it excludes and the reason it stands no higher, or not
rendered. What the gate cannot see: whether a facet's source was run,
and whether the class named is the right one.

--------------------------------------------------------------------------------
14. PORTFOLIO
--------------------------------------------------------------------------------
The package's portfolio has three statuses (CATALOGUED,
QUALIFICATION_FIXTURE, ACTIVE_RUNTIME), shortened here. Its own labels
for R3 and R7 are NEXT and RETIRE; the rows below are mine.

    R0     ACTIVE       ideal observer; in-context learner;
                        online-gradient learner, with the simple
                        fixed-topology plastic network inside it (B)
    R1/R2  ACTIVE       one thin kernel with switches; R2 splits off if
                        its author shows the switches misrepresent it
    R3     FIXTURE      the attractor on the panel; deep build only by
                        the rule below
    R4     FIXTURE      the lattice pattern on the panel by day 30;
                        campaign by door two
    R5     FIXTURE      the packet ring; engine later
    R6     CATALOGUED   paper design; the case where code and data are
                        one thing
    R7     CATALOGUED   no runtime; rank and precision dials inside R0
                        and R3 (I said retire, B said defer; neither
                        funds it)
    R8     ACTIVE       first, as the kit of section 12
    R9     CATALOGUED   two switches, on R3 and on a lattice
    R10    CATALOGUED   embodied and physical learning (B's compliant
                        body; my flow network)
    foundry             grammar only; a blind census as a measurement

THE SECOND DEEP BUILD. By what has been shown to limit, at day 60:
reach, R3; ontology or locality, R4; state capture, R5. The rule is O's,
B keeps it, and the package adds the third branch. It has no thresholds
yet, and needs them before day 60. Six entries trace to my design in
whole or part (R1, R3 with ASTRA, R5, R6, R7 and the lattice arm of R4);
R3 and R4 trace to ASTRA's. Neither reviewer chooses.

--------------------------------------------------------------------------------
15. NINETY DAYS
--------------------------------------------------------------------------------
ALLOCATION. Percent of effort. A judgment.

    tunnel core and qualification automation ............... 30%
    running and analysing experiments ....................... 15%
    known-answer organisms and the kit ...................... 15%
    candidate runtimes (R0 12, Track-A kernel 13) ........... 25%
    independent challenge and second implementations ........ 10%
    blind census ............................................ 5%

Organisms of every kind get 40, where the package gives 30 and the two
reviews 45 and 40. The difference comes out of the tunnel core and the
running of experiments.

GATES. Each is a list of checks that code can decide. The harness holds
toy versions of some of them. None is built for a real runner yet.
  GATE 15  The runner refuses unregistered and underpowered runs.
           RETAIN-1 with its derived bound. Two physics on the panel
           (stored word, packet ring), each with an impostor, the weak
           positive and the registered thresholds. Reset, observer and
           restart tests reject their mutants. R0's ideal observer.
           Smaller than the package's Gate 15 on purpose.
  GATE 30  Four physics on the panel, the lattice among them. Each
           ruler's scope measured; the physics-specific ruler flagged.
           The five built kit members ported; world parking added. A
           second adapter. A second author has attacked every gate in
           use with at least five broken cases each, and has scored the
           tests with at least 30 one-line changes.
  31-45    The boundary 2x2 as a pilot.
  GATE 45  Neutrality decided: if after one repair round a shared ruler
           still returns a wrong answer, cross-physics comparison is
           suspended. A second author's isomers on the panel. Repair
           reach and cold reach on the Track-A kernel, scored against
           exact reach. First W1 family with exact class values,
           registered.
  GATE 60  ONE confirmation frozen: cell, setting, comparators, unit,
           power, custody. One world and one ruler implemented a second
           time by another author. The second deep build chosen by rule.
  61-75    The confirmation is executed.
  76-90    Independent challenge. Demotion tests. One found organism per
           physics, by door two. The census, if GATE 30 was on time. The
           seven closing outputs of the package's plan.

WHAT SLIPS, in this order: the census; the boundary pilot; the found
organisms; the second deep build. What does not slip: GATE 15, the
second author's attack, and the single confirmation.

THE OPERATOR decides four times, at the gates, each from one packet.

--------------------------------------------------------------------------------
16. WHEN IT MAY BE CALLED A CROSS-PHYSICS OBSERVATORY
--------------------------------------------------------------------------------
The package's eleven conditions, and three more:

  - every gate passes its sound cases and rejects its mutants with the
    registered verdicts, and lists known escapes;
  - a second author has attacked every gate and scored its tests, and
    what was found is registered or listed;
  - the report checker has been fire-tested, and every number in the
    acceptance receipt is recomputed from a receipt.

--------------------------------------------------------------------------------
17. WHAT WOULD FALSIFY THIS DESIGN
--------------------------------------------------------------------------------
  1. NEUTRALITY. At day 45, after one repair round, a ruler declared
     shared still returns a wrong answer on some positive or impostor.
     Then no cross-physics comparison is read, and one physics goes deep.
  2. COST. At day 90 the tunnel and its automation have taken more than
     half of all spend, and fewer than six registered cells hold a
     qualified effect or a bounded negative. Then cut the tunnel to
     registration, exact bounds and receipts.
  3. IDLE GATES. By day 90 a gate has run on at least 20 real
     registrations and returned PASS every time. Then remove it, or
     show a mutant from real work that only it rejects.
  4. SECOND AUTHORS ADD NOTHING. Twice in a row, a second author's
     attack finds no broken case that a gate passes, and fewer than 1
     in 10 of at least 30 one-line changes to gate logic go unnoticed
     by the tests. Then the attack is cut to a spot check. So far no
     read has come back empty, and the tests missed 22 of 25, 34 of 44,
     20 of 32 and 26 of 36 changes at first sight, then 12 of 26 and 20
     of 54 on version three.
  5. CONVENTIONAL SUFFICES. On kinds never met in training and at twice
     its training horizon, R0 matches every certified cell of every
     candidate at lower total cost. Then unfamiliar physics are not
     justified at this scale.
  6. THE COMBINATION CERTIFICATE IS BLIND. In a run whose custody check
     passed, a second author's organism whose answer on the ninth pair
     does not come from this life's families is called COMBINED. Then
     the certificate is withdrawn, and claims about structure stay at
     L1. The same if, in a registered run, an organism of the excluded
     class scores above the bound: that can happen only if the world
     leaks. An earlier wording of this falsifier, without the custody
     check, was met once (section 19).

--------------------------------------------------------------------------------
18. NOT BUILT IN THIS ROUND
--------------------------------------------------------------------------------
AS THE PACKAGE: no universal runtime; no full R4, R5, R6 or R9 engine;
no R7; no W2. AS B, in its list of what not to build: no all-event
store, no foundry engine, no automatic promotion pipeline, no single
score for sagacity or scientific yield. And mine: no ruler that requires
a conventional learner to lose, or a library to be a fake. Nothing named
for the strong claim.

--------------------------------------------------------------------------------
19. LIMITS
--------------------------------------------------------------------------------
  - A design. Its sources are model outputs, and one of them is mine.
    Their agreement is not evidence.
  - Section 5 has been wrong three times. The first draft read a
    retention certificate as nested improvement. The second read a
    combination certificate as a ruler for reuse of built parts. The
    third said its control catches an answer that does not come from
    this life: the second reader's organism passed both arms where one
    arm's key was reused, which met falsifier 6 as it was then worded.
    Each was shown by a reader's simulation. The present wording claims
    less, and adds a custody check that no reader has attacked.
  - The general point of section 5 is an argument, and the rule that a
    nested claim names its class is my reading of A and B. Neither has
    been tested.
  - What runs is a toy: four physics by one author, one world, no noise
    (document 3). It shows that the gates can pass and fail, and lists
    29 faults they do not catch. The list is not complete.
  - What was changed after the final round of reading was checked by
    code only. No reader has seen it.
  - The bits certificate has one preregistered run, on designed
    organisms. The two simulations of section 5 are exploratory.
  - The strong claim has no ruler. This design does not supply one and
    says it does not expect one from behaviour alone.
  - Five of the seven files of the original package never reached me or
    B. I did not read B's design, or any design other than my own.
  - The percentages are judgments.

Bottom line, to confirm or contest: can anyone state a nested claim that
does not name a class it excludes?
================================================================================
END OF DOCUMENT 2
================================================================================
