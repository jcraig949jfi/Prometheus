"""prov0 content assay (V2-B): track the payload lineage of N origin sites through a post-warm-up soup.

Same world construction as the twin assay (aeth03_propagation.assay): scouts' sparse soup, B-balanced energy,
warm-up with perturbation ON, then a followed window. Origins are drawn from the same emitter candidates (WRITE sites,
plus receipt-activated sites for the rcv family) with the same seeded rng. Then, instead of a twin pair per origin,
ONE provenance-shadowed run tracks up to 64 origins' payload lineages at once.

Per origin and horizon it reports the rung readings of aeth_prov.Provenance.rung_profile:
- holders: stored template values descending from the origin;
- carried_away: holders at another site (P3);
- transformed: holders whose value differs from the origin's (P4);
- composed: holders with two or more tracked lineages (P5);
- max_hops: rewrites survived (P6);
- max_distance: Chebyshev distance on the torus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from observatory import aeth03_propagation as PR           # noqa: E402
from observatory import aeth03_scouts as S                 # noqa: E402
from observatory import aeth03_variants as V               # noqa: E402
from observatory import aeth_prov as P                     # noqa: E402

HORIZONS = (10, 50, 100, 200, 400)


def prov_assay(variant, n=128, warmup=1500, ticks=400, origins=64, seed_index=0, arm="off"):
    seed, rng_seed = S.SEED0 + seed_index, S.RNG0 + seed_index
    rng = np.random.default_rng(0xB0A7 + seed_index)        # same origin draw as the twin assay
    t0 = time.time()
    fields = S.initial(variant, n, rng_seed)
    par_on = S.params(seed, S.MUT_ON)
    w = PR.World(variant, fields)
    for t in range(1, warmup + 1):
        w.step(t, par_on)
    if variant == "rcv_sfz":
        w.extra["aim_energy"] = w.f[4].copy()
    em = S.emitters(variant, w.f, par_on["write_cost"])
    if variant in V.RCV_FAMILY:
        em = em | (w.received & (w.f[4].astype(np.int64) >= par_on["write_cost"]))
    cand = np.argwhere(em)
    pick = cand[rng.choice(len(cand), min(origins, len(cand), 64), replace=False)]
    par = S.params(seed, 0 if arm == "off" else S.MUT_ON)
    pv = P.Provenance(variant, w.f, received_value=w.extra.get("received_value"))
    for (r, c) in pick:
        pv.track((int(r), int(c)), 3)                      # the origin's PAYLOAD value
    f = [x.copy() for x in w.f]
    rec = w.extra.get("received")
    rv = w.extra.get("received_value")
    rows = {}
    for k in range(1, ticks + 1):
        t = warmup + k
        obs = []
        kw = {}
        if variant in V.RCV_FAMILY:
            kw["received"] = rec
        if variant == "fwd":
            kw["received_value"] = rv
        if "aim_energy" in w.extra:
            kw["aim_energy"] = w.extra["aim_energy"]
        out = V.step(variant, H=n, W=n, tick=t, opcode=f[0], arg0=f[1], arg1=f[2], payload=f[3], energy=f[4],
                     observer=obs, **kw, **par)
        post = list(out[:5])
        pv.step(t, f, post, obs, par, received=rec if variant in V.RCV_FAMILY else None)
        f = post
        if variant in V.RCV_FAMILY:
            rec = out[5]["received"]
        if variant == "fwd":
            rv = out[5]["received_value"]
        if k in HORIZONS:
            rows[k] = [pv.rung_profile(b) for b, _ in pv.origins]
    return {"instrument": "aeth_prov_assay", "prov_version": P.PROV_VERSION, "variant": variant,
            "semantics_id": V.SEMANTICS_ID[variant], "n": n, "warmup": warmup, "ticks": ticks,
            "seed_index": seed_index, "arm": arm, "origins": [[int(r), int(c)] for r, c in pick],
            "horizons": {str(k): v for k, v in rows.items()}, "nodes": int(pv.n),
            "wall_seconds": round(time.time() - t0, 1)}


def summarize(res, dist=5, hops=5):
    """Per horizon: share of origins whose lineage is CARRIED (a holder at Chebyshev distance >= dist after
    >= hops rewrites), TRANSFORMED (any transformed holder), COMPOSED (any composed holder)."""
    out = {}
    for k, profs in res["horizons"].items():
        nO = len(profs) or 1
        out[k] = {"carried": sum(p["max_distance"] >= dist and p["max_hops"] >= hops for p in profs) / nO,
                  "transformed": sum(p["transformed"] > 0 for p in profs) / nO,
                  "composed": sum(p["composed"] > 0 for p in profs) / nO,
                  "alive": sum(p["holders"] > 0 for p in profs) / nO}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--law", required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--arm", choices=("off", "on"), default="off")
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--warmup", type=int, default=1500)
    ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--origins", type=int, default=64)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = prov_assay(a.law, a.n, a.warmup, a.ticks, a.origins, a.seed_index, a.arm)
    body = json.dumps({k: v for k, v in res.items() if k != "wall_seconds"}, sort_keys=True, separators=(",", ":"))
    res["result_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, sort_keys=True)
    print(json.dumps({"law": a.law, "seed_index": a.seed_index, "result_sha256": res["result_sha256"],
                      "summary": summarize(res), "wall_seconds": res["wall_seconds"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
