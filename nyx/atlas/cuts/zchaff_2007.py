"""Cut: zchaff-2007 (ancestry-aware; SOURCE_READ zchaff_solver.cpp: real_solve/solve/back_track/deduce/set_var_value(_BCP)/
decide_next_branch/adjust_variable_order/decay_variable_score/delete_unrelevant_clauses/run_periodic_functions/restart/
finish_add_conf_clause; method index of the file). NOT read: conflict_analysis_firstUIP body, zchaff_dbase.cpp (clause storage),
zverify_df.cpp (proof checker), preprocess(). 'CDCL' is the human package name; below it the body has at least ten mechanisms."""
from nyx.atlas.author import Cut

S = "F:/Prometheus/vault/fossils/zchaff-2007/upstream/tree/zchaff64/zchaff_solver.cpp"
c = Cut("zchaff-2007", mode="ANCESTRY_AWARE",
        inspected=["zchaff_solver.cpp[54-330,406-712,863-960,1058-1200,1396-1418]", "method index"],
        evidence=[("SOURCE_READ", S)],
        note="a LOSING_RIVAL by Techne's disposition audit (superseded by minisat); the distinctive 2007 machinery (shrinking) is exactly what its successors dropped")

loop = c.organ("decide_deduce_analyze_loop", human_name="the CDCL main loop", status="ACCEPTED",
    human_interpretation="pick a variable, propagate, learn from conflicts, until SAT/UNSAT/timeout",
    mechanism="while undetermined: run the periodic housekeeping; if a decision can be made, propagate until no conflict (each conflict analysed and a backjump level returned; a conflict at level 0 is UNSAT); if no free variable remains, SAT; termination also on time, memory or external abort",
    input="a CNF (clause database), parameters", output="SAT/UNSAT/TIME_OUT/MEM_OUT/ABORTED", state="outcome flag; everything below", update="one decision per iteration",
    fitness_value_in_ancestor="the scaffold every other organ hangs on", evidence_ref=S + ":863-909", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="CSolver::real_solve + solve", coverage={"input_topology": "SET", "output_topology": "DECISION", "update_topology": "EVENT_DRIVEN", "stochasticity": "SEEDED_RANDOM", "temporal_horizon": "EPISODE"})

trail = c.organ("assignment_stack_per_level", parent=loop, human_name="trail / decision levels", status="ACCEPTED",
    mechanism="one vector of assigned variables per decision level; each variable records its level, its antecedent clause and its position; backtracking to level k unassigns every level >= k in reverse push order and drops the vectors",
    input="assignments with a level", output="ordered undo", state="vector<vector<int>> indexed by level; per-variable (value, dlevel, antecedent, pos)", update="push on assign; reverse pop on back_track",
    fitness_value_in_ancestor="makes non-chronological backjumping a single call", evidence_ref=S + ":246-260,910-923", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="_assignment_stack + back_track + set_var_value head", coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "memory": "FULL_HISTORY", "recovery": "ROLLS_BACK"})

bcp = c.organ("two_watched_literals_bidirectional_scan", parent=loop, human_name="two-watched-literal BCP", status="ACCEPTED",
    human_interpretation="unit propagation that only visits clauses whose watched literal became false",
    mechanism="each clause watches two literals; when a variable is assigned, only the clauses watching the now-false literal are visited; from the watched position the scan walks the clause in one direction to its terminator then the other, looking for a non-false literal to move the watch to; if none exists the OTHER watched literal is either false (conflict) or unknown (implied, queued with the clause as antecedent). Clauses live in a flat literal pool with terminator elements carrying the clause id, so the scan needs no clause header",
    input="a newly false literal", output="implications queued / conflicts recorded / watches moved", state="per-literal watch lists; per-literal-pool-element watch bit + direction", update="watch relocation by swap-with-last in the watch list",
    assumptions=["a clause has >= 2 literals", "the pool layout: literals then a terminator with val <= 0"], fitness_value_in_ancestor="the cost of propagation does not depend on clause length until a watch must move; backtracking needs no watch updates",
    failure_landscape="long clauses with many false literals still scanned when a watch moves", evidence_ref=S + ":261-311", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="CSolver::set_var_value_BCP", coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "update_topology": "EVENT_DRIVEN", "order_sensitivity": "SENSITIVE"})

ded = c.organ("implication_queue_with_antecedent_shortening", parent=loop, human_name="deduce()", status="ACCEPTED",
    mechanism="a FIFO of (literal, reason clause); pop: unknown variable -> assign with that reason (which enqueues more); already assigned opposite -> record the conflict and stop; already assigned same -> if the new reason is a shorter clause, replace the recorded reason. On conflict the remaining queue is discarded",
    input="implications from the watch scan", output="assignments or a conflict list", state="queue; _conflicts", update="FIFO",
    fitness_value_in_ancestor="breadth-first propagation; the antecedent-shortening keeps learned clauses smaller (a small, undocumented trick)", evidence_ref=S + ":924-957", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="CSolver::deduce", coverage={"input_topology": "STREAM", "output_topology": "EVENT", "update_topology": "EVENT_DRIVEN", "memory": "WINDOW"})

uip = c.organ("first_uip_conflict_analysis", parent=loop, human_name="1-UIP learning", status="CANDIDATE",
    mechanism="UNKNOWN in detail (body of conflict_analysis_firstUIP not read); the caller shows: a conflict at level 0 is UNSAT with an optional resolution trace; otherwise the routine returns a backjump level and fills _conflict_lits, which finish_add_conf_clause turns into a learned clause",
    input="the conflicting clause(s) + the trail", output="a learned clause + backjump level", state="_conflict_lits, marks", update="UNKNOWN (not read)",
    fitness_value_in_ancestor="the 'L' in CDCL", evidence_ref=S + ":1058-1110 (caller only)", confidence="LOW on mechanism; HIGH on existence and interface", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="CSolver::conflict_analysis_firstUIP (unread) + analyze_conflicts")

score = c.organ("literal_score_bump_with_galloping_reinsertion", parent=loop, human_name="VSIDS-style activity (zchaff form)", status="ACCEPTED",
    human_interpretation="variables in recent conflicts become more attractive to branch on",
    mechanism="every literal of a new learned clause gets its per-phase score incremented; the variable is then moved UP a sorted array by a galloping search: jump backwards in strides of bubble_init_step until a higher score is met, then halve the stride repeatedly to pin the insertion point, then swap; every decay_period backtracks ALL scores are halved and the array re-synchronised",
    input="the literals of a learned clause; a backtrack counter", output="a sorted array of (variable, score) with per-variable position", state="score(0), score(1) per variable; _ordered_vars; _max_score_pos", update="increment + galloping reinsertion; periodic halving",
    assumptions=["scores only rise between decays, so reinsertion only moves upward"], fitness_value_in_ancestor="branching follows the conflict frontier (the VSIDS idea) without a heap",
    failure_landscape="a full re-sort after each decay; the array becomes stale between syncs (the decay does not re-sort, only rewrites scores -- read at 569-580)",
    evidence_ref=S + ":532-580,1396-1405", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="adjust_variable_order + decay_variable_score + update_var_score", coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "SUMMARY_STATISTIC", "adaptation": "PARAMETER", "update_topology": "EVENT_DRIVEN"})

dec = c.organ("decide_from_newest_unsatisfied_learned_clause_else_top_score", parent=loop, human_name="decision heuristic (BerkMin-like first stage + VSIDS fallback)", status="ACCEPTED",
    mechanism="first: walk learned clauses from the newest downward to the first one not currently satisfied (caching a satisfying literal index per clause to skip fast); among its unknown variables pick the highest score. Only if every learned clause is satisfied: take the highest-score branchable unknown variable from the sorted array, skipping a random number of candidates bounded by a randomness parameter. Sign: the phase with the higher score, tie -> the phase with more binary-clause occurrences, tie -> coin flip",
    input="clause database, scores, randomness", output="a decision literal queued as an implication with no antecedent", state="top_unsat_cls pointer; per-clause sat_lit_idx cache; current_randomness", update="pointer decreases as learned clauses are satisfied; randomness decays to a base",
    fitness_value_in_ancestor="focuses on the most recent conflict region before global scores", failure_landscape="the newest-unsatisfied scan is linear in the number of learned clauses in the worst case",
    evidence_ref=S + ":581-711", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="CSolver::decide_next_branch", coverage={"input_topology": "SET", "output_topology": "DECISION", "stochasticity": "SEEDED_RANDOM", "memory": "LAST_VALUE", "update_topology": "PRIORITY"})

shrink = c.organ("learned_clause_shrinking_by_level_gap", parent=loop, human_name="clause shrinking (zchaff 2004+)", status="ACCEPTED",
    human_interpretation="when a learned clause is too long, backtrack further and re-decide its literals so a shorter clause is learned",
    mechanism="if a new learned clause exceeds a size threshold: sort its literals by decision level; walk upward while consecutive levels are within 2 of each other, deleting those; at the first gap > 2, backtrack to just above the last kept level, discard the learned clause, and queue the remaining literals (negated) as forced decisions one per level. A windowed statistic of (old length - new length) over recent shrinkings raises or lowers the size threshold every N shrinkings",
    input="a fresh learned clause", output="a backtrack + a queue of forced decisions, or nothing", state="_shrinking_cls multimap; window of recent benefits; adaptive size threshold", update="adaptive threshold: += upper_delta if benefit > upper_bound, += lower_delta if < lower_bound",
    assumptions=["re-deciding the same literals reproduces the conflict with a shorter reason"], fitness_value_in_ancestor="UNKNOWN in effect -- not measured here; historically zchaff's distinguishing 2004-2007 feature; successors (minisat, picosat, in the vault) do not have it",
    failure_landscape="restarts are suppressed while shrinking is in progress (run_periodic_functions checks _shrinking_cls.empty()); the forced decisions bypass the score heuristic",
    evidence_ref=S + ":581-604,1128-1185,187-190", confidence="HIGH on mechanism; UNKNOWN on value", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="finish_add_conf_clause shrinking block + decide_next_branch shrinking block", coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "adaptation": "PARAMETER", "memory": "WINDOW", "recovery": "ROLLS_BACK", "feedback": "CLOSED_LOOP"})

dele = c.organ("learned_clause_deletion_by_activity_and_size_with_age_split", parent=loop, human_name="clause database reduction", status="ACCEPTED",
    mechanism="at each restart, walk learned clauses oldest to newest: a clause satisfied at level 0 with more than one non-false literal is deleted outright; otherwise an activity threshold interpolated from head to tail (older clauses need MORE activity to survive) and a size threshold (older 'head' clauses allowed fewer unknown literals than 'tail' clauses) decide deletion by counting unknown literals",
    input="the learned clause list, activities", output="marked-deleted clauses", state="per-clause activity; head/tail parameters", update="sweep at restart",
    fitness_value_in_ancestor="bounds memory; keeps recent and active clauses", evidence_ref=S + ":406-470", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="delete_unrelevant_clauses", coverage={"input_topology": "SET", "output_topology": "SET", "resource_dependence": "MEMORY", "memory": "SUMMARY_STATISTIC", "update_topology": "SWEEP"})

rst = c.organ("restart_on_backtrack_count_with_pool_compaction", parent=loop, human_name="restarts", status="ACCEPTED",
    mechanism="when the backtrack count passes a moving target (target += a fixed increment each time), and no shrinking is pending: delete clauses, backtrack to level 1 (level-0 facts kept), and every fifth restart compact the literal pool",
    input="backtrack counter", output="a reset of the trail above level 0", state="next_restart, restart_incr, num_restarts", update="linear schedule",
    fitness_value_in_ancestor="escapes bad early decisions while keeping learned clauses", evidence_ref=S + ":187-200,1407-1416", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="run_periodic_functions (a) + restart", coverage={"input_topology": "SCALAR", "output_topology": "EVENT", "update_topology": "EVENT_DRIVEN", "recovery": "SELF_RESETS", "temporal_horizon": "WINDOW"})

c.organ("resolution_proof_checker", human_name="zverify_df", status="CANDIDATE", evidence_grade="METADATA",
    mechanism="UNKNOWN (24 KB file present, not read); the record says it checks UNSAT proofs; VERIFY_ON blocks in the solver emit per-conflict resolvent traces that would be its input",
    input="a trace of learned clauses and their resolvents (from the VERIFY_ON stream)", output="accept/reject of an UNSAT claim", evidence_ref="zverify_df.cpp exists; solver lines 1065-1099 emit the trace",
    confidence="LOW", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="zverify_df.cpp (unread)")

c.reject("hook functions / periodic callbacks", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":182-215 add_hook / hooks loop: a callback registry with intervals; scaffolding for embedding, no solving behaviour")
c.reject("statistics and timing (_stats, cpu time, time_out, mem_usage)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":54-146,528-531,1342-1350")
c.reject("'CDCL' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the name covers at least eight mechanisms with separate state and update rules (above); no single function or state corresponds to it", note="the famous name decomposes; this is the directive's example and the body confirms it")
c.reject("preprocess()", reason="OTHER", evidence="called once before the search (line 899); body not read; NOT a rejection of a mechanism but of a cut Nyx cannot yet make -- recorded so the gap is visible")

c.edge(bcp, ded, "feeds"); c.edge(ded, trail, "updates"); c.edge(ded, uip, "triggers"); c.edge(uip, trail, "restores", note="backjump")
c.edge(uip, score, "updates", note="the learned clause's literals get bumped"); c.edge(uip, shrink, "gates", note="a long learned clause may be shrunk instead of kept")
c.edge(shrink, trail, "restores"); c.edge(shrink, dec, "feeds", note="forced decisions bypass the heuristic"); c.edge(shrink, rst, "suppresses", note="no restart while shrinking")
c.edge(score, dec, "feeds"); c.edge(dec, ded, "feeds", note="a decision is an implication with no antecedent")
c.edge(rst, dele, "triggers"); c.edge(rst, trail, "restores"); c.edge(dele, dec, "updates", note="top_unsat_cls pointer resets over the surviving clauses")
c.edge(loop, rst, "schedules"); c.edge(loop, score, "schedules", note="decay every decay_period backtracks")

c.pressure("combinatorial_search_with_unbounded_learned_memory",
    condition="the space of assignments is exponential; every conflict yields a clause worth remembering; memory is finite", resource_or_constraint="memory for learned clauses; time",
    failure_condition="MEM_OUT or TIME_OUT before an answer", world_punishes="keeping everything (memory) and forgetting everything (repeat the same conflicts)", world_rewards="keeping the recent and active clauses",
    observable_consequence="delete_unrelevant_clauses at each restart; MEM_OUT outcome exists", vacuity_condition="instances small enough to finish before the first restart", trivial_shortcuts="never learn (DPLL)",
    cheat_control="Techne's ORACLE: agreement with minisat-2.2.0 and picosat-965 on the same CNFs", cost_class="exponential worst case", source_evidence="record.human_environmental_pressure + source", purpose="PURPOSE: decide satisfiability of industrial CNFs")
c.pressure("expensive_wrong_unsat",
    condition="an UNSAT answer cannot be checked by exhibiting a model; a wrong UNSAT silently certifies an impossible design as impossible", resource_or_constraint="trust in the answer",
    failure_condition="a bug in learning produces a clause that does not follow", world_punishes="undetected wrong UNSAT", world_rewards="a checkable trace of resolvents",
    observable_consequence="VERIFY_ON resolvent stream + zverify_df", vacuity_condition="SAT answers (the model is its own certificate)", trivial_shortcuts="none", cheat_control="UNKNOWN", cost_class="trace I/O per conflict",
    source_evidence="record.human_failure_condition 'a wrong UNSAT (hence zverify_df)'", purpose="PURPOSE: verification customers who act on UNSAT")
c.pressure("competition_by_race_time",
    condition="solvers are ranked by problems solved within a time limit in public competitions", resource_or_constraint="wall-clock per instance",
    failure_condition="being out-solved", world_punishes="slow propagation, poor branching", world_rewards="whatever wins races that year (shrinking did in 2004; minisat's simplicity won after)",
    observable_consequence="Techne's disposition: LOSING_RIVAL", vacuity_condition="no competition", trivial_shortcuts="tuning to the benchmark set", cheat_control="UNKNOWN", cost_class="engineering effort",
    source_evidence="record.acquisition_tags loser/superseded; historical_disposition", purpose="PURPOSE: same as above; the pressure is social, not computational")

c.residue("PARTIALLY_EXPLAINED", ["conflict_analysis_firstUIP body (the learning rule itself) not read", "clause database layout (zchaff_dbase.cpp) not read -- the literal pool with terminators is inferred from the scan code",
                                  "preprocess() not read", "zverify_df not read", "clause group ids / incremental add (add_clause_incr, delete_clause_group) not cut: incremental-SAT API surface"],
          note="the search loop is accounted for by organs 1-10; learning and storage are named but not opened")
c.save(state="DEEP")
