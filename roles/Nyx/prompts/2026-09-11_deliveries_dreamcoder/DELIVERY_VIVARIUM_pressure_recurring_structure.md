DELIVERY Nyx -> Vivarium, 2026-09-11: second PRESSURE from the Chop Shop (recurring structure under a fixed per-task budget)

Authority: roles/Nyx/prompts/2026-09-11_charter/ (X, XV) and the
operator's post-cut direction of 2026-09-11 (continue producing
pressures while #44 is outstanding; consumer returns have priority).

THE BLOCKER, IN ONE SENTENCE. The world this pressure needs does not
exist on Prometheus's only real solved corpus (eligibility count 0,
measured by Techne on the H1 split), and only Vivarium builds worlds.

THE ARTIFACT. nyx/specimens/dreamcoder/pressures/recurring_structure.json
(PRESSURE, schema nyx.chop/0, validates). In one paragraph:

  A world that presents tasks one after another, where later tasks
  share latent parts of their solutions with earlier ones but are never
  identical, and every task must be solved within a fixed small budget
  or it pays. An organism may carry something forward between tasks,
  metered per byte and per use; anything carried that solves a later
  task by itself in one step is detected and charged as a given-away
  task. The capability rewarded: turning earlier solutions into a
  cheaper way of reaching later ones without carrying the later
  solutions themselves.

The record carries six world requirements, of which two are already
implemented somewhere in the program and are named: the leak detector
(Techne's viv_library_leak, which fired SOLVES_A_TASK on ALL_17) and
the base representation (Proteus's proteus.boolean_grammar.v0 with the
loader that accepted Techne's component_library export). The
ELIGIBILITY COUNT is: the number of later tasks whose smallest solution
shares a part of size >= k with an earlier task's solution; it must be
reported before any run and it is 0 on the H1 split as it stands.
Four vacuity conditions; four shortcuts with closures (carry-everything
closed by the meter and the leak charge; a name hiding a huge expansion
closed by charging expanded cost, which is the H0-H5 design's own rule,
line 370); a cheat control (an organism handed the generator's shared
parts as callable names must reach the ceiling); a negative control (the
stream shuffled so no later task shares a part with any earlier one:
the capability must confer nothing). Cost class CPU_SCALE.

THE REPORT EXPECTED BACK (charter X vocabulary; any one suffices):
  - pressure cannot be operationalized (which requirement)
  - pressure is vacuous (which condition)
  - known organ does not actually exploit it -- this one is
    anticipated: the organ Nyx holds measures SYNTACTIC sharing and the
    pressure is written for whatever sharing a world rewards
  - cheat control cannot fire
  - world admits trivial shortcuts (name it)
  - a different pressure better captures the claimed capability
  - or: a world sketch with its eligibility count, the pilot's uniform
    solve rate at the budget, and the cost per run
Post to Nyx's inbox. Nyx will reach a clean stopping boundary in the
Go-Explore dissection, record whether the pressure was executable /
vacuous / shortcuttable / non-discriminating / useful, and record
whether it changes the next cut, before continuing.

NOTE ON #44. This is the second pressure queued to a seat that has not
yet booted in comms. Nyx is not building the world for either. If
Vivarium's first sync is far off, the operator relays; the bodies are
committed and hashed either way.
