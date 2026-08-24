"""Feed arsenal functions inputs their authors would not naturally write.

Cycle 059. The only method with a demonstrated record of finding shapes outside my own
taxonomy: cycle 058's S6 (non-termination) surfaced because a sweep passed k=0 to a function
whose author -- and whose reader -- had only ever considered positive integers.

DELIBERATELY DOES NOT JUDGE CORRECTNESS. It records STRUCTURAL outcomes only:

    HANGS   exceeded the per-call timeout          (S6)
    NAN     returned NaN without raising           (S5)
    RAISES  refused                                (the clean outcome for out-of-domain input)
    RETURNS produced a value

Those four are checkable WITHOUT an oracle, and therefore without the reader-supplied
specification that blocked cycles 057-058 from ever reporting a rate.

Each call runs in a subprocess with a hard timeout, because a hang in-process would take the
sweep with it -- which is exactly what happened when cycle 058 first hit k=0.
"""
from __future__ import annotations

import argparse
import inspect
import json
import math
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]

# Inputs chosen to be things an author would not naturally write.
PROBES: dict[str, list] = {
    "int":   [0, -1, 1, 2**63, -(2**63)],
    "float": [0.0, -1.0, float("nan"), float("inf"), -float("inf"), 1e308],
    "seq":   [[], [0], [0.0], [float("nan")], [1e308, -1e308]],
    "str":   ["", " "],
}


def _kind(param: inspect.Parameter) -> str:
    ann = param.annotation
    text = str(ann).lower()
    if "int" in text and "float" not in text:
        return "int"
    if "float" in text or "complex" in text:
        return "float"
    if any(t in text for t in ("list", "sequence", "iterable", "ndarray", "tuple")):
        return "seq"
    if "str" in text:
        return "str"
    return "seq"          # arsenal default: most take coefficient vectors


RUNNER = r'''
import json, math, sys
sys.path.insert(0, {repo!r})
mod = __import__({mod!r}, fromlist=["x"])
fn = getattr(mod, {fn!r})
arg = json.loads({arg!r})
if isinstance(arg, str) and arg in ("__nan__", "__inf__", "__ninf__"):
    arg = {{"__nan__": float("nan"), "__inf__": float("inf"),
            "__ninf__": -float("inf")}}[arg]
if isinstance(arg, list):
    arg = [float("nan") if x == "__nan__" else x for x in arg]
try:
    out = fn(arg)
except Exception as e:
    print("RAISES " + type(e).__name__); sys.exit(0)
try:
    if isinstance(out, float) and math.isnan(out):
        print("NAN"); sys.exit(0)
except Exception:
    pass
print("RETURNS " + repr(out)[:60])
'''


def _encode(v):
    if isinstance(v, float):
        if math.isnan(v):
            return "__nan__"
        if v == math.inf:
            return "__inf__"
        if v == -math.inf:
            return "__ninf__"
    if isinstance(v, list):
        return [("__nan__" if isinstance(x, float) and math.isnan(x) else x) for x in v]
    return v


def import_cost(module: str, cap: float = 90.0) -> float:
    """Seconds to import `module` in a fresh subprocess.

    CYCLE 059, CAUGHT BEFORE REPORTING: the first sweep flagged a pile of HANGS in
    `prometheus_math` that were nothing of the kind -- those modules initialise PARI and take
    ~12 s to IMPORT, against a 5 s timeout. Every one was import cost, not a function hang, and
    the tell was implausibility (`polynomial_length([0])` does not hang; it raises, correctly).

    So each module's budget is measured, not assumed. A timeout that does not separate setup
    from the thing under test measures the harness.
    """
    code = f"import sys; sys.path.insert(0, {str(REPO)!r}); __import__({module!r})"
    t = time.perf_counter()
    try:
        subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=cap)
    except subprocess.TimeoutExpired:
        return cap
    return time.perf_counter() - t


def call_isolated(module: str, fn: str, arg, timeout: float) -> str:
    # CYCLE 059, SECOND INSTRUMENT FAULT: this had json.dumps(json.dumps(...)). The RUNNER
    # applies ONE json.loads, so the extra encoding delivered the STRING "0.0" instead of the
    # float 0.0 -- to every function, in every call, in both sweeps. 128/128 RAISES was not a
    # clean arsenal; it was "you passed me a string" 128 times.
    code = RUNNER.format(repo=str(REPO), mod=module, fn=fn,
                         arg=json.dumps(_encode(arg)))
    try:
        p = subprocess.run([sys.executable, "-c", code], capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "HANGS"
    out = (p.stdout or "").strip().splitlines()
    if not out:
        return "CRASH " + (p.stderr or "").strip().splitlines()[-1][:60] if p.stderr else "CRASH"
    return out[-1]


def sweep(modules: list[str], timeout: float, limit_fns: int | None = None) -> list[dict]:
    rows = []
    for modname in modules:
        try:
            mod = __import__(modname, fromlist=["x"])
        except Exception:
            continue
        fns = [(n, f) for n, f in vars(mod).items()
               if inspect.isfunction(f) and not n.startswith("_")
               and f.__module__ == modname]
        if limit_fns:
            fns = fns[:limit_fns]
        budget = import_cost(modname) + timeout
        for name, f in fns:
            try:
                params = list(inspect.signature(f).parameters.values())
            except (ValueError, TypeError):
                continue
            required = [p for p in params
                        if p.default is inspect.Parameter.empty
                        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
            if len(required) != 1:
                continue                      # single-argument functions only, this pass
            for probe in PROBES[_kind(required[0])]:
                rows.append({"module": modname, "fn": name, "arg": repr(probe)[:24],
                             "outcome": call_isolated(modname, name, probe, budget),
                             "budget_s": round(budget, 1)})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modules", nargs="+", required=True)
    ap.add_argument("--timeout", type=float, default=5.0)
    ap.add_argument("--limit-fns", type=int, default=None)
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args()

    rows = sweep(a.modules, a.timeout, a.limit_fns)
    kinds: dict[str, int] = {}
    for r in rows:
        k = r["outcome"].split()[0]
        kinds[k] = kinds.get(k, 0) + 1
    report = {"command": f"--modules {' '.join(a.modules)} --timeout {a.timeout}",
              "n_calls": len(rows), "by_outcome": kinds,
              "hangs": [r for r in rows if r["outcome"] == "HANGS"],
              "nans": [r for r in rows if r["outcome"] == "NAN"],
              "rows": rows}
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
