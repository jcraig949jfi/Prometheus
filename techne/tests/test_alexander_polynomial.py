"""Test TOOL_ALEXANDER_POLYNOMIAL against knotinfo standard values."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.alexander_polynomial import alexander_polynomial, alexander_coeffs


def test_trefoil():
    """3_1: Δ = t - 1 + t^{-1}; coeffs = [1, -1, 1] descending."""
    r = alexander_polynomial('3_1')
    assert r['coeffs'] == [1, -1, 1]
    assert r['determinant'] == 3
    assert r['degree'] == 1
    assert not r['is_unit']
    print("[3_1 trefoil] OK")


def test_figure_8():
    """4_1: Δ = -t + 3 - t^{-1}; det = 5."""
    r = alexander_polynomial('4_1')
    assert r['coeffs'] == [-1, 3, -1]
    assert r['determinant'] == 5
    assert r['degree'] == 1
    print("[4_1 figure-8] OK")


def test_5_1():
    """5_1 cinquefoil: Δ = t^2 - t + 1 - t^{-1} + t^{-2}."""
    r = alexander_polynomial('5_1')
    assert r['coeffs'] == [1, -1, 1, -1, 1]
    assert r['determinant'] == 5
    assert r['degree'] == 2
    print("[5_1 cinquefoil] OK")


def test_5_2():
    """5_2: Δ = 2t - 3 + 2t^{-1}; det = 7."""
    r = alexander_polynomial('5_2')
    assert r['coeffs'] == [2, -3, 2]
    assert r['determinant'] == 7
    print("[5_2] OK")


def test_symmetry():
    """Δ_K(t) = Δ_K(t^{-1}) for knots: coefficient list is a palindrome."""
    for name in ['3_1', '4_1', '5_1', '5_2', '6_1', '7_4']:
        c = alexander_coeffs(name)
        assert c == c[::-1], f"{name}: {c} not palindromic"
    print("[palindrome symmetry] 6/6 OK")


def test_convenience_function():
    assert alexander_coeffs('3_1') == [1, -1, 1]
    assert alexander_coeffs('4_1') == [-1, 3, -1]
    print("[alexander_coeffs] OK")


if __name__ == '__main__':
    test_trefoil()
    test_figure_8()
    test_5_1()
    test_5_2()
    test_symmetry()
    test_convenience_function()
    print("\nALL ALEXANDER_POLYNOMIAL TESTS PASS")
