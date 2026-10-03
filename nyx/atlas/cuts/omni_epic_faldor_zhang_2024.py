"""Cut: omni-epic-faldor-zhang-2024 -- open-ended generation of learnable, interesting tasks written as code by a foundation model (Faldor, Zhang et al. 2024). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: main_omni_epic.py 1-329; rag_utils.py 9-25, 146-189; omni_epic/core/fm.py 199-208, 249-299, 454-486; omni_epic/core/prompts/query_interestingness.py 1-28; run_utils.py 93-115; configs/omni_epic.yaml 1-78.
NOT read: the other prompts, most of fm.py, environments and robots, main_dreamer.py, vendored dreamerv3/embodied, game/, analysis/. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('omni-epic-faldor-zhang-2024', mode="ANCESTRY_AWARE",
        inspected=['main_omni_epic.py 1-329', 'rag_utils.py 9-25, 146-189', 'omni_epic/core/fm.py 199-208, 249-299, 454-486', 'omni_epic/core/prompts/query_interestingness.py 1-28', 'run_utils.py 93-115', 'configs/omni_epic.yaml 1-78'],
        evidence=[('SOURCE_READ', 'vault:omni-epic-faldor-zhang-2024/upstream/tree/main_omni_epic.py:88-308'), ('SOURCE_READ', 'vault:omni-epic-faldor-zhang-2024/upstream/tree/main_omni_epic.py:148-179'), ('SOURCE_READ', 'vault:omni-epic-faldor-zhang-2024/upstream/tree/omni_epic/core/fm.py:454-486'), ('SOURCE_READ', 'vault:omni-epic-faldor-zhang-2024/upstream/tree/run_utils.py:105-112')],
        note="an append-only archive of task programs gated by three filters in series: the code runs, an LLM judges it interesting against its nearest archived tasks, and a DreamerV3 agent solves it [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('archive_admission_by_compile_then_llm_interestingness_then_agent_success', human_name='outer loop (main_omni_epic.py 88-308)', status='ACCEPTED',
    mechanism="a generated task is compiled and repaired (up to 5 reflections), judged interesting by an LLM (skipped while the archive is no larger than the seed set), trained on with DreamerV3 warm-started from the most similar archived task's checkpoint, and appended to the archive only if its success detector passes; failures go to append-only reject lists",
    input='a generated task program', output='archive or reject', state='four append-only lists', failure_landscape='by reading: with training or success detection disabled, task_success is set True, so every interesting task enters',
    evidence_ref='vault:omni-epic-faldor-zhang-2024/upstream/tree/main_omni_epic.py:88-308', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='outer loop (main_omni_epic.py 88-308)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'DECISION', 'stochasticity': 'ENVIRONMENT_RANDOM', 'memory': 'ARCHIVE'})

o1 = c.organ('example_selection_by_staleness_counter_then_embedding_nearest_neighbours', human_name='main_omni_epic.py 148-179; rag_utils.py 146-189', status='ACCEPTED',
    mechanism="a chosen task is drawn with probability proportional to a counter that rises by 1 each iteration and is reset to 0 for the tasks used as examples; its nearest archived tasks by cosine distance of code embeddings become the generator's examples, and failed tasks near it are shown as negatives",
    input='the archive, embeddings', output='prompt examples', state='per-task counters', failure_landscape='by reading: the counter array is normalised in place before += 1, so counts are not raw; the chosen task is always its own nearest neighbour',
    evidence_ref='vault:omni-epic-faldor-zhang-2024/upstream/tree/main_omni_epic.py:148-179', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='main_omni_epic.py 148-179; rag_utils.py 146-189', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('interestingness_as_an_llm_yes_no_against_the_ten_most_similar_archived_tasks', human_name='query_interestingness (fm.py 454-486; prompt file 1-28)', status='ACCEPTED',
    mechanism="the model is shown the new task and its 10 most similar archived tasks and asked whether the new one is novel, surprising, fun to watch, not too easy and useful; the answer is parsed as 'yes' in the first word",
    input='two task programs', output='a boolean', state='UNKNOWN', failure_landscape='by reading: the parse-failure retry calls the method without its robot_desc argument (TypeError)',
    evidence_ref='vault:omni-epic-faldor-zhang-2024/upstream/tree/omni_epic/core/fm.py:454-486', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='query_interestingness (fm.py 454-486; prompt file 1-28)', coverage={'input_topology': 'SET', 'output_topology': 'DECISION', 'stochasticity': 'ENVIRONMENT_RANDOM'})

o3 = c.organ('success_by_majority_vote_over_logged_step_files', human_name='run_utils.py 93-115', status='ACCEPTED',
    mechanism='a run is successful if any logged step line reads True; the task succeeds if at least half of the success files do',
    input='success files', output='a boolean', state='UNKNOWN', failure_landscape='by reading: with no success files, 0 >= 0 makes the task count as solved',
    evidence_ref='vault:omni-epic-faldor-zhang-2024/upstream/tree/run_utils.py:105-112', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='run_utils.py 93-115', coverage={'input_topology': 'SET', 'output_topology': 'DECISION', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: the other prompts, most of fm.py, environments and robots, main_dreamer.py, vendored dreamerv3/embodied, game/, analysis/', reason='OTHER', evidence='NOT READ; residue')
c.reject("'omni-epic-faldor-zhang-2024' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_generated_task_survives_only_if_it_runs_an_llm_finds_it_interesting_against_its_neighbours_and_an_agent_can_learn_it', condition='an LLM writes environment code; three filters in series decide admission', world_rewards='runnable, judged-interesting, learnable tasks', world_punishes='crashing, uninteresting or unlearnable tasks',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: open-ended generation of learnable, interesting tasks written as code by a foundation model (Faldor, Zhang et al. 2024)')

c.residue('LARGE_RESIDUE', ['not read: the other prompts, most of fm.py, environments and robots, main_dreamer.py, vendored dreamerv3/embodied, game/, analysis/', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
