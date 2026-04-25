"""Test TOOL_GALOIS_GROUP against classical Galois group computations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.galois_group import galois_group, is_abelian, disc_is_square


def test_quadratics():
    # Non-square disc: Gal = S2 = Z/2
    g = galois_group('x^2-2')
    assert g['order'] == 2
    assert g['degree'] == 2
    assert g['parity'] == -1
    assert g['is_abelian'] is True
    # Square disc (perfect square, reducible would fail — irreducible with square disc is rare for deg 2)
    # Actually x^2+1 has disc -4, not a square in Q. Disc is square iff G ⊆ A_n, degree 2 has no A_2 proper subgroup beyond trivial.
    print("[quadratics] OK")


def test_cubics():
    # S3: generic cubic
    g = galois_group('x^3-2')
    assert g['name'] == 'S3'
    assert g['order'] == 6
    assert g['parity'] == -1
    assert not g['is_abelian']

    # A3 = Z/3 (disc is square). x^3 - 3x - 1 has disc 81 = 9^2.
    g = galois_group('x^3-3*x-1')
    assert g['order'] == 3
    assert g['parity'] == 1
    assert g['is_abelian'] is True
    print("[cubics] 2/2 OK")


def test_quartics():
    # D(4): x^4 - 2
    g = galois_group('x^4-2')
    assert g['order'] == 8
    assert 'D' in g['name'] or '4' in g['name']
    assert not g['is_abelian']

    # S4: generic quartic
    g = galois_group('x^4-x-1')
    assert g['order'] == 24
    assert not g['is_abelian']

    # V4 (Klein): x^4 - 10*x^2 + 1 = (x^2 - (5+2sqrt(6)))(x^2 - (5-2sqrt(6)))
    # Root is sqrt(2)+sqrt(3). Gal = V4 = Z/2 x Z/2, order 4, abelian.
    g = galois_group('x^4-10*x^2+1')
    assert g['order'] == 4
    assert g['is_abelian'] is True
    print("[quartics] 3/3 OK")


def test_cyclotomics():
    # Phi_5: Gal = (Z/5)^* = Z/4, order 4, cyclic, abelian
    g = galois_group('polcyclo(5)')
    assert g['order'] == 4
    assert g['is_abelian'] is True

    # Phi_7: Gal = Z/6, abelian
    g = galois_group('polcyclo(7)')
    assert g['order'] == 6
    assert g['is_abelian'] is True

    # Phi_8: Gal = (Z/8)^* = Z/2 x Z/2 (Klein), order 4, abelian
    g = galois_group('polcyclo(8)')
    assert g['order'] == 4
    assert g['is_abelian'] is True
    print("[cyclotomics] 3/3 OK")


def test_quintics():
    # S5: generic quintic
    g = galois_group('x^5-x-1')
    assert g['order'] == 120
    assert not g['is_abelian']

    # F(5) = 5:4 Frobenius group: x^5 - 2
    g = galois_group('x^5-2')
    assert g['order'] == 20
    assert not g['is_abelian']

    # C5 cyclic quintic: min poly of 2*cos(2 pi/11)
    # x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1
    g = galois_group('x^5+x^4-4*x^3-3*x^2+3*x+1')
    assert g['order'] == 5
    assert g['is_abelian'] is True
    print("[quintics] 3/3 OK")


def test_helpers():
    assert is_abelian('x^3-3*x-1') is True
    assert is_abelian('x^3-2') is False
    assert disc_is_square('x^3-3*x-1') is True
    assert disc_is_square('x^3-2') is False
    print("[helpers] 4/4 OK")


def test_list_input():
    # x^3 - 2 via coeffs
    g = galois_group([1, 0, 0, -2])
    assert g['order'] == 6
    assert g['name'] == 'S3'
    print("[list input] OK")


if __name__ == '__main__':
    test_quadratics()
    test_cubics()
    test_quartics()
    test_cyclotomics()
    test_quintics()
    test_helpers()
    test_list_input()
    print("\nALL GALOIS_GROUP TESTS PASS")
