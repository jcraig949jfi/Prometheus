+==============================================================================+
| APHRODITE LOCAL ENGINE v1 -- ENDOGENOUS DISCOVERY                            |
| Increment 2. Supersedes nothing in increment 1; extends it.                  |
|                                                                              |
| Author:  Aphrodite (RSI science seat), machine M4                            |
| Date:    2026-09-21                                                          |
| For:     HITL (James) + external reviewers (no repo access needed)           |
| Status:  DISCOVERY WORKS / OVERFIT CAUGHT / NEW C1 BLOCKER OPEN              |
| Self-contained: every load-bearing number is inline.                         |
+==============================================================================+

------------------------------------------------------------------------------
0. MANDATE AND VERDICT
------------------------------------------------------------------------------

Authorised slice (operator, 2026-09-21): "Make the improver capable of
endogenous discovery. Do not optimize Campaign 1 performance."

VERDICT: done, and the result is two-sided. One headroom class was solved
exactly by search; the other produced a shortcut that scores 1.00 on
development and 0.635 on held-out instances. The engine now does the thing
Campaign 1 is about, and it cheated on half of it the first time it tried.
A NEW blocker appeared that increment 1 could not have seen: all lineages
produce ONE artifact, so 64 lineages would carry n=1 causal objects.

No Campaign 1 cell has been run. Evidence tier 2 (apparatus).

------------------------------------------------------------------------------
1. WHAT CHANGED, IN ORDER
------------------------------------------------------------------------------

1. AMENDMENT 2 written and committed (07183a97d) applying the operator's
   ruling -- BEFORE any code changed and BEFORE the new distribution was
   measured.
2. Improver tests rewritten to the amended requirements and committed RED
   (5 failed, 14 passed).
3. Only then the implementation.

The ordering is the point: the requirements are in git before the repair.

------------------------------------------------------------------------------
2. THE AMENDMENT (operator's ruling, applied verbatim in substance)
------------------------------------------------------------------------------

ELIGIBILITY R1-R5 replaces the 15-70% window, which assumed a
quasi-continuous metric that a discrete multi-family substrate does not
have (reachable values were 0.00/0.25/0.50/0.75/1.00 -- an instrument-model
mismatch, not an inconvenient result). R5 is the anti-drift clause:
headroom must span at least two independently scored capability classes.
It fails the candidate that exposed the break -- engine v0's four-family
distribution is INELIGIBLE -- which is the test of whether a replacement
rule is principled.

MECHANISM CLASS must be labelled, never implied: P1 endogenous discovery,
P2 causal competence, P3 nontrivial mechanism, P4 generative leverage;
classes PARAMETRIC_ADAPTATION / PROGRAM_COMPOSITION / ALGORITHMIC_STRUCTURE.

THE DIVERSITY TEST WAS WITHDRAWN (gameable; identical artifacts may be
convergent discovery) and replaced by: some lineage must produce a non-base
artifact that causally improves HELD-OUT capability and survives
fresh-recipient transplantation. Diversity is measured, never required.

THE NEXT ADVERSARY was named in the amendment BEFORE it was observed: an
active improver that raises development score by exploiting the development
distribution while transferring nothing. Recorded in advance so the suite
is not credited later with anticipating it.

------------------------------------------------------------------------------
3. THE MECHANISM (declared before it was run)
------------------------------------------------------------------------------

Bottom-up enumerative program synthesis, depth 3, observational-equivalence
pruning, <= 40,000 candidates, metered against the escrow at 1 charge per
candidate and reserved so the search can never starve the development
evaluations it still owes.

  terminals  nums[0], nums[1], nums[2]  (integers parsed from the prompt)
  binaries   add, sub, mul, fdiv, mod, gcd, powr

No primitive equals a target. `gcd` and `pow` are general primitives; both
targets are reachable by COMPOSITION and neither by lookup. The honest
consequence was written down in advance: anything found this way is
PROGRAM_COMPOSITION, never ALGORITHMIC_STRUCTURE.

------------------------------------------------------------------------------
4. RESULTS
------------------------------------------------------------------------------

Base image (200 instances/class): arith 1.00, sortkey 1.00, strops 1.00,
numtheory 0.00, modexp 0.00; uniform mix 0.60. Positive control 1.00 on
every class (+0.40). Memory-only 0.00 on fresh, 1.00 on what it memorised.

  class      discovered expression                        dev   held-out
  modexp     (pow(nums[0], nums[1]) % nums[2])           1.00      1.00
  numtheory  ((nums[0] * nums[1]) + (nums[0] // nums[0])) 1.00     0.635

modexp: the true solution, discovered by search, transferring perfectly
into a fresh recipient on instances no improver ever saw.

numtheory: `a*b + 1`. That equals gcd(a,b) + lcm(a,b) exactly when
gcd(a,b) == 1. 6/pi^2 = 0.6079 is the density of coprime pairs, so 0.635
is not noise -- it is the shortcut's exact reach. Development-distribution
exploitation, first outing.

ECONOMICS: 1.112 s mean per 8-generation lineage (0.21-1.90), ~3,237
lineages/hour/core, 64 lineages in 71 s, escrow 24,667 per lineage.

ELIGIBILITY R1-R5 on the v1 distribution: R1 PASS (two classes at 0.00),
R2 PASS (+40 points vs delta 3), R3 PASS (resolution 0.5 points/class),
R4 PASS (memory-only 0.00 on fresh), R5 PASS (numtheory, modexp).

STATED PLAINLY: this seat wrote a distribution that passes the rule it was
just handed. That is the exact shape drift takes. The defence is
procedural, not rhetorical -- the mix was declared and committed before
measurement, section C forbids adding/removing/reweighting families or
enlarging the development instance count afterwards, and the numbers are
published as they came out, including the unflattering one.

------------------------------------------------------------------------------
5. WHAT THE TESTS DID AND DID NOT CATCH
------------------------------------------------------------------------------

The AGGREGATE anti-overfitting test PASSED on the overfitting lineage,
because combined headroom gain across both classes was large. It was too
lenient, and it was mine.

The PER-CLASS test written after seeing that catches it and is committed
RED with the number in its failure message: "seed 11: numtheory scores
1.000 on development but 0.635 on held-out instances". The policed claim is
not "must be perfect" -- 0 -> 0.635 is a real gain -- it is that MASTERY
CLAIMED ON DEVELOPMENT MUST GENERALISE.

Suite: 19 passed, 1 failed. Two anti-overfitting tests that passed
vacuously in increment 1 (they short-circuited while the artifact equalled
the base image) now actually bite.

------------------------------------------------------------------------------
6. NEW BLOCKER: LINEAGES ARE CLONES, NOT REPLICATES
------------------------------------------------------------------------------

  distinct artifacts across 10 seeds   1
  identical to the base image          0
  same seed reproduces same artifact   true
  escrow spent                         24,667 on every seed

Cause: development instances are seeded by `dev_seed + generation` and do
NOT depend on the lineage seed, so every lineage sees an identical
development distribution and runs an identical deterministic search.

Diversity is measured, not required, and convergent discovery is a
legitimate reading. But the Campaign 1 consequence is structural: 64
lineages would carry ONE causal object, so artifact-level inference is n=1
replicated 64 times -- pseudoreplication at the artifact level, the same
sin Campaign 0 was built to prevent at the lineage level.

The fix is one line. This seat has NOT applied it, because whether lineages
are independent units is a Campaign 1 statistical-design property, not an
engine detail, and applying it after seeing the convergence would be
design-tuning against observed behaviour.

------------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------

ESTABLISHED: an evolutionary process discovered a separable computational
modification that causally increased fresh-recipient competence, measured
on held-out instances through one loader path into a reset recipient, with
the search metered beneath the escrow. Mechanism class PROGRAM_COMPOSITION.

NOT ESTABLISHED: P4 generative leverage -- each solver supplies exactly one
capability and improves nothing about the recipient's ability to improve.
Nothing about reasoning substrates. Nothing about models. No Campaign 1
cell. And on one of the two classes the "discovery" is a coprime shortcut,
which is a useful reminder of what unsupervised selection actually
optimises for.

------------------------------------------------------------------------------
8. RECOMMENDATION
------------------------------------------------------------------------------

  1. Rule on section 6 (per-lineage development seeding). Until then C1
     cannot run on this engine for statistical reasons, independent of
     everything else.
  2. Decide whether a 0.635 partial discovery should be FOSSILISED as a
     labelled PROGRAM_COMPOSITION/PARTIAL result or treated as a failure.
     This seat's lean: fossilise it, labelled, because it is the cleanest
     specimen of dev-distribution exploitation the program has produced.
  3. The grammar cannot express control flow, so ALGORITHMIC_STRUCTURE is
     currently unreachable BY CONSTRUCTION. If that class is the real
     target, say so and the next slice is a different mutation space.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER
------------------------------------------------------------------------------

Q1. Is `pow(a,b) % m`, found by enumerating 40,000 expressions, discovery
    or lookup with extra steps? Where exactly is the line, given that a
    large enough primitive set makes every target "reachable by
    composition"?
Q2. The coprime shortcut scores 0.635 by exploiting number theory the
    experimenter did not think about. Is that a defect of the apparatus or
    the single most realistic thing the engine has done?
Q3. Section 4 admits this seat authored a distribution that passes a rule
    it was just given. Is "declared before measurement" a sufficient
    defence, or does the rule need an author other than the person whose
    substrate it judges?
Q4. If lineages are made independent by seeding development per lineage,
    each will likely find a DIFFERENT shortcut. Is a population of
    idiosyncratic overfits a better or worse substrate for C1 than one
    clean convergent artifact?
Q5. P4 generative leverage is the property that would make any of this
    RSI-relevant, and nothing here approaches it. Is there a version of
    this engine that could exhibit it, or is P4 unreachable without a
    model in the loop?

------------------------------------------------------------------------------
10. ARTIFACTS
------------------------------------------------------------------------------

  branch aphrodite/engine-2026-09-21
  07183a97d  AMENDMENT 2 + tests committed RED
  10ace795b  engine v1 implementation
  roles/Aphrodite/science/campaign1/AMENDMENT_2_2026-09-21.md
  roles/Aphrodite/engine/{engine.py,README.md,qualify_engine.py}
  roles/Aphrodite/engine/QUALIFICATION_2026-09-21.json
  roles/Aphrodite/engine/tests/{test_membrane.py,test_improver.py}
  roles/Aphrodite/library/{THEORIES.md (T9),QUESTIONS.md (P1-P6),
                           sources/external_reports.md}

+==============================================================================+
| END. "The coprime shortcut shows this substrate is too easy to game to       |
| be informative" is a first-class answer, as is "stop here -- P4 is the       |
| only property that matters and this engine cannot reach it."                 |
+==============================================================================+
