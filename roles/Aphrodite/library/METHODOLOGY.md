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
