"""Registry source for the Necropolis workshop (LAYER: NECROPOLIS VALIDATION).

Generates engine/necropolis/workshop/TOOLS.jsonl from three measured inputs:

  1. the curated instrument table below (what the Keeper READ, and what each
     instrument's contract is) -- every row here was inspected by hand;
  2. tests/controls_result.json -- the canonical control run.  self_tests are
     derived from it per tool_key, never typed by hand: PASS/FAIL are copied,
     ERROR becomes NOT_RUN with the error in the note, INFO cases are NOT
     self_tests (the schema enum has no INFO) and are cited under
     known_failure_modes instead;
  3. `git log -1 -- <current_path>` for source_commit, so the row names the
     commit at which the instrument was characterised.

The planned necropolis_status of a row is CHECKED against the run: a row
planned READY whose controls contain any FAIL or ERROR aborts generation.
"A tool does not enter READY merely because it executes" (charter VI).

Usage:
    python engine/necropolis/workshop/registry_source.py \
        [--controls tests/controls_result.json] [--out TOOLS.jsonl]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = "engine/necropolis/workshop/tests/run_controls.py"
KEEPER = "Rhadamanthus"
HARVEST_DATE = "2026-09-13"
AUTHOR_TESTS = HERE / "AUTHOR_TESTS.json"      # {test_path: {rc, summary, seconds}}
CONSUMERS = HERE / "CONSUMERS.json"            # {current_path: [importer paths]} (adapters/consumer_trace.py)

ACCEPT_KINDS = {"ACCEPT", "SYNTHETIC_SIGNAL", "PARITY", "REPETITION"}
REJECT_KINDS = {"REJECT", "CHEAT", "SYNTHETIC_NULL", "CORRUPT_INPUT", "PERTURBATION", "LAUNDERING"}

ROWS: list[dict] = []


def T(key, name, path, cls, *, det="YES", mut="NO", model="NO", deps=(), dep_status="ALL_PRESENT",
      dep_detail=None, inputs, outputs, scope, forbidden, status, reason=None, caveat=None, kfm=(),
      adapter=None, layer="ORIGINAL_SCIENTIFIC_LOGIC", origin="LIVE_TREE", frank=(), inspected=True,
      batteries=(), historical_path=None, author_tests=(), source_commit=None, loop=1, techne_id=None,
      notes=None, consumers=None):
    ROWS.append(dict(key=key, name=name, path=path, cls=cls, det=det, mut=mut, model=model, deps=list(deps),
                     dep_status=dep_status, dep_detail=dep_detail, inputs=inputs, outputs=outputs, scope=scope,
                     forbidden=forbidden, status=status, reason=reason, caveat=caveat, kfm=list(kfm),
                     adapter=adapter, layer=layer, origin=origin, frank=list(frank), inspected=inspected,
                     batteries=list(batteries), historical_path=historical_path, author_tests=list(author_tests),
                     source_commit=source_commit, loop=loop, techne_id=techne_id, notes=notes,
                     consumers=consumers))


# ---------------------------------------------------------------------------
# WAVE 1 / 2 : live-tree instruments with Keeper controls (tool_key == run_controls group)
# ---------------------------------------------------------------------------
T("grading_oracle", "Harmonia grading-oracle staircase (grade_reasoner R0-R6)", "harmonia/services/grading_oracle.py",
  "grader", det="SEEDED",
  inputs="a reasoner callable + tier spec; probes carry `data` (and for R6 the `truth`) in the same object the reasoner sees",
  outputs="report dict: overall_pass_rate, staircase per tier, per-probe verdicts",
  scope="a reasoner's pass rate on the staircase AS THE ORACLE PRESENTS IT; useful to reproduce a historical score",
  forbidden="a high staircase score is NOT evidence of reasoning: the probe object carries its own answer (R6 `truth`, probe ground truth) and a 3-line reader ties the top baseline (memory 2026-08-12)",
  status="UNTRUSTED",
  reason="CHEAT controls FAIL: a reasoner that reads probe.data ground truth / R6 truth is graded as passing; CORRUPT_INPUT: a string trace aborts grading",
  kfm=["answer-key leak: truth readable at grade time (ladder R6, memory project_harmonia_B_ladder_leak_20260812)",
       "string trace raises instead of scoring zero (grading_oracle.CORRUPT_INPUT.string_trace_must_not_abort_grading)"],
  batteries=["historical_verdict_original_corrected", "claim_to_reproduction"], techne_id="grading-oracle-staircase")

T("coverage_diagnostic", "Harmonia coverage diagnostic (B1 degenerate vs B2 weak-search discriminator)",
  "harmonia/diagnostics/coverage_diagnostic.py", "coverage_diagnostic",
  inputs="target set with in-class flags + found set; class definition",
  outputs="verdict B1 / B2 / MIXED with recall and coverage fractions; refuses ceiling call without in-class recall",
  scope="whether a 'nothing novel' result is an expressiveness ceiling (B2) or a degenerate domain (B1) given a declared class",
  forbidden="does not establish that the declared class is the right class; out-of-class 'found' targets are refused, not adjudicated",
  status="READY", batteries=["output_replay_null_statistic_calibration"], techne_id="coverage-diagnostic")

T("kill_vector", "prometheus_math KillVector builder (falsifier margins -> niche descriptor)", "prometheus_math/kill_vector.py",
  "kill_vector",
  inputs="pipeline check_results dict (falsifier_name -> triggered, margin, method, ...)",
  outputs="KillVector with ordered components; same input -> same vector",
  scope="descriptor of WHICH falsifiers fired and by how much for a finding; basis for niche/void maps",
  forbidden="an empty check_results builds a vector (kill_vector.CORRUPT_INPUT.missing_check_keys, INFO): absence of checks is not absence of kills",
  status="READY_WITH_CAVEAT", caveat="empty check_results is accepted silently; callers must assert the falsifier list before building",
  kfm=["INFO kill_vector.CORRUPT_INPUT.missing_check_keys: empty check_results accepted, vector of untriggered components"],
  batteries=["output_replay_null_statistic_calibration"], techne_id="kill-vector")

T("residue_eligibility", "Erebos residue-eligibility gate (novel kill-pattern admission)", "charon/agents/erebos/_residue_eligibility.py",
  "residue_gate", deps=["charon.agents.erebos._kill_tensor"],
  inputs="kill ledger rows + candidate (plugin, domain, invariant, kill_pattern) + prior falsification signatures",
  outputs="eligible / not eligible with reason (repeated kp, dominant routing, missing signature)",
  scope="whether a residue candidate is admissible under the historical Erebos rule; replayable on ledger rows",
  forbidden="eligibility is a bookkeeping predicate, not evidence the residue is real",
  status="READY", frank=["FRANK-003"], batteries=["producer_fixture_consumer_differential"], techne_id="residue-gate")

T("reasoning_quality_emit", "prometheus_math reasoning_quality_emit (multi-evaluator vector ledger + contested-task detector)",
  "prometheus_math/reasoning_quality_emit.py", "feature_extractor", mut="WRITES_FILES",
  inputs="evaluator vectors per task (>=2 evaluators, valid vector shape); jsonl path",
  outputs="appended records; contested-task flag when evaluators disagree",
  scope="reproduce which tasks were contested between evaluators from a preserved ledger",
  forbidden="contested != wrong; unanimity != right", status="READY", techne_id="reasoning-quality-emit")

T("ks_ensemble", "anomaly_surface two-sample KS (ensemble vs reference)", "prometheus_math/research/anomaly_surface.py",
  "statistical_test", deps=["scipy"],
  inputs="two numeric samples", outputs="KS D and p",
  scope="distribution difference between two samples; p uniform under same-distribution null",
  forbidden="a small p on sorted/derived inputs says nothing about the raw process; check the transform first (see Pollux row)",
  status="READY", frank=["FRANK-004"], batteries=["output_replay_null_statistic_calibration"])

T("comms_manifest", "comms.manifest (line-normalised artifact hashes; write/verify)", "comms/manifest.py", "manifest_hash",
  inputs="a directory with a flat MANIFEST beside its files", outputs="(n_checked, bad_list); CRLF and LF hash equal",
  scope="whether the files beside a manifest still match the manifest",
  forbidden="verify() has no memory: a rewritten manifest passes (LAUNDERING INFO) and subdirectory files are silently uncovered (CORRUPT_INPUT INFO); provenance needs the manifest hash anchored elsewhere",
  status="READY_WITH_CAVEAT",
  caveat="laundering undetected and subdirectories uncovered -- use adapters/manifest_verify.py which reports uncovered files and the manifest's own hash",
  kfm=["INFO comms_manifest.LAUNDERING.rewritten_manifest_passes_verify: relaundered manifest verifies (1, [])",
       "INFO comms_manifest.CORRUPT_INPUT.subdirectory_file_not_covered: flat manifest, 2 present / 1 checked"],
  adapter="engine/necropolis/workshop/adapters/manifest_verify.py", batteries=["artifact_provenance_hash_reader_invariant"])

T("permutation_null", "Techne scipy_resampling_check permutation null", "techne/acquisition/checks/scipy_resampling_check.py",
  "null_generator", det="SEEDED", deps=["scipy"],
  inputs="two samples + statistic", outputs="permutation p; label-blind statistics are detected (CHEAT PASS)",
  scope="permutation p-value for a label-sensitive statistic", forbidden="p says nothing about effect size or mechanism",
  status="READY", batteries=["output_replay_null_statistic_calibration"])

T("validate_workshop", "Workshop registry validator (schema + status rules + negative self-tests)",
  "engine/necropolis/workshop/validate_workshop.py", "schema_validator", layer="NECROPOLIS_VALIDATION", origin="NECROPOLIS_BUILT",
  inputs="TOOLS.jsonl + batteries/*.json", outputs="error list, exit code; negative self-tests must fire on mutated rows",
  scope="structural admissibility of registry rows", forbidden="a validating row is not a working instrument",
  status="NEEDS_VALIDATION", reason="negative self-tests were skipped on the empty registry (INFO); no ACCEPT-family Keeper control yet",
  kfm=["INFO validate_workshop.CHEAT.negative_selftests_fire on the empty registry: selftests skipped"])

T("pollux_pipeline", "Pollux daemon statistic (sorted-Spearman + mean-spacing normalise + classify)", "charon/agents/pollux/daemon.py",
  "statistical_test", det="YES", deps=["prometheus_math.databases._mahler_data"],
  inputs="two numeric sequences (Mahler-measure subsets)", outputs="corr_raw, corr_norm, verdict PROMOTED/REJECTED/UNVERIFIED",
  scope="reproduces the HISTORICAL verdict for given inputs (adapters_pollux_replay.PARITY)",
  forbidden="corr_raw is a rank identity (both sides sorted before Spearman): 1.0 on independent samples. No Pollux PROMOTED verdict is evidence of coincidence",
  status="UNTRUSTED",
  reason="SYNTHETIC_NULL and PERTURBATION FAIL: independent samples correlate at ~1.0 and shuffling one side does not change corr_raw; adapters_pollux_replay.CHEAT shows the daemon does not reject such a verdict",
  kfm=["sorted(a)[:n] vs sorted(b)[:n] before Spearman is tautological (adapters_instrument_null.SYNTHETIC_NULL)"],
  adapter="engine/necropolis/workshop/adapters/pollux_statistic_replay.py", frank=["FRANK-004"],
  batteries=["historical_verdict_original_corrected"], notes="controls run through engine/necropolis/dossiers/pollux_evidence/pollux_instrument_null.py")

T("z3_oracle", "Techne z3 first-check / H1 oracle (SAT/UNSAT of boolean expressions)", "techne/acquisition/checks/z3_h1_oracle.py",
  "exact_oracle", deps=["z3-solver"], mut="WRITES_FILES",
  inputs="boolean expression text", outputs="sat/unsat + fixture json; agrees with the truth-table oracle (PARITY)",
  scope="exact satisfiability of a small boolean claim",
  forbidden="the script appends a receipt under techne/acquisition/receipts on a normal run; a coroner must run it through adapters/z3_receipt_redirect.py",
  status="READY_WITH_CAVEAT", caveat="ledger-appending side effect; use the redirect adapter",
  adapter="engine/necropolis/workshop/adapters/z3_receipt_redirect.py", batteries=["claim_to_reproduction"])

T("truth_table_oracle", "proteus.eval.boolean truth-table oracle", "proteus/eval/boolean.py", "exact_oracle",
  inputs="boolean expression + input width", outputs="label vector; malformed / out-of-range / wrong-width inputs refused",
  scope="exact ground truth for boolean tasks (the reference the z3 oracle is checked against)",
  forbidden="none beyond its domain: it is exact for well-formed inputs only", status="READY", batteries=["claim_to_reproduction"])

T("modal_collapse_synthetic", "prometheus_math modal-collapse synthetic diagnostic", "prometheus_math/modal_collapse_synthetic.py",
  "negative_control", det="SEEDED", inputs="an agent callable + tiny synthetic task set",
  outputs="verdict + score; random agent scores at chance (SYNTHETIC_NULL)",
  scope="chance floor for a modal-collapse claim", forbidden="passing the tiny diagnostic is not passing the real corpus",
  status="READY")

T("d3_null_calibration", "Archaeon D3 null calibration (exact vs simulated false-alarm rate)", "archaeon/calibrate_d3_null.py",
  "calibration_battery", det="SEEDED",
  inputs="band width, n, seed", outputs="false-alarm rate; exact and simulated agree (PARITY); tighter band raises rate",
  scope="calibrated false-alarm rate of the D3 detector at a given band", forbidden="calibration of D3 is not calibration of D1-D6",
  status="NEEDS_VALIDATION", reason="PARITY/REPETITION/SYNTHETIC_SIGNAL only; no REJECT-family control (needs a SYNTHETIC_NULL: no-effect input at nominal alpha)",
  batteries=["output_replay_null_statistic_calibration"])

T("canon_r11_calibration", "Techne canon R11 calibration audit (declared-vs-reported, witness for refutation)",
  "techne/ladder_circuits/canon_r11_calibration.py", "calibration_battery",
  inputs="forecasts with declared probabilities + external ledger of outcomes",
  outputs="calibration score; selective reporting detected by ledger; refuted-without-witness is unsupported",
  scope="whether a forecaster's declared confidences were calibrated and completely reported",
  forbidden="calibration on reported items says nothing about unreported ones unless the external ledger is complete",
  status="READY", batteries=["claim_to_reproduction"])

T("h3_replay", "Archaeon H3 replay (seeded archive + input-fingerprinting stream manifest)", "archaeon/producer/h3_replay.py",
  "replay_harness", det="SEEDED", inputs="birth stream + seed", outputs="archive top-k; manifest fingerprints inputs; bad birth_status refused",
  scope="deterministic re-derivation of an H3 archive from preserved births", forbidden="replay equality is not correctness of the births",
  status="READY", batteries=["artifact_provenance_hash_reader_invariant"])

T("hypothesis_minimiser", "Techne hypothesis first-check (property-based minimiser)", "techne/acquisition/checks/hypothesis_first_check.py",
  "falsifier", deps=["hypothesis"], dep_status="MISSING", dep_detail="python package `hypothesis` is not installed in the Keeper's interpreter (ERROR in run 3); Techne inventory reports it green on its host",
  inputs="a property + strategy", outputs="minimal counterexample", scope="shrunken counterexample for a falsified property",
  forbidden="none established: never executed here", status="NEEDS_DEPENDENCY",
  reason="ModuleNotFoundError: hypothesis (hypothesis_minimiser.ACCEPT.h1_minimiser_runs ERROR)")

T("capability_gap_fixture", "Techne capability-gap fixture battery (pytest)", "techne/tests/test_capability_gap_fixture.py",
  "calibration_battery", deps=["cvxpy", "pytest"], dep_status="MISSING", dep_detail="cvxpy absent; the pytest battery is RED here for that reason",
  inputs="pytest", outputs="green/red", scope="unknown here: never green on this host",
  forbidden="a RED caused by a missing package is not a capability finding (memory feedback_instrument_error_is_not_evidence)",
  status="NEEDS_DEPENDENCY", reason="capability_gap_fixture.ACCEPT.pytest_battery_green FAIL: cvxpy missing")

T("null_bound_reference", "Atalanta null_bound reference (declared bound required; emission-keyed bound fails)",
  "roles/Atalanta/reference/null_bound.py", "invariant_checker",
  inputs="a claimed bound + emissions", outputs="raises on undeclared bound; pytest reference battery",
  scope="whether a bound was declared before emissions were counted", forbidden="emission != productivity (Atalanta root law)",
  status="READY", author_tests=["roles/Atalanta/reference/test_null_bound.py"])

T("lean_runtime", "Lean runtime session (locate REPL, check theorem)", "agents/_shared/external_tools/lean_runtime/session.py",
  "proof_checker", deps=["lean", "lake"], dep_status="HOST_LOCAL", dep_detail="no lean/lake binary on the Keeper host; Techne inventory reports 32/32 on its host -- disputed, not reconciled",
  inputs="Lean theorem text", outputs="checked / rejected", scope="unknown here: never executed on this host",
  forbidden="none established", status="NEEDS_DEPENDENCY", reason="both cases ERROR: locator finds no REPL")

T("library_leak", "Vivarium library-leak check (component equal to task answer)", "vivarium/viv/library_leak.py", "anti_cheat",
  deps=["proteus.eval.boolean"], inputs="library components + task answer", outputs="flagged / clean",
  scope="whether a library component IS the task answer (exact leak)", forbidden="an unflagged library can still leak by composition",
  status="READY", batteries=["claim_to_reproduction"])

T("anti_anchors_registry", "Techne anti-anchor registry (attestation-graded jsonl)", "techne/registry/anti_anchors.jsonl", "inspection",
  inputs="none (data file)", outputs="rows with attestation grades", scope="what anchors Techne has registered against",
  forbidden="a registry row is a claim, not a control run", status="NEEDS_VALIDATION",
  reason="data file with an ACCEPT parse only; no REJECT-family control applies")

T("a148_obstruction", "sigma_kernel A148 obstruction analysis (unanimous kill rate over families)", "sigma_kernel/a148_obstruction.py",
  "failure_classifier", inputs="family csv/json under sigma_kernel/ (historical cwd convention)",
  outputs="unanimous kill rate (rate, n_unanimous, n_present) per family",
  scope="reproduce the historical A148 obstruction numbers from preserved family files",
  forbidden="the module does NOT import as a package or with sigma_kernel on sys.path (2 FAILs recorded as evidence, not repaired); only the fresh-interpreter-in-sigma_kernel convention works",
  status="NEEDS_ADAPTER", reason="in-process import FAILs recorded as evidence (not repaired); invoke through NT-055 adapters/sigma_kernel_runner.py, which is READY",
  adapter="engine/necropolis/workshop/adapters/sigma_kernel_runner.py",
  kfm=["in-process import fails (a148_obstruction.ACCEPT.imports_as_package / imports_in_process_with_sigma_kernel_on_path FAIL) -- historical convention was cwd-relative"])

T("bswcd_null", "Harmonia block-shuffle (BSWCD) null", "harmonia/nulls/block_shuffle.py", "null_generator", det="SEEDED",
  inputs="paired series + stratifier", outputs="null distribution preserving within-stratum structure",
  scope="dependence beyond what the stratifier explains", forbidden="collapse under the null means stratifier-only dependence, not no dependence",
  status="READY", batteries=["output_replay_null_statistic_calibration"])

T("pm_bootstrap", "prometheus_math.research.bootstrap (matched-null test, permutation test, bootstrap CI, Holm-Bonferroni)",
  "prometheus_math/research/bootstrap.py", "resampler", det="SEEDED",
  inputs="samples / statistic / null generator", outputs="p (floor 1/(n+1)), CI, corrected p list (hand-checked)",
  scope="resampling p-values with the correct floor", forbidden="p floor 1/(n+1): 'p=0' is never reportable",
  status="READY", batteries=["output_replay_null_statistic_calibration"])

T("kill_resurrection", "Harmonia kill-resurrection audit (relation evaluator + rule of three)",
  "harmonia/diagnostics/kill_resurrection_audit.py", "falsifier",
  inputs="kill records with relations + current values", outputs="resurrected / stays dead; rule-of-three bound",
  scope="whether any killed claim would survive re-evaluation", forbidden="0 resurrections on a 46% chance floor is not a strong survivor claim (memory 2026-08-19)",
  status="READY")

T("fossil_inference", "Archaeon fossil inference (two fossils pin target set; tampering raises)", "archaeon/producer/fossil_inference.py",
  "invariant_checker", inputs="fossil rows (hamming scores)", outputs="target set equal to brute force; contradiction on tampered score",
  scope="what the preserved fossils jointly imply about the target", forbidden="non-integer scores are refused, not rounded",
  status="READY", author_tests=["archaeon/tests/test_fossil_inference.py"], batteries=["artifact_provenance_hash_reader_invariant"])

T("baseline_costume", "Harmonia baseline-costume detector (claim vs every baseline; identity ties vacuous)",
  "harmonia/primitives/baseline_costume.py", "negative_control",
  inputs="claim score + baseline scores", outputs="COSTUME / NOT_COSTUME / VACUOUS",
  scope="whether a claim only beats the marginal majority", forbidden="not-costume is not novelty",
  status="READY", author_tests=["harmonia/primitives/test_baseline_costume_parity.py"])

T("kill_scheme_info_audit", "Harmonia kill-scheme information audit (MI vs null95)", "harmonia/primitives/kill_scheme_info_audit.py",
  "statistical_test", det="SEEDED", inputs="labels + coordinates", outputs="MI with null95; independent labels below null95",
  scope="whether kill labels carry coordinate information", forbidden="MI above null is not causation",
  status="READY", batteries=["output_replay_null_statistic_calibration"])

T("ladder_leakage_audit", "Harmonia ladder leakage audit (exact-equality leak fields; chance floor)",
  "harmonia/diagnostics/ladder_leakage_audit.py", "anti_cheat",
  inputs="probe objects", outputs="leak fields found by exact equality; chance floor = majority rate; R6 declared leak reproduced",
  scope="exact-value leakage of the answer into the probe", forbidden="a str-transformed key escapes detection (PERTURBATION INFO): clean is exact-equality-clean only",
  status="READY_WITH_CAVEAT", caveat="exact-equality scope; transformed leaks are invisible",
  kfm=["INFO ladder_leakage_audit.PERTURBATION.str_transformed_key_escapes_detection"])

T("nemesis_cheatlib", "Nemesis cheatlib (chance floor, constant responder)", "roles/Nemesis/science/cheatlib.py", "anti_cheat",
  inputs="answers + ground truth", outputs="chance floor (hand parity); constant responder scores exactly majority",
  scope="the floor any tool must beat", forbidden="None answers count as answers (CORRUPT_INPUT INFO) -- filter first",
  status="READY_WITH_CAVEAT", caveat="None answers are not filtered", kfm=["INFO nemesis_cheatlib.CORRUPT_INPUT.none_answers_count_as_answers"],
  author_tests=["roles/Nemesis/science/tests/test_cheatlib.py"])

T("pronoia_liveness", "Pronoia productive-liveness classifier (L0-L5)", "roles/Pronoia/science/productive_liveness.py",
  "liveness_attestor", inputs="attempt/success/heartbeat timestamps", outputs="PRODUCTIVE / STALLED / FAILING / INCOHERENT",
  scope="liveness class from artifacts, not stdout", forbidden="a heartbeat is not a productivity signal",
  status="READY", author_tests=["roles/Pronoia/science/test_productive_liveness.py"])

T("herakles_c3_null_check", "Herakles EvCA C3 null check (transform digest; identical needs more than accuracy agreement)",
  "herakles/evca/c3_null_check.py", "differential_test",
  inputs="two runs with transform fields + digests", outputs="IDENTICAL / INDETERMINATE / NOT_IDENTICAL",
  scope="whether two runs are the same computation", forbidden="accuracy agreement alone cannot buy IDENTICAL",
  status="READY", batteries=["producer_fixture_consumer_differential"])

T("measurement_guard", "Techne measurement guard (control must pass and match type before a value is admitted)",
  "techne/lib/measurement_guard.py", "invariant_checker",
  inputs="measurement + control result", outputs="admitted value or refusal", scope="that a measurement had a passing, type-matched control",
  forbidden="admission is not accuracy", status="READY")

T("icarus_tier_oracle", "Icarus tier oracle (declares its cheat fields)", "agents/icarus/tier_oracle.py", "grader",
  inputs="tier + reasoner output", outputs="grade; CHEAT_FIELDS declared", scope="which fields a reader could cheat from",
  forbidden="declaration is not prevention", status="NEEDS_VALIDATION", reason="ACCEPT only; no REJECT-family control written yet")

T("attacks_preflight", "attacks.preflight dead-field detector", "attacks/preflight.py", "invariant_checker",
  inputs="rows + field names", outputs="Finding(check, ok, detail) per field; fires on absent column, silent on varying",
  scope="whether a ledger column is dead (never populated)", forbidden="a live column is not a correct one",
  status="READY", batteries=["artifact_provenance_hash_reader_invariant"])

T("stygian_bocpd", "Stygian BOCPD changepoint loader", "charon/agents/stygian/loaders/_bocpd.py", "statistical_test",
  inputs="series", outputs="changepoint posterior; planted shift located; stationary series quiet",
  scope="location of a mean shift", forbidden="a changepoint is not a cause", status="READY",
  author_tests=["charon/agents/stygian/tests/test_bocpd_g10_v2.py"], frank=["FRANK-003"])

T("vivarium_spec_hash", "Vivarium spec hash (key-order invariant; invalid spec refused)", "vivarium/viv/spec.py", "manifest_hash",
  inputs="spec dict", outputs="hash; one element changes hash", scope="identity of an experiment spec",
  forbidden="equal hash is equal spec, not equal outcome", status="READY", batteries=["artifact_provenance_hash_reader_invariant"])

T("divergence_decomposition", "Harmonia divergence decomposition (ceiling and bounds)", "harmonia/diagnostics/divergence_decomposition.py",
  "statistical_test", inputs="divergence components", outputs="ceiling, lower/upper bounds (hand values)",
  scope="how much of a divergence is attributable below the ceiling", forbidden="below ceiling gives zero lower bound, not zero effect",
  status="READY")

T("pm_instrument_contract", "prometheus_math instrument contract (meter certified only with a negative)",
  "prometheus_math/instrument_contract.py", "anti_cheat",
  inputs="meter callable + positive/negative fixtures", outputs="certified / refused (constant signal, ignored invalid input, no negative)",
  scope="whether a meter responds to its inputs", forbidden="certified is not calibrated", status="READY")

T("pm_degenerate_audit", "prometheus_math degenerate audit (conflating vs refusing measures)", "prometheus_math/degenerate_audit.py",
  "negative_control", inputs="measure callable", outputs="flagged when it conflates distinct inputs; not flagged when it refuses",
  scope="B1 degeneracy of a measure", forbidden="not-degenerate is not informative", status="READY")

T("eos_intake", "Eos intake gate (referent must resolve; unknown sought state refused)", "agents/eos/src/intake.py",
  "provenance_validator", mut="WRITES_FILES",
  inputs="candidate acquisition Item", outputs="classification; anchor with no referent cannot reach pending",
  scope="whether a claim names a real referent in the tree", forbidden="a resolving referent is not a true claim",
  status="READY", author_tests=["agents/eos/tests/test_intake.py"])

T("comms_identity", "comms.identity environment identity check (fails closed on unknown env / wrong DB)", "comms/identity.py",
  "liveness_attestor", inputs="db connection + environment name", outputs="MATCH / refusal (rolled back)",
  scope="that a connection is the canonical store it claims to be", forbidden="identity is not freshness",
  status="READY", author_tests=["comms/tests/test_identity.py"])

T("charon_c1c2", "Charon C1/C2 checks (fingerprinted receipt; transport-failure residue exclusion)", "charon/probe/c1c2_checks.py",
  "provenance_validator", inputs="receipt + loader rows", outputs="PASS / FAIL / INDETERMINATE per check",
  scope="C1 unfingerprinted pool and C2 transport-failure residue rulings (memory 2026-09-01)",
  forbidden="INDETERMINATE is not PASS", status="READY", author_tests=["charon/probe/tests/test_c1c2_checks.py"],
  batteries=["artifact_provenance_hash_reader_invariant"])

T("control_certifier", "Techne control certifier + defect battery (every defect shape must be caught)",
  "techne/ladder_circuits/control_certifier.py", "calibration_battery", deps=["techne.ladder_circuits.defect_battery"],
  inputs="a battery of checks", outputs="CERTIFIED_CLEAN / defects caught / UNCERTIFIED when a shape is missing",
  scope="whether a battery catches each named defect shape", forbidden="clean on the shapes tested only (gate blind spots are structural)",
  status="READY", batteries=["output_replay_null_statistic_calibration"])

T("apollo_e9_score", "Apollo E9 scorer (mix-adjusted score)", "apollo/scripts/e9_score.py", "scorer",
  inputs="battery json + outputs", outputs="score; published 0.0667 reproduced (PARITY)",
  scope="reproduces the published E9 number from preserved inputs", forbidden="parity with a published number is not correctness of the number",
  status="NEEDS_VALIDATION", reason="PARITY only; no REJECT-family control")


# ---------------------------------------------------------------------------
# NECROPOLIS-BUILT adapters (LAYER: NECROPOLIS_ADAPTER); tool_key == run_controls group
# ---------------------------------------------------------------------------
_AD = "engine/necropolis/workshop/adapters/"


def A(key, name, fname, cls, **kw):
    kw.setdefault("layer", "NECROPOLIS_ADAPTER")
    kw.setdefault("origin", "NECROPOLIS_BUILT")
    T(key, name, _AD + fname, cls, **kw)


A("adapters_instrument_null", "Instrument-null probe (tautological / nondeterministic / unmeasurable / responsive)",
  "instrument_null.py", "negative_control", det="SEEDED",
  inputs="a statistic callable", outputs="TAUTOLOGICAL / NONDETERMINISTIC / UNMEASURABLE / SORT_INVARIANT / RESPONSIVE",
  scope="whether a statistic can respond to its inputs at all", forbidden="RESPONSIVE is not calibrated",
  status="READY", batteries=["historical_verdict_original_corrected"])

A("adapters_pollux_replay", "Pollux statistic replay (historical construction, unchanged daemon logic)", "pollux_statistic_replay.py",
  "replay_harness", deps=["charon.agents.pollux.daemon"],
  inputs="two sequences", outputs="historical_statistic + instrument-null reading", scope="what Pollux WOULD have said, and why that is not evidence",
  forbidden="never repair the daemon and call the repaired number history", status="READY", frank=["FRANK-004"],
  batteries=["historical_verdict_original_corrected"])

A("adapters_resampling_null", "Random-subset resampling null + KS + split-half / Poisson controls (FRANK-004 organ 6)",
  "resampling_null.py", "resampler", det="SEEDED", deps=["charon.agents.pollux.daemon", "scipy (crosscheck only)"],
  inputs="two value sequences + pool", outputs="two_sample_read verdict with p_lower, p_bonferroni, split_half, negative control",
  scope="whether two selected subsets have gap distributions closer than random subsets of the pool",
  forbidden="the lower tail of a same-distribution KS null is uniform at alpha for ANY iid continuous gap law (PERTURBATION INFO): split-half positive control cannot pass; only an identical gap multiset is visible",
  status="READY_WITH_CAVEAT", caveat="FRANK-004 kill condition (2) fires on synthetic data before any grave is read; upper-tail direction or a different statistic is the well-posed read",
  kfm=["INFO adapters_resampling_null.PERTURBATION.split_half_control_fails_at_alpha_rate_for_iid_continuous: hit rate 0.0133 at alpha 0.00556, 0/30 resolvable"],
  frank=["FRANK-004"], batteries=["output_replay_null_statistic_calibration"])

A("adapters_jsonl_census", "JSONL ledger census (rows, malformed lines, dead/partial fields, verdict columns, time ranges)",
  "jsonl_ledger_census.py", "artifact_reader",
  inputs="a jsonl path", outputs="census dict; malformed lines counted not dropped; missing file reported not invented",
  scope="what a preserved ledger contains", forbidden="a dead field is not a dead instrument", status="READY",
  batteries=["artifact_provenance_hash_reader_invariant"])

A("adapters_git_census", "Git-history census and read-only recovery (git show into scratch)", "git_history_census.py",
  "artifact_reader", deps=["git"],
  inputs="a repo path", outputs="history, deleted_in, recovered file + sha256; mutating verbs and live-tree recovery refused",
  scope="when an instrument existed and what its bytes were", forbidden="recovered bytes are not a runnable instrument", status="READY",
  batteries=["artifact_provenance_hash_reader_invariant"])

A("adapters_consumer_trace", "Consumer trace (who imports / mentions a path)", "consumer_trace.py", "graph_diagnostic", deps=["rg (optional)"],
  inputs="a target path", outputs="hits, importers, n_external; self-reference excluded",
  scope="whether anything consumed an instrument's output", forbidden="a grep hit is not an executed consumer", status="READY",
  batteries=["claim_to_reproduction"])

A("adapters_manifest_verify", "Manifest verify with coverage (uncovered files, manifest self-hash)", "manifest_verify.py",
  "provenance_validator", deps=["comms.manifest"],
  inputs="a directory", outputs="COVERED / UNCOVERED_FILES / HASH_MISMATCH / NO_MANIFEST + manifest_self_hash_lf",
  scope="coverage of a manifest over its directory", forbidden="COVERED without an external anchor for manifest_self_hash_lf is still launderable",
  status="READY", batteries=["artifact_provenance_hash_reader_invariant"])

A("adapters_pg_probe", "Read-only Postgres probe (SELECT-only guard, READ ONLY transaction, identity check)", "pg_readonly_probe.py",
  "db_probe", deps=["psycopg or psycopg2", "PG credentials via environment"], dep_status="HOST_LOCAL",
  dep_detail="TCP 192.168.1.202:5432 observed reachable 2026-09-13; driver/credentials not exercised by any control",
  inputs="conn + sql", outputs="rows; 12 write statements refused; never commits",
  scope="read a live store without writing", forbidden="no control issued a real query: the guard is validated, the connection path is not",
  status="READY_WITH_CAVEAT", caveat="guard validated offline; no live query executed", batteries=["claim_to_reproduction"])

A("adapters_sigma_runner", "sigma_kernel fresh-interpreter runner (historical cwd convention)", "sigma_kernel_runner.py", "replay_harness",
  inputs="module + expression", outputs="json result; missing module reported", scope="execute sigma_kernel modules as they were historically run",
  forbidden="running is not reproducing: inputs must be the preserved family files", status="READY",
  kfm=["INFO adapters_sigma_runner.PARITY.unanimous_kill_rate_hand_check: source excerpt only, no numeric parity yet"])

A("adapters_verdict_lint", "Literal-verdict lint (functions that return the same verdict unconditionally)", "literal_verdict_lint.py",
  "anti_cheat", inputs="python paths", outputs="UNCONDITIONAL_VERDICT findings",
  scope="functions that CANNOT discriminate", forbidden="an unflagged function is not shown to discriminate", status="READY",
  kfm=["INFO adapters_verdict_lint.ACCEPT.scan_of_necropolis_evidence_scripts: 35 files, 0 findings"])

A("adapters_z3_redirect", "Techne acquisition check runner with ledger redirect", "z3_receipt_redirect.py", "replay_harness",
  deps=["z3-solver"], inputs="check script path", outputs="fixture + ledger_touched (must be empty)",
  scope="run an append-only-ledger check without appending", forbidden="a clean ledger_touched is measured by mtime only",
  status="NEEDS_VALIDATION", reason="ACCEPT only so far; z3_oracle.PARITY exercises the same path but under its own key")


# ---------------------------------------------------------------------------
# WAVE 3 : inspected, author-tests only or dependency/DB blocked (no Keeper controls yet)
# ---------------------------------------------------------------------------
def N(key, name, path, cls, **kw):
    kw.setdefault("status", "NEEDS_VALIDATION")
    kw.setdefault("reason", "author tests only; no Keeper control written (charter VI)")
    T(key, name, path, cls, **kw)


N("erebos_residue_revocation", "Erebos residue revocation registry", "charon/agents/erebos/_residue_revocation.py", "residue_gate",
  inputs="revocation records + residues", outputs="active residues", scope="which residues were still active at a date",
  forbidden="active is not validated", author_tests=["charon/agents/erebos/tests/test_residue_revocation.py"], frank=["FRANK-003"])
N("erebos_kill_tensor", "Erebos KillTensor (plugin x domain x invariant x kill_pattern counts)", "charon/agents/erebos/_kill_tensor.py",
  "coverage_diagnostic", inputs="ledger rows", outputs="sparse count tensor, marginals", scope="coverage of kills over four axes",
  forbidden="a populated cell is a count, not a law", frank=["FRANK-003"])
N("stygian_bootstrap_ci", "Stygian percentile bootstrap CI", "charon/agents/stygian/loaders/_bootstrap_ci.py", "resampler", det="SEEDED",
  inputs="sample + statistic", outputs="CI", scope="CI of a statistic", forbidden="a CI is not a null",
  author_tests=["charon/agents/stygian/tests/test_bootstrap_ci_g23_v2.py"], frank=["FRANK-003"])
N("stygian_westfall_young", "Stygian Westfall-Young max-T permutation null over binary splits",
  "charon/agents/stygian/loaders/_mahler_composition_helpers.py", "null_generator", det="SEEDED",
  inputs="population + splits", outputs="family-wise corrected p", scope="multiple-comparison-corrected split effects",
  forbidden="corrected p is not effect size", author_tests=["charon/agents/stygian/tests/test_westfall_young_multi_binary.py"], frank=["FRANK-003"])
N("descriptor_collapse_audit", "Harmonia descriptor-collapse audit (Pearson / dCor / KSG-MI / shuffled null / conditional MI)",
  "harmonia/memory/diagnostics/descriptor_collapse_audit.py", "statistical_test", det="SEEDED", deps=["numpy", "scipy"],
  inputs="dict of 1-D descriptors", outputs="CLEAR / STRUCTURAL_COUPLING_SUSPECTED with per-pair tiers",
  scope="whether archive axes are secretly dependent", forbidden="CLEAR on the shuffled null is not independence in the archive's own distribution",
  author_tests=["harmonia/memory/diagnostics/test_descriptor_collapse_audit.py"])
N("battery_chain", "Techne battery-chain audit (ACCUMULATING vs DESTROYING)", "techne/ladder_circuits/battery_chain.py", "falsifier",
  inputs="chain of battery checks", outputs="direction + resolution", scope="whether later checks add or remove evidence",
  forbidden="accumulating is not sufficient", author_tests=["techne/ladder_circuits/tests/test_battery_chain.py"])
N("fossil_isolation", "Techne fossil isolation battery", "techne/tests/test_fossil_isolation.py", "calibration_battery", deps=["pytest"],
  inputs="pytest", outputs="12 passed", scope="that fossil readers are isolated from live state", forbidden="green is green on its fixtures",
  author_tests=["techne/tests/test_fossil_isolation.py"])
N("archaeon_calibration", "Archaeon detector calibration battery D1-D6 (planted / no-effect controls)", "archaeon/calibrate.py",
  "calibration_battery", det="SEEDED", inputs="detector + synth generators", outputs="null-fire rate, hit rate, power curves",
  scope="per-detector calibration", forbidden="calibrated on synth is not calibrated on the corpus",
  author_tests=["archaeon/tests/test_detectors.py"])
N("archaeon_c3_readout", "Archaeon C3 readout (exact-symmetry null identity, ICC1)", "archaeon/producer/c3_readout.py", "statistical_test",
  deps=["viv.research_experiment_queue (DB)"], dep_status="HOST_LOCAL", dep_detail="fetch() reads the Vivarium DB; icc1/null_identity are pure",
  inputs="CS-C3-2 rows", outputs="readout markdown", scope="exact-symmetry check and ICC on preserved rows",
  forbidden="ICC is agreement, not truth", author_tests=["archaeon/tests/test_c3_readout.py"])
N("archaeon_h1h0_readout", "Archaeon H1/H0 readout (spec_hash dedup; REFUSE_INDEPENDENT_ARMS)", "archaeon/producer/h1h0_readout.py",
  "invariant_checker", deps=["viv DB for fetch"], dep_status="HOST_LOCAL",
  inputs="rows", outputs="readout with degeneracy refusal", scope="two 'independent' arms with one spec_hash are refused",
  forbidden="distinct spec_hash is not independence", author_tests=["archaeon/tests/test_h1h0_readout.py"])
N("archaeon_h5_reference", "Archaeon H5 exact neighbourhood reference + frequency-preserving null decoder",
  "archaeon/producer/h5_reference.py", "exact_oracle", inputs="decoder + class map", outputs="exact reference over 49,152 edges; sampled-vs-exact check",
  scope="exact ground truth for H5", forbidden="exact under one decoder", author_tests=["archaeon/tests/test_h5_reference.py"])
N("archaeon_stage0_fragility", "Archaeon stage-0 fragility survey (pinned-blob replay + positive control)",
  "archaeon/stage0_fragility_survey.py", "replay_harness", deps=["git blob 0e2d654851ae"],
  inputs="frozen S17 predictor blob + corpus", outputs="PASS/KILL gate with positive control", scope="replay of a pinned predictor",
  forbidden="replay equality is not predictor validity", author_tests=["archaeon/tests/test_stage0_survey.py"])
N("arachne_frozen_specimen", "Arachne frozen specimen loader with manifest verification", "roles/Arachne/science/specimen.py", "loader",
  inputs="archive run dir", outputs="Specimen; manifest verified", scope="that the archived graph is the archived graph",
  forbidden="verified bytes, not verified science", author_tests=["roles/Arachne/science/tests/test_specimen_and_stats.py"])
N("herakles_workspace_guard", "Herakles workspace guard (assert_not_canonical / is_main_worktree)", "herakles/workspace.py",
  "invariant_checker", inputs="cwd", outputs="raises on the canonical worktree", scope="execution-context guard",
  forbidden="not-canonical is not isolated", author_tests=["herakles/tests/test_workspace.py"])
N("incubation_d_vm", "incubation_d homoiconic VM (typed failure descriptors, block hash)", "incubation_d/vm/machine.py", "replay_harness",
  inputs="object program", outputs="result or VMError.descriptor; deterministic", scope="deterministic replay substrate",
  forbidden="determinism of the VM is not determinism of the agent that used it", author_tests=["incubation_d/tests/test_vm.py"])
N("pattern_30_coupling", "Harmonia Pattern 30 algebraic-identity coupling detector (sympy)", "harmonia/sweeps/pattern_30.py",
  "symbolic_oracle", deps=["sympy"], inputs="X_expr, Y_expr, known identities", outputs="0 CLEAN / coupled class",
  scope="whether a correlation is an algebraic identity", forbidden="CLEAN under the listed identities only",
  author_tests=["harmonia/sweeps/test_sweeps.py"])
N("vivarium_orphan_verdicts", "Vivarium orphan-verdict / scope-recurrence / degeneracy / result-schema checks", "vivarium/viv",
  "schema_validator", inputs="viv result rows", outputs="orphan verdicts, scope recurrences, WP0B degeneracy, WP0F schema errors",
  scope="structural integrity of Vivarium results", forbidden="schema-valid is not true",
  author_tests=["vivarium/tests/test_orphan_verdicts.py", "vivarium/tests/test_scope_recurrence.py",
                "vivarium/tests/test_wp0b_degeneracy.py", "vivarium/tests/test_wp0f_result_schema.py"])
N("ergon_packet_controls", "Ergon probe packet invariants + leak-gate fire tests", "ergon/probe/packet_invariants.py", "anti_cheat",
  inputs="rendered packets", outputs="invariant violations; gate fires on planted leak", scope="that the packet leak gate fires when it should",
  forbidden="firing on planted leaks is not firing on real ones", author_tests=["ergon/probe/tests/test_packet_leak_gate_fire.py"])
N("harmonia_verifier_lens_z3", "Harmonia verifier lens (z3-backed)", "harmonia/experiments/verifier_lens.py", "proof_checker", deps=["z3-solver"],
  inputs="phase-0 reasoning claims", outputs="verified / refuted", scope="z3 verification of stated claims",
  forbidden="a verifier that cannot execute a claim must return NOT_EXAMINED, not SURVIVES", author_tests=["harmonia/experiments/test_verifier_z3.py"])
N("coeus_trace_defects", "Coeus trace-defects (perm_p_difference, magnitude-matched noise null over Nous->RLVF->forge)",
  "roles/Coeus/science/trace_defects.py", "statistical_test", det="SEEDED", inputs="Nous/forge ledgers", outputs="F1-F4 defect traces with permutation p",
  scope="whether Nous scores steered forge selection beyond noise", forbidden="a traced defect is a defect in the ledger, not in the world",
  frank=["FRANK-002"])
N("charon_generator_quality_probe", "Charon generator quality probe (COUNTER_EQUIVALENT kill patterns per generator)",
  "charon/quality/generator_quality_probe.py", "failure_classifier", inputs="kill ledger", outputs="per-generator classification",
  scope="which generators only ever produce one kill pattern", forbidden="counter-equivalence is not uselessness", frank=["FRANK-003"])
N("failure_primitive_atlas", "Harmonia failure-primitive atlas detectors FP-001..004 + void map",
  "harmonia/primitives/failure_primitives.py", "failure_classifier", inputs="rows", outputs="FP flags, atlas validation, void report",
  scope="typed failure shapes over a run", forbidden="an FP flag is a shape, not a cause (failure-signature doctrine)")
N("lane_exhaustion_audit", "Harmonia lane exhaustion rubric (EXHAUSTION@v1 over hand-curated ledger)",
  "harmonia/diagnostics/lane_exhaustion_audit.py", "failure_classifier", inputs="event ledger", outputs="rubric verdict per lane",
  scope="class-relative exhaustion of a lane", forbidden="void != gap; only class-relative exhaustion is certifiable")
N("proteus_specimen_gate", "Proteus specimen gate (BYTES / SHAPE / MEANING verification) + audit identity",
  "proteus/integration/specimen_gate.py", "provenance_validator", inputs="specimen + AUDIT_IDENTITY.json", outputs="three-level verdict",
  scope="that a specimen is the stamped specimen", forbidden="MEANING level is a declared check, not semantic truth")

# dependency / DB blocked
T("heph_knockout_ablation", "Hephaestus knockout ablation (Gate 6; per-engine disable)", "agents/hephaestus/src/knockout_ablation.py",
  "falsifier", det="SEEDED", model="YES", deps=["openai", "diversity_forge"], dep_status="MISSING",
  dep_detail="ModuleNotFoundError: openai raised by diversity_forge.py at import; the ablation logic itself was not reached",
  inputs="engines, n-per-category, seed", outputs="accuracy with each engine disabled", scope="unknown here",
  forbidden="none established", status="NEEDS_DEPENDENCY", reason="openai package absent; dead import in a sibling module", frank=["FRANK-002"])
T("rhea_ablation", "Rhea ablation + eval_v2 66-trap battery (fine-tuned verifier)", "rhea/src/ablation.py", "calibration_battery",
  model="YES", deps=["transformers", "torch"], dep_status="MISSING", dep_detail="transformers absent",
  inputs="model checkpoint", outputs="trap scores per ablation", scope="unknown here", forbidden="none established",
  status="NEEDS_DEPENDENCY", reason="transformers absent")
T("lattice_void_miner", "Harmonia lattice void miner (product-measure decision procedure + certificate verifier + 7 nulls)",
  "harmonia/primitives/lattice_void_miner.py", "exact_oracle", deps=["prometheus_math/databases/knots.json.gz"], dep_status="MISSING",
  dep_detail="knots.json.gz absent: author tests 1 failed / 3 passed / 7 errors here",
  inputs="LatticeSpec", outputs="hold counts + certificate", scope="exhaustive lattice evaluation with certificate",
  forbidden="7 author-test errors here are a data-absence fact, not an instrument fact", status="NEEDS_DEPENDENCY",
  reason="knots catalog absent", author_tests=["harmonia/experiments/test_lattice_void_miner.py"])
T("theseus_content_aware_promote", "Theseus content-aware promotion gate (F2 null, threshold 0.10)", "theseus/scoring/content_aware_promote.py",
  "residue_gate", deps=["prometheus_math/databases/knots.json.gz (one test)"], dep_status="MISSING",
  dep_detail="author tests 1 failed / 19 passed; failing test needs the knots catalog",
  inputs="candidate + null scores", outputs="promote / hold", scope="F2-null-scored promotion", forbidden="promotion is not validation",
  status="NEEDS_DEPENDENCY", reason="one author test blocked on knots catalog; others green", author_tests=["theseus/tests/test_content_aware_promote.py"])
T("evidence_wiki_store_identity_guard", "Evidence-wiki store identity guard (ew.db)", "evidence_wiki/tests/test_store_identity_guard.py",
  "liveness_attestor", deps=["ew.db", "Postgres credentials"], dep_status="HOST_LOCAL", dep_detail="3 failed here: needs the live store",
  inputs="store connection", outputs="identity verdict", scope="unknown here", forbidden="none established",
  status="NEEDS_DEPENDENCY", reason="DB-bound; not executable without credentials", author_tests=["evidence_wiki/tests/test_store_identity_guard.py"])
T("comms_instances", "comms instance registry (api)", "comms/api.py", "db_probe", deps=["Postgres credentials"], dep_status="HOST_LOCAL",
  dep_detail="1 passed / 6 errors here: needs EW_DB credentials", inputs="db", outputs="instance rows", scope="who is registered",
  forbidden="registered is not alive (status columns are fossils)", status="NEEDS_DEPENDENCY", reason="DB-bound",
  author_tests=["comms/tests/test_instances.py"])
T("thesauros_audit_all_tables", "Thesauros audit_all_tables (per-table counts, null rates, orphans, staleness)", "thesauros/audit_all_tables.py",
  "db_probe", deps=["Postgres credentials"], dep_status="HOST_LOCAL", dep_detail="connects at import; NOT executed",
  inputs="db", outputs="audit report", scope="unknown here", forbidden="none established", status="NEEDS_ADAPTER",
  inspected=True, notes="must be wrapped by pg_readonly_probe before any coroner use; connects at import time")
T("alethelia_rules", "Alethelia anomaly rules (stale heartbeats, zombies, dormant shadow input)", "agents/alethelia/alethelia.py",
  "liveness_attestor", deps=["Postgres credentials"], dep_status="HOST_LOCAL", inputs="db + git + queues",
  outputs="rule report with queries", scope="fleet anomalies at a moment", forbidden="a rule firing is not a diagnosis",
  status="NEEDS_VALIDATION", reason="author test file collects no tests (rc 3); rule logic not controlled",
  author_tests=["agents/alethelia/test_alethelia.py"])
T("icarus_holdout_R1", "Icarus holdout R1 battery", "agents/icarus/holdout/test_holdout_R1.py", "calibration_battery", deps=["pytest"],
  inputs="pytest", outputs="3 failed here", scope="unknown", forbidden="a red battery whose cause is unread is not a finding",
  status="BROKEN", reason="3 failed in author run; cause not diagnosed (recorded, not repaired)",
  author_tests=["agents/icarus/holdout/test_holdout_R1.py"])

# git-history only (noesis/ was gitignored at 8144f4f01; last tree containing it is 762d4f87)
T("noesis_verify_chains", "Noesis sympy chain verifier family (22/45/72/44 named checks)", None, "symbolic_oracle",
  origin="GIT_HISTORY", historical_path="noesis/v2/verify_chains.py", source_commit="762d4f8721b7f053d91b1d5bdc5f43db795d53dc",
  deps=["sympy"], inputs="none (self-contained)", outputs="Total: 22 | PASS: 20 | FAIL: 2 (replayed from a recovered copy 2026-09-13)",
  scope="what Noesis' own checks said about its derivation chains", forbidden="each verify(name, condition) is an author-chosen predicate; PASS counts are opinion-weighted",
  status="HISTORICAL_ONLY", notes="recovered via git show; exit 1 only because an F:/ path no longer exists")
T("noesis_invariant_extractors", "Noesis invariant extractors (12 scalar descriptors)", None, "feature_extractor",
  origin="GIT_HISTORY", historical_path="noesis/the_maths/invariant_extractors.py", source_commit="762d4f8721b7f053d91b1d5bdc5f43db795d53dc",
  deps=["numpy"], inputs="1-D array", outputs="12 scalars", scope="descriptor values", forbidden="descriptors are coordinates, not laws",
  status="HISTORICAL_ONLY")
T("noesis_tensor_completion", "Noesis tensor completion WITHOUT holdout (forensic value is what it lacks)", None, "model_runner",
  origin="GIT_HISTORY", historical_path="noesis/v2/tt_completion.py", source_commit="762d4f8721b7f053d91b1d5bdc5f43db795d53dc",
  deps=["numpy"], inputs="damage x hub matrix", outputs="completed matrix", scope="reproduce the historical completion",
  forbidden="no holdout was ever computed: completion 'fit' is not prediction", status="HISTORICAL_ONLY")


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------
def git_last_commit(path: str | None) -> str | None:
    if not path:
        return None
    r = subprocess.run(["git", "log", "-1", "--format=%H", "--", path], cwd=str(REPO), capture_output=True, text=True)
    sha = r.stdout.strip()
    return sha or None


def load_controls(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = d.get("results") or d.get("cases") or []
    by: dict[str, list] = {}
    for r in rows:
        by.setdefault(r["tool_key"], []).append(r)
    return {"meta": d, "by": by}


def build(controls: dict, head: str) -> tuple[list[dict], list[str]]:
    author = json.loads(AUTHOR_TESTS.read_text(encoding="utf-8")) if AUTHOR_TESTS.exists() else {}
    consumers = json.loads(CONSUMERS.read_text(encoding="utf-8")) if CONSUMERS.exists() else {}
    finished = controls["meta"].get("finished", "")[:10]
    out, errors = [], []
    for i, r in enumerate(ROWS, 1):
        cases = controls["by"].get(r["key"], [])
        self_tests, kfm = [], list(r["kfm"])
        n_fail = n_err = 0
        for c in cases:
            v = c["verdict"]
            path = RUNNER + "::" + c["case_id"]
            if v == "INFO":
                cid = c["case_id"]
                if not any(cid in k for k in kfm):
                    kfm.append("INFO " + cid + ": " + json.dumps(c.get("observed"), default=str)[:160])
                continue
            st = {"kind": c["kind"], "path": path, "result": "PASS" if v == "PASS" else ("FAIL" if v == "FAIL" else "NOT_RUN")}
            if v == "ERROR":
                st["note"] = "ERROR: " + json.dumps(c.get("observed"), default=str)[:200]
                n_err += 1
            elif v == "FAIL":
                st["note"] = json.dumps(c.get("observed"), default=str)[:200]
                n_fail += 1
            self_tests.append(st)
        for tp in r["author_tests"]:
            a = author.get(tp)
            if a is None:
                continue
            self_tests.append({"kind": "ACCEPT", "path": tp, "result": "PASS" if a.get("rc") == 0 else "FAIL",
                               "note": "author-written test (not a Keeper control): " + str(a.get("summary"))})
        status = r["status"]
        if status in ("READY", "READY_WITH_CAVEAT"):
            if n_fail or n_err:
                errors.append(f"{r['key']}: planned {status} but controls have {n_fail} FAIL / {n_err} ERROR")
            kinds = {s["kind"] for s in self_tests if s["result"] == "PASS" and s["path"].startswith(RUNNER)}
            if not (kinds & ACCEPT_KINDS and kinds & REJECT_KINDS):
                errors.append(f"{r['key']}: planned {status} without Keeper ACCEPT+REJECT families ({sorted(kinds)})")
        if status == "UNTRUSTED" and not any(s["kind"] in REJECT_KINDS and s["result"] == "FAIL" for s in self_tests):
            errors.append(f"{r['key']}: UNTRUSTED without a REJECT-family FAIL")
        sc = r["source_commit"] or git_last_commit(r["path"])
        if sc is None:
            errors.append(f"{r['key']}: no source_commit (untracked path {r['path']}?)")
            sc = head
        lve = None
        if cases and any(c["verdict"] != "ERROR" for c in cases):
            lve = {"date": finished, "by": KEEPER,
                   "how": "python " + RUNNER + " (canonical run at " + controls["meta"].get("git_head", "")[:12] + ")",
                   "result": "controls: " + ", ".join(f"{c['kind']}={c['verdict']}" for c in cases),
                   "artifact": "engine/necropolis/workshop/tests/controls_result.json"}
        elif r["author_tests"] and any(tp in author for tp in r["author_tests"]):
            lve = {"date": HARVEST_DATE, "by": KEEPER, "how": "pytest -q on author test files (harvest scout run)",
                   "result": "; ".join(str(author[tp].get("summary")) for tp in r["author_tests"] if tp in author)}
        row = {
            "schema_version": "1.0.0", "tool_id": f"NT-{i:03d}", "name": r["name"],
            "provenance": {"origin": r["origin"], "author_seat": "unknown" if r["origin"] != "NECROPOLIS_BUILT" else KEEPER,
                           "discovered_by": KEEPER, "discovery_loop": r["loop"],
                           **({"techne_inventory_id": r["techne_id"]} if r["techne_id"] else {}),
                           **({"notes": r["notes"]} if r["notes"] else {})},
            "current_path": r["path"], "historical_path": r["historical_path"], "source_commit": sc,
            "tool_class": r["cls"], "deterministic": r["det"], "mutates_state": r["mut"], "requires_model": r["model"],
            "dependencies": r["deps"], "dependency_status": r["dep_status"],
            **({"dependency_detail": r["dep_detail"]} if r["dep_detail"] else {}),
            "input_contract": r["inputs"], "output_contract": r["outputs"],
            "historical_consumers": r["consumers"] if r["consumers"] is not None else consumers.get(r["path"] or "", []),
            "last_verified_execution": lve, "self_tests": self_tests, "known_failure_modes": kfm,
            "evidentiary_scope": r["scope"], "forbidden_inference": r["forbidden"], "necropolis_status": status,
            **({"status_reason": r["reason"]} if r["reason"] else {}),
            **({"caveat": r["caveat"]} if r["caveat"] else {}),
            "necropolis_adapter": r["adapter"], "layer": r["layer"],
            "frankenstein_refs": r["frank"], "battery_refs": r["batteries"],
            "harvest": {"date": HARVEST_DATE, "keeper": KEEPER, "inspected": r["inspected"]},
        }
        out.append(row)
    keys = [r["key"] for r in ROWS]
    if len(set(keys)) != len(keys):
        errors.append("duplicate tool keys")
    unregistered = sorted(set(controls["by"]) - set(keys))
    if unregistered:
        errors.append("control groups without a registry row: " + ", ".join(unregistered))
    return out, errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", default=str(HERE / "tests" / "controls_result.json"))
    ap.add_argument("--out", default=str(HERE / "TOOLS.jsonl"))
    ap.add_argument("--allow-errors", action="store_true")
    a = ap.parse_args(argv)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    rows, errors = build(load_controls(Path(a.controls)), head)
    for e in errors:
        print("GEN-ERROR", e)
    if errors and not a.allow_errors:
        return 2
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=False) + "\n")
    from collections import Counter
    print("wrote", len(rows), "rows ->", a.out, dict(Counter(r["necropolis_status"] for r in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
