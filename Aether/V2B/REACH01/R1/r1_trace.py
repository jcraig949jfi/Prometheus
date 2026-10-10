"""REACH01 R1 causal-depth assay: the qualified PROP01 paired-world tracer (prop01_run.run_unit, unchanged code) driven
with the R1 law set (V1, X, R, RX from r1_test4.law_step, which reproduces aeth03_variants bit-for-bit).

Modes (one unit JSON each, schema aether.prop01.unit.v1 so prop01_reduce applies):
  uncut   payload bit-0 impulse at the rng(0x1A9F+k) origin after WARM ticks, H ticks in lockstep
  cut     clamp B (earliest gen-1 site with a STRUCT/CARRY child, from the uncut tree) to CONTROL from its first
          divergence tick
  nonanc  NON-ANCESTOR CONTROL: clamp a site that is NOT in the impulse tree, at the same Chebyshev distance from the
          origin as B (first in raster scan), from the same tick. B's descendants must still diverge.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "PROP01"))
import prop01_run as P  # noqa: E402
import prop01_tree as TR  # noqa: E402
import r1_test4 as T  # noqa: E402

P.LAWS = dict(T.LAWS)
P.law_step = lambda xp, K, law, n, seed, tick, s: T.law_step(xp, K, law, n, seed, tick, s)
P.RUNNER_VERSION = "prop01_run.v1 via r1_trace.v1"


def nonanc_site(unit, b, n):
    o = unit["origin"]
    oy, ox = divmod(o, n)
    by, bx = divmod(b, n)
    d = max(min((by - oy) % n, (oy - by) % n), min((bx - ox) % n, (ox - bx) % n))
    tree = set(unit["tree"]["site"])
    for y in range(oy - d, oy + d + 1):
        for x in range(ox - d, ox + d + 1):
            if max(abs(y - oy), abs(x - ox)) != d:
                continue
            s = (y % n) * n + (x % n)
            if s not in tree:
                return s
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--law", required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--warm", type=int, default=1000)
    ap.add_argument("--H", type=int, default=3000)
    ap.add_argument("--mode", choices=["uncut", "cut", "nonanc"], default="uncut")
    ap.add_argument("--from-uncut", default=None)
    ap.add_argument("--backend", default="gpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        return 0
    cs = ct = None
    if a.mode != "uncut":
        u = json.load(open(a.from_uncut))
        b, ct = TR.choose_cut(u)
        if b is None:
            json.dump({"schema": "aether.prop01.unit.v1", "law": a.law, "seed_index": a.seed_index, "cut": None,
                       "mode": a.mode, "note": "no qualifying generation-1 site with children"}, open(a.out, "w"))
            return 0
        cs = b if a.mode == "cut" else nonanc_site(u, b, a.n)
        if cs is None:
            json.dump({"schema": "aether.prop01.unit.v1", "law": a.law, "seed_index": a.seed_index, "cut": None,
                       "mode": a.mode, "note": "no non-ancestor site at B's distance"}, open(a.out, "w"))
            return 0
    res = P.run_unit(a.backend, a.law, a.seed_index, a.n, a.warm, a.H, cs, ct)
    res["mode"] = a.mode
    if a.mode != "uncut":
        res["cut"]["B"] = b
    tmp = a.out + ".partial"
    json.dump(res, open(tmp, "w"), separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done", a.law, a.seed_index, a.mode, res["ever_sites"], res["max_gen"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
