# Prompt 02: Diversity and illumination

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZIbEtkYXFWcmxLYlV5UV9Mckpxd0FREhZIbEtkYXFWcmxLYlV5UV9Mckpxd0FR
**Elapsed:** 304s

---

# Computational Research Bench Analysis: Diversity and Illumination Fields

Research suggests that diversity-driven algorithms and coevolutionary paradigms [cite: 1, 2] require distinct mechanisms—such as behavioral archives and dynamic opponent pools—that challenge traditional objective-based architectures [cite: 3, 4]. The analysis below mines these fields for runnable experiment templates suitable for the computational research bench. As requested, all proposals operate within the tight constraints of the bench's single-scalar outcome rule and isolated state architecture. Where the smallest characteristic experiment of a field demands capabilities the bench currently lacks, a new executor kind is proposed and the specific missing computational capability is explicitly delineated. 

## Quality-Diversity (MAP-Elites)

BEGIN_TEMPLATE
{
  "template_id": "map_elites.v0",
  "kind": "qd_map_elites_v0",
  "param_space": {
    "feature_resolution": {"int_range": [cite: 5]},
    "total_evaluations": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Quality-Diversity (MAP-Elites)",
    "reference": "Illuminating search spaces by mapping elites (Mouret and Clune, 2015)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "MAP-Elites explores a search space by mapping high-performing solutions into a discretized behavioral feature space. This executor internally simulates the MAP-Elites algorithm on a continuous optimization problem and returns the percentage of the behavioral grid filled. A SURVIVED verdict based on this scalar would indicate that the algorithm achieved a baseline coverage of the feature space, but it would NOT license the inference that the found elites are closer to a global optimum than those found by a purely objective-driven search, nor would it permit analysis of the morphological trade-offs, as the bench cannot return the archive itself."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Quality-Diversity (MAP-Elites)
LACKS: A behavioral archive subsystem that retains a population of phenotypes, their feature descriptors, and evaluation scores across independent specification runs.
WHY: Quality-diversity and novelty search methods are intrinsically based on mapping or rewarding behavioral differences relative to past discoveries. The current bench isolates every execution to a single world seed and outcome, providing no mechanism to store an archive of prior individuals or measure behavioral distances between runs.
SMALLEST_FORM: A phenotypic_archive object maintained across a repeat block, accepting an array of feature_vector floats and a fitness float per run, and exposing an archive_coverage scalar to the outcome rule.
BLOCKS: Quality-Diversity (MAP-Elites), Novelty Search, Illumination Algorithms
EVIDENCE: Mouret and Clune (2015) "Illuminating search spaces by mapping elites" explicitly requires an N-dimensional grid archive to evaluate new solutions against existing niche elites.
END_EXPANSION

## Novelty Search

BEGIN_TEMPLATE
{
  "template_id": "novelty_search.v0",
  "kind": "novelty_search_maze_v0",
  "param_space": {
    "k_nearest": {"int_range": [cite: 5, 6]},
    "population_size": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Novelty Search",
    "reference": "Exploiting Open-Endedness to Solve Problems Through the Search for Novelty (Lehman and Stanley, 2008)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Novelty search abandons objective fitness gradients and instead selects individuals based on the sparsity of their behaviors in an archive. This executor applies novelty search to a simulated maze navigation task and returns the maximum distance traveled from the start position. A SURVIVED verdict indicates that searching purely for novelty can reach a certain distance in the maze, but it would NOT license the claim that novelty search is universally more efficient than objective-based search without a multi-arm comparison that this bench currently forbids."
}
END_TEMPLATE

## Illumination Algorithms

BEGIN_TEMPLATE
{
  "template_id": "illumination.v0",
  "kind": "surrogate_illumination_v0",
  "param_space": {
    "surrogate_updates": {"int_range": [cite: 5]},
    "design_evaluations": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Illumination Algorithms",
    "reference": "Data-Efficient Exploration, Optimization, and Modeling of Diverse Designs through Surrogate-Assisted Illumination (Gaier et al., 2017)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Illumination algorithms seek to find high-performing solutions across a range of features, often using surrogate models to reduce the number of costly evaluations. This executor runs a surrogate-assisted illumination process on an aerodynamic or structural design task, returning the total hypervolume of valid designs found. A SURVIVED verdict confirms the model's ability to discover a minimum volume of valid configurations, but it does NOT license the conclusion that the surrogate model is accurate in regions of the feature space that were sparsely sampled."
}
END_TEMPLATE

## Coevolution

BEGIN_TEMPLATE
{
  "template_id": "coevolution.v0",
  "kind": "host_parasite_coevolution_v0",
  "param_space": {
    "sorting_network_size": {"choices": [cite: 7]},
    "generations": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Coevolution",
    "reference": "Co-evolving parasites improve simulated evolution as an optimization procedure (Hillis, 1990)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Competitive coevolution pits a population of candidate solutions against a population of test cases to prevent the solutions from stagnating in local optima. This executor replicates Hillis's sorting network experiment, evolving networks against co-evolving parasite test cases, and returns the maximum sorting accuracy achieved. A SURVIVED verdict demonstrates that coevolution successfully produced a functional sorting network, but it does NOT license the claim that the coevolutionary dynamic specifically prevented stagnation, as the bench cannot run the necessary non-coevolutionary control arm for comparison."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Coevolution
LACKS: A dual-population state module that permits candidate solutions from one evaluation to act as the environment or test cases for another.
WHY: Coevolutionary algorithms evaluate individuals not against a static world, but against an interacting population of opponents, parasites, or minimal-criterion targets. The current bench strictly isolates each evaluation to a derived static seed, making it impossible to evaluate one candidate against a dynamic pool of current opponents.
SMALLEST_FORM: A dual_population_buffer that retains the last N emitted parameters of executor runs as opponent seeds for subsequent repeats, adding a max_opponent_fitness field to the scalar results.
BLOCKS: Coevolution, Minimal-Criterion Coevolution
EVIDENCE: Hillis (1990) "Co-evolving parasites improve simulated evolution as an optimization procedure" relies on hosts explicitly evaluated against a dynamic, co-evolving population of parasite test cases.
END_EXPANSION

## Minimal-Criterion Coevolution

BEGIN_TEMPLATE
{
  "template_id": "minimal_criterion_coevolution.v0",
  "kind": "mcc_maze_v0",
  "param_space": {
    "mc_threshold": {"int_range": [cite: 1, 8]},
    "generations": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Minimal-Criterion Coevolution",
    "reference": "Minimal criterion coevolution: a new approach to open-ended search (Brant and Stanley, 2017)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Minimal-criterion coevolution drives open-ended search by requiring individuals from two coevolving populations (such as mazes and solvers) to simply meet a minimal threshold of interaction rather than optimizing an objective. This executor runs MCC and returns the maximum complexity score of the generated mazes. A SURVIVED verdict indicates that the minimal criterion alone was sufficient to bootstrap complexity up to the specified threshold, but it does NOT license claims about the diversity or topological structure of the resulting mazes, as the bench compresses the outcome into a single scalar."
}
END_TEMPLATE

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiqdJlp73-ZmnW1PfYdl9w_WK4eUMp-E9WGC_8jyFrOMWbp8UfZwhDCQfFVH4RCpjyE-vQqMXjXatWwsZ6uAwQ8K-vVpTH_zZws7CeE9Thbgw51eTFiQ==)
2. [gwern.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmrQImGOD9N0CYYGT9oUDjuUtnyYewEPpVddADLK-LExd-_kiP6LWxOg8R6DKW8HToyF8-8UcqnysRfjVt2qkP_qWytCvs2DrLK_m2p4UVHtrae_PPwS8xYmiwu_uv-E1s0b1uYD3mgAxdpeGvu4NCwrJsLWFuBKiPODN6Fr0=)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHgeddaZxCd5S7XncUcwHxXTpRyAYBCK9JqXJTRvk2dhDo0Hqmh-teuhVi99hurt90lmldKir8ysONVYeWyIPdu8stJvryLtaeDszuuTbmTbbVIiXMotLEkZw-kau-5eN5XQQgMrM9H_y9wofWgLvFlrvH0ffD783VNx-HBQYT-6R1FAgGwnS3hntlmbNrd3n6gdEal2AzgOoPSUHXhgH3iKMIgBaob6oCyByW9vFo-P_4tXYFC9_uqMdGsNZfPAWlDszQdQU=)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq9OUN-MnxQ3mRW81dNBEXFbj87YGi51cAmsa0KjqZkULBvxsRsy6KFs13A9Jf2cWJGNdC6HN8X8VloJz0XgeLptmT9UbwlpsSqxCI8TMmEJFXHFzSQA85obrzaB4DhBSutZ-XGY7GdiwZwyW9GPIhhB__YgXElNPUVuvvCQRvFTSIZGSi2BJP_R9ORJUoHaddljl9h_9J9kfKHZgvZ8B-dMbob8rtn9XdySSevgZYhvhoZiXB8hZ91enIW-bZtQ==)
5. [ucf.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4QB7Cj20MODBmOH3UokaZbH59nFAp1kJ5bJEG-aGkXeU0CoKcuVyzDLvnLVfPOhR2y1ppxq4TUMf0l4i8bEIeJWt8pw5eKe4HJbWdm5BEin5Gt6gH2fxr277qhDJw2U9lAEdY)
6. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4iq9Z4cDVdxc2nIIkw6oGp8cVWPtFlCKnu22NqcSg-dVGEo2WXelAoBhbBxE-aMX7fZEVv4xfUoBLakJroOqI9SoXpuJA4yOBa1BYFR0UH9iGRtND0grQgToYKCK95tr_Vghyz3JGAvAqETvAGzk1zbidBtP8DUgIO6ejW-nNxx9HthOd77lHPgKmCztYR9mgV_YmWnQ2)
7. [alife.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVz51j8KTgrvvFQ_7PKIB2vzfTsJjABN0vBgw38q-YRrkgMMfzXtCqwmxfQ06-1bZMJckzaOc8tSuo7vgKmMfP35jc_nZAse5Ml0iwYjLmiiGztgQDs11g9jst4V-gcCVesjrWZ7xZK7AxxVojv-MNagNxPB-Z5wk=)
8. [ametsoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-iagy6o4dddAX1R3yxHoEUZQXJ7MIZZXLnCcuXnlVvmyq0SKrslx1SGgT7WsxzgzSEaFap6DS56MpEIMsrjBxBeHtKa2-WO7gG44bQl6tkaDlsiV_5Nj3JrU2eV5-iWzBNeK6xwCfdjGyVnEcquvU_aTAYZF5uMXOMGrEuRFfBg==)

