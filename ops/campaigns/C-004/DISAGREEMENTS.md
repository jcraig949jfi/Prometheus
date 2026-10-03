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

Independence caveats carried with this register (Pallas EXPOSURE.md s4): agreement on T01.QCARRY,
T02.AMNESIAC, T02.CLOCKED, T02.FLIP, T05.WIPE, T06.LAGD is not independent; contract.json prints every case's
polarity, so polarity agreement is weak everywhere; 26 rows rest on assumption G01.
