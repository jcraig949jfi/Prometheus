"""S2 anomaly triage: open/resolved per epoch, children-then-age ordering, the RAISE_D rule."""
from __future__ import annotations

from primordial.score import anomaly_triage as AT


def recs():
    return [{"id": "1-0", "lane": "A", "ts": "0", "source": "round 1 seed", "subject": "ANOM-3-0 in prose is ignored"},
            {"id": "2-0", "lane": "D", "ts": "10", "source": "D1c (ANOM-1-0)"},
            {"id": "3-0", "lane": "C", "ts": "20", "source": "C-R2-01 rows/C"},
            {"id": "3-0", "lane": "D", "ts": "25", "event": True, "status": "RESOLVED", "exp_id": "D9"},
            {"id": "2-0", "lane": "D", "ts": "40", "event": True, "status": "INDETERMINATE", "exp_id": "D8"}]


def test_epoch_report_counts_and_orders_by_children_then_age():
    filed, events = AT.split_records(recs())
    assert AT.parents(filed["2-0"], filed) == ["1-0"] and AT.parents(filed["1-0"], filed) == []
    e1 = AT.epoch_report(filed, events, 0.0, 30.0)
    assert (e1["open"], e1["resolved"], e1["rule"]) == (2, 1, "HOLD")          # 2 > 2x1 is false
    assert [x["id"] for x in e1["triage"]] == ["1-0", "2-0"] and e1["triage"][0]["children"] == 1
    e2 = AT.epoch_report(filed, events, 30.0, 60.0)
    assert (e2["open"], e2["resolved"], e2["rule"]) == (2, 0, "RAISE_D")       # INDETERMINATE stays open
    assert e2["triage"][0]["age_s"] == 60.0


def test_proposal_moves_the_step_from_b_to_d_only():
    p = AT.proposal()
    assert p == {"B": 0.35, "C": 0.25, "D": 0.25, "E": 0.15} and abs(sum(p.values()) - 1.0) < 1e-9


def test_round2_replay_applies_the_rule_per_epoch():
    out = AT.triage()
    assert len(out["epochs"]) == 3 and out["epochs"][0]["window"][0] == out["start"]
    assert sum(e["resolved"] for e in out["epochs"]) == 4                        # D resolved 4 in round 2
    for e in out["epochs"]:
        assert e["rule"] == ("RAISE_D" if e["open"] > 2 * e["resolved"] else "HOLD")
        ages = [(x["children"], x["age_s"]) for x in e["triage"]]
        assert ages == sorted(ages, key=lambda t: (-t[0], -t[1]))
    assert (out["proposal"] is not None) == bool(out["raise_d_epochs"])
    assert AT.triage() == out
