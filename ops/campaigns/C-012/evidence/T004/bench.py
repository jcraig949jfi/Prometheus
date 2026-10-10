"""C-012-T004 fleet benchmark harness (preregistration: ops/campaigns/C-012/prereg/T004_PREREG.md; analysis:
bench_metrics.py, frozen with it). Runs on M2.

Each POINT runs in its own THROWAWAY schemas (Fabric fabric_b_<tag>, Moonshot moonshot_b_<tag>) on the canonical
cluster -- the canonical Fabric queue is never used, so no other seat's task can be claimed and no benchmark task
pollutes it -- while the canonical Fabric lease rows (ubu001:cpu4, ubu002:cpu4, spectrex5:cpu12) announce the
resource use. Frozen Fabric v0.2 workers on the nodes (FABRIC_SCHEMA set for them), the approved executor at
APPROVED, the coordinator (dispatch + publish) on M2.

    python bench.py calibrate --out F
    python bench.py point --arm N --D 30 --wpn 4 --wall-s 360 --iters I --run-id R --out DIR [--smoke]
    python bench.py point --arm R --D 30 --wpn 4 --wall-s 600 --iters I --run-id R --out DIR --kills 3
    python bench.py point --arm S --K 16 --wall-s 120 --run-id R --out DIR
    python bench.py report --run-dir DIR
"""
import argparse
import base64
import importlib.util
import json
import os
import secrets
import shlex
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))

from moonshot.epoch import canonical as C  # noqa: E402
from moonshot.epoch import model  # noqa: E402

_s = importlib.util.spec_from_file_location("bench_metrics", HERE / "bench_metrics.py")
BM = importlib.util.module_from_spec(_s)
_s.loader.exec_module(BM)

APPROVED = "55c74f7cb456b5417306136ebd4c4b1d4648a035"     # the executor qualified in T003 (moonshot.epoch.fabric_exec)
NODES = {"ubu001": "jcraig@192.168.1.218", "ubu002": "jcraig@192.168.1.219"}
RUNTIME_DIR, WORK_ROOT = "~/fabric-runtime-moonshot", "~/fabric-work-moonshot"
BASE_DIR = WORK_ROOT + "/worker.{host}.moonshot/bases/" + APPROVED[:12]
PRINCIPAL, CAMPAIGN, ACTOR = "Themis", "C-012-T004", "Themis[m2-0e9b1ed2]"
CAPS = ["fabric.runtime==0.2", "moonshot.epoch.v1", "python.stdlib"]
FILES = {"manifest": "MANIFEST.json", "spec": "SPEC.json", "trace": "TRACE", "checkpoint": "CHECKPOINT"}
# One publisher connection, reused (a steady-state publisher daemon). The coordinator's parallel mode opens a
# connection per publication so that RACES meet in the database (T003); it is not what this benchmark measures.
PUBLISH_PARALLEL = 1


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(*a):
    print("[{}]".format(now()), *a, flush=True)


def ssh(host, cmd, timeout=120, check=True):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", NODES[host], cmd],
                       capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("ssh {} ({}): {}\n{}".format(host, r.returncode, cmd, r.stderr[-800:]))
    return r.stdout


# ------------------------------------------------------------------------------------------------ calibration
CAL = ("import time,statistics; from moonshot.epoch import model; rs=[]\n"
       "for i in range(3):\n"
       "  g=model.make_genesis('cal',epochs=1,params={'work_iterations':N,'trace_every':N//16,'checkpoint_bytes':4096},"
       "approved_code_sha='c0de'*10,initial_checkpoint=b'x'*4096)\n"
       "  t=time.perf_counter(); model.execute(g.obj,1,g.initial_checkpoint); rs.append(N/(time.perf_counter()-t))\n"
       "print(statistics.median(rs))\n")


def calibrate():
    """synthetic.v1 iterations per second, single process, per node (median of 3), from the approved checkout."""
    n = 2000000
    out = {}
    for h in NODES:
        code = CAL.replace("N", str(n))
        cmd = "cd {} && python3 -c {}".format(BASE_DIR.format(host=h), shlex.quote(code))
        out[h] = float(ssh(h, cmd, timeout=300).strip().splitlines()[-1])
    rate = BM.median(list(out.values()))
    return {"at": now(), "iterations_per_s": out, "median_rate": rate,
            "iters_for_D": {str(d): int(round(d * rate)) for d in (60, 30, 10, 3, 1)}}


# ------------------------------------------------------------------------------------------------ workers
def start_node_workers(fschema, wpn, tag):
    pids = {}
    for h in NODES:
        pids[h] = []
        for i in range(wpn):
            logf = "{}/bench_{}_{}_{}.log".format(WORK_ROOT, tag, h, i)
            cmd = ("mkdir -p {w}; cd {r} || exit 1; FABRIC_SCHEMA={fs} EW_DB_HOST=192.168.1.202 nohup python3 -m fabric "
                   "worker --agent worker.{h}.moonshot --caps moonshot.epoch.v1 --executors script --work-root {w} "
                   "--poll-s 1 --idle-exit-s 900 >> {lf} 2>&1 < /dev/null & echo $!").format(
                w=WORK_ROOT, r=RUNTIME_DIR, fs=fschema, h=h, lf=logf)
            pids[h].append(int(ssh(h, cmd).strip()))
    log("node workers", pids)
    return pids


def stop_node_workers(pids, sig="TERM"):
    for h, ps in pids.items():
        if ps:
            ssh(h, "kill -{} {} 2>/dev/null; true".format(sig, " ".join(map(str, ps))))


def node_errors(tag):
    """Store errors the workers logged (Fabric prints {"store_error": ...} lines)."""
    n = 0
    for h in NODES:
        out = ssh(h, "cat {}/bench_{}_{}_*.log 2>/dev/null | grep -c store_error || true".format(WORK_ROOT, tag, h))
        n += int((out.strip() or "0").splitlines()[-1])
    return n


class SimWorkers:
    """Arm S: K in-process workers on M2 doing exactly the store calls a Fabric worker does (claim, 8 artifacts,
    finish) around an in-process epoch, so the measured cost is coordination, not process start-up."""

    def __init__(self, k):
        self.k, self.stop, self.threads, self.errors = k, threading.Event(), [], []

    def _run(self, i):
        from fabric import store as S
        fab = S.connect()
        agent, inst = "worker.m2sim.moonshot", "m2sim-{}-{}".format(i, secrets.token_hex(2))
        S.register_instance(fab, agent, "worker", inst, "spectrex5", capabilities=CAPS, executors=["script"],
                            capacity=1, description="T004 arm S simulated worker")
        while not self.stop.is_set():
            try:
                got = S.claim(fab, agent, inst, "spectrex5", CAPS, ["script"], ttl_s=90)
                if got is None:
                    time.sleep(0.05)
                    continue
                task, aid = got["task"], got["attempt_id"]
                a = task["params"]["args"]
                arg = lambda f: a[a.index(f) + 1]  # noqa: E731
                gobj = C.parse_canonical(base64.b64decode(arg("--genesis-b64")))
                r = model.execute(gobj, int(arg("--epoch-index")), base64.b64decode(arg("--input-b64")))
                line = json.dumps({"chain_id": r.chain_id, "epoch_index": r.epoch_index, "work_id": r.work_id,
                                   "epoch_digest": r.epoch_digest, "fault": None, "simulated": True}).encode()
                receipt = {"host": "spectrex5", "agent": agent, "instance": inst, "base_sha": task["base_sha"],
                           "worktree_head": task["base_sha"], "simulated": True}
                tid = task["task_id"]
                S.add_artifact(fab, tid, aid, "final_text.md", "final_text", b"", actor=agent)
                S.add_artifact(fab, tid, aid, "stdout", "stdout", line, actor=agent)
                S.add_artifact(fab, tid, aid, "stderr", "stderr", b"", actor=agent)
                S.add_artifact(fab, tid, aid, "env_receipt.json", "env_receipt", json.dumps(receipt).encode(),
                               media_type="application/json", actor=agent)
                for key, name in sorted(FILES.items(), key=lambda kv: kv[1]):
                    S.add_artifact(fab, tid, aid, name, "file", r.files()[key], media_type="application/octet-stream",
                                   actor=agent)
                S.finish_attempt(fab, aid, "succeeded", agent, exit_code=0, env_receipt=receipt)
            except Exception as e:                    # recorded; the point's db_errors bound sees it
                self.errors.append(repr(e)[:300])
                time.sleep(0.2)
        fab.close()

    def start(self):
        for i in range(self.k):
            t = threading.Thread(target=self._run, args=(i,), daemon=True)
            t.start()
            self.threads.append(t)

    def join(self):
        self.stop.set()
        for t in self.threads:
            t.join(60)


# ------------------------------------------------------------------------------------------------ one point
def run_point(arm, *, D, wpn, K, wall_s, iters, run_id, out_dir, kills=0, smoke=False):
    from fabric import store as S
    from moonshot.nf import coordinator as Kmod
    from moonshot.nf import pg
    W = wpn * len(NODES) if arm in ("N", "R") else K
    label = "{}_D{}_W{}".format(arm, D, W)
    tag = "{}_{}_{}".format(run_id.lower(), label.lower(), secrets.token_hex(2))
    fs, ms = "fabric_b_" + tag, "moonshot_b_" + tag
    os.environ["FABRIC_SCHEMA"] = fs
    fab0 = S.connect(require_schema=False)
    S.init_schema(fab0)
    fab0.close()
    admin = pg.connect()
    pg.init_schema(admin, ms)
    co = Kmod.Coordinator(ms, principal=PRINCIPAL, campaign=CAMPAIGN, actor=ACTOR)
    rec = {"arm": arm, "label": label, "D": D, "W": W, "wpn": wpn, "K": K, "wall_s": wall_s, "iters": iters,
           "fabric_schema": fs, "moonshot_schema": ms, "approved_code_sha": APPROVED, "smoke": smoke,
           "started_at": now(), "kills": []}
    params = {"work_iterations": max(1, iters), "trace_every": max(1, iters // 16), "checkpoint_bytes": 4096}
    chains = []
    for c in range(2 * W):
        cid = "B{}-{}".format(label.replace("_", ""), c)
        g = model.make_genesis(cid, epochs=100000, params=params, approved_code_sha=APPROVED,
                               initial_checkpoint=("bench " + cid).encode())
        co.create_chain(g, namespace="bench")
        chains.append(cid)
    pids, sim, loop_errors = {}, None, []
    if arm in ("N", "R"):                         # prereg s8 stop rule: no unrelated load on the nodes
        rec["node_load_before"] = {h: ssh(h, "uptime; ps -eo pcpu,comm --sort=-pcpu | head -6").strip().splitlines()
                                   for h in NODES}
    try:
        if arm in ("N", "R"):
            pids = start_node_workers(fs, wpn, tag)
        else:
            sim = SimWorkers(K)
            sim.start()
        retry = {c: 0 for c in chains}
        t0 = time.time()
        for c in chains:
            co.dispatch(c, wall_s=max(600, 4 * D + 120))
        kill_at = [t0 + wall_s * (i + 1) / (kills + 1) for i in range(kills)]
        while time.time() - t0 < wall_s:
            if kill_at and time.time() >= kill_at[0]:
                kill_at.pop(0)
                rec["kills"].append(kill_one(S, pids))
            try:
                for r in co.publish_ready(parallel=PUBLISH_PARALLEL):
                    cid = r["chain_id"]
                    if co.reader.head(cid)["state"] == "OPEN":
                        tagx = ""
                        if r["outcome"] != "PUBLISHED":
                            retry[cid] += 1
                            tagx = "-retry{}".format(retry[cid])
                        co.dispatch(cid, wall_s=max(600, 4 * D + 120), tag=tagx)
            except Exception as e:
                loop_errors.append(repr(e)[:300])
            time.sleep(0.2)
        t_wall = time.time() - t0
        drain_deadline = time.time() + 3 * max(D, 1) + 180      # in-flight attempts finish and are published
        while time.time() < drain_deadline:
            try:
                co.publish_ready(parallel=PUBLISH_PARALLEL)
            except Exception as e:
                loop_errors.append(repr(e)[:300])
            busy = [t for t in S.list_tasks(_fab(S), principal=PRINCIPAL, limit=100000)
                    if t["state"] in ("submitted", "working")]
            if not busy:
                break
            time.sleep(0.5)
    finally:
        if pids:
            stop_node_workers(pids)
        if sim:
            sim.join()
    rec["ended_at"] = now()
    rec["drain_left_busy"] = len([t for t in S.list_tasks(_fab(S), principal=PRINCIPAL, limit=100000)
                                  if t["state"] in ("submitted", "working")])
    rows = collect_rows(fs, ms)
    published = sum(1 for r in rows if r["outcome"] == "PUBLISHED")
    db_bytes = schema_bytes(admin, (fs, ms))
    errors = len(loop_errors) + (len(sim.errors) if sim else 0) + (node_errors(tag) if pids else 0)
    if rec["kills"]:
        ab = sorted([r for r in rows if r["status"] == "abandoned"], key=lambda r: r["started"])
        ks = sorted([k for k in rec["kills"] if "killed_at_db_epoch" in k], key=lambda k: k["killed_at_db_epoch"])
        rec["recovery"] = []
        for k, r in zip(ks, ab):
            ok = [x for x in rows if x["task_id"] == r["task_id"] and x["outcome"] == "PUBLISHED"]
            rec["recovery"].append({"task_id": r["task_id"], "abandoned_attempt": r["attempt_id"],
                                    "recovered_s": (ok[0]["classified"] - k["killed_at_db_epoch"]) if ok else None})
        rec["abandoned_attempts"] = len(ab)
    rec["validation"] = validate_point(co, chains)
    rec["metrics"] = BM.point_metrics(rows, wall_s=t_wall, published=published, db_bytes=db_bytes,
                                      rate_limit_or_db_errors=errors)
    rec["verdict"] = BM.verdict(rec["metrics"])
    rec["loop_errors"] = loop_errors[:20] + ((sim.errors[:20]) if sim else [])
    out = Path(out_dir) / label
    out.mkdir(parents=True, exist_ok=True)
    (out / "rows.json").write_text(json.dumps(rows, default=str) + "\n", encoding="utf-8", newline="\n")
    (out / "point.json").write_text(json.dumps(rec, indent=1, default=str, sort_keys=True) + "\n", encoding="utf-8",
                                    newline="\n")
    co.close()
    drop(admin, fs, ms)
    admin.close()
    log(label, rec["verdict"], {k: rec["metrics"][k] for k in ("published", "throughput_per_s",
                                                              "M1_coordination_wall_fraction",
                                                              "M3_p95_gap_over_median_execute", "M4_abandonment_rate")})
    return rec


_FAB = {}


def _fab(S):
    if "c" not in _FAB or _FAB["c"].closed:
        _FAB["c"] = S.connect()
    return _FAB["c"]


def kill_one(S, pids):
    """Arm R: SIGKILL one ubu001 worker that is executing; Fabric must reap and retry its attempt."""
    fab = _fab(S)
    t0 = time.time()
    while time.time() - t0 < 120:
        running = [a for t in S.list_tasks(fab, principal=PRINCIPAL, state="working", limit=1000)
                   for a in S.get_task(fab, t["task_id"])["attempts"] if a["status"] == "running" and a["host"] == "ubu001"]
        if running:
            break
        time.sleep(0.5)
    else:
        return {"skipped": "no running attempt on ubu001 within 120 s"}
    out = ssh("ubu001", "pgrep -f '[f]abric worker --agent worker.ubu001.moonshot' | head -50")
    alive = [int(p) for p in out.split()]
    victim = next((p for p in pids["ubu001"] if p in alive), None)
    # which process runs `att`: the instance names the host and a random suffix, not the pid -> kill the worker
    # whose child is executing (the executor's parent); fall back to any live one
    owner = ssh("ubu001", "for p in {}; do pgrep -P $p -f moonshot.epoch.fabric_exec >/dev/null && echo $p; done; true"
                .format(" ".join(map(str, alive)))).split()
    victim = int(owner[0]) if owner else victim
    cur = fab.cursor()
    cur.execute("SELECT extract(epoch FROM now())")
    killed_db = float(cur.fetchone()[0])
    fab.commit()
    ssh("ubu001", "kill -KILL {}".format(victim))
    pids["ubu001"] = [p for p in pids["ubu001"] if p != victim]
    return {"victim_pid": victim, "victim_was_executing": bool(owner), "killed_at_db_epoch": killed_db,
            "killed_at": now()}


def collect_rows(fs, ms):
    from moonshot.nf import pg
    c = pg.connect()
    cur = c.cursor()
    cur.execute("""SELECT a.task_id, a.attempt_id, a.instance, a.host, a.status, extract(epoch FROM t.created_at),
                          extract(epoch FROM a.started_at), extract(epoch FROM a.ended_at),
                          (SELECT extract(epoch FROM min(x.created_at)) FROM {fs}.artifacts x WHERE x.attempt_id = a.attempt_id),
                          (SELECT extract(epoch FROM max(x.created_at)) FROM {fs}.artifacts x WHERE x.attempt_id = a.attempt_id),
                          (SELECT coalesce(sum(x.size_bytes), 0) FROM {fs}.artifacts x WHERE x.attempt_id = a.attempt_id),
                          octet_length(t.params::text)
                     FROM {fs}.attempts a JOIN {fs}.tasks t USING (task_id)""".format(fs=fs))
    rows = []
    for r in cur.fetchall():
        rows.append({"task_id": r[0], "attempt_id": r[1], "instance": r[2], "host": r[3], "status": r[4],
                     "created": float(r[5]), "started": float(r[6]) if r[6] is not None else None,
                     "ended": float(r[7]) if r[7] is not None else None,
                     "first_artifact": float(r[8]) if r[8] is not None else None,
                     "last_artifact": float(r[9]) if r[9] is not None else None,
                     "artifact_bytes": int(r[10]), "params_bytes": int(r[11]), "classified": None, "outcome": None})
    cur.execute("SELECT attempt_id, outcome, extract(epoch FROM classified_at) FROM {}.attempts".format(ms))
    cls = {a: (o, float(t)) for a, o, t in cur.fetchall()}
    for r in rows:
        if r["attempt_id"] in cls:
            r["outcome"], r["classified"] = cls[r["attempt_id"]]
    c.rollback()
    c.close()
    return rows


def schema_bytes(conn, schemas):
    cur = conn.cursor()
    cur.execute("SELECT coalesce(sum(pg_total_relation_size(c.oid)), 0) FROM pg_class c JOIN pg_namespace n "
                "ON n.oid = c.relnamespace WHERE n.nspname = ANY(%s) AND c.relkind IN ('r', 'm')", (list(schemas),))
    v = int(cur.fetchone()[0])
    conn.rollback()
    return v


def validate_point(co, chains):
    """Prereg s4: every published epoch byte-verified; every 10th publication (by id) replay-verified, on M2."""
    from moonshot.epoch import model as M
    out = {"byte_verified": 0, "byte_failures": 0, "replayed": 0, "replay_mismatches": 0}
    for cid in chains:
        g = co.reader.genesis(cid)
        for p in co.reader.lineage(cid):
            k = p["epoch_index"]
            files = co.reader.epoch_files(cid, k)
            inp = co.reader.checkpoint_at(cid, k - 1)
            errs = M.verify_epoch(files, C.sha256_hex(inp))
            out["byte_verified"] += 1
            out["byte_failures"] += bool(errs)
            if p["publication_id"] % 10 == 0:
                out["replayed"] += 1
                out["replay_mismatches"] += M.execute(g, k, inp).epoch_digest != p["epoch_digest"]
    return out


def drop(admin, fs, ms):
    from moonshot.nf import pg
    pg.drop_schema(admin, ms)
    cur = admin.cursor()
    cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(fs))
    admin.commit()


# ------------------------------------------------------------------------------------------------ report
def report(run_dir):
    """Prereg s6: verdict per Arm N point, T*, the operating point, the correctness gate, B7, scaling."""
    pts = []
    for f in sorted(Path(run_dir).glob("*/point.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        if p.get("smoke"):
            continue
        rows = json.loads((f.parent / "rows.json").read_text(encoding="utf-8"))
        p["disagreements"] = sum(1 for r in rows if r["outcome"] == "DISAGREEMENT")
        pts.append(p)
    sweep = {p["D"]: p["verdict"][0] for p in pts if p["arm"] == "N" and p["W"] == 2 * 4}
    op = [p for p in pts if p["arm"] == "N" and p["D"] == 30 and p["W"] == 8]
    gate = all(p["validation"]["byte_failures"] == 0 and p["validation"]["replay_mismatches"] == 0
               and p["disagreements"] == 0 for p in pts)
    rec = [r for p in pts if p["arm"] == "R" for r in p.get("recovery", [])]
    kills = sum(len(p.get("kills", [])) for p in pts if p["arm"] == "R")
    b7 = bool(rec) and len(rec) == kills and all(r["recovered_s"] is not None and r["recovered_s"] <= 90 + 2 * 30
                                                 for r in rec)
    scaling = {p["W"]: p["metrics"]["throughput_per_s"] for p in pts if p["arm"] == "N" and p["D"] == 30}
    return {"points": [{k: p.get(k) for k in ("label", "verdict", "validation", "disagreements", "recovery")}
                       | {"metrics": p["metrics"]} for p in pts],
            "T_star": BM.envelope(sweep) if sweep else None,
            "operating_point": op[0]["verdict"] if op else None,
            "correctness_gate": "PASS" if gate else "FAIL",
            "B7_recovery": {"holds": b7, "kills": kills, "recovered": rec},
            "scaling_D30_throughput_by_W": scaling,
            "scaling_ratio_W8_over_4xW2": (scaling[8] / (4 * scaling[2])) if (8 in scaling and 2 in scaling
                                                                             and scaling[2]) else None}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("calibrate"); p.add_argument("--out")
    p = sub.add_parser("point")
    p.add_argument("--arm", choices=["N", "R", "S"], required=True); p.add_argument("--D", type=float, default=0)
    p.add_argument("--wpn", type=int, default=0); p.add_argument("--K", type=int, default=0)
    p.add_argument("--wall-s", type=float, required=True); p.add_argument("--iters", type=int, default=1)
    p.add_argument("--run-id", required=True); p.add_argument("--out", required=True)
    p.add_argument("--kills", type=int, default=0); p.add_argument("--smoke", action="store_true")
    p = sub.add_parser("report"); p.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    if a.cmd == "calibrate":
        r = calibrate()
        print(json.dumps(r, indent=1))
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=1) + "\n", encoding="utf-8", newline="\n")
    elif a.cmd == "point":
        d = int(a.D) if float(a.D).is_integer() else a.D
        run_point(a.arm, D=d, wpn=a.wpn, K=a.K, wall_s=a.wall_s, iters=a.iters, run_id=a.run_id, out_dir=a.out,
                  kills=a.kills, smoke=a.smoke)
    else:
        r = report(a.run_dir)
        print(json.dumps(r, indent=1, default=str))
        (Path(a.run_dir) / "REPORT.json").write_text(json.dumps(r, indent=1, default=str) + "\n", encoding="utf-8",
                                                    newline="\n")


if __name__ == "__main__":
    main()
