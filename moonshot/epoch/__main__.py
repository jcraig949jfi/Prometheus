"""python -m moonshot.epoch <command>  (campaign C-008)

    work      run one worker against a dedicated remote until its chains complete or --max-attempts
              (D3 case 2 kills this process mid-epoch; D4 runs it on the ubu nodes)
"""
import argparse
import json
import sys
import time

from .store import LAYOUTS, Store
from .worker import Outcome, Worker

_DONE = (Outcome.COMPLETE, Outcome.HALTED, Outcome.REFUSED_UNAPPROVED)
_PROGRESS = (Outcome.PUBLISHED, Outcome.DUPLICATE, Outcome.DISAGREEMENT, Outcome.STALE,
             Outcome.ABANDONED_RECOVERED)


def _work(a) -> int:
    st = Store(a.remote, namespace=a.namespace, layout=a.layout, local_dir=a.local_dir, actor=a.worker_id)
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m moonshot.epoch", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("work", help="run one worker")
    w.add_argument("--remote", required=True)
    w.add_argument("--namespace", required=True)
    w.add_argument("--layout", choices=LAYOUTS, required=True)
    w.add_argument("--local-dir", required=True)
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
    a = p.parse_args(argv)
    if a.cmd == "work":
        return _work(a)
    return 2


if __name__ == "__main__":
    sys.exit(main())
