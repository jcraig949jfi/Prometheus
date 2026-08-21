"""Cycle 013: round-5 fold-in — R8 constructed representations + the three epistemic corrections."""
from __future__ import annotations

import pathlib
import random
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r8_representation import (  # noqa: E402
    PrecomputedViewSelector, RawSearcher, RepresentationShifter, TwoGoalObject,
    generic_canonical_form, infer_partition, make_class_graph, quotient,
)
from techne.ladder_circuits.certification_provenance import (  # noqa: E402
    Certificate, CertificateIndex, ClaimGraph, Constitution, ConstitutionalViolation,
    NegativeDep, Observation,
)


# ---- R8: the representation must be CONSTRUCTED ---------------------------------------------

def test_partition_is_inferred_from_structure_not_from_names():
    rng = random.Random(20260821)
    g, truth = make_class_graph(rng, [7, 5, 6])
    colour = infer_partition(g)
    groups = {}
    for n, c in colour.items():
        groups.setdefault(c, set()).add(truth[n])
    assert all(len(v) == 1 for v in groups.values()), "inferred classes must be pure"
    assert len(groups) == 3


def test_SHIFTER_solves_within_budget_where_RAW_SEARCH_cannot():
    """The R8 probe: raw search over 60 nodes exceeds a budget of 10; the quotient has 3."""
    rng = random.Random(7)
    g, _truth = make_class_graph(rng, [20, 20, 20])
    shifter, raw = RepresentationShifter(), RawSearcher()
    assert shifter.solve(g, budget=10) == 3
    assert raw.solve(g, budget=10) is None
    assert shifter.work == 3 and raw.work == 60


def test_KILL_precomputed_view_selector_cannot_contain_the_instance_partition():
    """R4-in-R8-clothing: a fixed catalogue of views cannot hold this instance's partition —
    node names and class sizes are fresh each episode, so the useful representation is one of
    Bell(|V|) possibilities. The selector falls back to raw work and fails the budget."""
    rng = random.Random(11)
    g_train, _ = make_class_graph(rng, [5, 5, 5])
    catalogue = [infer_partition(g_train)]          # a genuinely good view — of the WRONG graph
    g_test, _ = make_class_graph(rng, [20, 20, 20])
    sel = PrecomputedViewSelector(catalogue=catalogue)
    assert sel.solve(g_test, budget=10) is None
    assert RepresentationShifter().solve(g_test, budget=10) == 3


def test_shift_survives_randomised_names_and_class_sizes_across_episodes():
    for seed in range(6):
        rng = random.Random(seed)
        sizes = [rng.randrange(3, 9) for _ in range(3)]
        g, _ = make_class_graph(rng, sizes)
        assert RepresentationShifter().solve(g, budget=6) == 3


# ---- R8 sharper twin: the map must be GOAL-CONDITIONED --------------------------------------

def test_goal_conditioned_map_beats_a_generic_canonicaliser():
    """Same object, two goals needing INCOMPATIBLE quotients. A goal-blind canonical form is
    right for one and wrong for the other; phi_{x,G} is right for both."""
    obj = TwoGoalObject(items=[(a, b) for a in range(4) for b in range(6)])
    assert obj.classes_for("parity") == 2
    assert obj.classes_for("residue3") == 3

    blind = generic_canonical_form(obj)
    assert len(set(blind.values())) == obj.classes_for("parity")      # right for one goal
    assert len(set(blind.values())) != obj.classes_for("residue3")    # wrong for the other


def test_the_two_quotients_are_genuinely_incompatible_neither_refines_the_other():
    """Battery-validity check: if one quotient refined the other, a single canonical form
    would suffice and the twin would prove nothing."""
    obj = TwoGoalObject(items=[(a, b) for a in range(4) for b in range(6)])
    p, r = obj.quotient_for("parity"), obj.quotient_for("residue3")
    same_p_diff_r = any(p[i] == p[j] and r[i] != r[j] for i in obj.items for j in obj.items)
    same_r_diff_p = any(r[i] == r[j] and p[i] != p[j] for i in obj.items for j in obj.items)
    assert same_p_diff_r and same_r_diff_p


# ---- 12.1: provenance catches what "consumed evidence" misses --------------------------------

def test_short_circuit_hole_predicate_change_dirties_a_cert_whose_evidence_is_untouched():
    """The soundness hole: E_0 short-circuited and consumed only e1, but its certificate
    RECORDS that predicate p_relevance was invoked. Changing p_relevance dirties the claim
    even though no evidence it consumed changed."""
    idx = CertificateIndex()
    idx.add(Certificate("C1", "E0", frozenset({"p_pass", "p_relevance"}), frozenset(),
                        frozenset({"e1"})))
    idx.add(Certificate("C2", "E0", frozenset({"p_pass"}), frozenset(), frozenset({"e1"})))
    dirty = idx.dirty_from_evaluator_change({"p_relevance"})
    assert dirty == {"C1"}


def test_NEGATIVE_dependency_is_invalidated_by_database_GROWTH():
    """'Accepted because no counterexample existed under query Q at snapshot v.' It consumed
    no evidence record, so an evidence-indexed scheme would never revisit it — yet a later
    record invalidates it."""
    idx = CertificateIndex()
    idx.add(Certificate("C_neg", "E0", frozenset({"p_nocex"}), frozenset(), frozenset(),
                        negative_deps=(NegativeDep("cex_for_C_neg", 0),)))
    idx.add(Certificate("C_pos", "E0", frozenset({"p_pass"}), frozenset(), frozenset({"e9"})))
    assert idx.dirty_from_evaluator_change(set()) == set()      # nothing changed in E
    dirty = idx.add_db_record("cex_for_C_neg")                  # the DB grew
    assert dirty == {"C_neg"}


# ---- 12.2: justification propagates, influence does not --------------------------------------

def build_graph() -> ClaimGraph:
    """B is certified by its OWN evidence but was INSPIRED by A. D genuinely uses A."""
    def verifier(claim: str, ev):
        need = {"B": {"B:e1"}, "D": {"A:e2", "D:e3"}, "A": {"A:e0"}}
        return need.get(claim, set()) <= ev
    return ClaimGraph(
        evidence={"A": {"A:e0"}, "B": {"B:e1"}, "D": {"A:e2", "D:e3"}},
        influence={"B": {"A"}},
        verifier=verifier,
    )


def test_influence_only_claim_SURVIVES_retraction_of_its_inspiration():
    """Their point: a false conjecture that inspired a search does not invalidate what the
    search independently certified. Otherwise one bad heuristic annihilates a lineage."""
    g = build_graph()
    assert g.just_deps("B", ["A"]) == set()          # inspiration is not justification
    survivors = g.propagate_retraction({"A"}, universe=["A", "B", "D"])
    assert "B" not in survivors                       # B survives
    assert "D" in survivors                           # D genuinely depended on A


def test_the_operational_test_is_verify_without_the_upstream_item():
    g = build_graph()
    assert g.just_deps("D", ["A"]) == {"A"}


# ---- 12.3: the immutable-observation bottom --------------------------------------------------

def test_history_is_append_only():
    c = Constitution()
    c.record(Observation("t1", "P1", predicted="y", observed="z"))
    with pytest.raises(ConstitutionalViolation):
        c.record(Observation("t1", "P1", predicted="y", observed="y"))


def test_amendments_that_change_metrics_are_ALLOWED():
    """The bottom is thin on purpose: almost everything above it stays plastic."""
    c = Constitution()
    c.record(Observation("t1", "P1", "y", "z"))
    c.amend("switch primary metric to thrust-per-watt", rewrites_observations=False)
    c.amend("raise significance threshold", rewrites_observations=False)
    assert len(c.amendments) == 2 and c.failures() == ["t1"]


def test_REGRESS_SEPARATOR_amendment_whose_sole_effect_is_to_unfail_a_failure_is_REJECTED():
    """Their smallest separator: E_0 fails on c_0; propose K_1 whose only effect is to make
    c_0 stop counting as a failure. A regress-permitting system accepts it; the fixed bottom
    refuses, because the recorded prediction/observation relation cannot be erased."""
    c = Constitution()
    c.record(Observation("c0", "P", predicted="survive", observed="killed"))
    with pytest.raises(ConstitutionalViolation, match="immutable"):
        c.amend("redefine failure", rewrites_observations=False,
                sole_effect_clears_failures=["c0"])
    with pytest.raises(ConstitutionalViolation, match="rewrite"):
        c.amend("edit the log", rewrites_observations=True)
    assert c.failures() == ["c0"] and c.amendments == []
