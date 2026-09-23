# Aphrodite methodology: permanent invariants

Standing rules this seat applies to its own work and to any claim it
assesses. Promoted here by operator ruling, not by the seat's preference.
Each carries the measurement that produced it.

--------------------------------------------------------------------------
INVARIANT 1 -- STRUCTURAL NOVELTY IS BASIS-RELATIVE
--------------------------------------------------------------------------

  A discovered mechanism cannot be credited as load-bearing when an
  allowed primitive implements the same input-output transformation
  within the surrogate budget.

Promoted 2026-09-21 (operator ruling on slice 2C).

ORIGIN. The local engine's grammar contained `gcd` as a primitive. A
lineage-discoverable helper implementing EUCLID'S ALGORITHM -- a genuine
bounded loop, searched for and not handed -- solves the numtheory class at
accuracy 1.000. The surrogate battery defeats it with a single
substitution: `gcd(x, y)`. Every capability class in that distribution sat
one primitive application from solved, so no structural mechanism could be
credited at any lineage count under any entropy. Certified analytically
before any lineage was run: structural_success_criterion_satisfiable =
FALSE.

WHAT IT IS NOT. It is not "loops good, primitives bad", and it is not a
claim that the mechanism is causally inert. Euclid genuinely computes the
answer. The point is sharper:

  A mechanism can be causally real and still COMPUTATIONALLY DECORATIVE
  relative to its substrate.

WHY IT GENERALISES. It is a falsifier for scaffolding claims, recursive
tool-use claims, agent architectures and some forms of learned modularity.
If a base model performs X in one forward pass, scaffolding that performs X
is decorative however elaborate its control flow. The question "did the
system discover an algorithm?" is UNANSWERABLE without naming the basis the
claim is relative to -- and most published claims do not name it.

HOW TO APPLY IT. Before crediting any structural or architectural claim:
  1. name the basis (primitives, base-model one-step capabilities, library
     calls, tool endpoints available to the system);
  2. construct the simpler causal surrogates -- constants,
     identity/passthrough, trivial single-primitive expressions, simplified
     control flow, removal/bypass;
  3. if any surrogate preserves the claimed capability under hostile
     evaluation, the structure is not credited;
  4. report presence, invocation, looping, depth and component counts as
     TELEMETRY ONLY. They are not evidence.

--------------------------------------------------------------------------
INVARIANT 2 -- THE BASIS-SEPARATION CERTIFICATE PRECEDES THE SEARCH
--------------------------------------------------------------------------

  A task family and its primitive basis are chosen JOINTLY, before any
  evolutionary search, and frozen only after a certificate shows that
  structural success is possible at all.

Promoted 2026-09-21 (operator ruling on slice 2C). The certificate is part
of the experiment, not an emergency diagnostic run afterwards.

For each proposed task family, establish BEFORE evolution that:
  B1 no depth/size-bounded composition of primitives solves it;
  B2 no single primitive surrogate reproduces a qualifying mechanism;
  B3 at least one bounded multi-step mechanism CAN solve it;
  B4 that mechanism requires a property actually being studied --
     persistent state, variable-length accumulation, branching, iteration
     to convergence, or a reusable intermediate representation.

Then freeze the family. If B1-B4 cannot all be met, the family is not used,
and no search is run against it.

COROLLARY, learned the expensive way: choosing the basis AFTER seeing which
basis change creates the opportunity makes the next result uninterpretable.
When slice 2C established that removing `gcd` would manufacture the
opportunity, that distribution became unusable for the question -- the
answer was already known. Both halves of the design must move together and
both must be declared before either is measured.

--------------------------------------------------------------------------
INVARIANT 3 -- A KNOWINGLY RED SUITE IS NOT A RECEIPT
--------------------------------------------------------------------------

Promoted 2026-09-21. Defect witnesses stay EXECUTABLE but leave the main
suite: strict xfail in a historical regression suite, so a green run means
green and a silently self-repairing defect fails loudly instead of being
absorbed. A suite that is "red on purpose" cannot be cited as evidence
about anything else it covers.

--------------------------------------------------------------------------
INVARIANT 4 -- INSTRUMENT DEFECTS LEAVE SCARS, NOT FOOTNOTES
--------------------------------------------------------------------------

Promoted 2026-09-21. When an implementation turns out not to have
instantiated the declared design, the affected result is marked IMPAIRED
where it lives, with its still-valid parts enumerated separately, and the
defective code path is retained so the impaired result can be reproduced
rather than trusted. Slice 2B's structural arm is the worked example:
engine/SLICE2B_VALIDITY_SCAR.md.


--------------------------------------------------------------------------
INVARIANT 5 -- A COMPONENT OF A FACTORISATION IS NOT AN ABSTRACTION UNIT
--------------------------------------------------------------------------

Promoted 2026-09-22 (Tier 3C).

  Do not abstract over one component of a program that decomposes in
  several equivalent ways. The component's form is contingent on its
  partner's, so syntactically incompatible components may implement the
  same program.

ORIGIN. A donor searching a sum-of-squares family did not find loop body
`acc + v*v` with final `acc + first`. It found body `acc - v*v` with
final `first - acc` -- accumulating the NEGATIVE sum and negating at the
end. Anti-unifying that against its other observed body `(v + acc)`
yields nothing: different operator AND different arguments. The donor
therefore formed no abstraction at all, and the slice's treatment arm
degenerated into its control.

APPLY IT BY: abstracting over WHOLE-PROGRAM semantic classes, or
canonicalising the factorisation (fixing a sign/scale/offset convention)
before abstracting. This generalises past this engine: any scheme that
learns "reusable parts" from its own successes must first fix what a part
IS, or it will learn parts that cannot be recombined.

--------------------------------------------------------------------------
INVARIANT 6 -- THE CONFORMANCE GATE
--------------------------------------------------------------------------

Promoted 2026-09-22, after FOUR slices were damaged by the same failure:
the implementation not matching the declared semantics (an asymmetric
enumerator; string-vs-semantic identity; an unguarded exponent; an
accumulator ceiling present in the searcher and absent from the emitted
artifact, which hung a run for 1,829 s).

  Where two evaluators exist for the same declared semantics, they must
  be DIFFERENTIALLY TESTED over normal, boundary, overflow and failure
  values before any run. No run begins while the gate is red.

In this engine that is engine/conformance.py: 900 program shapes x 24
input configurations = 21,600 comparisons between the search evaluator
and the sandboxed artifact evaluator. The first slice to start from a
green gate was also the first to hang nothing and leak nothing.

--------------------------------------------------------------------------
INVARIANT 7 -- QUALIFY THE GENERATOR, NOT ONE SAMPLE
--------------------------------------------------------------------------

Promoted 2026-09-22 (Tier 3B failure, Tier 3C repair).

  A discrimination guarantee established on ONE drawn development set
  does not transfer to other draws from the same generator. Qualify the
  GENERATOR: many independent draws per candidate size, a survival rate
  for wrong semantic classes, a confidence bound, and rejection of the
  family if the bound is not met.

EVIDENCE. Tier 3B qualified a battery to a zero false-positive basin on
its chosen sample and then measured 4.688 false positives per recipient
on fresh draws of the same size. Tier 3C qualified generators over 200
draws per size, rejected three families of nine -- including both that
had poisoned Tier 3B -- and recorded ZERO false positives across three
families and ten arms.

--------------------------------------------------------------------------
INVARIANT 8 -- IDENTICAL CONTENT MUST COST THE SAME
--------------------------------------------------------------------------

Promoted 2026-09-22 (Tier 3C design error).

  Randomisation must be PAIRED across arms and candidates. If two
  configurations with identical content can score differently, the
  comparison measures the seed.

EVIDENCE. Two candidate libraries with byte-identical expansions scored
13,479 and 51,018 -- a 3.8x spread -- because the search seed string
contained the library's NAME. The donor's selection between them carried
no information, and the cross-validation built to reward abstraction was
never functional.

--------------------------------------------------------------------------
INVARIANT 9 -- VERIFY TERMINATION BY PID
--------------------------------------------------------------------------

Promoted 2026-09-22.

  Task-control acknowledgement is not process death. Verify that the PID
  and its tree are gone.

EVIDENCE. Two detached python children survived TaskStop; one ran 18
hours at 3.8 GB, contaminating wall-clock measurements across two slices
and prompting a wrong diagnosis of a third. Those wall-clock figures are
permanently marked contaminated; the charge-based endpoints they
accompany are unaffected.
