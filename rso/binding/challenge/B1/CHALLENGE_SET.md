# C-009-T030 CC3 independent challenge set on FREEZE_B1 (committed before any outcome is observed)

Reviewer: Pallas[harry1-b97f1fc4], claude-fable-5-1 (Q3), harry1 (M4), headless. Frozen surface:
rso/binding/FREEZE_B1.md (code 97606378c; rso/binding v1.0.0 + the s6 v1.0.1 clarification); its 48 hashes were
verified against the committed LF blobs at 5fefee452 and at 97606378c and against the LF-normalised working tree
before this file was written (48 equal, 0 mismatch). Branch pallas/c009-t030 from 5fefee452; claim 4aaa10bbb on
main. Exposure: EXPOSURE.md beside this file (the binding unit test file WAS read; no slice test body was).

Packet rule (TASK.json; CONTRACT.md s3 CC3): at least 1 fresh sound, 2 fresh broken and 2 semantic edits on the
binding path (rso/binding/binding.py; evidence.py g_inv / launch_unbound / custody; producer ledger.py +
s2_bundle.py), committed before outcomes; fresh = not the CC1 shapes (fixtures/cc1_cases.py), which are T011's
regressions. Files: cases.py (3 sound, 6 broken, 1 probe), expected.json (answer key and scoring rule, as S3/S4/R2),
edits.json (5 edits), witnesses.py, run_cases.py, run_mutation.py. Drivers may be repaired after this commit; the
four data files (cases.py, expected.json, edits.json, witnesses.py) may not.

## Where the attack is aimed, and why these shapes

Under the binding, every identity dimension a receipt records is inside one digest, and that digest is in a row of
an inventory which custody requires to be keeper-registered (BX7, s6). With a registered inventory and a
keeper-anchored manifest, no receipt byte and no row byte can change after registration; a cross-execution borrow
of subject, predicate, observer, world, artifact or status is therefore refused by DIGEST_MISMATCH or by G-BIND
before the binding is even consulted. What remains attackable is what the ROW does not say and what the GATE does
not ask: (a) row shapes the slice producer never writes but a native runtime may (retries, siblings, nested
parents, children, legacy rows); (b) the launch row's own identity; (c) which rows the gate ignores. The set
measures exactly those, on two bases: the synthetic G0 and the committed C-009 fresh produce rso/binding/R1/G0
(real executions, producer-bound).

## Cases (VICTIM: REG's PRESERVE receipt; it cites its OWN row unless stated)

SOUND (must be accepted; a false rejection is a finding):

  B1.SOUND.FAILED_RETRY         a FAILED first attempt of the victim's node under the launch (no digest, as
                                ledger.py writes FAILED attempts), before the COMPLETED row the receipt cites.
  B1.SOUND.FAILED_RETRY_KEEPER  the same bundle, registered in a fixture keeper (manifest, inventory, table, stage
                                records): custody must QUALIFY on a retry-bearing inventory (BX7).
  B1.SOUND.CHARGED_CHILDREN     MUTATION_CHILD rows (COMPLETED, INTERRUPTED) parented to the launch and a REFUSED
                                TOP_LEVEL attempt in the inventory: accounting rows are provenance (BX5). This is
                                the shape this packet's own mutation launch writes into rso/binding/LEDGER.jsonl.

BROKEN (must be rejected; an admission is a survivor):

  B1.BROKEN.SIBLING_UNREPORTED  a SECOND COMPLETED execution of the victim's node under the SAME launch, recording
                                the digest of a receipt that says PRESERVE FAIL, is in the inventory and not
                                presented; the presented receipt cites its own fully-bound PASS row.
  B1.BROKEN.NESTED_PARENT       the victim's own row names the launch's TWIN_EQ RECEIPT row as parent (depth 2).
  B1.BROKEN.CHILD_AS_NODE_RUN   the victim's own row has launch_kind MUTATION_CHILD.
  B1.BROKEN.LAUNCH_IS_NODE_RUN  the anchored manifest names the TWIN_EQ RECEIPT row as the launch; every other row
                                and run.json follow it; no TOP_LEVEL row carries that id.
  B1.BROKEN.LEGACY_ROW          the victim's own row has no receipt_sha256.
  B1.BROKEN.UNPARENTED_ROW      the victim's own row has no parent_run_id.

PROBE (recorded, never scored):

  B1.PROBE.PRODUCTION_RUNJSON   CC1's LAUNCH_SUBSTITUTION shape through s2_run.consumer_for (the production
                                consume path, which builds EV.Bundle without run_id) beside the fixture path.

Why SIBLING_UNREPORTED is the fresh broken case that matters: T011 declared "a second COMPLETED row of the SAME
node under the SAME anchored launch with the presented receipt's digest binds" (two rows, one receipt, ambiguity
of which row). This case is different: two rows with DIFFERENT digests, one receipt. The gate binds the presented
receipt to its row and never looks at the sibling, because BX5's RUN_UNREPORTED reads only required nodes WITHOUT
a presented receipt. A launch that ran a required node twice and reports the attempt it prefers qualifies. The
slice producer cannot produce this (its run id is <launch>/<node>, so a retry collides in the ledger); a native
runtime with retry or re-execution semantics can. The report states its applicability on that condition.

Why the other broken cases are predicted REJECTED and still in the set: each leaves exactly one BX1/BX2 dimension
wrong at the slice level (NESTED_PARENT and UNPARENTED_ROW the parent, CHILD_AS_NODE_RUN the kind,
LAUNCH_IS_NODE_RUN the launch's kind, LEGACY_ROW the digest). They are the end-to-end fire cases of edits E1-E4:
an edit that survives has no slice-level case pinning it, and these cases are the reusable fixtures that would.

## Edits (edits.json; on the binding path; each with a behavioural witness)

    id                      module    edit                                               witness original -> mutant
    ----------------------  --------  -------------------------------------------------  -------------------------------
    E1-parent-default       binding   a row with NO parent_run_id defaults to the         [BIND_FOREIGN_LAUNCH] -> []
                                      anchored launch (row.get(k, launch))
    E2-launch-kind-any      binding   the launch need not be TOP_LEVEL; any single row    [BIND_LAUNCH_MISSING] -> []
                                      with the manifest's launch id is the launch
    E3-child-as-node-run    binding   launch_kind MUTATION_CHILD may stand for RECEIPT     [BIND_NOT_A_NODE_RUN] -> []
    E4-legacy-row-accepted  evidence  g_inv ignores a why list equal to [DIGEST_MISSING]  (FAIL, RECEIPT_WITHOUT_RUN:..)
                                      (digest-less rows bind)                             -> (PASS, ..)
    E5-runjson-trusted      evidence  launch_unbound uses the bundle's run.json launch     (FAIL, LAUNCH_UNBOUND)
                                      when it names one, else the anchored one             -> (PASS, ..)

E1-E3 are placed on binding.py where the frozen unit suite (read; EXPOSURE.md) does not pin them: its
foreign-launch case sets parent_run_id explicitly, its launch cases test absent / unanchored / FAILED launches but
not a launch row of the wrong kind, and its kind case cites the TOP_LEVEL row, not a child. E4 and E5 are on the
slice's reading of the binding in evidence.py, whose tests were not read: E4 is the backward-compatibility hole
("a legacy row binds"), E5 is "the bundle picks its own launch" (BX1's whole point). Whether the slice suite kills
them is the first-sight question.

Execution plan: launch 1 run_cases.py (consumer-only: controls, 9 cases on 2 bases, 1 probe on the r1 base);
launch 2 run_mutation.py (targeted suite: binding tests + test_evidence, test_checker_render,
test_stages_evidence, test_ledger; survivors then against the FULL frozen suite, both acceptance suites, within a
30 CPU-minute allowance of this packet). Two of the three permitted launches; the third is held for a driver
repair rerun if one is needed, and otherwise not used. Both launches and every mutation child are charged to
rso/binding/LEDGER.jsonl (contract rso/binding/contract.json). No separate unchanged-suite launch: T020's CC2
regression and the mutation runner's own baselines stand for it; the acceptance command is run once more,
unledgered, on the merged tree before integration and reported in the receipt.

Dry check before this commit: none that touched a case. If run_cases.py --dry (controls only, no ledger row) is
used after this commit to shake out the driver, its rows file is committed beside the results and named in
REPORT.md.

## Predictions (written to be lost)

Cases. FAILED_RETRY: accepted, identical to baseline (the FAILED sibling has a distinct run id; nothing reads
it). FAILED_RETRY_KEEPER: custody QUALIFIED (launch_reasons sees one TOP_LEVEL row; the registered inventory blob
is the presented one). CHARGED_CHILDREN: accepted, identical (own_launch_rows filters launch_kind RECEIPT;
inventory_terminal counts RUN rows of any kind). SIBLING_UNREPORTED: ADMITTED on both bases (G-INV PASS,
CL-RET(REG) identical to baseline): the survivor of this set. NESTED_PARENT, CHILD_AS_NODE_RUN,
LAUNCH_IS_NODE_RUN, LEGACY_ROW, UNPARENTED_ROW: all REJECTED with exactly the predicted BIND_* reason, both bases.
Probe: the production path reports G-INV PASS and custody without LAUNCH_UNBOUND (bundle.run_id None); the
fixture path reports LAUNCH_UNBOUND; paths_agree false.

Edits. E1 KILLED by the slice suite (the R2-reviewer builders reused in CC1 append rows without binding fields,
and the stage fire record compares the BIND_* list; if it compares the reason string only, E1 SURVIVES). E2
SURVIVES the targeted suite (no case anywhere gives the launch id to a non-TOP_LEVEL row) and the full suite.
E3 SURVIVES both suites (no case cites a MUTATION_CHILD row). E4 SURVIVES both suites (every CC1 DIGEST_MISSING
occurrence is paired with FOREIGN_LAUNCH, so no case yields exactly [DIGEST_MISSING]). E5 KILLED (CC1
LAUNCH_SUBSTITUTION and TestBX1Launch expect LAUNCH_UNBOUND with the {anchored, presented} witness; under the
edit the reason becomes RECEIPT_WITHOUT_RUN or PASS). Predicted survivors: 3 of 5. Calibration: R2 predictions
were 5/5 on cases and edits; S4 4/4 cases, 2/3 edits.
