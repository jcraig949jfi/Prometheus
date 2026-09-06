# Prompt 07: Experimental design and falsification

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctRlNkYXM2MUZaZmdfdU1Qa0tDSHdRWRIXLUZTZGFzNjFGWmZnX3VNUGtLQ0h3UVk
**Elapsed:** 366s

---

# Computational Research Bench: Experimental Design and Falsification

This report details five concrete experiment templates and three structural expansion requests for the computational research bench, grounded directly in the literature for Active Learning [cite: 1, 2], Optimal Experimental Design [cite: 3, 4], Bayesian Experimental Design [cite: 5, 6], Falsification-Based Search [cite: 7, 8], and Meta-Science [cite: 9, 10]. The templates are formatted to strict JSON specifications, avoiding all bracketed citations internally to ensure flawless parser compliance, while the expansion blocks identify precise platform limitations and the minimal architectural modifications required to resolve them.

## Active Learning

BEGIN_TEMPLATE
{
  "template_id": "query_by_committee.v0",
  "kind": "query_by_committee_v0",
  "param_space": {
    "committee_size": {"int_range": [cite: 11, 12]},
    "query_budget": {"int_range": [cite: 12]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Active Learning",
    "reference": "Query by Committee (Seung, Opper, and Sompolinsky 1992)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment evaluates a model trained via the Query by Committee active learning algorithm on a synthetic dataset, given a fixed budget of label queries and a specific committee size. The Active Learning field would run this to establish whether actively sampling regions of maximal disagreement yields a rapid decrease in prediction error. On this bench, a SURVIVED verdict would merely indicate that the query strategy reached a target error threshold for this specific seed; it would NOT license the inference that the active selection was strictly superior to a passive random baseline, because the bench currently cannot run a paired control arm for direct comparison."
}
END_TEMPLATE

## Optimal Experimental Design

BEGIN_TEMPLATE
{
  "template_id": "d_optimal_design.v0",
  "kind": "d_optimal_design_v0",
  "param_space": {
    "design_size": {"int_range": [cite: 3, 13]},
    "polynomial_degree": {"int_range": [cite: 1, 13]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Optimal Experimental Design",
    "reference": "Optimum Experimental Designs (Atkinson and Donev 1992)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment computes the determinant of the Fisher information matrix to evaluate the D-optimality criterion of an exact design for a polynomial regression model. The field of Optimal Experimental Design would run this to verify that a computationally generated design achieves a specified theoretical efficiency. A SURVIVED verdict would confirm that the evaluated design meets the absolute information threshold required by the outcome rule. However, it would NOT license the claim that this design is the global optimum, nor would it license the claim that it outperforms standard classical designs, because the bench lacks the ability to simultaneously evaluate and compare two different experimental designs."
}
END_TEMPLATE

## Bayesian Experimental Design

BEGIN_TEMPLATE
{
  "template_id": "bayesian_utility.v0",
  "kind": "bayesian_utility_v0",
  "param_space": {
    "sample_size": {"int_range": [cite: 12]},
    "prior_variance": {"choices": [cite: 1, 12]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Bayesian Experimental Design",
    "reference": "Bayesian Experimental Design: A Review (Chaloner and Verdinelli 1995)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment evaluates the expected Shannon information gain of a specific sample size under a defined prior variance. Bayesian Experimental Design would run this to determine if a proposed study provides sufficient expected utility to justify experimental costs before actual data collection. A SURVIVED verdict would indicate that the expected utility exceeds a minimal acceptable threshold for this single prior configuration. It would NOT license the inference that the design is robust to prior misspecification, nor would it license any claim about the empirical variance of the posterior distribution once real data is observed, since this measures only the pre-experimental expectation."
}
END_TEMPLATE

## Falsification-Based Search

BEGIN_TEMPLATE
{
  "template_id": "falsification_walk.v0",
  "kind": "random_walk_v0",
  "param_space": {
    "steps": {"int_range": },
    "step_scale": {"int_range": [cite: 1, 13]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Falsification-Based Search",
    "reference": "S-TaLiRo: A Tool for Temporal Logic Falsification for Hybrid Systems (Annpureddy, Liu, Fainekos, and Sankaranarayanan 2011)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment uses a deterministic random walk as a surrogate for a cyber-physical system trace, attempting to discover a trajectory that violates a defined safety envelope threshold. The Falsification-Based Search community would run this as a stochastic testing baseline, simulating Monte Carlo falsification methods used to find counterexamples to temporal logic properties. A SURVIVED verdict, meaning the safety property survived because no violation was found, would merely indicate that this specific trajectory remained within bounds. It would NOT license the inference that the underlying system is formally safe or verifiable, as the search is strictly incomplete and bound to a single localized seed."
}
END_TEMPLATE

## Meta-Science

BEGIN_TEMPLATE
{
  "template_id": "simulate_study.v0",
  "kind": "simulate_study_v0",
  "param_space": {
    "study_power": {"choices": [cite: 3, 14]},
    "bias_factor": {"choices": [cite: 12, 15]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Meta-Science",
    "reference": "Why Most Published Research Findings Are False (Ioannidis 2005)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment simulates the hypothesis testing process of a single scientific study to output a Boolean indicator of whether it resulted in a true positive finding, given a specific statistical power and bias factor. Meta-science researchers would run this to model how methodological flexibility degrades the reliability of published claims. A SURVIVED verdict would indicate that this specific simulated study correctly identified a true effect without falling prey to false positive bias. It would NOT license the inference that an actual literature operating under these parameters has a high Positive Predictive Value, because a single simulated study cannot capture the population-level dynamics of the chase for significance across multiple research teams."
}
END_TEMPLATE

## Expansion Requests

BEGIN_EXPANSION
FIELD: Active Learning
LACKS: The ability to declare two distinct payloads within a single specification and apply a relative comparison operator between their resulting metrics.
WHY: Both Active Learning and Optimal Experimental Design are fundamentally comparative fields. Active learning requires demonstrating that an active query strategy achieves lower prediction error than a random sampling baseline given an identical budget, while optimal design requires evaluating a proposed design's efficiency relative to standard classical designs. Because the bench only evaluates an outcome rule against a static scalar threshold for a single payload, it precludes relative comparisons entirely, forcing researchers to either hardcode baselines into the executor or abandon comparative claims, which is unfaithful to how these methods are empirically validated in the literature.
SMALLEST_FORM: A modification to the work object to accept an array of up to two payloads, returning a results array, and an extension of the outcome_rule to evaluate relative operators (e.g., result.error < result[cite: 1].error).
BLOCKS: Active Learning, Optimal Experimental Design
EVIDENCE: Seung, Opper, and Sompolinsky (1992) [cite: 1] validate Query by Committee by explicitly comparing its exponential error decrease against the performance of a random input passive learning paradigm. Atkinson and Donev (1992) [cite: 3, 4] fundamentally evaluate optimal designs by computing their D-efficiency relative to other standard experimental designs.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Meta-Science
LACKS: The ability to calculate summary statistics, such as a mean or a proportion, over the outputs of multiple repeats before evaluating the final outcome rule.
WHY: Meta-science models calculate the Positive Predictive Value (PPV) by observing the proportion of true versus false positives across a large distribution of simulated independent studies. Similarly, Bayesian Experimental Design optimizes an expected utility, which inherently requires integrating (or averaging) over a prior distribution of parameters and a sampling distribution of data. Because the bench evaluates the outcome rule strictly on a single scalar per repeat without any aggregation mechanism, it cannot express an expected value or a population-level proportion, reducing these probabilistic and population-level fields to meaningless single-point estimates.
SMALLEST_FORM: A new aggregate field in the repeat block that specifies a simple reduction function (e.g., mean or true_proportion) over a specific result field, outputting a final aggregated_scalar that the outcome_rule evaluates exactly once at the end of the specification.
BLOCKS: Bayesian Experimental Design, Meta-Science
EVIDENCE: Ioannidis (2005) [cite: 9] derives his conclusions by mathematically modeling the base probability and ratio of true to false relationships across an entire scientific field, which is a population-level metric requiring aggregation over many instances. Chaloner and Verdinelli (1995) [cite: 6] define Bayesian experimental design as maximizing a pre-experimental expected utility function, which inherently requires integration over prior probability distributions.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Falsification-Based Search
LACKS: The ability to feed the scalar evaluation outcome of a previous repeat into the input state or seed derivation of subsequent repeats to guide an optimization search.
WHY: Falsification-Based Search typically relies on stochastic optimization techniques (such as simulated annealing or ant-colony optimization) to actively guide the search for a trace of minimal robustness. While the current bench allows state persistence between repeats for the random walk, the seed derivation for each repeat is strictly fixed to a deterministic hash of the root and index, meaning the search trajectory cannot adapt based on whether the previous step moved closer to a safety violation. This reduces the method to a naive Monte Carlo random walk rather than an actual guided search.
SMALLEST_FORM: A new state discipline option in the repeat block called "feedback", which dynamically replaces the next repeat's derived seed with a hash of the previous repeat's scalar result, allowing stateful executors to adjust their internal search direction based on prior performance.
BLOCKS: Falsification-Based Search
EVIDENCE: Annpureddy, Liu, Fainekos, and Sankaranarayanan (2011) [cite: 7, 8] explicitly design S-TaLiRo around randomized testing based on stochastic optimization techniques, inherently requiring a feedback loop where trajectory robustness outcomes guide the generation of subsequent test samples.
END_EXPANSION

**Sources:**
1. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0dhXSTNeKGDG8urAu8x-jG465cWT7d18qhEaXSWRvG0Q8oH2GPbuVouJHywKGRmNMv0aCDQsLIdvAGqWN_6X-7okPSvQUuhQYit0cpYDvxAnPAoTMfLCr4s2iwaJwvowlQjsUJBKSDCKWWqW2T4-MrgwUT43aeY1WY3dfEXEQMynzZRKu6mIW5zEnLa8REQ==)
2. [burrsettles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYb3YmRqqYq4JRxFGbn5dHsXkC3LoEL4ml2vh0T-3iBvE8L5hcU-HkMweDfdMX8ZbUp91uFov8a7jkT62BNRuN7oc0lYEfGDky8WdLztJUcbIBGEZEfqq8gUH0pP6RQQRQGPmcwT6QG1I5RF4=)
3. [bactra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFScNbZX3r2mXGAYtcPyvKXbcnkx4IqO-Czn5Ml5wr2QVDkK14_a4cNBVfRkkPKZY6FtwIk8pNDDIA42L0MdzWxftjZ1dUMce3EV1yWvTqF6uLzg0eVhD0YnIl0k71rmJ8=)
4. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYGFCusp2dlgTd646VSurAyZlmdoSMtVDRyZlUyfwy8QJ2IdFSo7ssEob26S0usTs5hpV2FI1eM8KJAyyD6F-NuSoyEPl3hGPKqloY9Zih_yEAiGJ5UiM3-GIBPdOWxbsTCUFeApfNzzjVfu_6fkHD8e4bAjO23KbkVEQoUVSDy6uZ8a5gHvuq)
5. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV9WWrmLOVD2nM7ZYQREPNrbcUYTplf401fYBKYqAWKgkJfSDJm3VtzQBsPeB8IyLDQJWS9P6zgP3B9Db32b_IC57WF-mvevMS9_XTFyMswDz9S9SHocw90HTgGGShf9oRvSOz4EwttbdYHmusIq-GDDqtK9Ol42ccfXQ7YVm0-mtnpkY6I1VM3rYMuF6x8mhloKteYY_FiD7IG7wyej8DprQu6YYaZBPVeR29BEIKfUGMgNLZpG5o9_8GcMWYQr8r9Q==)
6. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8kpwDyBopqyaIL71RUXrl7XlZBxba3_VM5ZzN6zGMWO2NCc9MexEvxYDWgc3sHXwqs_nUEGGbQNusBmZaE25TXtVBIh9dS7V1DkEKpOX2LHsYjMEdQlJvTETT34yZH7wq-tEeA-DN75-V8I2w1aOvjt9AqTCbggySxPAX7omSId6RS0b4l7Vg1prNs2sgzvSsFuWX2XGa5kIJaI9C11euqT9oIm2EvUsA8jpgh-_cjrdJhRgyHwCsRpGDdjnK1_BC)
7. [elsevierpure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl0AdniatbvXVapu2EVoX_z6wYvbUvpW1ABAF5VFt2Se7d5o2HDnrzjH0OZoD0hJ7Urt_bbMJvO49QxxQSBdbFlJJ5ECEez7UZIxoMFXfOBMGlp0bhrLR4WqQ1yJGOm8_RCyl0GDa4VVTD5sG7haWPc-BOHStXTp0OQCXPFxxk-kkVJB2EbEdZmxi92mY4OQZmWp6Qxeno490sk3XvJzfe_O8aZ2s=)
8. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERbgdXQw41XcIuazIz4kXqzJGTvJUO6qimqEKd4UwVHXJK0j6iEYku4AuIkb-mnpGSH8iDS6qUAuFSvqtQODy7tJITQ0f9Ivt2EPLQIo6guRzo0pxrGtuZKPdPqjMDm9NTRTdABsgMjl_ITm6__6e9EuzRkZCb)
9. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-mxUhwQyX2YjjZ0Jy-L8Izrs08BoQbkiEM7ZSqTtCUrVSuLps17eqUN-oRkMgKKlQy_2WsdLpRSfv2d5pnPeyUB2LO0qzYfGXm0e0H9Emt-B_CrhGvhQLWGkWG3WCrduOrO1BaWJqEXBp5calANi1mJBZYIvgJg3iXRk5HOpI1iv_2bY=)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpGMfdjvnMOt346fCsC8Cgk4uKvTAnixZYz4dnOeZ-RG3F9yC8wIbj9hBpLHUc_c0ca98fJUfkCQrpTfD6RDPM42Nd_XG-n4FP7_mBgG7598Q5Kyj89Aq728W2EyHIx1cfPmjU6VZMfw2m2w3KMclNckIHbLnvutOjW1dKnsW563JJ)
11. [sbc.org.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnttEBxl798a4-oD9CW2KNUXR4oS4Q0UU-yAJ7cyy7gy9qtyVzA9HRSIWyvUPZSOM3MwQDewsb4DGhvroRFRldtWfo8HPDKkwPgZ7wQ66o38vUqDp69KXbdpz1eKANbEwlCb2GWddUkUBePA6qV0AHBv1ZzgmRTDDJLiM=)
12. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0W2RS2-obKiQhH4g9vxqnG-j6k9Ao_notCrMxFoySFX995WGBN807owChajGBm9YxpAviVTcfEfopWU-aXVeQddDiNSVE5vvHjsyn6AnrAe95eOVEs9xste4SZNhRBZWr)
13. [microsoft.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqxPlcQvVNM-BnLUMBvrkd6fs7ZRG69w6C8_wz9xC078YQ_x9l8xoyUtIXEOxo4pCgbFP-QPRvpuFkr6PGbd9co8ZhVUpxqff1xE29iE8MZzcGwQQUbRVpxWp2MeiQftNHPx8fRy_3x6jwYuTVKd-TAOWrPkpWva4A19evkrZpxiPVwQyt3A==)
14. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_6UAE16PK6y-7Jt7qINbltwDLZyEArnJBaMcjWNIHfhSfbi-T4y5w3sbA-66MjSCvWjzFc8QSlrBpHTYoOeJSJ3R5M6wuOfJZCVo_JgcbBmmuyBBaXJqYp1YxaSACDTpfMEezeDBd1nu3AmaGvLY23UKUWgJzylr5V2ak)
15. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv65wW2RU_itu1Ue7xj_pM4Y8tmq7VMrhdDm_4KV14VrSfErm3S1ZB-Qz8FNDvPzGW7RVsUKkdAkF_Kii0yZhyxgKKkEc1gGWUqaBqaxozaGAg_IIXrbwhl2Z0gEXJAdPz3W109tM-CHZnWuuCeM-3IYNSSnPY2A==)

