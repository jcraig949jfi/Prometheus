"""Whole-brain runs: an in-process reference, in-process recording, and local UDP clusters."""
import collections
import hashlib
import json
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path

from . import model
from .frames import RunDir
from .node import Node, NodeSummary
from .shard import Shard
from .transport import UdpEndpoint

Reference = collections.namedtuple(
    "Reference", "spikes shard_spikes shard_inbound shard_hashes global_digests"
)

_REPO = str(Path(__file__).resolve().parents[2])


def route(spec, emitted_by_shard):
    """{dst shard: sorted gids} for spikes that must cross to another shard."""
    out = collections.defaultdict(list)
    for s, gids in enumerate(emitted_by_shard):
        for g in gids:
            for d in model.dest_shards(spec, g):
                if d != s:
                    out[d].append(g)
    return {d: sorted(v) for d, v in out.items()}


def _simulate(spec, ticks, on_tick=None):
    shards = [Shard(spec, s) for s in range(spec.n_shards)]
    ref = Reference([], [], [], [], [])
    prev = [[] for _ in shards]
    for t in range(ticks):
        routed = route(spec, prev)
        inbound = [routed.get(s, []) for s in range(spec.n_shards)]
        prev = [sh.step(inbound[s]) for s, sh in enumerate(shards)]
        hashes = [sh.state_hash() for sh in shards]
        ref.shard_spikes.append(prev)
        ref.shard_inbound.append(inbound)
        ref.shard_hashes.append(hashes)
        ref.spikes.append(sorted(g for p in prev for g in p))
        ref.global_digests.append(
            hashlib.sha256(b"".join(sh.state_bytes() for sh in shards)).digest())
        if on_tick:
            on_tick(t, shards, inbound, prev, hashes)
    for sh in shards:
        sh.close()
    return ref


def reference_run(spec, ticks):
    """Every shard in one process, no network: the ground truth the fleet must match."""
    return _simulate(spec, ticks)


def record_in_process(spec, path, ticks, keyframe_interval, run_id=None):
    run = RunDir.create(path, spec, keyframe_interval, run_id=run_id)
    recs = [run.recorder(s) for s in range(spec.n_shards)]

    def on_tick(t, shards, inbound, out, hashes):
        for s, r in enumerate(recs):
            r.record(t, inbound[s], out[s], hashes[s])
            if t % keyframe_interval == 0:
                r.keyframe(t, shards[s].state_bytes())

    ref = _simulate(spec, ticks, on_tick)
    for r in recs:
        r.close()
    return ref


def _free_ports(n):
    socks = []
    for _ in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("127.0.0.1", 0))
        socks.append(s)
    ports = [s.getsockname()[1] for s in socks]
    for s in socks:
        s.close()
    return ports


def run_local_cluster(spec, path, ticks, keyframe_interval, drop=0.0, corrupt=0.0,
                      mode="thread", seed=0, nak_timeout=0.03, linger=2.0, run_id=None):
    """Run every shard as its own UDP node on this host (threads or processes)."""
    RunDir.create(path, spec, keyframe_interval, run_id=run_id)
    n = spec.n_shards
    if mode == "thread":
        eps = [UdpEndpoint(drop=drop, corrupt=corrupt, seed=seed * 1000 + s) for s in range(n)]
        peers = {s: eps[s].addr for s in range(n)}
        results, errors = [None] * n, []

        def go(s):
            try:
                results[s] = Node(path, s, eps[s], peers, ticks,
                                  nak_timeout=nak_timeout, linger=linger).run()
            except BaseException as e:  # surfaced below
                errors.append((s, e))

        threads = [threading.Thread(target=go, args=(s,)) for s in range(n)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        for ep in eps:
            ep.close()
        if errors:
            raise errors[0][1]
        return results
    if mode == "process":
        ports = _free_ports(n)
        peers = ",".join("%d=127.0.0.1:%d" % (s, ports[s]) for s in range(n))
        env = dict(os.environ)
        env["PYTHONPATH"] = _REPO + os.pathsep + env.get("PYTHONPATH", "")
        procs = [
            subprocess.Popen(
                [sys.executable, "-m", "odysseus.brain", "node", "--run", str(path),
                 "--shard", str(s), "--bind", "127.0.0.1:%d" % ports[s], "--peers", peers,
                 "--ticks", str(ticks), "--drop", str(drop), "--corrupt", str(corrupt),
                 "--seed", str(seed * 1000 + s), "--nak-timeout", str(nak_timeout),
                 "--linger", str(linger)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=_REPO)
            for s in range(n)
        ]
        results = []
        for s, pr in enumerate(procs):
            out, err = pr.communicate(timeout=300)
            if pr.returncode != 0:
                raise RuntimeError("shard %d exited %d: %s" % (s, pr.returncode, err.decode()[-2000:]))
            results.append(NodeSummary(**json.loads(out.decode().strip().splitlines()[-1])))
        return results
    raise ValueError("mode must be 'thread' or 'process'")
