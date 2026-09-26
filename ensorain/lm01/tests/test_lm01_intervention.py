from ensorain.lm01.intervention import positive_control


def test_intervention_positive_and_negative_controls():
    o = positive_control(seeds=range(9_350_000, 9_350_002))
    assert o["median_gap"] > 0.5 and o["median_neg_gap"] < 0.2
