"""D-R7-11: the AP-03 charge arithmetic and the reuse of D-R7-6's instrument (the committed-row read is the job's)."""
from primordial.cohorts.d import r7_11_ap03_pressure_binding as D
from primordial.fabric import rows as R


def row(arm, fam, rs, functional_bytes=14, nonnop=3, net_train=28000.0, beta=58.0):
    return {"kind": "run", "arm": arm, "family": fam, "run_seed": rs, "beta": beta,
            "top1_functional_bytes": functional_bytes, "top1_nonnop": nonnop,
            "train_fit_top1": net_train, "held_charge_per_episode": 31.71875,
            "held_unaffordable_per_episode": 0.0, "oracles": {"ok": True}}


def runs(cell_fb=14, control_fb=22):
    out = {}
    for f in D.FAMILIES:
        for rs in range(8):
            out[("cell", f, rs)] = row("cell", f, rs, cell_fb, 3)
            out[("control", f, rs)] = row("control", f, rs, control_fb, 7)
    return out


def test_charge_share_grosses_up_the_net_selection_fitness():
    """C's train_fit_top1 is NET of the charge, so earned = net + beta * bytes."""
    r = row("cell", 4200, 0, functional_bytes=14, net_train=28000.0, beta=58.0)
    paid = 58.0 * 14
    assert abs(D.charge_share(r, 58.0) - paid / (28000.0 + paid)) < 1e-12
    assert D.charge_share(r, 0.0) == 0.0                      # the control pays nothing by definition


def test_counts_use_functional_bytes():
    pp = D.B6.pairs_of(runs(cell_fb=14, control_fb=22))
    assert len(pp) == 32
    assert D.counts(pp) == (32, 0)                            # cell winner smaller in every pair
    assert D.counts(D.B6.pairs_of(runs(cell_fb=22, control_fb=22))) == (0, 32)


def test_reuses_d_r7_6s_rule_unchanged():
    """The instrument must be identical to AP-02's, or the two cells are not comparable."""
    assert D.B6.decide(True, True, 0.001, 0, 32) == "PRESSURE_DID_NOT_BIND"
    assert D.B6.decide(True, True, 0.10, 32, 0) == "PRESSURE_BOUND"
    assert D.B6.decide(True, True, 0.03, 30, 0) == "MIXED"
    assert D.B6.decide(False, True, 0.10, 32, 0) == "INDETERMINATE"
    assert D.B6.AGREE_PAIRS == 24 and D.B6.FREE_SHARE == 0.01 and D.B6.BOUND_SHARE == 0.05


def test_source_is_the_ap03_rows_and_families_match():
    assert D.SRC_ROWS.endswith("C-R7-AP-03-small-program-d1-bytecharge-falkordb-metered.jsonl")
    assert D.FAMILIES == D.B6.FAMILIES


def test_cross_cell_table_carries_the_two_prior_cells():
    t = D.CROSS_CELL
    assert t["C-R6-AP-01"]["mechanism"] == "SATURATED"
    assert t["C-R7-AP-02"]["decision"] == "MIXED" and t["C-R7-AP-02"]["median_charge_share"] == 0.0365
    assert t["C-R7-AP-03"]["measured_here"] is True


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
