"""WTP ledger (directive s2, s40): every run keeps genome + hash, seed, code
commit, hardware fingerprint, library versions, initial/final/event
digests, metrics, ancestry, mutation provenance and markers. Replay =
deterministic re-execution from (genome, seed) with a digest check."""
import json
import os
import platform
import subprocess
import sys

import numpy as np

from .genome import ghash


def fingerprint():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30,
                                cwd=os.path.dirname(__file__)).stdout.strip()
    except Exception:
        commit = "unknown"
    return dict(commit=commit, platform=platform.platform(), machine=platform.machine(), cpu_count=os.cpu_count(),
                python=sys.version.split()[0], numpy=np.__version__)


def record(g, seed, result, wave, markers=None, fp=None, extra=None):
    row = dict(wave=wave, genome_hash=ghash(g), seed=int(seed), genome=g, parents=g.get("meta", {}).get("parents", []),
               strategy=g.get("meta", {}).get("strategy"), mutations=g.get("meta", {}).get("mutations", []),
               markers=markers or [], fingerprint=fp or {}, **{k: v for k, v in result.items() if k != "_memory"})
    if extra:
        row.update(extra)
    return row


def write(rows, path):
    with open(path, "a") as f:
        for r in rows:
            f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)) + "\n")


def replay_check(g, seed, stored):
    """Re-execute and compare digests (directive s40: deterministic playback)."""
    from .world import run_world
    r = run_world(g, seed, record=True)
    ok = all(r.get(k) == stored.get(k) for k in ("init_digest", "event_digest", "final_digest"))
    return ok, r
