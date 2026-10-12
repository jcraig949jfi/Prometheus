# EXPOSURE -- what Pallas had seen before the C-016-T040 challenge set was written

Pallas[harry1-855aa018], claude-fable-5-1 (Q3; runtime verified by `python -m comms boot`, tier heavy), headless on
harry1 (M4). Session boot 2026-10-11 ~11:25Z. Worktree C:/Prometheus-worktrees/pallas-c016-t040, branch
pallas/c016-t040, base a5699de6e (origin/main at fetch). Claim on main 7c95657ab (11:38Z).

## No confirmatory outcome exists

FREEZE.md and T030's receipt state that no confirmatory lifetime (seeds 16_330_001..400) has been executed and that
no endpoint of any searched subject has been computed. There is no rso/ensorain/runs/ directory at the base. T050 (the
run) is not claimed. Nothing in this set runs a confirmatory seed, calls `assay confirm`, or computes an endpoint of a
searched subject. The searched genomes were read only for their STRUCTURE (plastic keys, eta, sigma, op list; the
same facts PREREGISTRATION s8 states). The 5 subjects without a plastic key have a deterministic verdict that could
be derived from the genome text alone; I did not derive it, because that would be the confirmatory outcome.

## Verified before writing

`python -B -m rso.ensorain.freeze check` printed OK at a5699de6e (26 files; FROZEN.json LF sha256 b198ab8f...
quoted in FREEZE.md). Environment harry1 / Python 3.12.10 / numpy 2.4.3 equals FROZEN.json. The independent hash
walk is case S1.

## Read in full (the packet says to)

PREREGISTRATION.md, FREEZE.md, FROZEN.json, COMPATIBILITY.md, ONBOARDING.md, SUBJECTS.json (structure),
DEV_QUALIFICATION.json (verdict block and one row; the rows file is the committed development evidence),
rerun_c_demand_result.json; rso/ensorain/{assay,analysis,subjects,freeze,rerun_c_demand}.py and
tests/test_assay.py; ensorain/wtp5/{tape,worlds,planted}.py; rso/registry/README.md and `registry for-adapter`;
the operator directive of 2026-10-11; the Palamedes wake note. The test bodies were read: this is an informed coverage
review of a frozen surface, not first-sight.

## One exposure to disclose

ops/campaigns/C-016/tasks/C-016-T030/TASK.json (read on main for the packet's lineage) carries the integrator's note
"integrator mutant (G_PRE gate removed from verdict) killed by test_smuggler_refused_reference_detected_on_dev". That
mutant (deleting the `if not st["G_PRE"]` branch) is therefore NOT in this set; the G_PRE edits here are different
(which arm the gate reads, E2; which threshold it uses, E6). The note also says "Coordinator endpoint alone would have
passed both Smugglers -- G_PRE is Argus's catch", which PREREGISTRATION s8 already states.

## Design-time discipline

No challenge genome was run before this set was committed. The predictions in expected.json come from reading
tape.py's update rule (tape.py:313-349) and the gate observation space (worlds.py:254-269), not from trial runs. The
one quantitative design argument (P2, the timer) is in CHALLENGE_SET.md with its assumptions; if its prediction fails,
that is reported as a miss, not re-fitted.

## Not seen

No confirmatory row, no searched-subject endpoint, no repair diff, no Ensorain WTP-05 DEEP result (ubu006, ETA
~13:00Z; nothing here touches ubu006 or a WTP-05 seed).
