"""Test TOOL_REGULATOR against LMFDB.

LMFDB regulator values for reference:
  11a1  rank 0  reg = 1 (convention)
  37a1  rank 1  reg = 0.0511114082636977
  389a1 rank 2  reg = 0.152460121230418
  5077a1 rank 3 reg = 0.417143558758384
  11a2  rank 0  reg = 1 (convention)
  15a1  rank 0  reg = 1 (convention)
  14a1  rank 0  reg = 1 (convention)
  27a1  rank 0  reg = 1 (convention)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.regulator import regulator, mordell_weil, height


TOL = 1e-5


def test_rank_0():
    """Rank-0 curves — regulator = 1 by convention."""
    cases = [
        ('11a1', [0, -1, 1, -10, -20]),
        ('15a1', [1, 1, 1, -10, -10]),
        ('14a1', [1, 0, 1, 4, -6]),
        ('27a1', [0, 0, 1, 0, -7]),
    ]
    for label, ainvs in cases:
        r = regulator(ainvs)
        assert abs(r - 1.0) < TOL, f"{label}: got {r}"
    print(f"[rank 0] {len(cases)}/{len(cases)} OK")


def test_rank_1():
    """Rank-1 curves — regulators from LMFDB ec_curvedata."""
    cases = [
        ('37.a1',  [0, 0, 1, -1, 0], 0.051111408239968840),
        ('43.a1',  [0, 1, 1,  0, 0], 0.062816507087487649),
        ('53.a1',  [1, -1, 1, 0, 0], 0.092981484638654303),
        ('58.a1',  [1, -1, 0, -1, 1], 0.042420307839929850),
    ]
    for label, ainvs, expected in cases:
        r = regulator(ainvs)
        assert abs(r - expected) < TOL, f"{label}: got {r}, expected {expected}"
    print(f"[rank 1] {len(cases)}/{len(cases)} OK")


def test_rank_2():
    """Rank-2 curves — regulators from LMFDB ec_curvedata."""
    cases = [
        ('389.a1', [0, 1, 1, -2, 0], 0.152460177943143752),
        ('433.a1', [1, 0, 0,  0, 1], 0.224694163418166742),
    ]
    for label, ainvs, expected in cases:
        r = regulator(ainvs)
        assert abs(r - expected) < TOL, f"{label}: got {r}, expected {expected}"
    print(f"[rank 2] {len(cases)}/{len(cases)} OK")


def test_rank_3():
    """Smallest rank-3 curve."""
    r = regulator([0, 0, 1, -7, 6])  # 5077.a1
    expected = 0.417143558758383970
    assert abs(r - expected) < TOL, f"5077a1: got {r}, expected {expected}"
    print("[rank 3] 1/1 OK")


def test_mordell_weil():
    """Full MW data structure."""
    mw = mordell_weil([0, 0, 1, -1, 0])  # 37a1
    assert mw['rank_lower'] == 1
    assert mw['rank_upper'] == 1
    assert mw['rank_proved'] is True
    assert len(mw['generators']) == 1
    assert abs(mw['regulator'] - 0.0511114082636977) < TOL
    assert mw['torsion_order'] == 1

    # 14a1 has torsion Z/6Z
    mw = mordell_weil([1, 0, 1, 4, -6])
    assert mw['rank_lower'] == 0
    assert mw['torsion_order'] == 6
    print("[mordell_weil] 2/2 OK")


def test_height():
    """Neron-Tate height on specific points."""
    # (0,0) on 37a1 has height 0.051114...
    h = height([0, 0, 1, -1, 0], [0, 0])
    assert abs(h - 0.0511114082636977) < TOL, f"got {h}"
    # 3*(0,0) = (-1,-1) should have height 9 * 0.0511 = 0.46
    h3 = height([0, 0, 1, -1, 0], [-1, -1])
    assert abs(h3 - 9 * 0.0511114082636977) < TOL, f"got {h3}"
    print("[height] 2/2 OK")


def test_saturation_matters():
    """Saturation must run — otherwise (index)^2 bug.

    This test is a regression guard against forgetting to call ellsaturation.
    If PARI returned the 3*P basis for 37a1, the unsaturated regulator
    would be 9 * 0.0511 = 0.46.
    """
    r = regulator([0, 0, 1, -1, 0])
    assert abs(r - 0.0511114082636977) < TOL, \
        f"Saturation regression: got {r}, expected 0.0511 (if ~0.46, saturation failed)"
    print("[saturation regression] 1/1 OK")


if __name__ == '__main__':
    test_rank_0()
    test_rank_1()
    test_rank_2()
    test_rank_3()
    test_mordell_weil()
    test_height()
    test_saturation_matters()
    print("\nALL REGULATOR TESTS PASS")
