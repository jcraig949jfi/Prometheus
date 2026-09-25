"""D-R7-7: D-R6-8's paired rule pointed at AP-02 (the committed-row read is the job's)."""
from primordial.cohorts.d import r7_7_ap02_train_vs_held as D
from primordial.fabric import rows as R


def pair(train_c, held_c, train_k, held_k, fam=4200):
    cell = {"family": fam, "train_nk_per_landscape_top1": train_c, "held_per_landscape_top1": held_c}
    ctrl = {"family": fam, "train_nk_per_landscape_top1": train_k, "held_per_landscape_top1": held_k}
    return cell, ctrl


def pairs(n_train_worse, n_held_worse, n=32):
    out = []
    for i in range(n):
        tc, tk = (1.0, 2.0) if i < n_train_worse else (2.0, 1.0)      # control train > cell train for the first n
        hc, hk = (1.0, 2.0) if i < n_held_worse else (2.0, 1.0)
        out.append(pair(tc, hc, tk, hk))
    return out


def test_counts_are_control_greater_than_cell():
    assert D.counts(pairs(32, 0)) == (32, 0)
    assert D.counts(pairs(0, 32)) == (0, 32)


def test_train_not_held():
    assert D.decide(True, True, *D.counts(pairs(32, 16))) == "TRAIN_NOT_HELD"
    assert D.decide(True, True, 26, 16) == "TRAIN_NOT_HELD"           # both boundaries inclusive


def test_both_lose_and_no_train_cost():
    assert D.decide(True, True, *D.counts(pairs(32, 32))) == "BOTH_LOSE"
    assert D.decide(True, True, 26, 26) == "BOTH_LOSE"
    assert D.decide(True, True, *D.counts(pairs(10, 0))) == "NO_TRAIN_COST"
    assert D.decide(True, True, 16, 0) == "NO_TRAIN_COST"


def test_mixed_matches_the_round6_reading():
    """C-R6-AP-01 read t = 32, h = 17 under this same rule: one pair short of TRAIN_NOT_HELD."""
    assert D.decide(True, True, 32, 17) == "MIXED"
    assert D.decide(True, True, 20, 5) == "MIXED"                     # train count between the thresholds


def test_indeterminate():
    assert D.decide(False, True, 32, 16) == "INDETERMINATE"
    assert D.decide(True, False, 32, 16) == "INDETERMINATE"


def test_self_pair_control_is_zero_zero():
    _, ctrl = pair(1.0, 1.0, 2.0, 2.0)
    assert D.counts([(ctrl, ctrl)]) == (0, 0)


def test_reuses_the_ap02_source_and_loader():
    assert D.SRC_ROWS.endswith("C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl")
    assert D.B6.pairs_of is not None and D.FAMILIES == D.B6.FAMILIES


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
