"""Tests for the multi-day campaign driver and supervisor (plan identity, founder premises, bounded events,
checkpoints, integrity gate). Science is not tested here; the premises the prereg relies on are."""
from __future__ import annotations

import json
import pathlib

from prometheus.z80atlas import multiday_campaign as MD
from prometheus.z80atlas import multiday_supervisor as SUP
from prometheus.z80atlas import coupling_campaign as CC
from prometheus.z80atlas.tasks import Task, verify_exact

ROOT = pathlib.Path(__file__).resolve().parents[3]
INPUTS = ROOT / "roles" / "Bellerophon" / "multiday_2026-09-26" / "receipts" / "md_inputs.json"


def _inputs():
    return json.loads(INPUTS.read_text(encoding="utf-8"))


def test_plan_is_deterministic_and_sized():
    a, b = MD.plan(_inputs()), MD.plan(_inputs())
    assert MD.plan_hash(a) == MD.plan_hash(b)
    by = {}
    for p in a:
        by[p["lane"]] = by.get(p["lane"], 0) + 1
    assert by == {"LADDER1": 2 * 4 * MD.N_SEEDS["LADDER1"], "LADDER2": 2 * 4 * MD.N_SEEDS["LADDER2"],
                  "COPIER": 2 * 4 * MD.N_SEEDS["COPIER"], "REPAIR": 2 * 3 * MD.N_SEEDS["REPAIR"]}
    assert len({p["id"] for p in a}) == len(a) and len({(p["pair"], p["arm"]) for p in a}) == len(a)


def test_arms_of_a_pair_share_the_seed_and_yoked_depends_on_on():
    P = MD.plan(_inputs()); ids = {p["id"]: p for p in P}
    pairs = {}
    for p in P:
        pairs.setdefault(p["pair"], []).append(p)
    for arms in pairs.values():
        assert len({p["seed"] for p in arms}) == 1
        for p in arms:
            if p["arm"] == "YOKED":
                assert ids[p["depends"]]["arm"] == "ON" and ids[p["depends"]]["pair"] == p["pair"]
            else:
                assert p["depends"] is None


def test_seeds_disjoint_from_earlier_campaigns():
    for p in MD.plan(_inputs()):
        assert 12_000_000_000_000 <= p["seed"] < 12_200_000_000_000


def test_founders_are_not_competent_on_the_paid_task():
    """The prereg's premise: any competent SR on the PAID task at the end of a ladder run is an acquisition."""
    fnd = _inputs()["founders"]
    for f in fnd["ECHO"]:
        t = bytes.fromhex(f["tape"])
        assert verify_exact(t, 64, Task("ECHO"), "ABR") and not verify_exact(t, 64, Task("INC"), "ABR")
    for f in fnd["INC"]:
        t = bytes.fromhex(f["tape"])
        assert verify_exact(t, 64, Task("INC"), "ABR") and not verify_exact(t, 64, Task("COND_ONE"), "ABR")
    rep = bytes.fromhex(CC.fixtures("ECHO", 1)["REP"])
    assert not verify_exact(rep, 64, Task("ECHO"), "ABR")                    # COPIER start cannot already ECHO


def test_bounded_events_keep_exactly_what_the_runner_writes():
    ev = [{"kind": "copy", "i": i} if i % 3 else {"kind": "migration", "i": i} for i in range(5000)]
    b = MD._BoundedEvents()
    for e in ev:
        b.append(e)
    expected = ev[:400] + [e for e in ev[400:] if e["kind"] != "copy"][:200]
    assert list(b) == expected


def test_checkpoints():
    assert MD.checkpoints(20_000) == [999, 1999, 4999, 9999, 14999, 19999]
    assert MD.checkpoints(300)[-1] == 299


def test_integrity_gate(tmp_path):
    P = MD.plan(_inputs())
    good = [{k: p[k] for k in ("id", "seed", "lane", "cell", "arm", "K", "k", "pair", "founder")} for p in P[:3]]
    (tmp_path / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in good), encoding="utf-8")
    assert SUP.integrity(tmp_path, INPUTS)["ok"]
    bad = good + [dict(good[0])]                                            # duplicate
    (tmp_path / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in bad), encoding="utf-8")
    assert not SUP.integrity(tmp_path, INPUTS)["ok"]
    wrong = [dict(good[0], seed=good[0]["seed"] + 1)]                        # treatment identity changed
    (tmp_path / "results.jsonl").write_text(json.dumps(wrong[0]) + "\n", encoding="utf-8")
    assert not SUP.integrity(tmp_path, INPUTS)["ok"]
    (tmp_path / "results.jsonl").write_text(json.dumps(good[0]) + "\n" + '{"id": "m0', encoding="utf-8")   # torn tail tolerated
    r = SUP.integrity(tmp_path, INPUTS)
    assert r["ok"] and r["torn_tail"] == 1
