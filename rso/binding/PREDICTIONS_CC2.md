# C-009 CC2 predictions (Palamedes, C-009-T020) -- committed BEFORE the fresh produce

Code: main after C-009-T010 and C-009-T011 integration (da11f6ead). Produce: the five slice bundles (G0, EXTRA,
HEAL, FLAT, LOSSY) into rso/binding/R1/, charged to rso/binding/LEDGER.jsonl under rso/binding/contract.json.
Registration (Aporia, registrar): R1 G0 EVIDENCE_MANIFEST + RUN_INVENTORY (as for S2/S4, only G0 is registered)
and the three regenerated stage records G-BIND, G-INV, G-RECOMP with their fire receipts. Then one first check:
matrix vs the independent table, and every claim of every bundle vs the S4 code on the S4 bundles (s4/MATRIX.json,
and decisions under FREEZE_S4 code as in T047).

Normalisation for the claim diff (identity, not verdict): run ids, launch ids, custody row ids and registered_at
times, receipt created_at, code/commit refs. Everything else is compared.

P1  Matrix vs table: 48 registered, 45 gating; AGREE 32, PARTIAL 8, DISAGREE 8; the same case ids in each class and
    the same OP-5 dispositions as S4. Expected text change: E02.MISSING's G-INV "got" reason now cites a run of the
    R1 G0 launch itself (BX5 own-launch rows), not the S2 run (resolves O-S4-1). It still matches the table's
    placeholder.
P2  Claim by claim, all 30 claims of the 5 bundles: eligibility, standing, execution, authority status, outcome
    value and (normalised) reason identical to S4.
P3  Custody: G0 QUALIFIED; EXTRA, HEAL, FLAT, LOSSY UNQUALIFIED with the same why as S4 and nothing added (each
    inventory binds its own launch: no INVENTORY_UNBOUND, no LAUNCH_UNBOUND).
P4  No G-INV LAUNCH_UNBOUND or RECEIPT_WITHOUT_RUN on any R1 bundle line where S4 had G-INV PASS.
P5  Ledger after produce: 5 of 12 launches; CPU well under 10 of 90 minutes.

Any difference outside P1-P5 is either explained in R1/REGRESSION.md with its cause or treated as a defect.

Also recorded before any CC2/CC3 outcome (CONTRACT.md v1.0.1 clarification): BX7 is enforced at bundle custody
(CL-CUST), which the slice keeps as a separate claim row (S2 table unchanged). For reporting, a claim that relies
on G-INV is QUALIFIED only together with its bundle's custody QUALIFIED; the native witness preregistration
inherits this as a hard rule.
