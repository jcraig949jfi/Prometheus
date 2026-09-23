+=====================================================================+
|  C4-07 -- THE COST OF INSULATION: PREREGISTRATION / RE-PREMISE        |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
+=====================================================================+

QUESTION (directive)
  Is graceful degradation useful only when it is free, and if so does it
  collapse into neutrality? Cost only the recovery/fizzle event itself;
  do not reward avoiding it.

THE PREMISE, CHECKED AGAINST C4-03 (D4-007)
  The directive's method starts from "the most informative local-
  insulation condition from C4-03". C4-03 found none: on this substrate
  932 of 932 parent instruction words are outside the opcode table and
  the interpreter's modulo decode is the instruction set; P(would-be-
  fatal) = 1.000 on every child. There is no "fizzle event" distinct
  from ordinary execution -- every executed instruction is the insulated
  kind -- so "cost only the recovery/fizzle event" would cost every
  instruction, which is the existing alpha (ops) term of the economics
  regime, already studied in campaigns 1-3 (READOUT_ssf.md: cost shapes
  ops before it shapes anything else).

WHAT COULD BE COSTED INSTEAD, AND WHY IT IS NOT DONE HERE
  Two countable events come close to "an operation that only worked
  because of insulation": an operand index that was reduced modulo
  n_regs, and a tape address that was reduced modulo tape_words. Both
  are countable in the interpreter's meter without an ISA change, but
  (a) reduction is the PUBLISHED semantics of every operand (there is no
  un-reduced reading against which it is a recovery), and (b) costing
  them would attach a price to the representation itself, which the
  directive forbids ("no reward term names robustness ... or a desired
  architecture") -- a cost on reduced operands is a reward for programs
  that keep their indices in range, i.e. for a representational
  property. This is not a different question the slot may substitute; it
  is the forbidden kind.

DISPOSITION
  REPRESENTATION_BLOCKED. No condition exists on the frozen substrate
  that isolates an insulation event from ordinary execution; the cost
  frontier the directive asks about cannot be placed. Recorded through
  the stack (one sealed preregistration, one engine record carrying this
  text's digest), not converted into an ISA or economics change.

WHAT IT LEAVES FOR CAMPAIGN 5 (a recommendation, not a slot)
  A substrate with a distinguishable insulation event -- an explicit
  trap-and-continue on an undefined word, with the ISA's in-table
  encoding made narrow enough that random words are usually undefined --
  is a NEW representation, and the cost frontier is a Campaign 5 question
  on that representation. Everything C4-01..05 measured here would need
  re-measuring there; the damage geometry does not transfer by
  assumption.
