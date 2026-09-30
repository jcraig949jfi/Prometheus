"""SPIKE K8 (= RB-3 Q1, analytic) -- does a composition move grow the derivable
NEW universe under inheritance? Coverage_C = L1 coverage + every in-space
instantiation of every wrap(G1, op, atom) schema (K6). Derivable universe =
single-hole, non-root LGGs of pairs with >= 1 composed body (pairs within the
old coverage are K3's). Compare NEW schemas against K3's L1/PRISTINE universe."""
import json, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
import a17, basis_v4 as G, fair as FR, identity as I, tier3d as T3D, tier3e as T3E  # noqa: E401,E402
HERE = Path(__file__).resolve().parent

def composed_bodies():
    rows = json.loads((HERE / "K6_COMPOUNDING.json").read_text())["rows"]
    out = []
    for r in rows:
        for f in FR.LEVEL1:
            b = T3D.in_space_body(r["schema"].replace("{H}", f))
            if b:
                out.append(b)
    return list(dict.fromkeys(out))

_ALL = None
def chunk(args):
    lo, hi, comp, allb = args
    tc = [I.normalise(I.parse(b)) for b in comp[lo:hi]]
    ta = [I.normalise(I.parse(b)) for b in allb]
    found = set()
    for a in tc:
        for b in ta:
            if a == b:
                continue
            g, t = T3D.lgg(a, b)
            if len(t) == 1 and not g[0].startswith("hole"):
                found.add(T3D.schema_src(g))
    return found

if __name__ == "__main__":
    L1 = a17.L1_entries()
    base = list(dict.fromkeys([b for e in L1 for b in e["bodies"]]))
    comp = [b for b in composed_bodies() if b not in set(base)]
    allb = base + comp
    print("base coverage", len(base), "composed new bodies", len(comp))
    step = max(1, len(comp) // 64)
    jobs = [(i, min(i + step, len(comp)), comp, allb) for i in range(0, len(comp), step)]
    found = set()
    with ProcessPoolExecutor(8) as ex:
        for s in ex.map(chunk, jobs):
            found |= s
    k3 = json.loads((HERE / "K3_DERIVABLE_UNIVERSE.json").read_text())
    old_new = {r["schema"] for r in k3["L1"]["new_examples"]}  # top-40 only; recompute set below
    rows = []
    for s in found:
        inst = T3D.instantiate(s)
        if len(inst) < 2:
            continue
        sn = T3E.semantically_new(s)
        rows.append({"schema": s, "inst": len(inst), "NEW": sn["SEMANTICALLY_NEW"], "n_new": sn["n_new_mechanism_bodies"],
                     "contains_G1": "(acc + {H})" in s or s.startswith("((acc + ") or "(acc + " in s})
    import k3_derivable_universe as K3
    pr = list(dict.fromkeys(FR.pristine().entries[0]["bodies"]))
    u_old = set(K3.universe(list(dict.fromkeys([b for e in L1 for b in e["bodies"]]))).keys())
    fresh = [r for r in rows if r["schema"] not in u_old]
    fresh_new = [r for r in fresh if r["NEW"]]
    print("schemas from composed pairs (>=2 inst):", len(rows), "| not in old L1 universe:", len(fresh),
          "| of which NEW by ruler:", len(fresh_new))
    for r in sorted(fresh_new, key=lambda r: -r["n_new"])[:30]:
        print("  ", r)
    Path(__file__).with_name("K8_COMPOSITION_UNIVERSE.json").write_text(json.dumps(
        {"base": len(base), "composed": len(comp), "rows": len(rows), "fresh": fresh, "fresh_new": len(fresh_new)}, indent=1))
