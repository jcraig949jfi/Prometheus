# Prompt 11: Reasoning modes

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdabGFkYXNiek50elRqTWNQdGZ6T2lBVRIXWmxhZGFzYnpOdHpUak1jUHRmek9pQVU
**Elapsed:** 338s

---

# Computational Research Bench: Design Templates and Expansions for Reasoning Modalities

The following report analyzes the integration of five foundational reasoning modalities into a tightly constrained computational research bench. The bench, currently restricted to a single scalar comparison outcome, isolated state, and deterministic integer seed roots, poses significant structural barriers to representing complex cognitive paradigms. Because the bench prohibits multi-world comparisons, qualitative relational graphs, and multi-hypothesis evaluation, none of the target disciplines’ characteristic experiments can be honestly expressed using the existing three executors (`noop_v0`, `evaluate_bitstring`, `random_walk_v0`). Distorting these established methods to fit a bitstring evaluator or a one-dimensional walk would strip them of their semantic core. Therefore, in accordance with the design constraints, every field is provided with a new, strictly parameterized executor kind template, representing a mandatory expansion request. These are followed by three precisely defined structural capabilities the bench lacks, which currently block these fields from native execution.

## I. Abductive Reasoning

BEGIN_TEMPLATE
{
  "template_id": "abduce_set_cover.v0",
  "kind": "abduce_set_cover_v0",
  "param_space": {
    "manifestations_count": {"int_range": [cite: 1, 2]},
    "hypothesis_space_size": {"int_range": [cite: 3]},
    "causal_density": {"choices": ["low", "medium", "high"]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Abductive Reasoning",
    "reference": "Reggia, Nau, and Wang 1983 Diagnostic expert systems based on a set covering model",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment implements the set-covering model for diagnostic abductive reasoning. It measures the ability of the executor to find a parsimonious set of hypotheses that covers a given set of manifestations. A working researcher in abduction would run this to test if an algorithmic variation successfully minimizes the explanation size while maintaining complete coverage of the symptoms. A SURVIVED verdict based on a scalar check of the returned cover size would indicate that the system found an explanation of the target parsimony. However, it would NOT license the inference that the system found the exact true causal set, nor that the generated cover is unique, because the outcome rule can only verify the size of the output set, not its composition or semantic validity against a ground truth."
}
END_TEMPLATE

## II. Inductive Reasoning

BEGIN_TEMPLATE
{
  "template_id": "version_space_search.v0",
  "kind": "version_space_search_v0",
  "param_space": {
    "concept_attributes": {"int_range": [cite: 3, 4]},
    "training_examples": {"int_range": [cite: 5]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Inductive Reasoning",
    "reference": "Mitchell 1977 Version Spaces: A Candidate Elimination Approach to Rule Learning",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment tests the Candidate Elimination algorithm within a predefined hypothesis space, characteristic of foundational work on concept learning. It measures the number of surviving hypotheses in the version space after processing a sequence of positive and negative training examples. A SURVIVED verdict, triggered by the version space size dropping to exactly one, would license the claim that the algorithm successfully converged on a single consistent hypothesis. However, it would NOT license the inference that the learned hypothesis generalizes correctly to unseen data, nor would it confirm which specific boundaries shifted during the training, because the bench can only record the final scalar size of the version space rather than the structural trajectory of the hypothesis boundaries."
}
END_TEMPLATE

## III. Analogical Reasoning

BEGIN_TEMPLATE
{
  "template_id": "structure_mapping.v0",
  "kind": "structure_mapping_v0",
  "param_space": {
    "base_entities": {"int_range": [cite: 6, 7]},
    "target_entities": {"int_range": [cite: 6, 7]},
    "systematicity_bias": {"choices": ["enabled", "disabled"]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Analogical Reasoning",
    "reference": "Falkenhainer, Forbus, and Gentner 1989 The Structure-Mapping Engine: Algorithm and Examples",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This template instantiates the Structure-Mapping Engine to compute an analogical match between a base domain and a target domain. It measures the structural evaluation score of the maximal interpretation found by aligning relational predicates. Analogical reasoning researchers would run this to test how systematicity constraints affect the depth of the resulting match. A SURVIVED verdict asserting that the structural evaluation score exceeds a critical threshold would license the claim that a mathematically significant alignment was found between the two domains. It would NOT license the inference that the specific mapped correspondences are semantically meaningful, nor that the candidate inferences generated are valid in the target domain, because the bench's scalar outcome rule reduces the rich topological mapping to a single numerical score, blinding the experimenter to the actual content of the analogy."
}
END_TEMPLATE

## IV. Case-Based Reasoning

BEGIN_TEMPLATE
{
  "template_id": "cbr_retrieval_cycle.v0",
  "kind": "cbr_retrieval_cycle_v0",
  "param_space": {
    "case_base_size": {"int_range": },
    "feature_dimensions": {"int_range": [cite: 5]},
    "similarity_metric": {"choices": ["euclidean", "cosine", "knowledge_guided"]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Case-Based Reasoning",
    "reference": "Aamodt and Plaza 1994 Case-Based Reasoning: Foundational Issues, Methodological Variations, and System Approaches",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment isolates the retrieval phase of the Case-Based Reasoning cycle, focusing on fetching the most similar historical cases to a new target problem. It measures the top-1 similarity score when querying a simulated memory of past experiences. A researcher would use this to evaluate the accuracy of different similarity metrics under varying case base sizes. A SURVIVED verdict indicating that a case was retrieved with a similarity score above a designated threshold would license the claim that the retrieval mechanism successfully navigated the feature space. It would NOT license the inference that the retrieved case is actually reusable or that the adaptation phase would succeed, because the bench cannot feed the retrieved case forward into a secondary outcome test, nor can it persist the complex case structure into a broader retention archive."
}
END_TEMPLATE

## V. Automated Conjecture Generation

BEGIN_TEMPLATE
{
  "template_id": "automated_conjecture_hr.v0",
  "kind": "automated_conjecture_hr_v0",
  "param_space": {
    "initial_axioms": {"int_range": [cite: 3, 4]},
    "production_rules": {"choices": ["all", "restrictive"]},
    "search_steps": {"int_range": [cite: 3]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Automated Conjecture Generation",
    "reference": "Colton 2002 Automated Theory Formation in Pure Mathematics",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment models the HR system's theory formation loop, where novel mathematical concepts are invented and empirically evaluated to form conjectures. It measures the raw yield of non-trivial conjectures generated within a fixed number of search steps. A SURVIVED verdict based on generating a threshold number of conjectures would license the claim that the production rules are sufficiently productive over the given axioms. However, it would NOT license the inference that any of these conjectures are mathematically true, nor that they are interesting to a human, because the bench lacks an integrated automated theorem prover to verify the statements, and the scalar outcome rule cannot express the logical structure or novelty of the individual conjectures."
}
END_TEMPLATE

## VI. Required Bench Expansions

BEGIN_EXPANSION
FIELD: Case-Based Reasoning
LACKS: A mechanism to inject structured data payloads that are independent of the world's seed_root.
WHY: Case-Based Reasoning fundamentally relies on a historical archive of previously solved problems to retrieve from, and Inductive Reasoning requires a set of distinct positive and negative examples to learn from. On the current bench, everything must be deterministically derived from a single integer seed_root, meaning an experimenter cannot rigorously test an algorithm against a controlled, independent dataset without conflating the data with the world state. No workaround exists because encoding a dataset into the executor's source code violates the requirement that the bench executes sealed specifications where inputs are strictly defined by parameters.
SMALLEST_FORM: A new field "dataset_uri" in the specification that accepts a string pointer to an external structured file, and a corresponding "dataset_hash" in the result record to ensure reproducibility.
BLOCKS: Case-Based Reasoning, Inductive Reasoning
EVIDENCE: Aamodt and Plaza's (1994) foundational CBR cycle explicitly requires a memory of past cases, and Mitchell's (1977) Version Space framework explicitly operates over a provided set of training instances.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Analogical Reasoning
LACKS: The ability to instantiate a world as a relational graph of entities and predicates rather than a single integer.
WHY: Analogical Reasoning operates by aligning the structural, relational connections between two domains, prioritizing constraints like parallel connectivity and systematicity. The current bench only provides an integer seed_root, which cannot natively represent the necessary predicate-argument structures. While one could theoretically encode a graph into a bitstring, doing so obscures the structural mapping mechanics and forces the executor to decode the representation, violating the methodological focus of the field.
SMALLEST_FORM: A new world object type "relational_graph" that takes a list of nodes and a list of directed edges with predicate labels, adding a "graph_hash" to the result record.
BLOCKS: Analogical Reasoning
EVIDENCE: Falkenhainer, Forbus, and Gentner's (1989) Structure-Mapping Engine fundamentally operates on predicate calculus representations of domains to compute alignments.
END_EXPANSION

BEGIN_EXPANSION
FIELD: Abductive Reasoning
LACKS: An outcome rule operator capable of evaluating whether a specific target element is a member of the executor's returned set.
WHY: Abductive Reasoning systems aim to find an explanation set that includes the true underlying cause of an observation, and Automated Conjecture Generation systems produce sets of logical statements that must be evaluated for specific target theorems. The current bench only allows a single scalar comparison, forcing these methods to output just the size of their sets or an aggregate score. This strips away the semantic core of the methods, as it is impossible to verify if the correct hypothesis or theorem was actually generated.
SMALLEST_FORM: An operator "CONTAINS" for the outcome rule that evaluates whether a predefined string or integer is present in a list returned by the work payload.
BLOCKS: Abductive Reasoning, Automated Conjecture Generation
EVIDENCE: Reggia's (1983) Set-Covering Model requires verifying that the inferred cover contains the correct causative disorders, and Colton's (2002) HR system measures success by whether its generated conjecture set includes recognized theorems.
END_EXPANSION

**Sources:**
1. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZLNUPoM7ZU18GPAUcSmCKrAeWdi6xpO4WkYt-k5m3hAVvJmr3UcD86duEjgJcbLU1AxgG2OPYQB2OMNYk9Bk92I20RYESPNa7DIi-Th3aFNVk0oCtNT2xiI7n9cxfELU9wmCB)
2. [supersummary.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6Iq62i-spbTGWxKx8o5IVUToZOVQ6VBF0vp5QJTdueQQrfRZ01YnWAVemPhpy8-qcomzA2phMACBDWU8WDYPTujU-8kSFhK17IFaJnmPLfHqcvJ_FVyNMg0n0DLg8FG1e4aw5Pb5r8MoIYA==)
3. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQFJwo1kEJK193WFvWB1yhm7o3050wVpmMm-ox1BsbcjX3YycoAhFjp2tEia4cWVZ49zACMajDAQ_xDqN3pX1JDLJkXn9TvWWiHjS1dzVSG82wM_-Rk71Mpg11qp9S15rp4dwfhXoefg2Q9GijYHYAmA==)
4. [unipv.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0lG4QdXfwnLE_3FsbjVlbpt4IGdPS7pZcGXUHRhPVqX69s9O-G4lIQz9SNrGekymMSqHyo37SOdd2QTsRYjusCexE5FyEXAjYfRL0L86KVKPLteA4jSbNdCkyEmE8A3yIqzJmfLeuhSFlhfQMJ4TOppoTFvVS68mXRE7yzCrz)
5. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEssf713Fm02eIC6umd4_So068fCqGGvvWpIMJ8dnpx9J1_L1KvrmKWRSAfiaSrkHpx94WbrSbVyr8nhChpGJyrljf3WPgcPdLE-TFcG8W_3ShhnT-j42Ps5f_nnPmFEVh7ud0W8IMH1bwua6Hxk5kOHVY=)
6. [unm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFyj-3CZSI-hUlsKe-5x4tybunaVdteaXcWdbSqNKUTds_B1DvtLOPAzsIgWvDEUcTmBQjsKRcmeXmQ--XwoFYjYlFkJpacW-CTRNgZscOyTLTpD5VDtONuKOBxUWsY7F-r0cPkAc-a4tG5vSCisKbBUyzf1wEBDXT1wP3-1GatbTgFkOh3UkCKuE5yA==)
7. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjphKLtxwwZ2RMBGgb--y0EP8nIJetbdkaKAUjSewCQ6P-ku6Poqfun9OybFs6tkysrJXFiUDIFb65ahVbTqr08ccGPUv-roP-LU9Ssxd0gtv2f2YgF16vgTelalA=)

