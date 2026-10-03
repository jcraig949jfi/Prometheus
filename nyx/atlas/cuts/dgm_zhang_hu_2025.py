"""Cut: dgm-zhang-hu-2025 -- Darwin Godel Machine: an archive of self-modifying coding agents (Zhang, Hu et al. 2025). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 2 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: DGM_outer.py 37-230, 315-322; self_improve_step.py 223-420; coding_agent.py 153-201; utils/evo_utils.py 28-127.
NOT read: llm_withtools, tools/, prompts, the SWE-bench and polyglot harnesses, git utils, analysis. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('dgm-zhang-hu-2025', mode="ANCESTRY_AWARE",
        inspected=['DGM_outer.py 37-230, 315-322', 'self_improve_step.py 223-420', 'coding_agent.py 153-201', 'utils/evo_utils.py 28-127'],
        evidence=[('SOURCE_READ', 'vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:95-104'), ('SOURCE_READ', 'vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:111-150'), ('SOURCE_READ', 'vault:dgm-zhang-hu-2025/upstream/tree/self_improve_step.py:223-420'), ('SOURCE_READ', 'vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:152-190')],
        note="an open archive of agent versions; parents are drawn by a steep sigmoid of benchmark accuracy discounted by their number of archived children; each child is the parent editing its own repository; nearly every child that compiles is kept [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 2 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('parent_choice_by_sigmoid_of_accuracy_times_one_over_one_plus_children', human_name='choose_selfimproves (DGM_outer.py 50-109)', status='ACCEPTED',
    mechanism='default score_child_prop: weight = 1/(1 + exp(-10*(accuracy - 0.5))) * 1/(1 + archived children), normalised; two parents with replacement',
    input='archive metadata', output='two parent commits', state='children counts', failure_landscape="by reading: the 'best' option sorts ascending (picks the worst); the argparse choices list concatenates 'score_child_prop' 'best' into one string, so explicitly passing score_child_prop is rejected (works only as the default)",
    evidence_ref='vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:95-104', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='choose_selfimproves (DGM_outer.py 50-109)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o1 = c.organ('self_improvement_target_chosen_from_failure_modes_or_unresolved_tasks', human_name='DGM_outer.py 111-150', status='ACCEPTED',
    mechanism='if empty patches are at least 10% of tasks, target them with probability 0.25; else stochasticity with 0.25; else context-length errors with 0.25; else a random unresolved task',
    input='parent evaluation', output='a target', state='UNKNOWN', failure_landscape='by reading: an empty unresolved list is compared to 0 (always False) and reaches random.choice([]) (IndexError)',
    evidence_ref='vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:111-150', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='DGM_outer.py 111-150', coverage={'input_topology': 'SET', 'output_topology': 'SCALAR', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('self_edit_in_a_rebuilt_lineage_container_then_staged_benchmark_evaluation', human_name='self_improve_step.py 223-420; evo_utils.py 28-94', status='ACCEPTED',
    mechanism="the parent's lineage is rebuilt by applying every ancestor's patch; a diagnosis model writes a problem statement; the agent edits its own repository for up to 30 minutes; the patch is evaluated on a small subset, then a medium subset only if at least 40% of the small one resolved; accuracy = resolved / submitted pooled over result files",
    input='a parent', output='a child and its accuracy', state='UNKNOWN', failure_landscape='by reading: the full-evaluation threshold and the big task list are loaded but never used',
    evidence_ref='vault:dgm-zhang-hu-2025/upstream/tree/self_improve_step.py:223-420', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='self_improve_step.py 223-420; evo_utils.py 28-94', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SCALAR', 'stochasticity': 'ENVIRONMENT_RANDOM'})

o3 = c.organ('archive_admission_keep_all_that_compile_and_submit', human_name='DGM_outer.py 152-190, 315-322', status='ACCEPTED',
    mechanism='default keep_all appends every child with the required keys, a non-empty patch and at least the small subset submitted; keep_better requires accuracy >= initial - 0.1',
    input='children', output='archive', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:dgm-zhang-hu-2025/upstream/tree/DGM_outer.py:152-190', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='DGM_outer.py 152-190, 315-322', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

c.reject('the rest of the body: llm_withtools, tools/, prompts, the SWE-bench and polyglot harnesses, git utils, analysis', reason='OTHER', evidence='NOT READ; residue')
c.reject("'dgm-zhang-hu-2025' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('an_agent_version_survives_by_compiling_and_is_reproduced_in_proportion_to_a_steep_sigmoid_of_its_benchmark_accuracy_discounted_by_its_offspring', condition='open archive; parent weight from accuracy and child count', world_rewards='higher-accuracy agents with few children', world_punishes='agents whose patches are empty or do not run',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: Darwin Godel Machine: an archive of self-modifying coding agents (Zhang, Hu et al. 2025)')

c.residue('LARGE_RESIDUE', ['not read: llm_withtools, tools/, prompts, the SWE-bench and polyglot harnesses, git utils, analysis', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
