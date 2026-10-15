"""Search-accessibility statistics (directive 2026-10-15 s5; C-019-T040 item 4). Pure Python + SciPy.

Unit: one SEARCH (a native run with its own seed and a registered budget). Per search the record is
(time, hit): `time` = generations (or evaluations) to the first generation whose champion the frozen ruler reads TRUE
when hit, else the budget actually spent (RIGHT-CENSORED). A failure to reach B is censored evidence, never an infinite
hitting time: nothing here returns inf or nan (JSON-safe), and a median that is not reached is the string
"NOT_REACHED". A search that never started (a wall-clock deadline before its first generation) is not a censored
observation; it is excluded upstream and counted separately (time 0 is refused).

    cp_interval(k, n)                       exact Clopper-Pearson interval for P(B within budget)
    fisher_one_sided(k1, n1, k0, n0)        P(X >= k1) under the hypergeometric null (arm 1 better)
    km(times, hits, budget=None)            Kaplan-Meier: step curve, P(B by budget), median, restricted mean
    logrank(t1, h1, t0, h0)                 two-sample log-rank (chi2, 1 df) -- descriptive with few events
    paired_binary([(hit1, hit0), ...])      exact McNemar on (cell, idx) pairs sharing gen-0 population and worlds
    paired_times([(t1, h1, t0, h0), ...])   which arm reached B first in each pair, censoring-aware
    power_fisher(p0, p1, n, alpha)          exact power of the one-sided Fisher test, n searches per arm
    min_detectable(p0, n, alpha, power)     smallest p1 reaching `power`
    n_per_arm(p0, p1, alpha, power)         smallest n per arm reaching `power`
"""
from __future__ import annotations

import math

from scipy import stats as _st


def cp_interval(k: int, n: int, level: float = 0.95) -> tuple:
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f"need 0 <= k <= n, n > 0 (k={k}, n={n})")
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(_st.beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(_st.beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def fisher_one_sided(k1: int, n1: int, k0: int, n0: int) -> float:
    """P(arm-1 successes >= k1 | total successes, margins): the exact one-sided test that arm 1 has the higher rate."""
    K, N = k1 + k0, n1 + n0
    if K == 0:
        return 1.0
    tot = math.comb(N, K)
    return min(1.0, sum(math.comb(n1, x) * math.comb(n0, K - x) for x in range(k1, min(n1, K) + 1)) / tot)


def km(times, hits, budget=None) -> dict:
    t = [float(v) for v in times]
    h = [bool(v) for v in hits]
    if len(t) != len(h) or not t:
        raise ValueError("times and hits must be non-empty and equal length")
    if any(v <= 0 for v in t):
        raise ValueError("time <= 0: a search that never ran is excluded upstream, not censored at 0")
    budget = float(budget if budget is not None else max(t))
    ev = sorted({v for v, x in zip(t, h) if x})
    S, curve, var_acc, gw = 1.0, [], 0.0, []
    for u in ev:
        n_risk = sum(1 for v in t if v >= u)
        d = sum(1 for v, x in zip(t, h) if x and v == u)
        S *= 1 - d / n_risk
        if n_risk > d:
            var_acc += d / (n_risk * (n_risk - d))
        curve.append(S); gw.append(math.sqrt(S * S * var_acc) if n_risk > d else 0.0)

    med = next((u for u, sv in zip(ev, curve) if sv <= 0.5), "NOT_REACHED")
    # restricted mean time to B, truncated at the budget: area under S on [0, budget]
    rmst, prev_t, prev_s = 0.0, 0.0, 1.0
    for u, sv in zip(ev, curve):
        if u > budget:
            break
        rmst += prev_s * (u - prev_t); prev_t, prev_s = u, sv
    rmst += prev_s * (budget - prev_t)
    return {"t": [int(u) if float(u).is_integer() else u for u in ev], "S": curve, "greenwood_se": gw,
            "n": len(t), "events": sum(h), "censored": len(t) - sum(h), "budget": budget,
            "p_by_budget": 1.0 - S_at({"t": ev, "S": curve}, budget), "median": int(med) if isinstance(med, float) and med.is_integer() else med,
            "rmst": rmst}


def S_at(r: dict, x: float) -> float:
    """Kaplan-Meier survival (no B yet) at time x from a km() record."""
    s = 1.0
    for u, sv in zip(r["t"], r["S"]):
        if u <= x:
            s = sv
    return s


def logrank(t1, h1, t0, h0) -> dict:
    rows = [(float(v), bool(x), 1) for v, x in zip(t1, h1)] + [(float(v), bool(x), 0) for v, x in zip(t0, h0)]
    ev = sorted({v for v, x, _ in rows if x})
    O1 = E1 = V = 0.0
    for u in ev:
        n1 = sum(1 for v, _, g in rows if g == 1 and v >= u); n0 = sum(1 for v, _, g in rows if g == 0 and v >= u)
        d1 = sum(1 for v, x, g in rows if g == 1 and x and v == u); d = sum(1 for v, x, _ in rows if x and v == u)
        n = n1 + n0
        O1 += d1; E1 += d * n1 / n
        if n > 1:
            V += d * (n1 / n) * (1 - n1 / n) * (n - d) / (n - 1)
    chi2 = (O1 - E1) ** 2 / V if V > 0 else 0.0
    return {"O1": O1, "E1": E1, "V": V, "chi2": chi2, "p": float(_st.chi2.sf(chi2, 1)) if V > 0 else 1.0,
            "events": len([1 for r in rows if r[1]])}


def paired_binary(rows) -> dict:
    """rows: (hit_arm1, hit_arm0) per (cell, idx) pair. b = arm1 only, c = arm0 only; exact one-sided McNemar."""
    b = sum(1 for x, y in rows if x and not y)
    c = sum(1 for x, y in rows if y and not x)
    n = b + c
    p = 1.0 if n == 0 else float(_st.binom.sf(b - 1, n, 0.5))
    return {"pairs": len(rows), "b": b, "c": c, "p_one_sided": p}


def paired_times(rows) -> dict:
    """rows: (t1, hit1, t0, hit0). A pair is decided when the earlier time is an observed hit (the other arm is then
    known not to have hit before it: its own hit is later or it was censored at or after that time). Ties in observed
    times, both censored, or a hit later than the other arm's censoring time are undecidable."""
    r1 = r0 = u = 0
    for t1, h1, t0, h0 in rows:
        if h1 and (t1 < t0 or (not h0 and t1 <= t0)):
            r1 += 1
        elif h0 and (t0 < t1 or (not h1 and t0 <= t1)):
            r0 += 1
        else:
            u += 1
    n = r1 + r0
    return {"reuse_first": r1, "control_first": r0, "undecidable": u,
            "p_one_sided": 1.0 if n == 0 else float(_st.binom.sf(r1 - 1, n, 0.5))}


def _binom_pmf(n, p):
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


_REJECT: dict = {}


def _reject(n: int, alpha: float) -> list:
    """kmin[k0] = smallest k1 with fisher_one_sided(k1, n, k0, n) <= alpha (n + 1 if none); p is monotone in k1."""
    key = (n, alpha)
    if key not in _REJECT:
        out = []
        for k0 in range(n + 1):
            k1 = next((k for k in range(n + 1) if fisher_one_sided(k, n, k0, n) <= alpha), n + 1)
            out.append(k1)
        _REJECT[key] = out
    return _REJECT[key]


def power_fisher(p0: float, p1: float, n: int, alpha: float = 0.05) -> float:
    """Exact power of the one-sided Fisher test (arm 1 better) with n searches per arm, by enumeration."""
    f0, f1 = _binom_pmf(n, p0), _binom_pmf(n, p1)
    km_ = _reject(n, alpha)
    return sum(f0[k0] * sum(f1[k1] for k1 in range(km_[k0], n + 1)) for k0 in range(n + 1) if f0[k0])


def min_detectable(p0: float, n: int, alpha: float = 0.05, power: float = 0.8, step: float = 0.0025):
    p1 = p0
    while p1 <= 1.0:
        if power_fisher(p0, p1, n, alpha) >= power:
            return round(p1, 6)
        p1 += step
    return "NOT_DETECTABLE"


def n_per_arm(p0: float, p1: float, alpha: float = 0.05, power: float = 0.8, n_max: int = 400):
    for n in range(2, n_max + 1):
        if power_fisher(p0, p1, n, alpha) >= power:
            return n
    return f"> {n_max}"


# ------------------------------------------------------------------ the search table (one row per native search)
def validate_searches(rows, arms) -> list:
    """Contract of a search table (refusals, never repairs). Row: {arm, cell, idx, ran, budget, checkpoints:
    [{gen, status}], hit, time}. `hit`/`time` are DERIVED: hit iff some checkpoint is TRUE, time = the first TRUE
    checkpoint's gen, else the last checkpoint's gen (right-censored). Every (cell, idx) must appear exactly once in
    every arm (arms share gen-0 populations and training worlds, so the pair is the unit). A search that never ran has
    no checkpoints and is excluded from the statistics, not counted as a failure."""
    probs, seen = [], {}
    for i, r in enumerate(rows):
        try:
            key = (r["arm"], r["cell"], int(r["idx"]))
            ran, budget, cks = bool(r["ran"]), int(r["budget"]), r["checkpoints"]
            hit, t = r["hit"], r["time"]
        except (KeyError, TypeError, ValueError) as e:
            probs.append(f"row {i}: missing or malformed field ({e})"); continue
        if key[0] not in arms:
            probs.append(f"row {i}: arm {key[0]} not declared")
        if key in seen:
            probs.append(f"row {i}: DUPLICATE search {key} (also row {seen[key]})")
        seen[key] = i
        if not isinstance(hit, bool):
            probs.append(f"row {i}: hit is not a boolean")
        if not ran:
            if cks or hit:
                probs.append(f"row {i}: a search that never ran carries checkpoints or a hit")
            continue
        gens = [c.get("gen") for c in cks]
        if not cks or gens != sorted(gens) or len(set(gens)) != len(gens) or gens[0] <= 0 or gens[-1] > budget:
            probs.append(f"row {i}: checkpoints missing, unordered, or outside (0, budget]"); continue
        first = next((c["gen"] for c in cks if c.get("status") == "TRUE"), None)
        want_hit, want_t = first is not None, first if first is not None else gens[-1]
        if hit != want_hit or t != want_t:
            probs.append(f"row {i}: derived hit/time ({hit}, {t}) != recomputed from checkpoints ({want_hit}, {want_t})")
        if not 0 < t <= budget:
            probs.append(f"row {i}: time {t} outside (0, budget {budget}]")
    pairs = {}
    for (arm, cell, idx) in seen:
        pairs.setdefault((cell, idx), set()).add(arm)
    for p, a in sorted(pairs.items()):
        if set(arms) - a:
            probs.append(f"UNPAIRED {p}: missing arms {sorted(set(arms) - a)}")
    return probs


def _recompute(r) -> tuple:
    first = next((c["gen"] for c in r["checkpoints"] if c["status"] == "TRUE"), None)
    return (first is not None, first if first is not None else r["checkpoints"][-1]["gen"])


def compare_arms(rows, arm1: str, arm0: str, alpha: float = 0.05) -> dict:
    """arm1 (e.g. REUSE) against arm0 (e.g. CONTROL). Refuses an invalid table. Hits and times are recomputed from
    the checkpoints (never read from the row). Pairs where either search never ran are dropped from the paired tests
    and counted."""
    probs = validate_searches(rows, (arm1, arm0))
    if probs:
        raise ValueError("search table refused: " + "; ".join(probs[:5]))
    by = {(r["arm"], r["cell"], int(r["idx"])): r for r in rows}
    out = {}
    for tag, arm in (("arm1", arm1), ("arm0", arm0)):
        ran = [r for r in rows if r["arm"] == arm and r["ran"]]
        hits = [_recompute(r) for r in ran]
        k, n = sum(h for h, _ in hits), len(ran)
        out[tag] = {"arm": arm, "n": n, "not_run": sum(1 for r in rows if r["arm"] == arm and not r["ran"]), "hits": k,
                    "p_hat": k / n if n else None, "cp95": list(cp_interval(k, n)) if n else None,
                    "km": km([t for _, t in hits], [h for h, _ in hits], budget=max(int(r["budget"]) for r in ran)) if n else None}
    keys = sorted({(c, i) for (a, c, i) in by})
    both = [(by[(arm1, c, i)], by[(arm0, c, i)]) for c, i in keys if by[(arm1, c, i)]["ran"] and by[(arm0, c, i)]["ran"]]
    pb = paired_binary([(_recompute(a)[0], _recompute(b)[0]) for a, b in both])
    pt = paired_times([(_recompute(a)[1], _recompute(a)[0], _recompute(b)[1], _recompute(b)[0]) for a, b in both])
    out["paired"] = dict(pb, pairs_dropped_not_run=len(keys) - len(both), first_to_B=pt)
    out["fisher_one_sided"] = fisher_one_sided(out["arm1"]["hits"], out["arm1"]["n"], out["arm0"]["hits"], out["arm0"]["n"])
    out["logrank"] = logrank([_recompute(a)[1] for a, _ in both], [_recompute(a)[0] for a, _ in both],
                             [_recompute(b)[1] for _, b in both], [_recompute(b)[0] for _, b in both])
    return out
