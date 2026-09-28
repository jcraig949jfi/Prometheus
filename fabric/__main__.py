"""fabric CLI -- what a Claude principal calls from its shell.

  python -m fabric init                                   create the fabric schema (sidecar to comms)
  python -m fabric agents                                 workers/principals, capabilities, liveness
  python -m fabric submit --as Archaeon --cap research.repo_readonly --thread thr-... --base <sha> \\
         --prompt-file q.md [--executor claude|script|synthetic] [--model M] [--wall-s N] [--tool web] \\
         [--resource pilot:cpu8] [--host ubu002] [--target worker.ubu002] [--key K] [--title T] [--wait 600]
  python -m fabric tasks [--state submitted] [--as P] [--thread thr-...]
  python -m fabric show <task>                            state, attempts, artifacts, leases
  python -m fabric events <task>                          the forensic history
  python -m fabric artifacts <task>                       list
  python -m fabric get <artifact> [--out FILE]            content (sha256-verified)
  python -m fabric cancel <task> --as P
  python -m fabric lease acquire|release|renew|status ... one lease convention for the fleet
  python -m fabric reap                                   abandon expired attempts now (workers also do this)
  python -m fabric worker --agent worker.<host> --caps ... [--executors claude script synthetic] [--once]
  python -m fabric gateway [--port 8710]                  the A2A boundary

The store is the canonical Postgres (EW_DB_HOST=192.168.1.202 off M1). If it
is unreachable every command fails closed; nothing falls back to local state.
"""
from __future__ import annotations

import argparse
import json
import re
import os
import sys
import time
from pathlib import Path

from . import store as S


def _j(x):
    print(json.dumps(x, indent=1, default=str))


def _principal(a) -> str:
    p = getattr(a, "as_", None) or os.environ.get("FABRIC_PRINCIPAL")
    if not p:
        sys.exit("say who you are: --as <Seat> (or FABRIC_PRINCIPAL)")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fabric")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init"); sub.add_parser("agents"); sub.add_parser("reap")
    s = sub.add_parser("submit")
    s.add_argument("--as", dest="as_"); s.add_argument("--cap", action="append", default=[])
    s.add_argument("--thread"); s.add_argument("--campaign"); s.add_argument("--experiment"); s.add_argument("--base")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt-file"); g.add_argument("--instruction")
    s.add_argument("--executor", default="claude", choices=S.EXECUTORS)
    s.add_argument("--model"); s.add_argument("--wall-s", type=int); s.add_argument("--tool", action="append", default=[])
    s.add_argument("--script"); s.add_argument("--arg", action="append", default=[])
    s.add_argument("--param", action="append", default=[], help="k=v (JSON value if parseable)")
    s.add_argument("--resource", action="append", default=[]); s.add_argument("--host"); s.add_argument("--target")
    s.add_argument("--priority", type=int, default=0); s.add_argument("--max-attempts", type=int, default=3)
    s.add_argument("--key"); s.add_argument("--title", default=""); s.add_argument("--context")
    s.add_argument("--wait", type=int, default=0, help="poll up to N seconds for a terminal state")
    s.add_argument("--skill", help="a fabric skill (fabric/skills/<name>.md): its brief is prepended and <name> is required")
    s.add_argument("--replicas", type=int, default=1,
                   help="N independent Tasks (each a fresh, disposable Attempt with no access to the others' outputs)")
    t = sub.add_parser("tasks"); t.add_argument("--state"); t.add_argument("--as", dest="as_"); t.add_argument("--thread")
    t.add_argument("--limit", type=int, default=50)
    for name in ("show", "events", "artifacts"):
        x = sub.add_parser(name); x.add_argument("task")
    gt = sub.add_parser("get"); gt.add_argument("artifact"); gt.add_argument("--out")
    c = sub.add_parser("cancel"); c.add_argument("task"); c.add_argument("--as", dest="as_")
    le = sub.add_parser("lease"); le.add_argument("op", choices=["acquire", "release", "renew", "status"])
    le.add_argument("resource", nargs="?"); le.add_argument("--as", dest="as_"); le.add_argument("--purpose", default="")
    le.add_argument("--ttl-s", type=int, default=3600); le.add_argument("--lease"); le.add_argument("--token")
    le.add_argument("--all", action="store_true")
    w = sub.add_parser("worker"); w.add_argument("--agent", help="generic executor name worker.<host>[.<env>]; default worker.<host>")
    w.add_argument("--caps", nargs="*", default=[], help="non-environment capabilities; python.*/pin.* are probed")
    w.add_argument("--probe", action="store_true", help="print the environment probe and exit")
    w.add_argument("--executors", nargs="+", default=["claude", "script", "synthetic"])
    w.add_argument("--work-root", default=os.path.expanduser("~/fabric-work")); w.add_argument("--poll-s", type=float, default=5.0)
    w.add_argument("--ttl-s", type=int, default=90); w.add_argument("--model"); w.add_argument("--once", action="store_true")
    w.add_argument("--max-tasks", type=int); w.add_argument("--idle-exit-s", type=float); w.add_argument("--description", default="")
    gw = sub.add_parser("gateway"); gw.add_argument("--host", default="0.0.0.0"); gw.add_argument("--port", type=int, default=8710)
    a = ap.parse_args(argv)

    if a.cmd == "init":
        c = S.connect(require_schema=False); S.init_schema(c); print("fabric schema ready:", S.schema()); return 0
    if a.cmd == "worker":
        from .worker import Worker, probe_environment
        if a.probe:
            _j(probe_environment()); return 0
        Worker(a.agent, a.caps, a.executors, work_root=Path(a.work_root), poll_s=a.poll_s, ttl_s=a.ttl_s, model=a.model,
               description=a.description).loop(once=a.once, max_tasks=a.max_tasks, idle_exit_s=a.idle_exit_s)
        return 0
    if a.cmd == "gateway":
        from .gateway import serve
        serve(a.host, a.port); return 0

    conn = S.connect()
    if a.cmd == "agents":
        _j(S.agents(conn)); return 0
    if a.cmd == "reap":
        _j(S.reap(conn, actor="cli")); return 0
    if a.cmd == "submit":
        instr = Path(a.prompt_file).read_text() if a.prompt_file else a.instruction
        params = {}
        if a.model: params["model"] = a.model
        if a.wall_s: params["wall_s"] = a.wall_s
        if a.tool: params["tools"] = a.tool
        if a.script: params["script"] = a.script
        if a.arg: params["args"] = a.arg
        for kv in a.param:
            k, v = kv.split("=", 1)
            try:
                params[k] = json.loads(v)
            except ValueError:
                params[k] = v
        caps = list(a.cap)
        if a.skill:
            if not re.fullmatch(r"[a-z0-9]+(\.[a-z0-9_-]+)+", a.skill):
                raise SystemExit("bad skill name")
            sk = Path(__file__).parent / "skills" / (a.skill + ".md")
            if not sk.is_file():
                raise SystemExit("unknown skill {} (no {})".format(a.skill, sk))
            instr = sk.read_text() + "\n\n---------------- THE BRIEF ----------------\n\n" + instr
            caps.append(a.skill)
        n = max(1, a.replicas)
        group = S.new_id("grp") if n > 1 else None
        made = []
        for i in range(n):
            p = dict(params, replica={"group": group, "index": i + 1, "of": n}) if group else params
            made.append(S.submit(conn, _principal(a), instr, a.executor, title=a.title + (" [replica {}/{}]".format(i + 1, n) if group else ""),
                                 required_caps=caps, resources=a.resource, host_affinity=a.host, target_agent=a.target,
                                 thread_id=a.thread, campaign_id=a.campaign, experiment_id=a.experiment, base_sha=a.base,
                                 params=p, priority=a.priority, max_attempts=a.max_attempts,
                                 idempotency_key=(a.key + ("-r{}".format(i + 1) if group else "")) if a.key else None,
                                 context_id=a.context))
        _j(made if group else made[0])
        if a.wait:
            t0 = time.time()
            while time.time() - t0 < a.wait:
                if all(S.get_task(conn, r["task_id"])["state"] in S.TERMINAL for r in made):
                    break
                time.sleep(5)
            for r in made:
                task = S.get_task(conn, r["task_id"])
                _j({"task_id": task["task_id"], "state": task["state"], "attempts": len(task["attempts"]),
                    "artifacts": [(x["artifact_id"], x["name"], x["sha256"][:12], x["size_bytes"]) for x in task["artifacts"]]})
        return 0
    if a.cmd == "tasks":
        _j(S.list_tasks(conn, state=a.state, principal=a.as_, thread_id=a.thread, limit=a.limit)); return 0
    if a.cmd == "show":
        t = S.get_task(conn, a.task)
        for at in t["attempts"]:
            at.pop("env_receipt", None)
        _j(t); return 0
    if a.cmd == "events":
        _j(S.events(conn, a.task)); return 0
    if a.cmd == "artifacts":
        _j(S.get_task(conn, a.task)["artifacts"]); return 0
    if a.cmd == "get":
        r = S.artifact_content(conn, a.artifact)
        if a.out:
            Path(a.out).write_bytes(r["content"]); print("wrote", a.out, r["sha256"])
        else:
            sys.stdout.buffer.write(r["content"])
        return 0
    if a.cmd == "cancel":
        try:
            _j(S.cancel(conn, a.task, _principal(a)))
        except S.NotCancelable as e:
            print("NOT CANCELABLE:", e); return 1
        return 0
    if a.cmd == "lease":
        import socket
        if a.op == "status":
            _j(S.leases(conn, active_only=not a.all)); return 0
        if a.op == "acquire":
            r = S.lease_acquire(conn, a.resource, _principal(a), socket.gethostname(), purpose=a.purpose, ttl_s=a.ttl_s)
            _j(r); return 0 if r["result"] == "ACQUIRED" else 3
        if a.op == "renew":
            ok = S.lease_renew(conn, a.lease, a.token, a.ttl_s); print("RENEWED" if ok else "NOT RENEWED"); return 0 if ok else 1
        if a.op == "release":
            ok = S.lease_release(conn, a.lease, a.token, _principal(a)); print("RELEASED" if ok else "NOT RELEASED"); return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
