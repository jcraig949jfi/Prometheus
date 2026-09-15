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


def test_check_is_stable_after_the_candidate_is_appended():
    # lane B ask 2026-09-14: a front over ALL rows let an appended dominating candidate evict its
    # baseline, so the same candidate PASSed before the append and failed after it
    rows = [row(90.0, 312), row(80.0, 4000, rep="tt_feat")]
    before = Q.check(rows, "w4", "p", 98.2, 2.8, 48, 8)
    rows.append(row(98.2, 48, iqr=2.8, baseline=False, rep="int4_linear"))
    after = Q.check(rows, "w4", "p", 98.2, 2.8, 48, 8)
    assert before["verdict"] == after["verdict"] == "PASS" and before == after


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


def screen_doc():
    """A planted worlds_r4 doc: w7 SURVIVED (train8), w8 CULLED, w9 HELD under the active gate_in|HOLD."""
    from primordial.metric import worlds as WR
    from primordial.tests.test_qd_ledger_r4 import base, suite
    s8 = "train8_held64"
    return WR.build([WR.cell(suite(7, s8, (100.0, 100.0, 5.0, 60.0), 90.0), base(7, s8, 200.0, 150.0, 250.0)),
                     WR.cell(suite(8, s8, (100.0, 100.0, 5.0, 60.0), 90.0), base(8, s8, 95.0, 80.0, 99.0)),
                     WR.cell(suite(9, s8, (100.0, 100.0, 5.0, 60.0), 170.0), base(9, s8, 140.0, 120.0, 160.0))],
                    commit="t")


def test_draw_is_reproducible_and_on_grid(monkeypatch):
    monkeypatch.setattr(DC, "visits", lambda: {})
    doc = screen_doc()
    a, b = DC.draw(seed=7, doc=doc), DC.draw(seed=7, doc=doc)
    ax = DC.axes(doc)
    assert a["cell"] == b["cell"]
    assert all(a["cell"][k] in ax[k] for k in ax)
    assert ax["world"] == ["w7"] + DC.NON_GRAPHWORLD
    assert a["grid_cells"] == 13 * (1 + len(DC.NON_GRAPHWORLD)) * 8 * 6 * 2


def test_draw_prefers_unvisited_cells(monkeypatch):
    doc = screen_doc()
    allk = list(itertools.product(*DC.axes(doc).values()))
    free = allk[1234]
    monkeypatch.setattr(DC, "visits", lambda: {k: 10**9 for k in allk if k != free})
    got = [DC._key(DC.draw(seed=s, doc=doc)["cell"]) for s in range(20)]
    assert got.count(free) >= 19


def test_draw_takes_graphworld_worlds_only_from_survivors(monkeypatch):
    monkeypatch.setattr(DC, "visits", lambda: {})
    drawn = {DC.draw(seed=s, doc=screen_doc())["cell"]["world"] for s in range(400)}
    assert "w7" in drawn and not drawn & {"w1", "w2", "w3", "w4", "w5", "w8", "w9"}
    none = {DC.draw(seed=s, doc=None)["cell"]["world"] for s in range(200)}      # no screen file: no graphworld
    assert none <= set(DC.NON_GRAPHWORLD)


def test_graphworld_b2_is_not_drawable_in_round_4():
    # C-R4-02/03: B2 has no obs/action/charge interface, so every draw on it aborted
    from primordial.ops import draw_cell as DC
    assert "graphworld_b2" not in DC.NON_GRAPHWORLD
    assert "graphworld_b2" not in DC.axes(None)["world"]
