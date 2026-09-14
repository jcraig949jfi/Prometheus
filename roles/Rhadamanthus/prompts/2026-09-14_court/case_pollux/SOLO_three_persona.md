# SOLO THREE-PERSONA READER -- case POLLUX (control arm)
# Court cycle 2026-09-14 -- reader role: solo -- tree: D:/Prometheus-worktrees/rhadamanthus-base-role @ HEAD (read-only)

Evidence tags per COMMON_RULES: [READ path:lines] [EXECUTED instrument] [QUOTED path:lines]
[RE-IMPLEMENTATION] [INFERRED] [NEEDS_CORONER].  Prior verdicts at ZERO weight.  No pass/fail
summaries; failure SHAPES only.  NOT_EXAMINED is used where I did not look.

--------------------------------------------------------------------------------------------------
## 0. Provenance of this reading
--------------------------------------------------------------------------------------------------

### files_opened (all paths relative to the tree; opened with sed/cat/grep, never imported)
  roles/Rhadamanthus/prompts/2026-09-14_court/case_pollux/COMMON_RULES.md     (instruction set, in full)
  roles/Rhadamanthus/prompts/2026-09-14_court/case_pollux/SOLO_prompt.md      (instruction set, in full)
  charon/agents/pollux/daemon.py                 (614 lines, in full; re-read :51-114, :127-268, :301-356, :405-440)
  charon/agents/pollux/__init__.py               (10 lines, in full)
  charon/agents/_base.py                         (306 lines, in full)
  charon/agents/_shared_queues/__init__.py       (123 lines, in full)
  charon/agents/.gitignore                       (in full)
  charon/agents/pollux/__pycache__/              (directory listing only; .pyc mtimes)
  charon/agents/hecate/daemon.py                 (:1-60, :243-340 and grep)
  charon/agents/stygian/daemon.py                (:182-243 and grep)
  charon/agents/stygian/executor.py              (:200-240 and grep)
  charon/agents/stygian/loaders/                 (directory listing; grep of composition_g15_ledger_mi.py,
                                                  composition_g15_v2_real_verdict_mi.py, composition_g19_ledger_transitivity.py)
  charon/agents/erebos/daemon.py                 (:50-170 and grep)
  charon/agents/erebos/generators/g01_intersection.py (:40-137)
  charon/agents/erebos/generators/g04_survivor_tightening.py (grep lines :9, :47-48, :121 only)
  ergon/learner/greedy/sources.py                (:150-210, :380-395 and grep)
  ergon/learner/greedy/corpus/manifest_v1.json   (pollux blocks); manifest_e_hidden.json / manifest_e_shown.json (grep only)
  ergon/learner/greedy/ablate_sources.py, run_ablation.sh (grep only)
  prometheus_math/databases/mahler.py            (:1-128, :147-152, :437-467; NOT imported)
  prometheus_math/databases/_mahler_data.py @ ca681ab43 (git show into scratch copy; :2304-2343, :2487-2514 and grep census; NOT imported)
  charon/agents/DESIGN_2026-05-19.md, charon/agents/v02_PROPOSAL_2026-05-19.md (grep: 0 pollux hits each)
  charon/CHARON_SESSION_2026-06-03.md (:3), charon/CHARON_SESSION_2026-06-15.md (:54), charon/CHARON_SESSION_2026-08-12.md (:165-175)
  pivot/charon_swarm_diminishing_returns_2026-05-25.md (:14, :55-59, :150-160, :184-189, :252)
  pivot/charon_swarm_2026-05-27.md (:35, :70)
  pivot/agent_roster_2026-05-28.md (:36)
  pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md (:1-66)
  pivot/generator_quality_handoff_for_ergon_2026-06-03.md (:33)
  pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md (grep only)
  aporia/docs/program_audit_2026-06-10.md (:118-119, :192, :247)
  pivot/REASSESSMENT_2026-06-22_consolidated.md (:754)
  pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md (:66)
  pivot/COMPONENT_DOSSIERS_2026-06-24.md (:391-406)
  aporia/docs/PROF_TRIAGE_2026-08-20.md (:28), engine/queues/PROF_TRIAGE.jsonl (:34)
  engine/ledger/AGENT_AUTOPSIES.jsonl (line 18), engine/ledger/AUTOPSY_TAXONOMY.md (:39-59, :83-98, :143-144)
  docs/state.json (:940, :959, :1200, :1262, :1280-1340, :1726)
  engine/queues/BACKLOG.jsonl (:106, :689)
  evidence_wiki/v2/blind/V2-T08/Q.md (:52 via grep), evidence_wiki/gold/harvest_a.jsonl (:24 via grep)
  git metadata (read-only): git log/show for 8c619443a, 43b094552, 7e38227ee, a8a276a40, 48337bc3e, 12a76bade, ca681ab43, ca6f7e6ab

### instruments_executed (static; all output under the scratchpad, nothing written into the tree)
  scratch dir: C:/Users/James/AppData/Local/Temp/claude/D--prometheus/73954ab7-6db7-4809-b206-7543b299f62b/scratchpad/solo/
  1. run_instruments.py -> instruments_result.json
       sys.path.insert(0, "<tree>/engine/necropolis/workshop/adapters"); import git_history_census, consumer_trace, literal_verdict_lint
       git_history_census.history(p, TREE) for p in {charon/agents/pollux/daemon.py, charon/agents/pollux/__init__.py,
           charon/agents/pollux/state/kill_ledger.jsonl, charon/agents/_shared_queues/stygian_priority.jsonl}
       consumer_trace.trace(t, TREE) for t in {charon/agents/pollux/daemon.py, charon/agents/pollux/state/kill_ledger.jsonl, charon/agents/pollux}
       literal_verdict_lint.lint_paths([charon/agents/pollux], TREE); lint_paths([_base.py, _shared_queues/__init__.py, hecate/daemon.py, stygian/daemon.py, stygian/executor.py], TREE)
  2. reimpl_pollux_null.py -> reimpl_pollux_null_result.json            [RE-IMPLEMENTATION, synthetic]
  3. reimpl_rotation.py / reimpl_rotation2.py -> reimpl_rotation2_result.json, reimpl_rotation2_trace.json  [RE-IMPLEMENTATION, synthetic]
  4. reimpl_classify_partition.py -> reimpl_classify_partition_result.json  [RE-IMPLEMENTATION, synthetic]
  5. git show ca681ab43:prometheus_math/databases/_mahler_data.py > scratch/_mahler_data_may2026.py (read with grep; never imported)
  6. trace_pkg_allowed.txt / trace_pkg_excluded.txt: per-file aggregation of consumer_trace("charon/agents/pollux") hits

### excluded_by_charter (returned by consumer_trace / grep; NOT opened; listed so the court knows they exist)
  engine/necropolis/: COUNTERFACTUAL_HISTORY.jsonl, DEFECTS.md, ORGANS.jsonl, ORGAN_NOTES.json, QUEUE.jsonl, ROSTER.jsonl, build_roster.py,
    dossiers/pollux.dossier.json, dossiers/_keeper_evidence/*, dossiers/pollux_evidence/{CLERIC.md, README.md, cleric_census_fit*,
    cleric_chance_floor*, pollux_consumer_trace*, pollux_instrument_null*, pollux_record_census*, pollux_rescan*},
    dossiers/erebos*/..., dossiers/nous_evidence/..., monsters/FRANK-002.monster.json, FRANK-003.monster.json, FRANK-004.monster.json,
    workshop/{CANDIDATE_INDEX.jsonl, CONSUMERS.json, FORENSIC_QUESTIONS.*, FRANKENSTEIN_XREF.*, FREEZE_2026-09-13.json, TOOLS.jsonl,
    adapters/instrument_null.py, adapters/pollux_statistic_replay.py, adapters/resampling_null.py, batteries/historical_verdict_original_corrected.json,
    build_consumers.log, build_forensic_map.py, candidates/*.json, coroner_plans/CR-001_pollux_frank004.json, coroner_plans/DISPOSITIONS.jsonl,
    coroner_run.py, registry_source.py, tests/*}
  roles/Ergon/{CORPUS_VALUE_AUDIT_2026-06-03.md, GREEDY_FOLLOWUP_FINDINGS_2026-06-07.md, GREEDY_FOLLOWUP_PROGRESS_2026-06-07.md,
    GREEDY_LORA_RESULT_2026-06-03.md, REVIVAL_ASSESSMENT_2026-08-12.md, TRAINING_DATA_SURVEY_2026-06-07.md}
  roles/Hephaestus/{META_ASSESSMENT_2026-08-12_fable_seat.md, surveys_2026-08-12/02*.json, 04*.json, 05*.json, 07*.json, 10*.json}
  roles/Metis/season1/bundles/E1_greedy_lora.json
  roles/Polyhymnia/ledgers/tensor_body_2026-09-11/{state_2026-05-30.json, tesserae.jsonl}
  roles/Pronoia/science/ledgers/liveness_survey_2026-09-11.json
  roles/Rhadamanthus/{BACKLOG_H0H5.md, RESPONSIBILITIES.md, STATUS.md, calibration/LEDGER.md, journal/2026-09-11.md, journal/2026-09-13.md,
    ledgers/CROSS_GRAVE_2026-09-11.md, ledgers/PROVENANCE_COVERAGE_2026-09-11.md, ledgers/SEAMS_INVENTORY_2026-09-11.md,
    prompts/2026-09-11_charter/*, prompts/2026-09-11_harvest/*, prompts/2026-09-11_inbox/reply_96_eos_ack.md, reply_98_atalanta_ack.md,
    prompts/2026-09-14_court/CHARTER_verbatim.md, REQUIREMENTS_to_Techne.md, case_pollux/CLERIC_prompt.md, case_pollux/NECROMANCER_prompt.md}
  Count: 80 excluded files carrying 845 of the 1,069 consumer_trace hits for "pollux" [EXECUTED consumer_trace; trace_pkg_excluded.txt].
  Note: engine/necropolis/workshop/adapters/resampling_null.py:4 and workshop/tests/run_controls.py:376 appear as "importers" of
  the pollux daemon in the trace; they are under the excluded path and were NOT opened.

--------------------------------------------------------------------------------------------------
## PART A -- NECROMANCER: reconstruction
--------------------------------------------------------------------------------------------------

### A.1 Claimed capability
[READ charon/agents/pollux/daemon.py:1-29] The module docstring describes Pollux as a "numerical-coincidence scanner":
for a pair of Mahler-measure subsets it computes a Spearman correlation before and after a "mean-spacing
normalization" and emits a kill_ledger row whose kill_pattern says whether the correlation "survives", "sign-flips"
or "attenuates" under normalization.  [READ charon/agents/pollux/__init__.py:1-10] The package docstring states the
programme-level purpose: Pollux is "the only agent in the swarm with operator class != Theseus that can populate the
kill_ledger" and is "a necessary precondition for Hecate's cross-generator MI to become non-zero", citing
pivot/stygian_executor_scoping_2026-05-21.md (NOT_EXAMINED).  [INFERRED from both] Two capabilities are therefore
claimed at once: (i) a scientific one -- detect scale-independent (shape) correlation between Mahler subsets -- and
(ii) an infrastructural one -- supply a second generator_id to the kill_ledger so Hecate's cross-generator MI has
something to compute.

### A.2 Implementation (line numbers, constants, thresholds)
[READ daemon.py:45-47] POLLUX_KILL_LEDGER = charon/agents/pollux/state/kill_ledger.jsonl.
[READ daemon.py:51-76] SEED_PAIRS (4): deg10_vs_deg12, deg14_vs_deg16, salem_vs_pisot, smyth_extremal_vs_rest.
[READ daemon.py:83-114] CANDIDATE_POOL (5, in order): deg18_vs_deg20, even_deg_vs_odd_deg, small_deg_vs_large_deg
(deg 2-8 vs 16-30), narrow_band_1.10_1.20_vs_1.30_1.50, lehmer_witness_neighborhood (M in [1.0001,1.20] vs [1.20,1.50]).
[READ daemon.py:120-124] SETTLE_THRESHOLD = 5; CORR_SIGNIFICANT = 0.30; CORR_FLIPPED_DELTA = 0.20.
[READ daemon.py:127-209] _load_subset: lazy import of prometheus_math.databases.mahler (smallest_known, all_below,
smyth_extremal); seven subset kinds, all built from all_below(2.0) except mahler_smyth_extremal (smyth_extremal())
and mahler_M_range (all_below(M_max) with an inclusive [M_min, M_max] filter); returns ([], err) on import failure,
unknown kind, or any exception.
[READ daemon.py:212-235] _spearman: n = min(len); n < 10 -> None; ranks assigned by position in the sorted index
(ties broken by original order, no average ranks); dx == 0 or dy == 0 -> None.
[READ daemon.py:238-250] _mean_spacing_normalize: sort, consecutive gaps, divide each gap by the mean gap; returns a
series of length len(vs)-1; a mean gap of 0 returns raw gaps.
[READ daemon.py:253-268] _classify (verbatim structure):
    None in either -> "pollux_correlation_unmeasurable"
    raw_sig = |corr_raw| >= 0.30 ; norm_sig = |corr_norm| >= 0.30 ; sign_flips = corr_raw*corr_norm < 0
    raw_sig and sign_flips and |corr_norm| < |corr_raw| - 0.20  -> "pollux_sign_flips_under_normalization"
    raw_sig and norm_sig and corr_raw*corr_norm > 0            -> "pollux_correlation_survives_normalization"
    not raw_sig                                                -> "pollux_no_correlation_observed"
    else                                                       -> "pollux_correlation_attenuates_under_normalization"
[READ daemon.py:415-424] run_tick pairing (verbatim):
    n = min(len(a_vals), len(b_vals)); a_paired = sorted(a_vals)[:n]; b_paired = sorted(b_vals)[:n]
    corr_raw = _spearman(a_paired, b_paired)
    a_norm/b_norm = _mean_spacing_normalize(a_paired / b_paired); n_norm = min(len); corr_norm = _spearman(...) if n_norm >= 10 else None
[READ daemon.py:427-434] verdict map: survives -> PROMOTED; sign_flips or no_correlation -> REJECTED; else UNVERIFIED.
[READ daemon.py:456-505] ledger row: generator_id = "pollux", method = "spearman_with_meanspacing_normalization",
convergence_status = "exact", kill_vector = {corr_raw, corr_norm, n_paired}, record_id = sha256 (:271-273), appended
by _emit_kill_ledger_row (:276-280).
[READ daemon.py:301-315] _record_verdict_and_check_settle: pair_history capped at 10; settled iff the last 5 verdicts
are identical AND that verdict is PROMOTED or REJECTED (UNVERIFIED never settles).
[READ daemon.py:317-340] _promote_settled_replace: appends to settled_pairs (:322-328) BEFORE checking the pool;
`if cand_idx >= len(CANDIDATE_POOL): return None` (:331-332) executes BEFORE the settled pair is removed from
active_pairs (:336-339).
[READ daemon.py:507-526] settle block in run_tick: on None it logs "CANDIDATE_POOL exhausted -- active rotation
shrunk" (:523-526).
[READ daemon.py:528-567] PROMOTED rows are enqueued to the Stygian priority queue under key f"pollux_survives_{pair}"
with a 24 h dedup via recent_keys("kill_pattern", 24h); cluster_size = n.
[READ daemon.py:580-614] _emit_short_circuit writes kill_pattern "pollux_scan_aborted", verdict UNVERIFIED, when a
subset fails to load.

### A.3 Assembly
[READ charon/agents/_base.py:283-302] PolluxAgent is dispatched by get_charon_agent("pollux"); CharonAgent extends
HarmoniaAgent and places state/ and artifacts/ under charon/agents/<name>/.  [READ charon/agents/_shared_queues/__init__.py:1-123]
JsonlQueue is an append/read JSONL file with recent_keys(); the docstring says it is not thread-safe and relies on the
charon_loop rotating agents sequentially.  [QUOTED pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md:55]
"8 daemons in one process (Stygian / Lethe / Acheron / Moros / Hecate / Nephele / Pollux / Erebos)".
[QUOTED pivot/agent_roster_2026-05-28.md:36] Pollux ran on M2 at a 28-minute cadence.  [READ daemon.py:342-356]
Each tick scans exactly one pair (self_generate_backlog always returns one item; _pick_and_advance round-robins over
active_pairs).

### A.4 Inputs
[READ prometheus_math/databases/mahler.py:1-128] Docstring (verified 2026-08-27, HITL #341) states 8,625 entries:
phase1_curated 178, known180_2022 8,431, arxiv_promoted_2026 16.  [READ mahler.py:457-467] all_below(M) returns
entries sorted ascending by Mahler measure.  [EXECUTED git log] _mahler_data.py commits: 48337bc3e (04-25),
12a76bade (05-03, Known180 ingest), ca681ab43 (05-05), ca6f7e6ab (08-27); mahler.py itself last changed 08-27 (prose
only per its own docstring).  [READ scratch/_mahler_data_may2026.py:2304-2343, :2487-2514] At the May-2026 revision
the Known180 rows (all salem_class=True, is_smyth_extremal=False, M < 1.3, even degree) are appended at import time by
_ingest_known180(); the curated literal rows census (deg10=14, deg12=20, deg14=14, deg16=15, deg18=10, deg20=4;
salem_class True 72 / False 112; is_smyth_extremal 16; none with M >= 2.0) therefore describes ONLY the curated tier.
[INFERRED from the above] Every input Pollux ever saw was fixed before Pollux existed (Known180 landed 05-03; Pollux
landed 05-24) and did not change during its life (05-24 .. 05-30).  Per-subset n_paired for the nine pairs is
[NEEDS_CORONER] (counting the gz-backed table is coroner action M3).

### A.5 Outputs -- present / absent in this tree
[READ charon/agents/.gitignore] */state/, */artifacts/, _shared_queues/*.jsonl and __pycache__ are ignored.
[EXECUTED git_history_census] charon/agents/pollux/state/kill_ledger.jsonl: n_commits 0, in_head false;
charon/agents/_shared_queues/stygian_priority.jsonl: n_commits 0, in_head false.  [READ ls] No state/ or artifacts/
directory exists under charon/agents/pollux/ in this worktree.  ABSENT here: the kill_ledger, the ~200 scan_*.md
artifacts, pair_history / settled_pairs / candidate_pool_idx / active_pairs / pair_rotation_idx state, the Stygian
queue file.  PRESENT here: daemon.py, __init__.py, and charon/agents/pollux/__pycache__/ containing __init__ .pyc
dated 2026-09-13 20:54 and daemon .pyc dated 2026-09-11 13:26 [READ ls -la] -- i.e. some process byte-compiled
(imported) the package in the last three days; who and why is NOT_EXAMINED.
Every row count, verdict count and correlation value in this report is therefore [QUOTED] from documents or from the
Postgres mirror snapshot in docs/state.json, never [READ] from the ledger.
[QUOTED docs/state.json:1300-1330] Postgres-mirror snapshot (generated 2026-09-11): Pollux status DEAD, last_tick_at
2026-05-30T15:55:23Z, last tick pair even_deg_vs_odd_deg, corr_raw 1.0, corr_norm 0.0817, kill_pattern
pollux_correlation_attenuates_under_normalization, verdict UNVERIFIED, pair_settled_this_tick false, session_started_at
2026-05-26T17:39:27Z.  [QUOTED docs/state.json:1290] Erebos' last tick recorded pollux_substantive_recent = 286.

### A.6 Dependencies
[READ daemon.py:38-40, :132-134] charon.agents._base (CharonAgent, REPO_ROOT), charon.agents._shared_queues
(stygian_priority_queue), prometheus_math.databases.mahler (lazy, inside _load_subset).  [READ daemon.py:212-214]
No scipy/numpy ("so Pollux stays light").  [READ _base.py] HarmoniaAgent (harmonia package) for heartbeat/state
persistence -- NOT_EXAMINED beyond the import line.

### A.7 Controls
[READ daemon.py:386-578] run_tick contains no permutation, no shuffled pairing, no bootstrap, no seed, no p-value,
no comparison against a random-pairing baseline; convergence_status is the literal "exact" (:456-505).
[READ daemon.py:51-76] The pair "rationale" strings state expectations ("expect minimal correlation if Mahler
measures are scale-independent") but no rationale is turned into a computed reference value.
[EXECUTED literal_verdict_lint] 0 findings on charon/agents/pollux (2 files scanned) and 0 on the five neighbouring
charon files; the instrument's own forbidden_inference clause applies: an unflagged function is not thereby shown to
discriminate.

### A.8 Gates -- can each refuse?
  G1 _load_subset (:127-209): refuses (returns []) on import failure / unknown kind / exception -> run_tick emits a
     pollux_scan_aborted UNVERIFIED row (:405-412, :580-614).  Can refuse.  Whether it ever did: [NEEDS_CORONER].
  G2 _spearman n < 10 (:216): refuses with None -> "unmeasurable" -> UNVERIFIED.  Can refuse.  Because corr_norm is
     computed on n-1 gaps (:421-424), a pair needs n >= 11 to be classified at all.
  G3 _spearman dx == 0 or dy == 0 (:233): refuses only when every value in a series is tied.  Practically inert for
     real-valued Mahler measures [INFERRED].
  G4 _classify (:253-268): CANNOT refuse on statistical grounds; every (corr_raw, corr_norm) pair maps to a label.
  G5 settle (:301-315): refuses to settle on UNVERIFIED; this is the only gate that reads history.
  G6 Stygian queue dedup (:528-567): refuses to re-enqueue the same pair within 24 h.
  G7 pool-exhaustion (:331-332): "refuses" to replace -- and, because of the ordering, also fails to remove (A.12).

### A.9 Consumers -- full consumer-trace hit list (file granularity; per-line JSON in scratch/instruments_result.json)
[EXECUTED consumer_trace.trace("charon/agents/pollux")] 1,069 hits in 144 files; 3 importers:
charon/agents/_base.py:301, engine/necropolis/workshop/adapters/resampling_null.py:4 (excluded), engine/necropolis/
workshop/tests/run_controls.py:376 (excluded).  [EXECUTED consumer_trace.trace(".../state/kill_ledger.jsonl")] 91 hits,
0 importers.  Allowed-path hits (64 files, 224 hits) [EXECUTED; trace_pkg_allowed.txt]:
   2 aporia/docs/reasoning_steering_progress_log.md          1 aporia/meta/pythia_dispatch_contract_schema.md
   1 charon/CHARON_SESSION_2026-06-03.md                      1 charon/agents/__init__.py
   2 charon/agents/_base.py                                   7 charon/agents/erebos/daemon.py
   1 charon/agents/erebos/generators/_base.py                 9 charon/agents/erebos/generators/g01_intersection.py
   3 charon/agents/erebos/generators/g04_survivor_tightening.py
   1 each: erebos/generators/g05_confound_swap.py, g06_null_space.py, g07_analogy.py, g08_dimensional_lift.py,
          g12_invariant_substitution.py, g14_relation_strengthening.py, g16_anti_anchor.py, g19_proof_obligation.py,
          g21_isomorphism_functor.py;  2 each: g17_causal_intervention.py, g20_instrument_disagreement.py
   8 charon/agents/erebos/tests/_fixtures.py                  7 erebos/tests/test_g01_intersection.py
  10 erebos/tests/test_g04_survivor_tightening.py             1 erebos/tests/test_g08_dimensional_lift.py
   2 erebos/tests/test_g12_invariant_substitution.py          7 erebos/tests/test_g14_relation_strengthening.py
   8 erebos/tests/test_g17_causal_intervention.py             1 erebos/tests/test_g25_degeneracy.py
   5 charon/agents/hecate/daemon.py                          33 charon/agents/pollux/daemon.py (self)
   8 charon/agents/stygian/daemon.py                          4 charon/agents/stygian/executor.py
   2 stygian/loaders/composition_g15_ledger_mi.py             1 stygian/loaders/composition_g15_v2_real_verdict_mi.py
   2 stygian/loaders/composition_g19_ledger_transitivity.py   1 stygian/loaders/composition_g19_v2_recursive_obligations.py
   1 stygian/tests/test_composition_g03_g09_g25_synthetic.py  8 stygian/tests/test_composition_g15_family.py
   9 stygian/tests/test_composition_g19_synthetic_transitivity.py  6 stygian/tests/test_composition_g19_v2_recursive.py
   4 docs/state.json
   1 each: ergon/learner/greedy/ablate_sources.py, aggregate_ablation.py, build_corpus.py, run_ablation.sh
   3 ergon/learner/greedy/corpus/manifest_e_hidden.json       3 manifest_e_shown.json      4 manifest_v1.json
   5 ergon/learner/greedy/sources.py
   1 evidence_wiki/gold/harvest_a.jsonl                       2 evidence_wiki/v2/arm_outputs/V2-T08_B_sonnet.md
   2 evidence_wiki/v2/blind/V2-T08/Q.md                       1 evidence_wiki/v2/packs/V2-T08_pack.json
   1 harmonia/experiments/hunt_raw_20260610.json              1 harmonia/memory/architecture/fp_candidate_shelf_20260610.json
   8 pivot/COMPONENT_DOSSIERS_2026-06-24.md                   1 pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md
   3 pivot/charon_swarm_2026-05-27.md                         1 pivot/charon_swarm_diminishing_returns_2026-05-25.md
   1 pivot/erebos_25_archetypes_spec_2026-05-26.md            3 pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md
   8 pivot/erebos_g09_projection_collapse_research_2026-05-26.md
   3 pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md
   1 pivot/generator_quality_handoff_for_ergon_2026-06-03.md
Excluded-path hits: 80 files / 845 hits (listed in section 0).

Consumer behaviour, by reading:
  C1 Hecate [READ hecate/daemon.py:30-35, :44-56, :243-258, :329-333]: LEDGER_CANDIDATES includes the Pollux ledger;
     missing files skipped; MAX_RECORDS_PER_TICK 50000, N_PERMUTATIONS 200, MIN_CLUSTER_SIZE 5, MI_DRIFT_THRESHOLD 2.0;
     a generator-prefix strip (_canon_kp, patch of 2026-05-25) exists so that "pollux_" / "stygian_" prefixes do not
     make every kill_pattern generator-unique.  Consumes ALL Pollux rows regardless of verdict.
  C2 Stygian [READ stygian/daemon.py:182-243; stygian/executor.py:221-236; ls stygian/loaders/]: a queued Pollux
     PROMOTED row is wrapped as problem id f"POLLUX-{pair}" with hardness "POLLUX_SURVIVOR"; the executor's first
     branch on that prefix returns a short-circuit row with kill_pattern "stygian_pollux_survivor_loader_pending",
     reason "pollux_survivor_loader_not_yet_implemented".  No file under stygian/loaders/ mentions pollux as a loader
     (the four hits there are ledger-union readers, see C5).  The Pollux -> Stygian hand-off therefore terminates in a
     placeholder verdict by construction.
  C3 Erebos [READ erebos/daemon.py:57-65, :87-106, :152-166; generators/g01_intersection.py:40-137; g04 grep :9, :47-48, :121]:
     _filter_substantive_recent keeps PROMOTED/UNVERIFIED/REJECTED rows whose kill_pattern does not end in _pending /
     _skipped / _loader_pending and whose emitted_at is within LOOKBACK_DAYS = 7; g01_intersection composes
     stygian_substantive x pollux_substantive reading kill_vector.corr_raw / corr_norm; g04_survivor_tightening takes
     "a PROMOTED Pollux row" as input.  [QUOTED docs/state.json:1290] pollux_substantive_recent = 286 at Erebos' last tick.
  C4 Ergon greedy corpus [READ ergon/learner/greedy/sources.py:158-201, :388]: pollux_examples reads the ledger path,
     skips rows with corr_raw or corr_norm None, and sets `gold = False  # kill_ledger entries are, by construction,
     the ones that did NOT survive`, justification "after normalization the correlation is {corr_norm}, so the raw
     correlation is a scale artifact ({kp})", tier 1, trust_weight 1.0, outcome "rejected".  This labels the 39
     PROMOTED rows as failures.  [READ manifest_v1.json] cap pollux 4000; yielded 286; by_outcome rejected 286; train
     86; gold_eval 200.  [EXECUTED git log] added in 7e38227ee (2026-06-07); manifest a8a276a40 (2026-06-09).
     [QUOTED pivot/generator_quality_handoff_for_ergon_2026-06-03.md:33] "charon/agents/pollux (286) NO_COOCCURRENCE 0.0%
     3 kps but every row unique batch_id".  [QUOTED evidence_wiki/v2/blind/V2-T08/Q.md:52] pollux is named as one of
     "the 3 originally-collapsing sources (theseus, hephaestus, pollux)" with a leave-one-out drop of 0.605.
  C5 Stygian composition loaders g15/g19 [grep only]: composition_g15_ledger_mi.py:40 and composition_g19_ledger_transitivity.py:41
     read the Pollux ledger path as part of a Stygian+Pollux+Erebos union.  [QUOTED pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md:39-41, :58-61]
     on 2026-05-26 the union held pollux rows sign_flips 47 / attenuates 44 / survives 39 (= 130), and the author
     classed the resulting MI as "structural by construction".
  C6 Ledgers/autopsies/triage (read-only registries): engine/ledger/AGENT_AUTOPSIES.jsonl line 18, engine/queues/BACKLOG.jsonl:106
     (AUTOPSY-POLLUX DONE) and :689 (PROF-Pollux PARKED "typed structural zero"), engine/queues/PROF_TRIAGE.jsonl:34
     (binding VACUOUS-NO-SOLVER).

### A.10 Historical verdicts (ZERO weight; recorded for the record)
  [QUOTED git log 8c619443a, 2026-05-24] v0.5 commit: "Live verification: deg10_vs_deg12 scan emitted REJECTED with
     pollux_sign_flips_under_normalization (raw 1.0, normalized -0.2235)".
  [QUOTED git log 43b094552, 2026-05-25] v0.6 commit: settle/auto-growth and PROMOTED->Stygian patches; "Pollux 100%
     deterministic"; Hecate prefix strip yields mi_crossgen 0.0046, z 0.489, n_crossgen_kps 4.
  [QUOTED pivot/charon_swarm_diminishing_returns_2026-05-25.md:14, :55-59, :184-189, :252] "Pollux 100% deterministic
     per-pair"; pool exhausts in ~5 weeks; POLLUX-* loader estimated ~120 LOC (never written); "2 Pollux survivor signals".
  [QUOTED pivot/charon_swarm_2026-05-27.md:70] tick log line: pair=narrow_band_1.10_1.20_vs_1.30_1.50 kp=pollux_sign_flips_under_normalization.
  [QUOTED aporia/docs/program_audit_2026-06-10.md:118-119] "39 PROMOTED ... 86 scale artifacts correctly REJECTED".
  [QUOTED pivot/REASSESSMENT_2026-06-22_consolidated.md:754] "Pollux = real signal".
  [QUOTED pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md:66] REVIVE, "Real signal".
  [QUOTED pivot/COMPONENT_DOSSIERS_2026-06-24.md:391-406] RETIRE-after-HITL; identifies the sorted/sorted pairing at
     :417-424 as a tautology; ALL 286 rows corr_raw = 1.0; verdicts REJECTED 86 / PROMOTED 39 / UNVERIFIED 161;
     candidate_pool_idx 5; ~200 artifacts; last run 2026-05-30; PROMOTED pairs deg14_vs_deg16, salem_vs_pisot,
     small_deg_vs_large_deg; "Ergon Learner has ZERO references to generator_id=pollux".
  [QUOTED charon/CHARON_SESSION_2026-08-12.md:165-175] "Pollux's sorted-array Spearman" listed as a tautology-cluster gold item.
  [QUOTED engine/ledger/AGENT_AUTOPSIES.jsonl line 18, 2026-08-21] failure_class LOW-BITS-PER-VERDICT-EMISSION
     (static-rescan form) + YIELD-BLIND-ROTATION; 286 rows {sign_flips 86, survives 39, attenuates 161}; 9 pairs each
     with distinct = 1; artifacts deg18_vs_deg20 x54, even_deg_vs_odd_deg x56; Hecate mi_crossgen 0.0034, z 0.98.
  [QUOTED engine/queues/PROF_TRIAGE.jsonl:34, 2026-08-20] binding VACUOUS-NO-SOLVER.

### A.11 Contradictory evidence (between records, and between records and code)
  X1 "real signal / REVIVE" (06-22, 06-23) versus "tautology, RETIRE" (06-24) versus "9 facts in 286 rows" (08-21):
     three verdict families about one unchanged corpse within nine weeks [QUOTED as above].
  X2 The 06-24 dossier's "Ergon Learner has ZERO references to generator_id=pollux" is contradicted by
     ergon/learner/greedy/sources.py pollux_examples (commit 7e38227ee, 2026-06-07, seventeen days earlier) and by
     manifest_v1.json (286 pollux rows) [READ; EXECUTED git log].
  X3 The 06-10 audit's "86 scale artifacts correctly REJECTED" presupposes that a raw correlation of 1.0 was a
     property of the data; under [READ daemon.py:415-420] it is a property of the pairing (P1).  The same
     presupposition is baked into Ergon's justification string [READ sources.py:158-201].
  X4 The v0.5 commit message treats "raw 1.0, normalized -0.2235" as the discipline firing correctly [QUOTED 8c619443a];
     the raw value was the same for every pair ever scanned [QUOTED dossier; INFERRED from P1].
  X5 The daemon's own log claims "active rotation shrunk" on pool exhaustion [READ :523-526]; the code path that
     precedes it never shrinks the rotation [READ :331-339] (P9).

### A.12 Later repairs
[EXECUTED git_history_census] daemon.py has exactly two commits (05-24 03:10, 05-25 01:46) and __init__.py one; no
change after 2026-05-25.  Repairs happened only around it: Hecate prefix strip (05-25, [QUOTED 43b094552]); Ergon
source added (06-07); Stygian POLLUX-* loader never written [READ ls loaders/; QUOTED diminishing-returns :184-189].
The settle/replace ordering defect (P9) was never patched.  The last tick on record is 2026-05-30T15:55:23Z
[QUOTED docs/state.json:1305].

### A.13 Surviving components (in-tree, importable, untouched by the defects)
_spearman (:212-235) -- a correct pure-python Spearman without tie-averaging; _mean_spacing_normalize (:238-250) --
a correct sorted-gap transform (the /mean_gap step is a no-op for any rank statistic, P3); _load_subset (:127-209) --
a reusable subset selector over mahler.py with seven kinds; the nine-pair taxonomy (:51-114) with written rationales;
the Theseus-shaped ledger row builder (:456-505); the settle machinery (:301-340) minus its ordering bug.  What does
NOT survive: the pairing step (:415-418) and the classifier's semantics when fed by it.

### A.14 PROPOSITIONS
P1  [READ daemon.py:415-420, :212-235] [RE-IMPLEMENTATION reimpl_pollux_null.py: 13,000/13,000 synthetic trials]
    Because a_paired and b_paired are both ascending-sorted before _spearman, corr_raw == 1.0 for every pair with
    n >= 10 and distinct values.  corr_raw carries zero bits about the data.
P2  [READ daemon.py:253-268] [RE-IMPLEMENTATION reimpl_classify_partition.py] Given P1 the classifier partitions on
    corr_norm alone: survives <=> corr_norm >= 0.30; sign_flips <=> -0.80 < corr_norm < 0; attenuates <=>
    0 <= corr_norm < 0.30 OR corr_norm <= -0.80; no_correlation_observed is UNREACHABLE.  A strong anti-correlation
    of gaps (<= -0.80) is labelled "attenuates" (UNVERIFIED), not "sign flips" (REJECTED).
P3  [READ daemon.py:238-250, :212-235] [RE-IMPLEMENTATION 2,000/2,000 trials, 0 mismatches] Dividing gaps by the mean
    gap does not change any rank; corr_norm equals Spearman(raw gaps of a, raw gaps of b).  The "normalization" is
    nominal; the operative transform is sorted differencing.
P4  [INFERRED from P1-P3] corr_norm measures whether the i-th smallest spacing in subset a co-ranks with the i-th
    smallest spacing in subset b, positionally.  It is a comparison of the two subsets' order-statistic spacing
    profiles, not a test of scale-independence of a correlation (there was no correlation to begin with).
P5  [READ daemon.py:415-418] sorted(x)[:n] censors the larger subset to its n smallest values; e.g. salem_vs_pisot
    compares the smallest-M Salem entries (of thousands, all near the Lehmer floor) against the full curated non-Salem
    set.  The pair names do not describe the populations actually compared.
P6  [READ daemon.py:386-578] No null, permutation, seed, p-value or reference distribution is computed anywhere;
    convergence_status is literally "exact".
P7  [READ daemon.py:216, :421-424] Refusal thresholds: n < 10 -> corr_raw None; n-1 < 10 -> corr_norm None; either
    yields UNVERIFIED "unmeasurable".  Hence a classified pair has n >= 11.
P8  [EXECUTED git log _mahler_data.py; READ mahler.py:457-467] [INFERRED] Inputs were constant across Pollux's
    lifetime (last data commit 05-05; Pollux ran 05-24 .. 05-30), so with a deterministic statistic every re-scan of
    a pair returned the identical row body; only emitted_at / record_id differed.  Consistent with [QUOTED autopsy
    line 18] "per-pair distinct = 1".
P9  [READ daemon.py:331-339, :523-526] When the pool is exhausted, _promote_settled_replace appends to settled_pairs,
    returns None, and never removes the settled pair from active_pairs; the log line "active rotation shrunk" is
    false.  A REJECTED pair that settles after the pool is exhausted is re-scanned and re-settled every fifth visit.
P10 [READ git show 8c619443a:charon/agents/pollux/daemon.py] v0.5 used a plain round-robin over TEST_PAIRS with no
    settle logic; settle/replace and the Stygian enqueue arrived in v0.6 (43b094552) after ~22.6 h of v0.5 running
    [EXECUTED git log timestamps].
P11 [RE-IMPLEMENTATION reimpl_rotation2.py, fitted only to the QUOTED final census] A two-phase model (K ticks of
    v0.5 round-robin, then v0.6 settle/replace with the P9 ordering defect, one row per tick, verdicts fixed per pair)
    reproduces the QUOTED census EXACTLY and UNIQUELY over the searched space (K in 0..120, all verdict assignments
    for the two pairs the record leaves open): K = 47; smyth_extremal_vs_rest = REJECTED; lehmer_witness_neighborhood
    = UNVERIFIED; totals R86/P39/U161; deg18_vs_deg20 x54; even_deg_vs_odd_deg x56; candidate_pool_idx 5;
    PROMOTED pairs exactly {deg14_vs_deg16, salem_vs_pisot, small_deg_vs_large_deg}.  Per-pair rows: deg10_12 17,
    deg14_16 17, salem_pisot 17, smyth 16, even_odd 56, small_large 5, narrow_band 53, deg18_20 54, lehmer 51.
P12 [RE-IMPLEMENTATION, same model, no extra parameter] [QUOTED pivot/erebos_substrate_finding_iter13...:39-41;
    docs/state.json:1318-1327] The fitted model predicts two records it was not fitted to: (a) the 2026-05-26 union
    census R47/U44/P39 occurs at exactly cumulative row 130 (and at no other row count); (b) the final row (tick 286)
    is even_deg_vs_odd_deg / UNVERIFIED, matching the Postgres mirror's last_tick_stats.
P13 [RE-IMPLEMENTATION trace] [NEEDS_CORONER to confirm] Predicted terminal state files: settled_pairs length 54
    (one each for smyth, deg10_12, salem, deg14_16, small_large in that order at ticks 63/64/65/68/82, then 49
    consecutive narrow_band REJECTED re-settles from tick 90 every 4 ticks); candidate_pool_idx 5; active_pairs =
    [deg18_vs_deg20, even_deg_vs_odd_deg, narrow_band_1.10_1.20_vs_1.30_1.50, lehmer_witness_neighborhood].
P14 [RE-IMPLEMENTATION reimpl_pollux_null.py] Under independent uniform inputs of n ~ 14-16 the classifier emits
    PROMOTED ~15 %, REJECTED ~48-50 %, UNVERIFIED ~35 %; at n = 72 PROMOTED 0.25 %; under two independent samples
    from the SAME exponential-gap family PROMOTED ~51 %.  The chance floor of "survives" is non-zero, strongly
    n-dependent, and inflated whenever both subsets share a spacing family -- which all Mahler subsets do [INFERRED].
P15 [READ stygian/executor.py:221-236; ls stygian/loaders/] Every PROMOTED Pollux row that reached Stygian was
    answered with stygian_pollux_survivor_loader_pending (UNVERIFIED) because no POLLUX loader exists.  Whether any
    row reached Stygian at all: 24 h dedup [READ daemon.py:528-567] plus three PROMOTED pairs settling by tick 82
    implies at most a handful of enqueues [INFERRED]; actual queue contents [NEEDS_CORONER].
P16 [READ erebos/daemon.py:87-106; g01:40-137; g04 grep] Erebos consumed Pollux rows (all three verdicts) inside a
    7-day window; g01 and g04 read corr_raw/corr_norm as if raw were informative.  Composed-claim outputs from those
    generators: NOT_EXAMINED (Erebos ledger not in tree).
P17 [READ ergon sources.py:158-201; manifest_v1.json] Ergon labelled all 286 Pollux rows gold=False / outcome
    "rejected", including the 39 PROMOTED rows, with a justification that asserts the raw correlation is a "scale
    artifact".  [QUOTED V2-T08/Q.md:52; harvest_a.jsonl:24] The pollux source later appears as a "collapsing"
    template class in the greedy-LoRA calibrating kill (leave-one-out drop 0.605).
P18 [READ hecate/daemon.py; QUOTED 43b094552, autopsy line 18] Hecate ingested the Pollux ledger; reported
    cross-generator MI was 0.0046 (z 0.489) on 05-25 and 0.0034 (z 0.98) at autopsy -- the infrastructural claim of
    __init__.py ("necessary precondition for ... MI to become non-zero") was met in the trivial sense (rows existed)
    and unmet in the intended sense (no cross-generator structure).
P19 [EXECUTED git_history_census; READ .gitignore] No output of Pollux is in git; the corpse's evidence exists only in
    M2 state directories and a Postgres mirror.  Every count above P11 is QUOTED, and P11-P13 are inferences about
    those quotes, not about the ledger.
P20 [QUOTED 06-10, 06-22, 06-23, 06-24, 08-21] Five records drew four incompatible conclusions about an artifact that
    did not change after 05-25; the divergence is in the readers, not the corpse.
P21 [READ daemon.py:51-76] The design's own stated expectation for deg10_vs_deg12 -- "expect minimal correlation if
    Mahler measures are scale-independent" -- names the one label (no_correlation_observed) that P2 shows the code
    cannot emit.
P22 [READ daemon.py:1-29, :456-505; __init__.py] The organism emitted rows in the Theseus ledger shape with
    method "spearman_with_meanspacing_normalization" and convergence "exact"; downstream readers (Hecate, Erebos, Ergon)
    had no field by which to distinguish a Pollux "verdict" from a Theseus battery verdict.
P23 [READ ls charon/agents/pollux/__pycache__] daemon .pyc mtime 2026-09-11 13:26 and __init__ .pyc mtime
    2026-09-13 20:54 -- the package has been imported on this machine within the last three days.  By whom:
    NOT_EXAMINED (candidates are under excluded paths).
P24 [QUOTED docs/state.json:1300-1330] The Postgres mirror gives last_tick corr_norm = 0.0817 for even_deg_vs_odd_deg;
    by P2 this is "attenuates" and by P14 is inside the region where an independent-input null would place ~35 % of
    outcomes.  It is the only per-pair corr_norm value I could locate outside excluded paths; the other eight are
    [NEEDS_CORONER].

### A.15 Draft DEATH CERTIFICATE
  Deceased:        Pollux (charon/agents/pollux/daemon.py @ 43b094552), Charon swarm, M2, 2026-05-24 .. 2026-05-30.
  Cause class:     DESIGN_ERROR.
  Mechanism:       The pairing step (P1) made the "raw" statistic a constant, so the experiment's stated contrast
                   (raw vs normalized) never existed; the residual statistic (P3-P4) had no null (P6, P14); the
                   rotation logic (P9-P11) re-emitted nine fixed facts 286 times.  The corpse could not have answered
                   its question from its first tick.
  Strongest rival: CONSUMER_ABSENT -- every downstream reader either could not act (Stygian loader never written,
                   P15), acted on the wrong premise (Ergon gold=False for PROMOTED, P17; Erebos g01/g04 reading
                   corr_raw as data, P16), or measured null (Hecate, P18).  Even a correct Pollux would have died here.
  Further rivals:  MEASUREMENT_ERROR (if one insists the statistic was fine and only the pairing was wrong -- but the
                   pairing IS the measurement); RECORD_INSUFFICIENT (P19: nothing to autopsy in git; but the design
                   verdict rests on code, not on the missing ledger).
  Not the cause:   HYPOTHESIS_FAILURE -- the hypothesis "Mahler subset correlations are scale artifacts" was never
                   put to a test that could fail it (P21).  INFRASTRUCTURE -- the loop ran, ticked, persisted and
                   mirrored (A.5); nothing crashed.

--------------------------------------------------------------------------------------------------
## PART B -- CLERIC: attack Part A
--------------------------------------------------------------------------------------------------

### B.1 Attack the death certificate (DESIGN_ERROR)
Attack: DESIGN_ERROR requires that the design could not have answered its question.  But the design DID produce a
data-dependent quantity, corr_norm, that varied across pairs (three PROMOTED, three or four REJECTED, others
UNVERIFIED, P11) and whose sign/magnitude was not preordained.  A scanner that partitions nine pairs three ways on a
genuine statistic is not a tautology; the Necromancer has let the constant raw column contaminate the verdict on the
whole.  The fair reading is that a mislabelled but real experiment ran: "do consecutive spacings of the n smallest
Mahler measures co-rank across subsets a and b?".
Evidence: P2, P3, P11, P24 (the corr_norm values differ by pair; -0.2235 for deg10_12 [QUOTED 8c619443a], 0.0817 for
even_odd [QUOTED state.json]).
Outcome: WEAKENED.  The certificate's mechanism sentence is overstated -- one of the two numbers was live.  But the
attack does not restore the CLAIMED question (raw-vs-normalized), only a different, unstated one, and it leaves P6/P14
untouched: the live number had no reference distribution, so even its three-way partition carries no evidence.
DESIGN_ERROR stands with the mechanism narrowed to "the contrast was constant and the residual was unreferenced".

### B.2 Attack the reconstructed cause (the P9-P13 rotation account)
Attack: P11-P13 are a synthetic model fitted to five QUOTED integers; a five-parameter search hitting five integers
proves fit, not truth.  The unique-solution claim depends on the search space chosen (K <= 120, one row per tick,
fixed verdicts).  The "prediction" of the 05-26 checkpoint uses the same mechanism and the same K, so it is not
independent of the fit.
Evidence: P11, P12; the census values themselves are unverified QUOTED numbers (P19).
Outcome: WEAKENED but not FALLS.  Reply on the record: the checkpoint (R47/U44/P39 at row 130) constrains the
ordering of verdicts in time, which the final census does not -- a model fitted only to totals has no reason to hit
an interior cumulative count at one and only one row.  And the last-tick pair (P12b) is a fourth-cycle phase check.
Still, three concordant QUOTED records could share one upstream error.  The account is a strong retrodiction, not an
observation; its checkable residue is P13 (settled_pairs length 54), which a coroner can read from M2 state in
seconds.  UNTESTABLE_WITHOUT_EXECUTION for the state files; STANDS as an inference about the code.

### B.3 FAIR-test claim: the experiment could have answered its question
Attack (Cleric arguing FAIR): the question "does the correlation survive normalization" is answerable by this
apparatus if one grants that the author's "raw correlation" was deliberately the Q-Q correlation of sorted values
(always 1 -- a known baseline) and the "normalized" one is the spacing-profile correlation.  Then the pipeline is a
legitimate one-sample-per-pair descriptive statistic, and the "test" is descriptive, not inferential.
Evidence: docstring [READ daemon.py:1-29] speaks of "numerical coincidence", a descriptive aim; rationales [READ :51-76].
Outcome: FALLS.  Three independent readings of the record refuse this: (i) the classifier uses the raw value as a
gate (`if not raw_sig`) and names a label for its absence (P2, P21) -- the author expected it to vary; (ii) the
v0.5 commit message reports "raw 1.0" as a finding, not a baseline (X4); (iii) every consumer treated the raw column
as data (X3, P16, P17).  A descriptive statistic without a reference distribution cannot answer a survive/not-survive
question; FAIR would require at least P14's null.  The experiment could not have answered its question.

### B.4 UNFAIR-test claim: the experiment could not have answered its question
Attack (Cleric arguing against UNFAIR, i.e. for the corpse): perhaps the apparatus is unfair only for n small; at the
full subset sizes (thousands of Known180 rows for even-degree/Salem) the spacing-profile Spearman between two
large ordered samples has a tight null (P14: PROMOTED 0.25 % at n = 72), so a PROMOTED at large n would have been
informative, and small_deg_vs_large_deg / salem_vs_pisot may have been such cases.
Evidence: P5 (n = min of the two, so n is governed by the SMALLER subset -- the curated tier, tens of entries);
P7; P14.  n_paired per pair is [NEEDS_CORONER].
Outcome: STANDS (UNFAIR).  Because n is the smaller subset's size and the smaller subset is always curated
(tens), the large-n regime the attack needs was never reached [INFERRED from A.4 counts; NEEDS_CORONER for exact n].
And P5 adds a second unfairness independent of n: the larger subset is censored to its n smallest values, so the
compared populations are not the named ones.  Both unfairnesses are visible in the code without the ledger.

### B.5 Salvage value
Attack: the Necromancer's A.13 salvage list is generous; _spearman lacks tie-averaging (P3's rank function), the
pair taxonomy encodes the P5 confusion in its names, and the ledger-row builder stamps "exact" on an unreferenced
statistic (P22) -- it is the vector by which the defect propagated.
Evidence: P3, P5, P22; A.13.
Outcome: WEAKENED.  Salvage reduces to: _mean_spacing_normalize (as a sorted-gap transform), _load_subset (seven
kinds over mahler.py, correct as far as read), and the nine pair DEFINITIONS (the specs, not the names).  The
statistic, the classifier, the row builder and the settle machinery should not be re-used without the P9 fix and a
null.  The most valuable salvage is negative knowledge: P1-P2 are a textbook instance for the tautology-cluster
[QUOTED CHARON_SESSION_2026-08-12.md:165-175].

### B.6 Frankenstein counterfactual (one mutation that would have changed the outcome)
Mutation F-A: replace `a_paired = sorted(a_vals)[:n]; b_paired = sorted(b_vals)[:n]` (:417-418) with pairing by a
common index (e.g. by polynomial identity or by degree-matched rank) so that corr_raw can vary.
Attack on F-A: there is no natural common index between two disjoint subsets of Mahler measures; any pairing is a
choice, and the rank-by-order pairing IS the Q-Q choice.  F-A changes the question, not the outcome.
Mutation F-B: keep the pairing, add a permutation null for corr_norm (shuffle gap order within each series, 200
draws, as Hecate already does with N_PERMUTATIONS = 200 [READ hecate/daemon.py:44-56]) and classify on the z-score.
Attack on F-B: under P14 the null of "same spacing family" is ~51 % PROMOTED, so a within-series shuffle null would
still promote shape-similar pairs; the correct null is between-family, which needs a model of Mahler spacings that
nobody had.
Mutation F-C: swap lines :331-332 below :336-339 (remove-then-check) so the rotation truly shrinks.
Attack on F-C: it changes the 286-row census (narrow_band would emit 5 rows, not 53; total rows would fall and the
final rotation would be three pairs) but not one verdict.
Evidence: P1, P9, P11, P14.
Outcome: F-A UNTESTABLE_WITHOUT_EXECUTION (needs the data); F-B STANDS as the one mutation that changes the
outcome's meaning (a z-scored corr_norm could REFUSE, G4 cannot); F-C STANDS as the one mutation that changes the
outcome's SHAPE (census) with zero change to content -- which is itself the cleanest demonstration that the rows
carried no information beyond nine facts.  Proposition attacked: P1 (survives), P9 (survives), P14 (survives, with
the caveat that the right null is unspecified).

### B.7 Cleric's own conclusion
The record decides DESIGN_ERROR at the level of code (P1, P2, P6, P9, P21) without any need for the ledger.  What the
record cannot decide is whether the residual statistic corr_norm carried any signal for any pair -- that is a
HYPOTHESIS question that was never posed properly and cannot be posed post hoc without a null over the actual inputs
[NEEDS_CORONER].  I decline to relabel as HYPOTHESIS_FAILURE: a hypothesis that was never tested did not fail.

--------------------------------------------------------------------------------------------------
## PART C -- JUDGE
--------------------------------------------------------------------------------------------------

### C.1 Disputed propositions
  D1  P1 (raw statistic constant) -- Necromancer: [READ :415-420] + 13,000 synthetic trials.  Cleric: does not
      dispute the fact, disputes its weight (B.1).  Type: taxonomic (is a constant column a "design error" or a
      "baseline").  Resolving observation: the author's intent as evidenced by the classifier branch `if not raw_sig`
      and the v0.5 commit message -- both already in the record (P2, X4).  Worth its cost: already paid.  Ruling: P1
      is a design error, not a baseline; the code names the unreachable case.
  D2  P11-P13 (rotation retrodiction) -- Necromancer: exact, unique fit + two out-of-fit hits.  Cleric: fit to
      QUOTED integers, shared mechanism.  Type: epistemic.  Resolving observation: read settled_pairs.json
      (predicted length 54, 49 narrow_band entries) and candidate_pool_idx (5) from M2 state -- a file read, no
      execution (P13).  Worth its cost: yes, trivially cheap, and it converts the whole rotation account from
      retrodiction to observation.  Until then: STANDS as inference; the ledger-level counts remain QUOTED.
  D3  P14 (chance floor of PROMOTED) -- Necromancer: 15 % / 51 % on synthetic inputs.  Cleric: the right null family
      is unspecified (B.6 F-B).  Type: causal (what would count as chance for this statistic).  Resolving observation:
      corr_norm of each of the nine pairs against (a) a within-series shuffle and (b) a between-subset resample of
      the actual Mahler table -- coroner action M3 [NEEDS_CORONER].  Worth its cost: only if anyone intends to reuse
      the spacing-profile statistic; for classifying this grave it is not needed (D1 suffices).
  D4  B.4 n regime -- Necromancer: n is bounded by the curated tier.  Cleric: maybe not for some pairs.  Type: factual.
      Resolving observation: n_paired field in any one ledger row per pair (nine JSON reads) [NEEDS_CORONER].  Worth
      its cost: yes; it is the cheapest observation on the list and settles P5's severity per pair.
  D5  Cause class DESIGN_ERROR vs CONSUMER_ABSENT -- Necromancer: design first.  Cleric (B.1, B.7): design at code
      level; consumers as amplifier.  Type: causal ordering.  Resolving observation: none available -- the two causes
      are not competing explanations of one death but two independent sufficient deaths (P1 kills the science; P15-P18
      kill the plumbing).  Worth its cost: no observation needed; the ruling is that both hold and the certificate
      should carry a secondary cause.
  D6  B.3/B.4 FAIR vs UNFAIR -- Type: taxonomic + causal.  Resolving observation: none required beyond the code
      (P2, P5, P6, P21).  Ruling: UNFAIR; the experiment could not answer its question with any input.
  D7  P17 (Ergon mislabelling) -- undisputed as fact; disputed as to consequence (did it matter?).  Type: causal.
      Resolving observation: the minus_pollux ablation condition [READ run_ablation.sh] result, which is under excluded
      paths (roles/Ergon/*) -- NOT_EXAMINED here; [QUOTED V2-T08/Q.md:52] gives 0.605 second-hand.  Worth its cost:
      moderate; relevant to Ergon's grave, not this one.
  D8  P23 (recent import of the package) -- undisputed fact; disputed relevance (contamination of a control arm?).
      Type: epistemic.  Resolving observation: who compiled it (excluded paths; the workshop adapters and
      run_controls.py are the trace's own candidates).  Worth its cost: low for this case; the court should know that
      the corpse has been imported on this machine during the cycle.

### C.2 Final classification of the grave
Cause of death: DESIGN_ERROR (primary; established from code alone: P1, P2, P6, P9, P21) with CONSUMER_ABSENT as an
independently sufficient secondary cause (P15-P18), not a rival.  Shape of the failure: a two-number contrast whose
first number was a constant by construction; a second number with a non-zero, n-dependent, family-dependent chance
floor and no null; a rotation that, after the pool emptied on the fifth settle, re-emitted four fixed rows forever
because of an ordering bug, so that 286 rows encoded nine facts; consumers that read the constant as data (Ergon,
Erebos), could not act (Stygian), or measured null (Hecate); a documentary trail that reversed itself three times
without the artifact changing.  The corpse was DOA at tick 1 (P21) and ran for six days.
Fairness of the test: UNFAIR (D6).  Salvage: _load_subset, _mean_spacing_normalize, the pair specs; and the design
itself as a calibration item for the tautology cluster.  HYPOTHESIS_FAILURE: not applicable -- untested.

### C.3 Unresolved (and, for some, deliberately so)
  U1 The actual per-pair (corr_norm, n_paired) for eight of nine pairs [NEEDS_CORONER: nine JSON reads on M2 state].
  U2 Whether P13's terminal state is as predicted [NEEDS_CORONER: one file read].  Until read, P11-P13 are inference.
  U3 Whether corr_norm carried any signal for any pair under a defensible null (D3).  Should remain unresolved unless
     someone proposes to reuse the statistic; resolving it would be a new experiment, not an autopsy.
  U4 How many PROMOTED rows actually reached the Stygian queue and how many loader_pending rows Stygian emitted
     [NEEDS_CORONER: stygian ledger + queue file].
  U5 What Erebos g01/g04 composed from Pollux rows and whether any composed claim was later graded [NOT_EXAMINED:
     Erebos ledger not in tree; dossiers under excluded paths].
  U6 The Ergon minus_pollux ablation figure at first hand (D7) [excluded paths].
  U7 Who imported the package on 2026-09-11 and 2026-09-13 (P23) [excluded paths].
  U8 Whether the 06-22/06-23 "real signal" verdicts rested on any observation beyond the 39 PROMOTED count -- the
     documents cite none [QUOTED :754, :66]; the readers who wrote them are not on trial here and I leave it open.
  U9 The contents of pivot/stygian_executor_scoping_2026-05-21.md, cited by __init__.py as the design's warrant
     [NOT_EXAMINED].

-- end of report -- propositions: 24 --
