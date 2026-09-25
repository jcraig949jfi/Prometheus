"""WTP-03 interventions WITH SUPPORT (PREREG_WTP03 s8). Every intervention records:
  attempted, changed (did it alter the state it claims to alter?), magnitude, and the outcome.
No change -> NOT_APPLICABLE, never causal support."""
import copy
import hashlib

import numpy as np

from .collider import _addr, make, train, RULE
from .world3 import AC


def digest(mem):
    h = hashlib.sha256()
    for a in mem.params():
        h.update(np.ascontiguousarray(a, float).tobytes())
    return h.hexdigest()[:16]


def _pred(mem, dims, T):
    return np.nan_to_num(mem.predict(_addr(dims, T)), nan=0.0, posinf=1e6, neginf=-1e6)


def intervene(kind, mem, st, T, cap, seed, rng):
    """Returns (new_mem, support dict). Support compares state and predictions on T."""
    dims = st["dims"]
    before_d, before_p = digest(mem), _pred(mem, dims, T)
    new = copy.deepcopy(mem)
    if kind == "ablate_half":
        for a in new.params():
            a[rng.random(a.shape) < 0.5] = 0.0
    elif kind == "reset":
        new = make(mem.kind if mem.kind != "none" else "constant", dims, cap, np.random.default_rng(seed + 991))
    elif kind == "shuffle_modes":  # permute the index rows of every factor/core along its value axis
        for a in new.params():
            if a.ndim >= 2:
                ax = 1 if (a.ndim == 3) else 0
                a[...] = np.take(a, rng.permutation(a.shape[ax]), axis=ax)
            elif a.ndim == 1 and a.shape[0] > 1:
                a[...] = a[rng.permutation(a.shape[0])]
    elif kind == "freeze":  # the never-trained substrate: support = training changed the parameters
        new = make(mem.kind if mem.kind != "none" else "constant", dims, cap, np.random.default_rng(seed + 101))
    else:
        raise KeyError(kind)
    after_d, after_p = digest(new), _pred(new, dims, T)
    mag = float(np.sqrt(np.mean((after_p - before_p) ** 2)))
    changed = (after_d != before_d) and mag > 1e-9
    return new, dict(attempted=kind, changed=bool(changed), state_changed=after_d != before_d, pred_rms_change=mag)


def autopsy(kind, st, T, cap, seed, base_ac, xc_null):
    """Train `kind` on stream st, then apply each intervention. Outcome = AC on T; XC via xc_null
    (the best null AC on T). Carrier criteria (s8): reset and freeze keep <= 20% of XC; ablate and
    shuffle, if supported, remove >= 50% of XC."""
    rng = np.random.default_rng(seed + 7)
    mem, _ = train(kind, st, cap, seed + 101)
    if mem is None:
        return dict(status="INCOMPATIBLE")
    x, V0 = st["x"].reshape(-1), st["V0"]
    xc0 = AC(_pred(mem, st["dims"], T), x[T], V0) - xc_null
    res = dict(XC_base=xc0, interventions={})
    for iv in ("ablate_half", "shuffle_modes", "reset", "freeze"):
        new, sup = intervene(iv, mem, st, T, cap, seed, rng)
        xc = AC(_pred(new, st["dims"], T), x[T], V0) - xc_null
        sup.update(XC=xc, retained=(xc / xc0) if xc0 > 0 else None,
                   verdict="NOT_APPLICABLE" if not sup["changed"] else ("REMOVES" if xc0 > 0 and xc <= 0.5 * xc0 else "KEEPS"))
        res["interventions"][iv] = sup
    ivs = res["interventions"]
    res["carrier"] = bool(xc0 >= 0.10 and ivs["reset"]["changed"] and ivs["reset"]["XC"] <= 0.2 * xc0
                          and ivs["freeze"]["changed"] and ivs["freeze"]["XC"] <= 0.2 * xc0
                          and all(ivs[k]["verdict"] in ("REMOVES", "NOT_APPLICABLE") for k in ("ablate_half", "shuffle_modes"))
                          and any(ivs[k]["verdict"] == "REMOVES" for k in ("ablate_half", "shuffle_modes")))
    return res
