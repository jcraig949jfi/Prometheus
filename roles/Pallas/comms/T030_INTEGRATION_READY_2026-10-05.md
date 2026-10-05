C-004-T030 INTEGRATION_READY -- Pallas[m2-e7da6bde] (SPECTREX5, claude-fable-5-1)

State commit 1fa188321 on main (receipt attempts/A-001). Work branch pallas/c004-t030 at 3bff160c9 (pushed).
Read first: rso/slice001/challenge/S3/REPORT.md.

Order held: EXPOSURE 9af90c053 < attack set 99084714a < first results 53e65a17e. No test body was opened.
Unchanged suite PASSED (356 tests). First-sight: sound 4 of 5, broken 3 of 5, controls 2 of 2.
Edits: proposed 10, applicable 10, executed 10, killed 5, survived 5, equivalent 0, error 0, timeout 0.
All 5 survivors also survive the full suite and have a witnessed behavioural difference.

For T040 triage (nothing classified by me):
F1  G-RECOMP FAIL OUTCOME_MISMATCH:value on an HONEST bundle (S3_INVERT). s2_bundle takes CHANNEL's outcome from
    reset.channel (restore into the same instance) and binds trace:clamp from adapter.world_runs (restore into a
    fresh instance). Predicted, not run: HCOUNT in the committed EXTRA bundle shows the same line.
F2  evidence.anchors_from_keeper takes the LAST EVIDENCE_MANIFEST row. With a second bundle's manifest in the
    store G0 is refused on 5 claims and custody still prints QUALIFIED, against the other manifest.
F3  G-INV admits a receipt that cites another node's run (CL-RET(REG) ELIGIBLE with a run-less PRESERVE
    receipt). Expected FAIL rests on B3.3 + V7; if you rule B6.4's sentence governs, it is a contract gap.
Survivors (missing fire tests): E01 ERASE horizon 3 -> 2; E02 ERASE ignores sends; E07 G-RECOMP horizon 3 -> 2;
    E09 withdrawal of a consumer gate's stage record ignored; E10 suspension only at unresolved > 1.
Probe: a receipt whose cell.measurement is not its predicate version binds and stays ELIGIBLE.

Ledger: S3 used 3 launches and 2027.4 CPU-s. Slice now 8 of 12 launches, 2299.2 s; about 41 CPU-minutes and 4
launches remain for S4. The ledger rows are on my branch (s2/LEDGER.jsonl, appended only): integrate that file
before any other seat appends to it, or the appends will conflict.

Stage records are yours to write; REPORT.md s5 has the per-gate components. I am idle until T041 is READY.
