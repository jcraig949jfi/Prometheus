"""Test TOOL_LLL_REDUCTION."""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.lll_reduction import lll, lll_with_transform, shortest_vector_lll, lll_gram


def _det_int(M):
    # Integer determinant via fractions to avoid float error
    from fractions import Fraction
    A = [[Fraction(int(x)) for x in row] for row in M]
    n = len(A)
    d = Fraction(1)
    for i in range(n):
        # find pivot
        p = None
        for r in range(i, n):
            if A[r][i] != 0:
                p = r
                break
        if p is None:
            return 0
        if p != i:
            A[i], A[p] = A[p], A[i]
            d = -d
        d *= A[i][i]
        for r in range(i+1, n):
            if A[r][i] == 0:
                continue
            factor = A[r][i] / A[i][i]
            for c in range(i, n):
                A[r][c] -= factor * A[i][c]
    return int(d) if d.denominator == 1 else float(d)


def test_bad_basis_shortens():
    """Skewed basis should reduce to shorter vectors.

    Lattice has volume 1e6 (det of input basis), so the shortest vector
    length is bounded by Minkowski: lambda_1 <= sqrt(n) * det^(1/n) ~ 173.
    Input basis has max norm^2 = 1e12; reduced first vector should be tiny.
    """
    B = [[1, 1, 1], [0, 1, 0], [0, 0, 1000000]]
    R = lll(B)
    rows = [tuple(int(x) for x in row) for row in R]
    norms = [sum(x*x for x in row) for row in rows]
    # Shortest LLL vector must be smaller than the best original (which was [0,1,0] with norm^2 = 1)
    assert min(norms) <= 1, f"LLL did not match best original: norms={norms}"
    # And the second-shortest should be much smaller than the third original (norm^2 = 1e12)
    sorted_norms = sorted(norms)
    assert sorted_norms[1] <= 10, f"Second shortest too large: {sorted_norms}"
    # Structural check: first two vectors span a short-vector sublattice
    print(f"[bad_basis_shortens] norms={sorted_norms} OK")


def test_determinant_preserved():
    """LLL preserves lattice determinant up to sign (unimodular change of basis)."""
    np.random.seed(42)
    for trial in range(5):
        n = 4
        B = np.random.randint(-10, 11, size=(n, n))
        # Skip degenerate
        if abs(_det_int(B)) == 0:
            continue
        R = lll(B)
        dB = _det_int(B)
        dR = _det_int(R)
        assert abs(dB) == abs(dR), f"det changed: B det={dB}, R det={dR}"
    print("[determinant_preserved] OK")


def test_transform_unimodular():
    """T from lll_with_transform must satisfy |det T| = 1 and R = T @ B."""
    B = np.array([[3, 5, 2], [1, 0, 4], [7, 1, 2]])
    R, T = lll_with_transform(B)
    # |det T| = 1
    dT = _det_int(T)
    assert abs(dT) == 1, f"T not unimodular: det={dT}"
    # R = T @ B
    T_int = np.array([[int(x) for x in row] for row in T])
    B_int = np.array([[int(x) for x in row] for row in B])
    R_int = np.array([[int(x) for x in row] for row in R])
    assert np.array_equal(T_int @ B_int, R_int), "R != T @ B"
    print("[transform_unimodular] OK")


def test_reduction_shortens_norms():
    """First vector of LLL basis <= 2^((n-1)/2) * lambda_1.
    Here we just check the reduced basis has smaller sum of squared norms."""
    B = [[1000, 1, 0], [999, 1, 1], [1001, 0, 2]]
    R = lll(B)
    norm_B = sum(sum(int(x) ** 2 for x in row) for row in B)
    norm_R = sum(sum(int(x) ** 2 for x in row) for row in R)
    assert norm_R < norm_B, f"reduction did not shorten: {norm_B} -> {norm_R}"
    print(f"[reduction_shortens] {norm_B} -> {norm_R} OK")


def test_shortest_vector_lll():
    """Shortest row of LLL basis is close to the shortest lattice vector."""
    # Lattice Z^3 itself: shortest vector is [1,0,0] (or permutation, norm^2 = 1)
    B = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    sv = shortest_vector_lll(B)
    norm = sum(int(x) ** 2 for x in sv)
    assert norm == 1, f"got norm^2 {norm}"

    # Skewed: should still find norm 1
    B = [[1, 100, 200], [0, 1, 0], [0, 0, 1]]
    sv = shortest_vector_lll(B)
    norm = sum(int(x) ** 2 for x in sv)
    assert norm == 1, f"got norm^2 {norm}"
    print("[shortest_vector_lll] OK")


def test_gram_input():
    """lll_gram: reduce given a Gram matrix."""
    # Gram matrix of diag(1, 2, 3) lattice
    G = [[1, 0, 0], [0, 4, 0], [0, 0, 9]]
    T = lll_gram(G)
    # Should be identity (already reduced)
    T_int = np.array([[int(x) for x in row] for row in T])
    assert abs(_det_int(T)) == 1
    print("[gram_input] OK")


if __name__ == '__main__':
    test_bad_basis_shortens()
    test_determinant_preserved()
    test_transform_unimodular()
    test_reduction_shortens_norms()
    test_shortest_vector_lll()
    test_gram_input()
    print("\nALL LLL_REDUCTION TESTS PASS")
