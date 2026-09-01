"""Standalone remote worker for the Serendipity Foundry Engine.

Runs on ANY machine that can reach the Engine. It claims queued work over the
REST API, runs a LOCAL executor callable, heartbeats its lease while it computes,
and commits the result. Workers are disposable: kill one mid-lease (Ctrl-C, power
loss) and the Engine reclaims the work for another worker -- nothing is lost, no
result is fabricated.

    python examples/run_worker.py --token <TOKEN> [--world <WORLD_ID>] \\
        [--base-url URL] [--cafile PATH] [--worker-id NAME] [--follow]

--token is required: a worker acts as an existing client (the one that owns the
worlds whose work it should run). Get a token by registering a client (see
docs/CONNECTING.md) or reuse one you already hold. Omit --world to take work from
ANY world the token owns; pass --world to pin the worker to one world.

--follow keeps the worker alive, polling for new work; without it the worker
drains the queue once and exits.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfclient import EngineClient, RemoteWorker


def executor(kind: str, payload: dict) -> dict:
    """Replace this with your real compute. It receives the work item's `kind`
    and `payload` and returns a JSON-serializable result dict, which the Engine
    stores verbatim as the authoritative outcome of the work item.

    This reference implementation scores a bitstring by its fraction of 1s."""
    bits = str(payload.get("bits", ""))
    score = (sum(1 for b in bits if b == "1") / len(bits)) if bits else 0.0
    return {"kind": kind, "bits": bits, "score": score, "solved": score >= 1.0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="bearer token of the owning client")
    ap.add_argument("--world", default=None, help="pin to one world id (optional)")
    ap.add_argument("--base-url", default="https://192.168.1.202:8811")
    ap.add_argument("--cafile", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config",
        "m1.crt"))
    ap.add_argument("--insecure", action="store_true")
    ap.add_argument("--worker-id", default=f"worker-{os.getpid()}")
    ap.add_argument("--lease", type=float, default=30.0)
    ap.add_argument("--follow", action="store_true",
                    help="keep polling for work instead of draining once")
    args = ap.parse_args()

    c = EngineClient(args.base_url, token=args.token, cafile=args.cafile,
                     insecure=args.insecure)
    print(f"worker {args.worker_id} -> {args.base_url} "
          f"(world={args.world or 'ANY'})  engine={c.version()['runtime']}")
    worker = RemoteWorker(c, args.worker_id, executor, lease_s=args.lease)

    if not args.follow:
        n = worker.run(world_id=args.world)
        print(f"drained {n} work item(s); exiting.")
        return 0

    # long-lived: poll forever, printing a heartbeat when idle
    total = 0
    try:
        while True:
            n = worker.run(world_id=args.world, max_idle_polls=0)
            if n:
                total += n
                print(f"processed {n} (total {total})")
            else:
                time.sleep(2.0)
    except KeyboardInterrupt:
        print(f"\nstopped; processed {total} item(s). In-flight leases will be "
              f"reclaimed by the Engine.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
