"""Test TOOL_CLASS_NUMBER against LMFDB / Cohen tables."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.class_number import class_number, class_group, regulator_nf


def test_imaginary_quadratic():
    """Imaginary quadratic fields — heavily tabulated."""
    # (polynomial_str, expected_h)
    cases = [
        ('x^2+1', 1),     # Q(i)
        ('x^2+2', 1),     # Q(sqrt(-2))
        ('x^2+3', 1),     # Q(sqrt(-3))
        ('x^2+5', 2),     # smallest non-trivial
        ('x^2+6', 2),
        ('x^2+7', 1),
        ('x^2+10', 2),
        ('x^2+14', 4),
        ('x^2+15', 2),
        ('x^2+23', 3),    # smallest h=3
        ('x^2+47', 5),    # smallest h=5
        ('x^2+163', 1),   # Heegner
        ('x^2+71', 7),    # smallest h=7
    ]
    for pol, expected in cases:
        got = class_number(pol)
        assert got == expected, f"{pol}: got {got}, expected {expected}"
    print(f"[imag quadratic] {len(cases)}/{len(cases)} OK")


def test_real_quadratic():
    """Real quadratic — Cohen Table 1.1."""
    cases = [
        ('x^2-2', 1),
        ('x^2-5', 1),
        ('x^2-10', 2),
        ('x^2-15', 2),
        ('x^2-79', 3),    # smallest real quadratic h=3
        ('x^2-82', 4),
    ]
    for pol, expected in cases:
        got = class_number(pol)
        assert got == expected, f"{pol}: got {got}, expected {expected}"
    print(f"[real quadratic] {len(cases)}/{len(cases)} OK")


def test_cubic():
    """Cubic fields — well-known examples."""
    cases = [
        ('x^3-2', 1),      # Q(2^(1/3))
        ('x^3-3', 1),
        ('x^3+x-1', 1),    # smallest cubic disc -23
    ]
    for pol, expected in cases:
        got = class_number(pol)
        assert got == expected, f"{pol}: got {got}, expected {expected}"
    print(f"[cubic] {len(cases)}/{len(cases)} OK")


def test_list_input():
    """Accept coefficient list [a_n,...,a_0]."""
    assert class_number([1, 0, 5]) == 2           # x^2 + 5
    assert class_number([1, 0, 0, -2]) == 1       # x^3 - 2
    assert class_number([1, 0, 23]) == 3          # x^2 + 23
    print("[list input] 3/3 OK")


def test_class_group_structure():
    """Verify full class group structure."""
    g = class_group('x^2+5')
    assert g['h'] == 2
    assert g['structure'] == [2]
    assert g['signature'] == (0, 1)
    assert g['disc'] == -20

    g = class_group('x^2+23')
    assert g['h'] == 3
    assert g['structure'] == [3]

    # Q(sqrt(-14)) has Cl = Z/4Z so structure = [4]
    g = class_group('x^2+14')
    assert g['h'] == 4
    assert g['structure'] == [4]
    print("[class_group] 3/3 OK")


def test_regulator_nf():
    """Regulator: imag quad = 1; real quad matches log(fundamental unit)."""
    import math
    # Imag quad convention: R = 1
    assert abs(regulator_nf('x^2+1') - 1.0) < 1e-10
    assert abs(regulator_nf('x^2+5') - 1.0) < 1e-10
    # Q(sqrt(2)) fund unit = 1 + sqrt(2), reg = log(1+sqrt(2)) ~ 0.881374
    r = regulator_nf('x^2-2')
    expected = math.log(1 + math.sqrt(2))
    assert abs(r - expected) < 1e-8, f"got {r}, expected {expected}"
    # Q(sqrt(5)) fund unit = golden ratio, reg = log((1+sqrt(5))/2) ~ 0.481212
    r = regulator_nf('x^2-5')
    expected = math.log((1 + math.sqrt(5)) / 2)
    assert abs(r - expected) < 1e-8, f"got {r}, expected {expected}"
    print("[regulator_nf] 4/4 OK")


if __name__ == '__main__':
    test_imaginary_quadratic()
    test_real_quadratic()
    test_cubic()
    test_list_input()
    test_class_group_structure()
    test_regulator_nf()
    print("\nALL CLASS_NUMBER TESTS PASS")
