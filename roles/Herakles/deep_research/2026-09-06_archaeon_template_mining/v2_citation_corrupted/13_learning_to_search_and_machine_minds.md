# Prompt 13: Learning to search, and machine minds

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd1VmVkYXFHd0QtQ2JfdU1QaWN1TzZBRRIXdVZlZGFxR3dELUNiX3VNUGljdU82QUU
**Elapsed:** 364s

---

# Experimental Design Templates for Computational Intelligence and Search

* Research suggests that mapping advanced paradigms like Artificial General Intelligence (AGI) and ALife to rigid computational benches requires bridging significant structural gaps [cite: 1, 2].
* It seems likely that existing single-state, non-interactive execution constraints fundamentally block characteristic experiments in Learning-to-Search and Darwinian Neurodynamics without adding environment interaction loops or population persistence [cite: 3, 4].

The fields of Learning-to-Search, Learning-to-Optimize, AGI, ALife, and Darwinian Neurodynamics represent diverse computational paradigms spanning imitation learning to simulated evolution [cite: 5, 6, 7]. Because the current bench supports only atomic, single-state executions—lacking sequential interaction loops, differentiable loss surfaces, or population mechanics—all five fields require the admission of new executor kinds to run their smallest honest experiments. The templates below define these novel executors in strict accordance with the literature, followed by expansion requests detailing the specific architectural capabilities the bench lacks to support them [cite: 8, 9, 10].

BEGIN_TEMPLATE
{
  "template_id": "l2s.dagger.v0",
  "kind": "l2s_dagger_v0",
  "param_space": {
    "trajectory_length": {"int_range": [cite: 11]},
    "oracle_probability": {"choices": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Learning-to-Search",
    "reference": "Ross, Gordon, and Bagnell (2011) A reduction of imitation learning and structured prediction to no-regret online learning.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Learning-to-Search treats structured prediction as a sequential decision problem. This characteristic experiment uses the DAgger algorithm to train a policy by rolling out trajectories and querying an expert oracle for corrections. A SURVIVED verdict based on test loss demonstrates the policy can successfully imitate the oracle on the specific training distribution, but it would NOT license the inference that the policy can improve upon a suboptimal reference policy, which would require an advanced algorithm like LOLS."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "l2o.meta.optimizer.v0",
  "kind": "meta_optimize_quadratic_v0",
  "param_space": {
    "matrix_dimensions": {"choices": [cite: 11]},
    "unroll_steps": {"int_range": [cite: 11]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Learning-to-Optimize",
    "reference": "Andrychowicz et al. (2016) Learning to learn by gradient descent by gradient descent.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Learning-to-Optimize replaces handcrafted update rules with trained neural models. The smallest characteristic experiment trains a coordinate-wise recurrent network to optimize a random 10-dimensional quadratic function over a set number of unrolled steps. A SURVIVED verdict indicates the learned optimizer outperforms a baseline on the specific quadratic function family it was trained on, but it would NOT license the claim that the optimizer generalizes to fundamentally different loss landscapes, such as deep non-convex neural networks or different activation functions."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "agi.mc.aixi.ctw.v0",
  "kind": "aixi_ctw_eval_v0",
  "param_space": {
    "horizon_depth": {"int_range": [cite: 3, 12]},
    "context_tree_depth": {"choices": [cite: 13, 14]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Artificial General Intelligence (AGI)",
    "reference": "Veness, Ng, Hutter, Uther, and Silver (2011) A Monte-Carlo AIXI Approximation.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This field studies agents that can achieve goals in wide ranges of unknown environments using theoretical models like Solomonoff induction. The characteristic experiment evaluates the computationally feasible MC-AIXI-CTW agent in a small partially observable Markov decision process, compressing interaction histories using Context Tree Weighting and planning via Monte Carlo Tree Search. A SURVIVED verdict shows the agent can learn and exploit short-term environmental dependencies to maximize reward, but it would NOT license claims that the agent is capable of human-level generalization or scaling to environments with massive state spaces."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "alife.tierra.soup.v0",
  "kind": "tierra_soup_v0",
  "param_space": {
    "memory_size": {"choices": },
    "mutation_rate": {"choices": [cite: 3, 5]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "ALife-Inspired AI",
    "reference": "Ray, T. S. (1991) An approach to the Synthesis of Life. Artificial Life II.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "ALife studies emergent complexity by simulating synthetic ecological dynamics. This classic experiment initiates a shared virtual memory soup with a single self-replicating ancestral program and allows mutations to occur during execution to observe competitive dynamics. A SURVIVED verdict based on the emergence of smaller, parasitic code sequences demonstrates basic host-parasite co-evolution, but it would NOT license the claim that the system exhibits unbounded open-ended evolution, as such systems typically reach a stabilization point where novelty ceases."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "neurodynamics.attractor.evo.v0",
  "kind": "attractor_evolution_v0",
  "param_space": {
    "population_size": {"int_range": [cite: 11]},
    "retrain_iterations": {"int_range": [cite: 3, 5]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Darwinian Neurodynamics",
    "reference": "Szilagyi, Zachar, Fedor, de Vladar, Szathmary (2017) Breeding novel solutions in the brain: A model of Darwinian neurodynamics.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This field tests the hypothesis that true evolutionary dynamics including multiplication and heredity occur in the brain to solve cognitive problems. The experiment simulates a population of recurrent attractor networks that generate binary pattern variants, select the fittest candidates, and retrain to search for a target solution. A SURVIVED verdict establishes that this evolutionary search algorithm is mathematically capable of finding a target pattern faster than purely selectionist search, but it would NOT license the physiological claim that the biological human brain actually implements this exact mechanism."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Learning-to-Search
LACKS: Sequential environment interaction interface.
WHY: Both Learning-to-Search and AGI require an agent to output an action and immediately receive a corresponding dynamic observation and reward based on that action, multiple times within a single execution block. The current bench only evaluates a static payload once and returns an outcome, offering no mechanism for an executor to pause, query a stateful world or oracle, and resume execution.
SMALLEST_FORM: An executor callback hook `yield_action(action)` that hashes the action with the current world state to return an observation integer and reward scalar, appending these interaction steps to a `trajectory` array in the final result.
BLOCKS: Learning-to-Search, Artificial General Intelligence (AGI)
EVIDENCE: DAgger (Ross et al., 2011) explicitly rolls out a trajectory by taking sequential actions and querying an interactive expert oracle for the correct action at each visited state; similarly, MC-AIXI-CTW (Veness et al., 2011) operates in standard discrete-time interaction cycles of action, observation, and reward.
END_EXPANSION

BEGIN_EXPANSION
FIELD: ALife-Inspired AI
LACKS: Population state persistence across repeats.
WHY: Simulating ecological dynamics or evolutionary breeding requires maintaining a diverse set of candidate entities (a population) that can interact, mutate, and be selected over successive generations. The bench currently limits state to a single deterministic walk or isolated seed roots, preventing the maintenance and generational updating of a shared pool of diverse candidate solutions.
SMALLEST_FORM: A persistent list of JSON objects `population_archive` in the repeat block state that executors can read from and write to across index increments, adding a `generation_index` tracking field to the result.
BLOCKS: ALife-Inspired AI, Darwinian Neurodynamics
EVIDENCE: The Tierra simulation (Ray, 1991) relies on a shared memory soup where multiple distinct digital organisms coexist, replicate, and compete for resources; Darwinian Neurodynamics (Szilagyi et al., 2017) explicitly maintains a population of multiple distinct attractor networks to implement heritable evolutionary variation.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Learning-to-Optimize
LACKS: Differentiable objective function.
WHY: Training a model to optimize another model requires computing gradients of a loss surface with respect to parameters to update the optimizer's state. The bench currently only evaluates discrete domains (bitstrings, integer walks) and lacks any mechanism to provide a continuous mathematical surface or return a gradient array.
SMALLEST_FORM: A lightweight continuous function (e.g., a quadratic surface derived from the seed_root) that provides a `.forward(params)` method returning a scalar loss and a `.backward()` method returning a gradient array, recorded in the result block.
BLOCKS: Learning-to-Optimize
EVIDENCE: Learning to learn by gradient descent by gradient descent (Andrychowicz et al., 2016) trains an LSTM meta-optimizer specifically by unrolling optimization steps and computing gradients via backpropagation through time on a base quadratic function.
END_EXPANSION

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFhCAbk2w-xlHpw_Q4AXJtNo6yoTaBKRhzYeOKaPiBlBzElMyY3plO3EeZz72T_NtrU6QNvtL6ryT4SeJQ6rVGxL-PjKx_xwIukYUj5kNOvQ-cLa7975lrnM-n0lmbsxd4WoHwKUfaz2SwJDSQ-pQB)
2. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRaLE3AfT8m1GCEiXVDYb2QHSGb5RxixLhWR-vfmJ5AFlCuSYUJ6jjtNGHKCqupFS-ODOGEzXmTsW3zti-5jQl6gSfzj1nQorpUPh2k7ln_VAyMqKU8hWK0ClrmjapWzQlvgbvRw-6AtiTOmc=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVWVEji36X_SGDmqOK-SWR1MeeByY0Dte0AjDszPuuqQGx00TRCr3vtc10lB41t_hTU9y_fhwtjQcrzVBfHUOGssOjYq0MK8gLN1Hv4oYCXHhsDbN3rw==)
4. [f1000research.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHERgarNl8Zsw2S_H1PDJhFqWr-P5ric7jje3bdsJpC72SScagxWvd5NUNeQa1Xsj1IbKl_n_n2toSRRX4aM-tw9-5Pck24ZPWCGW02pLohfX39nTdRM3_Vqx3_BEP3HA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_kjCmcjT67-p5MD9rx_1Y84QkzmPdHElAFB8gvuq2ZgXidMaCNfLDev6IEZOfQtw-e5mn1ZQaL02D9u82h90J7euo35HRa9HY33gj69UqL4d2UIfyl1oQLA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF06eoy_yPKuipHAI24UcY6vQgZZlmf0EF9H-4ZutwXbFomcjs1d7gkACJJXhqUTjW8_zeYNbZRw8S0wda_wjKTr0x4xbgVykpPaF-_AbSEkbyqXAjLwrNeCQ==)
7. [arn.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3KZNhMNuVL4ZPSKVd1Tatx6Qlk3lOD5NkkvDXf4_YBG9XA3w7NGGP9nmyELFURw0Zh3gJBujD_8UMHTfnZgW41sq9e3G56NFaY7tU9a-_49vf9hjYvdaxR61JESCcyMN-ami5ytlTAzt1)
8. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHozj-iizUkWPjpKmZhb5p-FWUcyCHOZXA_NxWjqx7wDqVwxdWOjriGC5zYIxV4V0Nlrb-xjlZpt74n9-QY0hkYuKGK5KlwFI1Woixp7aigtQGSOGM7P3vXDZeY6k8=)
9. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcOL5YyfUygOUauU55nAlMlERh14FxFz5CIkBYDpABAZj8Od3-lHVImnA1EKjx-VuSJCla4H5Y3KZW8Yeh6P2lXNbaFOEVufnJIdSyu98MsnFd_MWG0QTQF8NkIyuQWWNDkqw6tMFIvuF52oOtrFGp52k=)
10. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDO7B1D-J4sCftQwaEr42vjPd7w3A_pdU5p_CqATydhXqx2W8-KjJXyWAgDE7KeWVDtUdiZtFe-7TxrIC3mTVS0DxI5sFUoB2FeMiPI1xSr97-P_LKnK3HUjZLWGQwIC6euxVQn850V8rjwQHpTlMwOb0NdkLX)
11. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu_cHpUvDYkiVz_NPmaZLMSeKcUd8OqDdjaK17WddWby__B7YrtqBM-gB0LOb8VrvQRRQ18ztltchv3-pTRUAB0uP2ati7G8fSHvnrtplMDFmgNQPewHTMOkXCilKrszRh6z2NGsTxG8FZ-FJ5hTM4DkKVeMdd95q8k6drvL2PAG2yuXnTTUV0gGx-_4ppDp5xLeT38WzP)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvoXLlpNuZZeCBVXn52TRL7-dfewbwPoT29TrPfnxS4fBasLNLupnt1v84ZTyMTxt8rds1rPlnWn2ilvcG0V2WOrss7z6rmIpXk4dD-LrDdsvZ0NjcpdxB0A==)
13. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH62YBSrdsYRTvpWLsh1-1SN4qGYOxkX10YoQtl2ZQQDlJObNO7_JFaUpbKHyVMcQwKtu7kxnSSvlrbNt6igRTrr1amuflR1BkHTInQmf_7l97R7Mq991Ju6MjY23LDL_BIk8K2-U_1VlYV1KBEENZCZCSGxi9zi2Rd1XXBHUDAXyzSQ83tDtPMiQ==)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfD4shmg0PNqvRPyTRW5GtN42OzUqkS7h6-g3d_G0yOcfz8sReFF110qSItOdBKbsqVr9DceCXWefY3TzjSLiIMnVN-bBiEt0_NwSqZUODoikBcT9eybfIj6mKBZwItzKdCWvEgmgu)

