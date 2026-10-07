# C-009-T030 CC3 independent challenge on FREEZE_B1 -- REPORT

Reviewer: Pallas, claude-fable-5-1 (Q3), harry1 (M4), headless. Two instances of the same seat on ONE lease:
Pallas[harry1-b97f1fc4] wrote and committed the set, repaired the drivers, ran launch 1 and started launch 2, then
ended its turn mid-run (a headless session exits when its turn ends; its mutation child died at about 03:47Z).
Pallas[harry1-2697f39e] resumed at 04:19Z (TASK.json history, state commit 3ed43a232), re-verified the freeze, ran
launch 3 and wrote this report. 2026-10-07. Frozen surface: rso/binding/FREEZE_B1.md (code 97606378c; rso/binding
v1.0.0 + the s6 v1.0.1 clarification); 48 hashes verified before the set was written (at 5fefee452, at 97606378c
and against the LF-normalised working tree) and again by the resumed instance at 04:20Z before launch 3 (48 equal,
0 mismatch). Branch pallas/c009-t030 from 5fefee452. Caveat printed with every closure record: cell member, writes
no production code, same vendor family as the builders (T010 claude-sonnet-5-5, T011 claude-opus-5-5, T020
claude-opus-5-5). Exposure: EXPOSURE.md beside this file (the binding unit test file was read by the set's author;
no file under rso/slice001/tests/ or rso/witness/tests/ was opened by either instance); the resumed instance's
additional reads are in s9.

## 1. Ordering evidence (git, all on origin/main unless marked; times UTC)

    4aaa10bbb  claim of C-009-T030 (CLAIMED, LEASE.json)                                   03:31:32Z
    1b9c19ba9  set: cases.py, expected.json, edits.json, witnesses.py, run_cases.py,
               run_mutation.py, CHALLENGE_SET.md with predictions, EXPOSURE.md               03:42:34Z
    dry check  run_cases.py --dry (controls only, no ledger row; permitted by CHALLENGE_SET)   03:43:02Z
               rows: dry_controls_2026-10-07T034302Z.jsonl. Found: on the SYNTHETIC base G-RECOMP
               fails on the fixture traces for every CL-RET claim, baseline included.
    9f58a0cef  driver repair (branch): synthetic-base claim-type checks written as unscored
               rows (the r1 base is fully scored); no data file touched                      03:44:10Z
    launch 1   run_cases.py      B1-CASES-20261007T034433Z-5432                       03:44:33Z-03:44:42Z
    launch 2   run_mutation.py   B1-MUTATION-20261007T034505Z-9944                    03:45:05Z-TORN
               children 001-003 COMPLETED (two baselines PASSED; E1 KILLED, 3 failures); child-004
               (E2) and the top-level row have START and no END: the ledger reads them INTERRUPTED,
               cpu uncharged. Rows kept, censored: mutation_rows_launch2_interrupted.jsonl
               (sha256 284da0f2cb9de08d...). Nothing from launch 2 enters the score.
    3ed43a232  state: IMPLEMENTING, history note "resumed by Pallas[harry1-2697f39e] ..."      04:25:20Z
    launch 3   run_mutation.py   B1-MUTATION-20261007T042220Z-7224, 10 children         04:22:20Z-04:42:16Z
    c5bb5675f  merge of origin/main 94f95e2d1 into the branch (rso/witness, ops, roles only; nothing
               under rso/binding or rso/slice001 changed upstream)
    (next)     results rows, ledger rows, this report, journal -- one commit on the branch; receipt and
               INTEGRATION_READY as state commits on main.

The four data files (cases.py, expected.json, edits.json, witnesses.py) are byte-identical to 1b9c19ba9
(`git diff --quiet 1b9c19ba9 HEAD -- <the four>`: identical). The packet's three permitted launches were all used:
1 (cases), 2 (torn), 3 (mutation re-run). Disposition of the torn launch, the resumed instance's call: keep it as
censored evidence (its three completed children agree with launch 3: the same two baselines PASSED, E1 KILLED
with 3 failures in both), do not append END rows the process never wrote, re-run the whole mutation driver as
launch 3 so that every edit row and every confirmation comes from one uninterrupted run. No separate
unchanged-suite launch: T020's CC2 regression and the runner's own baselines (199 tests PASSED in each of two
children) stand for it; the acceptance command ran once more, unledgered, on the merged tree c5bb5675f
(slice001: OK, skipped=1; binding: 13 OK) and is reported in the receipt.

## 2. Score (denominators are the set's: 3 sound, 6 broken, 5 edits, 2 controls; the probe is outside them)

Every case ran on two bases: r1 (the committed C-009 fresh produce rso/binding/R1/G0: real executions, 26-row
inventory, bound by the producer) and synthetic (fixtures.evidence_cases G0). The r1 base is fully scored. On the
synthetic base the claim-type checks measure G-RECOMP (which fails on the fixture traces, baseline included) and
were recorded unscored (driver repair 9f58a0cef, disclosed in s1); the line, witness_binding, identical and custody
checks there are scored and gave the same pattern as r1.

    r1 base        sound 2 of 3   broken 5 of 6   controls 2 of 2   probe 1 recorded, unscored
    synthetic      sound 2 of 3   broken 5 of 6   controls 2 of 2   (claim checks unscored, see above)

    SOUND  FAILED_RETRY          CORRECT   G-INV PASS; every decision byte-identical to the baseline (both bases)
    SOUND  FAILED_RETRY_KEEPER   INCORRECT under the committed rule; a correct ACCEPTANCE in substance (s3 BX7)
                                 custody QUALIFIED, CL-CUST(G0) ELIGIBLE/SATISFIED, CL-RET(REG) ELIGIBLE/SATISFIED
                                 all held; the "identical to the KEEPER control" check failed on all five listed
                                 claims. diag_keeper_output.txt walks every claim field by field: the ONLY
                                 differing field in each of the six decisions is $.custody.rows[2],
                                 RUN_INVENTORY:ab3f391f9220 -> RUN_INVENTORY:77bea84b1f6c (CL-CUST(G0) also in
                                 the fields derived from it). The retry-bearing inventory is a different
                                 registered blob by construction, and the custody object is embedded in EVERY
                                 decision, not only in CL-CUST(G0) as expected.json's note assumed. Reviewer's
                                 check-design error; the frozen code did what BX7 requires. Scored as written.
    SOUND  CHARGED_CHILDREN      CORRECT   G-INV PASS; identical to the baseline (both bases)
    BROKEN SIBLING_UNREPORTED    ADMITTED  the survivor of this set (s4)
    BROKEN NESTED_PARENT         CORRECT   RECEIPT_WITHOUT_RUN, binding [BIND_FOREIGN_LAUNCH]; other claims = baseline
    BROKEN CHILD_AS_NODE_RUN     CORRECT   RECEIPT_WITHOUT_RUN, binding [BIND_NOT_A_NODE_RUN]; other claims = baseline
    BROKEN LAUNCH_IS_NODE_RUN    CORRECT   LAUNCH_UNBOUND, binding [BIND_LAUNCH_MISSING]; custody why contains
                                           INVENTORY_UNBOUND:BIND_LAUNCH_MISSING (bundle-level, every G-INV line)
    BROKEN LEGACY_ROW            CORRECT   RECEIPT_WITHOUT_RUN, binding [BIND_DIGEST_MISSING]; other claims = baseline
    BROKEN UNPARENTED_ROW        CORRECT   RECEIPT_WITHOUT_RUN, binding [BIND_FOREIGN_LAUNCH]; other claims = baseline
    PROBE  PRODUCTION_RUNJSON    recorded  paths_agree false (s6)

    edits  proposed 5 | applicable 5 | duplicate 0 | executed 5 | killed 2 | survived 3 | equivalent 0 |
           unresolved 0 | error 0 | timeout 0 | cap not exhausted
           baselines (targeted suite, 199 tests): rso.binding.binding child PASSED 50.4 s; rso.slice001.evidence
           child PASSED 57.3 s
           E1 parent-default        KILLED    199 run, 3 failures (48.5 s)
           E2 launch-kind-any       SURVIVED  targeted 199/0 failures (73.2 s); FULL frozen suite 433 run, 0
                                              failures (276.3 s); witness DIFFERS: ['BIND_LAUNCH_MISSING'] -> []
           E3 child-as-node-run     SURVIVED  targeted 199/0 (53.3 s); FULL 433/0 (275.1 s); witness DIFFERS:
                                              ['BIND_NOT_A_NODE_RUN'] -> []
           E4 legacy-row-accepted   SURVIVED  targeted 199/0 (51.5 s); FULL 433/0 (271.8 s); witness DIFFERS:
                                              (FAIL, RECEIPT_WITHOUT_RUN:rcpt:REG:PRESERVE:STANDARD) ->
                                              (PASS, inventory terminal; every run reported)
           E5 runjson-trusted       KILLED    199 run, 5 failures (38.4 s)
           All three survivors are NOT_EQUIVALENT_WITNESSED.

Which suite killed E1 and E5 (diag_e1_binding_suite_output.txt; unledgered, disclosed, the runner's in-process
child per module): the 13-test binding unit suite -- the one file the set's author had read -- passes under BOTH
mutants (13 run, 0 failures each). E1 is killed by test_evidence (2 failures) and test_stages_evidence (1); E5 by
test_evidence (4) and test_stages_evidence (1). Both kills are first-sight results of the slice suite, not
reviewer errors (EXPOSURE.md's criterion).

Predictions (CHALLENGE_SET.md, written before any outcome): cases 9 of 9 on polarity (SIBLING_UNREPORTED
predicted ADMITTED, the other eight predicted as they fell, with the predicted BIND_* reason on every rejected
case); FAILED_RETRY_KEEPER's substantive prediction (custody QUALIFIED on a retry-bearing inventory) held while the
scored identical-check was wrongly designed; probe as predicted; edits 5 of 5 (E1 and E5 killed by the slice
suite, E2-E4 survive both suites). Calibration ledger: S3/S4/R2 5/5, 4/4+2/3, 5/5; B1 9/9 and 5/5, with one
check-design error.

## 3. CLOSED / NOT CLOSED per binding surface (FREEZE_B1's list: binding.py; evidence.py g_inv / launch_unbound /
custody; the producer side ledger.py + s2_bundle.py)

    BX1  launch identity (binding.launch_reasons; evidence.launch_unbound)
         NOT CLOSED. The frozen code refuses a RECEIPT row standing as the launch (LAUNCH_IS_NODE_RUN: LAUNCH_UNBOUND
         [BIND_LAUNCH_MISSING] on every G-INV line and INVENTORY_UNBOUND in custody) and the slice suite kills E5
         (the bundle picking its own launch). E2 -- the launch row need not be TOP_LEVEL -- survives all 433 frozen
         tests with a witnessed behavioural difference: nothing in either suite pins the KIND of the launch row.
         Class: a missing fire test, not a defect of the frozen code. The committed case B1.BROKEN.LAUNCH_IS_NODE_RUN
         is the reusable fixture that pins it.

    BX2  cited-row binding (binding.binding_reasons; evidence.g_inv's reading of it)
         NOT CLOSED. Four broken cases each leave exactly one BX2 dimension wrong and each is refused with exactly
         that reason (parent x2, kind, digest); the sound retry case binds identically to the baseline; E1 is
         killed. Two edits survive 433 tests, witnessed:
           E3 (binding.py): a MUTATION_CHILD row may stand for the node execution. Fire case: CHILD_AS_NODE_RUN.
           E4 (evidence.py g_inv): a cited row whose only failing reason is BIND_DIGEST_MISSING binds. Fire case:
              LEGACY_ROW. This is the consequential one: under E4 a digest-less row binds any receipt, so the
              receipt-edited-after-the-run shape (CC1 ARTIFACT_SWAP) is undetectable for such rows; CC1's
              ARTIFACT_SWAP has a digest that MISMATCHES, which is a different reason and still refused. binding.py
              keeps reporting BIND_DIGEST_MISSING; the client's "if why:" is what the edit weakens. Every CC1
              occurrence of DIGEST_MISSING is paired with FOREIGN_LAUNCH, so no frozen case yields exactly
              [DIGEST_MISSING]; LEGACY_ROW does.
         Class for both: missing fire tests; the frozen code refuses both shapes.

    BX5  own-launch rows and the unreported-run check (binding.own_launch_rows; g_inv RUN_UNREPORTED)
         NOT CLOSED: one behavioural survivor, B1.BROKEN.SIBLING_UNREPORTED, admitted on both bases (s4). The
         sound CHARGED_CHILDREN case (mutation children and a REFUSED attempt under the launch) is accepted
         identically to the baseline, so accounting rows are provenance as BX5 says.

    BX7  custody of the inventory (evidence.custody; keeper-registered RUN_INVENTORY)
         CLOSED within this challenge's coverage (one sound case, one broken custody check, no edit placed on
         custody): a registered inventory holding a FAILED first attempt QUALIFIES (FAILED_RETRY_KEEPER; the
         scored miss is the reviewer's identical-check, diagnosed to the embedded RUN_INVENTORY row id, s2); an
         inventory whose anchored launch is a RECEIPT row is INVENTORY_UNBOUND:BIND_LAUNCH_MISSING. No false
         rejection, no survivor on the surface.

    producer side (ledger.py + s2_bundle.py)
         UNCHALLENGED by this set: consumer-only cases and edits, by design (CHALLENGE_SET.md). The only evidence is
         the controls: the producer-bound r1 rows bind every receipt under the frozen consumer (CTRL.G0@r1 and
         CTRL.KEEPER@r1 4/4 and 3/3). Neither CLOSED nor NOT CLOSED can be claimed from this packet; T020's CC2
         regression is the record for it.

    production consume path (s2_run.consumer_for; on the consume path, outside FREEZE_B1's binding list)
         recorded, not scored (s6): the production path cannot raise LAUNCH_UNBOUND for a run.json substitution
         because it builds EV.Bundle without run_id.

CC3's registered closure condition (CONTRACT.md s3): "no unresolved applicable survivor on the binding path". This
challenge leaves, for adjudication:
  1 behavioural survivor         SIBLING_UNREPORTED on BX5 -- applicable CONDITIONALLY (s4: a runtime that gives
                                 re-executions of one node distinct run ids under one launch). NOT on the path the
                                 native witness as drafted would use (s5).
  3 witnessed edit survivors     E2 (BX1), E3 (BX2), E4 (BX2) -- test-coverage class: the frozen code refuses each
                                 shape; no frozen test pins it. Each has a committed fire case in cases.py.
  1 wiring gap (probe)           s2_run.consumer_for passes no run_id -- applicable to any consumer built from
                                 consumer_for or an EV.Bundle without run_id; not claim-critical by BX1's own
                                 reading (run.json is never authoritative), a self-inconsistent bundle merely goes
                                 unflagged on that path.
Whether the three edit survivors count as "applicable survivors on the binding path" for CC3 is the adjudicator's
(Palamedes and the operator); this reviewer's reading is that a witnessed edit that survives the full frozen suite
is unresolved by definition (mutation.py: only EQUIVALENT resolves a survivor, and a witnessed one cannot be
EQUIVALENT), so the condition is NOT met on the letter. The one repair round the contract allows (1+1+1) would be
small and would not touch production code for three of the four: add the committed fire cases (LAUNCH_IS_NODE_RUN,
CHILD_AS_NODE_RUN, LEGACY_ROW) to the frozen suites and E2-E4 die; decide BX5's rule for SIBLING (s4) and pass
run_id in consumer_for. A fresh re-check must then use new shapes, not these (they become T011's regressions).

## 4. The admitted sibling, in detail (rows: results_cases.jsonl, case_claims B1.BROKEN.SIBLING_UNREPORTED, both bases)

r1 base. The victim is REG's PRESERVE receipt; its own row g0-ce1f8716cc5d-14660/rcpt:REG:PRESERVE:STANDARD is
fully bound (parent = the anchored launch, kind RECEIPT, COMPLETED, exact node id, digest of the presented bytes).
The case inserts, directly after it, a second COMPLETED RECEIPT row of the SAME node under the SAME launch,
run_id ...~attempt2, recording the digest 614c870a229c3341... of a receipt that was NOT presented: the victim's
receipt with execution.run_id = that row and outcome PRESERVE FAIL (the FAIL outcome shape of ERASE(LAGD) with the
predicate id kept; it validated on both bases, hidden_sibling.how = FAIL_TRANSPLANT; synthetic digest
a3d2be078377dc53...). Inventory terminal count updated. The consumer: G-INV PASS "inventory terminal; every run
reported"; CL-RET(REG) ELIGIBLE / SATISFIED; CL-RET(PKTD), CL-RET(LAGD), CL-CAL(STANDARD), TWIN(REG) byte-identical
to the baseline -- the admission is the only effect. Custody is UNQUALIFIED here (KEEPER_ROW_MISSING on the
stage-rows-only store, as in every S3/S4/R2/B1 broken case), so by the v1.0.1 reading this is a logic result,
never qualified evidence; a REGISTERED inventory holding both rows would qualify just the same, because custody
checks the inventory's registration and launch binding, not how many executions of a node it holds.

Why the contract's letter admits it: BX2 binds the PRESENTED receipt to the row it CITES, and that row is sound.
BX5's RUN_UNREPORTED reads only required nodes WITHOUT a presented receipt; a node with a presented receipt is
never asked whether the launch also ran it again with another outcome. T011's declared escape covered two rows
with the SAME digest (which attempt is cited is then immaterial); this shape has two rows with DIFFERENT digests,
one of them never shown. The sound FAILED_RETRY case shows the honest version of the same structure (a FAILED first
attempt, no digest) and binds identically to the baseline, so a repair that says "every COMPLETED row of a presented
node under the anchored launch must be the cited one" (or "exactly one COMPLETED row per required node under the
anchored launch") separates them without touching FAILED retries. That is the shape a repair would have to take;
it is not asked for here.

## 5. Applicability to the path the native witness would use (rso/witness on origin/main 94f95e2d1; read by the
resumed instance after all outcomes were in)

The witness client as committed (rso/witness/ares_client.py, class Launch) writes one row per produce():
run_id = "<launch>/<node_id>", parent_run_id = the launch, launch_kind RECEIPT, status COMPLETED, receipt_sha256 of
the canonical bytes; rows() prepends the TOP_LEVEL launch row and appends the TERMINAL row. There is no retry or
re-execution path and no attempt suffix: a second produce() of the same node under one launch yields two rows with
the SAME run_id, which binding_reasons refuses as BIND_AMBIGUOUS_ROW. So:

    SIBLING_UNREPORTED   not reachable through the witness client as drafted; reachable by any runtime adapter
                         that gives re-executions distinct run ids (the thin-federation invitation of BX6 and the
                         contract's own "retries ... count" charging rule in contract.json make that a live shape,
                         not a hypothetical). Record as applicable-conditional.
    E2, E3, E4           the witness's bundles will be read by the same evidence.g_inv / binding.py; the surviving
                         edits describe gaps in what the frozen SUITE pins, and the code refuses the shapes, so
                         they bear on the witness only as unpinned behaviour (a later edit to binding.py or
                         evidence.py could introduce any of the three faults without a test failing).
    probe (consumer_for) applicable iff the witness driver (C-009-T016) builds its consumer from s2_run.consumer_for
                         or an EV.Bundle without run_id; PREREG_DRAFT s7 names rso.binding and CONTRACT s6, not the
                         consume path, so this is for the owning engineer.
    BX7 custody          the witness preregistration (s7) requires registered manifests and inventories and a
                         QUALIFIED custody for every witness claim; the one custody case here (a retry-bearing
                         registered inventory qualifies) is the sound direction and holds.

## 6. The probe, in detail (rows: results_cases.jsonl, row probe B1.PROBE.PRODUCTION_RUNJSON, r1 base)

CC1's LAUNCH_SUBSTITUTION shape (run.json names fixture-launch-SUBSTITUTE, present as a COMPLETED TOP_LEVEL row;
every receipt row bound to the anchored launch) consumed two ways. (a) s2_run.consumer_for exactly as
decisions_real does: bundle.run_id None, G-INV PASS, custody UNQUALIFIED by the three KEEPER_ROW_MISSING only,
CL-RET(REG) ELIGIBLE / SATISFIED. (b) an EV.Bundle built with run_id=SUBSTITUTE (the CC1 fixture path): G-INV FAIL
LAUNCH_UNBOUND, witness {anchored g0-ce1f8716cc5d-14660, presented fixture-launch-SUBSTITUTE, binding []}, custody
adds LAUNCH_UNBOUND, every G-INV claim UNMET. paths_agree false. T011's receipt (notes (1)) asked T020 to pass
run_id=g.run_id in consumer_for; the frozen s2_run.py does not. Not a CC1 regression (the fixture path is what CC1
tests) and not claim-critical by BX1 (the anchored launch is used either way; nothing is borrowed); a production
consumer simply never sees the bundle's own claim of its launch.

## 7. Per-surface components (for the C4-style records)

    surface                         sound c/t  broken c/t  probes adm/rec  edits: prop appl exec kill surv  open
    ------------------------------  ---------  ----------  --------------  ------------------------------  ----------
    BX1 launch identity             0/0        1/1         0/0             2    2    2    1    1           E2
    BX2 cited-row binding           1/1        4/4         0/0             3    3    3    1    2           E3, E4
    BX5 own-launch / unreported     1/1        0/1         0/0             0    0    0    0    0           SIBLING
    BX7 custody                     1/1 (*)    0/0         0/0             0    0    0    0    0           -
    producer (ledger/s2_bundle)     controls 2/2 only                                                      unchallenged
    consume path (consumer_for)     0/0        0/0         1/1             0    0    0    0    0           run_id wiring
    (*) FAILED_RETRY_KEEPER: correct acceptance; scored INCORRECT under the committed rule (s2).

## 8. Resources (rso/binding/LEDGER.jsonl; contract.json caps)

    launch 1  B1-CASES-20261007T034433Z-5432             COMPLETED      8.4 s
    launch 2  B1-MUTATION-20261007T034505Z-9944          INTERRUPTED    children 001-003 COMPLETED 143.2 s;
                                                                        child-004 INTERRUPTED (uncharged)
    launch 3  B1-MUTATION-20261007T042220Z-7224          COMPLETED      top-level 0.2 s + 10 children 1195.7 s:
              baselines 50.4 + 57.3; edits 48.5, 73.2, 53.3, 51.5, 38.4; confirms 276.3, 275.1, 271.8
    packet    3 of 3 launches; 1347.5 CPU-s charged of the 1800 s allowance run_mutation.py reserves for B1
    campaign  8 of 12 top-level launches; 1518.2 CPU-s of 5400 (25.3 of 90 minutes); artifact bytes unchanged
              at 13,381,360 (this packet wrote no artifacts to the ledger)
    reviewer  about 1.0 h of model time across the two instances (03:28-03:47Z, 04:19-05:00Z); the packet's
              ceiling is 1 h, the contract's 2 h
    unledgered, disclosed: the --dry controls check (1.4 s), diag_keeper.py (two runs, about 2 s each),
              diag_e1_binding_suite.py (10 in-process children, 71 s wall), the acceptance command on the merged
              tree (about 4.5 min).

## 9. Exposure additions by the resumed instance (after every case outcome was on disk; before launch 3)

Read: the wake prompt and launch note; the committed B1 set and drivers; results_cases.jsonl, the dry rows, the torn
launch-2 rows; rso/binding/CONTRACT.md, contract.json, binding.py in full; evidence.py g_inv and launch_unbound and
the function index; s2_run.consumer_for; ledger.py's run reconstruction; mutation.py run(); rso/witness file list,
ares_client.py lines 195-275 (class Launch) and PREREG_DRAFT.md s6-s9 (after launch 3 ended); the T011 and T017
receipts; workgraph/core.py (lifecycle and receipt fields). Not opened: any test body under rso/slice001/tests/,
rso/binding/tests/ or rso/witness/tests/; any T010/T011/T020 diff; the slice CONTRACT.md body. The diagnostic
diag_e1_binding_suite.py ran test modules; it did not display their source.
