"""Shortcut audits (Pass D). Deterministic; no interpreter.

causality_audit   future observations replaced at 5 cut points; the lens
                  output up to each cut must be bit-identical. A lens that
                  reads the future is not a sense.
cheat_control     a world whose consequence is the NEXT observation, and a
                  lens that reads it through the forbidden LEAD op: the
                  gain channel must see it (gain large) and the causality
                  audit must reject it. If either fails, the instrument is
                  void.
sensor_class      LOCAL / FAMILY / TRANSFER / GENERAL from significant
                  test-split gains; significance on a tsd/prf world is a
                  FALSE_GRADIENT flag, never transfer.
"""

from __future__ import annotations

import numpy as np

from . import lens as Lm
from . import worlds as Wm
from .ecology import WorldEval

CUTS = (500, 2000, 5000, 8000, 11000)


def causality_audit(g, X, seed=0):
    rng = np.random.default_rng(seed)
    Z = Lm.execute(g, X)
    for t0 in CUTS:
        Xp = X.copy()
        if np.issubdtype(X.dtype, np.integer):
            Xp[t0 + 1:] = rng.integers(X.min(), X.max() + 1, size=Xp[t0 + 1:].shape)
        else:
            Xp[t0 + 1:] = rng.standard_normal(Xp[t0 + 1:].shape) * 3.0
        Zp = Lm.execute(g, Xp)
        if not np.array_equal(Z[:t0 + 1], Zp[:t0 + 1]):
            return {"pass": False, "first_cut_failed": t0}
    return {"pass": True, "first_cut_failed": None}


def cheat_control():
    spec = {"id": "CHEAT_future", "kind": "known", "d": 6, "uid": 999,
            "proc": {"kind": "bern", "p": 0.5}, "law": {"kind": "ident", "a": 2}}
    we = WorldEval(spec, 1)
    # consequence = the observation one step in the FUTURE (Y[t] = X[t+1, 2])
    we.Y = np.concatenate([we.X[1:, 2], [0]]).astype(np.int64)
    we.set_ecology([])
    cheat = {"ins": [[Lm.LEAD_OP, [2], 1]], "out": [Lm.NIN]}
    honest = {"ins": [["delay", [2], 1]], "out": [Lm.NIN]}
    gc = we.gains(cheat, splits=("conf",), scopes=("all",), orgs=("tree",), rulers=("R0",))
    gh = we.gains(honest, splits=("conf",), scopes=("all",), orgs=("tree",), rulers=("R0",))
    k = ("R0", "tree", "conf", "all")
    ac = causality_audit(cheat, we.X)
    ah = causality_audit(honest, we.X)
    ok = gc[k][1] >= 4.0 and not ac["pass"] and ah["pass"]
    return {"cheat_gain": gc[k][0], "cheat_z": gc[k][1], "cheat_audit_pass": ac["pass"],
            "honest_gain": gh[k][0], "honest_audit_pass": ah["pass"],
            "instrument_ok": bool(ok)}


NEGATIVE_KINDS = ("tsd", "prf")


def sensor_class(home_id, sig_worlds, specs):
    """sig_worlds: ids with a significant test gain (home included only if
    it replicated). Returns (class, false_gradient_worlds)."""
    by = {s["id"]: s for s in specs}
    home = by[home_id]
    neg = sorted(w for w in sig_worlds if by[w]["kind"] in NEGATIVE_KINDS)
    pos = [w for w in sig_worlds if by[w]["kind"] not in NEGATIVE_KINDS and w != home_id]
    fams = {by[w]["family"] for w in pos}
    other = fams - {home["family"]}
    if len(other | ({home["family"]} if pos or home_id in sig_worlds else set())) >= 3:
        c = "GENERAL_SENSOR"
    elif other:
        c = "TRANSFER_SENSOR"
    elif pos:
        c = "FAMILY_SENSOR"
    elif home_id in sig_worlds:
        c = "LOCAL_SENSOR"
    else:
        c = "NOT_REPLICATED"
    return c, neg


def planted_channels(spec):
    """World channels a planted law reads (answer key; audits/report only)."""
    L = spec["law"]
    return sorted({L[k] for k in ("a", "b", "c", "d") if k in L and isinstance(L[k], int)})
