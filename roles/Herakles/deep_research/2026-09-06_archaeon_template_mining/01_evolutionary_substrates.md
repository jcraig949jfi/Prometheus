# Prompt 01: Evolutionary substrates

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaMW1kYXNYVEphbU1qckVQaUs3QmdBcxIXWjFtZGFzWFRKYW1NanJFUGlLN0JnQXM
**Elapsed:** 304s

---

# Computational Research Bench Integration: Evolutionary Substrates

* Research suggests that adapting fields like Artificial Life and Digital Evolution to a constrained execution bench requires decomposing their overarching methods into atomic, single-specification evaluations [cite: 1, 2].
* It seems likely that Evolutionary Computation natively aligns with the bench's existing capabilities, specifically utilizing target-based bitstring evaluations as the fundamental loop of a genetic algorithm [cite: 3, 4].
* The evidence leans toward virtual machine environments and stateful behavioral archives being the most critical missing components required to support digital organism and open-ended evolution methodologies [cite: 5, 6, 7].

## Methodology and Context

This synthesis identifies the smallest viable experiments from five evolutionary disciplines [cite: 8, 9]. While some fields' foundational operations can be natively mapped to the current bench state, evaluating neural network topologies or self-replicating codes requires distinct capability expansions [cite: 10, 11]. The templates and capability expansions below define the exact parameters and operational gaps for integrating these methods onto the bench today.

## Main Body Sections

BEGIN_TEMPLATE
{
  "template_id": "alife.tierra.v0",
  "kind": "tierra_core_v0",
  "param_space": {"ancestor_instructions": {"choices": "80_tierran_opcodes, 82_tierran_opcodes"},
                  "soup_size": {"int_range": "10000 to 50000"},
                  "cycles": {"int_range": "1000000 to 5000000"}},
  "origin": {"source": "LITERATURE",
             "field": "Artificial Life (ALife)",
             "reference": "Thomas S. Ray 1991, An Approach to the Synthesis of Life",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a handwritten ancestor program can execute and successfully replicate its instructions within a simulated memory block. The field of ALife would run this to establish the baseline viability of a digital substrate before introducing mutation. A SURVIVED verdict confirming replication would not license the inference that the system is capable of open-ended evolution, nor that the resulting programs are ecologically stable or resistant to parasites."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "openended.novelty.v0",
  "kind": "novelty_maze_v0",
  "param_space": {"neural_weights": {"float_range": "-2.0 to 2.0"},
                  "maze_config": {"choices": "hard_maze, medium_maze"},
                  "eval_steps": {"int_range": "100 to 400"}},
  "origin": {"source": "LITERATURE",
             "field": "Open-Ended Evolution",
             "reference": "Lehman and Stanley 2011, Abandoning Objectives: Evolution Through the Search for Novelty Alone",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the behavioral endpoint of a single agent in a maze, providing the raw coordinates needed to compute novelty without a fitness target. The field would run this to verify the behavioral characterization function operates correctly. A SURVIVED verdict indicating completion of the steps would not license the inference that the agent solved the maze, nor that its behavior is historically novel compared to a population."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "evolcomp.fitness.v0",
  "kind": "evaluate_bitstring",
  "param_space": {"bits": {"uniform_bits": "length"},
                  "length": {"choices": "16, 24, 32"}},
  "origin": {"source": "LITERATURE",
             "field": "Evolutionary Computation",
             "reference": "John H. Holland 1975, Adaptation in Natural and Artificial Systems",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the objective fitness of a specific binary string against a hidden target landscape. The field would run this as the fundamental inner loop of a genetic algorithm to determine the viability of a single individual. A SURVIVED verdict indicating high fitness would not license the claim that the individual is the global optimum, nor that a full population would successfully maintain diversity on this landscape."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "digitevol.avida.v0",
  "kind": "avida_cpu_v0",
  "param_space": {"genome_sequence": {"choices": "default_ancestor, random_sequence"},
                  "environmental_resource": {"choices": "logic_not, logic_equ"}},
  "origin": {"source": "LITERATURE",
             "field": "Digital Evolution",
             "reference": "Lenski, Ofria, Pennock, and Adami 2003, The Evolutionary Origin of Complex Features",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a specific virtual CPU executing a sequence of instructions can correctly perform a logical operation and trigger a simulated resource reward. The field would run this to trace the functional capability of a single genotype. A SURVIVED verdict confirming the logical operation was performed would not license the inference that the organism evolved this trait naturally, only that the provided sequence mechanically produces the desired output."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "machineevol.neat.v0",
  "kind": "neat_eval_v0",
  "param_space": {"topology_genes": {"choices": "minimal_feedforward, recurrent_feedforward"},
                  "weight_genes": {"float_range": "-1.0 to 1.0"}},
  "origin": {"source": "LITERATURE",
             "field": "Machine Evolution",
             "reference": "Stanley and Miikkulainen 2002, Evolving Neural Networks through Augmenting Topologies",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This evaluates the control performance of a minimal starting neural network on a reinforcement learning task before any structural augmentation occurs. The field would run this to establish the baseline fitness of the simplest possible topology, which is the required starting point for structural complexification. A SURVIVED verdict indicating success would not license the inference that structural innovation is unnecessary, nor that speciation mechanisms were responsible for the performance."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Artificial Life (ALife)
LACKS: A virtual machine execution capability that processes a custom instruction set architecture and tracks memory states.
WHY: ALife and Digital Evolution rely fundamentally on self-replicating programs executing instructions in a simulated computer environment to observe emergent behaviors. No bitstring target evaluation on the current bench can faithfully simulate the operational execution loop of a Tierran or Avida organism.
SMALLEST_FORM: A new executor kind virtual_cpu_v0 taking parameters genome_sequence and environmental_resource, returning an integer field instructions_executed.
BLOCKS: Artificial Life (ALife), Digital Evolution
EVIDENCE: Thomas S. Ray 1991 Tierra system and Charles Ofria 2004 Avida software platform, both of which require simulated CPU cycles to run digital organisms.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Open-Ended Evolution
LACKS: A persistent inter-specification data structure to serve as a historical behavioral archive.
WHY: Open-ended novelty search requires scoring an individual based on its behavioral distance to previously evaluated individuals. Because the bench carries no state across specifications and maps only single scalars to outcomes, it cannot compute novelty relative to past runs.
SMALLEST_FORM: A key-value archive capability added to the world object, allowing an executor to write a coordinate and read the list of past coordinates to return a float field representing distance to the nearest neighbor.
BLOCKS: Open-Ended Evolution
EVIDENCE: Lehman and Stanley 2011 Evolutionary Computation paper on abandoning objectives, which explicitly requires a novelty archive to score behaviors.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Machine Evolution
LACKS: A dynamic simulation environment that can be incrementally stepped forward given neural network control inputs.
WHY: Machine evolution methods like NEAT are designed to evolve controllers for dynamic continuous tasks, not static bitstring landscapes. Without a stateful task environment that accepts network outputs as actions and returns physical observations, evaluating the control capacity of an augmented topology is impossible.
SMALLEST_FORM: A new executor kind neat_eval_v0 taking parameters topology_genes and weight_genes, running a pole-balancing physics simulation to return a float field survival_time.
BLOCKS: Machine Evolution
EVIDENCE: Stanley and Miikkulainen 2002 NEAT evaluation on the benchmark reinforcement learning task of double pole balancing.
END_EXPANSION

**Sources:**
1. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEen6wBq7okJwhsns-YCK6PqBNsuaGOUv6cp_A4zkEn8niLJbtIjqN168x2bYhgTDzethVUkw68RqSuVsygEaCj9B7Y2NHHPI-1anxla3GV_V6udqN2m0EzOvLSk-T_ZOeQpxmOCI3HDd4kwqRr0YoIWUgdbYU8u9tVsctyTKccbzpkhAaGtawxmt4O2GH_5GdEB1oPEPoZ_L7yKIGpqtDX3r-_-SyLVRvOnYi1pg==)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsxRdvWjj_7EklfopZVoVueF_nfrqmCi16kEwhahIblX0dhyWJfBkJdUFC7Pv6wgcoRNTBjMeeszgDJV_NtOffC907BgJ4JWeUQgSP-a95CX7BRfnFXjZQj_qTvjZviSME5faH)
3. [openlibrary.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIoog0gFPbuU5fBtTNkG6w3d3EwC6l5sL8DBR9TbWK1HDhSrsQPexFSQuXmTz6do-wr5im2aoRZqLOBp5VezQ-VeXq-fAHgjSEwaoQzYtsXcSzHA-pJKbvggqzNS-ZJTBifjE8r-in84G_MTnzGtO7pfBHzdysws_e8Ox7mYrtZvwqkJNfcDjvmrkQ)
4. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoDJBEqomQf5gmc-Zbt_Y75qJfel3QH2h_D7Xa_4DdI2C7HCJRWeN8Pe7hT59fZCce2hQ2bG-X3VEjSJ2tlM3nZYKrgrmtdQC7ch_ZWJ1IbpXD1ubayNB61U-s8uqdpylDq4E33cFFMa8ep4eaEFiRhGaWEWGINP0Iqg==)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGK5g2VFdk3miIWIYqTiclNgoJ2gBP13gpRlrq9nVx9VOSMKNq7oLxV8tT62-7ACvfrzZLL0diISFh0BoEUvQb5hdIxNz-uqJs8LR5viuwy3BJYaV2U1new7vN9hAaeg==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK4rtkxkS-CaR1yksNiswvxQWiGxX0hTXWw_ujcZ_TeYvpDyQ8_-X9uWsbdZNwkMMl70B0xfHfeDu1e-eim1nZWKIPGF8a6Rgqhvv2a2somjb2HfImXXcf6fCQaR5gXMgXxhrt9FQ4UX2WMG7P6txVNhTGMMk1mzJu4hsIm6x7FaGAgb_Hwt-8f11eNNqxEs0Nwq9juiOm7EJ62_l4uA1Dtqq00I5oM8-hpUxj)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaRmZZvQCV4LPEtaHuyVR-z_ro6ETWFLbOIna77jaUvLii9cw9Dr_0znIlnQJPnbhNOSr0BlSU3FY8mN4dyl-z9vrTEkfRonjOOKIdTD0gJkG-eZqAc6VbZxp7GJvvqNf7f8r2zorP)
8. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeo85WOGBrXIWubroKUMxGVHxuIEt97fDEmF82qKQchzl2Gkd_iRmeOuoM597cniJJOepzUZp37NctjJdnAEEiYn4h49Vp1CBbfwgr_OSjAC9jl4hHJEWrqgs1UDtJVyul0vUpGLB6)
9. [koth.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEECMwS_Cd2tgRLiRj5Rlqvsu7vTIxI7LP4276x__jmtI5w5Ejw3gIAlk1G8NhoPGL_QsylAWOQOtOtC49owXDNqV1L5cU0doIXCuLzKRd_6KzDidjZC9SeoQ==)
10. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtXXmxLGIkGYfVGW3OPU-K8qqk0uLS9M-8ywCALUNSwosy0F3kRFrGOa-3dH_0WTl9mU0HC-5iXE_zLDzVW8wtni4LzOhIHtIJYrhBezVR5IS-g1s0QIML9-lhyg==)
11. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGovVUUl8SVZCvTU-HkZ_fOtbGaW9WaFqSToiaItesGKf-GdyGM-G0qLj8Eoq059dG8Hdnr-PUsaDoV43FpCjjjwP3MKfHyHHrlZXWgl6LQJJwuKCEc3rpkhttGYZ3miw==)

