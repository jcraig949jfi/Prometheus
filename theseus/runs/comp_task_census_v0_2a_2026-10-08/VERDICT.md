# THESEUS-36b verdict (prereg roles/Theseus/prereg/2026-10-08_composition_task_census/, 1aefecb56)

Run: python -m theseus.synth.task_comp_census --tag comp_task_census_v0_2a_2026-10-08
--ref v0_2a_2026-10-08 --workers 2. Unselected arms of the aligned split-reader substrate;
composition-necessary task (V 4, k 8, sensor-only readout; validated: every 1-part control at
chance, every store+release control 1.0, comp_task_2026-10-08/CONTROLS.json).

Solvers (J >= .6) / mean J, 100 viable genomes per arm:
  D 60 / .681   C 35 / .497   P 32 / .464   B 31 / .453   R 23 / .395
H-UNSEL: D > pooled one-shot (98/300) one-sided Fisher p 1.4e-6; D > R p 8.4e-8.
VERDICT: SUPPORTED -- without any task selection, deep descendants solve a task that only a
combination of parts worthless alone (for this task) can solve, about twice as often as
one-shot collisions and nearly three times as often as complexity-unmatched random programs
of this run.

Stated with the verdict (scope, not a discount):
- "Composition" here is TASK-relative: parts each insufficient for the task. The commonest
  solver is plausibly two transport rules in opposite directions (relay out + relay back),
  each of which acts on the state alone -- weaker than 30c's TRACE-inert parts. 36b does no
  knockouts; THESEUS-36's evaluation knocks out D solvers to name their parts.
- Solver rates are far above my expectation for every arm (P 32%, R 23%): composition in this
  task-relative sense is COMMON in this substrate, not rare.
- R here is the random arm of v0_2a (complexity-matched to that run's D, as in every run).

Predictions: W1 every arm <= 5% solvers WRONG; W2 H-UNSEL supported (p .2) -- the statement
"H-UNSEL SUPPORTED" came true, scored RIGHT.
