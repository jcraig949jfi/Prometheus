"""D-R7-6: the binding rule, charge_share arithmetic and the paired counts (the committed-row read is the job's)."""
from primordial.cohorts.d import r7_6_ap02_pressure_binding as D
from primordial.fabric import rows as R


def row(arm, fam, rs, functional_bytes=6, train_nk=2_000_000.0, beta=169144.0):
    return {"kind": "run", "arm": arm, "family": fam, "run_seed": rs, "beta": beta,
            "top1_program": {"functional_bytes": functional_bytes, "code_len": 4, "d": 2, "cb": 0},
            "train_nk_per_landscape_top1": train_nk, "held_per_landscape_top1": 2_100_000.0,
            "held_delivered_share_top1": 1.0, "held_minus_random": 1000.0, "gens_done": 50,
            "oracles": {"ok": True}}


def runs(cell_fb=6, control_fb=6):
    out = {}
    for f in D.FAMILIES:
        for rs in range(8):
            out[("cell", f, rs)] = row("cell", f, rs, cell_fb)
            out[("control", f, rs)] = row("control", f, rs, control_fb)
    return out


def test_pairs_and_counts():
    pp = D.pairs_of(runs(cell_fb=5, control_fb=6))
    assert len(pp) == 32
    small, same = D.counts(pp)
    assert (small, same) == (32, 0)
    small, same = D.counts(D.pairs_of(runs()))
    assert (small, same) == (0, 32)


def test_charge_share_is_beta_times_bytes_over_earned():
    r = row("cell", 4200, 0, functional_bytes=6, train_nk=2_000_000.0, beta=169144.0)
    assert abs(D.charge_share(r) - (169144.0 * 6) / (2_000_000.0 * D.N_TRAIN)) < 1e-12
    assert abs(D.charge_share(r) - 0.063429) < 1e-6              # 6.3% of what the winner earned: material
    assert D.charge_share(r) > D.BOUND_SHARE
    cheap = row("cell", 4200, 0, functional_bytes=2, train_nk=20_000_000.0, beta=169144.0)
    assert D.charge_share(cheap) < D.FREE_SHARE                  # 0.21%: a winner paying almost nothing


def test_decisions_and_thresholds():
    assert D.decide(True, True, 0.001, 0, 32) == "PRESSURE_DID_NOT_BIND"
    assert D.decide(True, True, 0.01, 0, 24) == "PRESSURE_DID_NOT_BIND"     # boundary is inclusive
    assert D.decide(True, True, 0.10, 32, 0) == "PRESSURE_BOUND"
    assert D.decide(True, True, 0.05, 24, 0) == "PRESSURE_BOUND"            # boundary is inclusive
    assert D.decide(True, True, 0.001, 0, 23) == "MIXED"                    # pays nothing but winners differ
    assert D.decide(True, True, 0.10, 23, 0) == "MIXED"                     # material charge, few winners shrank
    assert D.decide(True, True, 0.03, 30, 0) == "MIXED"                     # between the thresholds
    assert D.decide(False, True, 0.001, 0, 32) == "INDETERMINATE"
    assert D.decide(True, False, 0.001, 0, 32) == "INDETERMINATE"


def test_planted_controls_are_what_the_job_asserts():
    """The job's two planted controls must read the two decisive labels, or every run is INDETERMINATE."""
    assert D.decide(True, True, 0.10, D.AGREE_PAIRS, 0) == "PRESSURE_BOUND"
    assert D.decide(True, True, 0.001, 0, D.AGREE_PAIRS) == "PRESSURE_DID_NOT_BIND"


def test_source_rows_path_points_at_C_AP02():
    assert D.SRC_ROWS.endswith("C-R7-AP-02-codebook-nk-bytecharge-falkordb-metered.jsonl")
    assert "rows/C/" in D.SRC_ROWS


def test_emitted_status_is_writable_by_the_rowwriter():
    import inspect
    assert inspect.signature(D.job).parameters["status"].default in R.STATUSES
