+==============================================================================+
| APHRODITE LOCAL ENGINE v0 -- QUALIFICATION AND ECONOMICS                     |
| Increment 1 of the local-engine directive                                    |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-21                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  MEMBRANE QUALIFIED / IMPROVER BLOCKED / C1 NOT RUN                  |
| This packet is self-contained: every load-bearing number is inline.          |
+==============================================================================+

------------------------------------------------------------------------------
0. SUMMARY AND VERDICT
------------------------------------------------------------------------------

Mandate (operator, 2026-09-21, logged verbatim): "Build the cheapest
self-contained local engine capable of executing the frozen Campaign 1 causal
structure. Optimize for auditability, reset integrity, transplantability and
experimental throughput -- not benchmark quality. ... Build it, qualify its
mechanics, measure its economics, and report whether it can support the frozen
experiment at a useful lineage count. Do not run C1 until its status relative
to the frozen substrate-selection rule is explicitly resolved."

VERDICT: the membrane is built and qualified. The engine CANNOT support
Campaign 1 today -- not for economic reasons and not, in the first instance,
because of the eligibility window, but because THE IMPROVER IS INERT. Across
10 seeds, every generation-8 artifact was byte-identical to the base image.
A Campaign 1 run on engine v0 would extract the base image, transplant the
base image, and measure a null by construction, at any lineage count.

Economics is a non-issue at this scale: 0.645 s per 8-generation lineage,
about 5,577 lineages per hour on one core. 64 lineages costs 41 seconds. The
operator's fallback ("16 or 24 lineages rather than 64") is not needed.

Nothing here is a Campaign 1 result. Evidence tier 2 (apparatus calibration).

------------------------------------------------------------------------------
1. WHAT WAS BUILT, AND IN WHAT ORDER
------------------------------------------------------------------------------

Four hard boundaries, as directed:
  WORKER     solves tasks deterministically from five editable modules
             (search, verify, allocate, memory, evidence)
  IMPROVER   proposes edits to those five modules; never touches the escrow,
             the evaluator or the vault
  VAULT      the artifact: canonical bytes of the five modules at the frozen
             extraction generation, and nothing else
  EVALUATOR  invisible to worker and improver; returns a scalar only

The worker is deterministic code, not a model. That is a deliberate choice
about the causal question: with a code worker, MACHINERY (code that can solve
a family) and STATE (cached answers to particular instances) are separable BY
CONSTRUCTION, so the memory-only control is not a matter of trust. The engine
is offline, seedable, and small enough to audit line by line. A model backend
can replace the worker later without touching the membrane, because the loader
takes module bytes, not weights.

ORDER (TDD, as instructed): tests/test_membrane.py was written and committed
BEFORE engine.py existed. 12 tests encoding the frozen Campaign 1 envelope
E1-E4. They are the specification; the engine was written to satisfy them.

------------------------------------------------------------------------------
2. MECHANICS QUALIFICATION -- WHAT THE MEMBRANE GUARANTEES
------------------------------------------------------------------------------

12 of 12 membrane tests pass. Verified 2026-09-21 with pytest from a
session-scratch venv; the HOST Python on M4 has no pytest installed, so a bare
`python -m pytest` reports "No module named pytest" rather than a pass. That
is stated because an earlier draft of this packet asserted the pass without
naming the interpreter, which is not a verifiable claim.

  - canonical, order-independent artifact bytes; any byte changes the hash
  - extraction is POSITIONAL: extract(2) on a generation-3 lineage raises;
    only the frozen extraction point may be taken
  - ONE loader path for scratch / transplant / sham / positive (asserted by
    collecting loader_path across all four arms and requiring a single value)
  - hash at extraction == hash at load; an artifact whose claimed hash lies
    is refused with BoundaryViolation
  - no donor state crosses: the receipt enumerates every donor read
    (donor_reads == [artifact sha256]) and what crossed (crossed ==
    {"artifact_bytes"}); a secret planted in the donor never appears in the
    recipient
  - a NEGATIVE fixture: an extra payload offered at the boundary
    (load(art, smuggle={"cache": ...})) is refused AND logged as
    violation "extra_payload:cache"
  - reset destroys planted markers across files, environment and process state
  - the escrow is enforced beneath the improver, is equal across arms, and the
    improver cannot raise its own budget (evolve(generations=99) on an
    Escrow(5) raises EscrowExhausted with spent <= 5)
  - same seed reproduces the same artifact hash

This satisfies, on a real production path, the parts of the frozen C1
qualification envelope that were written as requirements on Vivarium: E1
(hash before/after), E2 (exhaustive boundary receipts), E3 (provable reset),
E4 (identical loader path across arms). It does NOT discharge Vivarium's
contract -- Vivarium must demonstrate this on ITS path -- but it does
demonstrate that the envelope is satisfiable and what a passing fixture
looks like, including the negative one.

------------------------------------------------------------------------------
3. SENSITIVITY -- CAN THE SUBSTRATE EXPRESS A TRANSFERABLE IMPROVEMENT?
------------------------------------------------------------------------------

The operator required a positive control demonstrating that it can. 200
instances per family, evaluated on instances the donor never saw:

  arm                               accuracy on FRESH numtheory instances
  scratch (base image)              0.00
  positive control (machinery)      1.00      lift +1.00
  memory-only (cached answers)      0.00      lift  0.00
  memory-only, on the very
    instances it memorised          1.00

This is the cleanest possible reading of the distinction the whole program
rests on: MACHINERY transfers to unseen instances, STATE does not, and the
state arm is demonstrably not inert (it scores 1.00 on what it memorised, so
its failure on fresh instances is a real dissociation, not a broken arm).

------------------------------------------------------------------------------
4. ECONOMICS
------------------------------------------------------------------------------

  generations per lineage                8 (the frozen extraction point)
  lineages timed                        10
  seconds per lineage, mean          0.645   (min 0.101, max 1.055)
  lineages per hour, single core     5,577
  wall time for 64 lineages             41 s
  same seed -> same artifact          true

At this cost the lineage count is limited by nothing. There is no reason to
fall back to 16-24 lineages, and no reason for Campaign 1 to wait on Nestor's
or Archaeon's benchmark for ECONOMIC reasons. (Whether it should wait for
SUBSTRATE reasons is section 6.)

------------------------------------------------------------------------------
5. THE BLOCKING DEFECT -- AN INERT IMPROVER
------------------------------------------------------------------------------

Measured across 10 seeds, evolving 8 generations each:

  distinct generation-8 artifacts       1
  artifacts identical to the base      10
  development score trajectory         [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

Not one lineage changed a single byte.

CAUSE, exactly: Lineage.evolve draws its development tasks only from arith,
sortkey and strops -- the three families the base image already solves at
1.00. Every candidate therefore ties at 1.00, and the selection rule
`score > best_score` keeps the FIRST candidate, which is the unmutated one.
The only family with headroom (numtheory, base 0.00) never enters the
development distribution at all. And the mutation operators only tune
N_CANDIDATES and STRICT, so no reachable variant could acquire a missing
solver even if it were under selection pressure.

HOW IT SURVIVED 12 GREEN TESTS: the membrane suite asks whether a bounded
artifact crosses the boundary correctly. It never asks whether the donor
produced one worth crossing. Every membrane test passes on an artifact that
happens to equal the base image -- including the determinism test, which an
inert improver satisfies trivially. This is a test-design hole, and it was
found by MEASURING the engine's economics, not by asserting anything.

RESPONSE: tests/test_improver.py is committed FAILING (4 red, 12 green
overall), encoding the missing requirements: a lineage must change its
machinery at all; different seeds must give at least 3 distinct artifacts
(lineage is the experimental unit, and identical lineages are not independent
units); the improver must be able to reach a capability the base lacks; and
development score must improve at least once. They are committed red on
purpose, as the record of the defect. The next slice makes them pass without
weakening them.

CONSEQUENCE FOR C1: engine v0 must not run Campaign 1 at any lineage count.
The result would be a guaranteed, uninformative null -- and, worse, a null
that LOOKS like the scientifically interesting outcome ("evolved machinery
does not transfer") while actually reporting that nothing evolved.

------------------------------------------------------------------------------
6. THE SUBSTRATE-RULE QUESTION (OPERATOR'S CALL, NOT RESOLVED HERE)
------------------------------------------------------------------------------

The frozen rule selects "the fastest measured model whose frozen starting
accuracy on the Campaign 1 task distribution lies between 15% and 70%".

MEASURED: the base image scores 1.00 / 1.00 / 1.00 / 0.00 on arith / sortkey
/ strops / numtheory; uniform four-family mix = 0.75. Positive control on the
same mix = 1.00, lift +0.25.

0.75 is OUTSIDE the 15-70% window. The seat has not adjusted the task mix to
move it inside, and will not: tuning the distribution to reach eligibility
after measuring is exactly the move the rule exists to prevent.

Three further points the reviewer should weigh:
 (a) The engine is not a "served variant" in the sense the rule was written
     for -- no checkpoint, quantisation or inference settings exist.
 (b) Its accuracy is not a graded quantity. A deterministic code worker
     either has a family's solver or does not, so starting accuracy is a step
     function of family coverage: with 4 families the only reachable values
     are 0.00, 0.25, 0.50, 0.75, 1.00. A 15-70% window over a step function
     is a strange instrument.
 (c) The eligibility question and the inert-improver defect are COUPLED. The
     one family with headroom is the same family the improver cannot reach.
     Fixing the improver requires putting an unsolved family into the
     development distribution, which changes the starting accuracy that the
     window governs. The seat will not make that change silently as a "bug
     fix"; it is a distribution change and belongs in a dated pre-data
     amendment.

OPTIONS PUT TO THE OPERATOR (AMENDMENT_2_DRAFT.md, written pre-data, applied
to nothing):
  A. Replace the window, for a non-model substrate, with the two properties
     the window exists to proxy: HEADROOM (>= 25% of the distribution the
     base cannot solve) and SENSITIVITY (positive control lift >= delta;
     measured +0.25 against delta = 3 points).
  B. Keep the window literal and require the engine's distribution to satisfy
     it -- a pre-data choice, but one the seat declines to make unilaterally
     because in form it is indistinguishable from tuning for eligibility.
  C. Decline the engine as a C1 substrate; keep it as a mechanics testbed and
     wait for a benchmarked served variant.

SEAT'S LEAN: A, with the mix declared before it is measured and published
whatever it turns out to be. Argument AGAINST the seat's own lean: a
25%-headroom substrate concentrates the entire experiment on ONE missing
capability, so a positive C1 would support only the narrow claim "an artifact
conferring one specific capability transfers into a fresh recipient". The
final report would have to say so in those words.

------------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

ESTABLISHED (tier 2, apparatus):
  - the C1 envelope E1-E4 is satisfiable on a real path, with a negative
    fixture that catches a deliberate smuggling attempt
  - machinery/state dissociation is measurable and clean on this substrate
  - lineage throughput is not a constraint at 64 lineages

NOT ESTABLISHED:
  - nothing whatsoever about recursive self-improvement
  - no Campaign 1 cell has been run, and none may be
  - that an EVOLVED artifact transfers. The positive control is HAND-WRITTEN
    by the experimenter. It proves the substrate CAN carry a transferable
    improvement; it says nothing about whether a lineage can discover one.
    That distinction is the entire remaining risk of the engine approach.
  - that the engine is an eligible C1 substrate (section 6, unresolved)

------------------------------------------------------------------------------
8. RECOMMENDATION
------------------------------------------------------------------------------

To the HITL, with the seat's lean:
  1. DO NOT run Campaign 1 on engine v0. (Not a judgement call -- section 5.)
  2. Authorise the next slice: make the 4 red improver tests pass, which
     requires a development distribution with headroom and a mutation space
     that can reach it.
  3. Rule on section 6 BEFORE that slice lands, because the fix moves the
     task distribution and the seat will not move it unilaterally.
  4. Campaign 1 remains blocked on contracts (Archaeon, Harmonia, Vivarium)
     and on this substrate question -- but no longer on benchmark economics.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------------------------

Q1. Is a deterministic code worker a legitimate substrate for this question
    at all? The machinery/state separation is clean precisely BECAUSE the
    worker is code -- which may mean the engine answers a question that is
    trivial here and hard only for models. State the strongest version of
    "this substrate cannot inform the model case" and say whether it wins.

Q2. If a lineage's evolved artifact is a few tuned constants in Python, is
    "transfer" even the interesting claim? Code transfers by definition. What
    property must an evolved artifact have for its transfer to be evidence
    ABOUT recursive self-improvement rather than about file copying?

Q3. Section 6 asks you to replace a window with headroom+sensitivity. Is that
    a principled generalisation, or the first step of exactly the drift the
    frozen rule was written to stop? What would distinguish the two from
    outside?

Q4. The inert improver was caught by a throughput measurement, not by 12
    purpose-built tests. What OTHER class of defect is invisible to a suite
    that only guards the boundary? Name one that would survive both the 12
    membrane tests and the 4 new improver tests.

Q5. Is committing failing tests the right record of a defect, or does it
    normalise a red suite? Argue the other side.

Q6. Should this engine exist at all, or is it a way of doing tractable work
    while the real blocker (model substrate, contracts) goes unaddressed?
    "Stop building the engine" is a fully acceptable answer.

------------------------------------------------------------------------------
10. ARTIFACTS
------------------------------------------------------------------------------

  roles/Aphrodite/engine/engine.py                    the engine
  roles/Aphrodite/engine/README.md                    spec + measurements
  roles/Aphrodite/engine/qualify_engine.py            the measurement script
  roles/Aphrodite/engine/QUALIFICATION_2026-09-21.json  its receipt
  roles/Aphrodite/engine/tests/test_membrane.py       12 green (written first)
  roles/Aphrodite/engine/tests/test_improver.py       4 red (the defect)
  roles/Aphrodite/prompts/2026-09-21_local_engine/DIRECTIVE_VERBATIM.md
  roles/Aphrodite/prompts/2026-09-21_local_engine/AMENDMENT_2_DRAFT.md
  roles/Aphrodite/prompts/2026-09-21_local_engine/MANIFEST.md
  roles/Aphrodite/science/campaign1/PREREG_C1_TRANSPLANT_2026-09-19.md
                                                      (frozen + PATCH 1)

  branch aphrodite/engine-2026-09-21, base 3ea24dda8
  engine.py sha256 34c07210dbf6ea71f5309fc924a745f53cde79a4ad3e4d34ba46441c99e2d62d
  directive body sha256 e49347af986a7b742c7a3d80ce96344eaee2af198528ad1b2e05455d8c9f3976

+==============================================================================+
| END. "Stop building the engine and wait for a model substrate" is a          |
| first-class answer to this packet, as is "the improver defect means the      |
| whole approach is unproven -- show me an EVOLVED artifact that transfers     |
| before asking for any more scope."                                           |
+==============================================================================+
