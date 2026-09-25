"""WTP anomaly detectors A1-A6 and behavioural niches, exactly as
PREREG_WTP01 s3 / s5(c). Flags are not findings."""
import collections

import numpy as np


def _robust(v):
    v = np.asarray(v, float)
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med))) * 1.4826 + 1e-6
    return med, mad


def class_refs(rows):
    """Per memory-substrate reference (median, MAD) of CG, from Wave A."""
    d = collections.defaultdict(list)
    for r in rows:
        d[r["genome"]["memory"]["substrate"]].append(r["CG"])
    return {k: _robust(v) for k, v in d.items()}


def population_refs(rows):
    U = np.array([r["U"] for r in rows])
    CG = np.array([r["CG"] for r in rows])
    return dict(U95=float(np.quantile(U, .95)), U20=float(np.quantile(U, .20)), CG95=float(np.quantile(CG, .95)))


def jump(trace):
    nl = [t["nlmse"] for t in trace]
    inc = np.diff(nl)
    if len(inc) < 3:
        return False, 0.0
    med = float(np.median(np.abs(inc))) + 1e-9
    j = float(inc.max())
    return bool(j > 5 * med and j > 0.3), j


def flags(r, cref, pref):
    out = []
    med, mad = cref.get(r["genome"]["memory"]["substrate"], (0.0, 1.0))
    z = (r["CG"] - med) / mad
    if z > 4:
        out.append(("A1", round(z, 2)))
    jf, j = jump(r["trace"])
    if jf:
        out.append(("A2", round(j, 3)))
    if r["CG"] > 0.3 and r["n_floats"] <= 16:
        out.append(("A3", round(r["CG"], 3)))
    if r["CG"] < -1:
        out.append(("A4", round(r["CG"], 3)))
    if r["reach"] > 3 and r["CG"] > 0:
        out.append(("A5", round(r["reach"], 2)))
    if (r["U"] >= pref["U95"] and r["CG"] <= 0) or (r["CG"] >= pref["CG95"] and r["U"] <= pref["U20"]):
        out.append(("A6", round(r["U"], 2)))
    return out


def has(r, det, cref, pref):
    return any(f[0] == det for f in flags(r, cref, pref))


def niche(r, qU):
    cg = r["CG"]
    b_cg = 0 if cg <= 0.3 else (1 if cg <= 1 else 2)
    b_u = int(np.searchsorted(qU, r["U"]))
    nf = r["n_floats"]
    b_m = 0 if nf <= 16 else (1 if nf <= 128 else (2 if nf <= 512 else 3))
    b_r = 0 if r["reach"] < 0.8 else (1 if r["reach"] <= 1.25 else 2)
    return (b_cg, b_u, b_m, b_r)
