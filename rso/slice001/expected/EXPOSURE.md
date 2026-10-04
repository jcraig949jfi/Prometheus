# EXPOSURE record -- C-004-T005 independent expected-answer table

Author: Pallas[harry1-da86cf98], runtime claude-fable-5-1 (Q3), host harry1 (M4), 2026-10-03.
Built from: base 4daae3782 fast-forwarded to 5e0a2aafb; claim commit 95305e7ec; branch pallas/c004-t005;
worktree C:/Prometheus-worktrees/pallas-c004-t005. Contract frozen at 595916f9c (contract.json sha256
e98bb0c6...279d85, version 1.0.0).

## 1. Order of events

The table (EXPECTED_ANSWERS.json), its generator (_build_expected.py) and this file are COMMITTED AND PUSHED in
one commit BEFORE any of the items in section 3 is opened. COMPARISON.md is written afterwards in a later
commit; the commit order in git history is the evidence. The table is not edited after that; a correction is
a new file beside it.

## 2. What I read before the table was committed, in order

All through `git show origin/main:<path>` in the canonical checkout or in this worktree.

1.  roles/Palamedes/prompts/2026-10-03_wake_pallas_t005/WAKE_Pallas.md (the wake and launch note)
2.  roles/base-role/WORKING_CONTRACT.md s1-s9; ops/work_orders/CURRENT.md (MWO-0004, first 120 lines);
    roles/base-role/RESPONSIBILITIES.md; roles/base-role/DISTRIBUTED_WORK.md
3.  roles/rso-builder-role/RESPONSIBILITIES.md; roles/Pallas/RESPONSIBILITIES.md and WORK_STATE.json
4.  ops/campaigns/C-004/tasks/C-004-T005/TASK.json; the file LISTING of ops/campaigns/C-004/ and of
    rso/slice001/contract/
5.  rso/slice001/contract/README.md, MANIFEST.md, CONTRACT.md (full), contract.json (full)
6.  draft A: heading list with line numbers; lines 1-212 (header, A1-A5); lines 213-224 (A6 preamble and the
    REG / PKTD definitions); lines 225-290 CUT TO COLUMNS 1-25 (case and fixture columns only); lines 292-378 (A7)
7.  docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/NEXT_ROUND_PLAN_v0.4.md (full; in the packet's `reads`)
8.  draft B: heading list with line numbers; lines 1-431 (header, B1-B8.1); lines 542-566 (B10); lines 460-464
    (B9 notation); lines 466-531 CUT TO COLUMNS 1-49 (case and bundle columns only)
9.  docs/phase3/closure/FABLE-5.1/CLOSURE_REVIEW_v0.4.md lines 1-31 (header, A), 89-133 (C1-C5), 174-221 (F, G)
10. comms message #1325 from Palamedes (the same launch note)

## 3. What I did NOT read before the commit

- draft A A6 columns 26 onward of lines 225-290 ("expected (independent fact)" and "outcomes")
- draft A A8, A9, A10 (lines 379-435)
- draft B B8.2 (lines 432-457), B9 columns 50 onward of lines 466-531, B9 "Couplings" (lines 533-540),
  B11, B12, B13 (lines 567-625)
- every file under rso/slice001/ outside contract/ and expected/. A directory listing showed the NAMES
  `__init__.py`, `ci.py`, `tests`; none was opened.
- SYNTHESIS_AND_DECISIONS_v0.4, closure review sections B, D, E; either harness corpus

## 4. Leaks: author-expected values that reached me through text I was allowed to read

Recorded so that agreement on these rows is not counted as independent.

- CONTRACT.md R1: QCARRY "passes ERASE" and must not be CL-RET eligible; "the B8.2 instrument count of 11".
  contract.json note on T01.QCARRY says the same.
- draft A A7: QCARRY "passes ERASE"; which T-row each escape maps to (SLEEPER, EVERY3, HCOUNT, LAGD, PKTD_NOQ,
  SPLIT1, SPLIT2, CLOCKED) and a one-line description of each escape.
- draft A A5 couplings: wipe PASSes ERASE and is refused by PRESERVE and RETENTION NEGATIVE; restart PASS with
  erase FAIL; RETENTION POSITIVE with ERASE FAIL.
- draft B B4.1: the ruler's fire test is T01 REG (POSITIVE), T02 AMNESIAC (NEGATIVE), T02 FLIP (NOT_SHOWN).
- draft B B4.2: the T02 CLOCKED consequence (CALIBRATION FAIL; RETENTION RAN, UNQUALIFIED PRECONDITION:CALIBRATION).
- draft B B7.2: the rendering of T02 AMNESIAC (NOT_ELIGIBLE, UNMET).
- draft B B9 notation line: "Expected outcomes of draft A are taken as given"; G0's composition.
- draft B B9 bundle column: each case carries its polarity word in the bundle text ("(true)", "(false)",
  "(coupling with E05)", "(stated limit)", "(false for revocation)"); contract.json carries the same polarity.
- draft B B10: which E-case each evidence-plane escape maps to.
- the plan s4 matrix gives the required answer class for every T and E id.

Rows that rest wholly or mainly on such text: T01.QCARRY, T02.AMNESIAC, T02.CLOCKED, T02.FLIP, T05.WIPE (ERASE
and RETENTION side), T06.LAGD. The fixture and bundle columns could not be separated from polarity; the
expected and reason-code columns were not seen.

## 5. Consequence of the blinding for this table

Every A6 fixture except REG and PKTD is DEFINED only inside the blinded column. For those rows the outcome
value is derived from the predicate definitions, the plan row, A7 and the registered polarity, and every
witness, boundary, tick or statistic that needs the fixture's exact behaviour is an assumption or UNDETERMINED
(gap G01 in the table). 18 rows are DETERMINED, 26 DETERMINED_UNDER_ASSUMPTION, 4 PARTLY_UNDETERMINED
(T02.CLOCKED, E06.LOSSY, E02.RELABEL, E03.REANCHOR). No row's primary outcome was guessed.

## 6. Prior exposure

- Model: Fable 5.1, the model family of the closure reviewer (seat Dionysus) and of the FABLE-5.1 hardening
  package. This SESSION has no memory of those sessions and opened none of their files; whatever shaped the
  hardening package's choices may shape mine in the same direction. That is correlated judgment, not
  independent confirmation, and it is not removable.
- Earlier sessions: the Pallas seat booted once on M2 (2026-10-03, instance m2-e7da6bde) and idled; I have no
  record that it read contract material. This is the first session of the seat on harry1.
- This host's local Claude memory mentions other Prometheus seats (Aletheia, Aphrodite); it contains nothing
  about RSO, C-004 or either harness.
- No prototype was written or run. No code under rso/slice001/ was executed. Counts in the table were derived
  by hand (9600 = 2048 + 3584 + 3968; 6144; 24576; 237568; 196608; 98304).

## 7. Independence caveat (OP-3, printed with every first-sight and closure record)

Pallas is a member of the RSO Builder Cell, writes no production code, and is a different model family from
the Opus/Sonnet builders.
