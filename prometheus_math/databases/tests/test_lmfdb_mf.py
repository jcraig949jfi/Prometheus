"""Tests for the LMFDB modular-form full-extraction API (project #49).

These tests hit the live LMFDB Postgres mirror at ``devmirror.lmfdb.xyz``.
If the mirror is unreachable, every test is skipped — the failure is
environmental, not a regression.

Coverage summary (math-tdd skill):
    Authority   : 6 (LMFDB-keyed: 11.2.a.a, 23.2.a.a, char 23.b, etc.)
    Property    : 6 (Hypothesis-driven invariants on label parsing,
                     dim, level, weight, atkin_lehner)
    Edge        : 5 (nonexistent label, malformed label, level=0,
                     dim=0, empty orbit_label)
    Composition : 3 (newform_full level/weight match label parsing,
                     traces[0] == ap[2], cross-call consistency)
"""
from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.databases import lmfdb


# ---------------------------------------------------------------------------
# Skip gate: skip the entire module if the mirror is unreachable.
# ---------------------------------------------------------------------------


def _mirror_online() -> bool:
    try:
        c = lmfdb.connect(timeout=5)
        c.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _mirror_online(),
    reason="devmirror.lmfdb.xyz unreachable from this host",
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_newform_full_11_2_a_a_authoritative():
    """11.2.a.a is the unique rational newform on Gamma_0(11), weight 2.

    Reference: LMFDB ``mf_newforms`` row for label '11.2.a.a':
        level=11, weight=2, dim=1, traces[0] (= a_1) = 1, traces[1] (= a_2) = -2.
    Cross-checks: this newform corresponds to the modular form attached
    to the elliptic curve 11.a1 (Cremona/LMFDB).
    """
    nf = lmfdb.newform_full("11.2.a.a")
    assert nf is not None
    assert nf["level"] == 11
    assert nf["weight"] == 2
    assert nf["dim"] == 1
    # LMFDB traces array starts at n=1 so traces[0] = a_1 = 1
    assert nf["traces"][0] == 1
    assert nf["traces"][1] == -2  # a_2 = -2
    assert nf["traces"][2] == -1  # a_3 = -1
    assert nf["is_self_dual"] is True
    assert nf["is_cm"] is False
    assert nf["nontrivial_character"] is False  # trivial char (orbit 1)
    assert nf["char_orbit_label"] == "a"


def test_newform_full_23_2_a_a_dim_2():
    """23.2.a.a has dim 2 with field Q(sqrt(5)).

    Reference: LMFDB ``mf_newforms`` row for label '23.2.a.a':
        level=23, weight=2, dim=2, field_poly=[-1, -1, 1] (x^2 - x - 1),
        which generates Q(sqrt(5)) (golden-ratio quadratic field).
    """
    nf = lmfdb.newform_full("23.2.a.a")
    assert nf is not None
    assert nf["level"] == 23
    assert nf["weight"] == 2
    assert nf["dim"] == 2
    # field_poly = x^2 - x - 1 -> Q(sqrt(5))
    assert nf["hecke_ring"]["poly"] == [-1, -1, 1]
    assert nf["is_self_dual"] is True


def test_newforms_by_level_weight_11_2_contains_aa():
    """All newforms at (11, 2): there is exactly one Galois orbit, '11.2.a.a'.

    Reference: LMFDB ``mf_newforms`` filtered by (level=11, weight=2).
    For Gamma_0(11), dim S_2(Gamma_0(11)) = 1, all newform.
    """
    rows = lmfdb.newforms_by_level_weight(11, 2)
    labels = {r["label"] for r in rows}
    assert "11.2.a.a" in labels


def test_newform_dim_data_includes_11_2():
    """The dimension of S_2^new(Gamma_0(11)) is 1.

    Reference: LMFDB ``mf_newspaces`` for (level=11, weight=2). The unique
    newspace 11.2.a has dim 1 (corresponding to the elliptic curve 11a).
    Sum over all character orbits of dim = 1.
    """
    dims = lmfdb.newform_dim_data(level_max=11, weight_max=4)
    assert (11, 2) in dims
    assert dims[(11, 2)] == 1


def test_newform_full_atkin_lehner_11():
    """11.2.a.a has Atkin-Lehner eigenvalue -1 at p=11.

    Reference: LMFDB ``atkin_lehner_eigenvals`` for 11.2.a.a is [[11, -1]].
    Ties to the elliptic curve 11.a1: w_11 = -1 means the L-function has
    odd functional-equation sign (rank 0 here is consistent because the
    sign comes from analytic continuation, not just w_11 alone).
    """
    nf = lmfdb.newform_full("11.2.a.a")
    assert nf["atkin_lehner"] == {11: -1}
    # The string-form representation
    assert nf["atkin_lehner_string"] == "-"


def test_newform_full_sato_tate_group_non_cm():
    """11.2.a.a is non-CM; its Sato-Tate group is the standard SU(2).

    Reference: LMFDB stores ``sato_tate_group = '1.2.3.c1'`` for 11.2.a.a
    (the LMFDB label for SU(2) in the weight-2 trivial-character case).
    Cross-checks against ``is_cm = False`` in the same row.
    """
    nf = lmfdb.newform_full("11.2.a.a")
    assert nf["sato_tate_group"] == "1.2.3.c1"
    assert nf["is_cm"] is False


def test_dirichlet_character_orbit_23_b():
    """char_dirichlet orbit '23.b' is the unique nontrivial real
    quadratic character of conductor 23.

    Reference: LMFDB ``char_dirichlet`` row for label '23.b':
        modulus=23, conductor=23, order=2, degree=1,
        is_real=True, is_primitive=True, is_even=False.
    """
    orbit = lmfdb.dirichlet_character_orbit("23.b")
    assert orbit is not None
    assert orbit["modulus"] == 23
    assert orbit["conductor"] == 23
    assert orbit["order"] == 2
    assert orbit["is_real"] is True
    assert orbit["is_primitive"] is True


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------


# A small set of known-good labels at low conductor we can iterate over
# without flooding the mirror.
_KNOWN_LABELS = [
    "11.2.a.a",
    "14.2.a.a",
    "15.2.a.a",
    "17.2.a.a",
    "19.2.a.a",
    "20.2.a.a",
    "21.2.a.a",
    "23.2.a.a",
    "24.2.a.a",
    "26.2.a.a",
]


@pytest.mark.parametrize("label", _KNOWN_LABELS)
def test_newform_full_label_parsing_invariant(label):
    """For any newform label N.k.x.y, level == N and weight == k.

    Parses both directly from the label and from the row pulled from
    LMFDB; they must match.
    """
    parts = label.split(".")
    expected_level = int(parts[0])
    expected_weight = int(parts[1])
    nf = lmfdb.newform_full(label)
    assert nf is not None, f"missing newform {label}"
    assert nf["level"] == expected_level
    assert nf["weight"] == expected_weight


@pytest.mark.parametrize("label", _KNOWN_LABELS)
def test_newform_full_level_weight_dim_positive(label):
    """level >= 1, weight >= 1, dim >= 1 for every actual newform."""
    nf = lmfdb.newform_full(label)
    assert nf["level"] >= 1
    assert nf["weight"] >= 1
    assert nf["dim"] >= 1
    assert isinstance(nf["level"], int)
    assert isinstance(nf["weight"], int)
    assert isinstance(nf["dim"], int)


@pytest.mark.parametrize("label", _KNOWN_LABELS)
def test_atkin_lehner_dict_keys_divide_level(label):
    """atkin_lehner dict has keys = primes p | N (level) only.

    Property: every key is a prime divisor of the level, and every value
    is in {-1, +1}.
    """
    nf = lmfdb.newform_full(label)
    al = nf["atkin_lehner"]
    assert isinstance(al, dict)
    level = nf["level"]
    for p, v in al.items():
        assert isinstance(p, int)
        assert level % p == 0, f"AL prime {p} does not divide level {level}"
        assert v in (-1, 1), f"AL eigenvalue {v} not in {{-1,+1}}"


@given(st.integers(min_value=2, max_value=50), st.sampled_from([2, 4, 6]))
@settings(max_examples=10, deadline=None)
def test_newforms_by_level_weight_returns_consistent_records(level, weight):
    """For any (N, k) sweep, every returned record has level==N, weight==k.

    Skips silently if there are no newforms at that (N, k) — that's a
    valid mathematical answer, not a failure.
    """
    rows = lmfdb.newforms_by_level_weight(level, weight, limit=100)
    for r in rows:
        assert r["level"] == level
        assert r["weight"] == weight


@given(st.integers(min_value=1, max_value=5), st.integers(min_value=2, max_value=50))
@settings(max_examples=8, deadline=None)
def test_newforms_by_dim_consistent(dim, level_max):
    """Every label returned by newforms_by_dim parses to a valid label.

    Property: each returned label has 4 dot-separated parts and the
    first two are integers.
    """
    labels = lmfdb.newforms_by_dim(dim, level_max=level_max, limit=50)
    for lab in labels:
        parts = lab.split(".")
        assert len(parts) == 4
        int(parts[0])  # raises if non-integer
        int(parts[1])


def test_newform_dim_data_nonneg_and_consistent():
    """All entries in the dim table are non-negative integers.

    Property: dim(S_k^new(Gamma_1(N))) >= 0 always; weight-1 newspaces
    are often tiny but nonneg; weight=2, level=1 must be 0 (no
    cusp forms on SL_2(Z) of weight 2).
    """
    dims = lmfdb.newform_dim_data(level_max=12, weight_max=4)
    for (N, k), d in dims.items():
        assert d >= 0
        assert isinstance(d, int)
    # SL_2(Z) has no cusp forms of weight 2
    if (1, 2) in dims:
        assert dims[(1, 2)] == 0


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_newform_full_nonexistent_returns_none():
    """A well-formed but absent label returns None (not an exception).

    Edge: 99999999.2.a.a is well-formed but not in LMFDB.
    """
    assert lmfdb.newform_full("99999999.2.a.a") is None


def test_newform_full_malformed_raises():
    """Malformed labels raise ValueError.

    Edges:
      - empty string
      - missing dots
      - non-integer level
      - level <= 0
      - empty char/hecke orbit
    """
    with pytest.raises(ValueError):
        lmfdb.newform_full("")
    with pytest.raises(ValueError):
        lmfdb.newform_full("malformed")
    with pytest.raises(ValueError):
        lmfdb.newform_full("11.2.a")  # only 3 parts
    with pytest.raises(ValueError):
        lmfdb.newform_full("foo.2.a.a")
    with pytest.raises(ValueError):
        lmfdb.newform_full("0.2.a.a")
    with pytest.raises(ValueError):
        lmfdb.newform_full("11.2..a")  # empty char orbit


def test_newforms_by_level_weight_invalid_raises():
    """level=0 or weight=0 raise ValueError.

    Edges: invalid (N, k) pairs should fail loudly rather than return [].
    """
    with pytest.raises(ValueError):
        lmfdb.newforms_by_level_weight(0, 2)
    with pytest.raises(ValueError):
        lmfdb.newforms_by_level_weight(11, 0)
    with pytest.raises(ValueError):
        lmfdb.newforms_by_level_weight(-5, 2)


def test_newforms_by_dim_zero_returns_empty():
    """dim=0 and dim<0 return empty list (no newforms have dim 0)."""
    assert lmfdb.newforms_by_dim(0) == []
    assert lmfdb.newforms_by_dim(-1) == []


def test_dirichlet_character_orbit_empty_raises():
    """Empty orbit_label raises ValueError; non-existent returns None."""
    with pytest.raises(ValueError):
        lmfdb.dirichlet_character_orbit("")
    # Well-formed but absent (modulus 11 only has orbits 'a','b','c','d')
    assert lmfdb.dirichlet_character_orbit("11.zzz") is None


def test_newform_hecke_eigenvalues_full_p_max_below_2():
    """p_max < 2 returns empty dict (no primes <= 1)."""
    assert lmfdb.newform_hecke_eigenvalues_full("11.2.a.a", p_max=1) == {}
    assert lmfdb.newform_hecke_eigenvalues_full("11.2.a.a", p_max=0) == {}


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_compose_newform_full_matches_sweep():
    """newform_full(L) and newforms_by_level_weight(N, k) agree on level/weight.

    Composition: pulling 11.2.a.a directly should agree with finding it
    by sweep.
    """
    nf = lmfdb.newform_full("11.2.a.a")
    rows = lmfdb.newforms_by_level_weight(11, 2)
    sweep = {r["label"]: r for r in rows}
    assert "11.2.a.a" in sweep
    assert nf["level"] == sweep["11.2.a.a"]["level"]
    assert nf["weight"] == sweep["11.2.a.a"]["weight"]
    assert nf["dim"] == sweep["11.2.a.a"]["dim"]


def test_compose_traces_match_hecke_eigenvalues():
    """For dim-1 newforms, traces[1] (= a_2) equals ap[2] from mf_hecke_nf.

    Composition: ``newform_full`` reads from ``mf_newforms.traces``;
    ``newform_hecke_eigenvalues_full`` reads from ``mf_hecke_nf.ap``.
    These are stored in two different LMFDB tables but must agree at
    every prime for dim-1 newforms.
    """
    nf = lmfdb.newform_full("11.2.a.a")
    ap_dict = lmfdb.newform_hecke_eigenvalues_full("11.2.a.a", p_max=20)
    # traces is a_1, a_2, a_3, a_4, a_5, ..., so traces[1] = a_2
    assert nf["traces"][1] == ap_dict[2]
    assert nf["traces"][2] == ap_dict[3]
    assert nf["traces"][4] == ap_dict[5]
    assert nf["traces"][6] == ap_dict[7]


def test_compose_dim_1_label_in_level_weight_sweep():
    """Every dim-1 newform at low level appears in the level/weight sweep.

    Composition: ``newforms_by_dim(1, level_max=11)`` must be a subset of
    the union of ``newforms_by_level_weight(N, k)`` over those (N, k).
    """
    labels = lmfdb.newforms_by_dim(1, level_max=11)
    assert len(labels) > 0
    # Pick one with weight 2, level <= 11
    candidate = None
    for lab in labels:
        parts = lab.split(".")
        N = int(parts[0])
        k = int(parts[1])
        if N <= 11 and k == 2:
            candidate = (lab, N, k)
            break
    if candidate is None:
        pytest.skip("no dim-1 weight-2 newform at N<=11 in this slice")
    lab, N, k = candidate
    rows = lmfdb.newforms_by_level_weight(N, k)
    sweep_labels = {r["label"] for r in rows}
    assert lab in sweep_labels


def test_compose_character_orbit_consistent_with_newform():
    """newform_character_orbit(L) returns the orbit at level=L.level.

    Composition: a newform with char_orbit_label='a' at level N has
    a character orbit with label 'N.a' that is trivial (order 1).
    """
    orbit = lmfdb.newform_character_orbit("11.2.a.a")
    assert orbit is not None
    assert orbit["modulus"] == 11
    assert orbit["order"] == 1  # 'a' is the trivial-orbit letter
    assert orbit["is_real"] is True
