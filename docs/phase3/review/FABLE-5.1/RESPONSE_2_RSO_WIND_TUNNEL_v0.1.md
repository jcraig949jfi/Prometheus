================================================================================
PHASE 3 SYNTHESIS REVIEW -- RESPONSE 2 OF 3
REPLY TO RECURSIVE SAGACITY OBSERVATORY v0.1 (THE WIND TUNNEL)
================================================================================
Prepared:      2026-10-02 (UTC)   reviewer FABLE-5.1 (seat Dionysus)
Responds to:   01_RSO_WIND_TUNNEL_DESIGN_v0.1 (24 sections; the file
               number is the charter's)
Companions:    RESPONSE_1 (report to the charter), RESPONSE_3 (portfolio)
Location:      docs/phase3/review/FABLE-5.1/
Headline:      RIGHT DISCIPLINE, NOT YET A NEUTRAL INSTRUMENT.
               Of 24 sections: keep 2 with one addition each, modify 18,
               defer 4 (sections 9, 12, 16 and 17). Nothing is cut; much
               is postponed.

Not provided to me: files 00, 03, 04, 05, 07 of the package. Where v0.1
credits Gemini I could not read the source. A sequencing plan may exist
in file 05. Where I say v0.1 lacks something, I mean this file lacks it.
Three read-only reviewers attacked drafts of this response in turn;
several passages below say what they changed.

TERMS USED IN THIS RESPONSE
--------------------------------------------------------------------------------
    physics           the rules a kind of organism runs on (v0.1 also
                      says substrate)
    ruler             a measurement procedure with a registered verdict
    arm               one condition of an experiment (naive, lesion,
                      sham and so on)
    hooks             v0.1's intervention hooks: points where the
                      harness reads or changes an organism's internals
    carrier           the piece of state that holds a capability
    designed          an organism written by hand to have a capability;
    positive          with its impostor it is a known answer
    impostor          an organism built to look like a positive and not
                      be one
    plant             a designed organism used as a known answer or as a
                      target for search
    isomer panel      one known capability built by design in several
                      unlike physics, each with a matched impostor
    class exclusion   beating the exact best score of a restricted class
                      of policies, at a stated error rate
    interchange       swap a piece of state between two runs and see
                      whose behaviour follows
    counterfeit kit   designed organisms that must NOT earn a claim
    selector          an organism that only chooses among inherited
                      alternatives
    library learner   a fixed constructor that stores procedures which
                      worked and tries them, and pairs of them, first
    in-context        a network with fixed weights; all its lifetime
    learner           learning is in its activations
    census            an exhaustive count over a space small enough to
                      enumerate
    order             which regularity is exploited, by the nesting of the
                      world: within a task (1), across tasks of a family
                      (2), across families (3)
R0 to R9 are the portfolio's candidates (RESPONSE_3).

--------------------------------------------------------------------------------
1. VERDICT IN SIX LINES
--------------------------------------------------------------------------------
  1. The idea of one shared tunnel is right and should be adopted.
  2. Three of its definitions still fix the organism's shape.
  3. Its section-19 protocol has no arm that separates reuse of what was
     built from improvement of the builder, and leaves five choices
     open. In each of the three settings I registered, an organism with
     fixed inherited machinery passed.
  4. Its own rules imply a designed positive in every substrate; the
     second substrate is not yet described with one.
  5. This file gives no order of construction for the tunnel's own
     parts.
  6. Lines 2 to 5 are repairable. Section 4 gives replacement text.

--------------------------------------------------------------------------------
2. WHERE THE TUNNEL STILL DICTATES THE ORGANISM
--------------------------------------------------------------------------------
    Where in 01         What it presumes               Who pays
    -----------------   ----------------------------   -------------------
    5, 6: fast state    two kinds of state             any medium with a
       and persistent                                  continuum of time
       state                                           scales (R3, R4)
    19: V, U, S         levels that can be lesioned    R6 (code is data),
                        apart                          R3 (spread out)
    20: mechanism by    a part that can be cut out     every distributed
       hooks            and moved                      carrier

The first row is the sharpest. HOLD is defined against fast state and
BUILD against persistence, so both are relative to a declared split. For
a recurrent network, whoever labels the hidden state decides whether an
in-context learner can BUILD.

v0.1 is careful elsewhere. Its protocol "must not assume pointers,
registers, modules, global addresses, synchronized clocks". It allows a
statistical equivalence contract where exact equality is meaningless.
It has E and S channels for state outside the organism. So the list is
three, not more.

Four further suggestions, none of them a fault in the text:
  - register at least two ways of writing observations into each physics
    and require verdicts to agree across them;
  - define a common currency for cost before comparing one physics with
    another;
  - add unreliability of the organism's own parts, energy and upkeep to
    the example dimensions of demand in section 12;
  - if hooks are implemented, make them operators on captured state, not
    addresses of components.

The repair for the three rows: move the definition to the WORLD side
where that is possible, and test every ruler on organisms whose answer
is known in each physics. Sections 4 and 5. My replacement protocol
keeps two presumptions on purpose (an inheritance channel and an agent
loop) and says so.

--------------------------------------------------------------------------------
3. SECTION-BY-SECTION DISPOSITION
--------------------------------------------------------------------------------
S1  CENTRAL DECISION ............................ KEEP, MODIFY
    Build the tunnel, not one engine: yes. But "in parallel" needs a
    coupling rule or it repeats v1/v2 with tunnel parts as the engines:
    nothing is built before its known-answer case exists. The first cars
    are then the calibration standards.
    The name commits to the one quantity v0.1 cannot yet measure. The
    name is the operator's; the charter should not promise it.

S2  SCIENTIFIC TARGET ........................... KEEP, MODIFY
    Section 4 already separates capacity, demand, reach and detection.
    Carry that into the target sentence: whether development pays is
    computed from the world; whether it is reached is measured on
    search. The "recursive extension" sentence does not separate reuse
    of built parts from improvement of the builder (see S19).

S3  EXPERIMENTAL OBJECT ......................... KEEP, MODIFY
    Keep the cell and the rule that a claim is conditional on it. Add two
    coordinates that are now implicit: the ADAPTER (how observation and
    action are written into the physics) and the PRICE LIST. For the
    first 90 days: boundary internal only, execution classes E0 and E1.

S4  FIVE QUALIFICATION QUESTIONS ................ KEEP, MODIFY
    The best section. Four changes.
    4.2 It asks for "exact policy bounds where possible" and allows a
        fallback to "progressively stronger adversarial baseline
        classes". Give the fallback a ceiling: without an exact bound on
        the restricted class, no claim above C1 (qualified, not robust).
    4.3 Add climbability: some search on some substrate reaches the
        capability in this world from scratch.
    4.4 Detection is per physics for any ruler that looks inside the
        organism. Exact class exclusion reads only the world's inputs
        and outputs; it still needs a leak test of its harness in each
        physics.
    4.5 DEVELOPABILITY has no operational test in this file. One that
        works: per-life random keys, so the inherited state provably
        lacks the content, with the irrelevant-history arm of section 19
        kept.

S5  DEVELOPMENTAL COORDINATES ................... MODIFY
    v0.1 says "Retain Fable's useful functional coordinates". They are
    mine. They read like a staircase of stages and may be a prior I
    share with the synthesis. Two defects: BUILD and HOLD need the state
    split; and COMPOSE and RECURSE are not separated by their own
    sentences (a library learner satisfies both). Replace by two
    measured axes, section 4.

S6  ORGANISM PROTOCOL ........................... MODIFY
    The exclusion list is right. The inclusion list still holds the
    split of state. Replacement text in section 4.

S7  REALITY AND OBSERVATION PLANES .............. KEEP SMALL
    Sound and cheap. In a simulation, reading state does not disturb
    it, so "measurement can modify the dynamics" comes down to timing,
    rounding and shared random streams. One twin run with and without
    instruments tests it. Keep that; build a receipt log, not an event
    bus. Add two routes of interference v0.1 does not list: ruler
    outputs reaching the search (organisms adapt to the instrument), and
    harness artefacts reaching the organism (resets, counters, clocks).

S8  EXECUTION CLASSES ........................... MODIFY, DEFER E2, E3
    The four classes are the right list, and v0.1 already names
    deterministic scheduling for E2 and sensitivity to perturbation and
    precision for E3. Build E0 and E1. For now reach E2 only by a
    deterministic event scheduler, which makes it E1. Admit E3 claim by
    claim, each with a convergence certificate (the claim survives a
    finer step and higher precision). In any chaotic system one
    trajectory proves nothing: interventions need a sham of matched
    size and an ensemble.

S9  COGNITIVE BOUNDARY .......................... DEFER, KEEP ONE PART
    The question v0.1 asks is the right one: where does useful
    organization choose to live under different cost structures. Seven
    conditions is more design than it needs now. Keep one thing
    immediately: every W0 world certifies the persistent state the
    environment lets the organism write (zero unless declared), and the
    counterfeit kit holds an impostor that parks its memory in the world.
    After day 90, one price-sweep experiment in which the boundary is an
    outcome. The social channel waits.

S10 SUBSTRATE STRATEGY .......................... MODIFY
    The two-realization rule is right, and section 4.1 and W0 already
    imply a constructed positive and known cheats per substrate. The
    "small unlike shadow substrate" is not described with one, here or
    in the portfolio. Make it explicit with the isomer panel: one known
    capability
    designed in at least three unlike physics, each with a matched
    impostor, so that "operated correctly" means "returned the
    registered answers on designed positives and impostors". A reviewer
    pointed out three weaknesses of such a panel, and each has a repair:
    designed organisms are all legible, so add one FOUND organism per
    physics, certified by class exclusion; one designer writes
    everything, so one isomer per physics comes from a second author;
    the panel has no known answer of its own, so include one ruler built
    to be physics-specific, which the panel must flag. It still cannot
    prove neutrality for shapes nobody thought of.

S11 WORLD PROGRAM W0 / W1 / W2 .................. W0 KEEP, W1 MODIFY,
                                                  W2 DEFER
    W1 identifies a transition only with exact class values, the
    break-even price as observable, a mandatory inherited-information
    budget (01 lists it among parameters W1 "may include"), and the
    three reasons for development kept apart (capacity, variability,
    reach).
    W2, in the file I had, is twelve ingredients; it says cheap classes
    "can still be bounded aggressively" and not how. Planted random keys
    are one way: the bound is about the key, however rich the rest is.
    Details: RESPONSE_1 section 9.

S12 ADVERSARIAL DEMAND GENERATION ............... DEFER, MODIFY
    Its target is defined against a list of cheap baselines, so it will
    beat the list for dull reasons. 01 already asks for sealed
    third-party families; add that the generator may propose and an
    exact solver must certify. Not before exact W1 maps exist.

S13 SEARCH GEOMETRY ............................. KEEP, MODIFY
    Right to make it physics, and right to speak of substrate/search
    combinations. The ten statistics are estimators with no ground
    truth. Calibrate them on a machine small enough for a census. State
    R(d,B) as counts of independent lineages with bounds. Measure with
    lifetime learning on and off: whether development smooths the
    landscape is the reach question that matters most.

S14 SCAFFOLD DESCENT ............................ KEEP, MODIFY
    v0.1 already asks for several search operators and for the
    selectability of intermediates. It still starts from one organism.
    My own data: with one instruction missing, recovery was 24, 9 or 1
    of 24 depending only on the acceptance rule, and the organism one
    lineage built from nothing used a mechanism I had not designed. Add
    ascent from random and empty starts, and three unlike plants.

S15 COMPRESSION ................................. KEEP, MODIFY
    The control list is good, and "not merely smaller state" is right.
    The open problem is the certificate: for retained random content an
    exact bound exists; for compression the best available is a
    comparison with the best lookup or dictionary of equal size on
    held-out families, which is a designed reference class and weaker.

S16 CAUSAL / NUISANCE DISSOCIATION .............. DEFER, MODIFY
    Better than raw noise. Four changes. Which variable is nuisance is
    drawn per life, or an inherited filter passes. Statistics held "as
    similar as practical" become twins with identical low-order
    statistics and a different law. Add the two free riders:
    relearn-from-scratch (revises appropriately at no credit) and
    never-change (invariant at no credit). Drop "internal revision"
    until an interchange ruler is qualified in that physics. As an
    experiment it follows W1.

S17 CRITICAL THOUGHT ............................ DEFER, MODIFY
    "Build worlds where skepticism pays" is right. Give "warranted
    revision latency" an exact reference: worlds whose change-point
    posterior is computable. After W1.

S18 SAGACITY .................................... KEEP, MODIFY
    v0.1 already says not to collapse sagacity into one scalar and
    lists amortization. The ratio S has one merit I first missed: inside
    one organism it is unit-free. It is unstable when the carried
    machinery is cheap. Report the amortisation horizon beside it: how
    many later families before the development has paid for itself. My
    run 3 is an example: the selector that passed it was cheaper than a
    naive organism on B alone, development included, in 15 of 24
    replicates, where run 2's library learner was in 24 of 24.

S19 RECURSIVE SAGACITY .......................... MODIFY
    Four preregistered runs and a file of probes (RESPONSE_1 section
    11). The steps leave five choices open: cost; how the later
    families differ from A; content; the sham; what family A is. I
    turned steps 1 to 12 into conjuncts with thresholds of my own (four
    in run 1, six from run 2 on) and registered three settings.
      - As written, read the easy way: a move-to-front list over three
        inherited procedures passes.
      - Four part families, then targets that are pairs of those parts
        (kinds never met): a library learner with a fixed constructor
        passes all six in 24 of 24 replicates, at a savings factor of 4.
        A selector over 90 ready parts and pairs fails.
      - One composite family, then composites of other parts: a selector
        over 32 inherited search orders passes at a factor of 2, with a
        sham that cannot fail. The library learner fails.
    In two stricter settings (four part families with targets made of
    other parts; C a kind never met) none of the organisms I ran passes,
    and nobody has a positive to show the steps would pass anything
    there. In the first a positive may be impossible as the controls
    stand: a history that shares no part with the targets is itself a
    wrong history. Every organism I built has fixed inherited machinery,
    so the runs show what the steps admit, not what they would do with a
    true positive.
    The steps have no arm that separates reuse from improvement of the
    builder.
    v0.1's own label for a pass begins "nested developmental
    improvement"; that half is fair. Fix the five choices, report the
    setting, report how much developed, and keep the word "recursive"
    for something no organism here does. Section 4.3.

S20 CLAIM LADDER ................................ MODIFY
    In this file the seven rungs have no rule for moving up, and two of
    them name kinds of thing. A reviewer corrected my first objection:
    "Transferable mechanism" above "Causal mechanism" is a sensible
    order for mechanism claims. What the ladder lacks is a place for a
    transfer shown from behaviour with no mechanism claimed. Use one
    ladder for strength and record the kind of claim beside it (section
    4.4). Add types PHYSICS_SPECIFIC_RULER, PRICE_DEPENDENT,
    WORLD_UNCLIMBABLE and ADAPTER_DEPENDENT. BOUNDED_NEGATIVE needs all
    five questions answered and a stated power.

S21 HISTORICAL RECORD AS QUALIFICATION CORPUS ... KEEP
    Keep, including the line that critics must be qualified. One
    addition: a lesson enters as an executable failing test that the
    gate must catch, or it has not entered.

S22 RESOURCE DOCTRINE ........................... KEEP
    v0.1 already lists energy, tokens and operator interventions. One
    addition: a budget for operator attention (three gate decisions in
    90 days), and tokens and energy on every receipt. In the old tree
    nothing records energy and one tool logs tokens for its own calls.

S23 SCIENTIFIC YIELD ............................ KEEP, MODIFY
    Y cannot be computed. Usable proxy: every experiment registers,
    before it runs, the decision it could change. Experiments that could
    change no decision are not run.

S24 FALSIFIERS OF THE FRAMING ................... KEEP, MODIFY
    Give each clause a quantity, a threshold and a date. Add two: some
    ruler still disagrees across isomers after one repair round; no
    designed positive for improvement of the builder can be built. For
    the cost clause: by day 90, more than 80% of tokens and attention on
    instrument with fewer than six registered cells holding a qualified
    effect or a bounded negative.

--------------------------------------------------------------------------------
4. REPLACEMENT TEXT PROPOSED FOR v0.2
--------------------------------------------------------------------------------
4.1 TWO AXES (for section 5)

    ORDER      Defined by the nesting of the WORLD. Order 1: savings
               within a task. Order 2: across tasks of one family. Order
               3: across families. Order 4: across groups of families.
               Measured from behaviour: cost to reach competence on a
               fresh unit, against the count of earlier units met.
    RETENTION  The information about past experience that survives a
               declared boundary or perturbation and is used afterwards.
               As a curve over gap length and load. And as a number:
               where the world draws a regularity at random per life (a
               key), behaviour gives a lower bound on the bits of it the
               organism acquired, at each order, against the exact score
               of the class that carries nothing across that boundary.
               Run once, one order up: counterfeit/keys.py.

    ORDER needs nothing from inside the organism. RETENTION under a wait
    or a distraction needs nothing either. Under a quench it needs the
    physics to declare what is zeroed, so it is then relative to that
    declaration and should say so.

    The old names as regions: HOLD and BUILD are short and long
    retention. ADAPT is order 1. COMPRESS is order 2 below the best
    lookup of equal size. COMPOSE is order 3 that depends on shared
    built parts. RECURSE, in the strong sense, has no region.

    NOT AN AXIS YET. Where a capability came from: chosen among
    inherited alternatives, built by a fixed builder, or built by a
    builder that was itself built. A draft of this response made that a
    third axis, ORIGIN, decided by a threshold on acquired bits. A
    reviewer showed the threshold measures only the size of a memory (a
    selector with many indices is an acquirer). The number of bits
    stays, under RETENTION. The classification is an open problem.

4.2 ORGANISM PROTOCOL (for section 6)

    A participating physics declares:
      1. ADAPTERS: how observations are written in and actions read out.
         At least two. Verdicts must agree across them.
      2. INHERITANCE CHANNEL: what is carried in from before the
         lifetime, its capacity in bits under a stated encoding, and a
         dial that shrinks it.
      3. PERTURBATIONS the harness may apply. Always WAIT(n) and
         DISTRACT(n), which need no access to internals. Optionally
         QUENCH (the physics states what is zeroed or resampled) and
         NOISE(eps).
      4. STATE CAPTURE sufficient to restart, with its equivalence
         contract (exact, or statistical with the test named).
      5. COST in a native unit and its conversion to host instructions.
      6. INTERVENTIONS, optional: operators on captured state (replace a
         region or subspace from a donor), each with a generator of
         shams of matched size.
      7. A TRACER, if any claim about provenance will be made.
    What this keeps on purpose: an individual with an inheritance
    channel and a lifetime, and an agent loop through adapters. I do not
    know how to measure development without the first, or to pose a
    task without the second. What it drops: the split into fast and
    persistent state. Items 3 (QUENCH), 5 and 6 are declarations by the
    physics, and any result that uses them is relative to them.

    Every ruler carries a PRESUMPTION SHEET: what it assumes about the
    organism, and the isomers on which it has returned known answers.

4.3 NESTED IMPROVEMENT (for section 19)

    Keep steps 1 to 13, with V, U and S as a mapping the experimenter
    registers before the run. Where a substrate cannot separate them,
    steps 7 to 10 do not apply and the claim rests on the order profile.
    Fix the five choices the steps leave open:
      a. COST. Savings are tasks consumed until an acceptable procedure
         exists, with no cut-off; the savings factor is stated; plus
         lifecycle cost against a naive organism working on the targets
         alone, a same-compute arm on one target, and the amortisation
         horizon.
      b. LATER FAMILIES. Say how B, C, D and E must differ from A and
         from each other: a new seed of a known kind, a kind never met,
         or a kind sharing no built part with the history. Report each
         setting as a separate result. A pass in one says nothing about
         another.
      c. CONTENT. Declared content stores are cleared at steps 2 and 5,
         and one organism is built to pass only if they are not. (My
         kit does not hold one yet: skipping the resets moves one
         conjunct of my memoriser and not its verdict.)
      d. SHAM. As many entries as the lesion, among entries the target
         does not use, and shown able to fail; plus a random structure
         of equal size and a wrong-history donor. Say what makes a
         history wrong when the right one shares no part with the
         targets; otherwise the right history is a wrong one too.
      e. FAMILY A. One family or a curriculum, stated. Which organism
         passes depends on it.
    Add:
      0.   Qualify first. The ruler must classify the counterfeit kit
           as registered; every clause of every conjunct needs an
           organism built to fail it; and each registered verdict must
           be attainable at a stated power.
      14.  How much developed, and by which measure: the capacity of
           the developed store, what experience selects among, or the
           bits acquired where the world has a key.
      15.  The order profile from behaviour, in a world nested at least
           one level deeper than the claim.
      16.  Wording. Report "nested improvement, order k" with the
           setting and the bits. Use "recursive" only if the organism
           shows savings at an order above every inherited level, or a
           builder is shown to act on itself. Inherited depth is known
           for a designed organism and cannot be read from behaviour;
           nobody has a positive for this yet.

4.4 ONE LADDER FOR STRENGTH, WITH THE KIND OF CLAIM BESIDE IT
    (for section 20)

    STRENGTH
      L0 observed       a logged run
      L1 qualified      preregistered; ruler qualified for this
                        physics; whole baseline ladder beaten; 5
                        independent lineages
      L2 robust         an exact bound on the restricted class at the
                        order claimed; an attack round with no surviving
                        impostor; sealed worlds; second host; a second
                        implementation by another author
      L3 reproduced     by another author in another physics or world
                        family
      L4 predicted      a quantitative relation stated in advance for a
                        new cell, then confirmed
    KIND, recorded separately: EFFECT, TRANSFER, MECHANISM, LAW.
    A transfer shown from behaviour can reach L2 or L3 with no mechanism
    claimed. A mechanism claim needs interchange with matched shams and
    an ensemble, and a model that predicts interventions not yet run.
    A transplant, where one is claimed, moves developed state into a
    naive body; that needs a declared developed state.
    Every claim also carries an independence level and its cell. The
    exact bound that L2 requires exists today for retention and for one
    order of acquisition of random content. It does not exist for
    structure, so claims about structure stop at L1 for now.

--------------------------------------------------------------------------------
5. ACCEPTANCE TEST FOR v0.2 (WHEN MAY IT BE CALLED A TUNNEL)
--------------------------------------------------------------------------------
    RETAIN-1 and RETAIN, exact nothing-carried bounds ........... required
    Designed positive and impostor in 3 unlike physics .......... required
    One isomer per physics from a second author ................. required
    Every ruler returns the registered answer on all of them .... required
    A deliberately physics-specific ruler is flagged ............ required
    Twin run with and without instruments agrees ................ required
    Applicable fixtures of F-01 to F-18 caught by the gate ...... required
    Power gate: every registered verdict attainable at 0.99 ..... required
    Second implementation of one world and one ruler agrees ..... by day 60
    One found organism per physics agrees with the rulers ....... by day 90
Decided by code. Until it passes, "substrate-neutral" and "observatory"
are plans, and no cross-physics comparison is read. The second-author
isomers and a blind search for one-bit retention in each panel physics
are scheduled for days 30 to 60 in RESPONSE_1 section 13. The found
organisms come from that search, not from the census of new physics.

My own first gate failed in exactly this way: one preregistered verdict
came back INDETERMINATE because I froze sample sizes without computing
whether the verdicts were attainable (722 of 2,785 trials; exact power
0.865). A rule in a document did not stop it. A gate in the runner does.
And my first counterfeit run in this review was too easy in four ways
that a second reader caught, and my third repeated two of them, which a
third reader caught. The acceptance test should be run by someone who
did not write the tunnel.

--------------------------------------------------------------------------------
6. WHAT I WOULD POSTPONE FROM v0.1
--------------------------------------------------------------------------------
    W2 and the demand generator .............. until W1 has exact maps
    Boundary conditions beyond internal ...... until after day 90
    Classes E2, E3 as frameworks ............. until a claim needs them
    Sections 16 and 17 as experiments ........ until W1
    Event bus, dashboards, lineage indexer ... a receipt log suffices
    The word "recursive" ..................... until a designed positive

--------------------------------------------------------------------------------
7. LIMITS
--------------------------------------------------------------------------------
  - Five of seven package files were not available to me.
  - Evidence behind this response: my prototype (one target, one host,
    small counts), four runs in counterfeit/ and one file of
    exploratory probes (designed organisms, toy worlds, one author). All
    are observations about instruments.
  - The two axes of 4.1 are a proposal. Bits acquired have been bounded
    once, on designed organisms in a world built for it: the bound
    separated organisms that carry nothing from organisms that carry 23
    bits or more, and under-certified a partial acquirer. ORDER has been
    exercised up to order 3 only, on designed organisms; order 4 has not
    been run on anything.
  - Everything in 4.1 that has an exact certificate is about retaining
    random content. A reviewer put it plainly: what this tunnel can
    certify today is memory. Certificates for structure are an open
    problem, and section 4 does not solve it.
  - Recording the kind of claim separately removes a legibility
    requirement from transfer claims. It also removes a safeguard: a
    behavioural claim with no mechanism can hide an unknown shortcut.
    The exact bound and the attack round stand in its place, and they
    must be real.
  - Three read-only reviewers found that drafts of this response blamed
    v0.1 for lacking several safeguards it has, proposed an axis
    (ORIGIN) that does not hold up, and claimed more for my runs 2 and 3
    than they show. Those passages now say what v0.1 already does, what
    I would add, and what the runs rest on.

Reviewer's bottom line, to confirm or contest: can v0.1's authors name
one ruler in it that has returned a known answer in two unlike physics?
================================================================================
END OF RESPONSE 2
================================================================================
