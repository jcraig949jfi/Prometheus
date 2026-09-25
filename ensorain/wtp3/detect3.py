"""WTP-03 detectors (PREREG_WTP03 s7). Each has a named null.

X1 COMPLETION       a structured substrate (STRUCT, n_floats >= 8) with XC_interp >= .10 on the real
                    stream and SD = XC_real - XC_marg >= .10              null: marginal-preserving surrogate
X6 RECOMBINATION    the same on the recomb block (pairs of held-out values never seen)   null: same
X3 CROSSOVER        two panel substrates A, B (both OK) reverse order between ADJACENT budget levels
                    (or adjacent exposure levels): AC_A - AC_B >= .10 at one, <= -.10 at the other,
                    on interp or recomb                                    null: seed-split replication;
                                                                           surrogate tells STRUCTURE-(IN)DEPENDENT
X4 SUPERADDITIVE    hybrid_al AC >= max(additive, lowrank) + .10 at one budget, SD >= .10   null: surrogate
X7 CONVERSION       (Wave G only; see campaign3.wave_g)
Scalar / tiny substrates (constant, n_floats < 8) never fire X1/X6/X4 (s3)."""
import numpy as np

from .collider import STRUCT, PANEL

TH = 0.10
MIN_FLOATS = 8


def _xc(c, k, s):
    v = c["subs"].get(k, {})
    return v.get("XC", {}).get(s) if v.get("status") == "OK" and v.get("n_floats", 0) >= MIN_FLOATS else None


def _ac(c, k, s):
    v = c["subs"].get(k, {})
    return v.get("AC", {}).get(s) if v.get("status") == "OK" else None


def completion(real, marg, s="interp"):
    """[(substrate, XC_real, SD)] firing on set s."""
    out = []
    for k in STRUCT:
        a, b = _xc(real, k, s), (_xc(marg, k, s) if marg else None)
        if a is None or a < TH:
            continue
        if marg is not None and b is None:   # the null was not measurable: no structure-dependence claim
            continue
        sd = a - (b if b is not None else 0.0)   # marg=None only in replication hit-counting (completion(u, None))
        if sd >= TH:
            out.append((k, a, sd))
    return out


def crossovers(ladder, sets=("interp", "recomb")):
    """ladder: list of (level, collide-result) in increasing level. Returns reversals."""
    out = []
    for (l1, c1), (l2, c2) in zip(ladder, ladder[1:]):
        for s in sets:
            for i, a in enumerate(PANEL):
                for b in PANEL[i + 1:]:
                    x1a, x1b, x2a, x2b = _ac(c1, a, s), _ac(c1, b, s), _ac(c2, a, s), _ac(c2, b, s)
                    if None in (x1a, x1b, x2a, x2b):
                        continue
                    d1, d2 = x1a - x1b, x2a - x2b
                    if (d1 >= TH and d2 <= -TH) or (d1 <= -TH and d2 >= TH):
                        out.append(dict(pair=(a, b), set=s, levels=(l1, l2), d=(d1, d2)))
    return out


def superadditive(real, marg):
    out = []
    for s in ("interp", "recomb"):
        h, a, l = _ac(real, "hybrid_al", s), _ac(real, "additive", s), _ac(real, "lowrank", s)
        if h is None or a is None or l is None:
            continue
        ex = h - max(a, l)
        if ex < TH:
            continue
        hm, am, lm = (_ac(marg, "hybrid_al", s), _ac(marg, "additive", s), _ac(marg, "lowrank", s)) if marg else (None, None, None)
        if marg is not None and None in (hm, am, lm):
            continue
        exm = (hm - max(am, lm)) if None not in (hm, am, lm) else 0.0
        if ex - exm >= TH:
            out.append(dict(set=s, excess=ex, SD=ex - exm))
    return out


def status_units(hits, null_hits, n, sds, degenerate=0):
    """Replication status from n fresh-seed units (PREREG s7, as WTP-02 s5 with XC)."""
    if degenerate >= 3:
        return "DEGENERATE WORLD"
    med = float(np.median(sds)) if sds else float("nan")
    if hits <= 1:
        return "FALSIFIED"
    if hits == 2:
        return "UNRESOLVED"
    if null_hits >= 3:
        return "STRUCTURE-INDEPENDENT"
    if null_hits <= 1 and np.isfinite(med) and med >= TH:
        return "STRUCTURE-DEPENDENT"
    return "UNRESOLVED"
