"""Test TOOL_TROPICAL_RANK against Riemann-Roch predictions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.tropical_rank import tropical_rank, tropical_rank_graph, is_winnable


def test_K3_riemann_roch():
    """K_3 triangle has genus 1; r(D) = deg(D) - 1 for deg >= 1."""
    A = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    # deg 2
    assert tropical_rank(A, [2, 0, 0]) == 1
    assert tropical_rank(A, [1, 1, 0]) == 1
    # deg 3
    assert tropical_rank(A, [3, 0, 0]) == 2
    # deg -1 divisor: impossible to be effective (deg must match), rank = -1
    assert tropical_rank(A, [1, 0, -2]) == -1
    print("[K_3 Riemann-Roch] 4/4 OK")


def test_K3_is_winnable():
    A = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    assert is_winnable(A, [2, 0, 0]) is True
    assert is_winnable(A, [1, 0, -2]) is False   # deg -1, can't be effective
    assert is_winnable(A, [0, 0, 0]) is True  # trivial divisor is winnable (rank 0)
    print("[is_winnable] 3/3 OK")


def test_tree():
    """Tree (acyclic connected): genus 0. r(D) = deg(D) for any effective D."""
    # Path v0 - v1 - v2 (genus 0)
    A = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    assert tropical_rank(A, [2, 0, 0]) == 2  # deg 2, genus 0
    assert tropical_rank(A, [0, 1, 0]) == 1  # deg 1
    print("[tree (genus 0)] 2/2 OK")


def test_labeled_graph():
    """tropical_rank_graph with arbitrary labels."""
    V = ['a', 'b', 'c']
    E = [('a', 'b'), ('b', 'c'), ('a', 'c')]  # K_3
    degrees = [('a', 2), ('b', 0), ('c', 0)]
    r = tropical_rank_graph(V, E, degrees)
    assert r == 1
    print("[labeled graph] OK")


if __name__ == '__main__':
    test_K3_riemann_roch()
    test_K3_is_winnable()
    test_tree()
    test_labeled_graph()
    print("\nALL TROPICAL_RANK TESTS PASS")
