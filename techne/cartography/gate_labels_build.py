"""Build the reference labels for the measurement qualification gate.

Each entry is (bottleneck, representation_family, selection_family, evaluation_regime), and
each coordinate carries one of the five statuses. Judgments were made from the blind evidence
dump (title, abstract, targeted method/selection/evaluation passages) with the frozen tagger's
output not consulted.

NOTATION
    V(value, cite)      VALUE
    M([values], why)    MULTI_VALUE -- forcing one destroys information
    OM(concept, cite)   ONTOLOGY_MISSING -- concept is identifiable, no frozen value fits
    EA(needed)          EVIDENCE_AMBIGUOUS -- full text does not decide
    OOS(why)            OUT_OF_SCOPE -- the domain gate should not have admitted it

THE DISTINCTION THE GATE TURNS ON. ONTOLOGY_MISSING convicts the ontology; EVIDENCE_AMBIGUOUS
exonerates it. A paper whose mechanism I can name but cannot express is the first. A paper
whose mechanism I cannot determine even from full text is the second. Anything I could not cite
a passage for defaults to EVIDENCE_AMBIGUOUS.
"""
from __future__ import annotations

import json
import pathlib

CARTO = pathlib.Path(__file__).resolve().parent
OUT = CARTO / "gate_reference_labels.json"


def V(value, cite):
    return {"status": "VALUE", "value": value, "evidence": cite}


def M(values, why):
    return {"status": "MULTI_VALUE", "values": values, "why_forcing_destroys": why}


def OM(concept, cite):
    return {"status": "ONTOLOGY_MISSING", "concept_present": concept, "evidence": cite}


def EA(needed):
    return {"status": "EVIDENCE_AMBIGUOUS", "evidence_required": needed}


def OOS(why):
    return {"status": "OUT_OF_SCOPE", "why_gate_admitted": why}


#: The recurring ontology gaps, named once so the packet can count them.
GAP_VECTOR = ("fixed-length numeric vector genome (binary or real-valued). The frozen "
              "representation axis offers discrete_program, graph_circuit, continuous_neural, "
              "hybrid_differentiable, symbolic_expression. A bitstring for knapsack or a "
              "100-dimensional real vector for Rastrigin is none of these -- continuous_neural "
              "means neural WEIGHTS, not any real vector.")
GAP_BO = ("Bayesian optimisation: candidates chosen by maximising an acquisition function over "
          "a surrogate posterior. Not scalar_fitness, not gradient, not exact_search.")
GAP_PARETO = ("multi-objective / Pareto-front selection. The frozen selection axis has no value "
              "for non-scalar dominance-based selection.")
GAP_SPARSE = ("sparse regression / regularised model selection (L1, elastic net). Selection is "
              "by a penalty on a continuous coefficient vector, not by any listed mechanism.")
GAP_MDL = ("information-criterion model selection (minimum description length, Bayesian "
           "evidence). Not a fitness, not a test suite.")
GAP_LLM = ("LLM prompting as the candidate-proposal mechanism. Recorded as TX-005 and still "
           "absent from the frozen ontology.")
GAP_NOSEARCH = ("the paper reports no search or learning mechanism of its own -- it is a "
                "toolkit, dataset, benchmark, survey or theory paper. The frozen axes assume "
                "every in-scope paper performs a search.")

LABELS = {
 # -------- evolutionary computation ------------------------------------------------------
 "2605.28353": {  # CGP recombination on SRBench
   "bottleneck": M(["B1_REPRESENTATION", "B2_CREDIT_SEARCH"],
                   "the paper studies recombination OPERATORS, which are simultaneously a "
                   "statement about legal edits (B1) and about search efficiency (B2)"),
   "representation_family": V("graph_circuit", "'genotype encodes the program in terms of a "
                              "list of integers that describe the functions and connections of "
                              "the corresponding graph'"),
   "selection_family": V("scalar_fitness", "'tournament selection was adapted to run "
                         "recombination-based CGP'"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarking platform for symbolic regression' "
                          "(SRBench)")},
 "1001.1889": {  # GA with social interaction, knapsack
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a social term added to the fitness "
                   "used for selection"),
   "representation_family": OM(GAP_VECTOR, "'encoded as binary strings: a value of 1 indicates "
                               "that an object is placed in the knapsack'"),
   "selection_family": V("scalar_fitness", "'Selection (or reproduction) of a new generation'"),
   "evaluation_regime": V("scalar_objective", "'objective function, and f(x) is a social term "
                          "... included in the fitness function'")},
 "2008.03649": {  # Code Building GP
   "bottleneck": V("B1_REPRESENTATION", "the contribution is a representation able to express "
                   "non-primitive polymorphic types"),
   "representation_family": V("discrete_program", "code-building GP produces source programs"),
   "selection_family": V("scalar_fitness", "'parent selection strategy is used to pick "
                         "individuals for variation'"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarks that use non-primitive, polymorphic "
                          "data types as well as some standard program synthesis benchmarks'")},
 "2209.13233": {  # GP-based evolutionary deep learning, image classification
   "bottleneck": V("B1_REPRESENTATION", "the contribution is an evolved program representation "
                   "for image features"),
   "representation_family": V("discrete_program", "GP trees over image operators"),
   "selection_family": V("scalar_fitness", "'Elitism Crossover Mutation ... selection method "
                         "and new individuals are generated using genetic operators'"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarks including object classification, "
                          "digit recognition, medical image classification'")},
 "2004.11018": {  # Semantically-oriented mutation in CGP
   "bottleneck": V("B1_REPRESENTATION", "the contribution is a mutation operator conditioned on "
                   "phenotype semantics -- squarely a statement about legal edits"),
   "representation_family": V("graph_circuit", "CGP genotype/phenotype over circuit graphs"),
   "selection_family": V("scalar_fitness", "CGP (1+lambda) selection on a fitness value"),
   "evaluation_regime": V("fixed_test_suite", "'evaluated on Boolean problems'")},
 "2107.09484": {  # friction system SR
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the paper's problem is what counts as an accurate "
                   "model of a physical system"),
   "representation_family": V("symbolic_expression", "symbolic regression expressions"),
   "selection_family": M(["scalar_fitness"],
                         "GP fitness is used, but the paper's comparison arm trains an ANN and "
                         "a random forest by gradient/ensemble methods; a single value hides "
                         "that two selection regimes are being compared"),
   "evaluation_regime": V("scalar_objective", "predictive accuracy against measured data")},
 "2504.07152": {  # evolutionary generation of surreal numbers for benchmarking
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the paper generates BENCHMARK DATA -- its subject is "
                   "the evaluation environment itself"),
   "representation_family": OM(GAP_VECTOR, "surreal-number ensembles represented as weighted "
                               "sets, not a program, circuit, network or expression"),
   "selection_family": OM("weight-based ensemble construction rather than selection: 'it is "
                          "more mathematically tractable to use a simple weight and derive the "
                          "ensemble properties than to approach this as fitness'", "as quoted"),
   "evaluation_regime": V("fixed_test_suite", "'benchmark datasets where we can analyse and "
                          "control features of the resulting test sets'")},
 "2109.13110": {  # evolving EAs using linear GP
   "bottleneck": V("B2_CREDIT_SEARCH", "the evolved object IS a search algorithm"),
   "representation_family": V("discrete_program", "'Every LGP chromosome encodes an EA' -- a "
                              "linear instruction sequence"),
   "selection_family": V("scalar_fitness", "'tournament and are recombined with a fixed "
                         "crossover probability'"),
   "evaluation_regime": V("fixed_test_suite", "'test set consists in some other well-known "
                          "benchmarking problems'")},
 "2504.10253": {  # TinyverseGP benchmarking framework
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is a cross-domain benchmarking "
                   "framework"),
   "representation_family": M(["discrete_program", "graph_circuit", "symbolic_expression"],
                              "the framework's whole point is that it hosts MULTIPLE GP "
                              "representations side by side; forcing one erases the paper's "
                              "central claim"),
   "selection_family": EA("the framework supports 'selection mechanisms, island models and "
                          "local search' generically; no single selection regime is the "
                          "paper's own"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarking initiatives are fragmented ... "
                          "performance is not measured across the different domains'")},

 # -------- program synthesis ---------------------------------------------------------------
 "1004.4609": {  # reversible/quantum circuit synthesis cost metrics
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is new COST METRICS -- what counts as "
                   "a good circuit"),
   "representation_family": V("graph_circuit", "reversible and quantum logic circuits"),
   "selection_family": EA("the paper evaluates existing synthesis approaches (Reed-Muller, BDD) "
                          "rather than proposing a selection mechanism; which one drives the "
                          "search is not stated in the extracted text"),
   "evaluation_regime": V("scalar_objective", "'measuring the overhead needed to synthesize "
                          "circuits with an optimal NNC value of 0'")},
 "2107.14449": {  # Synth-by-Reg, medical image registration
   "bottleneck": OOS("'synthesis' here means IMAGE synthesis for inter-modality registration, "
                     "not program synthesis. The domain gate admitted it because it is "
                     "computational (CNN, loss functions) and the retrieval query contained "
                     "'synthesis'. It performs no search over programs or structures."),
   "representation_family": OOS("as above"),
   "selection_family": OOS("as above"),
   "evaluation_regime": OOS("as above")},
 "1807.03168": {  # NAPS dataset
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is a dataset defining the task"),
   "representation_family": V("discrete_program", "programs in a UAST language with I/O "
                              "examples"),
   "selection_family": OM(GAP_NOSEARCH, "a dataset paper; no selection mechanism is proposed"),
   "evaluation_regime": V("fixed_test_suite", "'accompanied by input/output examples'")},
 "2108.08724": {  # SyGuS recursive synthesis
   "bottleneck": V("B1_REPRESENTATION", "the contribution extends the SyGuS grammar to "
                   "recursive functions -- what is expressible"),
   "representation_family": V("discrete_program", "'search space of SyGuS to include recursive "
                              "functions'"),
   "selection_family": V("exact_search", "SyGuS solvers enumerate/deduce against constraints"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarks that demonstrate our approach is "
                          "able to solve SyGuS queries that require recursion'")},
 "1711.03243": {  # selecting representative examples for synthesis
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is choosing WHICH EXAMPLES define the "
                   "task -- the evaluator's content"),
   "representation_family": V("discrete_program", "'encoded as constraints and solved with a "
                              "constraint solver'"),
   "selection_family": V("exact_search", "CEGIS with a constraint solver"),
   "evaluation_regime": V("fixed_test_suite", "input-output example sets; 'We evaluate the "
                          "program on the set of inputs'")},
 "1411.0481": {  # synthesis from formal partial abstractions
   "bottleneck": EA("a position/architecture paper on model-driven development; no experiment "
                    "or mechanism is described in the extracted text"),
   "representation_family": EA("no representation is specified"),
   "selection_family": OM(GAP_NOSEARCH, "position paper; no search mechanism"),
   "evaluation_regime": EA("no evaluation is described")},
 "1807.07022": {  # deductive synthesis of heap-manipulating programs
   "bottleneck": V("B1_REPRESENTATION", "the contribution is a deductive rule system over "
                   "Separation Logic specifications"),
   "representation_family": V("discrete_program", "imperative programs with pointers"),
   "selection_family": V("exact_search", "deductive proof search over synthesis rules"),
   "evaluation_regime": V("formal_verifier", "pre/postconditions in Separation Logic are the "
                          "success criterion")},
 "2106.07175": {  # combine per-example solutions, neural program synthesis
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a two-stage credit structure: solve "
                   "per example, then combine"),
   "representation_family": M(["discrete_program", "continuous_neural"],
                              "the searched object is a program; the search is driven by a "
                              "learned neural module. Forcing one hides that this is a hybrid, "
                              "and hybrid_differentiable does not fit -- the program is not "
                              "relaxed, a network predicts it"),
   "selection_family": V("gradient", "'objective is to learn the parameters of the CA module'"),
   "evaluation_regime": V("fixed_test_suite", "'test cases first, and later modifying the "
                          "program to incorporate other corner cases'")},
 "2604.13290": {  # presynthesis, abstract semantics granularity
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is pruning granularity in the search"),
   "representation_family": V("discrete_program", "search-based program synthesis"),
   "selection_family": V("exact_search", "sound pruning over enumerated programs"),
   "evaluation_regime": V("formal_verifier", "'specification, such that they can be safely "
                          "pruned away'")},

 # -------- quality diversity --------------------------------------------------------------
 "2009.08438": {  # MAP-Elites vs PPO
   "bottleneck": V("B2_CREDIT_SEARCH", "the paper compares two credit-assignment families"),
   "representation_family": V("continuous_neural", "robot controllers as neural policies"),
   "selection_family": M(["archive_qd", "gradient"],
                         "the entire paper is a HEAD-TO-HEAD between MAP-Elites and PPO; "
                         "forcing one value erases the comparison that is the paper"),
   "evaluation_regime": V("behavioral_descriptor", "MAP-Elites archive over behaviour cells")},
 "2305.07767": {  # QD benefits without diversity?
   "bottleneck": V("B2_CREDIT_SEARCH", "the question is whether diversity is doing the work in "
                   "selection"),
   "representation_family": EA("the paper is a methodological argument across domains; no "
                               "single representation is its own"),
   "selection_family": OM(GAP_PARETO, "'individuals are selected based on the multi-objective "
                          "optimization algorithm being used' -- dominance-based selection has "
                          "no frozen value"),
   "evaluation_regime": V("behavioral_descriptor", "QD archives over behaviour")},
 "2107.04964": {  # Differential MAP-Elites
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a variation/selection scheme "
                   "(Differential Evolution inside CVT-MAP-Elites)"),
   "representation_family": OM(GAP_VECTOR, "'benchmarks and applications where the chromosome "
                               "is expressed as a vector of real numbers'"),
   "selection_family": V("archive_qd", "CVT-MAP-Elites archive"),
   "evaluation_regime": V("behavioral_descriptor", "'a behavior function b(x), the dimension of "
                          "a behavior space'")},
 "1807.02397": {  # QD through surprise
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a divergent-search signal"),
   "representation_family": EA("multiple domains; the extracted text does not fix one"),
   "selection_family": M(["novelty", "archive_qd"],
                         "surprise search is contrasted WITH novelty search and combined with "
                         "QD archives; the paper's claim is about the difference between them"),
   "evaluation_regime": V("behavioral_descriptor", "novelty/surprise measured in behaviour "
                          "space")},
 "2007.05352": {  # Multi-Emitter MAP-Elites
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is emitter selection driving search"),
   "representation_family": OM(GAP_VECTOR, "'genotype (100 dimensions and bounded between "
                               "-5.12...)' for Rastrigin"),
   "selection_family": V("archive_qd", "MAP-Elites with emitters"),
   "evaluation_regime": V("behavioral_descriptor", "archive over behaviour descriptors")},
 "2005.04320": {  # BOP-Elites
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is how the next sample is chosen"),
   "representation_family": OM(GAP_VECTOR, "continuous input space with user-chosen feature "
                               "functions"),
   "selection_family": OM(GAP_BO, "'acquisition function ... a calculation performed on the "
                          "posterior distribution, which attempts to predict the value of "
                          "sampling new points'"),
   "evaluation_regime": V("behavioral_descriptor", "'enforcing behavioural diversity of the "
                          "points over one or more interpretable, user chosen, feature "
                          "functions'")},
 "2211.13742": {  # QD neuroevolution performance
   "bottleneck": V("B2_CREDIT_SEARCH", "the paper assesses QD algorithms as search procedures"),
   "representation_family": V("continuous_neural", "'the genotype space equals the possible "
                              "weights of a neural network with two hidden layers'"),
   "selection_family": V("archive_qd", "QD methods under test"),
   "evaluation_regime": V("behavioral_descriptor", "QD benchmark descriptors")},
 "2211.02193": {  # QD neuroevolution benchmark suite
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is a benchmark suite defining tasks, "
                   "descriptors and fitness"),
   "representation_family": V("continuous_neural", "'genotypes are the parameters of the neural "
                              "network'"),
   "selection_family": V("archive_qd", "QD archive metrics"),
   "evaluation_regime": V("behavioral_descriptor", "'the definition of tasks, environments, "
                          "behavioral descriptors, and fitness'")},
 "1906.05175": {  # QD dungeon design, mixed initiative
   "bottleneck": V("B3_TELEOLOGY_EVAL", "a human designer is inside the evaluation loop"),
   "representation_family": OM(GAP_VECTOR, "dungeon level layouts as tile grids -- not a "
                               "program, circuit, network or expression"),
   "selection_family": V("archive_qd", "'uses the MAP-Elites algorithm, an illumination "
                         "algorithm which divides the population into a number of cells'"),
   "evaluation_regime": M(["behavioral_descriptor", "coevolved_moving"],
                          "MAP-Elites cells define the descriptor, but a human edits the "
                          "objective interactively during the run, so the evaluator is "
                          "non-stationary. Neither value alone is faithful")},

 # -------- mechanistic interpretability ---------------------------------------------------
 "2511.14465": {  # nnterp toolkit
   "bottleneck": OM(GAP_NOSEARCH, "a standardised software interface; no search, no learning "
                    "mechanism of its own"),
   "representation_family": V("continuous_neural", "transformer internals"),
   "selection_family": OM(GAP_NOSEARCH, "no selection mechanism"),
   "evaluation_regime": V("fixed_test_suite", "'test suite enabling local verification of "
                          "custom models'")},
 "2504.19475": {  # Prisma toolkit
   "bottleneck": OM(GAP_NOSEARCH, "an open-source framework and pretrained weights"),
   "representation_family": V("continuous_neural", "vision transformers"),
   "selection_family": OM(GAP_NOSEARCH, "no selection mechanism"),
   "evaluation_regime": EA("the extracted text describes tooling, not an evaluation regime")},
 "2402.03855": {  # challenges in interpreting representations
   "bottleneck": V("B1_REPRESENTATION", "the paper's subject is hidden representations as the "
                   "unit of analysis"),
   "representation_family": V("continuous_neural", "hidden activations"),
   "selection_family": OM(GAP_NOSEARCH, "a position/challenges paper"),
   "evaluation_regime": EA("no single evaluation regime; the paper argues about what evaluation "
                           "should be")},
 "2511.09432": {  # equivariant SAEs
   "bottleneck": V("B1_REPRESENTATION", "the contribution is an SAE architecture constrained to "
                   "be group-equivariant -- a representation claim"),
   "representation_family": V("continuous_neural", "SAE latents over activations"),
   "selection_family": V("gradient", "'we train our SAEs to learn G-invariant latents'"),
   "evaluation_regime": EA("'ground truth features are known, evaluating interpretability is an "
                           "open problem' -- the paper states its own evaluation is unsettled")},
 "2606.16939": {  # scalable circuit learning
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a cheaper way to attribute "
                   "behaviour to components"),
   "representation_family": V("graph_circuit", "'Our circuits can capture causal relations "
                              "between features'"),
   "selection_family": OM("causal intervention / attribution patching: components are credited "
                          "by ablating them and measuring the effect on model output. Recorded "
                          "as TX-003 and still absent from the frozen ontology.",
                          "intervention-based circuit learning, as stated in the abstract"),
   "evaluation_regime": OM("faithfulness of an extracted subgraph to a reference model. The "
                           "frozen evaluation axis has no value for 'reproduces the behaviour "
                           "of another model'.", "'accurately capturing circuits involving LLM "
                           "components'")},
 "2604.14477": {  # faithful MI for vision
   "bottleneck": V("B2_CREDIT_SEARCH", "'selection criterion for individual edges'"),
   "representation_family": V("graph_circuit", "edge-based circuits"),
   "selection_family": OM("causal intervention over graph edges (as above)",
                          "'selection criterion for individual edges'"),
   "evaluation_regime": OM("faithfulness to a reference model, measured as classification "
                           "accuracy of the extracted circuit", "'we evaluate faithfulness in "
                           "terms of classification accuracy'")},
 "2409.13714": {  # TracrBench
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is ground-truth testbeds for "
                   "evaluating interpretability methods"),
   "representation_family": V("continuous_neural", "compiled transformers"),
   "selection_family": OM(GAP_LLM, "'we select 121 simple, sequence-to-sequence algorithms' "
                          "generated with LLM assistance"),
   "evaluation_regime": OM("ground-truth weight-to-function mappings as the evaluator. Closest "
                           "frozen value is formal_verifier, but nothing is verified -- the "
                           "mapping is known by construction.",
                           "'ground truth mappings between model weights and their functional "
                           "roles'")},
 "2511.08854": {  # stochastic parameter decomposition for transformers
   "bottleneck": V("B1_REPRESENTATION", "the contribution decomposes models in PARAMETER space"),
   "representation_family": V("continuous_neural", "transformer parameters"),
   "selection_family": V("gradient", "'we train on a coefficient-weighted sum of them'"),
   "evaluation_regime": OM("faithfulness of a decomposition to the original model",
                           "'objective is to align the representation of token n with the "
                           "positional encoding of n+1'")},
 "2304.14997": {  # ACDC, automated circuit discovery
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution automates the attribution procedure"),
   "representation_family": V("graph_circuit", "subgraphs of a transformer"),
   "selection_family": OM("activation patching / causal intervention to select edges (TX-003)",
                          "'they apply activation patching to find which abstract neural "
                          "network units are involved in the behavior'"),
   "evaluation_regime": OM("KL divergence between the model and the subgraph -- faithfulness to "
                           "a reference, not a test suite or an objective",
                           "'we evaluate H by computing the KL divergence "
                           "DKL(G(xi)||H(xi,x'i))'")},

 # -------- neurosymbolic -------------------------------------------------------------------
 "2506.02483": {  # NSAR, LLM + symbolic facts
   "bottleneck": V("B1_REPRESENTATION", "the contribution is extracting symbolic facts and "
                   "generating executable code as an intermediate representation"),
   "representation_family": M(["discrete_program", "continuous_neural"],
                              "an LLM (neural) emits Python (program) which is then executed; "
                              "hybrid_differentiable does not fit because nothing is relaxed"),
   "selection_family": OM(GAP_LLM, "the LLM proposes the code; no listed selection mechanism "
                          "applies"),
   "evaluation_regime": V("fixed_test_suite", "'We evaluate the proposed approach on a question "
                          "answering task'")},
 "2505.20313": {  # reasoning in neurosymbolic AI (book chapter)
   "bottleneck": V("B1_REPRESENTATION", "the chapter is about how logic is represented in an "
                   "energy-based network"),
   "representation_family": M(["continuous_neural", "symbolic_expression"],
                              "the whole subject is the correspondence between a logical "
                              "encoding and a neural energy function; forcing one erases the "
                              "chapter's thesis"),
   "selection_family": OM(GAP_NOSEARCH, "a survey/chapter; no search mechanism of its own"),
   "evaluation_regime": EA("benchmarks are discussed generally, none is the chapter's own")},
 "2601.01982": {  # ChaosBench-Logic
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution is a benchmark"),
   "representation_family": V("symbolic_expression", "first-order logic ontology over dynamical "
                              "systems"),
   "selection_family": OM(GAP_LLM, "LLMs are the systems under test; no selection mechanism"),
   "evaluation_regime": V("fixed_test_suite", "'a benchmark that evaluates LLM reasoning across "
                          "30 diverse dynamical systems'")},
 "2509.03644": {  # Embodied-LM, image schemas
   "bottleneck": V("B1_REPRESENTATION", "the contribution is grounding reasoning in schematic "
                   "representations"),
   "representation_family": OM("image-schema structures -- neither a program, a circuit, a "
                               "network, a relaxation, nor a symbolic expression in the "
                               "algebraic sense", "'schematic representations based on image "
                               "schemas'"),
   "selection_family": OM(GAP_LLM, "'selection function could be designed based on the "
                          "identified image schemas' -- proposed, not implemented"),
   "evaluation_regime": V("fixed_test_suite", "'We evaluated our approach on the "
                          "LogicalDeduction dataset'")},
 "2507.09854": {  # model-grounded symbolic AI, metatuning
   "bottleneck": V("B1_REPRESENTATION", "reinterpreting instruction-tuned LLMs as a symbolic "
                   "substrate"),
   "representation_family": V("continuous_neural", "LLM parameters and activation subspaces"),
   "selection_family": V("gradient", "metatuning the model"),
   "evaluation_regime": V("fixed_test_suite", "'the Maths 500 Dataset'")},
 "2504.19354": {  # neurosymbolic association rule mining
   "bottleneck": V("B1_REPRESENTATION", "the contribution compresses the rule space"),
   "representation_family": M(["symbolic_expression", "continuous_neural"],
                              "logical rules learned through an autoencoder; the paper's point "
                              "is the pairing"),
   "selection_family": V("gradient", "'We train our autoencoder'"),
   "evaluation_regime": EA("the extracted text does not fix the evaluation regime")},
 "1909.09065": {  # explainable neural-symbolic visual reasoning
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the paper argues about how explanations should be "
                   "judged"),
   "representation_family": EA("a discussion paper; no representation is its own"),
   "selection_family": OM(GAP_NOSEARCH, "position paper"),
   "evaluation_regime": EA("the paper's subject is that no consensus evaluation exists")},
 "2506.21797": {  # why NNs discover symbolic structures (theory)
   "bottleneck": V("B1_REPRESENTATION", "the subject is emergence of discrete structure from "
                   "continuous parameters"),
   "representation_family": V("continuous_neural", "neural parameters lifted to a measure "
                              "space"),
   "selection_family": V("gradient", "Wasserstein gradient flow"),
   "evaluation_regime": OM(GAP_NOSEARCH, "a theoretical framework; no empirical evaluation "
                           "regime is reported")},
 "2507.09751": {  # sound and complete neurosymbolic reasoning with LLM
   "bottleneck": V("B1_REPRESENTATION", "an LLM is placed inside the interpretation function of "
                   "a paraconsistent formal semantics"),
   "representation_family": M(["symbolic_expression", "continuous_neural"],
                              "the contribution is precisely the coupling of a formal semantics "
                              "with an LLM interpretation function"),
   "selection_family": OM(GAP_LLM, "the LLM supplies interpretations; no listed mechanism fits"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarks derived from short-form factuality "
                          "benchmarks'")},

 # -------- symbolic regression (NOTE: unchartered sixth stratum, see INC-001) --------------
 "1905.07510": {  # SpaRTA turbulence closure
   "bottleneck": V("B1_REPRESENTATION", "models are built from a library of candidate tensor "
                   "polynomials"),
   "representation_family": V("symbolic_expression", "'models are written as tensor polynomials "
                              "and are built from a library of candidate functions'"),
   "selection_family": OM(GAP_SPARSE, "'model selection using sparse-regression techniques' "
                          "(elastic net)"),
   "evaluation_regime": V("fixed_test_suite", "'cross-validation of the resulting models' over "
                          "CFD test cases")},
 "2512.15920": {  # intro to SR in the physical sciences (editorial)
   "bottleneck": OM(GAP_NOSEARCH, "an editorial introducing a special issue"),
   "representation_family": V("symbolic_expression", "symbolic regression"),
   "selection_family": EA("multiple approaches are surveyed; none is the article's own"),
   "evaluation_regime": EA("no evaluation of its own")},
 "2506.15881": {  # T-SHRED
   "bottleneck": V("B1_REPRESENTATION", "SINDy-style symbolic regularisation inside a neural "
                   "decoder"),
   "representation_family": M(["continuous_neural", "symbolic_expression"],
                              "an RNN/MLP with a symbolic-regression regulariser; the coupling "
                              "is the contribution"),
   "selection_family": V("gradient", "'we train the SHRED models'"),
   "evaluation_regime": V("scalar_objective", "'test set RMSE'")},
 "2605.31276": {  # neuro-symbolic nitrogen fertilizer curves
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the objective is discovering site-specific functional "
                   "relationships under epistemic uncertainty"),
   "representation_family": V("symbolic_expression", "parametric response curves"),
   "selection_family": EA("the extracted text does not identify the search mechanism"),
   "evaluation_regime": V("scalar_objective", "'objective is the discovery of accurate "
                          "mathematical equations'")},
 "2304.06333": {  # priors for symbolic regression
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a non-uniform prior over functions "
                   "used in model selection"),
   "representation_family": V("symbolic_expression", "symbolic models"),
   "selection_family": OM(GAP_MDL, "'When performing Bayesian model selection, one begins with "
                          "a set of candidate models' and 'minimum description length'"),
   "evaluation_regime": V("fixed_test_suite", "'benchmarks and a real-world dataset from the "
                          "field of cosmology'")},
 "2511.08424": {  # constitutive models for aluminium alloys
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the target is a process-structure-property relation"),
   "representation_family": V("symbolic_expression", "equations from Pyoperon"),
   "selection_family": OM(GAP_PARETO, "'Pyoperon produces a set of the Pareto-optimal "
                          "expressions from the final population'"),
   "evaluation_regime": V("fixed_test_suite", "'We evaluated each expression on the CV hold-out "
                          "set'")},
 "2507.13033": {  # exhaustive SR and MDL
   "bottleneck": V("B2_CREDIT_SEARCH", "the contribution is a guaranteed exhaustive search plus "
                   "a principled selection criterion"),
   "representation_family": V("symbolic_expression", "functions from data"),
   "selection_family": M(["exact_search"],
                         "the search is exhaustive (exact_search fits) but the SELECTION among "
                         "survivors is by minimum description length, which has no frozen "
                         "value; a single value records only half the mechanism"),
   "evaluation_regime": V("fixed_test_suite", "'benchmark dataset (feynman_I_6_2a) from the "
                          "Penn Machine Learning Benchmarks ... as used in the SRBench "
                          "competition'")},
 "2405.18471": {  # SR for beyond-standard-model physics
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the objective is analytic expressions for physical "
                   "observables"),
   "representation_family": V("symbolic_expression", "'the symbolic formula that is generated "
                              "by its expression tree'"),
   "selection_family": OM(GAP_PARETO, "'the best individuals being those inhabiting the "
                          "corresponding Pareto front'"),
   "evaluation_regime": V("scalar_objective", "accuracy against computed observables")},
 "2511.22794": {  # synthetic data for SR extrapolation
   "bottleneck": V("B3_TELEOLOGY_EVAL", "the contribution alters the TRAINING DISTRIBUTION to "
                   "change extrapolation behaviour"),
   "representation_family": V("symbolic_expression", "GP-based symbolic regression"),
   "selection_family": OM(GAP_PARETO, "'selection to maintain a set of solutions that balance "
                          "two competing objectives'"),
   "evaluation_regime": V("fixed_test_suite", "'six benchmark datasets'")},
}


def main() -> int:
    doc = {
        "labels": LABELS,
        "n_papers": len(LABELS),
        "label_type": "REFERENCE_LABELS",
        "NOT_GROUND_TRUTH": (
            "produced by the same model that authored the tagger under test. No independent "
            "human adjudication was available. First pass was blind to the tagger's output, "
            "but the annotator had already seen aggregate results from Experiments 2 and 3 in "
            "earlier turns and that exposure cannot be undone."),
        "frozen_against": "gate_freeze_2026-09-02.json",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("wrote %s with %d papers" % (OUT, len(LABELS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
