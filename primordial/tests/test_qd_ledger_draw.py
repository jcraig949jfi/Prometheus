"""Round 2 QD ledger (clause A check, Pareto, round 1 seed) and anti-prior cell draw."""
from __future__ import annotations

import itertools

from primordial.ops import draw_cell as DC
from primordial.ops import qd_ledger as Q


def cell(world="w4", pressure="p", rep="linear"):
    return {"representation": rep, "world": world, "pressure": pressure, "substrate": "numba_fused", "channel": "none"}


def row(median, nbytes, iqr=6.0, baseline=True, rep="linear", status="record"):
    return {"cell": cell(rep=rep), "mechanism": rep, "fitness": {"held64_median": median, "iqr": iqr, "n_runs": 8},
            "footprint": {"genome_bytes": nbytes}, "baseline": baseline, "status": status, "source": {"exp_id": "t"}}


def test_clause_a_pass_fail_ineligible():
    rows = [row(90.0, 312), row(80.0, 4000, rep="tt_feat")]
    assert Q.check(rows, "w4", "p", 88.0, 5, 200, 8)["verdict"] == "PASS"          # parity at fewer bytes
    assert Q.check(rows, "w4", "p", 94.0, 5, 312, 8)["verdict"] == "PASS"          # better at equal bytes
    assert Q.check(rows, "w4", "p", 80.0, 5, 200, 8)["verdict"] == "FAIL"          # below parity band
    assert Q.check(rows, "w4", "p", 91.0, 5, 400, 8)["verdict"] == "FAIL"          # more bytes, inside band
    assert Q.check(rows, "w4", "p", 99.0, 5, 10, 4)["verdict"] == "INELIGIBLE"     # < 8 run seeds
    assert Q.check(rows, "w4", "p", 99.0, 5, 10, 8, oracle_clean=False)["verdict"] == "INELIGIBLE"
    assert Q.check(rows, "w1", "p", 99.0, 5, 10, 8)["verdict"] == "NO_BASELINE"


def test_pareto_drops_dominated_and_non_record_rows():
    rows = [row(90.0, 312), row(80.0, 4000, rep="tt_feat"), row(95.0, 5000, rep="tt_digits"),
            row(99.0, 100, rep="cheat", status="cheat")]
    assert [r["mechanism"] for r in Q.pareto(rows, "w4")] == ["linear", "tt_digits"]


def test_round1_seed_reads_receipts_and_computes_bytes():
    rows = Q.seed_rows()
    assert rows and all(r["baseline"] and r["footprint"]["genome_bytes"] > 0 for r in rows)
    w4_linear = [r for r in rows if r["cell"] == cell(pressure="train8_held64") and r["mechanism"].startswith("closed_loop_linear")]
    assert w4_linear[0]["fitness"]["held64_median"] == 89.94 and w4_linear[0]["fitness"]["n_runs"] == 8
    from primordial.qd import e7_run as E7
    assert w4_linear[0]["footprint"]["genome_bytes"] == E7.G7(4, "linear").glen


def test_draw_is_reproducible_and_on_grid(monkeypatch):
    monkeypatch.setattr(DC, "visits", lambda: {})
    a, b = DC.draw(seed=7), DC.draw(seed=7)
    assert a["cell"] == b["cell"]
    assert all(a["cell"][k] in DC.AXES[k] for k in DC.AXES)
    assert a["grid_cells"] == 13 * 8 * 8 * 6 * 2


def test_draw_prefers_unvisited_cells(monkeypatch):
    allk = list(itertools.product(*DC.AXES.values()))
    free = allk[1234]
    monkeypatch.setattr(DC, "visits", lambda: {k: 10**9 for k in allk if k != free})
    got = [DC._key(DC.draw(seed=s)["cell"]) for s in range(20)]
    assert got.count(free) >= 19
