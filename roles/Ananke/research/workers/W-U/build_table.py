"""Merge out/fc_w*.json + out/reach_w*.json; apply the frozen PLAN s4 selection; write
out/fc_table.json (all candidates, CIs) and out/rel3_table.json (the selected rule's table)."""
import glob
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-Q"))
import swap_rel2 as s2  # noqa: E402

PS = (8, 16, 32, 64, 128, 256)
KS = (3, 11, 12)
MODELS = ("worst", "realistic", "hetero")
VS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
CANDS = ("PCT", "BCA", "BOOTT", "TINT", "XPCT")
SIMPLE = ("TINT", "XPCT", "PCT", "BCA", "BOOTT")
ALL = CANDS + ("T90",)


def wilson(k, n, z=2.5758):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


fc = {}
for f in glob.glob(str(HERE / "out" / "fc_w*.json")):
    fc.update(json.load(open(f)))
rc = {}
for f in glob.glob(str(HERE / "out" / "reach_w*.json")):
    rc.update(json.load(open(f)))
missing = [f"P{P}_K{K}_{m}" for P in PS for K in KS for m in MODELS
           if len(fc.get(f"P{P}_K{K}_{m}", {})) != len(s2.FC_GRID)]
print("missing FC jobs:", missing)

T = {}   # T[c][P_K] = {pass, fc_max:{V:(fc, lo, hi, n, model, p)}, fails:[...]}
for c in ALL:
    T[c] = {}
    for P in PS:
        for K in KS:
            d = {"pass": True, "fc_max": {}, "fails": [], "robust": True, "stage2_points": 0}
            for v in VS:
                best = None
                for m in MODELS:
                    for p, r in fc.get(f"P{P}_K{K}_{m}", {}).items():
                        k, n = r["k"][c][v], r["n"]
                        d["stage2_points"] += r["stage2"] and v == "FLIP_REL"
                        x = (k / n, *wilson(k, n), n, m, p)
                        if best is None or x[0] > best[0]:
                            best = x
                        if k / n > 0.01:
                            d["pass"] = False
                            d["fails"].append((v, m, p, round(k / n, 5), n))
                        if wilson(k, n)[1] > 0.01:
                            d["robust"] = False
                d["fc_max"][v] = best
            T[c][f"P{P}_K{K}"] = d


def p_floor(c):
    fl = None
    for P in PS[::-1]:
        if all(T[c][f"P{P}_K{K}"]["pass"] for K in KS):
            fl = P
        else:
            break
    return fl


sel_power = {}
if "SEL" in rc:
    for c in ALL:
        xs = [rc["SEL"][m][p][c][v] for m in ("worst", "realistic") for p in rc["SEL"][m] for v in VS]
        sel_power[c] = sum(xs) / len(xs)
floors = {c: p_floor(c) for c in ALL}
print("P_floor:", floors)
print("selection power P64 K11:", {c: round(x, 4) for c, x in sel_power.items()})
elig = [c for c in CANDS if floors[c] is not None]
best_floor = min(floors[c] for c in elig) if elig else None
tier = [c for c in elig if floors[c] == best_floor]
winner = None
if tier and sel_power and best_floor <= 64:
    top = max(sel_power[c] for c in tier)
    near = [c for c in tier if sel_power[c] >= top - 0.01]
    winner = min(near, key=SIMPLE.index)
elif tier:
    winner = min(tier, key=SIMPLE.index)
print("tier:", tier, "WINNER:", winner)


def p_min(curve, v):
    pm = 1.01
    for p in sorted(curve, key=float, reverse=True):
        if curve[p][v] < 0.80:
            break
        pm = float(p)
    return pm


designs = {}
for P in PS:
    for K in KS:
        key = f"P{P}_K{K}"
        d = {"cert_ok": {v: bool(winner and T[winner][key]["fc_max"][v] and T[winner][key]["fc_max"][v][0] <= 0.01 and P >= best_floor) for v in VS},
             "fc_max": {v: T[winner][key]["fc_max"][v] for v in VS} if winner else None}
        if key in rc and winner:
            cur = {m: {p: rc[key][m][p][winner] for p in rc[key][m]} for m in ("worst", "realistic")}
            d["p_min_model"] = {m: {v: p_min(cur[m], v) for v in VS} for m in cur}
            d["p_min"] = {v: max(d["p_min_model"][m][v] for m in cur) for v in VS}
        designs[key] = d
json.dump({"T": T, "floors": floors, "sel_power": sel_power, "winner": winner, "missing": missing},
          open(HERE / "out" / "fc_table.json", "w"), indent=1)
json.dump({"METHOD": winner, "P_FLOOR": best_floor, "designs": designs}, open(HERE / "out" / "rel3_table.json", "w"),
          indent=1)
for c in ALL:
    print(f"\n== {c} floor={floors[c]}")
    for P in PS:
        print(f"  P{P:3d} " + " | ".join(
            f"K{K:2d} {'PASS' if T[c][f'P{P}_K{K}']['pass'] else 'FAIL'}{'r' if T[c][f'P{P}_K{K}']['robust'] else ' '} "
            + " ".join(f"{v[0]}{T[c][f'P{P}_K{K}']['fc_max'][v][0]*100:.2f}" for v in VS if T[c][f'P{P}_K{K}']['fc_max'][v]) for K in KS))
