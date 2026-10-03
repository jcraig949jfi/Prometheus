================================================================================
PHASE 3 SYNTHESIS REVIEW -- RESPONSE 3 OF 3
REPLY TO CANDIDATE ARCHITECTURE PORTFOLIO R0-R9 (THE RACE CARS)
================================================================================
Prepared:      2026-10-02 (UTC)   reviewer FABLE-5.1 (seat Dionysus)
Responds to:   02_RACE_CAR_PORTFOLIO_R0-R9 (file numbers are the
               charter's; 01 is the wind-tunnel design)
Companions:    RESPONSE_1 (report to the charter), RESPONSE_2 (wind tunnel)
Location:      docs/phase3/review/FABLE-5.1/
Headline:      THE PORTFOLIO'S OWN MVP, WITH TWO CHANGES. Designed
               organisms with known answers in three or four physics in
               place of the R4 shadow, and a thin R3 as the second build.
               Also: retire R7, which was mine; merge R1 with R2; fold
               R9 into two switches.

Not provided to me: files 00, 03, 04, 05, 07 of the package.
My stake: six entries trace to my own design in whole or part (R1, R3
with Astra, R5, R6, R7 and the lattice arm of R4). The builds I recommend
coincide with three of my own substrates. Section 1 says what I did
about that. Three read-only reviewers attacked drafts of this response
in turn.

TERMS USED IN THIS RESPONSE
--------------------------------------------------------------------------------
    physics           the rules a kind of organism runs on (the package
                      also says substrate)
    ruler             a measurement procedure with a registered verdict
    cell              the registered combination of physics, world,
                      search and budget that a claim is conditional on
                      (01 section 3)
    null              a result of not detected; 01 gives each null a
                      type that says why
    latch             an organism, or a circuit, that holds one bit
    designed          an organism written by hand to have a capability;
    positive          with its impostor it is a known answer
    impostor          an organism built to look like a positive and not
                      be one
    isomer panel      one known capability built by design in several
                      unlike physics, each with a matched impostor
    class exclusion   beating the exact best score of a restricted class
                      of policies, at a stated error rate
    counterfeit kit   designed organisms that must NOT earn a claim
    selector          an organism that only chooses among inherited
                      alternatives
    library learner   a fixed constructor that stores procedures which
                      worked and tries them, and pairs of them, first
    plant             a designed organism used as a known answer or as a
                      target for search
    census            an exhaustive count over a space small enough to
                      enumerate
    thin              the smallest version that can host a known-answer
                      organism
    order             which regularity is exploited, by the nesting of the
                      world: within a task (1), across tasks of a family
                      (2), across families (3)
Ids like O-09 or W-08 are rows of my SALVAGE_MATRIX.

--------------------------------------------------------------------------------
1. VERDICT
--------------------------------------------------------------------------------
The portfolio is honest about what it is: a preserved hypothesis space.
It says its entries "should not be treated as ten engines already
approved for implementation", and it has an MVP: R0; R1 or R2; a tiny R4
shadow. It adds R8 early, as a control. I agree with most of that.
Beyond the two changes to the MVP named in the headline, three things
about the portfolio as a whole.

  1. Entries name a physics and, except R0, no way of producing
     organisms in it. The cell has a search coordinate and 01 section 13
     speaks of substrate/search combinations, but the portfolio does not
     say which regimes each entry will run under. The record says reach
     is what failed. In the Ananke engine (my salvage matrix), designed
     organisms scoring .850 and .978 sat in a space where 19,873,536
     world-episodes of search reached .503 and .479. Make each candidate
     a pair (physics, search regime).
  2. Entry conditions exist ("when the wind tunnel can test them without
     custom scientific semantics") and are hard to test as worded. The
     rule below is a testable version.
  3. A lane meant to resist the designers' priors needs more than an
     unfamiliar genre. It needs blind search and a ruler that reads only
     behaviour (section 4).

THE ENTRY RULE, WITH TWO DOORS. Any physics may be run at any time under
a ruler that reads only the world's inputs and outputs (class
exclusion). Before a null is read, before a physics-specific ruler is
trusted, and before a search campaign is funded, the physics needs a
known answer. Door one: a designed positive and a matched impostor on
which the tunnel's rulers return the registered answers. Door two: a
positive found by blind search and certified by class exclusion. A
reviewer pointed out that door one alone admits only physics a designer
finds legible. Door two is how an illegible physics gets in.

ON MY STAKE. By this rule R5 is at least as qualified as R3 today: each
has a designed latch on record. I still put R3 second, because gradient
search is available in it and it shares tooling with R0. That is a prior
about reach, stated as a prior. The portfolio's own rule is to choose R3
"if the main unresolved question is reachability" and R4 if it is
"Track-A ontology dependence". I think both are open, and I answer the
second with designed organisms, which are cheap. If the other reviewer,
or the author of the R2 design, finds this ranking follows my stake,
take theirs.

--------------------------------------------------------------------------------
2. DISPOSITIONS AT A GLANCE
--------------------------------------------------------------------------------
    ID    Disposition   In the first 90 days
    ----  -----------   -------------------------------------------------
    R0    KEEP          two learners and the ideal observer; an owner
                        who wants it to win
    R1    MERGE         thin kernel shared with R2
    R2    MERGE         a proposal; two of its ideas kept as a switch
                        and a ruler
    R3    KEEP          thin build, second, if GATE 60 of RESPONSE_1
                        section 13 is met on time
    R4    DEFER         one designed lattice organism; the blind census
                        (RESPONSE_1, X5) if the day-30 gate is on time
    R5    DEFER         one small packet organism modelled on Ananke's
    R6    DEFER         paper design only
    R7    RETIRE        nothing
    R8    KEEP          first, as a kit; five members have run
    R9    MERGE         nothing separate; two switches later
    R10+  MODIFY        design only; one blind census

--------------------------------------------------------------------------------
3. CANDIDATE SHEETS
--------------------------------------------------------------------------------
R0 -- CONVENTIONAL REFERENCE ................................ KEEP
  Why. It decides whether anything else matters. The portfolio is right
  that "The reference needs to be strong enough to kill weak novelty
  claims", and right to list meta-learned and gradient variants.
  What I would add. Names, an order and an owner:
    a. the ideal observer: the exact Bayes value wherever computable.
       Not an organism; the bound every organism is scored against.
    b. in-context learner: fixed weights, trained across lives, all
       lifetime learning in activations. Such learners approach the
       Bayes optimum on their training distribution (Mikulik et al.
       2020), so matching (a) inside that distribution is expected and
       is not the test. The test is kinds never met and lifetimes
       longer than the training horizon.
    c. online-gradient learner: weights change during life by a designed
       rule.
    d. external-memory learner trained by gradient: the same physics as
       R1 reached by a different search. After day 90 unless needed.
    e. self-referential learner, as a toy: the conventional candidate
       for nested improvement (Kirsch and Schmidhuber 2022). After day
       90, with the nested-improvement gauntlet.
  Boundary with R3: R0 may use any designed, global learning rule. R3 may
  use only local rules found by search. As written R0's "plastic" and
  "structural plasticity" variants overlap R3.
  Owner: a role inside an existing seat, whose registered goal is that
  R0 wins, with a tuning budget at least equal to any candidate's search
  budget. R0 needs no designed positive: its known answer is (a).
  A trap to close: is the hidden state of (b) fast or persistent? Under
  v0.1 that label decides whether it can BUILD. Under a retention curve
  (RESPONSE_2, 4.1) it gets a curve like everyone else.

R1 -- ADDRESSABLE WORKSPACE MACHINE ......................... MERGE
  Evidence, from my own prototype of a tiny version: with one instruction
  missing, blind search recovered the builder in 24, 9 or 1 of 24
  lineages depending only on the acceptance rule; 0 of 2,000,000 random
  programs reached 0.9; and the one success from an empty program leaned
  on store instructions that are specific to the capability, which my
  package grades as a scaffold. From Crius: the layout works, typed
  opcodes put competence into the instruction set, and an identifier
  counter was a clock. One target, one machine, small counts: enough to
  say reach must be measured before building deep, not that Track A
  cannot work.
  The listed strength, "Mechanism boundaries may be unusually legible",
  is real and is a reason for caution: R1 is the machine the rulers were
  drawn around.
  Proposal. One thin kernel shared with R2: integer, every word decodes,
  compiled, pinned to a separately written oracle. That is the form of
  my prototype, kept because it has run. Switches: how a reference
  finds its target (by position, by content or by link); growth
  operations (off or on); rule store (fixed or writable). No block store
  with calls, arguments or rent until a W1 result asks for them. I
  designed those. They wait.
  Would change my mind: the census shows Track-A reach equal to or
  better than R3's under the same search regime.

R2 -- DEVELOPMENTAL GRAPH MACHINE ........................... MERGE
  A proposal, not a finding. I have read one paragraph about this machine
  (the DGM) and not its design. From that paragraph (nodes with spawn,
  link, unlink, rewrite, set-decay and prune; rules as state the lifetime
  can change) it looks expressible as settings of the same kernel as R1,
  and the portfolio already says "R1 or R2". Which setting is primary
  should be decided by measured reach, not by whose design it was. If the
  author of that design shows it does not fit, R2 stays separate and R1
  does not get built instead of it without that comparison.
  Two of its ideas should survive in any case:
    - rules as state the lifetime can rewrite. This is the natural
      Track-A route to improvement of the builder, and as a switch its
      effect is measured by on against off.
    - provenance of higher-order writes, as a tunnel ruler usable on any
      Track-A organism.
  The portfolio's own warning stands: "The developmental instruction set
  may already constitute a privileged programming language for
  self-construction." Any result that uses those operations carries that
  scaffold level on the claim.

R3 -- PLASTIC STRUCTURAL NETWORK ............................ KEEP
  Why second. The portfolio lists its expected strength as "Potentially
  much better reachability" and calls that a hypothesis. I share the
  hypothesis and cannot support it: a search of the old tree found no
  closed-loop network organism that keeps weights or topology across
  episodes (trainers for mathematical environments were not examined as
  learners). So there is no evidence either way. I rank it second on two
  grounds that are not evidence: gradient search is available, and it
  shares tooling with R0.
  Shape. Fixed-point arithmetic. Weights persist across episodes. The
  plasticity rule is local and found by search, by evolution and by
  meta-gradient (Miconi et al. 2018; Najarro and Risi 2020). Growth and
  pruning are a switch.
  The listed weakness, that composition "may be difficult to localize",
  matters less if a transfer can be certified from behaviour with no
  mechanism claimed (RESPONSE_2, 4.4).
  Enters when: a designed latch (the Ares hand-wired latch rebuilt, held
  by self-loop or by leak) and its impostor return registered answers.
  Would change my mind: under the same search regime and equal
  evaluations, reach for certified retention no better than Track A.

R4 -- SPATIAL DEVELOPMENTAL CHEMISTRY ....................... DEFER
  The portfolio wants a minimal R4 by Day 45 "as an observatory shadow
  comparator", and says its fossils "inform it but do not validate it".
  Agreed on both. The record has no evidence either way on development
  in a lattice. It does hold one known-answer corpus for a lattice arm:
  recovered cellular-automaton rule tables with their answers (W-08).
  What I would change: the shadow's first deliverable is a designed
  lattice organism with a known answer (one bit, then a mapping, held as
  a stable local pattern with a readout) and an impostor, so that every
  ruler has a registered answer for both. That is a sharper version of
  the shadow's stated job, revealing assumptions in "ruler expectations".
  How it earns a campaign: by door two. The blind census (RESPONSE_1,
  X5) samples local physics and scores them by class exclusion. A
  physics in which certified retention is common gets searched.
  A control to build with it: the same medium, fixed, with a trained
  readout. If that matches a designed or evolved medium, the design or
  the evolution added nothing.

R5 -- MESSAGE / PACKET ECOLOGY .............................. DEFER
  The Ananke engine is the best-instrumented fossil: a separately
  written oracle that agrees bit for bit, a conformance suite that passed
  on a second host (139 passed), dials for loss, latency, duplication
  and noise, and a designed organism that holds its bit only in flight.
  It is not an organism substrate yet: no step from observation to
  action, no episode boundary, built for GPU; and one of its worlds is
  solved by a 28-line clock, which is a fault of that world.
  Now: a small packet-ring organism modelled on the in-flight latch
  joins the isomer panel. The engine itself waits. A memory that is
  neither register nor weight is the hardest case for the retention
  rulers. The old carrier-swap lens is the warning: in 93 of 93 groups
  two interventions were one measurement by design.
  Later: a search campaign after a closed-loop adapter and a CPU kernel
  re-certified against the oracle. By the entry rule it is as qualified
  as R3; if R3's reach disappoints, R5 is next.

R6 -- EXPRESSION / REACTION CHEMISTRY ....................... DEFER
  Greenfield for Prometheus, and an established genre outside it:
  AlChemy (Fontana and Buss 1994), combinatory chemistry (Kruszewski and
  Mikolov 2021). The portfolio's own line decides the timing: "Huge
  search space and extremely weak initial demand alignment."
  Its special use is to the tunnel. It is the candidate in which code
  and data are one thing, so V, U and S cannot be lesioned apart. A
  designed organism in expression form is the sharpest test of whether
  any criterion for nested improvement is free of organism shape. Paper
  design only in these 90 days. It could share one chemistry engine with
  R4, with spatial or well-mixed as a dial.

R7 -- TENSOR / FACTOR ORGANISM .............................. RETIRE
  This was my open arm. I would retire it. It has no designed positive
  and no found one, so it fails both doors of the entry rule, and I can
  name no question it asks that R0 or R3 cannot ask with a rank or width
  dial. The portfolio's own danger line applies: it imports human
  factorisation into the substrate. I do not argue from the old
  tensor-train code, which the portfolio rightly calls "not a ready
  implementation".
  What survives: an explicit capacity dial inside R0 and R3.

R8 -- LIBRARY-BUILDING PROGRAM LEARNER ...................... KEEP
  The cheapest and most valuable entry, and it has already paid. I
  turned steps 1 to 12 of section 19 into six conjuncts with thresholds
  of my own. With targets that were kinds never met, built from parts
  it had just learned, a library learner whose constructor never
  changes passed all six in 24 of 24 replicates (313.5 tasks to acquire
  a new kind falling to 20.5; savings factor 4). By the portfolio's own
  rule ("If it calls ordinary library accumulation recursive sagacity,
  the ruler is insufficient") the ruler, as I ran it, is insufficient.
  Tightened so that targets share no part with the history, the library
  learner fails. In the one such setting I registered, a selector over
  inherited search orders passed instead, at half the threshold and
  under weaker controls. In two stricter settings none of the organisms
  I ran passes (RESPONSE_1 section 11).
  A kit, not one program. Five members have run, each in at least one
  of my four runs. None has yet run under one protocol with a fire test
  for every clause:
    SELECTOR OVER PROCEDURES   chooses among inherited procedures
    LIBRARY LEARNER            builds from parts with a fixed builder
    SELECTOR OVER ORDERS       chooses among inherited search orders
    MATURATION                 an unlock that needs experience of any
                               kind; also an organism that hides an
                               inherited answer
    MEMORISER                  carries task content
  Still to write: the impostor that parks its memory in the world, a
  hierarchical-Bayes selector, and R0's self-referential toy, whose
  answer is not known (it is the nearest thing to a candidate positive).
  The Aphrodite engine cannot be the library learner by itself: from
  nothing its donors derived 0 schemas in 8 of 8 runs.
  Every ruler for orders 2 and 3 classifies the whole kit as registered
  before it is used on anything else.
  Note. The library learner is a negative for "recursive" and a
  legitimate positive for reuse of built parts. Register which claim an
  organism is a control for.

R9 -- CELLULAR DEVELOPMENTAL AUTOMATON ...................... MERGE
  Its primitives (division, differentiation, local signalling, growth,
  pruning) are those of the lattice family. What is distinct is two
  ideas. One: a genome that encodes a growth process is easier for
  search to find than a mature architecture. That is a claim about
  encoding, testable as a switch (direct against developmental encoding
  at equal genome bits) on R3 and on a lattice. Two: growth that depends
  on experience. That is R3 with growth and pruning switched on, or a
  lattice organism with the same. Neither needs its own engine in 90
  days. The danger the portfolio names, "Development may merely unfold
  a precompiled blueprint", is MATURATION in the kit, and the
  irrelevant-history arm catches it.

R10+ -- ARCHITECTURE FOUNDRY ................................ MODIFY
  The one element that can escape the designers' priors, because what it
  produces need not be designed. The portfolio already says "Generate
  combinations without semantic names" and "Unclassifiable alone means
  nothing". Two changes. Its primitives are still a named list
  (persistence, movement, reaction, binding, copying and so on); sample
  local update rules under constraints (locality, conservation, a noise
  dial) instead. And score only with a ruler that reads behaviour:
  random-hit rate for certified retention.
  In these 90 days: one census (RESPONSE_1, X5), which moves past day
  90 if the day-30 gate is late. No engine. It is door two of the entry
  rule.

--------------------------------------------------------------------------------
4. MISSING CANDIDATE FAMILIES, AND THE ANTI-GRAVITY QUESTION
--------------------------------------------------------------------------------
    Family                          What it would settle
    ------------------------------  ------------------------------------
    Self-referential conventional   whether nested improvement needs an
      learner (inside R0)             unfamiliar substrate at all
    External-memory learner by      whether R1's trouble is its physics
      gradient (inside R0)            or blind search
    Content-addressable memory      capacity questions; its capacity
      machine                         theory is known, demand is not
                                      helped by it, and it imports human
                                      mathematics as R7 did. Unscheduled.
    Physical learning network       memory as transport structure under a
      (flow or resistor network       conservation law; no store, no
      with use-dependent              addressing, no program
      conductance)
    Selectionist learner            development and search as one
      (replicators inside a life)     process
    Reactive agent plus writable    the boundary question; and the
      world                           impostor for internal construction
    Fixed medium plus trained       the control for R4 and R5
      readout
    Unreliable components           whether noise alone creates demand
      (a regime, not a car)           for built, maintained structure

Pointers: Stern and Murugan 2023, Dillavou et al. 2022 and Kramar and
Alim 2021 for physical learning; Szilagyi et al. 2016 for selectionist
learning. Which of these I checked by search is listed in 00_README.md.

The charter asks which architecture could reveal a legitimate mechanism
that designers would not naturally invent. The question is about the
mechanism, not the name of the architecture. Old genres can still yield
such mechanisms: my own blind search in the most software-like machine
found a builder that uses never-written registers as free constants,
which I had not designed. What makes that likely is blind variation at
scale, constraints designers reason about badly (locality, conservation,
noise, dissipation), and a ruler that does not ask the mechanism to be
legible. So Track B is enough as physics and not as planned: a small
shadow with no search behind it reveals nothing. Of the families I can
name, the physical learning network is the least program-like, with
laboratory positives and a cheap exact equilibrium. Its learning rule is
a relative of contrastive Hebbian learning, so it is not outside the
corpus. The foundry, sampling unnamed local physics, is the instrument
for the question.

--------------------------------------------------------------------------------
5. PORTFOLIO STRATEGY, AMENDED
--------------------------------------------------------------------------------
    Portfolio says                      Amend to
    ----------------------------------  --------------------------------
    MVP: R0; R1 or R2; tiny R4 shadow   R0 (observer and two learners);
    by Day 45                           one Track-A kernel; designed
                                        organisms in 3 physics by day
                                        30, a fourth by day 60
    Next full competitor: R3 or R4,     R3 as a prior about reach; R5
    by which question is open           next if that prior fails; R4 by
                                        the census
    R8 early in lightweight form        R8 kit FIRST; five members have
                                        run (counterfeit/)
    Later: R5, R6, R7, R9, once the     the two doors; R7 retired; R9's
    tunnel can test them                ideas as switches
    Candidates are substrates           pairs (physics, search regime);
                                        three regimes per physics;
                                        gradient where the physics
                                        admits it
    (not stated)                        every sheet names its known
                                        answer, its cost, and the
                                        decision it could change
    (not stated)                        no seat per candidate

--------------------------------------------------------------------------------
6. WHAT LEARNING FROM FAILURE MEANS: THE FOSSIL LINES AGAINST THE RECORD
--------------------------------------------------------------------------------
File 07 was not available; this is about the seven lines at the end of
the portfolio, read against my salvage. Mostly I agree.

    Crius       says: workspace is interesting; opcodes can smuggle
                record: agrees. Layout works; typed rungs put competence
                in the instruction set; block ids are a clock (O-03)
    Proteus     says: graph/call substrate remains interesting; greedy
                search failures prove reach must be measured separately
                record: agrees. The walk could not accept a neutral step
                (3,132 of 4,881 sampled children were neutral): a search
                fixture, and no evidence about the physics (S-03)
    Ananke      says: packet physics remain interesting; capacity is not
                discovery
                record: agrees, and adds a fault of one of its worlds: a
                28-line clock solves it (O-09)
    Aether      says: propagation is real, and is not reasoning
                record: agrees (O-10)
    Ensorain    says: factorized representations are interesting; cheap
                baselines first
                record: agrees on baselines (the tuned one arrived after
                the data: W-03, F-06)
    Aphrodite   says: growing libraries can look recursive
                record: the lesson holds, but the fossil's library did
                not grow. From nothing: 0 schemas in 8 of 8 runs. A
                SUPPLIED library cut cost 47 and 345 times (O-13, matrix
                section 6)
    Nestor/BEE  says: copying physics remain useful; lineage confusion
                becomes a fixture
                record: agrees on the fixture; a second one belongs with
                it, a copy assay that certifies painters built to carry
                zero bits (C-10)

One addition. Five of the seven lines call a physics "interesting" or
"useful". The record is silent on whether any of them supports
development: what failed was search and rulers, not the physics. So the
word should carry no weight either way, and a fossil physics should
re-enter through the same two doors as a new one. My own salvage keeps
one of them (the Ananke engine) as an open arm on those terms. What the
record does supply, in quantity, is fixtures, baselines, designed
positives and negatives: see RESPONSE_1, REV 8.

--------------------------------------------------------------------------------
7. LIMITS
--------------------------------------------------------------------------------
  - Five of seven package files were not available to me.
  - My reach numbers are one target on one tiny machine, small counts,
    one author. They justify measuring reach before building deep. They
    do not show that Track A cannot work.
  - I have no measurement on R3, R4, R5 or R6 as developmental
    substrates, and neither does the Prometheus record. R3's place rests
    on a prior, the others on the entry rule.
  - The four runs and the probes in counterfeit/ are designed organisms
    in toy worlds. Three rounds of review each narrowed what they show.
  - What I kept of my own design: the thin kernel's form, class
    exclusion, key worlds, known-answer organisms. They are the parts
    that have run. They are also one kind of instrument, and a reviewer
    was right that what it certifies today is memory.
  - Literature is cited as pointers; see 00_README.md for what was
    checked.

Reviewer's bottom line, to confirm or contest: for which candidate,
today, does a designed positive with a matched negative exist in its own
physics? By my count: R1 (my builder and holder; the Crius designed
programs), R5 (the Ananke latches and must-fail control), R8 (five kit
members), and R3 for HOLD only (the Ares latch, in a machine that resets
everything each episode). For a lattice there is a corpus of rule tables
with known answers (W-08), not under an organism protocol. None of these
is under a common protocol. For R0 the known answer is the ideal
observer. For R2, R6, R7 and R9, none.
================================================================================
END OF RESPONSE 3
================================================================================
