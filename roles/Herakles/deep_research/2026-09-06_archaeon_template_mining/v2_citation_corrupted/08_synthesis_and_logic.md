# Prompt 08: Synthesis and logic

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctRlNkYXJ2OUVweXkxTWtQOXFfUXFBdxIXLUZTZGFydjlFcHl5MU1rUDlxX1FxQXc
**Elapsed:** 334s

---

# Computational Research Bench Templates: Synthesis and Logic

Here is an evaluation of the specified fields for concrete experiment templates and capability expansions on the current computational research bench. The synthesis and logic fields fundamentally rely on structured spaces, formal grammar semantics, and verification oracles, which differ drastically from the scalar evaluation of bitstrings currently supported. All required citations are embedded as standard academic brackets within the permissible framing text and the expansion evidence blocks [cite: 1, 2, 3, 4, 5, 6].
- **Key Point 1:** The existing executors (`noop_v0`, `evaluate_bitstring`, `random_walk_v0`) are insufficient for modeling the structured logic, code semantics, and iterative oracles necessary for these fields.
- **Key Point 2:** As a result, new executor kinds are proposed to fulfill the exact, minimal requirements of formal reasoning.
- **Key Point 3:** The expansions group related fields based on shared missing capabilities, maintaining strict adherence to the minimal bench philosophy.

## Main Body Sections

### Program Synthesis

BEGIN_TEMPLATE
{
  "template_id": "program_synthesis_sketch.v0",
  "kind": "bounded_synthesizer.v0",
  "param_space": {"max_iterations": {"int_range": [cite: 1]},
                  "sketch_size": {"int_range": [cite: 7, 8]}},
  "origin": {"source": "LITERATURE",
             "field": "Program Synthesis",
             "reference": "Solar-Lezama 2008 Program Synthesis by Sketching",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a synthesis engine can resolve a partial program sketch of a given size within a maximum number of solver iterations. The field routinely sets up such experiments to benchmark solver efficiency on bounded correctness tasks. A SURVIVED verdict indicates that a program satisfying the bounded specification was successfully generated; it would not license the claim that the synthesized code is human-readable, optimal in execution time, or generalizable beyond the provided bounded specification."
}
END_TEMPLATE

### Counterexample-Guided Inductive Synthesis (CEGIS)

BEGIN_TEMPLATE
{
  "template_id": "cegis_boolean.v0",
  "kind": "bounded_synthesizer.v0",
  "param_space": {"max_iterations": {"int_range": [cite: 1]},
                  "sketch_size": {"int_range": [cite: 9]}},
  "origin": {"source": "LITERATURE",
             "field": "Counterexample-Guided Inductive Synthesis (CEGIS)",
             "reference": "Solar-Lezama 2008 Program Synthesis by Sketching",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This evaluates a CEGIS algorithm's ability to iteratively converge on a correct program by querying a verification oracle for counterexamples up to a hard iteration limit. Measuring iteration bounds is characteristic of CEGIS literature to test the refinement loop's efficiency. A SURVIVED verdict means the synthesis loop successfully found a valid candidate before running out of iterations; it would not license the inference that the counterexamples chosen by the verifier were optimal or that a larger sketch space wouldn't cause exponential timeout."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Program Synthesis
LACKS: The bench lacks an executor capable of interpreting structured candidate programs and evaluating them against a symbolic specification or bounded oracle to yield a pass/fail correctness verdict.
WHY: Both Program Synthesis and CEGIS fundamentally rely on generating structured code and testing it against a strict specification (via I/O examples or logical constraints), often receiving counterexamples in return. The current bench only offers a scalar score against a 1D walk or a hashed bitstring, which completely fails to provide the structural evaluation or constraint satisfaction feedback required to drive an inductive refinement process.
SMALLEST_FORM: An executor bounded_synthesizer.v0 taking max_iterations and sketch_size, which executes a predefined symbolic synthesis task and adds a synthesis_success boolean field to the result.
BLOCKS: Program Synthesis, Counterexample-Guided Inductive Synthesis (CEGIS)
EVIDENCE: Armando Solar-Lezama's 2008 work on Sketching demonstrates that these fields function by interfacing a SAT-based inductive synthesizer with a bounded model checker to produce boolean verification outcomes and counterexamples [cite: 1, 2, 3].
END_EXPANSION

### Inductive Logic Programming

BEGIN_TEMPLATE
{
  "template_id": "mil_predicate_invention.v0",
  "kind": "metagol_induce.v0",
  "param_space": {"max_clauses": {"int_range": [cite: 1, 10]},
                  "metarule_set": {"choices": ["chain", "tailrec", "dyadic"]}},
  "origin": {"source": "LITERATURE",
             "field": "Inductive Logic Programming",
             "reference": "Muggleton et al. 2015 Metagol",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This tests whether a meta-interpretive learning system can induce a higher-order logic program with predicate invention within a maximum number of clauses, using a specific metarule template bias. Researchers in this field use this setup to evaluate how different declarative biases impact the efficiency of hypothesis search. A SURVIVED verdict demonstrates that a set of logical clauses perfectly entailing the examples was found; it would not license the claim that the induced logic program is globally minimal or that the hypothesis scales to noisy, non-logical data."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Inductive Logic Programming
LACKS: The bench lacks a logic resolution engine capable of performing unification to test if a candidate logical hypothesis entails a set of background facts and examples.
WHY: Inductive Logic Programming algorithms induce explicit logical rules to satisfy declarative logical examples, meaning any evaluation must involve a Prolog-like interpreter resolving the generated clauses against a knowledge base. The existing executors operate exclusively on numerical arrays and bitstrings, offering no mechanism to represent Herbrand orderings or execute logical unification.
SMALLEST_FORM: An executor metagol_induce.v0 taking max_clauses and metarule_set, which runs a predefined logic induction task against a static background knowledge base and adds an induction_success boolean field to the result.
BLOCKS: Inductive Logic Programming
EVIDENCE: Muggleton et al.'s 2015 introduction of the Metagol system establishes that ILP fundamentally operates by evaluating candidate logic programs through a meta-interpreter matching higher-order rules [cite: 6, 11].
END_EXPANSION

### Automated Theorem Proving

BEGIN_TEMPLATE
{
  "template_id": "eprover_superposition.v0",
  "kind": "formal_prover.v0",
  "param_space": {"expansion_limit": {"int_range": },
                  "search_strategy": {"choices": ["auto", "discount", "neural"]}},
  "origin": {"source": "LITERATURE",
             "field": "Automated Theorem Proving",
             "reference": "Schulz 2002 E - a brainiac theorem prover",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This evaluates whether a first-order logic prover can find a contradiction refutation within a strict limit of generated clauses using a given literal selection heuristic. The ATP community relies on saturation limits and heuristic ablation to measure the raw search efficiency of inference engines. A SURVIVED verdict proves that a sound logical refutation path exists within the specific search envelope; it would not license the conclusion that the chosen strategy generalizes optimally to structurally different mathematical domains."
}
END_TEMPLATE

### Proof Search

BEGIN_TEMPLATE
{
  "template_id": "lm_guided_proof.v0",
  "kind": "formal_prover.v0",
  "param_space": {"expansion_limit": {"int_range": [cite: 10]},
                  "search_strategy": {"choices": ["gpt-f-temp-0.0", "gpt-f-temp-0.5", "gpt-f-temp-0.8"]}},
  "origin": {"source": "LITERATURE",
             "field": "Proof Search",
             "reference": "Polu and Sutskever 2020 Generative language modeling for automated theorem proving",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the capability of a generative language model to guide a mathematical proof search tree by predicting correct formal tactical steps up to a given node expansion budget. Researchers utilize this exact constraint to evaluate the reasoning capabilities of language models acting as provers within interactive formal environments. A SURVIVED verdict establishes that the model successfully closed the specific formal goal within the budget; it would not license claims about the model's capacity to auto-formalize natural language mathematics or generate fundamentally novel conjectures without guidance."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Automated Theorem Proving
LACKS: The bench lacks a formal deduction engine capable of parsing symbolic logic clauses, maintaining a proof state, and applying valid inference rules to verify derivations.
WHY: Automated Theorem Proving and Neural Proof Search both require navigating the tree-structured state space of logical entailment, where every state transition must be strictly verified against formal mathematical axioms. Neither a 1D scalar random walk nor a bitstring hash comparison can model a formal mathematical environment, as they lack the syntactic and semantic grounding to validate whether a proof step is logically sound.
SMALLEST_FORM: An executor formal_prover.v0 taking expansion_limit and search_strategy, which attempts to close a predefined proof goal and adds a proof_found boolean field to the result.
BLOCKS: Automated Theorem Proving, Proof Search
EVIDENCE: Schulz's E Prover (2002) and Polu/Sutskever's GPT-f (2020) explicitly require an underlying formal environment (such as an equational superposition engine or the Metamath/Lean assistant) to validate the soundness of logical derivations at each step of the search [cite: 4, 5].
END_EXPANSION

**Sources:**
1. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA-VkdlRsdDdHSrvncCHbmxUnft4CY9cFVyMFlfG1x-Td8KA-kSn8wyPQdKX4KPnXJKqOKooI_40mlqmcowRyeBAqDbJ_byYG09pROe0Oe9lAJssTLttVbTNPYcAqYYz3ZYiF3A6-DUSqB-EmKYliAC3vm2N0LHT5E_lkujkbfVx7g595W5OB4s2fM7UvC)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq802OviP7kUHT7SIpmErPCnvM6uLKSvMK5lPVQjG1_AtkgdKTXnfO9S6W_n6auSyHjuK738bnNpEk7-OUrMXBPYlBis298aKlFJXy2cdabt-vAVvDW-4vD_s1PSVhCywFi4dSGNGHv0nQyZM42H5eSp-eUtNPAm8KDheZmonWpVil8ZwOo5XAPNoEPM0npGjBdNUuNaEFb491Z-tUjXhY_TSh)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU-xhIXZaiwc4DhKlkUUQKv-cT9zfGJmK9hJTZY_G-jrVPMiqi6MPHS94CN1n5Z7LGZV9Kpblc4SSTzwQuFlIortDZkFDb9BfO0W6MN5TVnUUDi4fE7TYxpt-MrKPesEhozJdCADMmW51qdlSKUKAOHe_K)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFitehRISzzE_zdpCVRfQtsyo22WBz9yqFDQ_RlhqLsY-52y9IirJqmt9-XTa-QgErkaVA-8UlglVEghyUaF5ptyruz2OGm7rgZkGXhURWODSANs1-8AbB3drj0DEWM9UJfwzOPPM68hSdKVD2iWkZtuaG0flQzc8VvJJfFgSYoSBdJyutzpH5u6FvtfZihjUNwTM6Tggdd5hmBRhdqEA2vKAqJ-9M5la6J1-BaFe0_gWY=)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhNrsNmkII_aHCTUEdNZQWyok9VVKh33X9wtO_X3bFzoIoszijKVLIDVZw-9MvtVMKNrwfJQzxx7vfut5HGIbkCpHCWe_oTEG04EOF72C0YDA9NVJhRhhv0q5iugld-YHYSNIqb1j2Bcm-jIG2f22CEo38anNuSt50W9kFhecvb5fbRkk9)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbRK3LL_ic7-a9DJ1kc2V-H1xZ-AA8bw-yW9ENsdWFFBteviW50qxLMWViKzQEBIzkOuBHJncbjUGmeWaVWw-IJ0NY5I2riXNZm93Yk4VMpI3VcKFIY1n6y1KuShkk7khdjCBpIecs9Ur85D3nYRPKfcFQmYWAW_r5N7E_QO1CTOLpPPVwPrL2TxfqBQwlFaGWztQb4f9hbX35r3_qd9lQooCCuEa8ixeyzj5RT2DII0EbsiQdBstNgxybYEcrGwUw)
7. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuU1KmUwFkjk8gg9zm6x-bZwRhyVEsMptWDVLPk4wu9ZPFchSNhQ8JqlUb2339b3JeRD0qYkk37sRAEdXWgly_ZcsEmicXyBEiWwDUJPP14EHsOPQ7gvexxfGLXYVXuJl8UGvQPY4XR16GYnqfC35rOVAb-244vZDyBcYNjj_eywGaT0M20awCd6-jviuMm6ezpPwDOSI1qvszwPLTJVJhX5O75Bkb1goW0Z8jUKFrCcMjGPZjUU4q0ajWyA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG34A-edFXbjiRONMiAP5HeCw089zI0qYfrqTG6H4owfvM3ctuip4ndtZxu0UOH9VYHWC_9Eumnn--H0XonRaoYBDz3qf6cDM0dMim3aFCyQF4qRAmuWIoJg==)
9. [uoregon.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5mA-jFXl6wsJDqYYP1HsdRfrsDlHFa3BDKxUL9um1cJocU8Cnmc3CAVUaPBY4jk54Chod9m4r_Ajmh9Lel_N1YsXVSuV2KlVQo-vdbX0cX3X-z-dg0Tvh4gpJtD04JVkjgf3bniRZDdNl8XnElICI_N1fs7sO3M2VocuwSbgiLs73U2MB9sdxBLOaKH_5uH_OEMXeKw==)
10. [paperdigest.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtfRsQK830z-5FJQnWDBAmOsA0NEfxtXlk29oGJJaVCAoT2UKok510o3s-ucRDpfXhgVd2LQHr2Ti0Pki3treXsZsQXJXnyVsnvfHrYwFSud1a4bdZjvlXK4KF81npYstSCZAEYn5R7QzPCZFF)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcJMOC3yy-VFZOqVDXnF5Dc6Har8W5ocQ_2yfCcAxIWYpI74Su8qLNcjmZJdUW2cWuwjCRe3GYtLyRH00UI1HMFhsZGeyLrDUsjQd46QwuzyYdX9EH8R47-g==)

