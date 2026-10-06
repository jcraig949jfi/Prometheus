C-004-T041 INTEGRATION_READY -- Pallas[m2-e7da6bde] (SPECTREX5, claude-fable-5-1)

State commit c28b523a5 on main (receipt attempts/A-001). Work branch pallas/c004-t041 at f233c83bf (pushed).
Read first: rso/slice001/challenge/S4/REPORT.md.

Order held: claim d92546849 < closure set be673092d (01:34:11Z) < first results. No test body opened (S3 or S4).
Closure score: sound 1 of 2, broken 2 of 2, controls 2 of 2; edits 3 proposed / 3 applicable / 2 killed / 1
survived (X3, full suite 378 tests, witnessed). Exit criteria of plan s5 NOT met: incomplete closure, not
acceptance; also not a failure of the repairs (F1 and F3 cases handled; measurement and version binding handled).

Open items for S5 (nothing classified by me):
C1  S4.SOUND.REPRODUCED (false rejection). The registry holds the S2 G0 manifest and the S4 G0 manifest (same 25
    node ids). resolve_anchors takes the earliest exact-node-set candidate = the S2 manifest; every S4 receipt is
    BYTES_MISMATCH:receipt (G-BIND FAIL on 5 claims) while custody reads QUALIFIED on the S2 row. Node ids alone
    cannot tell two productions of one node set apart; artifact hashes can.
C2  Edit X3 survives: nothing pins G-INV's node-id comparison per observer (a receipt for OBSERVER(M, o1) citing
    OBSERVER(M, o2)'s run). The committed case S4.BROKEN.OBS_RUN_BORROW is the fixture (frozen code refuses it).
Probe STALE_RUN admitted (S4 receipt citing the S2 run of the same node, inventory intact): the O-S4-1 question.

Ledger: S4 used 2 launches, 459.1 CPU-s. Slice now 15 of 20 launches, 2924.7 ledgered CPU-s. The ledger rows are
on my branch (appended only): integrate before another seat appends. Stage records are yours; REPORT.md s6 has
the per-gate closure components and S3 REPORT s5 the first-sight object to carry unchanged.

Entering idle (OP-7); hourly check continues without heartbeats.
