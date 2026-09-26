"""Command line.

    python -m odysseus.brain node   --run DIR --shard S --bind HOST:PORT --peers 0=H:P,1=H:P,... --ticks N
    python -m odysseus.brain local  --run DIR --neurons N --shards S --ticks T [--keyframe K] [--drop P]
    python -m odysseus.brain verify --run DIR     (full replay of every shard, root check per tick)

On a fleet, each machine runs one `node`; every machine needs the same
run.json (created by `init`), and writes only its own shard directory.

    python -m odysseus.brain init   --run DIR --neurons N --shards S --seed X --keyframe K --run-id R
"""
import argparse
import json
import sys


def _addr(text):
    host, port = text.rsplit(":", 1)
    return host, int(port)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="odysseus.brain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("--run", required=True)
    i.add_argument("--neurons", type=int, required=True)
    i.add_argument("--shards", type=int, required=True)
    i.add_argument("--seed", type=int, default=0)
    i.add_argument("--keyframe", type=int, default=10)
    i.add_argument("--run-id", type=int, required=True)

    n = sub.add_parser("node")
    n.add_argument("--run", required=True)
    n.add_argument("--shard", type=int, required=True)
    n.add_argument("--bind", type=_addr, required=True)
    n.add_argument("--peers", required=True)
    n.add_argument("--ticks", type=int, required=True)
    n.add_argument("--drop", type=float, default=0.0)
    n.add_argument("--corrupt", type=float, default=0.0)
    n.add_argument("--seed", type=int, default=0)
    n.add_argument("--nak-timeout", type=float, default=0.03)
    n.add_argument("--linger", type=float, default=2.0)

    lo = sub.add_parser("local")
    lo.add_argument("--run", required=True)
    lo.add_argument("--neurons", type=int, required=True)
    lo.add_argument("--shards", type=int, required=True)
    lo.add_argument("--seed", type=int, default=0)
    lo.add_argument("--ticks", type=int, required=True)
    lo.add_argument("--keyframe", type=int, default=10)
    lo.add_argument("--drop", type=float, default=0.0)
    lo.add_argument("--mode", default="process", choices=["thread", "process"])

    v = sub.add_parser("verify")
    v.add_argument("--run", required=True)

    a = ap.parse_args(argv)

    if a.cmd == "init":
        from .frames import RunDir
        from .model import ModelSpec
        RunDir.create(a.run, ModelSpec(a.neurons, a.shards, a.seed), a.keyframe,
                      run_id=a.run_id, exist_ok=True)
        return 0

    if a.cmd == "node":
        from .node import Node
        from .transport import UdpEndpoint
        peers = {int(k): _addr(v_) for k, v_ in (x.split("=") for x in a.peers.split(","))}
        ep = UdpEndpoint(bind=a.bind, drop=a.drop, corrupt=a.corrupt, seed=a.seed)
        try:
            summary = Node(a.run, a.shard, ep, peers, a.ticks,
                           nak_timeout=a.nak_timeout, linger=a.linger).run()
        finally:
            ep.close()
        print(json.dumps(summary._asdict()))
        return 0

    if a.cmd == "local":
        from .cluster import run_local_cluster
        from .model import ModelSpec
        res = run_local_cluster(ModelSpec(a.neurons, a.shards, a.seed), a.run, a.ticks,
                                a.keyframe, drop=a.drop, mode=a.mode)
        for r in res:
            print(json.dumps(r._asdict()))
        return 0

    if a.cmd == "verify":
        from .player import GlobalPlayer
        from .player import ReplayDivergence
        g = GlobalPlayer(a.run)
        last = min(p.last_tick for p in g.players)
        try:
            # Shard-local replay of every tick; each tick's hash and spikes are
            # checked inside play(), then the whole brain's root at the end.
            for p in g.players:
                p.play(until=last)
            ok = g.root() == g.recorded_root(last)
            err = None
        except ReplayDivergence as e:
            ok, err = False, str(e)
        print(json.dumps({"ticks": last + 1, "shards": len(g.players),
                          "root_ok": ok, "error": err}))
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
