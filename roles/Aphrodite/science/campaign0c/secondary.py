"""Campaign 0C: generator, true effects, and the fixed discovery procedure P (PREREG_C0C). TIER 2.

The procedure (screen -> decide -> estimate) sees only observations; the
generator's truth (carrier status, true effect) is recorded beside it for
scoring and never read by the procedure.
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "campaign0"))
from assay import t_cdf, t_ppf  # noqa: E402  (functions only; the frozen assay is not modified)

B0 = math.log(0.35 / 0.65)
SD_U, SD_V, SD_W, SD_E, SD_H = 0.8, 0.3, 0.15, 0.15, 0.3
DELTA_DISC = 0.03
C_SCREEN = 0.10
N_SCREEN_FAM, N_SCREEN_TASKS = 4, 20
N_CONF_FAM, N_CONF_TASKS = 8, 40
ALPHA, N_MIN = 0.05, 2


@dataclass(frozen=True)
class World:
    name: str
    kind: str          # "N0", "G", "FC", "AS", "WC"
    pi: float = 0.0
    J: float = 0.0


def worlds() -> List[World]:
    ws = [World("N0", "N0")]
    for pi in (0.01, 0.02, 0.05, 0.10, 0.20):
        for J in (0.5, 1.0, 2.0):
            ws.append(World(f"G_pi{pi}_J{J}", "G", pi, J))
    ws += [World("FC", "FC", 0.10, 2.0), World("AS", "AS", 0.20, 2.0), World("WC", "WC", 0.0, 0.08)]
    return ws


# ------------------------------------------------------------------ truth by Gauss-Hermite
def _gh(n=64):
    import numpy as np  # probabilists' Gauss-Hermite nodes and weights
    x, w = np.polynomial.hermite_e.hermegauss(n)
    return [float(xi) for xi in x], [float(wi) / math.sqrt(2 * math.pi) for wi in w]


_GX, _GW = _gh()


def _esig(m: float, s: float) -> float:
    return sum(w / (1 + math.exp(-(m + s * x))) for x, w in zip(_GX, _GW))


def true_effect(v: float, shift: float, frac: float = 1.0) -> float:
    """Expected solved-share difference I_8 - I_0 over the sealed-family distribution.
    frac: share of families on which the shift applies (FC: 1/3)."""
    s8 = math.sqrt(SD_U ** 2 + SD_W ** 2 + SD_E ** 2)
    s0 = math.sqrt(SD_U ** 2 + SD_E ** 2)
    base = _esig(B0 + v, s0)
    on = _esig(B0 + v + shift, s8) if shift else base
    return frac * (on - base)


# ------------------------------------------------------------------ one family cell pair
def _pair(rng, v, shift, n_tasks):
    u = rng.gauss(0, SD_U)
    x8 = B0 + u + v + rng.gauss(0, SD_E)
    if shift:
        x8 += shift + rng.gauss(0, SD_W)
    x0 = B0 + u + v + rng.gauss(0, SD_E)
    s8 = rng.binomialvariate(n_tasks, 1 / (1 + math.exp(-x8))) / n_tasks
    s0 = rng.binomialvariate(n_tasks, 1 / (1 + math.exp(-x0))) / n_tasks
    return s8 - s0


def simulate(world: World, L: int, rng: random.Random) -> List[Dict]:
    """Per lineage: truth + the three disjoint observation sets."""
    lins = []
    for _ in range(L):
        v = rng.gauss(0, SD_V)
        h = rng.gauss(0, SD_H)
        carrier = False
        if world.kind in ("G", "FC", "AS"):
            carrier = rng.random() < world.pi
        J = world.J * (1 + h) if carrier else 0.0

        def shift_for(stage):
            if world.kind == "WC":
                return 0.08
            if not carrier:
                return 0.0
            if world.kind == "AS":
                return J if stage == "screen" else 0.0
            if world.kind == "FC":
                return J if rng.random() < 1 / 3 else 0.0
            return J

        screen = [_pair(rng, v, shift_for("screen"), N_SCREEN_TASKS) for _ in range(N_SCREEN_FAM)]
        decide = [_pair(rng, v, shift_for("decide"), N_CONF_TASKS) for _ in range(N_CONF_FAM)]
        estimate = [_pair(rng, v, shift_for("estimate"), N_CONF_TASKS) for _ in range(N_CONF_FAM)]
        if world.kind == "WC":
            te = true_effect(v, 0.08)
        elif world.kind == "AS" or not carrier:
            te = 0.0
        elif world.kind == "FC":
            te = true_effect(v, J, 1 / 3)
        else:
            te = true_effect(v, J)
        lins.append({"screen": screen, "decide": decide, "estimate": estimate,
                     "truth": {"true_effect": float(te), "true_carrier": bool(te > DELTA_DISC),
                               "planted": bool(carrier)}})
    return lins


# ------------------------------------------------------------------ the fixed procedure P
def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        out[i] = run
    return out


def procedure(lins: List[Dict]) -> Dict:
    L = len(lins)
    k = math.ceil(0.25 * L)
    d = [sum(l["screen"]) / len(l["screen"]) for l in lins]
    qualified = [i for i in range(L) if d[i] >= C_SCREEN]
    nominated = sorted(qualified, key=lambda i: -d[i])[:k]
    ps = []
    for i in nominated:
        x = lins[i]["decide"]
        n = len(x)
        m = sum(x) / n
        sd = math.sqrt(sum((a - m) ** 2 for a in x) / (n - 1)) or 1e-9
        ps.append(1 - t_cdf((m - DELTA_DISC) / (sd / math.sqrt(n)), n - 1))
    padj = holm(ps) if ps else []
    confirmed = [nominated[j] for j in range(len(nominated)) if padj[j] < ALPHA]
    est = {}
    q = t_ppf(0.975, N_CONF_FAM - 1)
    for i in confirmed:
        x = lins[i]["estimate"]
        n = len(x)
        m = sum(x) / n
        se = math.sqrt(sum((a - m) ** 2 for a in x) / (n - 1)) / math.sqrt(n)
        est[i] = (m, m - q * se, m + q * se)
    return {"L": L, "k": k, "screen_d": d, "qualified": qualified, "nominated": nominated,
            "confirmed": confirmed, "estimates": est, "discovery": len(confirmed) >= N_MIN,
            "discovery_nmin1": len(confirmed) >= 1}
