"""Criterion as applied (thresholds verbatim from the spec), pooled over seeds x episodes."""
import json
import numpy as np


def load(path):
    rows = {}
    for line in open(path):
        r = json.loads(line)
        rows.setdefault(r["arm"], []).extend(r["episodes"])
    return rows


def pooled(eps):
    pr = sum(e["probes"] for e in eps)
    pb = sum(e["probe_bits"] for e in eps)
    return dict(n_episodes=len(eps),
                mean_forbidden=float(np.mean([e["forbidden"] for e in eps])),
                median_steps=float(np.median([e["steps"] for e in eps])),
                probes=int(pr), bits_per_probe=(pb / pr if pr else None),
                probes_per_episode=pr / len(eps),
                reach_rate=float(np.mean([e["reached"] for e in eps])),
                frac_ep_zero_forbidden=float(np.mean([e["forbidden"] == 0 for e in eps])),
                probe_true_safe_frac=(sum(e["probe_true_safe"] for e in eps) / pr if pr else None),
                trig_none_safe_frac=(sum(e["trig_none_safe"] for e in eps) / pr if pr else None))


def criterion(x, ce, nt):
    red = (1 - x["mean_forbidden"] / ce["mean_forbidden"]) if ce["mean_forbidden"] > 0 else None
    sr = x["median_steps"] / ce["median_steps"]
    br = (x["bits_per_probe"] / nt["bits_per_probe"]) if (x["bits_per_probe"] and nt["bits_per_probe"]) else None
    a = red is not None and red >= 0.50
    b = sr <= 1.5
    c = br is not None and br >= 1.5
    fail = (red is None or red < 0.20) or (br is None or br < 1.1)
    return dict(forbidden_reduction=red, median_steps_ratio=sr, bits_ratio=br,
                a=bool(a), b=bool(b), c=bool(c), meets_success=bool(a and b and c),
                meets_failure=bool(fail))
