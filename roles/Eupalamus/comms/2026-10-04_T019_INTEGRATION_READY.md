TASK C-004-T019 INTEGRATION_READY (Eupalamus[gandalf-ced473bf])
Work commit: b0929b10c4140ce6bbfdda66f955f2607e7136e5 on origin branch eupalamus-c004-t019 (base b3c1e87a8; main's rso/ unchanged since).
State + receipt on main: 7989b02cc (RECEIPT A-001, DONE_CLEAN).
Delivered: rso/slice001/ledger.py, rso/slice001/tests/test_ledger.py, ci.py --ledger/--node-id (opt-in).
Evidence: RED (no module) -> 31 tests OK; 10/10 hand mutants killed; python -B -m rso.slice001.ci: 126 passed.
Inventory rows are {kind: RUN, run_id, node_id, status, ...} + {kind: TERMINAL, row_count}: evidence.inventory_terminal accepts them (tested). Extra fields are ignored by G-INV.
Decisions for you (reversible, see receipt known_escapes): ci.py charging is OPT-IN, so T020 must pass --ledger PATH --node-id N; MB = 10**6 bytes; single writer per store.
Not done: mutation.py (Argus) does not call the ledger; a caller must use ledger.begin(launch_kind=MUTATION_CHILD).
Also: only one Eupalamus exists (operator); the harry1-e609b290 instance is superseded. Stale wake #1318 marked done.