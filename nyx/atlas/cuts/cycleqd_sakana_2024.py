"""Cut: cycleqd-sakana-2024 -- quality-diversity over LLM agents by model merging with cyclic task focus (Sakana AI, CycleQD 2024). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: main.py 150-207, 261-439; tasks/base.py 37-46; configs/config.yaml 1-42; sampler/random_sampler.py 1-18; sampler/elite_sampler.py 1-39; crossover/base.py 1-48; crossover/model_linear.py 1-32; mutation/gaussian_mutator.py 1-24; mutation/svd_uniform_mutator.py 1-47.
NOT read: helpers, celery utils, agentbench_db, the fishfarm evaluation, the CMA path in detail. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('cycleqd-sakana-2024', mode="ANCESTRY_AWARE",
        inspected=['main.py 150-207, 261-439', 'tasks/base.py 37-46', 'configs/config.yaml 1-42', 'sampler/random_sampler.py 1-18', 'sampler/elite_sampler.py 1-39', 'crossover/base.py 1-48', 'crossover/model_linear.py 1-32', 'mutation/gaussian_mutator.py 1-24', 'mutation/svd_uniform_mutator.py 1-47'],
        evidence=[('SOURCE_READ', 'vault:cycleqd-sakana-2024/upstream/tree/main.py:150-207'), ('SOURCE_READ', 'vault:cycleqd-sakana-2024/upstream/tree/main.py:261-439'), ('SOURCE_READ', 'vault:cycleqd-sakana-2024/upstream/tree/crossover/model_linear.py:1-32'), ('SOURCE_READ', 'vault:cycleqd-sakana-2024/upstream/tree/configs/config.yaml:1-8')],
        note="one MAP-Elites archive per task, keyed by the binned skills on the OTHER tasks; the task in focus rotates every generation; children are task-vector merges of two parents plus mutation. DEFAULTS DIFFER FROM THE RECORD'S DESCRIPTION: Gaussian (not SVD) mutation, random (not elite) sampling [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('per_task_archives_keyed_by_the_other_tasks_binned_skills', human_name='_get_bc_ids and insertion (main.py 150-207, 387-400)', status='ACCEPTED',
    mechanism="each task's archive key is the tuple of bins (15 over [0, 0.45] or [0, 0.75]) of the other tasks' accuracies and its value the task's own quality; a child is tried against every archive and inserted where the cell is empty or it is strictly better",
    input="a child's per-task accuracies", output='insertions', state='one archive per task', failure_landscape="by reading: binning clamps with the first BC's grid size whatever the dimension",
    evidence_ref='vault:cycleqd-sakana-2024/upstream/tree/main.py:150-207', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_get_bc_ids and insertion (main.py 150-207, 387-400)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o1 = c.organ('cyclic_rotation_of_the_task_in_focus', human_name='main loop (main.py 261-439; config.yaml)', status='ACCEPTED',
    mechanism="the focus task index advances every flip_interval generations (default 1, os -> mbpp -> db, 1200 generations); parents are drawn only from the focus task's archive",
    input='UNKNOWN', output='UNKNOWN', state='the focus index', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:cycleqd-sakana-2024/upstream/tree/main.py:261-439', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='main loop (main.py 261-439; config.yaml)', coverage={'stochasticity': 'DETERMINISTIC', 'temporal_horizon': 'STEP'})

o2 = c.organ('model_merge_crossover_as_noisy_weighted_average_of_task_vectors', human_name='ModelwiseLinearMerge (crossover/model_linear.py 1-32)', status='ACCEPTED',
    mechanism='task vectors tau_i = theta_i - theta_base; weights w_i ~ N(1, 0.01); child = theta_base + sum w_i tau_i / sum w_i per tensor',
    input='two models', output='a merged model', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:cycleqd-sakana-2024/upstream/tree/crossover/model_linear.py:1-32', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='ModelwiseLinearMerge (crossover/model_linear.py 1-32)', coverage={'input_topology': 'VECTOR', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('mutation_gaussian_by_default_or_directional_svd_of_the_focus_task_vector', human_name='gaussian_mutator.py 1-24; svd_uniform_mutator.py 1-47', status='ACCEPTED',
    mechanism="the default config adds N(0, 0.0003) to every tensor; the SVD variant adds U diag(r * S) V^T with r ~ U[0, 0.1) from the focus task's task-vector SVD, a file not in the tree",
    input='a model', output='a mutated model', state='UNKNOWN', failure_landscape="by reading: the SVD step only adds non-negative multiples of the focus task's components (directional, not symmetric noise)",
    evidence_ref='vault:cycleqd-sakana-2024/upstream/tree/configs/config.yaml:1-8', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='gaussian_mutator.py 1-24; svd_uniform_mutator.py 1-47', coverage={'input_topology': 'VECTOR', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: helpers, celery utils, agentbench_db, the fishfarm evaluation, the CMA path in detail', reason='OTHER', evidence='NOT READ; residue')
c.reject("'cycleqd-sakana-2024' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_merged_model_is_kept_if_it_is_the_best_on_the_focus_task_among_models_with_its_skill_profile_on_the_other_tasks', condition="per-task MAP-Elites over the other tasks' skill bins; focus rotates every generation", world_rewards='strict improvement on the focus task within a skill cell', world_punishes='everything else',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: quality-diversity over LLM agents by model merging with cyclic task focus (Sakana AI, CycleQD 2024)')

c.residue('LARGE_RESIDUE', ['not read: helpers, celery utils, agentbench_db, the fishfarm evaluation, the CMA path in detail', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
