"""Amino acids decomposed from pgmpy (v1.1.0) — Bayesian networks and causal inference.

Each function is 5-20 lines, performs one atomic reasoning operation,
and wraps a specific pgmpy capability that T1 primitives lack.
"""
from forge.amino_acids.registry import amino_acid


@amino_acid(
    id="pgmpy_build_bn",
    source="pgmpy",
    reasoning_type="causal",
    description="Build a Bayesian network from edges and optional CPD specs"
)
def build_bn(edges, cpd_specs=None):
    """Build a DiscreteBayesianNetwork from edges and optional CPD specifications.
    
    Args:
        edges: list of (parent, child) tuples
        cpd_specs: optional list of dicts with keys: variable, card, values, evidence, evidence_card
    Returns:
        Configured DiscreteBayesianNetwork (or None on failure)
    """
    from pgmpy.models import DiscreteBayesianNetwork
    from pgmpy.factors.discrete import TabularCPD
    try:
        model = DiscreteBayesianNetwork(edges)
        if cpd_specs:
            for spec in cpd_specs:
                cpd = TabularCPD(
                    spec["variable"], spec["card"], spec["values"],
                    evidence=spec.get("evidence"), evidence_card=spec.get("evidence_card")
                )
                model.add_cpds(cpd)
            if not model.check_model():
                return None
        return model
    except Exception:
        return None


@amino_acid(
    id="pgmpy_find_dseparators",
    source="pgmpy",
    reasoning_type="causal",
    description="Find the minimal set of variables that d-separates two variables in a Bayesian network"
)
def find_dseparators(model, var_a, var_b):
    """Find minimal d-separating set between var_a and var_b.
    
    Returns:
        set of variable names that d-separate var_a from var_b, or None if inseparable
    """
    try:
        dsep = model.minimal_dseparator(var_a, var_b)
        return dsep if dsep is not None else set()
    except Exception:
        return None


@amino_acid(
    id="pgmpy_get_markov_blanket",
    source="pgmpy",
    reasoning_type="causal",
    description="Get the Markov blanket of a variable (parents, children, co-parents)"
)
def get_markov_blanket(model, variable):
    """Returns the Markov blanket: the minimal set that makes variable conditionally
    independent of all other variables."""
    try:
        return model.get_markov_blanket(variable)
    except Exception:
        return []


@amino_acid(
    id="pgmpy_conditional_query",
    source="pgmpy",
    reasoning_type="probabilistic",
    description="Query P(target | evidence) using variable elimination in a Bayesian network"
)
def conditional_query(model, target_vars, evidence):
    """Compute P(target_vars | evidence) via variable elimination.
    
    Args:
        model: DiscreteBayesianNetwork with CPDs
        target_vars: list of variable names to query
        evidence: dict of {variable: observed_state}
    Returns:
        dict mapping state tuples to probabilities, or None on failure
    """
    from pgmpy.inference import VariableElimination
    try:
        infer = VariableElimination(model)
        result = infer.query(target_vars, evidence=evidence, show_progress=False)
        return {"values": result.values.tolist(), "variables": result.variables}
    except Exception:
        return None


@amino_acid(
    id="pgmpy_do_calculus",
    source="pgmpy",
    reasoning_type="causal",
    description="Compute P(Y | do(X)) — the causal effect of intervening on X"
)
def do_calculus(model, target_vars, do_vars, evidence=None):
    """Compute interventional distribution P(target | do(intervention), evidence).
    
    Args:
        model: DiscreteBayesianNetwork with CPDs
        target_vars: list of variables to query
        do_vars: dict of {variable: intervention_value}
        evidence: optional dict of {variable: observed_value}
    Returns:
        dict with probability values, or None on failure
    """
    from pgmpy.inference import CausalInference
    try:
        ci = CausalInference(model)
        result = ci.query(target_vars, do=do_vars, evidence=evidence, show_progress=False)
        return {"values": result.values.tolist(), "variables": result.variables}
    except Exception:
        return None


@amino_acid(
    id="pgmpy_get_adjustment_set",
    source="pgmpy",
    reasoning_type="causal",
    description="Find backdoor adjustment sets for estimating causal effect of X on Y"
)
def get_adjustment_set(model, treatment, outcome):
    """Find all valid backdoor adjustment sets for the causal effect of treatment on outcome.
    
    Returns:
        frozenset of frozensets, each a valid adjustment set. Empty if none exist.
    """
    from pgmpy.inference import CausalInference
    try:
        ci = CausalInference(model)
        return ci.get_all_backdoor_adjustment_sets(treatment, outcome)
    except Exception:
        return frozenset()


@amino_acid(
    id="pgmpy_detect_confounders",
    source="pgmpy",
    reasoning_type="causal",
    description="Identify common ancestors (confounders) of two variables in a DAG"
)
def detect_confounders(model, var_a, var_b):
    """Find variables that are ancestors of both var_a and var_b (potential confounders).

    Returns:
        set of confounder variable names
    """
    import networkx as nx
    try:
        dag = model.to_directed()
        ancestors_a = nx.ancestors(dag, var_a)
        ancestors_b = nx.ancestors(dag, var_b)
        return ancestors_a & ancestors_b
    except Exception:
        return set()


@amino_acid(
    id="pgmpy_compare_conditional_marginal",
    source="pgmpy",
    reasoning_type="probabilistic",
    description="Compare P(Y|X=x) vs P(Y) to detect if conditioning changes the distribution (Simpson's paradox detector)"
)
def compare_conditional_marginal(model, target, condition_var, condition_val):
    """Compare marginal P(target) with conditional P(target | condition_var=condition_val).

    Returns:
        dict with 'marginal', 'conditional', 'difference' arrays, or None on failure.
        A large difference suggests conditioning matters (potential Simpson's scenario).
    """
    from pgmpy.inference import VariableElimination
    try:
        infer = VariableElimination(model)
        marginal = infer.query([target], show_progress=False).values
        conditional = infer.query(
            [target], evidence={condition_var: condition_val}, show_progress=False
        ).values
        diff = [float(c - m) for c, m in zip(conditional, marginal)]
        return {
            "marginal": marginal.tolist(),
            "conditional": conditional.tolist(),
            "difference": diff,
            "max_abs_diff": max(abs(d) for d in diff),
        }
    except Exception:
        return None


@amino_acid(
    id="pgmpy_active_trails",
    source="pgmpy",
    reasoning_type="causal",
    description="Find all nodes reachable via active trails from a set of variables given observations"
)
def active_trails(model, start_vars, observed=None):
    """Find nodes connected to start_vars via active trails (not blocked by observed).

    This detects which variables are NOT conditionally independent of start_vars.
    Returns:
        dict mapping each start var to its set of reachable nodes
    """
    try:
        return model.active_trail_nodes(start_vars, observed=observed or set())
    except Exception:
        return {}


@amino_acid(
    id="pgmpy_map_query",
    source="pgmpy",
    reasoning_type="probabilistic",
    description="Find the most probable state assignment for target variables given evidence"
)
def map_query(model, target_vars, evidence):
    """Find argmax P(target_vars | evidence) — the most likely configuration.

    Returns:
        dict mapping variable names to their most probable states, or None on failure
    """
    from pgmpy.inference import VariableElimination
    try:
        infer = VariableElimination(model)
        return infer.map_query(target_vars, evidence=evidence, show_progress=False)
    except Exception:
        return None
