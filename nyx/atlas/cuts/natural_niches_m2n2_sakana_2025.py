"""Cut: natural-niches-m2n2-sakana-2025 -- model merging with competition for limited resources and attraction-based mate choice (Sakana AI, M2N2 / Natural Niches 2025). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: natural_niches_fn.py 13-148; helper_fn.py 8-95; model.py 24-72; data.py 4-14; main.py 16-56.
NOT read: map_elites_fn.py, cma_es_fn.py, brute_force_fn.py, plotting. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('natural-niches-m2n2-sakana-2025', mode="ANCESTRY_AWARE",
        inspected=['natural_niches_fn.py 13-148', 'helper_fn.py 8-95', 'model.py 24-72', 'data.py 4-14', 'main.py 16-56'],
        evidence=[('SOURCE_READ', 'vault:natural-niches-m2n2-sakana-2025/upstream/tree/natural_niches_fn.py:50-73'), ('SOURCE_READ', 'vault:natural-niches-m2n2-sakana-2025/upstream/tree/natural_niches_fn.py:13-39'), ('SOURCE_READ', 'vault:natural-niches-m2n2-sakana-2025/upstream/tree/helper_fn.py:8-75')],
        note="each data point is a resource shared among the models that solve it; the worst member is replaced by a child; the second parent is chosen for complementarity; crossover is SLERP with a random split point. The data are sklearn 8x8 digits, not MNIST [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('fitness_as_points_solved_divided_by_how_many_others_solve_them_with_worst_replacement', human_name='update archive (natural_niches_fn.py 42-73)', status='ACCEPTED',
    mechanism="z_j = (sum over population plus child of correctness on point j)^alpha with 0 replaced by 1; fitness_i = sum_j s_ij / z_j; the argmin is replaced by the child unless the child is itself the argmin (alpha 1.0; the 'ga' baseline uses alpha 0)",
    input='correctness matrix and a child', output='an updated archive', state='20 models', failure_landscape='by reading: ties go to the newcomer (the earlier existing index is the argmin and is replaced)',
    evidence_ref='vault:natural-niches-m2n2-sakana-2025/upstream/tree/natural_niches_fn.py:50-73', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='update archive (natural_niches_fn.py 42-73)', coverage={'input_topology': 'MATRIX', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'competition': 'CONTENDS', 'resource_dependence': 'SHARED_RESOURCE'})

o1 = c.organ('attraction_mate_choice_by_how_much_a_candidate_beats_the_first_parent_where_it_is_weak', human_name='matchmaker (natural_niches_fn.py 13-39)', status='ACCEPTED',
    mechanism='parent 1 is drawn proportionally to normalised fitness; parent 2 proportionally to sum_j max(0, F_kj - F_p1,j)',
    input='fitness matrix', output='two parents', state='UNKNOWN', failure_landscape='by reading: if parent 1 weakly dominates everyone, all attraction scores are 0 and the probabilities are NaN',
    evidence_ref='vault:natural-niches-m2n2-sakana-2025/upstream/tree/natural_niches_fn.py:13-39', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='matchmaker (natural_niches_fn.py 13-39)', coverage={'input_topology': 'MATRIX', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM', 'cooperation': 'SHARES'})

o2 = c.organ('slerp_crossover_with_a_random_split_point_on_the_flat_parameter_vector', human_name='helper_fn.py 8-75', status='ACCEPTED',
    mechanism='a split index and w ~ U[0,1) are drawn; parameters before the split interpolate with w and after it with 1 - w, using one global SLERP angle (linear interpolation if sin is tiny); the split ignores layer boundaries',
    input='two parameter vectors', output='a child', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:natural-niches-m2n2-sakana-2025/upstream/tree/helper_fn.py:8-75', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='helper_fn.py 8-75', coverage={'input_topology': 'VECTOR', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: map_elites_fn.py, cma_es_fn.py, brute_force_fn.py, plotting', reason='OTHER', evidence='NOT READ; residue')
c.reject("'natural-niches-m2n2-sakana-2025' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('models_are_kept_for_solving_data_points_few_others_solve_and_mated_for_complementarity', condition='implicit fitness sharing over data points; steady-state worst replacement', world_rewards='models good on under-served points', world_punishes='redundant models',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: model merging with competition for limited resources and attraction-based mate choice (Sakana AI, M2N2 / Natural Niches 2025)')

c.residue('LARGE_RESIDUE', ['not read: map_elites_fn.py, cma_es_fn.py, brute_force_fn.py, plotting', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
