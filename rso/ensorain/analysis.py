"""C-016-T030 decision rule (PREREGISTRATION.md s5). Exact and integer-first: no floating-point statistic decides.

Unit = the lifetime. Reused within scope: the exact binomial tails and integer thresholds of rso/witness/ruler.py
(registry entry ruler-binary-retention: a binary per-unit outcome with a known chance bound; here the unit is the
lifetime, so the 'dependent episodes' limit is respected) and Holm from rso/reach/stats.py.
"""
from fractions import Fraction

from rso.reach.stats import holm
from rso.witness.ruler import tail_ge, thresholds

ALPHA = Fraction(1, 20)
VERDICTS = ("INSTRUMENT_FAULT", "REFUSED_FIXED_PRIOR", "REVISION_HISTORY_DEPENDENT", "REVISION_NOT_HISTORY_DEPENDENT",
            "REVISION_WITHOUT_RETAINED_COMPETENCE", "REVISION_NOT_SHOWN")


class AnalysisError(ValueError):
    pass


def sign_p(wins, losses):
    """One-sided exact sign test: P(X >= wins), X ~ Binomial(wins + losses, 1/2); ties are dropped."""
    n = wins + losses
    return Fraction(1) if n == 0 else tail_ge(n, wins, Fraction(1, 2))


def cmp_late(a, b):
    """Sign of c_late/n_late (a) minus (b), by integer cross-multiplication."""
    x, y = a["c_late"] * b["n_late"], b["c_late"] * a["n_late"]
    return (x > y) - (x < y)


def _by(rows, n_required, arms):
    out = {}
    for r in rows:
        out.setdefault(r["subject"], {}).setdefault(r["arm"], {})[r["seed"]] = r
    for name, d in out.items():
        seeds = set(d.get("full", {}))
        if any(set(d.get(a, {})) != seeds for a in arms) or len(seeds) != n_required:
            raise AnalysisError("%s: every arm needs the same %d seeds" % (name, n_required))
    return out


def _gate(count, n, alpha):
    return count >= thresholds(n, alpha, Fraction(1, 20), Fraction(1, 2))["k_pos"]


def subject_stats(d, n, alpha=ALPHA):
    full = d["full"]
    pre = sum(1 for r in full.values() if 2 * r["c_pre"] > r["n_pre"])
    r5 = sum(1 for r in full.values() if 10 * r["c5_post"] >= 9 * r["n5_post"])
    out = dict(n=n, pre_competent_lives=pre, role5_retained_lives=r5, G_PRE=_gate(pre, n, alpha),
               G_R5=_gate(r5, n, alpha), instrument_ok=all(r["memory_ok"] and r["recompute_ok"]
                                                           for a in d.values() for r in a.values()))
    for k, ctrl in (("K1", "frozen"), ("K2", "shuffle")):
        s = [cmp_late(full[x], d[ctrl][x]) for x in sorted(full)]
        w, l = s.count(1), s.count(-1)
        out[k] = dict(control=ctrl, wins=w, losses=l, ties=s.count(0), p=sign_p(w, l))
    out["late"] = [sum(r["c_late"] for r in d[a].values()) for a in ("full", "frozen", "shuffle", "newlife")]
    out["late_n"] = [sum(r["n_late"] for r in d[a].values()) for a in ("full", "frozen", "shuffle", "newlife")]
    out["newlife_pre"] = [sum(r["c_pre"] for r in d["newlife"].values()), sum(r["n_pre"] for r in d["newlife"].values())]
    return out


def verdict(st, adj, alpha=ALPHA):
    if not st["instrument_ok"]:
        return "INSTRUMENT_FAULT"
    if not st["G_PRE"]:
        return "REFUSED_FIXED_PRIOR"
    k1, k2 = adj["K1"] <= alpha, adj["K2"] <= alpha
    if k1 and not st["G_R5"]:
        return "REVISION_WITHOUT_RETAINED_COMPETENCE"
    if k1:
        return "REVISION_HISTORY_DEPENDENT" if k2 else "REVISION_NOT_HISTORY_DEPENDENT"
    return "REVISION_NOT_SHOWN"


def verdicts(rows, n_required, alpha=ALPHA, families=None):
    """families: {family: [subjects]}; Holm runs over K1 and K2 of every subject in a family. Default: one family
    per subject."""
    by = _by(rows, n_required, ("full", "frozen", "shuffle", "newlife"))
    st = {name: subject_stats(d, n_required, alpha) for name, d in by.items()}
    families = families or {name: [name] for name in st}
    out = {}
    for fam, names in families.items():
        adj = holm({"%s|%s" % (nm, k): float(st[nm][k]["p"]) for nm in names for k in ("K1", "K2")})
        for nm in names:
            a = {k: adj["%s|%s" % (nm, k)] for k in ("K1", "K2")}
            out[nm] = dict(st[nm], family=fam, holm=a, verdict=verdict(st[nm], a, alpha))
    return out


def report(rows, n, searched=()):
    """The registered families: P = the reference; S = the searched subjects; each instrument control alone."""
    names = sorted({r["subject"] for r in rows})
    fam = {nm: [nm] for nm in names if nm not in searched}
    fam["P"] = fam.pop("reference")
    if searched:
        fam["S"] = list(searched)
    v = verdicts(rows, n, families=fam)
    for x in v.values():
        x["K1"]["p"], x["K2"]["p"] = str(x["K1"]["p"]), str(x["K2"]["p"])
    return v


def search_accessibility(v, searched):
    """Descriptive: how many of the searched subjects reached each verdict (the search budget is the scope)."""
    out = {}
    for nm in searched:
        out[v[nm]["verdict"]] = out.get(v[nm]["verdict"], 0) + 1
    return out


def q_shift(late_ref, effect):
    """P(reference beats a control whose late accuracy is the reference's lowered by `effect`), over every pair of
    independent development lives with the same switch block sw (the paired design matches sw by seed); exact
    rational, ties counted one half. No clipping at 0, so the shift cannot manufacture wins."""
    by, eff = {}, Fraction(effect)
    for sw, c, m in late_ref:
        by.setdefault(sw, []).append(Fraction(c, m))
    num = den = Fraction(0)
    for xs in by.values():
        for a in xs:
            for b in xs:
                d = a - (b - eff)
                num += 1 if d > 0 else (Fraction(1, 2) if d == 0 else 0)
                den += 1
    return num / den


def critical(n, alpha=ALPHA / 2):
    """Smallest win count k with P(X >= k | n, 1/2) <= alpha (alpha/2 = Holm's worst case over K1, K2)."""
    return next(k for k in range(n + 2) if k > n or tail_ge(n, k, Fraction(1, 2)) <= alpha)


def power(q, n, alpha=ALPHA / 2):
    """Exact power of the one-sided sign test with n untied pairs when P(win) = q."""
    return float(tail_ge(n, critical(n, alpha), Fraction(q).limit_denominator(10 ** 6)))
