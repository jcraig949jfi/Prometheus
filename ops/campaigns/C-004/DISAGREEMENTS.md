# C-004 disagreement register (input to C-004-T020)

Opened by Palamedes, 2026-10-03, from Pallas's COMPARISON.md and EXPECTED_ANSWERS.json gaps (T005, 5c9f0bc66)
and the coordinator's answer to escalation C-004-T005_1 (option 2 applied as AMENDMENT_v1.0.1; option 3 items
registered here). Nothing here is resolved. T020 runs the S2 implementation, then classifies each item as
IMPLEMENTATION, CONTRACT or TABLE defect with evidence (CONTRACT.md R4). An item that needs a case
expectation changed after S2 outcomes exist goes to the operator (CONTRACT.md s7).

The independent table (EXPECTED_ANSWERS.json) is the comparison target for T020; the author-expected columns
(draft A A6, draft B B9, B8.2) are a second opinion.

    id     case / area                 question                                                  source
    -----  --------------------------  --------------------------------------------------------  -------------------
    X01    T02.CLOCKED RETENTION       value of the ruler outside the product domain; CLOCKED    COMPARISON 2.1, G04
                                       domain and subject not stated (authority is UNQUALIFIED
                                       either way, so it is not evidence)
    X02    E02.RELABEL                 IDENTITY_UNKNOWN / EVIDENCE_MISSING vs SCOPE_MISMATCH     COMPARISON 2.2, G08
                                       :physics; whether node_ids are renamed with the subject
    X03    E03.REANCHOR                two cases under one id; G-RECOMP and CL-RET(REG) values   COMPARISON 2.3, D6
                                       unstated; which byte is flipped; whether recomputation
                                       from a flipped trace is FAIL OUTCOME_MISMATCH
    X04    E06.LOSSY                   witness (reason form now V4)                              COMPARISON 2.4
    X05    T02.AMNESIAC CHANNEL        answer read from `a` (CHANNEL PASS) or literal 0          COMPARISON 2.5
                                       (CHANNEL FAIL); one or two UNMET lines
    X06    E02.MISSING G-INV           RUN_UNREPORTED on CL-RET(REG) (V7 attributes it); BLOCKED D2, G07
                                       placed on PRESERVE verdict, on G-BIND, or both
    X07    E04.W_RESTART CL-RET(LAGD)  LAGD shares the withdrawn stage record: UNMET -> UNQUALIFIED D3
    X08    E04.W_UNRELATED TWIN        TWIN(M, M') is a registered claim: its line becomes       D4
                                       UNQUALIFIED WITHDRAWN
    X09    T06.PKTD_NOQ, T06.HCOUNT    CL-RET standing UNQUALIFIED (PRECONDITION:RESTART) vs      D7
                                       UNMET
    X10    G-BIND-failed prerequisite  keeps its standing (UNMET via G-BIND) or counts absent      G06
                                       (BLOCKED)
    X11    G10 anchors                 consumer keeps the original anchors, or accepts producer  G10
                                       re-made anchors (detection left to G-RECOMP / custody)
    X12    BLOCKED + preconditions     authority of CHANNEL/OBSERVER lines when RESTART is        G12
                                       BLOCKED
    X13    TWIN_EQ edges               no evidence edges to the compared receipts; withdrawal     G13
                                       does not reach TWIN by the letter of B6.5
    X14    custody standing            custody is not a three-field verdict; standing when        G14
                                       UNQUALIFIED
    X15    T06.HCOUNT detail           first RESTART witness; CHANNEL outcome masked by          COMPARISON 5
                                       authority (derived after unblinding; not in the table)
    X16    reset_model Q               draft A A2 calls Q = 8 = S x (K + 1) 'the reachable      T010 receipt
                                       maximum'; T010 shows at most 6 in flight from send()
                                       (S = 2, K = 3). Q stays a valid bound (BOUNDS
                                       CHANNEL_CAPACITY reachable only via restore()); no
                                       verdict changes. Contract wording defect for S5.
    X17    PASS reason text            the contract registers FAIL reason forms only (draft A    T011 integration
                                       A5, V4); PASS reasons are free text on both sides, so 6  check
                                       T03-T08 PASS reasons differ in wording only. Proposed
                                       class CONTRACT (no PASS form); T020 engine compares PASS
                                       reasons as NOT_COMPARED.
    X18    first-witness boundary      T04.LAGD ERASE and T05.WIPE PRESERVE: implementation     T011 integration
                                       witness at boundary 3, table at boundary 1. A5 orders    check
                                       witnesses by history first (lexicographic in (u_1, f_1,
                                       ..., u_6, f_6)), then boundary; the history differing
                                       only at f_3 sorts first. Proposed class TABLE (Pallas's
                                       assumption 'pair (all-zero, f_1 = 1)'); values agree.
    X19    T08 CL-RET standing         EVERY3, SLEEPER, SPLIT1: implementation UNQUALIFIED, table  T020 dry run
                                       UNMET. Their undeclared state fails RESTART, so CHANNEL
                                       and OBSERVER are UNQUALIFIED PRECONDITION:RESTART (B4.2
                                       A5) and the worst standing is UNQUALIFIED (B7.2); SPLIT2
                                       (captured channel state) is UNMET in both. Same logic as
                                       Pallas's D7 for T06. Proposed class TABLE.

Independence caveats carried with this register (Pallas EXPOSURE.md s4): agreement on T01.QCARRY,
T02.AMNESIAC, T02.CLOCKED, T02.FLIP, T05.WIPE, T06.LAGD is not independent; contract.json prints every case's
polarity, so polarity agreement is weak everywhere; 26 rows rest on assumption G01.

## Dispositions (operator OP-5, 2026-10-05)

    X18  TABLE          first-witness boundary (T04.LAGD, T05.WIPE, T06.LAGD)
    X19  TABLE          T08 CL-RET standing UNQUALIFIED via RESTART precondition
    X06  TABLE          E02.MISSING G-INV reason commentary; CL-CUST(G0) standing BLOCKED
    X06  CONTRACT GAP   E02.MISSING authority of an absent receipt (UNQUALIFIED vs n/a): preserved for S5
    X02  TABLE          E02.RELABEL claim CL-RET(REG2) not registered
No implementation repair and no contract amendment before S3; corrections and the gap are carried to S5
(C-004-T050). FREEZE_S2 preserved exactly as committed (c91e39e85).
