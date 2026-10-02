================================================================================
PHASE 3 HARDENING -- DOCUMENT 1 OF 3
TWO REVIEWS AND ONE HARDENING PACKAGE: COMPARISON AND SYNTHESIS
================================================================================
Prepared:    2026-10-02 (UTC)   FABLE-5.1 (seat Dionysus)
Compares:    A  my review, docs/phase3/review/FABLE-5.1/ (ff1d7f0f4)
             B  the review by Enceladus (ASTRA-6.0), branch
                enceladus/rso-review-2026-10-01 at f4d9e72d9
             C  the hardening package v0.2 by ChatGPT 5.6 (five files)
             O  the two documents A and B reviewed (see READ FIRST)
Companions:  02 hardening design v0.2, my version
             03 test harness specification, my version
             harness/  a reference harness that runs
             attack/   the adversarial reads of this package
Location:    docs/phase3/hardening/FABLE-5.1/
Headline:    THE TWO REVIEWS AGREE ON THE SHAPE AND ON THE FIRST FAULT.
             MY REPAIR OF IT WAS SHOWN INCOMPLETE BY A RUN. ASTRA'S IS
             UNTESTED AND PROMISES NO UNIVERSAL DETECTOR. THE PACKAGE
             MERGES THE TWO FAIRLY. ITS HARNESS DID NOT REACH ME. VERDICT
             ON ITS DESIGN: REPAIR.

READ FIRST
--------------------------------------------------------------------------------
WHAT WAS REVIEWED. O is two documents: the wind-tunnel design v0.1 (a
shared rig for measuring candidate architectures, called the Recursive
Sagacity Observatory, RSO) and a portfolio of ten candidates, R0 to R9.
A and B are independent reviews of O. C was written from A and B and
hardens O into a v0.2.

WHAT I READ. B: the five files of the review directory the operator
named, and nothing else in that worktree. C: five files found in the
operator's Downloads folder (design, harness spec, portfolio, 90-day
plan, next review charter). The operator pasted nothing, so I identified
C by title and time. Hashes are in
roles/Dionysus/prompts/2026-10-02_hardening_v0.2/.

WHAT DID NOT REACH ME. C's design ends: "The reference harness in this
package implements a minimal executable form of these rules." The
archive I found holds five empty folders, two of them compiled-code
caches, and no file. There is no file numbered 04. So a harness probably
ran where C was made, and it did not reach me. Its status here is NOT
VERIFIED.

MY STAKE. I wrote A. Where B is right against A, I say so and change my
position. Sections 4 and 7 are my own case and a third reader should
check them.

EVIDENCE. Three models agreeing is not evidence. Lines below are marked
RUN (a receipt exists), ARGUED (reasoning only) or FACT (checked against
a source). Most of both reviews is ARGUED.

HOW THIS WAS CHECKED. Three adversarial reads and a final round, all by
readers of my own model family. Their briefs, reports and scripts are
in attack/.
    first read, of the draft ........ 11 blocking and 46 major defects
    closure read, of version two .... of those 57: 45 closed, 11 partly,
                                      1 open; 1 blocking, 13 major new
    second read, by a fresh reader .. 8 blocking and 38 major defects
    final round, of version three ... both readers again: 2 blocking
                                      and 9 major, new or still open
This is version three with the final round's findings applied. The
defects were of three kinds: statements unfair to B or to C, claims
stronger than what ran, and faults the harness let through. Section 13
says what has not been re-read.

TERMS
    ruler       a measurement with a registered verdict
    gate        a check that admits or refuses a run or a claim
    receipt     the file a run writes: its numbers and the hash of its code
    positive    an organism known to have the capability
    impostor    one built to look like a positive and not be one
    isomer      the same capability built in another physics
    kit         designed organisms, each with a registered answer for
                each claim
    mutant      a case broken on purpose, which a gate must reject
    section 19  the part of O that tests the recursive claim: thirteen
                steps on three stores. S is the state that solves a
                task, U is what builds S, V is what builds U
    strong      O's recursive extension: what was built improves the
    claim       process that builds later learning machinery
    cargo       task content carried from one learner to the next, as
                opposed to a change in how learning is done
    clamp,      B's interventions: hold a learner fixed, or exchange it
    swap        between organisms with different histories
    W0, W1, W2  O's three tiers of worlds: exact calibration, economic,
                open-ended
    Track A     the candidates that are programs with addresses (R1, R2)

--------------------------------------------------------------------------------
1. THE TWO REVIEWS SIDE BY SIDE
--------------------------------------------------------------------------------
                   A (FABLE-5.1)                 B (ASTRA-6.0)
    -------------  ----------------------------  --------------------------
    evidence       four preregistered runs and   none new, and it says so:
                   one file of probes, on        nothing implemented,
                   designed toy organisms        nothing executed
    checked by     three adversarial readers,    source anchors; an
                   85 defects in drafts; a       executed consistency
                   checker with 72 checks        check; a read-only
                                                 adversarial pass, its
                                                 seven concerns each
                                                 adjudicated
    verdict        adopt the discipline; not     conditional go for a thin
                   yet a build specification     federation; no universal
                                                 runtime
    authority      exact bounds, and a known     exact truth in W0; beyond
    comes from     answer in each physics        it interventions, custody
                   before it is read             and equivalence margins
    first fault    section 19 passed fixed       write ancestry does not
    named          inherited machinery in        identify recursive order
                   three registered settings
    repair of      six items: fix the open       six items: define V, U, S
    that fault     choices; report the           by interventions; show
                   setting; bound the bits       lifetime origin; freeze
                   acquired where the world      U's law; clamp or swap U
                   has a key; say order k,       across histories, with
                   not recursive; qualify the    fixed-updater controls;
                   ruler; register V, U, S       matched lesions; compare
                                                 with flattened twins
    library        a negative for the strong     not a negative by
    learner        claim, a positive for reuse   pedigree; split in three
    next build     a thin R3, if a gate is met   a tiny R4 specimen by
                                                 days 10 to 15; the simple
                                                 R3 inside R0
    R7             retire                        defer
    boundary       fix it for 90 days            vary it: a 2x2 of
                                                 internal and external
                                                 retention, one cell in
                                                 days 31 to 55
    plan           gates at days 30, 60, 90;     five intervals, each with
                   the first decided by code     an exit decision; one
                                                 fresh confirmation
    reversals      nine: seven with a number,    one per candidate and one
                   two of them with a day;       per interval, in words
                   two in words
    effort         45 tunnel core, 45            30 tunnel, 40 candidates,
                   organisms, 5, 5 (section 10)  20 experiments, 10

B says of its own check: "This is a documentary adversarial pass, not an
independently reproduced scientific result or an external expert
review." The same holds for every read of this package.

--------------------------------------------------------------------------------
2. WHERE THEY AGREE
--------------------------------------------------------------------------------
Agreement between two models is weak evidence. The mark says what stands
behind each point besides the agreement.

  1. A thin tunnel: shared records, native physics. No universal
     runtime, no ten engines, no seat per candidate ............. ARGUED
  2. The section-19 steps can be met without the thing they are
     named for ............................... RUN (A); ARGUED (B)
  3. Promise no recursive positive. Report nested improvement with
     its depth, its boundary and its setting .................... ARGUED
  4. Recovery from a designed organism is not discovery from
     scratch ....... ARGUED (A, B); RUN on toy landscapes (document 3)
  5. Zero hits in n founders bounds a rate at 1 - 0.05^(1/n) and
     nothing more ............................................... FACT
  6. W1 needs frozen comparators and full lifecycle cost ......... ARGUED
  7. A strong R0 that may win; R1 and R2 as one kernel with
     switches; R8 first; R5 and R6 not as engines; R9 as switches  ARGUED
  8. The claim ladder mixes things that should be kept apart ..... ARGUED
  9. Test observer interference inside each physics ............. ARGUED
 10. The old record supplies fixtures, not qualified engines ..... ARGUED
 11. No foundry engine, no open-ended W2, no dashboards in 90 days ARGUED
 12. Five of the seven files of the package were missing for both
     of us ....................................................... FACT

--------------------------------------------------------------------------------
3. WHERE B IS RIGHT AND MY REVIEW WAS WRONG OR THIN
--------------------------------------------------------------------------------
Twelve points. After each: what my version does with it. Four of them
(5, 6, 8 and 12) are rules in document 2 that nothing yet tests.

  1. THE KIT NEEDS A GENUINE POSITIVE, AND A MEASURE OF FALSE REJECTION.
     A already said a library learner is a "legitimate positive for
     reuse of built parts". What B adds is the other half: a learned
     updater that may honestly pass, and a count of how often a ruler
     rejects it. B: "only demonstrated fakes are negatives". My review
     also leaned on the portfolio's blanket rule that a ruler which
     passes library accumulation "is insufficient"; B shows that rule
     collides with section 19's own permission for conventional
     meta-learning to pass. TAKEN: the kit registers the genuine updater
     as a positive. It is not built, so the ruler stays unqualified.
  2. RESETS ARE A CAUSAL ISSUE, NOT HOUSEKEEPING. B's list: "In-flight
     messages, optimizer state, external marks, time, RNG streams,
     allocator IDs and host caches". My run 3 called no content reset at
     all. TAKEN: the reset gate, and three reads' attacks on it.
  3. DISCOVERY AND CONFIRMATION NEED SEPARATE CUSTODY. I kept design
     seeds apart from registered seeds. I still fixed the acceptance
     rule and chose the worlds after seeing design output. TAKEN: the
     custody gate requires the time the rule was fixed and a second
     custodian.
  4. EQUIVALENCE NEEDS A MARGIN. "failure to reject a difference is not
     enough". My twin-run check had no margin. TAKEN: the demand gate
     decides by equivalence, with a third outcome when the data cannot
     say, and the sham audit uses a margin.
  5. FREEZE THE UPDATE LAW, NOT THE SNAPSHOT. A saved U that keeps
     adapting during the test "is not a frozen learning rule". TAKEN as
     a rule in document 2. Nothing that runs tests it.
  6. RECONSTRUCTION IN ANOTHER SUBSTRATE IS NOT DECISIVE BY ITSELF:
     "reconstruction alone proves neither new developmental origin nor
     higher causal order". I had left step 13 alone. TAKEN as a rule in
     document 2. Nothing that runs tests it.
  7. THE UNIT OF ANALYSIS IN A SHARED WORLD IS THE WORLD. "For shared
     niches the independent unit is the world/ecology". TAKEN as a
     required field of the registered cell. No shared world exists yet.
  8. ASK WHERE DEVELOPMENT PAYS, AND ALLOW THE ANSWER NOWHERE: "where,
     if anywhere, does development pay?" My W1 conditions assumed a
     transition and asked where. TAKEN as the wording of W1 in document
     2. No W1 world exists, so nothing that runs tests it.
  9. CAPABILITY PROFILES. "Missing capabilities cap claims". B never
     shuts a physics out. My draft entry rule did, and the second door
     I added was a repair of my own rule. TAKEN: in the neutrality gate
     a physics with no known answer is outside a ruler's authority and
     does not fail it.
 10. VARY THE BOUNDARY EARLY. B asks for a 2x2 of internal and external
     retention, with one cell in days 31 to 55. I deferred all of it.
     PARTLY TAKEN: every world certifies what the environment lets an
     organism write, from day 1; the 2x2 is a pilot after day 30 and
     the second thing to slip (document 2, section 15).
 11. FACETS. B stores seven independent evidence facets. TAKEN: a claim
     is a record of facets, each naming its source; kinds of claim
     (origin, economy, nested) need facets of their own.
 12. COST IS A VECTOR. The sagacity ratio "is not defined at a zero
     denominator". TAKEN as a rule: native and host cost side by side,
     no scalar. Nothing that runs tests it.

--------------------------------------------------------------------------------
4. WHAT MY REVIEW ADDS
--------------------------------------------------------------------------------
I am a party. A third reader should check each.

  1. IT RAN SOMETHING. B's first fault is an argument. Section 5 shows
     that my run 2 reproduces four of the six lines of evidence B says
     its counterfeit would supply.
  2. AN EXACT BOUND WHERE NO IDEAL OBSERVER CAN BE COMPUTED. B has exact
     truth in W0 and, in W1, "small exactly solvable cases and larger
     related cases". Of open-ended worlds it says: "A few strong
     baselines do not bound all cheap policies." Its remedy there is to
     narrow the claim. A adds one tool that stays exact in a large
     world: a key drawn at random per life, which no inherited state
     can contain.
  3. A BEHAVIOURAL ROUTE FOR PHYSICS THAT CANNOT BE CUT APART. Where a
     substrate cannot support clamps and swaps, B caps the nested and
     mechanism claims and keeps the behavioural ones. A gives those
     physics a number they can still earn: bits carried across a
     boundary. It certifies retention and no more (section 5).
  4. A KNOWN ANSWER BEFORE A NULL IS READ IN A PHYSICS. B asks for
     native positive witnesses, in W0 and beyond it. A makes it an entry
     rule with two doors, the second for organisms found by blind
     search.
  5. THE SIX COORDINATE NAMES DEPEND ON HOW STATE IS SPLIT. B flags the
     split itself ("Define intervention scope, not mandatory buffers.")
     and keeps the six names as observational coordinates. A shows
     that some of them need the split and replaces them by two axes
     read from the world.
  6. A RULE THAT LIVED IN A DOCUMENT DID NOT STOP A RUN. B asks that "an
     executable registration must set target effect, equivalence
     margins, independent units, sample size/power, caps,
     multiplicity/sequential policy and stop rules". A's contribution
     is the failure itself: in my design package the first gate had
     power 0.865 and the run went ahead.
  7. NUMBERS ON REVERSALS. Seven of A's nine carry a number, two of
     them a day. The other two are in words, as B's are.
  8. STAKE DISCLOSED. Six portfolio entries trace to my design in whole
     or part, and the build I rank next (R3) is one I share with B. B
     brings forward R4, which traces to its own design, as an early
     specimen. Neither of us should choose the second deep build. O
     already had the right rule; section 7.

--------------------------------------------------------------------------------
5. THE FIRST FAULT, AS AN ARGUMENT AND AS A RUN
--------------------------------------------------------------------------------
B describes a "compiler that launders task cargo": a fixed compiler that
wraps what was learned in new updater objects, so that every line of
section-19 evidence follows the cargo. My run 2 is one member of that
family: a library of parts and a fixed builder. It reproduces four of
B's six lines. It does not build the compiler.

    B's line of evidence (ARGUED)       my run 2 (RUN), in tasks
    ----------------------------------  ----------------------------------
    later acquisition becomes cheaper   313.5 fall to 20.5
    V to U to S write provenance        not measured
    V lesion, sham, rescue              316.0, 12.0 and 16.0
    fresh U and S allocations           not built
    relevant donors help, irrelevant    a donor's library 22.0; a history
    ones do not                         of other parts 323.5
    further transfer to D and E         held, and every target was one of
                                        the 16 pairs of the four parts
                                        just learned

    Setting of run 2: medians of 24 replicates; cost is tasks until a
    procedure is accepted, with no cut-off; factor 4; family A is four
    part families; worlds chosen so that the labels hold.

READ FROM THE RECEIPTS. The harness reads what each ruler returned on
every cell of my four receipts, 26 in all. At each of the three settings
I registered for section 19, the steps said yes to an organism whose
machinery is fixed and inherited: a selector over procedures and a fixed
builder (run 1), a fixed builder (run 2), a selector over search orders
(run 3, under a weaker protocol: no content reset, factor 2). For the
strong claim the ruler FAILS at all three. No positive for the strong
claim has been built in A, in B, in C or here.

WHERE EACH REPAIR STANDS.
  - A's repair includes a certificate in bits against an exact bound.
    The first draft of document 2 stretched it into a ruler for nested
    improvement. The first reader simulated the world I proposed and
    refuted that: an organism that keeps one answer table and tries 256
    inherited re-indexings of it, and learns nothing after its first
    family, scored 13.79 of 16 in the reader's run where the bound is
    3.38 (13.80 in my re-run; RUN, exploratory). The certificate is
    right about what it certifies: information crossed the boundary. It
    says nothing about how. So A's repair is shown incomplete by a run.
  - B's repair has not been run. It separates a changed way of learning
    from the export of answers where the physics allows the
    interventions, and B says what it is not: "it does not promise a
    universal depth detector". Its fixture experiment says: "A clean
    fixture result qualifies only the tested attack classes." Its first
    unresolved question allows that the notion may be relative: "If
    only an operational intervention-relative notion survives, adopt it
    openly and drop stronger ontological language."
  - MY READING, NOT B'S (ARGUED). Both repairs yield a claim that is
    relative to something registered in advance. For B it is the
    interventions that were possible and the attack classes that were
    tested. For A it is a class of organisms whose best score can be
    computed. Document 2, section 5 builds on that reading: a nested
    claim names the class it excludes. B's one sentence nearest to it is
    a control, hedged: "Carry equivalent task-relevant priors in
    fixed-updater controls where feasible."

--------------------------------------------------------------------------------
6. THE SYNTHESIS OF A AND B: POSITIONS I NOW HOLD
--------------------------------------------------------------------------------
    topic            position                               from
    ---------------  -------------------------------------  ----------
    shape            thin federation; contracts shared,     B, O, C
                     physics native
    authority        a known answer before a ruler, a       A, B; C asks
                     gate or a report is believed; an       for attacks;
                     attack by a second author is a         the condition
                     condition of believing a gate          is new here
    strong claim     no qualified ruler; the word is        A, B, C
                     reserved
    what is          retention in bits by boundary;         A, B, C
    reported         mediation where interventions
                     exist; the setting and the cost
    library          a positive for reuse, a negative for   A, B
    learner          the strong claim; answers per claim
    nested claims    name the class excluded                my reading
                                                            of A and B
    resets,          whole runs compared, with margins by   B
    observers        execution class
    boundary         certificate now; the 2x2 as a pilot    A, B
                     after day 30
    second deep      by what is shown to limit; chosen by   O, B, C
    build            neither reviewer
    R7               no runtime; kept as a hypothesis       A, B
    lattice          on the panel by day 30: later than     B, A
    specimen         B's days 10 to 15, earlier than A's
                     day 60
    W1               where development pays, including      B, A
                     nowhere; exact class values; one
                     fresh confirmation
    claims           facets, then level and kind            B, A
    effort           30 tunnel, 40 organisms, 15
                     experiments, 10 challenge, 5 census    B, C

--------------------------------------------------------------------------------
7. WHERE THE PACKAGE'S DESIGN COMES FROM
--------------------------------------------------------------------------------
The attributions to A are mine and should be checked.

    C, design section               from
    -----------------------------   ------------------------------------
    1  thin federation               B (3.1 and its verdict)
    2  strong ruler unqualified      A (its first flaw); B (section 11);
                                     the label is O's
    3  ORDER and RETENTION           A (two axes read from the world)
       ORIGIN left open              B (not from write ancestry); A (not
                                     from the size of a memory)
    4  search inside the cell        O
    5  NEUTRALITY as a facet         C's name; O's question; A's panel
    6  two doors                     A
    7  isomer panel                  A (panel, impostors); B (unlike
                                     specimens before the interface
                                     freezes)
    8  runtime contract              B (3.1, capability profiles); A
                                     (perturbations, inheritance dial)
    9  observer hardening            B (3.2); O (execution classes); A
                                     (ruler output kept from search)
    10 repair reach, cold reach      B (fault 2, section 8); A (section 8)
    11 W1 including nowhere          B; exact class values A and B
    12 boundary 2x2                  B
    13 facets, then L0 to L4         B (facets); A (levels, kind, the
                                     ceiling without an exact bound)
    14 kit of nine                   A (seven members); B (nested
                                     compiler, flattened twin)
       nine frozen choices           A (eight); A and B (amortization
                                     horizon)
    15 strong R0, in order           O and B (R0 may win); A (the order)
    16 acceptance list               both
    second build chosen by evidence  O: "Choose between R3 if the main
                                     unresolved question is
                                     reachability/continuous plasticity,
                                     or R4 if the main unresolved
                                     question is Track-A ontology
                                     dependence."; B ("Neither wins by
                                     calendar alone."); C adds R5

O's question, in its words: "No interface should be called
substrate-neutral until it has operated correctly on at least two
materially different physical realizations."

WHAT C ADDS OF ITS OWN. The ten harness layers H0 to H9, five of which
name the faults to plant. Four gate verdicts as one set, with BLOCKED
beside UNQUALIFIED. Three statuses for a candidate, so that many
hypotheses are kept and few runtimes built. Gate 15 and Gate 45 by name.
A next charter that asks reviewers to attack: "Add at least five
deliberate mutants the harness should reject." I count these as
improvements.

--------------------------------------------------------------------------------
8. WHAT THE PACKAGE LEFT OUT
--------------------------------------------------------------------------------
FROM A. A ruler built to be physics-specific, so that the neutrality
check has a case it must flag. C flags such rulers, and its charter asks
reviewers to "Try to make a physics-specific ruler masquerade as
shared."; its design plants none. The scale check (does a relation
measured small predict a world ten times larger). A cost test for the
tunnel itself. Eight of nine reversal conditions (C keeps neutrality at
day 45). The operator's attention as the budget.

FROM B. Equivalence margins. The frozen update law and the mediation
clamp. A clean twin for every attack and a count of false rejections (C
has one such case: the "persuasive false auditor accusation"). The world
as the unit of analysis. An explicit rule against a universal scalar for
cost (C does carry "native resource unit plus host-cost accounting").
The table of old engines with a forbidden inference for each.
Experiments written as alternative, arms, readout and decision.

NEW IN MY VERSION, IN NEITHER REVIEW. A gate that refuses a verdict
quoted without its setting (C carries the setting in the cell and in the
report line). A rule that an analyst's filter on which worlds are used
is registered; no gate enforces it yet. These are not omissions by C.

--------------------------------------------------------------------------------
9. GAPS IN THE PACKAGE
--------------------------------------------------------------------------------
THE HARNESS: NOT VERIFIED. Its purpose line is right: "The harness
prevents rules from living only in prose." I could not run it. Please
send the files.

GAPS IN THE DESIGN, in order of weight.
  G1. NO RULE THAT A GATE MUST ITSELF BE SHOWN ABLE TO FAIL AND ABLE TO
      PASS. C names faults to plant at five of its ten layers and
      requires that the historical fixtures fire. It also says "A
      missing positive for a ruler means UNQUALIFIED". It does not say
      that a gate with no case it rejects is unqualified too, and it
      asks for sound cases in one place only. Why it matters (RUN): my
      own first harness rejected all 62 broken cases its author wrote.
      A second reader then wrote 71 more, and by my count of that
      reader's scripts 65 of them got through (document 3, section 3).
  G2. ATTAINABILITY ARRIVES IN DAYS 16 TO 30 ("power/attainability
      preflight"). The first isomer runs are in days 1 to 15. It should
      refuse a run on day 1.
  G3. THE KIT HAS NO TABLE OF ANSWERS. The portfolio says "A control's
      expected verdict is claim-specific." No file says which answer for
      which claim, and all nine members are listed as counterfeits. The
      genuine positive that C requires before the strong ruler is
      qualified is not a kit member.
  G4. "Every clause needs a fixture capable of making it false." is
      asked of nested improvement only. Ask it of every conjunction.
      Audited by code, my run 2 has 4 of 13 clauses that fail in no
      cell; my run 3 has 6.
  G5. H3 does not say what is compared. B's contract does. Comparing
      scores passes a broken observer. So does comparing the organism's
      state alone, or every step and not the final state, or the state
      before the next step and not straight after the observer. My
      harness made each of the last three mistakes in turn, and each
      was found by a reader and not by me.
  G6. THE GATE VERDICTS HAVE NO THIRD OUTCOME AND NO RULE FOR COMBINING
      THEM. C has typed third outcomes in two places (INTERVENTION_INVALID
      in H6; a "typed inconclusive" W1 result) and not in the four gate
      verdicts.
  G7. GATE 15 CARRIES EIGHT BUILDS AND TWO RUNS. B's first interval is
      as heavy. A reader of my own draft plan, which put twenty packages
      behind one gate, called it too much for one operator.
  G8. THE WRONG-HISTORY DEFINITION IS FROZEN WITHOUT ITS CONSEQUENCE.
      Where the right history shares no part with the targets it is
      itself a wrong history, and no organism can gain from one and not
      the other.
SMALLER. R3 is "NEXT" in the portfolio and "by evidence" in the plan.
Second observation adapters are "preferably", and a shared claim needs
them. H9 names facets and gives no rule for the level. The numbering
skips 04. O's cell has a selection pressure where C's has exposure; C
does not say the coordinate was dropped.

--------------------------------------------------------------------------------
10. THE THREE ALLOCATIONS
--------------------------------------------------------------------------------
As each source states them, in percent of effort.

    bucket                                    A      B      C
    --------------------------------------  -----  -----  -----
    tunnel core                               45     30     35
    organisms of every kind                   45     40     30
    running experiments, as its own bucket     0     20     20
    independent challenge, second              5     10     10
      implementation, reserve
    blind census                               5      0      5

    A: "tunnel core (runner, worlds, rulers)" 45 | 20 standards + 10 R0
       + 15 kernels | none | 5 | 5
    B: 30 | 12 R0 + 14 R1/R2 + 6 R8 + 8 R4 | 20 | 10 | 0
    C: 35 | 30 runtimes and standards | 20 | 10 | 5

The rows are not fully comparable. A has no bucket for running
experiments: it counts them inside its other rows. B's first row is, in
its words, "30% of authorized engineering/analysis person-hours for the
thin tunnel and qualification fixtures", and it counts its R8 controls
and its tiny R4 as candidates where A and C would call them standards.

What can be said: C matches B on experiments and challenge and A on the
census, and sits between the reviews on the tunnel core. On organisms it
is below both: 30 against 45 and 40. That is a difference of judgment,
not a defect. Mine is in document 2, section 15.

--------------------------------------------------------------------------------
11. ANSWERS TO THE PACKAGE'S OWN REVIEW CHARTER
--------------------------------------------------------------------------------
Verdict on the design: REPAIR. Not REFRAME: it is a sound merge. Not
BUILD: the gaps above come first.

The charter's first instruction is to run "python -m unittest discover
-v". There was nothing to run. I built a reference harness for my own
version of the spec and answer the ten attacks against that. Numbers are
from harness/RECEIPT_harness_v0.json.

  1. FIVE MUTANTS. The harness holds 258, and 50 sound cases. Every
     mutant is rejected with the verdict registered for it: 125 FAIL, 99
     BLOCKED, 25 UNQUALIFIED, 9 INDETERMINATE. Most were written by
     the readers, or after them.
  2. A PHYSICS-SPECIFIC RULER PASSING AS SHARED. The one I planted FAILS
     when declared shared. The first reader then made it pass: three
     stored-word machines under three physics names. The gate counts
     physics by name. A known escape.
  3. AN INCOMPLETE RESET. Seventeen such cases are rejected, eight on
     reset and nine on capture and restore. Three escape: state that a
     runtime hides and uses two episodes later, a reset that leaks on
     every third call, and a hidden count of episodes.
  4. REPAIR PASSING AS COLD DISCOVERY. Rejected three ways: by the
     declared start, by replaying the registered search on the
     registered founders, and by scoring counts against exact reach. On the
     valley landscape exact cold reach is 0.0000 and exact repair reach
     from one flip is 1.0000 under the strict rule.
  5. A MISSING FACET. Promotion is BLOCKED. If another facet has failed
     the verdict is FAIL: the worse reason wins.
  6. THE NESTED GATE. Section 5: for the strong claim, every ruler
     tried said yes to a known negative. For reuse of built parts no
     ruler has been checked at all (document 2, section 12).
  7. A GENUINE POSITIVE FOR THE STRONG CLAIM. Not built.
  8. CAN ONE BE DEFINED WITHOUT SMUGGLING THE ANSWER. From behaviour
     alone, and with no bound on what an organism inherits: no. A fixed
     inherited rule with enough carried content produces any behaviour
     (ARGUED; the reader's cache is one case). With a bound on
     inheritance and a registered class it can: say which organisms are
     excluded and compute their best score. Then the claim is as wide
     as the class and no wider. Document 2, section 5.
  9. ASSUMPTIONS THAT FAVOUR R1 AND R2. Document 3, section 9 lists
     nine in my own harness.
 10. BLOCKED AND UNQUALIFIED AGAINST FAIL. Distinct and tested. The
     fifth verdict, INDETERMINATE, is computed by six gates.

What the charter asks to be returned:
    HARNESS ESCAPES. 29 pinned, at least one in each of the 21 gates.
      Each read found more than the one before had left (document 3,
      section 10).
    MUTANTS ADDED. 258.
    TESTS FIT FOR CI. 110, deterministic, under a minute. About a dozen
      read four receipts of my review and belong with those receipts.
    MISLEADING OR OVERFIT TESTS. After each round the tests were extended
      to notice the changes its readers had made. At first sight they
      missed 22 of 25, then 34 of 44, 20 of 32 and 26 of 36, and on
      version three 12 of 26 and 20 of 54.
    DESIGN CHANGES. Document 2.
    ALLOCATION CHANGES. Organisms 40%.
    STRONG RECURSION. Unqualified; every ruler tried has failed on a
      known negative.
    SMALLEST NEXT EXPERIMENT. Combination on a pair never seen, against
      an exact bound (document 3, section 8).

--------------------------------------------------------------------------------
12. WHERE THE THREE SOURCES LEAVE THE PROGRAM
--------------------------------------------------------------------------------
  - AGREED BY ALL THREE, AND BY ME: a thin federation; no recursive
    positive promised; a strong conventional baseline that may win; the
    kit of counterfeits first. B and C add one fresh confirmation in 90
    days, and I take it.
  - SETTLED BY THIS ROUND OF WORK: a gate tried only by its author is
    not a gate (RUN: every read found faults that passed). A certificate
    in bits certifies retention and nothing about how (RUN,
    exploratory).
  - STILL OPEN, AND NOT SETTLED BY ANY OF A, B OR C: whether nested
    improvement can be told from cargo at all. B's experiment 5 is the
    test. B's plan holds it. C's plan holds part of it: "Expand R8 with
    nested-compiler cargo and flattening attacks."
  - WHAT I ASK OF THE OPERATOR: the files of C's harness; and a second
    author, not of my model family, for the next attack.

--------------------------------------------------------------------------------
13. LIMITS
--------------------------------------------------------------------------------
  - I am one of the two reviewers compared.
  - I identified the package by file name and time, not from a paste.
  - I did not read B's design package, or any original design other
    than my own. B's review is judged as written.
  - The harness is a toy: four physics written by one author,
    deterministic, on one world. It shows that its gates can pass and
    fail. It qualifies nothing about Prometheus.
  - The only new runs are two exploratory simulations inside the
    harness (the two key worlds of document 3, section 8). Neither is
    preregistered. The audits read receipts that already existed.
  - Three reads and a final round, by readers of my own model family.
    Each found what the one before had missed. Another would find more.
  - NOT RE-READ. What was changed after the final round: the corrections
    it asked for in these documents; in the harness, stricter
    registration, a search held to its registration, torture checks on
    the whole panel, audits refused at other sizes than 24, and a
    custody check on keys in the unseen-pair world. These were checked
    by code only: the unit tests, the mutation probe, the checker and
    its fire test. No reader has seen them.

Bottom line, to confirm or contest: is a gate that only its author has
tried to break a gate?
================================================================================
END OF DOCUMENT 1
================================================================================
