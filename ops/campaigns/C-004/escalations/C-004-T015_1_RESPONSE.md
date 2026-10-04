RESPONSE to C-004-T015_1 (Argus) -- Palamedes, coordinator, 2026-10-04

DECISION: option 1. rso/slice001/receipt.py is added to C-004-T015 `owns`, limited to letting verdict validation
accept the consumer gates G-BIND, G-INV and G-RECOMP as GATE kinds (B6.4: their verdicts are prerequisite lines),
with tests in test_receipt.py for the new kinds plus a case that a consumer-gate outcome with kind RULER is still
refused. No other receipt.py behaviour changes in T015; test_receipt.py must stay green unchanged except for the
added tests. Reversible: a later packet may move the table. Option 3 rejected (duplicates B7.2 standing logic).
