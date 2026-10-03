"""Cut: minimax-facebookresearch-2023 -- unsupervised environment design in JAX (Jiang et al. 2023 minimax; DCD reimplementation). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: src/minimax/util/rl/plr.py 87-378; src/minimax/util/rl/ued_scores.py 1-218; runners/plr_runner.py 40-98, 173-335, 389-540; envs/maze/maze_mutators.py 20-102; runners/paired_runner.py 554-555.
NOT read: train.py, arguments and configs, dr/eval/xp runners, maze envs, models, PPO, agent_pop. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('minimax-facebookresearch-2023', mode="ANCESTRY_AWARE",
        inspected=['src/minimax/util/rl/plr.py 87-378', 'src/minimax/util/rl/ued_scores.py 1-218', 'runners/plr_runner.py 40-98, 173-335, 389-540', 'envs/maze/maze_mutators.py 20-102', 'runners/paired_runner.py 554-555'],
        evidence=[('SOURCE_READ', 'vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/plr.py:106-139'), ('SOURCE_READ', 'vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/plr.py:265-378'), ('SOURCE_READ', 'vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/ued_scores.py:1-218'), ('SOURCE_READ', 'vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/runners/plr_runner.py:40-98, 389-540')],
        note="the same PLR/ACCEL family as jaxued, with seven UED scores, a parallel new|replay|mutate evaluation, and a tie-inclusive insertion rule [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('replay_distribution_over_one_over_one_plus_rank_scores_mixed_with_ages', human_name='PLR manager (plr.py 106-139, 158, 211)', status='ACCEPTED',
    mechanism='rank mode replaces scores by 1/(1+rank) over the whole buffer, masks by filled, raises to 1/temperature and normalises; staleness is ages*filled normalised (falling back to the score distribution); replay = (1-staleness_coef)*score + staleness_coef*staleness; every draw ages all filled levels by 1 and zeroes the drawn one',
    input='scores, ages', output='a replay distribution', state='ages', failure_landscape="by reading: the 'equal weight to present levels' fallback is dead code (z forced to 1 before the test)",
    evidence_ref='vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/plr.py:106-139', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='PLR manager (plr.py 106-139, 158, 211)', coverage={'input_topology': 'SET', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM', 'memory': 'ARCHIVE'})

o1 = c.organ('tie_inclusive_insertion_into_the_lowest_replay_weight_slot_with_mutation_lineage', human_name='buffer update (plr.py 265-378, 141-147)', status='ACCEPTED',
    mechanism="a new level targets the next empty slot, else argmin(replay_dist), and is inserted iff score >= that slot's score (ties replace; jaxued uses strict <); episodes without a done are masked; mutated children carry n_mutations = parent + 1",
    input='levels and scores', output='insertion decisions', state='the buffer', failure_landscape="by reading (MEDIUM): max_returns is overwritten by the current rollout's max, so the stored value can decrease",
    evidence_ref='vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/plr.py:265-378', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='buffer update (plr.py 265-378, 141-147)', coverage={'input_topology': 'SCALAR', 'output_topology': 'DECISION', 'stochasticity': 'DETERMINISTIC'})

o2 = c.organ('seven_ued_scores_from_regret_variants_to_value_disagreement', human_name='ued_scores.py 1-218', status='ACCEPTED',
    mechanism='RELATIVE_REGRET = clip(max_return[agent1] - mean_return[agent0], 0); MEAN_RELATIVE_REGRET mean - mean; POPULATION_REGRET max over agents - mean; L1_VALUE_LOSS mean |advantage| (the PLR default); POSITIVE_VALUE_LOSS mean clip(adv, 0); MAX_MC max(max_return) - value; VALUE_DISAGREEMENT std of values; envs without a done get ignore_val',
    input='returns, values, advantages', output='a level score', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/util/rl/ued_scores.py:1-218', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='ued_scores.py 1-218', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o3 = c.organ('parallel_new_replay_mutate_evaluation_with_gradients_only_from_replay', human_name='plr_runner.py 40-98, 389-540', status='CANDIDATE',
    mechanism='parallel mode forces replay_prob 1.0 and the batch criterion and evaluates new, replayed and mutated levels in one rollout, taking gradients only from the replay slice; robust PLR skips gradients on non-replay steps; easy/hard mutation criteria pick parents by min/max UED score',
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='by reading (MEDIUM): line 327 calls self.student.update; no assignment of self.student was found in runners/',
    evidence_ref='vault:minimax-facebookresearch-2023/upstream/tree/src/minimax/runners/plr_runner.py:40-98, 389-540', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='plr_runner.py 40-98, 389-540', coverage={'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: train.py, arguments and configs, dr/eval/xp runners, maze envs, models, PPO, agent_pop', reason='OTHER', evidence='NOT READ; residue')
c.reject("'minimax-facebookresearch-2023' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('as_jaxued_levels_with_high_value_loss_or_regret_are_kept_and_replayed_and_ties_displace_incumbents', condition='a 100-level buffer; replay priority from a UED score and age', world_rewards='high L1 value loss / regret levels; edited descendants that at least tie the weakest slot', world_punishes='solved and episode-less levels',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: unsupervised environment design in JAX (Jiang et al. 2023 minimax; DCD reimplementation)')

c.residue('LARGE_RESIDUE', ['not read: train.py, arguments and configs, dr/eval/xp runners, maze envs, models, PPO, agent_pop', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
