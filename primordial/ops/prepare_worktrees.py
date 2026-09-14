"""Round 2 gate F6: build lane worktrees ONE AT A TIME, sparse, warmed, verified.

Round 1: four clones ran `git worktree add` (43k files on the F: HDD) at once;
two failed with "Could not reset index file" and one lane never booted. Here
the conductor builds every worktree before any prompt is pasted:

  for each lane, sequentially:
    git worktree add --no-checkout [-b] nestor/<round>-<l>-<date> <root>/nestor-<round>-<l> <base>
    git sparse-checkout set --cone <SPARSE...>; git checkout
    verify: hygiene test, numba warmup, pre-commit preflight probes, comms import, bus import

    python -m primordial.ops.prepare_worktrees --lanes b,c,d,e [--dry]

Timings and outcomes go to pm-data/launcher/prepare_log.jsonl.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import time

PY = os.environ.get("PM_PY", "C:/Users/jcrai/lab/gw-venv/Scripts/python.exe")
SPARSE = ["primordial", "roles/Nestor", "comms", "attacks", "SerendipityFoundry/worldfoundry", ".claude"]
LOG = pathlib.Path(os.environ.get("PM_PREPARE_LOG", "C:/Users/jcrai/lab/pm-data/launcher/prepare_log.jsonl"))


def run(cmd, cwd=None, timeout=900, env=None):
    t = time.perf_counter()
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    return p.returncode, round(time.perf_counter() - t, 2), (p.stdout + p.stderr).strip()[-600:]


def verify(d: pathlib.Path) -> dict:
    env = dict(os.environ, OMP_NUM_THREADS="3", NUMBA_NUM_THREADS="3", PYTHONPATH=str(d))
    checks = {
        "hygiene_test": [PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "primordial/tests/test_fabric_hygiene.py"],
        "warmup": [PY, "-m", "primordial.ops.warmup"],
        "preflight_probes": ["python", "attacks/preflight.py", "--probes"],
        "comms_import": ["python", "-c", "import comms, comms.api"],
        "bus_import": [PY, "-c", "import primordial.bus.bus, primordial.fabric.rows"],
    }
    out = {}
    for name, cmd in checks.items():
        rc, s, tail = run(cmd, cwd=str(d), env=env)
        out[name] = {"rc": rc, "s": s, **({} if rc == 0 else {"tail": tail})}
    return out


def prepare(lane: str, a) -> dict:
    d = pathlib.Path(a.root) / f"nestor-{a.round}-{lane}"
    br = f"nestor/{a.round}-{lane}-{a.date}"
    rec = {"lane": lane, "dir": str(d), "branch": br, "base": a.base, "sparse": a.sparse,
           "ts": datetime.datetime.now().astimezone().isoformat(), "steps": {}}
    if a.dry:
        rec["dry"] = True
        return rec
    if not d.exists():
        rc, s, tail = run(["git", "-C", a.repo, "fetch", "-q", "origin"])
        rec["steps"]["fetch"] = {"rc": rc, "s": s}
        exists = run(["git", "-C", a.repo, "rev-parse", "--verify", "--quiet", br])[0] == 0
        add = ["git", "-C", a.repo, "worktree", "add", "--no-checkout"] + ([] if exists else ["-b", br]) + [str(d)] \
            + ([br] if exists else [a.base])
        rc, s, tail = run(add)
        rec["steps"]["worktree_add"] = {"rc": rc, "s": s, **({} if rc == 0 else {"tail": tail})}
        if rc != 0:
            return rec
        rc, s, tail = run(["git", "-C", str(d), "sparse-checkout", "set", "--cone", *a.sparse])
        rec["steps"]["sparse_set"] = {"rc": rc, "s": s, **({} if rc == 0 else {"tail": tail})}
        rc, s, tail = run(["git", "-C", str(d), "checkout", br])
        rec["steps"]["checkout"] = {"rc": rc, "s": s, **({} if rc == 0 else {"tail": tail})}
    else:
        rec["steps"]["exists"] = True
    rc, s, n = run(["git", "-C", str(d), "ls-files"])
    rec["files_in_checkout"] = len([x for x in subprocess.run(["git", "-C", str(d), "ls-files", "-t"], capture_output=True,
                                                             text=True).stdout.splitlines() if not x.startswith("S ")])
    rec["verify"] = verify(d)
    rec["ok"] = all(v["rc"] == 0 for v in rec["verify"].values())
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lanes", default="b,c,d,e")
    ap.add_argument("--round", default="r2")
    ap.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("--base", default="origin/nestor/sidequest-graphworld-2026-09-14")
    ap.add_argument("--root", default="F:/Prometheus-worktrees")
    ap.add_argument("--repo", default="F:/Prometheus")
    ap.add_argument("--sparse", nargs="+", default=SPARSE)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    ok = True
    for lane in a.lanes.split(","):
        rec = prepare(lane.strip().lower(), a)
        with open(LOG, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(json.dumps(rec, indent=1))
        ok = ok and rec.get("ok", a.dry)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
