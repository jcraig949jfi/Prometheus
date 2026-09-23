"""Holdout broker (main-process side). Talks to the sealed family ONLY through a subprocess.

Order of operations for an adjudication (each step is a receipt, in this order):
  1  verify the law is FROZEN in the ledger and its freeze hash matches
  2  verify the sealed spec's sha256 equals the preregistered commitment and that
     well.py still hashes to the spec's family_src_sha
  3  subprocess: declared coordinates of the sealed worlds (spec only, no runs)
  4  compute and RECEIPT the frozen law's predictions (hash of the prediction vector)
  5  subprocess: run the sealed worlds; score predictions against observed verdicts
  6  compute and RECEIPT intervention prescriptions (f_star, band, direction)
  7  subprocess: run the intervention ladders; score prescriptions
Nothing from steps 5 or 7 can influence 4 or 6: the prediction hashes are already in
the chain when the outcomes exist.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.hashing import file_sha, h
from prometheus.cosmos.miner import law_from_json

HOLDOUT = Path(__file__).resolve().parent / "holdout"
SPEC = HOLDOUT / "sealed_spec.json"
REPO = Path(__file__).resolve().parents[2]


class SealBroken(RuntimeError):
    pass


def _call(req: Dict[str, Any], timeout: int = 3600) -> Any:
    with tempfile.TemporaryDirectory() as td:
        rq, rp = Path(td) / "req.json", Path(td) / "rep.json"
        rq.write_text(json.dumps(req), encoding="utf-8")
        env = dict(os.environ, COSMOS_BROKER="1", PYTHONPATH=str(REPO))
        r = subprocess.run([sys.executable, "-m", "prometheus.cosmos.holdout.run", str(rq), str(rp)],
                           env=env, cwd=str(REPO), capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError("broker subprocess failed: " + r.stderr[-2000:])
        return json.loads(rp.read_text(encoding="utf-8"))


def selftest() -> Dict[str, Any]:
    return _call({"cmd": "selftest"})


def load_spec(commitment: str) -> Dict[str, Any]:
    if not SPEC.exists():
        raise SealBroken("no sealed spec")
    got = file_sha(SPEC)
    if got != commitment:
        raise SealBroken("sealed spec sha %s != preregistered commitment %s" % (got, commitment))
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if file_sha(HOLDOUT / "well.py") != spec["family_src_sha"]:
        raise SealBroken("well.py changed after sealing")
    return spec


def _ba(pred: np.ndarray, y: np.ndarray) -> float:
    if y.sum() == 0 or (1 - y).sum() == 0:
        return float("nan")
    return 0.5 * ((pred & (y == 1)).sum() / (y == 1).sum() + (~pred & (y == 0)).sum() / (y == 0).sum())


def adjudicate(store, law_id: str, commitment: str, baselines: Dict[str, Any] | None = None) -> Dict[str, Any]:
    law_row = store.law(law_id)
    if not law_row["freeze_hash"] or not any(e["status"] == "FROZEN" for e in law_row["events"]):
        raise SealBroken("law %s is not frozen; the broker adjudicates frozen laws only" % law_id)
    fh = h({"law_id": law_id, "body": law_row["body"], "parent": law_row["parent"]})
    if fh != law_row["freeze_hash"]:
        raise SealBroken("freeze hash mismatch")
    spec = load_spec(commitment)
    store.receipts.append("holdout_open", {"law_id": law_id, "freeze_hash": fh, "spec_sha": commitment})
    L = law_from_json(law_row["body"]["law"])

    coords = _call({"cmd": "coords", "spec": spec})
    X = {k: np.array([c["coords"][k] for c in coords]) for k in ("C", "N", "K", "G")}
    p = L.prob(X)
    pred = L.predict(X)
    preds = {"law_id": law_id, "pred": pred.astype(int).tolist(), "prob": np.round(p, 6).tolist()}
    extra = {}
    for name, fn in (baselines or {}).items():
        extra[name] = np.asarray(fn(X), bool)
        preds["baseline:" + name] = extra[name].astype(int).tolist()
    pred_hash = h(preds)
    store.receipts.append("holdout_predictions", {"law_id": law_id, "pred_hash": pred_hash, "n": len(pred)})
    store.commit()

    obs = _call({"cmd": "run", "spec": spec})
    y = np.array([int(o["verdict"] == "PAYS") for o in obs])
    res = {"law_id": law_id, "freeze_hash": fh, "spec_sha": commitment, "pred_hash": pred_hash,
           "n_worlds": int(len(y)), "base_rate_D": float(y.mean()),
           "law_ba": _ba(pred, y), "law_acc": float((pred == (y == 1)).mean()),
           "brier": float(np.mean((p - y) ** 2)), "brier_climatology": float(np.mean((y.mean() - y) ** 2))}
    res["baselines"] = {k: {"ba": _ba(v, y), "acc": float((v == (y == 1)).mean())} for k, v in extra.items()}
    res["rows"] = [{"i": o["i"], "coords": coords[o["i"]]["coords"], "prob": float(p[o["i"]]),
                    "pred": int(pred[o["i"]]), "y": int(y[o["i"]]), "margin": o["margin"], "se": o["se"]} for o in obs]
    store.receipts.append("holdout_revealed", {k: v for k, v in res.items() if k != "rows"})
    store.event(law_id, "HOLDOUT_TESTED", "BA %.3f on %d sealed worlds" % (res["law_ba"], len(y)))
    store.commit()
    return res


def _flip_factor(L, x: Dict[str, float], ladder: List[float]) -> Dict[str, Any]:
    """C scales linearly with kappa; scan the law's P along the ladder (fine grid) for P=0.5/0.75/0.25."""
    fs = np.geomspace(min(ladder) / 4, max(ladder) * 4, 2000)
    X = {k: np.full(len(fs), x[k]) for k in ("N", "K", "G")}
    X["C"] = x["C"] * fs
    P = L.prob(X)
    cls = L.predict(X)

    def cross(level):
        idx = np.nonzero(P < level)[0]
        return float(fs[idx[0]]) if len(idx) else None

    flips = np.nonzero(~cls)[0]
    return {"f_star": float(fs[flips[0]]) if len(flips) else None, "f_p75": cross(0.75), "f_p25": cross(0.25)}


def intervene(store, law_id: str, commitment: str, holdout_res: Dict[str, Any]) -> Dict[str, Any]:
    spec = load_spec(commitment)
    prot = spec["intervention_protocol"]
    law_row = store.law(law_id)
    L = law_from_json(law_row["body"]["law"])
    cand = [r for r in holdout_res["rows"] if r["prob"] >= 0.9]
    cand.sort(key=lambda r: h([r["i"], spec["nonce"]]))
    bases = cand[: prot["n_base"]]
    presc = []
    for r in bases:
        fl = _flip_factor(L, r["coords"], prot["ladder"])
        presc.append({"i": r["i"], "coords": r["coords"], **fl,
                      "direction": "PAYS at f_star/2, QUIET at 2*f_star"})
    ph = h(presc)
    store.receipts.append("intervention_prescriptions", {"law_id": law_id, "presc_hash": ph, "n": len(presc),
                                                          "prescriptions": presc})
    store.commit()
    jobs = []
    for pr in presc:
        if pr["f_star"] is None:
            continue
        fs = sorted(set([round(f, 6) for f in prot["ladder"]] + [round(pr["f_star"] / 2, 6), round(pr["f_star"] * 2, 6)]))
        jobs.append({"i": pr["i"], "factors": fs, "episodes": prot["episodes"]})
    out = _call({"cmd": "ladder", "spec": spec, "jobs": jobs}) if jobs else []
    scored = []
    for pr, o in zip([p for p in presc if p["f_star"] is not None], out):
        rows = {round(r["f"], 6): r for r in o["rows"]}
        lo, hi = rows[round(pr["f_star"] / 2, 6)], rows[round(pr["f_star"] * 2, 6)]
        direction_ok = lo["verdict"] == "PAYS" and hi["verdict"] == "QUIET"
        ladder_rows = [r for r in o["rows"] if any(abs(r["f"] - f) < 1e-9 for f in prot["ladder"])]
        f_obs = next((r["f"] for r in sorted(ladder_rows, key=lambda r: r["f"]) if r["margin"] < 0.10), None)
        mag_ok = f_obs is not None and abs(math.log2(f_obs / pr["f_star"])) <= 1.0
        scored.append({"i": pr["i"], "f_star": pr["f_star"], "band": [pr["f_p75"], pr["f_p25"]], "f_obs": f_obs,
                       "direction_ok": direction_ok, "magnitude_ok": mag_ok,
                       "margin_at_half": lo["margin"], "margin_at_double": hi["margin"],
                       "in_band": (f_obs is not None and pr["f_p75"] is not None and pr["f_p25"] is not None
                                   and pr["f_p75"] / 1.5 <= f_obs <= pr["f_p25"] * 1.5)})
    res = {"presc_hash": ph, "n_prescribed": len(presc), "n_scored": len(scored),
           "direction_ok": sum(s["direction_ok"] for s in scored), "magnitude_ok": sum(s["magnitude_ok"] for s in scored),
           "in_band": sum(s["in_band"] for s in scored), "rows": scored}
    res["G6"] = "PASS" if (len(scored) >= prot["n_base"] and res["direction_ok"] >= 10 and res["magnitude_ok"] >= 8) else "FAIL"
    store.receipts.append("intervention_revealed", {k: v for k, v in res.items() if k != "rows"})
    store.event(law_id, "INTERVENTION_TESTED", "G6 %s dir %d/%d mag %d/%d" % (
        res["G6"], res["direction_ok"], len(scored), res["magnitude_ok"], len(scored)))
    store.commit()
    return res
