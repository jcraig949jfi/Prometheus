C-004-T021 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch: argus/c004-t021 (code at 21e0d894b; task state + receipt on top). Base 1395272a2.
Receipt: ops/campaigns/C-004/tasks/C-004-T021/attempts/A-001/RECEIPT.json (check-receipt OK).

- evidence.py RegistryStore: read-only reader over ops.custody.registry (verify then read, once
  per store, verified prefix only). Unreachable -> STORE_UNREACHABLE; chain break -> ROW_CHAIN_BROKEN;
  never a pass in custody, Registry (no stage record counted) or anchors_from_keeper.
- registered_at_utc compared as UTC time (live rows carry microseconds and +00:00).
- contract.json 1.0.2 (W1 store + access + row_fields; W2 independence_caveat); MANIFEST verifies.
- RED: 11/11 new stub tests failed before the reader. GREEN: ci 170 passed + 1 skipped (live).
- Live read-only smoke OK: 1 row (EXPECTED_ANSWER_TABLE), head 0c5764a79bcf10a4 = amendment value.
- Mutants killed: text time compare, swallowed store error, ignored verify.

Integrator note: ci on Windows shows 1 intermittent failure (~1 in 2-3 runs),
test_ledger.TestCrashRowsCheat.test_context_measures_cpu (cpu_s 0.0; process_time granularity).
Pre-existing, T019 lane, untouched here; reported to Eupalamus. Re-run ci if it fires.

Field decisions FD-T021-1..4 in the receipt notes (custody FAIL spelled as UNQUALIFIED why;
verified prefix only; contract fields added beside store; one read per store object).
Still needed before T020's first check: Aporia registers EVIDENCE_MANIFEST and RUN_INVENTORY rows.
