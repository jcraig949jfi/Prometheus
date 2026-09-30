#!/usr/bin/env python3
# EXPERIMENTAL / UNVERIFIED / NOT ENABLED FOR FABRIC WORKERS -- see fabric/promexec/STATUS_EXPERIMENTAL.md
"""promexec -- the ONE way a fabric worker's code gets executed (operator ruling 2026-09-28).

    promexec <script.py> [--input PATH]... [--wall-s N] [--mem-mb M] [--cpu-pct P] [--tasks T] [-- script args...]

The Claude worker writes a script (normally under its output directory) and calls this command. It cannot run
python or a shell itself. This wrapper runs as the worker account and:
  1. stages the script as main.py, the script arguments as .promexec_args.json (never argv: B1), and the
     declared inputs into <attempt>/exec/<n>/in. Inputs must be inside the attempt's output directory or the
     pinned worktree; symlinks and anything under .git are refused or skipped. Worktree inputs keep their
     repo-relative paths, output-dir inputs go under out/;
  2. checks that the installed broker is byte-identical to the committed fabric/promexec/broker.py of this
     checkout (M20), then calls it: `sudo -n /usr/local/sbin/promexec-run`. The broker executes main.py under a
     transient per-run UID (no credentials, no home, no network, no other runs visible) with CPU, memory, task
     and wall-time bounds;
  3. receives the script's $PROMEXEC_OUT files into <out>/exec/<n>/, writes summary.json there (result, exit
     code, stdout/stderr tails), and prints the summary.
Inside the script, inputs are under $PROMEXEC_IN, files to deliver go to $PROMEXEC_OUT, the arguments are the JSON
list in $PROMEXEC_ARGS, and the working directory is scratch. There is no network, no git and no access to any home
directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BROKER = "/usr/local/sbin/promexec-run"
COMMITTED_BROKER = Path(__file__).resolve().parents[1] / "promexec" / "broker.py"
ENTRY, ARGS_FILE = "main.py", ".promexec_args.json"
CAPS = {"wall_s": 1800, "mem_mb": 4096, "cpu_pct": 200, "tasks": 64}


def fail(msg: str) -> int:
    sys.stderr.write("promexec: refused: %s\n" % msg)
    return 64


def inside(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def broker_matches(installed: Path = Path(BROKER), committed: Path = COMMITTED_BROKER) -> tuple:
    """M20: the installed root-owned broker must be byte-identical to the committed source of this checkout."""
    try:
        a = hashlib.sha256(installed.read_bytes()).hexdigest()
        b = hashlib.sha256(committed.read_bytes()).hexdigest()
    except OSError as e:
        return False, "cannot hash broker: %s" % e.__class__.__name__
    return a == b, "installed %s, committed %s" % (a[:16], b[:16])


def copy_tree_regular(src: Path, dst: Path) -> int:
    n = 0
    if src.is_symlink():
        return 0
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dst, follow_symlinks=False); return 1
    for root, dirs, files in os.walk(src, followlinks=False):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d)) and d != ".git"]
        for f in files:
            s = Path(root) / f
            if s.is_symlink() or not s.is_file():
                continue
            d = dst / s.relative_to(src)
            d.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(s, d, follow_symlinks=False); n += 1
    return n


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    out_dir = Path(os.environ.get("FABRIC_OUT_DIR", ""))
    wt = Path(os.environ.get("FABRIC_WORKTREE", ""))
    if not out_dir.is_dir():
        return fail("FABRIC_OUT_DIR is not set to the attempt's output directory")
    script_args = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    if not argv:
        return fail("usage: promexec <script.py> [--input PATH]... [--wall-s N] [--mem-mb M] [-- args]")
    script, inputs, lim, i = argv[0], [], {}, 1
    while i < len(argv):
        k = argv[i]
        if k == "--input" and i + 1 < len(argv):
            inputs.append(argv[i + 1]); i += 2
        elif k in ("--wall-s", "--mem-mb", "--cpu-pct", "--tasks") and i + 1 < len(argv):
            key = k[2:].replace("-", "_")
            try:
                lim[key] = min(CAPS[key], max(1, int(argv[i + 1])))
            except ValueError:
                return fail("%s needs an integer" % k)
            i += 2
        else:
            return fail("unknown argument %r" % k)
    roots = [r for r in (out_dir, wt) if str(r) and r.is_dir()]

    def resolve(p: str) -> Path:
        q = Path(p)
        for base in ([q] if q.is_absolute() else [out_dir / q, wt / q]):
            if base.exists() and any(inside(base, r) for r in roots) and not base.is_symlink():
                return base
        raise ValueError("%s is not inside the output directory or the worktree (or is a symlink)" % p)
    try:
        sp = resolve(script)
        if sp.suffix != ".py" or not sp.is_file():
            return fail("the script must be a .py file")
        ins = [resolve(p) for p in inputs]
    except ValueError as e:
        return fail(str(e))
    for p in [sp] + ins:
        if ".git" in p.resolve().parts:
            return fail("%s is inside .git" % p)
    ok, why = broker_matches()
    if not ok:
        return fail("installed broker differs from the committed source (M20): %s" % why)
    attempt = out_dir.parent
    base = attempt / "exec"; base.mkdir(exist_ok=True)
    n = 1 + max([int(p.name) for p in base.iterdir() if p.name.isdigit()] or [0])
    stage = base / str(n) / "in"; stage.mkdir(parents=True)
    shutil.copyfile(sp, stage / ENTRY, follow_symlinks=False)
    (stage / ARGS_FILE).write_text(json.dumps(script_args))
    staged = 0
    for p in ins:
        rel = (Path("out") / p.resolve().relative_to(out_dir.resolve())) if inside(p, out_dir) else p.resolve().relative_to(wt.resolve())
        if str(rel) in (ENTRY, ARGS_FILE):
            return fail("input %s would replace the staged %s" % (p, rel))
        staged += copy_tree_regular(p, stage / rel)
    result_dir = out_dir / "exec" / str(n)
    result_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["sudo", "-n", BROKER, "--run-id", "%s-%d" % (attempt.name, n), "--in", str(stage), "--out", str(result_dir)]
    for k, v in lim.items():
        cmd += ["--" + k.replace("_", "-"), str(v)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=CAPS["wall_s"] + 300)
    try:
        summary = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        summary = {"ok": False, "broker_error": (r.stderr or r.stdout)[-2000:]}
    summary.update({"exec_n": n, "script": sp.name, "inputs_staged_files": staged, "results_dir": str(result_dir)})
    summary["output_files"] = sorted(str(p.relative_to(result_dir)) for p in result_dir.rglob("*") if p.is_file())
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=1))
    shutil.rmtree(stage.parent / "in", ignore_errors=True)
    print(json.dumps({k: summary.get(k) for k in ("ok", "result", "exit_code", "wall_s_used", "output_files", "results_dir",
                                                  "refused", "broker_error")}, indent=1))
    print("---- stdout (tail) ----\n" + (summary.get("stdout") or "")[-4000:])
    print("---- stderr (tail) ----\n" + (summary.get("stderr") or "")[-2000:])
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
