"""Design-size control: the relative rule at W-L's OWN design (M=64 W-L seeds, trials 4,6,8)
vs at W-N's design; separates 'rule' from 'sample size' in the verdict change."""
import json, numpy as np, torch
torch.set_num_threads(2)
import plants_rel as pr, swap_rel as sr
pr.nb.install()
ph = pr.nb.m2()[0]
seeds = pr.nb.seeds(pr.nb.NS, 0xCA, M=64)
out = {}
for tag in ["n1_s0", "n1_s3", "n2_s1", "n2_s2"]:
    d = json.load(open(pr.WL / "out" / f"search_{tag}.json"))
    g = np.asarray(d["evolve"]["champion"], dtype=np.int64)
    env = pr.nb.spec(d["n"])
    ep, nrm, arms, _, _ = pr.run_fork(ph, g, env, seeds, ["S"], [4, 6, 8], offset=-1)
    v = sr.swap_verdict_rel(nrm, arms["S"])
    a = sr.absolute_verdict(nrm, arms["S"])
    out[tag] = {k: v[k] for k in ("normal", "swap", "DF", "DN", "p_min", "verdict", "verdict_ungated", "P", "K")}
    out[tag]["absolute"] = a
    print(tag, "n", [round(x, 3) for x in v["normal"]], "s", [round(x, 3) for x in v["swap"]], "pmin", v["p_min"],
          "REL", v["verdict"], "ungated", v["verdict_ungated"], "ABS", a, flush=True)
json.dump(out, open("out/wl_design.json", "w"), indent=1)
