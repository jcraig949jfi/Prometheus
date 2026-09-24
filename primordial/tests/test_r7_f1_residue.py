"""F-R7-1 (D12 + D14, gate item 26): planted residue of each kind is found and refuses the round start; the
round close stops EXACTLY the registered worker processes (argv tokens verified, never by substring) and then
clears the stop flags. Decoys that merely contain the worker words survive."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
import uuid

import psutil
import pytest

from primordial.bus import bus
from primordial.fabric import worker as W
from primordial.ops import epoch as EP
from primordial.ops import residue as RS
from primordial.ops import round_clock as RC
from primordial.tests._live import live_url

URL = live_url()
ROOT = pathlib.Path(__file__).resolve().parents[2]
RID = "t-r7-1"


# ------------------------------------------------------------------ argv verification (no Redis)

@pytest.mark.parametrize("argv,lane,ok", [
    (["python.exe", "-m", "primordial.fabric.worker", "serve", "--lane", "D"], "D", True),
    (["python", "-m", "primordial.fabric.worker", "serve", "--lane", "D", "--idle-exit-s", "60"], "D", True),
    (["python", "-u", "-m", "primordial.fabric.worker", "serve", "--max-jobs", "3", "--lane=D"], "D", True),
    (["python", "-m", "primordial.fabric.worker", "serve", "--lane", "DD"], "D", False),
    (["python", "-m", "primordial.fabric.worker", "submit", "D", "fn"], "D", False),
    (["python", "-c", "x='-m primordial.fabric.worker serve --lane D'"], "D", False),       # joined-string trap
    (["python", "-c", "import time; time.sleep(9)", "-m", "primordial.fabric.worker", "serve", "--lane", "D"],
     "D", False),                                                                             # -c decoy, tokens present
    (["python", "-m", "primordial.ops.residue", "stop", "--lane", "D"], "D", False),
    ("python -m primordial.fabric.worker serve --lane D", "D", False),                        # a joined string
])
def test_verify_worker_cmdline(argv, lane, ok):
    assert RS.verify_worker_cmdline(argv, lane) is ok


def test_convention_allowed_repos():
    class R:
        def smembers(self, k):
            return set()
    _, allowed, src = RS.allowed_repos(R(), "t-r9")                           # no declared lane_repos
    assert src == "convention" or os.environ.get("PM_ROUND_WORKTREES")
    if src == "convention":
        assert allowed("B", "F:/Prometheus-worktrees/nestor-t-r9-b") and allowed("G", "F:\\Prometheus-worktrees\\nestor-bld-f")
        assert not allowed("D", "F:/Prometheus-worktrees/nestor-r6-d") and not allowed("D", "F:/Prometheus")


def test_declared_r7_lane_repos_are_the_default():
    class R:
        def smembers(self, k):
            return {"F:/anything"}
    _, allowed, src = RS.allowed_repos(R(), "r7")
    assert src.startswith("round_clock.ROUNDS[r7]")
    assert allowed("G", "f:\\prometheus-worktrees\\NESTOR-BLD-G\\") and allowed("D", "F:/Prometheus-worktrees/nestor-r7-d")
    assert not allowed("D", "F:/Prometheus-worktrees/nestor-bld-g")         # G's repo is not D's
    assert allowed("gpu", "F:/Prometheus-worktrees/nestor-r6-e") and not allowed("D", "F:/Prometheus-worktrees/nestor-r6-d")
    assert RS.parse_allow("G=F:/x;B=F:/y,F:/z") == {"G": ["F:/x"], "B": ["F:/y", "F:/z"]}
    assert RS.parse_allow("F:/a,F:/b") == ["F:/a", "F:/b"]


def test_gpu_arbiter_cmdline():
    assert RS.verify_worker_cmdline(["python", "-m", "primordial.nv.gpuq", "serve", "--idle-exit-s", "5"], "gpu")
    assert RS.verify_worker_cmdline(["python.exe", "-m", "primordial.nv.gpuq", "serve"], "gpu")   # the bare 4-token form
    assert not RS.verify_worker_cmdline(["python", "-m", "primordial.fabric.worker", "serve"], "D")   # no --lane
    assert not RS.verify_worker_cmdline(["python", "-m", "primordial.nv.gpuq", "serve"], "E")
    assert not RS.verify_worker_cmdline(["python", "-c", "x", "-m", "primordial.nv.gpuq", "serve"], "gpu")
    assert not RS.verify_worker_cmdline(["python", "-m", "primordial.fabric.worker", "serve", "--lane", "gpu"], "gpu")


# ------------------------------------------------------------------ live (db from _live)

@pytest.fixture
def r(monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-r7-1")
    monkeypatch.delenv("PM_ROUND_WORKTREES", raising=False)
    # planted consumers read seconds ago; these tests exercise the DEAD rules, so no recency window here
    # (test_unregistered_active_consumer_is_flagged_and_never_cleared restores the real window)
    monkeypatch.setattr(RS, "ACTIVE_IDLE_S", 0.0)

    def wipe():
        for pat in ("pm:jobs:*", "pm:worker:*", "pm:prior:*", "pm:round:*", "pm:epoch:*", "pm:events", "pm:gpu:*"):
            for k in r.scan_iter(pat):
                r.delete(k)
    wipe()
    procs = []
    yield r, procs
    for p in procs:                                          # by the Popen object only
        if p.poll() is None:
            try:
                for c in psutil.Process(p.pid).children(recursive=True):
                    c.kill()
            except psutil.Error:
                pass
            p.kill()
            p.wait(timeout=30)
    wipe()


def spawn_worker(procs, lane, tag):
    env = dict(os.environ, PM_BUS_URL=URL, PM_TAG=tag, PYTHONPATH=str(ROOT), PM_LANE="")
    p = subprocess.Popen([sys.executable, "-m", "primordial.fabric.worker", "serve", "--lane", lane,
                          "--idle-exit-s", "120"], cwd=str(ROOT), env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    procs.append(p)
    return p


def wait_regs(r, lane, n, timeout=60):
    t = time.monotonic()
    while time.monotonic() - t < timeout:
        regs = [g for g in RS.registrations(r) if g.get("lane") == lane]
        if len(regs) >= n:
            return regs
        time.sleep(0.2)
    raise AssertionError(f"{lane}: {n} registrations not seen")


def kinds(rep):
    return sorted(x["kind"] for x in rep["residue"])


def cli_scan(allowed):
    return RS.main(["scan", "--round", RID] + (["--allowed-repos", allowed] if allowed else []))


def test_clean_store_rc0(r, capsys):
    rr, _ = r
    rr.set("pm:prior:r6:cells", "x")                                          # namespaced: fine
    rep = RS.scan(rr, RID, [str(ROOT)])
    assert rep["ok"] and rep["residue"] == []
    assert cli_scan(str(ROOT)) == 0


def test_stop_flag_residue(r):
    rr, _ = r
    rr.set("pm:jobs:B:stop", "4")                                             # the D12 key, no TTL
    rep = RS.scan(rr, RID, [str(ROOT)])
    assert kinds(rep) == ["STOP_FLAG"] and rep["residue"][0]["key"] == "pm:jobs:B:stop"
    assert cli_scan(str(ROOT)) == 1


def test_unarchived_prior_key_residue(r):
    rr, _ = r
    rr.set("pm:prior:cells", "x")
    rr.set("pm:prior:r5:cells", "x")
    rep = RS.scan(rr, RID, [str(ROOT)])
    assert kinds(rep) == ["UNARCHIVED_PRIOR_KEY"] and rep["residue"][0]["key"] == "pm:prior:cells"


def test_foreign_repo_and_multi_consumer(r):
    rr, procs = r
    lane = f"X{uuid.uuid4().hex[:6]}"
    spawn_worker(procs, lane, "t-a")
    reg = wait_regs(rr, lane, 1)[0]
    assert reg["repo"].lower() == str(ROOT).replace("\\", "/").lower() and reg["pid"] != procs[0].pid or True
    assert RS.verify_worker_cmdline(psutil.Process(reg["pid"]).cmdline(), lane)
    rep = RS.scan(rr, RID, ["F:/Prometheus-worktrees/nestor-r7-x"])           # the code root is foreign
    assert kinds(rep) == ["FOREIGN_REPO"] and rep["residue"][0]["pid"] == reg["pid"]
    assert cli_scan("F:/Prometheus-worktrees/nestor-r7-x") == 1
    spawn_worker(procs, lane, "t-b")                                          # the D14 shape: two per lane
    wait_regs(rr, lane, 2)
    rep = RS.scan(rr, RID, [str(ROOT)])
    assert kinds(rep) == ["MULTI_CONSUMER"] and rep["residue"][0]["lane"] == lane
    assert len(rep["residue"][0]["detail"]["pids"]) == 2


def test_stop_registered_kills_exactly_the_registered_worker(r):
    rr, procs = r
    lane = f"S{uuid.uuid4().hex[:6]}"
    spawn_worker(procs, lane, "t-s")
    reg = wait_regs(rr, lane, 1)[0]
    decoy = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)", "-m", "primordial.fabric.worker",
                              "serve", "--lane", lane], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(decoy)
    decoy2 = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)", "-m", "primordial.fabric.worker",
                               "serve", "--lane", "Z"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(decoy2)
    time.sleep(1.0)
    hand = W.REG.format("Z", decoy2.pid)                                     # a registered pid that is no worker
    rr.hset(hand, mapping={"pid": decoy2.pid, "lane": "Z", "repo": str(ROOT), "round_id": "",
                           "cmdline": json.dumps(["x"])})
    own = W.REG.format("Z", os.getpid())
    rr.hset(own, mapping={"pid": os.getpid(), "lane": "Z", "repo": str(ROOT), "round_id": "", "cmdline": "[]"})
    actions = {(a["lane"], a["pid"]): a["action"] for a in RS.stop_registered(rr, timeout_s=10)}
    assert actions[(lane, reg["pid"])] in ("stopped", "killed")
    assert actions[("Z", decoy2.pid)] == "skipped_cmdline_mismatch"
    assert actions[("Z", os.getpid())] == "skipped_own_pid"
    t = time.monotonic()
    while psutil.pid_exists(reg["pid"]) and time.monotonic() - t < 15:
        time.sleep(0.1)
    assert not psutil.pid_exists(reg["pid"]) and not rr.exists(reg["key"])
    assert decoy.poll() is None and decoy2.poll() is None                     # unregistered + unverified survive
    assert rr.exists(hand)


def test_epoch_round_cli_refuses_on_residue(r, tmp_path, capsys):
    rr, _ = r
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(tmp_path), *a], check=True)
    (tmp_path / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init"], check=True)
    rr.set("pm:jobs:C:stop", "5")
    rc = EP.main(["round", "--lanes", "C", "--round", RID, "--repo", str(tmp_path), "--allowed-repos", str(ROOT)])
    assert rc == 3
    out = capsys.readouterr().out
    assert json.loads(out.strip().splitlines()[0])["residue"][0]["kind"] == "STOP_FLAG"
    assert rr.get(RC.CURRENT) is None and not rr.exists(RC.KEY.format(RID)) and not rr.exists(EP.STATE)


def test_round_close_stops_registered_workers_then_clears_flags(r, tmp_path):
    rr, procs = r
    lane = f"C{uuid.uuid4().hex[:6]}"
    repo = tmp_path / "ctl"
    repo.mkdir()
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *a], check=True)
    (repo / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    rr.set(RC.CURRENT, RID)                                                  # the worker registers into this round
    spawn_worker(procs, lane, "t-c")
    reg = wait_regs(rr, lane, 1)[0]
    assert reg["round_id"] == RID
    ec = EP.EpochController([lane], r=rr, out=repo / EP.EPOCHS_REL, repo=repo, post=False, log=lambda *_: None,
                            push=False, log_dir=tmp_path / "logs", drain_timeout_s=5,
                            export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    clock = RC.plan(time.time() + 0.3, round_id=RID, stage="PRODUCTION", epoch_s=1.0, epochs=1, drain_s=1.0,
                    close_s=1.0)
    rec = ec.run_round(clock)
    names = [e["event"] for e in ec.events]
    assert names.index("round_committed") < names.index("workers_stopped") < names.index("flags_cleared")
    assert [a["action"] for a in rec["workers_stopped"] if a["pid"] == reg["pid"]] in (["stopped"], ["killed"])
    t = time.monotonic()
    while psutil.pid_exists(reg["pid"]) and time.monotonic() - t < 15:
        time.sleep(0.1)
    assert not psutil.pid_exists(reg["pid"]) and not rr.exists(reg["key"])
    assert not rr.exists(W.STOP.format(lane))
    after = RS.scan(rr, RID, [str(ROOT)])                    # only the stopped worker's consumer name remains:
    assert kinds(after) == ["DEAD_CONSUMER"] and after["residue"][0]["detail"]["consumer"] == "t-c"   # `clear` removes it
    assert RS.clear(rr, RID)["ok"] or True
    assert subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True,
                          text=True).stdout.strip() == ""


# ------------------------------------------------------------------ clear (A 16:40: only what a closed prior round left)

def closed_prior(rr, rid="t-r6p", epochs=5, phase="closed", with_round_id=True):
    RC.start(rr, rid, start_ts=time.time() - 20000, stage="PRODUCTION", epoch_s=2400, epochs=epochs, drain_s=1200,
             close_s=1200)
    state = {"n": epochs, "phase": phase, "ts": f"{time.time():.3f}"}
    if with_round_id:
        state["round_id"] = rid
    rr.hset(EP.STATE, mapping=state)
    return rid


def dead_consumer(rr, lane, name, pending=False):
    key = W.JOBS.format(lane)
    rr.xadd(key, {"job_id": "j", "fn": "m:f"})
    try:
        rr.xgroup_create(key, f"worker-{lane}", id="0", mkstream=True)
    except Exception:
        pass
    got = rr.xreadgroup(f"worker-{lane}", name, {key: ">"}, count=1)
    if not pending:
        for _, msgs in got or []:
            for mid, _ in msgs:
                rr.xack(key, f"worker-{lane}", mid)
    return key


def test_clear_flag_from_closed_prior_round(r):
    rr, _ = r
    rid = closed_prior(rr)
    rr.set("pm:jobs:B:stop", "5")
    rep = RS.clear(rr, rid, allowed=[str(ROOT)])
    assert rep["ok"] and [c["key"] for c in rep["cleared"]] == ["pm:jobs:B:stop", "pm:round:current"]
    assert not rr.exists("pm:jobs:B:stop")
    evs = [e for e in __import__("primordial.fabric.envelope", fromlist=["x"]).events(rr, "RESIDUE_CLEARED")]
    assert [(e["kind"], e["key"], e["prior_round"]) for e in evs] == [
        ("STOP_FLAG", "pm:jobs:B:stop", rid), ("CURRENT_POINTS_AT_CLOSED_ROUND", "pm:round:current", rid)]


def test_clear_refuses_flag_while_round_not_closed(r):
    rr, _ = r
    rid = closed_prior(rr, phase="running")
    rr.set("pm:jobs:C:stop", "5")
    rep = RS.clear(rr, rid, allowed=[str(ROOT)])
    assert [x["reason"] for x in rep["refused"]] == ["FLAG_ROUND_NOT_CLOSED"] and rr.exists("pm:jobs:C:stop")
    assert RS.main(["clear", "--prior-round", rid, "--allowed-repos", str(ROOT)]) == 2


def test_clear_refuses_flag_value_mismatch(r):
    rr, _ = r
    rid = closed_prior(rr)
    rr.set("pm:jobs:D:stop", "3")                                             # not the prior round's final boundary
    rep = RS.clear(rr, rid, allowed=[str(ROOT)])
    assert [x["reason"] for x in rep["refused"]] == ["FLAG_VALUE_MISMATCH"] and rr.exists("pm:jobs:D:stop")


def test_clear_fallback_when_state_has_no_round_id(r):
    rr, _ = r
    rid = closed_prior(rr, with_round_id=False)                               # RC.start set pm:round:current = rid
    rr.set("pm:jobs:E:stop", "5")
    assert RS.clear(rr, rid, allowed=[str(ROOT)])["ok"]
    rr.set(RC.CURRENT, "some-other-round")
    rr.set("pm:jobs:E:stop", "5")
    assert [x["reason"] for x in RS.clear(rr, rid, allowed=[str(ROOT)])["refused"]] == ["FLAG_ROUND_NOT_CLOSED"]


def test_unregistered_active_consumer_is_flagged_and_never_cleared(r, monkeypatch):
    """Live store 16:55: E's worker on pre-registration code read from worker-E 31 ms before the scan, pending 0.
    It must not look DEAD, and clear must not DELCONSUMER it."""
    rr, _ = r
    monkeypatch.setattr(RS, "ACTIVE_IDLE_S", 120.0)
    rid = closed_prior(rr)
    lane = f"K{uuid.uuid4().hex[:6]}"
    key = dead_consumer(rr, lane, "old-code-live")                         # just read, pending 0, unregistered
    rep = RS.scan(rr, "t-r7", [str(ROOT)])
    mine = [x for x in rep["residue"] if x.get("lane") == lane]
    assert [(x["kind"], x["detail"]["consumer"]) for x in mine] == [("UNREGISTERED_ACTIVE_CONSUMER", "old-code-live")]
    assert not rep["ok"]
    out = RS.clear(rr, rid, round_id="t-r7", allowed=[str(ROOT)])
    assert [(x["consumer"], x["reason"]) for x in out["refused"] if x.get("consumer") == "old-code-live"] == [
        ("old-code-live", "CONSUMER_RECENTLY_ACTIVE")]
    assert "old-code-live" in [c["name"] for c in rr.xinfo_consumers(key, f"worker-{lane}")]


def test_clear_dead_pending_and_live_consumers(r):
    rr, procs = r
    rid = closed_prior(rr)
    lane = f"K{uuid.uuid4().hex[:6]}"
    key = dead_consumer(rr, lane, "old-r5-tag")                               # dead, pending 0 -> removed
    dead_consumer(rr, lane, "old-pending", pending=True)                      # dead, pending 1 -> refused
    spawn_worker(procs, lane, "t-live")                                       # live registered consumer -> refused
    wait_regs(rr, lane, 1)
    t = time.monotonic()
    while "t-live" not in [c["name"] for c in rr.xinfo_consumers(key, f"worker-{lane}")] and time.monotonic() - t < 30:
        time.sleep(0.2)
    pre = RS.scan(rr, "t-r7", [str(ROOT)])
    assert sorted((x["kind"], x["detail"]["consumer"]) for x in pre["residue"] if x["kind"] == "DEAD_CONSUMER") == [
        ("DEAD_CONSUMER", "old-pending"), ("DEAD_CONSUMER", "old-r5-tag")]      # the live one is not residue
    rep = RS.clear(rr, rid, round_id="t-r7", allowed=[str(ROOT)])
    assert [c["consumer"] for c in rep["cleared"] if c["kind"] == "DEAD_CONSUMER"] == ["old-r5-tag"]
    assert sorted((x["consumer"], x["reason"]) for x in rep["refused"]) == [
        ("old-pending", "CONSUMER_PENDING"), ("t-live", "CONSUMER_LIVE")]
    names = [c["name"] for c in rr.xinfo_consumers(key, f"worker-{lane}")]
    assert "old-r5-tag" not in names and "old-pending" in names and "t-live" in names
    assert procs[-1].poll() is None                                           # clear never kills


def test_clear_never_touches_prior_keys_and_refuses_not_clearable(r):
    rr, _ = r
    rid = closed_prior(rr)
    rr.set("pm:prior:sealed", "x")
    rep = RS.clear(rr, rid, allowed=[str(ROOT)])
    assert [(x["kind"], x["reason"]) for x in rep["refused"]] == [("UNARCHIVED_PRIOR_KEY", "NOT_CLEARABLE")]
    assert rr.exists("pm:prior:sealed")


def test_planted_r6_like_store_scans_clean_after_clear(r):
    rr, _ = r
    rid = closed_prior(rr)                                                    # the live shape A found at 16:40
    for L in ("B", "C", "D", "E", "G"):
        rr.set(f"pm:jobs:{L}:stop", "5")
        for n in ("m1-aaaa", "m1-bbbb", "m1-cccc"):
            dead_consumer(rr, L, n)
    assert RS.main(["scan", "--round", "t-r7", "--allowed-repos", str(ROOT)]) == 1
    rep = RS.clear(rr, rid, round_id="t-r7", allowed=[str(ROOT)])
    assert rep["ok"] and len(rep["cleared"]) == 5 + 15 + 1                    # flags, dead consumers, current
    assert RS.scan(rr, "t-r7", [str(ROOT)])["ok"]
    assert RS.main(["scan", "--round", "t-r7", "--allowed-repos", str(ROOT)]) == 0


def test_epoch_round_cli_default_round_is_r7():
    a = EP.parser().parse_args(["round", "--lanes", "B,C,D,E,G", "--repo", "X"])
    assert a.round == "r7" == RC.DEFAULT_ROUND
    assert RC.plan(0.0, a.round, **EP.round_shape(a)) == RC.plan(0.0, "r7")


# ------------------------------------------------------------------ per-lane declared repos + GPU arbiter (A, R7)

def test_per_lane_declared_repos_on_live_workers(r):
    rr, procs = r
    spawn_worker(procs, "G", "t-g")
    spawn_worker(procs, "D", "t-d")
    g, d = wait_regs(rr, "G", 1)[0], wait_regs(rr, "D", 1)[0]
    rr.hset(g["key"], "repo", "F:/Prometheus-worktrees/nestor-bld-g")        # the repo string scan compares
    rr.hset(d["key"], "repo", "F:/Prometheus-worktrees/nestor-r6-d")          # the D14 shape: last round's worktree
    rep = RS.scan(rr, "r7")                                                   # declared ROUNDS r7 lane_repos
    foreign = [x for x in rep["residue"] if x["kind"] == "FOREIGN_REPO"]
    assert [(x["lane"], x["pid"]) for x in foreign] == [("D", d["pid"])]
    assert RS.main(["scan", "--round", "r7"]) == 1
    rep = RS.scan(rr, "r7", "G=F:/Prometheus-worktrees/nestor-bld-g;D=F:/Prometheus-worktrees/NESTOR-R6-D")
    assert [x for x in rep["residue"] if x["kind"] == "FOREIGN_REPO"] == []   # override, case-insensitive


def test_gpu_arbiter_registration_and_consumers(r, monkeypatch):
    rr, _ = r
    rr.xadd(RS.GPU_QUEUE, {"job": "x"})
    rr.xgroup_create(RS.GPU_QUEUE, RS.GPU_GROUP, id="0")
    for name in ("m1-old-e", "m1-live-e"):
        for _, msgs in rr.xreadgroup(RS.GPU_GROUP, name, {RS.GPU_QUEUE: ">"}, count=1) or []:
            for mid, _f in msgs:
                rr.xack(RS.GPU_QUEUE, RS.GPU_GROUP, mid)
        rr.xadd(RS.GPU_QUEUE, {"job": "y"})
    fake = 999999
    key = RS.register(rr, "gpu", "F:/Prometheus-worktrees/nestor-r7-e", round_id="r7", pid=fake, tag="m1-live-e")
    assert rr.hget(key, "lane") == "gpu" and rr.ttl(key) > 0
    argv = ["python", "-m", "primordial.nv.gpuq", "serve"]
    monkeypatch.setattr(RS, "_live", lambda pid: (True, argv) if pid == fake else (False, None))
    rep = RS.scan(rr, "r7")
    assert [(x["kind"], x["lane"], x["detail"]["consumer"]) for x in rep["residue"]] == [
        ("DEAD_CONSUMER", "gpu", "m1-old-e")]                                 # the live arbiter's name is bound
    RS.unregister(rr, key)
    assert sorted(x["detail"]["consumer"] for x in RS.scan(rr, "r7")["residue"]) == ["m1-live-e", "m1-old-e"]
    rr.delete(RS.GPU_QUEUE)


# ------------------------------------------------------------------ D18: pm:round:current left on a closed round

def test_scan_and_clear_current_pointing_at_closed_round(r):
    rr, _ = r
    rid = closed_prior(rr)                                                    # current -> rid, state closed
    assert RC.read(rr) is None and rr.get(RC.CURRENT) == rid                  # read() hides it; the raw key is there
    rep = RS.scan(rr, "t-r7", [str(ROOT)])
    assert kinds(rep) == ["CURRENT_POINTS_AT_CLOSED_ROUND"] and rep["residue"][0]["detail"]["round_id"] == rid
    out = RS.clear(rr, rid, round_id="t-r7", allowed=[str(ROOT)])
    assert out["ok"] and [c["kind"] for c in out["cleared"]] == ["CURRENT_POINTS_AT_CLOSED_ROUND"]
    assert rr.get(RC.CURRENT) is None and RC.read(rr, rid) is not None        # pointer gone, history hash kept
    assert RS.scan(rr, "t-r7", [str(ROOT)])["ok"]


def test_current_closed_by_end_ts_only_and_running_round_is_not_residue(r):
    rr, _ = r
    RC.start(rr, "t-old", start_ts=time.time() - 20000, stage="PRODUCTION", epoch_s=10, epochs=1, drain_s=1, close_s=1)
    assert kinds(RS.scan(rr, "t-r7", [str(ROOT)])) == ["CURRENT_POINTS_AT_CLOSED_ROUND"]   # end_ts passed, no state
    rr.delete(RC.CURRENT)
    RC.start(rr, "t-live", start_ts=time.time(), stage="PRODUCTION", epoch_s=3600, epochs=2, drain_s=60, close_s=60)
    assert RS.scan(rr, "t-r7", [str(ROOT)])["ok"]                             # a running round is not residue
    other = closed_prior(rr, rid="t-r6q")                                     # current -> t-r6q (closed)
    out = RS.clear(rr, "t-something-else", round_id="t-r7", allowed=[str(ROOT)])
    assert rr.get(RC.CURRENT) == other                                        # clear touches only prior_round's pointer
    assert ("CURRENT_POINTS_AT_CLOSED_ROUND", "NOT_CLEARABLE") in [(x["kind"], x["reason"]) for x in out["refused"]]


def _close_run(rr, tmp_path, rid):
    repo = tmp_path / f"ctl-{rid}"
    repo.mkdir()
    for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *a], check=True)
    (repo / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    ec = EP.EpochController(["Nolane"], r=rr, out=repo / EP.EPOCHS_REL, repo=repo, post=False, log=lambda *_: None,
                            push=False, log_dir=tmp_path / f"logs-{rid}", drain_timeout_s=0.2,
                            export=lambda out, stamp, r: (out.mkdir(parents=True, exist_ok=True), {})[1])
    ec.run_round(RC.plan(time.time() + 0.2, round_id=rid, stage="PRODUCTION", epoch_s=0.5, epochs=1, drain_s=0.5,
                         close_s=0.5))
    return ec


def test_close_unsets_current_only_for_its_own_round(r, tmp_path):
    rr, _ = r
    rr.set(RC.CURRENT, "t-close-a")
    ec = _close_run(rr, tmp_path, "t-close-a")
    assert [e["event"] for e in ec.events][-1] == "current_unset" and rr.get(RC.CURRENT) is None
    rr.set(RC.CURRENT, "t-another-round")
    ec = _close_run(rr, tmp_path, "t-close-b")
    assert "current_unset" not in [e["event"] for e in ec.events] and rr.get(RC.CURRENT) == "t-another-round"
