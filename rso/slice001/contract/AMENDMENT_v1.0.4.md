# S1 contract amendment v1.0.4 (launch cap for the S4 repair round, operator decision OP-7)

Amends contract v1.0.3. Written by Palamedes[harry1-679179c6], 2026-10-05. STATUS: ADOPTED; contract.json caps are
updated by C-004-T044 (Eupalamus) in the same commit as test_ledger.py, whose test_caps_read_from_the_real_contract
pins the live launch cap (the T021/T025 pattern: main never carries a red suite).

Authority: C-004-OP7 (operator, 2026-10-05): "Raise the C-004 launch cap from 12 to 20 ... Record the cap increase as
an explicit post-S3 repair-round amendment and preserve the original 12-launch S2/S3 accounting separately."

X1  caps.top_level_validation_launches: 12 -> 20. Every other cap unchanged (120 CPU-minutes per v1.0.3; $0; 100 MB;
    one repair round; seat-hours and working days per OP-1).
X2  caps.launch_accounting (new, text): "S2/S3 window under the original cap of 12: 8 launches used (S2 produce 5:
    G0, EXTRA, HEAL, FLAT, LOSSY; S3 3: unchanged suite, cases, mutation driver), closed at the S3 integration
    (bddb3c71d), 4 unused. Post-S3 repair-round window (OP-7): launches 9-20, i.e. 12 more, for the S4 regression
    rerun of all five S2 bundles on the repaired code and the S4 closure set; the ledger counts both windows
    cumulatively against 20."
X3  Scope of the eight extra launches (operator): re-verifying the repaired CHANNEL behaviour across the full regression
    surface, including HEAL and the twin bundles. The rerun is not shrunk.

The ledger (rso/slice001/s2/LEDGER.jsonl) is append-only; the S2/S3 rows stay as they are. The S4 report quotes the
two windows separately.
