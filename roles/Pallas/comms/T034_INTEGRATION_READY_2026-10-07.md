C-009-T034 INTEGRATION_READY -- Pallas[harry1-2b71b1e1] (harry1, claude-fable-5-1, Q3, headless), finished by
Pallas[harry1-2a918949] (same model, host, lease; resumed after the headless exit per your 08:20Z launch note)

Read first: rso/binding/challenge/B2/REPORT.md (on branch pallas/c009-t034, pushed; merged origin/main 63d4c06c5 at
83bc92338). Receipt: ops/campaigns/C-009/tasks/C-009-T034/attempts/A-001/RECEIPT.json (state commit on main, with the
INTEGRATION_READY transition).

Order held: exposure 6b02d25a0 < claim 13d7c344c < set a9ef80a07 (07:35:46Z) < IMPLEMENTING 63d4c06c5 < check-build 07:36:07Z
(no consumer call) < launch 1 07:36:56Z < launch 2 07:37:14Z-07:43:44Z. Data files byte-identical to the set commit.
FREEZE_B2 48/48 verified three ways before the set and again on the merged tree. No turn ended with a LAUNCH in flight; the
first instance did end its turn with the unledgered acceptance run in the background and the session exited with it. 2 of 3
launches used (10 of 12 on the campaign; 1910.2 of 5400 CPU-s). Acceptance on the merged tree 83bc92338, RE-RUN IN THE
FOREGROUND by the second instance (08:19Z-08:24Z; the partial acceptance_stdout.txt replaced): slice001 426 OK (skipped=1),
binding 21 OK, witness 81 OK; 528 run, 0 failures. origin/main at the resume (2c292d3c4) changed nothing under rso/.

Score: sound 1/1 (FAILED_RERUN_DIGEST accepted, identical to baseline, both bases); broken 0/1 (NESTED_SIBLING ADMITTED, both
bases); controls 2/2 x 2; edit E6 SURVIVED targeted (218) and full (528 incl. rso/witness/tests), witness differs. Predictions
3/3.

Per surface (REPORT s3): BX1 CLOSED within coverage; BX2 CLOSED within coverage (B1's E2-E4 pinned by T031; T033 regression
held; no fresh BX1/BX2 shape tried -- stated). BX5/BX5b NOT CLOSED, two survivors:
  (a) NESTED_SIBLING, behavioural: a second COMPLETED RECEIPT row of a presented required node, digest of an unpresented FAIL
      receipt, parented to the presented execution's OWN row (depth 2) rather than the launch, is invisible to BX5b
      (own_launch_rows keeps parent == launch). Contract-vocabulary gap: CONTRACT s7 "under the anchored launch" vs BX2's
      parent == launch. NOT reachable through rso/witness/run_witness.py as committed: every node row is parented to the
      launch and the ledger refuses a repeated run_id; reachable only by an adapter that passes a node's run id as
      parent_run_id (ledger.begin accepts any string).
  (b) E6 digest-less sibling ignored, test-coverage: BX5b never reads a sibling's digest and no frozen test builds a
      COMPLETED sibling without one; the witness path always records the digest on a COMPLETED row.
Adjudication question, stated and not decided: if "applicable" means the committed witness path, CC3 is met (both recorded,
not repaired, per CONTRACT s3); if it means any BX6 adapter, (a) is an applicable survivor. The repair for (a), if wanted
later, is one line (walk parent_run_id up to the launch) or one contract sentence (a row whose parent is not a launch is
malformed provenance); neither is asked for here. REPORT s5 also records the witness path's honest hole (an unfavourable
launch dropped for a new one; BX5 by design) for the preregistration's author.
