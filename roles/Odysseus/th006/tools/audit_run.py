"""Run a Python script under an audit hook that records every file it opens or lists.

    python3 -I audit_run.py LOG.json SCRIPT [ARGS...]        run SCRIPT, write the access log
    python3 -I audit_run.py --report ROOT LOG.json [...]      list accesses outside ROOT and the stdlib

Used by the TH-006 node check to show that verification read nothing but
the task directory (and Python's own library). Stdlib only.
"""
import json
import os
import runpy
import sys
import sysconfig


def _run(log_path, script, args):
    seen = []

    def hook(event, a):
        if event == "open" and a and isinstance(a[0], (str, bytes)):
            p = a[0].decode() if isinstance(a[0], bytes) else a[0]
            seen.append(("open", os.path.abspath(p), str(a[1]) if len(a) > 1 else ""))
        elif event in ("os.listdir", "os.scandir") and a and isinstance(a[0], (str, bytes)):
            p = a[0].decode() if isinstance(a[0], bytes) else a[0]
            seen.append((event, os.path.abspath(p), ""))

    sys.addaudithook(hook)
    sys.argv = [script] + list(args)
    code = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        uniq = sorted(set(seen))
        with open(log_path, "w", encoding="ascii") as f:
            json.dump({"script": script, "args": list(args), "exit": code, "accesses": uniq}, f, indent=0)
    return code


def _report(root, logs):
    root = os.path.abspath(root)
    stdlib = {os.path.abspath(sysconfig.get_paths()[k]) for k in ("stdlib", "platstdlib", "purelib", "platlib")}
    outside, attempted_missing = [], []
    for lp in logs:
        with open(lp, encoding="ascii") as f:
            d = json.load(f)
        for kind, p, mode in d["accesses"]:
            if p == root or p.startswith(root + os.sep) or any(p.startswith(s) for s in stdlib):
                continue
            (outside if os.path.exists(p) else attempted_missing).append([os.path.basename(lp), kind, p, mode])
    print(json.dumps({"root": root, "outside_existing": outside, "outside_nonexistent": attempted_missing}, indent=1))
    return 0 if not outside else 1


if __name__ == "__main__":
    if sys.argv[1] == "--report":
        sys.exit(_report(sys.argv[2], sys.argv[3:]))
    sys.exit(_run(sys.argv[1], sys.argv[2], sys.argv[3:]))
