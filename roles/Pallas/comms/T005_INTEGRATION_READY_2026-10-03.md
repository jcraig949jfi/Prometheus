C-004-T005 INTEGRATION_READY -- Pallas[harry1-da86cf98] (claude-fable-5-1, Q3), harry1

Branch pallas/c004-t005 (pushed). Please integrate.

Deliverables (rso/slice001/expected/):
  EXPECTED_ANSWERS.json  48 rows, one per contract.json case id; committed at 3ea4af125 BEFORE unblinding
  EXPOSURE.md            reading order, leaks through readable text, prior exposure
  _build_expected.py     generator (asserts the 48 ids equal contract.json's, in order)
  COMPARISON.md          written after reading A6 / B8.2 / B9; table untouched since 3ea4af125
Escalation: ops/campaigns/C-004/escalations/C-004-T005_1.md (check-escalation OK)
Receipt: ops/campaigns/C-004/tasks/C-004-T005/attempts/A-001/RECEIPT.json (state commit on main)

Result: 18 DETERMINED, 26 DETERMINED_UNDER_ASSUMPTION, 4 PARTLY_UNDETERMINED
(T02.CLOCKED, E06.LOSSY, E02.RELABEL, E03.REANCHOR). Against the authors: 43 of 48 primary values agree,
0 contradict, 5 not scorable. Agreement is weak evidence: contract.json prints every case's polarity and
six rows leaked through readable sections (EXPOSURE.md s4).

Disagreements left unresolved for T020:
  D1 node_id uses predicate NAME in B9, predicate ID in B3.1
  D2 E02.MISSING: G-INV RUN_UNREPORTED also fires; scope across claims undefined
  D3 E04.W_RESTART: CL-RET(LAGD) also loses authority (UNMET -> UNQUALIFIED); author omits it
  D4 E04.W_UNRELATED: TWIN(M, M') is a B7.1 claim and depends on the withdrawn receipt
  D5 custody why spelled with a record-kind parameter in B8.2, plain in B5.3 / R3
  D6 E03.REANCHOR: "undetectable against producer anchors" ignores G-RECOMP; row is two cases in one id
  D7 PKTD_NOQ / HCOUNT: CL-RET standing is UNQUALIFIED (PRECONDITION:RESTART), not UNMET
  plus E02.RELABEL: IDENTITY_UNKNOWN precedes SCOPE_MISMATCH in B6.3 when the subject is renamed

Contract defects worth a spelling-only amendment before any S2 outcome (escalation option 2): B3.1 cites
a B7.3 that does not exist (trace roles); no FAIL reason form for P0, P7, P8; node_id form; edge / field
spellings. Case-expectation changes are the operator's after any S2 outcome (CONTRACT.md s7).

For Aporia via you (R3): the EXPECTED_ANSWER_TABLE record to register is
rso/slice001/expected/EXPECTED_ANSWERS.json at commit 3ea4af125 (blob hash in the receipt).

Not run: no test, no ci, no matrix; no file under rso/slice001 outside contract/ and expected/ opened.
Reviewer time used: about 1 hour of 3 (estimated from commit times). T030 / T041 not taken.
