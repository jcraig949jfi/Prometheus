C-004-T013 INTEGRATION_READY (Argus[harry1-91cbacb8], claude-opus-5-5, Q2).
Branch argus/c004-t013, work commit 6b6827fc9 (base b02c6f66d). State commit c2471ed0f; receipt
ops/campaigns/C-004/tasks/C-004-T013/attempts/A-001/RECEIPT.json (DONE_CLEAN).
Deliverables: rso/slice001/receipt.py, rso/slice001/tests/test_receipt.py (35 tests).
RED: ImportError, then 28/35 failing against a naive stub (missing-field, lowest-stage, cheat control).
GREEN: python -B -m rso.slice001.ci exit 0 at 6b6827fc9, 44 tests, dirty false (validation launch 1).
Cheat control: producer authority key refused (FD-B1); QUALIFIED above the stage record for the exact
instrument version refused STAGE_EXCEEDS_RECORD; no record -> NO_STAGE_RECORD.
X items: none touched directly; X10/X12 remain in T014/T015 (make_verdict takes authority as given).
Field decisions FD-T013-1..5 in the receipt notes. Unblocks T014, T016. Next: C-004-T017.
