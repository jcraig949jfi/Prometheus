"""_build_dossier.py -- assembles ../erebos.dossier.json from the five
result JSONs in this directory so every number in the dossier is traceable
to an executed script (or is labelled as a historical quote). Re-run after
any evidence script changes. Pure ASCII output; repo root from __file__.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
EV = "engine/necropolis/dossiers/erebos_evidence/"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="ascii"))


seam = load("erebos_seam_census_result.json")
tests = load("erebos_tests_offline_result.json")
refs = load("erebos_external_refs_result.json")
hist = load("erebos_history_census_result.json")
cal = load("erebos_null_instrument_calibration_result.json")
cons = load("erebos_consumer_audit_rerun_result.json")
keeper = json.loads((REPO / "engine/necropolis/dossiers/_keeper_evidence/"
                     "intelligence_outputs_census_result.json").read_text())
keeper_e = keeper["graves"]["erebos"]

tc = {k: v["counts"] for k, v in tests["scopes"].items()}
n_pass = sum(c.get("passed", 0) for c in tc.values())
n_fail = sum(c.get("failed", 0) + c.get("error", 0) + c.get("errors", 0)
             for c in tc.values())
h3k = hist["historical_quotes"]["PHASE3_K_verdict_doc"]
cal_s = cal["summary"]
runs_null = [r for r in cal["runs"] if r["world"] == "NULL"]
runs_pl = [r for r in cal["runs"] if r["world"] == "PLANTED"]

E_SEAM = EV + "erebos_seam_census_result.json"
E_TEST = EV + "erebos_tests_offline_result.json"
E_REFS = EV + "erebos_external_refs_result.json"
E_HIST = EV + "erebos_history_census_result.json"
E_CAL = EV + "erebos_null_instrument_calibration_result.json"
E_CONS = EV + "erebos_consumer_audit_rerun_result.json"
E_KEEP = "engine/necropolis/dossiers/_keeper_evidence/intelligence_outputs_census_result.json"
E_HALT = "engine/necropolis/dossiers/_keeper_evidence/fleet_halt_census_result.json"

seam_line = (f"[EXECUTED {E_SEAM}] REGISTRY={seam['erebos_registry_n']} plugins; "
             f"executor force-imports {seam['executor_forced_import_modules_n']} composition "
             f"loader modules, {seam['loaders_registered_n']} register, "
             f"{len(seam['loader_import_failures'])} import failures; find_loader() resolves a "
             f"daemon-shaped row for {seam['find_loader_synthetic_hits_n']}/25 plugins; the "
             f"{seam['erebos_quarantined_n']} plugins with 0 loaders are exactly the "
             f"{seam['erebos_quarantined_n']} quarantined by _quarantine.py (loader-debt cap); "
             f"daemon queue-row keys cover every key the loaders read "
             f"(missing={seam['loader_keys_not_emitted_by_daemon']}); non-erebos control row "
             f"resolves={seam['control_non_erebos_row_resolves']}.")
test_line = (f"[EXECUTED {E_TEST}] pytest offline at baseline: erebos tests "
             f"{tc['erebos_tests']}, sprint1 {tc['erebos_sprint1_tests']}, stygian composition "
             f"{tc['stygian_composition_tests']}; total passed={n_pass} failed/error={n_fail}; "
             f"0 network-library imports in the packages grepped.")
refs_line = (f"[EXECUTED {E_REFS}] P57 grep replicated in its own scope (case-sensitive EREBOS "
             f"over engine/, techne/, charon/BACKLOG.md, charon/CHARON_SESSION_*.md): "
             f"{refs['A_p57_replication']['files_with_hits_n']} files, all autopsy/queue ledgers "
             f"written by the same program; same scope case-insensitive: "
             f"{refs['A2_p57_scope_case_insensitive']['files_with_hits_n']} files. Tracked tree, "
             f"case-insensitive, excluding the agent's own dir and pivot/erebos_*: "
             f"{refs['B_extended_census']['files_external_n']} files, of which "
             f"charon/agents/stygian={refs['B_extended_census']['external_by_bucket'].get('charon/agents/stygian')}, "
             f"harmonia={refs['B_extended_census']['external_by_bucket'].get('harmonia')}; code importers of "
             f"charon.agents.erebos outside it: {refs['B2_code_importers']['files']}.")
hist_line = (f"[EXECUTED {E_HIST}] git log charon/agents/erebos: "
             f"{hist['git_log_erebos_dir']['commits_n']} commits "
             f"{hist['git_log_erebos_dir']['first']}..{hist['git_log_erebos_dir']['last']}; "
             f"composition loaders: {hist['git_log_stygian_composition_loaders']['commits_n']} commits "
             f"{hist['git_log_stygian_composition_loaders']['first']}..{hist['git_log_stygian_composition_loaders']['last']}; "
             f"highest ITER named in docs/code below 100 = 84; ITER-100 named only as the future "
             f"pre-committed kill ({hist['historical_quotes']['ITER_100_mentions_n']} mentions); runtime "
             f"state/artifacts/logs/queues absent in this worktree, the main worktree and the data backup.")
keeper_line = (f"[EXECUTED-BY-KEEPER {E_KEEP}] agora.intelligence_outputs: {keeper_e['rows']} rows stage "
               f"erebos_tick_complete, all success=true, {keeper_e['first_finished_at'][:16]} .. "
               f"{keeper_e['last_finished_at'][:16]} local, {keeper_e['distinct_cycle_id']} distinct cycle_id; "
               f"every summary ends enqueued=True; heartbeat online at last row. Dual-recorded, "
               f"single-mechanism: written by the Erebos daemon itself.")
cal_line = (f"[EXECUTED {E_CAL}] committed harness pair_aware_permutation_null.py run unchanged on "
            f"synthetic 699-row ledgers: NULL worlds observed={cal_s['NULL_observed']} null_p95="
            f"{cal_s['NULL_null_p95']} p={cal_s['NULL_p_values']}; PLANTED strong partner-conditioned "
            f"linkage observed={cal_s['PLANTED_observed']} p={cal_s['PLANTED_p_values']} detected at "
            f"p<0.05: {cal_s['PLANTED_detected_at_p05']}/3; smallest observed count that clears p<0.05 = "
            f"{sorted(set(r['min_observed_to_clear_p05'] for r in cal['runs']))}. Historical Phase 3.K: "
            f"observed=2, null_p95=2, p=0.105 [QUOTED {h3k['path']}].")
cons_line = (f"[EXECUTED {E_CONS} via scripts/composed_claim_consumer_audit.py] ComposedClaim fields "
             f"{cons['summary']['n_fields']}, with consumers {cons['summary']['n_with_consumers']}, "
             f"zero-use {cons['summary']['zero_use_field_names']} (May 28 audit: 4 zero-use; the two cost "
             f"fields gained consumers after May 28 [QUOTED pivot/erebos_composed_claim_consumer_audit_2026-05-28.json]).")

L = lambda v, f, ev, cc=(), lb=False: {  # noqa: E731
    "verdict": v, "finding": f, "evidence": list(ev), "cause_classes": list(cc), "load_bearing": lb}

stack = {
    "HYPOTHESIS": L("VALID",
        "Two hypotheses sit under one agent_id. H-A (Layer 1): composing existing Stygian/Pollux/Hecate "
        "verdicts into new falsifiable claims yields claims the falsifier can verdict. H-B (Layer 2): a "
        "kill_tensor + cross-cell motif + routing substrate adds measurable value over a Layer-1-only "
        "baseline (pre-committed test at ITER-100). Neither was refuted on the record: H-A was exercised "
        "(14/25 plugins reached a loader; PROMOTED/REJECTED/UNVERIFIED verdicts by ITER-5, later "
        "self-reclassified to catalog/substrate tier); H-B's pair-aware claim was reported STATISTICALLY "
        "UNDERDETERMINED and its triplet sub-claim FALSIFIED, and the ITER-100 test was never run "
        "(max ITER-84). Not a HYPOTHESIS_FAILURE on this record; also not a confirmation.",
        [seam_line, hist_line,
         "[QUOTED pivot/erebos_substrate_finding_iter5_salem_extends_to_band_2026-05-26.md] tally at ITER-5: "
         "7 composition loaders, 2 PROMOTED, 4 REJECTED at expected kill pattern, 1 UNVERIFIED.",
         "[QUOTED pivot/erebos_finding_reclassification_2026-05-27.md] the author moved the ITER-4/5/13 "
         "findings to Catalog tier and G10/G15 to Substrate tier: real verdicts, modest mathematics.",
         f"[QUOTED {h3k['path']}] {h3k['verdict_line'][:220]}"]),
    "DESIGN": L("VALID",
        "The design pre-committed its own kill (ITER-100 Layer-2-vs-Layer-1; Sprint-1 rule >=4/10 fails -> "
        "PAUSED), capped loader debt with an explicit quarantine (the 11 loaderless plugins are exactly the "
        "11 quarantined), and shaped its queue rows to the loader contract. Two design weaknesses are "
        "recorded but not found load-bearing: (i) two hypotheses share one agent and one kill switch; "
        "(ii) the Sprint-1 gate ran on synthetic fixtures (10/10 PASS) and is calibration, not value.",
        [seam_line, test_line,
         "[READ charon/agents/erebos/sprint1/verdict.py] KILL_RULE_MAX_FAILS = 4; go_no_go PROCEED/PAUSED.",
         "[READ pivot/erebos_doctrine_v1_2026-05-27.md L55; pivot/erebos_design_philosophy_dna_2026-05-26.md L309] "
         "ITER-100 pre-commitment text."]),
    "IMPLEMENTATION": L("VALID",
        "The compose->falsify seam exists in code and executes offline today: daemon enqueues a "
        "stygian_priority row; charon/agents/stygian/daemon.py maps source=erebos rows to EREBOS-<composed_id> problems; "
        "the executor force-imports 29 composition loaders and dispatches via find_loader() or "
        "short-circuits to *_loader_pending. 813 tests pass at baseline. The P57 statement that the seam "
        "'was never built' is contradicted by executed evidence.",
        [seam_line, test_line, cons_line,
         "[READ charon/agents/_base.py L303-305] the Charon swarm host instantiates ErebosAgent by name."]),
    "CONFIGURATION": L("VALID",
        "No configuration defect found. Daemon input paths are the three sibling kill_ledgers under "
        "charon/agents/*/state plus Hecate artifacts (LOOKBACK_DAYS=7); the daemon's own tick summaries "
        "report stygian_recent=166 / pollux_recent=95, i.e. it saw its inputs. Queue-row keys match loader "
        "keys (0 missing). Caveat: the runtime config it actually ran under (M2, May 2026) is not on the "
        "tree; this verdict rests on the code contract plus the daemon's self-reports.",
        [seam_line, keeper_line]),
    "EXECUTION": L("VALID",
        "It ran: 213 tick rows 2026-05-26 02:32 .. 2026-05-30 11:59 (local), all success=true, every "
        "summary enqueued=True; 39 commits on the agent dir 05-26..06-03 reaching ITER-84 of a 100-ITER "
        "pre-commitment. It did not stop on its own: 15 May-fleet agents wrote their last row 11:40-12:25 "
        "on 05-30 (fleet halt), Stygian/Pollux/Hecate included. 234 composed_claim artifacts (P57 count) "
        "vs 213 ticks: different objects or windows; gap recorded, not reconciled. No runtime artifact "
        "survives on this host.",
        [keeper_line, hist_line,
         f"[EXECUTED-BY-KEEPER {E_HALT}] stygian last 2026-05-30 12:03, hecate 12:20, pollux 11:55, erebos 11:59 (local)."]),
    "INSTRUMENTATION": L("INVALID",
        "The primary observations (kill_ledger.jsonl, composed_claim_*.md artifacts, per-plugin logs, "
        "tick_counter, stygian_priority queue) were gitignored and were never archived: absent from this "
        "worktree, the main worktree and the data backup; Harmonia B already reported 'real ledgers absent "
        "on M2' on 2026-06-15. What survives is second-hand: pivot docs, the 06-03 verdict doc, and the "
        "daemon's own agora rows. Not load-bearing for the original run (the instruments wrote), but "
        "load-bearing for any re-audit: the 699-row ledger behind Phase 3.K cannot be re-measured.",
        [hist_line, keeper_line,
         "[READ git show 2905c5659] Harmonia B 2026-06-15: imports charon.agents.erebos._cross_cell_motif "
         "and sprint1.phase3 harnesses; notes real ledgers absent on M2."],
        ["INSTRUMENT_ERROR"], False),
    "MEASUREMENT": L("INVALID",
        "The number behind '0 permutation-null survivors' is Phase 3.K: observed=2 substrate-vs-pair-aware "
        "deltas against a null with p95=2 (p=0.105, N=699 rows, 200 permutations, seed 1789). Executing the "
        "committed harness unchanged on synthetic 699-row ledgers shows the statistic has no resolution in "
        "this regime: NULL worlds give observed 0 with null_p95 1; a strongly PLANTED partner-conditioned "
        "linkage gives observed 0-1 and is detected 0/3 times, because the pair-aware counter captures the "
        "same linkage the substrate does. The smallest count that clears p<0.05 is 2-3. 'Underdetermined' "
        "was therefore a property of the instrument, not evidence about Layer-2 value. Scope limit: the "
        "planted signal is one class; a lift-only signal class was not tried.",
        [cal_line,
         f"[QUOTED {h3k['path']}] N_PERMUTATIONS={h3k['n_permutations_quoted']}, SEED={h3k['seed_quoted']}, "
         f"observed vs pair-aware={h3k['observed_deltas_vs_pair_aware']}, vs per-plugin={h3k['observed_deltas_vs_per_plugin']}, "
         f"p={h3k['p_value_quoted']}, 7-seed mean={h3k['seven_seed_mean_quoted']}.",
         "[QUOTED charon/CHARON_SESSION_2026-06-03.md] triplet: observed 1 vs null ~14, FALSIFIED; per-plugin "
         "p 0.055->0.075 on the 699-row ledger. Not re-executed (ledger absent)."],
        ["MEASUREMENT_ERROR"], True),
    "INTERPRETATION": L("INVALID",
        "Two later interpretations diverge from the primary record. (1) 'STATISTICALLY UNDERDETERMINED' "
        "(06-03) became 'realized ~0 (0 perm-null survivors)' (06-23/24) and 'realized value ~0' (queue): an "
        "unresolved test read as a null result. (2) P57 (08-21) asserted the seam 'was never built' and "
        "'ZERO external references' from a case-sensitive grep whose scope excluded charon/agents/stygian "
        "(53 files naming Erebos, 29 loaders) and harmonia/ (19 files, one importing Erebos code), and read "
        "review.py (a per-plugin health runner) as self-verdicting. The grep reproduces inside its own "
        "scope, so the error is scope, not fabrication. Load-bearing for the SELF-CONTAINED-GENERATION "
        "label; not the cause of the pause.",
        [refs_line, seam_line,
         "[QUOTED engine/ledger/AGENT_AUTOPSIES.jsonl Erebos row] 'the compose->falsify seam, which was never "
         "built ... ZERO external references across charon session docs, backlogs, and other workers' artifacts'.",
         "[QUOTED pivot/COMPONENT_DOSSIERS_2026-06-24.md L317] 'composition-aware loader never shipped (claims "
         "short-circuit as *_pending)'; contradicted by 19 loader commits 05-26..05-30 and ITER-5 verdicts."],
        ["INTERPRETATION_ERROR"], True),
    "ECOSYSTEM": L("INVALID",
        "Erebos stopped because its ecosystem stopped, twice: the 2026-05-30 fleet halt (all May agents "
        "within 45 minutes) and the 2026-06-15 program reset ('immune system with no organism'; 'off-spine "
        "until it has a consumer'), where 'consumer' meant an organism that uses verdicts, not the falsifier "
        "(which existed and had loaders). No kill condition of Erebos's own ever fired: Sprint-1 rule 10/10 "
        "PASS, ITER-100 unreached. This is the primary cause of death.",
        [keeper_line, hist_line,
         "[QUOTED charon/CHARON_SESSION_2026-06-15.md L7,L51-52] reset; 'Don't reopen Erebos ... off-spine until it has a consumer.'",
         "[QUOTED pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md L75] 'PAUSED -> revive only post-organism ... "
         "Pre-committed kill at ITER-100.'"],
        ["ECOSYSTEM_FAILURE"], True),
}

dossier = {
    "schema_version": "1.0.0",
    "kind": "necropolis_dossier",
    "_README": "Necromancer dossier for Erebos (Charon swarm composer, 25 generator archetypes, May 2026). "
               "Every bracketed [EXECUTED ...] number comes from a script under erebos_evidence/ with a "
               "*_result.json; [QUOTED ...] numbers are historical and not re-measured; [READ ...] is "
               "code or prose inspected without execution. See erebos_evidence/README.md sections 7-8 for "
               "portability defects and the validator output.",
    "identity": {
        "agent_id": "Erebos",
        "aliases": ["erebos", "ErebosAgent", "Erebos composer", "metabolization composer (25 archetypes)"],
        "historical_machine": "M2 (ROSTER.jsonl); daemon rows in agora.intelligence_outputs on the M1 store",
        "historical_kind": "tool (ROSTER.jsonl); Charon swarm v0.8 plugin agent",
        "historical_operator": "Charon (2026-05-26..06-03); paused by the 2026-06-15 program reset",
        "source_paths": [
            "charon/agents/erebos/daemon.py", "charon/agents/erebos/generators/ (25 plugins, REGISTRY)",
            "charon/agents/erebos/_quarantine.py", "charon/agents/erebos/review.py",
            "charon/agents/erebos/sprint1/verdict.py", "charon/agents/erebos/sprint1/phase3/",
            "charon/agents/erebos/tests/ (39 files + sprint1/ 11 files)",
            "charon/agents/stygian/executor.py (EREBOS-* branch L151-215)",
            "charon/agents/stygian/daemon.py (L197-207)", "charon/agents/stygian/loaders/_composition.py",
            "charon/agents/stygian/loaders/composition_*.py (29)",
            "charon/agents/stygian/tests/test_composition_*.py (14)", "charon/agents/_base.py (L303-305)",
            "pivot/erebos_* (44 docs)", "pivot/sprint1/phase3/ (7 verdict docs)",
            "charon/CHARON_SESSION_2026-06-03.md", "charon/CHARON_SESSION_2026-06-15.md",
            "engine/ledger/AGENT_AUTOPSIES.jsonl (Erebos row, P57)",
            "pivot/COMPONENT_DOSSIERS_2026-06-24.md (### Erebos)",
            "pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md (row 33)",
            "engine/necropolis/dossiers/_keeper_evidence/ (agora census, read-only)",
        ],
        "evidence_baseline": "e17934d9a82855b6e0ae1c0bf54c0cce569b7795",
    },
    "original_organism": {
        "premise": "A generative layer over an existing falsification swarm: compose new claims from prior "
                   "verdicts (Layer 1), route composition by a kill-pattern tensor and cross-cell motifs "
                   "(Layer 2), and let the existing falsifier verdict them; value = PROMOTED claims per cost.",
        "mechanism": "Per tick: build SwarmState from Stygian/Pollux/Erebos kill_ledgers (7-day lookback, "
                     "substantive verdicts only) + Hecate crossgen artifacts; select a plugin (round-robin, "
                     "later kp-routed at ITER-38); generate a ComposedClaim; write composed_claim_*.md; append "
                     "a kill_ledger row (verdict UNVERIFIED, kill_pattern erebos_<plugin>_pending); enqueue a "
                     "stygian_priority row (source=erebos). Stygian maps it to EREBOS-<composed_id>, resolves "
                     "a composition loader or short-circuits *_loader_pending.",
        "producers": ["charon/agents/erebos/daemon.py ErebosAgent.run_tick",
                      "charon/agents/erebos/generators/g01..g25"],
        "inputs": ["charon/agents/stygian/state/kill_ledger.jsonl", "charon/agents/pollux/state/kill_ledger.jsonl",
                   "charon/agents/erebos/state/kill_ledger.jsonl", "charon/agents/hecate/artifacts/ (gradient_archaeology)"],
        "outputs": ["charon/agents/erebos/artifacts/composed_claim_*.md", "erebos kill_ledger rows",
                    "charon/agents/_shared_queues stygian_priority rows", "agora.intelligence_outputs erebos_tick_complete rows",
                    "pivot/erebos_<plugin>_review_<date>.md (review.py health reports)"],
        "intended_consumers": ["Stygian executor (composition loaders -> battery verdict)",
                               "Layer-2 kill_tensor/motif routing (self-consumption for plugin selection)",
                               "a downstream organism that uses PROMOTED composed claims (never specified)"],
    },
    "observed_history": {
        "run_period": "2026-05-26 02:32 .. 2026-05-30 11:59 local (daemon rows); code activity 2026-05-26..2026-06-03 (ITER-84)",
        "measurements": [keeper_line, hist_line, cal_line, refs_line, seam_line, test_line, cons_line],
        "artifact_counts": {
            "agora_erebos_tick_rows": keeper_e["rows"],
            "agora_distinct_cycle_id": keeper_e["distinct_cycle_id"],
            "composed_claim_artifacts_P57_count_QUOTED": 234,
            "agent_dir_commits": hist["git_log_erebos_dir"]["commits_n"],
            "composition_loader_modules": seam["executor_forced_import_modules_n"],
            "plugins_with_loader": seam["find_loader_synthetic_hits_n"],
            "plugins_quarantined": seam["erebos_quarantined_n"],
            "tests_passed_at_baseline": n_pass,
            "tests_failed_at_baseline": n_fail,
            "pivot_erebos_docs": hist["historical_quotes"]["pivot_erebos_docs_n"],
            "external_files_naming_erebos": refs["B_extended_census"]["files_external_n"],
            "runtime_artifacts_on_this_host": 0,
        },
        "actual_consumers": [
            "Stygian executor composition loaders (14/25 plugins; verdicts PROMOTED/REJECTED/UNVERIFIED reported by ITER-5) [seam EXECUTED; verdict path QUOTED]",
            "Erebos Layer-2 routing (next_plugin_kp_routed, ITER-38) [READ]",
            "harmonia/primitives/test_baseline_costume_parity.py (Harmonia B, 2026-06-15) imports _cross_cell_motif + phase3 harnesses [EXECUTED grep]",
            "Aporia autopsy/consumption ledgers (design-doc consumption only) [READ engine/queues/CONSUMPTION.jsonl]",
        ],
        "consumption_evidence": [
            "No independent record of Stygian DEQUEUING an Erebos row survives: the stygian_priority queue file is gitignored and absent; Stygian's own agora summaries are not in the Keeper census. The loader verdicts on record (ITER-3..5) are reported by Charon in pivot docs; whether they flowed through the daemon dequeue path or a manual loader call is unresolved.",
            cons_line,
        ],
    },
    "autopsy": {
        "prior_verdicts": [
            "2026-06-03 Charon Phase 3.K: pair-aware claim STATISTICALLY UNDERDETERMINED (p=0.105), triplet FALSIFIED; 'no Erebos Layer-2 real-data signal claim survives a permutation null'.",
            "2026-06-15 Charon reset: PAUSED, off-spine until it has a consumer.",
            "2026-06-23 disposition row 33: PAUSED -> revive only post-organism; realized~0 (0 perm-null survivors); pre-committed kill at ITER-100.",
            "2026-06-24 component dossier: RETIRE-after-HITL; 'composition-aware loader never shipped'.",
            "2026-08-21 Aporia P57: SELF-CONTAINED-GENERATION; 'seam never built'; 'ZERO external references'.",
            "2026-09 ROSTER/QUEUE: autopsy_failure_class SELF-CONTAINED-GENERATION; calibration_role '4 of 5 - likely TRUE_CORPSE' (treated as zero weight).",
        ],
        "death_certificates": [
            {"source": "engine/ledger/AGENT_AUTOPSIES.jsonl (Erebos row, Aporia P57, 2026-08-21)",
             "claim": "SELF-CONTAINED-GENERATION: the compose->falsify seam was never built; 234 composed claims with ZERO external references; review.py is self-review.",
             "review": "OVERTURNED",
             "errors": [
                 "Seam built: daemon._enqueue_to_stygian, charon/agents/stygian/daemon.py EREBOS-<composed_id> mapping, executor EREBOS-* branch with 29 loaders; find_loader resolves 14/25 plugins today [EXECUTED seam census].",
                 "External references exist: 198 tracked files outside the agent dir name Erebos; 53 under charon/agents/stygian, 19 under harmonia; harmonia/primitives/test_baseline_costume_parity.py imports Erebos code [EXECUTED refs census].",
                 "Grep scope error: case-sensitive 'EREBOS' over engine/, techne/, charon/BACKLOG.md and session docs reproduces (3 self-hits) but excludes charon/agents/stygian and harmonia and misses 'Erebos' in prose (14 files in the same scope case-insensitive).",
                 "review.py is a per-plugin HEALTH runner (HEALTHY/DRIFT/PLATEAUED/BROKEN bands), not a claim verdict [READ header].",
             ]},
            {"source": "pivot/COMPONENT_DOSSIERS_2026-06-24.md (### Erebos)",
             "claim": "RETIRE-after-HITL; realized=none (0 Layer-2 signal claims survive a permutation null); composition-aware loader never shipped (claims short-circuit as *_pending).",
             "review": "PARTIALLY_UPHELD",
             "errors": [
                 "'Loader never shipped' is false: 19 loader commits 2026-05-26..05-30, 29 modules, ITER-5 tally 2 PROMOTED / 4 REJECTED / 1 UNVERIFIED [EXECUTED history census; QUOTED iter5 doc].",
                 "'realized=none' converts STATISTICALLY UNDERDETERMINED into zero; the statistic has no resolution at N=699 [EXECUTED calibration].",
                 "Correctly relayed: Phase 3.K numbers, the PAUSED state, and the absence of a downstream organism.",
             ]},
            {"source": "pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md (row 33)",
             "claim": "PAUSED -> revive only post-organism; realized~0 (0 perm-null survivors); latent high; pre-committed kill at ITER-100.",
             "review": "PARTIALLY_UPHELD",
             "errors": ["'0 perm-null survivors' re-labels an underdetermined test as a null result; the ITER-100 kill it cites was never executed (max ITER-84), so no Erebos kill condition fired."]},
            {"source": "charon/CHARON_SESSION_2026-06-03.md + pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md",
             "claim": "Pair-aware claim STATISTICALLY UNDERDETERMINED (p=0.105, 7-seed mean 0.102); triplet claim FALSIFIED; no Layer-2 real-data signal claim survives a permutation null.",
             "review": "PARTIALLY_UPHELD",
             "errors": ["The numbers stand as quoted and the author's own label (underdetermined) is honest; but 'does not survive' overstates: on 699-row ledgers the substrate-vs-pair-aware delta statistic cannot clear p<0.05 even for a strongly planted linkage (0/3) [EXECUTED calibration]. The triplet FALSIFIED verdict was not re-executed (ledger absent)."]},
            {"source": "charon/CHARON_SESSION_2026-06-15.md (program reset)",
             "claim": "PAUSE Erebos; off-spine until it has a consumer (an organism), the swarm is an immune system with no organism.",
             "review": "UPHELD",
             "errors": []},
            {"source": "engine/ledger/AUTOPSY_TAXONOMY.md (Cluster 5, SELF-CONTAINED-GENERATION)",
             "claim": "Erebos instantiates a class of agents that generate without an outward seam.",
             "review": "OVERTURNED",
             "errors": ["For this instance the outward seam exists and executes (14/25 plugins); the class assignment inherits P57's scope error. Whether other cluster-5 members fit the class is not examined here."]},
            {"source": "engine/necropolis/QUEUE.jsonl (Erebos row, calibration_role '4 of 5 - likely TRUE_CORPSE')",
             "claim": "Realized value ~0 with 0 permanence-null survivors; likely a defended TRUE_CORPSE.",
             "review": "OVERTURNED",
             "errors": ["TRUE_CORPSE needs a FAIR test and a HYPOTHESIS/PREMISE failure; the record has neither: the only Layer-2 value test was underdetermined by its instrument and the pre-committed kill never ran."]},
        ],
        "cause_of_death_stack": stack,
        "fair_test": {
            "verdict": "UNFAIR",
            "scope": "H-B (Layer-2 value over Layer-1) is the claim the death certificates rest on; the only real-data test of it (Phase 3.K, 2026-06-03, 699-row ledger) used a statistic shown to have no resolution in that regime, and the pre-committed ITER-100 discriminating test was never run. H-A (the composer) was exercised for 14/25 plugins over 4.4 days and produced verdicts; no kill condition of its own fired; its findings were self-graded catalog-tier. Scope excludes the 11 quarantined plugins (never exercised: no loader) and the triplet sub-claim (falsified on the record, not re-executed).",
            "finding": "No fair test of the capability the grave is labelled for exists on the record. The composer worked mechanically; the value bet was measured with an instrument that cannot say yes or no at the ledger size available; then the ecosystem stopped.",
            "evidence": [cal_line, hist_line, keeper_line, seam_line],
        },
        "primary_cause": "ECOSYSTEM_FAILURE",
        "contributing_causes": ["MEASUREMENT_ERROR", "INTERPRETATION_ERROR", "INSTRUMENT_ERROR"],
        "premise_exclusion": [],
        "failure_classes": ["ECOSYSTEM_FAILURE", "MEASUREMENT_ERROR", "INTERPRETATION_ERROR", "INSTRUMENT_ERROR"],
        "kill_boundary": "KILLED on this record: (1) the SELF-CONTAINED-GENERATION label for Erebos -- the outward seam existed, executed, and is executable today; (2) 'ZERO external references'; (3) 'loader never shipped'; (4) '0 perm-null survivors' as a measurement of Layer-2 value -- it is an underdetermined statistic at the instrument floor; (5) the queue's 'likely TRUE_CORPSE' -- no fair test and no hypothesis failure on record. NOT KILLED: (a) H-B may still be worthless -- nothing here shows Layer-2 routing adds value; the triplet sub-claim stands falsified as quoted; (b) H-A's realized value was modest by its author's own reclassification (catalog-tier Mahler/Salem findings), and 11/25 plugins never produced a falsifiable claim; (c) the 06-15 judgement that no organism consumed the verdicts stands; (d) that Stygian actually dequeued the daemon's rows (vs manual loader runs) is unproven -- the queue and ledgers are gone.",
        "surviving_claims": [
            "The composer + loader seam runs end to end offline at baseline (813 tests pass; 29 loaders import; 14/25 plugins resolve).",
            "By ITER-5 the loop produced 2 PROMOTED / 4 REJECTED / 1 UNVERIFIED composition verdicts [QUOTED]; the author then reclassified them to catalog/substrate tier -- an honest downgrade, not a failure.",
            "Erebos never fired its own kill: Sprint-1 rule 10/10 PASS (synthetic); ITER-100 unreached (ITER-84).",
            "Erebos stopped with the fleet on 2026-05-30 and was paused by the 2026-06-15 reset for lack of an organism, not for lack of a falsifier.",
        ],
        "uncertainty": [
            "Whether the loader verdicts at ITER-3..5 flowed through Stygian's dequeue of daemon rows or through Charon invoking loaders directly: queue/ledger files are gone; the daemon's enqueued=True is self-report.",
            "234 artifacts (P57, counted in August on a host that still had them) vs 213 ticks (agora): not reconciled.",
            "The calibration planted one signal class (partner-conditioned kill pattern); a lift-only class might separate the two counters. The finding is 'no resolution for this class at N=699', not 'no power for any signal'.",
            "The triplet FALSIFIED verdict (observed 1 vs null ~14) is quoted, not re-executed.",
            "Whether the 06-15 'consumer' reading (organism, not falsifier) is the only reasonable reading of that session note.",
            "Alternative classification a competent reader could reach: CONSUMER_BLOCKED (the 06-15 reason) with the same stack; or NEEDS_MORE_EVIDENCE if executed-by-original-author evidence is ruled inadmissible for MEASUREMENT.",
        ],
        "contradictory_evidence": [
            "Against overturning P57: its grep genuinely reproduces within its stated scope (3 files, all self-hits), and the ROSTER lists source_locations [] -- the certificate was written without the code in view.",
            "Against 'seam worked': no artifact independent of the daemon shows a dequeue; the 06-24 dossier author (with artifacts in hand) still wrote 'claims short-circuit as *_pending', which is true for the 11 loaderless plugins and may have been true for a large share of rows.",
            "Against 'no fair test': Charon's Phase 3.K was a competent, pre-registered-style null test that the author labelled underdetermined rather than claiming a kill; the unfairness is in the statistic's power, not in conduct.",
        ],
        "capability_contingency": {
            "frontier_dependent": False,
            "frontiers": [],
            "era_bound_claim": "Not era-bound: the composer and loaders are deterministic code over catalogues (Mossinghoff/Mahler, BSD strata); no LLM is in the tick path (daemon has no LLM call; generators are rule-based).",
            "what_would_move_it": "Not the model frontier. What would move it: a Layer-2-vs-Layer-1 test with a statistic that has power at the available N (or a ledger >= the size at which the pair-aware delta count clears its floor), plus an organism that consumes PROMOTED composed claims.",
        },
    },
    "residue": {
        "salvageable_code": [
            "charon/agents/stygian/loaders/composition_*.py (29 loaders) + _composition.py registry: a working composed-claim -> battery bridge with 146 passing tests.",
            "charon/agents/erebos/generators/ (25 archetypes; 14 with loaders) + _quarantine.py loader-debt cap.",
            "charon/agents/erebos/_cross_cell_motif.py, _kill_tensor.py, sprint1/phase3/*.py harnesses (already imported by Harmonia B).",
            "scripts/composed_claim_consumer_audit.py (static per-field consumer audit; re-ran cleanly).",
        ],
        "salvageable_data": [
            "pivot/erebos_substrate_finding_iter*.md (7 verdicted findings with numbers); pivot/sprint1/phase3/*.md (7 verdict docs).",
            "engine/necropolis/dossiers/_keeper_evidence/intelligence_outputs_census_result.json (213 tick rows summary).",
        ],
        "salvageable_schemas": ["ComposedClaim (charon/agents/erebos/generators/_base.py, 16 fields, 14 with consumers)", "stygian_priority row shape (daemon._enqueue_to_stygian)", "CompositionLoader Protocol"],
        "salvageable_operators": ["run_binary_split_permutation_null (_mahler_composition_helpers)", "extract_cooccurrence_motifs / conditional_kp_recommendations / per_plugin_majority", "pair_aware_counter_recommendations"],
        "salvageable_tests": ["charon/agents/erebos/tests (608 pass, 1 skip)", "charon/agents/erebos/tests/sprint1 (59 pass)", "charon/agents/stygian/tests/test_composition_* (146 pass)"],
        "representation_hints": [
            "The Layer-2 value question needs a statistic whose null floor is below the effect size at the available N; 'count of disagreements between two counters' is not that statistic.",
            "Runtime ledgers must be archived (or dual-written to a store that is later exported) or every re-audit reduces to prose.",
        ],
    },
    "disposition": {
        "classification": "NO_FAIR_TEST_ON_RECORD",
        "rationale": "The capability the grave is labelled for (Layer-2 routing value over Layer-1, with the composer as its substrate) was never fairly tested: the one real-data test used a statistic shown by executing the committed harness to have no resolution at the ledger size it ran on, and the pre-committed ITER-100 discriminator was never reached because the ecosystem halted (05-30) and was reset (06-15). The composer itself was exercised for 14/25 plugins and produced verdicts; no Erebos kill condition fired. The SELF-CONTAINED-GENERATION certificate is overturned on executed evidence. This is not a resurrection claim: nothing here shows Layer-2 adds value, and the author's own catalog-tier downgrade of the Layer-1 findings stands.",
    },
    "provenance": {
        "investigator": "Rhadamanthus (Necromancer fork)",
        "role": "Necromancer",
        "branch": "rhadamanthus/native-trial-2026-09-11",
        "baseline_sha": "e17934d9a82855b6e0ae1c0bf54c0cce569b7795",
        "evidence_paths": [E_SEAM, E_TEST, E_REFS, E_HIST, E_CAL, E_CONS, E_KEEP, E_HALT,
                           EV + "README.md",  # written after this script
                           "pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md",
                           "pivot/erebos_substrate_finding_iter5_salem_extends_to_band_2026-05-26.md",
                           "pivot/erebos_finding_reclassification_2026-05-27.md",
                           "charon/CHARON_SESSION_2026-06-03.md", "charon/CHARON_SESSION_2026-06-15.md",
                           "engine/ledger/AGENT_AUTOPSIES.jsonl", "pivot/COMPONENT_DOSSIERS_2026-06-24.md",
                           "pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md"],
        "commands_run": [
            "python engine/necropolis/dossiers/erebos_evidence/erebos_seam_census.py",
            "python engine/necropolis/dossiers/erebos_evidence/erebos_tests_offline.py",
            "python engine/necropolis/dossiers/erebos_evidence/erebos_external_refs.py",
            "python engine/necropolis/dossiers/erebos_evidence/erebos_history_census.py <data-backup-root>",
            "python engine/necropolis/dossiers/erebos_evidence/erebos_null_instrument_calibration.py",
            "python scripts/composed_claim_consumer_audit.py --json-path engine/necropolis/dossiers/erebos_evidence/erebos_consumer_audit_rerun_result.json",
            "python engine/necropolis/dossiers/erebos_evidence/_build_dossier.py",
            "git log --format='%h|%ad|%s' --date=short -- charon/agents/erebos",
            "git grep -l EREBOS -- engine techne charon/BACKLOG.md charon/CHARON_SESSION_*.md",
            "git grep -i -l erebos",
            "git show 2905c5659 (read)",
            "python <scratch>/erebos_validate/validate.py (on a scratch copy of engine/necropolis; never in the worktree)",
        ],
        "unresolved_questions": [
            "Did Stygian dequeue and execute the daemon's stygian_priority rows in May 2026, and for what share of the 213 ticks? (Needs Stygian's agora output_summary rows or the lost queue/ledger files.)",
            "Why 234 composed_claim artifacts vs 213 tick rows? (Manual runs? multi-claim ticks? different window?)",
            "Does a lift-only planted signal separate the substrate from the pair-aware counter at N=699, i.e. is the statistic powerless for every signal class or only for partner-conditioned ones?",
            "Where were the May runtime ledgers when P57 counted 234 artifacts on 2026-08-21, and do they still exist on any host?",
            "Is executed-by-the-original-author evidence (Phase 3.K) admissible for a VALID layer verdict under LAW N17, or must the Necromancer re-execute? (Portability defect; see README section 7.)",
        ],
        "created": "2026-09-11",
    },
}

out = HERE.parent / "erebos.dossier.json"
out.write_text(json.dumps(dossier, indent=2) + "\n", encoding="ascii")
print("wrote", out, len(json.dumps(dossier)), "bytes")
