"""C0s: post-freeze stress on the frozen law (roles/Cosmos/campaigns/c0s/PREREG.md).

  python -m prometheus.cosmos.stress <c0b_campaign_out_dir> <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.adversary import attack
from prometheus.cosmos.boundary import scan
from prometheus.cosmos.campaign0 import build_pools
from prometheus.cosmos.contract import coords_of
from prometheus.cosmos.miner import law_from_json
from prometheus.cosmos.pipeline import Chamber
from prometheus.cosmos.store import Store
from prometheus.cosmos.substrates import visible
from prometheus.cosmos.world import world_id


def pool_rows(fams, pools):
    out = {}
    for f, P in pools.items():
        rows = []
        for i, p in enumerate(P):
            if f == "regs" and i % 2 == 1:
                p = dict(p, code=3)
            rows.append({"family": f, "world_id": world_id(fams[f], p), "params": p,
                         "coords": coords_of(fams[f], p, "v1"), "coords_v2": coords_of(fams[f], p, "v2"),
                         "coords_v3": coords_of(fams[f], p, "v3")})
        out[f] = rows
    return out


def s1(c0b: Path, out: Path):
    st = Store(c0b / "store")
    law_row = [l for l in st.laws() if l["freeze_hash"]][0]
    L = law_from_json(law_row["body"]["law"])
    fams = visible()
    pools = pool_rows(fams, build_pools(fams, 1200, 20260926))
    ch = Chamber(list(fams.values()), store=st, campaign="c0s")
    rounds = []
    for r in range(4):
        st.event(law_row["law_id"], "ATTACKED", "c0s stress round %d" % r)
        rep = attack(L, ch, pools, np.random.default_rng(20260930 + r), per_family=60, law_id=law_row["law_id"],
                     cmap=law_row["body"]["cmap"])
        st.event(law_row["law_id"], "SURVIVED" if rep["verdict"] == "SURVIVED" else "FAILED",
                 "c0s round %d: %d/%d confirmed" % (r, rep["n_confirmed"], rep["n_confident"]))
        st.receipts.append("c0s_round", {"round": r, "verdict": rep["verdict"], "n_confirmed": rep["n_confirmed"],
                                         "n_confident": rep["n_confident"]})
        st.commit()
        rounds.append(rep)
        print("round", r, rep["verdict"], rep["n_confirmed"], "/", rep["n_confident"], rep["by_family"], flush=True)
    (out / "S1_stress.json").write_text(json.dumps(rounds, indent=1, default=str), encoding="utf-8")
    return rounds


def s2(out: Path):
    fams = visible()
    cells = []
    specs = {
        "regs": (dict(H=16, K=7, R=1.0, q=0.0), "bitcost", lambda p, v: v * np.log2(p["V"]) * p["H"] / p["R"]),
        "ring": (dict(H=12, K=5, R=1.0, s=1, n=64, lam=0.0), "ehop", lambda p, v: v * p["s"] * p["H"] / p["R"]),
        "ca": (dict(H=20, K=8, R=2.0, r=1, Lc=510, p=0.0), "ccell", lambda p, v: v * np.log2(p["V"]) * p["r"] * p["H"] / p["R"]),
    }
    for f, (base, knob, to_c) in specs.items():
        for V in (2, 4, 16):
            p = dict(base, V=V)
            G = 1 - 1 / V
            c_lo, c_hi = 0.2 * G, 1.3 * G
            v_lo, v_hi = c_lo / to_c(p, 1.0), c_hi / to_c(p, 1.0)
            vals = list(np.geomspace(v_lo, v_hi, 15))
            r = scan(fams[f], dict(p, **{knob: vals[0]}), knob, vals, episodes=(1600,), replicates=6, campaign="c0s-s2")
            x0 = r["per_E"]["1600"]["x0"]
            c_star = to_c(p, x0)
            cells.append({"family": f, "V": V, "G": G, "C_star": c_star, "law_ceiling": G - 0.055, "econ_ceiling": G - 0.10,
                          "near_econ": abs(c_star - (G - 0.10)) <= 0.02, "near_law": abs(c_star - (G - 0.055)) <= 0.02,
                          "width_log": r["per_E"]["1600"]["width_log"]})
            print(cells[-1], flush=True)
    n_ok = sum(c["near_econ"] and not c["near_law"] for c in cells)
    res = {"cells": cells, "n_supporting_bias": n_ok, "prediction_held": n_ok >= 7}
    (out / "S2_ceiling.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"n_supporting_bias": n_ok, "prediction_held": n_ok >= 7}))
    return res


if __name__ == "__main__":
    c0b, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    which = sys.argv[3] if len(sys.argv) > 3 else "both"
    if which in ("s2", "both"):
        s2(out)
    if which in ("s1", "both"):
        s1(c0b, out)
