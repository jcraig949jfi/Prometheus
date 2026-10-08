from prometheus.cosmos.c4 import labels as L


def test_a15_ananke_stormy_example_is_marginal():
    assert L.three_way("FUNCTIONAL", 0.262, 4) == "MARGINAL"      # J .262 vs chance .25 (R-STAT A15)
    assert L.three_way("FUNCTIONAL", 0.40, 4) == "USABLE"
    assert L.three_way("PASSIVE", 0.9, 4) == "NOT"
    assert L.three_way("INDETERMINATE", 0.9, 4) == "INDETERMINATE"


def test_a14_single_class_family_excluded_and_counted():
    fams = ["a"] * 30 + ["b"] * 30
    y = [1] * 30 + [0] * 15 + [1] * 15
    r = L.informative_families(fams, y)
    assert r["informative"] == ["b"] and r["excluded"] == ["a"] and not r["reached"]
