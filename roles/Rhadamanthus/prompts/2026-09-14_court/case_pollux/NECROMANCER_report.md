# NECROMANCER report -- case POLLUX (court cycle 2026-09-14)

Reconstruction only. No FAIR/UNFAIR grade is offered. Prior verdicts are
recorded in section 10 at zero weight. Every factual sentence carries an
evidence class per COMMON_RULES. All paths are relative to the working tree
D:/Prometheus-worktrees/rhadamanthus-base-role unless prefixed with a drive.
Scratch directory (S): C:/Users/James/AppData/Local/Temp/claude/D--prometheus/73954ab7-6db7-4809-b206-7543b299f62b/scratchpad/necromancer/

---

## 0. files_opened / instruments_executed / excluded_by_charter

### 0.1 files_opened (READ with eyes; "full" = every line)

Instruction files
- roles/Rhadamanthus/prompts/2026-09-14_court/case_pollux/COMMON_RULES.md (full)
- roles/Rhadamanthus/prompts/2026-09-14_court/case_pollux/NECROMANCER_prompt.md (full)

The organism and its swarm
- charon/agents/pollux/daemon.py (full, 614 lines, HEAD)
- charon/agents/pollux/__init__.py (full, 10 lines)
- charon/agents/__init__.py (full)
- charon/agents/_base.py (full, 306 lines)
- charon/agents/_shared_queues/__init__.py (full, 123 lines)
- charon/agents/.gitignore (full)
- harmonia/agents/_base.py (full, 418 lines; the parent class of CharonAgent)
- charon/agents/hecate/daemon.py (lines 20-60, 290-340)
- charon/agents/stygian/daemon.py (lines 160-260)
- charon/agents/stygian/executor.py (lines 210-240)
- charon/agents/stygian/loaders/ (directory listing only; grep hits at composition_g15_ledger_mi.py:40, composition_g19_ledger_transitivity.py:41, g15_v2, g19_v2, g16)
- charon/agents/erebos/daemon.py (lines 50-110, 150-170, 305-330)
- charon/agents/erebos/generators/g01_intersection.py (lines 35-70)
- charon/agents/erebos/generators/g04_survivor_tightening.py (lines 110-130)
- ergon/learner/greedy/sources.py (lines 155-205, 380-392)
- ergon/learner/greedy/build_corpus.py (lines 20-40)
- ergon/learner/greedy/corpus/manifest_v1.json (lines 18-35, 55-66)
- ergon/learner/greedy/ablate_sources.py (line 27 via grep)
- scripts/charon_loop.py (grep lines 38-39, 139-178, 201-236 only)
- prometheus_math/databases/mahler.py (READ ONLY, NOT imported: lines 1-60, 430-470)
- prometheus_math/databases/_mahler_data.py (READ ONLY, NOT imported: lines 70-95, 2304-2345; and `git show ca681ab43:` version around line 2304)

Historical record (primary artifact set)
- charon/agents/DESIGN_2026-05-19.md (grep only: 0 pollux hits)
- charon/agents/v02_PROPOSAL_2026-05-19.md (grep only: 0 pollux hits)
- charon/CHARON_SESSION_2026-06-03.md (line 3 and grep)
- charon/CHARON_SESSION_2026-06-15.md (line 54 and grep)
- charon/CHARON_SESSION_2026-08-12.md (lines 160-180)
- pivot/charon_swarm_diminishing_returns_2026-05-25.md (lines 1-60, 145-195, 245-260)
- pivot/agent_roster_2026-05-28.md (lines 30-40, 105-115)
- aporia/docs/program_audit_2026-06-10.md (lines 110-125, 190-195, 245-250)
- pivot/REASSESSMENT_2026-06-22_consolidated.md (lines 750-758)
- pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md (lines 60-70, 110-118)
- pivot/COMPONENT_DOSSIERS_2026-06-24.md (lines 1-16, 40-50, 110-120, 290-305, 385-410)
- aporia/docs/PROF_TRIAGE_2026-08-20.md (lines 25-32)
- engine/queues/PROF_TRIAGE.jsonl (line 34)
- engine/ledger/AGENT_AUTOPSIES.jsonl (line 18)
- engine/ledger/AUTOPSY_TAXONOMY.md (lines 35-60, 80-100, 130-145)
- docs/state.json (agents[31], agents[33], agents[34], anomalies[28]; header fields)
- engine/queues/BACKLOG.jsonl (grep pollux: lines 106, 689)

Secondary record reached by grep
- pivot/charon_swarm_2026-05-27.md (lines 11, 29-35, 51, 60-81, 93)
- pivot/generator_quality_handoff_for_ergon_2026-06-03.md (lines 25-40)
- pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md (lines 55, 121 via grep)
- pivot/stygian_executor_scoping_2026-05-21.md (grep only; 0 lines containing "pollux" -- the __init__.py citation of it is a pointer, not a mention)
- git commit messages of 8c619443a and 43b094552 (git show --stat / git log)

### 0.2 instruments_executed (exact commands)

All from S; TREE = D:/Prometheus-worktrees/rhadamanthus-base-role.

1. `python S/run_instruments.py S` -- the script (kept at S/run_instruments.py) does
   `sys.path.insert(0, TREE/"engine/necropolis/workshop/adapters")` and calls:
   - `git_history_census.history(<p>, TREE)` for p in {charon/agents/pollux/daemon.py, charon/agents/pollux/__init__.py, charon/agents/pollux/state/kill_ledger.jsonl, charon/agents/pollux/artifacts, charon/agents/pollux/state}
   - `git_history_census.recover("charon/agents/pollux/daemon.py", <sha>, TREE, S/recovered)` for sha in {8c619443a7939186d3317f1d5c47ded14dcb1d67, 43b094552462de5be62501c2fdd973590b9b90ae}
   - `git_history_census.deleted_python_files(TREE, grep="pollux", limit=50)`
   - `consumer_trace.trace(t, TREE)` for t in {charon/agents/pollux/daemon.py, charon/agents/pollux, charon/agents/pollux/state/kill_ledger.jsonl, stygian_priority, pollux_survivor}
   - `literal_verdict_lint.lint_paths([9 files: pollux/daemon.py, _base.py, _shared_queues/__init__.py, stygian/daemon.py, stygian/executor.py, hecate/daemon.py, erebos/daemon.py, ergon/learner/greedy/sources.py, S/recovered/8c619443a793/daemon.py], TREE)`
   Output: S/instruments.json. The trace results report `"command": None` (the adapter's rg-fallback path); `truncated: False` on every trace.
2. `git diff 8c619443a 43b094552 -- charon/agents/pollux/` > S/pollux_diff_c1_c2.txt (268 lines); `git diff 43b094552 HEAD -- charon/agents/pollux/` (empty).
3. `git log --format=... -- prometheus_math/databases/_mahler_data.py prometheus_math/databases/_known180_raw.gz prometheus_math/databases/mahler.py`; `git show ca681ab43:prometheus_math/databases/_mahler_data.py | grep -n _ingest_known180`; `git log -L2487,2490:prometheus_math/databases/_mahler_data.py`; `git log -L161,202:ergon/learner/greedy/sources.py`; `git log -1 -- ergon/learner/greedy/corpus/manifest_v1.json`.
4. `ls -la charon/agents/pollux charon/agents/pollux/__pycache__ charon/agents/_shared_queues charon/agents/stygian/loaders`; same `ls` on D:/prometheus/charon/agents/pollux (main tree, read-only look for state/ or artifacts/).
5. `python S/reimpl_pollux.py > S/reimpl_pollux.json` -- [RE-IMPLEMENTATION], stdlib only, synthetic data, seed 20260914. Re-codes _spearman, _mean_spacing_normalize, _classify, the sorted pairing, the verdict map and the settle/replace state machine as READ in daemon.py, and runs five synthetic tests T1-T5 (section 2.7, 8).

### 0.3 excluded_by_charter (hits returned by consumer_trace / grep, NOT opened)

engine/necropolis/ (all hits, none opened; instrument adapters excepted):
COUNTERFACTUAL_HISTORY.jsonl; DEFECTS.md; ORGANS.jsonl; ORGAN_NOTES.json;
dossiers/pollux.dossier.json; dossiers/pollux_evidence/{CLERIC.md, README.md, cleric_census_fit.py, cleric_census_fit_result.json, cleric_chance_floor.py, cleric_chance_floor_result.json, pollux_consumer_trace.py, pollux_consumer_trace_result.json, pollux_instrument_null.py, pollux_instrument_null_result.json, pollux_record_census.py, pollux_record_census_result.json, pollux_rescan.py, pollux_rescan_result.json};
dossiers/_keeper_evidence/{pollux_replay_corrected.py, pollux_replay_corrected_result.json, pollux_settling_query.py, pollux_settling_query_result.json, fleet_halt_census_result.json, intelligence_outputs_census.py, intelligence_outputs_census_result.json};
dossiers/{argos.dossier.json, erebos.dossier.json}; dossiers/argos_evidence/{README.md, argos_selector_test.py}; dossiers/erebos_evidence/{CLERIC.md, README.md, _build_dossier.py, erebos_consumer_audit_rerun_result.json, erebos_external_refs_result.json, erebos_history_census.py, erebos_history_census_result.json, erebos_seam_census.py}; dossiers/nous_evidence/{README.md, nous_salvage_reproduce.py, nous_salvage_reproduce_result.json};
monsters/{FRANK-002, FRANK-003, FRANK-004}.monster.json;
workshop/{CANDIDATE_INDEX.jsonl, CONSUMERS.json, FRANKENSTEIN_XREF.json, FREEZE_2026-09-13.json, TOOLS.jsonl, build_frankenstein_xref.py, coroner_run.py, registry_source.py}; workshop/adapters/{pollux_statistic_replay.py, resampling_null.py}; workshop/candidates/{file_exists.json, import_verify.json, scout_table.json}; workshop/coroner_plans/{CR-001_pollux_frank004.json, DISPOSITIONS.jsonl}; workshop/tests/{cases_f.py, controls_result.json, run_controls.py, test_coroner_gate.py, test_evidence_stamp.py}.

roles/ (all hits, none opened except the two instruction files):
Alethelia/notes/NAME_COLLISION_2026-08-27.md; Atalanta/{ARCHAEOLOGY_2026-09-11.md, BACKLOG_H0H5.md, CENSUS_LOOP_RISK_2026-09-11.md, DEAD_GATING_SPECIMEN.md, PROPOSED_INVARIANT_2026-09-11.md, RESPONSIBILITIES.md, SALVAGE_ASSESSMENT_2026-09-11.md, STATUS.md, calibration/LEDGER.md, journal/2026-09-11.md, journal/2026-09-11b.md, prompts/2026-09-11_closeout/HANDOVER_ARCHAEON_two_rulings.md, prompts/2026-09-11_closeout/HANDOVER_RHADAMANTHUS_telemetry_instrument.md, prompts/2026-09-11_specimen/REPORT_ARCHAEON_invariant.md, reference/test_null_bound.py}; Eos/{CALIBRATION.md, EOS03_ARCHAEOLOGY_CLIO.md, EOS31_CONTACT_WITNESS.md, RESPONSIBILITIES.md, STATUS.md, intake/FIRST_SEASON_2026-09-11.md, intake/contact_witnesses_2026-09-11.json, intake/ledger_2026-09-11.json, prompts/2026-09-11_admission_queue/TO_Icarus.md, prompts/2026-09-11_clio_corpse/TO_NECROPOLIS.md, prompts/2026-09-11_eos30_attack/COMMISSION.md}; Ergon/{CORPUS_VALUE_AUDIT_2026-06-03.md, GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md, GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md, GREEDY_LORA_RESULT_2026-06-03.md, TRAINING_DATA_SURVEY_2026-06-07.md}; Harmonia/{AUDIT_20260819_detector_band.md, DOSSIER_20260812_harmonia_B_review_index.md, RESUME_20260615_icarus_ladder.md, RETRODICTIONS_20260819_harmonia_C.md, SESSION_JOURNAL_E_20260615.md, SESSION_STATE_20260605_three_threads.md}; Hephaestus/surveys_2026-08-12/{01_TECHNE..., 02_CHARON..., 04_THESEUS..., 05_The_Reasoning_Ladder..., 11_APORIA..., 13_Mathematical_Substrate_Core...}.json; Hermes/science/convergence/observations.json; Hypatia/{BACKLOG_H0H5.md, RESPONSIBILITIES.md, STATUS.md, journal/2026-09-11.md, science/seam_contract_test.py, science/season1/ladders/run1_POS-3_nephele.jsonl, science/season1/ladders/run2_POS-3_nephele.jsonl, science/season1/packets/PKT-NEPHELE.json}; Icarus/{ARCHAEOLOGY_2026-09-11.md, BACKLOG_H0H5.md, RESPONSIBILITIES.md, STATUS.md}; Metis/{ARCHAEOLOGY_2026-09-11.md, journal/2026-09-11.md, season1/bundles/E1_greedy_lora.json}; Pheme/{BACKLOG_H0H5.md, design/INVENTORY_2026-09-11.md, journal/2026-09-11.md, prompts/2026-09-11_seat_creation/REPORT_ARCHAEON_new_seat.md}; Polyhymnia/{ARCHAEOLOGY_2026-09-11.md, ledgers/tensor_body_2026-09-11/state_2026-05-30.json, ledgers/tensor_body_2026-09-11/tesserae.jsonl, superseded/RESPONSIBILITIES_2026-09-11_adoption_pass.md}; Rhadamanthus/{BACKLOG_H0H5.md, STATUS.md, calibration/LEDGER.md, journal/2026-09-11.md, ledgers/CROSS_GRAVE_2026-09-11.md, ledgers/PROVENANCE_COVERAGE_2026-09-11.md, prompts/2026-09-11_charter/RECEIPT.md, prompts/2026-09-11_harvest/RECEIPT.md, prompts/2026-09-11_inbox/msg_96.json, prompts/2026-09-11_inbox/msg_98.json, prompts/2026-09-11_inbox/reply_98_atalanta_ack.md, prompts/2026-09-14_court/REQUIREMENTS_to_Techne.md, prompts/2026-09-14_court/case_pollux/CLERIC_prompt.md, prompts/2026-09-14_court/case_pollux/SOLO_prompt.md}; Talos/{BACKLOG_H0H5.md, RESPONSIBILITIES.md, journal/2026-09-11.md}; Techne/{FORENSIC_INVENTORY_2026-09-11.txt, SUBSTRATE_FIRE_LOG_2026-05-21.md}; Vivarium/{MACHINE_REPORT_2026-09-06.md, TEST_RESULTS_MACHINE_2026-09-06.txt, journal/2026-09-11.md}; base-role/MONITORS.md.

comms/: no hits returned by the traces run. C:/Users/James/.claude/: not searched.

Note on the two `ls` results: charon/agents/pollux/__pycache__/ holds daemon.cpython-314.pyc (mtime 2026-09-11 13:26) and __init__.cpython-314.pyc (mtime 2026-09-13 20:54) [READ ls]. Something imported the module on this worktree on those dates; the charter forbids me from reading the necropolis evidence that would say what [INFERRED from the ls tags; identity NOT_EXAMINED].

---

## 1. Claimed capability

In the organism's own words:
- "Pollux -- numerical coincidence scanner. Sixth member of the Charon swarm ... the only agent in the swarm with operator class != Theseus that can populate the kill_ledger. Necessary precondition for Hecate's cross-generator MI to become non-zero." [QUOTED charon/agents/pollux/__init__.py:1-10]
- The daemon docstring names three outcomes per scan -- "correlation survives normalization" (PROMOTED-class), "correlation is a scale artifact" (REJECTED-class), "no correlation / unmeasurable" (UNVERIFIED-class) -- and states "generator_id='pollux' is the second non-Theseus operator class to populate the kill ledger (Stygian is the first)", with cross-database pairs, prime-power detrending and a battery-call hook deferred to "v0.6+". [READ charon/agents/pollux/daemon.py:1-29]
- The statistic: "Spearman correlation BEFORE and AFTER mean-spacing normalization" between two Mahler-measure subsets. [READ daemon.py:1-29; QUOTED pivot/charon_swarm_2026-05-27.md:35]

In the commissioner's words:
- Commit 8c619443a (2026-05-24 03:10 -0400) introduced it as the "third operator class after Theseus and Stygian" and reported a live verification: "deg10_vs_deg12 scan emitted REJECTED with pollux_sign_flips_under_normalization (raw 1.0, normalized -0.2235)". [QUOTED git log message of 8c619443a]
- Commit 43b094552 (2026-05-25 01:46 -0400) states the tuning motive: Pollux was "100% deterministic" (the same four pairs re-scanned forever) and adds a settle-and-replace pool so the rotation advances. [QUOTED git log message of 43b094552; READ pivot/charon_swarm_diminishing_returns_2026-05-25.md:55-59]
- The 2026-05-27 swarm memo frames the point of Pollux as adding "structurally-different operator classes to the kill ledger" so that Hecate's cross-generator MI has something to measure. [QUOTED pivot/charon_swarm_2026-05-27.md:11, 81]

Note the __init__ claim ("only agent with operator class != Theseus") and the daemon docstring claim ("second non-Theseus ... Stygian is the first") disagree with each other about Stygian, within the same commit. [READ __init__.py:1-10 vs daemon.py:1-29] [INFERRED]

---

## 2. Implementation (what the code computes, with line numbers)

All line numbers refer to charon/agents/pollux/daemon.py at HEAD, which is byte-identical to commit 43b094552 for this directory. [EXECUTED `git diff 43b094552 HEAD -- charon/agents/pollux/` -> empty]

### 2.1 Constants and selectors
- POLLUX_KILL_LEDGER = REPO_ROOT/charon/agents/pollux/state/kill_ledger.jsonl (45-47). [READ]
- SEED_PAIRS (51-76), four pairs: deg10_vs_deg12; deg14_vs_deg16; salem_vs_pisot; smyth_extremal_vs_rest. [READ]
- CANDIDATE_POOL (83-114), five pairs in fixed order: deg18_vs_deg20; even_deg_vs_odd_deg; small_deg_vs_large_deg (degrees 2-8 vs 16-30); narrow_band_1.10_1.20_vs_1.30_1.50; lehmer_witness_neighborhood (M in [1.0001,1.20] vs [1.20,1.50]). [READ]
- SETTLE_THRESHOLD = 5 (120); CORR_SIGNIFICANT = 0.30 (123); CORR_FLIPPED_DELTA = 0.20 (124). [READ]
- Spearman minimum n = 10, hard-coded inside _spearman (212-235) and again for the normalized branch (421-424). [READ]
- Stygian enqueue dedup window: 24 hours, key `pollux_survives_<pair>` (533-567). [READ]

### 2.2 Subset loader `_load_subset` (127-209)
Lazily imports `smallest_known, all_below, smyth_extremal` from prometheus_math.databases.mahler (I did not import them). Kinds: `mahler_by_degree` = all_below(2.0) filtered to one degree; `mahler_by_class` = all_below(2.0) filtered by `bool(e.get("salem_class")) == salem`; `mahler_smyth_extremal` = smyth_extremal(); `mahler_non_smyth` = all_below(2.0) minus smyth-extremal; `mahler_by_degree_parity`; `mahler_degree_range`; `mahler_M_range` = all_below(mhi) filtered mlo <= M <= mhi. Returns a list of Mahler-measure floats (the field `mahler_measure`) and an error string; on any exception returns ([], err). [READ daemon.py:127-209]
- all_below(x) in the database module returns entries sorted ascending by mahler_measure. [READ prometheus_math/databases/mahler.py:457-468]

### 2.3 The pairing step -- the load-bearing lines
```
417  a_paired = sorted(a_vals)[:n]
418  b_paired = sorted(b_vals)[:n]
```
where n = min(len(a_vals), len(b_vals)). [READ daemon.py:414-418] Both subsets are independently sorted ascending and then truncated to the shorter length, and the i-th smallest value of A is paired with the i-th smallest value of B. There is no key joining an element of A to an element of B; the "pairing" is by rank position. [READ 417-418] [INFERRED]

### 2.4 `_spearman(a, b)` (212-235)
n = min(len); returns None if n < 10; truncates both to n; ranks each by the index of a stable sort (no tie correction); Pearson on the ranks; None if either rank vector has zero variance. [READ daemon.py:212-235]
- Consequence: applied to two independently sorted lists of the same length (2.3), the rank vectors are both 0..n-1 in order, so corr_raw = +1.0 identically, for any inputs with n >= 10 and no exact ties. [INFERRED from READ 212-235 and 417-418; confirmed on synthetic data: corr_raw in [0.9999999999999998, 1.0000000000000002] across 200 trials, RE-IMPLEMENTATION T1, S/reimpl_pollux.json]

### 2.5 `_mean_spacing_normalize(v)` (238-250)
Sorts v; takes consecutive gaps; divides each gap by the mean gap; returns len(v)-1 values (empty if mean gap is 0). [READ daemon.py:238-250] corr_norm (421-424) is then the Spearman of the two gap sequences, again paired by index (the i-th gap of A with the i-th gap of B), None if fewer than 10 gaps. [READ 421-424]
- The whole statistic is a function of sorted(a_vals) and sorted(b_vals) only, so it is invariant to any reordering of the inputs (RE-IMPLEMENTATION T2: sorted vs shuffled inputs give identical (raw, norm, kill_pattern)). [READ 417-424] [RE-IMPLEMENTATION S/reimpl_pollux.json T2]

### 2.6 `_classify(corr_raw, corr_norm)` (253-268) and verdict map (427-434)
- either None -> `pollux_correlation_unmeasurable` -> UNVERIFIED
- raw_sig = |raw| >= 0.30; norm_sig = |norm| >= 0.30
- raw_sig and raw*norm < 0 and |norm| < |raw| - 0.20 -> `pollux_sign_flips_under_normalization` -> REJECTED
- raw_sig and norm_sig and raw*norm > 0 -> `pollux_correlation_survives_normalization` -> PROMOTED
- not raw_sig -> `pollux_no_correlation_observed` -> UNVERIFIED
- else -> `pollux_correlation_attenuates_under_normalization` -> UNVERIFIED
[READ daemon.py:253-268, 427-434] (Exact strings: lines 256, 261, 263, 265, 268; the docstring at line 10-14 and the record's shorthand "attenuates/survives/sign_flips" drop the `correlation_` infix.) [READ daemon.py:10-14]
- Given 2.4 (raw == 1.0), the branches reduce to: norm < 0 (any magnitude, since |norm| < 0.80 always holds for |norm| <= 1 unless norm <= -0.8) -> REJECTED; norm >= 0.30 -> PROMOTED; 0 <= norm < 0.30 -> UNVERIFIED(attenuates); `pollux_no_correlation_observed` is unreachable. [INFERRED from READ 253-268 + 2.4] Exact edge: norm in (-1.0, -0.8] fails the flip clause (|norm| < 0.80 false), falls through, raw*norm < 0 so not "survives", raw_sig so not "no_correlation", lands in `attenuates` -> UNVERIFIED. [INFERRED from READ 253-268]

### 2.7 Synthetic behaviour of the design [RE-IMPLEMENTATION, S/reimpl_pollux.py, seed 20260914]
- T1: 200 trials of two independent Uniform(1,2) samples of random sizes 10-400: corr_raw = 1.0 in all 200; kill_pattern counts sign_flips 106 / attenuates 92 / survives 2; |corr_norm| >= 0.30 in 2.5% of trials.
- T3: n = 9 on one side -> (None, None, pollux_correlation_unmeasurable).
- T4: A vs (3 - A) (a perfectly anti-monotone relation): corr_raw = 1.0, corr_norm = 0.099, `attenuates`. The statistic cannot see the sign of a true relation because it never uses the relation. [INFERRED from T4]
These are facts about the formula as READ, not about the original run. (The re-implementation labels its outcomes with the short forms sign_flips / survives / attenuates / unmeasurable, without the `correlation_` infix used by daemon.py lines 256-268.)

### 2.8 Record and ledger row (271-280, 458-503)
`_record_id` = sha256 of the sorted-key JSON of the row (271-273). `_emit_kill_ledger_row` appends one JSON line (276-280). Row fields (458-503) include claim_kind "pollux_correlation_scan", generator_id "pollux", method "spearman_with_meanspacing_normalization", precision_dps 4, convergence_status "exact", kill_vector {corr_raw, corr_norm, n_paired}, verdict, kill_pattern, pair name and both subset specs. [READ daemon.py:271-280, 458-503] The 2026-05-24 commit message calls this "Theseus shape". [QUOTED git log 8c619443a]

### 2.9 Rotation, settle, replace (292-356, 511-526)
- `_active_pairs` seeds state `active_pairs` from SEED_PAIRS on first call (292-299).
- `_record_verdict_and_check_settle` appends the verdict to `pair_history[pair]`, caps at 10, and returns True iff the last 5 are identical AND that verdict is PROMOTED or REJECTED (301-315). UNVERIFIED can never settle. [READ]
- `_promote_settled_replace` appends to `settled_pairs`, then reads `candidate_pool_idx`; if idx >= 5 it returns None BEFORE removing the pair from `active_pairs` (330-332); only when a candidate remains does it remove the settled pair and append the candidate (336-339). [READ daemon.py:317-340]
- Consequence: once the pool is exhausted, a settled pair stays in rotation and is re-declared settled on every subsequent visit, appending a new `settled_pairs` row each time, while the tick log at line 525 nonetheless prints "active rotation shrunk". [INFERRED from READ 317-340, 511-526; RE-IMPLEMENTATION T5_all_PROMOTED: 200 ticks -> 164 settled rows over 9 distinct pairs, cand_idx 5, final active still 4 pairs, tail events "settled_but_NOT_removed_pool_exhausted"]
- `_pick_and_advance` uses `pair_rotation_idx mod len(active)` (351-356). [READ]
- `run_tick` (386-578): dry_run returns after the pick (402-404); loader failure -> errors+1 and `_emit_short_circuit` (408-413, 580-614: kill_pattern "pollux_scan_aborted", verdict UNVERIFIED, convergence_status "skipped"); otherwise compute, emit artifact (`scan_<pair>_<UTC>.md`, 358-384), emit ledger row, settle check, and if PROMOTED enqueue to stygian_priority with 24 h dedup (533-567); log_work (570-577). [READ]

### 2.10 Lint
literal_verdict_lint over the 9 files listed in 0.2: files_scanned 9, n_findings 0 -- no function returns a single verdict unconditionally. [EXECUTED literal_verdict_lint.lint_paths; S/instruments.json "lint"] The adapter's own caveat applies: an unflagged function is not thereby shown to discriminate. [QUOTED S/instruments.json lint.forbidden_inference] Section 2.4-2.6 shows the discrimination that does exist runs entirely through corr_norm on index-paired gap sequences. [INFERRED]

---

## 3. Assembly

### 3.1 Wiring
- `charon.agents.AGENT_NAMES` = [stygian, lethe, acheron, moros, hecate, nephele, pollux, erebos] (8 names). [READ charon/agents/__init__.py:17]
- scripts/charon_loop.py rotates through AGENT_NAMES by a persisted `next_index`, calls `get_charon_agent(name).tick(dry_run=...)`, and in `--loop` mode sleeps `--interval` (default 240 s). [READ scripts/charon_loop.py:38-39, 139-178, 201-236] `get_charon_agent("pollux")` imports PolluxAgent. [READ charon/agents/_base.py:300-302]
- CharonAgent: operator "Charon", machine "M2", state_dir charon/agents/<name>/state/, artifacts_dir charon/agents/<name>/artifacts/. [READ charon/agents/_base.py] Parent HarmoniaAgent: `load_state/save_state` are JSON files `<state_dir>/<key>.json` (309-324); `write_artifact` (326-330); `tick` wraps run_tick, converts exceptions into {"errors":1}, and heartbeats via `session_telemetry.register_session` with `last_tick_stats` (334-395); Redis env defaults 192.168.1.176:6379 (45-47); agora_persist and session_telemetry are soft imports. [READ harmonia/agents/_base.py]
- Pollux state keys: active_pairs, pair_history, settled_pairs, candidate_pool_idx, pair_rotation_idx. [READ daemon.py:295-355]
- Queue: `stygian_priority_queue()` -> JsonlQueue over charon/agents/_shared_queues/stygian_priority.jsonl with append/read_all/read_unconsumed/mark_consumed/recent_keys; not locked. [READ charon/agents/_shared_queues/__init__.py:1-123]
- DB rows: the daemon itself writes no database rows; heartbeats/log_work go through the soft-imported telemetry in the parent class. [READ daemon.py full; harmonia/agents/_base.py:178-218] Whether those calls reached a store is NEEDS_CORONER (section 16).
- All of state/, artifacts/ and _shared_queues/*.jsonl are gitignored. [READ charon/agents/.gitignore]

### 3.2 The two commits
- 8c619443a (2026-05-24 03:10 -0400, "Charon swarm v0.5 ...") added __init__.py and a 420-line daemon.py with a fixed TEST_PAIRS list of four pairs. [EXECUTED git_history_census.history; recovered copy S/recovered/8c619443a793/daemon.py, sha256_lf d17218e5..., 16792 bytes] The sorted pairing was already present (c1 lines 286-289). [READ S/recovered/8c619443a793/daemon.py:286-289]
- 43b094552 (2026-05-25 01:46 -0400, "Charon swarm v0.6: 4-patch tuning (Moros + Pollux + Hecate + ...)") -- diff of 268 lines [EXECUTED git diff; S/pollux_diff_c1_c2.txt]: adds `timedelta` and `stygian_priority_queue` imports; replaces TEST_PAIRS with SEED_PAIRS + CANDIDATE_POOL + SETTLE_THRESHOLD; adds loader kinds mahler_by_degree_parity / mahler_degree_range / mahler_M_range; adds the settle/replace state machine; adds PROMOTED -> Stygian enqueue with the 24 h dedup key. [READ diff] The statistic (sorting, Spearman, normalization, thresholds) is unchanged between the commits. [READ diff] [INFERRED]
- Why, per the record: "Pollux 100% deterministic" and the daemon "bounced; 7-agent rotation continues at 4-min cadence (28-min full cycle)". [QUOTED git log 43b094552] The 05-25 memo: the four fixed pairs "will emit the same 4 verdicts forever"; with the pool, exhaustion is expected "~5 weeks". [QUOTED pivot/charon_swarm_diminishing_returns_2026-05-25.md:55-59]
- No commit touched charon/agents/pollux/ after 43b094552; no Python file mentioning pollux was ever deleted from history. [EXECUTED git_history_census.history (n_commits 2); deleted_python_files(grep="pollux") -> {}]

---

## 4. Inputs

- Source: the in-repo Mossinghoff Mahler table exposed by prometheus_math.databases.mahler (`all_below`, `smyth_extremal`, `smallest_known`), read at tick time by lazy import. [READ daemon.py:127-140] No file, DB, or network input other than that module and the daemon's own state JSONs. [READ daemon.py full]
- Fields used: `mahler_measure` (float), `degree`, `salem_class` (truthiness), `is_smyth_extremal`. [READ daemon.py:143-205]
- Size at HEAD: the module docstring states 8,625 entries = 178 phase1_curated + 8,431 known180_2022 + 16 arxiv_promoted_2026, verified 2026-08-27. [READ prometheus_math/databases/mahler.py:37-56]
- Size at run time (2026-05-24..30): _mahler_data.py's last content change is commit 12a76bade (2026-05-03), which already ingests Known180 at import (`_ingest_known180()` at lines 2304-2343). [EXECUTED git log/show; READ _mahler_data.py:2304-2343] So the 8,431-row tier was present in the tree three weeks before Pollux's first commit. [INFERRED] The exact n_paired per pair is only in the ledger rows, which are not in this tree: NEEDS_CORONER.
- Every Known180 row is appended with salem_class=True, is_smyth_extremal=False, and (per the in-code comment) M < 1.3. [READ _mahler_data.py:2318-2338] Consequences for the selectors [INFERRED]: `salem_vs_pisot` compares ~8,4xx Salem-flagged rows against only the curated/arxiv rows with a falsy salem_class; `smyth_extremal_vs_rest` draws the extremal side from curated rows only; `narrow_band_1.10_1.20_vs_1.30_1.50` has no Known180 rows on the 1.30-1.50 side; `mahler_by_degree` sides are dominated by Known180 counts per degree. Which sides fell below n=10 (and so produced `pollux_correlation_unmeasurable`) is NEEDS_CORONER; the 08-21 autopsy pattern counts show no unmeasurable rows (section 10). [QUOTED engine/ledger/AGENT_AUTOPSIES.jsonl:18]
- Truncation: the longer side is cut to the shorter side's length after sorting, i.e. only the n smallest measures of the larger subset are used. [READ daemon.py:414-418]

---

## 5. Outputs

Written by the organism [READ daemon.py]:
1. charon/agents/pollux/state/kill_ledger.jsonl -- one row per tick (276-280, 458-503; short-circuit rows 580-614).
2. charon/agents/pollux/artifacts/scan_<pair>_<UTC>.md -- one per successful scan (358-384).
3. charon/agents/pollux/state/{active_pairs,pair_history,settled_pairs,candidate_pool_idx,pair_rotation_idx}.json (292-356).
4. Rows appended to charon/agents/_shared_queues/stygian_priority.jsonl on PROMOTED (533-567).
5. Heartbeat / log_work records through the parent class's soft-imported telemetry (harmonia/agents/_base.py:178-218, 334-395).

Presence in this tree today [EXECUTED ls; git_history_census.history]:
- charon/agents/pollux/ contains only __init__.py, daemon.py, __pycache__/. No state/, no artifacts/. charon/agents/_shared_queues/ contains no .jsonl. Same absence in D:/prometheus/charon/agents/pollux. All of (1)-(4) have zero commits in history (in_head False, n_commits 0) and are gitignored. [READ charon/agents/.gitignore]
- (5): docs/state.json (generated 2026-09-11T19:14:39Z, schema 3, data_source "postgres_fallback") carries Pollux's last heartbeat: status "DEAD", last_tick_at 2026-05-30T15:55:23.901164Z, session_started_at 2026-05-26T17:39:27Z, heartbeat_age 8997555 s, last_tick_stats {verdict UNVERIFIED, corr_raw 1.0, corr_norm 0.0817, kill_pattern attenuates, pair_scanned even_deg_vs_odd_deg, kill_ledger_row_id de34494b..., pair_settled_this_tick false, elapsed 0.39}. [READ docs/state.json agents[34], anomalies[28]]

Where the record says the absent outputs went:
- Machine M2, in the daemon's own directories: the 06-24 dossier reports a 435 KB kill_ledger, 286 rows, ~200 artifacts, candidate_pool_idx = 5, last activity 2026-05-30. [QUOTED pivot/COMPONENT_DOSSIERS_2026-06-24.md:391-405]
- Erebos's last heartbeat counted `pollux_substantive_recent` = 286 (with stygian 344). [READ docs/state.json agents[33]]
- The ergon greedy corpus manifest (committed 2026-06-09) records `pollux: yielded 286, skipped 0, by_outcome {rejected: 286}` and 86 pollux examples in train. [READ ergon/learner/greedy/corpus/manifest_v1.json:21-27, 58-62; EXECUTED git log -1]
- 08-21 autopsy: "286 ledger rows + 286 md artifacts". [QUOTED engine/ledger/AGENT_AUTOPSIES.jsonl:18]
Whether any of these files still exist on M2 is NOT_EXAMINED (no network, no other host).

---

## 6. Dependencies

- Code: charon.agents._base.CharonAgent -> harmonia.agents._base.HarmoniaAgent; charon.agents._shared_queues; prometheus_math.databases.mahler (+ _mahler_data.py, _known180_raw.gz at import); stdlib json/hashlib/datetime. [READ daemon.py:31-40, 127-140; mahler.py:1-60]
- Data: the Mossinghoff table (section 4). No credentials required by the daemon itself. [READ daemon.py full]
- Services: optional Redis (192.168.1.176:6379 defaults) and the agora_persist / session_telemetry modules for heartbeat and log_work; both are soft imports in the parent, so the daemon runs without them. [READ harmonia/agents/_base.py:45-47, and the try/except import blocks near the top]
- Machine: "M2" is hard-coded as the CharonAgent machine label. [READ charon/agents/_base.py] The roster lists Pollux on M2, active, 28 m cadence, 43 events. [QUOTED pivot/agent_roster_2026-05-28.md:36, 110]
- Scheduler: scripts/charon_loop.py --loop --interval 240 (section 3.1).

---

## 7. Controls

NONE FOUND in the organism. Where I looked: charon/agents/pollux/daemon.py in full (no shuffle, permutation, surrogate, chance floor, positive or negative pair, or calibration constant appears; the only thresholds are 0.30/0.20/n>=10); charon/agents/pollux/__init__.py; both commit messages; the 05-25 and 05-27 memos. [READ daemon.py:1-614; READ __init__.py; QUOTED git log 8c619443a, 43b094552]

Controls applied by operators elsewhere, on Pollux's output rather than its input:
- Hecate runs a permutation null (N_PERMUTATIONS = 200) on MI(kill_pattern, generator_id) over the merged ledgers that include Pollux's; its last heartbeat gives mi_crossgen 0.0034, z 0.982, n_crossgen_kps 4, total_records 13392. [READ charon/agents/hecate/daemon.py:33, 44-48, 301-334; READ docs/state.json agents[31]] This is a control on the swarm-level co-occurrence statistic, not on Pollux's correlation. [INFERRED]
- The 06-03 handoff ran a co-occurrence screen and classed the Pollux ledger NO_COOCCURRENCE (0.0 % multi-emission, "3 kps but every row unique batch_id"). [QUOTED pivot/generator_quality_handoff_for_ergon_2026-06-03.md:33]
- The 08-12 session proposes, but does not report having run, "the script that computes Pollux's statistic on sorted and on shuffled inputs". [QUOTED charon/CHARON_SESSION_2026-08-12.md:173-174]
- Post-mortem instruments under engine/necropolis/ (pollux_instrument_null.py, resampling_null.py, cleric_chance_floor.py, pollux_replay_corrected.py, pollux_statistic_replay.py) exist by filename but are excluded_by_charter: NOT_EXAMINED.
- Synthetic-design control by me: RE-IMPLEMENTATION T1/T2/T4 (section 2.7).

---

## 8. Gates

| Gate | Where | Can it refuse? |
|---|---|---|
| n >= 10 on both sides, else `pollux_correlation_unmeasurable` -> UNVERIFIED | daemon.py:212-215, 421-424 | Yes: refuses on small subsets. [READ] RE-IMPLEMENTATION T3 confirms. |
| zero rank variance -> None -> UNVERIFIED | 229-233 | In principle; reachable only with all-tied inputs. [READ] [INFERRED] |
| \|corr_raw\| >= 0.30 (raw_sig) | 253-268 | Cannot refuse: corr_raw is identically 1.0 by construction (2.4), so raw_sig is always True and `pollux_no_correlation_observed` is unreachable. [INFERRED from READ 212-235, 417-418; RE-IMPLEMENTATION T1: 200/200 raw = 1.0] |
| sign flip: raw*norm < 0 and \|norm\| < \|raw\| - 0.20 | 259-262 | Yes, data-dependent through corr_norm; fires on any negative corr_norm > -0.8. [INFERRED] |
| survives: \|norm\| >= 0.30 and same sign | 263-264 | Yes, data-dependent; on independent uniform synthetic inputs it fired in 2/200 trials. [RE-IMPLEMENTATION T1] |
| settle: 5 identical PROMOTED/REJECTED in a row | 301-315 | Yes; but since the statistic is deterministic for a fixed table (2.5, T2), a pair that yields PROMOTED or REJECTED once will settle after exactly 5 visits, and an UNVERIFIED pair never settles. [INFERRED from READ 301-315 and T2] |
| pool exhaustion | 330-332 | Refuses to replace, but does not remove the settled pair (2.9). [READ] |
| 24 h dedup on Stygian enqueue | 533-567 | Yes, keyed on pair name. [READ] |
| Stygian executor POLLUX-* branch | stygian/executor.py:221-236 | Refuses everything: every POLLUX-* problem is short-circuited with kill_pattern "stygian_pollux_survivor_loader_pending". [READ] No loaders/pollux_survivor.py exists. [EXECUTED ls charon/agents/stygian/loaders] |
| literal_verdict_lint | 9 files | 0 findings; adapter caveat quoted in 2.10. [EXECUTED] |

---

## 9. Consumers

Intended (per the record): Hecate's cross-generator MI, Stygian via the priority queue, Erebos's composer, and Theseus-shape ledger readers generally. [READ __init__.py:1-10; QUOTED pivot/charon_swarm_2026-05-27.md:11, 29-35]

Consumer trace, target "charon/agents/pollux", pattern "pollux": 1069 hits, truncated False, 3 importers. [EXECUTED consumer_trace.trace] Full non-excluded hit list (file: hit count) -- excluded paths are in 0.3:
aporia/docs/reasoning_steering_progress_log.md 2; aporia/meta/pythia_dispatch_contract_schema.md 1; charon/CHARON_SESSION_2026-06-03.md 1; charon/agents/__init__.py 1; charon/agents/_base.py 2; charon/agents/erebos/daemon.py 7; charon/agents/erebos/generators/_base.py 1; g01_intersection.py 9; g04_survivor_tightening.py 3; g05_confound_swap.py 1; g06_null_space.py 1; g07_analogy.py 1; g08_dimensional_lift.py 1; g12_invariant_substitution.py 1; g14_relation_strengthening.py 1; g16_anti_anchor.py 1; g17_causal_intervention.py 2; g19_proof_obligation.py 1; g20_instrument_disagreement.py 2; g21_isomorphism_functor.py 1; charon/agents/erebos/tests/_fixtures.py 8; test_g01_intersection.py 7; test_g04_survivor_tightening.py 10; test_g08_dimensional_lift.py 1; test_g12_invariant_substitution.py 2; test_g14_relation_strengthening.py 7; test_g17_causal_intervention.py 8; test_g25_degeneracy.py 1; charon/agents/hecate/daemon.py 5; charon/agents/pollux/daemon.py 33; charon/agents/stygian/daemon.py 8; charon/agents/stygian/executor.py 4; stygian/loaders/composition_g15_ledger_mi.py 2; composition_g15_v2_real_verdict_mi.py 1; composition_g19_ledger_transitivity.py 2; composition_g19_v2_recursive_obligations.py 1; stygian/tests/test_composition_g03_g09_g25_synthetic.py 1; test_composition_g15_family.py 8; test_composition_g19_synthetic_transitivity.py 9; test_composition_g19_v2_recursive.py 6; docs/state.json 4; ergon/learner/greedy/ablate_sources.py 1; aggregate_ablation.py 1; build_corpus.py 1; corpus/manifest_e_hidden.json 3; corpus/manifest_e_shown.json 3; corpus/manifest_v1.json 4; run_ablation.sh 1; sources.py 5; evidence_wiki/gold/harvest_a.jsonl 1; evidence_wiki/v2/arm_outputs/V2-T08_B_sonnet.md 2; evidence_wiki/v2/blind/V2-T08/Q.md 2; evidence_wiki/v2/packs/V2-T08_pack.json 1; harmonia/experiments/hunt_raw_20260610.json 1; harmonia/memory/architecture/fp_candidate_shelf_20260610.json 1; pivot/COMPONENT_DOSSIERS_2026-06-24.md 8; pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md 1; pivot/charon_swarm_2026-05-27.md 3; pivot/charon_swarm_diminishing_returns_2026-05-25.md 1; pivot/erebos_25_archetypes_spec_2026-05-26.md 1; pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md 3; pivot/erebos_g09_projection_collapse_research_2026-05-26.md 8; pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md 3; pivot/generator_quality_handoff_for_ergon_2026-06-03.md 1.
Importers: charon/agents/_base.py:301 (dispatch); the other two importer hits are under engine/necropolis (excluded). [EXECUTED]

Trace on the ledger path (pattern `kill_ledger\.jsonl`, 91 hits, 0 importers): non-excluded files charon/BACKLOG.md 1; erebos/daemon.py 3; erebos/sprint1/phase3/real_residue_smoke.py 2; seam_sufficiency_audit.py 2; hecate/daemon.py 3; pollux/daemon.py 1; stygian/executor.py 1; stygian/loaders composition_g15_ledger_mi.py 4, g15_v2 1, g16_lehmer_extremum.py 1, g19_ledger_transitivity.py 4, g19_v2 1; docs/state.json 1; engine/ledger/AGENT_AUTOPSIES.jsonl 1; ergon/learner/greedy/sources.py 2; harmonia/proposals/2026-06-09/A_CLOSURE_2026-06-15_by_B.md 1; pivot/* (COMPONENT_DOSSIERS 6, charon_swarm_2026-05-27 4, erebos_g03 2, erebos_g09 3, erebos_whitepaper_v1 2, generator_quality_handoff 1, stygian_executor_scoping 1); aporia/docs/erebos_v2_deep_research_deck_2026-05-27.md 1. [EXECUTED] (This pattern matches every agent's kill_ledger.jsonl, not only Pollux's.) [INFERRED]

Trace "stygian_priority": 49 hits, 4 importers (erebos, hecate, pollux, stygian daemons). Trace "pollux_survivor": 23 hits, 0 importers; non-excluded: stygian/executor.py 3, diminishing_returns memo 1. [EXECUTED]

What each actual consumer did with Pollux rows:
- Hecate: lists Pollux's ledger among LEDGER_CANDIDATES (33); merges up to MAX_RECORDS_PER_TICK 50000 rows; counts rows with a kill_pattern (301-308); strips the `pollux_` prefix in its cross-generator regex (329-334) so `pollux_sign_flips_under_normalization` is compared as `sign_flips_under_normalization` against other generators' patterns. [READ hecate/daemon.py] Result at last tick: mi_crossgen 0.0034, z 0.982. [READ docs/state.json agents[31]]
- Stygian daemon: reads up to 10 unconsumed queue rows sorted by cluster_size (167-170); wraps a pollux row as problem id "POLLUX-<pair>", hardness "POLLUX_SURVIVOR" (182-260, pollux branch 225-243). Executor: every POLLUX-* id -> `_emit_short_circuit_row` with kill_pattern "stygian_pollux_survivor_loader_pending", reason "pollux_survivor_loader_not_yet_implemented" (221-236). [READ stygian/daemon.py, stygian/executor.py] So every PROMOTED signal Pollux forwarded was converted into a Stygian UNVERIFIED-class row and nothing else. [INFERRED]
- Erebos: POLLUX_LEDGER path (57-59); `_filter_substantive_recent` keeps rows with verdict in {PROMOTED, UNVERIFIED, REJECTED} within LOOKBACK_DAYS 7, excluding *_pending/_skipped/_loader_pending patterns (87-106); swarm state built at 152-167; generators G01 (pairs Stygian x Pollux rows newest-first, g01_intersection.py:39-66) and G04 (prefers PROMOTED/UNVERIFIED rows, g04_survivor_tightening.py:117-126) read them; self-audit null text at 311-324. [READ erebos/daemon.py; generators] Last heartbeat: pollux_substantive_recent 286. [READ docs/state.json agents[33]]
- Stygian composition loaders G15/G16/G19 (and v2) name the Pollux ledger path as one of several inputs. [READ loader files at the grep lines]
- ergon/learner/greedy/sources.py `pollux_examples` (161-202, registered at 388; added in commit 7e38227ee 2026-06-07): reads the ledger, skips rows lacking corr_raw/corr_norm, and sets `gold = False  # kill_ledger entries are, by construction, the ones that did NOT survive` for EVERY row regardless of verdict; source "pollux", tier 1, trust_weight 1.0. [READ sources.py:161-202; EXECUTED git log -L] The corpus manifest confirms the effect: 286 yielded, by_outcome {rejected: 286}; 86 in train; per-source cap 4000. [READ manifest_v1.json:21-27, 58-62; build_corpus.py:26-33] So the 39 PROMOTED rows reported by the record (section 10) entered the training corpus labelled as non-survivors. [INFERRED]
- Documents: the 05-27 and 05-30 memos, the 06-03 handoff, the 06-10 audit, the 06-22/23/24 pivot documents, the 08-20 triage and the 08-21 autopsy each read the ledger or its counts (section 10).

---

## 10. Historical verdicts (zero weight; recorded, not adopted)

- 2026-05-24 commit 8c619443a: live verification "REJECTED ... (raw 1.0, normalized -0.2235)". [QUOTED git log]
- 2026-05-25 pivot/charon_swarm_diminishing_returns_2026-05-25.md: Pollux "was 100% deterministic"; pool "exhausts ~5 weeks" (55-59); event items E5/E7/E9 (150-160, 173-177, 184-189); "2 Pollux survivor signals" (252). [QUOTED]
- 2026-05-27 pivot/charon_swarm_2026-05-27.md: 21 events/12 h, sample `pair=narrow_band_1.10_1.20_vs_1.30_1.50 kp=pollux_sign_flips_under_normalization`; "Pollux is mining sign-..." (70-73). [QUOTED]
- 2026-05-28 pivot/agent_roster_2026-05-28.md: M2, active, 28 m, 43 events (36, 110). [QUOTED]
- 2026-05-30 pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md: "8 daemons in one process (... Pollux / Erebos)" (55). [QUOTED]
- 2026-06-03 pivot/generator_quality_handoff_for_ergon_2026-06-03.md: ledger (286) NO_COOCCURRENCE, 0.0 % multi-emission, "3 kps but every row unique batch_id" (33); charon/CHARON_SESSION_2026-06-03.md line 3 mentions Pollux. [QUOTED]
- 2026-06-10 aporia/docs/program_audit_2026-06-10.md: "39 PROMOTED ... 86 scale artifacts correctly REJECTED" (118-119; also 192, 247). [QUOTED]
- 2026-06-15 charon/CHARON_SESSION_2026-06-15.md line 54 mentions Pollux. [QUOTED]
- 2026-06-22 pivot/REASSESSMENT_2026-06-22_consolidated.md:754: "Pollux = real signal". [QUOTED]
- 2026-06-23 pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md:66, 115: REVIVE, "Real signal". [QUOTED]
- 2026-06-24 pivot/COMPONENT_DOSSIERS_2026-06-24.md:391-405 (document self-labels as AI-generated and unverified at 1-16): RETIRE-after-HITL; "ALL 286 ledger rows have corr_raw=1.0"; verdicts REJECTED 86 / PROMOTED 39 / UNVERIFIED 161; 435 KB ledger; candidate_pool_idx=5; ~200 artifacts; last 2026-05-30; "Learner has ZERO references to generator_id=pollux"; salvage list. [QUOTED]
- 2026-08-12 charon/CHARON_SESSION_2026-08-12.md:167, 173-174: "Pollux's sorted-array Spearman"; proposes the sorted-vs-shuffled script. [QUOTED]
- 2026-08-20 aporia/docs/PROF_TRIAGE_2026-08-20.md:27-30 and engine/queues/PROF_TRIAGE.jsonl:34: VACUOUS-NO-SOLVER; BACKLOG.jsonl:689 PROF-Pollux PARKED. [QUOTED]
- 2026-08-21 engine/ledger/AGENT_AUTOPSIES.jsonl:18 (Aporia, P69): LOW-BITS-PER-VERDICT-EMISSION; "286 ledger rows + 286 md artifacts carry 9 distinct facts"; patterns {sign_flips 86, survives 39, attenuates 161}; deg18_vs_deg20 x54, even_vs_odd x56; Hecate mi_crossgen 0.0034 z 0.98; BACKLOG.jsonl:106 AUTOPSY-POLLUX DONE; taxonomy entries at engine/ledger/AUTOPSY_TAXONOMY.md:39-59, 83-97, 132-134, 143-144. [QUOTED]
- 2026-09-11 docs/state.json: status DEAD (generated field, not a judgement). [READ]
- Post-2026-09-10 Necropolis dossier, cleric, monsters, coroner plan: excluded_by_charter, NOT_EXAMINED.

---

## 11. Contradictory evidence

1. "Real signal" (06-22, 06-23) vs the code: corr_raw is +1.0 for any two inputs of length >= 10 (2.4), so the "before normalization" half of every PROMOTED verdict carries no information about the pair; the record's own 06-24 count "ALL 286 rows corr_raw = 1.0" is what the code predicts on any input. [INFERRED from READ 212-235, 417-418; QUOTED COMPONENT_DOSSIERS:391-405; RE-IMPLEMENTATION T1]
2. "39 PROMOTED" and "86 correctly REJECTED" (06-10) vs the pairing: no row can be "correct" about a relation between the two subsets, because no element of A is ever matched to an element of B (2.3). The REJECTED/PROMOTED split is the sign and size of a Spearman between two gap sequences aligned by index. [INFERRED]
3. "Learner has ZERO references to generator_id=pollux" (06-24) vs ergon/learner/greedy/sources.py, added 2026-06-07, which reads the Pollux ledger by path and yielded 286 rows into the corpus (manifest 2026-06-09). [READ sources.py:161-202; EXECUTED git log -L; READ manifest_v1.json] The sentence is literally true of the string `generator_id` and false of consumption. [INFERRED]
4. __init__.py ("only agent with operator class != Theseus") vs daemon.py docstring ("second ... Stygian is the first") vs 05-27 memo ("Stygian + Pollux + Erebos now contribute"). [READ; QUOTED pivot/charon_swarm_2026-05-27.md:11]
5. The log message "active rotation shrunk" (daemon.py:525) vs the pool-exhaustion branch that leaves the pair in rotation (330-332); and the 06-24 dossier's candidate_pool_idx = 5 means the exhausted branch was reached. [READ; QUOTED; RE-IMPLEMENTATION T5]
6. The autopsy's per-pair counts (deg18_vs_deg20 x54, even_vs_odd x56 out of 286) are consistent with post-exhaustion re-scanning of pool pairs, and inconsistent with a rotation that shrinks as pairs settle. [QUOTED AGENT_AUTOPSIES.jsonl:18] [INFERRED]
7. The roster's "active" (05-28) and docs/state.json's "DEAD" are both status words; the timestamp in state.json (last tick 2026-05-30T15:55:23Z) is the only clock reading. [QUOTED; READ]
8. The 2026-05-24 live verification "raw 1.0, normalized -0.2235" is itself an instance of the tautology, recorded as a success. [QUOTED git log 8c619443a] [INFERRED]

---

## 12. Later repairs

- None to the code: two commits total, no change after 2026-05-25. [EXECUTED git_history_census.history]
- No pollux_survivor loader was ever added to charon/agents/stygian/loaders/. [EXECUTED ls; consumer_trace "pollux_survivor": 0 importers]
- Proposals only: 06-24 dossier salvage list (QUOTED 391-405); 08-12 session proposes a sorted-vs-shuffled control script (QUOTED CHARON_SESSION_2026-08-12.md:173-174); 08-20 PROF triage parks Pollux (QUOTED BACKLOG.jsonl:689); 08-21 autopsy closes AUTOPSY-POLLUX (QUOTED BACKLOG.jsonl:106).
- Re-scans and replays by Necropolis after 2026-09-10 exist by filename only (pollux_rescan.py, pollux_replay_corrected.py, pollux_statistic_replay.py, resampling_null.py, CR-001 coroner plan): excluded_by_charter, NOT_EXAMINED.
- The 2026-06-07 ergon change is a consumer, not a repair. [READ sources.py]

---

## 13. Surviving components (stated, not recommended)

- `_mean_spacing_normalize` (238-250): a self-contained unfolding of a sorted sample to unit mean spacing. [READ]
- `_spearman` (212-235): a stdlib rank correlation without tie handling and with an n >= 10 refusal. [READ]
- `_load_subset` (127-209): seven named selectors over the Mahler table, each a pure function of (kind, params). [READ]
- SEED_PAIRS / CANDIDATE_POOL (51-114): nine declared subset contrasts. [READ]
- The Theseus-shape ledger row schema (458-503) and the sha256 record id (271-273). [READ]
- The settle/replace state machine (301-340) minus the exhaustion branch. [READ]
- The Stygian POLLUX-* problem wrapper (stygian/daemon.py:225-243) with no executor behind it. [READ]
- The instrument set under engine/necropolis/ (by filename only; NOT_EXAMINED).

---

## 14. PROPOSITIONS

P1. [READ daemon.py:417-418] The two subsets are independently sorted ascending and truncated to the shorter length before any correlation is taken; no key joins an element of A to an element of B.
P2. [READ daemon.py:212-235; RE-IMPLEMENTATION T1] Under P1, corr_raw equals +1.0 (to floating error) for every pair with n >= 10 and no exact ties; 200/200 synthetic trials gave raw in [0.9999999999999998, 1.0000000000000002].
P3. [INFERRED from READ 253-268 + P2] The branch `pollux_no_correlation_observed` is unreachable; the verdict is decided by corr_norm alone: negative and > -0.8 -> REJECTED; >= 0.30 -> PROMOTED; otherwise UNVERIFIED.
P4. [RE-IMPLEMENTATION T2; READ 417-424] The statistic is a function of the sorted multisets only, so it is invariant to any reordering of the inputs; a sorted-vs-shuffled control cannot separate it from itself.
P5. [RE-IMPLEMENTATION T4] A perfectly anti-monotone relation between A and B (B = 3 - A) yields corr_raw = +1.0 and `attenuates`; the statistic does not measure the relation between the subsets.
P6. [RE-IMPLEMENTATION T1] On two independent Uniform(1,2) samples the design emits PROMOTED in about 1 % (2/200), REJECTED in about 53 %, UNVERIFIED in about 46 % of trials, i.e. every verdict class is reachable from independent noise.
P7. [READ daemon.py:1-614] The daemon contains no null, shuffle, surrogate, baseline pair, chance floor, or calibration of its thresholds.
P8. [READ daemon.py:120-124] The only thresholds are SETTLE_THRESHOLD 5, CORR_SIGNIFICANT 0.30, CORR_FLIPPED_DELTA 0.20, plus the hard-coded n >= 10.
P9. [READ daemon.py:301-315] A pair settles only on five consecutive identical PROMOTED or REJECTED verdicts; UNVERIFIED pairs never settle.
P10. [READ daemon.py:330-332; RE-IMPLEMENTATION T5] After CANDIDATE_POOL is exhausted, a settled pair is not removed from `active_pairs`; it is re-scanned and re-appended to `settled_pairs` on every subsequent visit (synthetic: 164 settled rows over 200 ticks for 9 pairs).
P11. [READ daemon.py:525; P10] The tick log's "active rotation shrunk" text is emitted in the exhausted case in which the rotation did not shrink.
P12. [EXECUTED git_history_census] charon/agents/pollux/daemon.py has exactly two commits, 8c619443a (2026-05-24) and 43b094552 (2026-05-25); HEAD is byte-identical to 43b094552 for this directory; no pollux-mentioning Python file was ever deleted.
P13. [READ S/pollux_diff_c1_c2.txt] The 05-25 commit changed rotation, loaders, settle logic and the Stygian enqueue; it did not change the sorting, Spearman, normalization or thresholds.
P14. [EXECUTED git log/show; READ _mahler_data.py:2304-2343] The Known180 ingest (8,431 rows, all salem_class True, is_smyth_extremal False, M < 1.3 per in-code comment) has been present in _mahler_data.py since commit 12a76bade (2026-05-03), i.e. before Pollux existed.
P15. [INFERRED from P14 + READ daemon.py:143-205] The non-Salem side of `salem_vs_pisot`, the extremal side of `smyth_extremal_vs_rest`, and the 1.30-1.50 side of the narrow-band pair could draw only from the 178 curated (+16 arxiv) rows; exact n_paired per pair is NEEDS_CORONER.
P16. [EXECUTED ls; git_history_census; READ charon/agents/.gitignore] No kill_ledger.jsonl, scan_*.md, state JSON, or stygian_priority.jsonl for Pollux exists in this tree or in git history; all four are gitignored.
P17. [READ docs/state.json agents[34]] The last recorded Pollux tick is 2026-05-30T15:55:23.901164Z (even_deg_vs_odd_deg, UNVERIFIED, corr_raw 1.0, corr_norm 0.0817), session started 2026-05-26T17:39:27Z.
P18. [READ docs/state.json agents[31], agents[33], agents[34]] Pollux's last tick (2026-05-30T15:55:23Z), Erebos's (15:59:24Z) and Hecate's (16:20:54Z) fall within 26 minutes of each other and share session_cycle_id 19ac6398-66e8-4c27-bb80-8fda24ea54f2 and session_started_at 2026-05-26T17:39:27Z, so the halt was swarm-wide rather than Pollux-specific. [INFERRED]
P19. [READ stygian/executor.py:221-236; EXECUTED ls loaders] Every POLLUX-* problem Stygian received was short-circuited as "stygian_pollux_survivor_loader_pending"; no pollux_survivor loader exists anywhere in the tree.
P20. [READ sources.py:161-202; EXECUTED git log -L; READ manifest_v1.json:21-27, 58-62] ergon's greedy corpus builder (added 2026-06-07) labels every Pollux ledger row gold=False regardless of verdict; the 2026-06-09 manifest records 286 yielded / 286 rejected / 86 in train.
P21. [READ hecate/daemon.py:329-334; docs/state.json agents[31]] Hecate strips the `pollux_` prefix before cross-generator comparison and last measured mi_crossgen 0.0034 (z 0.982) over 13,392 merged records.
P22. [EXECUTED literal_verdict_lint] Across the 9 scanned files no function returns one verdict unconditionally (0 findings).
P23. [READ __init__.py:1-10 vs daemon.py:1-29] The package docstring and the daemon docstring disagree about whether Stygian is a non-Theseus operator class.
P24. [QUOTED git log 8c619443a] The organism's only recorded acceptance test was one scan reporting raw 1.0 / normalized -0.2235 -> REJECTED; under P2 that raw value was guaranteed.
P25. [EXECUTED consumer_trace] Textual consumers of the Pollux ledger in the tree outside excluded paths are: hecate/daemon.py, stygian/daemon.py + executor.py, erebos/daemon.py + G01/G04 (+ tests and fixtures), stygian composition loaders G15/G15v2/G16/G19/G19v2, ergon/learner/greedy/{sources.py, build_corpus.py, ablate_sources.py, aggregate_ablation.py, run_ablation.sh, corpus manifests}, and prose documents; importers of the daemon module: charon/agents/_base.py:301 only.

---

## 15. DEATH CERTIFICATE (draft, for the judge)

When it stopped: last tick 2026-05-30T15:55:23.901164Z (docs/state.json); no later heartbeat, artifact, commit, or ledger count is on the record. [READ docs/state.json; EXECUTED git_history_census]

What stopped it: the record shows Pollux, Erebos and Hecate all ceasing within 26 minutes on 2026-05-30 under one session_cycle_id (P18) and the loop script runs all eight agents from one process (scripts/charon_loop.py; "8 daemons in one process" QUOTED pivot/aporia_ecosystem_status_...2026-05-30.md:55). The stop was therefore an external halt of the shared process, not a Pollux-specific failure. [INFERRED] The reason for the halt is not in any file I was permitted to open (fleet_halt_census_result.json is excluded_by_charter): RECORD_INSUFFICIENT on the halt itself.

What the record can establish about WHY the experiment produced nothing usable: the statistic as written cannot measure a relation between two Mahler subsets, because the subsets are never joined (P1-P5); its raw half is a constant (P2); its verdicts are reachable from independent noise (P6) with no control (P7); its PROMOTED signals were forwarded to a consumer that had no implementation (P19) and were absorbed into a training corpus labelled as non-survivors (P20); and its rotation, after ~5 weeks' worth of settling compressed into six days, re-scanned the same pairs (P10, section 11 item 6).

Cause class offered: DESIGN_ERROR (the measurement was defined so that it could not answer the question asked, before any data was loaded).
Strongest rival: CONSUMER_ABSENT (the Stygian loader was never written and the Learner mislabelled the rows, so even a sound statistic would have died unread).
Separating observation: run the daemon's exact `_load_subset` + lines 417-424 on the real table for the nine pairs (coroner action M3), then repeat with B replaced by an independent draw from the same marginal (e.g. a shuffled split of A ∪ B). If verdicts do not change between the real B and the independent B, DESIGN_ERROR stands independently of consumers. If verdicts differ systematically, the statistic had content and the death moves to CONSUMER_ABSENT. Second rival, INFRASTRUCTURE, explains the date of the stop but not the content of the 286 rows; the two are not exclusive.

---

## 16. NEEDS_CORONER (proposed, not executed)

C1. Recover the 286-row kill_ledger.jsonl and ~200 scan_*.md from M2 (charon/agents/pollux/state/, artifacts/) with sha256 and mtimes. Expected: 286 rows, all corr_raw = 1.0, verdict counts 86/39/161. A different count or any corr_raw != 1.0 falsifies P2 for the original run (would indicate ties or a different code path).
C2. From the recovered ledger, tabulate n_paired, corr_norm and verdict per pair; count rows per pair. Expected under P10: deg18_vs_deg20 and even_deg_vs_odd_deg dominate (54/56); expected under P9: no `pollux_correlation_unmeasurable` rows unless some side < 10 (settles P15 for each pair).
C3. Recover state/{settled_pairs, candidate_pool_idx, active_pairs, pair_history}.json. Expected under P10: candidate_pool_idx = 5, settled_pairs has many more than 9 entries with repeated names, active_pairs still has 4 entries. Nine entries exactly would falsify P10 for the original run.
C4. M3 replay: with the frozen HEAD Mahler table, run `_load_subset` and lines 414-424 for the nine pairs and diff against the recovered rows (verdict, corr_norm to 4 dp). Exact match would show the table did not change between May and August on the fields used; a mismatch dates a data drift (compare against the ca681ab43 and 12a76bade table versions).
C5. Independent-marginal control on the real table (section 15 separating observation): for each pair, replace B by a random half of A ∪ B, 1000 draws; report the distribution of corr_norm and the fraction of draws reproducing the original verdict. A fraction near the T1 rates (about 1 % PROMOTED) with the original PROMOTED pairs sitting inside the null distribution would confirm P6 on the real data.
C6. Read the Stygian ledger for rows with kill_pattern "stygian_pollux_survivor_loader_pending": count and pair names. Expected: one per PROMOTED Pollux pair per 24 h window (P19). Zero rows would mean the queue was never consumed and would need the queue file's consumed flags to explain.
C7. Read the ergon greedy corpus artifacts (corpus/*.jsonl if present on M1/M2) to confirm the 86 pollux training examples carry gold=False including rows whose verdict field is PROMOTED (P20).
C8. Query the telemetry store (agora.intelligence_outputs or the Postgres fallback that produced docs/state.json) for Pollux heartbeats between 2026-05-24 and 2026-05-30: count ticks, confirm the 2026-05-30T15:55:23Z last tick, and read the process-halt record for the shared charon_loop process. Expected: ~7 ticks/day at 28-min cycle (roughly 40-50 on the 05-28 roster count of 43); the halt reason decides INFRASTRUCTURE vs deliberate stop.
C9. Establish who imported charon.agents.pollux on this worktree on 2026-09-11 and 2026-09-13 (the __pycache__ mtimes) and whether that import executed a tick; the necropolis evidence files that would answer this are excluded_by_charter for me.

End of report.
