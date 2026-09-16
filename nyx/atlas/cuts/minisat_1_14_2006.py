"""Cut: minisat-1.14-2006 (ancestry-aware, Stage A COARSE; SOURCE_READ Solver.C 239-325 (analyze), 448-527 (propagate), 528-545 (reduceDB),
614-678 (search), 721-781 (solve, grepped for the schedule), Solver.h 43-62/105-110, VarOrder.h in full; newClause 62-142, analyzeFinal,
simplifyDB skimmed). The 987-line CDCL core the record pairs with zchaff for a recurrence test; organ names are chosen so the
zchaff-2007 cut's organs line up where the mechanism is the same and diverge where it is not."""
from nyx.atlas.author import Cut

S = "vault:minisat-1.14-2006/upstream/tree/MiniSat_v1.14/"
c = Cut("minisat-1.14-2006", mode="ANCESTRY_AWARE", inspected=["Solver.C (analyze, propagate, reduceDB, search, solve)", "Solver.h (activity)", "VarOrder.h"],
        evidence=[("SOURCE_READ", S + "Solver.C"), ("SOURCE_READ", S + "VarOrder.h"), ("SOURCE_READ", S + "Solver.h")],
        note="the same nine-part anatomy as zchaff at coarse grain; the differences visible by reading: per-VARIABLE activity in a heap (zchaff: per-literal score with galloping reinsertion), geometric restart growth 1.5x with a learnt-limit growth 1.1x (zchaff: backtrack-count restarts), binary clauses stored inline in the watch list, and a rescale-at-1e100 activity representation")

loop = c.organ("propagate_analyze_backjump_learn_loop", human_name="Solver::search (the CDCL loop)", status="ACCEPTED",
    mechanism="loop: propagate; on conflict at the root level -> UNSAT (analyzeFinal); else analyze -> learnt clause + backtrack level, cancelUntil, add the clause, decay both activities; on no conflict: stop after nof_conflicts (restart), simplify at level 0, reduceDB when learnts exceed the limit, then pick a variable and assume its NEGATIVE literal (line 672: always false first)",
    input="a clause database", output="l_True with a model / l_False / l_Undef (restart)", state="trail, levels, reasons, learnts", update="per conflict / per decision", assumptions=["polarity: the default decision is ~x"],
    evidence_ref=S + "Solver.C:614-678", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="search()",
    coverage={"input_topology": "SET", "output_topology": "DECISION", "state_amount": "SUPERLINEAR", "update_topology": "EVENT_DRIVEN", "stochasticity": "SEEDED_RANDOM"})

tr = c.organ("assignment_trail_with_level_marks_and_reason_pointers", parent=loop, human_name="trail / trail_lim / reason / level", status="ACCEPTED",
    mechanism="assignments are pushed on one vector (trail) with the start index of each decision level in trail_lim; each assigned variable records the clause (or binary literal, GClause) that forced it; cancelUntil(level) pops the trail down to trail_lim[level], un-assigning and re-inserting variables in the order heap",
    input="enqueue / cancelUntil calls", output="the current partial assignment", state="trail, trail_lim, reason[], level[], qhead", update="per assignment", evidence_ref=S + "Solver.C:200-216,423-446", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="assume, cancelUntil, enqueue",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "FULL_HISTORY", "recovery": "ROLLS_BACK"})

wl = c.organ("two_watched_literals_with_inline_binary_clauses", parent=loop, human_name="propagate() / watches", status="ACCEPTED",
    mechanism="each clause is watched by its first two literals; when literal p becomes true the watch list of index(p) is scanned: a binary clause is stored AS the other literal (GClause isLit) and enqueued directly; a longer clause swaps the false literal to c[1], is satisfied if c[0] is true, else looks for a non-false literal from c[2] on to become the new watch (moving the clause to that literal's list), else is unit -> enqueue c[0] or conflict; on conflict the remaining watches are copied and qhead jumps to the end",
    input="the trail from qhead", output="new assignments or a conflicting clause", state="watches[2*nVars], qhead", update="per propagated literal", assumptions=["no clause of size < 2 in the watch lists"],
    fitness_value_in_ancestor="the cost of the solver; the inline binary encoding is 1.14's specific twist (absent in zchaff's cut)", evidence_ref=S + "Solver.C:448-527", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="propagate()",
    coverage={"input_topology": "SEQUENCE", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "update_topology": "EVENT_DRIVEN", "order_sensitivity": "SENSITIVE"})

an = c.organ("first_uip_conflict_analysis_by_trail_walk", parent=loop, human_name="analyze()", status="ACCEPTED",
    mechanism="walk the trail backwards from the conflict: for each literal of the current clause not yet seen and above level 0, bump its variable's activity; literals of the current decision level are counted (pathC), others are added to the learnt clause and raise the backtrack level; follow the reason of the most recent seen literal until pathC hits 0 -- that literal negated is the asserting literal (out_learnt[0]); learnt clauses touched get their activity bumped",
    input="a conflicting clause, trail, reason, level", output="learnt clause, backtrack level", state="analyze_seen[]", update="per conflict", evidence_ref=S + "Solver.C:239-280", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="analyze() first half",
    coverage={"input_topology": "GRAPH", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP"})

mn = c.organ("learnt_clause_minimisation_by_reason_subsumption_cheap_or_recursive", parent=an, human_name="conflict clause minimisation (expensive_ccmin)", status="ACCEPTED",
    mechanism="cheap: drop a learnt literal whose reason clause's other literals are all seen or at level 0; expensive: recursively check (analyze_removable) whether every literal in the implication cone is seen, using a 32-bit level-set abstraction to abort early; the two are selected by a flag",
    input="out_learnt, reasons", output="a shorter learnt clause", state="analyze_toclear, the level abstraction", update="per conflict", evidence_ref=S + "Solver.C:280-325,327-366", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="analyze() second half + analyze_removable",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE"})

va = c.organ("variable_activity_bump_and_geometric_decay_with_rescale", parent=loop, human_name="VSIDS as activity += var_inc; var_inc /= decay", status="ACCEPTED",
    mechanism="bumping adds var_inc to a variable's activity; decaying multiplies var_inc by 1/var_decay (0.95) once per conflict, so older bumps shrink relatively; when any activity passes 1e100 all activities and var_inc are divided by 1e100; a negative var_decay disables bumping (static order); clause activities use the same scheme with 0.999",
    input="bumped variables (from analyze)", output="activity[]", state="activity[], var_inc, cla_inc", update="per conflict", assumptions=["relative order is all that matters; the absolute scale is free (hence the rescale)"],
    fitness_value_in_ancestor="the decision heuristic's whole input", evidence_ref=S + "Solver.h:43-62,105-110; Solver.C:692-712", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="varBumpActivity / varDecayActivity / varRescaleActivity and the cla* twins",
    coverage={"input_topology": "EVENT", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "memory": "SUMMARY_STATISTIC", "adaptation": "PARAMETER"})

vo = c.organ("decide_the_top_activity_unassigned_variable_from_a_heap_with_rare_random_picks", parent=loop, human_name="VarOrder::select", status="ACCEPTED",
    mechanism="a binary heap ordered by activity holds unassigned variables; update() re-sifts a bumped variable, undo() re-inserts an unassigned one; select() with probability random_var_freq (0.02 suggested) tries a uniformly random variable, else pops the heap until an unassigned variable appears",
    input="activity[], assigns[]", output="a variable or var_Undef", state="the heap, random_seed", update="per decision", evidence_ref=S + "VarOrder.h:1-80", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="VarOrder.h + Heap.h",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "competition": "ARBITRATES"})

rd = c.organ("learnt_clause_deletion_halving_by_activity_with_a_floor_for_the_rest", parent=loop, human_name="reduceDB", status="ACCEPTED",
    mechanism="sort learnts by activity; delete the less active half except binary and locked (reason) clauses; from the upper half delete those below cla_inc / learnts.size(); triggered when learnts - assigned variables exceeds nof_learnts, which grows 1.1x per restart",
    input="learnts, activities", output="a smaller learnts vector", state="none", update="on trigger", evidence_ref=S + "Solver.C:528-545,735-750", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="reduceDB()",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "memory": "FULL_HISTORY", "resource_dependence": "MEMORY"})

rs = c.organ("restart_after_a_conflict_budget_growing_geometrically", parent=loop, human_name="solve() schedule", status="ACCEPTED",
    mechanism="search() returns l_Undef after nof_conflicts conflicts (initially 100); solve() multiplies the budget by 1.5 and the learnt limit by 1.1 and calls again, keeping learnt clauses and activities (only the trail is undone to root_level)",
    input="search outcomes", output="the final answer", state="nof_conflicts, nof_learnts", update="per restart", evidence_ref=S + "Solver.C:721-781 (lines 6-7, 48-50 of the function)", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="solve()",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "temporal_horizon": "EPISODE", "adaptation": "PARAMETER"})

c.reject("'CDCL' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="nine mechanisms with separate state; the same finding as on zchaff-2007")
c.reject("Main.C (DIMACS parser, reporting, signal handling)", reason="EFFECT_FROM_ENVIRONMENT", evidence=S + "Main.C by name; the CNF interface")
c.reject("vec / Heap / Sort templates", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + "Global.h, Heap.h, Sort.h -- containers (the heap's ORDER is VarOrder's, recorded there)")
c.reject("progressEstimate()", reason="OTHER", evidence=S + "Solver.C:679-690 -- reporting only ('Not extremely reliable' per its own comment)", note="an instrument")
c.reject("simplifyDB (top-level satisfied-clause removal)", reason="BELOW_MEANINGFUL_GRAIN", evidence=S + "Solver.C:558-612 -- removes satisfied clauses at level 0; skimmed, no state of its own beyond a propagation counter")

c.edge(wl, an, "triggers", note="conflict clause"); c.edge(an, va, "updates", note="bumps"); c.edge(an, mn, "feeds"); c.edge(mn, tr, "restores", note="backjump to out_btlevel"); c.edge(va, vo, "feeds"); c.edge(vo, tr, "feeds", note="decision pushed on the trail")
c.edge(tr, wl, "feeds", note="qhead"); c.edge(rs, loop, "schedules"); c.edge(rs, rd, "updates", note="nof_learnts"); c.edge(rd, wl, "forgets", note="removed clauses leave the watch lists"); c.edge(mn, rd, "stores", note="learnt clause added with activity")

c.pressure("an_exponential_search_space_where_most_branches_die_for_reasons_shared_with_other_branches",
    condition="a decision tree of 2^n leaves; a failed branch's cause usually involves few variables and recurs elsewhere in the tree", resource_or_constraint="time; memory for remembered causes",
    failure_condition="re-exploring the same dead sub-space; or drowning in remembered clauses", world_punishes="forgetting why a branch failed; keeping everything", world_rewards="extracting a small reason, jumping back past irrelevant decisions, and forgetting reasons that stop being used",
    observable_consequence="conflicts / decisions / propagations per instance (the record's cross-solver comparison)", vacuity_condition="instances solved by pure propagation", trivial_shortcuts="a lookup table of solved instances (the world must present unseen instances)",
    cheat_control="a solver given the satisfying assignment must finish with zero conflicts; one given the refutation clauses must finish near-instantly; if the world cannot tell, it is not measuring search", cost_class="CPU-scale", source_evidence="record pressure; search()", purpose="PURPOSE: decide propositional satisfiability")
c.pressure("the_useful_ordering_of_choices_is_only_knowable_from_recent_failures",
    condition="no static measure of a variable predicts where conflicts will come from; the search's own recent conflicts are the only signal, and it drifts", resource_or_constraint="one heuristic evaluation per decision",
    failure_condition="a stale order that keeps choosing variables irrelevant to the current conflicts", world_punishes="static orders; orders that never forget", world_rewards="an order driven by recent conflict participation with geometric forgetting",
    observable_consequence="decisions to solution with var_decay = 0.95 vs a static order (var_decay < 0 in this body)", vacuity_condition="instances where any order works", trivial_shortcuts="random order with restarts",
    cheat_control="a heuristic told the variables of the final refutation must beat VSIDS; if it does not, the world's instances do not reward focus", cost_class="CPU-scale", source_evidence="Solver.h var_decay comment; VarOrder.h", purpose="PURPOSE: same")

c.ancestry("successor_of", "zchaff-2007", note="Techne records the superseded edge on both records; the algorithms (two watched literals, 1UIP, activity) are Chaff's, the representation (activity heap, inline binaries, decay-by-inc) is MiniSat's")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["newClause (clause construction, duplicate/tautology removal, learnt clause watch placement) skimmed only", "analyzeFinal (the assumption-conflict path) skimmed", "nothing ran here; Techne's harness (agreement with 2.2.0, picosat, zchaff) is on M1"],
          note="search / propagate / analyze / reduceDB / VarOrder are read line by line; the nine organs account for them")
c.save(state="COARSE")
