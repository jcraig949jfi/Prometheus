C-004-T014 INTEGRATION_READY (Argus[harry1-91cbacb8], claude-opus-5-5, Q2).
Branch argus/c004-t014, work commit c62878b1d (base 398db5c43). State commit cac84f1ec; receipt
ops/campaigns/C-004/tasks/C-004-T014/attempts/A-001/RECEIPT.json (DONE_CLEAN).
Deliverables: rso/slice001/evidence.py, rso/slice001/fixtures/evidence_cases.py,
rso/slice001/tests/test_evidence.py (37 tests). fixtures/ has no __init__.py (namespace package).
RED: a hash-only stub admits every E02/E03 broken fixture (8/10 tests fail with it); kept as TestFireStub.
GREEN: ci exit 0 at c62878b1d, 81 tests, dirty false (validation launch 3 this session).
All 20 registered E01-E05 ids have fixtures. G-RECOMP is T015's: E01.OUTCOME_EDIT's G-RECOMP line is
untested until then (the evidence-plane parts are tested).
X items: see receipt notes. X02 both readings fixtured, not chosen; X06 G-BIND BLOCKED + G-INV FAIL
RUN_UNREPORTED; X07 LAGD UNQUALIFIED; X08/X13 TWIN line WITHDRAWN; X12 BLOCKED precondition ->
UNQUALIFIED by the letter of A5.

TASK_ID:           C-004-T015
BLOCKER:           T015's consumer must turn G-BIND / G-INV / G-RECOMP results into three-field verdict
                   lines, but receipt.make_verdict (T013, integrated) accepts only P0..P8 outcomes, and
                   receipt.py is not in T015's owns list.
EVIDENCE:          rso/slice001/receipt.py _verdict_outcome: PREDICATE_KINDS.get(pid) != outcome["kind"]
                   raises VERDICT_SCHEMA:outcome for predicate "G-BIND"; T015 TASK.json owns checker.py,
                   render.py, tests/test_checker_render.py only.
OPTIONS:           1. Add rso/slice001/receipt.py to T015's owns (Argus owns both; one-table change:
                      consumer gates as GATE kinds in verdict validation). Cheap, reversible.
                   2. A small separate packet for the receipt.py change before T015. One more state cycle.
                   3. T015 builds consumer-gate lines outside make_verdict. Duplicates B7.2 logic; not advised.
RECOMMENDATION:    1.
CAPABILITY_NEEDED: the coordinator (Palamedes).
