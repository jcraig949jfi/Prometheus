"""FORENSIC PILOT for AMENDMENT 18 (timing + wiring only; not a disposition).
Constructed supply in W5: sample composed-panel families + background, Q2
qualify (a17.qualify), then run DONOR_G1 (compose) and DONOR_P on one
replicate. Labels 'PILOT-C1'."""
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ENG = Path(__file__).resolve().parents[3] / "engine"
sys.path.insert(0, str(ENG))
os.environ["A17_FASTEVAL"] = "1"
os.environ["A18_TAG"] = "PILOT-C1"
import a17  # noqa: E402
import a18  # noqa: E402
import basis_v4 as G  # noqa: E402

HERE = Path(__file__).resolve().parent
LET = "abcdefghijklmnopqrstuvwxyz"


def qual(args):
    a18.worker_init()
    name, body, init, final = args
    prov = a17.Prov({name: (body, final, init)})
    a17.M.use_provider(prov)
    return name, a17.qualify(prov, name, "PILOT-C1")


if __name__ == "__main__":
    t0 = time.time()
    panel = a18.build_panel()
    sb = a18.supply_bodies(panel, ["G1", "SHAM_0", "SHAM_1", "SHAM_2"])
    rng = random.Random("APHRODITE/A18/PILOT/v1")
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    draws = []
    for k, bodies in sb.items():
        for j in range(10):
            draws.append(("pc%s%s" % (LET[len(draws) // 26], LET[len(draws) % 26]), rng.choice(bodies),
                          rng.choice(["0", "1"]), rng.choice(finals), k))
    with ProcessPoolExecutor(8, initializer=a18.worker_init) as ex:
        q = dict(ex.map(qual, [d[:4] for d in draws]))
    ok = [d for d in draws if q[d[0]] is not None]
    print("Q2 pass by source:", {k: sum(1 for d in ok if d[4] == k) for k in sb}, "t=%.0fs" % (time.time() - t0))
    obs = [d for d in ok if d[4] == "G1"][:2] + [d for d in ok if d[4] == "SHAM_0"][:2]
    val = [d for d in ok if d[4] == "G1"][2:4] + [d for d in ok if d[4] == "SHAM_1"][:2]
    fams = ([{"name": d[0], "role": "OBSERVE", "qualified_dev_size": q[d[0]]} for d in obs]
            + [{"name": d[0], "role": "VALIDATE", "qualified_dev_size": q[d[0]]} for d in val])
    specs = {d[0]: (d[1], d[3], d[2]) for d in obs + val}
    jobs = [("pilot", "G1", 0, fams, specs, panel, True), ("pilot", "P", 0, fams, specs, panel, True)]
    with ProcessPoolExecutor(2, initializer=a18.worker_init) as ex:
        res = list(ex.map(a18.donor, jobs))
    for r in res:
        print(r["donor"], "cands comp=%d lgg=%d" % (r["n_composed_candidates"], r["n_derived"]), "sel", r["selected"],
              r["selected_schema"], r["selected_origin"], "NOV", r["NOVELTY_vs_G1"], "COMP", r["COMPOSES_held"], "raw", r["n_composed_raw"],
              "secs", r["seconds"])
        top = sorted(r["selection_table"].items(), key=lambda kv: -kv[1]["mean_paired_saving"])[:4]
        print("   top", top)
    (HERE / "PILOT_C1.json").write_text(json.dumps({"panel": panel, "q": q, "donors": [
        {k: v for k, v in r.items() if k != "selected_entries"} for r in res]}, indent=1))
    print("total %.0fs" % (time.time() - t0))
