"""R8 item 4: the frozen world set screened with R16 semantics -- world keys resolve through the frozen manifest."""
from __future__ import annotations

import pytest

from primordial.metric import screen_r8 as S8
from primordial.metric import world_set_r8 as WS
from primordial.metric.tests.test_r16 import Ctx
from primordial.tests._live import live_url


def test_keys_are_collision_free_and_resolve_to_the_manifest_world():
    ks = S8.keys()
    assert len(ks) == 232 and len({v["key"] for v in ks.values()}) == 232
    body = S8.manifest()["body"]
    S8.install()
    from primordial.qd import e4_run as E4
    from primordial.soup.b1 import common as CM
    for e in body["entries"]:
        k = ks[e["world_id"]]["key"]
        assert (k >= S8.L_KEY0) == (e["stratum"] == "L")
        if e["stratum"] == "B":
            assert 900000 <= k < 900064
    for w in body["screen_order"][:8]:
        spec = E4.Spec(ks[w]["key"])
        e = body["entries"][ks[w]["entry_index"]]
        assert spec.wid == w and spec.mech.manifest_hash() == e["mech_hash"] and WS.summary(spec.mech) == e["summary"]
    assert CM.make_world(13)[1] == WS.BASE_WORLD_ID                       # the grid is untouched
    with pytest.raises(KeyError):
        CM.make_world(S8.L_KEY0 + 10_000)


def test_plan_follows_the_frozen_screen_order_and_admits():
    from primordial.fabric import envelope as EV
    order = S8.manifest()["body"]["screen_order"]
    p = S8.plan(order[:4])
    assert [x["kwargs"]["world_id"] for x in p[::2]] == order[:4] and all(x["band"] == "L1" for x in p)
    for x in p:
        assert EV.admit(x["envelope"])["ok"], EV.admit(x["envelope"])


def test_world_cell_job_smoke_tiny_budget(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    c = redis.Redis.from_url(live_url())
    try:
        c.ping()
    except Exception:
        pytest.skip("substrate not reachable")
    from primordial.metric import baseline as B
    from primordial.metric import invariant as I
    from primordial.metric import r16_cells as RC
    from primordial.metric import replication as RP
    monkeypatch.setattr(RP, "STREAM", "pm:test:g-r8-smoke-repl")
    monkeypatch.setattr(RP, "PUBLISHED", "pm:test:g-r8-smoke-repl:published:{}|{}")
    monkeypatch.setattr(RC, "EVENTS", "pm:test:g-r8-smoke-events")
    empty = tmp_path / "none.jsonl"
    monkeypatch.setattr(RC.R, "ROWS", {**RC.R.ROWS, "baseline": str(empty)})
    url = live_url()
    pub = redis.Redis.from_url(url, decode_responses=True)
    w = S8.manifest()["body"]["screen_order"][0]
    ctx = Ctx()
    try:
        S8.world_cell_job(ctx, w, "train128_held64", replication_r=pub, families=(4200, 2101), run_seeds=(0, 1),
                          gens=2, batch=8, learner_gens=2, learner_batch=8, base_archive=url, learn_archive=url,
                          base_elites=str(tmp_path / "b"), learn_elites=str(tmp_path / "l"), prefill_paths=(empty,),
                          cpu_budget_s=0.0)
    finally:
        for k in c.scan_iter(f"pm:qd:g-r16-*w{S8.keys()[w]['key']}*", count=5000):
            c.delete(k)
    kinds = [x["kind"] for x in ctx.rows]
    assert kinds[0] == "r8_world_key" and ctx.rows[0]["world_id"] == w and kinds[-1] == "r8_cell"
    assert "floor_suite_r16" in kinds and "r16_cell" in kinds
