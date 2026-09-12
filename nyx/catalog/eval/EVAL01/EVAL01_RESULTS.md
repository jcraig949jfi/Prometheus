# EVAL01 -- results (frozen search, frozen catalogue, pre-registered queries)

prereg commit 6a6deb29d9b030109546b7e1ef403015da7217cf; frozen main sha bc37f828d39b3a5037c75efb4fec9468c01cde8b; bits loaded 321; bits digest 6af7ae914f68e9b9... (asserted unchanged at run); search.py 215b52a8e48d3717... (asserted unchanged)
post-hoc repair: NO -- nothing changed between prereg and run (digests asserted)

## Question

Can the frozen catalogue retrieve a relevant algorithmic bit from a behavioural description it was not designed around?

## Summary (mechanical, per the frozen rules)

  TOP-1  HIT 3 / RELATED 3 / MISS 4
  TOP-5  HIT 3 / RELATED 4 / MISS 3
  failure classes: COVERAGE: Q02_archaeon_coverage_biased_exploration, Q03_archaeon_cadence_gate, Q04_vivarium_queue_claim, Q08_vault_lzw, Q09_vault_ldpc; NONE (HIT@1): Q01_archaeon_reserve_allocation, Q10_vault_tscp_chess; REPRESENTATION: Q05_vivarium_cegis_loop, Q06_vault_cmaes, Q07_vault_minisat

Split by whether a HIT was POSSIBLE at the frozen sha (expected_hit non-empty, decided at prereg):
  hit-possible (5): top-1 HIT 3, top-5 HIT 3; misses: ['Q05_vivarium_cegis_loop', 'Q06_vault_cmaes']
  no-bit-exists (5): top-5 RELATED 3, top-5 MISS 2

## Per query

### Q01_archaeon_reserve_allocation  --  top-1 HIT, top-5 HIT, class NONE (HIT@1), top score 1.0, tie group 1
source: archaeon/producer/allocation.py (module docstring)
query axes: {"verb": ["SCHEDULE", "ALLOCATE"], "in_geometry": ["SET", "MULTISET"], "state_req": "GLOBAL", "control": "SCHEDULED"}
top-5:
    1.00  bit.schedule.allocate_by_group_entitlement  exact
    0.88  bit.schedule.rotate_fixed_quanta_over_ready_queue  disagrees {"state_req": 0.5}
    0.75  bit.allocate.copy_live_objects_to_a_fresh_space  disagrees {"in_geometry": 0.0}
    0.75  bit.allocate.mark_reachable_then_free_unmarked  disagrees {"in_geometry": 0.0}
    0.75  bit.schedule.use_pool_k_only_on_every_2_to_the_k_th_reseed  disagrees {"in_geometry": 0.0}
expected / related positions:
    EXPECTED rank   1 score 1.000  bit.schedule.allocate_by_group_entitlement
    related  rank   2 score 0.875  bit.schedule.rotate_fixed_quanta_over_ready_queue  disagrees {"state_req": "LOCAL"}
    related  rank   7 score 0.625  bit.schedule.demote_tasks_that_use_their_whole_quantum  disagrees {"state_req": "LOCAL", "control": "REACTIVE"}
    related  rank  14 score 0.500  bit.allocate.split_power_of_two_blocks_and_coalesce_buddies  disagrees {"in_geometry": "SCALAR", "control": "CALLBACK"}
    related  rank  40 score 0.375  bit.schedule.assign_next_ready_task_to_first_free_machine  disagrees {"in_geometry": "DAG", "state_req": "LOCAL", "control": "REACTIVE"}

### Q02_archaeon_coverage_biased_exploration  --  top-1 MISS, top-5 MISS, class COVERAGE, top score 1.0, tie group 1
source: archaeon/explore.py (module docstring)
query axes: {"verb": ["SAMPLE", "SELECT"], "in_geometry": "MAP", "order_req": "TOTAL", "state_req": ["GLOBAL", "EXTERNAL"], "strategy": "GREEDY"}
top-5:
    1.00  bit.archive.cell_replacement_by_fitness  exact
    0.80  bit.search.order_gated_greedy_acceptance  disagrees {"in_geometry": 0.5, "state_req": 0.5}
    0.70  bit.repair.reassign_conflicting_variable_to_least_conflict_value  disagrees {"verb": 0.0, "state_req": 0.5}
    0.70  bit.select.add_cheapest_edge_joining_components  disagrees {"in_geometry": 0.0, "state_req": 0.5}
    0.70  bit.select.each_component_picks_cheapest_outgoing_edge  disagrees {"in_geometry": 0.0, "state_req": 0.5}
expected / related positions:
    related  rank   9 score 0.700  bit.select.move_to_fewest_onward_options  disagrees {"in_geometry": "GRAPH", "state_req": "LOCAL"}
    related  rank  74 score 0.400  bit.remember.evict_by_balancing_recency_and_frequency_lists  disagrees {"verb": "REMEMBER", "in_geometry": "STREAM", "strategy": "ADAPTIVE_SWITCH"}
    related  rank  77 score 0.400  bit.sample.draw_in_proportion_to_score  disagrees {"in_geometry": "SET", "state_req": "NONE", "strategy": "RANDOMIZED"}
    related  rank  78 score 0.400  bit.sample.pick_best_of_random_subset  disagrees {"in_geometry": "SET", "state_req": "NONE", "strategy": "RANDOMIZED"}
    related  rank 186 score 0.200  bit.partition.representation_selection_by_occupancy  disagrees {"verb": "PARTITION", "in_geometry": "SEQUENCE", "order_req": "NONE", "strategy": "RANDOMIZED"}
    related  rank 282 score 0.000  bit.archive.descriptor_keyed_niching  disagrees {"verb": "PARTITION", "in_geometry": "SEQUENCE", "order_req": "NONE", "state_req": "NONE", "strategy": "DISTRIBUTION"}
POST-HOC JUDGMENT (not a score): top-1 = the MAP-Elites cell-keyed archive (a Nyx T1 organ). Shares the SUBSTRATE (a grid of cells keyed by declared coordinates) but not the operation (replacement by fitness vs selection by low visit count). Weak analogue. The mechanism actually described -- pick the least-visited cell -- is a Go-Explore component that Nyx delivered as a PRESSURE, not as a bit: the coverage gap is in Nyx's own chop.

### Q03_archaeon_cadence_gate  --  top-1 MISS, top-5 MISS, class COVERAGE, top score 0.75, tie group 1
source: archaeon/cadence.py (module docstring)
query axes: {"verb": "BOUND", "in_geometry": "STREAM", "out_geometry": "BOOLEAN", "order_req": "TOTAL", "state_req": "EXTERNAL", "control": "REACTIVE"}
top-5:
    0.75  bit.synchronize.enter_after_all_replies_deferring_lower_priority  disagrees {"verb": 0.0, "state_req": 0.5}
    0.58  bit.detect.termination_by_conserved_weight  disagrees {"verb": 0.0, "order_req": 0.0, "state_req": 0.5}
    0.58  bit.generate.accumulate_entropy_into_pools_and_reseed_a_cipher_counter_generator_when_a_pool_fills  disagrees {"verb": 0.0, "out_geometry": 0.0, "state_req": 0.5}
    0.58  bit.predict.update_value_toward_reward_plus_discounted_best_next  disagrees {"verb": 0.0, "out_geometry": 0.0, "state_req": 0.5}
    0.58  bit.remember.evict_by_balancing_recency_and_frequency_lists  disagrees {"verb": 0.0, "out_geometry": 0.0, "state_req": 0.5}
expected / related positions:
    related  rank   7 score 0.500  bit.bound.double_the_wait_after_each_collision  disagrees {"in_geometry": "SCALAR", "out_geometry": "SCALAR", "state_req": "LOCAL"}
    related  rank   8 score 0.500  bit.bound.hold_small_sends_until_previous_is_acknowledged  disagrees {"out_geometry": "STREAM", "order_req": "NONE", "state_req": "LOCAL"}
    related  rank  19 score 0.417  bit.synchronize.flag_intent_then_yield_by_turn_variable  disagrees {"verb": "SYNCHRONIZE", "in_geometry": "BOOLEAN", "order_req": "NONE", "state_req": "GLOBAL"}
    related  rank  35 score 0.333  bit.synchronize.pass_a_single_token_along_a_tree  disagrees {"verb": "SYNCHRONIZE", "in_geometry": "TREE", "order_req": "NONE", "state_req": "LOCAL"}
POST-HOC JUDGMENT (not a score): top-1 = mutual exclusion by request/reply with priority deferral. The cadence gate has two halves (serialise concurrent enqueues; cap the daily rate); the retrieval captured the serialisation half only. Partial analogue, not in the prereg RELATED set (Nyx's omission when listing RELATED).

### Q04_vivarium_queue_claim  --  top-1 RELATED, top-5 RELATED, class COVERAGE, top score 0.7, tie group 3
source: vivarium/viv/queue.py (module docstring)
query axes: {"verb": "SYNCHRONIZE", "in_geometry": "RECORD", "state_req": "EXTERNAL", "control": "REACTIVE", "guarantee": ["SOUND", "EXACT"]}
top-5:
    0.70  bit.synchronize.agree_by_majority_promises_then_majority_accepts  disagrees {"in_geometry": 0.0, "state_req": 0.5}
    0.70  bit.synchronize.enter_after_all_replies_deferring_lower_priority  disagrees {"in_geometry": 0.0, "state_req": 0.5}
    0.70  bit.synchronize.flag_intent_then_yield_by_turn_variable  disagrees {"in_geometry": 0.0, "state_req": 0.5}
    0.60  bit.synchronize.pass_a_single_token_along_a_tree  disagrees {"in_geometry": 0.0, "state_req": 0.0}
    0.50  bit.detect.termination_by_conserved_weight  disagrees {"verb": 0.0, "in_geometry": 0.0, "state_req": 0.5}
expected / related positions:
    related  rank   1 score 0.700  bit.synchronize.agree_by_majority_promises_then_majority_accepts  disagrees {"in_geometry": "SET", "state_req": "GLOBAL"}
    related  rank   2 score 0.700  bit.synchronize.enter_after_all_replies_deferring_lower_priority  disagrees {"in_geometry": "STREAM", "state_req": "GLOBAL"}
    related  rank   3 score 0.700  bit.synchronize.flag_intent_then_yield_by_turn_variable  disagrees {"in_geometry": "BOOLEAN", "state_req": "GLOBAL"}
    related  rank   4 score 0.600  bit.synchronize.pass_a_single_token_along_a_tree  disagrees {"in_geometry": "TREE", "state_req": "LOCAL"}
    related  rank  25 score 0.300  bit.repair.replay_log_forward_then_undo_uncommitted  disagrees {"verb": "REPAIR", "in_geometry": "STREAM", "state_req": "GLOBAL", "control": "SCHEDULED"}

### Q05_vivarium_cegis_loop  --  top-1 MISS, top-5 MISS, class REPRESENTATION, top score 0.583, tie group 2
source: vivarium/viv/cegis_boolean.py (module docstring)
query axes: {"verb": "SEARCH", "in_geometry": ["PREDICATE", "SET"], "out_geometry": "PROGRAM", "state_req": "LOCAL", "strategy": "INCREMENTAL", "guarantee": "TERMINATES"}
top-5:
    0.58  bit.search.grow_a_simplex_toward_the_origin_using_support_points_of_the_difference_shape  disagrees {"out_geometry": 0.0, "guarantee": 0.0, "strategy": 0.5}
    0.58  bit.search.reflect_expand_contract_simplex  disagrees {"out_geometry": 0.0, "guarantee": 0.0, "strategy": 0.5}
    0.50  bit.detect.sweep_a_line_and_test_only_neighbours_in_the_active_order_at_each_event  disagrees {"verb": 0.0, "out_geometry": 0.0, "guarantee": 0.0}
    0.50  bit.generate.sweep_a_line_maintaining_a_front_of_parabolic_arcs_with_site_and_circle_events  disagrees {"verb": 0.0, "out_geometry": 0.0, "guarantee": 0.0}
    0.50  bit.predict.adjust_weights_by_misclassified_example  disagrees {"verb": 0.0, "in_geometry": 0.0, "out_geometry": 0.0}
expected / related positions:
    related  rank   7 score 0.500  bit.search.assign_propagate_backtrack  disagrees {"out_geometry": "MAP", "guarantee": "COMPLETE", "strategy": "BACKTRACKING"}
    related  rank  51 score 0.333  bit.search.decision_tree_enumeration_of_a_procedure  disagrees {"in_geometry": "FUNCTION", "out_geometry": "SEQUENCE", "guarantee": "COMPLETE", "strategy": "BACKTRACKING"}
    EXPECTED rank  66 score 0.333  bit.repair.add_violated_constraint_and_resolve  disagrees {"verb": "REPAIR", "in_geometry": "MATRIX", "out_geometry": "SCALAR", "guarantee": "MONOTONE"}
    related  rank 147 score 0.167  bit.compress.repeated_subexpression_abstraction  disagrees {"verb": "COMPRESS", "in_geometry": "TREE", "out_geometry": "TREE", "state_req": "GLOBAL", "guarantee": "LOCAL_OPTIMUM", "strategy": "GREEDY"}
    related  rank 220 score 0.083  bit.search.recognition_guided_enumeration  disagrees {"verb": "GENERATE", "in_geometry": "FUNCTION", "out_geometry": "STREAM", "state_req": "GLOBAL", "guarantee": "NONE", "strategy": "BRANCH_AND_BOUND"}
POST-HOC JUDGMENT (not a score): top-1/2 = simplex-growing distance test and Nelder-Mead: NOT analogues (coincidence on SEARCH/FUNCTION-type axes). The expected counterexample-guided bit ranks 66 because its T2 signature carries its lineage's OBJECTS (MATRIX in, SCALAR out, verb REPAIR, guarantee MONOTONE) rather than the abstract shape 'candidate + counterexample set -> candidate'. The representation miss sits on the BIT's side as much as on the mapping.

### Q06_vault_cmaes  --  top-1 RELATED, top-5 RELATED, class REPRESENTATION, top score 1.0, tie group 5
source: techne/fossils/specimens/c-cmaes-hansen/record.json (human_capability_summary)
query axes: {"verb": "SEARCH", "in_geometry": "FUNCTION", "out_geometry": ["TENSOR", "SCALAR"], "metric_req": ["NONE", "DISTANCE"], "guarantee": ["APPROXIMATE", "PROBABILISTIC_BOUND"]}
top-5:
    1.00  bit.search.accept_worse_moves_with_cooling_probability  exact
    1.00  bit.search.evaluate_at_random_points  exact
    1.00  bit.search.step_to_the_zero_of_a_model_fitted_through_the_last_few_points  exact
    1.00  bit.search.step_to_the_zero_of_the_local_linearisation  exact
    1.00  bit.search.step_to_the_zero_of_the_local_second_order_rational_model  exact
expected / related positions:
    related  rank   1 score 1.000  bit.search.accept_worse_moves_with_cooling_probability
    related  rank   2 score 1.000  bit.search.evaluate_at_random_points
    related  rank   7 score 0.800  bit.search.climb_then_restart_from_random  disagrees {"guarantee": "LOCAL_OPTIMUM"}
    related  rank  27 score 0.600  bit.search.adaptive_step_search  disagrees {"in_geometry": "PREDICATE", "guarantee": "EXACT"}
    related  rank  49 score 0.600  bit.search.reflect_expand_contract_simplex  disagrees {"in_geometry": "SET", "guarantee": "NONE"}
    related  rank 124 score 0.400  bit.search.move_toward_own_and_group_best  disagrees {"in_geometry": "SET", "out_geometry": "SET", "guarantee": "NONE"}
    related  rank 207 score 0.200  bit.generate.perturb_by_scaled_difference_of_others  disagrees {"verb": "GENERATE", "in_geometry": "SET", "out_geometry": "SET", "guarantee": "NONE"}
    EXPECTED rank 241 score 0.200  bit.sample.refit_distribution_to_elite_samples  disagrees {"verb": "SAMPLE", "in_geometry": "DISTRIBUTION", "out_geometry": "DISTRIBUTION", "guarantee": "NONE"}
POST-HOC JUDGMENT (not a score): five optimisers tie at 1.0 (annealing acceptance, random evaluation, three root-finding steps); the expected bit ranks 241 under verb SAMPLE. The description says WHAT the tool is built to do (minimise); the catalogue verb says HOW the mechanism moves (refit a sampling distribution). Teleological description vs mechanistic signature: the verb axis is the fault line, and it is systematic (same pattern as Q05).

### Q07_vault_minisat  --  top-1 HIT, top-5 HIT, class REPRESENTATION, top score 0.75, tie group 3
source: techne/fossils/specimens/minisat-2.2.0/record.json (human_capability_summary)
query axes: {"verb": ["SEARCH", "VERIFY"], "in_geometry": "PREDICATE", "out_geometry": ["BOOLEAN", "MAP"], "guarantee": "COMPLETE"}
top-5:
    0.75  bit.search.assign_propagate_backtrack  disagrees {"in_geometry": 0.0}
    0.75  bit.search.expand_deepest_first  disagrees {"in_geometry": 0.0}
    0.75  bit.search.expand_frontier_level_by_level  disagrees {"in_geometry": 0.0}
    0.50  bit.rewrite.recursive_side_condition_discharge  disagrees {"out_geometry": 0.0, "guarantee": 0.0}
    0.50  bit.search.adaptive_step_search  disagrees {"out_geometry": 0.0, "guarantee": 0.0}
expected / related positions:
    EXPECTED rank   1 score 0.750  bit.search.assign_propagate_backtrack  disagrees {"in_geometry": "SET"}
    related  rank  11 score 0.500  bit.search.cover_by_choosing_column_with_fewest_options  disagrees {"in_geometry": "MATRIX", "out_geometry": "SET"}
    related  rank  12 score 0.500  bit.search.depth_first_with_undo  disagrees {"in_geometry": "FUNCTION", "out_geometry": "RECORD"}
    related  rank  21 score 0.500  bit.search.wildcard_match_by_backtracking  disagrees {"in_geometry": "STRING", "guarantee": "EXACT"}
    related  rank  52 score 0.250  bit.repair.reassign_conflicting_variable_to_least_conflict_value  disagrees {"verb": "REPAIR", "in_geometry": "MAP", "guarantee": "NONE"}
    related  rank 244 score 0.000  bit.repair.add_violated_constraint_and_resolve  disagrees {"verb": "REPAIR", "in_geometry": "MATRIX", "out_geometry": "SCALAR", "guarantee": "MONOTONE"}
POST-HOC JUDGMENT (not a score): HIT@1 despite a geometry disagreement (bit says SET of clauses, description mapped to PREDICATE). The frozen rule labels this REPRESENTATION because an axis scored < 1; the hit stands. The rule is coarse, not wrong; it is reported as written.

### Q08_vault_lzw  --  top-1 RELATED, top-5 RELATED, class COVERAGE, top score 0.917, tie group 1
source: techne/fossils/specimens/ncompress-5.0-lzw-1985/record.json (human_capability_summary)
query axes: {"verb": "COMPRESS", "in_geometry": ["STRING", "STREAM"], "out_geometry": ["BITSTRING", "SEQUENCE"], "state_req": ["LOCAL", "GLOBAL"], "guarantee": "EXACT", "strategy": ["INCREMENTAL", "STREAMING"]}
top-5:
    0.92  bit.compress.replace_repeat_with_back_reference  disagrees {"strategy": 0.5}
    0.83  bit.order.vector_of_per_process_counters  disagrees {"verb": 0.0}
    0.75  bit.compress.narrow_interval_by_symbol_probabilities  disagrees {"in_geometry": 0.5, "guarantee": 0.0}
    0.75  bit.compress.store_differences_from_predecessor  disagrees {"in_geometry": 0.5, "strategy": 0.0}
    0.75  bit.order.build_search_structure_then_traverse  disagrees {"verb": 0.0, "in_geometry": 0.5}
expected / related positions:
    related  rank   1 score 0.917  bit.compress.replace_repeat_with_back_reference  disagrees {"strategy": "GREEDY"}
    related  rank   3 score 0.750  bit.compress.narrow_interval_by_symbol_probabilities  disagrees {"in_geometry": "SEQUENCE", "guarantee": "OPTIMAL"}
    related  rank   6 score 0.667  bit.compress.merge_most_frequent_adjacent_pair  disagrees {"in_geometry": "SEQUENCE", "guarantee": "NONE", "strategy": "GREEDY"}
    related  rank  51 score 0.417  bit.compress.repeated_subexpression_abstraction  disagrees {"in_geometry": "TREE", "out_geometry": "TREE", "guarantee": "LOCAL_OPTIMUM", "strategy": "GREEDY"}
    related  rank  68 score 0.417  bit.predict.blend_context_statistics_with_escape  disagrees {"verb": "PREDICT", "in_geometry": "SEQUENCE", "out_geometry": "DISTRIBUTION", "guarantee": "NONE"}

### Q09_vault_ldpc  --  top-1 MISS, top-5 RELATED, class COVERAGE, top score 0.643, tie group 1
source: techne/fossils/specimens/ldpc-codes-neal-2001/record.json (human_capability_summary)
query axes: {"verb": "CORRECT", "in_geometry": ["GRAPH", "BITSTRING"], "out_geometry": "BITSTRING", "state_req": "LOCAL", "strategy": "FIXPOINT_ITERATION", "iteration": "PARALLEL_ROUNDS", "guarantee": ["APPROXIMATE", "PROBABILISTIC_BOUND"]}
top-5:
    0.64  bit.transform.move_each_vertex_to_the_mean_of_its_neighbours  disagrees {"verb": 0.0, "out_geometry": 0.0, "state_req": 0.5}
    0.57  bit.repair.prune_domains_until_arc_consistent  disagrees {"verb": 0.5, "out_geometry": 0.0, "guarantee": 0.0, "iteration": 0.5}
    0.57  bit.search.iterate_pairwise_forces_to_equilibrium  disagrees {"verb": 0.0, "out_geometry": 0.0, "guarantee": 0.0}
    0.50  bit.accumulate.stationary_scores_by_propagation  disagrees {"verb": 0.0, "out_geometry": 0.0, "state_req": 0.5, "guarantee": 0.0}
    0.50  bit.order.number_vertices_by_breadth_first_levels_from_a_peripheral_start  disagrees {"verb": 0.0, "out_geometry": 0.0, "strategy": 0.0, "iteration": 0.5}
expected / related positions:
    related  rank   2 score 0.571  bit.repair.prune_domains_until_arc_consistent  disagrees {"verb": "REPAIR", "out_geometry": "MAP", "guarantee": "MONOTONE", "iteration": "FIFO"}
    related  rank   4 score 0.500  bit.accumulate.stationary_scores_by_propagation  disagrees {"verb": "ACCUMULATE", "out_geometry": "MAP", "state_req": "GLOBAL", "guarantee": "EXACT"}
    related  rank   9 score 0.429  bit.correct.syndrome_locates_single_error  disagrees {"state_req": "NONE", "guarantee": "EXACT", "strategy": "PRECOMPUTED_TABLE", "iteration": "SWEEP"}
    related  rank 125 score 0.143  bit.correct.locate_errors_by_solving_syndrome_equations  disagrees {"in_geometry": "SEQUENCE", "out_geometry": "SEQUENCE", "state_req": "NONE", "guarantee": "EXACT", "strategy": "DIRECT", "iteration": "NONE"}
    related  rank 152 score 0.143  bit.predict.forward_backward_posteriors_on_a_trellis  disagrees {"verb": "PREDICT", "in_geometry": "SEQUENCE", "out_geometry": "DISTRIBUTION", "guarantee": "EXACT", "strategy": "DYNAMIC_PROGRAMMING", "iteration": "SWEEP"}
POST-HOC JUDGMENT (not a score): top-1 = move each vertex to the mean of its neighbours (mesh smoothing). Belief propagation on a sparse graph and neighbour-mean smoothing are both iterated local neighbour aggregation on a graph in parallel rounds: a GENUINE cross-lineage analogue in shape, though not in what is aggregated (posteriors vs positions). Also in top-5: constraint propagation to a fixpoint, stationary-score propagation. The message-passing family surfaced from three lineages although no error-correction bit of that kind exists.

### Q10_vault_tscp_chess  --  top-1 HIT, top-5 HIT, class NONE (HIT@1), top score 1.0, tie group 1
source: techne/fossils/specimens/tscp-1.81-kerrigan-1997/record.json (human_capability_summary)
query axes: {"verb": ["SEARCH", "BOUND"], "in_geometry": "TREE", "order_req": "TOTAL", "strategy": "BRANCH_AND_BOUND", "guarantee": ["DETERMINISTIC", "EXACT"]}
top-5:
    1.00  bit.bound.prune_branches_outside_window  exact
    0.80  bit.search.probe_bins_in_order_of_boundary_distance  disagrees {"guarantee": 0.0}
    0.60  bit.search.adaptive_step_search  disagrees {"in_geometry": 0.0, "strategy": 0.0}
    0.60  bit.bound.fill_a_large_memory_pseudorandomly_then_read_it_back_in_a_data_dependent_order  disagrees {"in_geometry": 0.0, "strategy": 0.0}
    0.60  bit.bound.iterate_a_one_way_function_a_tunable_number_of_times_to_slow_each_guess  disagrees {"in_geometry": 0.0, "strategy": 0.0}
expected / related positions:
    EXPECTED rank   1 score 1.000  bit.bound.prune_branches_outside_window
    related  rank   7 score 0.600  bit.search.branch_and_prune_by_bound  disagrees {"in_geometry": "FUNCTION", "guarantee": "OPTIMAL"}
    related  rank  35 score 0.400  bit.bound.keep_only_k_best_frontier  disagrees {"in_geometry": "SET", "guarantee": "NONE", "strategy": "GREEDY"}
    related  rank 149 score 0.200  bit.bound.raise_depth_limit_and_restart  disagrees {"in_geometry": "FUNCTION", "order_req": "NONE", "guarantee": "COMPLETE", "strategy": "ADAPTIVE_SWITCH"}
    related  rank 150 score 0.200  bit.bound.strategy_switch_on_depth  disagrees {"in_geometry": "FUNCTION", "order_req": "NONE", "guarantee": "PROBABILISTIC_BOUND", "strategy": "ADAPTIVE_SWITCH"}
    related  rank 227 score 0.200  bit.search.expand_deepest_first  disagrees {"in_geometry": "GRAPH", "order_req": "NONE", "guarantee": "COMPLETE", "strategy": "INCREMENTAL"}

## Failure classes, read

  COVERAGE (5/10): least-visited-cell exploration, rate limiting, unique-constraint claim, adaptive dictionary coding, belief
    propagation on a sparse graph. Three of the five still returned a defensible neighbour in top-5 (mutual exclusion for the
    claim; back-reference coding for the dictionary coder; propagation-to-fixpoint bits for belief propagation). Two returned
    nothing in the RELATED set (Q02, Q03), with partial analogues visible only on post-hoc reading.
  REPRESENTATION (3/10, one of them a HIT@1): the systematic fault line is the VERB axis. Owners describe what a tool is
    built to do (minimise, decide, search); the catalogue's verb records how the mechanism moves (SAMPLE, REPAIR). When the
    two coincide (prune, schedule, decide-by-search) the hit is exact; when they diverge the expected bit falls to rank 66
    or 241. A second representation fault: T2 geometry axes sometimes carry the lineage's objects (MATRIX/SCALAR for the SMT
    bit) rather than the mechanism's abstract shape.
  RANKING (0/10) and SIGNATURE_COLLISION (0/10 by the >5 rule): Q06's tie of five optimisers at 1.0 is the closest case;
    a 5-axis query with 2-valued lists on three axes does not separate derivative-free optimisers from root-finders.
  SURPRISING CROSS-LINEAGE (post-hoc judgment): Q09 belief propagation -> neighbour-mean smoothing / constraint propagation /
    score propagation (message passing surfaced from geometry, CSP and ranking lineages with no coding-theory bit present);
    Q03 rate gate -> distributed mutual exclusion (captures the serialisation half). Q02's top-1 is a substrate match only.

## Verdict

  CATALOGUE RETRIEVAL SUPPORTED? INDETERMINATE.
  For: 3 of 5 hit-possible queries retrieved the expected mechanism at rank 1 from an independently written description;
  3 of 5 no-bit queries returned a defensible mechanism neighbour in top-5; one genuine cross-lineage analogue surfaced.
  Against: n = 10; the axis mapping was done by Nyx, who knows the vocabulary and many signatures (a same-author mapping is
  a fit statistic); both non-coverage misses share one systematic cause (teleological verb vs mechanistic verb), which means
  the representation has a known blind spot rather than random error. Nothing here says anything about SFE usefulness.

## Cheapest falsification next

  Same 10 descriptions, same frozen catalogue and search, but the axis mapping done by a NON-Nyx seat (Techne or Archaeon)
  using only the vocabulary docstrings in nyx/catalog/schema.py, preregistered before the run. If HIT@1 on the five
  hit-possible queries drops below 2, the signal was in Nyx's mapping, not in the representation -> NO. If it holds at 3 or
  more, the verdict moves toward YES for mechanistic descriptions, and the verb what/how fault becomes the next preregistered
  test (a verb-blind query variant), not a repair.
