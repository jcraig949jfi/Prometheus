import gzip, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from prometheus.ananke.physics import Physics
from prometheus.ananke import envs
import econ
rows = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
IDS = sys.argv[1].split(",")
out = {}
for c in IDS:
    r = [x for x in rows if x["cell_id"].startswith(c) and x["kind"]=="evolve"][0]
    ph = Physics.from_dict(r["physics"]); env = envs.EnvSpec(**r["env"])
    cE = ph.c_emit*ph.copies()
    line = []
    o = {}
    for m in (0, 1):
        for w, nm in ((env.period(), 1), (2, 1)):
            t = econ.row_table(ph, env, ks=range(0, 13), m=m, w=w, nmax=nm)
            # steady state = mean emissions over the second half of the episode
            ss = {k: round(float(v[len(v)//2:].mean()), 3) for k, v in t.items()}
            o[f"m{m}_w{w}"] = ss
    out[r["cell_id"]] = {"cE": cE, "mode": ph.update_mode, "P": ph.update_period, "p": ph.update_p,
                         "Pd": env.period(), "trials": env.trials, "tab": o}
    print(c, env.family, "cE", cE, ph.update_mode, ph.update_period if ph.update_mode=="sync" else ph.update_p, "Pd", env.period())
    for key, ss in o.items():
        print("   ", key, " ".join(f"{k}:{v:.2f}" for k, v in ss.items()))
json.dump(out, open(HERE/"out"/f"econ_{sys.argv[2]}.json","w"), indent=1)
