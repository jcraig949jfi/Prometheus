"""Control arms (POSITIVE_CONTROL, NULL_TWIN, CHEAT) for W1. Used by pilot.py and world.py."""
import common as K


def positive_control(w):
    q = K.make_q(w, 0, 0.0)
    conds = []
    for lam in K.LAMS:
        m, _ = K.measure(q, w["P"], lam)
        conds.append({"r": 0, "c": 0.0, "lam": lam, **m})
    return conds


def null_twin_and_cheat(w):
    nt, ch = [], []
    for c in K.C:
        for r in K.R:
            qs = K.shuffle_q(K.make_q(w, r, c), w["seed"], r, c)
            zc = K.planted_rank_r(w["seed"], r, c)
            zb = K.bonds_all(zc)
            for lam in K.LAMS:
                m, V = K.measure(qs, w["P"], lam)
                nt.append({"r": r, "c": c, "lam": lam, **m})
                ch.append({"r": r, "c": c, "lam": lam, "z": zb, "V": m["V"], "tanh": m["tanh"],
                           "quant": m["quant"], "injected": "z := planted TT-rank-r tensor"})
    return nt, ch
