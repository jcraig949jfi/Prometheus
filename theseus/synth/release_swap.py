"""THESEUS-49: causal release swap -- does a donor's essential release law rescue release?

Prereg: roles/Theseus/prereg/2026-10-10_release_swap/PREREG.md.

Recipients: every no-law solver of 48 (theseus/runs/store_release_2026-10-10/TABLE.jsonl) that is
store-intact (J_store >= .6) and release-fail (J_release < .6) at V 8, k 8.
Donor laws: from law-on solvers of the SAME seed stratum with J_release >= .6 at V 8, every
essential rule (task_comp knockouts) with 'law:' provenance and dst == 0 (a sensor-writing law).
Per recipient, 3 donor laws drawn without replacement (rng 20261012, sorted pools).
For each (recipient, donor law):
  SWAP     the donor law appended as the recipient's last rule (src channels taken mod the
           recipient's C; dst 0)
  CONTROL  the same rule with its per-source gains sign-flipped and permuted (rng 20261013):
           same op, same sources, same amplitude/bias, scrambled coupling
J at V 8, k 8, sensor readout, task seed 0 (task_comp/task_J protocol).

  python -m theseus.synth.release_swap --tag release_swap_2026-10-10 [--workers 4]
"""

import argparse
import copy
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import probe_store as ps  # noqa: E402
from . import sel_eval as se  # noqa: E402
from . import task_comp as tcm  # noqa: E402
from . import task_system as ts  # noqa: E402

KO_DIR = {r: d for _, _, r, d in ps.SOURCES}
N_DONORS = 3


def J8(g):
    return ts.task_J(g, V=8, k=8, seed=0, readout="ch0")["J"]


def adapt(rule, C):
    r = copy.deepcopy(rule)
    r["src"] = [int(s) % C for s in r["src"]]
    r["dst"] = 0
    r["prov"] = "swap|" + str(r.get("prov", ""))
    return r


def scramble(rule, rng):
    r = copy.deepcopy(rule)
    g = [-x for x in r["p"][2:]]
    r["p"] = r["p"][:2] + [g[i] for i in rng.permutation(len(g))]
    r["prov"] = "ctrl|" + str(r.get("prov", ""))
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    tab = [json.loads(l) for l in open("theseus/runs/store_release_2026-10-10/TABLE.jsonl", encoding="utf-8")]
    genomes = {}
    for r in {x["run"] for x in tab}:
        genomes[r] = dict(se.sample(r))
    donors = {s: [] for s in (1, 2, 3, 4)}
    for x in sorted(tab, key=lambda x: (x["run"], x["id"])):
        if x["arm"] == "law" and x["J_release"] >= 0.6:
            KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{KO_DIR[x['run']]}/KO_{x['run']}.jsonl", encoding="utf-8")}
            g = genomes[x["run"]][x["id"]]
            for i in KO[x["id"]]["essential"]:
                rule = g["rules"][i]
                if "law:" in str(rule.get("prov")) and rule["dst"] == 0:
                    donors[x["stratum"]].append({"donor": f"{x['run']}:{x['id']}:{i}", "rule": rule})
    rng, crng = np.random.default_rng(20261012), np.random.default_rng(20261013)
    items = []
    recips = sorted([x for x in tab if x["arm"] == "nolaw" and x["J_store"] >= 0.6 and x["J_release"] < 0.6],
                    key=lambda x: (x["run"], x["id"]))
    for x in recips:
        pool = donors[x["stratum"]]
        pick = rng.choice(len(pool), size=min(N_DONORS, len(pool)), replace=False)
        g = genomes[x["run"]][x["id"]]
        for j, k in enumerate(sorted(int(v) for v in pick)):
            d = pool[k]
            sw = copy.deepcopy(g)
            sw["rules"] = g["rules"] + [adapt(d["rule"], g["C"])]
            ct = copy.deepcopy(g)
            ct["rules"] = g["rules"] + [adapt(scramble(d["rule"], crng), g["C"])]
            base = f"{x['run']}:{x['id']}:{j}"
            items.append((base + ":SWAP", sw))
            items.append((base + ":CTRL", ct))
    meta = {"recipients": len(recips), "donor_pool": {s: len(v) for s, v in donors.items()}}
    json.dump(meta, open(f"{out}/META.json", "w"), indent=1)
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{out}/ROWS.jsonl", items, J8)
    print(json.dumps({**meta, "evaluated": len(done)}))


if __name__ == "__main__":
    main()
