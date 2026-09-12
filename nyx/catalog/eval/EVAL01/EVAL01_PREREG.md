# EVAL01 pre-registration (frozen before any search run)

frozen main sha bc37f828d39b3a5037c75efb4fec9468c01cde8b; 321 bit files, digest 6af7ae914f68e9b9...; search.py 215b52a8e48d3717...; schema.py 8077918ec9fad1de...

For each description Nyx set an axis ONLY where the redacted text states or directly implies its value; lists mean the text is ambiguous between two vocabulary values; unstated axes are omitted. Nyx did not open any bit file while mapping. Disclosed bias: Nyx knows the vocabulary and remembers many signatures; an independent mapper is the cheapest falsification of this step.

## Q01_archaeon_reserve_allocation
source: archaeon/producer/allocation.py (module docstring) (seat code, Archaeon)

description (redacted for mapping):

    WP-X6: the exploration reserve, allocated across FAMILIES first.
    
    Rule R1 (SELECTION_RULES.md): each lane's daily quota is partitioned into an
    ESTABLISHED share and a RESERVE share. The reserve may be drawn only by
    families that are young or thin. The failure this prevents: an established
    family with a hundred templates absorbs every draw a young family with one
    template would otherwise get.
    
    Design, per the order:
    
    * **Family first, template second.** A draw chooses an eligible FAMILY by a
      declared bounded-fairness rule ([name], deterministic replay),
      then a template within it. A family with 100 templates and a family with 1
      receive the same family-level entitlement (X6-a).
    * **Family identity is explicit.** A template names its family in a
      ``family`` field. Templates without one belong to the implicit family
      ``ki

query axes: {"verb": ["SCHEDULE", "ALLOCATE"], "in_geometry": ["SET", "MULTISET"], "state_req": "GLOBAL", "control": "SCHEDULED"}
expected HIT: ['bit.schedule.allocate_by_group_entitlement']
RELATED: ['bit.schedule.rotate_fixed_quanta_over_ready_queue', 'bit.schedule.demote_tasks_that_use_their_whole_quantum', 'bit.allocate.split_power_of_two_blocks_and_coalesce_buddies', 'bit.schedule.assign_next_ready_task_to_first_free_machine']
note: a fair-share / group-entitlement scheduler is catalogued (from the OS section); HIT is possible

## Q02_archaeon_coverage_biased_exploration
source: archaeon/explore.py (module docstring) (seat code, Archaeon)

description (redacted for mapping):

    Exploration fallback.
    
    When no detector fires, Archaeon still proposes an experiment. This is
    DELIBERATE EXPLORATION, not an error condition and not a verdict about the
    corpus. Nothing in this module may be read as "there was nothing to find".
    
    Policy: coverage-biased, not uniform. Uniform RNG re-samples the dense regions
    in proportion to how dense they already are, which is the opposite of what an
    archaeology service wants. The bias is the simplest one that is still
    inspectable by hand:
    
      1. Enumerate the LEGAL cells: the observed (world_family x player_family)
         grid, plus every world x player combination those families license.
      2. Count observations per cell from the fossil record.
      3. NEVER-SAMPLED legal cells are preferred outright (they carry the most
         coverage per run).
      4. Otherwise take cells at or below

query axes: {"verb": ["SAMPLE", "SELECT"], "in_geometry": "MAP", "order_req": "TOTAL", "state_req": ["GLOBAL", "EXTERNAL"], "strategy": "GREEDY"}
expected HIT: NONE (coverage miss expected)
RELATED: ['bit.sample.draw_in_proportion_to_score', 'bit.archive.descriptor_keyed_niching', 'bit.partition.representation_selection_by_occupancy', 'bit.select.move_to_fewest_onward_options', 'bit.remember.evict_by_balancing_recency_and_frequency_lists', 'bit.sample.pick_best_of_random_subset']
note: no least-visited-first sampling bit is known to be catalogued; HIT impossible by expectation -> a top-5 RELATED is the best available outcome; otherwise COVERAGE miss

## Q03_archaeon_cadence_gate
source: archaeon/cadence.py (module docstring) (seat code, Archaeon)

description (redacted for mapping):

    Cadence enforcement: at most SIX autonomous proposals per UTC day, at least
    FOUR HOURS apart, unevadeable by concurrent instances.
    
    The enforcement lives in PostgreSQL. This module is the client of it, and it is
    written so that *its own correctness is not required*: if everything here were
    wrong, the partial unique index on ``(lane, utc_day, day_ordinal)`` would still
    cap the day at six.
    
    The transaction shape, in order, is the whole design:
    
        BEGIN
          SELECT ... FROM archaeon.cadence_gate WHERE gate_id='lane:<lane>' FOR UPDATE
              -- serializes every concurrent Archaeon enqueue in this lane
          SELECT count(*), max(created_at), now()          -- DATABASE clock
            FROM archaeon.experiment_queue
           WHERE lane = <lane>
             AND source_reason IN ('weak_signal','exploration')
             AND utc_day =

query axes: {"verb": "BOUND", "in_geometry": "STREAM", "out_geometry": "BOOLEAN", "order_req": "TOTAL", "state_req": "EXTERNAL", "control": "REACTIVE"}
expected HIT: NONE (coverage miss expected)
RELATED: ['bit.bound.hold_small_sends_until_previous_is_acknowledged', 'bit.bound.double_the_wait_after_each_collision', 'bit.synchronize.flag_intent_then_yield_by_turn_variable', 'bit.synchronize.pass_a_single_token_along_a_tree']
note: no rate-limiter / token-bucket bit is known to be catalogued; expected COVERAGE miss unless a RELATED bound surfaces

## Q04_vivarium_queue_claim
source: vivarium/viv/queue.py (module docstring) (seat code, Vivarium)

description (redacted for mapping):

    The queue state machine.
    
    Every function here takes an open connection and does NOT commit: the caller
    owns the transaction boundary, because a transition and its event row must land
    together or not at all.
    
    The invariants are enforced in the DATABASE (migrations/001), not here:
    
      * a unique partial index on `active_singleton` makes two simultaneously
        claimed/running rows impossible, so a race loses with unique_violation
        rather than double-running an experiment;
      * a BEFORE UPDATE trigger freezes terminal rows whole and rejects every
        transition outside the legal graph;
      * an append-only trigger on the events table refuses UPDATE and DELETE.
    
    This module's job is to make the legal moves and write down that it made them.
    It never chooses WHICH experiment deserves to run on any ground other than
    (priority, cr

query axes: {"verb": "SYNCHRONIZE", "in_geometry": "RECORD", "state_req": "EXTERNAL", "control": "REACTIVE", "guarantee": ["SOUND", "EXACT"]}
expected HIT: NONE (coverage miss expected)
RELATED: ['bit.synchronize.flag_intent_then_yield_by_turn_variable', 'bit.synchronize.pass_a_single_token_along_a_tree', 'bit.synchronize.agree_by_majority_promises_then_majority_accepts', 'bit.repair.replay_log_forward_then_undo_uncommitted', 'bit.synchronize.enter_after_all_replies_deferring_lower_priority']
note: no unique-constraint / optimistic-claim bit is known to be catalogued; expected COVERAGE miss unless a mutual-exclusion bit surfaces as RELATED

## Q05_vivarium_cegis_loop
source: vivarium/viv/cegis_boolean.py (module docstring) (seat code, Vivarium (semantics owned by Proteus))

description (redacted for mapping):

    `[name]` -- a bounded [name] loop, sealed inside one kind.
    
    WHERE THE ADAPTIVE PART LIVES. Inside here, and nowhere else. The loop chooses
    its next candidate and its next counterexample from its own previous internal
    results, and every input that governs those choices -- the candidate policy and
    its seed, the case ordering, the source pack, the component library, the caps,
    the trace bound and the termination rule -- is SEALED in work.payload and
    therefore inside spec_hash. The generic Vivarium runner sees a kind name and a
    result; it never learns that a search happened. That is [name]'s whole requirement,
    and it is structural rather than promised: `viv/executors.py` calls this with a
    payload, a seed and frozen artifact data, and there is no route back out.
    
    PROTEUS OWNS THE SEMANTICS. The grammar, the compiler, the VM, the independent
    t

query axes: {"verb": "SEARCH", "in_geometry": ["PREDICATE", "SET"], "out_geometry": "PROGRAM", "state_req": "LOCAL", "strategy": "INCREMENTAL", "guarantee": "TERMINATES"}
expected HIT: ['bit.repair.add_violated_constraint_and_resolve']
RELATED: ['bit.search.recognition_guided_enumeration', 'bit.search.decision_tree_enumeration_of_a_procedure', 'bit.search.assign_propagate_backtrack', 'bit.compress.repeated_subexpression_abstraction']
note: the counterexample-guided mechanism is catalogued under verb REPAIR (from the SMT lineage); the description says 'search' -> a REPRESENTATION miss on the verb axis is the predicted failure

## Q06_vault_cmaes
source: techne/fossils/specimens/c-cmaes-hansen/record.json (human_capability_summary) (Techne fossil record)

description (redacted for mapping):

    built_to: minimise a black-box, possibly noisy and ill-conditioned objective in continuous space without derivatives | pressure: non-separable, badly scaled landscapes where gradient methods fail or are unavailable | success_means: reaching the optimum's function value within tolerance in a small multiple of the dimension's evaluations

query axes: {"verb": "SEARCH", "in_geometry": "FUNCTION", "out_geometry": ["TENSOR", "SCALAR"], "metric_req": ["NONE", "DISTANCE"], "guarantee": ["APPROXIMATE", "PROBABILISTIC_BOUND"]}
expected HIT: ['bit.sample.refit_distribution_to_elite_samples']
RELATED: ['bit.search.reflect_expand_contract_simplex', 'bit.search.evaluate_at_random_points', 'bit.search.climb_then_restart_from_random', 'bit.generate.perturb_by_scaled_difference_of_others', 'bit.search.accept_worse_moves_with_cooling_probability', 'bit.search.move_toward_own_and_group_best', 'bit.search.adaptive_step_search']
note: the expected bit is catalogued under verb SAMPLE; the description says 'minimise' -> a REPRESENTATION miss on the verb axis is the predicted failure; the query is broad so a SIGNATURE COLLISION among optimisers is also predicted

## Q07_vault_minisat
source: techne/fossils/specimens/minisat-2.2.0/record.json (human_capability_summary) (Techne fossil record)

description (redacted for mapping):

    built_to: decide propositional satisfiability of large CNF formulas and, when satisfiable, produce a model | pressure: industrial verification instances with millions of clauses; the need for a small, readable, extensible solver others could build on | success_means: correct SAT/UNSAT answers (models checkable, UNSAT trusted or proof-logged) fast on competition and industrial benchmarks

query axes: {"verb": ["SEARCH", "VERIFY"], "in_geometry": "PREDICATE", "out_geometry": ["BOOLEAN", "MAP"], "guarantee": "COMPLETE"}
expected HIT: ['bit.search.assign_propagate_backtrack']
RELATED: ['bit.search.depth_first_with_undo', 'bit.repair.add_violated_constraint_and_resolve', 'bit.repair.reassign_conflicting_variable_to_least_conflict_value', 'bit.search.cover_by_choosing_column_with_fewest_options', 'bit.search.wildcard_match_by_backtracking']
note: HIT possible

## Q08_vault_lzw
source: techne/fossils/specimens/ncompress-5.0-lzw-1985/record.json (human_capability_summary) (Techne fossil record)

description (redacted for mapping):

    built_to: shrink files losslessly with an adaptive dictionary that needs no side information | pressure: 1980s disk and modem bandwidth; the patent history of [name] is why [name] displaced it | success_means: exact reconstruction after decompression, with a good compression ratio on text

query axes: {"verb": "COMPRESS", "in_geometry": ["STRING", "STREAM"], "out_geometry": ["BITSTRING", "SEQUENCE"], "state_req": ["LOCAL", "GLOBAL"], "guarantee": "EXACT", "strategy": ["INCREMENTAL", "STREAMING"]}
expected HIT: NONE (coverage miss expected)
RELATED: ['bit.compress.replace_repeat_with_back_reference', 'bit.compress.merge_most_frequent_adjacent_pair', 'bit.compress.repeated_subexpression_abstraction', 'bit.predict.blend_context_statistics_with_escape', 'bit.compress.narrow_interval_by_symbol_probabilities']
note: no adaptive-dictionary (LZ78-type) bit is known to be catalogued; expected COVERAGE miss with a RELATED back-reference/dictionary bit in top-5

## Q09_vault_ldpc
source: techne/fossils/specimens/ldpc-codes-neal-2001/record.json (human_capability_summary) (Techne fossil record)

description (redacted for mapping):

    built_to: correct transmission errors with sparse-graph codes decoded by iterative probabilistic message passing | pressure: approach the Shannon limit with practical decoding complexity | success_means: block/bit error rate after decoding, at a given channel noise, near the code's threshold

query axes: {"verb": "CORRECT", "in_geometry": ["GRAPH", "BITSTRING"], "out_geometry": "BITSTRING", "state_req": "LOCAL", "strategy": "FIXPOINT_ITERATION", "iteration": "PARALLEL_ROUNDS", "guarantee": ["APPROXIMATE", "PROBABILISTIC_BOUND"]}
expected HIT: NONE (coverage miss expected)
RELATED: ['bit.predict.forward_backward_posteriors_on_a_trellis', 'bit.correct.locate_errors_by_solving_syndrome_equations', 'bit.correct.syndrome_locates_single_error', 'bit.accumulate.stationary_scores_by_propagation', 'bit.repair.prune_domains_until_arc_consistent']
note: no belief-propagation-on-a-sparse-graph bit is known to be catalogued (only 2 CORRECT bits exist, both algebraic); expected COVERAGE miss; the interesting question is whether message-passing bits from OTHER verbs surface

## Q10_vault_tscp_chess
source: techne/fossils/specimens/tscp-1.81-kerrigan-1997/record.json (human_capability_summary) (Techne fossil record)

description (redacted for mapping):

    built_to: play legal, reasonable chess with the smallest readable code, so people could learn how chess programs search | pressure: the branching factor of chess: search must prune ([name]), order moves ([name]) and resolve tactics ([name]) | success_means: playing strength on a clock; here, deterministic best-move output at a fixed depth

query axes: {"verb": ["SEARCH", "BOUND"], "in_geometry": "TREE", "order_req": "TOTAL", "strategy": "BRANCH_AND_BOUND", "guarantee": ["DETERMINISTIC", "EXACT"]}
expected HIT: ['bit.bound.prune_branches_outside_window']
RELATED: ['bit.search.branch_and_prune_by_bound', 'bit.bound.raise_depth_limit_and_restart', 'bit.bound.keep_only_k_best_frontier', 'bit.search.expand_deepest_first', 'bit.bound.strategy_switch_on_depth']
note: HIT possible; names redacted before mapping

