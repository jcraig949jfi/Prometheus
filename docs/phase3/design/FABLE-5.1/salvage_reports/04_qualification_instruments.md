# Salvage worker report: scope 4, qualification instruments and failure fixtures

Deposited by Dionysus[m1-3815a3b9] on 2026-10-01. Extracted by script
(process/deposit_worker_reports.py) from the coordinator's session transcript:
the worker's final message, recorded 2026-10-01T15:35:34.938Z. The text is the worker's,
unchanged except that XML escapes from the notification wrapper are undone
and trailing whitespace is stripped; one sentence is redacted (see the note below).

The same worker sent an earlier message (2026-10-01T15:26:54.203Z). This one
replaced it after the coordinator's search-rule correction. The earlier text
is not deposited.

Brief: roles/Dionysus/prompts/2026-10-01_salvage_workers/00_COMMON.md and
04_SCOPE_qualification_instruments.md. Worker model: opus, read-only.
Worker usage as reported by the harness: 569,088 tokens, 210 tool uses, about
39.3 minutes (totals for the worker, all messages).

Redaction. One of this worker's searches printed one line of a holdout file
(the brief's exclusion pattern covered directories only; the fault is the
coordinator's). The worker reported it and described the row in one sentence.
That sentence is replaced below by a marker so the description does not enter
a tracked file. Path and line number are kept. See 00_SEARCH_RULE_INCIDENT.md.

This is a worker's fact sheet. Its claims are the worker's, graded by its own
VERIFIED BY ME lines. Where SALVAGE_MATRIX.md relies on one, it says so.

----------------------------------------------------------------------

===BEGIN REPORT===

SALVAGE FACT-FINDING, SCOPE 4: QUALIFICATION INSTRUMENTS AND FAILURE FIXTURES

Worker: read-only fact-finder for Dionysus, worktree dionysus-base-role at e3d7c7034. The only things I ran were read-only git commands, wc, grep, and Python one-liners that read JSON. No test suite and no script was run. Every "N tests" figure below counts "def test_" functions in the source; parametrised tests expand further. "Code-inferred" means I read the code but did not run it.

----------------------------------------------------------------------
COMPONENT: Charon C1/C2 executable checks (c1c2_checks)
PATHS: charon/probe/c1c2_checks.py; charon/probe/tests/test_c1c2_checks.py; charon/probe/c1c2_gate_fire_2026-09-11.py and .json
OWNER / DATES: Charon. Single commit 5af5e5562, 2026-09-11.
WHAT IT REALLY DOES: C1 hashes each input pool itself (sha256 of LF-normalised bytes, plus a count of non-blank lines). It FAILs a receipt that omits a fingerprint, quotes one that differs from the bytes, or differs from the preregistration. C2 lists the rep-1 rows whose status is not "ok", runs a loader supplied by the caller, and FAILs if any such row is admitted; it judges per row (seq), not per uid. A third check FAILs any receipt that does not carry earlier PASS verdicts for C1 and C2.
SIZE: 394 lines. 17 tests. 7 Keeper cases in engine/necropolis/workshop/tests/cases_e.py.
DEMONSTRATED CORRECTNESS:
- The tests make every check FAIL. Examples: a receipt that copies the preregistered sha over changed bytes; a naive loader that renders a planted 504.
- They get INDETERMINATE in three cases: a loader that admits nothing; no failed row (NOTHING_COULD_HAVE_FIRED); a uid shared between rows with no seq (UNATTRIBUTABLE).
- Live gate-fire FAILed both blocks: 6/6 and 55/55 failed rows rendered; the planted copy 56/56.
- Aporia re-ran it: 17 passed, gate-fire reproduced (71403839d). Keeper: 7 PASS.
- Defects (code-inferred): a malformed record_count raises instead of FAILing; verdicts are strings, not an enumeration.
INTERFACE: Importable library. Inputs are a receipt dict, pool paths and a loader callable. Output is a Verdict dataclass: verdict, reasons, rows, eligible_count, fired_count, checks_version. Verdict type is PASS/FAIL/INDETERMINATE, and the reason string separates "nothing could have fired" from "loader admits nothing". Deterministic; hashes and integers only; no model call.
THROUGHPUT / SCALE: Not recorded (pools of 415 and 534 rows).
COUPLING: Stdlib only. The row schema (rep/uid or key, status) is hard-coded. Imported only by its own test, the gate-fire script and Necropolis.
FIT TO SLOT: VERDICT TYPE.
- Meets SCI-02's own check word for word (a loader that admits nothing gets INDETERMINATE) and carries SCI-02's counts. C1 meets PROV-02's normalisation and is a REPR-05 pattern for inputs.
- Detects T03, T12, T19 and T23 by existing fixtures.
- Missing: the apparatus labels of section 1.2, a ruler hash (MEAS-06), denominator and exclusion fields (MEAS-09).
MODIFICATION COST: S (enumeration, labels, hash, schema parameters). Rebuild: S. The tests are the real asset either way.
VERIFIED BY ME: All of the above in source and JSON, except the Aporia re-run, which I took from its commit text.

----------------------------------------------------------------------
COMPONENT: Charon exit-review-3 arm-leak classifier (plus the independent gate-fire of 08-25)
PATHS: charon/probe/exit_review_3_attack.py; charon/probe/exit_review_3_evidence.json and _LIVE.json; charon/probe/TIER_A_EXIT_REVIEW_3_CHARON_2026-08-21.md; charon/probe/charon_gate_fire_2026-08-25.py and .json
OWNER / DATES: Charon. 574c86447, 2026-08-23 (one commit). Gate-fire 2026-08-25.
WHAT IT REALLY DOES:
- Renders all six arms through ergon.probe.campaign and strips content: alphanumeric runs become W/N, or characters become a/9.
- For each of 15 arm pairs, fits a logistic classifier on character 1-4-gram TF-IDF plus 21 non-content counts, with 3-fold GroupKFold by task. Also reports whether the stripped strings are exactly disjoint.
- A 10-refit permutation null runs only when accuracy is below 0.999.
SIZE: 248 lines, no tests. The gate-fire is 180 lines with 9 worlds.
DEMONSTRATED CORRECTNESS:
- The positive control cannot fail. Lines 233-238 add a trailing space to F-answer and compare it with F0 (the code comment says F-null).
- F0|F-answer is already separable at 1.0000 (separable_exactly true) in every recorded state before anything is planted. The ruling's own table lists "all 14 other pairs 1.0000".
- The decisive matched pair sat at 0.5000 (null mean 0.4829).
- The separate gate-fire does not import Ergon's tests. It plants per-arm one-character leaks (trailing space, homoglyph, zero-width space); each fired 40/40, while the clean W0 world and the arm-invariant W3 world stayed silent.
INTERFACE: A script bound to the probe's arm names and campaign module, not a library. Verdict type: an accuracy figure plus a boolean, with no "could not fire" outcome. Floats; sklearn; seed 20260823; no model call.
THROUGHPUT / SCALE: Not recorded (240 tasks subsampled).
COUPLING: ergon.probe.campaign (it monkeypatches C.DIR), sklearn, scipy.
FIT TO SLOT: QUALIFICATION GATE / WLD-05 leak probe. As built it fails WLD-05's "planted one-character leak is caught" check, and MEAS-07. The gate-fire worlds do meet WLD-05's check for one packet invariant and are good T01 fixtures.
MODIFICATION COST: M (extract pair_attack, plant on a matched pair, exact permutation counts). Rebuild: S.
VERIFIED BY ME: The code, both evidence JSONs, ruling lines 55-140, and the gate-fire JSON.

----------------------------------------------------------------------
COMPONENT: R7 identity-null calibration and the three-valued band rule
PATHS: ergon/probe/f_null.py (calibrate_tolerances, classifier_auc, r7_verdict); charon/probe/run_r7_verification.py and r7_verification_2026-08-16.json; ergon/probe/chain_run.py (classify); ergon/probe/tests/test_f_null.py and test_gates_fire.py
OWNER / DATES: Charon, with the code in Ergon's tree (per the dossier). f_null.py 2026-08-16 (afd5913c0, 1c3b4b4e5).
WHAT IT REALLY DOES:
- R7(a) draws 200 pairs of disjoint samples from one pool, renders both through the production assembler, and freezes the p95 of each of 12 divergences plus the family-wise exceedance rate. A null passes if its own exceedance rate is not higher.
- R7(b) is the cross-validated balanced accuracy of a logistic model, with a ceiling of 0.55.
- The band rule labels an interval IN-BAND, OUT-OF-BAND or UNDECIDED against [0.35, 0.60].
SIZE: f_null.py 731 lines with 27 tests. The runner is 188 lines. classify is 6 lines.
DEMONSTRATED CORRECTNESS:
- D3 result: R7-PASS (exceedance 0.15 against a calibrated 0.315; balanced accuracy 0.5125 on 40+40 texts). The tests show layer (b) firing on obviously different texts.
- Defect: classifier_auc returns passed=True when an arm has fewer than 2 samples, and a test asserts exactly that.
- Defect (code-inferred): r7_verdict passes an empty balance list.
- Defect (code-inferred): a 0.55 ceiling on 80 texts is about one standard error above chance (MEAS-08).
- Defect (dossier): R7 validated a .text/.text renderer while .body/.text was deployed (T23).
- The band rule's only test recomputes the verdict inline and never calls chain_run.classify.
INTERFACE: Bound to ergon.probe types, not a library. R7's verdict is a two-valued string (R7-PASS / R7-FAIL-* / INADMISSIBLE-*) with no INDETERMINATE. The band rule is three-valued. Floats; seeded.
THROUGHPUT / SCALE: Not recorded.
COUPLING: ergon.probe.assemble; pivot/probe_d3_pool_2026-08-16.jsonl.
FIT TO SLOT: QUALIFICATION GATE, as a method for measuring a false-positive rate against a same-distribution reference (MEAS-01). Detects T05 (null build #1, 0.662). Fails SCI-02, MEAS-07 and MEAS-08.
MODIFICATION COST: M. Rebuild: S.
VERIFIED BY ME: Code, tests and result JSON. The T23 instance is from the dossier.

----------------------------------------------------------------------
COMPONENT: Nemesis cheatlib and the NEMESIS-01 protocol
PATHS: roles/Nemesis/science/cheatlib.py; roles/Nemesis/science/tests/test_cheatlib.py; roles/Nemesis/attacks/2026-09-11_eos_intake_gate/ (PREREGISTRATION.md, attack.py, results*.json); roles/Nemesis/attacks/2026-09-11_eos_gate_repaired/reattack.py
OWNER / DATES: Nemesis. The prereg is 73e6f46c1 (2026-09-11 13:15). The library, its 12 tests, the attack and its results came together in 72bf820ab (13:29). No change since.
WHAT IT REALLY DOES:
- Three incapable responders: a constant; the most common correct answer; an accessor that reads a field carried beside the item.
- chance_floor (majority rate and uniform rate) and score_responder (hits over eligible).
- Four forgeries: an existing path chosen without reading it, a token lifted from a file, filler text, a marker guaranteed absent.
- A greedy shrink of a fraud that crosses the gate, run to fixpoint.
- attack.py runs assert_builder_built_something before Eos's gate sees anything.
SIZE: 300 lines with 12 tests. attack.py 318 lines; reattack.py 66.
DEMONSTRATED CORRECTNESS:
- Negatives: a constant scores 0.01 on 100 distinct answers. Positives: the payload reader scores 40/40; the majority responder 0.70. The shrink reaches the known minimum of 5 from 40; its first version stopped at 28 (docstring).
- The cheat fixture pins 0.674 on the April ledger.
- Defect: the pinned "292 of 294" counts missing evaluations as wrong (crawl item 10), and the test freezes that number.
- Defect (code-inferred): run() reports rate 0.0 for an empty population.
INTERFACE: Generic library. It has no verdict type; empty populations raise ValueError. Rates are floats. The tests run git show and git grep --cached over the whole tree.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Stdlib. The attack imports Eos's intake module and archaeon.workspace.
FIT TO SLOT: TRIVIAL RESPONDERS.
- Meets MEAS-04 for the constant, majority and payload-reader responders. Detects T01, T05 and T08 by existing fixtures.
- Missing: a lookup responder, enforcement of the same population and denominator, integer rates, and the WLD-03 ladder rungs.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: All source. The numbers 0.674 and 292 were read from the test text; I did not run the tests.

----------------------------------------------------------------------
COMPONENT: Harmonia AP-1.1.0 audit primitives, STANDING_RULES F1-F8, VACUOUS_READINGS register
PATHS: roles/Harmonia/qualification/primitives/audit_primitives.py and tests/; roles/Harmonia/STANDING_RULES.md (section F); roles/Harmonia/VACUOUS_READINGS.md
OWNER / DATES: Harmonia[m2-475d761f]. AP 2026-09-30 (db6897ecf, 8819423e4). Rules and register 2026-09-17..09-30.
WHAT IT REALLY DOES:
- reachability: lists the gated labels that no input in a declared design space can reach.
- absence_control: requires a calibration item that expects the label and got it.
- baseline_gaming: runs a frozen rule on committed baselines that lack the construct.
- ceiling: flags a clause that sits within one margin of the scale maximum.
- null_pass_binomial: the binomial tail.
- freeze_precedes: asks git whether the commit that first added the plan strictly precedes the commits that first added the results.
SIZE: 209 lines with 9 tests. STANDING_RULES.md 366 lines. The register is 81 lines (V-001..V-008).
DEMONSTRATED CORRECTNESS:
- RA to RD each fire on a real defect from 09-30: Tyche v0 H1 at 3 valid worlds; a gravity calibration with no UNFAMILIAR item; lookup baselines (AUC 0.844 and 0.852) passing Hecate's novelty rule; Odysseus S3 at 9.1 of 10. Each is quiet on a clean twin.
- freeze_precedes flags the real Ananke W-O plan and passes a clean twin.
- Defect: the ablation helper chk forces flag=False, so "the defect escapes when disabled" cannot fail.
- Defect: freeze_precedes ignores git return codes and looks only at the plan's first add.
- Fixture numbers are hand-transcribed. F7 and F8 are reading-only rules.
INTERFACE: Library. Outputs are boolean flags, not three-valued. reachability does name unreachable labels. Floats; uses git.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Stdlib and git only. No code imports it apart from its tests.
FIT TO SLOT: PREREG/FREEZE CHECKS (the core of SCI-03's attainability, and PROV-06), plus helpers for the QUALIFICATION GATE (MEAS-08, WLD-03). Detects T03, T04, T08, T11, T12 and T15. Missing: three-valued output, receipts, exact rationals.
MODIFICATION COST: S. Rebuild: S, keeping the fixtures.
VERIFIED BY ME: Code, tests, section F of STANDING_RULES, and the head of the register.

----------------------------------------------------------------------
COMPONENT: Harmonia qualification library (QR-1.2.1, AF-1.1.0, Campaign 1 HA-1.0.1) and its defects
PATHS: roles/Harmonia/qualification/h0h5/ (qualification_rules.py, adversarial_fixtures.py, h1h0_phase2_analysis.py, tests/); roles/Harmonia/qualification/campaign1/; roles/Harmonia/qualification/t3_strict_cutover_rehearsal.py
OWNER / DATES: Harmonia. QR dd38720c0, 2026-09-09..09-18. HA a88410dde, 2026-09-28.
WHAT IT REALLY DOES:
- QR validates lane plans and decides each contrast as SUPPORTED, UNSUPPORTED, INCONCLUSIVE or INELIGIBLE. INELIGIBLE means the sign-flip lattice cannot reach alpha. Gate.eligibility prints NOTHING_COULD_FIRE.
- AF generates nine defective run records together with their detectors.
- HA is a toy in-process world plus adjudicate(). adjudicate() refuses a verdict supplied from outside, rows that do not match the manifest hash, and analysis code that does not match the preregistered hash.
SIZE: h0h5 has 2,505 lines across 8 modules with 33 tests. HA is 473 lines with 6 tests.
DEMONSTRATED CORRECTNESS: The plan refusals and the clean twins of AF F7-F9 are real; adjudicate's A1-A3 refusals are tested. Defects I verified in source:
- t_crit takes the next tabulated df (df 11 uses 2.179).
- With 3 or more primaries it uses the 0.025 quantile while alpha_used is alpha/3.
- eligibility tests against alpha but decide() tests against alpha/n: 6 blocks with 2 primaries gives 0.03125 > 0.025.
- The HA ablation returns [] (lines 320-321), and a test asserts the result.
- The h1h0 NEGATIVE control is "pass": True (line 268).
- The t3 rehearsal records "n/a" as pass (lines 84-86).
INTERFACE: Library. INELIGIBLE and INCONCLUSIVE are distinct outcomes. Floats.
THROUGHPUT / SCALE: Not recorded. Per the dossier, it never governed a confirmatory run.
COUPLING: archaeon.workspace (h1h0 only). HA is self-contained.
FIT TO SLOT: VERDICT TYPE (decide), and MEAS-11/REPR-05 (adjudicate is the only fixture in the tree where an outside verdict is refused). Fails MEAS-07 and MEAS-08.
MODIFICATION COST: M. Rebuild: S for decide() and adjudicate().
VERIFIED BY ME: The lines cited. AF clean-twin coverage is partly from the dossier.

----------------------------------------------------------------------
COMPONENT: Harmonia emission-path census and evidence audit by re-execution
PATHS: harmonia/diagnostics/detector_band_audit.py; roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30*.md and RULER_QUALITY_2026-09-30.md
OWNER / DATES: Harmonia. Census 7ad201fb3, 2026-08-19. Audits 2026-09-30.
WHAT IT REALLY DOES:
- The census runs every Theseus generator, classifies the emitted records against F2's predicates, and counts the generators whose records all carry a verdict at the moment of emission (self-verdicted).
- A test requires the self-verdicted share of lifetime records to stay above 0.95. Positive control a1 and cheat control a3 are asserted in code.
- The evidence audit is a procedure, not code: agents re-execute committed analyses, check freeze-before-result in git, and Harmonia re-verifies MAJOR findings.
SIZE: 356 lines with 4 in-module tests. The audits are 485 lines of prose and no code.
DEMONSTRATED CORRECTNESS:
- The census controls are asserted in code. The 99.98% figure (658,302,367 of 658,454,531) is from the taxonomy; I did not recompute it.
- Audit: of 5 packages, 4 were SUPPORTED_WITH_DEFECTS. It missed its own F1 rule once (C-2, d3f99cfdc). It has never been calibrated on planted defects.
INTERFACE: The census is a CLI bound to Theseus. Its verdict is a label per generator.
THROUGHPUT / SCALE: Not recorded.
COUPLING: theseus.generators, theseus.scoring.content_aware_promote, harmonia.experiments.verifier_lens.
FIT TO SLOT: FAILURE FIXTURES (a T02 detector), Theseus only. If MEAS-11 is enforced by write permission in the kernel, the census becomes unnecessary.
MODIFICATION COST: XL to generalise. Rebuild of the check itself: S.
VERIFIED BY ME: Census source and the audit summary. The figures are from the taxonomy.

----------------------------------------------------------------------
COMPONENT: Techne modal-collapse synthetic null with learnability check
PATHS: prometheus_math/modal_collapse_synthetic.py and modal_collapse_continuous.py; prometheus_math/tests/test_modal_collapse_*.py; prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md
OWNER / DATES: Techne (an Aporia diagnostic). 2026-05-04 (cda018015, 1b1f0c668).
WHAT IT REALLY DOES:
- A synthetic world y = w.x + b + noise, binned into 21 cells, with reward 100 or 0. It is trained with byte-for-byte ports of the real environments' random, REINFORCE and PPO trainers, over 4 variants and 3 seeds.
- The verdict (A/B/C) compares V3 accuracy with random at 2x and 4x and requires at least 8 active bins.
- The learnability check exists only as a test: least squares must reach at least 60% on V3.
SIZE: 755 + 642 lines, with 16 + 15 tests.
DEMONSTRATED CORRECTNESS:
- The least-squares test is a positive control for the world.
- Reported: REINFORCE 4.91% against random 4.84%; the six-domain claim was retracted (7339269a1).
- No positive control for the trainers. The learnability result is not an input to the verdict function.
INTERFACE: Bound to RL trainers. Verdict values are A/B/C/indeterminate. Floats; seeded.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Mirrors the constants of the modular_form and bsd_rank environments.
FIT TO SLOT: QUALIFICATION GATE as a pattern only: a null world with a demonstrated solver, nearer to WLD-08 and SRCH-02. Detects T08 and T13. Fails SCI-02 and MEAS-07.
MODIFICATION COST: L. Rebuild: S.
VERIFIED BY ME: The verdict code and the test lines. The result numbers are from documents.

----------------------------------------------------------------------
COMPONENT: Techne F2 planted-relation promote gate and promotion replay audit
PATHS: theseus/scoring/content_aware_promote.py; theseus/scripts/calibration_v0_murasugi.py, calibration_v1_ec_torsion.py (and v2, v3, v3c); theseus/scripts/promotion_replay_audit.py; tests in theseus/tests/
OWNER / DATES: Techne. F2 2026-05-30..06-09 (7637b7f42, 962012725). Replay 2026-06-23 (b092b86ac, 1f86b2590).
WHAT IT REALLY DOES:
- F2 score = |observed - null|. "observed" is whether the relation holds on the record's own values; "null" is the fraction of 1,000 random pairs drawn from the same value pools that satisfy it. Threshold 0.10.
- The calibration scripts plant true relations and decoys.
- The replay rebuilds each batch's historical shape-promoted set and re-runs F2 on it.
SIZE: 330 lines with 20 tests. Calibration scripts 705 + 445 lines. Replay 531 lines with 9 tests.
DEMONSTRATED CORRECTNESS:
- Tests calibrate on a true planted relation and on a random marginal.
- Per the dossier, the replay showed that promotion was shape-only and the 2,351 count is not reproducible.
- Defects (code-inferred): empty pools, unparsable payloads and exceptions all return 0.0; the default rng is unseeded.
INTERFACE: Bound to TheseusRecord. Two-valued (score against threshold). Floats.
THROUGHPUT / SCALE: The replay streams a corpus of about 362 GB (docstring). No timing recorded.
COUPLING: theseus.emit and theseus.generators; the corpus is host-local.
FIT TO SLOT: FAILURE FIXTURES only: T02/T14 cases, plus a design for planted-relation calibration. Fails SCI-02 and MEAS-07.
MODIFICATION COST: XL to reuse. Rebuild of the pattern: S.
VERIFIED BY ME: The score function, the threshold and the test names. The outcomes are from the dossier.

----------------------------------------------------------------------
COMPONENT: Techne fossil hash preservation and FOSSIL_PACKET validator
PATHS: techne/fossils/record.py, harvest.py, packet.py; techne/tests/test_fossil_*.py (20 files)
OWNER / DATES: Techne. packet.py and record.py 2026-09-12..09-25 (11 commits).
WHAT IT REALLY DOES:
- Preserves software bodies with upstream and tree hashes, receipts and pins.
- packet.validate checks only that fields are present, that two hashes are 64 hex characters, that values are in the vocabulary, that the world-id prefix is right, that the capability matrix equals WORLDS.json, the copy count, and that receipt paths exist.
SIZE: 1330 + 236 + 231 lines. 119 tests.
DEMONSTRATED CORRECTNESS:
- Reported: hashing caught 23/57 dirty bodies (7c5bfcb08) and 11 records hashed over CRLF (47e13ef65).
- Defect: the validator checks form only. An all-zero tree hash passes; any existing file passes as a receipt.
- Crawl finding I did not repeat: PAYLOAD_MANIFEST_ID is hashed over CRLF bytes for three packets.
INTERFACE: Library and CLI. Returns a list of problems. Deterministic.
THROUGHPUT / SCALE: Not recorded.
COUPLING: Vault paths; WORLDS.json.
FIT TO SLOT: None of this scope's slots directly; it is a PROV-02/PROV-03 asset. It supplies T16/T18 fixtures.
MODIFICATION COST: M. Rebuild of a validator: S.
VERIFIED BY ME: packet.validate read in full. The preservation results are from the dossier.

----------------------------------------------------------------------
COMPONENT: Techne loop instrument primitives and the gate mutation assay (absent from the Tityos inventory)
PATHS: prometheus_math/battery.py (structural_constancy); prometheus_math/instrument_contract.py; prometheus_math/measurement.py; prometheus_math/migration_liveness.py; prometheus_math/tests/; techne/loop/measure_062_gate_probes.py and rung_notes/cycle_062_gate_probes.json
OWNER / DATES: The Techne loop. 2026-08-21 (93be46561, 0c96ec0ab, 90be14761). Assay dd3a0d677, 2026-08-25.
WHAT IT REALLY DOES:
- structural_constancy returns one of four values: VARIES (a flipping input was exhibited); PARAMETER_INDEPENDENT (the AST shows the body never reads its arguments); UNSETTLED; INVALID_PROBE (every probe raised).
- certify() runs four fixture factories: POSITIVE must signal; NEGATIVE must not; INVALID must give neither; a SENSITIVITY pair must differ. It can redraw the fixtures several times, and memorisation_is_still_possible demonstrates the contract's own hole.
- Measurement is SIGNAL, NO_SIGNAL or OUT_OF_DOMAIN. On OUT_OF_DOMAIN, both .value and bool() raise.
- The assay mutates a claim record in 8 declared ways and checks whether the promotion decision changes.
SIZE: 227 + 187 + 157 + 168 lines, with 15, 11 and 12 tests. The assay is 208 lines.
DEMONSTRATED CORRECTNESS:
- The constancy probe caught discovery_pipeline F9 (docstring); I verified that F9 returns True unconditionally.
- Assay: 6 of 8 mutations detected; a corrupted value and a changed row count went undetected (sensitivity 0.75).
- Code-inferred: certify's sensitivity test passes any nondeterministic instrument. There are no counts, and no separate impostor or channel-test class.
INTERFACE: Generic stdlib libraries; deterministic.
THROUGHPUT / SCALE: Not recorded.
COUPLING: None outside prometheus_math. Used by techne/ladder_circuits.
FIT TO SLOT: QUALIFICATION GATE (the calibration and fire-test core of MEAS-02) and VERDICT TYPE (SCI-02 guard mechanics). Detects T03 and T04. Missing: error rates (MEAS-01) and receipts.
MODIFICATION COST: S. Rebuild: S to M.
VERIFIED BY ME: All four modules, the test counts, and the assay JSON.

----------------------------------------------------------------------
COMPONENT: NYX_PREDICTION_PACKET v1 and the mechanism ledger
PATHS: nyx/atlas/predictions/schema.py; nyx/atlas/predictions/MECH-*.json and .FREEZE (8 packets); nyx/atlas/mechanisms.py; nyx/atlas/gates/MECHANISMS.json; nyx/tests/test_prediction_schema.py and test_scoreboard.py
OWNER / DATES: Nyx. 2026-09-16..09-19 (f8b84265e, c2921864d, d8741f71a).
WHAT IT REALLY DOES:
- validate() requires every field: a boundary with path, payload hash and line range; the claim; interventions with direction and numeric band; cheat and positive controls (or a stated reason why no positive control exists); cut_kill and indeterminate outcomes; a return protocol.
- freeze stores the sha256 of the canonical bytes and REFUSES if those bytes later change. A correction is a new packet that names the old one in "supersedes".
- The ledger requires a boundary and a falsifier for each mechanism, and a SUPPORTED transplant row before a mechanism can be marked SURVIVED_TRANSPLANT. It counts unique mechanism ids.
SIZE: 130 + 130 lines. 2 schema tests and 1 scoreboard test.
DEMONSTRATED CORRECTNESS:
- Frozen packets re-hash to their FREEZE files; a bad vocabulary value is rejected. The ledger holds 7 mechanisms (4 PROPOSED, 3 EVIDENCE_SUPPORTED).
- Defect: the payload hash is checked for length only, and no .py file in the tree recomputes it.
- Defect: barring the author from adjudicating is not in code.
- Defect: the ledger accepts the outcome "SURVIVED", which is outside its own vocabulary.
INTERFACE: Library and CLI. cut_kill and indeterminate exist only as preregistered prose fields.
THROUGHPUT / SCALE: Not recorded.
COUPLING: None.
FIT TO SLOT: PREREG/FREEZE CHECKS: the freeze is a PROV-04 append-only pattern and a MEAS-06-style refusal. Detects T11; T16 by form only. Fails SCI-03, PROV-06 and MEAS-11.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: Both modules, the tests, the ledger counts, and a git grep for file_payload_hash.

----------------------------------------------------------------------
COMPONENT: Hecate metamorphic evaluator-corruption harness and evaluator contract
PATHS: hecate/metamorphic/harness.py; roles/Hecate/harvest_w2/INV_F_metamorphic_results.md and .json; hecate/programs/_lib/evaluator_contract.py; hecate/tests/test_evaluator_contract.py
OWNER / DATES: Hecate[m1-dd0c3882]. Harness 41fbe01ed, 2026-09-30. Contract 2dc4fbb01, 2026-10-01 (a draft, not issued).
WHAT IT REALLY DOES:
- Copies each world to a scratch area, corrupts its rows with one of 9 operators, reruns the evaluator, and judges the reaction (OK, UNINF, INSENSITIVE, ASYM, BLIND, CRASH; a crash never counts as detection).
- Operators: swap treatment and null twin; copy treatment into the twin; replace treatment with control or twin; drop all positive-control rows; drop all cheat rows; copy treatment into the cheat; copy seed 0 into every seed; permute payloads within a seed.
- The contract is a spec-driven evaluator: five mandatory arms including CHEAT and SIMPLE_ALT; INSTRUMENT_FAIL on missing arms, seeds or fields; a seed-independence check; Fraction comparisons; one success rule applied to every arm.
SIZE: Harness 726 lines. Contract 416 lines with 33 tests.
DEMONSTRATED CORRECTNESS:
- Across 42 evaluators, baselines reproduced 42/42.
- It found HT-47f4c02be4/W1 passing with zero control rows.
- Removing controls was "caught" only by crashing in 32/42 and 33/42 evaluators. Pseudo-replication was accepted almost everywhere.
- A test shows the procedure catching a naive evaluator.
INTERFACE: The harness is bound to Hecate's row schema. The contract is a library that never raises; INSTRUMENT_FAIL takes precedence over CONFOUNDED, SIGNAL and NULL.
THROUGHPUT / SCALE: 486 s wall on 6 workers; the slowest run was 42.6 s.
COUPLING: The harness depends on the hecate/programs layout. The contract has no dependencies.
FIT TO SLOT: QUALIFICATION GATE fire tests: the closest existing form of MEAS-02's "break each control and expect a failure". The contract fits VERDICT TYPE with MEAS-07 exactness. Detects T03, T07 and T10.
MODIFICATION COST: M. Rebuild: M.
VERIFIED BY ME: judge(), the operators, findings F1-F4, the contract header, and the test names.

----------------------------------------------------------------------
COMPONENT: Hecate exact-arithmetic shadow evaluator and derived-file reproduction tests
PATHS: hecate/alien/shadow_decisions.py; hecate/tests/test_shadow_decisions.py; hecate/tests/test_derived_reproduce.py
OWNER / DATES: Hecate. Shadow evaluator 264854c4b, 2026-09-30. Derived-file tests 2dc4fbb01, 2026-10-01.
WHAT IT REALLY DOES:
- The shadow evaluator re-decides every preregistered decision of the alien assay in Fractions. It maps frozen floats back to rationals and asserts the round trip, replays the bootstrap on the same random stream, and reports recorded vs shadow vs DIVERGES.
- The derived-file tests regenerate each committed derived file under hecate/ and require equality, apart from listed exceptions.
SIZE: 556 lines with 12 tests. The derived-file tests are 665 lines with 16 tests.
DEMONSTRATED CORRECTNESS:
- DIVERGES on H3: the exact value is 1/10, against a float comparison at analyze.py:276.
- DIVERGES on H4.
- Per-item replay: 0 mismatches. No decision changed (roles/Hecate/harvest_w2/LEDGER.md line 26).
INTERFACE: Bound to one assay. The tests are pytest.
THROUGHPUT / SCALE: Not recorded.
COUPLING: hecate.alien; sandbox copies of the programs.
FIT TO SLOT: Support for MEAS-07 (a second evaluator recomputes every decision) and for REPR-05 / derived state. Detects T10 and T23. The method is reusable; the code is not.
MODIFICATION COST: L. Rebuild: M.
VERIFIED BY ME: The header and constants, the test counts, and the ledger line. Only the header of the derived-file tests.

----------------------------------------------------------------------
COMPONENT: attacks/REGISTRY.md, attacks/preflight.py, the probes, and the ADMISSIBLE hook
PATHS: attacks/REGISTRY.md; attacks/preflight.py; attacks/probes/atk013_*.py, atk014_*.py, atk015_*.py; attacks/known_failing.json; attacks/install_hook.sh
OWNER / DATES: Watchers/Hephaestus (registry 84cf1cb50, 2026-08-20); preflight by Charon. 12 commits, the last 2026-09-01.
WHAT IT REALLY DOES:
- The registry lists 20 classes, ATK-001 to ATK-020. 10 name an executable probe somewhere; 10 are described only.
- preflight.py has five checks, a selftest (a planted and a clean case for each of three checks, plus 3 ratchet cases), and a ratchet against known_failing.json.
- The hook only runs "preflight.py --probes", which executes the three scripts in attacks/probes/ and prints ADMISSIBLE unless one of them newly fails. So ADMISSIBLE certifies only three things:
  - ATK-013: total under-reading, in ergon/probe/ledgers/campaign/ only;
  - ATK-014: one estimator, on a synthetic corpus;
  - ATK-015: three hard-coded pairs.
  It never inspects the commit being made.
SIZE: Registry 435 lines; preflight 334 lines; probes 77, 106 and 67 lines. No pytest.
DEMONSTRATED CORRECTNESS: The selftest fixtures are synthetic. Defects I verified:
- --ledgers is documented but not implemented.
- The three data checks run only inside the selftest, and the "unsourced" check is never called.
- Three checks return PASS when their result is "not informative".
- ATK-015 skips any pair whose verdict file is missing.
- known_failing.json is {}.
- Git hooks are not tracked, so each clone needs its own install.
INTERFACE: CLI. Findings are two-valued; there is no "could not fire" outcome.
THROUGHPUT / SCALE: Not recorded.
COUPLING: The probes are hard-wired to ergon/probe paths.
FIT TO SLOT: FAILURE FIXTURES (the registry as a taxonomy with signatures; the ratchet has its own positive control). As a gate it fails SCI-02 and MEAS-02.
MODIFICATION COST: M. Rebuild: S.
VERIFIED BY ME: All the files listed.

----------------------------------------------------------------------
COMPONENT: Necropolis admissibility ladder and tool registry
PATHS: engine/necropolis/workshop/registry_source.py (lines 603-655); engine/necropolis/workshop/TOOLS.jsonl; engine/necropolis/workshop/tests/ (run_controls.py, cases_b..f.py, fake_reasoners.py, controls_result.json)
OWNER / DATES: Rhadamanthus / Keeper. 8 commits, 2026-09-13..09-14. Frozen since.
WHAT IT REALLY DOES: Computes the ladder PATH EXISTS, IMPORTS, EXECUTES, CONTROLLED, ADMISSIBLE for 93 historical instruments. A tool is admissible only if all of these hold: Keeper (non-author) cases ran; none of them FAILed or ERRORed; its hand-set status is READY or READY_WITH_CAVEAT. There are 194 cases of 10 kinds: ACCEPT 51, REJECT 28, CHEAT 24, SYNTHETIC_SIGNAL 23, SYNTHETIC_NULL 18, CORRUPT_INPUT 17, REPETITION 11, PERTURBATION 11, PARITY 10, LAUNDERING 1.
SIZE: The builder is 767 lines; the control and test code is 2,924 lines.
DEMONSTRATED CORRECTNESS:
- Run at 2d97a6c66: 174 PASS, 8 FAIL, 9 INFO, 3 ERROR. The FAILs include grading-oracle cheat readers scoring 0.75 and 1.0, and Pollux's null.
- 45 tools admissible (38 EVIDENCE, 7 WITH_CAVEAT). Control by KEEPER 57, AUTHOR_ONLY 24, NONE 12. Author unknown for 81.
- Defect (code-inferred): no structural rule requires a control in the failing direction. Eight tools have no such case and are blocked only by their hand-set status.
INTERFACE: Each case returns (bool, observed); verdicts are PASS/FAIL/INFO/ERROR.
THROUGHPUT / SCALE: 194 cases in 74 s.
COUPLING: Imports every tool under test.
FIT TO SLOT: QUALIFICATION GATE (admissibility from executed, non-author controls; partial MEAS-02) and FAILURE FIXTURES. Detects T01, T03 and T05; records the author/non-author split relevant to T17.
MODIFICATION COST: M. Rebuild: S for the ladder, M for the cases.
VERIFIED BY ME: The ladder code. The counts I recomputed from TOOLS.jsonl and controls_result.json.

----------------------------------------------------------------------
COMPONENT: Artemis constructed-specimen heredity panel and commit-reveal self-test
PATHS: roles/Artemis/challenge/p11/ (specimens.py, certs.py, verdict.py, RESULT.md, results/); roles/Artemis/selftest/ (build_packages.py, build_scoring.py, RESULT.md)
OWNER / DATES: Artemis[ubu002-78a7bd7b]. Prereg d5241a102, then result 2af325f7b, both 2026-09-28.
WHAT IT REALLY DOES:
- The panel is 17 specimens written as literal hex, each with known heritable content: zero-bit painters, copiers, 1-bit and 4-bit painters, and stress cases. They are run against the P-11 certificate and its alternatives, and verdict.py applies the preregistered rules mechanically.
- The self-test committed a sha256 of the secret mapping before anything was revealed, and scored its forecasts with Brier against a constant forecast.
SIZE: 8 files, 1187 lines. Self-test scripts 50 + 22 lines. No tests.
DEMONSTRATED CORRECTNESS:
- P-11 certified all 4 painters (pass rates 0.90-1.00) and rejected 4 genuine replicators. CVT-2 sorted all 17 as predicted. The E0 and E1 gates PASS.
- Brier 0.470 against a constant forecast's 0.391.
INTERFACE: Scripts bound to the z8 and toy VMs; deterministic.
THROUGHPUT / SCALE: Panel 60 s wall (run 3 times); the natural set 9.5 s.
COUPLING: Archived copies of Nestor's NPE code.
FIT TO SLOT: QUALIFICATION GATE exemplar: the cleanest positive/negative/impostor set with a confusion table (section 1.3). Also a SCI-06 exemplar. Detects T14, T12 and T13.
MODIFICATION COST: M. Rebuild: S per world family.
VERIFIED BY ME: The RESULT tables, the specimen dataclass, and the commit order.

----------------------------------------------------------------------
COMPONENT: Clymene repository probe and tree comparator
PATHS: roles/Clymene/science/repo_audit.py (and model_audit.py, weights_probe.py, consumption_audit.py)
OWNER / DATES: Clymene. One commit, 2026-09-11.
WHAT IT REALLY DOES:
- Fetches each archived repository at its recorded SHA and compares git blob hashes (raw and CRLF-normalised) with ls-tree.
- Its controls are written out as result rows: a POSITIVE fetch, a fabricated SHA, a dead URL, and "CHEAT_KNOWN_GOOD_TREE" (a real checkout must score 1.0).
SIZE: 6 files, 1281 lines. No tests.
DEMONSTRATED CORRECTNESS:
- The control rows are recorded as True/False/None, but nothing aborts when a control fails.
- The "cheat" control is really a positive or channel control in Phase 3 terms.
INTERFACE: A script with a hard-coded absolute host path to the M2 vault.
THROUGHPUT / SCALE: 37 artifacts, about 51 GB (dossier).
COUPLING: The M2 vault and network access.
FIT TO SLOT: FAILURE FIXTURES for T19. Fails MEAS-02.
MODIFICATION COST: M. Rebuild: S.
VERIFIED BY ME: The controls and the comparator. The results are from the dossier.

----------------------------------------------------------------------
COMPONENT: Elenchus closed-form ground truth against solver status
PATHS: roles/Elenchus/investigations/2026-09-11_epistemic_debt/verify_sdp_family.py
OWNER / DATES: Elenchus. One commit, 2026-09-11.
WHAT IT REALLY DOES: For a family of semidefinite programs it compares the solvers' returned values, and trace(CX) recomputed from the returned X, against the analytic optimum, across seeds and condition spreads from 1e4 to 1e14.
SIZE: 65 lines. Print-only: no asserts and no tests. The disputed values are hard-coded.
DEMONSTRATED CORRECTNESS: Reported: SCS returned status "optimal" while being 188% wrong (from the dossier; I could not re-run it without cvxpy).
INTERFACE: A script.
THROUGHPUT / SCALE: Not recorded.
COUPLING: cvxpy, CLARABEL, SCS.
FIT TO SLOT: A SCI-05 known-answer pattern and a T19 fixture. Nothing reusable as code.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: The script. The numbers are from the dossier.

----------------------------------------------------------------------
COMPONENT: Hypatia three-valued stall predicate
PATHS: roles/Hypatia/science/stall_check.py
OWNER / DATES: Hypatia. One commit, 2026-09-11.
WHAT IT REALLY DOES: Samples a probe and returns PROGRESSING, STALLED or INDETERMINATE. It refuses STALLED unless the interval can resolve one unit and the readings are monotone.
SIZE: 200 lines. An in-module selftest with 6 checks.
DEMONSTRATED CORRECTNESS: Selftest cases: a dead process gives STALLED; a fast process gives PROGRESSING; a slow but live process is not STALLED; a snapshot, a short interval and non-monotone readings each give INDETERMINATE. Known defect (dossier): pointed at the wrong quantity (gitdir size during a merge), it returned STALLED for a live process.
INTERFACE: A library function over a probe callable; floats.
THROUGHPUT / SCALE: Not recorded.
COUPLING: None.
FIT TO SLOT: VERDICT TYPE exemplar. A T21 detector for liveness only.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: The branches and the selftest keys.

----------------------------------------------------------------------
COMPONENT: Eos typed intake states
PATHS: agents/eos/src/intake.py; agents/eos/tests/test_intake.py
OWNER / DATES: Eos. 2026-09-11: prereg b3245156e, then 54a1f97cc (KEEP_DARK).
WHAT IT REALLY DOES:
- Runs predicates for each sought state. Returns REFUSED, PENDING_ADMISSION, RESOURCE, INDETERMINATE (one of its own instruments did not answer) or NOT_EXAMINED (the verdict would be the same whatever the item said).
- capability_absent searches the whole tracked tree with git grep --cached.
SIZE: 515 lines with 25 tests.
DEMONSTRATED CORRECTNESS:
- Nemesis crossed the gate 30/30 on the RESOURCE path (since repaired) and 200/200 on wrong referents (unrepaired).
- Defect: NOT_EXAMINED fires only when the proposer string contains "auto", "constructor" or "generated", i.e. a self-declared label.
INTERFACE: Library; deterministic. INDETERMINATE and NOT_EXAMINED are distinct outcomes.
THROUGHPUT / SCALE: 56 items and 34 controls (engine index).
COUPLING: git.
FIT TO SLOT: VERDICT TYPE vocabulary. Detects T12 and T19.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: The states, classify() and the capability check.

----------------------------------------------------------------------
COMPONENT: comms/manifest.py
PATHS: comms/manifest.py; comms/tests/test_manifest.py
OWNER / DATES: comms (base role). 8bb162a77, 2026-09-11.
WHAT IT REALLY DOES: Writes and verifies the sha256 of every file in one directory. For text files it normalises CRLF and lone CR to LF first.
SIZE: 85 lines. 2 tests and 5 Keeper cases (3 PASS, 2 INFO).
DEMONSTRATED CORRECTNESS:
- LF and CRLF copies hash identically, and a real change is caught.
- Keeper INFO: files in subdirectories are not covered, and a rewritten manifest still passes verify.
- Code-inferred: verify returns (0, []) and exits 0 when no line of the manifest parses.
INTERFACE: Library and CLI.
THROUGHPUT / SCALE: Not recorded.
COUPLING: None.
FIT TO SLOT: PREREG/FREEZE CHECKS. PROV-02's check names "the existing manifest tool", and this is that tool. Detects T18. Missing: recursion, a non-empty check, an anchored manifest hash.
MODIFICATION COST: S. Rebuild: S.
VERIFIED BY ME: Source, tests and the Keeper results.

----------------------------------------------------------------------
A. BEST EXISTING DETECTOR (D) AND FIXTURE (F) PER FAILURE CLASS
(Paths verified by me unless marked [dossier] or [prose].)

T01 measurement carries its own answer
  D: roles/Nemesis/science/cheatlib.py (PayloadReader); charon/probe/charon_gate_fire_2026-08-25.py
  F: harmonia/experiments/reasoning_phase0.py:131 together with engine/necropolis/workshop/tests/fake_reasoners.py and run_controls.py:122-136 (recorded FAIL, 1.0); charon/src/ingest_zeros.py:107
T02 self-verdicting
  D: roles/Harmonia/qualification/campaign1/c1_hostile_adjudication.py adjudicate(); harmonia/diagnostics/detector_band_audit.py (Theseus only)
  F: theseus/generators/a1_catalog_cross_product.py:182-185; prometheus_math/discovery_pipeline.py:486-510; sigma_kernel/omega_oracle.py:39-69
T03 controls that cannot fail
  D: prometheus_math/battery.py structural_constancy; hecate/metamorphic/harness.py (M4, M4c)
  F: hecate/programs/HT-47f4c02be4/worlds/W1/evaluate.py:14-15; prometheus_math/discovery_pipeline.py:272-282; charon/scripts/bsd_battery.py:213; charon/agents/pollux/daemon.py:416-420
T04 positive control absent or aimed beside
  D: audit_primitives.py absence_control; prometheus_math/instrument_contract.py certify
  F: cartography/shared/scripts/known_truth_battery.py:18-33; charon/probe/exit_review_3_attack.py:233-238; ergon/probe/tests/test_gates_fire.py:122-134
T05 invalid null, no chance floor
  D: cheatlib chance_floor and MajorityClass; audit_primitives null_pass_binomial
  F: agents/nemesis/adversarial/adversarial_results.jsonl (pinned by test_cheatlib.py:107-127); harmonia/nulls/block_shuffle.py:109-110
T06 tautology
  D: harmonia/sweeps/pattern_30.py (header read; 28 shared tests in test_sweeps.py)
  F: prometheus_math/discovery_pipeline.py:285-306 (F11: M(p) against M(reversed p))
T07 construction artifacts
  D: attacks/preflight.py degenerate_strata and frame
  F: none executable on real data [prose: aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md, not opened]
T08 baseline omitted
  D: audit_primitives baseline_gaming; cheatlib MajorityClass
  F: audit_primitives.py HECATE_BASELINES; prometheus_math/modal_collapse_synthetic.py
T09 selection effects
  D: none (partial: preflight frame; qualification_rules.refuse_endpoint, where the field is declared by the caller)
  F: none executable found
T10 statistical malpractice in gates
  D: hecate/alien/shadow_decisions.py; hecate/programs/_lib/evaluator_contract.py; harness M6
  F: hecate/alien/analyze.py:276; roles/Harmonia/qualification/h0h5/qualification_rules.py:230-286
T11 post-exposure change
  D: audit_primitives freeze_precedes; nyx/atlas/predictions/schema.py freeze refusal
  F: roles/Ananke/research/workers/W-O/PLAN.md (93e2e544b); charon/agents/moros/daemon.py:48-56
T12 unreachable design
  D: audit_primitives reachability; QR Gate.eligibility; c1c2 NOTHING_COULD_HAVE_FIRED
  F: audit_primitives._tyche_h1(3); ergon/probe/f_null.py classifier_auc with fewer than 2 samples
T13 world or organism too weak
  D: none general (prometheus_math/tests/test_modal_collapse_synthetic.py tests world solvability only)
  F: roles/Artemis/challenge/p11/specimens.py Z3u96 (a genuine copier that cannot pass C2: 0/20)
T14 label stands in for property
  D: roles/Artemis/challenge/p11/certs.py CVT-2/CVT-R with the panel
  F: roles/Artemis/challenge/p11/specimens.py Z1, Z2, TV-1, TV-2 (the painters)
T15 novelty conflation
  D: audit_primitives absence_control; nothing measures prior-art recall
  F: audit_primitives.py GRAVITY_CALIBRATION
T16 mechanism by description
  D: nyx/atlas/mechanisms.py validate (form only)
  F: techne/fossils/packet.py:80-160; nyx/atlas/predictions/schema.py (hash checked for length only)
T17 improper independence
  D: none (partial: registry_source.py records KEEPER vs AUTHOR_ONLY)
  F: agents/nemesis/src/validators.py:16-27
T18 provenance failures
  D: comms/manifest.py; c1c2 pool_fingerprint; attacks/probes/atk015_unsourced_verdict.py
  F: comms/tests/test_manifest.py (synthetic); Techne's CRLF PAYLOAD_MANIFEST_ID [dossier]
T19 status from the wrong layer
  D: c1c2 C2; roles/Clymene/science/repo_audit.py compare()
  F: ergon/probe/ledgers/campaign_blockB/p1_prepass.jsonl (55 failed rows rendered as residue); harmonia/src/validate.py:219-228; roles/Elenchus/.../verify_sdp_family.py
T20 safeguards never wired
  D: prometheus_math/migration_liveness.py (partial)
  F: attacks/install_hook.sh; preflight's "unsourced" (never called) and --ledgers (not implemented)
T21 activity read as productivity
  D: roles/Hypatia/science/stall_check.py (liveness only)
  F: none executable found
T22 auditor commits the audited class
  D: none
  F: audit_primitives.py:160-165; c1_hostile_adjudication.py:320-321; exit_review_3_attack.py:233-238
T23 validated differs from deployed
  D: c1c2 C1; adjudicate() (analysis-code hash); hecate/tests/test_derived_reproduce.py
  F: R7 .text vs .body [dossier: charon/probe/TIER_A_EXIT_REVIEW_CHARON_2026-08-19.md]; the c1c2 copied-sha test (synthetic)
T24 model-specific hazards
  D: hecate/tests/test_llm_isolation.py (2 string checks)
  F: hecate/llm.py:57-84 (a truncated reply returns its first complete inner object; code-inferred)

----------------------------------------------------------------------
B. REAL HISTORICAL DEFECTS THAT WOULD MAKE GOOD FIXTURES (path | commit | class)

Documented on the record:
B1  Answer key inside the probe | harmonia/experiments/reasoning_phase0.py:131 (graded at :440) | 830a83a3f 2026-06-09; executable cheat reader already exists (2d97a6c66) | T01
B2  Metadata appended to the measured vector | charon/src/ingest_zeros.py:107 | 9e189d683 2026-04-01 | T01
B3  Generator writes its own verdict and prefixes its label | theseus/generators/a1_catalog_cross_product.py:182-185 | 0bd7b5c27 2026-05-18 | T02, T01
B4  CLEAR written by SQL; F9 always True; F11 compares a value with itself | prometheus_math/discovery_pipeline.py:272-282, 285-306, 486-510 | 09a7dccb9 2026-05-03 | T02, T03, T06
B5  Falsifier over a number supplied by the caller | sigma_kernel/omega_oracle.py:39-69 | d2ce08cfa 2026-04-29 | T02
B6  Hard-coded PASS inside a tally | charon/scripts/bsd_battery.py:213; charon/scripts/abc_battery.py:237, 336 | 5cff61282 2026-04-18 | T03
B7  Hard-coded negative control | roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis.py:266-269 | 341a92b89 2026-09-14 | T03
B8  Ablation that forces silence, with a test asserting it | c1_hostile_adjudication.py:320-321 and its test lines 29-31 (a88410dde); audit_primitives.py:160-165 (db6897ecf) | T03, T22
B9  Empty control arm passes | hecate/programs/HT-47f4c02be4/worlds/W1/evaluate.py:14-15 | ad693571a 2026-09-29; found by 41fbe01ed | T03
B10 Dead input field makes a gate constant | ergon/probe/drip_coldband.py | introduced f592a7885, fixed 307f6fe67; preserved ledger coldband_drip/nvidia_nemotron-super-49b-v1.STALE-WRITER-no-tokens.jsonl | T03, T19
B11 Correlation of two sorted lists | charon/agents/pollux/daemon.py:416-420 | 8c619443a 2026-05-24 | T03, T05
B12 Detector that cannot fire | agents/nemesis/src/evaluator.py:94 | 1c4e1a38d 2026-03-25 | T03
B13 Wrong-signature call always reads UNTESTED | harmonia/src/validate.py:219-228 | 98ae574eb 2026-04-12 | T03, T19
B14 Degenerate null mapped to certainty (z = inf) | harmonia/nulls/block_shuffle.py:109-110, also bootstrap.py, frame.py, model.py | 043ba7821 2026-04-18 | T05
B15 Probe passes when its inputs move | attacks/probes/atk015_unsourced_verdict.py:42-43 | 574c86447 2026-08-23 | T03, T20
B16 Leak check strips the region where the leak lives | ergon/probe/packet_invariants.py | 32e38d970, fixed 986bf0058; regression test test_packet_leak_gate_fire.py:345-372 | T01, T03
B17 Threshold lowered after the data | charon/agents/moros/daemon.py:48-56 | 43b094552 2026-05-25 | T11
B18 Plan committed together with its results | roles/Ananke/research/workers/W-O/PLAN.md | 93e2e544b 2026-09-29 | T11
B19 Float comparison sitting exactly at the threshold | hecate/alien/analyze.py:276 | 1fed85d95 2026-09-30 | T10
B20 Anti-conservative quantile table | qualification_rules.py:230-286 | dd38720c0 2026-09-09 onward | T10
B21 "n/a" recorded as pass | t3_strict_cutover_rehearsal.py:84-86 | f3c9d267f 2026-09-05 | T03
B22 Validator drawn from the population under test | agents/nemesis/src/validators.py:16-27 | 1c4e1a38d | T17
B23 Form-only validator | techne/fossils/packet.py:80-160 | bc92fd942 2026-09-16 | T16, T18
B24 Estimator that is correct only when the hypothesis is true | ergon/probe/corpus_scan_full.py (the cond loop) | ce3157a7b 2026-08-22 | T03, T06
B25 Calibration aimed beside the battery | cartography/shared/scripts/known_truth_battery.py:18-33 | 12f4403aa [taxonomy] | T04
B26 Truncated model reply parsed as an answer | hecate/llm.py:57-84 | b15a475b8 2026-09-29 | T24 (code-inferred)

Documented only by this report (not confirmed by the owners):
B27 Positive control planted on a pair that is already separable | charon/probe/exit_review_3_attack.py:233-238 | 574c86447 | T03, T04, T22
B28 Insufficient samples counted as a pass, and a test enshrines it | ergon/probe/f_null.py classifier_auc; test_f_null.py:216-217 | afd5913c0 | T03, T12
B29 A test re-implements the rule it claims to test | ergon/probe/tests/test_gates_fire.py:122-134 | 24153512c 2026-08-24 | T04
B30 Checks marked "not informative" return PASS | attacks/preflight.py:94-96, 127-129, 185-186 | cf58080fd [engine index] | T03
B31 Manifest verify passes with nothing checked | comms/manifest.py verify() and main() | 8bb162a77 | T03, T18 (code-inferred)

----------------------------------------------------------------------
COMPARISON

QUALIFICATION GATE (calibration set, channel test, fire tests)
 1 Hecate metamorphic harness + contract  only executed "break each control" suite; found a real defect
 2 Techne instrument_contract + constancy  generic positive/negative/invalid/sensitivity + "can it fire"
 3 Necropolis ladder + Keeper cases        admissibility from executed non-author controls; frozen
 4 Artemis P-11 panel                      best calibration set with a confusion table; one VM family
 5 Harmonia AP absence_control / ceiling   small gate checks; boolean flags
 6 attacks/preflight selftest + ratchet    planted/clean pairs, synthetic; ADMISSIBLE is hollow
 7 Charon R7 calibration                   measured same-distribution false-positive method; passes empty input
 8 Techne modal-collapse null              world-solvability control; bound to RL
 9 Charon exit-review-3                    positive control cannot fail; rewrite
10 Clymene / Elenchus                      exemplars only

FAILURE FIXTURES
 1 Necropolis Keeper cases (194)           executable against real old code; real FAILs on record
 2 Harmonia AP fixtures                    five real defects, each with a clean twin
 3 Charon c1c2 tests                       planted, cheat and nothing-could-fire cases
 4 Hecate metamorphic operators            9 operators run over 42 real evaluators
 5 Charon 08-25 gate-fire worlds           one-character leaks: space, homoglyph, zero-width
 6 attacks/REGISTRY.md                     20 classes with signatures; half are only described
 7 Harmonia AF F1-F9                       synthetic, co-written with their detectors
 8 Techne F2 calibration                   planted relations and decoys; bound to Theseus
 9 Harmonia emission-path census           Theseus only

TRIVIAL RESPONDERS
 1 Nemesis cheatlib                        generic constant / majority / payload reader / floor / shrink
 2 Harmonia AP baseline_gaming             runs a frozen rule on committed baselines
 3 Harmonia AP null_pass_binomial          binomial tail for count thresholds; floats
 4 Techne modal-collapse random arm        RL only

VERDICT TYPE
 1 Charon c1c2 Verdict                     three values plus counts and rows; meets SCI-02's own fixture
 2 prometheus_math Measurement             OUT_OF_DOMAIN cannot be read as a value; no counts
 3 Hecate evaluator_contract               exact Fractions; INSTRUMENT_FAIL takes precedence; draft
 4 Harmonia QR decide()                    INELIGIBLE separate from INCONCLUSIVE; wrong quantiles
 5 Eos intake states                       INDETERMINATE vs NOT_EXAMINED; trigger is self-declared
 6 Hypatia stall predicate                 asymmetric three-valued rule; narrow
 7 Charon band rule                        three values, float, the code is untested
 8 Charon R7 verdict                       two-valued; empty input passes

PREREG / FREEZE CHECKS
 1 Harmonia AP freeze_precedes + reachability  git-ancestry freeze plus attainable set; real fixture
 2 Harmonia HA adjudicate()                rows and code bound by hash; refuses outside verdicts
 3 Charon c1c2 C1 + ordering check         bytes vs receipt vs prereg; gate verdicts carried in receipt
 4 Nyx packet freeze                       canonical-bytes hash, refusal on change; validation form-only
 5 comms/manifest.py                       the tool PROV-02 names; passes when nothing is checked
 6 Hecate shadow + derived-file tests      recompute decisions and files; bound to one assay
 7 Harmonia QR validate_plan               plan fields declared by the author; lane-specific

----------------------------------------------------------------------
COULD NOT DETERMINE

- I ran no test or script. Every PASS count above comes from committed artifacts or commit messages.
- Not opened, for lack of time:
  - Harmonia: exchangeability.py, floor_precheck.py, packet_rules.py, run_qualification.py, and the science rulers.
  - Hecate: the control-first world generator (its "6 of 16 to 0 of 8" claim).
  - Techne: the F2 calibration bodies and the replay body; harvest and rematerialise.
  - Nyx: the probe battery and the contents of the packets.
  - Artemis: certs.py and the CVT-R adapter.
  - Clymene: the other three audits.
  - Necropolis: coroner_run.py, validate_workshop.py, the adapters.
  - ergon/probe/r3_controls.py: its header claims measured operating characteristics (false alarm 5%; power 100% at +15pp and 85% at +10pp; N=400 over 40 seeds). This could be the only measured control error rate in this territory; I did not verify it.
- Wiring after commit: a git grep (with the full exclusions) for Python importers found that c1c2_checks, audit_primitives, c1_hostile_adjudication, detector_band_audit, stall_check and evaluator_contract are used only by their own tests, scripts and Necropolis.
- T07, T09, T13, T17, T21 and T22: no executable detector in my components or in the Tityos indexes. This was not a repository-wide search.
- Whether anyone noticed the exit-review-3 pairing: a tree-wide git grep for "trailing space" turned up no discussion of it.
- Taken from documents, not recomputed: 99.98%, 23/57, SCS 188%, the P-11 numbers, and Techne's CRLF manifest id.
- Throughput is not recorded for most instruments.

----------------------------------------------------------------------
SURPRISES

1. The exit-review-3 positive control could not fail.
   - It plants the trailing space on F-answer and compares with F0, a pair already separable at 1.0000. The code comment says F-null.
   - This contradicts Tityos REPORT section A ("caught a planted 1-character leak at 1.0000").
   - The Charon dossier says it never read this file.

2. Techne's prometheus_math has a tested, generic primitive library that the Tityos inventory does not mention at all.
   - structural_constancy, instrument_contract (POSITIVE / NEGATIVE / INVALID / SENSITIVITY, including its own memorisation anti-case), the Measurement type (OUT_OF_DOMAIN cannot be read as a value) and migration_liveness.
   - It is a stronger starting point for the gate library and verdict type than several of the listed components.

3. R7's layer (b) records "insufficient samples" as passed=True, and its own test asserts it. r7_verdict passes an empty balance list. The band rule's code has no test; its "test" recomputes the rule inline.

4. cheatlib and its 12 self-controls were committed in the same commit as the NEMESIS-01 results (14 minutes after the prereg). Its cheat test pins the "292 of 294" denominator artifact.

5. The Necropolis ladder never requires a control in the failing direction; the hand-set status string is the only thing blocking 8 accept-only tools. On the other hand, the Keeper already holds an executable T01 fixture (grading-oracle cheat readers scoring 0.75 and 1.0), which is better than "NT-001 UNTRUSTED" suggests.

6. preflight returns PASS for "not informative" in 3 of its 5 checks. ADMISSIBLE certifies only that three hard-wired probes passed.

7. The Nyx payload hash is checked for length only, and no Python file in the tree recomputes it. "Hash-bound" is procedural, not code.

8. Hecate's harness found a real positive control that cannot fail (HT-47f4c02be4/W1, all() over an empty arm). In 32/42 and 33/42 evaluators, removing a control was caught only by a crash.

9. Harmonia's adjudicate() is the only existing fixture in which an outside verdict is refused (closest to MEAS-11's check).

10. Holdout incident, reported as the coordinator asked:
    - Command: cd /f/Prometheus-worktrees/dionysus-base-role && timeout 60 git grep -n -i "trailing space" -- ':!**/*holdout*/**' ':!**/nestor_secrets/**' | cut -c1-250 | head -30
    - It returned CONTENT: one line (line 18) of evidence_wiki/gold/holdout_corpus_v1.jsonl, cut at 250 characters. [REDACTED at deposit by Dionysus: one sentence in which the worker described the fields of the row it saw. See 00_SEARCH_RULE_INCIDENT.md.]
    - I did not open the file and used nothing from it; my HB3-1 facts come from ergon/probe/tests/test_packet_leak_gate_fire.py.
    - Every search after that one used both holdout exclusions.
    - Two other searches used the old single exclusion. A git grep -l for "c1c2_checks" listed file names only; none was holdout-named. The search for "def test_correlation" over '*.py' also omitted ':!**/nestor_secrets/**'; it returned 1 match (cartography/shared/scripts/battery_unified.py:196).
    - Three searches restricted to ergon/ or nyx/ also lacked the nestor_secrets term.
    - Whole-tree listings were "git ls-files | grep X | grep -v -i holdout": names only, with holdout names filtered out before display.
    - I never touched prometheus/cosmos/tests/test_holdout_isolation.py.

11. Two instruments in scope run a git grep --cached over the whole tracked tree by design, which reads holdout-named paths when executed: the cheatlib test test_cheat_absent_marker_really_is_absent_from_the_tracked_tree, and Eos's capability_absent. This matters for sealed-world custody (WLD-06, PROV-10).

12. Clymene's "CHEAT_KNOWN_GOOD_TREE" is a positive or channel control, not an impostor. The REPORT's "real cheat control" uses a different meaning of "cheat" from section 1.3.

===END REPORT===
