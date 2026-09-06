# Prompt 09: Testing and verification

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctRlNkYW83NUZkemUtc0FQNUxxSDhBbxIXLUZTZGFvNzVGZHplLXNBUDVMcUg4QW8
**Elapsed:** 334s

---

# Testing and Verification: Experiment Templates and Bench Expansions

This report synthesizes concrete experiment templates and identifies critical infrastructural gaps for a computational research bench, mining five distinct fields within the testing and verification cluster. Research suggests that while certain probabilistic approaches can be minimally modeled on the existing architecture, the majority of advanced verification paradigms require structural enhancements [cite: 1, 2]. It seems likely that Property-Based Testing can map its stateful assertions onto the current random walk executor, albeit in a highly constrained form [cite: 3, 4]. However, the evidence leans heavily toward the conclusion that Metamorphic Testing, Counterexample-Guided Verification, Formal Methods, and Search-Based Software Engineering are fundamentally blocked by the bench's current lack of cross-repeat outcome evaluation, exhaustive constraint solving, and dynamic feedback loops [cite: 5, 6, 7]. The templates and expansions below directly formalize these findings into actionable system specifications. 

## Property-Based Testing

BEGIN_TEMPLATE
{
  "template_id": "pbt.stateful.walk.v0",
  "kind": "random_walk_v0",
  "param_space": {
    "steps": {"int_range": [cite: 8]},
    "step_scale": {"choices": [cite: 1, 9, 10]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Property-Based Testing",
    "reference": "Claessen and Hughes 2000 QuickCheck a lightweight tool for random testing of Haskell programs",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Property-based testing asserts that specific invariants hold across randomly generated inputs. Here the stateful random walk executor models a system undergoing a sequence of randomly generated state-mutating API calls. A SURVIVED verdict demonstrates that the invariant was not violated for this specific generated sequence of inputs, but it explicitly does not license the claim that the software is completely free of bugs for all possible input sequences."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Property-Based Testing
LACKS: A generator mapping layer that translates numerical random seeds into constrained, structured payload inputs.
WHY: Property-based testing fundamentally relies on domain-aware generators to create structured inputs (like valid trees, formatted lists, or specific state transitions) that satisfy test preconditions. The current bench only feeds raw seed-derived integers into a walk, entirely bypassing the structured generation and shrinking capabilities essential to the method.
SMALLEST_FORM: A generator_map object within the repeat block that allows mapping the repeat's derived seed to basic constrained types (e.g. integer ranges or string lengths) to dynamically populate the executor payload.
BLOCKS: Property-Based Testing
EVIDENCE: Claessen and Hughes 2000, QuickCheck: a lightweight tool for random testing of Haskell programs [cite: 1, 3].
END_EXPANSION

## Metamorphic Testing

BEGIN_TEMPLATE
{
  "template_id": "mt.relation.eval.v0",
  "kind": "evaluate_metamorphic_v0",
  "param_space": {
    "base_bits": {"choices": ["00001111", "10101010"]},
    "mutation_mask": {"choices": ["00000001", "00000010"]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Metamorphic Testing",
    "reference": "Chen Cheung and Yiu 1998 Metamorphic testing a new approach for generating next test cases",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Metamorphic testing bypasses the oracle problem by asserting that relations hold between the outputs of an original input and a systematically transformed follow-up input. A SURVIVED verdict indicates that the specific metamorphic relation holds for this exact input pair, but it does not license the assumption that the output data is actually mathematically correct, only that it is consistent with the transformation relation."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Metamorphic Testing
LACKS: Cross-repeat outcome comparison rules for evaluating relations between distinct experimental runs.
WHY: Metamorphic testing evaluates untestable programs by checking metamorphic relations between the outputs of a source test case and a mutated follow-up test case. The bench strictly restricts the outcome rule to a single scalar comparison on a single run, making it structurally impossible to evaluate an equation across two distinct executions.
SMALLEST_FORM: An outcome rule operator capable of cross-referencing and equating a specific result field from two explicitly defined repeat indices.
BLOCKS: Metamorphic Testing
EVIDENCE: Chen, Cheung, and Yiu 1998, Metamorphic Testing: A New Approach for Generating Next Test Cases [cite: 7, 11].
END_EXPANSION

## Counterexample-Guided Verification

BEGIN_TEMPLATE
{
  "template_id": "cegar.abstraction.loop.v0",
  "kind": "cegar_loop_v0",
  "param_space": {
    "initial_abstraction_bits": {"choices": ["11000000", "11110000"]},
    "property_bits": {"choices": ["10101010"]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Counterexample-Guided Verification",
    "reference": "Clarke et al 2000 Counterexample-guided abstraction refinement",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment evaluates an initial over-approximation of a model, analyzing counterexamples to refine the abstraction until a property is proven or a genuine bug is found. A SURVIVED verdict implies the property successfully holds on the refined abstraction state space, but does not license the claim that the physical implementation is free from hardware faults or bugs outside the modeled abstraction layer."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Counterexample-Guided Verification
LACKS: A dynamic feedback discipline where a repeat mutates its payload for iteration N+1 based on the output of iteration N.
WHY: Counterexample-guided verification and search-based engineering are fundamentally iterative feedback loops. CEGAR must dynamically refine its abstraction payload using spurious counterexamples generated from the previous run, while SBSE must mutate evaluation candidates based on prior fitness scores. The bench's sealed, static specifications completely isolate repeats and prevent this required dynamic state transfer.
SMALLEST_FORM: A feedback_function parameter in the repeat block that applies a predefined bitwise mutation to the executor payload if the previous repeat's result falls within a specified scalar range.
BLOCKS: Counterexample-Guided Verification, Search-Based Software Engineering
EVIDENCE: Clarke et al. 2000, Counterexample-guided abstraction refinement [cite: 2, 12]; Harman and Jones 2001, Search-based software engineering [cite: 6, 13].
END_EXPANSION

## Formal Methods

BEGIN_TEMPLATE
{
  "template_id": "fm.bounded.model.check.v0",
  "kind": "bounded_model_check_v0",
  "param_space": {
    "transition_formula_bits": {"choices": ["1111000011110000", "0101010101010101"]},
    "bound_k": {"int_range": [cite: 1, 14]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Formal Methods",
    "reference": "Biere et al 1999 Symbolic Model Checking without BDDs",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Bounded model checking unrolls a system transition relation into a boolean formula up to length k to exhaustively search for property violations using a SAT solver. A SURVIVED unsatisfiable verdict provides a mathematical guarantee that no counterexample exists up to length k, but it strictly does not license the claim that the system is safe at step k+1 unless a k-induction proof is also successfully completed."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Formal Methods
LACKS: An exhaustive constraint solving executor capable of proving mathematical unsatisfiability over an entire domain.
WHY: Formal methods provide rigorous guarantees by exhaustively exploring all paths up to a bound to ensure no counterexample exists for a specific transition relation. The bench's existing executors only perform single-point evaluations and random sampling walks, which can discover shallow bugs but fundamentally cannot prove their definitive absence.
SMALLEST_FORM: A deterministic symbolic executor kind that takes a bitstring representing a CNF formula and a bound integer, returning a guaranteed boolean scalar indicating satisfiability.
BLOCKS: Formal Methods
EVIDENCE: Biere et al. 1999, Symbolic Model Checking without BDDs [cite: 5, 15].
END_EXPANSION

## Search-Based Software Engineering

BEGIN_TEMPLATE
{
  "template_id": "sbse.hillclimb.search.v0",
  "kind": "sbse_hill_climb_v0",
  "param_space": {
    "initial_candidate_bits": {"choices": ["00000000", "11111111"]},
    "max_evaluations": {"int_range": [cite: 8]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Search-Based Software Engineering",
    "reference": "Harman and Jones 2001 Search-based software engineering",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "Search-based software engineering formulates software engineering problems as optimization tasks, navigating a fitness landscape using metaheuristics to find an optimal bitstring candidate. A SURVIVED verdict indicates that an adequate solution crossing the fitness threshold was discovered by the search, but it does not license the claim that the discovered solution is the global optimum or the only valid candidate available."
}
END_TEMPLATE

**Sources:**
1. [paperswelove.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELPG7KfVFsNNUNnU5SzJn-48SDL2XVSuOV1ig6M0BPFxRx-K1a_62D5f_fQp2tyFgPmQ6FBwFXCQNLdlYjj46Z2MOTbx0BlXKPSr8fk9WE-scmSEunGSSVa4p01zdwG6iNHNryvnFflC61NI6OQ54G662QxtrLD4TDQCctcB-8zCEBG_GhxM08ispND5PpT8ci)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_b1Sf8WEk5-9RR66RxHOsYiw0JQBMK8QbMMGtclj8iyd752hMh1e4xn6iVGrqZNzCPzV5nQ0LNtZOIMyuNeeXthgGJ0xP6Lux3j4PYaQ5UVnEEnYbTnh1KBVqjRvmJEVtKDFBn6MUZcx5LfAG5YzyijiFbclOVGDyjkIN1ejyc5VsmSK_EbeUrZMqJTSXB6bWTIHukiMMJWHnbbMnmasWVFJ7we0hoP67TLjOBWkziZmkDohd_XC2-1ILVzONWTZo)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHmXb_FQxkx2c2wGMt6JLd7lanqrcOsAjKlv3qmSBFwh5SnX3DaUSbgwQIEcqUV7kYjtIffXkzNGk3JfUO7QeY1QKvEdzUrgUWk-9CFUOV1yML-IMITBzu)
4. [tufts.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvPRGyfkJbBROoijnGM1BtHaxnlN1wTJZfzcKveVbLbQhr_xBtE03gPQmEZjQTcIjGTRpOdIux8d4-So5-gNdC60wRa7OAOAs8-hwEQ9c4py3zM9Qno9T3DnNSV5wwxua7_eqSWRn8h-1kHruJTnVK4MHUqrLKyvFFTdWGUQ==)
5. [papersflow.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdb6zYc7mS-6cCp-lwU0Pa7iIjqC7xOMBwVQ8qnZ7JMgyTsVaynh06nt7qgt0o3jQNeYv913hRnq6N72sIa0lHipFZmN4YlicRKbBdT3k9vkH1QOltiA622jQ0WVSgHnCjOFAS0jrEbfReBrTOPdMXB3xqE_igfGQSxOYzrY2y4QFsEVqMwCg73p4ys_L4SeUt)
6. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT_rzy80rRd4QPKgMRS1llEJ2Cs-kkcdFN7HFEG9WXLWkjQStvG6S1VVzo1RGdHGBGJxvYGGEvhN5pZELZPik5dGKN7A12DYu8LBAr98IdNPGzUs6iasPz0G65PftwFesIJU0bkWPl9HkPB56LBF_xTxyPdcHopANml2HJjT5W-MIuQAIHwHlFzaVPxFXs2B-1PbV-qs6pp3Y=)
7. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhpwl6HrSoe6sH4YgNbDqj2Q44UHwQE4rwxV5b11ZNV-1DgbPvL6C1SvMQGDIszufDJMrxNOjWUNY2jUEcp31c0um9ipBJ4-1mGUDd6ZOakTzUpQmXvI0Z9QkAsdF-Mjwe6yy7FmZ6GC5QlX2mcWv-w9DA9u91tcLhwILLn7ydTGWg8yXH2RXjmsd2Y1IJlqDVtf4fWaEILg==)
8. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmuGitU6NjTT_SBQSta2voFa7JuHPaflhbeUM5Ql6mmiclXr0sjUsQX__tvarp11jQzRSt5vlt0jByFUwbvdCOGACn8YwQE04ipOL-wBlOzXeYJBupYmTHjXNBUbbkAT9ObjZ8Ss_Wuv8WEGTrKg1v8OlRfuQ2BwA=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI5Jzsmgu3z3OqQtCmz3uh0_UoGWeZCl7fGmzsIMRqqBK60DRzOaHJg5Qu3sMvTFDG16bTqZn6AlDclJjNutcttD8PPjLv2EStxBXOqMGGdreKNW9owBgUTrEuBo0oNeGNsoMOeC61x5qvplEFdUf1cFSG9ogZDNvM-sZp9ViuPiVnDm9xAM6X0Q0AR4vVQtcCzMI5z35Ck9WXonq-Pys9MLisTe5cu6ZxkA==)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-2Q0HeaCm0YVjBc3H2qSIzONdSzzAolYDyv8qKgCkWX0FziuNvsg1TDDV2z1I4KuPNgns0EeEG19pDcE2qtT0238fohjmYP0ooliKGrkDOYKR8VbV_WqSscA57o4z)
11. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZNcn9R1-kkc7Q_JHJxrdtKSuWvGtycdYif1ZiSCxxHxtZXrHZKE_vy_GM-1PvjCKOf1eaudaqG-bFyruOOuRy6MNoFu1CrrNu8uOKflPMtpEgXez91TBoNzby1_q4W6s3-2PEzBm-yDPq6tQyEXeF9z9Vn9y7UALK-og=)
12. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUicgcxpDUcMphEflxRzoNVwIQu8NWKhwLUCYm9FsCyv-L0sDW8MuILwtpYiS4ORXHo47RdMmdzba7YQwpcVLNmWRqSFZTAJ5MBEl1-YYdK_rx6Ybt8fZEy0Sc1tPim-GOg-8cfbfA8e7B1KJi_A2Iqs_z0p3Py7gUt9SYuXJ3)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs4DdU6hRRS_Ud_l7Br45QCz-0zI_7jQ7wQdyYQfG-U5G2SmP-fyRLi9LT6tGh9EaZwc6QFcF6M6g-ztEC39YcSUCMdIOBspAtC6iDE6SXn6IE3UjVhnViIDLIi-iAVHohUF5CbGypMNBlYfJO7aTv0ytqqg==)
14. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA0xBM3DEgITGzmxkcrs6cFS3hrl-oBoTG49XBvIUffEM4GA3NGIC0nhl_QwNL2y0UHOb2x6s13SxgzacUcSJPcnJCYpXJi8qWWPOA3OQFLRuGfv4d_aVG93YHF6z8aUItFZEcQh_6fnX9k5TXltAd0NSqFX9OkDWSEUFk8yw5bT2XWL6-)
15. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoGWUga0MEs6CujujAiCruyJ9XoDID5tft2OKviENsjZxJybTFWKPkM7ZMlZIfBdTkBLmp8GrZcCVFJsD_OhudQCOI99Wo1JUcZcNf8nWWQZg5ewna1Ukut9fgOLbazw7rLOB7AozVQ-ehMPLhNcADi-tVcg==)

