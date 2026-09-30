"""Success/failure criteria of HT-2a8a3aedeb/W1 as applied (NOTES.md)."""
import numpy as np
from scipy.stats import spearmanr

LAM_HI = (1.0, 3.0, 10.0)
RS = (1, 2, 4)


def _cells(rows, c, tol):
    """rows: list of arm rows (one per seed). returns {(r,lam): [(bz,bV,bt), ...]}."""
    out = {}
    for row in rows:
        for cd in row["conds"]:
            if cd["c"] != c or cd["lam"] not in LAM_HI:
                continue
            out.setdefault((cd["r"], cd["lam"]), []).append(
                (cd["z"][tol], cd["V"][tol], cd["tanh"][tol]))
    return out


def success(rows, c=0.5, tol="1e-06", use_s3=True):
    cells = _cells(rows, c, tol)
    s1 = {f"r{r}_lam{l:g}": sum(bz <= bv - 1 for bz, bv, _ in v) for (r, l), v in cells.items()}
    s2 = {f"r{r}_lam{l:g}": sum(bz <= bt - 1 for bz, _, bt in v) for (r, l), v in cells.items()}
    n = {f"r{r}_lam{l:g}": len(v) for (r, l), v in cells.items()}
    S1 = len(cells) > 0 and all(s1[k] >= 8 for k in s1)
    S2 = len(cells) > 0 and all(s2[k] >= 7 for k in s2)
    rho = {}
    for l in LAM_HI:
        xs, ys = [], []
        for (r, ll), v in cells.items():
            if ll == l:
                xs += [r] * len(v); ys += [bz for bz, _, _ in v]
        if len(set(xs)) < 2 or len(set(ys)) < 2:
            rho[f"{l:g}"] = None
        else:
            rho[f"{l:g}"] = float(spearmanr(xs, ys).correlation)
    S3 = all(v is not None and v >= 0.6 for v in rho.values()) if use_s3 else None
    ok = S1 and S2 and (S3 if use_s3 else True)
    return {"success": bool(ok), "S1": bool(S1), "S2": bool(S2), "S3": S3,
            "S1_counts": s1, "S2_counts": s2, "n": n, "rho": rho}


def failure(rows, tol="1e-06"):
    hits = {}
    for c in (0.5, 2.0):
        for (r, l), v in _cells(rows, c, tol).items():
            a = sum(bz >= bv for bz, bv, _ in v)
            b = sum(not (bz < bt) for bz, _, bt in v)
            hits[f"c{c:g}_r{r}_lam{l:g}"] = {"z_ge_V": a, "z_not_lt_tanh": b}
    fail = any(h["z_ge_V"] >= 5 or h["z_not_lt_tanh"] >= 5 for h in hits.values())
    return {"failure": bool(fail), "cells": hits}


def positive_meets(rows, tol="1e-06"):
    exact = all(cd["z"]["1e-06"] == 1 and cd["V"]["1e-06"] == 2 for row in rows for cd in row["conds"])
    s = success(rows, c=0.0, tol=tol, use_s3=False)
    # positive-control cells: c=0; r recorded as 0
    return {"meets": bool(exact and s["S1"] and s["S2"]), "exact_z1_V2": bool(exact), **s}
