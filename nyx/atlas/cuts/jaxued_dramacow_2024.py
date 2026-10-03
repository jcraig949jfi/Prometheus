"""Cut: jaxued-dramacow-2024 -- unsupervised environment design: curricula of levels for RL agents (Jiang et al. PLR; Parker-Holder et al. ACCEL; Dennis et al. PAIRED). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: src/jaxued/level_sampler.py 1-404 (all); src/jaxued/utils.py 1-57; examples/maze_plr.py 389-395, 462, 515-718, 875-891; examples/maze_paired.py 538-590; src/jaxued/environments/maze/util.py 126-200.
NOT read: maze env, wrappers, craftax and gymnax examples, maze_dr.py, PPO and eval code, the PAIRED adversary network. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('jaxued-dramacow-2024', mode="ANCESTRY_AWARE",
        inspected=['src/jaxued/level_sampler.py 1-404 (all)', 'src/jaxued/utils.py 1-57', 'examples/maze_plr.py 389-395, 462, 515-718, 875-891', 'examples/maze_paired.py 538-590', 'src/jaxued/environments/maze/util.py 126-200'],
        evidence=[('SOURCE_READ', 'vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/level_sampler.py:108-129, 288-341'), ('SOURCE_READ', 'vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/level_sampler.py:145-178, 375-404'), ('SOURCE_READ', 'vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/utils.py:1-57'), ('SOURCE_READ', 'vault:jaxued-dramacow-2024/upstream/tree/examples/maze_plr.py:515-718'), ('SOURCE_READ', 'vault:jaxued-dramacow-2024/upstream/tree/examples/maze_paired.py:538-590')],
        note="a level-replay buffer that keeps the levels on which the agent's value error (or a regret proxy) is high, refreshes stale ones, evicts by a combined score/staleness weight, and (ACCEL) mutates replayed levels to make new candidates; PAIRED trains an adversary on a regret estimate [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('replay_distribution_mixing_rank_transformed_score_with_staleness', human_name='level_weights / sample_replay_level (level_sampler.py 108, 121-129, 288-341)', status='ACCEPTED',
    mechanism='replay weights are (1 - staleness_coeff) * w_s + staleness_coeff * w_c, where w_s ranks filled slots by score (1/rank)^(1/temperature) (or a softmax over the top-k) and w_c is normalised staleness episode_count - timestamp; a replay happens iff the buffer is at least minimum_fill_ratio full and uniform < replay_prob (class defaults 0.95 / staleness 0.5 / min fill 1.0; the maze example overrides to 0.8 / 0.3 / 0.5, temperature 0.3)',
    input='scores, timestamps, episode count', output='a level index; replay or new', state='the buffer', failure_landscape='by reading: _insert_new increments episode_count even when nothing is inserted (392), so rejected candidates age every buffered level',
    evidence_ref='vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/level_sampler.py:108-129, 288-341', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='level_weights / sample_replay_level (level_sampler.py 108, 121-129, 288-341)', coverage={'input_topology': 'SET', 'output_topology': 'DECISION', 'stochasticity': 'SEEDED_RANDOM', 'memory': 'ARCHIVE'})

o1 = c.organ('insertion_only_when_the_new_level_strictly_beats_the_lowest_combined_weight_slot', human_name='_insert_new / _get_next_idx (level_sampler.py 375-404)', status='ACCEPTED',
    mechanism="a new level goes to the next free slot, else to the argmin of the COMBINED replay weight (so staleness counts, not score alone), and is written only if that slot's score is strictly lower than the new score; with duplicate_check a matching level is re-scored and re-stamped instead",
    input='a level and its score', output='an insertion or not', state='the buffer', failure_landscape='by reading: unfilled slots hold -inf and an episode-less score is -inf, so a level with no completed episode never enters even an empty buffer',
    evidence_ref='vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/level_sampler.py:145-178, 375-404', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_insert_new / _get_next_idx (level_sampler.py 375-404)', coverage={'input_topology': 'SCALAR', 'output_topology': 'DECISION', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o2 = c.organ('level_score_as_time_averaged_maxmc_regret_proxy_or_positive_value_loss', human_name='max_mc / pvl (utils.py 1-57); maze_plr.py 389-395, 604', status='ACCEPTED',
    mechanism='MaxMC (the default) scores a level by the time-averaged per-episode mean of max_return - value; PVL by the time-averaged positive advantage; both return -inf when no episode completed; on replay the stored max_return is max(stored, new)',
    input='rollout returns, values, advantages', output='a scalar level score', state='max_return per level', failure_landscape='by reading: max_val starts at zeros, so the stored max return is floored at 0',
    evidence_ref='vault:jaxued-dramacow-2024/upstream/tree/src/jaxued/utils.py:1-57', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='max_mc / pvl (utils.py 1-57); maze_plr.py 389-395, 604', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o3 = c.organ('accel_edit_mutation_of_replayed_levels_without_a_solvability_check', human_name='branch controller (maze_plr.py 515-718) and maze mutator (environments/maze/util.py 126-200)', status='ACCEPTED',
    mechanism='with ACCEL every replay step is followed by a mutate step on the replayed batch; each of n edits is uniform over {no-op, flip a wall, move the goal}; new and mutated levels update the policy only if exploratory_grad_updates (default False: robust PLR), replay always does',
    input='replayed levels', output='mutated candidate levels', state='UNKNOWN', failure_landscape='by reading: about one third of edits are no-ops and no solvability check exists',
    evidence_ref='vault:jaxued-dramacow-2024/upstream/tree/examples/maze_plr.py:515-718', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='branch controller (maze_plr.py 515-718) and maze mutator (environments/maze/util.py 126-200)', coverage={'input_topology': 'MATRIX', 'output_topology': 'MATRIX', 'stochasticity': 'SEEDED_RANDOM'})

o4 = c.organ('paired_adversary_rewarded_by_antagonist_max_minus_protagonist_mean_return', human_name='est_regret (maze_paired.py 538-590)', status='ACCEPTED',
    mechanism='est_regret = antagonist max return - protagonist mean return, unclipped, given to the level-writing adversary only as its final-step reward; the adversary trains with PPO',
    input="two agents' returns", output='an adversary reward', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:jaxued-dramacow-2024/upstream/tree/examples/maze_paired.py:538-590', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='est_regret (maze_paired.py 538-590)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: maze env, wrappers, craftax and gymnax examples, maze_dr.py, PPO and eval code, the PAIRED adversary network', reason='OTHER', evidence='NOT READ; residue')
c.reject("'jaxued-dramacow-2024' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('levels_are_kept_and_replayed_where_the_learner_s_value_error_or_regret_proxy_is_high_and_evicted_when_solved_or_stale', condition="a fixed-capacity buffer of environment levels; the learner trains mostly on replayed levels; a level's priority is its value-error or regret score and its staleness", world_rewards='levels with high positive value error / regret on completed episodes', world_punishes='solved levels (low error) and levels with no completed episode (-inf)',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: unsupervised environment design: curricula of levels for RL agents (Jiang et al. PLR; Parker-Holder et al. ACCEL; Dennis et al. PAIRED)')

c.residue('LARGE_RESIDUE', ['not read: maze env, wrappers, craftax and gymnax examples, maze_dr.py, PPO and eval code, the PAIRED adversary network', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
