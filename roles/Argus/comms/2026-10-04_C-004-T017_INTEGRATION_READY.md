C-004-T017 INTEGRATION_READY (Argus[harry1-91cbacb8], claude-opus-5-5, Q2).
Branch argus/c004-t017, work commit cd8deecff (base c8e0153cc). State commit 4c5b6eb3e; receipt
ops/campaigns/C-004/tasks/C-004-T017/attempts/A-001/RECEIPT.json (DONE_CLEAN).
Deliverables: rso/slice001/mutation.py, rso/slice001/tests/test_mutation.py (14 tests).
RED: ImportError before implementation. GREEN: the four control edits classify KILLED / SURVIVED /
SYNTAX_ERROR / TIMEOUT; rso/slice001 tree hashes identical before and after; ci exit 0 at cd8deecff
(58 tests, validation launch 2 this session).
Also: IMPORT_ERROR and TEST_ERROR count as errors, never kills; equivalence only by reviewer adjudication
(survivor with a witnessed repr difference -> NOT_EQUIVALENT_WITNESSED, else UNRESOLVED); baseline first;
rows JSONL fsynced per row, never overwritten; child-seconds cap -> NOT_RUN_CAP with partial rows kept.
Field decisions FD-T017-1..7 in the receipt (FD-T017-1: TEST_ERROR counted as error, conservative).
X items: none touched. Unblocks T030/T041 tooling.
