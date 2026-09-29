"""W-H Part 2 arms A/B/C: bounded search per PLAN.md. GPU under lease.
Usage: python search_arms.py <cell_id> [<cell_id> ...]"""
import sys, json, time, pathlib, dataclasses
REPO = pathlib.Path(__file__).resolve().parents[5]; sys.path.insert(0, str(REPO))
import numpy as np, torch
from prometheus.ananke import c1b_run, assays, search, lens
from prometheus.ananke.rng import H_int

OUT = pathlib.Path(__file__).parent / "out"
DEV = "cuda" if torch.cuda.is_available() else "cpu"
AN = assays.world_seeds(0x5ED, 64)


def rescore(ph, g, env):
    r = assays.evaluate(ph, np.asarray(g)[None], env, AN, device=DEV)
    return lens.ci(r.pair_acc()[0])


def main(cids):
    for si, cid in enumerate(cids):
        ph, env, g, row = c1b_run.load(cid)
        sp = search.SearchSpec(**row["search"])
        R, L = ph.rules, ph.prog_len
        f = OUT / f"search_{cid[:8]}.json"
        res = json.loads(f.read_text()) if f.exists() else {}
        res["champion_analysis"] = rescore(ph, g, env)
        arms = {"A_orig": ph,
                "B_fixed_L": dataclasses.replace(ph, rules=1, setrule=0),
                "C_fixed_RL": dataclasses.replace(ph, rules=1, setrule=0, prog_len=R * L)}
        for an, p2 in arms.items():
            for k in range(4):
                key = f"{an}/{k}"
                if key in res:
                    continue
                seed = H_int(0x5ED, si, list(arms).index(an), k) & 0x7FFFFFFF
                t = time.time()
                o = search.evolve(p2, env, seed, sp, device=DEV)
                res[key] = {"seed": seed, "held": o["held"], "train_final": o["champ_train_final"],
                            "analysis": rescore(p2, o["champion"], env), "champion": o["champion"],
                            "curve_best": [c["best_acc"] for c in o["curve"]], "wall": time.time() - t}
                print(cid[:8], key, "held", round(o["held"]["acc"], 3), "an", [round(x, 3) for x in res[key]["analysis"]],
                      "wall", round(res[key]["wall"], 1), flush=True)
                f.write_text(json.dumps(res))


if __name__ == "__main__":
    main(sys.argv[1:])
