# Prompt 14: Evolutionary epistemology

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd1VmVkYW9Xd0VMeUYtOFlQMXFTTThBTRIXdVZlZGFvV3dFTHlGLThZUDFxU004QU0
**Elapsed:** 364s

---

# Experimental Design in Evolutionary Epistemology

Evolutionary epistemology asserts that the growth of human knowledge and scientific discovery follow Darwinian processes of variation and selection [cite: 1, 2]. Research in this cluster requires computational environments capable of stateful selection, constraint satisfaction, and heuristic induction [cite: 3, 4]. The current computational bench requires specific structural expansions to faithfully execute the characteristic experiments of these fields, such as cumulative selection loops, connectionist network evaluators, and symbolic regression over empirical datasets [cite: 4, 5].

## Universal Darwinism
BEGIN_TEMPLATE
{
  "template_id": "universal_darwinism.weasel.v0",
  "kind": "cumulative_bitstring.v0",
  "param_space": {
    "length": {"int_range": [cite: 4]},
    "mutation_rate": {"int_range": [cite: 1, 4]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Universal Darwinism",
    "reference": "Richard Dawkins' Weasel program from The Blind Watchmaker (1986)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This models cumulative selection by mutating a string and keeping variants that approach a target. A SURVIVED verdict would license the claim that cumulative selection exponentially outpaces single-step random generation, but it would NOT license the claim that biological evolution operates with a predefined distant target, as the model artificially supplies a fixed goal sequence."
}
END_TEMPLATE

## Evolutionary Epistemology
BEGIN_TEMPLATE
{
  "template_id": "evo_epistemology.bvsr.v0",
  "kind": "cumulative_bitstring.v0",
  "param_space": {
    "length": {"int_range": [cite: 6, 7]},
    "mutation_rate": {"int_range": [cite: 1, 6]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Evolutionary Epistemology",
    "reference": "Donald T. Campbell's Blind Variation and Selective Retention (BVSR) model of creative thought (1960)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the rate of adaptation of a knowledge-generating agent employing Blind Variation and Selective Retention, modeled as bitstring evolution. Evolutionary Epistemology uses this to model how cognitive progress mirrors biological evolution through unjustified trials and culling. A SURVIVED verdict would demonstrate that BVSR is sufficient for knowledge accumulation, but it would NOT license the claim that human creativity is entirely devoid of heuristic foresight, as it models the pure null hypothesis of purely blind trials."
}
END_TEMPLATE

## Computational Philosophy of Science
BEGIN_TEMPLATE
{
  "template_id": "comp_phil_sci.echo.v0",
  "kind": "echo_coherence_network.v0",
  "param_space": {
    "hypotheses": {"int_range": [cite: 7, 8]},
    "evidence": {"int_range": [cite: 6]},
    "cycles": {"int_range": [cite: 4]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Computational Philosophy of Science",
    "reference": "Paul Thagard's ECHO connectionist model of Explanatory Coherence (1989)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This models the acceptance or rejection of competing scientific theories by propagating activation through a network of excitatory and inhibitory links representing explanatory coherence. The field relies on this to operationalize how scientists weigh complex, sometimes contradictory evidence. A SURVIVED verdict would license the claim that explanatory coherence can be computationally modeled as constraint satisfaction, but it would NOT license the claim that this mechanism is statistically optimal or guarantees the objective truth of the accepted hypothesis."
}
END_TEMPLATE

## Computational Models of Scientific Discovery
BEGIN_TEMPLATE
{
  "template_id": "comp_sci_discovery.bacon.v0",
  "kind": "bacon_heuristic_search.v0",
  "param_space": {
    "variables": {"int_range": [cite: 1, 6]},
    "noise": {"int_range": [cite: 7]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Computational Models of Scientific Discovery",
    "reference": "Pat Langley and Herbert Simon's BACON systems for empirical discovery (1978-1987)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiments with heuristic search spaces to discover quantitative invariants like Kepler's third law from raw empirical data. The field uses this to demonstrate that scientific discovery can be formalized as rule-based problem solving. A SURVIVED verdict would license the claim that data-driven heuristic induction is capable of historical scientific discoveries, but it would NOT license the claim that human scientists operate without top-down structural models or theoretical priors."
}
END_TEMPLATE

## Expansion Requests

BEGIN_EXPANSION
FIELD: Universal Darwinism
LACKS: A conditional state-update mechanism that retains executor state between repeats only if an evaluation score improves.
WHY: Both Dawkins' Weasel and Campbell's BVSR rely fundamentally on cumulative selection, where a variant is generated, tested, and kept only if it outperforms its parent. The current bench has a stateful random walk, but it updates state unconditionally on every step, meaning no selection pressure can be applied to guide the state over time.
SMALLEST_FORM: An executor cumulative_bitstring.v0 taking parameters length and mutation_rate, which persists a bitstring across repeats, mutating it each time, but discarding the mutation and reverting to the previous state if the hidden target match score drops, outputting a best_fitness integer field.
BLOCKS: Universal Darwinism, Evolutionary Epistemology
EVIDENCE: Richard Dawkins' The Blind Watchmaker (1986) uses the Weasel program to contrast cumulative selection against single-step selection. Donald Campbell's BVSR (1960) requires Selective Retention as the third mandatory component after a variation mechanism and a selection process.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Computational Philosophy of Science
LACKS: The ability to define and execute a connectionist network of propositions with positive and negative links to find an activation equilibrium.
WHY: The field models scientific theory acceptance not as single-scalar outcomes, but as a holistic constraint satisfaction problem where multiple hypotheses and evidence nodes settle into a stable state. The bench's current single-scalar outcome and isolated repeats cannot represent mutual coherence or competition between multiple propositions.
SMALLEST_FORM: An executor echo_coherence_network.v0 taking parameters hypotheses, evidence, and cycles, building a network graph seeded by the world root, running activation cycles, and emitting an accepted_hypothesis_id integer.
BLOCKS: Computational Philosophy of Science
EVIDENCE: Paul Thagard's ECHO program (1989), which explicitly uses a connectionist network algorithm to compute explanatory coherence (e.g., in the Oxygen vs. Phlogiston debate) by settling into a maximal coherence state.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Computational Models of Scientific Discovery
LACKS: A facility to generate an empirical dataset and perform heuristic search over mathematical operators to find an invariant algebraic expression.
WHY: The field's foundational method is the data-driven discovery of quantitative laws. The bench currently executes pre-formulated specifications but lacks any mechanism to evaluate a dataset of variables and iteratively compose symbolic mathematical expressions to test for constant fits.
SMALLEST_FORM: An executor bacon_heuristic_search.v0 taking parameters variables and noise, which generates a simulated numerical dataset from the seed, searches for an algebraic invariant, and returns a found_invariant boolean field.
BLOCKS: Computational Models of Scientific Discovery
EVIDENCE: Pat Langley and Herbert Simon's BACON project (1978-1987), which used heuristic rules to incrementally formulate terms and discover numerical laws like Kepler's third law of planetary motion from raw quantitative data.
END_EXPANSION

**Sources:**
1. [tabrizu.ac.ir](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCgGLjH7lj5wtx2epakSmD4aa3Lv6TzEnxyHJSeAFFf2nE6xtfnpsD13bAUGX-KyXenb_7GfEo8EwwGMPs-qf8Vg0QX9RGCA9j5jnYkLSsng9IEPQHG-TSjVzWlW0gtCH8hchT1-0iKSr9xfJih5bOLQ==)
2. [opensym.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEuvWYR2WkEz-BEk7oFI0KaPr-vf5guxrtwMi4J0gvPp5wql2YHLR1r30dhHZ5p1oQU1h8y9_-KV8uuQN5V_7cITxQarp9A8T2gCcRk1QnMDmg3i6CQP7bZXqvsS_XCNRxS7zxEC44aEIAGdMzm1CPv2cnPJ1JHu4=)
3. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbMAcAz1FU9x7keenUYdNBPsO6u6fGH1Gyiy-KV3aRYoU-p9geOzyQKdfb9dAFfqXdzamkBFrQzQO4cjI8-OdZ9ZNsUwk2WsQJpL7k44qIwxFWdC7Q6ar6YapOufAbrpSY7tDWn3aHsUU8HuUrzOiszxE=)
4. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-F5089ROvce4-ovyQOcdXeBOjpxmOXoQHvYUGTi6D3CozmLj7voNQh99uMCl42mSb8vQohcv5mRcJdmrMtCZaF8EJQI5l_ElRevKv8hEGujT7ErppbDTekucwVHpDhFIaoONmfP3jCJbCxHwIj1VClOI=)
5. [bionity.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF22dZPX-nO798Htszr6KEdNt4GgagBPZdUE0fMC2hHmJHOmiOCaefhkBawlsU8i1AZu33qsKdhUBR-2CGmvqn3vOSIugwvBNh5MoQskwc4bpLUEZ6j2647cRk8nkz9Dh-Pt77YykiAud5dEr_5rI6PvckCR4zKlA==)
6. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXJ2K95DIhr-LvtEAMroYgA_kdJVfZJJ55QmXC3NDeMfgVkS8TOEnCgYfcS4FKI40neojrV5_VyMrl3oQQUqmjk7ruk81_wBRVo6Wi3_OKnvG5fXrnNc-ikPkZMmYveCKDYdwkfGdTXf3jbWuyn5JP0v2SrJ5muUjO3ofakd_WJ_7kXG4sKDPp)
7. [southampton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvE_ZWZO6KDDB3vL-TQlsmnpGPUn_9LlSh0KcCFXpabDNLU_pTlhI3oh95tkI_O72RjHqf7n7UzlTbpSg5gCQ9lyU6Wy7fD_TrqZbbgMIE7Ja-DU6EWWmpB8S6kwuP0_f7oxrNYRbALlreVsMcY33uosl2hCWT_sVnCWTzIC58eMI=)
8. [informationphilosopher.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQysF3mZRi7uBxKQgtI_EWfwUTEsL6nqteiyuq8g4Tkgmqp5WF9tKkhh-UndIlh6rVmiPkGma7zXSJwOOJvxyMgre0eGr5Px5sG8cU6DYyUleN_9ylguxa6FGmAaUW-V5biGJf5DA0sDIxaxCzVOAfXpVDxEhitJKuROU=)

