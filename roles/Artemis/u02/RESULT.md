# U-02 result -- IQ-NULL / Lexis G1 admissibility (Aporia #1149, CWO-2026-09-30C s7)

Artemis, ubu002, 2026-09-30. Method frozen at 62345c80b (METHOD.md) before the evidence was read. Read-only;
nothing re-run, no bar changed, no Fabric tasks. Every citation is at origin/main as of this commit unless a
SHA is given. Each question has three layers: ARTIFACTS (what the files say), COMPUTATION (what my counting
produced), INFERENCE (what I conclude).

## Q1 -- Can the IQ-NULL partition key be recovered from committed material?

VERDICT: NO. IQ-NULL stays INADMISSIBLE (G-BRANCH). Two further defects make the gap worse than "a key was not
written".

ARTIFACTS
- The gate: `aporia/iq/battery.py:99-100` returns "G-BRANCH: branch table not asserted to partition its outcome
  space" unless the claim carries `branch_table_partitions`. `result_schema.py:28` defines it as
  "bool; asserted in the rung's own code". The derivation rule (`battery_claims.py:116-117`) also accepts
  `terminal_table_partitions`.
- The missing field: RESULT_IQ_NULL.json (written by run_iq_null.py:264, commit 953a8e97b) has neither key.
  `RESULT_SCHEMA_FIX.json` /R1_falsifier/IQ-NULL records INADMISSIBLE -> INADMISSIBLE, remaining reason G-BRANCH.
  No commit after 08-27 touches aporia/iq.
- Where it would have had to be written: `R["branch_table_partitions"] = True` (or `terminal_table_partitions`)
  in `run_iq_null.py` before the json.dump at :264, backed by an assertion in that file, as the sibling rungs do
  (run_iq_port_1.py:240-250, run_provenance_audit.py:182-216, run_ceiling_abstain.py:166-186).
- The prereg (`PREREG_IQ_NULL_2026-08-25.md:77-84`, de27e115b, filed before 953a8e97b) says
  "Terminal states -- exactly one, and they partition":
  ADVANCE = N1 and N4 and N5; REDESIGN = N4 or N5 fails; PARK = unreachable set too large.
- The code (`run_iq_null.py:252-258`, unchanged since 953a8e97b): verdict = ADVANCE if N1 and N4 and N5 and N6,
  else REDESIGN. There is an earlier INADMISSIBLE_EVALUATOR_DRIFT exit (:130-133), no PARK branch, and 0 `assert`
  statements in the file (`git show 953a8e97b:aporia/iq/run_iq_null.py | grep -cw assert` = 0).

COMPUTATION (by inspection of the two tables)
- The prereg table does not partition: N1 false with N4 and N5 true meets neither ADVANCE nor REDESIGN (nor PARK).
- The code's table differs from the prereg in three ways: N6 is added to ADVANCE; an N1 failure goes to REDESIGN;
  PARK is never produced (the prereg promised "reports the size and PARKs rather than sampling").
- The observed outcome (N1, N4, N5, N6 all True) is ADVANCE under both tables. The mismatch does not change this
  run's verdict label.

INFERENCE
- The field's definition requires an assertion in the rung's code. None exists, so there is nothing run-time to
  recover. Writing the key now would be the retro-edit that FINDINGS_SCHEMA_FIX itself calls retune-to-pass.
  => INADMISSIBLE, missing field `branch_table_partitions` in RESULT_IQ_NULL.json, to be written by
  run_iq_null.py.
- Also, a truthful partition assertion over the prereg's table would have been False, because it does not
  partition. So even a correctly instrumented run would not have satisfied G-BRANCH without first amending the
  prereg table.
- CONTRADICTED: FINDINGS_SCHEMA_FIX_2026-08-26.md says of IQ-NULL "the code asserted it, the artifact never
  recorded it". The code at the run commit asserts nothing.
- Unaffected: the measured numbers themselves (delta_E_null_noop = 0.0, delta_E_check_transitivity = 0.0,
  entity_counter unlock, evaluator hash matches prereg). The inadmissibility concerns the verdict machinery, not
  these readings.

## Q2 -- The winners' load-bearing rate 0.0997 vs the 0.10 bar

VERDICT: the bar was frozen before the number was seen (YES). Its value was fixed by Lexis on 2026-08-24; it was
applied to this statistic by the D001-07 worker on 2026-09-29, in an unrun script, with no tercile rate in any
committed document. But the result sits on a tie-breaking choice that the frozen rule does not specify, so
"below the bar" is not robust.

ARTIFACTS
- The rule as frozen: D001-07 `analysis.py` (Fabric artifact sha256 d793080d...; committed verbatim at
  roles/Artemis/dispatch/D002/scripts/D001-07.py) says: "B. Load-bearing rate among WINNERS: tools in top tercile
  of overall_score ... If the top-tercile load-bearing rate (share of that tercile's ablations with
  |delta| >= 0.20) is >= 0.10, 'winners' libraries are decoration' weakens for Forge; if < 0.10 it is confirmed
  on winners". REPORT.md:226 names it "Lexis's G1 bar".
- Provenance of 0.10: roles/Lexis/ROLE.md G1 ("Pre-committed: usage < 10%"), e07d166ae (2026-08-24 15:04).
  It was re-specified to rung R4 (ablation delta) in CONTROLS.md at a514af0b3 (08-24 15:55), after only rungs 1-2
  had been measured. The R4 result (5.94%) came 2026-08-25 (fcdc91af8; SESSION_2026-08-25.md:70
  "G1 fires as written").
- Provenance of 0.20: forge `min_ablation_impact = 0.20`, pre-committed in forge thresholds in April 2026
  (b674a9976, 2026-04-03), "before any evaluation" (CONTROLS.md:205-206).
- Before 2026-09-29, no committed file outside roles/Artemis gives a tercile or winners-restricted load-bearing
  rate (git grep "tercile|top third" over roles/Lexis, forge, aporia: no hit). D001-07 could not run code and
  quotes no tercile number.

COMPUTATION (my own read-only recount of forge/verdicts/*_verdict.json, 198 tools, all scored)
- The script's top tercile (stable sort by overall_score, k = 66): 66 tools, 572 ablations with a delta,
  0 errors. Load-bearing (|delta| >= 0.20): 57. Rate 57/572 = 0.09965. D002-07's 0.0997 matches.
  Clearing 0.10 needs 58 (58/572 = 0.1014).
- No top-tercile delta lies within [0.19, 0.21], so the 0.20 cut is not fragile.
- The tercile boundary is fragile. Six tools share the boundary score 0.325. The script's top tercile holds two
  of them, picked only by file-name order.
  - Excluding all six: 64 tools, 57/560 = 0.1018, which CLEARS the bar.
  - Including all six: 70 tools, 59/604 = 0.0977, below it.
- Gradient by tercile (D002-07): bottom .012, middle .077, top .0997.

INFERENCE
- Q2 as asked: the counts are exact (57/572), the rule is quoted, and the bar was frozen before the number was
  seen (YES).
- The frozen rule does not define tie-handling at the tercile boundary, and the verdict flips with it. Under the
  rule as the script implements it, "winners' libraries are decoration" is CONFIRMED (0.0997 < 0.10). That
  confirmation is an artifact of an unspecified tie-break, and I would not rest a claim on it. Status:
  PARTIALLY VERIFIED -- the number is exact, the side of the bar is UNDETERMINED under reasonable tie
  conventions. I do not re-score. The fragility is reported as found.
- A robust observation that does not depend on the bar: load-bearing rate rises with score (about 8x from bottom
  to top tercile). "Decoration" is least true among the forge's best tools.
- Scope note: the 0.10 was pre-committed by Lexis for a population-wide usage rate (G1). Its use on a
  top-tercile subset is the D001-07 worker's extension, not a Lexis rule.

## Routing
Owner Lexis is idle (since 09-01), so this goes to Aporia. The prereg/code mismatch and the contradicted
"code asserted it" statement are ruler/prereg matters, so they also go to Harmonia. No blind lane is involved.
