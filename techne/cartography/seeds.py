"""Seed corpus for the cartography campaign.

SEEDS ARE QUERIES, NOT PAPERS. Naming specific papers from memory would (a) risk fabricating
citations, which is the one error this campaign cannot afford, and (b) bias the map toward what
one model happens to remember, which is a popularity prior wearing a lab coat. Queries are
resolved against live indexes, and whatever comes back comes back with provenance.

COVERAGE PRESSURE IS BUILT INTO THE SEED SET. The brief warns against spending every cycle on
whatever produced the easiest early wins, so the seeds deliberately include the awkward
neighbourhoods: negative results, replication studies, old terminology, and the cross-field
collisions where two communities describe one mechanism in incompatible vocabulary.
"""
from __future__ import annotations

#: The Gen-0 collision surface named in the brief. Expansion beyond this must be EARNED by a
#: mechanism, failure mode, representation or evaluation regime the current corpus cannot
#: represent -- and the justification is recorded on the cycle that expands.
CORE_SURFACE = (
    "evolutionary computation",
    "genetic programming",
    "quality diversity map-elites",
    "novelty search",
    "lexicase selection",
    "program synthesis",
    "inductive program synthesis",
    "symbolic regression",
    "cartesian genetic programming",
    "grammatical evolution",
    "neuroevolution",
    "neural architecture search",
    "differentiable programming",
    "neurosymbolic reasoning",
    "mechanistic interpretability",
    "circuit discovery neural network",
    "sparse autoencoder feature",
    "program distillation",
    "self-play curriculum",
    "coevolution competitive",
    "automated theorem proving search",
)

#: Cross-field collisions. Each pairs two communities that plausibly study one mechanism under
#: different names. These are the queries most likely to expose whether the Rosetta Stone is
#: operational or merely lexical.
COLLISION_QUERIES = (
    "quality diversity program synthesis",
    "lexicase selection program synthesis",
    "novelty search program space",
    "map-elites discrete representation",
    "circuit discovery search algorithm",
    "evolutionary search neural network circuit",
    "behavioral descriptor program semantics",
    "semantic locality genetic programming mutation",
    "archive based search theorem proving",
    "coevolution program synthesis test cases",
    "sparse circuit extraction optimization",
    "library learning abstraction reuse",
    "equality saturation program optimization",
    "diversity preservation neural architecture search",
    "counterexample guided inductive synthesis diversity",
)

#: Queries aimed at the parts of the literature that retrieval systems systematically bury.
#: Negative results and replications are where failure cartography actually lives, and they are
#: exactly what citation-count-driven expansion will never surface.
AWKWARD_QUERIES = (
    "negative results evolutionary computation",
    "failure modes genetic programming",
    "replication study evolutionary algorithm",
    "reproducibility crisis machine learning benchmark",
    "ablation study reveals no improvement",
    "premature convergence diversity loss",
    "deceptive fitness landscape",
    "benchmark overfitting evolutionary",
    "baseline mismatch unfair comparison",
    "compute matched comparison neural",
    "hand-designed behavior descriptor limitation",
    "does novelty search actually work",
    "critique of quality diversity",
    "when does genetic programming fail",
)

#: Historical terminology. Search engines are biased toward current vocabulary, so a map built
#: from modern terms alone will invent holes that were filled decades ago under other names.
HISTORICAL_QUERIES = (
    "evolutionary programming Fogel",
    "classifier system Holland",
    "genetic algorithm schema theorem",
    "evolution strategies Rechenberg Schwefel",
    "automatic programming induction 1980s",
    "inductive logic programming",
    "learning classifier system credit assignment",
    "bucket brigade algorithm",
    "artificial life open ended evolution",
    "Tierra Avida digital evolution",
)


def all_seeds() -> list:
    """Every seed query, tagged with the lane it came from so cycle selection can maintain
    diversity pressure rather than draining the easiest lane first."""
    out = []
    for q in CORE_SURFACE:
        out.append({"query": q, "lane": "core"})
    for q in COLLISION_QUERIES:
        out.append({"query": q, "lane": "collision"})
    for q in AWKWARD_QUERIES:
        out.append({"query": q, "lane": "awkward"})
    for q in HISTORICAL_QUERIES:
        out.append({"query": q, "lane": "historical"})
    return out


#: Independent re-formulations used when trying to KILL a coverage hole. The point is that
#: these are not rephrasings of one idea -- they attack the cell from different vocabularies,
#: so that surviving all of them is weak evidence of absence rather than evidence of a
#: thesaurus with a blind spot.
def hole_formulations(coords: tuple) -> list:
    """Build independent query formulations for a QD cell.

    coords = (bottleneck, representation_family, selection_family, evaluation_regime)
    """
    _b, rep, sel, ev = coords
    rep_words = {
        "discrete_program": ["program", "genetic programming", "code synthesis"],
        "graph_circuit": ["circuit", "graph", "subgraph"],
        "continuous_neural": ["neural network", "weights", "parameters"],
        "hybrid_differentiable": ["differentiable program", "relaxation", "soft execution"],
        "symbolic_expression": ["symbolic expression", "equation", "term rewriting"],
        "unknown": [""],
    }[rep]
    sel_words = {
        "case_wise": ["lexicase", "case-wise selection", "per-test selection"],
        "novelty": ["novelty search", "behavioral novelty", "curiosity"],
        "archive_qd": ["map-elites", "quality diversity", "elite archive"],
        "gradient": ["gradient descent", "backpropagation"],
        "exact_search": ["enumerative search", "smt", "constraint solving"],
        "adversarial": ["coevolution", "self-play", "adversarial"],
        "scalar_fitness": ["fitness function", "tournament selection"],
        "unknown": [""],
    }[sel]
    ev_words = {
        "fixed_test_suite": ["test cases", "input-output examples"],
        "scalar_objective": ["objective function", "scalar reward"],
        "behavioral_descriptor": ["behavior descriptor", "behavior space"],
        "coevolved_moving": ["coevolved", "curriculum", "environment generation"],
        "formal_verifier": ["theorem prover", "formal verification"],
        "unknown": [""],
    }[ev]

    forms = []
    # F1 -- the plain conjunction
    forms.append({"formulation": "F1_direct",
                  "query": " ".join(x for x in (rep_words[0], sel_words[0], ev_words[0]) if x)})
    # F2 -- alternate vocabulary for the same cell
    forms.append({"formulation": "F2_alt_vocab",
                  "query": " ".join(x for x in (rep_words[-1], sel_words[-1], ev_words[-1]) if x)})
    # F3 -- mechanism pair only, dropping the evaluation axis (catches papers that never name it)
    forms.append({"formulation": "F3_mechanism_pair",
                  "query": " ".join(x for x in (rep_words[0], sel_words[-1]) if x)})
    # F4 -- selection + evaluation, dropping representation (catches method-first papers)
    forms.append({"formulation": "F4_selection_eval",
                  "query": " ".join(x for x in (sel_words[0], ev_words[0]) if x)})
    return [f for f in forms if f["query"].strip()]
