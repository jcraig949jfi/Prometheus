"""Test TOOL_FUNCTIONAL_EQ_CHECK."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.functional_eq_check import functional_eq_check, fe_residual


def test_zeta():
    """Riemann zeta's FE is canonical."""
    r = functional_eq_check(1)
    assert r['kind'] == 'zeta'
    assert r['degree'] == 1
    assert r['satisfies'] is True
    assert r['residual_log10'] <= -10
    print(f"[zeta] residual 10^{r['residual_log10']} OK")


def test_elliptic_curves():
    """EC L-functions: FE must hold across rank 0/1/2/3."""
    cases = [
        ('11.a1', [0, -1, 1, -10, -20]),
        ('37.a1', [0, 0, 1, -1, 0]),
        ('389.a1', [0, 1, 1, -2, 0]),
        ('5077.a1', [0, 0, 1, -7, 6]),
    ]
    for label, ainv in cases:
        r = functional_eq_check(ainv)
        assert r['kind'] == 'elliptic_curve'
        assert r['degree'] == 2
        assert r['satisfies'], f"{label}: FE failed, residual 10^{r['residual_log10']}"
        assert r['conductor'] is not None
    print(f"[EC rank 0-3] {len(cases)}/{len(cases)} FE verified OK")


def test_known_conductors():
    """Sanity check: conductor matches LMFDB."""
    r = functional_eq_check([0, -1, 1, -10, -20])
    assert r['conductor'] == 11, f"got {r['conductor']}"
    r = functional_eq_check([0, 0, 1, -1, 0])
    assert r['conductor'] == 37, f"got {r['conductor']}"
    r = functional_eq_check([1, 1, 1, -352, -2689])
    assert r['conductor'] == 66
    print("[conductors] 3/3 OK")


def test_fe_residual_shortcut():
    r = fe_residual([0, 0, 1, -1, 0])
    assert r <= -10
    print(f"[fe_residual shortcut] {r} OK")


def test_threshold_tunable():
    """Can tighten threshold; should still pass on good L-functions."""
    r = functional_eq_check([0, 0, 1, -1, 0], threshold_log10=-30)
    assert r['satisfies'] is True
    print("[tight threshold] OK")


def test_bad_input():
    """Unsupported input type raises TypeError."""
    try:
        functional_eq_check(3.14)
        assert False, "expected TypeError"
    except TypeError:
        pass
    print("[bad input rejected] OK")


if __name__ == '__main__':
    test_zeta()
    test_elliptic_curves()
    test_known_conductors()
    test_fe_residual_shortcut()
    test_threshold_tunable()
    test_bad_input()
    print("\nALL FUNCTIONAL_EQ_CHECK TESTS PASS")
