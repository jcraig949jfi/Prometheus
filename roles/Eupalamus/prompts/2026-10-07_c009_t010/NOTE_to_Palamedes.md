C-009-T010 CLAIMED (cbd9603d2) and INTEGRATION_READY (state ee5117490 on main; receipt attempts/A-001).
Work: branch eupalamus/c009-t010 @ 2d2c41304 (ledger.py, s2_bundle.py, s2_run.py + 3 test files).
Both suites green at 2d2c41304: slice 404 OK (1 skipped), binding 13 OK.
Bound: RECEIPT rows carry parent_run_id + receipt_sha256; manifest launch_run_id; s2_run produce --contract.
Caveats for you: (1) s2_bundle.py is pinned by stage records -> CC4 regeneration applies, not done here.
(2) Bundle-level RED was not run on old code (build_bundle refuses uncommitted code); ledger/s2_run RED was.
(3) Fields are omitted, not null, when unrecorded, so old ledgers/inventories are byte-identical.
No ledgered launch made; evidence.py untouched.
