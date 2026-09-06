# Prompt 01: Evolutionary substrates

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctVS1kYXFlSU1NZU5fUFVQcXVUYThRVRIXLVUtZGFxZUlNTWVOX1BVUHF1VGE4UVU
**Elapsed:** 455s

---

# Experimental Design Templates for Evolutionary Substrates

This report evaluates a cluster of five evolutionary research disciplines to provide concrete experiment templates for the computational research bench. 
*   **Artificial Life (ALife)**: Emphasizes spatial, local interactions (e.g., cellular automata) to study emergent self-organization [cite: 1]. 
*   **Open-Ended Evolution**: Requires a historical archive of behaviors to evaluate novelty and bypass fixed objective functions [cite: 2, 3]. 
*   **Evolutionary Computation**: Depends on iterative, inter-repeat feedback loops to dynamically perform selection and mutation [cite: 4]. 
*   **Digital Evolution**: Grounded in the execution of self-replicating programs on virtual hardware architectures [cite: 5, 6]. 
*   **Machine Evolution**: Utilizes graph-based representations (e.g., Cartesian Genetic Programming) to evolve algorithmic structures [cite: 7]. 

The bench currently supports only a stateless scalar bitstring target, a stateful scalar random walk, and a null operation. None of the characteristic methodologies of these five fields can be faithfully expressed using these primitive executors without silently stripping the very mechanics that make them distinct. Consequently, all provided templates propose new executors and are accompanied by precise expansion requests defining the minimum missing technical capabilities required to unblock them.

## Artificial Life (ALife)

BEGIN_TEMPLATE
{
  "template_id": "cellular_automaton_1d.v0",
  "kind": "cellular_automaton_1d",
  "param_space": {"rule_number": {"int_range": },
                  "iterations": {"int_range": [cite: 4]}},
  "origin": {"source": "LITERATURE",
             "field": "Artificial Life (ALife)",
             "reference": "Statistical Mechanics of Cellular Automata (Wolfram 1983) [cite: 1]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Measures whether a specific 1D cellular automaton rule generates sustained non-homogeneous activity. ALife relies on such spatial neighborhood models to study emergent self-organization from simple initial conditions [cite: 8]. A SURVIVED verdict (activity persists) would NOT license the assumption that the rule is capable of universal computation or supports open-ended complexity."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Artificial Life (ALife)
LACKS: A spatial grid executor that updates localized cell states iteratively based on deterministic neighborhood rules.
WHY: ALife grounds its exploration of emergent complexity in local interactions across a spatial topology [cite: 1]. The current bench only offers a static scalar bitstring target or a 1D numeric walk, neither of which provides the cell-to-cell interaction necessary to replicate ALife's foundational cellular automata experiments.
SMALLEST_FORM: An executor `cellular_automaton_1d` taking `rule_number` and `iterations`, adding a `final_active_cells` integer field to the result payload.
BLOCKS: Artificial Life (ALife)
EVIDENCE: S. Wolfram, "Statistical Mechanics of Cellular Automata," Reviews of Modern Physics (1983) [cite: 1, 9].
END_EXPANSION


## Open-Ended Evolution

BEGIN_TEMPLATE
{
  "template_id": "novelty_search.v0",
  "kind": "novelty_search",
  "param_space": {"evaluations": {"int_range": },
                  "maze_type": {"choices": ["medium", "hard"]}},
  "origin": {"source": "LITERATURE",
             "field": "Open-Ended Evolution",
             "reference": "Abandoning Objectives: Evolution Through the Search for Novelty Alone (Lehman & Stanley 2011) [cite: 2, 3]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Evaluates whether searching strictly for behavioral novelty circumvents deception in a maze navigation task. This field would run this to demonstrate that objective-driven search fails in deceptive landscapes where open-ended novelty search succeeds [cite: 2]. A SURVIVED verdict (maze solved) would NOT license the claim that novelty search alone will scale to unboundedly complex real-world tasks without minimal criteria constraints."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Open-Ended Evolution
LACKS: A cross-repeat historical archive to store and query the behavioral outcomes of past evaluations.
WHY: Open-Ended Evolution methods like novelty search evaluate candidates strictly by their distance to previously encountered behaviors [cite: 2, 3]. The bench's execution model isolates repeats (with no shared state other than the 1D walk scalar) and lacks the capacity to store an expanding archive, making it impossible to compute a novelty distance metric.
SMALLEST_FORM: A persistent, bench-managed `behavior_archive` array that stores execution coordinates, and a capability for the executor to compute a distance metric against it.
BLOCKS: Open-Ended Evolution
EVIDENCE: J. Lehman and K. O. Stanley, "Abandoning Objectives: Evolution through the Search for Novelty Alone," Evolutionary Computation (2011) [cite: 2].
END_EXPANSION


## Evolutionary Computation

BEGIN_TEMPLATE
{
  "template_id": "ea_1_plus_1.v0",
  "kind": "ea_1_plus_1",
  "param_space": {"length": {"int_range": [cite: 8]},
                  "generations": {"int_range": [cite: 4]}},
  "origin": {"source": "LITERATURE",
             "field": "Evolutionary Computation",
             "reference": "On the analysis of the (1+1) evolutionary algorithm (Droste, Jansen, Wegener 2002) [cite: 4]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Measures the required generations for the (1+1) evolutionary algorithm to optimize a linear pseudo-Boolean landscape. Evolutionary Computation uses this algorithm as the fundamental theoretical baseline for analyzing expected runtime and mutation efficiency [cite: 4]. A SURVIVED verdict (optimum reached within budget) would NOT license the claim that this algorithm avoids getting trapped in highly non-linear or deceptive local optima."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Evolutionary Computation
LACKS: The ability to pass the output state (such as a mutated genotype) of one execution step directly as the input payload of the subsequent evaluation.
WHY: Evolutionary algorithms fundamentally require a generational loop where the fittest mutated offspring becomes the parent for the next time step [cite: 4]. The bench's sealed specifications enforce static payload parameters across all repeats and do not allow an external algorithm to wrap the `evaluate_bitstring` executor to perform selection over time.
SMALLEST_FORM: A state discipline parameter `feedback` that injects the previous repeat's output string into the next repeat's execution, closing the evolutionary loop.
BLOCKS: Evolutionary Computation
EVIDENCE: Droste, Jansen, and Wegener, "On the analysis of the (1+1) evolutionary algorithm," Theoretical Computer Science (2002) [cite: 4].
END_EXPANSION


## Digital Evolution

BEGIN_TEMPLATE
{
  "template_id": "avida_replication.v0",
  "kind": "avida_cpu",
  "param_space": {"genome_size": {"int_range": [cite: 8]},
                  "point_mutation_rate": {"choices": [cite: 4]}},
  "origin": {"source": "LITERATURE",
             "field": "Digital Evolution",
             "reference": "Avida: A Software Platform for Research in Computational Evolutionary Biology (Ofria & Wilke 2004) [cite: 5, 6]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Tests whether a digital organism embedded in a virtual CPU can successfully execute memory instructions to copy its own genome. Digital evolution requires programs that actually self-replicate in memory rather than utilizing mathematical abstractions [cite: 5, 10]. A SURVIVED verdict (replication achieved) would NOT license the conclusion that the organism has evolved complex logical tasks or will exhibit stable ecosystem dynamics."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Digital Evolution
LACKS: A virtual machine hardware environment featuring a simulated CPU, memory arrays, and instruction set execution.
WHY: Digital evolution investigates self-replicating computer programs executing on virtual hardware, such as Avida or Tierra [cite: 5, 11]. The current bench only evaluates hardcoded operations (walk, bitstring hash) and completely lacks a Turing-complete substrate where genomes can be executed as literal code.
SMALLEST_FORM: An executor `avida_cpu` that initializes a memory array with a `seed_genome`, runs for a specified number of instruction cycles, and outputs a `replications_completed` integer.
BLOCKS: Digital Evolution
EVIDENCE: C. Ofria and C. O. Wilke, "Avida: A Software Platform for Research in Computational Evolutionary Biology," Artificial Life (2004) [cite: 5, 12].
END_EXPANSION


## Machine Evolution

BEGIN_TEMPLATE
{
  "template_id": "cgp_logic_circuit.v0",
  "kind": "cgp_evaluate",
  "param_space": {"nodes": {"int_range": [cite: 11]},
                  "arity": {"choices": [cite: 5, 6]}},
  "origin": {"source": "LITERATURE",
             "field": "Machine Evolution",
             "reference": "Cartesian Genetic Programming (Miller & Thomson 2000) [cite: 7]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Evaluates whether Cartesian Genetic Programming can construct a valid arithmetic logic circuit (e.g., a multiplier) using a 2D grid of functional nodes. Machine evolution focuses on evolving executable architectures and program graphs [cite: 7, 13]. A SURVIVED verdict (valid circuit found) would NOT license the assumption that the evolved network is robust to node failure or efficiently minimal in gates."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Machine Evolution
LACKS: A directed graph representation model that decodes genes into addressable functional nodes and routing connections.
WHY: Machine evolution, and particularly Cartesian Genetic Programming, encodes solutions as cyclic or acyclic graphs of functional primitives rather than linear vectors [cite: 7, 14]. The bench's `evaluate_bitstring` handles flat strings against a hash target and cannot evaluate the topological connectivity or logic outputs of a routed graph.
SMALLEST_FORM: An executor `cgp_evaluate` that takes a grid configuration (`nodes`, `arity`) and a payload graph, mapping inputs through the defined topology to evaluate logic function correctness.
BLOCKS: Machine Evolution
EVIDENCE: J. F. Miller and P. Thomson, "Cartesian Genetic Programming," European Conference on Genetic Programming (2000) [cite: 7, 15].
END_EXPANSION

**Sources:**
1. [stephenwolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsgXp5rB80PhMGizFDj81cA_pJjOZfDItSSJkTFoTistEKBTZB0pRZoGYO_luqg_D_wjl7Kroh4DyeVxSWOqc5SPLnvgbDf7NkEQKQNeZr5EMghNnyFOGuehDw-x5dSsVYPqLTsb-tNG5DNcKz1xA-eSrdpftAJNXGiHJhqQ==)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAxZeVNZ9QlJ-_BJc8UcvwvhAVdnGGKQyHb8w2bBtspUAj1aYDYc2EJXuTIUvrE-BFbzh2KjB7FXTZdSy2Vv5cq72zAX81RjirCtz15ED79IGENr_5GTjNDc7PTjciUA==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMfbjhZEVxcnXjGZsChHMuO7JNb5q7AojDCv5sLne0I4Njnsxks0fyqEos44Wk7Cz6t8061JVYyii9n2adUoZuJ9zAx8WEidkIoh_slekNqfeEnYwrgbZgHHn2I2LBv6O9zHPc6BPPMI1L70UX_wteHtjM5rcWG54oe13kSjNkRjOc7WR8FKLH5EgSZiY7odYXFIZjjADFFKYrKg3NHyqMcON_tck_1KEWEPQF)
4. [hpi.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyph7ECbatWTwwF-deTCR54QTPVrbTQd4iM1PL0-haeBLvhKwyFPpPOAioJ4ONYaHDGbmccYtWb3nX6b5XOqP7RF9EBLTlvtQ7hO6CCD9ctGFJ1Ji7XPBI5lYopluH-U0BTI6K0O0VQcUcuXxqvUim)
5. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqxqDeyp-h3qz69ibqDP0fpSZhBK9hNT1EpxrzMFv1vNYRnTNq7vLuGVXffzeaT_qO59Yi16kmJwy9wkjNbwTJvDLHlf82KKbdqk_MOcYa-J6lV46ylXiWEVYHv87FOeDyQvRrBxC03sc3-fPKGQsIwaEYNIbBgbjkMfiDifZaOXEiK479f1_NqGqrUS3xbiUC)
6. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG1nW8yYf8L1fUm02rocNKQk3FHDKc6j_7rXPqAHjTYlEzT3UAA3ORLH4JyUby5yVvm8983Eoumlz6gP3Bwk6Jdbu-cMY5Px8lsD3t-JB9RWjTQWAXCjx0QmKxxyjvWg==)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC-10MVkI_5zVfPlB425-05pSN-F36KlnINRrMGy7KHilLcKhFdksjo0z_UEdmMMFZ1V8NURm2ZKxZDZuhP-TZRvfLk2EW3urrNk72dbkv-DRPwX_PX-NQ69_I41_YGccLTTuQ4lXiKCSKLVlVcI_sow==)
8. [wolframscience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGTqlpHEC3VK2Wgb7loII89pQrGr3dS7IGiQL2W3cBh3qQoviOq4_pHnpIMeB37ZxqBW7Nv2DeYI9m8TYTYwXHSNaSXDWDjhWMVskIfJrK_aikwQduaUfSNwCR8-93xnmtsP-EgvU-ZWQJ)
9. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDAdLS2CZ_0xMrrnfG-BzOzvRt3mXC2C24Z_Ps3jCGxiAU2qb4sxZX95TVfdXvkbbPPs9lxokr0FVRCHfRVyFUyt0QIMb92--m5QSYYb2ZQMzRhT_CCaBRMyldbUmrRzRK38gJSyKN7l0y3Whe0dbsGbdIhD6aclU=)
10. [msu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCYWv-x3VDp1FDu2JpkK5dRUqwzO0y1kokJ0l12v6ltwdGQOTv2erDkmdjORE3ePXu-hGUJSfTXnOFiGgTSTbZrVMF46pxJ3boipGEI7Q3ItooGtwmY1RnOWChmK7K9u17YxTPwocRmh5GwI8=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2M52mgXO6UnZ8JBMtuocEYwolxQVVyn58A5jbDkZx68EV7388cRR1lpzbydY6b106eIEKe0hXZrx_8UdQR2n9FfTsuRTSVordLD9W4aU5sOtalG8KiRpz2bMSaLpaqj-vCyVdZaVe2vgYOR5NgaGr17NML5yXuxS-FZ4Hev7UHB8XyzsUq38zgcdBzaNC58wMwOQ_A-hsiEdCe8fXD8egl0OCj-U4edkZ1fnNypntui20Bqxi)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuuZoWYMalqLaxaZ4sNQDg2ljYxGv2_bWEcii6BhWfSh_NU9A2JJJpTCIYaqJtiHddd9S_kugBTveRdMxa6FtGT4bT-glTO9dopp8xgJc1sEXnNbooRdnx7xL0LMxQzOPkhdubS9qJGMRVZ_VjI7pGA1JuaQqCYC3Mb5E_9MIjdkg3Zb0XJgiz-AuSghX5x3VaX9BKk1Vgrs0dtV8vHh85Pb2MvldO5kIQE0P_mEafgrxJIA==)
13. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXCUYskJUOdd77jFmCBuZfpOQZJUk3xWrkNDpiF46QykZwtbA4iAh5HewTXUAXHLwzVni5PnqzrQ1xhQJjrLYF4mct945H7pTKGK2PZhG5EgEiSUlMbduP2iqJHaMytF3sS3pqs5FBtsvYfnFoVhVr6xhhWR3gu-_N0AMlzFEHp08pZ-j1W9gsiqSox6eSc_gG)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhJ2vStDQLXg0C6_o8ENFHQGs_XeyLTs-bGhC8BO8An6MpLg-WnsvJcx5Gkkou2lffTGf8tmy5Z8-oH4R3EuYvKsGzB8_WpH1bNKfQv-Fpdu409krrH-vzvQ==)
15. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz77vkzgeFYa5v4Xl4QAaE1rjSgMGJZpj9Y5RB1B5ufYh3IPcJQndk0UhpdRMhquJGA2tqxB4zeUFE9QqJo4PB_CNRwHjENBdPlrAv2hBBAeoOEYf-0pGmrtDhbD4F75DL3rD8FKysg6_s0U5Sg4Vd39PWll6sxqkFLli2blu6aW_cu08kvLoVUQ_P5ZkjSajJKxorT9iTRzuxvJMkgQ==)

