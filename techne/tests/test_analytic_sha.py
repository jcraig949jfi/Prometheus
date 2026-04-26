"""Test TOOL_ANALYTIC_SHA against LMFDB ec_mwbsd.sha_an."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.analytic_sha import analytic_sha, sha_an_rounded


TOL = 0.01


def test_sha_one():
    """Curves with Sha = 1, across rank 0/1/2/3."""
    cases = [
        ('11.a1',   [0, -1, 1, -10, -20]),
        ('37.a1',   [0, 0, 1, -1, 0]),
        ('389.a1',  [0, 1, 1, -2, 0]),
        ('5077.a1', [0, 0, 1, -7, 6]),
    ]
    for label, ainv in cases:
        r = analytic_sha(ainv)
        assert abs(r['value'] - 1) < TOL, f"{label}: got {r['value']}"
        assert r['rounded'] == 1
    print(f"[sha=1 rank 0-3] {len(cases)}/{len(cases)} OK")


def test_sha_4():
    """Curves with Sha = 4."""
    cases = [
        ('66.b1',  [1, 1, 1, -352, -2689]),
        ('102.c1', [1, 0, 0, -27744, -1781010]),
    ]
    for label, ainv in cases:
        r = analytic_sha(ainv)
        assert abs(r['value'] - 4) < TOL, f"{label}: got {r['value']}"
        assert r['rounded'] == 4
    print(f"[sha=4] {len(cases)}/{len(cases)} OK")


def test_sha_9():
    """182.d1 has Sha = 9."""
    r = analytic_sha([1, 0, 0, -15663, -755809])
    assert abs(r['value'] - 9) < TOL
    assert r['rounded'] == 9
    print("[sha=9 182.d1] OK")


def test_sha_16():
    """210.e1 has Sha = 16."""
    r = analytic_sha([1, 0, 0, -1920800, -1024800150])
    assert abs(r['value'] - 16) < TOL
    assert r['rounded'] == 16
    print("[sha=16 210.e1] OK")


def test_metadata_shape():
    """Returned dict has all expected keys."""
    r = analytic_sha([0, -1, 1, -10, -20])
    for k in ['value', 'rounded', 'rank', 'L_r_over_fact', 'Omega', 'Reg', 'tam', 'tors', 'disc_sign']:
        assert k in r, f"missing key: {k}"
    assert r['rank'] == 0
    assert r['tors'] == 5  # 11.a1 has torsion Z/5
    assert r['tam'] == 5
    print("[metadata] OK")


def test_shortcut():
    assert sha_an_rounded([1, 0, 0, -15663, -755809]) == 9
    print("[shortcut sha_an_rounded] OK")


if __name__ == '__main__':
    test_sha_one()
    test_sha_4()
    test_sha_9()
    test_sha_16()
    test_metadata_shape()
    test_shortcut()
    print("\nALL ANALYTIC_SHA TESTS PASS")
