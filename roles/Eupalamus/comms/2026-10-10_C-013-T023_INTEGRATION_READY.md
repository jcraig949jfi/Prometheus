C-013-T023 INTEGRATION_READY (Eupalamus[harry1-f28941a3], claude-sonnet-5-5, Q1)

Branch eupalamus/c013-t023 (pushed). Code commit: see receipt end_sha. Files: rso/slice001/ledger.py, rso/slice001/tests/test_ledger.py only.
- Caps gpu_hours / cloud_usd optional (ledger.py Caps); finish() records them; usage() sums; begin() refuses with typed CapExhausted.cap before the START row (REFUSED row, like existing caps); est_gpu_hours / est_cloud_usd on begin() refuse a run that would pass the cap.
- RED observed (stash ledger.py, new class: 1 failure + 6 errors), then green. slice suite OK, rso/witness 149 OK, rso/binding 21 OK; workgraph validate OK.
- Field decision / catch: real contract.json has gpu_hours 0 and cloud_usd 0. A first draft (used >= limit) refused every CPU-only run (29 s2_bundle errors). Fixed: refuse only on non-zero spend at/over limit, or a declared estimate past the limit. Pinned by test_zero_cap_is_no_paid_compute_not_no_runs.
- Inventory units: gpu_micro_hours / cloud_micro_usd integers, only on rows that recorded them (canonical bytes refuse floats).
- Limit: the ledger only counts what callers declare; unmetered callers are unaffected.
Receipt: ops/campaigns/C-013/tasks/C-013-T023/attempts/A-001/RECEIPT.json. Please integrate.
