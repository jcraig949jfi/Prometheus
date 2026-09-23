+==============================================================================+
| APHRODITE LOCAL ENGINE -- SLICE 2C                                           |
| Stopped at the reachability gate: no load-bearing structure is possible      |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-21                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  STOPPED BEFORE EVOLUTIONARY SEARCH -- by the ruling's own gate      |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. HEADLINE
------------------------------------------------------------------------------

The enumerator was repaired and both capability classes became reachable. The
slice then stopped before running a single lineage, because a pre-run
certificate established that NO LOAD-BEARING STRUCTURAL MECHANISM EXISTS in
this grammar:

    structural_success_criterion_satisfiable = FALSE

Euclid's algorithm -- a genuine bounded loop, discovered rather than handed --
solves numtheory at accuracy 1.000 and is defeated by a single surrogate:
`gcd(x, y)`. Because `gcd` is a primitive, any structure computing it is
redundant by construction.

THE FINDING: structure can only be load-bearing RELATIVE TO A PRIMITIVE SET.
Every class in the declared distribution is one primitive application away
from solved, so no qualifying artifact can exist at any lineage count under
any entropy. Running 16 lineages would have produced a second 0/16 whose cause
was already known analytically.

Campaign 1 remains frozen and unrun. Tier 3 not self-authorized.

------------------------------------------------------------------------------
1. THE AUTHORISED REPAIR (grammar v2)
------------------------------------------------------------------------------

    slice 2B   v1-frontier-asymmetric    (retained, unused, reproduces 0/16)
    slice 2C   v2-size-indexed-symmetric
               hash 713195e32926e538e2cebb9831359782854e20f29c227c3fbdd2f1f3f6849d16
               MAX_SIZE = 4 operator applications

v1 built each round as op(LEFT from the previous frontier, RIGHT from pool),
so op(terminal, deep) was never constructed. v2 enumerates by size: for size
s, every split (i, j) with i + j = s - 1, both directions.

TWO REPAIRS, BOTH DECLARED RATHER THAN BURIED:
 (a) In slice 2B the structural search still called the OLD asymmetric
     enumerator. Repairing only the composition path would have been
     cosmetic.
 (b) HELPER_CANDIDATE_CAP was 40 -- an arbitrary truncation I introduced in
     2B. The declared helper space holds 48 distinct helpers, and EUCLID IS
     RANK 44. My own cap excluded the only structural witness for numtheory.
     Raised to "enumerate the declared space".

Reviewers should weigh (b): removing a truncation after watching it exclude
the witness is adjacent to tuning for yield. My defence is that the
truncation was never part of a declared grammar, the space it truncated was
declared, and the change is recorded with its effect stated before any
lineage ran. I would not object to a reviewer calling it a violation.

------------------------------------------------------------------------------
2. REACHABILITY CERTIFICATE (before any lineage, no tribunal in existence)
------------------------------------------------------------------------------

Validation used a CERTIFICATE entropy domain that is neither development nor
tribunal. Witnesses live in the certificate file and were never given to the
improver.

    class      composition witness       size    charges   validated(400)
    modexp     (pow(n0,n1) % n2)            2        900       1.000
    numtheory  NONE within MAX_SIZE = 4     -     47,719          -
    numtheory  structural witness           -  3,504,938       1.000

numtheory's composition-only witness add(gcd, fdiv(mul, gcd)) is SIZE 5 --
outside the declared bound. I did not raise the bound to admit it. So
numtheory is reachable ONLY through a helper, which is the cleanest possible
setup for this slice's objective. That is not what stopped it.

------------------------------------------------------------------------------
3. WHAT STOPPED IT
------------------------------------------------------------------------------

Descriptive C6 is retired; presence/invocation/looping/AST-depth/helper-count
are telemetry only. A structural component counts only if no simpler surrogate
preserves the capability: constants, identity/passthrough, all 28 single
primitive applications over {x, y}, single-iteration control flow, and
removal/bypass.

I enumerated EVERY helper that enables an exact solution and ran the battery
on each, before any lineage:

    class      enabling helpers   load-bearing witnesses
    numtheory        4                   0
    modexp           1                   0

    h = (y | x % y)      EUCLID. accuracy 1.000. defeated by expr_gcd(x,y)
    h = (x*y | x - x)    one-iteration product. 1.000. defeated by
                         expr_mul(x,y) and by single_iteration
    (two further enabling helpers score 0.15 and solve nothing)

`gcd` and `pow` are primitives. Every declared class is one primitive
application from solved. Structure is therefore redundant BY CONSTRUCTION and
the battery correctly refuses to credit it.

WHAT I DID NOT DO: remove `gcd`/`pow` from the primitive set to manufacture a
necessity for structure. That is the same forbidden move in the opposite
direction -- altering the declared primitive set to produce the hoped-for
result.

------------------------------------------------------------------------------
4. REPORTED QUANTITIES
------------------------------------------------------------------------------

    qualifying_artifacts / independent_lineages      0 / 0  (no run)
    distinct_artifact_hashes / independent_lineages  0 / 0  (no run)
    disposition of every failed artifact             none produced

Slice 2B stands separately and unpooled: 0/16 qualifying, 14/16 distinct
hashes, disposition GRAMMAR_INCOMPLETE.

Suite: 32 passed, 1 failed (the numtheory generalisation defect witness from
slice 2, still red and still accurate). Two new permanent fixtures:
  - the decorative-loop fossil, now adjudicated by the battery;
  - "even Euclid is not load-bearing while gcd is a primitive", encoding
    this slice's finding so it cannot be quietly forgotten.

------------------------------------------------------------------------------
5. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

ESTABLISHED:
  - an adjudication procedure that credits structure only against simpler
    causal surrogates, and that rejects both a decorative loop AND a
    genuinely correct Euclid implementation, for the right reason in each case
  - that "did the system discover an algorithm?" is not answerable without
    naming the primitive basis the claim is relative to
  - that this grammar cannot host the slice's objective

NOT ESTABLISHED:
  - whether the process CAN discover load-bearing structure. That question
    was not tested, because the substrate cannot pose it.
  - nothing about Campaign 1; engine remains outside eligibility
  - RSI: NO

------------------------------------------------------------------------------
6. RECOMMENDATION (named, not executed)
------------------------------------------------------------------------------

The next rung in the ruling -- isolating and transplanting a discovered
structural component -- is NOT recommended, because nothing can currently be
credited as structural.

Making the question askable is a PRIMITIVE-SET / TASK CO-DESIGN decision, and
it is the operator's:
  - a capability class whose solution is not one primitive application away
    (iteration to a fixed point, accumulation over variable-length input, a
    branching decision procedure no single primitive expresses); AND
  - a primitive set that does not already contain that operation.

Both halves must move together, and both should be declared before either is
measured -- otherwise the design is chosen to produce a discovery.

------------------------------------------------------------------------------
7. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is "load-bearing relative to a primitive set" the right definition, or
    does it prove too much? Under it, a system that rediscovers a known
    algorithm gets no credit whenever a library call exists. Is that correct
    austerity or a definition that makes discovery unobservable?
Q2. Same question aimed at models: if a base model can do X in one forward
    pass, is scaffolding that does X ever creditable? Most agent-framework
    results would fail this battery. Should they?
Q3. I removed my own helper cap after watching it exclude the witness. Is
    that legitimate repair or tuning? I have argued both sides in section 1
    and genuinely do not know where the line is.
Q4. Stopping before the run saved 16 lineages of compute and produced an
    analytic result instead of an empirical null. But it also means I decided
    the experiment was pointless without running it. When is that judgement
    a researcher's duty and when is it a way of avoiding an unwelcome number?
Q5. The task distribution was designed before any of this and turns out to
    make structure redundant. How much published work on "emergent
    algorithmic discovery" has the same property un-noticed, because nobody
    ran a surrogate battery against the primitive basis?

------------------------------------------------------------------------------
8. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  roles/Aphrodite/engine/AMENDMENT_4_2026-09-21.md
  roles/Aphrodite/engine/certify_reachability.py
  roles/Aphrodite/engine/REACHABILITY_CERTIFICATE_2026-09-21.json
  roles/Aphrodite/engine/engine.py   (grammar v2, surrogate_battery,
                                      structural_telemetry, v1 retained)
  roles/Aphrodite/engine/tests/test_slice2b.py  (+2 permanent fixtures)
  slice 2B, unpooled: SLICE2B_RESULTS_2026-09-21.json,
                      pivot/APHRODITE_ENGINE_REVIEW_3_2026-09-21.md

+==============================================================================+
| END. "You should have run the lineages anyway" is a first-class answer, as   |
| is "the surrogate battery is too strict and no real system would survive     |
| it -- which is a fact about the battery, not about the systems."             |
+==============================================================================+
