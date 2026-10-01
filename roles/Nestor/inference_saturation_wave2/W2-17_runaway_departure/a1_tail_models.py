"""W2-17 a1: is the d~20 'departure' a second regime, or the ordinary crossover of ONE slightly
supercritical branching process (S(d) ~ 1/d for d << 1/eps, then a plateau 2*eps/sigma^2)?
Data: the K2b BASE splice-off pool (670 runs, 367 with D >= 1). Likelihood on D | D >= 1 with
D >= DC right-censored (DC = 22 primary; DC = 161 secondary, which also scores the 22..160 gap).
Models (S(d) = P(D >= d | D >= 1)):
  CRIT   1/d                                      k=0
  POW    d^-a                                     k=1
  GEOM   q^(d-1)                                  k=1
  GW     homogeneous Galton-Watson, zero-modified geometric offspring (p0, r), exact iterates  k=2
  GEOM+I geometric body + immortal fraction pi    k=2
  CRIT+I 1/d body + immortal fraction pi          k=1
Prediction readouts: P(D >= 161 | D >= 22), P(14 <= D <= 21 | D >= 8)."""
import json, math, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a0_pool import load

DMAX = 700


def gw_S(p0, r, dmax=DMAX):
    # offspring pgf f(s) = p0 + (1-p0)(1-r)s/(1-rs)
    s, ext = 0.0, [0.0]
    for _ in range(dmax + 2):
        s = p0 + (1 - p0) * (1 - r) * s / (1 - r * s)
        ext.append(s)            # ext[d] = P(Z_d = 0)
    P = [1 - e for e in ext]     # P(Z_d > 0) = P(D >= d)
    return lambda d: P[d] / P[1]


def ll(ds, S, DC):
    t = 0.0
    for d in ds:
        if d >= DC:
            t += math.log(max(S(DC), 1e-300))
        else:
            t += math.log(max(S(d) - S(d + 1), 1e-300))
    return t


def grid_fit(ds, DC):
    out = {}
    out["CRIT"] = (ll(ds, lambda d: 1.0 / d, DC), 0, {})
    b = max(((ll(ds, lambda d, a=a: d ** -a, DC), a) for a in [i / 100 for i in range(30, 300)]))
    out["POW"] = (b[0], 1, {"a": b[1]})
    b = max(((ll(ds, lambda d, q=q: q ** (d - 1), DC), q) for q in [i / 1000 for i in range(300, 999)]))
    out["GEOM"] = (b[0], 1, {"q": b[1]})
    best = None
    for p0 in [i / 100 for i in range(5, 95)]:
        for r in [i / 100 for i in range(1, 99)]:
            m = (1 - p0) / (1 - r)
            if not 0.7 <= m <= 1.6:
                continue
            S = gw_S(p0, r)
            v = ll(ds, S, DC)
            if best is None or v > best[0]:
                best = (v, p0, r)
    v, p0, r = best
    # refine
    for _ in range(2):
        for dp in [i / 1000 for i in range(-20, 21, 2)]:
            for dr in [i / 1000 for i in range(-20, 21, 2)]:
                q0, rr = p0 + dp, r + dr
                if not (0 < q0 < 1 and 0 < rr < 1):
                    continue
                vv = ll(ds, gw_S(q0, rr), DC)
                if vv > v:
                    v, p0, r = vv, q0, rr
    m = (1 - p0) / (1 - r)
    var = (1 - p0) * (1 + r) / (1 - r) ** 2 - m * m
    S = gw_S(p0, r)
    out["GW"] = (v, 2, {"p0": round(p0, 3), "r": round(r, 3), "m": round(m, 4), "sigma2": round(var, 3),
                        "S_inf_given_pos": round(S(DMAX), 4), "S": S})
    b = max(((ll(ds, lambda d, q=q, pi=pi: pi + (1 - pi) * q ** (d - 1), DC), q, pi)
             for q in [i / 200 for i in range(100, 199)] for pi in [i / 1000 for i in range(1, 150)]))
    out["GEOM+I"] = (b[0], 2, {"q": b[1], "pi": b[2]})
    b = max(((ll(ds, lambda d, pi=pi: pi + (1 - pi) / d, DC), pi) for pi in [i / 1000 for i in range(0, 150)]))
    out["CRIT+I"] = (b[0], 1, {"pi": b[1]})
    return out


def main():
    rows = load()
    ds = [r[2] for r in rows if r[2] >= 1]
    n = len(ds)
    obs = {"n_pos": n, "ge8": sum(d >= 8 for d in ds), "14_21": sum(14 <= d <= 21 for d in ds),
           "ge22": sum(d >= 22 for d in ds), "ge161": sum(d >= 161 for d in ds),
           "P161_given_22": round(sum(d >= 161 for d in ds) / sum(d >= 22 for d in ds), 3)}
    res = {"observed": obs}
    for DC in (22, 161):
        fits = grid_fit(ds, DC)
        tab = {}
        for k, (v, kk, par) in fits.items():
            S = par.pop("S", None)
            if k == "CRIT": S = lambda d: 1.0 / d
            elif k == "POW": S = lambda d, a=par["a"]: d ** -a
            elif k == "GEOM": S = lambda d, q=par["q"]: q ** (d - 1)
            elif k == "GEOM+I": S = lambda d, q=par["q"], pi=par["pi"]: pi + (1 - pi) * q ** (d - 1)
            elif k == "CRIT+I": S = lambda d, pi=par["pi"]: pi + (1 - pi) / d
            tab[k] = {"ll": round(v, 2), "k": kk, "aic": round(2 * kk - 2 * v, 2), **par,
                      "pred_P161_given_22": round(S(161) / S(22), 3),
                      "pred_n_14_21": round(n * (S(14) - S(22)), 2),
                      "pred_n_ge22": round(n * S(22), 2),
                      "pred_n_8_13": round(n * (S(8) - S(14)), 2),
                      "S_2_4_8_16_20": [round(S(d), 4) for d in (2, 4, 8, 16, 20)]}
        res["censor_%d" % DC] = tab
    obs["n_8_13"] = sum(8 <= d <= 13 for d in ds)
    obs["S_2_4_8_16_20"] = [round(sum(x >= d for x in ds) / n, 4) for d in (2, 4, 8, 16, 20)]
    (HERE / "a1_tail_models.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


main()
