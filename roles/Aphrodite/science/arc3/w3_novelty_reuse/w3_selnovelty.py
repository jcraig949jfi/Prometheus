"""W3 -- NOVELTY of the C2 G1 selections under the frozen ruler and under a None-tolerant
trajectory criterion (<= 25% None allowed; the T29 product limit). Forensic."""
import json, os, sys
from pathlib import Path
os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "engine" / "accel"))
import a18; a18.use_world("W5")
import ruler_v2 as R, tier3d as T3D
G1 = "(acc + {H})"
sp = R.span_of_schema(G1); tsp = R.traj_span(R.reexpression_bodies(G1))
def tol_nd(t, k=5, tol=0.25):
    vals = [x for x in t if x is not None]
    return len(t) - len(vals) <= tol * len(t) and len(set(vals)) >= k
out = {}
for s in ["math.gcd(abs(first), abs((acc + {H})))", "(v - (acc + {H}))", "(first + (acc + {H}))", "((acc + {H}) * v)"]:
    inst = T3D.instantiate(s); acc = [b for b in inst if R.accumulating(b)]
    v = R.verdict_full(s, G1, sp, tsp, inst)
    tn = [b for b in acc if any(tol_nd(R.traj(b, i)) and R.traj(b, i) not in tsp for i in ("0", "1"))]
    none_frac = [sum(x is None for x in R.traj(b, "1")) / 80 for b in acc]
    out[s] = {"NEW_FINAL": v["NEW_FINAL"], "NEW_V2": v["NEW_V2"], "novel_traj": v["novel_traj"], "acc": len(acc),
              "novel_traj_tol25": len(tn), "NEW_with_tol25": v["NEW"] and len(tn) >= 2 and len(tn) >= 0.1 * len(acc),
              "median_none_frac": sorted(none_frac)[len(none_frac) // 2] if none_frac else None}
    print(s, out[s])
(HERE / "W3_SELECTION_NOVELTY.json").write_text(json.dumps(out, indent=1))
