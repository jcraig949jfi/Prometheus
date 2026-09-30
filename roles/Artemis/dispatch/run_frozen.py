#!/usr/bin/env python3
"""Run one frozen worker-authored script inside a Fabric script Task, unmodified.

usage (as the Task's --script): roles/Artemis/dispatch/run_frozen.py SCRIPT CWD [ARG ...]

The script executor starts in the pinned worktree with an allow-listed env. This runner only
supplies what the scripts' own usage lines ask for: PROMETHEUS_REPO and REPO = the worktree,
the worktree on sys.path, argv, and a cwd (CWD is "repo" or "out"; "out" = $FABRIC_OUT_DIR, so
files a script writes to its cwd come back as artifacts). "{repo}" in an ARG becomes the worktree.
It writes out/run_meta.json (script sha256, argv, cwd, times, versions) before and after the run.
"""
import hashlib, json, os, platform, runpy, sys, time

repo = os.getcwd()
out = os.environ.get("FABRIC_OUT_DIR", repo)
script, where, args = sys.argv[1], sys.argv[2], [a.replace("{repo}", repo) for a in sys.argv[3:]]
path = os.path.join(repo, script)
meta = {"script": script, "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
        "argv": args, "cwd": where, "python": platform.python_version(),
        "started_utc": time.strftime("%FT%TZ", time.gmtime())}
try:
    import numpy
    meta["numpy"] = numpy.__version__
except ImportError:
    meta["numpy"] = None


def dump(**kw):
    meta.update(kw)
    with open(os.path.join(out, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)


dump()
os.environ["PROMETHEUS_REPO"] = os.environ["REPO"] = repo
sys.path.insert(0, repo)
os.chdir(out if where == "out" else repo)
sys.argv = [path] + args
t0 = time.time()
try:
    runpy.run_path(path, run_name="__main__")
    dump(status="returned", wall_s=round(time.time() - t0, 1), ended_utc=time.strftime("%FT%TZ", time.gmtime()))
except SystemExit as e:
    dump(status="exit", code=e.code, wall_s=round(time.time() - t0, 1), ended_utc=time.strftime("%FT%TZ", time.gmtime()))
    raise
except BaseException as e:
    dump(status="raised", error=repr(e)[:2000], wall_s=round(time.time() - t0, 1),
         ended_utc=time.strftime("%FT%TZ", time.gmtime()))
    raise
