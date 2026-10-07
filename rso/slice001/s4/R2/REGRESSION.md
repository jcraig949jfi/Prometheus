# C-004 R2 regression (C-004-T047): S4 bundles consumed by the second-repair code

Palamedes, 2026-10-06. Code: T046 (Argus; second and final repair, OP6) integrated on main at ad6b3fa96; contract
v1.0.5. Consume-only: the producer is unchanged, so the five committed S4 bundles (rso/slice001/s4/, produced at
0e1943bff) are reused and NO launch is charged (launches stay 15 of 20).

Custody: Aporia registered the three regenerated stage records (rows 42 G-BIND, 43 G-INV, 44 G-RECOMP at
ad6b3fa96; chain_ok, 44 rows, head c84180a3a8299c86dd643026e9c9738976cb3eef4b719c3410e86f21860e3d89, comms #1706)
before the first check. The three fire-receipt lines of request (5) were REFUSED by the registrar: I had stated
working-tree (CRLF) hashes, not committed-byte hashes. Corrected request (6), #1708: registered as rows 45-47 (#1709; chain_ok, 47 rows, head
18b346c5a62d1759f04434b254c912a0165bae3259306878ef0f958d6a8328e3). The consumer does not read
fire-receipt rows (A2 checks the fire receipt's bytes against the hash cited in the registered stage record), so
the refusal does not affect this regression.

Method: one first-check time (2026-10-06T23:04:07Z), one live store; decisions_real over the five S4 bundles under
(a) the frozen S4 code (8b98c2702, FREEZE_S4) and (b) the R2 code; plus the matrix under (b).

## 1. Against the independent table

    48 registered, 45 gating: AGREE 32, PARTIAL 8, DISAGREE 8. The report section of MATRIX.json is identical
    to s4/MATRIX.json (and so to S2): OP-5 dispositions only, no new disagreement. Rows: MATRIX.json, MATRIX.txt.

## 2. Against the S4 code, every claim of every bundle (30 claims, 5 bundles)

    Outcome, eligibility, standing, execution, authority: 0 differences.
    Custody status per bundle: unchanged (G0 QUALIFIED; EXTRA, FLAT, HEAL, LOSSY UNQUALIFIED).
    The only differences (7 G0 items: the bundle custody and 6 claims) are custody CITATIONS: rows 34, 35, 36
    (the S4 stage records) become 42, 43, 44 (the R2 records), and registered_at_utc moves with them. Expected:
    the R2 code carries new instrument versions, so it cites their registrations.

## 3. What this does not test

    The registered bundles do not exercise C1 (two keeper manifests, one node set, a reproduced bundle), C2 (an
    observer-borrowed run) or B3.3 (an earlier window's run). Those are T046's RED/GREEN tests (author-run) and
    T048's fresh re-check (independent). Known escape carried to T048 (T046 FD-T046-1): B3.3 is checked as
    run.end_utc >= receipt.created_at_utc, so two OVERLAPPING launches of one node are not separated.

## 4. Caps

    Launches 15 of 20 (unchanged). Ledgered CPU unchanged (48.7 of 80 ledgered minutes; development runs here
    are not ledgered launches). Artifacts: +2 small files.
