"""D-R6-8: pairing, counts and decision rule on synthetic rows (C's committed values are the job's, after the predicate)."""
from primordial.cohorts.d import r6_8_ap01_paired_train_held as D


def rows(train_gain: float, held_gain: float):
    runs = {}
    for f in D.FAMILIES:
        for s in range(8):
            base = 1000.0 + 10 * s
            runs[("cell", f, s)] = {"family": f, "run_seed": s, "gens_done": 80,
                                    "train_per_landscape_top1": base, "held_per_landscape_top1": base}
            runs[("control", f, s)] = {"family": f, "run_seed": s, "gens_done": 400,
                                       "train_per_landscape_top1": base + train_gain, "held_per_landscape_top1": base + held_gain}
    return runs


def test_pairs_and_counts():
    pp = D.pairs(rows(5.0, -5.0))
    assert len(pp) == 32 and all(x["run_seed"] == c["run_seed"] and x["family"] == c["family"] for x, c in pp)
    assert D.counts(pp) == (32, 0)


def test_decide():
    assert D.decide(True, True, 30, 10) == "TRAIN_NOT_HELD"
    assert D.decide(True, True, 30, 30) == "BOTH_GAIN"
    assert D.decide(True, True, 10, 30) == "NO_TRAIN_GAIN"
    assert D.decide(True, True, 20, 20) == "MIXED"
    assert D.decide(False, True, 30, 10) == "INDETERMINATE"
    assert D.decide(True, False, 30, 10) == "INDETERMINATE"


def test_self_pair_is_zero():
    pp = D.pairs(rows(5.0, 5.0))
    assert D.counts([(c, c) for _, c in pp]) == (0, 0)


def test_committed_rows_have_32_pairs():
    runs, ref, summ = D.load((D.ROOT / D.SRC_ROWS).read_text(encoding="utf-8"))
    assert len(D.pairs(runs)) == 32 and "random_bits_mean_per_held_landscape" in ref and "held_median_cell" in summ
