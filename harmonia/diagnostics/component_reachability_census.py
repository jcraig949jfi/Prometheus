"""Component reachability census — the FROZEN/FINISHED/ABANDONED/STRANDED trichotomy.

Prometheus has ~44 top-level components, most last touched before the May 2026
collapse in activity. Prior reviews treated "frozen" as one bucket. It is three:

  FINISHED  — frozen, and something live still reaches it (or it needs no consumer:
              a proof, a dataset, a terminal artifact).
  ABANDONED — frozen, nothing reaches it, and it no longer stands up on its own
              (imports fail / dependencies gone / superseded).
  STRANDED  — frozen, nothing reaches it, but it STILL WORKS. A working asset with
              no live consumer. This is the high-value bucket: recovering a stranded
              asset costs an import line; rebuilding it costs a month.

Method
------
1. Enumerate tracked .py files. Map path -> dotted module.
2. Parse imports with `ast` (NOT regex — a regex import screen produced a 20/20
   false-reject in this program on 2026-08-12; see REVIEW_20260812_syntactic_router.md
   section 6). Resolve `import a.b` / `from a.b import c` against repo modules.
3. Last-touch date per file from ONE `git log --name-only` pass (not per-file).
4. LIVE = touched on/after --cutoff. Edges from live files are "live inbound".
5. Emit per-component and per-module reachability. Candidate STRANDED modules
   (zero live inbound, non-trivial, has an entry point) are listed for the
   executability probe in stage 2 (`--probe`), which imports each in a subprocess
   with a timeout.

Usage
-----
  PYTHONPATH=. python harmonia/diagnostics/component_reachability_census.py
  PYTHONPATH=. python harmonia/diagnostics/component_reachability_census.py --probe
  ... --json D:\\Prometheus\\harmonia\\diagnostics\\_reachability_census.json

Harmonia C, 2026-08-12.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CUTOFF_DEFAULT = "2026-05-01"

SKIP_PARTS = {
    "__pycache__", "node_modules", ".venv", "venv", "site-packages",
    ".git", "external_deps", "build", "dist", ".mypy_cache",
}


def sh(args, cwd=REPO, timeout=600):
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
        errors="replace",
    ).stdout


def tracked_py_files():
    out = sh(["git", "ls-files", "*.py"])
    files = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('"'):
            # git quotes paths containing non-ASCII/control chars; those are never
            # importable modules anyway (one exists: a markdown sprint plan saved
            # with a .py extension under charon/TheFive/).
            continue
        line = line.replace("\\", "/")
        if not line or not line.endswith(".py"):
            continue
        parts = set(line.split("/"))
        if parts & SKIP_PARTS:
            continue
        files.append(line)
    return files


def last_touch_map():
    """One pass over history: path -> most recent commit date (YYYY-MM-DD)."""
    out = sh(["git", "log", "--name-only", "--date=short", "--pretty=format:@%ad"])
    dates = {}
    cur = None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = line[1:].strip()
        elif line.strip() and cur:
            p = line.strip().replace("\\", "/")
            if p not in dates:          # log is newest-first, so first seen == latest
                dates[p] = cur
    return dates


# Generated-specimen corpora: forge/generator OUTPUT, never intended to be imported.
# Counting these as "unreachable" inflates the headline by ~5.5k modules and would be
# the exact failure this review is auditing for, so they are typed out explicitly.
GENERATED_PREFIXES = (
    "agents/hephaestus/humanreadable/", "agents/hephaestus/scrap/",
    "agents/hephaestus/scrap_staging/", "agents/hephaestus/forge",
    "agents/hephaestus/tier_specialists/", "forge/candidates/",
    "forge/tester_quarantine/", "agents/icarus/cycles/",
)


def classify(path, inbound_any, entry_point):
    """GENERATED / SCRIPT / LIBRARY.

    Reachability is only a meaningful test for LIBRARY. A SCRIPT with no importer
    is normal; it is judged by whether its RESULT was captured, not by inbound edges.
    """
    p = path.replace("\\", "/")
    if any(p.startswith(g) for g in GENERATED_PREFIXES):
        return "GENERATED"
    if inbound_any > 0:
        return "LIBRARY"
    return "SCRIPT" if entry_point else "LIBRARY"


def to_module(path):
    assert path.endswith(".py")
    p = path[:-3]
    if p.endswith("/__init__"):
        p = p[: -len("/__init__")]
    return p.replace("/", ".")


def parse_imports(abspath):
    """Return the set of dotted names this file imports. ast, never regex."""
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as fh:
            tree = ast.parse(fh.read())
    except (SyntaxError, ValueError, OSError):
        return None                      # unparseable -> evidence, not silence
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:               # relative import
                continue
            if node.module:
                names.add(node.module)
                for a in node.names:
                    names.add(node.module + "." + a.name)
    return names


def has_entry_point(abspath):
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except OSError:
        return False
    return '__main__' in src


def loc(abspath):
    try:
        with open(abspath, "r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def build(cutoff):
    files = tracked_py_files()
    dates = last_touch_map()
    modules = {}                          # dotted module -> path
    for f in files:
        modules[to_module(f)] = f

    inbound_live = defaultdict(set)
    inbound_any = defaultdict(set)
    unparseable = []

    for f in files:
        abspath = os.path.join(REPO, f)
        names = parse_imports(abspath)
        if names is None:
            unparseable.append(f)
            continue
        d = dates.get(f, "0000-00-00")
        live = d >= cutoff
        for n in names:
            # resolve longest matching repo module prefix
            target = None
            parts = n.split(".")
            for k in range(len(parts), 0, -1):
                cand = ".".join(parts[:k])
                if cand in modules and modules[cand] != f:
                    target = cand
                    break
            if target is None:
                continue
            inbound_any[target].add(f)
            if live:
                inbound_live[target].add(f)

    rows = []
    for mod, path in sorted(modules.items()):
        abspath = os.path.join(REPO, path)
        d = dates.get(path, "0000-00-00")
        ia, il = len(inbound_any.get(mod, ())), len(inbound_live.get(mod, ()))
        ep = has_entry_point(abspath)
        rows.append({
            "module": mod,
            "path": path,
            "component": path.split("/")[0],
            "kind": classify(path, ia, ep),
            "last_touch": d,
            "frozen": d < cutoff,
            "loc": loc(abspath),
            "inbound_live": il,
            "inbound_any": ia,
            "lost_consumers": ia > 0 and il == 0,
            "live_importers": sorted(inbound_live.get(mod, ()))[:5],
            "entry_point": ep,
        })
    return rows, unparseable, dates


def probe(rows, limit, timeout=25):
    """Stage 2: does the frozen, unreachable module still stand up?

    Import in a subprocess (isolation + timeout). An import that succeeds is not
    proof the asset is useful, but an import that FAILS is proof it is not
    STRANDED — it is ABANDONED. Fail-closed on the flattering verdict.
    """
    cands = [r for r in rows
             if r["kind"] == "LIBRARY" and r["frozen"]
             and r["lost_consumers"] and r["loc"] >= 40]
    cands.sort(key=lambda r: (-r["inbound_any"], -r["loc"]))
    cands = cands[:limit]
    env = dict(os.environ, PYTHONPATH=REPO, PYTHONIOENCODING="utf-8")
    results = []
    for r in cands:
        try:
            p = subprocess.run(
                [sys.executable, "-c", f"import {r['module']}"],
                cwd=REPO, capture_output=True, text=True, timeout=timeout,
                env=env, errors="replace",
            )
            ok = p.returncode == 0
            err = (p.stderr.strip().splitlines() or [""])[-1][:160]
        except subprocess.TimeoutExpired:
            ok, err = False, "TIMEOUT (top-level code blocks — not importable)"
        results.append({**r, "imports_ok": ok, "import_error": "" if ok else err})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff", default=CUTOFF_DEFAULT,
                    help="LIVE means last touched on/after this date")
    ap.add_argument("--probe", action="store_true",
                    help="stage 2: subprocess-import the unreachable frozen modules")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    rows, unparseable, _ = build(a.cutoff)

    kinds = defaultdict(lambda: {"n": 0, "loc": 0, "frozen": 0, "lost": 0})
    for r in rows:
        k = kinds[r["kind"]]
        k["n"] += 1
        k["loc"] += r["loc"]
        k["frozen"] += bool(r["frozen"])
        k["lost"] += bool(r["lost_consumers"] and r["frozen"])

    print(f"Component reachability census  (LIVE cutoff = {a.cutoff})")
    print("=" * 86)
    print("What the repo is made of — reachability is only meaningful for LIBRARY.")
    print(f"{'kind':<12}{'modules':>9}{'LOC':>11}{'frozen':>9}"
          f"{'frozen+lost_consumers':>24}")
    print("-" * 86)
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]["n"]):
        print(f"{k:<12}{v['n']:>9}{v['loc']:>11}{v['frozen']:>9}{v['lost']:>24}")
    print("-" * 86)

    lib = [r for r in rows if r["kind"] == "LIBRARY"]
    by_comp = defaultdict(lambda: {"n": 0, "frozen": 0, "lost": 0, "loc": 0,
                                   "last": "0000-00-00"})
    for r in lib:
        c = by_comp[r["component"]]
        c["n"] += 1
        c["loc"] += r["loc"]
        c["last"] = max(c["last"], r["last_touch"])
        if r["frozen"]:
            c["frozen"] += 1
            if r["lost_consumers"]:
                c["lost"] += 1

    print("\nLIBRARY modules by component  (lost = had importers, has none live)")
    print("=" * 86)
    print(f"{'component':<22}{'library':>9}{'frozen':>8}{'lost':>7}"
          f"{'LOC':>9}  last_touch")
    print("-" * 86)
    for comp, c in sorted(by_comp.items(), key=lambda kv: -kv[1]["lost"]):
        print(f"{comp:<22}{c['n']:>9}{c['frozen']:>8}{c['lost']:>7}"
              f"{c['loc']:>9}  {c['last']}")
    print("-" * 86)
    print(f"{'TOTAL':<22}{len(lib):>9}"
          f"{sum(1 for r in lib if r['frozen']):>8}"
          f"{sum(1 for r in lib if r['frozen'] and r['lost_consumers']):>7}"
          f"{sum(r['loc'] for r in lib):>9}")
    if unparseable:
        print(f"\nunparseable (ast.parse failed): {len(unparseable)}")
        for f in unparseable[:10]:
            print(f"  {f}")

    out = {"cutoff": a.cutoff, "rows": rows, "unparseable": unparseable}

    if a.probe:
        res = probe(rows, a.limit)
        out["probe"] = res
        ok = [r for r in res if r["imports_ok"]]
        bad = [r for r in res if not r["imports_ok"]]
        print(f"\nStage 2 — executability probe on {len(res)} unreachable frozen "
              f"modules (largest first)")
        print("=" * 86)
        print(f"STRANDED candidates (import OK, zero live consumers): {len(ok)}")
        for r in ok:
            print(f"  {r['loc']:>5} LOC  {r['last_touch']}  {r['module']}"
                  f"  (inbound_any={r['inbound_any']})")
        print(f"\nABANDONED (import fails — cannot be reached even by hand): {len(bad)}")
        for r in bad:
            print(f"  {r['loc']:>5} LOC  {r['last_touch']}  {r['module']}")
            print(f"        {r['import_error']}")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
