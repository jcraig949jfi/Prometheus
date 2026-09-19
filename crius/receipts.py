"""Receipts: structured records written before any narrative (charter s14).

Every receipt carries code_commit, config_hash, world fingerprint and the
partition fingerprint, so the executed configuration can be reconstructed
from the receipt alone (tests/test_receipts.py proves it).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time

from . import streams, tasks as tasks_mod


def load_config(path: str) -> dict:
    with open(path, "r", encoding="ascii") as f:
        return json.load(f)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(canonical(cfg).encode("ascii")).hexdigest()[:16]


def code_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20)
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return "unknown"


def code_dirty() -> bool:
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", "crius"], capture_output=True, text=True, timeout=20)
        return bool(out.stdout.strip())
    except Exception:
        return True


def run_meta(cfg: dict, config_path: str) -> dict:
    fp = streams.fingerprints(cfg)
    meta = {
        "code_commit": code_commit(),
        "code_dirty_crius": code_dirty(),
        "config_path": config_path,
        "config_hash": config_hash(cfg),
        "config": cfg,
        "world_id": streams.world_id(cfg),
        "world_fingerprint": fp["world_fingerprint"],
        "partitions_fingerprint": fp["partitions_fingerprint"],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if streams.world_id(cfg) == "c0":
        parts = tasks_mod.build_partitions(cfg)
        meta["partition_sizes"] = {k: len(v) for k, v in parts.items()}
    return meta


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return o


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii", newline="\n") as f:
        json.dump(_jsonable(obj), f, indent=None, separators=(",", ":"), sort_keys=False)
        f.write("\n")
    os.replace(tmp, path)


def open_text(path: str):
    """Open a receipt for reading; a missing plain file falls back to path + '.gz'."""
    import gzip
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", encoding="ascii")
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="ascii")
    return open(path, "r", encoding="ascii")


def read_json(path: str):
    with open_text(path) as f:
        return json.load(f)


def lifetime_receipt(meta: dict, player, tasks, seed: int, suite: str, life: dict,
                     parent_hash: str = None, run_id: str = None) -> dict:
    """RunReceipt (charter s14) for one lifetime."""
    m = life["metrics"]
    return {
        "run_id": run_id,
        "candidate_hash": player.spec_hash(),
        "candidate_spec": player.spec(),
        "candidate_name": player.name,
        "parent_hash": parent_hash,
        "code_commit": meta["code_commit"],
        "config_hash": meta["config_hash"],
        "world_fingerprint": meta["world_fingerprint"],
        "partitions_fingerprint": meta["partitions_fingerprint"],
        "seed": seed,
        "search_or_qualification": suite,
        "condition": life["condition"],
        "task_sequence_hash": tasks_mod.task_sequence_hash(tasks),
        "tasks": [t.to_dict() for t in tasks],
        "task_results": life["task_results"],
        "workspace_history": life["workspace_history"],
        "artifact_history": life["artifact_history"],
        "adaptation_curve": m["adaptation_curve"],
        "metrics": m,
        "compute_cost": m["vm_steps_total"] + m["ws_cost_total"],
        "storage_cost": m["retained_state"],
        "replay_hash": life["replay_hash"],
        "reset_points": life.get("reset_points", []),
    }


def battery_receipt(meta: dict, player, tasks, seed: int, suite: str, bat: dict,
                    wall_seconds: float = None, parent_hash: str = None, run_id: str = None) -> dict:
    out = {
        "run_id": run_id,
        "candidate_hash": player.spec_hash(),
        "candidate_name": player.name,
        "candidate_spec": player.spec(),
        "parent_hash": parent_hash,
        "code_commit": meta["code_commit"],
        "config_hash": meta["config_hash"],
        "world_fingerprint": meta["world_fingerprint"],
        "partitions_fingerprint": meta["partitions_fingerprint"],
        "seed": seed,
        "search_or_qualification": suite,
        "task_sequence_hash": tasks_mod.task_sequence_hash(tasks),
        "tasks": [t.to_dict() for t in tasks],
        "wall_seconds": wall_seconds,
        "conditions": {},
        "reuse_gain": bat["reuse_gain"],
        "causal": bat["causal"],
    }
    for cond in ("ACCUMULATED", "FRESH", "WORKSPACE_RESET", "WORKSPACE_SCRAMBLED"):
        out["conditions"][cond] = lifetime_receipt(meta, player, tasks, seed, suite, bat[cond],
                                                   parent_hash=parent_hash, run_id=run_id)
    return out


def one_line(name: str, seed: int, bat: dict, dt: float) -> str:
    a = bat["ACCUMULATED"]["metrics"]
    f = bat["FRESH"]["metrics"]
    r = bat["WORKSPACE_RESET"]["metrics"]
    s = bat["WORKSPACE_SCRAMBLED"]["metrics"]
    le = a["late_early_ratio_by_depth"]
    return ("%-13s seed %d  fit A=%.3f F=%.3f R=%.3f S=%.3f  succ A=%d F=%d  inter A=%d F=%d  "
            "late/early d2=%s d3=%s  reuse_gain=%.1f  blocks=%d  %.1fs" % (
                name, seed, a["fitness"], f["fitness"], r["fitness"], s["fitness"],
                a["successes"], f["successes"], a["interactions_total"], f["interactions_total"],
                le.get("2"), le.get("3"), sum(bat["reuse_gain"]), a["blocks_created_total"], dt))
