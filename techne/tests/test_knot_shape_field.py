"""Test TOOL_KNOT_SHAPE_FIELD against known invariant trace fields."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.knot_shape_field import knot_shape_field, polredabs


def test_figure_8():
    """4_1 trace field = Q(sqrt(-3)), disc = -3, poly = x^2 - x + 1."""
    r = knot_shape_field('4_1')
    assert r['degree'] == 2
    assert r['disc'] == -3
    assert 'x^2 - x + 1' in r['poly']
    assert r['is_hyperbolic'] is True
    print(f"[4_1] {r['poly']} disc={r['disc']} OK")


def test_5_2():
    """5_2 invariant trace field = LMFDB 3.1.23.1, cubic of disc -23."""
    r = knot_shape_field('5_2')
    assert r['degree'] == 3
    assert r['disc'] == -23, f"got disc {r['disc']}"
    print(f"[5_2] {r['poly']} disc={r['disc']} OK")


def test_torus_knot_raises():
    """Trefoil (3_1) is a torus knot — NOT hyperbolic. Should raise."""
    try:
        knot_shape_field('3_1')
        assert False, "expected ValueError for non-hyperbolic knot"
    except ValueError as e:
        assert 'not hyperbolic' in str(e), f"wrong error: {e}"
    print("[3_1 non-hyperbolic] correctly raised OK")


def test_polredabs_utility():
    assert polredabs('x^3-2*x^2+3*x-1') == 'x^3 - x^2 + 1'
    assert polredabs('x^2+5') == 'x^2 + 5'
    # List input
    assert polredabs([1, 0, 5]) == 'x^2 + 5'
    print("[polredabs] 3/3 OK")


def test_false_fit_rejection():
    """At high precision, algdep can return spurious low-degree polys with
    astronomical coefficients that pass a loose tolerance check. Regression
    guard for Ergon bug 1776902425706-0."""
    import cypari
    from lib.knot_shape_field import _shape_from_poly_verify
    _pari = cypari.pari
    # Pick a transcendental-looking number: pi/e in high precision
    _pari.allocatemem(1_000_000_000)
    z = _pari('Pi/exp(1) + I*sqrt(2)/Pi')  # not algebraic of low degree
    # At bits_prec=400, the coefficient-height guard should reject any
    # spurious low-degree "fit" rather than returning an astronomical disc.
    r = _shape_from_poly_verify(z, max_deg=2, bits_prec=400)
    # Either None (clean reject), or a poly with small discriminant.
    if r is not None:
        deg, poly_str, disc = r
        assert abs(disc) < 10**20, (
            f"false-fit not rejected: got deg={deg}, poly={poly_str}, disc={disc}"
        )
    print("[false-fit rejection] OK")


if __name__ == '__main__':
    test_figure_8()
    test_5_2()
    test_torus_knot_raises()
    test_polredabs_utility()
    test_false_fit_rejection()
    print("\nALL KNOT_SHAPE_FIELD TESTS PASS")
