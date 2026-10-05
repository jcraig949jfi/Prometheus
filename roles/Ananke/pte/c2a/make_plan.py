"""PTE-C2A plan builder: admitted cells -> PLAN.json (cells + interleaved job list).

usage: python make_plan.py ADMISSION_DIR OUT_PLAN.json [--flight] [--n-per-family 4] [--arms SPEC]

Cell selection rule (declared before any search): per family, the admitted candidates in ascending candidate
index (the W2-AD sampler order is a seeded random draw over the C1 A0 dial ranges, so index order is outcome-
blind), first n. No anchors from C1 history: every core cell is fresh (never searched by C1).
Positive control: C1 cell d9cc RELAY d=3 delta=8 (ring N144 r3: the sensor is one transport hop away; C1 12/12
seeds SIGNAL), its C1 physics/env exactly, plant relay_flood (C1 plant), ruler RELAY-1h (SIGNAL).
--flight: same cells, but cell_key -> H(cell_key, FLIGHT) so no flight seed is a production seed.
Job order: rounds by seed index r = 0..11; within a round, cells interleave across families
(R1 F1 R2 F2 ... CTRL) and within a cell the arms run in the order PSEED, KSEED-1, KSEED-2, KSEED-4, BASE, W0,
M32 (each only while r < its n). A censoring wall therefore removes the highest seed indices of every arm first.
"""
import argparse
import glob
import gzip
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c2a_common as C  # noqa: E402
from prometheus.ananke import envs  # noqa: E402

FLIGHT = 0xF11647
CORE_ARMS = {"PSEED": 4, "KSEED-1": 4, "KSEED-2": 4, "KSEED-4": 4, "BASE": 12, "W0": 8, "M32": 8}
CTRL_ARMS = {"PSEED": 2, "BASE": 8}
ARM_ORDER = ["PSEED", "KSEED-1", "KSEED-2", "KSEED-4", "BASE", "W0", "M32"]
CTRL_CELL = ("d9cc", "RELAY", 3, 8)


def control_cell():
    rows = [json.loads(l) for l in gzip.open(C.ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
    for r in rows:
        if r["kind"] != "evolve":
            continue
        ph = C.Physics.from_dict(r["physics"])
        if (ph.digest()[:4], r["env"]["family"], r["env"]["d"], r["env"]["delta"]) == CTRL_CELL:
            return r, ph.validate()
    raise SystemExit("control cell not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adm"); ap.add_argument("out"); ap.add_argument("--flight", action="store_true")
    ap.add_argument("--n-per-family", type=int, default=4)
    ap.add_argument("--arms", default=None, help="JSON overriding CORE_ARMS counts (size rule s18)")
    ap.add_argument("--ctrl-arms", default=None)
    a = ap.parse_args()
    core_arms = dict(CORE_ARMS, **(json.loads(a.arms) if a.arms else {}))
    ctrl_arms = dict(CTRL_ARMS, **(json.loads(a.ctrl_arms) if a.ctrl_arms else {}))
    recs = []
    for p in glob.glob(os.path.join(a.adm, "*.jsonl")):
        recs += [json.loads(l) for l in open(p) if l.strip()]
    cells, rejected = [], []
    for fam, role in (("RELAY", "RELAY-mh"), ("FLIP", "FLIP")):
        fr = sorted([r for r in recs if r["family"] == fam], key=lambda r: r["i"])
        adm = [r for r in fr if r["verdict"] == "ADMITTED"]
        for r in fr:
            if r["verdict"] != "ADMITTED":
                rejected.append({"cid": r["cid"], "verdict": r["verdict"]})
        for r in adm[: a.n_per_family]:
            ph = C.Physics.from_dict(r["physics"]).validate()
            pn = r["plant_of_record"]
            key = C.H_int(C.C2A_NS, C.FAM_ID[fam], r["i"])
            cells.append({"cell_id": r["cid"], "family": fam, "role": role, "i": r["i"],
                          "physics": r["physics"], "env": r["env"], "plant_name": pn,
                          "plant_genome": C.PLANTS[fam][pn](ph).tolist(),
                          "cell_key": C.H_int(key, FLIGHT) if a.flight else key,
                          "ceiling": r["ceiling"], "binding": r["binding"], "hops": r["hops"],
                          "admission": {"plants": r["plants"], "adversaries": r["adversaries"],
                                        "V_scope": r.get("V_scope"), "thresholds": r["thresholds"]},
                          "arms": core_arms})
        print(fam, "admitted", len(adm), "of", len(fr), "-> selected", [r["cid"] for r in adm[: a.n_per_family]])
    r, ph = control_cell()
    env = envs.EnvSpec(**r["env"])
    plant = C.relay_flood(ph)
    seeds = C.assays.world_seeds(C.H_int(C.C2A_NS, C.ADMIT_KEY, 0xC0), 128)
    pt, ep = C.eval_programs(ph, env, seeds, [plant, C.null(ph)], device="cpu")
    pc, nc = C.competence("RELAY-1h", pt[0], ep), C.competence("RELAY-1h", pt[1], ep)
    key = C.H_int(C.C2A_NS, 0xC0, 1)
    cells.append({"cell_id": "CTRL-RELAY1h-" + r["cell_id"], "family": "RELAY", "role": "RELAY-1h", "i": None,
                  "physics": r["physics"], "env": r["env"], "plant_name": "relay_flood",
                  "plant_genome": plant.tolist(), "cell_key": C.H_int(key, FLIGHT) if a.flight else key,
                  "c1_history": "C1 d9cc RELAY d3 delta8: 12/12 seeds SIGNAL",
                  "admission": {"plant": C.slim(pc), "null": C.slim(nc)}, "arms": ctrl_arms})
    print("control plant", pc["status"], round(pc["all"]["mean"], 3), "null", nc["status"])
    order = [c for pair in zip([c for c in cells if c["role"] == "RELAY-mh"], [c for c in cells if c["role"] == "FLIP"])
             for c in pair]
    order += [c for c in cells if c["role"] in ("RELAY-mh", "FLIP") and c not in order]
    order += [c for c in cells if c["role"] == "RELAY-1h"]
    jobs = []
    for rnd in range(max(max(c["arms"].values()) for c in cells)):
        for c in order:
            for arm in ARM_ORDER:
                if rnd < c["arms"].get(arm, 0):
                    jobs.append({"job_id": f"{c['cell_id']}|{arm}|{rnd:02d}", "cell_id": c["cell_id"], "arm": arm,
                                 "idx": rnd})
    # held/train disjointness (asserted, operator order s4 RNG item): every held seed of every job vs every
    # training/final seed of every job in the plan, and vs every admission seed.
    from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS
    held, train = set(), set()
    for c in cells:
        for idx in range(max(c["arms"].values())):
            s = C.search_seed(c["cell_key"], idx)
            held.update(C.assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD))
            train.update(C.assays.world_seeds(C.H_int(s, FINAL_NS), 16))
            for gen in range(36):
                train.update(C.assays.world_seeds(C.H_int(s, TRAIN_NS, gen), 32))
    admitw = set()
    for c in cells:
        if c["i"] is not None:
            admitw.update(C.admit_seeds(c["family"], c["i"]))
    disj = {"held_n": len(held), "train_n": len(train), "admit_n": len(admitw),
            "held_x_train": len(held & train), "held_x_admit": len(held & admitw), "train_x_admit": len(train & admitw)}
    print("disjointness", disj)
    assert disj["held_x_train"] == 0 and disj["held_x_admit"] == 0, disj
    plan = {"schema": "pte_c2a.plan.v1", "flight": a.flight, "cells": cells, "jobs": jobs, "rejected": rejected,
            "disjointness": disj, "arms": {"core": core_arms, "control": ctrl_arms}, "arm_order": ARM_ORDER}
    C.jdump(a.out, plan)
    print("jobs", len(jobs), "cells", len(cells))


if __name__ == "__main__":
    main()
