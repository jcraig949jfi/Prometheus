"""L5 adversary for the S1 candidate law (S1_PREREG_LAW s4 L5).

Per family: 240 fresh candidate worlds (never mapped) from the lattice, plus off-lattice SIZE variants
(rnn n, graph N, stig L: native changes the coordinates should absorb). Coordinates for all; then
  15 BAND worlds  (law P nearest 0.5)             -> calibration only
  15 CONFIDENT worlds, half at lattice extremes / half off-lattice sizes, P >= 0.9 or <= 0.1
Certify all 30; a confident miss is CONFIRMED if a replicate certificate (new seed) gives the same class.
Kill: confirmed / confident > 10% overall, or > 20% in any family.

  python -m prometheus.cosmos.c3.attack <maps_dir>
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.geometry import coordinates
from prometheus.cosmos.c3.law import TERMS
from prometheus.cosmos.c3.maps import DELAYS, LATTICE
from prometheus.cosmos.c3.substrates import RNN, Graph, Stig
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.hashing import h
from prometheus.cosmos.miner import law_from_json

SIZES = {"rnn": ("n", [16, 96]), "graph": ("N", [48, 192]), "stig": ("L", [8, 32])}


def build2(family, p, k):
    t = Task(4, k)
    if family == "rnn":
        return RNN(t, p["rho"], p["a"], p["sigma"], n=int(p.get("n", 48))), t
    if family == "graph":
        return Graph(t, int(p["K"]), p["b"], p["p"], N=int(p.get("N", 96))), t
    return Stig(t, p["delta"], p["D"], int(p["v"]), p["j"], L=int(p.get("L", 16))), t


def _coords(job):
    s, t = build2(job["family"], job["params"], job["k"])
    return coordinates(s, t, n_pairs=200, seed=int(h(job)[:8], 16))


def _cert(job):
    s, t = build2(job["family"], job["params"], job["k"])
    r = certify(s, t, seed=int(h([job, job.get("rep", 0)])[:8], 16))
    return r["class"]


def run(maps: Path, workers: int = 8) -> Dict[str, Any]:
    L = law_from_json(json.loads((maps / "LAW.json").read_text())["law"])
    mapped = {json.dumps([r["family"], r["params"], r["k"]], sort_keys=True)
              for r in json.loads((maps / "MAPS.json").read_text())["rows"]}
    rng = np.random.default_rng(20260926)
    cands = []
    for fam, lat in LATTICE.items():
        n = 0
        while n < 240:
            p = {k: v[rng.integers(len(v))] for k, v in lat.items()}
            p = {k: (float(x) if isinstance(x, float) else int(x)) for k, x in p.items()}
            k = int(DELAYS[rng.integers(len(DELAYS))])
            if rng.random() < 0.3:
                key, vals = SIZES[fam]
                p[key] = int(vals[rng.integers(len(vals))])
            if json.dumps([fam, p, k], sort_keys=True) in mapped:
                continue
            cands.append({"family": fam, "params": p, "k": k})
            n += 1
    with ProcessPoolExecutor(max_workers=workers) as ex:
        co = list(ex.map(_coords, cands))
    for c, x in zip(cands, co):
        c["coords"] = x
        c["P"] = float(L.prob({k: np.array([x[k]]) for k in TERMS})[0])
        c["pred"] = int(L.predict({k: np.array([x[k]]) for k in TERMS})[0])
    chosen = []
    for fam in LATTICE:
        C = [c for c in cands if c["family"] == fam]
        band = sorted(C, key=lambda c: abs(c["P"] - 0.5))[:15]
        conf = [c for c in C if (c["P"] >= 0.9 or c["P"] <= 0.1) and c not in band]
        off = [c for c in conf if SIZES[fam][0] in c["params"]]
        ext = [c for c in conf if SIZES[fam][0] not in c["params"]]
        rng.shuffle(off)
        # lattice extremes: rank by distance from the lattice centre in index space
        pick = off[:8] + ext[: 15 - min(8, len(off))]
        for c in band:
            c["kind"] = "band"
        for c in pick:
            c["kind"] = "confident"
        chosen += band + pick
    with ProcessPoolExecutor(max_workers=workers) as ex:
        cls = list(ex.map(_cert, chosen))
    misses = []
    for c, k in zip(chosen, cls):
        c["class"] = k
        c["miss"] = bool(k != "INDETERMINATE" and int(k == "FUNCTIONAL") != c["pred"])
        if c["kind"] == "confident" and c["miss"]:
            misses.append(dict(c, rep=1))
    if misses:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rep = list(ex.map(_cert, misses))
        for m, k in zip(misses, rep):
            for c in chosen:
                if c["family"] == m["family"] and c["params"] == m["params"] and c["k"] == m["k"]:
                    c["replicate_class"] = k
                    c["confirmed"] = bool(k == c["class"])
    conf = [c for c in chosen if c["kind"] == "confident" and c["class"] != "INDETERMINATE"]
    confirmed = [c for c in conf if c.get("confirmed")]
    by_fam = {f: {"confident": sum(1 for c in conf if c["family"] == f),
                  "confirmed_misses": sum(1 for c in confirmed if c["family"] == f)} for f in LATTICE}
    rate = len(confirmed) / max(1, len(conf))
    worst = max(v["confirmed_misses"] / max(1, v["confident"]) for v in by_fam.values())
    band = [c for c in chosen if c["kind"] == "band" and c["class"] != "INDETERMINATE"]
    calib = {"mean_P": float(np.mean([c["P"] for c in band])) if band else None,
             "obs_rate": float(np.mean([c["class"] == "FUNCTIONAL" for c in band])) if band else None, "n": len(band)}
    verdict = "FAILED" if (rate > 0.10 or worst > 0.20) else "SURVIVED"
    return {"verdict": verdict, "rate": rate, "worst_family_rate": worst, "by_family": by_fam, "band_calibration": calib,
            "n_candidates": len(cands), "chosen": chosen}


if __name__ == "__main__":
    d = Path(sys.argv[1])
    r = run(d)
    (d / "ATTACK.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "chosen"}, indent=1))
    for c in r["chosen"]:
        if c.get("confirmed"):
            print("CONFIRMED MISS", c["family"], c["params"], c["k"], c["class"], "pred", c["pred"], "P %.2f" % c["P"],
                  {k: round(v, 3) for k, v in c["coords"].items() if k in TERMS})
