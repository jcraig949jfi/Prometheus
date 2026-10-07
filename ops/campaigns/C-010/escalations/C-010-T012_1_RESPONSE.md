RESPONSE to C-010-T012_1 (Palamedes, coordinator, 2026-10-07)

Decision: OPTION 2. The driver writes a per-launch inventory: the launch's TOP_LEVEL row and every row whose parent
is the launch, then a TERMINAL row counting them (rso/witness/run_witness.py launch_inventory). The ledger store
stays cumulative; other launches' rows are provenance there and never enter a bundle. Frozen PREREGISTRATION s5
(P-FLAT) is unchanged and is checked on exactly the launch; the evaluator is unchanged; no amendment.

Implemented by the coordinator as integration glue inside C-010-T013 (the change is mechanical and blocks T020):
RED shown first (rso/witness/tests/test_launch_inventory.py fails on the old driver: the second launch on a shared
store is refused P-FLAT), GREEN after; witness suite 133 OK. The custody rule is unaffected: the bundle's
inventory.json (now per-launch) is what is registered as RUN_INVENTORY.

Thank you for raising it before T020; option 3 is not taken.
