"""W3 PART 1c -- the ruler GRID assumes acc >= 0. How often do folds on the ruler's own
trajectory battery reach acc < 0, and how many accumulating instances that the grid calls
ADDITIVE (hence excluded from novelty as 'G1's idea') stop being additive once acc < 0 is
allowed? Random W5 schemas from W3_BASERATE_ROWS_W5_200.json. Single core.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine" / "accel"))
import a18                  # noqa: E402
a18.use_world("W5")
import ruler_v2 as R        # noqa: E402
import tier3d as T3D        # noqa: E402
import fasteval as FE       # noqa: E402

NEG = (-1, -2, -5, -13, -97, -1000)


def additive_neg(b):
    fn = FE.fn(b)
    for v in R.VS:
        for f in R.FIRSTS:
            for l in R.LASTS:
                ds = set()
                for a in (0,) + NEG:
                    try:
                        y = fn(a, v, f, l)
                    except Exception:  # noqa: BLE001
                        return False
                    if y is None:
                        return False
                    ds.add(y - a)
                if len(ds) != 1:
                    return False
    return True


def neg_reached(b, init):
    """does the fold reach acc < 0 on some battery input?"""
    fn = FE.fn(b)
    for x in R._traj_inputs():
        acc = int(init)
        vals, first, last = x[:-1], x[0], x[-1]
        for v in vals:
            try:
                acc = fn(acc, v, first, last)
            except Exception:  # noqa: BLE001
                break
            if acc is None or abs(acc) > R.CEIL:
                break
            if acc < 0:
                return True
    return False


rows = json.loads((HERE / "W3_BASERATE_ROWS_W5_200.json").read_text())
n_acc = n_add = n_add_broken = n_negreach = 0
sch_affected = []
g1_neg = sum(neg_reached(b, "0") for b in T3D.instantiate("(acc + {H})"))
for r in rows:
    inst = [b for b in T3D.instantiate(r["schema"]) if R.accumulating(b)]
    broken = 0
    for b in inst:
        n_acc += 1
        nr = neg_reached(b, "0") or neg_reached(b, "1")
        n_negreach += nr
        if R.fclass(b) == "ADDITIVE":
            n_add += 1
            if not additive_neg(b) and nr:
                n_add_broken += 1
                broken += 1
    if broken:
        sch_affected.append({"schema": r["schema"], "additive_on_grid_not_below_zero_and_reached": broken,
                             "accumulating": len(inst)})
out = {"accumulating_instances": n_acc, "reach_acc_below_zero_on_battery": n_negreach,
       "grid_ADDITIVE": n_add, "grid_ADDITIVE_but_not_additive_for_acc<0_and_fold_reaches_acc<0": n_add_broken,
       "schemas_affected": len(sch_affected), "examples": sch_affected[:10],
       "G1_instances_reaching_acc<0_init0": g1_neg, "G1_instances": len(T3D.instantiate("(acc + {H})"))}
(HERE / "W3_DOMAIN_W5.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "examples"}, indent=1))
print(out["examples"][:5])
