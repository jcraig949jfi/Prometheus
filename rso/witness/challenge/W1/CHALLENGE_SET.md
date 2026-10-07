# C-010-T014 W1 challenge set on FREEZE_W1 (committed before any outcome is observed)

Reviewer: Pallas[harry1-14289af6], claude-fable-5-1 (Q3), harry1 (M4), headless. Frozen surface: rso/witness/
FREEZE_W1.md (code 98345e104; 22 witness files + 11 dependencies); its 33 hashes and lengths were verified against
the committed LF blobs at HEAD 17b03160d before EXPOSURE.md (9b10d0b4d) was written. Branch pallas/c010-t014 from
17b03160d; claim 2ff41b5d9 on main. Exposure: EXPOSURE.md beside this file (test_evaluate.py and test_ares_client.py
WERE read in full; the other witness test bodies were not).

Packet rule (TASK.json; PREREGISTRATION s8): >= 1 sound, 2 broken, 2 semantic edits on the witness path, committed
before outcomes; synthetic or hand-wired organisms only; <= 2 launches on rso/witness/LEDGER.jsonl; CLOSED / NOT
CLOSED per surface; survivors with applicability to the registered witness run. Files: cases.py (fixtures and
constructions), expected.json (answer key and scoring rule), edits.json (6 edits), witnesses.py, run_cases.py,
run_mutation.py. Drivers may be repaired after this commit; the four data files (cases.py, expected.json,
edits.json, witnesses.py) may not.

## Where the set is aimed, and why these shapes

The frozen path has one trust boundary the contract names explicitly ("nothing a producer computed is trusted":
counts, decisions, outcomes are recomputed from bytes) and several it does not name. Reading the five modules
against PREREGISTRATION s3-s7, RULER.md and ERASE_PROBES.md, the places where the words and the code can come apart
are: (1) WHICH seeds a node ran on -- enforced for P-RET / P-CHAN when `--seeds` is passed, enforced for nothing
else; (2) WHICH episodes count -- the window is "after the LAST interrupt", pinned only by the ruler's own unit test,
never through the evaluator; (3) HOW MANY bundles may present a node -- P-FLAT refuses duplicates within a launch,
nothing refuses them across launches, and s10's "both are reported" invites exactly two; (4) WHAT a node id asserts
-- the evaluator builds ids from (digest, arm, predicate, world) but never checks a receipt's own fields against
the id it is filed under; (5) WHAT the one-step probes can see -- a one-episode delay line, declared out of scope by
ERASE_PROBES s1; (6) WHAT "no-carry" means for the NULL arm -- reset_each_step zeroes activations, not plastic W1.
The set puts one case on each, plus a sound end-to-end run of the honest driver at the registered n (the dry run
used tiny n, so the ruler was never reached on driver output), confirming tampers on that output, and six edits
that ask whether the frozen suites pin the same dimensions.

## Cases (expected.json has the full key; DA / DB are the evaluator's S4 / S15 ROLES on synthetic digests)

SOUND (must be accepted / read correctly; a false refusal or a false POSITIVE is a finding):

  W1.S1.DRIVER_END_TO_END     the real driver (temp ledger inside this challenge's launch), 3 launches, full
                              registered node map on two hand-wired / random organisms, seeds >= 5,000,000; fixture
                              keeper; evaluate at n = 2048 with registered_seeds. Expected: nothing refused, P-FLAT
                              PASS, custody QUALIFIED, every receipt binds, P-CAL evaluated, every subject gate
                              evaluated and a class present (values REDACTED in the rows).
  W1.S2.PRE_INTERRUPT_ONLY    correct at every step <= the last interrupt (the interrupt step's action is pre-reset),
                              abstain after: P-RET NEGATIVE, 0 correct, 0 wrong.
  W1.S3.MID_WINDOW            correct only between the first and the last interrupt, abstain after the last:
                              P-RET NEGATIVE, 0 / 0. (Witness of E1.)

BROKEN (must be refused / must fail; an admission is a survivor):

  W1.B1.DUPLICATE_NODE_ACROSS_BUNDLES   two completed, registered launches present the same node ids; DA's P-RET
                              is POSITIVE in one and NEGATIVE in the other. Both argument orders.
  W1.B2.P_CAL_SEEDS_UNREGISTERED        NULL / SHUF / POS on a different balanced 2048 list than the registered one.
  W1.B3.LEAKY_SUBJECT_PASSES_ERASE_ON_SAME_REGIME_TRIPLES   a hand-wired leaky runtime (SignLeakRuntime over the POS
                              carrier) as X on triples whose pre-episodes share a regime (D = 0 by construction),
                              the same runtime as X-LEAK on registered-shape triples (D > 0). A leak that passes
                              P-ERASE.
  W1.B4.TWO_BACK_LEAK_ESCAPES_ERASE_AND_PRES   construction only: a one-slot delay-line reset; both one-step gates
                              read 0, a three-episode probe shows the carry. The DECLARED escape of ERASE_PROBES s1,
                              demonstrated, with its applicability to S.Runtime stated from the code.
  W1.B5.NODE_ID_FIELDS_DISAGREE         DA's S/P-RET receipt says arm SHUF (shuffled-mode traces and oracle) and
                              genome DB under node id ares:<DA>:S:P-RET:W15.
  W1.B6.COUNTERFEIT_TRACE_FOR_BUNDLED_GENOME   a real canonical genome in subjects/, an always-correct trace it never
                              produced, everything consistent. Documented LIMIT (no replay registered), not a defect
                              claim; the case measures exactly what the evaluator does not read.
  W1.B7.STORAGE_TAMPER        four tampers on COPIES of S1's SA bundle: artifact contents swapped; manifest entry
                              pointing at another node's receipt (re-registered); inventory row digest edited
                              (original registered; and re-registered). Confirming cases on real driver output.
  W1.B8.NULL_ARM_IS_NOT_NO_CARRY        construction only: the POS carrier under arm NULL vs arm S, action equality
                              and W1 state. A semantic question about the registered P-CAL, not about code.

## Edits (edits.json; each with a behavioural witness in witnesses.py)

    id                                  module        edit                                            prediction
    ----------------------------------  ------------  ----------------------------------------------  ----------
    W1.E1-window-on-first-interrupt     evaluate      episodes(): max(steps) -> min(steps)            SURVIVES
    W1.E2-nopl-mutates-shared-subject   ares_client   arm('S-NOPL'): subject.copy() -> subject         SURVIVES
    W1.E3-run-unreported-dropped        evaluate      check_bundle: RUN_UNREPORTED check disabled      SURVIVES
    W1.E4-interrupt-before-step         ares_client   run_episodes: W15 reset applied before the step  KILLED (control)
    W1.E5-erase-pres-oracle-unchecked   evaluate      _check_oracle: P-ERASE / P-PRES branch returns   SURVIVES
    W1.E6-pcal-margin-two-sided         ruler         p_cal: x > k_neg -> x >= k_pos                   SURVIVES

Why these: E1, E3, E5, E6 are the four dimensions the evaluator / ruler suites (read: test_evaluate in full; test_ruler
by name) do not pin and each changes a registered rule's meaning (the window; BX5 on the witness path; the probe
oracle; the one-sided P-CAL margin, FD-T014-3). E2 is the one producer-side fault whose consequence is invisible in
every receipt field (the arm population's plasticity state is not recorded) and order-dependent in the driver. E4
is the control: the central W15 semantic is pinned by a test I read, and the set should show that pin firing.

## Execution plan

Launch 1 (W1-CASES, TOP_LEVEL on rso/witness/LEDGER.jsonl under contract.json): run_cases.py -- S1's three driver
launches on a TEMP ledger inside it (FD-W1-1: no "WITNESS:" launch of this challenge enters the campaign ledger),
then B7, S2, S3, B1, B2, B3, B5, B6, B4, B8; CPU charged as the process's CPU time, bytes as the scratch tree.
Launch 2 (W1-MUTATION, TOP_LEVEL): run_mutation.py -- baseline + 6 edits on the acceptance suites (witness 133 +
binding 21), each child a MUTATION_CHILD row charged its wall seconds, within a 20 CPU-minute allowance. Exactly the
two permitted launches. Pre-outcome check after this commit (unledgered, disclosed): run_cases.py --check-build
(builds the synthetic bundles and the S1 configs, verifies B3's two premises, calls NO evaluator).

## Predictions (written to be lost)

Sound: S1 accepted end to end; S2, S3 NEGATIVE 0 / 0. Broken: B1 ADMITTED, class follows argument order; B2
ADMITTED (P-CAL computed on the unregistered list); B3 ADMITTED (P-ERASE PASS, qualified); B4 escape confirmed
(TwoBack 0 / 0 / carry > 0; LeakyReset fires; Runtime 0); B5 ADMITTED; B6 ADMITTED (limit); B7 all four REFUSED;
B8 NULL(POS) == S(POS) action for action, W1 written. Edits: E1, E2, E3, E5, E6 SURVIVE the acceptance suites with
witnesses differing; E4 KILLED. Calibration ledger: S3/S4/R2 5/5, 4/4+2/3, 5/5; B1 9/9 cases, 5/5 edits (one
check-design error); B2 2/2 cases, 1/1 edit.

## Verdict rule for the report (fixed now; expected.json "verdict_rule")

evaluate.py CLOSED iff B1, B2, B5 refused and E1, E3, E5 killed. ruler.py CLOSED iff S2, S3 NEGATIVE and E6 killed.
ares_client node executions CLOSED iff E2, E4 killed and B4 confirmed unreachable under S.Runtime; B8 reported as a
semantic finding regardless. run_witness storage / inventory / seed refusals CLOSED iff S1 accepted and B7 all
refused. make_configs: read, not challenged (B2 shows what the evaluator cannot verify of its output). Every
survivor is classed behavioural / test-coverage / contract-vocabulary / contract-limit, with whether it bears on the
registered witness run. The report prints no accuracy, retention or ruler value of POS / NULL / SHUF / RECUR.
