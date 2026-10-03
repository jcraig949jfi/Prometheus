"""Cut: xland-minigrid-corl-2023 -- meta-reinforcement learning benchmark over procedurally sampled gridworld rulesets (Nikulin et al. 2023). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: scripts/ruleset_generator.py 1-310; src/xminigrid/benchmarks.py 30-63, 113-123; src/xminigrid/core/rules.py 14-139; src/xminigrid/core/goals.py 17-94; src/xminigrid/environment.py 61-90; src/xminigrid/envs/xland.py 142-198.
NOT read: actions, grid, observation, most rule and goal classes, wrappers, registration, training nets, notebooks. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('xland-minigrid-corl-2023', mode="ANCESTRY_AWARE",
        inspected=['scripts/ruleset_generator.py 1-310', 'src/xminigrid/benchmarks.py 30-63, 113-123', 'src/xminigrid/core/rules.py 14-139', 'src/xminigrid/core/goals.py 17-94', 'src/xminigrid/environment.py 61-90', 'src/xminigrid/envs/xland.py 142-198'],
        evidence=[('SOURCE_READ', 'vault:xland-minigrid-corl-2023/upstream/tree/scripts/ruleset_generator.py:96-275'), ('SOURCE_READ', 'vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/benchmarks.py:30-63'), ('SOURCE_READ', 'vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/environment.py:76-79'), ('SOURCE_READ', 'vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/core/rules.py:14-139')],
        note="tasks are rulesets sampled OFFLINE by growing a production tree backward from a goal, frozen into benchmarks, and drawn uniformly at training time; there is no adaptive curriculum in the tree [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('ruleset_sampled_by_growing_a_production_tree_backward_from_a_goal_with_pruning_and_distractors', human_name='ruleset_generator.py 1-310', status='ACCEPTED',
    mechanism='a goal is drawn uniformly over 11 types; each open tile is either pruned (p = prune_prob, default 0.5 when --prune_chain) into an initial tile or given a rule that produces it from tiles not yet used, whose inputs become the next layer; distractor objects and dead-end rules are added; exact-encoding duplicates are rejected',
    input='seed, depth, pruning', output='a ruleset', state='used tiles', failure_landscape='by reading: deep chains without pruning can exhaust the 60-tile pool (random.choice on an empty list); deduplication is on the exact encoding, so reordered rules count as new',
    evidence_ref='vault:xland-minigrid-corl-2023/upstream/tree/scripts/ruleset_generator.py:96-275', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='ruleset_generator.py 1-310', coverage={'input_topology': 'SCALAR', 'output_topology': 'TREE', 'stochasticity': 'SEEDED_RANDOM'})

o1 = c.organ('uniform_draw_of_a_pre_generated_ruleset_per_environment_per_meta_step', human_name='benchmarks.py 30-63; train_meta_task.py 155-170', status='ACCEPTED',
    mechanism='sample_ruleset is randint over a fixed benchmark; each environment redraws per meta-step; the code comment invites custom curricula but none exists',
    input='a benchmark', output='a ruleset', state='UNKNOWN', failure_landscape='by reading (MEDIUM): the meta-training script evaluates on the same benchmark object it trains on; a split() exists but is not called there',
    evidence_ref='vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/benchmarks.py:30-63', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='benchmarks.py 30-63; train_meta_task.py 155-170', coverage={'input_topology': 'SET', 'output_topology': 'SCALAR', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('reward_one_minus_point_nine_times_elapsed_fraction_on_reaching_the_hidden_goal', human_name='environment.py 61-90', status='ACCEPTED',
    mechanism='reward = 1.0 - 0.9 * step_num / max_steps when the goal is met, else 0; termination zeroes the discount; truncation at max_steps (default 3 * height * width)',
    input='goal check, step count', output='a reward', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/environment.py:76-79', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='environment.py 61-90', coverage={'input_topology': 'SCALAR', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o3 = c.organ('rules_and_goals_as_switch_dispatched_production_checks_on_specific_actions', human_name='core/rules.py 14-139; core/goals.py 17-94', status='CANDIDATE',
    mechanism='every step each rule encoding is scanned through a 12-way switch (e.g. holding tile T while acting turns it into P; standing near T turns it into P) and the goal through a 15-way switch; the code itself notes that rules fire only on certain actions',
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='UNKNOWN by run (action ids not verified)',
    evidence_ref='vault:xland-minigrid-corl-2023/upstream/tree/src/xminigrid/core/rules.py:14-139', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='core/rules.py 14-139; core/goals.py 17-94', coverage={'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: actions, grid, observation, most rule and goal classes, wrappers, registration, training nets, notebooks', reason='OTHER', evidence='NOT READ; residue')
c.reject("'xland-minigrid-corl-2023' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('an_agent_must_infer_a_hidden_production_ruleset_within_an_episode_and_reach_its_goal_quickly', condition='rulesets are fixed in advance and drawn uniformly; within an episode the reward falls linearly with steps', world_rewards='fast in-context discovery of the hidden rule chain', world_punishes='slow or failed goal reaching',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: meta-reinforcement learning benchmark over procedurally sampled gridworld rulesets (Nikulin et al. 2023)')

c.residue('LARGE_RESIDUE', ['not read: actions, grid, observation, most rule and goal classes, wrappers, registration, training nets, notebooks', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
