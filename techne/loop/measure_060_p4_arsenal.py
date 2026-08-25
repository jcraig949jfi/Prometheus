"""Cycle 060, prediction 4: does the non-finite class reach OUTSIDE the height family?

DECLARED POPULATION, fixed before running: every function named in the `interface` or `also`
field of every tool in `techne/inventory.json` -- the arsenal's own registry, so the set is not
chosen by me -- restricted to those whose signature has exactly ONE required parameter, which
is where a single non-finite argument is unambiguous.

WHAT IS DROPPED, AND IT IS REPORTED RATHER THAN SILENTLY CAPPED: functions needing two or more
required arguments (a non-finite value could go in any slot, and choosing one would make this a
sample rather than an enumeration), functions that cannot be imported, and modules that exceed
the per-module time budget. Every drop is counted and named in the output.

One subprocess per MODULE, not per call, so a ~12 s PARI import is paid once -- cycle 059 read
exactly that import cost as a family of function hangs.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]

PROBE = r'''
import inspect, json, math, sys, importlib
sys.path.insert(0, r"{repo}")
mod_path = {mod!r}
names = {names!r}
rows = []
try:
    mod = importlib.import_module(mod_path)
except BaseException as e:
    print(json.dumps([{{"module": mod_path, "function": None, "outcome": "MODULE_IMPORT_FAILED",
                       "detail": type(e).__name__ + ": " + str(e)[:80]}}]))
    raise SystemExit(0)

NAN = float("nan")
SEQ_HINTS = ("coeff", "poly", "list", "vector", "seq", "array", "rational", "values",
             "samples", "matrix", "data", "points")

for name in names:
    fn = getattr(mod, name, None)
    if fn is None or not callable(fn):
        rows.append({{"module": mod_path, "function": name, "outcome": "NOT_FOUND", "detail": ""}})
        continue
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError) as e:
        rows.append({{"module": mod_path, "function": name, "outcome": "NO_SIGNATURE",
                      "detail": str(e)[:60]}})
        continue
    required = [p for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    if len(required) != 1:
        rows.append({{"module": mod_path, "function": name, "outcome": "DROPPED_ARITY",
                      "detail": "required args = %d" % len(required)}})
        continue
    p = required[0]
    lowered = p.name.lower() + " " + str(p.annotation).lower()
    arg = [NAN, 1.0, -1.0] if any(h in lowered for h in SEQ_HINTS) else NAN
    kind = "sequence" if isinstance(arg, list) else "scalar"
    try:
        r = fn(arg)
    except ValueError as e:
        rows.append({{"module": mod_path, "function": name, "outcome": "RAISES", "arg": kind,
                      "detail": "ValueError: " + str(e)[:70]}}); continue
    except TypeError as e:
        rows.append({{"module": mod_path, "function": name, "outcome": "RAISES_TYPE", "arg": kind,
                      "detail": "TypeError: " + str(e)[:70]}}); continue
    except BaseException as e:
        rows.append({{"module": mod_path, "function": name, "outcome": "RAISES_OTHER", "arg": kind,
                      "detail": type(e).__name__ + ": " + str(e)[:70]}}); continue
    if isinstance(r, bool):
        rows.append({{"module": mod_path, "function": name, "outcome": "RETURNS_BOOL",
                      "arg": kind, "detail": repr(r)}}); continue
    try:
        ok = math.isfinite(float(r))
        rows.append({{"module": mod_path, "function": name,
                      "outcome": "RETURNS_FINITE" if ok else "RETURNS_NONFINITE",
                      "arg": kind, "detail": repr(r)[:60]}})
    except (TypeError, ValueError):
        rows.append({{"module": mod_path, "function": name, "outcome": "RETURNS_OTHER",
                      "arg": kind, "detail": repr(r)[:60]}})
print(json.dumps(rows))
'''


def entry_points() -> dict:
    """`{module_path: [function names]}` from the registry, not from my judgement."""
    inv = json.loads((REPO / "techne" / "inventory.json").read_text(encoding="utf-8"))
    out: dict[str, list] = {}
    for tool in inv["tools"]:
        f = tool.get("file")
        if not f or not f.endswith(".py"):
            continue
        mod = f[:-3].replace("/", ".").replace("\\", ".")
        sigs = [tool.get("interface", "")] + list(tool.get("also", []))
        names = []
        for s in sigs:
            s = (s or "").strip()
            head = s.split("(")[0].strip()
            if head and head.replace("_", "").isalnum() and not head[0].isdigit():
                names.append(head)
        if names:
            out.setdefault(mod, [])
            for n in names:
                if n not in out[mod]:
                    out[mod].append(n)
    return out


def main() -> int:
    eps = entry_points()
    rows, timeouts = [], []
    for mod, names in sorted(eps.items()):
        code = PROBE.format(repo=str(REPO), mod=mod, names=names)
        try:
            proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=90, cwd=str(REPO))
        except subprocess.TimeoutExpired:
            timeouts.append(mod)
            rows.append({"module": mod, "function": None, "outcome": "MODULE_TIMEOUT",
                         "detail": "90 s budget for the whole module, import included"})
            continue
        line = next((l for l in reversed((proc.stdout or "").splitlines())
                     if l.startswith("[")), None)
        if line is None:
            rows.append({"module": mod, "function": None, "outcome": "PROBE_NO_OUTPUT",
                         "detail": (proc.stderr or "")[-120:]})
            continue
        rows.extend(json.loads(line))

    tally: dict = {}
    for r in rows:
        tally[r["outcome"]] = tally.get(r["outcome"], 0) + 1
    leaking = sorted({f"{r['module']}::{r['function']}" for r in rows
                      if r["outcome"] in ("RETURNS_NONFINITE", "RETURNS_FINITE",
                                          "RETURNS_BOOL", "RETURNS_OTHER")})
    height = ("mahler_measure", "log_mahler_measure", "is_cyclotomic", "polynomial_length",
              "house")
    outside = [x for x in leaking if x.split("::")[-1] not in height]
    out = {
        "population": ("every function named in techne/inventory.json interface/also fields "
                       "with EXACTLY ONE required positional parameter, called with a single "
                       "non-finite argument (nan, or [nan, 1.0, -1.0] where the parameter name "
                       "or annotation indicates a sequence). Full scan of the registry."),
        "command": "python techne/loop/measure_060_p4_arsenal.py",
        "modules_probed": len(eps),
        "functions_considered": len(rows),
        "tally": tally,
        "dropped_arity": [f"{r['module']}::{r['function']}" for r in rows
                          if r["outcome"] == "DROPPED_ARITY"],
        "module_timeouts": timeouts,
        "accepts_nonfinite_returns_a_value": leaking,
        "outside_the_height_family": outside,
        "n_outside_the_height_family": len(outside),
        "rows": rows,
    }
    dest = REPO / "techne" / "loop" / "rung_notes" / "cycle_060_p4_arsenal.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
