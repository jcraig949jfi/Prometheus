"""ARACHNE-03/06/07/08 instrumentation: loud adapter failure, the
productivity signal, the freshness record, and the intervention ledger.
Negative, positive and cheat controls per base s2. No database, no
landscape, no crawl: everything here runs on fakes and a temp dir."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from agents.arachne.landscapes import probe                     # noqa: E402
from agents.arachne.productivity import tick_productivity, freshness_record   # noqa: E402
from agents.arachne.fabric import Fabric, Edge                  # noqa: E402


# ---- ARACHNE-03: adapters fail loudly -------------------------------------
class _Dead:
    name = "dead"
    def available(self):
        return False
    def unavailable_reason(self):
        return "table missing: topology.knots"


class _Raises:
    name = "raises"
    def available(self):
        raise RuntimeError("connection refused")


class _Alive:
    name = "alive"
    def available(self):
        return True


def test_probe_negative_dead_adapter_names_its_reason():
    inst, ok, reason = probe(_Dead)
    assert ok is False and "topology.knots" in reason


def test_probe_negative_raising_adapter_is_not_swallowed():
    inst, ok, reason = probe(_Raises)
    assert ok is False and "connection refused" in reason


def test_probe_positive_live_adapter():
    inst, ok, reason = probe(_Alive)
    assert ok is True and reason == "ok"


def test_probe_cheat_an_adapter_that_lies_available_is_reported_available():
    """The probe measures the adapter's claim, not the data: an adapter that
    says available() -> True with no data will pass here. That is why the
    census (ARACHNE-02) also counts rows: this test documents the limit."""
    class Liar:
        name = "liar"
        def available(self):
            return True
    _, ok, _ = probe(Liar)
    assert ok is True


# ---- ARACHNE-07: productivity ---------------------------------------------
def _e(src, dst, op, null_p, ls="x"):
    return Edge(src=src, dst=dst, op=op, landscape=ls, crawler="c", born_at="t", null_p=null_p)


def test_productivity_negative_empty_tick_is_an_explicit_no_op():
    p = tick_productivity([], [], {})
    assert p["new_edges"] == 0 and p["new_nodes"] == 0
    assert p["no_op_reason"]


def test_productivity_positive_counts_and_discounts():
    edges = [_e("a:1", "a:2", "same_x", 0.9), _e("a:2", "b:3", "computes", 0.1)]
    p = tick_productivity(edges, ["a:1", "a:2", "b:3"], {"deaths": 1})
    assert p["new_edges"] == 2 and p["new_nodes"] == 3
    assert p["cross_landscape_new_edges"] == 1
    # a:1 introduced only by a 0.9 edge -> 0.1; a:2 by min(0.9,0.1) -> 0.9; b:3 -> 0.9
    assert p["null_discounted_new_nodes"] == pytest.approx(1.9, abs=1e-6)
    assert p["deaths"] == 1 and p["no_op_reason"] is None


def test_productivity_cheat_injected_new_node_is_observed():
    """Success deliberately injected: a single low-null edge to a fresh node
    must move the discounted count by ~1, proving the channel can see it."""
    base = tick_productivity([], [], {})["null_discounted_new_nodes"]
    p = tick_productivity([_e("a:1", "a:9", "computes", 0.0)], ["a:9"], {})
    assert p["null_discounted_new_nodes"] - base == pytest.approx(1.0)


def test_fabric_drain_recent_reports_exactly_the_persisted_new_edges(tmp_path):
    f = Fabric(tmp_path)
    d = f.add([_e("a:1", "a:2", "same_x", 0.5), _e("a:1", "a:2", "same_x", 0.5)])  # duplicate
    assert d == {"new_edges": 1, "new_nodes": 2, "dup_edges": 1}
    edges, nodes = f.drain_recent()
    assert len(edges) == 1 and sorted(nodes) == ["a:1", "a:2"]
    assert f.drain_recent() == ([], [])


# ---- ARACHNE-06: freshness -----------------------------------------------
def test_freshness_record_states_productive_vs_no_op():
    rep = {"knots": {"available": False, "reason": "r", "credential_source": "none"}}
    ws = {"base_sha": "abc", "branch": "b", "worktree_path": "p", "dirty": False, "main_worktree": False}
    r0 = freshness_record(tick=1, started_at="s", last_success_at=None, landscape_report=rep,
                          workspace=ws, productivity=tick_productivity([], [], {}), alive=0)
    assert r0["state"] == "ACTIVE_NO_OP" and r0["last_success_at"] is None
    assert r0["landscapes"]["knots"]["reason"] == "r"
    r1 = freshness_record(tick=2, started_at="s", last_success_at="t2", landscape_report=rep, workspace=ws,
                          productivity=tick_productivity([_e("a:1", "a:2", "o", 0.1)], ["a:1", "a:2"], {}), alive=1)
    assert r1["state"] == "PRODUCTIVE" and r1["last_success_at"] == "t2"


# ---- ARACHNE-08: intervention ledger -------------------------------------
def test_intervention_ledger_rows_are_appended_with_workspace(tmp_path, monkeypatch):
    import agents.arachne.swarm as S
    monkeypatch.setattr(S, "INTERVENTIONS", tmp_path / "ledgers" / "interventions.jsonl")
    sw = S.Swarm.__new__(S.Swarm)
    sw.tick = 7
    sw.workspace = {"base_sha": "abc", "branch": "b", "worktree_path": "p"}
    sw._intervene("tweak", id="oeis-0-4", knobs={"novelty_floor": 0.7})
    sw._intervene("kill", id="oeis-0-4")
    rows = [json.loads(l) for l in (tmp_path / "ledgers" / "interventions.jsonl").read_text().splitlines()]
    assert [r["kind"] for r in rows] == ["tweak", "kill"]
    assert rows[0]["tick"] == 7 and rows[0]["workspace"]["base_sha"] == "abc" and rows[0]["knobs"] == {"novelty_floor": 0.7}
