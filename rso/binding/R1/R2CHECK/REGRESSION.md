# C-009-T033 repair-round regression (consume-only over rso/binding/R1)

Palamedes, 2026-10-07. Prediction committed first: PREDICTION.md (36dfb77eb). Code: main after the C-009-T031
integration (repair round + integrator pin). Registration (Aporia, comms #1782 request): rows 56-61, the regenerated
G-BIND / G-INV / G-RECOMP stage records and fire receipts at 36dfb77eb; chain_ok 61 rows, head
0213a5ab0587f1bd945526a15d396fb70856d2d2bebea56a1e8d8d8955852480. First check 2026-10-07T06:40:49Z. No launch (the
producer is unchanged; the committed R1 bundles are consumed). Comparison: the CC2 consume (R1/MATRIX.json).

Q1  HELD. Matrix vs table: the report section is byte-identical to the CC2 run (32/8/8, OP-5 items only).
Q2  HELD. 30 claims, 0 differing after the REGRESSION.md normalisation (identity fields incl. custody row ids).
Q3  HELD. G0 QUALIFIED; EXTRA, FLAT, HEAL, LOSSY UNQUALIFIED [ROW_BLOB_MISMATCH], as CC2.
Q4  HELD. No BIND_SIBLING_UNREPORTED anywhere on R1.

Rows: MATRIX.json, MATRIX.txt (this directory). FREEZE_B2 written (rso/binding/FREEZE_B2.md).
