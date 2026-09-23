"""Adversary: spends its budget trying to kill the current candidate law.

Attack classes (all on VISIBLE families; the holdout is never touched):
  band        worlds the law is least sure about (P in [0.25, 0.75]) -> calibration of the
              transition width, not counterexamples
  coordpres   microscopically different worlds with IDENTICAL declared coordinates (the family's
              coord_preserving() transforms) around confidently-predicted worlds: the law must
              predict the same verdict, so any confirmed flip is a counterexample against the
              COORDINATES, not just the threshold
  extreme     confidently-predicted pool worlds at the extremes of each coordinate
  errorseek   confidently-predicted pool worlds nearest to previously observed law errors
A contradiction (confident prediction, opposite observation) is CONFIRMED only if two fresh
replicates at 4x episodes also contradict and the margin is > 2 SE from 0.10 in both.
Verdict per round: FAILED if confirmed / confident attacks > KILL_RATE, else SURVIVED.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import coords_of, terminals_for
from prometheus.cosmos.miner import Law
from prometheus.cosmos.phenomenon import MARGIN
from prometheus.cosmos.sampler import feats

KILL_RATE = 0.05
CONF = 0.9


def _X(coords_list, cmap="v1"):
    return {k: np.array([c[k] for c in coords_list], float) for k in terminals_for(cmap)}


CKEY = {"v1": "coords", "v2": "coords_v2", "v3": "coords_v3"}


def attack(law: Law, chamber, pool: Dict[str, List[Dict[str, Any]]], rng, per_family: int = 40,
           law_id: str = "?", cmap: str = "v1") -> Dict[str, Any]:
    """cmap is the LAW's coordinate map: every prediction and every 'coordinate-preserving'
    claim is made in the law's own coordinates (defect I1 of C0 run 2)."""
    key = CKEY[cmap]
    fams = list(pool)
    attacks: List[Dict[str, Any]] = []
    meta: List[Dict[str, Any]] = []      # metamorphic pairs: equal declared coords, different microphysics
    skipped_not_preserving: List[Dict[str, Any]] = []
    prior = chamber.rows
    errs = [r for r in prior if bool(law.predict(_X([r[key]], cmap))[0]) != bool(r["y"])]

    def fire(kind, fam, params, parent=None, edge=None):
        c = coords_of(chamber.fams[fam], params, cmap)
        p = float(law.prob(_X([c], cmap))[0])
        row = chamber.observe(fam, params, purpose="attack:" + kind, parent=parent, edge_kind=edge,
                              delta={"attack": kind}, keep=True)
        attacks.append({"kind": kind, "family": fam, "params": params, "coords": c, "p": p,
                        "pred": int(law.predict(_X([c], cmap))[0]), "y": row["y"], "margin": row["margin"],
                        "se": row["se"], "world_id": row["world_id"]})

    for f in fams:
        fam = chamber.fams[f]
        P = pool[f]
        Xp = _X([r[key] for r in P], cmap)
        pp = law.prob(Xp)
        conf = np.nonzero((pp >= CONF) | (pp <= 1 - CONF))[0]
        q = per_family // 4
        # band
        band = np.argsort(np.abs(pp - 0.5))[:q]
        for i in band:
            fire("band", f, P[i]["params"])
        # coordinate-preserving transforms of confident worlds
        base = rng.choice(conf, min(len(conf), q), replace=False) if len(conf) else []
        n = 0
        for i in base:
            if n >= q:
                break
            fire("coordpres_base", f, P[i]["params"])
            b_row = attacks[-1]
            n += 1
            c0 = coords_of(fam, P[i]["params"], cmap)
            for v in fam.coord_preserving(P[i]["params"], rng):
                if n >= q:
                    break
                cv = coords_of(fam, v, cmap)
                if any(abs(cv[k] - c0[k]) > 1e-9 * max(1.0, abs(c0[k])) for k in c0):
                    skipped_not_preserving.append({"family": f, "variant": v})
                    continue
                try:
                    fire("coordpres", f, v, parent=P[i]["world_id"], edge="COORD_PRESERVING")
                    n += 1
                except ValueError:
                    continue
                a = attacks[-1]
                meta.append({"family": f, "base": b_row["params"], "variant": v, "coords": a["coords"],
                             "base_margin": b_row["margin"], "var_margin": a["margin"],
                             "flip": b_row["y"] != a["y"],
                             "significant": abs(b_row["margin"] - a["margin"]) > 2 * (b_row["se"] ** 2 + a["se"] ** 2) ** 0.5})
        # extremes (confident only)
        ext = []
        for k in ("C", "N", "K", "G"):
            ci = conf[np.argsort(Xp[k][conf])] if len(conf) else []
            ext += list(ci[:2]) + list(ci[-2:])
        for i in list(dict.fromkeys(ext))[:q]:
            fire("extreme", f, P[i]["params"])
        # error-seeking
        if errs and len(conf):
            Ze = feats([r["coords"] for r in errs])
            Zc = feats([P[i]["coords"] for i in conf])     # distance in the fixed v1 feature space
            d = ((Zc[:, None, :] - Ze[None, :, :]) ** 2).sum(-1).min(1)
            for i in conf[np.argsort(d)[:q]]:
                fire("errorseek", f, P[i]["params"])

    # confirmation of confident contradictions
    confirmed = []
    for a in attacks:
        confident = a["p"] >= CONF or a["p"] <= 1 - CONF
        a["confident"] = bool(confident)
        a["contradiction"] = bool(confident and a["pred"] != a["y"])
        if not a["contradiction"]:
            continue
        reps = [chamber.observe(a["family"], a["params"], purpose="confirm", replicate=k, episodes=4 * chamber.episodes,
                                keep=False) for k in (1, 2)]
        ok = all(r["y"] != a["pred"] and abs(r["margin"] - MARGIN) > 2 * r["se"] for r in reps)
        a["confirm_margins"] = [r["margin"] for r in reps]
        a["confirmed"] = bool(ok)
        if ok:
            confirmed.append(a)
    n_conf = sum(a["confident"] for a in attacks)
    band = [a for a in attacks if a["kind"] == "band"]
    calib = None
    if band:
        calib = {"mean_pred": float(np.mean([a["p"] for a in band])), "obs_rate": float(np.mean([a["y"] for a in band])), "n": len(band)}
    by_kind = {}
    for a in attacks:
        k = by_kind.setdefault(a["kind"], {"n": 0, "confident": 0, "contradictions": 0, "confirmed": 0})
        k["n"] += 1
        k["confident"] += a["confident"]
        k["contradictions"] += a["contradiction"]
        k["confirmed"] += a.get("confirmed", False)
    by_family = {}
    for a in attacks:
        k = by_family.setdefault(a["family"], {"confident": 0, "confirmed": 0})
        k["confident"] += a["confident"]
        k["confirmed"] += a.get("confirmed", False)
    rate = len(confirmed) / max(1, n_conf)
    metamorphic = {}
    for m in meta:
        k = metamorphic.setdefault(m["family"], {"pairs": 0, "verdict_flips": 0, "significant_margin_shifts": 0})
        k["pairs"] += 1
        k["verdict_flips"] += m["flip"]
        k["significant_margin_shifts"] += m["significant"]
    return {"law_id": law_id, "n_attacks": len(attacks), "n_confident": n_conf, "n_confirmed": len(confirmed),
            "rate": rate, "verdict": "FAILED" if rate > KILL_RATE else "SURVIVED", "by_kind": by_kind,
            "by_family": by_family, "band_calibration": calib, "metamorphic": metamorphic,
            "metamorphic_pairs": meta[:60], "cmap": cmap, "n_transforms_not_preserving": len(skipped_not_preserving),
            "counterexamples": [{k: a[k] for k in ("kind", "family", "params", "coords", "p", "margin", "confirm_margins")}
                                for a in confirmed][:40]}
