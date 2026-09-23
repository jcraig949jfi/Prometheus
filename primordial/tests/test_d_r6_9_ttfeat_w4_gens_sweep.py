"""D-R6-9: decision rule on synthetic checkpoint tables (the sweep itself is the job's, after the predicate)."""
from primordial.cohorts.d import r6_9_ttfeat_w4_gens_sweep as D


def runs(train14, train50, train200, held14, held50, held200):
    return [{"run_seed": rs, "checkpoints": {"14": {"train": train14, "held64": held14},
                                             "50": {"train": train50, "held64": held50},
                                             "200": {"train": train200, "held64": held200}}} for rs in range(8)]


def test_held_keeps_rising():
    got, st = D.decide(True, runs(92.0, 98.0, 100.0, 60.0, 70.0, 80.0))
    assert got == "HELD_KEEPS_RISING" and st["held_up_50_to_200"] == 8 and st["d"] > 0.05


def test_tracks():
    assert D.decide(True, runs(90.0, 95.0, 100.0, 72.0, 76.0, 80.0))[0] == "TRACKS"


def test_train_keeps_rising():
    assert D.decide(True, runs(60.0, 80.0, 100.0, 78.0, 79.0, 80.0))[0] == "TRAIN_KEEPS_RISING"


def test_mixed_when_held_gain_is_early_only():
    assert D.decide(True, runs(92.0, 98.0, 100.0, 60.0, 81.0, 80.0))[0] == "MIXED"


def test_indeterminate():
    assert D.decide(False, runs(92.0, 98.0, 100.0, 60.0, 70.0, 80.0))[0] == "INDETERMINATE"
    assert D.decide(True, runs(92.0, 98.0, 100.0, 60.0, 70.0, 80.0)[:7])[0] == "INDETERMINATE"
