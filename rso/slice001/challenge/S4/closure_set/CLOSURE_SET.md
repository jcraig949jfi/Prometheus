# C-004-T041 S4 closure set (committed before any outcome is observed)

Reviewer: Pallas[m2-e7da6bde], claude-fable-5-1. Frozen repaired surface: rso/slice001/FREEZE_S4.md (code
0e1943bff, contract v1.0.4); the working tree's 24 implementation files were checked against its hashes before
this commit (all equal). Branch pallas/c004-t041 from the claim commit d92546849.

Exposure since S3 (this instance): read AMENDMENT_v1.0.4, FREEZE_S4.md, s4/REGRESSION.md, the repair diff of
adapter.py, evidence.py and checker.py (b220c7e39..0e1943bff), the S2 and S4 G0 receipts' node ids and one run
id each. NOT opened: any file under rso/slice001/tests/ (then or during S3), s4/MATRIX.*, T042/T043 receipts.
Same-family and cell-membership caveats as S3 (CONTRACT.md s6).

Files: cases.py (four case builders and the probe), expected.json (answer key and scoring rule, as S3),
edits.json (X1-X3), witnesses.py, run_cases.py, run_mutation.py. Drivers may be repaired after this commit;
the four data files may not.

## Cases (plan s5: 2 fresh sound, 2 fresh broken), on the committed S4 G0 bundle

S4.SOUND.REPRODUCED (custody, G-BIND; F2). The keeper holds the S2 G0 manifest (registered earlier) AND the S4
G0 manifest: the same 25 node ids, new receipts -- which is the real registry's state after T045. The consumer
is handed the S4 bundle and both blobs. B5.2/B5.3: custody qualifies against the row whose blob is THIS
bundle's manifest. Expected: custody QUALIFIED and every decision byte-identical to the single-manifest keeper
control.

S4.SOUND.RETRY_ROW (G-INV; F3). The inventory also holds an INTERRUPTED row (a first attempt that died) for
REG's PRESERVE node before the COMPLETED row the receipt cites. B6.4 requires the cited run once and a receipt
for every COMPLETED row; an interrupted row is neither. Expected: CL-RET(REG) ELIGIBLE, G-INV PASS, every
decision identical to the baseline.

S4.BROKEN.OBS_RUN_BORROW (G-INV; F3). OBSERVER(REG, BOOKKEEP)'s receipt cites the run of OBSERVER(REG, NULL):
same subject and predicate, another observer; its own row removed; anchors re-made. The repaired check must
compare the full node id. Expected: G-INV FAIL RECEIPT_WITHOUT_RUN:rcpt:REG:OBSERVER:BOOKKEEP:STANDARD;
CL-RET(REG) NOT_ELIGIBLE, UNMET; the other claims identical to the baseline.

S4.BROKEN.VERSION_OF_ANOTHER (authority A1, measurement binding). REG's ERASE receipt names as its version the
list the OBSERVER stage record registers (a real staged version, of another instrument), with cell.measurement
made consistent. B4.1: a stage belongs to (instrument, version). Expected: ERASE(REG) UNQUALIFIED
NO_STAGE_RECORD; CL-RET(REG) NOT_ELIGIBLE, standing UNQUALIFIED; G-BIND PASS; other claims identical.

Probe S4.PROBE.STALE_RUN (unscored): the S4 PRESERVE receipt cites the S2 run of the same node; inventory intact.
See expected.json. Related to T045 observation O-S4-1.

## Edits (plan s5: 3, covering touched claim-critical predicates)

    id  module    edit                                              witness: original -> mutant
    --  --------  ------------------------------------------------  ------------------------------------------
    X1  adapter   clamp at (TICK j PROBE_D), before the reset at j  trace:clamp of WIPE, history 0:
                  (F1 surface: the bound trace must clamp right     "010101" -> "000000"
                  after the reset, as reset.clamp_answers does)
    X2  evidence  custody guard inverted (>= for <=): a manifest     custody why with anchors omitting LAGD:
                  omitting presented nodes qualifies again (F2)      contains ROW_BLOB_MISMATCH -> does not
    X3  evidence  G-INV compares the cited row's node id on          g_inv, BOOKKEEP citing NULL's run:
                  subject and predicate only (F3)                    (FAIL, RECEIPT_WITHOUT_RUN:...) -> (PASS, ..)

Execution plan: one launch for the cases (consumer-only, no build), one for the edits (targeted suite:
test_adapter, test_evidence, test_checker_render, test_stages_evidence; survivors then against the full suite
within a 20 CPU-minute S4 allowance). No separate unchanged-suite launch: T045's regression run (REGRESSION.md)
and the runner's own baselines stand for it; this is stated in the report.

## Predictions (to be lost)

REPRODUCED: refused -- resolve_anchors prefers the earliest exact-node-set candidate, the S2 manifest, so
G-BIND fails BYTES_MISMATCH:receipt on five claims while custody reads QUALIFIED against the S2 row. RETRY_ROW,
OBS_RUN_BORROW, VERSION_OF_ANOTHER: as expected. STALE_RUN: admitted. Edits: X1 survives, X2 killed, X3 survives.
