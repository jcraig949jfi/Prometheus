"""C-012-T003 two-node demonstration (OP-NF2 s5): Fabric task claim -> approved execution -> immutable evidence
publication -> PostgreSQL chain update -> independent replay -> durable receipt, on ubu001 + ubu002, with racing,
faulty-host, invalid, unapproved, worker-crash, publisher-crash and lost-acknowledgement cases.

Runs on M2. The coordinator (dispatch, publish, validate, resolve, receipt) runs here; the nodes run frozen Fabric v0.2
workers (fabric/FREEZE.md "Node runtime") named worker.<host>.moonshot, caps moonshot.epoch.v1, executor script only.
No git remote is contacted between `stage` and the end of `run`: the approved commit is staged on the nodes first,
and FETCH_HEAD mtimes are recorded before and after as evidence.

    python run_two_node.py stage    --approved-sha SHA [--other-sha SHA]   # deployment, BEFORE the window
    python run_two_node.py preflight --approved-sha SHA --out F
    python run_two_node.py workers  start|stop|status
    python run_two_node.py run      --approved-sha SHA --other-sha SHA --run-id R --out DIR [--scenarios S1,..]
    python run_two_node.py audit    --since ISO --out F
"""
import argparse
import base64
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))

from moonshot.epoch import canonical as C  # noqa: E402
from moonshot.epoch import model  # noqa: E402

NODES = {"ubu001": "jcraig@192.168.1.218", "ubu002": "jcraig@192.168.1.219"}
RUNTIME_SHA = "9c022347e"                  # fabric-v0.2 + DEF-ODY-019, as FREEZE.md's node runtime
RUNTIME_DIR = "~/fabric-runtime-moonshot"
WORK_ROOT = "~/fabric-work-moonshot"
FAULT_DIR = "/var/tmp/moonshot-fault"
SCHEMA = "moonshot_qual"
NAMESPACE = "qual"
PRINCIPAL, CAMPAIGN, ACTOR = "Themis", "C-012", "Themis[m2-0e9b1ed2]"
PARAMS = {"work_iterations": 60, "trace_every": 20, "checkpoint_bytes": 64}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(*a):
    print("[{}]".format(now()), *a, flush=True)


# ------------------------------------------------------------------------------------------------ nodes
def ssh(host, cmd, timeout=120, check=True):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", NODES[host], cmd],
                       capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("ssh {} failed ({}): {}\n{}".format(host, r.returncode, cmd, r.stderr[-800:]))
    return r.stdout


def node_facts(host, approved_sha):
    out = ssh(host, "hostname; uptime; stat -c %Y ~/Prometheus/.git/FETCH_HEAD 2>/dev/null || echo none; "
                    "git -C ~/Prometheus cat-file -e {}^{{commit}} && echo approved_present || echo approved_missing; "
                    "git -C {} rev-parse HEAD 2>/dev/null || echo no_runtime; "
                    "pgrep -af '[f]abric worker' || true".format(approved_sha, RUNTIME_DIR))
    lines = out.strip().splitlines()
    return {"host": lines[0], "uptime": lines[1], "fetch_head_mtime": lines[2], "approved_sha": lines[3],
            "runtime_head": lines[4], "fabric_worker_processes": lines[5:]}


def set_fault(host, chain_id, epochs, mode, **extra):
    spec = [dict({"chain_id": chain_id, "epochs": epochs, "mode": mode}, **extra)]
    body = base64.b64encode(json.dumps(spec).encode()).decode()
    ssh(host, "mkdir -p {d} && echo {b} | base64 -d > {d}/{ns}.json".format(d=FAULT_DIR, b=body, ns=NAMESPACE))
    log("fault on", host, spec)


def clear_fault(host):
    ssh(host, "rm -f {}/{}.json".format(FAULT_DIR, NAMESPACE))
    log("fault cleared on", host)


def worker_cmd(host):
    agent = "worker.{}.moonshot".format(host)
    # `;` not `&&` before the worker: `a && b && c &` would background the whole list as a subshell that keeps the
    # ssh channel open (found 2026-10-10: the start hung until the ssh timeout)
    return ("mkdir -p {w}; cd {r} || exit 1; EW_DB_HOST=192.168.1.202 nohup python3 -m fabric worker --agent {a} "
            "--caps moonshot.epoch.v1 --executors script --work-root {w} --poll-s 2 --idle-exit-s 1800 "
            ">> {w}/{a}.log 2>&1 < /dev/null & echo started $!").format(w=WORK_ROOT, r=RUNTIME_DIR, a=agent)


def workers(op, hosts=None):
    out = {}
    for h in hosts or NODES:
        pat = "[f]abric worker --agent worker.{}.moonshot".format(h)   # [f]: the ssh shell running pgrep/pkill
        # carries this pattern in its own command line; the bracket keeps it from matching (or killing) itself
        if op == "start":
            if ssh(h, "pgrep -f {} || true".format(shlex.quote(pat))).strip():
                out[h] = "already running"
                continue
            out[h] = ssh(h, worker_cmd(h)).strip()
        elif op == "stop":
            out[h] = ssh(h, "pkill -TERM -f {} && echo stopped || echo none".format(shlex.quote(pat))).strip()
        elif op == "kill":
            out[h] = ssh(h, "pkill -KILL -f {} && echo killed || echo none".format(shlex.quote(pat))).strip()
        else:
            out[h] = ssh(h, "pgrep -af {} || echo none".format(shlex.quote(pat))).strip()
    log("workers", op, out)
    return out


# ------------------------------------------------------------------------------------------------ fabric reads
def fabric():
    from fabric import store as S
    return S, S.connect()


def wait_task(S, fab, task_id, *, states=("completed", "failed", "canceled"), timeout=600, poll=1.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        t = S.get_task(fab, task_id)
        if t["state"] in states:
            return t
        time.sleep(poll)
    raise TimeoutError("task {} not in {} after {} s (state {})".format(task_id, states, timeout, t["state"]))


def wait_running_attempt(S, fab, task_id, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        t = S.get_task(fab, task_id)
        run = [a for a in t["attempts"] if a["status"] == "running"]
        if run:
            return run[-1]
        time.sleep(0.5)
    raise TimeoutError("no running attempt for {}".format(task_id))


def timing(t):
    """Claim latency and run time per attempt, from Fabric's own timestamps."""
    out = []
    for a in t["attempts"]:
        st, en = a.get("started_at"), a.get("ended_at")
        out.append({"attempt_id": a["attempt_id"], "host": a.get("host"), "status": a["status"],
                    "claim_latency_s": round((st - t["created_at"]).total_seconds(), 3) if st else None,
                    "run_s": round((en - st).total_seconds(), 3) if (st and en) else None})
    return out


# ------------------------------------------------------------------------------------------------ scenarios
class Run:
    def __init__(self, approved_sha, other_sha, run_id, out_dir):
        from moonshot.nf import coordinator as K
        from moonshot.nf import pg
        self.K, self.pg = K, pg
        self.S, self.fab = fabric()
        admin = pg.connect()
        pg.init_schema(admin, SCHEMA)          # idempotent; the qualification schema persists as evidence
        admin.close()
        self.co = K.Coordinator(SCHEMA, principal=PRINCIPAL, campaign=CAMPAIGN, actor=ACTOR)
        self.approved, self.other, self.run_id = approved_sha, other_sha, run_id
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "receipts").mkdir(exist_ok=True)
        self.record = {"run_id": run_id, "schema": SCHEMA, "namespace": NAMESPACE, "approved_code_sha": approved_sha,
                       "other_sha": other_sha, "started_at": now(), "scenarios": {}}

    def chain(self, tag, epochs):
        cid = "{}-{}".format(self.run_id, tag)
        g = model.make_genesis(cid, epochs=epochs, params=PARAMS, approved_code_sha=self.approved,
                               initial_checkpoint=("moonshot qual " + cid).encode())
        self.co.create_chain(g, namespace=NAMESPACE)
        return cid, g

    def go(self, cid, *, replicas=1, hosts=None, base_sha=None, tag="", parallel=None, timeout=600, **hooks):
        """dispatch -> wait for Fabric -> publish; returns the step record."""
        ts = self.co.dispatch(cid, replicas=replicas, hosts=hosts, base_sha=base_sha, tag=tag)
        tasks = [wait_task(self.S, self.fab, t["task_id"], timeout=timeout) for t in ts]
        res = self.co.publish_ready(parallel=parallel or replicas, **hooks)
        return {"epoch_index": ts[0]["epoch_index"], "generation": ts[0]["generation"],
                "tasks": [{"task_id": t["task_id"], "state": t["state"], "attempts": timing(t)} for t in tasks],
                "published": res}

    def finish(self, cid, sc):
        sc["validation"] = self.co.validate(cid)
        rec = self.co.receipt(cid)
        body = C.canonical_bytes(rec["receipt"])
        (self.out / "receipts" / (cid + ".json")).write_bytes(body)
        sc["receipt_sha256"] = rec["sha256"]
        sc["head"] = rec["receipt"]["head"]
        sc["attempt_outcomes"] = rec["receipt"]["attempt_outcomes"]
        sc["contests"] = rec["receipt"]["contests"]

    def complete(self, cid, sc, **kw):
        while self.co.reader.head(cid)["state"] == "OPEN":
            sc["steps"].append(self.go(cid, **kw))

    # S1: the one-epoch path, then the chain to completion -------------------------------------------------
    def S1(self):
        cid, g = self.chain("S1", 3)
        sc = {"chain_id": cid, "steps": []}
        self.complete(cid, sc)
        self.finish(cid, sc)
        sc["equals_reference_replay"] = [p["epoch_digest"] for p in self.co.reader.lineage(cid)] == \
            [r.epoch_digest for r in model.replay_chain(g, 3)]
        return sc

    # S2: two workers race for every successor with identical results --------------------------------------
    def S2(self):
        cid, g = self.chain("S2", 3)
        sc = {"chain_id": cid, "steps": []}
        self.complete(cid, sc, replicas=2, hosts=["ubu001", "ubu002"])
        self.finish(cid, sc)
        return sc

    # S3: two workers race with conflicting results (ubu002 is a faulty host for epoch 1) -------------------
    def S3(self):
        cid, g = self.chain("S3", 2)
        sc = {"chain_id": cid, "steps": []}
        set_fault("ubu002", cid, [1], "flip_checkpoint")
        try:
            sc["steps"].append(self.go(cid, replicas=2, hosts=["ubu001", "ubu002"]))
        finally:
            clear_fault("ubu002")
        sc["head_after_race"] = self.co.reader.head(cid)["state"]
        sc["contest_before"] = self.co.reader.open_contest(cid)
        sc["verdict"] = self.co.resolve(cid)
        self.complete(cid, sc)
        self.finish(cid, sc)
        return sc

    # S4: a faulty host publishes; replay validation catches it; the straggler from that lineage is STALE ----
    def S4(self):
        cid, g = self.chain("S4", 3)
        sc = {"chain_id": cid, "steps": []}
        set_fault("ubu002", cid, [1], "flip_checkpoint")
        try:
            sc["steps"].append(self.go(cid, hosts=["ubu002"]))
        finally:
            clear_fault("ubu002")
        set_fault("ubu001", cid, [2], "delay", delay_s=45)
        try:
            straggler = self.co.dispatch(cid, hosts=["ubu001"])[0]
            wait_running_attempt(self.S, self.fab, straggler["task_id"])
        finally:
            clear_fault("ubu001")                 # read at executor start; later runs are not delayed
        sc["validate_epoch_1"] = self.co.validate(cid, epochs=[1])
        sc["contest"] = self.co.reader.open_contest(cid)
        sc["verdict"] = self.co.resolve(cid)
        t = wait_task(self.S, self.fab, straggler["task_id"], timeout=300)
        sc["straggler"] = {"task_id": t["task_id"], "attempts": timing(t), "published": self.co.publish_ready()}
        self.complete(cid, sc)
        self.finish(cid, sc)
        return sc

    # S5: bytes that disagree with their manifest are INVALID; another host then publishes ------------------
    def S5(self):
        cid, g = self.chain("S5", 1)
        sc = {"chain_id": cid, "steps": []}
        set_fault("ubu001", cid, [1], "corrupt_trace")
        try:
            sc["steps"].append(self.go(cid, hosts=["ubu001"]))
        finally:
            clear_fault("ubu001")
        sc["steps"].append(self.go(cid, hosts=["ubu002"], tag="-again"))
        self.finish(cid, sc)
        return sc

    # S6: code the chain did not approve runs (Fabric cannot stop that) but is REFUSED_UNAPPROVED ------------
    def S6(self):
        cid, g = self.chain("S6", 1)
        sc = {"chain_id": cid, "steps": []}
        sc["steps"].append(self.go(cid, base_sha=self.other, timeout=900))
        self.complete(cid, sc)
        self.finish(cid, sc)
        return sc

    # S7: the worker is killed while it executes; Fabric reaps the attempt and retries (repeated) ----------
    def S7(self, repeats=3):
        cid, g = self.chain("S7", repeats)
        sc = {"chain_id": cid, "steps": [], "kills": []}
        for k in range(1, repeats + 1):
            set_fault("ubu001", cid, [k], "delay", delay_s=60)
            t = self.co.dispatch(cid, hosts=["ubu001"])[0]
            a = wait_running_attempt(self.S, self.fab, t["task_id"])
            killed_at = now()
            workers("kill", ["ubu001"])
            clear_fault("ubu001")
            kill = {"epoch_index": k, "task_id": t["task_id"], "killed_attempt": a["attempt_id"], "killed_at": killed_at}
            # the dead attempt must be abandoned by Fabric's reaper (ubu002's worker loop) after its TTL
            t0 = time.time()
            while time.time() - t0 < 300:
                st = {x["attempt_id"]: x["status"] for x in self.S.get_task(self.fab, t["task_id"])["attempts"]}
                if st.get(a["attempt_id"]) == "abandoned":
                    break
                time.sleep(2)
            kill["abandoned_after_s"] = round(time.time() - t0, 1)
            workers("start", ["ubu001"])
            done = wait_task(self.S, self.fab, t["task_id"], timeout=600)
            kill["attempts"] = timing(done)
            kill["published"] = self.co.publish_ready()
            sc["kills"].append(kill)
        self.finish(cid, sc)
        return sc

    # S8: the publisher dies mid-transaction / its acknowledgement is lost (repeated) -----------------------
    def S8(self, repeats=3):
        cid, g = self.chain("S8", 2 * repeats)
        sc = {"chain_id": cid, "publisher_kills": [], "lost_acks": []}
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(x for x in (str(REPO), os.environ.get("PYTHONPATH")) if x))
        for _ in range(repeats):
            t = self.co.dispatch(cid)[0]
            done = wait_task(self.S, self.fab, t["task_id"])
            aid = [x for x in done["attempts"] if x["status"] == "succeeded"][0]["attempt_id"]
            child = subprocess.Popen([sys.executable, "-m", "moonshot.nf.coordinator", "publish", "--schema", SCHEMA,
                                      "--only-attempt", aid, "--hold-before-commit-s", "10"], cwd=str(REPO), env=env,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            t0 = time.time()
            while time.time() - t0 < 60 and not self.co.reader.publisher_waiting(SCHEMA):
                time.sleep(0.2)
            held = self.co.reader.publisher_waiting(SCHEMA)
            child.kill()
            child.wait(30)
            time.sleep(1.0)
            before = self.co.reader.attempt(aid)
            res = self.co.publish_ready(only_attempts={aid})
            sc["publisher_kills"].append({"attempt_id": aid, "held_in_transaction": held,
                                          "classified_after_kill": before, "published": res})
            t = self.co.dispatch(cid)[0]
            wait_task(self.S, self.fab, t["task_id"])
            sc["lost_acks"].append({"published": self.co.publish_ready(_lose_acks=1)})
        self.finish(cid, sc)
        return sc

    def run(self, names):
        for n in names:
            log("scenario", n, "start")
            t0 = time.time()
            try:
                sc = getattr(self, n)()
                sc["ok"] = True
            except Exception as e:                # recorded as found; the run continues with the next scenario
                import traceback
                sc = {"ok": False, "error": repr(e), "traceback": traceback.format_exc()[-3000:]}
            sc["seconds"] = round(time.time() - t0, 1)
            self.record["scenarios"][n] = sc
            self.save()
            log("scenario", n, "ok" if sc["ok"] else "FAILED", sc["seconds"], "s")
        self.record["ended_at"] = now()
        self.save()

    def save(self):
        (self.out / "RUN.json").write_text(json.dumps(self.record, indent=1, default=str, sort_keys=True) + "\n",
                                          encoding="utf-8", newline="\n")


# ------------------------------------------------------------------------------------------------ audit
def audit(since):
    """Every attempt by a moonshot worker since `since` must belong to a C-012 Moonshot task of the qual schema."""
    S, fab = fabric()
    cur = fab.cursor()
    s = S.schema()
    cur.execute("SELECT a.attempt_id, a.task_id, a.agent, a.host, a.status, a.started_at, t.principal, t.campaign_id, "
                "t.metadata->'moonshot'->>'schema' FROM {s}.attempts a JOIN {s}.tasks t USING (task_id) "
                "WHERE a.agent LIKE 'worker.%%.moonshot' AND a.started_at >= %s ORDER BY a.started_at".format(s=s),
                (since,))
    rows = cur.fetchall()
    foreign = [r for r in rows if not (r[6] == PRINCIPAL and r[7] == CAMPAIGN and r[8] == SCHEMA)]
    cur.execute("SELECT kind, count(*) FROM {s}.events WHERE at >= %s GROUP BY kind ORDER BY kind".format(s=s), (since,))
    kinds = dict(cur.fetchall())
    cur.execute("SELECT actor, kind, at, detail FROM {s}.events WHERE at >= %s AND actor NOT LIKE 'worker.%%.moonshot%%' "
                "AND actor NOT IN (%s) ORDER BY event_id".format(s=s), (since, PRINCIPAL))
    others = cur.fetchall()
    fab.commit()
    fab.close()
    return {"since": since, "moonshot_worker_attempts": len(rows), "foreign_claims": [list(map(str, r)) for r in foreign],
            "events_by_kind": kinds, "events_by_other_actors": [list(map(str, r)) for r in others]}


def preflight(approved_sha):
    S, fab = fabric()
    cur = fab.cursor()
    s = S.schema()
    cur.execute("SELECT state, count(*) FROM {s}.tasks GROUP BY state".format(s=s))
    states = dict(cur.fetchall())
    cur.execute("SELECT count(*) FROM {s}.attempts WHERE status = 'running'".format(s=s))
    running = cur.fetchone()[0]
    cur.execute("SELECT lease_id, resource, holder, expires_at FROM {s}.leases WHERE released_at IS NULL".format(s=s))
    leases = [list(map(str, r)) for r in cur.fetchall()]
    cur.execute("SELECT agent, instance, status, last_seen_at FROM {s}.agent_instances WHERE status <> 'offline'".format(s=s))
    instances = [list(map(str, r)) for r in cur.fetchall()]
    fab.commit()
    fab.close()
    return {"at": now(), "tasks_by_state": states, "running_attempts": running, "unreleased_leases": leases,
            "non_offline_instances": instances, "nodes": {h: node_facts(h, approved_sha) for h in NODES}}


def stage(approved_sha, other_sha):
    """Deployment, BEFORE the window: the approved (and the deliberately unapproved) commit present in each node's
    canonical clone, the frozen runtime as a detached worktree, the work root. The only step that uses a git remote."""
    out = {}
    for h in NODES:
        cmds = ["for s in {} {}; do git -C ~/Prometheus cat-file -e $s^{{commit}} 2>/dev/null || "
                "git -C ~/Prometheus fetch -q origin; done".format(approved_sha, other_sha or approved_sha),
                "test -d {r} || git -C ~/Prometheus worktree add --detach {r} {sha}".format(r=RUNTIME_DIR, sha=RUNTIME_SHA),
                "mkdir -p {}".format(WORK_ROOT),
                "git -C {} rev-parse HEAD".format(RUNTIME_DIR),
                "git -C ~/Prometheus cat-file -e {}^{{commit}} && echo approved_present".format(approved_sha)]
        out[h] = ssh(h, " && ".join(cmds), timeout=900).strip().splitlines()
    log("staged", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage"); p.add_argument("--approved-sha", required=True); p.add_argument("--other-sha")
    p = sub.add_parser("preflight"); p.add_argument("--approved-sha", required=True); p.add_argument("--out")
    p = sub.add_parser("workers"); p.add_argument("op", choices=["start", "stop", "status", "kill"])
    p.add_argument("--host", action="append")
    p = sub.add_parser("run"); p.add_argument("--approved-sha", required=True); p.add_argument("--other-sha", required=True)
    p.add_argument("--run-id", required=True); p.add_argument("--out", required=True)
    p.add_argument("--scenarios", default="S1,S2,S3,S4,S5,S6,S7,S8")
    p = sub.add_parser("audit"); p.add_argument("--since", required=True); p.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "stage":
        stage(a.approved_sha, a.other_sha)
    elif a.cmd == "preflight":
        r = preflight(a.approved_sha)
        print(json.dumps(r, indent=1, default=str))
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    elif a.cmd == "workers":
        workers(a.op, a.host)
    elif a.cmd == "run":
        Run(a.approved_sha, a.other_sha, a.run_id, a.out).run(a.scenarios.split(","))
    elif a.cmd == "audit":
        r = audit(a.since)
        print(json.dumps(r, indent=1, default=str))
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
