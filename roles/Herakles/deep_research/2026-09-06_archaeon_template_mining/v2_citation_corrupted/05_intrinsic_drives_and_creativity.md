# Prompt 05: Intrinsic drives and creativity

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpMU9kYXY2VkVjMlVfdU1QX0xtcW1BWRIXaTFPZGF2NlZFYzJVX3VNUF9MbXFtQVk
**Elapsed:** 334s

---

# Operationalizing Intrinsic Drives and Creativity on a Computational Research Bench

Research into computational intrinsic drives suggests that autonomous exploration, unguided by extrinsic rewards, is fundamental to bootstrapping complex agent behaviors and avoiding deception in open-ended search [cite: 1, 2]. The current computational bench architecture, however, is heavily constrained: it relies on isolated, stateless bitstring evaluations and deterministic 1D walks, with verdicts restricted to single-scalar comparisons against fixed values [cite: 3, 4]. It seems likely that translating the foundational literature of intrinsic motivation, artificial curiosity, empowerment, and computational creativity to this environment requires targeted architectural expansions. Specifically, the bench critically lacks stateful, interactive Markov Decision Process (MDP) environments and the capacity for multi-arm comparative evaluations [cite: 3, 5, 6]. 

The following sections define the design parameters required to port the smallest characteristic experiments from five target disciplines onto the bench, utilizing the requested template and expansion structures.

## Intrinsic Motivation

Intrinsic motivation in developmental robotics heavily focuses on mechanisms that drive an agent to explore situations where it maximizes its empirical learning progress. The hallmark implementation is the Intelligent Adaptive Curiosity (IAC) system [cite: 1]. IAC segments sensorimotor spaces and focuses the agent on regions that are neither too predictable nor too random, leading to an emergent, stage-like developmental trajectory [cite: 7, 8]. Because the current bench lacks an interactive sensorimotor environment, this experiment necessitates a new executor kind to evaluate learning progress over variable state dimensions.

BEGIN_TEMPLATE
{
  "template_id": "intrinsic.v0",
  "kind": "iac_exploration.v0",
  "param_space": {
    "sensor_dim": {"int_range": [cite: 9, 10]},
    "learning_rate": {"choices": [0.01, 0.05, 0.1]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Intrinsic Motivation",
    "reference": "Oudeyer, Kaplan, and Hafner 2007: Intrinsic Motivation Systems for Autonomous Mental Development",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Evaluates the Intelligent Adaptive Curiosity algorithm's ability to self-organize developmental trajectories. The field would run this to observe agents transitioning autonomously from simple to complex sensorimotor tasks based on empirical learning progress. A SURVIVED verdict would license the claim that the specified learning rate successfully differentiates task complexity to create an exploration curriculum, but it would NOT license the claim that the algorithm is sample-efficient in unbounded continuous spaces or avoids catastrophic forgetting."
}
END_TEMPLATE

## Curiosity-Driven Exploration

Curiosity-driven exploration extends classical count-based exploration into non-tabular, high-dimensional spaces by deriving "pseudo-counts" from sequential density models [cite: 3, 9]. This approach measures the agent's uncertainty and assigns exploration bonuses based on the recoding probability of an observed state [cite: 9, 11]. A characteristic experiment evaluates whether these pseudo-counts accurately drive an agent to resolve uncertainty in environments where traditional myopic exploration fails. 

BEGIN_TEMPLATE
{
  "template_id": "curiosity.v0",
  "kind": "pseudo_count_exploration.v0",
  "param_space": {
    "density_model": {"choices": ["cts", "pixelcnn"]},
    "bonus_scale": {"int_range": [cite: 3, 10]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Curiosity-Driven Exploration",
    "reference": "Bellemare et al. 2016: Unifying Count-Based Exploration and Intrinsic Motivation",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Measures whether pseudo-counts derived from sequential density models successfully drive exploration in non-tabular environments. The field would run this to verify theoretical bounds on information gain when mapping complex state spaces to exploration bonuses. A SURVIVED verdict would license the claim that the chosen bonus scale reduces uncertainty in the specified model representation, but it would NOT license the claim that the pseudo-counts perfectly approximate true state visitation frequencies in highly stochastic domains."
}
END_TEMPLATE

## Artificial Curiosity

The earliest rigorous formulations of artificial curiosity propose a dual-network architecture: a controller network that dictates actions and a model network that predicts environmental dynamics [cite: 6, 12]. The controller receives a delayed reinforcement signal for actions that increase the model's predictive knowledge, implementing dynamic curiosity and boredom [cite: 6, 13]. The characteristic experiment isolates this heterostatic drive to test if the controller successfully escapes static equilibria.

BEGIN_TEMPLATE
{
  "template_id": "artificial_curiosity.v0",
  "kind": "model_building_controller.v0",
  "param_space": {
    "hidden_units": {"int_range": [cite: 1]},
    "delayed_reward_steps": {"choices": [cite: 10, 14, 15]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Artificial Curiosity",
    "reference": "Schmidhuber 1991: A possibility for implementing curiosity and boredom in model-building neural controllers",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Implements a dual-network architecture where a controller network maximizes the prediction error of a model network, simulating heterostatic motivation. The field would run this to study the emergence of dynamic curiosity and boredom as the model learns. A SURVIVED verdict would license the claim that the controller successfully escapes static equilibria by seeking novel inputs, but it would NOT license the claim that this mechanism prevents the agent from being permanently trapped by highly unpredictable white noise."
}
END_TEMPLATE

## Empowerment

Empowerment is defined as an intrinsic, universal, task-independent utility function that quantifies an agent's control over its environment [cite: 5, 16]. It is formally calculated as the maximum mutual information (channel capacity) between an agent's potential actions and the resulting future states [cite: 17, 18]. Evaluating this requires testing whether calculating empowerment over a specific lookahead horizon correctly guides an agent toward states with maximum available options.

BEGIN_TEMPLATE
{
  "template_id": "empowerment.v0",
  "kind": "channel_capacity_evaluator.v0",
  "param_space": {
    "lookahead_horizon": {"int_range": [cite: 3, 14]},
    "actuator_bits": {"choices": [cite: 9, 19, 20]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Empowerment",
    "reference": "Klyubin, Polani, and Nehaniv 2005: Empowerment: A Universal Agent-Centric Measure of Control",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Calculates the maximum mutual information between an agent's sequence of actions and future environmental states to establish an intrinsic utility function. The field would run this to determine if empowerment landscapes naturally guide agents toward states maximizing future options. A SURVIVED verdict would license the claim that local empowerment calculation correctly identifies maximum-control states within the lookahead horizon, but it would NOT license the claim that this metric alone can solve complex, sparse-reward tasks without external guidance."
}
END_TEMPLATE

## Computational Creativity

Computational creativity, particularly through the lens of Novelty Search, addresses the problem of deception in objective-based optimization [cite: 2, 4]. Rather than optimizing for a specific goal, the algorithm searches purely for behavioral novelty, maintaining an archive of past behaviors and computing distance metrics (typically k-nearest neighbors) to encourage complexification [cite: 2]. 

BEGIN_TEMPLATE
{
  "template_id": "creativity.v0",
  "kind": "novelty_search.v0",
  "param_space": {
    "archive_size": {"int_range": },
    "k_nearest": {"choices": [cite: 10, 14, 21]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Computational Creativity",
    "reference": "Lehman and Stanley 2008: Exploiting Open-Endedness to Solve Problems Through the Search for Novelty",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Executes a divergent evolutionary search driven purely by behavioral novelty rather than objective fitness. The field would run this to bypass deception in complex search spaces where intermediate steps do not resemble the final goal. A SURVIVED verdict would license the claim that measuring behavioral distance via the specified nearest-neighbor parameters successfully generates increasing complexity, but it would NOT license the claim that the search will efficiently converge on a specific functional objective in bounded spaces."
}
END_TEMPLATE

## Expansion Requests and Architectural Deficiencies

Translating the characteristic experiments of these fields to the bench requires bridging profound architectural gaps. Intrinsic motivation, artificial curiosity, and empowerment fundamentally require an agent to perceive the consequences of its actions to update internal state models [cite: 1, 6, 16]. The bench currently provides a deterministic 1D walk and a stateless bitstring scorer, completely lacking a closed-loop interactive environment. Furthermore, proving the efficacy of novelty search relies upon directly comparing its performance against objective-based baselines [cite: 2], which violates the bench's single-scalar outcome limitation.

BEGIN_EXPANSION
FIELD: Intrinsic Motivation
LACKS: An interactive sequential decision-making loop (MDP) where payloads can emit actions and receive subsequent state observations over multiple timesteps.
WHY: Intrinsic drives mathematically depend on an agent perceiving the consequence of its actions to compute learning progress, pseudo-counts, or prediction errors. The current deterministic 1D walk does not accept action inputs, and the bitstring evaluator is stateless, meaning no workaround on the current bench can faithfully simulate autonomous environmental exploration.
SMALLEST_FORM: A new stateful executor kind grid_mdp_v0 taking parameters grid_size and episode_length, exposing a step interface for an agent to submit an action and receive a state, and returning an array of visited states in the final result.
BLOCKS: Curiosity-Driven Exploration, Artificial Curiosity, Empowerment
EVIDENCE: Oudeyer et al. 2007 (Intelligent Adaptive Curiosity) relies on action-driven state transitions to measure learning progress; Bellemare et al. 2016 requires a sequential density model over states generated by active agent policies.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Computational Creativity
LACKS: A comparative outcome rule evaluating statistics between two distinct experimental payload arms.
WHY: Novelty search's fundamental theoretical claim is that abandoning the objective function outperforms objective-based search in deceptive domains. Because the current bench outcome rule is strictly limited to a single scalar comparison of one run against a static value, there is no way to mathematically express or falsify a hypothesis comparing two methods.
SMALLEST_FORM: An outcome rule operator GREATER_THAN_ARM that compares a specific scalar field from the result of the current specification against the same field in the result of a paired baseline specification.
BLOCKS: Intrinsic Motivation, Curiosity-Driven Exploration
EVIDENCE: Lehman and Stanley 2008 explicitly validate novelty search by plotting its maze-solving efficacy (nodes visited, evaluations to solution) directly against a baseline fitness-based NEAT algorithm.
END_EXPANSION

**Sources:**
1. [southampton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO7keuKVw_8tj8H8aQfghDwFXlBCyKGyrkGysBupuncvBDfkxnMC4aUEObKkO79hn-WpeVOCF1gsEf66YpXz5w6XdSIu3_v5bncxfijCHidklrX_2kU5wVgGX3y25dJAWb7_APJ-Gdwbrl-4J1VEGC5ECsb2wewgQU)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGE3CKhOVPOf9-a9_YSkc9ePr-DO5UAr2yyxv4IOrUzwpoj7beM6FNBUoVtnFtY-Aokht4BKfDL7JrEriqXM-W9cJCvlNhg_OZrs8WIWAO3QxYiW5hyzJ39zqm_uBVSt6sFgzEHGTD5CbzY6gkNvcwoPXisjlPemVYvsS_iNri_JSi2G38URCgjwiwPZ0WmdttkR3tfMVF16KAuC6UXOWrEG69USzGIjSysCNhObL2jVq1fkQ==)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1QnRpI6cFB9ZbjH_4drnNu1nRW_AUZ_eGknJNSGUZpAgNsFQOst8op3N47tqsLUiXm28y8SxA4fyj80jpe_utVY_tEx9m-IwEVGu0IjySA5HCVqpcPV7dNbP66rVWm8D5inzms-MWalTP-I4JEXEg_E_GsZsq38RkGtihDiNRQQxGlbBmIyY5Z0YqSCjEidVjXEQGECjZNawvk9l6-niIk7mpJmMuOaeXUdgNuIdi2C5gYKSwkLpmj4zA7gxsHwQn91r1rhF-zpM=)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnxtvASBFbn_4TKTDjzZVc5aCliTw51TnmyjaULcV_2uNTwUns-rSBtQJLxvf-KoYW-GoWL9oMyyOq7d0Xmpe2UiKuX8XVEe89bretqCg19lqUxKb7LSc0unP99Vv3XuNPzpDEHr6NRoQLNNMQNKg_dzWRcHX-qX8aM-l-UtFrjJhDk_8yOIb6XipNmVyvC1wR-YSHH-ltMuyPxSxwR6JuG4S4r2bduKX7wtJvFdWj_01dOOqq18Lvo2QhhA2CR04Jd9FwNVQ72g==)
5. [herts.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwivjb70vGst7vw05dIWj-wM9Jy6NnhH6tlkmxksHACAb37pjGH0mWwqbyzrXF4EOfyB5XpKVEzltMuO0c5K2zLGU0lhXgHGse3N3DU4Wqw--HP4i6nIk8CIo-VkT1Preimdin2_lKZ1nxh9OeuhsL9RSKma9SobhJuD1Lhi_s3YQuiYoAd2gO0MofvIZaV6KLu3m9gq62XFH5xVDjG17hkillFw==)
6. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-BN8WvIlOowdJwJNnuY6qnj9RrUwe32mH-iZG97dorVSuAI0OS_zkDA8wpVBVHRDRqcbdLYy0KAtCmCNVpTRU4x61REFatHlPul1eC6GmuqCvqjzHfrrkA9WqXvxcOkJuUC6ztRHyDmIanpt8nnA88f0-uU4fU5KH2tztLGPiz2LTO7CLeLj3xGk5HteipCJX6adM3PjvZUfe550hFvZGHW0jIgr_vMJ6eD1UQtmf2kMnP1VG142KIHPUyuT5NfEX)
7. [inria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp0AgNFScRvDE6FYyrktSwlSQUjwSj2miSuHGzVx1z8nemiURfODg6_PJesrKYi3SFduJ2x3ZmY6JWj2-vsSbgxTMpmICDg9Vr3rwXhyli5QPR__bVDO7atsbnwE8qYw==)
8. [pyoudeyer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc8EfPGd-86SzhHaOgPepJJMcr0aTUL_GytUTUD_ZJpimN0S7XGunJBmwUIepVDKef6Zxpwxuf5R3cRRODrrPi2oBUJ1KWZEn3T1FDdnBC12PP4Ce2EA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTp9KMkhp9NAvEgTD5Cizkzt6m3JnNpa7FaTQHA2VnESwnqPeb8O8t_BGpw7mvuTadI1abRgyOLpy5QgPhdm6bXtv3RW1uYXtu9JC-Zgf2JsTdZ3zoyd8t3g==)
10. [mxcog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzmaqECnvCCvE-TlEdddubUtHPXlwbMHNILbtj5svDYV2LgIB29TGYdABsi2K49TrlhipGMh56XxlxistUA2S1cOmXNsdnfIRbiTzjIEqaBhnDRbNwM3wImGj7VF0E_30w)
11. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvrDovTPpBbj6xzyuX2MJalwAJjGw52cSgtXBkqduYWBvLje6CAjEakCxMeqxk30MXXgSJPC8tU88WfWxDU11IL_v9eKwio5VKxKRdLJjFqEd4TPMM0LXnE8e7_kZR11mf6a29MvWw4FMgaFI=)
12. [idsia.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdzrhMrjn7N8J2NQaGWBU1fKN9CzNCALxwytRIsoVoUNi1jc9p7Vt9SBGmQh4vI0RxIgwJC1EPgB-dTUZ-43z8AmYjgg2qnzM7NJOH3MYoczD6cwNv5IZkWHvnuAA2UeQZB2zZPEW7aKDCnzQClNlEB0mfv3Q=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4xSbxjKmj91Du2jc10MvzG9z0sKTgNim7mCs85QmZq3tGib8g6VyjZqpn3I7PgxBc5f3bUW-MT_65Uw0huH8kkBwuzytxUw74_McY4sIU6bru_HD-WgoNmw==)
14. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfNSC2EKDp04nEG9bUfB6tLxCMZF2NRt5PRZlTX3ldUJqg5JO4j502FU0m3ZR1e7koKNJSe7suxzQqHfJgrp72g8r1nuNj36qGtW2zJLIBlpOuuKRq6VP319TJVXf3y-eX37MZYtY8w0fNLZXiECXd)
15. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkbNXNc-OdbuhWtLMzrt4zNJDDiD61ctUpScXyxi0lRhcyrIYus1vSnshaodO61TXUJTzf0VbJvJ7d6OVc3vLhxlFV7vhmXMx3wKNnX95sgWjAVo5CSvhkjtfvyxlXYqRWgHjUsTyQeY_q3IP_XDkMVWc=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAn8j7hpFtZARhtiGa5QokcJIoObR99RANQ1RD9VO9Lwjqf1EUIJdDOngThhW9o8DzShRjw2sFSgsT8c3I-xJn4r3gp5hmcvTSUjbUwZPAr7b8tCXwEu9fmww1rMYCAxqINfllhFTu3xmztCHgMi3U_9q1Tg1xt7yG1eiHpIx40kgZTnoktiIa_FQZLz2FEBP5Djc65InFE5XPMO8dq2c=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEh_BnPTD7iXqfo-50PZqjPr8JzfxSu1LSWocsR8mvtWxusNVqSoWeqBFmHl-Ix8SEiOEOwn81rkA5wRZa90s2k7rJ58LaPiZubbLYFW-Qr-cQuaWD1zZJ)
18. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGDCIcAkRXIH0GHQMfdQJ8wHiP5KjRI2UHMQ_goF1ByX1c8F25xlAsGc0_THOXajP0SdUmCXVepxQN_JfaOIrEdasyUJoUbSRCaBfhAf81NwwV8XcknzSPmBL0fIM=)
19. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrh16c3ZseZhgM9-GfIccDyvMxb1JbcG5iEXhzN9-AgNMzV5FTHtKk4-HJfqbeuzwLWf9zs7SBVz6JMO18_SsEnqi4syZeDp0xmwAYVmSAxkg4eC4kffHo2t9-_RK0jJFAodu95tk92GWtNtLK2fV50WcV4A9eATwrydZjRAGgUxYtytxqBFAH-gLE9_0plN1-YYl750K2Bic_hKml)
20. [alignmentforum.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtPFLc4ln2GZdciprvV1F-bdac4ykti4UdtHU0BubmokO-iUFw0wCiefX1OxDyaN5wwvb59zqsyHUtzOQ7MjqQY3j6ddekwouIjnJuT1Hr2Q2siUIQzAEHZ2LqOWsbSRP5PCdcfcnxhXVn5Aef4kPiZ6LCrhEKXUFV89xw6b_x_MS9lUC9DeNcU23UPS3v)
21. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHb5tbWLLj_7TGnn5XSBE7otF7NYYOzcne_8g70A5ow-UkaBaSCsAeONiRS8RdpxvN3HL1O7yFNRD9qXFcIBHL1TRl7QmQ6cL0OR7U88xb5x3Os3CSA7-OIHXqfVrEmC1M8ltAn_YNCQxbzvupLr20dX3iwiaHXnrDLMOJBkqkY5gJjf099Q7BqOfBdcEbbl3TaRJR8cxsA)

