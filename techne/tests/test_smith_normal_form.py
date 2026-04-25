"""Test TOOL_SMITH_NORMAL_FORM."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.smith_normal_form import (
    smith_normal_form, invariant_factors, abelian_group_structure
)


def test_invariant_factors_basic():
    # Cohen Example 2.4.14-ish
    assert invariant_factors([[2, 4, 4], [-6, 6, 12], [10, -4, -16]]) == [2, 6, 12]
    # Diagonal input
    assert invariant_factors([[2, 0, 0], [0, 4, 0], [0, 0, 6]]) == [2, 2, 12]
    # Identity
    assert invariant_factors([[1, 0], [0, 1]]) == [1, 1]
    # Zero row
    assert invariant_factors([[2, 0], [0, 0]]) == [2]
    print("[invariant_factors_basic] 4/4 OK")


def test_divides_chain():
    """Invariant factors must satisfy d_i | d_{i+1}."""
    import random
    random.seed(0)
    for trial in range(10):
        m = random.randint(3, 5)
        n = random.randint(3, 5)
        M = [[random.randint(-5, 5) for _ in range(n)] for _ in range(m)]
        ifs = invariant_factors(M)
        for i in range(len(ifs) - 1):
            assert ifs[i+1] % ifs[i] == 0, f"divisibility failed at {i}: {ifs}"
    print("[divides_chain] 10/10 OK")


def test_full_snf_shape():
    M = [[2, 4, 4], [-6, 6, 12], [10, -4, -16]]
    D = smith_normal_form(M)
    assert D.shape == (3, 3)
    # Diagonal
    for i in range(3):
        for j in range(3):
            if i != j:
                assert int(D[i, j]) == 0
    # Ordering: sympy gives ascending, which is d_1 | d_2 | ... by default
    diag = [int(D[i, i]) for i in range(3)]
    assert diag == [2, 6, 12]
    print("[full_snf_shape] OK")


def test_homology_circle():
    """H_0(S^1) = Z, H_1(S^1) = Z. Model: 3 vertices, 3 edges in a triangle.

    Boundary B_1: edges -> vertices. Columns of B_1 are +end - start.
    For triangle v0->v1, v1->v2, v2->v0:
      e1=(v1-v0), e2=(v2-v1), e3=(v0-v2)
    As a 3x3 matrix (rows = vertices, cols = edges):
      [[-1, 0, 1], [1, -1, 0], [0, 1, -1]]
    Rank(B_1) = 2, kernel dim = 1 -> H_1 = Z.
    H_0 = Z^3 / im(B_1) = Z (vertices mod connected component).
    """
    B1 = [[-1, 0, 1], [1, -1, 0], [0, 1, -1]]
    ifs = invariant_factors(B1)
    # Rank = 2, so two nonzero invariant factors, both should be 1 (no torsion)
    assert ifs == [1, 1], f"got {ifs}"

    # H_0 structure: Z^3 / im(B_1), presentation matrix = B1
    h0 = abelian_group_structure(B1)
    assert h0['free_rank'] == 1, f"H_0 free rank: {h0}"
    assert h0['torsion'] == []
    assert h0['trivial_factors'] == 2
    print("[homology_circle] OK")


def test_homology_with_torsion():
    """Presentation for Z/2 x Z/6: diag(2, 6). Invariant factors [2, 6]."""
    st = abelian_group_structure([[2, 0], [0, 6]])
    assert st['torsion'] == [2, 6]
    assert st['free_rank'] == 0

    # Z/4 x Z/6 should reduce to Z/2 x Z/12 via SNF
    st = abelian_group_structure([[4, 0], [0, 6]])
    assert st['torsion'] == [2, 12], f"got {st}"
    assert st['free_rank'] == 0
    print("[torsion] 2/2 OK")


def test_empty_cases():
    """Degenerate shapes."""
    # 1x1 matrix
    assert invariant_factors([[7]]) == [7]
    # Zero matrix
    assert invariant_factors([[0, 0], [0, 0]]) == []
    # Row vector
    assert invariant_factors([[3, 6, 9]]) == [3]
    # Column vector
    assert invariant_factors([[3], [6], [9]]) == [3]
    print("[empty_cases] 4/4 OK")


if __name__ == '__main__':
    test_invariant_factors_basic()
    test_divides_chain()
    test_full_snf_shape()
    test_homology_circle()
    test_homology_with_torsion()
    test_empty_cases()
    print("\nALL SMITH_NORMAL_FORM TESTS PASS")
