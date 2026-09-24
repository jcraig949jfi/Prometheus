"""Transition location, width and finite-size behaviour along one native knob (charter s XI).

For a family, a base world and one knob, evaluate a ladder of knob values with R replicates at
several episode counts E. Fit P(PAYS | x) = sigmoid((x0 - log x) / w) by maximum likelihood per E.
Reported: x0 (location), w (width in log-knob units), and whether w shrinks as E grows (a finite
system whose boundary is sharp in the limit) or not (an intrinsically probabilistic boundary).
This is instrumentation, not a law: it says how sharp a boundary is where one exists.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

import numpy as np

from prometheus.cosmos.world import evaluate


def _fit(logx: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    best = (-np.inf, None, None)
    for x0 in np.linspace(logx.min(), logx.max(), 121):
        for w in np.geomspace(0.01, 3.0, 60):
            z = np.clip((x0 - logx) / w, -40, 40)
            p = np.clip(1 / (1 + np.exp(-z)), 1e-9, 1 - 1e-9)
            ll = float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
            if ll > best[0]:
                best = (ll, x0, w)
    return {"x0": float(np.exp(best[1])), "log_x0": float(best[1]), "width_log": float(best[2]), "ll": best[0]}


def scan(fam, base: Dict[str, Any], knob: str, values: Sequence[float], episodes: Sequence[int] = (100, 400, 1600),
         replicates: int = 6, campaign: str = "boundary") -> Dict[str, Any]:
    out: Dict[str, Any] = {"family": fam.name, "knob": knob, "base": base, "per_E": {}}
    for E in episodes:
        xs, ys, margins = [], [], []
        for v in values:
            p = dict(base, **{knob: v})
            for r in range(replicates):
                rec = evaluate(fam, p, replicate=r, episodes=E, campaign=campaign)
                xs.append(v)
                ys.append(int(rec["verdict"] == "PAYS"))
                margins.append(rec["margin"])
        xs, ys = np.array(xs, float), np.array(ys, int)
        fit = _fit(np.log(xs), ys)
        rate = {float(v): float(ys[xs == v].mean()) for v in values}
        out["per_E"][str(E)] = {**fit, "pays_rate_by_value": rate}
    ws = [out["per_E"][str(E)]["width_log"] for E in episodes]
    out["width_shrinks_with_E"] = bool(all(ws[i + 1] <= ws[i] * 1.05 for i in range(len(ws) - 1)) and ws[-1] < ws[0])
    return out
