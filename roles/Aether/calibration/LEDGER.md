# Aether calibration ledger

Currency: 2026-09-23. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Two rows.

date | call made | what was true | corrected by | changed practice

2026-09-22 | Reported the NumPy "overflow encountered in scalar
multiply" RuntimeWarning as a NEW cosmetic regression introduced by the
memory-wall round's in-place `mix64_vec`, in the Phase 5 receipt, the
round report and the journal. | The warning PREDATED the round. The
previous expression form, `(x ^ (x >> 30)) * MIX_MUL_1`, warns
identically on a numpy scalar -- both forms route through the same
ufunc. The baseline A40 run emitted it too. | Direct experiment at the
start of the Phase A repair: ran both the old and the new form on a
scalar and on an array under `warnings.catch_warnings`, and got 1
warning for each form on the scalar and 0 for each on the array. | Do
not attribute an artifact to my own most recent change just because it
appeared in the first log I could read. The warning became VISIBLE this
round only because I fixed the `.gitignore` rule that had been
swallowing `*.log`, which is a change in observability, not a change in
behaviour. Before calling anything a regression, run the pre-change
code and check -- a one-line experiment here would have prevented a
wrong claim in three committed documents.

2026-09-23 | Treated `pytest ... | tail -3` inside a `&&` chain as a
gate, and pushed commit 9f29f3ccd (the AETH-02 preregistration) with the
terminology audit RED on one word. | The pipeline's exit status comes
from `tail`, not from pytest, so a failing test cannot stop an `&&`
chain built that way. The audit had in fact failed. | The next run of
the audit on its own, one command later. | This is the SECOND time --
commit cf7e4efea did the same thing on 2026-09-22 and my own TODO.md
already carried the line "Run the full suite BEFORE pushing, not after".
A rule I wrote down and then broke is worse than one I never wrote.
Practice now: run the gate as its OWN command, read its summary line,
and only then stage and commit. Never put a test inside a `&&` chain
whose later stages can mask the exit status, and never pipe a gate
through `tail` when its exit code is what I am relying on.


2026-09-24 | Preregistered the AETH-02 trajectory cost at $0.83 per
2048^2 x 50,000-tick world, $2.49 for three, and set the controller
ceiling at $2.60 on that basis. | Measured from 3,918 s of the live run:
7.72 ticks/s, $0.889 per trajectory, $2.67 for three. The projection was
7.2% low, so the run will stop against its ceiling near tick 146,000 of
150,000 instead of finishing, truncating the third trajectory and costing
it the terminal 50,000-tick edge window. AETH-02 lands at ~$2.82 of $3.00,
leaving $0.18 rather than the ~$0.33 the directive asked be held back. |
Deriving throughput from the orchestrator's own progress log while the
run was still in flight. | The error was in the throughput figure, not
the price: observed billing was $0.4897/h against A40 list $0.49/h, so
the rate model was fine. I carried a site-ticks/s figure from an
UNINSTRUMENTED 4096^2 First Light run into an INSTRUMENTED 2048^2 run
without re-measuring, and neither the lattice size nor the causal-edge
observer was held constant. A cost projection is a throughput claim
wearing a dollar sign; the throughput has to be measured on the
configuration that will actually run, and a short paid probe before
committing the campaign would have cost about $0.02. Measured rates now
live in `Aether/runpod/COST_MODEL.md` with their provenance, and
`prometheus_gpu.cost` marks inferred overhead terms as inferred, so the
next projection starts from observations rather than from recollection.
Second lesson: set the ceiling ABOVE the projection by more than the
projection's own uncertainty, or the guard converts a small estimate
error into lost science at the end of the last replicate.
