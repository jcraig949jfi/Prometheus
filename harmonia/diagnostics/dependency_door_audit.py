"""Dependency-door audit — how many missing packages stand between this host and a library?

A STRANDED asset (see component_reachability_census.py) is code that still works but
that nothing can reach. The commonest strander is not rot: it is a small number of
hard top-level imports of optional third-party packages. One `import cypari` at the
bottom of a dependency chain takes down every module that transitively touches it,
including modules whose own math needs no PARI at all.

This audit measures the number of DOORS. It iteratively installs permissive stubs for
whatever package the import error names, and re-runs, until the recovered-module count
stops growing. The output is:

    doors = [cypari, snappy, ...]          <- packages that gate the library
    recovered_by_door                       <- modules each door releases
    still_dead                              <- genuinely broken, not doored

Interpretation. `recovered` modules are not proven correct — an import is a weak test.
It is a strong test in the negative direction: a module that cannot be imported cannot
be used by anyone, whatever its quality. So `recovered` bounds STRANDED from above and
`still_dead` bounds ABANDONED from below.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/dependency_door_audit.py --pkg prometheus_math --pkg techne.lib
  ... --json D:\\Prometheus\\harmonia\\diagnostics\\_dependency_doors.json

Harmonia C, 2026-08-12.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Modules whose TOP-LEVEL code blocks (network / input / long compute). They are a
# separate defect from a missing dependency and are reported, not probed.
BLOCKERS = {
    "prometheus_math.recipes.persistent_homology.api",
    "prometheus_math.research",
}

CHILD = r'''
import importlib, json, sys, types
sys.path.insert(0, {repo!r})

class _Any:
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return _Any()
    def __getattr__(self, n): return _Any()
    def __iter__(self): return iter(())

def _install(name):
    m = types.ModuleType(name)
    m.__getattr__ = lambda n: _Any()          # PEP 562: satisfies `from pkg import X`
    m.__path__ = []                            # allow `pkg.sub` imports
    sys.modules[name] = m

for _n in {stubs!r}:
    _install(_n)

out = []
for mod in {mods!r}:
    try:
        importlib.import_module(mod)
        out.append({{"module": mod, "ok": True, "err": ""}})
    except BaseException as e:
        out.append({{"module": mod, "ok": False,
                     "err": "{{}}: {{}}".format(type(e).__name__, e)[:200]}})
print("@@JSON@@" + json.dumps(out))
'''


def sh(args, timeout=900):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          timeout=timeout, errors="replace").stdout


def discover(pkgs):
    pathspecs = []
    for p in pkgs:
        pathspecs.append(p.replace(".", "/") + "/*.py")
        pathspecs.append(p.replace(".", "/") + ".py")
    out = sh(["git", "ls-files"] + pathspecs)
    mods = []
    for line in out.splitlines():
        q = line.strip().replace("\\", "/")
        if not q.endswith(".py") or "/tests/" in q or q.endswith("__init__.py"):
            continue
        mods.append(q[:-3].replace("/", "."))
    return sorted(set(m for m in mods if m not in BLOCKERS))


def run_round(mods, stubs, timeout):
    code = CHILD.format(repo=REPO, stubs=list(stubs), mods=mods)
    env = dict(os.environ, PYTHONPATH=REPO, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, "-c", code], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=timeout,
                       errors="replace")
    for line in p.stdout.splitlines():
        if line.startswith("@@JSON@@"):
            return json.loads(line[len("@@JSON@@"):])
    raise RuntimeError(f"child produced no result: {p.stderr[-400:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", action="append", required=True)
    ap.add_argument("--max-rounds", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    mods = discover(a.pkg)
    print(f"Dependency-door audit — {len(mods)} modules in {', '.join(a.pkg)}")
    print(f"(excluded {len(BLOCKERS)} modules whose top-level code blocks on import)")
    print("=" * 78)

    stubs, history, prev_ok = [], [], None
    last_rows = []
    rows = []
    for rnd in range(a.max_rounds):
        rows = run_round(mods, stubs, a.timeout)
        ok = sum(r["ok"] for r in rows)
        missing = []
        for r in rows:
            if r["ok"]:
                continue
            m = re.search(r"No module named '([^']+)'", r["err"])
            if m:
                missing.append(m.group(1).split(".")[0])
        history.append({"round": rnd, "stubs": list(stubs), "importable": ok,
                        "dead": len(rows) - ok})
        label = "baseline (this host as it stands)" if not stubs else \
                f"+ stub {stubs[-1]}"
        gained = "" if prev_ok is None else f"   ({ok - prev_ok:+d})"
        print(f"round {rnd}: {ok:>3}/{len(rows)} importable   {label}{gained}")

        # A stub that REDUCES the importable count is not a door -- the permissive
        # stub is shadowing a package that is actually installed and actually used
        # (measured 2026-08-23: stubbing `flint` took 242 -> 44). Revert it and stop.
        # Without this guard the loop reports a phantom door on a healthy host.
        if prev_ok is not None and ok < prev_ok:
            print(f"         ^ stubbing {stubs[-1]} REDUCED reachability "
                  f"({prev_ok} -> {ok}); it is installed and load-bearing, not a door. "
                  f"Reverting and stopping.")
            stubs.pop()
            rows = last_rows
            break
        prev_ok = ok
        last_rows = rows
        if not missing:
            break
        nxt = max(set(missing), key=missing.count)
        if nxt in stubs:
            break
        stubs.append(nxt)

    ok_rows = [r for r in rows if r["ok"]]
    dead_rows = [r for r in rows if not r["ok"]]
    print("-" * 78)
    print(f"DOORS ({len(stubs)}): {', '.join(stubs) if stubs else 'none'}")
    print(f"Modules released by installing those {len(stubs)} package(s): "
          f"{history[0]['importable']} -> {len(ok_rows)}")
    print(f"Still dead for other reasons: {len(dead_rows)}")
    for r in dead_rows[:12]:
        print(f"   {r['module']}  <- {r['err'][:90]}")

    out = {"packages": a.pkg, "doors": stubs, "history": history,
           "importable_final": len(ok_rows), "dead_final": len(dead_rows),
           "blocked_on_import": sorted(BLOCKERS), "rows": rows}
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
