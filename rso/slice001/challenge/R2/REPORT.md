# C-004-T048 R2 closure re-check (second and final repair) -- REPORT

Reviewer: Pallas[m2-1500b878], claude-fable-5-1 (Q3), SPECTREX5. 2026-10-06. Frozen second-repair surface:
rso/slice001/FREEZE_R2.md (code ad6b3fa96, contract v1.0.5 with AMENDMENT_v1.0.5); 41 hashes verified against
the committed bytes and the working tree before the set was written. Branch pallas/boot-2026-10-06, pushed to
main at each step. Caveat printed with every closure record (CONTRACT.md s6): cell member, writes no production
code, same vendor family as the builders (T046 author on claude-opus-5-5), same family as the S3/S4 reviewer and
the T005 table. The S3 first-sight and S4 closure records are preserved unchanged (challenge/S3/REPORT.md,
challenge/S4/REPORT.md); the figures here are second-repair re-check figures, reported separately (plan s5).
Exposure: closure_set/EXPOSURE.md (no test body opened; no repair diff read).

## 1. Ordering evidence (git, all on origin/main)

    6f0ac7773  claim of C-004-T048 (CLAIMED, LEASE.json)                               2026-10-06T23:25Z
    c8f702862  R2 set: cases, expected.json, edits.json, witnesses, drivers, CLOSURE_SET.md
               with predictions, EXPOSURE.md                                            2026-10-06T23:32:45Z
    launch 1   run_cases.py       R2-CASES-20261006T233303Z-2496      23:33:03Z-23:33:05Z
    launch 2   run_mutation.py    R2-MUTATION-20261006T233338Z-21956  23:33:38Z-23:38:00Z
    (next)     results rows, ledger rows, this report, receipt -- one commit

The data files of the set (cases.py, expected.json, edits.json, witnesses.py) are byte-identical to c8f702862;
no driver repair was needed, so the third permitted launch was not used. No separate unchanged-suite launch:
T047's consume-only regression (s4/R2/REGRESSION.md) and the mutation runner's own baseline (165 tests,
PASSED, 22.3 s) stand for it; the full frozen suite (393 tests) ran once, as the confirmation child of the
survivor, and passed there (0 failures on the mutant: the suite does not pin the edited behaviour).

## 2. Re-check score (denominators are the packet's 1 + 1 + 1; probes are outside them)

    sound cases    1 correct of 1   R2.SOUND.SUPERSET_MANIFEST: custody QUALIFIED on the S4 manifest row
                                    (EVIDENCE_MANIFEST:924f6cc3392e, the keeper control's row), CL-CUST(G0)
                                    SATISFIED, all six decisions byte-identical to the keeper control
    broken cases   0 correct of 1   R2.BROKEN.LATER_WINDOW_RUN: ADMITTED. G-INV PASS "inventory terminal; every
                                    run reported"; CL-RET(REG) ELIGIBLE / SATISFIED; the other four claims
                                    identical to the baseline (so the admission is the only effect)
    controls       2 of 2           R2 G0 baseline; R2 single-manifest keeper case
    probes         2 recorded, unscored, both ADMITTED (G-INV PASS): OVERLAP_RUN (FD-T046-1 as declared),
                                    FAILED_ROW_CITED (undeclared shape)

    edit           proposed 1 | applicable 1 | duplicate 0 | executed 1 | killed 0 | survived 1 | equivalent 0 |
                   error 0 | timeout 0
                   Y1 (G-INV world-insensitive) SURVIVED the targeted suite (165 tests, 0 failures) and the FULL
                   frozen suite (393 tests, 0 failures); witness DIFFERS, NOT_EQUIVALENT_WITNESSED:
                   original (FAIL, RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD) -> mutant (PASS, "inventory
                   terminal; every run reported")

## 3. CLOSED / NOT CLOSED, per the packet's acceptance condition

    C1  manifest selection for a reproduced bundle (resolve_anchors by artifact match; smallest full match)
        CLOSED within this re-check. The fresh sound case on the surface is correct: with three verified keeper
        manifests (S2: same node ids, other artifacts; S4: this bundle's; a 26-node superset with the S4
        artifacts) the consumer anchors to the S4 manifest, custody cites that row, and every decision equals the
        single-manifest control. No false rejection, no survivor on the C1 surface (the one edit was placed on
        C2). The S4 false rejection itself (S4.SOUND.REPRODUCED) is T046's regression, author-run; it was not
        replayed here, by the packet's rule.

    C2  G-INV binds the cited run to the receipt's FULL node id
        NOT CLOSED. The observer axis -- the S4 open item -- is pinned by T046's TestC2ObserverRunBinding (per the
        T046 receipt: X3 now fails RED; not re-run here). The WORLD axis of the same binding is not pinned: Y1,
        which drops the trailing world component from the comparison, survives all 393 frozen tests, and the
        witness shows the mutant admitting a receipt for PRESERVE(REG, STANDARD) that cites the run of
        PRESERVE(REG, TWINWORLD). Same class as the S4 finding (a missing fire test, not a defect of the frozen
        code), one axis over. Scope fact for the adjudicator: every one of the 232 real inventory rows is world
        STANDARD, so the fault is reachable only in a registry that holds runs of more than one world variant;
        the slice's node id carries the world axis (V7) and the C2 ruling names it.

    B3.3  run attribution after AMENDMENT_v1.0.5 (the amended predicate, in the packet's surface list)
        NOT CLOSED. The operationalisation `run.end_utc >= receipt.created_at_utc` refuses an earlier window's run
        (STALE_RUN, T046's regression) and admits a LATER window's run of the same node: the scored broken case
        was admitted with no change to any other claim. The author declared FD-T046-1 as "two OVERLAPPING
        launches of one node are not separated"; the run in this case starts eleven hours after the S4 launch
        ended and does not overlap it, so the admitted shape is wider than the declared one -- the bound is
        one-sided and binds nothing to the receipt's own launch. The probes confirm the declared overlap
        admission and add a second undeclared shape: a FAILED row of the receipt's own node, inside the S4
        window, is accepted as the run that produced the receipt (g_inv does not read the cited row's status).

    New unresolved claim-critical survivors found by this re-check: 2 scored (Y1 on C2; LATER_WINDOW_RUN on
    B3.3) and 1 probe shape (FAILED_ROW_CITED) for adjudication. OP6's condition for opening the native
    retained-information witness ("only if C1/C2 close with no new unresolved claim-critical survivor") is NOT
    met by this re-check's figures. No third repair round exists (OP6); what follows is the operator's.

## 4. The admitted later-window run, in detail (rows: results_cases.jsonl, case_claims R2.BROKEN.LATER_WINDOW_RUN)

The S4 PRESERVE receipt of REG: created_at_utc 2026-10-06T00:00:53Z; its own row g0-...-9752/rcpt:REG:PRESERVE:
STANDARD ran 00:00:56-00:00:57Z. The case rewrites execution.run_id to a new COMPLETED row of the same full node
id with start 2026-10-07T12:00:00Z, end 12:00:01Z, appended to the 232-row cumulative inventory (233 RUN rows,
terminal count updated); the receipt's own row stays, uncited. g_inv: exactly one row carries the cited run_id,
its node_id equals the receipt's, _ended_before(row, created_at) is False because 12:00:01Z on the 7th is not
before 00:00:53Z on the 6th -- PASS. The uncited S4 row raises nothing: RUN_UNREPORTED is checked only for
required nodes WITHOUT a presented receipt (Y2, by design). Custody in this case is UNQUALIFIED
(KEEPER_ROW_MISSING on the three bundle rows, as in every S3/S4 broken case built on the stage-rows-only store)
and is not scored; the measured object is G-INV alone.

Design fact that fixed the case: in the real S4 bundle every receipt's created_at_utc (00:00:53Z) PRECEDES the
start_utc of its own run (00:00:54Z-00:01:39Z). The receipt timestamp is the bundle's build time. So a start-based
bound ("the run must have started before the receipt existed") would reject every real receipt, and a "future
run" case is indistinguishable from sound data; the consumer's only honest bound is the bundle's own launch
window (the TOP_LEVEL row of the bundle's run_id, present in the inventory), which the implementation does not
consult. That is the shape a repair would have to address; it is not asked for here.

## 5. The surviving edit, in detail (rows: mutation_rows.jsonl, mutation_confirm.jsonl)

    find     cited[0].get("node_id") != rc.node_id                       (evidence.py, g_inv; X3's line)
    replace  (cited[0].get("node_id") or "").rsplit(":", 1)[0] != rc.node_id.rsplit(":", 1)[0]
    targeted suite  test_evidence, test_checker_render, test_stages_evidence, test_ledger: 165 run, 0 failures
    full suite      16 modules: 393 run, 0 failures, 216.1 s
    witness         synthetic G0; the row cited by rcpt:REG:PRESERVE:STANDARD renamed to rcpt:REG:PRESERVE:TWINWORLD

The fixture that would pin it is the witness itself (a receipt in one world citing the run of the same subject,
predicate and observer in another world); it is reusable as a fire case for G-INV.

## 6. Per-gate re-check components (for the C4 records, draft B B4.1)

    gate / surface                 sound c/t  broken c/t  probes adm/rec  edits: prop appl exec kill surv  open
    -----------------------------  ---------  ----------  --------------  ------------------------------  -------
    custody + G-BIND (C1)          1/1        0/0         0/0             0    0    0    0    0           -
    G-INV observer binding (C2)    0/0        0/0         0/0             1    1    1    0    1           Y1 (world)
    G-INV run attribution (B3.3)   0/0        0/1         2/2             0    0    0    0    0           LATER_WINDOW;
                                                                                                          FAILED_ROW

Which records may be CLOSED_AFTER_REPAIR is the registrar's (Palamedes) and the operator's; this reviewer
records only that C1 has no open item and C2 and B3.3 each have one scored open item.

## 7. Predictions (CLOSURE_SET.md), scored

5 of 5: SUPERSET_MANIFEST correct; LATER_WINDOW_RUN admitted; OVERLAP_RUN admitted; FAILED_ROW_CITED admitted;
Y1 survived both suites. A perfect prediction score on a set this small is also a warning that the reviewer
wrote cases it already believed in; the set was fixed before any run and is open to that criticism.

## 8. Resources (ledger rows with run ids starting "R2-"; rso/slice001/s2/LEDGER.jsonl)

    launches (TOP_LEVEL)   2 of the 3 permitted   cases 1.1 s; mutation driver 0.1 s
    MUTATION_CHILD rows    3                      baseline 22.3 s, targeted edit 22.9 s, full-suite confirm 216.1 s
    CPU charged            262.5 s (4.4 CPU-minutes) of the ~15 allowed; wall seconds for children
    slice ledger after     17 of 20 launches; 3187.2 s ledgered CPU (53.1 of 80 ledgered minutes); 31.8 MB
    reviewer time          about 30 minutes (claim 23:25Z, set 23:32Z, results 23:38Z, report to ~23:55Z)
    stage records          none regenerated; nothing registered with Aporia (consume-only, V8 fixture store)

## 9. Limits; what would falsify; what to stop

- One sound, one broken, one edit, two probes: a closure re-check at the packet's minimum, not a rate. Evidence
  plane only; world predicates untouched.
- C1 CLOSED is falsified by a keeper state this case did not model: e.g. two candidates that BOTH fully match
  with equal node counts but different blobs (impossible for byte-identical artifacts unless the manifest schema
  or node order differs); not probed.
- The B3.3 finding is wrong if the contract intends "window" to mean only "not before" -- Y1 of the amendment
  says "the launch that produced the receipt", which a later launch is not; the adjudicator reads the text.
- The C2 finding is a missing test; it is falsified by a test that fails on Y1. Its practical reach depends on
  whether the registry will ever hold runs of more than one world variant (today: none).
- Not worth continuing in this campaign: further G-INV borrow variants (observer and world are now both
  measured; subject and predicate were S3's); further time-bound variants (the one-sided shape is established by
  the scored case and both probes). What remains is a contract-and-design question for the operator, not a
  fixture question.
