# C-004-T030 S3 attack set (committed before any outcome is observed)

Reviewer: Pallas[m2-e7da6bde], claude-fable-5-1. Frozen surface: rso/slice001/FREEZE_S2.md (code commit
b220c7e39, contract v1.0.3). Branch pallas/c004-t030. Nothing in this directory has been executed against the
frozen code, no edit has been applied, and no file under rso/slice001/tests/ has been opened. The only commands
run before this commit: the JSON emitter _build_edits.py (pure data) and a byte-compile of the files here.

Files (machine-readable; this file is the prose):

    cases_world.py    fresh runtimes and observers (attack tooling)
    expected.json     the expected typed verdicts, checks and the scoring rule -- the committed answer key
    edits_A.json      E01-E04, reset / observer        (schema rso.slice001.mutation_edits.v1)
    edits_B.json      E05-E10, binding and invalidation
    witnesses.py      one behavioural witness per edit (the runner evaluates it on original and mutant)
    run_cases.py      driver for the cases (one ledgered launch)
    run_mutation.py   driver for the edits (one ledgered launch; charges every mutation child)
    _build_edits.py   emits the two edits files

If a driver turns out to have a defect, it may be repaired after this commit; expected.json, the edits files,
cases_world.py and witnesses.py may not. Any such repair is listed in REPORT.md with its commit.

## 1. Reading record since EXPOSURE.md (step 2 of the packet)

Read in full, in this order: contract/CONTRACT.md; AMENDMENT_v1.0.1, v1.0.2, v1.0.3; contract.json; drafts A and
B (all sections, including A6, B8.2 and B9: the reviewer reads the whole contract at S3); NEXT_ROUND_PLAN_v0.4
section 5 only; implementation files mutation.py, world.py, reset.py, observer.py, rulers.py,
fixtures/world_cases.py, evidence.py, checker.py, fixtures/evidence_cases.py, receipt.py, adapter.py,
s2_bundle.py, render.py, ledger.py, ci.py, encoding.py, s2_run.py.

NOT read: matrix.py, stages/*.py, stages/*.json, expected/ (the T005 table, COMPARISON, _build_expected.py),
anything under s2/ (only its file names and the ledger summary command's totals were seen), CLOSURE_REVIEW_v0.4,
ops/campaigns/C-004/DISAGREEMENTS.md, the T005 and T020 escalations, both hardening corpora. No test body.

Deviation from EXPOSURE.md section 5: CLOSURE_REVIEW sections C and F were not read (not needed; C1-C5 are
written into the drafts).

Consequence for freshness: the existing fixtures and cases of A6, B9 and the two fixture modules are known to
this reviewer and none is reused. Whether a case or finding below duplicates an item already registered in
DISAGREEMENTS.md (X01-X19) or in s2/CLASSIFICATION.md cannot be known before this commit; any such overlap is
marked NOT FRESH in REPORT.md after those files are read.

## 2. Scoring rule (also in expected.json)

A case is CORRECT iff every scored check holds and no exception is raised while building or deciding it. Checks
compare the consumer's decision record with expected.json: claim eligibility, standing and the exact list of
non-SATISFIED prerequisites; listed fields of named prerequisite lines (execution, authority, outcome value,
reason, first witness, counts, vacuity); byte-identity with a reference decision; custody status. A sound case
that is refused, or a broken case refused for the wrong reason, is not correct. Probes are recorded, not scored.

Two controls run first (the real G0 baseline and the single-manifest keeper case). If a control fails, the
evidence-plane cases are unscorable and are reported so, not counted as findings.

## 3. Five fresh sound cases

S3.SOUND.LATCH (world). The cue writes an undeclared latch g (captured and restored as an extra key, A3 allows
it); the reset copies g into a. Derivation: y_A at episode j+1 is a = u_j, so RETENTION POSITIVE 12288/12288.
Outputs after boundary j depend only on u_j and later inputs: ERASE PASS, 9600 pairs. With the reset at j
skipped, a still holds u_(j-1) (0 for j = 1), so no pair differing only in u_j differs: PRESERVE PASS with 0
applicable pairs, vacuous. Clamping a after the reset is answered: CHANNEL PASS. Capture is complete: RESTART
PASS. CL-RET(S3_LATCH) ELIGIBLE, and its PRESERVE line must print "(vacuous: 0 applicable)". This is sound by
the letter of A5; that a runtime with RETENTION POSITIVE can pass PRESERVE vacuously is a property of P4 worth
the reader's attention, recorded here before the run.

S3.SOUND.BEACON (world). REG plus a constant packet (1, 2) at every CUE; the reset keeps the channel. The
FORBIDDEN channel is non-empty across every boundary, but what it carries is the same in every history.
Derivation: displays at PROBE_A are 0, 0, 1, 1, 1, 1 in every history; sends are constant; ERASE PASS (9600),
PRESERVE PASS (6144 applicable), CHANNEL PASS, RESTART PASS (the channel is captured), BOUNDS PASS (at most 3
packets in flight). CL-RET(S3_BEACON) ELIGIBLE.

S3.SOUND.MIGRATE (world, observer). Observer on REG that, after every tick, captures and restores into a new
instance and continues with it. REG's capture is complete, so outputs and declared state are identical to the
null observer: OBSERVER(REG, S3_MIGRATE) PASS, 196608 eligible; CL-RET(REG) with observers NULL and S3_MIGRATE
ELIGIBLE.

S3.SOUND.W_OTHER_VERSION (evidence). Real G0 plus a registered withdrawal whose target is the stage node of a
DIFFERENT version of the RESTART instrument (stage:P6:<another hash>). B4.1: a stage belongs to a version;
B6.5: only the reverse closure of the target loses authority. Nothing in G0 is in that closure: every decision
record byte-identical to the G0 baseline.

S3.SOUND.TWO_MANIFESTS (evidence, custody). The keeper case of E05, with one more keeper row: the
EVIDENCE_MANIFEST of another bundle, registered after G0's rows and before the consumer's first check. B5.2
registers a manifest per bundle; B5.3 qualifies custody when every required record of THIS bundle has a row
whose blob matches. A store holding a second bundle's manifest is the normal state of an append-only registry.
Expected: anchors fetched from the keeper are G0's; custody QUALIFIED; every decision byte-identical to the
single-manifest keeper control. The consumer is handed both manifest blobs.

## 4. Five fresh broken cases

S3.BROKEN.INVERT (world). The reset complements a and sets an undeclared, UNCAPTURED flag; the answer
un-complements while the flag is set. Primary verdict: RESTART FAIL, reason "capture/restore loses
future-influencing state at (RESET 1), target FRESH", witness {history 0, cut 4, point [RESET, 1], target
FRESH} (history 0, cuts 0-3: both targets reproduce the run; at the after-reset cut the fresh instance has the
complemented a without the flag and answers 1 where the run answers 0). RETENTION POSITIVE, ERASE PASS,
PRESERVE PASS (6144 applicable). CHANNEL and OBSERVER(NULL) ran but have authority UNQUALIFIED
(PRECONDITION:RESTART). Claim NOT_ELIGIBLE, standing UNQUALIFIED, non-satisfied exactly {CHANNEL, OBSERVER:NULL,
RESTART}. The bundle is built honestly, so G-BIND, G-INV and G-RECOMP must PASS: B3.1 says a receipt's outputs
are "every output trace the outcome is computed from" and B6.4 that G-RECOMP fails only when the recomputation
from those traces differs. CHANNEL's value is recorded, not scored (under the in-place reading of P5's restore
it is FAIL at {history 0, j 1, v 0}).

S3.BROKEN.SHADOW (world). a is written and never read; the answer comes from an undeclared register that IS
captured and restored. Everything passes except the one predicate that tests the allowed channel: CHANNEL FAIL,
reason "retained answer does not follow the declared allowed channel at 1", witness {history 0, j 1, v 1},
24576 eligible. RESTART PASS, RETENTION POSITIVE. Claim NOT_ELIGIBLE, standing UNMET, non-satisfied exactly
{CHANNEL}. (QCARRY carries through the declared forbidden channel; this carries through undeclared state with
a complete capture.)

S3.BROKEN.LOGDEP_BOOKKEEP (world, observer). REG whose answer also reads log_n, the component it declares
BOOKKEEPING; observer BOOKKEEP only increments log_n. A5 P7 excludes BOOKKEEPING from the state part and
"never from the output part". OBSERVER(S3_LOGDEP, BOOKKEEP) FAIL, reason "observer BOOKKEEP changes output at
(1, PROBE_A)", witness {history 0, episode 1, tick PROBE_A, what output}; OBSERVER(S3_LOGDEP, NULL) PASS; claim
NOT_ELIGIBLE, UNMET, non-satisfied exactly {OBSERVER:BOOKKEEP}.

S3.BROKEN.RUN_BORROW (evidence, G-INV). In the real G0, REG's PRESERVE receipt is rewritten to cite the run_id
of REG's ERASE run, the inventory row of the PRESERVE run is removed (terminal count corrected) and the anchors
are made from the edited receipts: a receipt for an evaluation that has no run of its own. B3.3: run_id is "the
attempted-run inventory row that launched it"; V7: every inventory row records the node_id it launched; B6.4:
a receipt naming a run never launched is RECEIPT_WITHOUT_RUN. Expected: G-INV FAIL
RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD on CL-RET(REG); claim NOT_ELIGIBLE, UNMET; CL-RET(PKTD),
CL-RET(LAGD), CL-CAL, TWIN(REG) byte-identical to the baseline. Derivation note: B6.4's sentence "every
receipt's run_id appears exactly once" read alone is satisfied (the borrowed id appears once); the expected
verdict rests on B3.3 and V7. If the coordinator rules the contract does not determine this case, it moves to
the probes.

S3.BROKEN.W_CALIBRATION (evidence, invalidation). Real G0 plus a registered withdrawal of the CALIBRATION
receipt. B6.5: every node in the reverse closure loses authority. CALIBRATION and the three RETENTION receipts
(B6.2 edge) become UNQUALIFIED (WITHDRAWN:W-S3-CAL); CL-CAL and all three CL-RET claims NOT_ELIGIBLE, standing
UNQUALIFIED; ERASE(REG) keeps its authority; TWIN(REG) byte-identical to the baseline.

## 5. Probes (recorded, not scored)

VERSION_DRIFT, MEASUREMENT_LIE, OBS_TRANSPLANT: definitions and this reviewer's readings are in expected.json
"probes". They are unscored because the contract does not fully determine the typed result.

## 6. Ten semantic edits

Each row: the edit (exact text in the edits files), its intended fault, and the witness (witnesses.py) with the
value it must give on the original and on the mutant if the fault is real.

    id   module    edit                                           witness: original -> mutant
    ---  --------  ---------------------------------------------  ------------------------------------------
    E01  reset     ERASE horizon j+1..j+H  ->  j+1..j+H-1          erase(S3_LAG3_EP3): FAIL -> PASS
    E02  reset     ERASE ignores the CUE (sends) output            erase(S3_RELAY): (FAIL, CUE) -> (PASS, None)
    E03  reset     RESTART cuts at after-tick points only          restart(S3_RESETCUT): (FAIL, [RESET, 1]) ->
                                                                   (PASS, None)
    E04  observer  OBS_EQ state part: ALLOWED component only       obs_eq(REG, S3_DFLIP): FAIL "changes state:d
                                                                   at (1, PROBE_D)" -> PASS
    E05  evidence  B6.2 edge OBSERVER -> RESTART not required      required_deps(OBSERVER(REG, NULL)): BOUNDS and
                                                                   RESTART -> BOUNDS only
    E06  evidence  slot identity compares the subject only         OBSERVER(BOOKKEEP) slot holding NULL's receipt:
                                                                   G-BIND FAIL IDENTITY_MISMATCH:node_id -> PASS
    E07  checker   G-RECOMP ERASE horizon 3 -> 2                   recompute_erase(traces of S3_LAG3_EP3):
                                                                   FAIL -> PASS
    E08  evidence  upstream closure stops after one edge           withdrawals applying to CHANNEL(REG) under
                                                                   W_RESTART: [W-RESTART] -> []
    E09  evidence  withdrawal of a consumer gate's stage ignored   gate_authority(G-BIND) after a registered
                                                                   withdrawal: UNQUALIFIED -> QUALIFIED
    E10  evidence  suspension needs unresolved > 1                 A1/A2/A4 reasons, unresolved = 1:
                                                                   [SUSPENDED] -> []

Span: reset/observer E01-E04; binding E05-E07 (policy edges, slot identity, recomputation); invalidation
E08-E10 (closure, gate withdrawal, suspension).

Execution plan (run_mutation.py). The caps do not allow ten full-suite children (about 7 CPU-minutes each), so
phase 1 runs each edit against the test modules that exercise its module (suite A: test_reset_observer,
test_encoding, test_stages_world; suite B: test_evidence, test_checker_render, test_stages_evidence,
test_receipt). A phase-1 kill is a kill. A phase-1 survivor is then run once against the full frozen suite, in
edit order, while this reviewer's S3 CPU allowance (40 CPU-minutes in total, leaving the rest of the cap for S4)
permits; a survivor not confirmed that way is reported as "survived the targeted suite only" and counts as
UNRESOLVED, never as equivalent. Test-module names come from FREEZE_S2.md; no test body was read to choose them.

## 7. Predictions (written to be lost)

Cases: LATCH, BEACON, MIGRATE, W_OTHER_VERSION, SHADOW, LOGDEP_BOOKKEEP and W_CALIBRATION will be handled as
expected. TWO_MANIFESTS will be refused or will raise (evidence.anchors_from_keeper takes the LAST manifest row).
INVERT will be refused for a wrong additional reason: G-RECOMP FAIL OUTCOME_MISMATCH:value on an honest bundle,
because s2_bundle takes the CHANNEL outcome from reset.channel (restore into the same instance) and the bound
trace:clamp from adapter.world_runs (restore into a fresh instance). RUN_BORROW will be admitted (G-INV counts
occurrences of the run id and does not compare the row's node_id). Probes: VERSION_DRIFT as expected;
MEASUREMENT_LIE admitted; OBS_TRANSPLANT refused with IDENTITY_MISMATCH:node_id.

Edits: E01, E02, E03, E04, E06, E07, E09 will survive the frozen suite; E05, E08, E10 will be killed. Every
prediction that fails is listed as failed in REPORT.md.

## 8. Ledger and caps

Three launches are planned for S3 (of 7 left for S3 + S4): the unchanged suite (ci --ledger), run_cases.py,
run_mutation.py. Every mutation child is a MUTATION_CHILD row charged its wall seconds. S3 stops at 40
CPU-minutes of its own rows or at the first exhausted slice cap, whichever comes first, keeping partial rows.
