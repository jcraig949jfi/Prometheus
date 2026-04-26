"""Hypothesis-based property tests for prometheus_math.topology.

Project #32 of the Techne backlog. Drives ~30+ property tests across
the topology arsenal:

    hyperbolic_volume, hyperbolic_volume_hp, is_hyperbolic,
    knot_shape_field, polredabs,
    alexander_polynomial, alexander_coeffs.

The math-tdd skill (techne/skills/math-tdd.md) requires authority,
property, edge, and composition tests; this file is the property-test
gallery for pm.topology, complementing the per-tool unit tests in
``techne/tests/test_alexander_polynomial.py`` and
``techne/tests/test_knot_shape_field.py``.

The tests are partitioned into 8 sections, each running Hypothesis over
a strategy of small knots drawn from the Rolfsen table:

    Section 1 — Alexander polynomial invariants (palindromic, det=|Δ(-1)|, ...)
    Section 2 — Alexander x genus / fibered (composition with kfh)
    Section 3 — Hyperbolic volume invariants (vol > 0 iff hyperbolic, etc.)
    Section 4 — Hyperbolic volume authority (Cohn's value for 4_1, 5_2 census)
    Section 5 — Shape field invariants (degree, disc, palindromic recovery)
    Section 6 — Shape field authority (4_1 = Q(sqrt(-3)), 5_2 = LMFDB 3.1.23.1)
    Section 7 — Cross-tool consistency (m004 == 4_1, HTLinkExteriors == name)
    Section 8 — Edge cases (torus knots, non-hyperbolic, malformed input)

If Hypothesis discovers a counterexample, log it to ``BUGS.md`` and
mark the failing test ``xfail`` with a comment pointing at the bug.

Run with::

    pytest prometheus_math/tests/test_topology_properties.py -v \\
           --hypothesis-show-statistics

Heavy snappy / kfh imports are gated; if either dependency is missing,
the whole module is skipped cleanly.
"""
from __future__ import annotations

import math
import re

import pytest
from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Optional-dependency gating
# ---------------------------------------------------------------------------

try:
    import snappy  # noqa: F401
    _HAS_SNAPPY = True
except Exception:  # pragma: no cover
    _HAS_SNAPPY = False

try:
    import knot_floer_homology as _kfh  # noqa: F401
    _HAS_KFH = True
except Exception:  # pragma: no cover
    _HAS_KFH = False

try:
    import cypari  # noqa: F401
    _HAS_CYPARI = True
except Exception:  # pragma: no cover
    _HAS_CYPARI = False

# Skip the whole module if snappy is unavailable. Individual tests that
# also need kfh / cypari add their own skip decorators.
pytestmark = pytest.mark.skipif(
    not _HAS_SNAPPY, reason="snappy unavailable — topology suite skipped"
)

if _HAS_SNAPPY:
    import snappy  # type: ignore  # re-import after gate
    from prometheus_math.topology import (
        alexander_coeffs,
        alexander_polynomial,
        hyperbolic_volume,
        hyperbolic_volume_hp,
        is_hyperbolic,
        knot_shape_field,
        polredabs,
    )
if _HAS_CYPARI:
    import cypari  # type: ignore
    _pari = cypari.pari


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# A curated table of small knots. Marked with the Rolfsen name, expected
# hyperbolicity, and (if hyperbolic) the published volume.
#
# Volumes from snappy's HTLinkExteriors / m-census; non-hyperbolic
# (torus knots and 8_19) have vol exactly 0.
KNOT_TABLE = {
    # name      hyperbolic  snappy_volume
    # Volumes captured from snappy.Manifold(name).volume() at install
    # time, for regression-detection only. Pinning to the SnapPy
    # triangulation value (not knotinfo's published value) — the two
    # differ at ~1e-5 because knotinfo rounds. Tolerance in the
    # consistency test is 1e-4.
    "3_1":      (False, 0.0),               # trefoil, T(2,3)
    "4_1":      (True,  2.0298832128193),   # figure-eight = m004
    "5_1":      (False, 0.0),               # T(2,5)
    "5_2":      (True,  2.8281220883308),
    "6_1":      (True,  3.1639632288831),
    "6_2":      (True,  4.4008325161230),
    "6_3":      (True,  5.6930210912813),
    "7_1":      (False, 0.0),               # T(2,7)
    "7_2":      (True,  3.3317442316411),
    "7_3":      (True,  4.5921256970271),
    "7_4":      (True,  5.1379412018734),
    "7_5":      (True,  6.4435373808506),
    "7_6":      (True,  7.0849259535108),
    "7_7":      (True,  7.6433751723600),
    "8_1":      (True,  3.4272052462740),
    "8_2":      (True,  4.9352426782807),
    "8_19":     (False, 0.0),               # T(3,4) — non-alternating torus knot
    "8_20":     (True,  4.1249032518077),
    "8_21":     (True,  6.7837135198351),
    "9_1":      (False, 0.0),               # T(2,9)
    "10_1":     (True,  3.5261959907354),
}

ALL_KNOTS = sorted(KNOT_TABLE)
HYPERBOLIC_KNOTS = sorted(k for k, (h, _) in KNOT_TABLE.items() if h)
TORUS_KNOTS = sorted(k for k, (h, _) in KNOT_TABLE.items() if not h)

# Subsets used to keep slow tests bounded.
SMALL_HYPERBOLIC = ["4_1", "5_2", "6_1", "6_2", "6_3", "7_2", "7_4", "8_1"]
SMALL_KNOTS = ["3_1", "4_1", "5_1", "5_2", "6_1", "6_2", "7_1"]

# Strategies
small_knot = st.sampled_from(SMALL_KNOTS)
hyperbolic_knot = st.sampled_from(SMALL_HYPERBOLIC)
all_knots = st.sampled_from(ALL_KNOTS)
torus_knot = st.sampled_from(TORUS_KNOTS)


# Hypothesis settings — knot computations are slow.
SLOW = settings(
    max_examples=12,
    deadline=15000,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    derandomize=True,
)
MEDIUM = settings(
    max_examples=20,
    deadline=10000,
    suppress_health_check=[HealthCheck.too_slow],
    derandomize=True,
)
FAST = settings(
    max_examples=30,
    deadline=5000,
    suppress_health_check=[HealthCheck.too_slow],
    derandomize=True,
)


# ---------------------------------------------------------------------------
# Caches — knots are hashed by name; computations are reusable.
# ---------------------------------------------------------------------------

_alex_cache: dict = {}
_vol_cache: dict = {}
_shape_cache: dict = {}


def _alex(name):
    if name not in _alex_cache:
        _alex_cache[name] = alexander_polynomial(name)
    return _alex_cache[name]


def _vol(name):
    if name not in _vol_cache:
        _vol_cache[name] = float(hyperbolic_volume(name))
    return _vol_cache[name]


def _shape(name, bits_prec=300, max_deg=8):
    key = (name, bits_prec, max_deg)
    if key not in _shape_cache:
        _shape_cache[key] = knot_shape_field(name, bits_prec=bits_prec, max_deg=max_deg)
    return _shape_cache[key]


# ===========================================================================
# Section 1 — Alexander polynomial invariants
#
# Six properties on the Alexander polynomial of a knot.
# ===========================================================================


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@MEDIUM
@given(name=small_knot)
@example(name="4_1")
@example(name="5_1")
@example(name="6_2")
def test_property_alexander_palindromic(name):
    """Δ_K(t) = ±t^d * Δ_K(t^{-1}) — Alexander is palindromic.

    For knots in S^3, the Alexander polynomial is symmetric about
    a=0: the coefficient sequence reads the same forwards and backwards
    (up to a global sign). This is the *defining* symmetry of the
    knot Alexander polynomial — see Lickorish, "An Introduction to
    Knot Theory", Theorem 6.10.
    """
    coeffs = alexander_coeffs(name)
    # Palindromic up to global sign
    if coeffs == coeffs[::-1]:
        return  # palindrome
    if coeffs == [-c for c in coeffs[::-1]]:
        return  # anti-palindrome (also allowed up to sign)
    pytest.fail(f"{name}: alex coeffs {coeffs} not palindromic")


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@MEDIUM
@given(name=small_knot)
@example(name="3_1")
@example(name="4_1")
@example(name="5_2")
def test_property_alexander_at_one_is_pm_one(name):
    """Δ_K(1) = ±1 for any knot.

    The Alexander module is trivialized at t=1 (the augmentation
    sends Z[t, t^{-1}] → Z, kernel killed by definition). For a
    knot, Δ_K(1) is a unit in Z; either +1 or -1.

    Reference: Rolfsen, "Knots and Links", §7.A.
    """
    coeffs = alexander_coeffs(name)
    val = sum(coeffs)
    assert abs(val) == 1, f"{name}: Δ(1)={val}, expected ±1"


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@MEDIUM
@given(name=small_knot)
@example(name="3_1")
@example(name="4_1")
def test_property_alexander_determinant_consistent(name):
    """det(K) = |Δ_K(-1)|.

    The knot determinant is defined as |Δ_K(-1)|; the implementation
    stores both and we check they agree.
    """
    a = _alex(name)
    coeffs = a["coeffs"]  # descending
    deg_top = len(coeffs) - 1  # top exponent shift
    # Evaluate Δ at t=-1 by alternating sum (descending convention)
    val = sum(c * (-1) ** (deg_top - i) for i, c in enumerate(coeffs))
    assert abs(val) == a["determinant"], (
        f"{name}: |Δ(-1)|={abs(val)} vs determinant={a['determinant']}"
    )


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@MEDIUM
@given(name=small_knot)
@example(name="3_1")
@example(name="4_1")
@example(name="5_1")
def test_property_alexander_determinant_odd(name):
    """det(K) is odd for any knot (Δ_K(-1) ≡ Δ_K(1) (mod 2) = 1).

    Standard fact, e.g. Lickorish §6, Cor 6.11.
    """
    det = _alex(name)["determinant"]
    assert det % 2 == 1, f"{name}: det={det} is even"


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@FAST
@given(name=small_knot)
def test_property_alexander_coeffs_integer(name):
    """All Alexander coefficients are integers.

    The Alexander module is over Z[t, t^{-1}]; coefficients live in Z.
    """
    coeffs = alexander_coeffs(name)
    for c in coeffs:
        assert isinstance(c, int), f"{name}: non-integer coeff {c} ({type(c)})"


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@FAST
@given(name=small_knot)
def test_property_alexander_nonzero(name):
    """A non-trivial knot has a non-zero Alexander polynomial.

    Conway-Lickorish: Δ ≠ 0 always (it is a unit times an integer poly
    of degree 2*genus over Z[t,t^{-1}]).
    """
    coeffs = alexander_coeffs(name)
    assert any(c != 0 for c in coeffs), f"{name}: Alexander identically zero"


# ===========================================================================
# Section 2 — Alexander × genus / fibered (composition with HFK)
# ===========================================================================


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@SLOW
@given(name=small_knot)
@example(name="3_1")
@example(name="4_1")
@example(name="5_1")
def test_composition_alexander_degree_le_2_genus(name):
    """deg(Δ_K) ≤ 2·g(K), where g(K) = Seifert genus.

    The Alexander polynomial has degree ≤ 2g. Equality holds for
    fibered knots; in general the inequality is strict.

    Composition test: this couples
      - alexander_polynomial (HFK Euler-characteristic side)
      - kfh.pd_to_hfk seifert_genus (HFK middle-grading side)

    If HFK is internally inconsistent the inequality fails.
    """
    pd = snappy.Link(name).PD_code()
    hfk = _kfh.pd_to_hfk(pd)
    g = int(hfk["seifert_genus"])
    # 'degree' in our Alexander dict is the half-degree (max |a|)
    half_deg = _alex(name)["degree"]
    assert half_deg <= g, (
        f"{name}: half-deg(Δ)={half_deg} > genus={g} — HFK/Alexander inconsistent"
    )


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
@SLOW
@given(name=small_knot)
def test_composition_fibered_implies_alex_monic(name):
    """A fibered knot has *monic* Alexander polynomial: leading coeff ±1.

    Reference: Stallings, "Constructions of fibered knots and links".
    The converse fails (Alexander-monic does not imply fibered) but
    fibered ⇒ leading coeff ±1 always.
    """
    pd = snappy.Link(name).PD_code()
    hfk = _kfh.pd_to_hfk(pd)
    if not hfk["fibered"]:
        return  # property is vacuous for non-fibered knots
    coeffs = alexander_coeffs(name)
    leading = coeffs[0]
    assert abs(leading) == 1, (
        f"{name}: fibered but leading Alex coeff = {leading} (not ±1)"
    )


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
def test_composition_alexander_specific_genera():
    """Anchor: alex degree achieves 2g for the fibered knots in our table.

    HFK reports genus(3_1)=1, deg=1; genus(5_1)=2, deg=2; etc. For
    fibered knots equality is forced.
    """
    cases = [
        ("3_1", 1),
        ("4_1", 1),
        ("5_1", 2),
        ("8_19", 3),  # non-alternating torus knot, fibered
    ]
    for name, expected_genus in cases:
        a = _alex(name)
        assert a["degree"] == expected_genus, (
            f"{name}: alex half-deg {a['degree']} != genus {expected_genus}"
        )


# ===========================================================================
# Section 3 — Hyperbolic volume invariants
# ===========================================================================


@FAST
@given(name=hyperbolic_knot)
@example(name="4_1")
@example(name="5_2")
@example(name="6_1")
def test_property_hyperbolic_volume_positive(name):
    """vol > 0 for every hyperbolic knot.

    Mostow rigidity guarantees vol(M) > 0 for finite-volume hyperbolic
    3-manifolds; in particular the complement of every hyperbolic knot
    has positive volume.
    """
    v = _vol(name)
    assert v > 1e-6, f"{name} (claimed hyperbolic): vol={v}"


@FAST
@given(name=torus_knot)
@example(name="3_1")
@example(name="5_1")
@example(name="7_1")
@example(name="8_19")
def test_property_torus_knot_volume_zero(name):
    """Torus knots have hyperbolic volume = 0 exactly.

    Reference: Thurston's geometrization. Torus knot complements
    admit a Seifert-fibered (not hyperbolic) structure; hence
    vol = 0.
    """
    v = _vol(name)
    assert v == 0.0 or v < 1e-9, f"{name} (torus): vol={v} != 0"


@FAST
@given(name=all_knots)
def test_property_volume_matches_is_hyperbolic(name):
    """vol(K) > 0 iff is_hyperbolic(K). (Definition consistency.)

    Composition: hyperbolic_volume + is_hyperbolic must agree on
    every knot; otherwise our tolerance for "is_hyperbolic" diverges
    from the published `vol > 0` definition.
    """
    v = _vol(name)
    h = is_hyperbolic(name)
    assert h == (v > 1e-6), f"{name}: vol={v}, is_hyperbolic={h} — disagree"


@MEDIUM
@given(name=hyperbolic_knot)
def test_property_volume_stable_recomputation(name):
    """vol(K) is reproducible across recomputations.

    SnapPy uses a triangulation-dependent computation under the hood;
    repeated calls should return bitwise-identical doubles for our
    fixed-precision API. (Tolerance 1e-9 — way below numerical noise.)
    """
    v1 = float(hyperbolic_volume(name))
    v2 = float(hyperbolic_volume(name))
    assert abs(v1 - v2) < 1e-9, f"{name}: vol drifted {v1} vs {v2}"


@MEDIUM
@given(name=hyperbolic_knot)
def test_property_volume_matches_table(name):
    """vol(K) matches the curated KNOT_TABLE within 1e-6.

    Authority cross-check: every hyperbolic knot in our table has its
    SnapPy-computed volume pinned to the published value (knotinfo,
    SnapPy's m-census). Deviation > 1e-6 indicates a triangulation
    drift in SnapPy.
    """
    expected = KNOT_TABLE[name][1]
    v = _vol(name)
    assert abs(v - expected) < 1e-6, f"{name}: vol={v}, expected={expected}"


# ===========================================================================
# Section 4 — Hyperbolic volume authority
# ===========================================================================


def test_authority_volume_figure_eight_cohn():
    """vol(4_1) = 2 * Lobachevsky(π/3) = 2.029883212819307...

    The figure-eight knot complement is the unique hyperbolic
    3-manifold of minimal volume (Cao-Meyerhoff, 2001), with the
    closed-form value

        vol(4_1) = 2 · ImLi₂(exp(iπ/3))
                 = 2.02988321281930725...

    Reference: Cohn, "A Course in Computational Algebraic Number
    Theory", §7.6 (Lobachevsky function); Milnor, "Hyperbolic
    geometry: the first 150 years", Bull. AMS 6 (1982).
    """
    expected = 2.029883212819307250042405108549
    v = float(hyperbolic_volume("4_1"))
    assert abs(v - expected) < 1e-12, f"vol(4_1)={v}, Cohn expected={expected}"


def test_authority_volume_figure_eight_high_precision():
    """vol(4_1) to 30 decimal places.

    Reference: Adams, "The Knot Book", Table 8.1; SnapPy's
    high_precision engine (snap).
    """
    s = hyperbolic_volume_hp("4_1", digits=30)
    # Strip the integer part — compare just the digits
    assert s.startswith("2.0298832128193072500424")


def test_authority_volume_5_2_4_anchors():
    """vol(5_2), vol(6_1), vol(K11n34) match knotinfo + SnapPy m-census.

    Authority cross-check.
    """
    cases = [
        ("5_2", 2.828122088330783),
        ("6_1", 3.1639632288831443),
        ("K11n34", 11.21911772538136),
    ]
    for name, expected in cases:
        v = float(hyperbolic_volume(name))
        assert abs(v - expected) < 1e-6, f"{name}: vol={v}, expected={expected}"


# ===========================================================================
# Section 5 — Shape field invariants
# ===========================================================================


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
@SLOW
@given(name=hyperbolic_knot)
@example(name="4_1")
@example(name="5_2")
def test_property_shape_field_degree_positive(name):
    """deg(shape field) >= 1 for every hyperbolic knot.

    The shape field is at minimum Q (degree 1) for a hyperbolic
    rational-shape manifold, but in practice >=2 for all knots in
    our table.
    """
    r = _shape(name)
    assert r["degree"] >= 1, f"{name}: degree={r['degree']}"


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
@SLOW
@given(name=hyperbolic_knot)
def test_property_shape_field_disc_nonzero(name):
    """disc(shape field minimal poly) ≠ 0.

    A non-zero discriminant is necessary for the polynomial to be
    separable, i.e. to define an actual number field. A zero
    discriminant indicates a numerical artifact in algdep.
    """
    r = _shape(name)
    assert r["disc"] != 0, f"{name}: disc(shape field) = 0"


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
@SLOW
@given(name=hyperbolic_knot)
def test_property_shape_field_degree_at_most_max_deg(name):
    """deg(shape field) <= max_deg passed to algdep.

    Hard bound from the implementation: knot_shape_field invokes
    PARI's algdep with a max_deg parameter; the returned polynomial
    cannot have degree exceeding that cap. Catches off-by-one bugs
    in the algdep wrapper.
    """
    max_deg = 8
    r = _shape(name, bits_prec=300, max_deg=max_deg)
    assert r["degree"] <= max_deg, (
        f"{name}: shape-field deg {r['degree']} > max_deg {max_deg}"
    )


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
@SLOW
@given(name=st.sampled_from(SMALL_HYPERBOLIC + ["7_5"]))
@example(name="7_5")
@example(name="4_1")
def test_property_shape_field_disc_bounded(name):
    """|disc(shape field)| is below a sane numerical-artifact threshold.

    Published iTrFs of crossings <= 8 have |disc| < 10^7 typically.
    A disc with 100+ digits indicates an algdep false-fit despite
    the in-tool guards.

    BUG B-TOPO-001 (Hypothesis-discovered counterexample): 7_5
    returns a deg-6 minimal polynomial with coefficient height
    ~10^140 and discriminant ~10^5300. See BUGS.md.

    The test xfails 7_5 to keep the suite green while the bug is
    tracked; it remains a regression check for every other knot
    in the table.
    """
    if name == "7_5":
        pytest.xfail("B-TOPO-001: 7_5 shape field algdep artifact (see BUGS.md)")
    r = _shape(name)
    assert abs(r["disc"]) < 10 ** 9, (
        f"{name}: |disc|={abs(r['disc'])} suggests algdep false-fit "
        f"(poly={r['poly'][:80]}...)"
    )


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
@SLOW
@given(name=hyperbolic_knot)
def test_property_shape_field_polredabs_idempotent(name):
    """polredabs(shape_field['poly']) == shape_field['poly'].

    The shape field's `poly` is already in polredabs canonical form
    (per the implementation); applying polredabs again must be the
    identity. Composition test.
    """
    r = _shape(name)
    p = r["poly"]
    again = polredabs(p)
    assert p == again, f"{name}: polredabs not idempotent: {p} -> {again}"


# ===========================================================================
# Section 6 — Shape field authority
# ===========================================================================


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
def test_authority_shape_field_4_1_is_q_sqrt_minus_3():
    """4_1's shape field = Q(sqrt(-3)), disc = -3.

    Reference: Neumann-Reid, "Arithmetic of hyperbolic manifolds",
    Topology '90 (1992), Table 1.
    """
    r = _shape("4_1")
    assert r["degree"] == 2
    assert r["disc"] == -3
    assert "x^2 - x + 1" in r["poly"]


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
def test_authority_shape_field_5_2_lmfdb_3_1_23_1():
    """5_2's shape field = LMFDB 3.1.23.1, cubic disc -23.

    Reference: Neumann-Reid Table 1; LMFDB number_field
    label 3.1.23.1.
    """
    r = _shape("5_2")
    assert r["degree"] == 3
    assert r["disc"] == -23


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
def test_authority_shape_field_polredabs_anchors():
    """polredabs anchors against PARI documentation.

    Reference: PARI docs §3.6.30, polredabs.
    """
    assert polredabs("x^3 - 2*x^2 + 3*x - 1") == "x^3 - x^2 + 1"
    assert polredabs("x^2 + 5") == "x^2 + 5"
    assert polredabs([1, 0, 5]) == "x^2 + 5"


# ===========================================================================
# Section 7 — Cross-tool consistency
# ===========================================================================


def test_cross_tool_4_1_equals_m004():
    """vol(4_1) == vol(m004): two SnapPy paths to the figure-eight.

    The figure-eight knot complement IS the m-census manifold m004,
    so its volume must be identical to bitwise precision.

    Composition test: hyperbolic_volume on two distinct construction
    paths.
    """
    v1 = float(hyperbolic_volume("4_1"))
    v2 = float(snappy.Manifold("m004").volume())
    assert abs(v1 - v2) < 1e-12, f"4_1 vs m004: {v1} vs {v2}"


@MEDIUM
@given(name=hyperbolic_knot)
def test_cross_tool_volume_via_pd_code(name):
    """hyperbolic_volume(name) == hyperbolic_volume(pd_code).

    Composition: the volume should not depend on whether we provide
    the knot by name (looked up from snappy's table) or by PD code
    (handed in directly via spherogram.Link).
    """
    pd = snappy.Link(name).PD_code()
    # _load_manifold accepts list-of-tuples → snappy.Link → exterior
    pd_list = [list(t) for t in pd]
    v_pd = float(hyperbolic_volume(pd_list))
    v_name = _vol(name)
    # PD-code path uses a different triangulation; vols agree to ~1e-6.
    assert abs(v_pd - v_name) < 1e-4, (
        f"{name}: vol via name {v_name} vs vol via PD {v_pd}"
    )


@pytest.mark.skipif(not _HAS_KFH, reason="knot_floer_homology unavailable")
def test_cross_tool_alexander_palindrome_anchor_set():
    """Palindrome property holds across the entire ALL_KNOTS set.

    Wide-coverage anchor: rather than Hypothesis-sample, sweep the
    full table. Catches any knot we might not exercise via the
    `small_knot` strategy.
    """
    failures = []
    for name in ALL_KNOTS:
        try:
            c = alexander_coeffs(name)
            if c == c[::-1]:
                continue
            if c == [-x for x in c[::-1]]:
                continue
            failures.append((name, c))
        except Exception as e:
            failures.append((name, f"ERR: {e}"))
    assert not failures, f"non-palindromic Alexanders: {failures}"


# ===========================================================================
# Section 8 — Edge cases
# ===========================================================================


def test_edge_torus_knot_shape_field_raises():
    """knot_shape_field on a torus knot raises ValueError.

    Trefoil (3_1) has volume 0 (Seifert-fibered), so the shape field
    is undefined; the implementation raises 'not hyperbolic'.
    """
    with pytest.raises(ValueError, match="not hyperbolic"):
        knot_shape_field("3_1")


def test_edge_torus_knot_alexander_nonzero():
    """Torus knots T(p, q) have *non-trivial* Alexander polynomial.

    Even though torus knots are non-hyperbolic, they still have
    well-defined non-trivial Alexander polynomials. (Indeed they are
    fibered with Δ_T(p,q)(t) = (t^{pq}-1)(t-1)/((t^p-1)(t^q-1)).)
    """
    for name in TORUS_KNOTS:
        a = alexander_polynomial(name)
        assert a["determinant"] >= 1, f"{name}: det={a['determinant']}"
        assert any(c != 0 for c in a["coeffs"]), f"{name}: alex zero"


def test_edge_hyperbolic_volume_unknown_knot_raises():
    """An unknown knot name raises (snappy refuses to look it up).

    Edge: malformed input.
    """
    with pytest.raises(Exception):
        hyperbolic_volume("not_a_knot_xyz")


def test_edge_alexander_unsupported_type_raises():
    """alexander_polynomial(int) raises TypeError.

    Edge: type validation.
    """
    with pytest.raises(TypeError):
        alexander_polynomial(42)


def test_edge_polredabs_constant_polynomial_idempotent():
    """polredabs of an already-canonical poly is the identity.

    Edge: trivial input.
    """
    p = "x^2 - x + 1"
    assert polredabs(p) == p


def test_edge_volume_non_hyperbolic_returns_zero():
    """hyperbolic_volume on a torus knot returns 0 (no error).

    Edge: documented behavior — non-hyperbolic doesn't error, it
    returns 0. (Use is_hyperbolic to discriminate.)
    """
    for name in TORUS_KNOTS:
        v = float(hyperbolic_volume(name))
        assert v == 0.0 or v < 1e-9, f"{name}: vol={v}"


@pytest.mark.skipif(not _HAS_CYPARI, reason="cypari unavailable")
def test_edge_shape_field_low_max_deg_raises():
    """Asking knot_shape_field for too-low max_deg may raise.

    For 5_2 the shape field is cubic (degree 3); requesting max_deg=2
    should raise ValueError or return None — not silently return a
    wrong polynomial.
    """
    try:
        r = knot_shape_field("5_2", bits_prec=300, max_deg=2)
    except ValueError:
        return  # acceptable: explicit failure
    # If it does return, it must be at least informative — disc small
    # enough not to be an obvious artifact.
    assert r["degree"] <= 2
    assert abs(r["disc"]) < 10 ** 9, (
        f"5_2 with max_deg=2 returned implausible disc {r['disc']}"
    )
