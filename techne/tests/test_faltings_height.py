"""Test TOOL_FALTINGS_HEIGHT against LMFDB ec_curvedata.faltings_height."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.faltings_height import faltings_height, faltings_data


TOL = 1e-8


def test_lmfdb_values():
    """LMFDB-stored Faltings heights, multiple ranks."""
    cases = [
        ('37.a1',   [0, 0, 1, -1, 0],       -0.99654220763736714794656344357),
        ('389.a1',  [0, 1, 1, -2, 0],       -0.79564165429425290828872937437),
        ('5077.a1', [0, 0, 1, -7, 6],       -0.56139014229398666466212500182),
        ('66.b1',   [1, 1, 1, -352, -2689], -0.094953900850670871486256809047),
    ]
    for label, ainv, expected in cases:
        got = faltings_height(ainv)
        assert abs(got - expected) < TOL, f"{label}: got {got}, expected {expected}"
    print(f"[LMFDB values] {len(cases)}/{len(cases)} OK")


def test_data_dict_shape():
    r = faltings_data([0, 0, 1, -1, 0])
    assert 'h_F' in r
    assert 'omega_1' in r
    assert 'tau' in r
    assert 'minimal_ainvs' in r
    assert 'is_minimal' in r
    assert r['tau'].imag > 0
    assert abs(r['h_F'] - (-0.99654220763736714794656344357)) < TOL
    print("[data dict] OK")


def test_non_minimal_input():
    """Non-minimal input should be reduced; same h_F as minimal."""
    # [0, 0, 64, -64, 0] — not minimal
    min_ainvs = faltings_data([0, 0, 64, -64, 0])['minimal_ainvs']
    # Should match whatever the minimal model is
    h_nonmin = faltings_height([0, 0, 64, -64, 0])
    h_min = faltings_height(min_ainvs)
    assert abs(h_nonmin - h_min) < TOL, f"non-min vs min: {h_nonmin} vs {h_min}"
    print(f"[non-minimal input] reduced to {min_ainvs}, h_F matches OK")


if __name__ == '__main__':
    test_lmfdb_values()
    test_data_dict_shape()
    test_non_minimal_input()
    print("\nALL FALTINGS_HEIGHT TESTS PASS")
