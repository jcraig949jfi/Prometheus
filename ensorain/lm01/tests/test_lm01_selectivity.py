from ensorain.lm01.selectivity import calibrate_relative, load_threshold


def test_threshold_is_derived_and_committed():
    t = load_threshold()
    assert t is not None and 0 < t < 0.05


def test_relative_reading_passes_known_answer_trio():          # method rule (#652/#653)
    for n in (400, 800, 1500):
        o = calibrate_relative(n=n)
        assert o["PASS"], (n, {k: v["verdict"] for k, v in o.items() if isinstance(v, dict)})
