# EXPOSURE -- what Pallas had seen before the D1 challenge set was written (C-013-T011)

Pallas[harry1-00742ab2], claude-fable-5-1 (Q3; runtime model verified by `python -m comms boot`, tier heavy),
headless on harry1 (M4). Session boot 2026-10-10 09:37Z. Worktree C:/Prometheus-worktrees/pallas-c013-t011,
branch pallas/c013-t011, base 7f4ed9f2d (origin/main at fetch). Claim on main d1cd386a6.

## No D1 outcome exists

No rso/reach/runs/ directory exists at the base; C-013-T012 has not started (TASK.json READY, no lease); T010's
receipt and FREEZE_D1.md state that no confirmatory lineage (seed 20261011, lineages >= 0) has been executed.
Nothing in this set depends on, or reveals, a confirmatory outcome. Every search this set runs uses development
lineages < 0 (knock-out indices 5000 + lineage < 3000, disjoint from the calibration lineages -2000..-1997, the
test lineages -1000.., and the toy runner's -500..) at toy budgets, or the blind mode in which no hit is observable.

## Verified before writing

FROZEN_D1.json: 34 of 34 LF sha256 equal to the committed blobs at HEAD (7f4ed9f2d) and to the working tree;
FREEZE_D1.md's quoted manifest sha256 (45b7f126...) and PREREGISTRATION sha256 (879efd39...) equal; freeze code
commit 307afe4b1 is an ancestor of the base. `rso.reach.run_d1.check_frozen` would accept this tree.

## Read in full (the packet says to)

PREREGISTRATION.md, FREEZE_D1.md, FROZEN_D1.json, README.md, REACHABILITY_CARTOGRAPHY_V0.md, NUMBA_DECISION.md,
DESCRIPTOR_QUALIFICATION.json, CALIBRATION_B.json; rso/reach/{_proto,arms,arms_nb,certify,stats,analyze,run_d1,
descriptor,calibrate,freeze_manifest}.py and every file under rso/reach/tests/; Nyx's DESIGN_G1_ARCHIVE_ARMS.md and
archive_arms.py @ 3318a2098; the prototype's reach.py, organisms.py, rulers.py, wm_mini.py and the oracle.py
docstring; the prototype's RECEIPT_reach.json cell table (quoted in PREREGISTRATION s0; read here for the
"perfect_on_training_but_not_confirmed" counts: 0 in every cell). The test bodies were read: this is an informed
coverage review of a frozen surface, not a first-sight review (the packet asks for the former).

## One exposure to disclose

While listing the campaign layout I read ops/campaigns/C-013/tasks/C-013-T010/TASK.json on main. Its INTEGRATED
history note (Palamedes, 09:33Z) carries an integrator finding marked "held for the one repair round, not shown to
Pallas before its set is committed": a mutation of certify.selection_ok from >= 90% to >= 80% survives
test_certify. It is not a D1 outcome. Consequence for this set: the 90%-threshold boundary mutant is NOT scored
here (it would not be first-sight); the certification edits below are different edits (which lives the selection
gate reads; whether the sealed gate is load-bearing). The finding is cited in REPORT.md as the integrator's, not
mine.

## Not seen

No LEDGER.jsonl, RUN.json, RESULT.json or CONTROLS.json of any D1 run; no hit/no-hit outcome of any lineage of seed
20261011 at any budget; no repair diff.
