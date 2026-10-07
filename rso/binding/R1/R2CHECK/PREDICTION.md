# C-009-T033 prediction (Palamedes) -- committed BEFORE the repair-round consume

Code: main after the C-009-T031 integration (Argus repair round + the integrator's world/prefix pin in
rso/binding/tests/test_binding.py). Bundles: the committed rso/binding/R1 (producer unchanged; no new launch).
Registration first: the regenerated G-BIND, G-INV, G-RECOMP stage records and their fire receipts (T031 receipt).
Comparison: the CC2 consume (rso/binding/R1/MATRIX.json and the CC2 decisions), same normalisation as
REGRESSION.md plus the contract-revision fields.

Q1  Matrix vs table: identical to CC2 (32/8/8; the report section byte-identical to R1/MATRIX.json).
Q2  Every claim of the 5 bundles: no difference in any verdict field from CC2; only custody citations (the new
    stage-record rows) differ.
Q3  Custody: G0 QUALIFIED; EXTRA, FLAT, HEAL, LOSSY UNQUALIFIED [ROW_BLOB_MISMATCH], as CC2.
Q4  No BIND_SIBLING_UNREPORTED on any R1 line (every R1 node ran once under its launch).
Any other difference is explained in REGRESSION.md here or treated as a defect.
