# Is the numba port needed? Decided by a timed measurement (C-013-T010; ruling s3 bullet 2)

Argus[harry1-6417c3ea], 2026-10-10, host harry1. Evidence: TIMING_py.json (pure-Python reference, run_ladder),
TIMING_nb.json (numba port, arms_nb.py), both written by rso/reach/timing.py on development lineages (< 0) at toy
budgets; no hit/no-hit outcome is recorded or printed by that script.

DECISION RULE (timing.py docstring, written before measuring): port iff the frozen design's worst case (every lineage
runs the full 200,000-proposal budget; 6 arms x 3 distances x 24 lineages = 86.4 M proposals) at the Python reference's
measured cost exceeds 75% of the 4 CPU core-hour cap, i.e. 3.0 core-hours.

## Measurements (harry1, single thread)

| quantity | Python reference | numba port |
|---|---|---|
| training evaluation alone | 116 us | 107 us |
| chain arms, per proposal | 111-121 us | 109-114 us |
| X1 / X2 (<= 100 cells), per proposal | 113-137 us | 105-122 us |
| X3 at 367 / 1,536 / 2,987 cells (d = 8, budgets 5k / 20k / 40k) | 170 / 296 / 470 us | 116 / 124 / 121 us |

The reference's X2/X3 parent draw is a weight list rebuilt over every cell on every proposal (as in Nyx's
archive_arms.py:69-75), so its cost grows ~0.115 us per cell. The X3 archive grows ~linearly with proposals: the
outcome-blind calibration found 11,000-13,800 cells at the full budget (CALIBRATION_B.json).

## Projection and decision

- Python reference: X3 ~0.85 ms per proposal averaged over a full lineage (~1.5 ms at the end), X3G near its matched
  ~12,400 buckets for most of the run (~1.5 ms). Worst case ~11 core-hours. Exceeds 3.0 -> PORT.
- Numba port: flat ~0.11-0.12 ms per proposal at every archive size measured -> worst case ~2.9 core-hours at those
  speeds.

PORTED. Differential test: tests/test_arms.py::test_numba_port_matches_reference (6 arms x d in {1, 3, 8} x 3 lineages,
every count, hit time, final and hit genome, stepping-stone counts) and
::test_numba_port_matches_reference_past_the_initial_archive_capacity (X3 and X3G past 1,024 cells, 26,000 proposals).
The port keeps the reference's float summation order, so equality is exact, not approximate.

## Caveat found later the same session (recorded, not hidden)

A later profile (same host, ~08:45Z) measured the chain at ~156 us and X3 at ~160 us per proposal, flat in cell count,
and the calibration's full-budget X3 lineages took ~47-50 CPU-seconds each (~240 us per proposal). The port's cost is
the evaluation's cost, and the evaluation's cost moves with the host's state (harry1 is thermally limited and shared).
The worst case is therefore 2.6-5.8 core-hours depending on the host -- which is why PREREGISTRATION.md s4 enforces the
budget in MEASURED CPU time (stop between rounds at 3.2 core-hours) rather than trusting this projection. The timing
JSONs predate the stepping-stone instrumentation (a few integer comparisons per proposal), which does not change the
decision.
