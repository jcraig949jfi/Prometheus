"""Cut: ai-scientist-v2-sakana-2025 -- agentic tree search over experiment code for automated research (Sakana AI, AI Scientist v2). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: ai_scientist/treesearch/parallel_agent.py 453-547, 713, 1020-1023, 1487-1522, 1535-1659, 1931-2051; ai_scientist/treesearch/journal.py 202-212, 390-502; bfts_config.yaml 36-87.
NOT read: agent_manager.py, metric ordering, the interpreter, multi-seed aggregation, idea generation, the writeup and review code. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('ai-scientist-v2-sakana-2025', mode="ANCESTRY_AWARE",
        inspected=['ai_scientist/treesearch/parallel_agent.py 453-547, 713, 1020-1023, 1487-1522, 1535-1659, 1931-2051', 'ai_scientist/treesearch/journal.py 202-212, 390-502', 'bfts_config.yaml 36-87'],
        evidence=[('SOURCE_READ', 'vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/parallel_agent.py:1931-2051'), ('SOURCE_READ', 'vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/journal.py:420-502'), ('SOURCE_READ', 'vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/parallel_agent.py:713')],
        note="a best-first tree search in which drafting, debugging and improving are single LLM calls, 'buggy' is an LLM verdict or an exception, and 'best' is chosen by an LLM over the good nodes [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('node_choice_drafts_then_debug_with_probability_half_else_best', human_name='_select_parallel_nodes (parallel_agent.py 1931-2051)', status='ACCEPTED',
    mechanism="until the worker slots fill: draft while fewer than num_drafts (3) drafts exist; else with probability debug_prob (0.5) a buggy leaf within max_debug_depth (3); else (stages 1 and 3) the best node, falling back to good nodes by metric, one per tree; stages 2 and 4 expand the stage's best node",
    input='the journal', output='nodes to expand', state='UNKNOWN', failure_landscape='by reading: the first step drafts all 4 worker slots (more than num_drafts); <= max_debug_depth allows depth 4',
    evidence_ref='vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/parallel_agent.py:1931-2051', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_select_parallel_nodes (parallel_agent.py 1931-2051)', coverage={'input_topology': 'TREE', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o1 = c.organ('best_node_chosen_by_an_llm_over_good_nodes_with_argmax_fallback', human_name='get_best_node (journal.py 420-502)', status='ACCEPTED',
    mechanism="unless restricted to the validation metric, the good nodes' ids and metrics are sent to an LLM (default gpt-4o at temperature 0.3) that names the best; on failure, the metric argmax",
    input='good nodes', output='one node', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/journal.py:420-502', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='get_best_node (journal.py 420-502)', coverage={'input_topology': 'SET', 'output_topology': 'SCALAR', 'stochasticity': 'ENVIRONMENT_RANDOM'})

o2 = c.organ('buggy_as_llm_review_or_exception_or_metric_parse_failure_with_a_vlm_plot_gate', human_name='parallel_agent.py 713, 1020-1023, 1641-1659; journal.py 390-407', status='ACCEPTED',
    mechanism="is_buggy = the reviewer's is_bug or an exception; failed or invalid metric parsing also marks it buggy; good nodes additionally need a vision model to accept the plots",
    input="a node's run", output='buggy / good flags', state='UNKNOWN', failure_landscape='by reading: a node that is not buggy but fails the plot check (or has none) is neither good nor buggy and is never selected again',
    evidence_ref='vault:ai-scientist-v2-sakana-2025/upstream/tree/ai_scientist/treesearch/parallel_agent.py:713', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='parallel_agent.py 713, 1020-1023, 1641-1659; journal.py 390-407', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'DECISION', 'stochasticity': 'ENVIRONMENT_RANDOM'})

c.reject('the rest of the body: agent_manager.py, metric ordering, the interpreter, multi-seed aggregation, idea generation, the writeup and review code', reason='OTHER', evidence='NOT READ; residue')
c.reject("'ai-scientist-v2-sakana-2025' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('experiment_nodes_survive_by_running_without_error_passing_llm_and_vision_reviews_and_being_named_best_by_an_llm', condition='half of expansions repair buggy leaves; selection is LLM-arbitrated with a numeric fallback', world_rewards='runnable experiments that LLM and VLM reviewers accept', world_punishes='crashing or rejected experiments',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: agentic tree search over experiment code for automated research (Sakana AI, AI Scientist v2)')

c.residue('LARGE_RESIDUE', ['not read: agent_manager.py, metric ordering, the interpreter, multi-seed aggregation, idea generation, the writeup and review code', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
