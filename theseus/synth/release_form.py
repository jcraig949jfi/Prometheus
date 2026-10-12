"""THESEUS-50: is the FORM of a generated law (multi-source react into the sensor channel)
the release machinery?

Prereg: roles/Theseus/prereg/2026-10-10_release_form/PREREG.md.

Part A (no new task runs): per solver of 48, F = number of rules with op "react", dst 0 and
>= 2 distinct source channels (MULTI-SOURCE SENSOR-WRITING REACT). Written to FORM.jsonl.
Part B: on the 49 recipients and the IDENTICAL donor draws (release_swap's rng 20261012 and
sorted pools), a SINGLE variant: the donor law cut to one source -- its first source channel
that is not the sensor (channel 0) taken mod the recipient's C (channel 1 if none) -- keeping
amp, bias and that source's gain. Appended as the last rule; J at V8 k8 (task seed 0).

  python -m theseus.synth.release_form --tag release_form_2026-10-10 [--workers 4]
"""

import argparse
import copy
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import release_swap as rs  # noqa: E402
from . import sel_eval as se  # noqa: E402
from . import task_comp as tcm  # noqa: E402


def multi_sensor_react(g):
    return sum(1 for r in g["rules"] if r["op"] == "react" and r["dst"] == 0 and len(set(r["src"])) >= 2)


def single(rule, C):
    srcs = list(rule["src"])
    k = next((i for i, s in enumerate(srcs) if int(s) % C != 0), None)
    ch = int(srcs[k]) % C if k is not None else (1 % C)
    gain = rule["p"][2 + k] if k is not None else rule["p"][2]
    return {"op": "react", "src": [ch], "dst": 0, "p": [rule["p"][0], rule["p"][1], gain],
            "prov": "single|" + str(rule.get("prov", ""))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    tab = [json.loads(l) for l in open("theseus/runs/store_release_2026-10-10/TABLE.jsonl", encoding="utf-8")]
    genomes = {r: dict(se.sample(r)) for r in sorted({x["run"] for x in tab})}
    with open(f"{out}/FORM.jsonl", "w", encoding="utf-8") as f:
        for x in tab:
            g = genomes[x["run"]][x["id"]]
            f.write(json.dumps({"run": x["run"], "id": x["id"], "arm": x["arm"], "stratum": x["stratum"],
                                "F": multi_sensor_react(g), "J_store": x["J_store"], "J_release": x["J_release"]},
                               separators=(",", ":")) + "\n")
    # identical donor construction and draws to release_swap
    donors = {s: [] for s in (1, 2, 3, 4)}
    for x in sorted(tab, key=lambda x: (x["run"], x["id"])):
        if x["arm"] == "law" and x["J_release"] >= 0.6:
            KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{rs.KO_DIR[x['run']]}/KO_{x['run']}.jsonl", encoding="utf-8")}
            g = genomes[x["run"]][x["id"]]
            for i in KO[x["id"]]["essential"]:
                rule = g["rules"][i]
                if "law:" in str(rule.get("prov")) and rule["dst"] == 0:
                    donors[x["stratum"]].append({"donor": f"{x['run']}:{x['id']}:{i}", "rule": rule})
    rng = np.random.default_rng(20261012)
    recips = sorted([x for x in tab if x["arm"] == "nolaw" and x["J_store"] >= 0.6 and x["J_release"] < 0.6],
                    key=lambda x: (x["run"], x["id"]))
    items = []
    for x in recips:
        pool = donors[x["stratum"]]
        pick = rng.choice(len(pool), size=min(rs.N_DONORS, len(pool)), replace=False)
        g = genomes[x["run"]][x["id"]]
        for j, k in enumerate(sorted(int(v) for v in pick)):
            h = copy.deepcopy(g)
            h["rules"] = g["rules"] + [single(pool[k]["rule"], g["C"])]
            items.append((f"{x['run']}:{x['id']}:{j}:SINGLE", h))
    with Pool(a.workers) as pool:
        done = tcm._stage(pool, f"{out}/ROWS.jsonl", items, rs.J8)
    print(json.dumps({"recipients": len(recips), "evaluated": len(done)}))


if __name__ == "__main__":
    main()
