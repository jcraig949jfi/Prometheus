# Prompt 06: Automated discovery systems

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpMU9kYW9QbkVJU2FqckVQclpYQi1ROBIXaTFPZGFvUG5FSVNhanJFUHJaWEItUTg
**Elapsed:** 365s

---

The following templates and expansion requests translate the methods of automated discovery systems into concrete specifications for the computational bench. The primary friction in porting these fields is their reliance on symbolic knowledge representation, closed-loop active learning, and baseline-comparative validation—none of which are currently expressible under the bench's strictly scalar, single-arm, sealed-specification constraints.

BEGIN_TEMPLATE
{
  "template_id": "bacon_equation_discovery.v0",
  "kind": "discover_equation_v0",
  "param_space": {
    "max_variables": {
      "int_range": [cite: 1, 2]
    },
    "heuristic_depth": {
      "int_range": [cite: 1, 3]
    }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Automated Scientific Discovery",
    "reference": "BACON: A production system that discovers empirical laws (Langley 1977)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a data-driven heuristic search can successfully identify an underlying empirical law from noisy observations. The field would run this to test the robustness of equation discovery algorithms. A SURVIVED verdict would indicate the system found a mathematical model with high explanatory power, but would NOT license the inference that the discovered equation represents the true physical causal mechanism."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Automated Scientific Discovery
LACKS: String-valued outcome rules to compare discovered symbolic representations against a target.
WHY: Automated discovery systems output symbolic knowledge (such as empirical equations or Lisp programs) rather than just scalar metrics. On the current bench, a rule can only perform a scalar comparison, meaning it cannot express a verdict on whether the system actually discovered the correct functional form (e.g., P*V=N*R*T), only whether its internal error metric was low.
SMALLEST_FORM: A new outcome rule operator STRING_MATCH that takes a target_string parameter, compares the executor's primary string output to this target, and adds a string_matched boolean field to the execution result.
BLOCKS: Automated Scientific Discovery, Machine Discovery
EVIDENCE: BACON (Langley 1977) and AM (Lenat 1977) both demonstrate that the fundamental output of early machine discovery is symbolic structures, which must be evaluated for structural or semantic correctness, not just numerical thresholds.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "am_concept_generation.v0",
  "kind": "evaluate_lisp_concept_v0",
  "param_space": {
    "initial_concepts": {
      "int_range": [cite: 3]
    },
    "agenda_steps": {
      "int_range": 
    }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Machine Discovery",
    "reference": "AM: Automated Mathematician (Lenat 1977)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the ability of a heuristic-driven agenda to combine elementary set-theoretic concepts into novel, mathematically interesting constructs. A SURVIVED verdict indicates the system generated concepts scoring above a predefined novelty threshold, but would NOT license the claim that the system understands the semantic meaning of the mathematical concepts it proposes."
}
END_TEMPLATE

BEGIN_TEMPLATE
{
  "template_id": "ai_scientist_training.v0",
  "kind": "train_llm_idea_v0",
  "param_space": {
    "idea_id": {
      "choices": [
        "nanoGPT_baseline",
        "grokking_variant",
        "diffusion_ablation"
      ]
    },
    "training_steps": {
      "int_range": 
    }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "AI Scientist systems",
    "reference": "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery (Lu et al. 2024)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether an LLM-generated codebase modification to a baseline machine learning training script results in successful execution and a measurable validation loss. The field runs this to validate if an AI can independently implement an architectural improvement. A SURVIVED verdict means the modified code compiled and achieved the target loss, but would NOT license the inference that the modification is conceptually novel or free of contamination from the LLM training data."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: AI Scientist systems
LACKS: Multi-arm comparison in outcome rules, allowing the result of one run to be compared directly against a baseline run.
WHY: AI Scientist systems validate their hypotheses by comparing the performance of a novel, AI-generated algorithm against a control baseline. Because the current bench's outcome rule is a single scalar comparison against a hardcoded value, it is impossible to express a verdict of whether the new idea actually outperformed the baseline.
SMALLEST_FORM: A new outcome rule operator GREATER_THAN_BASELINE that takes a baseline_run_id parameter and evaluates the current run's primary field against the same field from the baseline run, adding a baseline_comparison_result field to the execution result.
BLOCKS: AI Scientist systems
EVIDENCE: The AI Scientist (Lu et al. 2024) establishes that the system executes experiments and summarizes results by explicitly comparing the validation metrics of the newly proposed algorithm against the original template codebase.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "adam_yeast_growth.v0",
  "kind": "simulate_yeast_knockout_v0",
  "param_space": {
    "knockout_orf": {
      "choices": [
        "YHR090C",
        "YAL012W",
        "YBR218C"
      ]
    },
    "media_supplement": {
      "choices": [
        "none",
        "uracil",
        "histidine",
        "leucine"
      ]
    }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Robot Scientists",
    "reference": "The Automation of Science / Robot Scientist Adam (King et al. 2009)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment simulates the physical growth assay of a specific yeast strain knockout in defined media, which Adam used to infer gene-enzyme relationships. A SURVIVED verdict based on final optical density demonstrates that the given media supplement rescues the metabolic defect, but would NOT license the claim that the gene directly codes for the enzyme producing that supplement, as the rescue could occur via an alternative metabolic pathway."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Robot Scientists
LACKS: Closed-loop sequential parameter selection, where a repeat's payload is generated dynamically by an active learning agent observing previous repeats.
WHY: Both Robot Scientists and Self-Driving Labs fundamentally rely on closed-loop active learning to choose the next experiment to run, minimizing the search space rather than executing a pre-planned grid. The current bench forces all repeats to use the fixed parameters declared in the sealed specification, making autonomous optimization impossible.
SMALLEST_FORM: A new repeat order type active_learning that takes a surrogate_model parameter and a learning_rate parameter, and adds a dynamically generated chosen_parameters object field to the result of each repeat.
BLOCKS: Robot Scientists, Automated Experimentation
EVIDENCE: King et al. 2009 (Robot Scientist Adam) and MacLeod et al. 2020 (Ada self-driving laboratory) both explicitly establish that their systems generate the next experimental parameters autonomously in a closed loop after analyzing previous physical results.
END_EXPANSION

BEGIN_TEMPLATE
{
  "template_id": "ada_thin_film.v0",
  "kind": "synthesize_thin_film_v0",
  "param_space": {
    "dopant_ratio": {
      "int_range": 
    },
    "annealing_time_sec": {
      "int_range": [cite: 3]
    }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Automated Experimentation",
    "reference": "Self-driving laboratory for accelerated discovery of thin-film materials (MacLeod et al. 2020)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This tests the optimization of hole mobility in organic hole transport materials by varying doping ratios and annealing times. The field runs this to rapidly map the processing landscape for thin-film materials. A SURVIVED verdict confirms that a specific parameter pair exceeds a target pseudomobility threshold, but would NOT license the conclusion that this material formulation will be structurally stable or durable in a fully assembled perovskite solar cell device."
}
END_TEMPLATE

**Sources:**
1. [nae.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdfBZKqEFWaWX_04rivUFzbrjsXUyN0HaCRCdv51F5cpa7563-oT6QGDr01SYfCAWDkUoiNHiAt09cEjAZ1xDpO-yvFIc57tnMhJ__SrIro6KaL6nl05hfWKz-qC49KZfrkOsYmmU0plyRd-zd9lz1rkDqSarlv_OEZX6VQBmAekVJFmNQoeAt12AtQEVbRr6Ik0Po)
2. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA3ti-PCm7Q2aeXcBCtk1itk7g9pZgpcGONuPDRIgSyBbXfUqE9WvTzFyIGogLlU4vfPvBUa9wup_oYOjyY9RRqZv8hbEiyCqlXtM-2yIgddDVSjBUBbsaNQ==)
3. [case.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5WdlaH89JmNJd28kM0QRbeeivYZMFSbBQPflGoRtnHTAep4MWZTHFhrRSML4rjFCtg8ecX-WDFYaNJrm3-0iNgT8-9wj3yFciLqoH3J4kUhTe1kp-HCnCMIsmlLTAY4FDfBjviayGfsKpxqFmwRcMVR468N0A9C4=)

