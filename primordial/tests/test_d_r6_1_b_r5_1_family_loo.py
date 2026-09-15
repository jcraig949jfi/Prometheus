"""D-R6-1: leave-one-family-out read of B-R5-1 (synthetic pools; the real LOO numbers are the job's, after the predicate)."""
import numpy as np

from primordial.cohorts.d import r6_1_b_r5_1_family_loo as D
from primordial.metric.ci import median_ci

FLOOR, BASE = 100.0, 120.0
DEN = BASE - FLOOR


def runs(value_of):
    return [{"rng_family": f, "run_seed": rs, "held64_per_seed": float(value_of(f, rs))} for f in D.ORDER for rs in range(8)]


def stub_judge(med, held, s):
    if s["runs_total"] < 32 or s["rng_family_count"] < 4:
        return {"verdict": "INELIGIBLE", "why": "CANDIDATE_N"}
    lo, hi = median_ci(held)
    return {"verdict": "PASS", "progress": (med - FLOOR) / DEN, "progress_ci95": [(lo - FLOOR) / DEN, (hi - FLOOR) / DEN]}


def ref_of(cand):
    held = D.held_of(cand)
    lo, hi = median_ci(held)
    return {"progress": (float(np.median(held)) - FLOOR) / DEN, "progress_ci95": ((lo - FLOOR) / DEN, (hi - FLOOR) / DEN)}


BASE_RUNS = runs(lambda f, rs: BASE + (rs - 3.5) * 0.1)


def test_robust_when_every_family_is_well_above():
    cand = runs(lambda f, rs: 150.0 + rs)
    out = D.analyse(cand, BASE_RUNS, FLOOR, DEN, stub_judge, ref=ref_of(cand))
    assert out["checks"]["I1_full_pool_reproduces_B_receipt_via_check_r4"]
    assert out["checks"]["controls_ok"]
    assert out["loo_ci_low_gt_095_k_of_4"] == 4 and out["decision"] == "ROBUST"
    assert all(v["judge"]["verdict"] == "INELIGIBLE" for v in out["leave_one_family_out"].values())
    assert all(v["runs_total"] == 24 and v["rng_family_count"] == 3 for v in out["leave_one_family_out"].values())


def test_not_robust_when_one_family_carries_the_pool():
    cand = runs(lambda f, rs: 200.0 + rs if f == D.ORDER[0] else FLOOR + 5.0 + rs)
    out = D.analyse(cand, BASE_RUNS, FLOOR, DEN, stub_judge, ref=ref_of(cand))
    assert out["checks"]["I1_full_pool_reproduces_B_receipt_via_check_r4"]
    assert not out["leave_one_family_out"][str(D.ORDER[0])]["ci_low_gt_robust_at"]
    assert out["decision"] == "NOT_ROBUST"


def test_indeterminate_when_the_full_pool_does_not_reproduce_the_receipt():
    cand = runs(lambda f, rs: 150.0 + rs)
    out = D.analyse(cand, BASE_RUNS, FLOOR, DEN, stub_judge, ref={"progress": 9.9, "progress_ci95": (9.0, 9.9)})
    assert out["decision"] == "INDETERMINATE"


def test_below_floor_counts_and_order():
    cand = runs(lambda f, rs: FLOOR - 1.0 if (f == 3303 and rs in (2, 6, 7)) else 150.0)
    out = D.analyse(cand, BASE_RUNS, FLOOR, DEN, stub_judge, ref=ref_of(cand))
    assert out["reported_not_judged"]["runs_below_floor_by_family"] == {"4200": 0, "2101": 0, "3303": 3, "5501": 0}
    assert out["full"]["runs_below_floor"] == 3


def test_load_runs_reads_committed_b_r5_1_in_plan_order():
    text = (D.ROOT / D.CAND_ROWS).read_text(encoding="utf-8")
    got = D.load_runs(text)
    assert len(got) == 32
    assert [(x["rng_family"], x["run_seed"]) for x in got] == [(f, rs) for f in D.ORDER for rs in range(8)]
