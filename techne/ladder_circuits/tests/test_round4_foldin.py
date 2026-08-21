"""Cycle 011: round-4 fold-in — the three items, executed.

1. R6 provenance-sensitive diagnosis: rederive-and-diff killed BEHAVIOURALLY (non-unique
   proofs), plus the correct-endpoint / corrupt-middle case.
2. Add-only plasticity poisons selection under a finite evaluation budget; guarding is not
   retraction; R_next SUBSET R_now is the real power.
3. Band G: epistemic-rule plasticity + RETROACTIVE revalidation, with the constitutional
   constraint (revisions need an evaluator-independent warrant) enforced.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r6_localization import (  # noqa: E402
    Derivation, Step, localize_and_repair, rederive_and_diff, validate,
)
from techne.ladder_circuits.operator_plasticity import BudgetedSelector  # noqa: E402
from techne.ladder_circuits.epistemic_plasticity import (  # noqa: E402
    Claim, ResearchCorpus, UnwarrantedRevision, Warrant, sampling_evaluator,
    symbolic_evaluator,
)

x = sp.Symbol("x")


# ---- 1. R6: localization vs rederive-and-diff ------------------------------------------------

def corrupted() -> Derivation:
    """(x+1) --square--> valid --add_one--> INVALID (+5) --double--> valid given bad input."""
    sq = sp.expand((x + 1) ** 2)
    return Derivation(start=x + 1, steps=[
        Step("square", sq),
        Step("add_one", sq + 5),
        Step("double", sp.expand(2 * (sq + 5))),
    ])


def test_validate_names_the_first_invalid_step():
    assert validate(corrupted()) == 1


def test_localizer_repairs_minimally_and_preserves_the_valid_prefix():
    idx, repaired = localize_and_repair(corrupted())
    assert idx == 1
    assert repaired.steps[0].result == corrupted().steps[0].result   # prefix untouched
    assert repaired.steps[1].result == sp.expand((x + 1) ** 2) + 1
    assert validate(repaired) is None                                 # whole proof now sound


def test_KILL_rederive_and_diff_smears_when_the_proof_is_non_unique():
    """A from-scratch solver takes a DIFFERENT valid route; the diff reports broad
    disagreement and cannot localize the fault to step 1."""
    flagged = rederive_and_diff(corrupted(), ["double", "square", "add_one"])
    assert len(flagged) >= 2, "diff should smear across the proof"
    assert flagged != [1], "diff must not coincidentally localize"


def test_SHARPER_correct_endpoint_hides_a_corrupt_middle():
    """Their sharpest case: the invalid step's damage is carried but the ENDPOINT is a
    legitimate value, so endpoint checking passes while provenance is broken."""
    deriv = Derivation(start=x, steps=[
        Step("add_one", x + 3),                    # INVALID: add_one gives x+1
        Step("sub_one", sp.expand(x + 3 - 1)),     # a valid rule applied to a bad predecessor
    ])
    assert sp.simplify(deriv.result - sp.expand(x + 2)) == 0   # endpoint: a real value
    assert validate(deriv) == 0                                 # provenance: fault at step 0
    idx, repaired = localize_and_repair(deriv)
    assert idx == 0 and validate(repaired) is None
    assert sp.simplify(repaired.result - x) == 0                # the TRUE endpoint differs


# ---- 2. add-only poisoning -------------------------------------------------------------------

def _stale(n: int):
    return [(f"g{i}", (lambda v, i=i: v + 1000 + i)) for i in range(n)]


def test_add_only_accuracy_collapses_as_stale_vocabulary_grows():
    """Budget B=3: with >= B stale macros the useful primitive is never reached."""
    gold = lambda v: 2 * v
    for n_stale, expect in ((0, True), (2, True), (3, False), (10, False)):
        sel = BudgetedSelector(budget=3, primitive=gold)
        for name, rule in _stale(n_stale):
            sel.install_macro(name, rule)
        assert sel.solve(7, gold(7))[0] is expect, f"n_stale={n_stale}"


def test_guarding_is_not_retraction_the_stale_macros_still_consume_budget():
    gold = lambda v: 2 * v
    sel = BudgetedSelector(budget=3, primitive=gold)
    for name, rule in _stale(3):
        sel.install_macro(name, rule)
    sel.install_macro("g_guarded", lambda v: None)   # a well-behaved replacement, added only
    assert sel.solve(7, gold(7))[0] is False


def test_retraction_restores_performance():
    gold = lambda v: 2 * v
    sel = BudgetedSelector(budget=3, primitive=gold, can_retract=True)
    for name, rule in _stale(3):
        sel.install_macro(name, rule)
    assert sel.solve(7, gold(7))[0] is False
    for i in range(3):
        assert sel.retract(f"g{i}") is True
    assert sel.solve(7, gold(7))[0] is True


def test_add_only_system_cannot_retract_at_all():
    sel = BudgetedSelector(budget=2, primitive=lambda v: v, can_retract=False)
    sel.install_macro("g0", lambda v: v + 1)
    assert sel.retract("g0") is False


# ---- 3. Band G: evaluator revision + retroactive revalidation ---------------------------------

POOL = list(range(10))


def build_corpus(fixed: bool) -> ResearchCorpus:
    """100 claims certified under E_0 (sampling 0..9). C37 is adversarial: FALSE but agreeing
    at every sampled point (difference = x(x-1)...(x-9)). C80 depends on C37."""
    corpus = ResearchCorpus(evaluator=sampling_evaluator(POOL), evaluator_fixed=fixed)
    for i in range(100):
        if i == 37:
            diff = sp.prod([x - n for n in POOL])
            claim = Claim("C37", lhs=sp.expand(x**2 + diff), rhs=x**2)
        elif i == 80:
            claim = Claim("C80", lhs=x + x, rhs=2 * x, depends_on=("C37",))
        else:
            claim = Claim(f"C{i}", lhs=sp.expand((x + i) ** 2),
                          rhs=sp.expand(x**2 + 2 * i * x + i**2))
        corpus.submit(claim)
    return corpus


def test_the_weak_evaluator_certifies_the_adversarial_claim():
    corpus = build_corpus(fixed=False)
    assert corpus.trusted_count() == 100 and "C37" in corpus.certified


def test_terminal_cheat_is_REFUSED_revisions_need_an_independent_warrant():
    """'My claim was killed, so I redefine killing.' The constitutional gate refuses it."""
    corpus = build_corpus(fixed=False)
    bogus = Warrant(claim_id="C5", witness_point=3, old_verdict="survive")  # C5 is truly valid
    with pytest.raises(UnwarrantedRevision):
        corpus.revise(symbolic_evaluator, bogus)
    assert corpus.revisions == 0


def test_BAND_G_evaluator_revision_plus_retroactive_revalidation():
    """The killer: after a warranted revision the plastic corpus unwinds the false claim AND
    its downstream consequence; the fixed-evaluator system reports its old count forever."""
    plastic, fixed = build_corpus(fixed=False), build_corpus(fixed=True)
    warrant = Warrant(claim_id="C37", witness_point=11, old_verdict="survive")

    plastic.revise(symbolic_evaluator, warrant)
    retracted = plastic.revalidate()

    assert "C37" in retracted and "C80" in retracted
    assert plastic.trusted_count() == 98
    with pytest.raises(UnwarrantedRevision):
        fixed.revise(symbolic_evaluator, warrant)
    assert fixed.trusted_count() == 100


def test_prospective_only_revision_leaves_history_contaminated():
    """Revising without revalidating is the half-measure their critique names."""
    corpus = build_corpus(fixed=False)
    corpus.revise(symbolic_evaluator, Warrant("C37", 11, "survive"))
    assert corpus.trusted_count() == 100     # nothing unwound yet
    corpus.revalidate()
    assert corpus.trusted_count() == 98      # only revalidation cleans the corpus
