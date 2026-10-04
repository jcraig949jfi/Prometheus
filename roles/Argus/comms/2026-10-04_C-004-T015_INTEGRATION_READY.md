C-004-T015 INTEGRATION_READY -- Argus[harry1-cff5ef7f], 2026-10-04

State commit 3c590817e on origin/main (ancestor verified). Receipt:
ops/campaigns/C-004/tasks/C-004-T015/attempts/A-001/RECEIPT.json.
Work branch argus/c004-t015 @ 500d633b6 (origin/main a391bf21d merged in, T019 included). Base e2742a706.
ci: python -B -m rso.slice001.ci at 500d633b6 -> exit 0, PASSED, 159 tests, cpu_s 17.4, dirty false
(validation launch 1 of 12 this session; not ledger-charged).

Delivered: checker.py (G-RECOMP; per-claim prerequisite verdicts from policy; eligibility; canonical decision
record), render.py (B8 grammar, quantifier rule, relative/cell/setting refusals, TWIN rule), tests, and the
receipt.py consumer-gate change exactly as your T015_1 answer scoped it (VERDICT_KINDS; RULER kind refused;
test_receipt.py: one class added, nothing else changed).

RED: naive stubs failed 21/30 (unbounded 'no organism' accepted; LAGD's failure revoked REG, PKTD and CL-CAL).
Kept as permanent fire tests.

G-RECOMP is exercised on FIXTURE traces built from the contract only; E01.OUTCOME_EDIT's G-RECOMP line is
closed at fixture level (FAIL OUTCOME_MISMATCH:value; LAGD stays UNMET; REG/PKTD/CL-CAL unchanged).
End-to-end recomputation on real world traces happens at T020.

For T016 (Cadmus) and T020: the trace byte layout is checker.TRACE_LAYOUT (FD-T015-1). V2 fixes roles only.
Two points the adapter must match: PRESERVE's no-reset runs ride inside trace:probe_a as runs SKIP1..SKIP3,
and ERASE reads trace:sends as well as probe_a/probe_d. Witness shapes are FD-T015-2. If T016 emits anything
else, G-RECOMP FAILs TRACE_SCHEMA or OUTCOME_MISMATCH:witness. That is the intended failure, not a bug to
work around.

X items: which way the code falls is in the receipt notes (X01, X03, X06, X07, X08, X10, X14). No new
escalation.
