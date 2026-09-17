"""The architectural acceptance test (operator order s12, point release 2026-09).

A SMALL Campaign-3-shaped run -- a curriculum ladder with rung transitions, a
mid-run controlled import with an intended and a realized dose, a checkpoint,
a counterfactual fork under a different schedule, and a run that ends before
its horizon -- is recorded through the v9 surface. Then a DOWNSTREAM
CONSUMER (the `Reconstruct` class below, which knows only the public read
routes) rebuilds every fact the science layer would need:

    exact world manifest; logical generations; pressure/event changes;
    start/fork ancestry; the realized intervention; observations; the
    termination horizon; censoring-relevant facts; artifacts; the complete
    paginated event history

and the engine's own record contains none of the words SHELF, SUMMIT,
CORRIDOR, TAKEOVER, GENERALIZATION -- those are the CALLER's words (they
appear in the manifest and the payloads the fixture writes, deliberately)
and the engine has stored them as opaque bytes. The science that decides
"was this a shelf" happens in the consumer, from facts, after the fact.
"""
import base64
import json
import os
import re
import sys

from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from sfe.api import create_app                                    # noqa: E402
from sfe.ids import content_hash                                  # noqa: E402

HDR = "X-SFE-Session"
FORBIDDEN = ("SHELF", "SUMMIT", "CORRIDOR", "TAKEOVER", "GENERALIZATION")

# The caller's world definition. The thresholds and level names are THEIRS;
# the engine hashes this object and reads only the two reserved keys.
MANIFEST = {
    "kind": "wse.bitstring.k2",
    "logical_time_unit": "generation",
    "declared_event_kinds": ["ladder.rung", "import.intended", "import.realized", "probe.dense"],
    "cell": "W2_K2", "value_bits": 4, "N": 200,
    "levels": {"floor": 0.0, "SHELF_MIN": 0.45, "SUMMIT_MIN": 0.90},   # caller vocabulary, opaque here
    "ladder": {"rungs": [0, 1, 2, 4], "rung0_max_hold": "until best >= 0.5"},
    "stop_rule": "first_confirmed_summit_or_horizon",
    "horizon": 120,
}


class Run:
    """the CAMPAIGN side: writes facts through the public routes"""

    def __init__(self, tmp_path):
        self.c = TestClient(create_app(str(tmp_path / "c3.db")))
        tok = self.c.post("/v2/clients", json={"name": "cmp-fixture"}).json()["token"]
        self.h = {"Authorization": "Bearer " + tok}
        sess = self.c.post("/v2/sessions", json={"name": "c3-fixture"}, headers=self.h).json()
        self.h[HDR] = sess["session_key"]
        self.sid = sess["session_id"]

    def post(self, path, body, key=None):
        h = dict(self.h)
        if key:
            h["Idempotency-Key"] = key
        r = self.c.post(path, json=body, headers=h)
        assert r.status_code == 200, (path, r.text)
        return r.json()

    def world(self, name, labels):
        w = self.post("/v2/worlds", {"session_id": self.sid, "name": name, "manifest": MANIFEST,
                                     "manifest_schema": "archaeon.wse.world/3", "labels": labels, "seed_root": 20260920})
        self.post("/v2/worlds/%s/start" % w["world_id"], {})
        return w

    def generation(self, wid, g, best, key_tag):
        e = self.post("/v2/worlds/%s/experiments" % wid, {"spec": {"g": g, "cell": "W2_K2"}}, key="%s:e:%d" % (key_tag, g))["exp_id"]
        self.post("/v2/worlds/%s/experiments/%s/commit" % (wid, e), {})
        self.post("/v2/worlds/%s/observations" % wid,
                  {"exp_id": e, "content": {"best_training": best, "held_out": round(best * 0.95, 3)},
                   "outcome": "SURVIVED", "logical_time": g}, key="%s:o:%d" % (key_tag, g))


class Reconstruct:
    """the DOWNSTREAM side: knows only the read routes + cursors"""

    def __init__(self, c, h, wid):
        self.c, self.h, self.wid = c, h, wid

    def get(self, path):
        r = self.c.get(path, headers=self.h)
        assert r.status_code == 200, (path, r.text)
        return r.json()

    def walk(self, path, key, limit=7):
        rows, after = [], 0
        while after is not None:
            p = self.get("%s?after_seq=%d&limit=%d" % (path, after, limit))
            rows += p[key]; after = p["next_after_seq"]
        return rows

    def rebuild(self):
        w = self.get("/v2/worlds/%s" % self.wid)
        events = self.walk("/v2/worlds/%s/events" % self.wid, "events")
        obs = self.walk("/v2/worlds/%s/observations" % self.wid, "observations")
        arts = self.walk("/v2/worlds/%s/artifacts" % self.wid, "artifacts")
        man = self.get("/v2/worlds/%s/manifest" % self.wid)
        wev = [e for e in events if e["event_type"] == "WORLD_EVENT"]
        by_kind = {}
        for e in wev:
            by_kind.setdefault(e["payload"]["kind"], []).append(
                {"t": e["payload"]["logical_time"], **e["payload"]["payload"]})
        forked = [e for e in events if e["event_type"] == "WORLD_FORKED"]
        return {
            "manifest": man["manifest"], "manifest_hash": man["manifest_hash"], "labels": w["labels"],
            "generations": [o["logical_time"] for o in obs],
            "best_by_gen": {o["logical_time"]: o["content"]["best_training"] for o in obs},
            "pressure_changes": by_kind.get("ladder.rung", []),
            "probes": by_kind.get("probe.dense", []),
            "import_intended": by_kind.get("import.intended", []),
            "import_realized": by_kind.get("import.realized", []),
            "ancestry": {"parent": w["parent_world_id"], "fork_point": w["fork_point"],
                         "changed": forked[0]["payload"]["changed"] if forked else None,
                         "interventions": forked[0]["payload"]["interventions"] if forked else None},
            "termination": w["termination"],
            "artifacts": [(a["kind"], a["blob_hash"]) for a in arts],
            "n_events": len(events), "chain_ok": all(events[i]["prev_hash"] == events[i - 1]["entry_hash"]
                                                     for i in range(1, len(events))
                                                     if events[i]["world_index"] == events[i - 1]["world_index"] + 1),
        }


def test_campaign3_shaped_run_is_fully_reconstructable_from_facts(tmp_path):
    run = Run(tmp_path)
    w = run.world("C3-fixture/a01", {"campaign": "cmp-fixture", "experiment": "C3-FIX-01", "attempt": "a01"})
    wid = w["world_id"]
    assert w["manifest_hash"] == content_hash(MANIFEST)

    # the ladder: rung 0 held until best >= 0.5, then fixed schedule
    schedule = {0: 0, 31: 1, 56: 2, 81: 4}
    best = 0.0
    for g in range(100):                                           # the run stops at 100 of a 120 horizon
        if g in schedule:
            run.post("/v2/worlds/%s/events" % wid, {"kind": "ladder.rung", "logical_time": g,
                                                    "payload": {"rung": schedule[g], "delay": schedule[g]}}, key="rung:%d" % g)
        if g == 40:
            run.post("/v2/worlds/%s/events" % wid, {"kind": "import.intended", "logical_time": g,
                                                    "payload": {"dose": 4, "source": "W0-mature", "cap": 0.25}})
            run.post("/v2/worlds/%s/events" % wid, {"kind": "import.realized", "logical_time": g,
                                                    "payload": {"dose": 3, "ids": ["org_1", "org_2", "org_3"],
                                                                "origin_shares": {"import": 0.015}}})
        best = min(1.0, best + 0.012 + (0.02 if 31 <= g < 56 else 0))
        run.generation(wid, g, round(best, 3), "run")
        if g % 10 == 0:
            run.post("/v2/worlds/%s/events" % wid, {"kind": "probe.dense", "logical_time": g,
                                                    "payload": {"held_out": {"d0": round(best, 3), "d4": round(best * 0.5, 3)}}})
        if g == 60:
            ck = run.post("/v2/worlds/%s/checkpoint" % wid, {})
            run.post("/v2/worlds/%s/artifacts" % wid, {"kind": "population", "data_b64": base64.b64encode(b"pop@60").decode(),
                                                       "meta": {"logical_time": 60}})
    # the counterfactual: same organisms, same RNG, different schedule from generation 60
    kids = run.post("/v2/worlds/%s/fork" % wid, {"checkpoint_id": ck["checkpoint_id"], "children": [
        {"name": "C3-fixture/a01/cf-Q", "manifest": {**MANIFEST, "ladder": {"rungs": [0, 4], "rung0_max_hold": "none"}},
         "manifest_schema": "archaeon.wse.world/3", "interventions": {"schedule": "Q"}}]})["children"]
    cf = kids[0]["world_id"]
    run.post("/v2/worlds/%s/start" % cf, {})
    for g in range(61, 70):
        run.generation(cf, g, 0.5, "cf")
    run.post("/v2/worlds/%s/terminate" % cf, {"reason": "fixture:budget", "logical_time": 69, "horizon": 120})
    # the run stops BEFORE its horizon (censoring-relevant)
    run.post("/v2/worlds/%s/terminate" % wid, {"reason": "stop_rule:operator_budget", "logical_time": 99, "horizon": 120,
                                               "budget_consumed": {"evaluations": 20000}, "reference": "C3-FIX-01/a01"})

    # ---- downstream reconstruction from the read surface only
    R = Reconstruct(run.c, run.h, wid)
    f = R.rebuild()
    assert f["manifest"] == MANIFEST and f["manifest_hash"] == content_hash(MANIFEST)
    assert f["labels"] == {"campaign": "cmp-fixture", "experiment": "C3-FIX-01", "attempt": "a01"}
    assert f["generations"] == list(range(100))
    assert [(p["t"], p["rung"]) for p in f["pressure_changes"]] == [(0, 0), (31, 1), (56, 2), (81, 4)]
    assert len(f["probes"]) == 10
    assert f["import_intended"][0]["dose"] == 4 and f["import_realized"][0]["dose"] == 3   # intended != realized, visible
    assert f["termination"]["horizon"] == 120 and f["termination"]["logical_time"] == 99
    censored_before_horizon = f["termination"]["logical_time"] < f["termination"]["horizon"]
    assert censored_before_horizon                                   # "0 summits" is interpretable: the run ended early
    assert f["artifacts"] and f["artifacts"][0][0] == "population"
    assert f["chain_ok"] and f["n_events"] > 300
    # the consumer applies ITS thresholds to the engine's facts
    thr = f["manifest"]["levels"]["SHELF_MIN"]
    first_at = next((g for g in sorted(f["best_by_gen"]) if f["best_by_gen"][g] >= thr), None)
    assert first_at is not None and 0 < first_at < 60
    # the counterfactual branch: ancestry and exactly what changed
    C = Reconstruct(run.c, run.h, cf).rebuild()
    assert C["ancestry"]["parent"] == wid and C["ancestry"]["fork_point"] == ck["world_index"]
    assert set(C["ancestry"]["changed"]) == {"manifest_hash"} and C["ancestry"]["interventions"] == {"schedule": "Q"}
    assert C["manifest"]["ladder"]["rungs"] == [0, 4] and C["generations"] == list(range(61, 70))
    # the child inherits the parent's event prefix (its pre-fork history is readable by reference)
    assert C["n_events"] > 9 * 3

    # ---- the words are the caller's, not the engine's
    src_dir = os.path.join(os.path.dirname(HERE), "sfe")
    engine_src = "\n".join(open(os.path.join(src_dir, n), encoding="utf-8").read()
                           for n in os.listdir(src_dir) if n.endswith(".py"))
    for word in FORBIDDEN:
        assert not re.search(word, engine_src, re.IGNORECASE), word
    # ...and they DO travel through the engine unchanged, as opaque bytes
    assert "SHELF_MIN" in json.dumps(f["manifest"])
    cap = run.c.get("/v2/capabilities").json()
    for word in FORBIDDEN:
        assert word not in json.dumps(cap).upper()
