from prometheus.cosmos.locate import TOL, _summ


def test_location_verdicts():
    assert _summ([0.1, 0.12, 0.09])["verdict"] == "INDETERMINATE"          # < 4 bases
    assert _summ([0.2, 0.21, 0.19, 0.2])["verdict"] == "LOCATION_BIASED"
    assert _summ([0.01, -0.01, 0.02, -0.02])["verdict"] == "LOCATION_OK"
    assert _summ([0.3, -0.3, 0.3, -0.3])["verdict"] == "LOCATION_OK"          # biases that cancel look OK pooled
    assert TOL == 0.05
