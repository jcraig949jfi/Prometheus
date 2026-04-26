"""Test TOOL_CM_ORDER_DATA on the 13 CM-over-Q discriminants."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.cm_order_data import cm_order_data


def test_fundamental_heegners():
    """9 Heegner discs are all fundamental with f=1, h=1."""
    for D in [-3, -4, -7, -8, -11, -19, -43, -67, -163]:
        r = cm_order_data(D)
        assert r['fundamental_disc'] == D, f"D={D}: {r}"
        assert r['cm_conductor'] == 1
        assert r['class_number'] == 1
        assert r['is_maximal'] is True
    print("[9 Heegner fundamentals] OK")


def test_non_maximal_orders():
    """Four non-maximal-order CM-j-over-Q cases."""
    cases = [
        (-12, -3, 2),   # Q(√-3), f=2
        (-16, -4, 2),   # Q(i), f=2
        (-27, -3, 3),   # Q(√-3), f=3
        (-28, -7, 2),   # Q(√-7), f=2
    ]
    for D, d_K_exp, f_exp in cases:
        r = cm_order_data(D)
        assert r['fundamental_disc'] == d_K_exp, f"D={D}: d_K={r['fundamental_disc']}, expected {d_K_exp}"
        assert r['cm_conductor'] == f_exp, f"D={D}: f={r['cm_conductor']}, expected {f_exp}"
        assert r['class_number'] == 1
        assert r['is_maximal'] is False
    print(f"[non-maximal orders] {len(cases)}/{len(cases)} OK")


def test_ring_class_polynomials():
    """Known rational j-values."""
    # j(E) for CM by d_K=-3 is 0, for -4 is 1728, etc.
    assert 'x' == cm_order_data(-3)['ring_class_polynomial']
    assert '1728' in cm_order_data(-4)['ring_class_polynomial']
    assert '54000' in cm_order_data(-12)['ring_class_polynomial']  # j = 54000
    assert '287496' in cm_order_data(-16)['ring_class_polynomial']
    assert '12288000' in cm_order_data(-27)['ring_class_polynomial']
    print("[ring class polynomials] OK")


def test_bad_input():
    """Non-negative D raises ValueError."""
    try:
        cm_order_data(12)
        assert False, "expected ValueError for positive D"
    except ValueError:
        pass
    # D=2 is not ≡ 0 or 1 mod 4
    try:
        cm_order_data(-2)
        assert False, "expected ValueError for D=-2"
    except ValueError:
        pass
    print("[bad input] OK")


def test_non_fundamental_with_h_greater_than_1():
    """D=-15 = -15 fundamental (d≡1 mod 4), h(O_K) = 2."""
    r = cm_order_data(-15)
    assert r['fundamental_disc'] == -15
    assert r['cm_conductor'] == 1
    assert r['class_number'] == 2
    # Hilbert class polynomial of Q(√-15) is a quadratic
    assert r['degree'] == 2
    print("[-15 non-trivial class group] OK")


if __name__ == '__main__':
    test_fundamental_heegners()
    test_non_maximal_orders()
    test_ring_class_polynomials()
    test_bad_input()
    test_non_fundamental_with_h_greater_than_1()
    print("\nALL CM_ORDER_DATA TESTS PASS")
