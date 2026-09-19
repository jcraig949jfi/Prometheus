"""P-J06 [T-X17; requires P-J03]: GATEWAY STRUCTURE. Descendants that carried conditional machinery (P-J03's
scaffolded lineage after the xor-15 stage, S2; WITNESS-SEEDED, flagged) face NOVEL conditional transforms
never used in their evolution: regime 1 expects (v + 1) mod 16 (a different operator) and v XOR 5 (a
different constant), 60 generations, 2 seeds, against the plateau-ladder lineage (P2) and a fresh walker
population. Readouts: generation of first crossing, top-4 held-out; REUSE read by intervention on crossed
tops: unread words at the answering OUT, regime registers at the OUT (P-J02's probes), control-instruction
knockouts. Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
import evolver as EV           # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-J02"))
sys.path.insert(0, str(HERE.parent / "P-J04"))
from run_PJ02 import reached_out, probe_out   # noqa: E402
from run_PJ04 import knockouts                # noqa: E402
A, L = CM.A, CM.L
PID, TID, G = "P-J06", "T-X17", 60
TRANSFORMS = ("add:1", "xor:5")
STORE = {"held": []}


def stage(init, seed, transform, label):
    STORE["held"] = []
    sets = CE.held_sets("A", seed, transform=transform)

    def hook(g, pop, evs):
        i = int(np.argmax([e["reward_per_ask"] for e in evs]))
        STORE["held"].append(round(CE.held_reward(pop[i]["m"], sets), 3))
    r = CE.run_world("A", seed, G=G, init=init, label=label, transform=transform, on_generation=hook)
    g_cross = next((g for g, h in enumerate(STORE["held"]) if h >= CE.THRESH["A"]), None)
    return {"transform": transform, "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best_held": r["tops"][0]["held"], "crossed": CE.crossed(r), "g_cross": g_cross, "held_by_gen": STORE["held"][::5], "tops": r["tops"][:4], "sets": sets}


def reuse_probe(m, sets):
    pos, a, ch = reached_out(m, sets[0])
    if pos is None:
        return {"reached_out": None}
    pr = probe_out(m, pos, a, sets)
    ko = knockouts(m, sets[0], set())
    base = CW.reward(m, sets[0])
    return {"reached_out": pos, "out_reg": a, "unread_at_out": pr["unread_at_out_mean"], "literal_regime_regs": pr["literal_regime_registers_at_out"], "xval_regime_regs": [x["reg"] for x in pr["xval_regime_registers_at_out"]],
            "control_knockouts": [(k["i"], k["op"], k["reward"]) for k in ko], "n_control_necessary": sum(1 for k in ko if k["reward"] < base - 0.2)}


def job(j):
    pops = j["pops"]
    init = pops if j["lineage"] != "fresh" else EV.init_population()[0]
    st = stage(init, 400 + j["seed"], j["transform"], "nestor.pj06|%s|%s" % (j["lineage"], j["transform"]))
    out = {"lineage": j["lineage"], "seed": j["seed"], **{k: v for k, v in st.items() if k not in ("tops", "sets")}}
    if st["crossed"]:
        out["reuse"] = [reuse_probe(t["m"], st["sets"]) for t in st["tops"][:2]]
    return out


def main():
    t0 = time.time()
    with gzip.open(HERE.parent / "P-J03" / "populations.json.gz", "rt", encoding="utf-8") as fh:
        pops = json.load(fh)
    lin = {}
    for p in pops:
        for k, v in p["pops"].items():
            lin[(k, p["seed"])] = v
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J03"], "scope": CM.SCOPE, "claim_type": "gateway-test", "FLAG": "the scaffolded lineage is witness-seeded (P-J03)",
                         "lineages": {"S2": "P-J03 scaffolded after the xor-15 stage", "P2": "P-J03 plateau ladder after the xor-15 stage", "fresh": "init walkers"}, "transforms": TRANSFORMS, "G": G, "seeds": [1, 2],
                         "readouts": "g_cross, top-4 held-out; reuse probes on crossed tops (unread words at OUT, regime registers at OUT, control knockouts)",
                         "gateway_rule": "S2 crosses a novel transform that P2 and fresh do not, or crosses it earlier", "material_rule": "material if any lineage crosses any novel transform", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"lineage": ln, "seed": s, "transform": tr, "pops": lin.get((ln, s))} for ln in ("S2", "P2", "fresh") for s in (1, 2) for tr in TRANSFORMS]
    with A.pool(12) as ex:
        rows = list(ex.map(job, jobs))
    table = {"%s|s%d|%s" % (r["lineage"], r["seed"], r["transform"]): {"top4_held": round(r["top4_held"], 3), "crossed": r["crossed"], "g_cross": r["g_cross"]} for r in rows}
    crossed = {ln: {tr: [r["crossed"] for r in rows if r["lineage"] == ln and r["transform"] == tr] for tr in TRANSFORMS} for ln in ("S2", "P2", "fresh")}
    g_cross = {ln: {tr: [r["g_cross"] for r in rows if r["lineage"] == ln and r["transform"] == tr] for tr in TRANSFORMS} for ln in ("S2", "P2", "fresh")}
    gateway = any(any(crossed["S2"][tr]) and not any(crossed["P2"][tr]) and not any(crossed["fresh"][tr]) for tr in TRANSFORMS)
    material = any(any(v) for c in crossed.values() for v in c.values())
    summary = {"FLAG": "witness-seeded scaffold", "table": table, "crossed": crossed, "g_cross": g_cross, "gateway_rule_met": bool(gateway), "reuse": [r.get("reuse") for r in rows if r.get("reuse")]}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": rows, "material": bool(material), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "gateway structure (novel transforms add:1 / xor:5; witness-seeded flag): crossings %s; g_cross %s; gateway rule met %s; reuse probes %s" % (crossed, g_cross, gateway, summary["reuse"][:2]), bool(material), detail=summary)
    L.append_evidence("T-X21", PID, "cross: novel conditional transforms after a scaffold: %s" % crossed, bool(material))
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps({k: v for k, v in summary.items() if k != "table"}, default=CM.js)[:1500])
    print(json.dumps(table)[:1500])


if __name__ == "__main__":
    main()
