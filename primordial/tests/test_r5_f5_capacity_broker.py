"""F-R5-5: the O3 capacity rule and the CPU broker (launch gate item 5 is the committed profile itself).
Rule: k* = largest grid k with every step >= 1.15x the previous throughput, p95 wall <= 1.5x p95(1), no
errors; the probe stops at the first failing step (O9). Broker: tokens cap total concurrency at k*, any
cohort may take idle CPU, grants carry the cohort while budget stays in done records."""
from __future__ import annotations

import json
import subprocess
import threading
import time

import pytest

from primordial.bus import bus
from primordial.fabric import broker as BR
from primordial.fabric import envelope as EV
from primordial.fabric import worker as W
from primordial.ops import capacity as CAP
from primordial.tests._live import live_url

URL = live_url()


def step(k, thr, p95=10.0, errors=0):
    return {"k": k, "threads": CAP.threads_for(k), "throughput": thr, "p95_wall_s": p95, "errors": errors,
            "copies": [{"wall_s": p95}]}


def test_threads_per_worker():
    assert [CAP.threads_for(k) for k in CAP.GRID] == [8, 8, 5, 4, 2, 2]


@pytest.mark.parametrize("steps,k_star,failed_at", [
    ([step(1, 100), step(2, 116), step(3, 134), step(4, 155), step(6, 179), step(8, 206)], 8, None),
    ([step(1, 100), step(2, 116), step(3, 127)], 2, 3),                      # 127 < 1.15 x 116
    ([step(1, 100), step(2, 200), step(3, 300), step(4, 400, p95=15.1)], 3, 4),   # p95 15.1 > 1.5 x 10
    ([step(1, 100), step(2, 200, errors=1)], 1, 2),
    ([step(1, 100, errors=1)], None, 1),
])
def test_o3_rule(steps, k_star, failed_at):
    v = CAP.rule(steps)
    assert v["k_star"] == k_star and v["failed_at"] == failed_at
    assert v["threads"] == (None if k_star is None else CAP.threads_for(k_star))


def test_probe_stops_at_first_failing_step():
    calls = []
    table = {1: 100, 2: 150, 3: 160, 4: 999, 6: 999, 8: 999}

    def fake(k, gens, timeout_s):
        calls.append((k, gens))
        return step(k, table[k])
    prof = CAP.probe(step_fn=fake, gens=50, log=lambda *_: None)
    assert [k for k, _ in calls] == [1, 2, 3]                                  # O9: never ran 4, 6, 8
    assert prof["k_star"] == 2 and prof["threads_per_worker"] == 8 and prof["untested"] == [4, 6, 8]
    assert prof["rule"]["failed_at"] == 3 and prof["workload"]["fn"] == "primordial.metric.baseline:baseline_run"


def test_probe_calibrates_gens_from_measurement():
    seen = []

    def fake(k, gens, timeout_s):
        seen.append(gens)
        s = step(k, 100 * k)
        s["copies"] = [{"wall_s": gens * 0.01}]                                # 10 ms per gen
        return s
    prof = CAP.probe(step_fn=fake, target_s=20, cal_gens=400, grid=(1, 2), log=lambda *_: None)
    assert seen == [400, 2000, 2000] and prof["workload"]["gens"] == 2000 and prof["k_star"] == 2


# ------------------------------------------------------------------ broker (live db)

@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    lanes = ("FbB", "FbD")
    keys = [BR.PROFILE_KEY, EV.EVENTS, EV.CANDIDATES, "pm:round:current"] + [BR.TOKEN.format(i) for i in range(8)]
    for L in lanes:
        keys += [W.JOBS.format(L), W.ROWS.format(L), W.DONE.format(L), W.STOP.format(L), W.WSTATE.format(L)]
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r5-5")
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    yield r, tmp_path
    r.delete(*keys)


def test_token_cas_and_cap(env):
    r, _ = env
    assert BR.acquire(r, "FbD") is None                                        # no profile, no broker
    r.set(BR.PROFILE_KEY, json.dumps({"k_star": 2, "threads_per_worker": 8}))
    a, b = BR.acquire(r, "FbD"), BR.acquire(r, "FbB")
    assert a and b and BR.acquire(r, "FbD") is None and {a["slot"], b["slot"]} == {0, 1}
    stale = dict(a)
    a = BR.assign(r, a, {"job_id": "j1"}, "D", ttl_s=30)
    assert not BR.release(r, stale) and BR.release(r, a) and BR.acquire(r, "FbB")["slot"] == a["slot"]


def test_idle_cohort_strands_no_cpu_and_cap_holds(env):
    r, repo = env
    r.set(BR.PROFILE_KEY, json.dumps({"k_star": 2, "threads_per_worker": 8}))
    for i in range(4):
        W.submit("FbD", "primordial.fabric.selftest_jobs:sleep_rows", f"D{i}", "rows/d.jsonl", 30, {"s": 1.5}, r=r,
                 envelope=EV.example(cohort="D"))
    workers = [W.Worker("FbD", url=URL, repo=repo, log=lambda *_: None),
               W.Worker("FbD", url=URL, repo=repo, log=lambda *_: None),
               W.Worker("FbB", url=URL, repo=repo, log=lambda *_: None)]
    done = {i: [] for i in range(3)}
    ths = [threading.Thread(target=lambda i=i, w=w: done[i].extend(w.serve(block_ms=300, deadline_s=40,
                                                                          idle_exit_s=6)))
           for i, w in enumerate(workers)]
    for t in ths:
        t.start()
    time.sleep(4)
    W.submit("FbB", "primordial.fabric.selftest_jobs:sleep_rows", "B0", "rows/b.jsonl", 30, {"s": 1.5}, r=r,
             envelope=EV.example(cohort="B"))
    for t in ths:
        t.join(timeout=60)
    recs = [d for i in done for d in done[i]]
    assert sorted(d["status"] for d in recs) == ["ok"] * 5
    iv = sorted((d["started"], d["ended"]) for d in recs)
    peak = max(sum(1 for s, e in iv if s <= t0 < e) for t0, _ in iv)
    assert peak <= 2                                                           # k* caps host concurrency
    d_iv = sorted((d["started"], d["ended"]) for d in recs if d["cohort"] == "D")
    assert any(d_iv[i + 1][0] < d_iv[i][1] for i in range(len(d_iv) - 1))      # D used both slots while B idle
    assert all(d["cpu_token"]["threads"] == 8 for d in recs)
    grants = [e for e in EV.events(r, "CPU_TOKEN_GRANT")]
    assert sorted(e["cohort"] for e in grants) == ["B", "D", "D", "D", "D"]
    assert {d["cohort"] for d in recs} == {"B", "D"} and BR.holders(r) == []


# ------------------------------------------------------------------ profile writing (06:35 crash regression)

def _git_repo(p):
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(p), *a], check=True)
    (p / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(p), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(p), "commit", "-q", "-m", "init"], check=True)


MEASURED = [(1, 9917.271880240265, 20.818628600005468), (2, 13259.81214153191, 31.14131599999382),
            (3, 14854.6, 41.697)]                                      # the 06:35 committed step rows


def test_write_profile_row_and_rebuild_from_rows(tmp_path, monkeypatch):
    monkeypatch.setenv("PM_TAG", "t-r5-5w")
    _git_repo(tmp_path)
    out = tmp_path / "rows"
    steps = [dict(step(k, thr, p95), gens=1613, batch=128, copies=[{"wall_s": p95, "cpu_s": 1.0}])
             for k, thr, p95 in MEASURED]
    prof = CAP.probe(step_fn=lambda k, g, t: steps[[1, 2, 3].index(k)], gens=1613, log=lambda *_: None)
    assert prof["profile_status"] == "OK" and prof["k_star"] == 2          # k=3: 1.12x < 1.15x and p95 41.7 > 31.2
    CAP.write(prof, repo=tmp_path, out=out)                               # raised ValueError at 06:35
    rows = [json.loads(x) for x in (out / f"{CAP.EXP}.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [x["kind"] for x in rows] == ["capacity_step"] * 3 + ["capacity_profile"]
    assert all(x["status"] == "record" for x in rows) and rows[-1]["profile_status"] == "OK"
    again = CAP.from_rows(out / f"{CAP.EXP}.jsonl")
    assert (again["k_star"], again["threads_per_worker"], again["rule"]["failed_at"], again["untested"]) == (
        2, 8, 3, [4, 6, 8])
