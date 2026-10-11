"""C-016-T030 decision rule, amended in C-016-T041 (PREREGISTRATION.md v1.1.0 s5). Exact and integer-first: no
floating-point statistic decides.

v1.1.0 (the one repair round; rso/ensorain/challenge/REPORT.md s4-s5): the contrasts read a WHOLE-LIFE binary endpoint
(`revised`: majority-correct on role 1 before the switch AND in the late window), so no fixed-sign policy on either
side of the law can score; K1 must hold against BOTH the frozen arm and the noise-matched arm (an intersection-union
test: its p is the larger of the two); G_R5 has a competence bound; family S is declared from genome structure.

Unit = the lifetime. Reused within scope: the exact binomial tails and integer thresholds of rso/witness/ruler.py
(registry entry ruler-binary-retention: a binary per-unit outcome with a known chance bound; here the unit is the
lifetime, so the 'dependent episodes' limit is respected) and Holm from rso/reach/stats.py.
"""
from fractions import Fraction

from rso.reach.stats import holm
from rso.witness.ruler import tail_ge, thresholds

ALPHA = Fraction(1, 20)
R5_BOUND = Fraction(9, 10)                 # G_R5: significantly more than 9 lives in 10 keep role 5 (v1.1.0, B3)
ARMS = ("full", "frozen", "noise", "shuffle", "newlife", "noswitch")
REVISIONS = ("REVISION_HISTORY_DEPENDENT", "REVISION_NOT_HISTORY_DEPENDENT", "REVISION_WITHOUT_RETAINED_COMPETENCE")
VERDICTS = ("INSTRUMENT_FAULT", "REFUSED_FIXED_PRIOR") + REVISIONS + ("REVISION_NOT_SHOWN", "NOT_TESTED_PARAMETER_FREE")


class AnalysisError(ValueError):
    pass


def sign_p(wins, losses):
    """One-sided exact sign test: P(X >= wins), X ~ Binomial(wins + losses, 1/2); ties are dropped."""
    n = wins + losses
    return Fraction(1) if n == 0 else tail_ge(n, wins, Fraction(1, 2))


def cmp_late(a, b):
    """Sign of c_late/n_late (a) minus (b), by integer cross-multiplication. Descriptive in v1.1.0."""
    x, y = a["c_late"] * b["n_late"], b["c_late"] * a["n_late"]
    return (x > y) - (x < y)


def revised(r):
    """The v1.1.0 per-life endpoint: role 1 majority-correct before the switch AND in the late window (b >= sw + 3).
    A fixed sign policy, +s or -s, with or without perturbation noise, is correct with the same per-gate probability
    p on one side and 1 - p on the other, so in expectation it cannot hold both halves."""
    return 2 * r["c_pre"] > r["n_pre"] and 2 * r["c_late"] > r["n_late"]


def contrast(full, ctrl, control):
    """Paired by seed: a win is a life revised in the full arm and not in the control, a loss the reverse."""
    s = [revised(full[x]) - revised(ctrl[x]) for x in sorted(full)]
    w, l = s.count(1), s.count(-1)
    return dict(control=control, wins=w, losses=l, ties=s.count(0), p=sign_p(w, l))


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


def _competence(count, n, alpha):
    """G_R5 (v1.1.0): the count of lives keeping role 5 is significantly above R5_BOUND of the lives (exact binomial,
    the ruler's integer threshold with bound 9/10). 180 lives at zero role-5 accuracy out of 400 cannot pass."""
    return count >= thresholds(n, alpha, Fraction(1, 20), R5_BOUND)["k_pos"]


def subject_stats(d, n, alpha=ALPHA):
    full = d["full"]
    pre = sum(1 for r in full.values() if 2 * r["c_pre"] > r["n_pre"])
    r5 = sum(1 for r in full.values() if 10 * r["c5_post"] >= 9 * r["n5_post"])
    out = dict(n=n, pre_competent_lives=pre, role5_retained_lives=r5, G_PRE=_gate(pre, n, alpha),
               G_R5=_competence(r5, n, alpha), instrument_ok=all(r["memory_ok"] and r["recompute_ok"]
                                                                 for a in d.values() for r in a.values()))
    for k, ctrl in (("K1", "frozen"), ("K2", "shuffle")):
        out[k] = contrast(full, d[ctrl], ctrl)
    out["K1_noise"] = contrast(full, d["noise"], "noise")
    out["K1"]["p_frozen"], out["K1"]["control"] = out["K1"]["p"], "frozen+noise"
    out["K1"]["p"] = max(out["K1"]["p"], out["K1_noise"]["p"])          # intersection-union: both must hold
    # printed beside every verdict (REPORT s4.1): per-arm revised lives and late-window accuracy (descriptive)
    out["arms"] = list(ARMS)
    out["revised_lives"] = [sum(revised(r) for r in d[a].values()) for a in ARMS]
    out["late"] = [sum(r["c_late"] for r in d[a].values()) for a in ARMS]
    out["late_n"] = [sum(r["n_late"] for r in d[a].values()) for a in ARMS]
    out["newlife_pre"] = [sum(r["c_pre"] for r in d["newlife"].values()), sum(r["n_pre"] for r in d["newlife"].values())]
    out["noswitch_late_majority_lives"] = sum(2 * r["c_late"] > r["n_late"] for r in d["noswitch"].values())
    return out


def verdict(st, adj, alpha=ALPHA):
    if not st["instrument_ok"]:
        return "INSTRUMENT_FAULT"
    if adj is None:
        return "NOT_TESTED_PARAMETER_FREE"
    if not st["G_PRE"]:
        return "REFUSED_FIXED_PRIOR"
    k1, k2 = adj["K1"] <= alpha, adj["K2"] <= alpha
    if k1 and not st["G_R5"]:
        return "REVISION_WITHOUT_RETAINED_COMPETENCE"
    if k1:
        return "REVISION_HISTORY_DEPENDENT" if k2 else "REVISION_NOT_HISTORY_DEPENDENT"
    return "REVISION_NOT_SHOWN"


def verdicts(rows, n_required, alpha=ALPHA, families=None, untested=()):
    """families: {family: [subjects]}; Holm runs over K1 and K2 of every subject in a family. Default: one family
    per subject. `untested`: subjects reported (statistics, instrument check) but not tested."""
    by = _by(rows, n_required, ARMS)
    st = {name: subject_stats(d, n_required, alpha) for name, d in by.items()}
    families = families or {name: [name] for name in st if name not in untested}
    out = {nm: dict(st[nm], family=None, holm=None, verdict=verdict(st[nm], None, alpha)) for nm in untested}
    for fam, names in families.items():
        adj = holm({"%s|%s" % (nm, k): float(st[nm][k]["p"]) for nm in names for k in ("K1", "K2")})
        for nm in names:
            a = {k: adj["%s|%s" % (nm, k)] for k in ("K1", "K2")}
            out[nm] = dict(st[nm], family=fam, holm=a, verdict=verdict(st[nm], a, alpha))
    return out


def report(rows, n, searched=(), tested=None):
    """The registered families: P = the reference; S = the searched subjects that carry an active plastic parameter
    (`tested`, declared from genome structure before the run: assay.family_s); each instrument control alone. The
    parameter-free searched subjects are reported, not tested (v1.1.0, REPORT s5.5)."""
    names = sorted({r["subject"] for r in rows})
    tested = list(searched) if tested is None else list(tested)
    untested = [nm for nm in searched if nm not in tested]
    fam = {nm: [nm] for nm in names if nm not in searched}
    fam["P"] = fam.pop("reference")
    if tested:
        fam["S"] = tested
    v = verdicts(rows, n, families=fam, untested=untested)
    for x in v.values():
        for k in ("K1", "K2", "K1_noise"):
            x[k] = dict(x[k], **{f: str(x[k][f]) for f in ("p", "p_frozen") if f in x[k]})
    return v


def qualification(v):
    """PREREGISTRATION v1.1.0 s5: the run is DETECTION_UNQUALIFIED, and no subject verdict is read, if any fails."""
    q = {"Q-a": all(x["instrument_ok"] for x in v.values()),
         "Q-b": all(v[nm]["verdict"] == "REFUSED_FIXED_PRIOR"
                    for nm in ("smuggler", "smuggler_decorative", "constant_plus", "constant_minus")),
         "Q-c": v["memoryless_plus"]["verdict"] not in REVISIONS,
         "Q-d": v["jitter"]["verdict"] not in REVISIONS,
         "Q-e": v["learns_pre"]["verdict"] in REVISIONS}
    return dict(q, qualified=all(q.values()))


def search_accessibility(v, searched):
    """Descriptive: how many of the searched subjects reached each verdict (the search budget is the scope); the
    parameter-free ones are counted under NOT_TESTED_PARAMETER_FREE."""
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


def power_revised(p_full, p_ctrl, n, alpha=ALPHA / 2):
    """Power of the v1.1.0 contrast at n lives when a life is revised with probability p_full in the full arm and
    p_ctrl in the control, independently given the seed: discordant pairs D ~ Bin(n, w + l), wins | D ~ Bin(D,
    w / (w + l)), w = p_full (1 - p_ctrl), l = p_ctrl (1 - p_full). Descriptive (float), summed over every D."""
    from math import comb
    w, l = p_full * (1 - p_ctrl), p_ctrl * (1 - p_full)
    if w + l == 0:
        return 0.0
    q, pd, tot = w / (w + l), w + l, 0.0
    for dd in range(1, n + 1):
        k = critical(dd, alpha)
        if k <= dd:
            tot += comb(n, dd) * pd ** dd * (1 - pd) ** (n - dd) * sum(
                comb(dd, j) * q ** j * (1 - q) ** (dd - j) for j in range(k, dd + 1))
    return tot
