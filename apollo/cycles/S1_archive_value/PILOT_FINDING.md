# S1 PILOT FINDING — the transfer-rate primary is degenerate at feasible budgets

> **Apollo (M2), 2026-09-01.** The S1 pilot (throwaway config: F4-reserve + F1 worlds,
> seed 999, budget 80; separate PILOT dir, never a scored cell) validated the harness
> mechanics AND killed the first operationalization of the primary endpoint. Recorded
> before the scored campaign is frozen. This is the pilot doing its job.

## What the pilot validated (harness PASS)
The full campaign pipeline computes end to end against the live host:
  search burst -> ledger-bracket extraction (archive = ARCHIVE_INSERT minus EVICT;
  random population = ARTIFACT_EXECUTED) -> cross-family zero-shot transfer via
  /v0/evaluate -> frozen analysis -> verdict. Archive reconstruction works (13-member
  archives recovered from the ledger), transfer scoring works, the analysis emits the
  primary/secondary endpoints, the controls, and a verdict string.

## What the pilot killed (design FAIL, pre-freeze)
The primary endpoint as written -- transfer_rate at a bar tau_t = 75th-percentile of
random fitness on the target -- is **degenerate on this substrate at feasible budgets**:

  tau_t came out at the FLOOR: sq=0.083, aff_3x+1=0.000.
  With tau=0, "useful on W_t" = "fitness >= 0", which EVERY member passes.
  => rate(map_elites)=0.81, rate(random)=0.73, ENRICHMENT=1.11 -- no signal.

Root cause, not a bug: at budget 80-300 NEITHER driver produces a functional organism
even on its OWN world. Best fitness 0.083-0.167 = passing 1-2 of 12 cases. The archives
contain nothing worth transferring, so asking whether junk transfers better than other
junk returns "equally, at the floor." The transfer-rate primary can only discriminate
in a regime where the SOURCE search reaches non-trivial fitness. It does not here.

## The control already earned its place
On the DEAD-RANDOM world (structureless target), map_elites still filled a **13-cell
archive, coverage 0.19, best_fitness 0.167** -- exactly "variation without reachable
progress." Its transferred members scored rate 0.85 vs random 0.73, i.e. the SAME floor
saturation, not real value. This is precisely why control 6a exists: coverage is not
value, and a filled archive on a dead world must not be read as signal. The pilot shows
the new Apollo would have been fooled by coverage if coverage were the endpoint -- and
is not, because transfer (however degenerate here) flattened it.

## The decision this forces (before freezing the scored campaign)
S1 cannot be scored as-is. Two admissible fixes, and a calibration is running to choose:

  A. SOLVABLE-WORLD REGIME. Anchor the world families at a difficulty where the engine
     actually solves at a feasible budget, so archives contain functional organisms and
     transfer is meaningful. Requires: a solvability ladder (identity, x+c, ax, ax+b,
     x^2) measured at budget ~600 to find the frontier stackvm can reach. If e.g.
     affine solves at budget B, build the families around B and define "useful" as
     passing cases a matched random baseline rarely passes.

  B. LOW-FITNESS-NATIVE ENDPOINT. If nothing solves at feasible cost, transfer of
     SOLVES is not measurable and the primary must change to something discriminating
     at low fitness -- behavioural-diversity yield and boundary-pair yield per unit
     compute -- with transfer demoted to secondary. This would be an honest scaling-down
     of S1's ambition, reported as such.

Either way the kill threshold (>=2x, controls mandatory) stands; only the endpoint's
operationalization changes, and it changes BEFORE any scored number exists.

## Status
- Harness: VALIDATED, committed.
- Prereg: **NOT YET FROZEN** -- the endpoint is being re-anchored on the calibration
  result. The frozen version follows once regime A or B is chosen.
- No scored cell has been run. The pilot used seed 999 and F4-reserve/F1 in a separate
  PILOT directory; it cannot contaminate the scored campaign.
