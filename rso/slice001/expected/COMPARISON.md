# COMPARISON -- independent table (Pallas) vs author-expected columns (draft A A6, draft B B9, B8.2)

Packet C-004-T005. Written by Pallas[harry1-da86cf98] (claude-fable-5-1) AFTER the table was committed and
pushed at 3ea4af125 (branch pallas/c004-t005). EXPECTED_ANSWERS.json was not edited after the author columns
were read. Nothing here is resolved: each item is evidence for C-004-T020, which classifies it as
implementation, contract or table defect (CONTRACT.md R4).

Read after the commit, in order: draft A lines 225-290 in full (A6); draft B lines 432-541 in full (B8.2, B9,
B9 couplings); a grep of draft A A8-A10 and draft B B11-B13 for "B7.3", "trace:", FD ids and reason forms. No
file under rso/slice001/ outside contract/ and expected/ was opened at any time in this session.

## 1. Score, with denominators

    48 rows compared on the PRIMARY outcome value (the verdict the case exists to exercise)
      43  agree with the author-expected value
       0  contradict it
       5  cannot be scored as agree/contradict (sections 2.1-2.5): mine UNDETERMINED or wider than the
          author's, or the author's row is conditional / silent on the field
    Beyond the primary value:
       4  disagreements on a typed reason, a spelling or a secondary claim line (D1-D4)
       3  author-expected statements my table does not reproduce and that I think are wrong or incomplete
          by the letter of the contract (D5-D7)

Agreement is NOT independent on the rows listed in EXPOSURE.md section 4 (T01.QCARRY, T02.AMNESIAC,
T02.CLOCKED, T02.FLIP, T05.WIPE, T06.LAGD): the author's answer was visible in text I was allowed to read.
Agreement on polarity alone (PASS vs FAIL) is weak everywhere: contract.json prints the polarity of every case.

## 2. Rows that cannot be scored as agreement

2.1 T02.CLOCKED -- RETENTION value. Author: "RETENTION not reported as evidence on this world" (no value).
    Mine: execution RAN, authority UNQUALIFIED PRECONDITION:CALIBRATION, outcome UNDETERMINED (gap G04: the
    CLOCKED domain is not stated; with u_j fixed the NEGATIVE condition is vacuously true for every runtime
    while the clock-following policy has s = 1). Neither table gives T020 a value to compare. CALIBRATION
    FAIL agrees.

2.2 E02.RELABEL -- reason code. Author: SCOPE_MISMATCH:physics, "CL-RET(REG) and the relabelled branch
    NOT_ELIGIBLE, UNMET". Mine: G-BIND FAIL, reason UNDETERMINED among SCOPE_MISMATCH:physics and
    IDENTITY_UNKNOWN:<node_id> (gap G08). The author's answer holds only if node_ids keep "REG" while the
    subject is renamed; node_id embeds the subject (B3.1), and B6.3 checks "node_id present in the manifest"
    BEFORE scope equality, so a consistent rename gives IDENTITY_UNKNOWN. If every REG node is renamed,
    CL-RET(REG) itself has no nodes left: by B6.3 row 1 that is BLOCKED / EVIDENCE_MISSING, not UNMET.

2.3 E03.REANCHOR -- not one answer. Author: "against producer anchors G-BIND PASS; against keeper rows G-BIND
    FAIL; custody UNQUALIFIED when only producer anchors are presented" with reasons "BYTES_MISMATCH /
    ANCHORS_FROM_PRODUCER". Mine: G-BIND PASS (producer anchors), custody UNQUALIFIED ANCHORS_FROM_PRODUCER,
    G-RECOMP and CL-RET(REG) UNDETERMINED. The author row is two cases under one id and gives no CL-RET(REG)
    eligibility and no G-RECOMP value. See D6.

2.4 E06.LOSSY -- reason. Author: TWIN_EQ FAIL (RETENTION NEGATIVE vs POSITIVE). Mine: FAIL, witness
    UNDETERMINED, no registered reason form (G02). Value agrees; the typed reason has no contract form.

2.5 T02.AMNESIAC -- CHANNEL sub-line. Author fixture: "a is never written; answer is 0", no CHANNEL value.
    Mine: CHANNEL UNDETERMINED (PASS if the answer is read from `a`, FAIL at v = 1 if it is the literal 0).
    The author text does not settle it either. The primary value (RETENTION NEGATIVE 1/2, CL-RET UNMET)
    agrees; the CL-RET(AMNESIAC) decision record lists one or two UNMET lines depending on this.

## 3. Disagreements on reasons, spellings and secondary lines

D1  node_id spelling (E02.MISSING, E03.STRIP and every node id). Author: rcpt:REG:PRESERVE:STANDARD and
    rcpt:REG:RETENTION:STANDARD->rcpt:WORLD:CALIBRATION:STANDARD (predicate NAME). Mine:
    rcpt:REG:P4:STANDARD (predicate ID). B3.1 defines node_id as "rcpt:<subject>:<predicate>[...]" and the
    predicate field as "id in P0..P8"; contract.json gates carry both id and name. The contract does not say
    which goes in the node id; the author's choice appears only in the blinded column.

D2  E02.MISSING -- G-INV. Author: no G-INV statement; "CL-RET(PKTD), CL-CAL unchanged". Mine: the removed
    receipt's run is still COMPLETED in the terminal inventory, so B6.4 gives G-INV FAIL RUN_UNREPORTED on
    CL-RET(REG) as well (standing still BLOCKED), and whether that FAIL reaches the other claims is gap G07.
    Also: the author places the BLOCKED on the PRESERVE verdict; B6.3's table places "execution BLOCKED" on
    the G-BIND check. My row carries both.

D3  E04.W_RESTART -- CL-RET(LAGD). Author: REG and PKTD receipts lose authority; CL-RET(REG), CL-RET(PKTD)
    UNQUALIFIED; LAGD not mentioned. Mine: one stage record per instrument version (B4.1), so RESTART,
    CHANNEL and OBSERVER of LAGD lose authority too, and CL-RET(LAGD) moves from UNMET to UNQUALIFIED (B7.2
    worst standing). Its decision record is not byte-identical.

D4  E04.W_UNRELATED -- the TWIN line. Author: "(no B7.1 claim depends on it)", "every claim's decision
    byte-identical". Mine: TWIN(M, M') IS a registered claim in B7.1 and contract.json `claims`, and its
    only prerequisite is the withdrawn TWIN_EQ receipt, so TWIN(REG, REG-ONEHOT) becomes UNQUALIFIED
    WITHDRAWN:<id>. The CL-CAL / CL-RET decisions are byte-identical in both tables.

## 4. Author-expected statements I do not reproduce

D5  B8.2 custody why: "UNQUALIFIED (KEEPER_ROW_MISSING: EVIDENCE_MANIFEST)" carries a record-kind parameter.
    B5.3 lists the typed whys without parameters, and R3 writes plain KEEPER_ROW_MISSING. Mine: plain. With
    five required record kinds missing at once, the author form does not say whether one or five are
    printed.

D6  B9 couplings: "edited traces are ... undetectable against producer anchors". For E03.REANCHOR as
    written (one flipped byte, receipts untouched) G-RECOMP recomputes RETENTION / ERASE / PRESERVE /
    CHANNEL from the flipped PROBE_A trace and compares with the unchanged receipt; unless the flipped byte
    is outside every recomputed quantity the result is G-RECOMP FAIL OUTCOME_MISMATCH. "Undetectable" is
    true only for a fabrication that also rewrites the receipts (E01.FAB_CONSISTENT). The author row does
    not say which byte is flipped.

D7  T06.PKTD_NOQ and T06.HCOUNT -- consequence of RESTART FAIL. Author: RESTART FAIL (plus, for HCOUNT,
    ERASE PASS and RETENTION NOT_SHOWN s = 1/3, which I confirm after unblinding: the answer is right at
    j = 1 and inverted at j = 2, 3). Mine adds what B4.2 A5 and B7.2 force: CHANNEL and OBSERVER on that
    runtime are UNQUALIFIED PRECONDITION:RESTART, so the CL-RET headline standing is UNQUALIFIED, not UNMET.
    The author column gives no standing; an implementation that prints UNMET contradicts B7.2.

## 5. My assumptions, checked against the now-visible fixture definitions

    row            my assumption                                    author definition              result
    -------------  -----------------------------------------------  -----------------------------  ---------
    T01.QCARRY     answers from the delivered bit                   a := delivered bit; sends      same verdict; mechanism
                                                                    (u, 1); no flush               differs (a IS written)
    T02.FLIP       s = 0 if it answers the complement               answers 1 - a; s = 0           match
    T04.LAGD       k = 1; reset clears d only; visible at           (f, 1); d := 0 only; display   match
                   episode 2 PROBE_A                                at PROBE_A of j+1 is f_j
    T05.WIPE       reset also sets a := 0; 6144 applicable          same; 6144 of 6144             match
    T06.PKTD_NOQ   capture omits chan                               same                           match
    T06.HCOUNT     hidden episode counter, used from episode 2      hidden RESET counter; answer   same verdict; my guess of
                                                                    inverted after >= 2 resets     the mechanism was wrong
    T07.HEAL       flips a declared component or an output and      flips d after CUE, restores    match (output part)
                   restores it                                      after PROBE_D
    T07.BOOKKEEP   writes only log_n                                same, via capture/restore      match
    T08.EVERY3     leak on call 3 = uncleared d; boundary 3 only    keeps d on call 3; j = 3 only  match
    T08.SLEEPER    f_e carried: boundary 1, first seen episode 3    f_e XOR f_(e-2) at PROBE_D     match (first branch)
    T08.SPLIT1/2   shares that separately look clean                c = f XOR u; packet f XOR u    match; ticks were blind
    P0.OVERDELAY   k >= 4                                           sends (f, 4)                   match
    E06.LOSSY      non-reversible encoding                          both values of a -> one code   match

Derived only now, NOT part of the committed table: T06.HCOUNT first RESTART witness = history all-zero, cut
"after reset 1", target FRESH (COMPLEMENT_PREFIX cannot fail: the counter is schedule-determined, so the
complement instance holds the same count); HCOUNT also FAILs CHANNEL in outcome at j = 2, 3 (the clamped
answer is inverted), masked by its UNQUALIFIED authority; E06.LOSSY's outcome vector should differ from
REG's in CHANNEL as well as RETENTION, and its PRESERVE is a vacuous PASS against REG's non-vacuous PASS --
whether TWIN_EQ compares values only or values with counts and vacuity is not stated.

## 6. Contract gaps the comparison confirms (full text in EXPECTED_ANSWERS.json `gaps`)

    G01  fixture definitions live in the blinded column                       confirmed (structure)
    G02  no FAIL reason form for P0, P7, P8                                    confirmed: the author column
                                                                               gives none either
    G03  canonical order lacks v and the pair partner; 9600 vs "any two"       open; counts agree at 9600
    G04  ruler on CLOCKED                                                      open (2.1)
    G05  authority with the keeper store UNSET                                 open; B8.2 prints QUALIFIED at
                                                                               author-tested with custody
                                                                               KEEPER_ROW_MISSING, i.e. the
                                                                               author assumes fixture anchors
                                                                               carry stage records
    G07  G-INV per-claim scope                                                 open (D2)
    G08  RELABEL reason                                                        open (2.2)
    G09  "B7.3" does not exist; role / edge / field spellings                  confirmed: "trace:probe_a" and
                                                                               the edge spelling exist only in
                                                                               the B9 expected column
    G10  what the anchor is when custody is not exercised                      author's coupling text adopts
                                                                               "whatever anchors the consumer
                                                                               holds"; consistent with my
                                                                               reading for OUTCOME_EDIT
    G11  custody why list                                                      open (D5)
    G12, G13, G14, G15                                                         open; not addressed by the
                                                                               author columns

## 7. What would falsify this comparison

- An S2 matrix run (T020) in which REG, PKTD or any fixture returns a primary value different from BOTH
  tables: the two tables share plan s4 and contract.json polarity, so joint agreement is not proof.
- A reading of B6.3 under which RELABEL deterministically yields SCOPE_MISMATCH:physics with renamed
  subjects would move 2.2 from contract gap to table defect (mine).
- If stage records are per (instrument, subject) rather than per instrument version, D3 is a table defect.
