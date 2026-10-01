"""RB-1 validation: score known schema sets under the OLD ruler
(tier3e.semantically_new) and RULER v2, and report agreement and every class
of disagreement.
Sets: K3 PRISTINE universe (all single-hole LGGs of H2 pairs), K5 donor
candidates, K8 fresh composed schemas, 100 random single-hole junk schemas
(seeded), and the named cases."""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPK = HERE.parents[1] / "frontier" / "spikes"
ENG = HERE.parents[2] / "engine"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ENG))
sys.path.insert(0, str(SPK))
import ruler_v2 as R      # noqa: E402
import basis_v4 as G      # noqa: E402
import fair as FR         # noqa: E402
import identity as I      # noqa: E402
import tier3d as T3D      # noqa: E402
import tier3e as T3E      # noqa: E402

G1 = "(acc + {H})"


def junk(n=100):
    rng = random.Random("APHRODITE/COMPOUNDING/RB1/JUNK/v1")
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


TSP = None


def score(schemas, sp, tag):
    rows = []
    for s in schemas:
        inst = T3D.instantiate(s)
        if len(inst) < 2:
            continue
        old = T3E.semantically_new(s)["SEMANTICALLY_NEW"]
        new = R.verdict_full(s, G1, sp, TSP, inst)
        rel = {k: new[k] for k in ("REFINES", "COMPOSES", "EQUAL")}
        rows.append({"set": tag, "schema": s, "old_NEW": old, "NEW_V2": new["NEW_FINAL"], "grid_only_NEW": new["NEW"], "novel_traj": new["novel_traj"],
                     "accumulating": new["accumulating"], "novel": new["novel"],
                     "novel_classes": new["novel_classes"], **rel})
    return rows


if __name__ == "__main__":
    sp = R.span_of_schema(G1)
    TSP = R.traj_span(R.reexpression_bodies(G1))
    k3 = json.loads((SPK / "K3_DERIVABLE_UNIVERSE.json").read_text())
    import k3_derivable_universe as K3
    pr = list(dict.fromkeys(FR.pristine().entries[0]["bodies"]))
    universe = sorted(K3.universe(pr).keys())
    k5 = json.loads((SPK / "K5_SUPPLY_VS_MECHANISM.json").read_text())["rows"]
    k5c = sorted({c[0] for r in k5 for c in r["candidates"]})
    k8 = sorted({r["schema"] for r in json.loads((SPK / "K8_COMPOSITION_UNIVERSE.json").read_text())["fresh"]})
    named = [G1, "(acc - {H})", "({H} + acc)", "({H} + v)", "(acc * {H})", "math.gcd(abs(acc), abs({H}))",
             "(acc + math.gcd(abs({H}), abs(v)))", "((acc + {H}) * last)", "(0 // {H})", "({H} + first)"]
    rows = []
    for tag, ss in (("K3_universe", universe), ("K5_candidates", k5c), ("K8_fresh", k8),
                    ("junk100", junk()), ("named", named)):
        rows += score(ss, sp, tag)
    summ = {}
    for tag in sorted({r["set"] for r in rows}):
        rr = [r for r in rows if r["set"] == tag]
        c = Counter((r["old_NEW"], r["NEW_V2"]) for r in rr)
        summ[tag] = {"n": len(rr), "old_only": c[(True, False)], "v2_only": c[(False, True)],
                     "both": c[(True, True)], "neither": c[(False, False)],
                     "refines_G1": sum(r["REFINES"] for r in rr), "composes_G1": sum(r["COMPOSES"] for r in rr),
                     "v2_new_classes": dict(Counter(k for r in rr if r["NEW_V2"] for k in r["novel_classes"]))}
    # why old-only (false positives removed) and v2-only (new detections)
    reasons = Counter()
    for r in rows:
        if r["old_NEW"] and not r["NEW_V2"]:
            reasons["removed: accumulating<2 or novel<10% (" + ("few-acc" if r["accumulating"] < 2 else "in-span/edge") + ")"] += 1
        if r["NEW_V2"] and not r["old_NEW"]:
            reasons["added"] += 1
    out = {"summary": summ, "old_only_reasons": dict(reasons), "rows": rows,
           "k5_candidate_verdicts": [r for r in rows if r["set"] == "K5_candidates"]}
    (HERE / "RB1_RESULTS.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(summ, indent=1))
    print(dict(reasons))
    for r in out["k5_candidate_verdicts"]:
        print("K5 %-40s old=%-5s v2=%-5s acc=%3d novel=%3d refines=%s composes=%s" % (
            r["schema"], r["old_NEW"], r["NEW_V2"], r["accumulating"], r["novel"], r["REFINES"], r["COMPOSES"]))
