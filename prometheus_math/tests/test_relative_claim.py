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
