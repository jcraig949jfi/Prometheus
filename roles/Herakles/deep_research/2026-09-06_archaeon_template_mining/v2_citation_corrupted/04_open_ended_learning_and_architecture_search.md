# Prompt 04: Open-ended learning and architecture search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpMU9kYXM2REVlYmNqTWNQdU9tam1RcxIXaTFPZGFzNkRFZWJjak1jUHVPbWptUXM
**Elapsed:** 365s

---

# Research Bench Templates for Open-Ended Learning and Architecture Search

The disciplines of open-ended learning, autocurricula, population-based training, neural architecture search, and meta-learning present unique challenges for static computational benches because they inherently rely on dynamic populations, emergent interactions, and continuous task distributions [cite: 1, 2]. While standard reinforcement learning might target a single predefined environment, methods like POET endlessly generate novel environmental challenges alongside their solutions [cite: 3, 4], and multi-agent autocurricula produce emergent skills like tool use through competitive self-play rather than explicit reward design [cite: 5, 6]. Similarly, neural architecture search algorithms query massive predefined spaces of graph topologies to optimize performance without prohibitive training costs [cite: 7, 8], and meta-learning models are explicitly trained across diverse task distributions to enable few-shot adaptation [cite: 9, 10]. Implementing these methods on the current bench requires either proposing new executor kinds that encapsulate their complex internal logic or identifying the precise missing capabilities—such as population state tracking and cross-repeat aggregation—that block their native execution [cite: 11, 12]. The following templates and expansion requests formally define the smallest characteristic experiments for each field and the minimal architectural changes needed to unblock them.

BEGIN_TEMPLATE
{
  "template_id": "poet_paired_coevolution.v0",
  "kind": "poet_loop_v0",
  "param_space": {
    "num_environments": {"choices": [cite: 11, 13, 14]},
    "transfer_interval": {"int_range": [cite: 15]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "POET / Open-Ended Learning",
    "reference": "Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions (Wang et al. 2019)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "POET confronts open-endedness by evolving a population of diverse environmental challenges while collectively optimizing neural network agents to solve them, leveraging transfer learning between environments as stepping stones. This template tests if cross-environment transfers yield higher final scores than isolated training. A SURVIVED verdict would prove that paired co-evolution improves optimization on this specific set of environments, but it would not license the claim that the algorithm is capable of endlessly generating complexity without bound, as the bench's bounded evaluation budget cannot prove true open-endedness."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: POET / Open-Ended Learning
LACKS: The ability to maintain, evaluate, and selectively update a population of distinct, interacting entities concurrently across repeats.
WHY: POET, Autocurricula, and PBT all fundamentally require managing a diverse population (paired environments and agents, competing policies, or hyperparameter workers) that interact or transfer knowledge over time. The bench's current state constraint allows only a single deterministic walk to carry state forward, meaning there is no workaround to simulate the evolutionary pressures, self-play competition, or worker replacement mechanisms central to these methods.
SMALLEST_FORM: A new specification field 'population_size' taking an integer, which spins up an array of independent stateful contexts for the executor and returns an array of distinct results rather than a single scalar.
BLOCKS: POET / Open-Ended Learning, Autocurricula, Population-Based Training
EVIDENCE: The Paired Open-Ended Trailblazer (POET) requires co-evolving an archive of paired environments and agents [cite: 4, 16]; multi-agent autocurricula require multiple interacting agents to drive emergent strategy [cite: 5, 13]; and Population Based Training requires a population of workers to exploit and explore hyperparameter schedules [cite: 2, 17].
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "hide_and_seek_autocurriculum.v0",
  "kind": "multi_agent_competition_v0",
  "param_space": {
    "num_hiders": {"choices": [cite: 1, 5, 18]},
    "num_seekers": {"choices": [cite: 1, 5, 18]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Autocurricula",
    "reference": "Emergent Tool Use From Multi-Agent Autocurricula (Baker et al. 2019)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "In multi-agent autocurricula, agents create a self-supervised curriculum through competition, leading to emergent strategies such as tool use without external task design. This template measures whether increasing the number of agents induces a higher rate of strategy shifts (phases) compared to a single-agent baseline. A SURVIVED verdict would confirm that competition drives strategic adaptation in this specific setting, but it would not license the assumption that these emergent skills transfer zero-shot to entirely unrelated domains or human-relevant tasks."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "pbt_hyperparam_schedule.v0",
  "kind": "pbt_optimize_v0",
  "param_space": {
    "population_size": {"choices": [cite: 12, 15]},
    "exploit_explore_freq": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Population-Based Training",
    "reference": "Population Based Training of Neural Networks (Jaderberg et al. 2017)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "PBT jointly optimizes network weights and hyperparameters by training a population of models and periodically replacing poor performers with mutated copies of strong performers, discovering dynamic hyperparameter schedules. This template tests whether the dynamic schedule achieves a target performance threshold faster than a random search baseline. A SURVIVED verdict would indicate that the adaptive mutation strategy accelerates convergence here, but it would not license the conclusion that the specific discovered hyperparameter schedule is optimal or transferable to different neural network architectures."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "nas_bench_evaluation.v0",
  "kind": "nas_search_v0",
  "param_space": {
    "search_algorithm": {"choices": ["random_search", "regularized_evolution"]},
    "query_budget": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Neural Architecture Search",
    "reference": "NAS-Bench-101: Towards Reproducible Neural Architecture Search (Ying et al. 2019)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Neural Architecture Search aims to algorithmically discover high-performing neural network topologies, often evaluated using reproducible tabular benchmarks to avoid prohibitive compute costs. This template asks whether an advanced search algorithm like regularized evolution can find an architecture exceeding a specific accuracy threshold within a strict evaluation budget. A SURVIVED verdict would demonstrate the search algorithm's efficiency on this surrogate benchmark, but it would not license the inference that the chosen algorithm will scale to larger, more complex search spaces without pre-computed weights."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Neural Architecture Search
LACKS: An outcome rule capable of aggregation and comparison across multiple repeats, such as finding the maximum value over a search trajectory.
WHY: Neural Architecture Search algorithms explore a vast space of configurations, evaluating many architectures sequentially or in parallel to find the best one. Because the bench's current outcome rule can only evaluate a single scalar from a single result, there is no way to express a verdict on whether the best architecture found during a multi-repeat search successfully exceeded a target baseline.
SMALLEST_FORM: An expansion to the 'outcome_rule' allowing an aggregation operator (such as 'max' or 'mean') to be applied to a specific result field across all repeats before the scalar comparison is evaluated.
BLOCKS: Neural Architecture Search
EVIDENCE: The NAS-Bench-101 dataset (Ying et al. 2019) benchmarks search algorithms by analyzing the maximum validation accuracy achieved across a budget of thousands of architecture queries [cite: 7, 11].
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "maml_few_shot.v0",
  "kind": "maml_adapt_v0",
  "param_space": {
    "inner_gradient_steps": {"int_range": [cite: 1, 15]},
    "inner_learning_rate": {"choices": [0.001, 0.01, 0.1]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Meta-Learning",
    "reference": "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks (Finn et al. 2017)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Model-Agnostic Meta-Learning optimizes a model's initialization so that it can be quickly fine-tuned to new tasks with only a few gradient steps. This template tests if the meta-learned initialization achieves a target accuracy on a held-out task after the specified number of inner gradient steps. A SURVIVED verdict would confirm that the parameters successfully adapted to the new task within the few-shot constraint, but it would not license the claim that the model learned a universally adaptable representation that is immune to catastrophic forgetting on out-of-distribution tasks."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Meta-Learning
LACKS: The ability to specify and draw from a predefined distribution of distinct worlds (tasks) within a single specification.
WHY: Meta-learning methods explicitly optimize for fast adaptation across a variety of learning tasks, fundamentally requiring a meta-training phase on a broad task distribution and a meta-testing phase on held-out tasks. The bench currently restricts each specification to exactly one world (a single seed root), making it impossible to evaluate generalization across a diverse family of tasks.
SMALLEST_FORM: A modification to the 'world' object to accept a 'seed_roots' array and a 'distribution_type' string, providing the executor with a structured set of multiple tasks to iterate over during training and testing.
BLOCKS: Meta-Learning
EVIDENCE: Model-Agnostic Meta-Learning (Finn et al. 2017) trains models such that a small number of gradient steps on a new, unseen task drawn from a broader distribution produces good generalization performance [cite: 9, 19].
END_EXPANSION

**Sources:**
1. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzpM_tNHr65tizlMK8uyMZfcF_tO4l9yFSv_EzuWdvLByV1YVhf6CBUP0BK-INTI9cPZCEcC65z92d86lvNw-RiCZJcYLkihw-_B3SO98oun0OR3PifYiB3WPl3N23GAhlBhLqLdljUadouC1L45rJNKTNya10DGNaZTLdaJL_cHarO_zwhwOuY7DPIKKxtscwInVbFR8PVHuIOWf-Z7sXlEC82yO5KYgHhjayXKsBeCDSsgRRuBOgvxjYALUoQZoqXAGi_OrRbOOh)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoEy9IppN37GbQnCt4OyfG2UwLs20F2ujNs3TnEW44hOOZKs1YldNuWaBn6v0aPOHqqesmab17eZInaRRwuQ0m9QDl6NAkKq2LjxiK5DwNTyKlcVbkC50pbg==)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrAJLGEQbCmNiUttSTzH84Ur3Eh6XjV8N8CT3PLFoZye0tDBDokS-cy78zLXa2uXRCjFhwc0l1FHZZBIaAQ9PUh6WfAZUlI8NAR1iC9Yika358iGfn4yUC2Jp1JZ-H2k9dFAbwhh3smlGzKZfXk25uxhvsGubHfNpIqbm4ihTZUlv8DYDOEMWasoT-MNMh9xxqES44DREqApxcNAAKCCpUpv3sgTbNPG3XaPmUxPwsv6d0XKdCuKmIFcVdtrt7iYf0r1g_x0Y2)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm5EJ_oeEEKhoBZW9GoIOLIdj1E-MCj03st0ymm9yva0xlHvKvM5Qh3nVlFU5sm0Ev6ZXqnzoeI5tRHqrrorc3AhOTJcjgAXUFcaoA1KTaosPq2entYq2vIQ==)
5. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPlDZoTK73daSBnvHArpO_qDvG5zoF53sq5UfxAPeznIqqevuBMHbyJW--V8GCeJDQfxaxa026dz5VH6jqxM7Nu4b9Zy0dH6OLWb3dRxzRpuy0FPJzUjWGPxmbt1G5)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpQif5hh0zLVgpZ6ufjRsEG_4ouekd04sgZqupC19MAtGtmOwsz0qvkH5--K3BQm2Hj6d6ogXHZqLQOTWkgyr6z_yHsd2f_KbSMVCaqPuhr0_vrg==)
7. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEawZ5vitfiV_xRVJqzH1HFImjyaK48VQmx-nHjRuH6g8riOJreSkUwXj8mSlJy0CO8UvohFE_CEpyaGWVBKqbup2K5WVAJYjND1ObDLVwfsu-p0DWYbglZ6u-GpnfMsFvuw8wS)
8. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGXxwJBhrL_9YI6e-tLqlIJ3dLE_Tmzl-KZ3nmK8e7kdYljn-r5fIS3eXXzSb_8D-qe201gMRWuqmxB2lFaPMjcMUf5lhCAyIr7VG6OuSJHhPH46VIPD6Phwap7g==)
9. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMc5XFPPD_bhsxiMkdVXWnopWGnHIUpYyaomkNL-Tn3RvCZTdkXalhUwB9zuTTuqe3MMWDtyPDROURuAXukQa5tSarFb33-BIyRVJ4jmxGhx5mhEEeNzmTadCFlt_ZiA9sHrUl)
10. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTTNrHEUt9L9zcmA_NssjYgw_gQOyf1g0wxh1Idi6p6_7bWsCAxK9GauS-bvJkwzTKZgXFG8FSLh-f1CNqVWNdkI7w01QImVZeS11dnAArlwh9ucAHp9Z-SZsDn6zNKsmF59Cd9bK5-3BG49u74gbKQ7fwKvTKCNwjvMCbMdaWqcEWZBHVWzr0bJZDuoiKKCV2R6I7H57CLptBm27VuujysTaMhAi2Gf8KZWm9-ZZ8OWYSVGAxHRjzuqxw65clugzwYvhwiw==)
11. [automl.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCUYUMMGfLPLA1KMNFY8HlbZKcjbMHJa1vHGWLeHAHD2kHaZtKetsgaSp5pMdnPOI7uHwV3LGNstM8otVIUtiT7J4mqyTHnzfCRsVvD0X2wDvXh0PqRPpp1cyyDWIkauI6YO0aFcNwhp_LGkV1-2buubchlY26Cee6pfgJsRaIhBOqS3IdeJboXsEv)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqqe1a-nOTWjaf-tzN8Ctaxsk7za9OHDV7FXYK5F_el_SU-8h5Zvv6pF0nSfXZMGzRGaWRNGXzOZ2NPTCrXQrYrTNoHA7oMvEzE_VtSQyFBqr_G9KbcA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkUYtAQDLADQFoL4a8sktQ2NQqkbwnJFSjgUKyNEbQTY7-mZP7NAAyXCHwg8EiD57pqUFhiyLSH8iV3fv7u3C109xUQOW1gpsJFL7T06Gf7ZDUV6EZvQ==)
14. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETdyaJkvbEHKukVqi4Y8ewH5fltxV5yu2H3KudrGtMJqQr9_B98uPQXmPfXNmL1pUxEIQb8UOOGH9xgXOATZCgBFnEze_1vDUlCvLRrwdQu4x7vzfYa7QvfDiX)
15. [instadeep.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy6IibYiHHS7CJ_T1aVD2CV5xP9onGa0Nu8J9c5z8Bl2Dhpa615rVZZgyWUW4KqS7RPMGmg03btjcP-CLLuNUIrEJpjUMy0zMQ5Er_g1EWFPRquZ-FcPOUsFAnKiH7W0wHr769V4CLuaMgxj8uBFRes7wX4XQvhghrRKGLjQ==)
16. [uber.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmU2zwVKqIvunIlL8eBF0t4_IlMoHFbxQj-jeEdJTE0j6DJ0cKIMJ-S0vgYkaHJW4MvLNtDplm9hrSWbMUA6w6OULC9XBsiey8IF8mlOm_wiQqKk91Nzn8on2aZrUI6PFH1c78oI8DqtLZVmUJ3Oug2tOqlg==)
17. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8vkLeKEpvnDnXkrLOqHz-r5P6QpM7_taf1amoFk0wIvmIYEeDXcCZxhB3dZ4YsnUhyFA59b80DDfNn_ys8-8X0-P7dojos8rDkXHPO2uGkGnnXpEs7qWm15w9_7iLsYB5bIhf6fDgdlm_ySeI4TErTpqN4wAy0uDWhbje89PuEw==)
18. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG95vp_6lKX-NX8Tuw-DOMQTh1tPASEZHVdKOoC3EKWFTV1hqZeVTzow4W1cLmqpP7eyh3CM_QCum3GdO3-R2igtLSYO9AVZHklZsEsrm-dQMezKJpxLUiN97wwJ3yjHxLoapjOwFgNE1IugKMpDe56uU8d53m79-mp7Tc7FT31yQshmNwfny83XMi8Y5esUgUZVeaiE5FthPMmFO2JmEyS6j9X)
19. [mohansrirama.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfw4OGLX6J8VtvGoC5SO70nppI27pSYFseeVZohLbbgj3ePnuVsPEF4ISyuKMRFNhQ6q8wW9UBcQ2AbI27QtTRu69fz2D0md5P9-calmweqaoIQy1NiSlFQ8DpuO0=)

