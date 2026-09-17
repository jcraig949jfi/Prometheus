"""Cut: ff-planner-2.3 (Hoffmann's FF; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; eighth of the 2026-09-17 NOT_CUT order).
Read: search.c 1-120 (header), 174-437 (enforced hill-climbing, breadth-first search for a better state, node expansion), 765-815
(goal-added deletion check); relax.c 359-445 (relaxed planning-graph fixpoint), 770-960 (backward extraction of the relaxed plan,
helpful-action collection and ordering). Skimmed: relax.c function list; search.c best-first section headers. NOT read: the
instantiation pipeline (inst_pre/easy/hard/final, ~6,500 lines), parse.c, output.c, memory.c, main.c, extract_1P's body
(662-770), the best-first search body (815-1060), the hashing routines. Nothing ran.
"""
from nyx.atlas.author import Cut

S = "vault:ff-planner-2.3/upstream/tree/FF-v2.3/search.c"
R = "vault:ff-planner-2.3/upstream/tree/FF-v2.3/relax.c"
c = Cut("ff-planner-2.3", mode="ANCESTRY_AWARE", inspected=["search.c 1-120, 174-437, 765-815", "relax.c 359-445, 770-960 (+ function list)"],
        evidence=[("SOURCE_READ", S + ":174-437"), ("SOURCE_READ", S + ":765-815"), ("SOURCE_READ", R + ":359-445"), ("SOURCE_READ", R + ":770-960")],
        note="the famous name (FF, 'the planner that won 2000') covers: a relaxation that ignores delete effects, a layered reachability fixpoint, a backward plan extraction whose LENGTH is the heuristic, "
             "a pruning rule that keeps only the actions the relaxed plan used first, a local search that commits to the first strictly better state found by breadth-first search, "
             "a second pruning rule that discards successors whose newly achieved goal the relaxed plan would delete, and a complete fallback")

fix = c.organ("layered_reachability_fixpoint_over_facts_and_effects_ignoring_deletes", human_name="build_fixpoint / activate_ft / activate_ef (relax.c 359-530)", status="ACCEPTED",
    mechanism="from the current state, facts are activated at level 0; an effect becomes active at the first level where all its preconditions are active (a per-effect counter of active preconditions), and its add effects (deletes ignored) become new facts at the next level; the loop stops when every current goal is active or no new fact appears (then the goal is unreachable: h = INFINITY)",
    input="a state S and the current goal set", output="a level for every fact and effect reached; the depth at which the goals are all reached", state="lF/lE lists, per-fact and per-effect level fields (reset per call)", update="per heuristic evaluation",
    assumptions=["delete effects can be ignored to bound the distance from below (the relaxation)", "the connectivity graph gft_conn/gef_conn/gop_conn is precomputed by instantiation"],
    fitness_value_in_ancestor="a polynomial reachability analysis that terminates in a handful of layers on benchmark domains; the level structure is what makes extraction cheap",
    failure_landscape="by reading: domains where deletes matter (resource consumption, one-way doors) get a heuristic that is badly optimistic; the record's note that it is 'symbolic-ai / strips' is the scope",
    human_prior="Graphplan's layered graph (Blum & Furst 1995) without mutexes; the vault's graphplan-blum-furst-1995 is the ancestor for a recurrence test", evidence_ref=R + ":359-530", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="build_fixpoint and the four activation helpers",
    coverage={"input_topology": "SET", "output_topology": "GRAPH", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "PARALLEL_ROUNDS", "temporal_horizon": "UNBOUNDED"})

ext = c.organ("backward_extraction_of_a_relaxed_plan_choosing_the_achiever_with_the_cheapest_preconditions", human_name="achieve_goals (relax.c 770-875); extract_1P", status="ACCEPTED",
    mechanism="goals are placed at the level where they first became true; from the top level down, each goal not already made true at that level is assigned the achiever effect active one level below whose precondition levels sum to the least; the achiever's preconditions become goals at their own levels (unless already true or already goals), its add effects (and those of its implied effects) are marked true at this level so later goals at the same level can be covered for free; the count of distinct operators used (lh) is the heuristic value",
    input="the fixpoint levels and the goal set", output="a relaxed plan (a set of effects per level) and h = number of actions in it", state="lgoals_at[level], is_true/is_goal marks, gin_plan_E", update="per heuristic evaluation",
    assumptions=["the relaxed plan's length approximates the real distance better than the fixpoint depth alone; ties among achievers are broken by precondition cost, a greedy choice"],
    fitness_value_in_ancestor="the heuristic is the LENGTH of a concrete relaxed plan, not an abstract level count, so it is sensitive to how many actions are needed at each level; the plan itself feeds the next organ",
    failure_landscape="by reading: greedy achiever choice is not optimal for the relaxed problem (which is NP-hard to solve optimally); the comment in the code notes the ordering constraints 'don't explore the full potential'",
    human_prior="Hoffmann's choice of the min-precondition-level-sum achiever and the 'true at this level' bookkeeping", evidence_ref=R + ":770-875", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="achieve_goals and its callers in extract_1P",
    coverage={"input_topology": "GRAPH", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

hlp = c.organ("helpful_actions_as_the_first_level_achievers_of_first_level_subgoals_ordered_by_fewest_goal_deletes", human_name="collect_H_info (relax.c 876-955); gH used in search.c", status="ACCEPTED",
    mechanism="after extraction, the actions considered by the search are ONLY those whose effects are at level 0 and add a goal placed at level 1 (i.e. what the relaxed plan would do first); they are ordered so that actions deleting fewer goal/subgoal facts come first, and later-collected (deeper) goals' achievers are preferred on ties by inserting from the back",
    input="the relaxed plan's level-1 goals", output="the ordered list gH of applicable operators to expand", state="gH, gnum_H, is_in_H flags", update="per heuristic evaluation",
    assumptions=["what the relaxed plan does first is a good proxy for what the real plan should do first (incomplete: a needed action may be pruned)"],
    fitness_value_in_ancestor="branching factor collapses from all applicable actions to the handful the heuristic 'wants'; the incompleteness is caught by the fallback organ",
    failure_landscape="by reading: pruning is incomplete by design; when EHC fails FF restarts with best-first search over ALL actions", human_prior="the helpful-action pruning (Hoffmann & Nebel 2001) -- a search-space cut derived from the heuristic's own computation",
    evidence_ref=R + ":876-955; " + S + ":298-301, 396-399", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="collect_H_info and the gH loops",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "order_sensitivity": "SENSITIVE"})

ehc = c.organ("enforced_hill_climbing_committing_to_the_first_strictly_better_state_found_by_breadth_first_search", human_name="do_enforced_hill_climbing / search_for_better_state / expand_first_node (search.c 174-437)", status="ACCEPTED",
    mechanism="from S with h(S), run breadth-first search over helpful-action successors (a FIFO of EhcNodes, states hashed to skip repeats) evaluating h at each node; the FIRST node with h < h(S) ends the search: its path is appended to the plan, it becomes S, and the outer loop repeats until h = 0; if the FIFO empties (a plateau or dead end with no escape) EHC fails and returns FALSE; the search depth is reported as it grows",
    input="start and goal states", output="a plan (sequence of operators) or FALSE", state="the EHC space list, the hash table, the plan hash", update="per plateau escape",
    assumptions=["h decreases somewhere within a small breadth-first radius on most benchmark instances (the 'plateau' assumption); no backtracking over committed steps"],
    fitness_value_in_ancestor="linear-in-plan-length memory in the common case; the commitment is what makes FF fast and what makes it incomplete",
    failure_landscape="by reading: unbounded breadth-first search on a large plateau; dead ends are only detected when the FIFO empties; states already visited in an earlier plateau escape are re-visited (the hash is reset per call)",
    human_prior="the 'enforced' variant (exhaustive BFS for a better state instead of sampling neighbours)", evidence_ref=S + ":174-437", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the three functions and add_to_ehc_space",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "UNBOUNDED", "state_persistence": "PER_EPISODE", "feedback": "CLOSED_LOOP", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "PRIORITY", "failure_mode": "STALLS", "recovery": "EXTERNAL_RESET"})

gad = c.organ("goal_added_deletion_pruning_of_successors_whose_new_goal_the_relaxed_plan_would_delete", human_name="new_goal_gets_deleted (search.c 765-780); expand_first_node 387-391", status="ACCEPTED",
    mechanism="when a successor is generated, result_to_dest records which goal fact (if any) the action newly achieved; when that node is expanded, if any effect in the CURRENT relaxed plan deletes that goal, the node is pruned (h = INFINITY) because the plan would undo what was just gained",
    input="a node's new_goal and the relaxed plan's effects", output="prune / keep", state="new_goal per node", update="per expansion",
    assumptions=["achieving a goal that the heuristic's own plan will delete is wasted; the check is against the relaxed plan, so it is itself approximate"], fitness_value_in_ancestor="cuts oscillation between achieving and destroying goals in domains with interacting goals",
    failure_landscape="UNKNOWN by run", human_prior="the 'informed goal added deletion heuristic' named in the file header", evidence_ref=S + ":765-780, 387-391, 1067-1170 (result_to_dest, not read in full)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="new_goal_gets_deleted and its call site",
    coverage={"input_topology": "SET", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC"})

bfs = c.organ("complete_best_first_fallback_over_all_actions_when_the_local_search_fails", human_name="do_best_first_search (search.c 815-1060, headers read; body not read)", status="CANDIDATE",
    mechanism="when EHC returns FALSE the planner restarts from the initial state with a greedy best-first search over all applicable actions using the same heuristic (per the file header and main.c control flow, not traced line by line)",
    input="the failed EHC", output="a plan or unsolvable", state="the BFS open list and hash", update="once per problem",
    assumptions=["the fallback restores completeness (for the relaxed-plan heuristic it is complete but may be slow)"], fitness_value_in_ancestor="EHC's incompleteness costs at most a restart", failure_landscape="UNKNOWN",
    evidence_ref=S + ":815-1060 (function headers only)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="do_best_first_search; CANDIDATE because the body was not read",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "UNBOUNDED", "stochasticity": "DETERMINISTIC", "update_topology": "PRIORITY", "recovery": "RETRIES"})

c.reject("the instantiation pipeline (inst_pre/easy/hard/final: grounding PDDL/ADL into the connectivity graph), parse.c, output.c, memory.c, main.c", reason="OTHER", evidence="NOT READ (about 10,000 of 15,846 lines); residue", note="grounding is where the ADL-to-STRIPS compilation lives; a mechanism-bearing region for a second pass")
c.reject("state hashing and repeated-state detection (hash_ehc_node, ehc_state_hashed, state_sum)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":438-613 (not read in full); a sum-based hash with a bucket list", note="an instrument for the search, not a planning mechanism")
c.reject("'FF' / 'heuristic search planning' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the relaxation, the extraction, the helpful-action cut, the local search, the goal-deletion cut and the fallback are each separately replaceable (later planners replaced each one independently)")
c.reject("printf progress output ('Cueing down from goal distance', '[depth]')", reason="OTHER", evidence="instrument", note="the printed h sequence is the natural observable for a Stage C run")

c.edge(fix, ext, "feeds"); c.edge(ext, hlp, "feeds"); c.edge(hlp, ehc, "selects", note="which successors are generated"); c.edge(ext, ehc, "feeds", note="h value"); c.edge(ext, gad, "feeds", note="the plan's delete effects"); c.edge(gad, ehc, "gates")
c.edge(ehc, fix, "triggers", note="h evaluated at every expanded node"); c.edge(ehc, bfs, "triggers", note="on failure"); c.edge(fix, bfs, "feeds")

c.pressure("goal_distance_must_be_estimated_cheaply_from_a_relaxation_that_ignores_the_consequences_that_make_the_problem_hard",
    condition="an organism must choose actions toward a goal in a state space too large to search; it may compute anything polynomial about a SIMPLIFIED version of the world (one where nothing is ever undone) and use it as a distance estimate",
    resource_or_constraint="evaluations per step; the estimate's cost must be polynomial in the description size", failure_condition="an estimate so optimistic that the search wanders (plateaus) or so expensive that no step is taken",
    world_punishes="wandering on plateaus; time per node", world_rewards="an estimate that orders neighbours correctly often enough that greedy commitment reaches the goal", observable_consequence="nodes expanded per solved instance and solved fraction across domains where deletes matter vs not",
    vacuity_condition="a world with no delete effects (the relaxation is exact) or one small enough to search exactly", trivial_shortcuts="a world-provided distance; exact search on tiny instances",
    cheat_control="an organism given the true distance must solve with zero wandering; the ancestor must fail (EHC returns FALSE) on a domain built so that every relaxed plan deletes its own subgoals: if the world cannot exhibit the plateau it is not exerting this pressure",
    cost_class="CPU-scale", source_evidence="relax.c 359-445, 770-875; search.c 174-270; record domain planning/heuristic-search/strips", purpose="PURPOSE: domain-independent classical planning (Hoffmann & Nebel 2001)")

c.pressure("the_estimator_itself_must_tell_the_search_which_neighbours_are_worth_generating",
    condition="branching is too wide to evaluate every neighbour; the organism's own estimate computation produces a by-product (which actions it would take first) that can cut the branching, at the risk of cutting the needed action",
    resource_or_constraint="evaluations per step vs completeness", failure_condition="pruning the only action that leads out (incompleteness) or pruning nothing (cost)", world_punishes="both", world_rewards="a cut that keeps the needed action almost always, with a detectable failure that triggers a complete fallback",
    observable_consequence="fallback rate and evaluations per instance with the cut on vs off", vacuity_condition="small branching factor", trivial_shortcuts="a world that labels the useful actions",
    cheat_control="an organism given the optimal plan's first action must expand exactly one successor per step; the ancestor with helpful actions disabled must show the evaluation blow-up on wide domains: both must be visible",
    cost_class="CPU-scale", source_evidence="relax.c 876-955; search.c 298-301", purpose="PURPOSE: helpful-action pruning (FF)")

c.ancestry("algorithm_from", "Graphplan (Blum & Furst 1995) planning graph without mutexes; HSP (Bonet & Geffner) heuristic search; Hoffmann & Nebel 2001 JAIR", note="from the file headers; the vault's graphplan-blum-furst-1995 is a sibling fossil for a recurrence test")
c.residue("PARTIALLY_EXPLAINED", ["extract_1P body and initialize_goals (662-770) not read: the heuristic value's exact accounting is inferred from achieve_goals", "best-first search body not read (bfs organ is CANDIDATE)", "the grounding pipeline (~10,000 lines) not read", "nothing ran; a STRIPS benchmark domain is a ready Stage C world"],
          note="the heuristic-and-search core is located; the relation to graphplan-blum-furst-1995 is the first recurrence candidate this pass produces")
c.save(state="COARSE")
