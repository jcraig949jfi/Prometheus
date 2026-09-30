"""W3 -- CON1 forensic: is the CON1 G1 selection (v - (acc + {H})) novel relative to
SHAM_0 = (v - (acc - {H})) (the panel schema whose group supplied the solved families)?
Ruler v2 with SHAM_0 as reference (its own re-expression closure), plus raw overlap of
the two instance sets' folded trajectories. Forensic."""
import json, os, sys
from pathlib import Path
os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine")); sys.path.insert(0, str(ROOT / "engine" / "accel"))
import a18; a18.use_world("W5")
import ruler_v2 as R, tier3d as T3D
S, SH = "(v - (acc + {H}))", "(v - (acc - {H}))"
out = {}
for a, b in ((S, SH), (SH, S)):
    sp = R.span_of_schema(b); tsp = R.traj_span(R.reexpression_bodies(b))
    v = R.new_v2(a, sp, exclude_classes=())
    t = R.new_traj(a, tsp)
    ia = [x for x in T3D.instantiate(a) if R.accumulating(x)]
    tb = {R.traj(x, i) for x in T3D.instantiate(b) for i in ("0", "1")}
    shared = sum(1 for x in ia if R.traj(x, "0") in tb and R.traj(x, "1") in tb)
    out["%s vs ref %s" % (a, b)] = {"accumulating": len(ia), "grid_novel": v["novel"], "traj_novel": t["novel_traj"],
                                     "NEW_V2": v["NEW_V2"], "NEW_TRAJ": t["NEW_TRAJ"],
                                     "instances_with_both_trajectories_in_ref_instance_set": shared,
                                     "relations": R.relations(a, b)}
    print(a, "vs", b, out["%s vs ref %s" % (a, b)])
(HERE / "W3_CON1_VS_SHAM0.json").write_text(json.dumps(out, indent=1))
