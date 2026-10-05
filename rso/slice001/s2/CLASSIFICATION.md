# C-004 S2 matrix -- classification of every disagreement (C-004-T020)

Real run: consume at first check 2026-10-04T18:35:28Z against the live custody store (chain verified, 33 rows),
bundles produced at 6379cd3a6 and committed at b220c7e39 before any consume. Comparison target: the independent
table (Pallas, T005). Result: 48 registered cases, 45 gating; AGREE 32, PARTIAL 8 (fields the table leaves
UNDETERMINED / "as measured" / "see G<n>"), DISAGREE 8. Full rows: MATRIX.json; summary: MATRIX.txt.

Classification is the coordinator's reading of the frozen contract text with the evidence cited; it is
ESCALATED to the operator (C-004-T020_1), not self-accepted (CONTRACT.md R4: nothing resolved silently).
No item is classified IMPLEMENTATION.

    case(s)                       field                          implementation vs table              class     why
    ----------------------------  -----------------------------  -----------------------------------  --------  ------------------------------------------
    T04.LAGD, T06.LAGD (X18)      ERASE FAIL reason              boundary 3 (4, PROBE_A) vs boundary 1 TABLE     draft A A5 witness order: histories
                                                                                                                 lexicographic in (u_1,f_1,...,u_6,f_6)
                                                                                                                 first; the history differing only at
                                                                                                                 f_3 precedes the one differing at f_1.
                                                                                                                 Table assumed pair (all-zero, f_1=1).
    T05.WIPE (X18)                PRESERVE FAIL reason           reset at 3 vs reset at 1             TABLE     same order rule
    T08.EVERY3/SLEEPER/SPLIT1     CL-RET standing                UNQUALIFIED vs UNMET                 TABLE     undeclared state fails RESTART; CHANNEL
      (X19)                                                                                                      and OBSERVER UNQUALIFIED PRECONDITION:
                                                                                                                 RESTART (B4.2 A5); worst standing is
                                                                                                                 UNQUALIFIED (B7.2). Table applied this
                                                                                                                 logic to T06 (D7), not to T08.
    E02.MISSING (X06)             PRESERVE authority (absent)    UNQUALIFIED: EVIDENCE_MISSING vs n/a CONTRACT  authority of an absent receipt is not
                                                                                                                 specified; standing BLOCKED either way.
    E02.MISSING (X06)             G-INV reason                   RUN_UNREPORTED:<run_id> vs same form TABLE     table reason carries prose commentary
                                                                 + commentary                                    "(if the inventory still lists ...)".
    E02.MISSING (X06)             CL-CUST(G0) standing           BLOCKED vs UNQUALIFIED               TABLE     G-BIND BLOCKED (EVIDENCE_MISSING) is a
                                                                                                                 CL-CUST prerequisite; B7.2 orders BLOCKED
                                                                                                                 worst.
    E02.RELABEL (X02)             claim CL-RET(REG2)             no such claim vs NOT_ELIGIBLE/UNMET  TABLE     only registered claims are evaluated
                                                                                                                 (B7.1, policy); the relabelled claim is
                                                                                                                 CL-RET(REG): G-BIND FAIL SCOPE_MISMATCH:
                                                                                                                 physics, one of the table's alternatives
                                                                                                                 (G08 resolved by the fixture keeping ids).

Real-store results reported beside the matrix (not table cells): CL-CUST(G0) ELIGIBLE, custody QUALIFIED on
registered rows (1, 20-24, ...); EXTRA/HEAL/FLAT/LOSSY custody UNQUALIFIED ROW_BLOB_MISMATCH (not registered, by
design: only G0 carries a custody claim). Every CL-RET/CL-CAL authority on the real store is QUALIFIED at
AUTHOR_TESTED except where A5 preconditions apply.

Register status after T020: X02, X06, X18, X19 classified above; X01 (CLOCKED: direct path, ruler not evidence),
X05 (AMNESIAC reads a: CHANNEL PASS, agrees), X07/X08 (E04 withdrawals: agree), X09/X15 (T06: PARTIAL, values as
measured), X10-X14 and X16-X17 general (no cell-level disagreement observed). Comparator rules used (from the
table's conventions, fixed before the real run): reasons compared for FAIL only (X17); placeholders are patterns,
including inside values and with arrows; 'as measured' / 'see G<n>' / UNDETERMINED are not predictions.
