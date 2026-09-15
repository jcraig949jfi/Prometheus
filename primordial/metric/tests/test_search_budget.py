"""G-R6-1: search-budget accounting from committed rows; the O2 comparator rule."""
from __future__ import annotations

import pytest

from primordial.metric import search_budget as SB


def test_fields_are_explicit_and_consistent():
    f = SB.fields(800, 128, "train128_held64", cpu_s=10.0, wall_s=2.0)
    assert f == {"search_generations": 800, "search_batch": 128, "search_evals": 102400,
                 "search_train_episodes": 102400 * 128, "search_cpu_s": 10.0, "search_wall_s": 2.0}
    assert SB.fields(200, 128, "train8_held64")["search_train_episodes"] == 25600 * 8


def test_b_r5_1_and_w13_baseline_from_committed_rows():
    c, b = SB.candidate_b_r5_1(), SB.baseline_w13()
    assert (c["runs_total"], c["rng_family_count"], c["runs_per_family"]) == (32, 4, 8)
    assert (b["runs_total"], b["rng_family_count"], b["runs_per_family"]) == (32, 4, 8)
    assert c["search_evals_per_run"] == 102400 and b["search_evals_per_run"] == 102400
    assert c["search_evals_total"] == b["search_evals_total"] == 32 * 102400
    assert c["search_cpu_s_total"] is None and "not in rows" in c["search_cpu_s_basis"]
    assert b["search_cpu_s_basis"].startswith("ESTIMATED") and b["search_cpu_s_total"] > 0


def test_equal_evals_per_run_do_not_fire_the_comparator_and_both_readings_are_reported():
    a = SB.accounting()
    assert a["ratio_evals_per_run"] == 1.0 and a["comparator_fires"] is False
    assert set(a["interpretations"]) == {"clause_a_as_worded", "equal_budget"}


def _acc(evals, total=None):
    return {"search_evals_per_run": evals, "search_evals_total": total or evals * 32,
            "search_train_episodes_total": (total or evals * 32) * 128}


def test_the_rule_fires_only_when_the_candidate_searched_more_per_run():
    assert SB.accounting(_acc(102401), _acc(102400))["comparator_fires"] is True
    assert SB.accounting(_acc(102400), _acc(102400))["comparator_fires"] is False
    assert SB.accounting(_acc(51200), _acc(102400))["comparator_fires"] is False
    with pytest.raises(ValueError):
        SB.accounting({**_acc(1), "search_evals_per_run": [1, 2]}, _acc(1))


def test_r16_run_rows_carry_measured_search_fields(tmp_path):
    """G-R6-1: new R16 baseline and learner run rows stamp the search budget (evals = generations x batch, CPU measured)."""
    redis = pytest.importorskip("redis")
    from primordial.metric import baseline as B
    from primordial.metric import invariant as I
    from primordial.tests._live import live_url
    r = redis.Redis.from_url(live_url())
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    try:
        b = B.baseline_run(r, 4, "train8_held64", 0, gens=3, batch=8, elites_dir=tmp_path / "b", rng_family=4200)
        l = I.learner_run(r, 4, "train8_held64", 0, gens=3, batch=8, elites_dir=tmp_path / "l", rng_family=2101)
    finally:
        for k in r.scan_iter("pm:qd:g-r16-*", count=5000):
            r.delete(k)
    for row in (b, l):
        assert (row["search_generations"], row["search_batch"], row["search_evals"]) == (3, 8, 24)
        assert row["search_train_episodes"] == 24 * 8 and row["search_cpu_s"] > 0 and row["search_wall_s"] > 0
    v1 = B.baseline_run(r, 4, "train8_held64", 0, gens=2, batch=8, elites_dir=tmp_path / "v1")
    for k in r.scan_iter("pm:qd:g-r4-base-*", count=5000):
        r.delete(k)
    assert "search_evals" not in v1                                        # v1 rows reproduce unchanged
