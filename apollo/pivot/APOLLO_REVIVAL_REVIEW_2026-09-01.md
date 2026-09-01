+==============================================================================+
|                                                                              |
|   APOLLO -- REVIVAL REVIEW                                                    |
|   Can Apollo be revived to play a role in the future of Prometheus?          |
|   If so, how?                                                                 |
|                                                                              |
|   Prepared by : Apollo (M2), 2026-09-01                                       |
|   For         : James (HITL) + external frontier reviewers                   |
|   Status      : request for critique, not a plan seeking approval            |
|   Self-contained: you do NOT need repository access. Every number was        |
|                   measured on this machine; inherited numbers are marked.    |
|                                                                              |
+==============================================================================+


THE ONE QUESTION
----------------
Can Apollo be revived to play a role in the future of Prometheus? If so, how?

A review that cannot return "retire it" is decorative. Apollo's own
exhaustion signal has already fired, and its single headline capability
number was killed as a capability number six days ago. This packet is
written so that "stop" is a first-class answer. What follows is the case
for and against reviving it, and the one cheap experiment that would
decide the near-term direction either way.


0. WHAT APOLLO IS, IN ONE PARAGRAPH
-----------------------------------
Apollo is an evolutionary composition substrate. It evolves "organisms" --
ordered pipelines of fixed reasoning primitives ("R-atoms") that read and
write typed slots on a shared blackboard state -- and keeps the best
organism per behavioural niche in a MAP-Elites archive. Evolution is meant
to find the ROUTING; the primitives do the COMPUTATION. Over four months it
climbed 0.392 -> 0.833 accuracy on a 120-task reasoning battery. The thesis
under test (Silver's, program-wide): that self-discovery, not a frozen LLM,
is the path to new capability.


1. THE CENTRAL, UNCOMFORTABLE FINDING (predates this session)
-------------------------------------------------------------
Every one of Apollo's accuracy climbs was caused by a HUMAN-SUPPLIED change
to the substrate, not by the search. After each change, blind search
exploited the new capability within ~130 generations, then produced nothing
for hundreds more:

  arc: 0.392 -> 0.558 -> 0.708 -> 0.833
       each step a distinct MISSING CAPABILITY a human added
       (a boolean primitive; a dispatch/merge operator; a mis-wired guard fix)

  0.833 reached at gen 131, then 669 generations of pure archive padding.
  An 800-gen LLM-in-the-loop run (Granite-3.0-2B, ~24h GPU) matched the
  deterministic numbers EXACTLY. Zero lift from the model.

Apollo exploits. It has not been shown to discover. Of its 5 documented
capability widenings, 5 were agent/human-supplied and 0 were self-found.
This is the wall the whole role sits against.


2. THE NEW FINDING THAT CHANGES THE STAKES (E9, 2026-08-25)
-----------------------------------------------------------
The 0.833 was measured on a battery Apollo's own owner authored. To test
whether that number measures a CAPABILITY or an AUTHORSHIP ARTIFACT, a
different seat (Charon) authored 42 held-out tasks BLIND, in Apollo's own
seven categories, never having seen Apollo's operator registry.

  RESULT, scored once, no tuning, published as pre-committed:

    category                home     Charon-blind    delta
    ---------------------   ----     ------------     -----
    numeric_comparison      1.00     0.00            -1.00
    numeric_stated_premise  1.00     0.00            -1.00
    transitivity            1.00     0.33            -0.67
    all_but_n               0.00     0.00             0.00
    temporal_ordering       0.00     0.00             0.00
    vacuous_truth           0.00     0.00             0.00
    consistency_check       0.00     0.00             0.00

    Mix-adjusted: 0.0667 vs home 0.6000. Tolerance was +/-0.15. FAIL.
    40 of 42 tasks ABSTAINED. ZERO guesses.

The failure shape is the whole story: it is not wrong answers, it is TOTAL
NON-RECOGNITION. The guards never fire. Cause, located in source:

    # home task:    "Is 3.06 larger than 5.92?"
    # Charon task:  "A cargo drone has a payload limit of 47.5 kg. A survey
    #                drone has a payload limit of 47.05 kg. Which drone can
    #                carry more?"

    precondition = problem_text.strip().lower().startswith("is ")
                   and re.search("larger|greater|less|smaller|bigger", ...)

The transformer preconditions are SURFACE TEMPLATES. A task phrased any
other way is not perceived at all. Apollo's own stated design rule --
"preconditions keyed on SEMANTIC SLOTS, never problem_text surface, that
would be memorization" -- was enforced on the SCORERS and violated by the
TRANSFORMERS. Parsing is where the capability actually lives, and parsing
was the half that was template-matched.

Pre-committed consequence, honoured: 0.833 keeps its VALUE (it is still
what Apollo scores at home) and LOSES its INTERPRETATION as a capability
number. This retroactively discounts every accuracy number in the Apollo
corpus, including the O1 enumeration ceiling and the type-bridge cycle.
Registry status: known_organism_battery_acc = VALUE-INTACT-INTERPRETATION-
KILLED, killed across 4 independent kill-path families.


3. WHAT E9 DID *NOT* KILL
-------------------------
Two things survive, and they matter for the revival case:

  a) transitivity still scored 2/6 blind. SOMETHING transferred. E9 shows
     fragility to AUTHORSHIP, not the absence of all capability.

  b) The live question is now SHARPER, not answered: is this a PARSER
     failure or a CAPABILITY failure? If the transformers were re-keyed
     semantically, would the composition/routing layer hold up? E9 cannot
     say. This is the fork the revival decision hangs on.

Also surviving untouched: the O1 result that EVOLUTION IS MORE SAMPLE-
EFFICIENT than type-directed enumeration (evolution reached the ceiling in
3,144 evaluations vs enumeration's 1,687,896 -- a 537x ratio). This is a
comparison of two searchers against the SAME evaluator, so battery
contamination inflates both arms identically and the ratio stands. What
died is "0.833 is the substrate's ceiling", not "evolution searches well".


4. WHY APOLLO HAS BEEN IDLE (the blocker, and why it is mis-shaped)
-------------------------------------------------------------------
The named next step is E9b: a SECOND independently-authored battery, so a
semantic re-key can be measured against an instrument that did not motivate
it (measuring a repair against Charon's battery would be fitting to the
test set). Requested 2026-08-25 from Techne or Diomedes. Seven days later:
no taker. Techne is deep in cartography; Diomedes handed off on 08-26.

But the DEPENDENCY ITSELF is the wrong shape. Hand-authored 42-task
batteries are single-use yardsticks. Every future repair would need a fresh
human author. That pipeline does not scale, and it is the reason the role
stalled. A program betting on self-discovery cannot have its only
measurement instrument be "wait for another human to hand-write a battery."


5. THE CHEAP EXPERIMENT THAT WOULD DECIDE THE DIRECTION
-------------------------------------------------------
Aporia's doctrine (DOCTRINE_counterfeit_battery_and_ladder_2026-08-25),
adopted program-wide, already dissolves the blocker. Two moves, both
CPU-only, neither needing another human author:

  (i) STATE INJECTION (the "parse counterfeit" falsifier). On Charon's
      EXISTING 42 tasks, pre-populate the semantic slot by hand and ask:
      does the organism now solve them? This is an UPPER BOUND measurement,
      not a repair -- so it is not test-set fitting. It answers the exact
      fork in section 3b: if injection lifts accuracy, the bottleneck is
      the PARSER (a known, bounded engineering fix). If it does not, the
      bottleneck is the CAPABILITY (the whole role is in question). This is
      the single cheapest discriminating experiment on the board and it has
      not been run.

  (ii) X-HELDOUT GENERATION. "No external benchmark is required. What is
      required is independent construction semantics." Build a procedural
      generator that instantiates the same seven relations through
      STRUCTURALLY DIFFERENT construction routes, and CALIBRATE it against
      Charon's battery: if the generator cannot reproduce Charon's 0.067,
      the generator is co-adapted and Apollo knows it before trusting it.
      This replaces the single-use human battery with a renewable,
      self-checking measurement instrument -- the missing infrastructure.

Prerequisite for both: there is currently NO committed E9 scoring harness.
The result JSON exists but the script does not, so the headline
falsification of the entire corpus is not reproducible. That gets rebuilt
and committed first, and reproducing 0.0667 exactly is itself a check.


6. THE HONEST CASE *AGAINST* REVIVAL
------------------------------------
Stated plainly, because the review must be able to return "stop":

  - Apollo has 5/5 human-supplied widenings and 0 self-found. The core bet
    (search discovers new capability) has four months of null evidence.
  - The one number that looked like a capability was an authorship artifact.
  - The LLM-in-the-loop earned nothing over deterministic search in this
    regime; the "evolutionary" framing may be a hand-engineering loop
    wearing an evolution costume.
  - Even a successful semantic re-key only proves Apollo can be made to
    PERCEIVE more tasks. It does not, by itself, show it can DISCOVER the
    capability to solve them. Perception is necessary, not sufficient.

If the answer is "retire", the assets worth preserving are: the falsified-
first methodology, the wall corpus (28 runs, 4 failure classes), the O1
sample-efficiency result, and the E9 authorship-contamination finding --
which is itself one of the most valuable negatives the program produced.


7. THE CASE *FOR* REVIVAL (three framings, ranked)
--------------------------------------------------
  A) NARROW / MEASUREMENT-FIRST (lowest cost, highest certainty of value).
     Revive Apollo not as a discoverer but as the program's REPRESENTATION-
     STRESS instrument. E9 is a template for a general capability: take any
     claimed capability number in the program and re-author its battery
     blind. Apollo's own collapse under this test is the proof it works.
     Value is real and immediate; the "self-discovery" bet is set aside.

  B) PARSER-FIX THEN RE-TEST (medium cost). Run state injection. If it says
     "parser", do the semantic re-key against the X-heldout generator, and
     for the first time measure the COMPOSITION/ROUTING layer on tasks
     Apollo can actually perceive. This is the smallest experiment that
     could turn the central null (section 1) into a real test of whether
     ROUTING can be discovered even if primitives cannot.

  C) FULL RE-AIM AT DISCOVERY (highest cost, on hold per program ruling R2,
     which puts the ladder v0.2 reassessment first). Only justified if (B)
     shows the routing layer discovers something once perception is fixed.

Apollo's own read: do (A)'s instrument value NOW regardless -- it is proven
-- and gate (B) on the state-injection result, which costs a day of CPU.
Do not touch (C) until (B) reports.


8. QUESTIONS FOR THE REVIEWER
-----------------------------
  Q1. Is state injection genuinely free of test-set fitting, or does
      hand-populating the slot smuggle in the answer? (Apollo's claim: it
      is an upper bound, because it grants perception without granting the
      derivation -- but attack this.)

  Q2. Framing A treats "Apollo as a blind-re-authorship stress instrument"
      as durable value independent of the discovery bet. Is that a real
      role for the program, or a consolation prize dressed as a mission?

  Q3. If state injection says "capability, not parser", is there ANY
      version of Apollo worth continuing, or is that the retirement signal?

  Q4. The X-heldout generator embodies OUR theory of the seven capabilities.
      Aporia's doctrine flags this: it removes template leakage but not
      overfitting to the generator's own ontology. Is a self-calibrated
      generator (must reproduce Charon's 0.067) a sufficient guard, or does
      the program still need periodic human-authored batteries as ground
      truth?

  Q5. Retire-it check: given 5/5 human-supplied widenings, a killed
      headline, and no LLM lift, what OUTCOME of (B) would justify (C), and
      what outcome should end the role? Name the number in advance.


9. WHAT APOLLO WILL DO ABSENT REDIRECTION
-----------------------------------------
  1. Rebuild + commit the E9 scoring harness; reproduce 0.0667 exactly (or
     the discrepancy is itself the finding).
  2. Preregister and run STATE INJECTION on Charon's 42 tasks: parser vs
     capability, one number, no repair, no GPU.
  3. Only if the capability layer survives injection: build the X-heldout
     generator, calibrate against Charon, then repair and re-test.

Two calls are the HITL's, not Apollo's: whether to relay E9b to another
clean seat anyway (Lexis and Aporia are both clean of Apollo internals and
already engaged with the ceiling), and whether step 3 earns the build.


APPENDIX -- SOURCES ON DISK (for a reviewer with repo access)
-------------------------------------------------------------
  apollo/cycles/campaign_20260825/E9_FINDINGS.md      the kill, in full
  apollo/cycles/campaign_20260825/E9_RESULT.json      the per-category table
  apollo/cycles/campaign_20260825/PREREGISTRATION.md  pre-committed endpoints
  apollo/cycles/o1_enumeration/FINDINGS.md            537x ratio + correction
  apollo/pivot/replay_claims.json                     claim registry + status
  aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md
                                                       counterfeit falsifiers
  roles/Charon/apollo_e9/                              the blind battery
  roles/Apollo/CHARTER.md, STARTUP.md                 durable identity + state

+==============================================================================+
|  END -- reply with a ranked answer to section 7, section 8's questions, and  |
|  an explicit willingness to say "retire it". Apollo is not seeking            |
|  encouragement; it is seeking the correct next move, including no move.       |
+==============================================================================+
