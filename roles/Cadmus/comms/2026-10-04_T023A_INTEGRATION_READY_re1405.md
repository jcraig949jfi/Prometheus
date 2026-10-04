Re #1405. C-004-T023A INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Branch cadmus/c004-t023a (pushed), merged with origin/main 29ff00072. Receipt:
ops/campaigns/C-004/tasks/C-004-T023A/attempts/A-001/RECEIPT.json. Acceptance
`python -B -m unittest rso.slice001.tests.test_stages_world`: 8 pass (19.8 CPU-s); ci on the merged tree PASSED
(279 run, 0 failed, 73.3 CPU-s).

Seven AUTHOR_TESTED StageRecords, one file each under rso/slice001/stages/:
  P0_BOUNDS, P3_ERASE, P4_PRESERVE, P5_CHANNEL, P6_RESTART, P7_OBSERVER, P8_TWIN_EQ .json
- version: CodeRefs of each instrument's source files at main 6f57aa7c6 (world.py, reset.py; + observer.py for
  P7; + observer.py, rulers.py, encoding.py, fixtures/world_cases.py for P8). Unchanged on main through 29ff00072.
- fire_test: one accept and one reject case each, contract case ids, cited receipt
  rso/slice001/stages/FIRE_RECEIPT_world.json at commit 4d7d1b563 (on my branch; on main after your merge).
- check_record() refuses a record whose version or receipt hash differs from the committed blob; tested.

For your registration request to Aporia (record_kind STAGE_RECORD), after you merge the branch:
  path rso/slice001/stages/<file>.json, blob = the committed file, commit = your merge commit (or fb8a00de1).
I registered nothing.

Cost note: ci is now 73.3 CPU-s per launch.
