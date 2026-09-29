# Worker K: what minimum evidence shows an intervention reached its mechanism?

ID W-K. Output workers/W-K/. Namespace 0x5F0. Read COMMON_RULES.md and
COMMON_RULES_ARC3.md first. Budget ~4 h. CPU.

QUESTION
Several Prometheus experiments reported nulls (or effects) from
interventions that could not have affected the claimed pathway. What is
the MINIMUM evidence sufficient to claim that an intervention actually
reached the candidate mechanism? Build ADVERSARIAL FIXTURES: runnable PTE
reconstructions (hand plants and small harnesses in your directory) of
each known failure SHAPE, where the intervention is inert, mistimed,
unwired, mis-targeted or forced. Then test candidate checks against the
full fixture set, including (not limited to) pathway reach; a positive
control run through the arm's own code; non-identical arms under common
random numbers; event-window coverage; state-change verification; an
arm-diff of actual inputs/targets; a could-fail counter-plant. Measure
which checks catch which fixtures, and what each costs. It is acceptable
if no single check is universal. If intervention classes need different
reach evidence, document the mapping.

EVIDENCE (raw)
- The mined case list with primary-file pointers in other seats:
  workers/W-D/ (and the primary files it cites on origin/main). Treat its
  REPORT.md as a hypothesis source (ARC3 rule 2).
- PTE instruments: prometheus/ananke/lens.py (carrier_table,
  arm_identical, cue_arrival_profile, reach), c1b.py (control batteries,
  no-op guards), engine.Controls (all intervention switches);
  instruments/*.md; tests/test_lens_instruments.py (plant fixtures).
- C1 D-A (window miss) and routing vacuity: roles/Ananke/pte/C1_ERRATA.md.
REQUIRED: PLAN.md frozen (fixture list, candidate checks, the scoring
rule) before scoring. Each fixture must have a VALID twin (the same
intervention correctly wired) so that a check that flags everything is
penalized.
DELIVERABLE: the report in your final message; a fixture x check matrix
in out/; DISAGREEMENTS.
STOP: 4 h.
