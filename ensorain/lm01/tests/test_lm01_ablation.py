import copy

from ensorain.lm01.ablation import positive_control, planted_scrambled, OracleKeyHybrid, _feed


def test_R1e_positive_control_collapses():                  # B5: the ablation has teeth
    assert positive_control(seeds=range(9_340_000, 9_340_002))["median_gap"] > 0.5


def test_ablation_keeps_exact_store():
    w = planted_scrambled(9_340_000, n=600)
    a = _feed(OracleKeyHybrid(w["dims"], w["U"], w["V"], w["s"]), w["segs"])
    b = copy.deepcopy(a)
    b.ablate_index(0)
    assert b.store.digest() == a.store.digest()
