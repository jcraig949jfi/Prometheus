"""Cut: openevolve-codelion-2025 -- open-source reimplementation of AlphaEvolve-style LLM program evolution (OpenEvolve). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: openevolve/database.py 157-161, 332-508, 543-602, 977-1097, 1243-1348, 1442-1460, 1631-1645, 1726-1860, 1907-2131, 2293-2500; openevolve/config.py 329-355; openevolve/utils/metrics_utils.py 72-118; openevolve/utils/code_utils.py 137-227, 378-394; openevolve/process_parallel.py 150-329, 1027-1031; openevolve/prompt/sampler.py 262-473.
NOT read: LLM novelty judge (off by default), evaluator cascade, controller, LLM ensemble, templates, checkpointing. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('openevolve-codelion-2025', mode="ANCESTRY_AWARE",
        inspected=['openevolve/database.py 157-161, 332-508, 543-602, 977-1097, 1243-1348, 1442-1460, 1631-1645, 1726-1860, 1907-2131, 2293-2500', 'openevolve/config.py 329-355', 'openevolve/utils/metrics_utils.py 72-118', 'openevolve/utils/code_utils.py 137-227, 378-394', 'openevolve/process_parallel.py 150-329, 1027-1031', 'openevolve/prompt/sampler.py 262-473'],
        evidence=[('SOURCE_READ', 'vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:477-483'), ('SOURCE_READ', 'vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:977-1097'), ('SOURCE_READ', 'vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:1442-1460'), ('SOURCE_READ', 'vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:2020-2131'), ('SOURCE_READ', 'vault:openevolve-codelion-2025/upstream/tree/openevolve/utils/code_utils.py:137-227')],
        note="islands of programs each with a MAP-Elites grid over code length and a cheap diversity heuristic; parents mostly from a 100-slot elite archive; ring migration; the LLM edits by SEARCH/REPLACE diffs [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('per_island_map_elites_cell_admission_with_population_cap', human_name='_add (database.py 332-508); _enforce_population_limit (1907-2000)', status='ACCEPTED',
    mechanism="a child joins its parent's island and takes its feature cell if empty or stale or if fitter (combined_score, else the mean of non-feature metrics); it is added to the island set even when it loses the cell; above population_size (1000) the least fit non-cell-owners are evicted first, the best and newest protected",
    input='a child program', output='cell and island membership', state='islands, cell maps', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:477-483', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_add (database.py 332-508); _enforce_population_limit (1907-2000)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o1 = c.organ('feature_binning_by_running_min_max_of_code_length_and_a_diversity_heuristic', human_name='feature coordinates (database.py 977-1097, 2293-2500)', status='ACCEPTED',
    mechanism='features default to complexity = len(code) and diversity = mean of a fast heuristic (length, line and character differences) against 20 reference programs, min-max scaled over running statistics into 10 bins',
    input='a program', output='a cell key', state='running min and max', failure_landscape='by reading: bin boundaries drift as the running stats move, so incumbent and challenger are binned under different scales; sampling inspirations updates the stats as a side effect',
    evidence_ref='vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:977-1097', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='feature coordinates (database.py 977-1097, 2293-2500)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'VECTOR', 'stochasticity': 'DETERMINISTIC', 'representation_sensitivity': 'SENSITIVE'})

o2 = c.organ('parent_choice_twenty_percent_island_seventy_percent_elite_archive_ten_percent_global', human_name='_sample_parent / sample_from_island (database.py 1442-1460, 543-602, 1631-1645)', status='ACCEPTED',
    mechanism='exploration 0.2 picks uniformly from the island, exploitation 0.7 uniformly from the 100-slot archive, the rest uniformly from all (single process) or fitness-proportionally within the island (parallel path); the archive admits first-come up to 100, then replaces its least fit if the new program is better',
    input='UNKNOWN', output='a parent', state='the archive', failure_landscape='by reading: the first 100 programs fill the archive regardless of fitness',
    evidence_ref='vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:1442-1460', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_sample_parent / sample_from_island (database.py 1442-1460, 543-602, 1631-1645)', coverage={'input_topology': 'SET', 'output_topology': 'SCALAR', 'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('ring_migration_of_island_top_ten_percent_every_fifty_generations', human_name='migrate (database.py 2020-2131)', status='ACCEPTED',
    mechanism="when the island generation counter has advanced by migration_interval (50), each island's top 10% are copied to both ring neighbours through the normal admission; migrants are never re-migrated and identical code is skipped",
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:openevolve-codelion-2025/upstream/tree/openevolve/database.py:2020-2131', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='migrate (database.py 2020-2131)', coverage={'stochasticity': 'DETERMINISTIC'})

o4 = c.organ('llm_edit_by_search_replace_diff_with_silent_skip_of_unmatched_blocks', human_name='apply diff (code_utils.py 137-227); worker (process_parallel.py 283-303)', status='ACCEPTED',
    mechanism='SEARCH/REPLACE blocks are applied by exact line match, then with trailing whitespace stripped; unmatched blocks are skipped silently; the child is rejected only if nothing applied or the code is unchanged',
    input='an LLM diff', output='a child program', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:openevolve-codelion-2025/upstream/tree/openevolve/utils/code_utils.py:137-227', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='apply diff (code_utils.py 137-227); worker (process_parallel.py 283-303)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SEQUENCE', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: LLM novelty judge (off by default), evaluator cascade, controller, LLM ensemble, templates, checkpointing', reason='OTHER', evidence='NOT READ; residue')
c.reject("'openevolve-codelion-2025' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('mostly_elitist_seventy_percent_of_parents_from_a_fitness_archive_with_diversity_only_through_length_and_text_heuristic_cells', condition='per-island grids over code length and a diversity heuristic; elite archive; ring migration', world_rewards='fitter programs', world_punishes='less fit programs in occupied cells',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: open-source reimplementation of AlphaEvolve-style LLM program evolution (OpenEvolve)')

c.residue('LARGE_RESIDUE', ['not read: LLM novelty judge (off by default), evaluator cascade, controller, LLM ensemble, templates, checkpointing', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
