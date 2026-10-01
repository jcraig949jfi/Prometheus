"""W-Q T-SWAP-REL2: relative carrier-swap verdict with PER-VERDICT attainability.
Rule frozen in PLAN.md (sha256 e0bbee84...) s2. Summary:

CERTIFICATE (W-N swap_rel.rule, copied; bootstrap evaluated as a count-matrix
product, numerically identical to W-N's index-gather up to float summation order):
    DF = (s-.5)+(a-.5)/2, DN = (s-.5)-(a-.5)/2, 99% pair bootstrap, 2000, seed 0
    FLIP_REL hi(DF)<0 | NO_EFFECT_REL lo(DN)>0 | CHANCE_REL lo(DF)>0 & hi(DN)<0
IDENTIFICATION GUARD: lo99(normal) <= .5 -> NOT_ELIGIBLE for all verdicts.
PER-VERDICT ATTAINABILITY (from P, K and the normal CI):
    CERT_OK_V  false-certificate rate at V's boundary <= 1% on the FC grid, under
               the WORST and REALISTIC dependence models (simulation, n=4000).
    REACH_V    lo99(normal) >= p_min_V = smallest p with power_V >= .80 at all
               p' >= p (max over the two models; n=400).
    ATTAIN_V   guard & CERT_OK_V & REACH_V.
LABEL (primary REL2): certificate V -> V if CERT_OK_V else NOT_ELIGIBLE;
    no certificate -> INDETERMINATE if any ATTAIN_V else NOT_ELIGIBLE.
    NE = verdicts not attainable (their absence is uninformative).
REL2-STRICT (sensitivity): a certificate V also needs REACH_V.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

N_BOOT = 2000
LEVEL = 0.99
FC_MAX = 0.01
POWER = 0.80
N_SIM_FC = 4000
N_SIM_POW = 400
FC_GRID = (0.50, 0.51, 0.52, 0.55, 0.58, 0.60, 0.65, 0.70, 0.80, 0.90, 0.95, 0.99)
POW_GRID = tuple(round(0.5 + 0.01 * i, 2) for i in range(51))
MODELS = ("worst", "realistic")
CERTS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
TRUE_Z = {"FLIP_REL": -1.0, "CHANCE_REL": 0.0, "NO_EFFECT_REL": 1.0}
HERE = pathlib.Path(__file__).resolve().parent
TABLE = HERE / "out" / "attain2_table.json"


# ------------------------------------------------------------------ bootstrap / certificate
def boot_counts(P: int, n_boot: int = N_BOOT, seed: int = 0) -> np.ndarray:
    """[n_boot, P] resample counts from exactly W-N's index draw."""
    idx = np.random.default_rng(seed).integers(0, P, size=(n_boot, P))
    C = np.zeros((n_boot, P))
    np.add.at(C, (np.repeat(np.arange(n_boot), P), idx.ravel()), 1.0)
    return C


def _ci(v: np.ndarray, C: np.ndarray, level: float):
    bs = (v @ C.T) / C.shape[1]
    q = (1 - level) / 2
    lo, hi = np.quantile(bs, [q, 1 - q], axis=-1)
    return v.mean(-1), lo, hi


def certificate(a, s, C=None, level=LEVEL) -> dict:
    """a, s: [..., P] pair means. Returns certificate verdict (INDETERMINATE when none)."""
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    if C is None:
        C = boot_counts(a.shape[-1])
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    mF, loF, hiF = _ci(DF, C, level)
    mN, loN, hiN = _ci(DN, C, level)
    v = np.full(np.shape(mF), "INDETERMINATE", dtype="<U13")
    v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
    v = np.where(loN > 0, "NO_EFFECT_REL", v)
    v = np.where(hiF < 0, "FLIP_REL", v)
    return {"verdict": v, "DF": (mF, loF, hiF), "DN": (mN, loN, hiN)}


# ------------------------------------------------------------------ dependence models
def simulate(model: str, p: float, z: float, P: int, K: int, n: int, rng, conc: float = 4.0):
    """-> a, s [n, P] pair means under a truth (normal p, relative swap z)."""
    if model == "worst":
        a = rng.binomial(K, p, (n, P)) / K
        s = rng.binomial(K, 0.5 + z * (p - 0.5), (n, P)) / K
    elif model == "realistic":
        a = rng.binomial(K, p, (n, P)) / K
        t, u = (-z, 0.0) if z < 0 else (0.0, z)
        r = rng.random((n, P))
        fresh = rng.binomial(K, 0.5, (n, P)) / K
        s = np.where(r < t, 1 - a, np.where(r < t + u, a, fresh))
    elif model == "hetero":   # OUT-OF-MODEL check only (PLAN V1): overdispersed pairs
        if p in (0.0, 1.0):
            pi = np.full((n, P), p)
        else:
            pi = rng.beta(p * conc, (1 - p) * conc, (n, P))
        a = rng.binomial(K, pi) / K
        s = rng.binomial(K, 0.5 + z * (pi - 0.5)) / K
    else:
        raise KeyError(model)
    return a, s


def rates(model, p, z, P, K, n, level=LEVEL, seed=777, C=None, chunk=1000):
    """Fraction of simulations returning each certificate."""
    rng = np.random.default_rng([seed, P, K, int(round(p * 1000)), int(round(z * 1000) + 5000),
                                 MODELS.index(model) if model in MODELS else 9])
    C = boot_counts(P) if C is None else C
    cnt = {v: 0 for v in (*CERTS, "INDETERMINATE")}
    done = 0
    while done < n:
        m = min(chunk, n - done)
        a, s = simulate(model, p, z, P, K, m, rng)
        v = certificate(a, s, C, level)["verdict"]
        for k in cnt:
            cnt[k] += int(np.sum(v == k))
        done += m
    return {k: c / n for k, c in cnt.items()}


def fc_curve(model, P, K, grid=FC_GRID, n=N_SIM_FC, level=LEVEL):
    """FC_V(p): certificate V issued at V's boundary truth(s)."""
    C = boot_counts(P)
    out = {}
    for p in grid:
        if p == 0.5:
            r = rates(model, p, 0.0, P, K, n, level, C=C)
            out[p] = {v: r[v] for v in CERTS}
            continue
        rm = rates(model, p, -0.5, P, K, n, level, C=C)
        rp = rates(model, p, +0.5, P, K, n, level, C=C)
        out[p] = {"FLIP_REL": rm["FLIP_REL"], "NO_EFFECT_REL": rp["NO_EFFECT_REL"],
                  "CHANCE_REL": max(rm["CHANCE_REL"], rp["CHANCE_REL"])}
    return out


def power_curve(model, P, K, grid=POW_GRID, n=N_SIM_POW, level=LEVEL):
    C = boot_counts(P)
    return {p: {v: rates(model, p, TRUE_Z[v], P, K, n, level, seed=4242, C=C)[v] for v in CERTS}
            for p in grid}


def p_min_from_curve(curve: dict, v: str, power=POWER) -> float:
    pm = 1.01
    for p in sorted(curve, reverse=True):
        if curve[p][v] < power:
            break
        pm = p
    return pm


def build_design(P: int, K: int, level=LEVEL) -> dict:
    d = {"P": P, "K": K, "level": level, "fc": {}, "power": {}, "p_min": {}, "cert_ok": {}}
    for m in MODELS:
        fc = fc_curve(m, P, K, level=level)
        pw = power_curve(m, P, K, level=level)
        d["fc"][m] = {f"{p:.2f}": v for p, v in fc.items()}
        d["power"][m] = {f"{p:.2f}": v for p, v in pw.items()}
        d["p_min"][m] = {v: p_min_from_curve(pw, v) for v in CERTS}
    for v in CERTS:
        worst_fc = max(d["fc"][m][p][v] for m in MODELS for p in d["fc"][m])
        d["cert_ok"][v] = bool(worst_fc <= FC_MAX)
        d["p_min"][v] = max(d["p_min"][m][v] for m in MODELS)
    d["fc_max"] = {v: max(d["fc"][m][p][v] for m in MODELS for p in d["fc"][m]) for v in CERTS}
    return d


def load_table() -> dict:
    return json.loads(TABLE.read_text()) if TABLE.exists() else {}


def design(P: int, K: int, table: dict | None = None, compute=True) -> dict:
    t = load_table() if table is None else table
    key = f"P{P}_K{K}"
    if key not in t:
        if not compute:
            raise KeyError(key)
        t[key] = build_design(P, K)
        if table is None:
            TABLE.write_text(json.dumps(t, indent=1))
    return t[key]


# ------------------------------------------------------------------ the verdict
def label(cert: str, normal_lo: float, P: int, K: int, dz: dict | None = None,
          guard=True, reach_at: float | None = None) -> dict:
    """Frozen REL2 label from a certificate + normal lo99 + design.
    reach_at overrides the normal value used for REACH (for must-fail tests only)."""
    dz = design(P, K) if dz is None else dz
    ident = (normal_lo > 0.5) or not guard
    x = normal_lo if reach_at is None else reach_at
    reach = {v: bool(x >= dz["p_min"][v]) for v in CERTS}
    cok = {v: bool(dz["cert_ok"][v]) for v in CERTS}
    attain = {v: bool(ident and cok[v] and reach[v]) for v in CERTS}
    ne = [v for v in CERTS if not attain[v]]
    if not ident:
        lab = strict = "NOT_ELIGIBLE"
    elif cert in CERTS:
        lab = cert if cok[cert] else "NOT_ELIGIBLE"
        strict = cert if (cok[cert] and reach[cert]) else "NOT_ELIGIBLE"
    else:
        lab = strict = "INDETERMINATE" if any(attain.values()) else "NOT_ELIGIBLE"
    return {"label": lab, "strict": strict, "certificate": cert, "ident": ident, "reach": reach,
            "cert_ok": cok, "attain": attain, "NE": ne,
            "p_min": {v: dz["p_min"][v] for v in CERTS}}


def pair_means(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    M = x.shape[0]
    with np.errstate(invalid="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmean(x.reshape(M // 2, -1), 1)


def swap_verdict_rel2(normal_pt, swap_pt, dz=None, level=LEVEL, guard=True) -> dict:
    """[M, trials] world-trial scores (NaN = not scored for the arm) -> REL2 verdict."""
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = pair_means(np.where(both, n, np.nan))
    s = pair_means(np.where(both, sw, np.nan))
    g = ~np.isnan(a) & ~np.isnan(s)
    a, s = a[g], s[g]
    P = int(len(a))
    K = int(round(both.sum() / max(1, 2 * P)))
    C = boot_counts(P)
    q = (1 - LEVEL) / 2
    bs = (a @ C.T) / P
    nlo, nhi = np.quantile(bs, [q, 1 - q])
    bss = (s @ C.T) / P
    slo, shi = np.quantile(bss, [q, 1 - q])
    c = certificate(a, s, C, level)
    out = label(str(c["verdict"]), float(nlo), P, K, dz=dz, guard=guard)
    gm = a.mean() - 0.5
    out.update(P=P, K=K, normal=(float(a.mean()), float(nlo), float(nhi)),
               swap=(float(s.mean()), float(slo), float(shi)),
               DF=tuple(float(v) for v in c["DF"]), DN=tuple(float(v) for v in c["DN"]),
               z=float((s.mean() - 0.5) / gm) if gm > 0 else None)
    return out
