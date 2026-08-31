"""Gen-0 bottleneck taxonomy and the operational vocabulary, plus the rules a mutation must beat.

THE TAXONOMY IS A HYPOTHESIS. B1/B2/B3 are a guess about where search physics actually has
joints. The campaign is allowed -- encouraged -- to split, merge, add or delete them, but only
against frozen held-out tests, and never after seeing the result it would flatter. A taxonomy
that changes because a new one sounds more elegant is an ontology paying for itself with
aesthetics.

WHY LEXICAL MATCHING IS USED AND WHAT IT CANNOT DO. The mechanism vocabulary below drives
regex-based tagging of titles and abstracts. That is deliberately a WEAK instrument: it finds
the words, not the mechanisms. Its output is always adjudication=PROPOSED. It exists to
generate candidates cheaply and to give the held-out semantic test something to fail against --
if operational neighbours turn out to be exactly the papers sharing vocabulary, the Rosetta
Stone is lexical and the campaign must say so rather than dress up a thesaurus as a map.
"""
from __future__ import annotations

import re

# --- the Gen-0 bottlenecks ----------------------------------------------------------------

BOTTLENECKS = {
    "B1_REPRESENTATION": {
        "name": "syntax-to-semantics / representation",
        "question": "what is legal to write, and how far does a legal edit move behaviour?",
        "probes": [
            "what fraction of local mutations remain semantically meaningful",
            "how local is phenotype displacement under a single edit",
            "how compositional is the representation",
            "how much prior ontology is baked into the representation",
            "at what complexity does semantic locality break",
        ],
    },
    "B2_CREDIT_SEARCH": {
        "name": "credit assignment / search / selection",
        "question": "what receives credit, at what granularity, and does selection destroy "
                    "the diversity the search needs?",
        "probes": [
            "is credit scalar, case-wise, gradient, causal, novelty or archive-relative",
            "does selection collapse diversity or preserve specialists",
            "is improvement limited by search, evaluation budget, or representation",
            "is the archive preserving possibilities or reflecting a chosen descriptor ontology",
        ],
    },
    "B3_TELEOLOGY_EVAL": {
        "name": "teleology / evaluation / environment",
        "question": "who defines success, and where does task information actually enter?",
        "probes": [
            "does the evaluator encode the target decomposition",
            "is the landscape smooth, sparse, deceptive, discontinuous, adversarial or moving",
            "are behavioural descriptors human-smuggled ontology",
            "does self-play remove human teleology or relocate it",
        ],
    },
}

# --- mechanism vocabulary ------------------------------------------------------------------
# Each entry maps a canonical mechanism to the surface forms different communities use for it.
# The synonym lists are the Rosetta Stone's raw material AND its main failure risk: if two
# communities use the same word for different mechanisms, this table will merge them wrongly,
# and the held-out semantic test is what is supposed to catch that.

MECHANISMS = {
    # B1 -- representation
    "tree_gp": ["genetic programming", "tree-based gp", "koza", "symbolic expression tree"],
    "linear_gp": ["linear genetic programming", "register machine", "instruction sequence"],
    "cartesian_gp": ["cartesian genetic programming", "cgp", "graph-based gp"],
    "push_gp": ["pushgp", "push language", "stack-based genetic programming"],
    "grammatical_evolution": ["grammatical evolution", "grammar-based", "grammar-guided",
                              "context-free grammar"],
    "symbolic_regression": ["symbolic regression", "equation discovery", "formula discovery"],
    "neural_representation": ["neural network", "weight vector", "continuous parameterization"],
    "circuit_representation": ["circuit", "subgraph", "computational subgraph", "sparse circuit"],
    "sparse_autoencoder": ["sparse autoencoder", "sae", "dictionary learning", "feature basis"],
    "differentiable_program": ["differentiable program", "differentiable interpreter",
                               "neural program", "soft execution", "relaxation"],
    "dsl_library": ["domain-specific language", "dsl", "library learning", "abstraction learning",
                    "refactoring", "compression"],
    "egraph": ["e-graph", "egraph", "equality saturation", "rewrite rule", "term rewriting"],

    # B2 -- credit / search / selection
    "tournament_selection": ["tournament selection", "truncation selection", "roulette"],
    "lexicase": ["lexicase", "case-wise selection", "epsilon-lexicase", "down-sampled lexicase"],
    "novelty_search": ["novelty search", "behavioral novelty", "novelty metric",
                       "curiosity search"],
    "map_elites": ["map-elites", "map elites", "illumination algorithm", "elite archive"],
    "quality_diversity": ["quality diversity", "quality-diversity", "qd algorithm",
                          "qd score", "behavioral repertoire"],
    "cmaes": ["cma-es", "covariance matrix adaptation", "evolution strategy", "natural gradient"],
    "gradient_descent": ["backpropagation", "gradient descent", "sgd", "adam optimizer"],
    "enumerative_synthesis": ["enumerative search", "bottom-up synthesis", "top-down synthesis",
                              "version space", "observational equivalence"],
    "constraint_solving": ["smt solver", "sat solver", "constraint solving", "cegis",
                           "counterexample-guided"],
    "beam_search": ["beam search", "best-first", "a* search", "branch and bound"],
    "coevolution": ["coevolution", "co-evolution", "competitive coevolution",
                    "host-parasite", "arms race"],
    "self_play": ["self-play", "selfplay", "population play", "league training"],
    "causal_attribution": ["causal attribution", "causal tracing", "activation patching",
                           "ablation study", "intervention", "path patching"],
    "circuit_discovery": ["circuit discovery", "automated circuit", "acdc", "attribution patching",
                          "mechanistic interpretability"],
    "distillation": ["distillation", "student-teacher", "model compression", "pruning"],
    "nas": ["neural architecture search", "architecture search", "supernet", "weight sharing"],

    # B3 -- teleology / evaluation
    "scalar_objective": ["fitness function", "objective function", "scalar reward",
                         "single objective"],
    "test_suite": ["test suite", "test cases", "input-output examples", "specification",
                   "unit tests"],
    "behavior_descriptor": ["behavior descriptor", "behavioural descriptor", "behavior space",
                            "feature descriptor", "measure function", "niche"],
    "adversarial_curriculum": ["curriculum", "environment generation", "poet", "paired",
                               "regret-based", "unsupervised environment design"],
    "open_endedness": ["open-ended", "open endedness", "endless novelty", "divergent search"],
    "formal_verification": ["theorem prover", "proof assistant", "formal verification",
                            "lean", "coq", "isabelle"],
}

#: Which bottleneck each mechanism primarily loads on. A mechanism can inform several; this is
#: the PRIMARY assignment, and disagreement between this table and observed failure behaviour
#: is exactly the residual signal taxonomy mutation should feed on.
MECHANISM_BOTTLENECK = {
    "tree_gp": "B1_REPRESENTATION", "linear_gp": "B1_REPRESENTATION",
    "cartesian_gp": "B1_REPRESENTATION", "push_gp": "B1_REPRESENTATION",
    "grammatical_evolution": "B1_REPRESENTATION", "symbolic_regression": "B1_REPRESENTATION",
    "neural_representation": "B1_REPRESENTATION", "circuit_representation": "B1_REPRESENTATION",
    "sparse_autoencoder": "B1_REPRESENTATION", "differentiable_program": "B1_REPRESENTATION",
    "dsl_library": "B1_REPRESENTATION", "egraph": "B1_REPRESENTATION",

    "tournament_selection": "B2_CREDIT_SEARCH", "lexicase": "B2_CREDIT_SEARCH",
    "novelty_search": "B2_CREDIT_SEARCH", "map_elites": "B2_CREDIT_SEARCH",
    "quality_diversity": "B2_CREDIT_SEARCH", "cmaes": "B2_CREDIT_SEARCH",
    "gradient_descent": "B2_CREDIT_SEARCH", "enumerative_synthesis": "B2_CREDIT_SEARCH",
    "constraint_solving": "B2_CREDIT_SEARCH", "beam_search": "B2_CREDIT_SEARCH",
    "causal_attribution": "B2_CREDIT_SEARCH", "circuit_discovery": "B2_CREDIT_SEARCH",
    "distillation": "B2_CREDIT_SEARCH", "nas": "B2_CREDIT_SEARCH",

    "coevolution": "B3_TELEOLOGY_EVAL", "self_play": "B3_TELEOLOGY_EVAL",
    "scalar_objective": "B3_TELEOLOGY_EVAL", "test_suite": "B3_TELEOLOGY_EVAL",
    "behavior_descriptor": "B3_TELEOLOGY_EVAL", "adversarial_curriculum": "B3_TELEOLOGY_EVAL",
    "open_endedness": "B3_TELEOLOGY_EVAL", "formal_verification": "B3_TELEOLOGY_EVAL",
}

#: QD archive axes over ResearchGenomes. The archive preserves NICHES, not winners -- the point
#: is coverage of distinct experimental settings, and a "best paper" ranking would destroy
#: exactly the information the map is for.
QD_AXES = {
    "bottleneck": list(BOTTLENECKS.keys()),
    "representation_family": ["discrete_program", "graph_circuit", "continuous_neural",
                              "hybrid_differentiable", "symbolic_expression", "unknown"],
    "selection_family": ["scalar_fitness", "case_wise", "novelty", "archive_qd",
                         "gradient", "exact_search", "adversarial", "unknown"],
    "evaluation_regime": ["fixed_test_suite", "scalar_objective", "behavioral_descriptor",
                          "coevolved_moving", "formal_verifier", "unknown"],
}

_COMPILED = {m: [re.compile(r"\b" + re.escape(s) + r"\b", re.I) for s in syns]
             for m, syns in MECHANISMS.items()}


def tag_mechanisms(text: str) -> dict:
    """Lexical mechanism tagging. Returns {mechanism: [matched surface forms]}.

    WEAK BY CONSTRUCTION. This finds vocabulary, not mechanisms, and everything it produces is
    adjudication=PROPOSED. A paper that says "we do not use novelty search" tags for
    novelty_search here; negation is not handled, and pretending otherwise with a bag of
    hand-written negation patterns would give false precision.
    """
    if not text:
        return {}
    hits = {}
    for mech, pats in _COMPILED.items():
        found = []
        for p in pats:
            m = p.search(text)
            if m:
                found.append(m.group(0).lower())
        if found:
            hits[mech] = sorted(set(found))
    return hits


#: Mechanisms that fire on almost every paper in this corpus and therefore carry almost no
#: information about which bottleneck a paper loads on. Down-weighted rather than removed:
#: they are still evidence, just weak evidence.
#:
#: Measured cycle 021: of 9 genomes with all three descriptor axes known, 5 lost their
#: bottleneck to a TIE -- 56% of the otherwise-classifiable set. Every one of those ties was
#: manufactured by a coarse tag. `tournament_selection` is the worst offender because the
#: concept tagger added the previous cycle maps OpenAlex's "Selection (genetic algorithm)",
#: "Genetic algorithm" and "Evolutionary algorithm" all onto it -- so it now fires on nearly
#: every evolutionary paper and reliably ties against whatever specific mechanism the paper is
#: actually about. Four canonical lexicase papers were unclassifiable for exactly this reason
#: while carrying the tag `lexicase`.
COARSE_MECHANISMS = {
    "tournament_selection": 0.25,
    "scalar_objective": 0.4,
    "neural_representation": 0.4,
    "tree_gp": 0.6,
    "test_suite": 0.6,
    "gradient_descent": 0.6,
}


def assign_bottleneck(mech_hits: dict) -> str:
    """Weighted-vote the primary bottleneck from tagged mechanisms.

    Specific mechanisms outweigh generic ones. `lexicase` is a claim about credit assignment;
    `tournament_selection` inferred from a generic "Genetic algorithm" concept label is barely
    a claim at all, and letting the two vote equally lets noise cancel signal.

    Empties, and genuine ties between EQUALLY SPECIFIC mechanisms, still return B_UNASSIGNED.
    That matters: an unassigned genome is a visible residual, and residuals are what taxonomy
    mutation feeds on. The fix removes ties manufactured by coarse tags, not ties that reflect
    a paper genuinely spanning two bottlenecks.
    """
    if not mech_hits:
        return "B_UNASSIGNED"
    votes = {}
    for mech in mech_hits:
        b = MECHANISM_BOTTLENECK.get(mech)
        if b:
            votes[b] = votes.get(b, 0.0) + COARSE_MECHANISMS.get(mech, 1.0)
    if not votes:
        return "B_UNASSIGNED"
    top = max(votes.values())
    # A margin is required, not just a maximum: 1.0 vs 0.95 is a tie in everything but
    # arithmetic, and declaring a winner there would be false precision.
    winners = [b for b, v in votes.items() if v >= top - 1e-9]
    if len(winners) != 1:
        return "B_UNASSIGNED"
    runner_up = max([v for b, v in votes.items() if b != winners[0]], default=0.0)
    if top - runner_up < 0.2:
        return "B_UNASSIGNED"
    return winners[0]


def descriptors_from(mech_hits: dict) -> dict:
    """Project tagged mechanisms onto the QD axes. Unknown stays unknown."""
    rep = "unknown"
    for m, val in (("circuit_representation", "graph_circuit"),
                   ("sparse_autoencoder", "graph_circuit"),
                   ("differentiable_program", "hybrid_differentiable"),
                   ("symbolic_regression", "symbolic_expression"),
                   ("tree_gp", "discrete_program"), ("linear_gp", "discrete_program"),
                   ("push_gp", "discrete_program"), ("cartesian_gp", "graph_circuit"),
                   ("grammatical_evolution", "discrete_program"),
                   ("dsl_library", "discrete_program"), ("egraph", "symbolic_expression"),
                   ("neural_representation", "continuous_neural")):
        if m in mech_hits:
            rep = val
            break
    sel = "unknown"
    for m, val in (("lexicase", "case_wise"), ("novelty_search", "novelty"),
                   ("map_elites", "archive_qd"), ("quality_diversity", "archive_qd"),
                   ("constraint_solving", "exact_search"),
                   ("enumerative_synthesis", "exact_search"), ("beam_search", "exact_search"),
                   ("gradient_descent", "gradient"), ("cmaes", "gradient"),
                   ("coevolution", "adversarial"), ("self_play", "adversarial"),
                   ("tournament_selection", "scalar_fitness")):
        if m in mech_hits:
            sel = val
            break
    ev = "unknown"
    for m, val in (("formal_verification", "formal_verifier"),
                   ("behavior_descriptor", "behavioral_descriptor"),
                   ("adversarial_curriculum", "coevolved_moving"),
                   ("coevolution", "coevolved_moving"), ("self_play", "coevolved_moving"),
                   ("test_suite", "fixed_test_suite"),
                   ("scalar_objective", "scalar_objective")):
        if m in mech_hits:
            ev = val
            break
    return {"representation_family": rep, "selection_family": sel, "evaluation_regime": ev}


def cell_of(genome: dict) -> tuple:
    """The QD cell a genome occupies. Cells, not scores -- the archive preserves niches."""
    d = genome.get("descriptors") or {}
    return (genome.get("bottleneck", "B_UNASSIGNED"),
            d.get("representation_family", "unknown"),
            d.get("selection_family", "unknown"),
            d.get("evaluation_regime", "unknown"))


def total_cells() -> int:
    n = 1
    for axis in QD_AXES.values():
        n *= len(axis)
    return n


#: A taxonomy mutation must IMPROVE one of these on held-out data. Listed here so the bar is
#: fixed before any mutation is proposed, rather than chosen afterwards to justify one.
TAXONOMY_MUTATION_TESTS = (
    "held_out_failure_prediction",   # does the split predict which failure mode appears?
    "cross_field_retrieval",         # do operational neighbours cross vocabulary boundaries?
    "contradiction_detection",       # does it surface genuine disagreements?
    "compression_without_loss",      # fewer categories, same predictive power
)

# --- SIGNAL 2 FOR MECHANISM TAGGING: index concept labels ----------------------------------
#
# The lexical tagger alone placed only 3.3% of abstract-bearing genomes on all three axes
# (measured cycle 020, n=123). Per-axis unknown rates: evaluation_regime 79%, selection_family
# 75%, representation_family 69%. OpenAlex assigns its own concept labels, and a survey of the
# corpus shows they carry real mechanism signal independent of our vocabulary -- "Genetic
# programming" (41 papers), "Selection (genetic algorithm)" (29), "Genetic algorithm" (25),
# "Evolutionary algorithm" (21), "Symbolic regression" (9), "Genetic representation" (8).
#
# They are COARSER than our mechanisms -- OpenAlex does not distinguish lexicase from
# tournament, or MAP-Elites from novelty search -- so this signal raises the floor without
# reaching the ceiling. It is added as a second tagger, not a replacement, and its output is
# PROPOSED exactly like the lexical one.
CONCEPT_TO_MECHANISM = {
    "genetic programming": "tree_gp",
    "symbolic regression": "symbolic_regression",
    "cartesian genetic programming": "cartesian_gp",
    "grammatical evolution": "grammatical_evolution",
    "linear genetic programming": "linear_gp",
    "genetic representation": "tree_gp",
    "artificial neural network": "neural_representation",
    "deep learning": "neural_representation",
    "autoencoder": "sparse_autoencoder",
    "program synthesis": "enumerative_synthesis",
    "automated theorem proving": "formal_verification",
    "formal verification": "formal_verification",
    "satisfiability": "constraint_solving",
    "boolean satisfiability problem": "constraint_solving",
    "constraint satisfaction": "constraint_solving",
    "selection (genetic algorithm)": "tournament_selection",
    "tournament selection": "tournament_selection",
    "truncation selection": "tournament_selection",
    "fitness proportionate selection": "tournament_selection",
    "genetic algorithm": "tournament_selection",
    "evolutionary algorithm": "tournament_selection",
    "evolution strategy": "cmaes",
    "cma-es": "cmaes",
    "gradient descent": "gradient_descent",
    "backpropagation": "gradient_descent",
    "stochastic gradient descent": "gradient_descent",
    "reinforcement learning": "gradient_descent",
    "neural architecture search": "nas",
    "coevolution": "coevolution",
    "novelty search": "novelty_search",
    "beam search": "beam_search",
    "local search (optimization)": "beam_search",
    "fitness function": "scalar_objective",
    "fitness landscape": "scalar_objective",
    "benchmark (surveying)": "test_suite",
    "benchmark": "test_suite",
    "test suite": "test_suite",
    "overfitting": "test_suite",
    "generalization": "test_suite",
    "multi-objective optimization": "quality_diversity",
    "pareto principle": "quality_diversity",
}


def tag_from_concepts(concepts) -> dict:
    """Second, independent mechanism tagger driven by index concept labels."""
    out = {}
    for c in (concepts or []):
        m = CONCEPT_TO_MECHANISM.get(str(c).strip().lower())
        if m:
            out.setdefault(m, []).append("concept:" + str(c))
    return out


def tag_all(text: str, concepts=None) -> dict:
    """Union of the lexical and concept taggers.

    Two weak signals that fail differently. The lexical tagger reads what the authors wrote;
    the concept tagger reads what an independent classifier inferred. Neither is adjudication --
    both feed records written as PROPOSED.
    """
    hits = tag_mechanisms(text)
    for m, ev in tag_from_concepts(concepts).items():
        hits.setdefault(m, []).extend(ev)
    return {m: sorted(set(v)) for m, v in hits.items()}

