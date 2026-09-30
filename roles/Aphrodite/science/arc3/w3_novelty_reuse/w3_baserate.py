"""W3 PART 1b -- sensitivity of the RULER v2 random-schema NEW_FINAL base rate to its
conventions: proportion floor, minimum count, distinct-value criterion, battery length,
None tolerance, and the instantiation world (G4 vs W5).
Random schemas: the RB-1 junk generator (rb1_validate.junk) re-implemented with a
parameterised seed. Seed "APHRODITE/COMPOUNDING/RB1/JUNK/v1" with n=100 in G4 reproduces
RB-1's junk100 set exactly (checked below).
Single core. Usage: python w3_baserate.py <G4|W5> <n>
"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine" / "accel"))
import ruler_v2 as R        # noqa: E402
import basis_v4 as G        # noqa: E402
import identity as I        # noqa: E402
import tier3d as T3D        # noqa: E402
import fasteval as FE       # noqa: E402

G1 = "(acc + {H})"


def junk(n, seed="APHRODITE/COMPOUNDING/RB1/JUNK/v1"):
    rng = random.Random(seed)
    out = set()
    while len(out) < n:
        b = rng.choice(G.BODY_SPACE)
        t = I.normalise(I.parse(b))
        paths = []

        def walk(x, p):
            for i, a in enumerate(x[1]):
                paths.append(p + (i,))
                walk(a, p + (i,))
        walk(t, ())
        if not paths:
            continue
        path = rng.choice(paths)

        def put(x, p):
            if not p:
                return ("hole", [])
            op, args = x
            args = list(args)
            args[p[0]] = put(args[p[0]], p[1:])
            return (op, args)
        s = T3D.schema_src(put(t, path))
        if len(T3D.instantiate(s)) >= 2:
            out.add(s)
    return sorted(out)


BATTERIES = {"L2-10": (2, 10, 80), "L2-40": (2, 40, 80), "L2-200": (2, 200, 40)}


def battery(lo, hi, n):
    rng = random.Random("APHRODITE/COMPOUNDING/RULER_V2/TRAJ/v1/%d-%d-%d" % (lo, hi, n))
    return [[rng.randint(2, 30) for _ in range(rng.randint(lo, hi))] + [rng.randint(3, 97)] for _ in range(n)]


BAT = {k: battery(*v) for k, v in BATTERIES.items()}
BAT["L2-40"] = R._traj_inputs()          # the frozen battery itself


def tr(b, init, key):
    return tuple(FE.run_program(("fold", init, b, "acc"), x, True) for x in BAT[key])


def nondeg(t, k, tol):
    vals = [x for x in t if x is not None]
    return (len(t) - len(vals)) <= tol * len(t) and len(set(vals)) >= k


def main(world, n):
    if world == "W5":
        import a18
        a18.use_world("W5")
    sp = R.span_of_schema(G1)
    refb = R.reexpression_bodies(G1)
    tspan = {k: {tr(r, i, k) for r in refb for i in ("0", "1")} for k in BAT}
    schemas = junk(n)
    if world == "G4" and n == 100:
        rb1 = json.loads((ROOT / "science/compounding/rb1/RB1_RESULTS.json").read_text())
        ref = sorted(r["schema"] for r in rb1["rows"] if r["set"] == "junk100")
        print("reproduces RB-1 junk100:", ref == schemas, flush=True)
    rows = []
    for j, s in enumerate(schemas):
        inst = T3D.instantiate(s)
        acc = [b for b in inst if R.accumulating(b)]
        rel = R.relations(s, G1)
        per = []
        for b in acc:
            gn = R.vec(b) not in sp and R.fclass(b) != "ADDITIVE"
            d = {"g": gn}
            for key in BAT:
                ts = [tr(b, i, key) for i in ("0", "1")]
                for k in (2, 3, 5, 10):
                    for tol in (0.0, 0.25):
                        d["%s/k%d/tol%s" % (key, k, tol)] = any(
                            nondeg(t, k, tol) and t not in tspan[key] for t in ts)
            per.append(d)
        rows.append({"schema": s, "accumulating": len(acc), "REFINES": rel["REFINES"], "EQUAL": rel["EQUAL"],
                     "COMPOSES": rel["COMPOSES"], "per": per})
        if j % 20 == 0:
            print(world, j, s, len(acc), flush=True)
    (HERE / ("W3_BASERATE_ROWS_%s_%d.json" % (world, n))).write_text(json.dumps(rows))
    summarise(world, n, rows)


def verdict(row, floor, mincount, tkey, both):
    a = row["accumulating"]
    if a == 0 or row["REFINES"] or row["EQUAL"]:
        return False
    g = sum(p["g"] for p in row["per"])
    t = sum(p[tkey] for p in row["per"])
    ok = lambda c: c >= mincount and c >= floor * a   # noqa: E731
    if both:          # a stricter variant: the SAME instances must be grid- AND trajectory-novel
        gt = sum(p["g"] and p[tkey] for p in row["per"])
        return ok(gt)
    return ok(g) and ok(t)


def summarise(world, n, rows):
    out = {"world": world, "n": len(rows), "grid": []}
    for floor in (0.0, 0.05, 0.10, 0.20, 0.33, 0.50):
        for mc in (1, 2, 3):
            for key in BAT:
                for k in (2, 3, 5, 10):
                    for tol in (0.0, 0.25):
                        tk = "%s/k%d/tol%s" % (key, k, tol)
                        for both in (False, True):
                            c = sum(verdict(r, floor, mc, tk, both) for r in rows)
                            out["grid"].append({"floor": floor, "mincount": mc, "battery": key, "distinct": k,
                                                "none_tol": tol, "same_witness": both, "NEW": c,
                                                "rate": round(c / len(rows), 4)})
    base = [g for g in out["grid"] if g["floor"] == 0.10 and g["mincount"] == 2 and g["battery"] == "L2-40"
            and g["distinct"] == 5 and g["none_tol"] == 0.0 and not g["same_witness"]][0]
    out["frozen_convention"] = base
    rates = [g["rate"] for g in out["grid"]]
    out["range_all"] = [min(rates), max(rates)]
    (HERE / ("W3_BASERATE_%s_%d.json" % (world, n))).write_text(json.dumps(out, indent=1))
    print("frozen", base, "range", out["range_all"], flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "summ":
        w, n = sys.argv[2], int(sys.argv[3])
        summarise(w, n, json.loads((HERE / ("W3_BASERATE_ROWS_%s_%d.json" % (w, n))).read_text()))
    else:
        main(sys.argv[1], int(sys.argv[2]))
