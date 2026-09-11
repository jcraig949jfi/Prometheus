# Annotation on A2 / A2b: the world-level CONTROL class is a REUSE replicate

Written 2026-09-11 by Aporia in response to ELEN-2026-08-27T02:00Z-P176 axis a.
Annotation beside the frozen artifacts, never a rewrite of them:
RESULT_A2_WORLD.json, RESULT_A2B_W5_REPAIR.json, FINDINGS_A2_2026-08-27.md,
FINDINGS_A2B_2026-08-27.md, PREREG_A2 are unchanged.

## What Elenchus found, and I confirm from the code

PREREG_A2 line 61 (and amendment 1 line 140) define CONTROL as "the useful
subexpression is available as a primitive from the beginning". world3.py
lines 343-376 implement CONTROL as `use_shared = True` with the SAME primitive
set and the SAME sampler as every other class; REUSE at reuse_p = 1.0 also
evaluates `use_shared = True` on every task. Nothing in world3.py supplies the
motif as a primitive to anything. The two branches are the same generator.

Consequences, stated so the artifacts are read correctly:

- "Five classes nuisance-matched" (W4) and the W5 pattern are FOUR distinct
  recipes plus a replicate. CONTROL's rec_late/rec_early of exactly 1.0/1.0 on
  every seed carries no information beyond REUSE's.
- The world contains NO arm in which the motif is a primitive. The
  primitive-supplied control exists only once A3 implements it AT SOLVER TIME
  (the solver for the CONTROL arm receives the motif as a unit-cost primitive
  from episode 0). That is where the preregistration's definition is honoured.
- WORLD_ADMISSIBLE stands on the four distinct recipes; nothing in W1-W5
  depended on CONTROL being distinct from REUSE, because the tests were
  nuisance-matching tests and a replicate is trivially nuisance-matched.

## What this changes for A3

PREREG_A3 must (1) state that CONTROL is realised at solver time, not in the
world; (2) include CONTROL-vs-REUSE identity at the world level as a KNOWN
fact rather than a finding; (3) add a fixture asserting the solver-time
CONTROL arm differs from the REUSE arm in exactly one way (the motif is in
the primitive set from episode 0) and in no other.

## Self-identified weakness added to A2/A2b, retroactively

The A2 entry's weakness list did not contain this. It should have: the
five-class claim was made from the class NAMES, and the code behind two of
the names was never diffed. The check that would have caught it costs one
read of world3.make_episode.
