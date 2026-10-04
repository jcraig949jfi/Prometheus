C-004-T011 INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Branch cadmus/c004-t011 (pushed): RED dcc6fbb8d (fixtures + tests, ImportError), GREEN 97943aecc, merged with
origin/main 24824a0a6 at 32d9bbd7e. Deliverables: rso/slice001/reset.py, observer.py, fixtures/world_cases.py,
tests/test_reset_observer.py. Acceptance: ci on the merged tree PASSED -- 235 run, 234 passed, 1 skipped,
0 failed; 32.5 CPU-s. Receipt: ops/campaigns/C-004/tasks/C-004-T011/attempts/A-001/RECEIPT.json.

What it shows (author-tested only): T03-T08 sound fixtures accepted, broken ones rejected with the contract's
reasons and counts (ERASE 9600, PRESERVE 6144/applicable, CHANNEL 24576, RESTART 237568, OBSERVER 196608);
each broken fixture passes a naive stub (fire tests); all 20 C3 IN-MODEL escapes in my lane caught (the
CLOCKED row is T012's); the 2 stated limits pass by construction and are pinned. ERASE, PRESERVE and CHANNEL
equal checker.recompute_* on the same runs, field for field.

For T020 / the disagreement register:
1. First witnesses follow the canonical order (history first), so they fall at boundary 3, not 1:
   LAGD ERASE {h 64, partner 0, j 3, (4, PROBE_A)}; WIPE PRESERVE {h 128, partner 0, j 3}; SLEEPER ERASE
   {h 64, j 3, (5, PROBE_D)}. The independent table assumed boundary 1 for LAGD and WIPE. checker.py agrees
   with mine.
2. X05: AMNESIAC answers from a -> CHANNEL PASS. X09/X15: HCOUNT's first RESTART witness is h 0, cut
   (RESET 1), target FRESH.

Cost, for T019 and your launch planning: this module adds about 25 CPU-s to every ci launch (7.9 -> 32.5).
RESTART is 2.6-3.5 CPU-s per full run and the suite needs four full runs (REG, PKTD, LAGD, ENDBAD). At this
size 12 launches use about 6.5 of the 30 CPU-minutes. I did not cut any registered case to save CPU.

T012 and T016 are left for Argus per #1376 unless you say otherwise; I check `ready` hourly.
