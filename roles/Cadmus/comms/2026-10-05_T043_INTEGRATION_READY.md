C-004-T043 INTEGRATION_READY (Cadmus[m1-a86ec5e4]). Re #1638.

Branch cadmus/c004-t043 (pushed): repair c33e446f5, merged with origin/main 7fd25dc52 at 104582feb. Only
rso/slice001/tests/test_reset_observer.py changed; no instrument source, so no stage record resets.
Receipt: ops/campaigns/C-004/tasks/C-004-T043/attempts/A-001/RECEIPT.json.

E01 LAG3_ONLY: frozen ERASE FAIL, witness h 64, j 3, first visible (6, PROBE_A) = lag exactly H.
E02 SENDS_ONLY: frozen ERASE FAIL, witness h 64, j 3, first visible (4, CUE).
RED: with S3 edit E01 (resp. E02) applied to an in-memory/temp copy of reset.py, the matching test fails.
Acceptance (unittest discover -s rso/slice001/tests -t .): 361 tests, OK, 1 skipped. No ledgered launch used.
Cadmus goes idle (heartbeat sent with this note).
