"""thr-c64dca3118a1 (replicator identity): does the block-13 transition -- a non-self-copying founder whose copy map reaches an
exact self-copier (a fixed point) -- recur?

Two populations, both ALREADY RECORDED (nothing re-simulated):
  CENSUS   archaeon/z80atlas/census/HITS.json vmcopy32: the 176 copier-like tapes found in 1e7 random tapes by the frozen census
  FOUNDERS archaeon/envgate/LINEAGES.json: the 475 ENVGATE-01 lineage founders (all blocks, all arms), with their lineage outcomes

For each tape T (isolated VM, zero neighbour, all 256 inputs -- the frozen ruler's convention):
  class(T) by the frozen ruler; T is a self-copier iff it writes an exact copy of itself on some input.
  copy map: for every input x on which T gives a birth (>= 0.9 of the window written), child_x = the written window.
  orbit: breadth-first over distinct children, up to DEPTH generations and WIDTH tapes per generation; the first depth at which a
  tape that is an exact self-copier appears is `fp_depth` (0 if T itself is one; None if not reached).
  fixed point in the strict sense: a child c with copy_x(c) == c on the same input x.
Output: per tape rows + summaries by class and, for founders, lineage outcome (births, peak, persistence) by fp_depth.
    python -m archaeon.attribution.probes.fixedpoint_census OUT.json [--depth 3] [--width 16]
"""
import json
import sys
import time
from collections import Counter, defaultdict

from archaeon.envgate import ruler as R
from archaeon.envgate.engine import ZERO, STEP_CAP
from archaeon.z80atlas import vm

G = 32


def births(t):
    """input -> child window, for inputs giving a birth; plus the set of inputs where the copy is exact."""
    out = {}; exact = []
    for x in range(256):
        r = vm.execute(t, ZERO, (x,), STEP_CAP, True, -1.0)
        if sum(r["nbr_mask"]) / G >= 0.9:
            out[x] = r["nbr_window"]
            if r["nbr_window"] == t: exact.append(x)
    return out, exact


def orbit(t, depth, width):
    b, ex = births(t)
    if ex: return {"fp_depth": 0, "strict_fp_depth": 0, "fp_tape": t.hex(), "n_birth_inputs": len(b)}
    frontier = [t]; seen = {t}; strict = None
    for d in range(1, depth + 1):
        nxt = []
        for u in frontier:
            bu, _ = births(u) if u != t else (b, ex)
            for x, c in bu.items():
                if c in seen: continue
                seen.add(c); nxt.append(c)
        nxt = nxt[:width]
        for c in nxt:
            bc, exc = births(c)
            if exc:
                return {"fp_depth": d, "strict_fp_depth": d, "fp_tape": c.hex(), "n_birth_inputs": len(b), "fp_class": R.measure(c)["class"],
                        "fp_diff_loci": [p for p in range(G) if c[p] != t[p]]}
        frontier = nxt
        if not frontier: break
    return {"fp_depth": None, "strict_fp_depth": None, "n_birth_inputs": len(b)}


def main(out, depth, width):
    t0 = time.time()
    hits = json.load(open("archaeon/z80atlas/census/HITS.json"))["hits"]["vmcopy32"]
    lin = json.load(open("archaeon/envgate/LINEAGES.json"))["lineages"]
    rows = []
    for h in hits:
        t = bytes.fromhex(h["tape"]); o = orbit(t, depth, width)
        rows.append({"pop": "CENSUS", "tape": h["tape"], "class": h["class"], **o})
    cache = {}
    for l in lin:
        tp = l["founder_tape"]
        if tp not in cache: cache[tp] = orbit(bytes.fromhex(tp), depth, width)
        rows.append({"pop": "FOUNDERS", "tape": tp, "class": l["founder_class"], "block": l["block"], "arm": l["arm"], "births": int(l["births"]),
                     "peak": int(l["peak"]), "max_gen": int(l["max_gen"]), "exact_fraction": float(l["exact_fraction"]),
                     "persistence_after_removal": int(l["persistence_after_removal"]), **cache[tp]})
    summ = {}
    for pop in ("CENSUS", "FOUNDERS"):
        by = defaultdict(Counter)
        for r in rows:
            if r["pop"] == pop: by[r["class"]][str(r["fp_depth"])] += 1
        summ[pop] = {k: dict(v) for k, v in by.items()}
    outc = defaultdict(list)
    for r in rows:
        if r["pop"] == "FOUNDERS": outc[str(r["fp_depth"])].append(r)
    summ["founder_outcomes_by_fp_depth"] = {k: {"n": len(v), "mean_births": round(sum(x["births"] for x in v) / len(v), 1),
                                                "mean_peak": round(sum(x["peak"] for x in v) / len(v), 1),
                                                "mean_max_gen": round(sum(x["max_gen"] for x in v) / len(v), 1),
                                                "peak_ge_64": sum(1 for x in v if x["peak"] >= 64)} for k, v in outc.items()}
    json.dump({"depth": depth, "width": width, "wall_s": round(time.time() - t0, 1), "summary": summ, "rows": rows}, open(out, "w"), indent=1)
    print(json.dumps(summ, indent=1)); print("wall_s", round(time.time() - t0, 1))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], int(a[a.index("--depth") + 1]) if "--depth" in a else 3, int(a[a.index("--width") + 1]) if "--width" in a else 16)
