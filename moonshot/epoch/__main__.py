"""python -m moonshot.epoch <command>  (campaign C-008)

    work           run one worker until its chains complete or --max-attempts (D3 case 2 kills this process)
    calibrate      synthetic.v1 iterations per second on this host (D4)
    make-chains    the coordinator creates a run's chains (D4)
    bench-worker   one timed D4 worker; ends with a WORKER_SUMMARY on the remote
    validate-all   the validator checks every chain with a prefix (D4)
    report         the preregistered D4 metrics and bounds, as JSON (D4)
"""
import argparse
import json
import sys
import time

from . import bench
from .store import COORDINATOR, LAYOUTS, VALIDATOR, Store
from .worker import Outcome, Worker

_DONE = (Outcome.COMPLETE, Outcome.HALTED, Outcome.REFUSED_UNAPPROVED)
_PROGRESS = (Outcome.PUBLISHED, Outcome.DUPLICATE, Outcome.DISAGREEMENT, Outcome.STALE,
             Outcome.ABANDONED_RECOVERED)


def _store(a, role="worker", actor=None):
    return Store(a.remote, namespace=a.namespace, layout=a.layout, local_dir=a.local_dir, role=role,
                 actor=actor or getattr(a, "worker_id", None) or role)


def _work(a) -> int:
    st = _store(a)
    w = Worker(st, a.worker_id, code_sha=a.code_sha, approved=set(a.approve or []), spool_dir=a.spool_dir,
               leases=not a.no_leases, lease_ttl_s=a.ttl, host_label=a.host_label)
    try:
        for r in w.recover():
            print(json.dumps({"recovered": r.attempt_id, "outcome": r.outcome.value}), flush=True)
        active, attempts = list(a.chain), 0
        while active and attempts < a.max_attempts:
            progressed = False
            for cid in list(active):
                r = w.run_attempt(cid)
                attempts += 1
                print(json.dumps({"chain": cid, "epoch": r.epoch_index, "outcome": r.outcome.value,
                                  "attempt": r.attempt_id}), flush=True)
                if r.outcome in _DONE:
                    active.remove(cid)
                progressed = progressed or r.outcome in _PROGRESS
                if attempts >= a.max_attempts:
                    break
            if active and not progressed:
                time.sleep(a.idle_sleep)
        w.flush_receipts()
    finally:
        st.close()
    return 0


def _common(p):
    p.add_argument("--remote", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--layout", choices=LAYOUTS, required=True)
    p.add_argument("--local-dir", required=True)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m moonshot.epoch", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("work", help="run one worker")
    _common(w)
    w.add_argument("--spool-dir", required=True)
    w.add_argument("--worker-id", required=True)
    w.add_argument("--code-sha", required=True)
    w.add_argument("--approve", action="append", help="an approved code sha (repeatable)")
    w.add_argument("--chain", action="append", required=True)
    w.add_argument("--max-attempts", type=int, default=100000)
    w.add_argument("--no-leases", action="store_true")
    w.add_argument("--ttl", type=int, default=60)
    w.add_argument("--host-label", default=None)
    w.add_argument("--idle-sleep", type=float, default=0.5)

    c = sub.add_parser("calibrate", help="synthetic.v1 iterations per second here")
    c.add_argument("--seconds", type=float, default=3.0)

    m = sub.add_parser("make-chains", help="the coordinator creates a run's chains")
    _common(m)
    m.add_argument("--prefix", required=True)
    m.add_argument("--count", type=int, required=True)
    m.add_argument("--iterations", type=int, required=True)
    m.add_argument("--checkpoint-bytes", type=int, default=4096)
    m.add_argument("--epochs", type=int, default=100000)
    m.add_argument("--approved-code-sha", required=True)

    b = sub.add_parser("bench-worker", help="one timed D4 worker")
    _common(b)
    b.add_argument("--spool-dir", required=True)
    b.add_argument("--worker-id", required=True)
    b.add_argument("--code-sha", required=True)
    b.add_argument("--approve", action="append")
    b.add_argument("--prefix", required=True)
    b.add_argument("--count", type=int, required=True)
    b.add_argument("--start", type=int, default=0)
    b.add_argument("--duration-s", type=float, required=True)
    b.add_argument("--no-leases", action="store_true")
    b.add_argument("--ttl", type=int, default=60)
    b.add_argument("--flush-every", type=int, default=10)
    b.add_argument("--host-label", default=None)

    v = sub.add_parser("validate-all", help="the validator checks every chain with a prefix")
    _common(v)
    v.add_argument("--prefix", required=True)
    v.add_argument("--replay-every", type=int, default=10)

    r = sub.add_parser("report", help="the preregistered D4 metrics and bounds")
    _common(r)
    r.add_argument("--prefix", required=True)
    r.add_argument("--wall-s", type=float, required=True)
    r.add_argument("--repo-bytes", type=int, default=None)
    r.add_argument("--refs", type=int, default=None)

    j = sub.add_parser("join", help="D5: join a namespace from a clean approved checkout and drain its chains")
    j.add_argument("--remote", required=True)
    j.add_argument("--namespace", required=True)
    j.add_argument("--layout", choices=LAYOUTS, required=True)
    j.add_argument("--code-dir", default=".", help="the clean pinned checkout this process runs from")
    j.add_argument("--approval-ref", default="origin/main")
    j.add_argument("--fetch", action="store_true", help="git fetch origin in --code-dir first")
    j.add_argument("--node-id", default=None)
    j.add_argument("--workers", type=int, default=1)
    j.add_argument("--duration-s", type=float, required=True)
    j.add_argument("--data-dir", required=True)
    j.add_argument("--no-leases", action="store_true")
    j.add_argument("--ttl", type=int, default=60)
    j.add_argument("--host-label", default=None)

    a = p.parse_args(argv)
    if a.cmd == "join":
        from . import join as J
        try:
            out = J.join(a.remote, namespace=a.namespace, layout=a.layout, code_dir=a.code_dir,
                         approval_ref=a.approval_ref, node_id=a.node_id, workers=a.workers, duration_s=a.duration_s,
                         data_dir=a.data_dir, leases=not a.no_leases, ttl=a.ttl, host_label=a.host_label,
                         fetch=a.fetch, bind_running_code=True)
        except J.JoinRefused as e:
            print(json.dumps({"refused": str(e)}))
            return 3
        print(json.dumps({"node_id": out["node_id"], "code_sha": out["code_sha"], "chains": out["chains"],
                          "workers": [{k: s[k] for k in ("worker_id", "attempts", "executions", "polls", "flags")}
                                      for s in out["workers"]]}))
        return 0
    if a.cmd == "work":
        return _work(a)
    if a.cmd == "calibrate":
        print(json.dumps(bench.calibrate(a.seconds)))
        return 0
    if a.cmd == "make-chains":
        st = _store(a, COORDINATOR, "coordinator")
        try:
            ids = bench.make_chains(st, a.prefix, a.count, iterations=a.iterations,
                                    checkpoint_bytes=a.checkpoint_bytes, epochs=a.epochs,
                                    approved_code_sha=a.approved_code_sha)
        finally:
            st.close()
        print(json.dumps({"chains": ids}))
        return 0
    if a.cmd == "bench-worker":
        st = _store(a)
        try:
            chains = ["{}{:03d}".format(a.prefix, i) for i in range(a.count)]
            s = bench.bench_worker(st, a.worker_id, chains, code_sha=a.code_sha, approved=set(a.approve or []),
                                   spool_dir=a.spool_dir, leases=not a.no_leases, duration_s=a.duration_s,
                                   lease_ttl_s=a.ttl, flush_every=a.flush_every, start=a.start,
                                   host_label=a.host_label)
        finally:
            st.close()
        print(json.dumps(s))
        return 0
    if a.cmd == "validate-all":
        st = _store(a, VALIDATOR, "validator")
        try:
            print(json.dumps(bench.validate_all(st, a.prefix, a.replay_every)))
        finally:
            st.close()
        return 0
    if a.cmd == "report":
        st = _store(a, "worker", "reporter")
        try:
            print(json.dumps(bench.report(st, a.prefix, wall_s=a.wall_s, repo_bytes=a.repo_bytes, refs=a.refs),
                             indent=1, sort_keys=True))
        finally:
            st.close()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
