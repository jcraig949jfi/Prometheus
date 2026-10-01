# PREREG v2 Block R -- amendment 1 (before any Block R result exists)

Currency: 2026-09-30T13:30Z.

What happened: the first Block R launch (e9fd76349) ran three rbroad runs
concurrently (27 workers). The Claude Code harness stopped the runner for
host memory pressure; the Python run processes and the runner script
survived the stop, and this seat killed all of them at ~13:12Z (4.6 GB
free before, 19.1 GB after). No run finished; partial rows kept unscored
at tyche/runs/v2_blockR_ABORTED_memory/. No result was read beyond the
last generation line of three runs (best val gains per slot).

Cause (measured): each worker held 0.5-0.7 GB -- lens-output caches of up
to 200 float64 entries per world, binarised-output caches of up to 2000
int64 entries per world, and up to 48 worlds cached per worker.

Change (tyche/v2/eco_v2.py): lens outputs cached as float32 (<= 100 per
world), binarised outputs int8 (<= 150 per world), <= 12 worlds per
worker. Numerics: organism inputs are float32-rounded lens outputs; no
threshold, gate, world, seed or hypothesis changes. Measured after the
fix (rbroad, RES, 9 workers, 8 generations, seed 9, results unused):
max 287 MB per worker, 2.4 GB total. The runner now runs at most two
rbroad runs at once and kills its whole process tree on exit.
Tests 37 passed.
