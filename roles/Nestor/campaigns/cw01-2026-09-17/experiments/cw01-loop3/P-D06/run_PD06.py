"""P-D06 (T-X04): the founder-control SEPARATRIX at phi 0.5.

Items drawn from the legacy tree-native target with probability phi = 0.5 and from the graph
targets otherwise (P-A08's mixture); mixed populations seeded at TREE frequency .1...9, evolved 40
generations, recombination {0.5, 1.0}, 2 attempt ids. Final TREE frequency vs seeded frequency;
the unstable equilibrium is where final - f0 changes sign; bistable when low seeds fall and high
seeds rise.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID = "P-D06", "T-X04"
PHI, F0S, RATES, IDS, GENS = 0.5, tuple(round(0.1 * i, 1) for i in range(1, 10)), (0.5, 1.0), ["cw01-loop3-PD06-%d" % i for i in range(2)], 40
MIX = {"phi": PHI, "legacy": None}
_orig_make = W6.make_items


def make_items_mixed(cfg, rng, target):
    t = cfg["task"]
    lo, hi = t["input_domain"]
    graph_targets = target if isinstance(target, list) else [target]
    out = []
    for _ in range(t["items_per_episode"]):
        use_legacy = rng.random() < MIX["phi"]
        tt = graph_targets[int(rng.integers(0, len(graph_targets)))]
        x = [float(v) for v in rng.integers(lo, hi + 1, size=t["n_inputs"])]
        core = MIX["legacy"] if use_legacy else (tt["graph"] if (isinstance(tt, dict) and "graph" in tt) else tt)
        out.append((x, W6.target_eval(core, x)))
    return out


W6.make_items = make_items_mixed


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-map", "phi": PHI, "f0": F0S, "rates": RATES, "ids": IDS, "generations": GENS,
                         "unchanged": "e06 world, sharing, prices, tournament 3, P-A08's mixture construction",
                         "readout": "final TREE frequency vs f0 per (rate, id); separatrix = f0 interval where sign(final - f0) changes; bistable = final(.1) < .1 and final(.9) > .9 - .05",
                         "material_rule": "a separatrix located (exactly one sign change with falls below and rises above) in >= 2 of the 4 (rate, id) series, or bistability in >= 2"})
    rows = []
    for aid in IDS:
        cfg = L.load_cfg("cw01-e06", aid)
        MIX["legacy"] = W6.legacy_tree_target(cfg, S.seed)
        graph = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
        for rate in RATES:
            cfg = L.load_cfg("cw01-e06", aid)
            cfg["ecology"]["recombination_rate"] = rate
            for f0 in F0S:
                run = W6.evolve(cfg, "mixed_assortative", GENS, 96, S.seed, "%s|rr%.1f|f%.1f" % (aid, rate, f0), freq_first=f0, target=graph)
                rows.append({"aid": aid, "rate": rate, "f0": f0, "final": W6.final_frequency(run, "TREE"), "coexist": W6.coexisting(run), "traj": [round(h["freq_TREE"], 4) for h in run["history"]]})
                print("   %s rate %.1f f0 %.1f -> %.3f" % (aid[-1], rate, f0, rows[-1]["final"]), flush=True)
    series = {}
    for aid in IDS:
        for rate in RATES:
            rs = sorted([r for r in rows if r["aid"] == aid and r["rate"] == rate], key=lambda r: r["f0"])
            signs = [int(np.sign(r["final"] - r["f0"])) for r in rs]
            changes = [(rs[i]["f0"], rs[i + 1]["f0"]) for i in range(len(rs) - 1) if signs[i] != signs[i + 1]]
            bistable = rs[0]["final"] < 0.1 and rs[-1]["final"] > 0.85
            sep = changes[0] if (len(changes) == 1 and signs[0] < 0 and signs[-1] > 0) else None
            series["%s|%.1f" % (aid, rate)] = {"finals": [round(r["final"], 3) for r in rs], "signs": signs, "sign_changes": changes, "separatrix": sep, "bistable": bistable, "coexist": sum(r["coexist"] for r in rs)}
    n_sep = sum(1 for v in series.values() if v["separatrix"])
    n_bi = sum(1 for v in series.values() if v["bistable"])
    material = bool(n_sep >= 2 or n_bi >= 2)
    out = {"perturbation_id": PID, "parent": TID, "series": series, "n_separatrix": n_sep, "n_bistable": n_bi, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "separatrix map at phi .5: %s; separatrix located in %d/4, bistable %d/4" % ({k: (v["finals"], v["separatrix"], v["bistable"]) for k, v in series.items()}, n_sep, n_bi), material, detail=series)
    print("DONE material=%s sep %d bi %d (%.0f s)" % (material, n_sep, n_bi, time.time() - t0))


if __name__ == "__main__":
    main()
