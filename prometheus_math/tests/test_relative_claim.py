"""TDD suite for prometheus_math.relative_claim — the four required categories."""
from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.relative_claim import (  # noqa: E402
    AGGREGATE, EXISTENTIAL, ClaimError, Domain, RelativeClaim,
)


# ---- 1. authority --------------------------------------------------------------------------

def test_a_witnessed_existential_is_upward_closed_and_may_be_stated_absolutely():
    """Hand-checked from the definition: `∃ x ∈ D : P(x)` with witness w implies `∃ x ∈ D' : P(x)`
    for every D' ⊇ D, because w ∈ D ⊆ D'. That is the entire content of monotonicity here."""
    small = Domain("small", (1, 2, 3))
    big = Domain("big", (1, 2, 3, 4, 5))
    claim = RelativeClaim("has_even", True, small, EXISTENTIAL, witness=2)
    assert claim.is_upward_closed
    assert claim.entails_on(big)
    assert "witness" in claim.state_absolutely()


def test_a_negative_existential_does_NOT_travel():
    """"No witness in D" says nothing about D ∪ anything — the asymmetry that makes UNSETTLED
    a real verdict rather than a weak yes."""
    small = Domain("small", (1, 3, 5))
    big = Domain("big", (1, 3, 5, 2))
    claim = RelativeClaim("has_even", False, small, EXISTENTIAL)
    assert not claim.is_upward_closed
    assert not claim.entails_on(big)
    with pytest.raises(ClaimError):
        claim.state_absolutely()


def test_an_aggregate_never_travels_and_never_states_absolutely():
    """Measured non-monotone in BOTH directions on real data (F6: 0.0000 -> 0.3651 -> 0.2285 as
    the domain grew), so a superset value cannot be inferred at all, only re-measured."""
    small = Domain("small", (1, 2, 3))
    big = Domain("big", (1, 2, 3, 4))
    claim = RelativeClaim("mean_resolution", 0.9082, small, AGGREGATE)
    assert not claim.is_upward_closed
    assert not claim.entails_on(big)
    with pytest.raises(ClaimError) as exc:
        claim.state_absolutely()
    assert "relative to domain" in str(exc.value)


# ---- 2. property (Hypothesis) ----------------------------------------------------------------

members = st.lists(st.integers(min_value=0, max_value=30), min_size=1, max_size=20, unique=True)


@settings(max_examples=200, deadline=None)
@given(members, members)
def test_existential_entailment_tracks_the_subset_relation_exactly(a, b):
    """The entailment rule must agree with set inclusion, with no slack in either direction."""
    da = Domain("a", tuple(a))
    db = Domain("b", tuple(sorted(set(a) | set(b))))
    claim = RelativeClaim("nonempty", True, da, EXISTENTIAL, witness=a[0])
    assert claim.entails_on(db) is db.contains_all_of(da)
    assert claim.entails_on(db)                       # the union is always a superset


@settings(max_examples=150, deadline=None)
@given(members, st.floats(min_value=0.0, max_value=10.0, allow_nan=False))
def test_no_aggregate_ever_entails_on_any_domain(a, v):
    da = Domain("a", tuple(a))
    claim = RelativeClaim("agg", v, da, AGGREGATE)
    assert not claim.entails_on(da)                   # not even on its OWN domain
    assert not claim.entails_on(Domain("wider", tuple(a) + (999,)))


@settings(max_examples=120, deadline=None)
@given(members)
def test_the_digest_is_stable_and_content_addressed(a):
    """Two domains built separately from equal members must quote identically."""
    assert Domain("x", tuple(a)).digest == Domain("y", tuple(a)).digest
    assert len(Domain("x", tuple(a)).digest) == 16


# ---- 3. edge cases ---------------------------------------------------------------------------

def test_claim_edges():
    """Edges covered:
    - domain omitted entirely: ClaimError, NOT a default to "all inputs" or to the sample
    - empty domain: ClaimError (a claim measured over nothing is not a weak claim)
    - unnamed domain: ClaimError (an anonymous domain cannot be quoted)
    - unknown kind: ClaimError
    - positive existential with no witness: ClaimError — it cannot travel, so it is an
      aggregate in disguise
    - negative existential with no witness: fine, that is the normal case
    """
    d = Domain("d", (1, 2))
    with pytest.raises(ClaimError):
        RelativeClaim("p", True, None, EXISTENTIAL, witness=1)      # type: ignore[arg-type]
    with pytest.raises(ClaimError):
        Domain("empty", ())
    with pytest.raises(ClaimError):
        Domain("", (1,))
    with pytest.raises(ClaimError):
        RelativeClaim("p", 1.0, d, "SOMETHING_ELSE")
    with pytest.raises(ClaimError):
        RelativeClaim("p", True, d, EXISTENTIAL)                     # positive, no witness
    RelativeClaim("p", False, d, EXISTENTIAL)                        # negative, fine


def test_a_singleton_domain_still_carries_a_digest_and_a_size():
    d = Domain("one", (42,))
    c = RelativeClaim("p", True, d, EXISTENTIAL, witness=42)
    assert len(d) == 1 and d.digest
    assert "n=1" in c.render() and "one" in c.render()


def test_domains_compare_by_member_value_not_identity():
    """Two domains built in separate processes from equal values must relate correctly."""
    a = Domain("a", (1, 2, 3))
    b = Domain("b", (3, 2, 1, 4))
    assert b.contains_all_of(a)
    assert not a.contains_all_of(b)


# ---- 4. composition ---------------------------------------------------------------------------

def test_composes_with_the_real_F11_constancy_result():
    """Chain into cycle 029's live measurement. F11 reads UNSETTLED on well-formed candidates and
    VARIES once hostile input is added — so the negative claim must NOT travel and the positive
    one must."""
    from prometheus_math.battery import VARIES, structural_constancy
    from prometheus_math.discovery_pipeline import _f11_cross_validation
    from techne.ladder_circuits.battery_chain import wide_candidates
    from techne.ladder_circuits.constancy_sweep import polynomial_probes

    pred = lambda p: _f11_cross_validation(list(p[0]), p[1])[0]
    wellformed = [tuple(c) for c in wide_candidates()[:40]]
    hostile = [tuple(c) for c in polynomial_probes(limit=120)]

    quiet = structural_constancy("F11", pred, wellformed)
    loud = structural_constancy("F11", pred, wellformed + hostile)
    assert loud.status == VARIES

    d_small = Domain("wellformed", tuple(wellformed))
    d_big = Domain("wellformed+hostile", tuple(wellformed + hostile))

    negative = RelativeClaim("F11_can_fire", False, d_small, EXISTENTIAL)
    positive = RelativeClaim("F11_can_fire", True, d_big, EXISTENTIAL, witness=loud.witness)
    assert not negative.entails_on(d_big)             # quietness does not survive widening
    assert positive.entails_on(d_big)


def test_composes_with_the_real_F6_aggregate_result():
    """Chain into the cycle-030 measurement: F6's resolution moved 0.0000 -> 0.3651 -> 0.2285 as
    the domain grew, so no aggregate claim about it may travel."""
    from prometheus_math.battery import member_resolution
    from techne.ladder_circuits.battery_chain import CHECKS, wide_candidates

    wide = wide_candidates()
    f6 = dict(CHECKS)["F6"]
    col = []
    for c, m in wide:
        try:
            col.append(bool(f6(list(c), m)[0]))
        except Exception:
            col.append(None)
    firing = [i for i, v in enumerate(col) if v is False]
    quiet_idx = [i for i in range(len(wide)) if i not in firing][:40]

    def res(idxs):
        return member_resolution({"F6": [col[i] for i in idxs]})["F6"]

    narrow_v = res(quiet_idx)
    mid_v = res(quiet_idx + firing)
    assert narrow_v == pytest.approx(0.0)
    assert mid_v > narrow_v                            # widening INCREASED it

    d_narrow = Domain("quiet_subset", tuple(quiet_idx))
    d_mid = Domain("quiet+firing", tuple(quiet_idx + firing))
    claim = RelativeClaim("F6_resolution", narrow_v, d_narrow, AGGREGATE)
    assert not claim.entails_on(d_mid)                 # and the value really did change


# ---- cycle 031: the derivation, and the two kinds cycle 030 missed --------------------------

def test_THE_2x2_IS_EXHAUSTIVE_BY_CONSTRUCTION():
    """**Answers HITL #112, and the answer is that three was not exhaustive either.**

    "Monotone up?" and "monotone down?" are two independent booleans, so a claim's behaviour
    under domain extension has exactly four possibilities. The taxonomy cannot acquire a fifth
    member without someone finding a third monotonicity direction.
    """
    from prometheus_math.relative_claim import (
        INVARIANT, KIND_TABLE, UNIVERSAL, kind_from_monotonicity,
    )

    assert kind_from_monotonicity(True, False) == EXISTENTIAL
    assert kind_from_monotonicity(False, True) == UNIVERSAL
    assert kind_from_monotonicity(True, True) == INVARIANT
    assert kind_from_monotonicity(False, False) == AGGREGATE
    assert len(KIND_TABLE) == 4
    assert set(KIND_TABLE) == {(True, False), (False, True), (True, True), (False, False)}


def test_a_holding_universal_travels_DOWNWARD_and_a_failed_one_travels_UP():
    """The duality: a universal's positive is inherited by subsets, and its NEGATION is an
    existential (of a counterexample) inherited by supersets."""
    from prometheus_math.relative_claim import UNIVERSAL

    big = Domain("big", (1, 2, 3, 4))
    small = Domain("small", (1, 2))
    holds = RelativeClaim("all_positive", True, big, UNIVERSAL)
    assert holds.is_downward_closed and not holds.is_upward_closed
    assert holds.entails_on(small)
    assert not holds.entails_on(Domain("bigger", (1, 2, 3, 4, -9)))

    fails = RelativeClaim("all_positive", False, small, UNIVERSAL, witness=-5)
    assert fails.is_upward_closed and not fails.is_downward_closed
    assert fails.entails_on(Domain("sup", (1, 2, -5, 7)))


def test_a_failed_universal_without_its_counterexample_is_refused():
    """Symmetric to the witnessless positive existential: the negation of a universal IS an
    existential, so it travels only with its witness."""
    from prometheus_math.relative_claim import UNIVERSAL
    d = Domain("d", (1, 2))
    with pytest.raises(ClaimError):
        RelativeClaim("all_positive", False, d, UNIVERSAL)
    RelativeClaim("all_positive", True, d, UNIVERSAL)


def test_an_invariant_travels_everywhere_and_states_absolutely():
    """The fourth cell, which cycle 030 had no name for: a claim that never depended on a
    domain. F9's "cannot fire" is one — parameter-independence makes it domain-independent."""
    from prometheus_math.relative_claim import INVARIANT
    d = Domain("d", (1, 2))
    c = RelativeClaim("F9_can_fire", False, d, INVARIANT)
    assert c.is_upward_closed and c.is_downward_closed
    assert c.entails_on(Domain("anything", ("x",)))
    assert "independent of domain" in c.state_absolutely()


def test_probe_monotonicity_classifies_all_four_from_one_chain():
    from prometheus_math.relative_claim import INVARIANT, UNIVERSAL, probe_monotonicity
    chain = [Domain(f"d{k}", tuple(range(n))) for k, n in enumerate((2, 4, 6, 8))]
    assert probe_monotonicity(lambda d: len(d), chain) == EXISTENTIAL
    assert probe_monotonicity(lambda d: -len(d), chain) == UNIVERSAL
    assert probe_monotonicity(lambda d: 1, chain) == INVARIANT
    # sizes 2,4,6,8 -> 2,1,0,2 : down, down, then up. Neither direction holds.
    assert probe_monotonicity(lambda d: len(d) % 3, chain) == AGGREGATE


def test_probe_monotonicity_refuses_a_non_increasing_chain():
    from prometheus_math.relative_claim import probe_monotonicity
    bad = [Domain("big", (1, 2, 3)), Domain("small", (1,))]
    with pytest.raises(ClaimError):
        probe_monotonicity(lambda d: len(d), bad)
    with pytest.raises(ClaimError):
        probe_monotonicity(lambda d: len(d), [Domain("only", (1,))])


def test_COMPOSITION_normalisation_is_what_destroys_monotonicity():
    """**The load-bearing measurement, on real substrate.** The SAME statistic — F6's firings —
    is EXISTENTIAL as a count and AGGREGATE as a rate. Same predicate, same data, same firings;
    dividing by |D| changes the kind.

    So a claim's kind is a property of its aggregation operator, not of its subject matter, and
    "is this rate a fact about the object?" always answers no.
    """
    from prometheus_math.relative_claim import probe_monotonicity
    from techne.ladder_circuits.battery_chain import CHECKS, wide_candidates

    wide = wide_candidates()
    f6 = dict(CHECKS)["F6"]
    col = []
    for c, m in wide:
        try:
            col.append(bool(f6(list(c), m)[0]))
        except Exception:
            col.append(None)
    firing = [i for i, v in enumerate(col) if v is False]
    quiet = [i for i in range(len(wide)) if i not in firing]
    seq = [quiet[:20], quiet[:20] + firing, quiet[:20] + firing + quiet[20:50],
           list(range(len(wide)))]
    chain = [Domain(f"d{k}", tuple(idxs)) for k, idxs in enumerate(seq)]

    count = lambda d: sum(1 for i in d.members if col[i] is False)
    rate = lambda d: count(d) / len(d)
    assert probe_monotonicity(count, chain) == EXISTENTIAL
    assert probe_monotonicity(rate, chain) == AGGREGATE


def test_COMPOSITION_kronecker_is_a_holding_universal_on_real_polynomials():
    """M >= 1 for every integer polynomial, measured on the real candidate sets. It travels
    downward: holding on the wide set entails holding on any subset of it."""
    from prometheus_math.relative_claim import UNIVERSAL
    from techne.ladder_circuits.battery_chain import wide_candidates

    wide = wide_candidates()
    assert all(m >= 1.0 - 1e-9 for _c, m in wide)
    d_wide = Domain("wide", tuple(c for c, _m in wide))
    d_part = Domain("part", tuple(c for c, _m in wide[:20]))
    claim = RelativeClaim("kronecker_M_ge_1", True, d_wide, UNIVERSAL)
    assert claim.is_downward_closed
    assert claim.entails_on(d_part)


# ---- cycle 033: the normal form generalises to ARITY, and two preconditions ------------------

import itertools as _it


def _pairs(d):
    return list(_it.combinations(sorted(d.members), 2))


def test_RELATIONAL_CLAIMS_FIT_THE_NORMAL_FORM_AT_ARITY_2():
    """**Resolves the soft spot I declared at cycle 031 (HITL #117).**

    The derivation assumed aggregation over independent PER-ELEMENT values, and relational
    claims — "the domain contains two elements that disagree", exactly what
    `find_aliasing_witness` computes — did not obviously fit. They do: the repair is arity.

        Phi(O, D) = A({ phi(O, t) : t in D^k })

    Monotonicity survives untouched because D subset D' implies D^k subset D'^k. Measured at
    k = 2 over a chain built to CROSS the thresholds (my first chain fired everything at step
    one and read INVARIANT across the board, which measured nothing).
    """
    from prometheus_math.relative_claim import UNIVERSAL, probe_monotonicity

    pi, truth = lambda v: v % 5, lambda v: v % 2
    seq = [(0, 1, 2), (0, 1, 2, 5), (0, 1, 2, 5, 20), (0, 1, 2, 5, 20, 21, 22)]
    chain = [Domain(f"d{k}", t) for k, t in enumerate(seq)]

    alias = lambda d: 1 if any(pi(a) == pi(b) and truth(a) != truth(b)
                               for a, b in _pairs(d)) else 0
    consistent = lambda d: 1 if all(not (pi(a) == pi(b) and truth(a) != truth(b))
                                    for a, b in _pairs(d)) else 0

    assert [alias(d) for d in chain] == [0, 1, 1, 1]
    assert [consistent(d) for d in chain] == [1, 0, 0, 0]
    assert probe_monotonicity(alias, chain) == EXISTENTIAL
    assert probe_monotonicity(consistent, chain) == UNIVERSAL


def test_min_over_pairs_is_a_holding_universal():
    """A min over D^2 can only fall as the domain grows — monotone down, UNIVERSAL."""
    from prometheus_math.relative_claim import UNIVERSAL, probe_monotonicity
    seq = [(0, 10, 20), (0, 5, 10, 20), (0, 1, 5, 10, 20)]
    chain = [Domain(f"m{k}", t) for k, t in enumerate(seq)]
    mindist = lambda d: min(abs(a - b) for a, b in _pairs(d))
    assert [mindist(d) for d in chain] == [10, 5, 1]
    assert probe_monotonicity(mindist, chain) == UNIVERSAL


def test_P1_a_predicate_that_READS_the_domain_size_is_AGGREGATE():
    """Precondition 1, and it is cycle 031's rate defect reappearing at arity 2. "At least half
    of D is even" reads |D|, so it is normalised, so it moves both ways."""
    from prometheus_math.relative_claim import probe_monotonicity
    seq = [(0, 2), (0, 2, 1, 3), (0, 2, 1, 3, 5, 7), (0, 2, 1, 3, 5, 7, 4, 6)]
    chain = [Domain(f"e{k}", t) for k, t in enumerate(seq)]
    half = lambda d: 1 if sum(1 for v in d.members if v % 2 == 0) >= len(d) / 2 else 0
    assert [half(d) for d in chain] == [1, 1, 0, 1]
    assert probe_monotonicity(half, chain) == AGGREGATE


def test_P2_AN_UNORDERED_VALUE_IS_NOW_REFUSED_RATHER_THAN_CLASSIFIED():
    """**Precondition 2, found by my own instrument misbehaving.**

    Asked to classify an ARGMIN — which pair is closest, a selection rather than a magnitude —
    `probe_monotonicity` returned UNIVERSAL. Not because the claim is universal, but because
    Python orders tuples lexicographically and the comparisons went through silently. The
    verdict was meaningless.

    It now refuses. Booleanise the selection first and it classifies honestly.
    """
    from prometheus_math.relative_claim import probe_monotonicity

    seq = [(0, 10, 20), (0, 5, 10, 20), (0, 1, 5, 10, 20)]
    chain = [Domain(f"a{k}", t) for k, t in enumerate(seq)]
    argmin = lambda d: min(_pairs(d), key=lambda t: (abs(t[0] - t[1]), t))

    with pytest.raises(ClaimError) as exc:
        probe_monotonicity(argmin, chain)
    assert "meaningfully ordered" in str(exc.value)

    booleanised = lambda d: 1 if argmin(d) == (0, 1) else 0
    assert [booleanised(d) for d in chain] == [0, 0, 1]
    assert probe_monotonicity(booleanised, chain) == EXISTENTIAL


def test_P2_still_accepts_bools_and_numbers():
    """The guard must not break the ordinary cases it exists to protect."""
    from prometheus_math.relative_claim import INVARIANT, probe_monotonicity
    chain = [Domain(f"d{k}", tuple(range(m))) for k, m in enumerate((2, 4, 8))]
    assert probe_monotonicity(lambda d: len(d), chain) == EXISTENTIAL      # int
    assert probe_monotonicity(lambda d: len(d) / 2.0, chain) == EXISTENTIAL  # float
    assert probe_monotonicity(lambda d: True, chain) == INVARIANT          # bool
