C-004-T018 INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Branch cadmus/c004-t018 (pushed): RED 8425cbbbd (ImportError), GREEN, merged with origin/main 5c290b461.
Deliverables: rso/slice001/encoding.py, tests/test_encoding.py. Acceptance: ci on the merged tree PASSED --
271 run, 270 passed, 1 skipped, 0 failed; 53.2 CPU-s. Receipt:
ops/campaigns/C-004/tasks/C-004-T018/attempts/A-001/RECEIPT.json.

E06 (reported, not an exit criterion): REG_ONEHOT (a, d held only as one-hot pairs) and REG_FLAT (one state
tuple, 224-entry table explored from REG) give REG's outcome values on P0-P7: TWIN_EQ PASS for both. LOSSY
(both values of a -> one code): TWIN_EQ FAIL, "twin LOSSY differs from REG on RETENTION: POSITIVE vs
NEGATIVE". Every report row (encoding.e06_report) says physics ONE, exit_criterion false, no promotion.

Cost, again for launch planning: ci is now 53.2 CPU-s per launch (T011 adds about 25, T018 about 15). At this
size 12 launches would use about 10.6 of the 30 CPU-minutes. The T018 packet's "cpu < 1 CPU-minute" is
exceeded once its acceptance ci launch is counted (about 70 CPU-s in all); I stopped there and ran no mutants.

All Cadmus packets in C-004 S2 (T010, T011, T018) are now delivered. I keep the hourly sync for T020 support,
repairs, or S4 repair packets.
