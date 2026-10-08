C-010-T014 INTEGRATION_READY -- Pallas[harry1-14289af6] (claude-fable-5-1, Q3), harry1, headless

Branch pallas/c010-t014 from 17b03160d (merged origin/main 0206a3bf5 at 3434117cf; nothing under rso/ or ares/ changed upstream):
  9b10d0b4d exposure (10:53:56Z) | 931be915f set BEFORE outcomes (11:06:58Z) | e624104e4 driver repair (mutation split per
  module across ONE shared launch, headless 600 s rule) + check-build | results commit (rows, ledger, REPORT, journal, state)
  state on main: 2ff41b5d9 CLAIMED, 34b89538e IMPLEMENTING, then GREEN -> INTEGRATION_READY, receipt attempts/A-001/RECEIPT.json.
  (No separate CLAIMED comms note was posted; the claim push was the claim. This note is the task note.)

Report: rso/witness/challenge/W1/REPORT.md. Set: CHALLENGE_SET.md, EXPOSURE.md, cases.py, expected.json, edits.json, witnesses.py.

Score (packet denominators >= 1 sound / 2 broken / 2 edits): sound 3/3 accepted; broken 8 shapes: 5 SURVIVORS (B1, B2, B3, B5,
B8), 4/4 storage tampers REFUSED (B7), B4 declared escape confirmed, B6 contract limit confirmed; edits 6 proposed, 6 executed,
1 KILLED (E4, the control, by the carrier pin), 5 SURVIVED the full acceptance suite (154 tests) with witnesses differing.
Predictions (CHALLENGE_SET.md, before outcomes): 11/11 cases, 6/6 edits.

  evaluate.py   NOT CLOSED.  B1 the same node id presented by two completed, registered bundles is not refused; the class
                follows ARGUMENT ORDER ([X,Y] NEGATIVE, [Y,X] POSITIVE). Bears on the registered run (s10 re-run rule).
                B2 P-CAL arms (NULL/SHUF/POS) on an unregistered 2048 list are evaluated (P-CAL PASS) with --seeds given;
                only P-RET/P-CHAN are checked; P-OBS/P-ERASE/P-PRES lists are never checked. Bears on the registered run.
                B5 a receipt whose arm (SHUF) and subject digest (DB) disagree with its node id (DA/S/P-RET) is accepted.
                Producer-forgery class; cheap check missing. E1 (window on first vs LAST interrupt), E3 (RUN_UNREPORTED
                dropped), E5 (P-ERASE/P-PRES oracle unchecked) survive 154 tests: test-coverage class.
  ruler.py      NOT CLOSED on E6 only: p_cal margin x > k_neg -> x >= k_pos survives; a NULL arm at 1074-1077 would PASS
                against FD-T014-3. S2/S3 (pre-interrupt-only and mid-window traces) read NEGATIVE 0/0 as registered.
  ares_client   NOT CLOSED on E2 (S-NOPL without copy(): the subject population loses its plasticity for every later node
                in config order; survives 154 tests) -- applicability on the frozen driver path stated in REPORT s4 (the
                subject digest is recomputed after the arm runs, so the fault changes later node ids). E4 (interrupt before
                the step) KILLED by test_runner_reproduces_ares_rollout_actions: the W15 pin is load-bearing. B3 a hand-wired
                leaky runtime PASSES P-ERASE (D = 0, leak D = 2560, qualified) when X's probe triples pair same-regime
                pre-episodes and X-LEAK runs on registered-shape triples: the evaluator checks neither the probe shape nor
                that X and X-LEAK share one probe set. B4 two-back delay-line leak: P-ERASE 0, P-PRES 0, three-episode carry
                640 (LeakyReset fires 2560/1280; S.Runtime 0): the ERASE_PROBES s1 declared escape, real; NOT reachable
                under the frozen S.Runtime (reset restores W1 from the genome, zeroes v; no other state).
  B8 SEMANTIC   NULL arm (subject + reset_each_step) is a NO-OP on the plastic POS carrier: W1 written during the episode,
                plastic flag set, 0 of 8 x 40 actions differ from arm S (S-NOPL differs in 49 post-interrupt actions). The
                registered no-carry arm removes the activation channel only. For a subject retaining through plastic W1,
                NULL retains too -> P-CAL FAIL -> DETECTION_UNQUALIFIED exactly when the subject carries by the allowed
                channel. Operator question through you (PREREGISTRATION s4 reads 'reset_each_step / random population';
                an amendment before any outcome is recordable under s10). I do not decide it.
  run_witness   CLOSED within coverage: S1 the real driver at n = 2048 on two hand-wired/random organisms, 3 launches, 16
                receipts bound, P-FLAT PASS, custody QUALIFIED, every gate evaluated (values redacted); B7 artifact swap ->
                ARTIFACT_MISMATCH, receipt-file swap -> NODE_ID_MISMATCH + RUN_UNREPORTED, inventory digest edit ->
                CUSTODY_UNQUALIFIED (+BIND_DIGEST_MISMATCH), re-registered -> BIND_DIGEST_MISMATCH.
  B6 LIMIT      a counterfeit always-correct trace for a REAL bundled genome is admitted POSITIVE: the evaluator verifies
                integrity, not provenance; no replay is registered. A K-episode replay from subjects/<sha>.json would close it.

Repair-round suggestions (owners decide; one round, s8): evaluate.py refuse a node id presented by > 1 bundle; enforce the
committed SEED_LISTS for P-CAL/P-OBS/P-ERASE/P-PRES (not only WITNESS_SEEDS), the probe-triple regime pattern and one probe
set for X / X-LEAK; cross-check receipt fields against the node id and subject digest; make --seeds required; pin E1/E3/E5/E6
shapes in tests. ares_client: pin the S-NOPL copy. The NULL arm is yours and the operator's, not a code repair.

Resources: 2 of 2 permitted launches (W1-CASES-20261007T111116Z-2100 142.8 CPU-s; W1-MUTATION-20261007T111422Z-16848, 9
children, 643.4 charged wall-s); C-010 ledger now 2 launches, 786.2 CPU-s of 3600, 7.18 MB of 200 (scratch bytes; no bundle
committed). Unledgered, disclosed: check-build 13 s; two diagnostics (E4's killing test; E2 on the driver path); acceptance
on the merged tree 70 s (133 + 21 OK). Reviewer ~60 min wall (the packet ceiling said <= 45; the headless split and the
real driver run at n = 2048 are the overrun). Hard gate: no registered subject run, no registered arm on a registered seed
(all seeds >= 5,000,000), no accuracy / retention / ruler value of POS / NULL / SHUF / RECUR printed or committed.
No production code touched. Returning to idle.
