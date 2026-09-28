"""PLAN s5 on SUCCESS champions (+ n1_s2 near-miss, labelled). GPU under lease."""
import json, sys
import numpy as np, torch
import nback as nb
import carriers as cr
from prometheus.ananke import lens, plants
torch.set_num_threads(2)
nb.install()
ph = nb.m2()[0]
seeds = nb.seeds(nb.NS, 0xCA, M=64)
dev = sys.argv[1] if len(sys.argv) > 1 else "cuda"
inv = {v: k for k, v in plants.OPS.items()}
rm = {v: k for k, v in plants.regmap(ph).items()}
res = {}
for tag in ["n1_s0", "n1_s3", "n2_s1", "n2_s2", "n1_s2"]:
    d = json.load(open(nb.HERE / "out" / f"search_{tag}.json"))
    n = d["n"]
    g = np.asarray(d["evolve"]["champion"], dtype=np.int64)
    r = {"SUCCESS": d["held_5F3"]["SUCCESS"]}
    r["back0"] = cr.table(ph, g, n, seeds, device=dev)
    if n == 2:
        r["back1"] = cr.table(ph, g, n, seeds, device=dev, back=1, resets=False)
    # per-trial accuracy profile (normal run)
    env = nb.spec(n)
    base = lens.run(ph, g, env, seeds, ep=nb.build_nback(ph, env, seeds), device=dev)
    r["per_trial"] = [float(x) for x in np.nanmean(np.where(base.ep.scored, base.per_trial, np.nan), 0)]
    # decompile (fields pre-reduced as in the engine)
    NW, NR = ph.n_write(), ph.n_read()
    prog = []
    for i, (op, dd, a, b, imm) in enumerate(g[0]):
        prog.append(f"{i:2d} {inv[op % 16]:7s} {rm.get(dd % NW, dd % NW)} <- {rm.get(a % NR)}, {rm.get(b % NR)} (bf={b}) imm={imm}")
    r["program"] = prog
    res[tag] = r
    short = {k: (v.get("verdict"), round(v["acc"][0], 3)) if isinstance(v, dict) and "acc" in v else v
             for k, v in r["back0"].items()}
    print(tag, json.dumps(short), flush=True)
    if n == 2:
        print(tag, "back1", json.dumps({k: (v.get("verdict"), round(v["acc"][0], 3)) if isinstance(v, dict) and "acc" in v else v for k, v in r["back1"].items()}), flush=True)
    print(tag, "per_trial", [round(x, 2) for x in r["per_trial"]], flush=True)
    print("\n".join(prog), flush=True)
(nb.HERE / "out" / "carriers_champs.json").write_text(json.dumps(res, indent=1))
