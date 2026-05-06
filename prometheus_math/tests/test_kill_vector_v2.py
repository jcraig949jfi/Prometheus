"""Tests for KillVector v2 — substrate v2.3 §7 (+8 components) and §7.1
(co-occurrence + MI commitment).

Companion to ``test_kill_vector.py`` (the v1 tests). The v1 file
exercises the legacy 12-component shape; this file exercises:

  * The +8 components from Aporia Study 02 (mathematical-failure-mode
    literature).
  * Backwards-compatibility (legacy 12-component readers and to_dict /
    from_dict round-trip).
  * The ``coalescing_failure_signature`` auto-caveat at the 3+ co-
    occurring threshold.
  * ``compute_pairwise_mi`` over a synthetic corpus.
  * The pre/post-falsification classification per Q-E5.
"""
from __future__ import annotations

import math

import pytest

from prometheus_math.kill_vector import (
    ALL_COMPONENT_NAMES,
    COALESCING_FAILURE_THRESHOLD,
    KillComponent,
    KillVector,
    LEGACY_COMPONENT_NAMES,
    NEW_COMPONENT_NAMES,
    POST_FALSIFICATION_ONLY,
    PRE_FALSIFICATION_DERIVABLE,
    component_is_pre_falsification_derivable,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_component(name: str, triggered: bool = True, **kwargs) -> KillComponent:
    """Construct a KillComponent by canonical name with sensible defaults."""
    return KillComponent(
        falsifier_name=name,
        triggered=triggered,
        margin=kwargs.get("margin"),
        margin_unit=kwargs.get("margin_unit"),
        metadata=kwargs.get("metadata", {}),
    )


def _kv(*comps, candidate_hash: str = "h") -> KillVector:
    return KillVector(components=tuple(comps), candidate_hash=candidate_hash)


# ---------------------------------------------------------------------------
# Authority — registry, +8 names, classification
# ---------------------------------------------------------------------------


def test_registry_legacy_count_is_twelve():
    """Legacy 12-component registry has exactly 12 names."""
    assert len(LEGACY_COMPONENT_NAMES) == 12


def test_registry_new_components_count_is_eight():
    """The +8 expansion adds exactly 8 new component names."""
    assert len(NEW_COMPONENT_NAMES) == 8


def test_registry_full_count_is_twenty():
    """ALL_COMPONENT_NAMES = 12 legacy + 8 new = 20 total."""
    assert len(ALL_COMPONENT_NAMES) == 20


def test_registry_new_components_are_appended_not_inserted():
    """Backwards compat for content-addressed hashing: legacy names
    appear first in canonical order, new names appended at the end.
    """
    # Legacy slice matches LEGACY_COMPONENT_NAMES exactly.
    assert ALL_COMPONENT_NAMES[:12] == LEGACY_COMPONENT_NAMES
    # Tail is the new names.
    assert ALL_COMPONENT_NAMES[12:] == NEW_COMPONENT_NAMES


def test_authority_all_eight_new_components_instantiate_via_name():
    """All 8 +8 components instantiate as KillComponent via name."""
    expected_names = {
        "relativizes", "naturalizes", "local_global_gap",
        "requires_unproven_conjecture", "asymptotic_only",
        "small_case_artifact", "asymmetric_effort", "interpretive_slack",
    }
    assert set(NEW_COMPONENT_NAMES) == expected_names
    for name in NEW_COMPONENT_NAMES:
        c = _make_component(name, triggered=True)
        assert c.falsifier_name == name
        assert c.triggered is True


def test_authority_pre_falsification_classification_correct():
    """Exactly 2 components are pre-falsification-derivable per Q-E5."""
    assert PRE_FALSIFICATION_DERIVABLE == frozenset(
        {"requires_unproven_conjecture", "asymptotic_only"}
    )
    assert len(PRE_FALSIFICATION_DERIVABLE) == 2


def test_authority_post_falsification_classification_correct():
    """Exactly 6 components are post-falsification-only per Q-E5."""
    assert POST_FALSIFICATION_ONLY == frozenset({
        "relativizes", "naturalizes", "local_global_gap",
        "small_case_artifact", "asymmetric_effort", "interpretive_slack",
    })
    assert len(POST_FALSIFICATION_ONLY) == 6


def test_authority_pre_post_partition_disjoint_and_covers_eight():
    """Pre and post sets partition the +8 (disjoint, union = all 8)."""
    assert PRE_FALSIFICATION_DERIVABLE.isdisjoint(POST_FALSIFICATION_ONLY)
    union = PRE_FALSIFICATION_DERIVABLE | POST_FALSIFICATION_ONLY
    assert union == set(NEW_COMPONENT_NAMES)


def test_authority_helper_pre_falsification_derivable():
    """component_is_pre_falsification_derivable returns True for the
    2 pre-derivable names and False for everything else."""
    assert component_is_pre_falsification_derivable("requires_unproven_conjecture") is True
    assert component_is_pre_falsification_derivable("asymptotic_only") is True
    # Post-only.
    assert component_is_pre_falsification_derivable("naturalizes") is False
    assert component_is_pre_falsification_derivable("relativizes") is False
    # Legacy.
    assert component_is_pre_falsification_derivable("F1_permutation_null") is False
    assert component_is_pre_falsification_derivable("out_of_band") is False
    # Unknown name → False (not in the pre set).
    assert component_is_pre_falsification_derivable("nonexistent_name") is False


# ---------------------------------------------------------------------------
# Property — backwards compat + KillComponent shape preserved
# ---------------------------------------------------------------------------


def test_property_new_components_take_full_killcomponent_shape():
    """Each new component takes the full KillComponent shape (margin,
    margin_unit, precision_dps, method, convergence_status, stability,
    stability_pass) — no shape change."""
    c = KillComponent(
        falsifier_name="naturalizes",
        triggered=True,
        margin=0.5,
        margin_unit="absolute",
        metadata={"reason": "natural property holds"},
        precision_dps=60,
        method="exact",
        convergence_status="exact",
        stability=0.9,
    )
    assert c.falsifier_name == "naturalizes"
    assert c.margin == 0.5
    assert c.margin_unit == "absolute"
    assert c.precision_dps == 60
    assert c.method == "exact"
    assert c.convergence_status == "exact"
    assert c.stability == 0.9
    assert c.stability_pass is None


def test_property_mixed_legacy_plus_new_components():
    """A KillVector can carry legacy + new components together."""
    legacy = _make_component("F6_base_rate", triggered=True,
                             margin=-1.0, margin_unit="z_score")
    new1 = _make_component("naturalizes", triggered=True)
    new2 = _make_component("requires_unproven_conjecture", triggered=False)
    kv = _kv(legacy, new1, new2)
    assert len(kv.components) == 3
    names = [c.falsifier_name for c in kv.components]
    assert "F6_base_rate" in names
    assert "naturalizes" in names
    assert kv.triggered_count == 2


def test_property_legacy_twelve_component_reader_still_works():
    """Backwards-compat: a legacy reader iterating only over the 12
    legacy names sees them all when present, and ignores new names
    safely."""
    components = []
    for n in LEGACY_COMPONENT_NAMES:
        components.append(_make_component(n, triggered=False))
    # Append a new component.
    components.append(_make_component("naturalizes", triggered=True))
    kv = _kv(*components)

    # Legacy reader: only iterates over LEGACY names.
    legacy_seen = [
        c.falsifier_name
        for c in kv.components
        if c.falsifier_name in LEGACY_COMPONENT_NAMES
    ]
    assert len(legacy_seen) == 12
    # The legacy reader doesn't crash on the new component; the new
    # component is simply not in its visible set.
    assert "naturalizes" not in legacy_seen


def test_property_to_dict_from_dict_roundtrip_preserves_new_components():
    """to_dict / from_dict round-trip preserves +8 components without
    data loss (substrate v2.3 hard requirement)."""
    components = (
        _make_component("out_of_band", triggered=False, margin=0.0,
                        margin_unit="absolute"),
        _make_component("naturalizes", triggered=True, margin=1.0,
                        margin_unit="absolute",
                        metadata={"complexity_class": "TC0"}),
        _make_component("requires_unproven_conjecture", triggered=True,
                        metadata={"conjecture": "GRH"}),
    )
    kv = KillVector(
        components=components,
        candidate_hash="rt",
        operator_class="opTest",
        region_meta={"degree": 14},
    )
    s = kv.to_json()
    kv2 = KillVector.from_json(s)
    # Same length, same names, same triggered flags.
    assert len(kv2.components) == len(kv.components)
    for a, b in zip(kv.components, kv2.components):
        assert a.falsifier_name == b.falsifier_name
        assert a.triggered == b.triggered
        assert a.margin == b.margin
        assert a.margin_unit == b.margin_unit
        assert a.metadata == b.metadata


# ---------------------------------------------------------------------------
# Coalescing-failure-signature caveat (substrate v2.3 §7.1)
# ---------------------------------------------------------------------------


def test_caveat_threshold_is_three():
    """Substrate v2.3 §7.1 commits to threshold = 3."""
    assert COALESCING_FAILURE_THRESHOLD == 3


def test_caveat_fires_at_three_co_occurring():
    """≥3 triggered components on a single KillVector → caveat fires."""
    kv = _kv(
        _make_component("naturalizes", triggered=True),
        _make_component("requires_unproven_conjecture", triggered=True),
        _make_component("interpretive_slack", triggered=True),
    )
    assert kv.coalescing_failure_signature_caveat() == "coalescing_failure_signature"


def test_caveat_does_not_fire_at_two_co_occurring():
    """Exactly 2 triggered components → caveat does NOT fire (§7.1
    explicitly notes 2 co-occurring is allowed without flagging)."""
    kv = _kv(
        _make_component("naturalizes", triggered=True),
        _make_component("requires_unproven_conjecture", triggered=True),
        _make_component("relativizes", triggered=False),
    )
    assert kv.coalescing_failure_signature_caveat() is None


def test_caveat_does_not_fire_at_one_co_occurring():
    """Single trigger → caveat does NOT fire."""
    kv = _kv(
        _make_component("naturalizes", triggered=True),
        _make_component("requires_unproven_conjecture", triggered=False),
    )
    assert kv.coalescing_failure_signature_caveat() is None


def test_caveat_fires_on_mixed_legacy_and_new_three_triggers():
    """3+ co-occurring across legacy + new components fires the caveat
    (per §7.1: all 20 components participate)."""
    kv = _kv(
        _make_component("F6_base_rate", triggered=True, margin=-1.0,
                        margin_unit="z_score"),
        _make_component("F1_permutation_null", triggered=True),
        _make_component("naturalizes", triggered=True),
    )
    assert kv.coalescing_failure_signature_caveat() == "coalescing_failure_signature"


def test_caveat_threshold_override_works():
    """Passing threshold=2 fires the caveat at 2 co-occurring."""
    kv = _kv(
        _make_component("naturalizes", triggered=True),
        _make_component("requires_unproven_conjecture", triggered=True),
    )
    assert kv.coalescing_failure_signature_caveat(threshold=2) == "coalescing_failure_signature"
    assert kv.coalescing_failure_signature_caveat(threshold=3) is None


# ---------------------------------------------------------------------------
# Pairwise MI (substrate v2.3 §7.1 substrate-level reporting)
# ---------------------------------------------------------------------------


def test_mi_returns_dict():
    """compute_pairwise_mi returns a dict (sparse pairwise table)."""
    kvs = [
        _kv(_make_component("naturalizes", triggered=True),
            _make_component("relativizes", triggered=False),
            candidate_hash=f"h{i}")
        for i in range(5)
    ]
    out = KillVector.compute_pairwise_mi(kvs)
    assert isinstance(out, dict)


def test_mi_identical_components_have_high_mi():
    """Two perfectly-correlated boolean flags → MI ≈ 1 bit
    (theoretical maximum for binary flags with marginal=0.5)."""
    # Build a corpus where naturalizes and requires_unproven_conjecture
    # are perfectly correlated and 50/50.
    corpus = []
    for i in range(20):
        triggered = (i % 2 == 0)
        kv = _kv(
            _make_component("naturalizes", triggered=triggered),
            _make_component("requires_unproven_conjecture", triggered=triggered),
            _make_component("relativizes", triggered=False),
            candidate_hash=f"h{i}",
        )
        corpus.append(kv)
    out = KillVector.compute_pairwise_mi(corpus)
    key = ("naturalizes", "requires_unproven_conjecture")
    # With Laplace smoothing on N=20, the MI approaches but doesn't
    # reach the theoretical 1.0; check it's substantial.
    assert key in out
    assert out[key] > 0.5  # Strong correlation → high MI


def test_mi_independent_components_have_low_mi():
    """Two independent boolean flags → MI ≈ 0 bits."""
    corpus = []
    # naturalizes alternates per-record; relativizes follows a different
    # period (every 3) — they're effectively independent.
    for i in range(30):
        kv = _kv(
            _make_component("naturalizes", triggered=(i % 2 == 0)),
            _make_component("relativizes", triggered=(i % 3 == 0)),
            candidate_hash=f"h{i}",
        )
        corpus.append(kv)
    out = KillVector.compute_pairwise_mi(corpus)
    # Both have non-trivial marginals so the pair appears.
    key = ("naturalizes", "relativizes")
    if key in out:
        # Should be small (independent series) — under 0.3 bits.
        assert out[key] < 0.3


def test_mi_returns_empty_for_singleton_corpus():
    """Fewer than 2 vectors → MI undefined → empty dict."""
    out = KillVector.compute_pairwise_mi([])
    assert out == {}
    out = KillVector.compute_pairwise_mi([_kv(_make_component("naturalizes"))])
    assert out == {}


def test_mi_skips_constant_components():
    """A component that's never triggered (or always triggered) has
    marginal 0 (or 1) → analytical MI = 0 → omitted from sparse dict."""
    # naturalizes never triggers; requires_unproven_conjecture varies.
    corpus = []
    for i in range(10):
        kv = _kv(
            _make_component("naturalizes", triggered=False),
            _make_component("requires_unproven_conjecture", triggered=(i % 2 == 0)),
            candidate_hash=f"h{i}",
        )
        corpus.append(kv)
    out = KillVector.compute_pairwise_mi(corpus)
    # naturalizes has marginal=0 → no pair involving it appears in the
    # sparse output.
    for key in out:
        assert "naturalizes" not in key


def test_mi_keys_are_sorted():
    """Pair keys are sorted (a < b) for determinism."""
    corpus = []
    for i in range(15):
        kv = _kv(
            _make_component("naturalizes", triggered=(i % 2 == 0)),
            _make_component("relativizes", triggered=(i % 2 == 0)),
            candidate_hash=f"h{i}",
        )
        corpus.append(kv)
    out = KillVector.compute_pairwise_mi(corpus)
    for (a, b) in out.keys():
        assert a < b


def test_mi_restricted_component_names():
    """Passing component_names restricts the pairwise computation."""
    corpus = []
    for i in range(10):
        kv = _kv(
            _make_component("naturalizes", triggered=(i % 2 == 0)),
            _make_component("relativizes", triggered=(i % 2 == 0)),
            _make_component("interpretive_slack", triggered=(i % 3 == 0)),
            candidate_hash=f"h{i}",
        )
        corpus.append(kv)
    out = KillVector.compute_pairwise_mi(
        corpus,
        component_names=("naturalizes", "relativizes"),
    )
    # Only the (naturalizes, relativizes) pair can appear.
    for key in out:
        assert set(key) <= {"naturalizes", "relativizes"}
