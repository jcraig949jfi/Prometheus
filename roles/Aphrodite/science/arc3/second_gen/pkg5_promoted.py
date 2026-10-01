"""PKG-5 (forensic, 1 core): promote G2 = (v - (acc + {H})) to a one-node primitive
P2(x). A G3 candidate wrap(P2({H}), op, atom) then has node-depth 2, so {H} ranges over
LEVEL1 fillers (depth <= 1) WITHOUT the depth-3 in-space restriction (bodies are
evaluated directly). For each G3 candidate: extent (accumulating instances), grid- and
trajectory-novelty vs G2's span (ruler v2 functions, reference = G2 instances + conj),
and the T4 family-admissibility rate. Compared with G3 in plain W5 (G3_REACH.json)."""
import json, random, sys
from pathlib import Path
ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG)); sys.path.insert(0, str(ENG.parent / "science" / "compounding" / "rb1"))
import a18, fair as FR, engine as E, basis_v4 as G, tier3d as T3D, tribunal_t4 as T4  # noqa
import ruler_v2 as R  # noqa
a18.use_world("W5")
G2 = "(v - (acc + {H}))"
P2 = lambda x: "(v - (acc + %s))" % x
g2_inst = T3D.instantiate(G2)
sp = R.span(g2_inst)
tsp = R.traj_span(g2_inst)
finals = [f for f in G.FINAL_SPACE if "acc" in f]
rng = random.Random("APHRODITE/ARC3/PKG5/v1")
rows = []
for _n, (_f, tmpl) in sorted(E.PRIMITIVES.items()):
    for a in G.BODY_ATOMS:
        for side in (0, 1):
            bodies = []
            for f in FR.LEVEL1:
                b = tmpl.format(P2(f), a) if side == 0 else tmpl.format(a, P2(f))
                bodies.append(b)
            acc = [b for b in bodies if R.accumulating(b)]
            nov = [b for b in acc if R.vec(b) not in sp and R.fclass(b) != "ADDITIVE"]
            tn = [b for b in acc if any(R.traj_nondegenerate(R.traj(b, i)) and R.traj(b, i) not in tsp for i in ("0", "1"))]
            adm = 0
            samp = rng.sample(acc, min(20, len(acc))) if acc else []
            for b in samp:
                adm += T4.family_profile(("fold", rng.choice(G.H1_SPACE), b, rng.choice(finals)))["admissible"]
            rows.append({"g3": (tmpl.format("P2({H})", a) if side == 0 else tmpl.format(a, "P2({H})")),
                         "extent_acc": len(acc), "novel_grid": len(nov), "novel_traj": len(tn),
                         "NEW": len(nov) >= 2 and len(tn) >= 2 and len(nov) >= 0.1 * max(1, len(acc)),
                         "T4_admissible_rate": round(adm / len(samp), 2) if samp else 0.0})
good = [r for r in rows if r["NEW"] and r["extent_acc"] >= 20 and r["T4_admissible_rate"] >= 0.25]
print("G3 candidates", len(rows), "| NEW & extent>=20 & T4>=.25:", len(good))
for r in sorted(good, key=lambda r: -r["extent_acc"])[:12]:
    print("  ", r)
Path(__file__).with_name("PKG5_PROMOTED.json").write_text(json.dumps({"rows": rows, "good": good}, indent=1))
