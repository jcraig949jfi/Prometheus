"""Cut: funsearch-deepmind-2023 -- LLM-guided program search over an island-based program database (Romera-Paredes et al. 2023, FunSearch). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 3 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: implementation/programs_database.py 34-297; implementation/config.py 20-37; implementation/evaluator.py 46-155; implementation/sampler.py 31-33.
NOT read: funsearch.py, code_manipulation.py beyond the calls, tests, notebooks. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('funsearch-deepmind-2023', mode="ANCESTRY_AWARE",
        inspected=['implementation/programs_database.py 34-297', 'implementation/config.py 20-37', 'implementation/evaluator.py 46-155', 'implementation/sampler.py 31-33'],
        evidence=[('SOURCE_READ', 'vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:143-145'), ('SOURCE_READ', 'vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:49-56'), ('SOURCE_READ', 'vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:292-297'), ('SOURCE_READ', 'vault:funsearch-deepmind-2023/upstream/tree/implementation/evaluator.py:46-155')],
        note="programs are clustered by their per-test score signature inside islands; prompts draw clusters by a temperature-annealed softmax and short programs within a cluster; every 4 hours the worse half of the islands is reset. The LLM and the sandbox are stubs (NotImplementedError) [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 3 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('island_reset_of_the_weaker_half_on_a_wall_clock_period', human_name='register_program / reset_islands (programs_database.py 75-167)', status='ACCEPTED',
    mechanism="10 islands; a prompt's island is uniform; when more than 4 h of wall time have passed at a registration, islands are sorted by best score (tiny random tie-break) and the lower half are replaced by new islands seeded with the best program of a random survivor",
    input='registrations', output='reset islands', state='best per island', failure_landscape='by reading: resets happen only inside register_program (no registrations, no resets); a program can land on an island reset after its prompt was made',
    evidence_ref='vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:143-145', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='register_program / reset_islands (programs_database.py 75-167)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM', 'temporal_horizon': 'UNBOUNDED'})

o1 = c.organ('clusters_by_per_test_score_signature_with_the_last_test_key_as_the_score', human_name='_get_signature / _reduce_score (programs_database.py 49-56, 191-203)', status='ACCEPTED',
    mechanism="a program's signature is the tuple of its per-test scores in sorted key order; its scalar score is the score of the LAST key in insertion order, not an aggregate",
    input='per-test scores', output='a cluster and a score', state='UNKNOWN', failure_landscape="by reading: partial score dicts (failed tests) give a different signature and possibly a different 'last' test",
    evidence_ref='vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:49-56', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_get_signature / _reduce_score (programs_database.py 49-56, 191-203)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o2 = c.organ('cluster_choice_by_softmax_with_a_sawtooth_temperature_and_short_program_preference', human_name='get_prompt and sample_program (programs_database.py 205-297)', status='ACCEPTED',
    mechanism='clusters are drawn with replacement by softmax(score / T), T = 0.1 * (1 - (n mod 30000) / 30000); within a cluster a program is drawn by softmax of minus its length normalised by the maximum (a weak preference for short code); the two chosen are ordered by score in the prompt',
    input='clusters', output='prompt programs', state='a program count', failure_landscape='by reading: with replacement, the same cluster can fill both prompt slots',
    evidence_ref='vault:funsearch-deepmind-2023/upstream/tree/implementation/programs_database.py:292-297', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='get_prompt and sample_program (programs_database.py 205-297)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('evaluator_trimming_unparsable_output_and_keeping_passing_tests_only', human_name='evaluator.py 46-65, 103-155', status='ACCEPTED',
    mechanism='LLM output is trimmed line by line until it parses; a per-test score is kept only if the run succeeded, did not call an ancestor and returned a number; a program registers if at least one test passed',
    input='a sample', output='scores per test', state='UNKNOWN', failure_landscape='by reading: the sandbox raises NotImplementedError as shipped',
    evidence_ref='vault:funsearch-deepmind-2023/upstream/tree/implementation/evaluator.py:46-155', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='evaluator.py 46-65, 103-155', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'VECTOR', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: funsearch.py, code_manipulation.py beyond the calls, tests, notebooks', reason='OTHER', evidence='NOT READ; residue')
c.reject("'funsearch-deepmind-2023' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('programs_with_higher_scores_on_the_tests_are_shown_to_the_model_more_often_and_weak_islands_are_periodically_erased', condition='softmax over score clusters at low temperature; half of the islands reset every 4 h', world_rewards='high-scoring, shorter programs', world_punishes='programs on weak islands',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: LLM-guided program search over an island-based program database (Romera-Paredes et al. 2023, FunSearch)')

c.residue('LARGE_RESIDUE', ['not read: funsearch.py, code_manipulation.py beyond the calls, tests, notebooks', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
