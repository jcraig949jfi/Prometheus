# C-004-T048 R2 closure re-check set (committed before any outcome is observed)

Reviewer: Pallas[m2-1500b878], claude-fable-5-1 (Q3), SPECTREX5. Frozen second-repair surface:
rso/slice001/FREEZE_R2.md (code ad6b3fa96, contract v1.0.5 with AMENDMENT_v1.0.5); its 41 hashes were checked
against the committed bytes at ad6b3fa96 and against the working tree before this commit (41 equal, 0 mismatch).
Branch pallas/boot-2026-10-06 from the claim commit 6f0ac7773. Exposure: EXPOSURE.md beside this file.

Packet rule (plan s5, OP6, TASK.json): 1 fresh sound, 1 fresh broken, 1 semantic edit covering the C1 / C2 /
B3.3 surfaces; fresh means not a replay of the S4 cases (those are T046's regressions); the set is committed
before any outcome; no third repair round exists. Files: cases.py (two case builders and two probes),
expected.json (answer key and scoring rule, as S3/S4), edits.json (Y1), witnesses.py, run_cases.py,
run_mutation.py. Drivers may be repaired after this commit; the four data files may not.

## Cases, on the committed S4 G0 bundle (real executions, cumulative 232-row inventory)

R2.SOUND.SUPERSET_MANIFEST (C1 surface: custody and G-BIND). The keeper holds three verified manifests: the S2
G0 manifest (registered earlier; same 25 node ids, other artifacts), the S4 G0 manifest (this bundle's), and a
26-node manifest registered later whose nodes are the S4 nodes with their S4 artifacts plus one node the bundle
does not present (a superset production). The consumer is handed the S4 bundle and all three blobs. B5.2/B5.3:
custody qualifies against the row whose blob is THIS bundle's manifest. Expected: custody QUALIFIED, CL-CUST(G0)
SATISFIED, every decision byte-identical to the single-manifest keeper control (the CL-CUST decision embeds the
custody row ids, so qualifying against the superset row would show as a difference). S4.SOUND.REPRODUCED asked
"which of two same-node-set manifests"; this asks "which of an exact and a covering manifest", the branch of the
C1 repair (smallest full-artifact-match candidate) that the S4 case did not reach.

R2.BROKEN.LATER_WINDOW_RUN (B3.3 surface: G-INV run attribution, v1.0.5 Y1). The S4 PRESERVE receipt of REG
(created 2026-10-06T00:00:53Z; its own run 00:00:56-00:00:57Z) cites a COMPLETED run of the same full node id from
a later launch window (2026-10-07T12:00:00-12:00:01Z); both rows are in the inventory; anchors re-made from the
edited receipts, as S4.PROBE.STALE_RUN did. Y1: the cited row must belong to the launch that produced the
receipt. An earlier window's run is now refused (STALE_RUN); a later window's run did not launch or produce this
receipt either. Expected: G-INV FAIL RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD; CL-RET(REG) NOT_ELIGIBLE,
UNMET; CL-RET(PKTD), CL-RET(LAGD), CL-CAL(STANDARD), TWIN(REG) identical to the baseline.

Why this is the fresh broken case and not the overlap: the author declared FD-T046-1 as "two OVERLAPPING
launches of one node are not separated". A run that starts eleven hours after the S4 launch ended does not
overlap it; if it is admitted, the operationalisation (run.end_utc >= receipt.created_at_utc) is one-sided --
it excludes the past and binds nothing to the receipt's own launch -- which is a wider shape than the declared
one. Whether that counts as a NEW unresolved claim-critical survivor under OP6 is Palamedes's and the operator's
call; this set only measures it. Data fact that fixed the design: in the real S4 bundle every receipt's
created_at_utc (00:00:53Z) PRECEDES its own run's start_utc, so a start-based bound is not available to the
consumer and a "future run" case would be indistinguishable from sound data; the later-WINDOW case is the one a
consumer can in principle decide (the bundle's own TOP_LEVEL row bounds its launch).

## Probes (recorded, never scored; they do not enter CLOSED / NOT CLOSED)

R2.PROBE.OVERLAP_RUN: FD-T046-1 exactly as declared -- a second COMPLETED run of the same node overlapping the
S4 window (00:00:55-00:01:10Z) is cited instead of the receipt's own row. Expected admitted (declared escape).

R2.PROBE.FAILED_ROW_CITED: the receipt cites a FAILED row of its own node inside the S4 window; its own COMPLETED
row stays, uncited. g_inv does not read the cited row's status. Expected admitted; for the owning engineer.

## Edit (plan s5: one, on a touched claim-critical predicate)

    id  module    edit                                                 witness: original -> mutant
    --  --------  ---------------------------------------------------  ------------------------------------------
    Y1  evidence  G-INV compares the cited row's node id with its       g_inv, PRESERVE(REG, STANDARD) citing the
                  trailing world component dropped (C2 surface: the    row of PRESERVE(REG, TWINWORLD):
                  binding must be the FULL node id -- subject,          (FAIL, RECEIPT_WITHOUT_RUN:...) -> (PASS, ..)
                  predicate, observer AND world, V7)

S4's X3 dropped the observer and T046 killed it with TestC2ObserverRunBinding. Y1 drops the world instead and
asks whether the binding's fourth axis has a test. The find string is the same line X3 used (kept verbatim by
T046), so the edit applies to the frozen file.

Execution plan: launch 1 run_cases.py (consumer-only, no build: controls, two cases, two probes); launch 2
run_mutation.py (targeted suite test_evidence, test_checker_render, test_stages_evidence, test_ledger; a
survivor then against the full frozen suite within a 15 CPU-minute R2 allowance). Two of the three permitted
launches; the third is held for a driver repair rerun if one is needed, and otherwise not used. No separate
unchanged-suite launch: T047's regression (s4/R2/REGRESSION.md) and the mutation runner's own baseline stand for
it; stated again in the report.

## Predictions (written to be lost)

SUPERSET_MANIFEST: correct -- `full` holds the S4 and superset candidates, min by node count picks S4.
LATER_WINDOW_RUN: ADMITTED (G-INV PASS; CL-RET(REG) identical to baseline): _ended_before only refuses rows that
ended before created_at_utc. OVERLAP_RUN: admitted. FAILED_ROW_CITED: admitted. Y1: SURVIVES the targeted suite
and the full suite (the receipt describes observer tests, none on world; all fixture rows are world STANDARD).
Calibration: S4 predictions were 4/4 on cases, 2/3 on edits (X1 was predicted to survive and was killed).
