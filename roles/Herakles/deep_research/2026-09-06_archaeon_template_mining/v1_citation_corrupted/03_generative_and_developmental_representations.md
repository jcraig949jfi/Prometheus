# Prompt 03: Generative and developmental representations

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctVS1kYW9TUk10S29fdU1QX0szamtBURIXLVUtZGFvU1JNdEtvX3VNUF9LM2prQVE
**Elapsed:** 334s

---

# Computational Bench Design: Generative and Developmental Representations

## Executive Summary

*   **Research suggests** that the current computational bench—which relies on stateless string evaluation and direct evaluations—lacks the fundamental architectural primitives required to natively support generative, developmental, and interactive research representations.
*   **It seems likely that** effectively transitioning to these fields will require precise bench expansions targeting intermediate genotype-to-phenotype mappings, graph-based structural analysis, and multiset reaction simulations. 
*   **The evidence leans toward** encapsulating the entirety of the developmental or chemical simulation step within the executor payload to remain compatible with the bench's strict, single-scalar outcome rules. 

The following sections define the smallest viable experimental templates for five disciplines within this research cluster. Because the current bench is strictly constrained to `noop_v0`, `evaluate_bitstring`, and `random_walk_v0` without population-level logic or interactive topology, none of these fields' most characteristic experiments can run faithfully on the bench today. Consequently, each template proposes the exact executor missing from the bench, followed immediately by the expansion request necessary to build it. 

## Main Body Sections

### 1. Genetic Programming

BEGIN_TEMPLATE
{
  "template_id": "genetic.programming.koza.v0",
  "kind": "evaluate_s_expression.v0",
  "param_space": {"expression_string": {"choices": ["(+ X 1)", "(* X X)", "(IF (> X 0) X 0)"]},
                  "test_domain": {"choices": ["symbolic_regression", "multiplexer"]}},
  "origin": {"source": "LITERATURE",
             "field": "Genetic Programming",
             "reference": "Genetic Programming: On the Programming of Computers by Means of Natural Selection (Koza 1992) [cite: 1, 2]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the algorithmic fitness of a specific tree-structured program (S-expression) against a known computational problem domain [cite: 2]. The field would run this to evaluate the computational problem-solving capability of a specific syntax tree mapping. A SURVIVED verdict would license the claim that this specific program correctly resolves the test cases, but it would NOT license claims about population dynamics, evolutionary trajectories, or how easily this tree structure can be discovered by a selection algorithm."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Genetic Programming
LACKS: Execution and evaluation of tree-structured abstract syntax trees (ASTs) against a predefined problem domain.
WHY: Genetic programming fundamentally relies on representing solutions as executable, branching tree structures rather than fixed-length strings [cite: 2]. No workaround using the existing `evaluate_bitstring` or `random_walk_v0` can faithfully parse, execute, and measure the programmatic logic of an AST against a data set.
SMALLEST_FORM: A new executor kind `evaluate_s_expression.v0` that takes an `expression_string` (string) and a `test_domain` (string), adding a `fitness_score` (float) field to the result for outcome rule comparison.
BLOCKS: Genetic Programming
EVIDENCE: Koza 1992 [cite: 1, 2]
END_EXPANSION

### 2. Artificial Chemistry

BEGIN_TEMPLATE
{
  "template_id": "artificial.chemistry.turing_gas.v0",
  "kind": "simulate_turing_gas.v0",
  "param_space": {"initial_population_size": {"int_range": [cite: 3]},
                  "collision_budget": {"int_range": }},
  "origin": {"source": "LITERATURE",
             "field": "Artificial Chemistry",
             "reference": "Algorithmic Chemistry: A Model for Functional Self-Organization (Fontana 1991) [cite: 4, 5]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the emergence of organizational closure by simulating random, function-on-function collisions between programmatic entities in a multiset reactor [cite: 4]. The field runs this to test whether a random soup of interacting programs will inevitably converge into a stable, self-maintaining cooperative structure [cite: 5]. A SURVIVED verdict (e.g., final_diversity below a scalar threshold) licenses the claim that organizational closure was reached within the given budget, but it would NOT license claims regarding the thermodynamic plausibility of the reactions or the internal graph topology of the resulting organization."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Artificial Chemistry
LACKS: A multispatial reactor environment that applies computational interaction rules between multiple entities to generate new entities over time.
WHY: Artificial chemistry studies emergent properties from the collisions of interacting components (such as Lisp expressions computing on one another) [cite: 4]. The current bench isolates single specifications to solitary evaluations and lacks a mechanism to simulate continuous interactions within a mixed population.
SMALLEST_FORM: A new executor kind `simulate_turing_gas.v0` taking `initial_population_size` (int) and `collision_budget` (int), adding a `final_diversity` (float) field to the result.
BLOCKS: Artificial Chemistry
EVIDENCE: Fontana 1991 [cite: 4, 5, 6]
END_EXPANSION

### 3. Autocatalytic Sets

BEGIN_TEMPLATE
{
  "template_id": "autocatalytic.sets.raf_detection.v0",
  "kind": "detect_raf_set.v0",
  "param_space": {"max_polymer_length": {"int_range": [cite: 7]},
                  "catalysis_probability_scale": {"int_range": [cite: 8]}},
  "origin": {"source": "LITERATURE",
             "field": "Autocatalytic Sets",
             "reference": "Detecting autocatalytic, self-sustaining sets in chemical reaction systems (Hordijk & Steel 2004) [cite: 3, 9, 10]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the mathematical existence and size of a reflexively autocatalytic and food-generated (RAF) set within a random chemical reaction network [cite: 10]. The field runs this to determine the theoretical probability of self-sustaining systems emerging under varying catalysis rates [cite: 3]. A SURVIVED verdict (e.g., raf_size > 0) licenses the claim that a structurally closed autocatalytic topology exists for these parameters, but it would NOT license claims that the set would dominate dynamically in an actual kinetic simulation with varying molecular concentrations."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Autocatalytic Sets
LACKS: Graph-theoretic detection of structurally closed and self-sustaining sub-networks in a bipartite reaction-catalysis graph.
WHY: Autocatalytic set research relies on applying the RAF detection algorithm over an entire generated chemical network to calculate topological closure [cite: 10]. The current bench evaluates isolated strings but has no primitive to generate a combinatorial reaction graph or execute a network search algorithm on it.
SMALLEST_FORM: A new executor kind `detect_raf_set.v0` taking `max_polymer_length` (int) and `catalysis_probability_scale` (int), adding an `raf_size` (int) field to the result.
BLOCKS: Autocatalytic Sets
EVIDENCE: Hordijk & Steel 2004 [cite: 3, 9, 10]
END_EXPANSION

### 4. Artificial Gene Regulatory Networks

BEGIN_TEMPLATE
{
  "template_id": "gene.regulatory.kauffman.v0",
  "kind": "simulate_rbn.v0",
  "param_space": {"n_nodes": {"int_range": [cite: 3]},
                  "k_inputs": {"int_range": [cite: 7, 8]}},
  "origin": {"source": "LITERATURE",
             "field": "Artificial Gene Regulatory Networks",
             "reference": "Metabolic stability and epigenesis in randomly constructed genetic nets (Kauffman 1969) [cite: 11, 12, 13]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the state attractor length of a randomly constructed Boolean network to study epigenetic stability. The field runs this to analyze how macroscopic order (approximating biological cell types) emerges from discrete, interconnected genetic logic gates [cite: 12, 13]. A SURVIVED verdict (e.g., attractor_length <= threshold) licenses the claim that the specific network architecture exhibits ordered, stable state cycles, but it would NOT license claims about the network's resilience to permanent structural damage or mutational node deletion."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Artificial Gene Regulatory Networks
LACKS: Execution of discrete-time, deterministic state transitions on a directed graph of Boolean logic gates to compute cycle attractors.
WHY: Analyzing an artificial gene regulatory network (like a Kauffman network) requires simulating the simultaneous logic updates of an interconnected graph until a cyclic state attractor is identified [cite: 12]. The bench's `random_walk_v0` is stateful but performs only 1D, stochastic increments that cannot replicate multi-node boolean topology.
SMALLEST_FORM: A new executor kind `simulate_rbn.v0` taking `n_nodes` (int) and `k_inputs` (int), adding an `attractor_length` (int) field to the result.
BLOCKS: Artificial Gene Regulatory Networks
EVIDENCE: Kauffman 1969 [cite: 11, 12, 13]
END_EXPANSION

### 5. Evolutionary Developmental Systems (Evo-Devo)

BEGIN_TEMPLATE
{
  "template_id": "evo.devo.artificial_development.v0",
  "kind": "develop_phenotype.v0",
  "param_space": {"developmental_steps": {"int_range": [cite: 8]},
                  "genotype_seed": {"int_range": }},
  "origin": {"source": "LITERATURE",
             "field": "Evolutionary Developmental Systems (Evo-Devo)",
             "reference": "Artificial Development (Harding & Banzhaf 2008) [cite: 8, 14, 15]",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the spatial or structural properties of a final phenotype produced by unfolding a localized developmental rule set (genotype) over a series of discrete mapping steps. The field runs this to study how biological growth processes, such as cellular division or graph rewriting, scale and self-organize from minimal instructions [cite: 14, 15]. A SURVIVED verdict (e.g., phenotype_size > threshold) licenses the claim that the specific developmental trajectory reached a sufficiently complex form, but it would NOT license claims about the evolutionary search trajectory or fitness landscape required to discover that particular genotype."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Evolutionary Developmental Systems (Evo-Devo)
LACKS: An intermediate genotype-to-phenotype mapping phase that applies iterative developmental rewriting rules prior to final evaluation.
WHY: Evo-Devo fundamentally relies on an indirect mapping paradigm where a genotype "grows" or develops into a structurally distinct phenotype via iterative simulation [cite: 15]. The current bench maps specifications directly to fitness evaluations (e.g., `evaluate_bitstring`), completely lacking a simulated embryogeny or growth phase.
SMALLEST_FORM: A new executor kind `develop_phenotype.v0` taking `genotype_seed` (int) and `developmental_steps` (int), adding a `phenotype_size` (int) field to the outcome result.
BLOCKS: Evolutionary Developmental Systems (Evo-Devo)
EVIDENCE: Harding & Banzhaf 2008 [cite: 8, 14, 15]
END_EXPANSION

**Sources:**
1. [abebooks.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqwmwTFTbCA-Uai_dbb2Au5Pl0XMaUZ6K7FLp7zYWU6OalKPlM9SI7j9RDhD3I8HgSufDCxsmzq75-Qvk5mGwub2CdzxW1cF_O4tEsjOoAPd41OqMSW2dzlt8xnOdhrNxm5qUTN3RY2M1cPJUsIxoyOplXyoYdkLCUsaMhw5VY)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFARbXo_hQektaJW1ZiNutj17Zojyfj59yabEbGx3Ju5nDXnbWbMH_GvAu-KlBkLXNsu50L-8X3BdVkuh0ENDWFbtWCWC8Uao9RulT53zPHhq0F5Dv6Z9oTGqg4uCtXMk4zoBGIPIBQb4J4ZWjnlIBl507nzqoam-yinl2Zy1dyYICF5iX9tGGN-DqOWYM5wDvMmtEOF0l_gXyqbARN3WGLPYhfQy0kFZcFtIDnjyoThPl6jzVqrvf7hqwVDg==)
3. [bioone.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj7gnxBawqKg2EUEVyuv-zhIOtEwhqrm9a7aUjV4DxH88tSf6lgHIQLPQDY_LFk1MVLaXeZpLN-qI9m_svvmRyV7iKyxYzIC5lYSgx9gfdy20YctwF8F4K9B-gfOG6J_pF3XBklgiKlgn8Tw6ix478UW1Dm1RKH5XKFqiPu3tw8jyZzP-YTvtBlNlHT9BW3XQcs_AocYJuG2sg_mePiMBDKnCqIXbip5Glcnl0i_G3UQiXXbG1PSY2wD-YfE4LABd-IYofKK62VuU7il1t4tJ52AsT)
4. [santafe.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2x01REu-xyu-GqBuBtwQlKhM5eVb9lHZuZVOUx_zTgk0DgMkCeXdrKxyQGtGbw0PGa7ayVPu3ryl2mCyYvEggVLeZ6iCL-1tjUX-Gkucx1Mi_o9ltoS5K4UnWGtD-4ZeUrkFI_fcdXRxQG892qlCUDDNw53dG6HX8agU2KI4Dg0ibBrxMMpPyDSTAvgKuavDOuuDdL2t89DrtbCxDvNcT)
5. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhO1FDIbXhoc8l-FV0lTPDByZpVx8Pip1vWDsuv7ouCXgPpARb5NuGM2KFXHzwfE3IobyKe2Df8IJCbjEYW-c2VCdngvnbrA7vHAZV4rEiET520qywOgy-YQJ12cE=)
6. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnvnK-IbR8gJL6hg6DdGQLtoBKaoV6-KtybxmNxUTmoHW9AgzTYX6Gd1iDALk_fkB5NT7jOxn3kx_H6DLN2LisJi-M3DbQTUrSPnVFOkTCbn1X6ibMnxYhYucKJTf1gEOssuZfeToOYuvtW3B-j0P2LSEwWMxm5ZLkhA3yjHmUccxuuTnqiZIz-wrHE1YcqZ_mn-JJTNib9xkbrerjjTjDiJJ4iCcf3Q-kjCz946DAt8Q=)
7. [gbv.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJbiDRUymov9_70KT3IbYjfZq4gG_XgisiH9Vk8tWbzzMW4rjiOwLRIMscttFl0elsf64fqYB5r7mdNos3XJlDJvL2RTAWXfkuQlDFnsn-nQG2paCGfcDAoTrjFWVntmzOcszpqIsRO4I=)
8. [bibbase.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDS2yYUzHMtq9TmZt41d91hfGIl7HxUu1ujJWDkm3B4rXttY-TEFOGmiWjIc4jTvarhz23XUIvK2fMTYMVoPgU_O2jUY1sOOkMSUYX_w7lZvheaCtSdr3G4TJSbueZX9ZLK4-vtEo7pl6RoEE_xfrgat5edcgSZGG1LnjhF1BOi7sF3BsC8xEv)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0UcG3R1-PHUtR9v01GjbFsh2yaxq8_wYR0HnnCq-hEGR_3yDzqQcDNzDRIb0e49VJEFLH7kEACZkK85-0gPxCAzWon2sv3gy2BW9_MsWyj_vd0kdYvpwQknAvr-2UrA==)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDfQQaNPsFXka0KfdK0arLbp4c2FjcAxpp4TXLC9J8KSiYtSs20n6OGFPnix19Pz945udbIxQVyvNpKPbM1L49NGjygmW2EhdJ-3hpyBAtdVya7qBs-wiDqo5mh6DsPMV2u4sJ-2m_)
11. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHndZSTTs2kXAUkoRjjo5d9XhzK_b2rDGAWP1pDrmUePs48e653jAyuDhoiGtrFE1fbZQWWY8hdvnlQ2ykKmK3XME6S49RxNpsuSsoA6dlzhyNdVpqCD4lfILXd-X0s)
12. [kth.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSbwCsbeF4FeiSNDCS8UDode7aXSCrMf4POwGzVUyHtKS0pD8niCfGan_V3_VC4c3Gz3fvJ-UG0uzLqtYuqWXK8eldV8Mt4DmcLVfiTi1bIHbPP1K09nLybATuYWIwQq6nkmo4xs3yDzE=)
13. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuHossK9aCsUP-UrGu9ica-HHemuOUubCX5xt6uZrYLOY-ojZlIdTpr_Zn7kjvG-RGfmjmM67pJ-ilGHTQ4Y8yuU36v6wZ868oJ_ad-E3P-bPHG5L-eE5sNzYEiBLnEnQAWcR9CCHqs4IkOkQ605rBpna0-TOm4fdfrrj5Ms5zlhgam43r1C8jOFz3-O6ANarXmubc732b)
14. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvEiEekGZJCtpAbg73iPmg4snbK0CFSDLoViplI2Oj7y1L3rBOX45rM_5o9ZH-vuiHdmX1wj_Bund3mlMYtio_2In76Nn_Pvw0ck3P5p6LBN1BPp9-aC1yX5oJikpAckCThR0mH14rv2qa2eSwiEK6tV64KCj-F7cY3TdYG3EDJoI=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRHHjA8tvPQkt3hwbji7NzYWimUkjOp6eRMNn7Im104dG-Grl72RuL5IiDczKXkLxer-Rm7aq0_6Voc0yEs4_DQDoiRKoK-9xUzI7MJm5R5axOZl3ACUzVS0iEGfk7UfHy3g_FMRUiDxsUsZOkALd8HAYKRY8fs3MoaAL0I7Av)

