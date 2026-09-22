"""F-R7-4 prep: the capacity probe runs as NODE_CAPACITY_PROFILE_R7 under a 1200 s budget (SWARM_R7 O3, gate 29).
The exp name reaches the rows file, the JSON profile and pm:capacity:profile; the profile key holds no orphanable
pushed sha (R5: the stamped sha was rewritten by the ops.push rebase); the budget cut marks later k untested."""
from __future__ import annotations

import json
import subprocess

import pytest

from primordial.fabric import broker as BR
from primordial.ops import capacity as CAP
from primordial.tests._live import live_url

R7 = "NODE_CAPACITY_PROFILE_R7"


def step(k, thr, p95=10.0):
    return {"k": k, "threads": CAP.threads_for(k), "throughput": thr, "p95_wall_s": p95, "errors": 0, "gens": 50,
            "batch": 128, "copies": [{"wall_s": p95, "cpu_s": 1.0}]}


def test_probe_exp_and_budget_cut():
    t = {1: 100, 2: 200, 3: 300, 4: 400, 6: 500, 8: 560}
    prof = CAP.probe(step_fn=lambda k, g, to: step(k, t[k]), gens=50, exp=R7, log=lambda *_: None)
    assert prof["exp"] == R7 and prof["k_star"] == 6 and prof["rule"]["failed_at"] == 8     # 560 < 1.15 x 500
    cut = CAP.probe(step_fn=lambda k, g, to: step(k, t[k]), gens=50, exp=R7, budget_s=0.0, log=lambda *_: None)
    assert cut["steps"] == [] and cut["untested"] == list(CAP.GRID) and cut["k_star"] is None


def test_write_uses_exp_and_no_pushed_sha(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(live_url(), decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setenv("PM_TAG", "t-r7-4")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    r.delete(BR.PROFILE_KEY)
    try:
        prof = CAP.probe(step_fn=lambda k, g, to: step(k, {1: 100, 2: 200, 3: 210}[k]), gens=50, grid=(1, 2, 3),
                         exp=R7, log=lambda *_: None)
        CAP.write(prof, r=r, repo=tmp_path, out=tmp_path / "rows")
        assert (tmp_path / "rows" / f"{R7}.jsonl").exists() and (tmp_path / "rows" / f"{R7}.json").exists()
        rows = [json.loads(x) for x in (tmp_path / "rows" / f"{R7}.jsonl").read_text(encoding="utf-8").splitlines()]
        assert {x["exp_id"] for x in rows} == {R7} and rows[-1]["kind"] == "capacity_profile"
        key = json.loads(r.get(BR.PROFILE_KEY))
        assert key["exp"] == R7 and key["k_star"] == 2 and key["threads_per_worker"] == 8
        assert "sha" not in key and key["sha_local"]
        assert BR.profile(r)["k_star"] == 2                                     # the broker reads k* from it
        again = CAP.from_rows(tmp_path / "rows" / f"{R7}.jsonl", exp=R7)
        assert again["exp"] == R7 and again["k_star"] == 2
    finally:
        r.delete(BR.PROFILE_KEY)
