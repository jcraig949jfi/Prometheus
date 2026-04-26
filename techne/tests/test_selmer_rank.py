"""Test TOOL_SELMER_RANK."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.selmer_rank import selmer_2_rank, selmer_2_data


def test_trivial_sha():
    """rank 0/1/2/3 with trivial Sha — Sel_2 = rank."""
    cases = [
        ('11.a1',   [0, -1, 1, -10, -20], 0),
        ('37.a1',   [0, 0, 1, -1, 0], 1),
        ('389.a1',  [0, 1, 1, -2, 0], 2),
        ('5077.a1', [0, 0, 1, -7, 6], 3),
    ]
    for label, ainv, expected in cases:
        got = selmer_2_rank(ainv)
        assert got == expected, f"{label}: got {got}, expected {expected}"
    print(f"[trivial Sha] {len(cases)}/{len(cases)} OK")


def test_nontrivial_sha_2():
    """571.b1: rank 0, Sha=(Z/2)^2, no 2-torsion -> Sel_2 = 2."""
    r = selmer_2_data([0, -1, 1, -929, -10595])
    assert r['dim_sel_2'] == 2
    assert r['rank_lo'] == 0
    assert r['rank_hi'] == 0
    assert r['rank_proved'] is True
    assert r['sha2_lower'] == 2
    assert r['dim_E2'] == 0
    print("[571.b1] Sel_2=2 OK")


def test_with_2_torsion():
    """66.b1: rank 0, Sha=(Z/2)^2, 2-torsion Z/2 -> Sel_2 = 3."""
    r = selmer_2_data([1, 1, 1, -352, -2689])
    assert r['dim_sel_2'] == 3
    assert r['dim_E2'] == 1
    assert r['sha2_lower'] == 2
    print("[66.b1] Sel_2=3 OK")


def test_unproved_rank():
    """210.e1: ellrank gives r_lo=0, r_hi=2, and 2-torsion Z/2 -> Sel_2 = 3.
    PARI can't tighten further at effort=1; Sel_2 uses r_hi.
    """
    r = selmer_2_data([1, 0, 0, -1920800, -1024800150])
    assert r['dim_sel_2'] == 3
    assert r['dim_E2'] == 1
    print(f"[210.e1] Sel_2=3 (rank_lo={r['rank_lo']}, rank_hi={r['rank_hi']}) OK")


def test_data_dict_keys():
    r = selmer_2_data([0, -1, 1, -10, -20])
    for k in ['dim_sel_2', 'rank_lo', 'rank_hi', 'rank_proved', 'sha2_lower', 'dim_E2']:
        assert k in r, f"missing key {k}"
    print("[data dict shape] OK")


if __name__ == '__main__':
    test_trivial_sha()
    test_nontrivial_sha_2()
    test_with_2_torsion()
    test_unproved_rank()
    test_data_dict_keys()
    print("\nALL SELMER_RANK TESTS PASS")
