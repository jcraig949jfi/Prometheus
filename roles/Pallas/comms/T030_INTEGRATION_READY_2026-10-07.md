C-009-T030 INTEGRATION_READY -- Pallas[harry1-2697f39e] (harry1, claude-fable-5-1, headless; same lease as harry1-b97f1fc4)

Read first: rso/binding/challenge/B1/REPORT.md (on branch pallas/c009-t030, pushed; merged origin/main 94f95e2d1 at
c5bb5675f). Receipt: ops/campaigns/C-009/tasks/C-009-T030/attempts/A-001/RECEIPT.json (state commit on main, with the
INTEGRATION_READY transition).

Order held: claim 4aaa10bbb (03:31:32Z) < set 1b9c19ba9 (03:42:34Z) < dry controls 03:43:02Z < driver repair 9f58a0cef
< launch 1 03:44:33Z < launch 2 03:45:05Z (torn at ~03:47Z by the headless exit) < resume 3ed43a232 < launch 3
04:22:20Z-04:42:16Z. Data files byte-identical to the set commit. FREEZE_B1 48/48 re-verified before launch 3. No test
body under rso/slice001/tests/ or rso/witness/tests/ opened by either instance.

Torn launch 2: kept as censored (mutation_rows_launch2_interrupted.jsonl); its two ledger rows without END read
INTERRUPTED (uncharged); no END rows fabricated; the whole mutation driver re-run as launch 3 (the packet's third and
last). Launch 2's completed children agree with launch 3 (baselines PASSED, E1 KILLED).

Score (r1 base, scored): sound 2/3, broken 5/6, controls 2/2; synthetic base the same pattern (claim checks unscored:
G-RECOMP fails on the fixture traces, baseline included). Edits: 5 proposed / 5 executed / 2 killed (E1, E5, by the
slice suite) / 3 survived the targeted AND the full 433-test frozen suite, all witnessed (E2 launch kind, E3 child as
node run, E4 digest-less row binds). Predictions 9/9 cases on polarity, 5/5 edits; one reviewer check-design error
(FAILED_RETRY_KEEPER scored INCORRECT on an identical-check; the only differing field is the embedded RUN_INVENTORY
custody row id -- a correct acceptance; REPORT s2).

Per surface (REPORT s3): BX7 CLOSED within coverage. BX1 NOT CLOSED (E2). BX2 NOT CLOSED (E3, E4). BX5 NOT CLOSED:
B1.BROKEN.SIBLING_UNREPORTED admitted on both bases -- a second COMPLETED execution of a required node under the
anchored launch, carrying the digest of an unpresented FAIL receipt, is invisible to G-INV (BX2 binds the cited row;
BX5 reads only nodes without a presented receipt). Applicable-conditional: needs a runtime that gives re-executions
distinct run ids; NOT reachable through rso/witness/ares_client.py's Launch as drafted (run_id = launch/node, a repeat
is BIND_AMBIGUOUS_ROW). Producer side unchallenged (controls only). Probe: s2_run.consumer_for builds the Bundle
without run_id, so the production path never raises LAUNCH_UNBOUND for a run.json substitution (T011 notes (1)).

CC3's letter ("no unresolved applicable survivor") is not met by my reading: 3 witnessed edit survivors
(test-coverage class, the frozen code refuses each shape; committed fire cases pin them: LAUNCH_IS_NODE_RUN,
CHILD_AS_NODE_RUN, LEGACY_ROW) + 1 behavioural, applicable-conditional survivor + 1 wiring gap. Adjudication is yours
and the operator's. The one repair round would not touch production code for three of the four. A re-check must use
fresh shapes.

Acceptance on the merged tree c5bb5675f: slice001 OK (skipped=1), binding 13 OK. Ledger: packet 3 of 3 launches,
1347.5 CPU-s; campaign 8 of 12 launches, 1518.2 of 5400 CPU-s. The ledger rows are on my branch (appended only):
integrate before another seat appends. Nothing under rso/binding or rso/slice001 changed upstream since the freeze.

Headless lesson, for the wake template: the previous instance ended its turn to "wait" for a background run. This
instance polled from foreground until-loops. Closing after this note (packet-only session).
