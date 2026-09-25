"""Broker subprocess entry (COSMOS_BROKER=1 only). Reads a JSON request on a file, writes a JSON reply.

  selftest                 instrument controls on FIXED control worlds (not sealed worlds);
                           returns booleans only
  coords   spec            declared coordinates of the sealed worlds (spec-only; no runs)
  run      spec            certificates of the sealed worlds
  ladder   spec, jobs      certificates along intervention ladders
"""
from __future__ import annotations

import json
import sys

import importlib

from prometheus.cosmos.world import evaluate

FAMILIES = {"well": "prometheus.cosmos.holdout.well", "swarm": "prometheus.cosmos.holdout.swarm",
            "clone": "prometheus.cosmos.holdout.clone"}
CONTROL_WORLDS = {
    "well": [dict(V=4, T=5.0, K=2, R=1.0, A=4.0, sigma=0.1, kappa=1e-4),
             dict(V=8, T=2.0, K=4, R=3.0, A=8.0, sigma=0.1, kappa=1e-4)],
    "swarm": [dict(V=4, H=16, K=2, R=1.0, M=3, u=0.0, c_agent=1e-4, A_max=1000),
              dict(V=8, H=8, K=4, R=4.0, M=5, u=0.0, c_agent=1e-4, A_max=1000)],
    "clone": [dict(V=4, H=8, K=2, R=1.0, n0=4, b=0.0, d=0.0, c_cell=1e-4),
              dict(V=8, H=16, K=4, R=3.0, n0=2, b=0.0, d=0.0, c_cell=1e-4)],
}
D = None   # bound per request to the requested sealed family


def _campaign(spec):
    return "c0-holdout-" + spec["nonce"]


def selftest(name):
    out = {}
    for i, p in enumerate(CONTROL_WORLDS[name]):
        a = evaluate(D, p, campaign="selftest")
        b = evaluate(D, p, campaign="selftest")
        s = evaluate(D, D.sham(p), campaign="selftest")
        out["w%d" % i] = {"replay_identical": a["obs_digest"] == b["obs_digest"],
                          "positive_control_sel_acc_ge_0.95": a["acc"]["SEL"] >= 0.95,
                          "memoryless_below_0.5": a["acc"]["LAST"] < 0.5,
                          "sham_quiet": s["verdict"] == "QUIET"}
    return out


def main(req_path, reply_path):
    global D
    req = json.load(open(req_path))
    cmd = req["cmd"]
    name = req.get("family", "well")
    D = importlib.import_module(FAMILIES[name]).FAMILY
    if cmd == "selftest":
        rep = selftest(name)
    elif cmd == "coords":
        from prometheus.cosmos.contract import coords_of
        rep = [{"i": i, "coords": coords_of(D, p, req.get("cmap", "v1"))} for i, p in enumerate(req["spec"]["worlds"])]
    elif cmd == "run":
        rep = []
        for i, p in enumerate(req["spec"]["worlds"]):
            r = evaluate(D, p, campaign=_campaign(req["spec"]))
            rep.append({"i": i, "world_id": r["world_id"], "verdict": r["verdict"], "margin": r["margin"],
                        "se": r["margin_se"], "acc": r["acc"], "obs_digest": r["obs_digest"]})
    elif cmd == "ladder":
        rep = []
        for job in req["jobs"]:
            base = req["spec"]["worlds"][job["i"]]
            rows = []
            for f in job["factors"]:
                p = D.with_cost_factor(base, f)
                r = evaluate(D, p, episodes=job.get("episodes", 1600), campaign=_campaign(req["spec"]) + "-ladder")
                rows.append({"f": f, "coords": D.coords(p), "verdict": r["verdict"], "margin": r["margin"], "se": r["margin_se"]})
            rep.append({"i": job["i"], "rows": rows})
    elif cmd == "sample":
        # fresh candidate worlds for a salted protocol (e.g. G6b); spec-side only, no runs
        import hashlib
        import numpy as np
        from prometheus.cosmos.contract import coords_of
        spec = req["spec"]
        seed = int(hashlib.sha256((spec["nonce"] + req["salt"]).encode()).hexdigest(), 16) % (2 ** 63)
        rng = np.random.default_rng(seed)
        sp = D.space()
        sealed = {json.dumps(w, sort_keys=True) for w in spec["worlds"]}
        rep = []
        for i in range(req["n"]):
            w = {k: v[rng.integers(len(v))] for k, v in sp.items()}
            w = {k: (float(x) if isinstance(x, float) else int(x)) for k, x in w.items()}
            if json.dumps(w, sort_keys=True) in sealed:
                continue
            rep.append({"i": i, "params": w, "coords": coords_of(D, w, req.get("cmap", "v3"))})
    elif cmd == "ladder_params":
        from prometheus.cosmos.world import world_id
        rep = []
        for job in req["jobs"]:
            base = job["params"]
            key = world_id(D, base)
            rows = []
            for f in job["factors"]:
                p = D.with_cost_factor(base, f)
                r = evaluate(D, p, episodes=job.get("episodes", 1600), campaign=_campaign(req["spec"]) + "-" + req["salt"],
                             seed_key=key)
                rows.append({"f": f, "verdict": r["verdict"], "margin": r["margin"], "se": r["margin_se"],
                             "acc": r["acc"]})
            rep.append({"j": job["j"], "rows": rows})
    else:
        raise SystemExit("unknown cmd " + cmd)
    json.dump(rep, open(reply_path, "w"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
