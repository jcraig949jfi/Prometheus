"""B3g: where does the 'unaccounted' 13-46% of the B2 graphblas form's wall time go?

cProfile over run_gb at several sizes; every profiled function is assigned to ONE group
by its own name/module (tottime, i.e. time inside that function body, so nothing double
counts):
  kernel      SuiteSparse execution entered via graphblas expression .new / dup / <<
  convert     to_coo / from_coo and numpy conversions they call
  trace       the per-tick trajectory line (_line) and hashlib
  numpy_glue  numpy functions called directly from graphworld.py (setdiff1d, arange, ...)
  py_glue     pure-Python bytecode in graphworld.py itself (loops, dict/zip, Spec)
  gb_python   python-graphblas's own Python layer (expression building, dtype/mask checks)
  other       everything else (reported with its top functions)
Shares are tottime / total profiled time; cProfile's own overhead inflates small Python
calls, so the receipt compares groups, not absolute seconds.

usage: python -m primordial.soup.b3.glue --L 64,256 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import cProfile
import json
import pstats
from collections import Counter


def group(file: str, fn: str) -> str:
    f = file.replace("\\", "/").lower()
    if fn in ("_line",) or "hashlib" in f or fn in ("<built-in method _hashlib.openssl_sha256>",):
        return "trace"
    if "primordial/soup/b2/graphworld.py" in f:
        return "py_glue"
    if "graphblas" in f:
        if fn in ("to_coo", "from_coo", "_from_coo"):
            return "convert"
        if fn in ("new", "dup", "__lshift__", "_update", "update"):
            return "gb_python"
        return "gb_python"
    if "numpy" in f:
        return "numpy_glue"
    if f == "~" and "graphblas" in fn.lower():
        return "kernel"
    if f == "~" and ("_graphblas" in fn or "suitesparse" in fn.lower() or "cffi" in fn.lower()
                     or "lib." in fn or "GrB_" in fn or "GxB_" in fn):
        return "kernel"
    if f == "~" and ("numpy" in fn or "method 'astype'" in fn or "ufunc" in fn or "np." in fn):
        return "numpy_glue"
    return "other"


def profile_one(L: int) -> dict:
    from primordial.soup.b2.graphworld import Spec, run_gb
    e = max(8, (L * L) // 8)
    s = Spec(L=L, n_pred=e // 8, n_prey=3 * e // 8, n_food=e // 2, ticks=16, seed=L)
    run_gb(Spec(L=8, n_pred=1, n_prey=3, n_food=4, ticks=2, seed=1))       # warm imports outside the profile
    pr = cProfile.Profile()
    pr.enable()
    run_gb(s)
    pr.disable()
    st = pstats.Stats(pr)
    groups, total = Counter(), 0.0
    per_fn = []
    for (file, line, fn), (cc, nc, tt, ct, callers) in st.stats.items():
        g = group(file, fn)
        groups[g] += tt
        total += tt
        per_fn.append((tt, g, f"{file.split('/')[-1].split(chr(92))[-1]}:{line}:{fn}", nc))
    per_fn.sort(reverse=True)
    top_other = [x for x in per_fn if x[1] == "other"][:8]
    return {"L": L, "entities": s.n, "ticks": s.ticks, "profiled_total_s": total,
            "share": {g: round(v / total, 4) for g, v in groups.items()},
            "top_functions": [{"tottime_s": round(t, 4), "group": g, "fn": name, "calls": n}
                              for t, g, name, n in per_fn[:15]],
            "top_other": [{"tottime_s": round(t, 4), "fn": name, "calls": n} for t, _, name, n in top_other]}


def setup_share_unprofiled(L: int, reps: int = 5) -> dict:
    """No profiler: median wall of run_gb with ticks=0 (static relations + initial AT only)
    vs ticks=16. cProfile inflates the 262k tiny step_cell calls; this does not."""
    import time
    from primordial.soup.b2.graphworld import Spec, run_gb, run_ref
    e = max(8, (L * L) // 8)
    kw = dict(L=L, n_pred=e // 8, n_prey=3 * e // 8, n_food=e // 2, seed=L)
    run_gb(Spec(ticks=1, **kw))                                               # warm

    def med(f):
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter()
            f()
            ts.append(time.perf_counter() - t0)
        return sorted(ts)[reps // 2]

    t_setup = med(lambda: run_gb(Spec(ticks=0, **kw)))
    t_full = med(lambda: run_gb(Spec(ticks=16, **kw)))
    t_ref = med(lambda: run_ref(Spec(ticks=16, **kw)))
    # negative control for the subtraction method: the reference has (almost) no setup,
    # so its ticks=0 run must be a negligible share of its full run
    t_ref0 = med(lambda: run_ref(Spec(ticks=0, **kw)))
    n = Spec(ticks=16, **kw).n
    tick_only = max(t_full - t_setup, 1e-9)
    return {"L": L, "entities": n, "gb_setup_s": t_setup, "gb_full_s": t_full, "ref_full_s": t_ref,
            "ref_setup_s": t_ref0, "ref_setup_share": round(t_ref0 / t_ref, 4),
            "gb_setup_share": round(t_setup / t_full, 4),
            "gb_ent_ticks_per_s_with_setup": n * 16 / t_full,
            "gb_ent_ticks_per_s_ticks_only": n * 16 / tick_only,
            "ref_ent_ticks_per_s": n * 16 / t_ref}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", default="64,256")
    ap.add_argument("--setup-L", default="64,256,512,1024")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = [profile_one(int(x)) for x in a.L.split(",")]
    setup_rows = [setup_share_unprofiled(int(x)) for x in a.setup_L.split(",")]
    with open(a.out.replace(".jsonl", "-setup.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for r in setup_rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    for r in setup_rows:
        print(f"setup L={r['L']} n={r['entities']} gb_setup_share={r['gb_setup_share']:.1%} "
              f"gb with setup {r['gb_ent_ticks_per_s_with_setup']:,.0f} / ticks only "
              f"{r['gb_ent_ticks_per_s_ticks_only']:,.0f} / ref {r['ref_ent_ticks_per_s']:,.0f} ent-ticks/s")
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    for r in rows:
        print(f"L={r['L']} n={r['entities']} total={r['profiled_total_s']:.3f}s share={r['share']}")
        for f in r["top_functions"][:10]:
            print(f"    {f['tottime_s']:8.4f}s {f['group']:<11} {f['calls']:>7} {f['fn']}")
        if r["top_other"]:
            print("  top 'other':", [(o["fn"], o["tottime_s"]) for o in r["top_other"][:5]])


if __name__ == "__main__":
    main()
