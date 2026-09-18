"""Campaign 0 assay: the blind analysis (PREREG_C0 sections 3-4). TIER 2.

Sees only the observation record. One number per lineage per contrast;
inference across lineages (the lineage is the experimental unit).
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple

from worlds import CELLS, MODULES, N_TASKS

ALPHA = 0.05


# ------------------------------------------------------------------ t distribution (stdlib)
def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > FPMIN else FPMIN)
        c = 1.0 + aa / c
        c = c if abs(c) > FPMIN else FPMIN
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: int) -> float:
    x = df / (df + t * t)
    tail = 0.5 * _ibeta(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_ppf(q: float, df: int) -> float:
    lo, hi = -50.0, 50.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def norm_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# ------------------------------------------------------------------ per-lineage contrasts
def share(solved: List[int]) -> float:
    return sum(solved) / (len(solved) * N_TASKS)


def _c(kind, mods=(), M="M0", A="A0", met="enf", fs="VAULT", B=1.0):
    return ((kind, tuple(mods)), M, A, met, fs, B)


CONTRASTS: Dict[str, Tuple] = {
    "D_VAULT": (_c("I8"), _c("I0")),
    "D_DEV": (_c("I8", fs="DEV"), _c("I0", fs="DEV")),
    "D_MEM": (_c("I0", M="M8", fs="DEV"), _c("I0", fs="DEV")),
    "D_WORK": (_c("I0", A="A8"), _c("I0")),
    "D_COMP": (_c("I8", met="asrun"), _c("I8")),
    "ASRUN": (_c("I8", M="M8", A="A8", met="asrun", fs="DEV"), _c("I0", fs="DEV")),
}
for _m in MODULES:
    CONTRASTS[f"NEC_{_m}"] = (_c("I8"), _c("I8-", (_m,)))
    CONTRASTS[f"SUF_{_m}"] = (_c("I0+", (_m,)), _c("I0"))
FRONTIER = {b: (_c("I8", B=b), _c("I0", B=b)) for b in (0.5, 1.0, 2.0)}


def lineage_values(obs: Dict, a, b) -> List[float]:
    return [share(l["cells"][a]) - share(l["cells"][b]) for l in obs["lineages"]]


# ------------------------------------------------------------------ inference
def holm(ps: Dict[str, float]) -> Dict[str, float]:
    order = sorted(ps, key=ps.get)
    m, out, run = len(order), {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[k]))
        out[k] = run
    return out


def summarize_t(x: List[float], delta: float):
    n = len(x)
    mean = sum(x) / n
    var = sum((v - mean) ** 2 for v in x) / (n - 1)
    se = math.sqrt(var / n) if var > 0 else 1e-12
    df = n - 1
    p_sup = 1 - t_cdf(mean / se, df)
    p_inf = t_cdf(mean / se, df)
    p_eq = max(1 - t_cdf((mean + delta) / se, df), t_cdf((mean - delta) / se, df))
    return mean, se, p_sup, p_inf, p_eq


def summarize_boot(x: List[float], delta: float, rng: random.Random, nb: int = 300):
    n = len(x)
    mean = sum(x) / n
    reps = sorted(sum(rng.choices(x, k=n)) / n for _ in range(nb))
    p_sup = max(sum(r <= 0 for r in reps) / nb, 1 / nb)
    p_inf = max(sum(r >= 0 for r in reps) / nb, 1 / nb)
    lo, hi = reps[int(0.05 * nb)], reps[int(0.95 * nb) - 1]
    p_eq = 0.01 if (lo > -delta and hi < delta) else 0.99
    return mean, None, p_sup, p_inf, p_eq


def summarize_pseudo(obs: Dict, a, b, delta: float):
    """WRONG analysis on purpose (sensitivity d): every task treated as independent."""
    sa = sum(sum(l["cells"][a]) for l in obs["lineages"])
    sb = sum(sum(l["cells"][b]) for l in obs["lineages"])
    n = len(obs["lineages"]) * len(obs["lineages"][0]["cells"][a]) * N_TASKS
    pa, pb = sa / n, sb / n
    d = pa - pb
    se = math.sqrt(max(pa * (1 - pa) + pb * (1 - pb), 1e-12) / n)
    p_sup, p_inf = 1 - norm_cdf(d / se), norm_cdf(d / se)
    p_eq = max(1 - norm_cdf((d + delta) / se), norm_cdf((d - delta) / se))
    return d, se, p_sup, p_inf, p_eq


def verdict(sig: bool, p_inf: float, p_eq: float) -> str:
    eq = p_eq < ALPHA
    if sig and not eq:
        return "SUPERIOR"
    if sig and eq:
        return "TRIVIAL"
    if eq:
        return "EQUIVALENT"
    if p_inf < ALPHA:
        return "INFERIOR"
    return "INDETERMINATE"


def analyse(obs: Dict, delta: float = 0.03, method: str = "t", use_holm: bool = True,
            rng: random.Random = None) -> Dict:
    rng = rng or random.Random(12345)
    stats = {}
    for k, (a, b) in CONTRASTS.items():
        if method == "pseudo":
            stats[k] = summarize_pseudo(obs, a, b, delta)
        elif method == "boot":
            stats[k] = summarize_boot(lineage_values(obs, a, b), delta, rng)
        else:
            stats[k] = summarize_t(lineage_values(obs, a, b), delta)
    p_sup = {k: s[2] for k, s in stats.items()}
    p_adj = holm(p_sup) if use_holm else p_sup
    v = {k: verdict(p_adj[k] < ALPHA, stats[k][3], stats[k][4]) for k in stats}
    meter = [l["meter"] for l in obs["lineages"]]
    n = len(meter)
    mm = sum(meter) / n
    sd = math.sqrt(sum((x - mm) ** 2 for x in meter) / (n - 1))
    meter_lo = mm - t_ppf(0.975, n - 1) * sd / math.sqrt(n)
    flags = set()
    if v["D_VAULT"] == "SUPERIOR":
        flags.add("TRANSFER")
    if v["D_DEV"] == "SUPERIOR" and v["D_VAULT"] in ("EQUIVALENT", "TRIVIAL", "INFERIOR"):
        flags.add("SPECIALIZATION")
    if v["D_MEM"] == "SUPERIOR":
        flags.add("MEMORY")
    if v["D_WORK"] == "SUPERIOR":
        flags.add("WORKER")
    if meter_lo > 1.05 and v["D_COMP"] == "SUPERIOR":
        flags.add("COMPUTE")
    ambiguous = v["D_DEV"] == "SUPERIOR" and v["D_VAULT"] == "INDETERMINATE"
    modules = {m for m in MODULES if v[f"NEC_{m}"] == "SUPERIOR" and v[f"SUF_{m}"] == "SUPERIOR"}
    frontier = {b: sum(lineage_values(obs, *FRONTIER[b])) / n for b in FRONTIER}
    return {"verdicts": v, "flags": flags, "ambiguous": ambiguous, "modules": modules,
            "meter_lo": meter_lo, "means": {k: s[0] for k, s in stats.items()}, "frontier": frontier}


RULES = {
    "W1": lambda r: r["flags"] == {"TRANSFER"},
    "W2": lambda r: (r["flags"] == {"MEMORY"} and r["verdicts"]["ASRUN"] == "SUPERIOR"
                     and r["verdicts"]["D_DEV"] != "SUPERIOR" and r["verdicts"]["D_VAULT"] != "SUPERIOR"),
    "W3": lambda r: (r["flags"] == {"COMPUTE"} and r["verdicts"]["D_COMP"] == "SUPERIOR"
                     and r["verdicts"]["D_DEV"] != "SUPERIOR" and r["verdicts"]["D_VAULT"] != "SUPERIOR"),
    "W4": lambda r: r["flags"] == {"SPECIALIZATION"},
    "W5": lambda r: r["flags"] == {"TRANSFER"} and r["modules"] == {"verify"},
    "W6": lambda r: not r["flags"],
    "W7": lambda r: r["flags"] == {"WORKER"},
    "W8": lambda r: r["flags"] == {"TRANSFER", "MEMORY", "COMPUTE"},
    "W9": lambda r: not r["flags"],  # AMENDMENT 1
}
PLANTED = {"W1": {"TRANSFER"}, "W2": {"MEMORY"}, "W3": {"COMPUTE"}, "W4": {"SPECIALIZATION"},
           "W5": {"TRANSFER"}, "W6": set(), "W7": {"WORKER"}, "W8": {"TRANSFER", "MEMORY", "COMPUTE"},
           "W9": set()}


def recovered(world_key: str, r: Dict) -> bool:
    return (not r["ambiguous"]) and RULES[world_key](r)
