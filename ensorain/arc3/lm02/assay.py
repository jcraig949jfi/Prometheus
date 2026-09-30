"""LM02 bounded window-sufficiency assay (operator rulings 2026-09-30: roles/Ensorain/prompts/2026-09-30_operator_direction/
and 2026-09-30_pkgf_pop_lm02_ruling/). Preregistration: ensorain/arc3/lm02/PREREG_LM02_ASSAY.md.

Question: under what environmental regimes can bounded temporal memory preserve the downstream conclusions we care about
(competence, substrate ordering, anomaly flags), at what stale contamination?

A memory POLICY maps the history (A, y) to a kept record set with a provenance label per record:
  POST (after the policy's boundary), CERTIFIED_FRESH (strict per-cell equivalence), POPULATION_SUPPORTED (stratum-level
  stale-risk bound), UNVERIFIED (FULL / WINDOW keep records without any freshness claim), ORACLE (truly non-stale).
Every SUBSTRATE is then fitted on the kept records only, in stream order, and scored against the FINAL field.
The strict gate is pkgf_obs.obs_keep, imported unchanged. PKG-F-HIER only adds POPULATION_SUPPORTED on top of it.
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01 import families as FAM
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_cp3 import pairs
from ensorain.arc3.pkgf_cp5 import last_regime_start
from ensorain.arc3.pkgf_obs import obs_keep, DELTA, Z

HERE = os.path.dirname(__file__)
DIMS = tuple(FAM.LEVELS["L2"]["dims"]); N = int(round(FAM.LEVELS["L2"]["n_obs"] * FAM.LIFE_MULT)); K = 6; M = N // K
T0 = (2 * N) // 3                                   # switch time of the single-switch regimes

# ---- preregistered constants (PREREG_LM02_ASSAY.md s3) ----
P_MAX = 0.10                                        # governing stale-risk bound
P_MAX_SENS = (0.05, 0.20)                           # declared sensitivity values (reported, not governing)
M_MIN, COV_MIN = 30, 0.20                           # coverage: tested cells per stratum, and tested / cells-with-pre
WINDOWS = (1 / 12, 1 / 6, 1 / 3, 1 / 2)
SUBSTRATES = ("CONST", "TABLE", "MARGINAL", "S-lowrank", "S-cp", "S-tt", "S-dct", "S-additive")
CHEAP = ("CONST", "TABLE", "MARGINAL")
ANOM_MARGIN = 0.10                                  # flag: substrate beats the best cheap competitor by > .10 AC
PRES_AC, PRES_TAU, PRES_CONTAM = 0.10, 0.60, 0.10    # preservation thresholds per world (vs the REF consensus)
ANOM_BAND = 0.05                                    # consensus margins within +-.05 of ANOM_MARGIN are ambiguous
REFS = ("REF1", "REF2", "REF3", "REF_HOLD")          # REF1-3 form the consensus; REF_HOLD is the noise control
REGIMES = ("STAT", "ABRUPT", "DIFFUSE", "RAMP05", "RAMP20", "RAMP50", "MULTI", "LOCAL_BLOCK", "LOCAL_BOX", "MODE_SLAB", "HIDDEN")


# ------------------------------------------------------------------ worlds
def world(regime, seed):
    gen = "cp" if seed % 2 == 0 else "tt"
    rw, rx = FAM._rng(seed, f"lm02:{regime}:world"), FAM._rng(seed, f"lm02:{regime}:walk")
    rank = int(rw.integers(1, 4))
    A = FAM.walk(DIMS, N, rx)
    x0 = FAM._field(gen, DIMS, rank, rw)
    t = np.arange(N)
    cells = tuple(A.T)
    if regime == "MULTI":
        rhos = [float(rw.choice([1.0, 0.5, 0.1, 0.0])) for _ in range(K - 1)]
        s = np.empty(N); x = x0.copy(); last = 0
        for k in range(K):
            if k > 0 and rhos[k - 1] > 0:
                x = np.where(rw.random(DIMS) < rhos[k - 1], FAM._field(gen, DIMS, rank, rw), x); last = k * M
            sl = slice(k * M, N if k == K - 1 else (k + 1) * M); s[sl] = x[tuple(A[sl].T)]
        xf, boundary, info = x, last, dict(rhos=rhos)
    elif regime == "STAT":
        s, xf, boundary, info = x0[cells], x0, 0, {}
    else:
        x1 = FAM._field(gen, DIMS, rank, rw)
        mask = np.ones(DIMS, bool); lam = (t >= T0).astype(float); boundary = T0
        if regime == "DIFFUSE":
            mask = rw.random(DIMS) < 0.3
        elif regime.startswith("RAMP"):
            w = int(regime[4:]) / 100; lam = np.clip((t / N - (2 / 3 - w / 2)) / w, 0, 1)
            boundary = int(np.ceil((2 / 3 + w / 2) * N))
        elif regime == "LOCAL_BLOCK":
            o = rw.integers(0, 2, 3); mask = np.zeros(DIMS, bool)
            mask[tuple(slice(6 * b, 6 * b + 6) for b in o)] = True
        elif regime == "LOCAL_BOX":
            o = rw.integers(0, DIMS[0] - 7 + 1, 3); mask = np.zeros(DIMS, bool)
            mask[tuple(slice(b, b + 7) for b in o)] = True
        elif regime == "MODE_SLAB":
            mode = int(rw.integers(3)); idx = rw.choice(DIMS[mode], 3, replace=False)
            mask = np.zeros(DIMS, bool); sl = [slice(None)] * 3; sl[mode] = idx; mask[tuple(sl)] = True
        elif regime == "HIDDEN":
            visited_after = np.zeros(DIMS, bool); visited_after[tuple(A[T0:].T)] = True
            mask = ~visited_after & (rw.random(DIMS) < 0.5)
        m = mask[cells]
        s = np.where(m, (1 - lam) * x0[cells] + lam * x1[cells], x0[cells])
        xf = np.where(mask, x1, x0); info = dict(changed_frac=round(float(mask.mean()), 3))
    y = s + FAM.NOISE * rx.normal(size=N)
    # test splits against the FINAL field
    seen_last = np.zeros(DIMS, bool); seen_last[tuple(A[N - M:].T)] = True
    seen_any = np.zeros(DIMS, bool); seen_any[cells] = True
    grid = np.array(np.unravel_index(np.arange(int(np.prod(DIMS))), DIMS)).T
    rt = np.random.default_rng(seed + 99)
    pick = lambda G: G[np.sort(rt.choice(len(G), size=min(512, len(G)), replace=False))] if len(G) else G
    fl, fa = seen_last.reshape(-1), seen_any.reshape(-1)
    splits = {"RECENT": pick(grid[fl]), "STALE": pick(grid[~fl & fa]), "GEN": pick(grid[~fa])}
    stale = np.abs(s - xf[cells]) > DELTA
    return dict(regime=regime, seed=seed, gen=gen, A=A, y=y, s=s, xf=xf, stale=stale, boundary=boundary,
                splits={k: (v, xf[tuple(v.T)]) for k, v in splits.items() if len(v) >= 20}, info=info)


# ------------------------------------------------------------------ PKG-F-HIER
def octant(k):
    a = np.frombuffer(k, dtype=np.int64) if isinstance(k, bytes) else np.asarray(k)
    return tuple(int(v >= d // 2) for v, d in zip(a, DIMS))


def hier_keep(A, y, tau_eff, stratify=True, p_max=P_MAX):
    """Strict gate unchanged, plus POPULATION_SUPPORTED for UNKNOWN cells in strata whose stale-risk bound passes.
    Bound (distribution-free, Markov): among a stratum's TESTED cells (>= 1 pre and >= 1 post record), q_i = d_i^2 - se_i^2
    is unbiased for Delta_i^2. The fraction of cells with |Delta| > DELTA is <= E[Delta^2] / DELTA^2. The governing bound is
    pi_ucb = max(0, mean(q) + 1.645 sd(q) / sqrt(m)) / DELTA^2, and a stratum is SUPPORTED iff m >= M_MIN,
    m / (stratum cells with pre records) >= COV_MIN and pi_ucb <= p_max. Global pooling (stratify=False) is the weak baseline."""
    keep_strict, _, sd = obs_keep(A, y, tau_eff)
    n = len(y); keys = [r.astype(np.int64).tobytes() for r in A]
    pre, post = {}, {}
    for i, k in enumerate(keys):
        (pre if i < tau_eff else post).setdefault(k, []).append(y[i])
    state, q, strat_of = {}, {}, {}
    for k in pre:
        strat_of[k] = octant(k) if stratify else (0,)
        if k in post:
            se2 = sd ** 2 * (1 / len(pre[k]) + 1 / len(post[k])); d = np.mean(pre[k]) - np.mean(post[k])
            q[k] = d * d - se2
            state[k] = "CERTIFIED_FRESH" if abs(d) + Z * np.sqrt(se2) <= DELTA else ("CHANGED" if abs(d) > Z * np.sqrt(se2) else "UNKNOWN")
        else:
            state[k] = "UNKNOWN"
    strata = {}
    for k, st in strat_of.items():
        strata.setdefault(st, []).append(k)
    sup, sinfo = set(), {}
    for st, ks in strata.items():
        qs = np.array([q[k] for k in ks if k in q]); m = len(qs); cov = m / len(ks)
        ucb = (max(0.0, qs.mean() + 1.645 * qs.std(ddof=1) / np.sqrt(m)) / DELTA ** 2) if m >= 2 else np.inf
        ok = m >= M_MIN and cov >= COV_MIN and ucb <= p_max
        sinfo[str(st)] = dict(m=m, cells=len(ks), cov=round(cov, 3), pi_ucb=round(float(ucb), 4), supported=bool(ok))
        if ok:
            sup.add(st)
    label = np.empty(n, dtype=object)
    for i, k in enumerate(keys):
        if i >= tau_eff:
            label[i] = "POST"
        elif state[k] == "CERTIFIED_FRESH":
            label[i] = "CERTIFIED_FRESH"
        elif state[k] == "UNKNOWN" and strat_of[k] in sup:
            label[i] = "POPULATION_SUPPORTED"
        else:
            label[i] = "QUARANTINED" if state[k] == "UNKNOWN" else "CHANGED"
    assert np.array_equal(np.isin(label, ["POST", "CERTIFIED_FRESH"]), keep_strict)   # strict gate untouched
    return label, sinfo


# ------------------------------------------------------------------ substrates (fitted on kept records only)
def fit_predict(name, A, y, Q):
    if len(y) == 0:
        return np.zeros(len(Q))
    mu = float(np.mean(y))
    if name == "CONST":
        return np.full(len(Q), mu)
    if name == "TABLE":
        tab = {}
        for a, v in zip(map(tuple, A), y):
            tab.setdefault(a, []).append(v)
        return np.array([np.mean(tab[tuple(q)]) if tuple(q) in tab else mu for q in Q])
    if name == "MARGINAL":
        f = [np.zeros(d) for d in DIMS]; r = y - mu
        for _ in range(10):
            for j in range(3):
                part = r + f[j][A[:, j]]
                s_ = np.bincount(A[:, j], part, DIMS[j]); c = np.bincount(A[:, j], None, DIMS[j])
                f[j] = np.where(c > 0, s_ / np.maximum(c, 1), 0.0)
                r = part - f[j][A[:, j]]
        return mu + sum(f[j][Q[:, j]] for j in range(3))
    arm = Selective(name[2:], list(DIMS), cap=max(160, int(np.prod(DIMS)) // 4))
    for i in range(0, len(y), 50):
        arm.observe(A[i:i + 50], y[i:i + 50])
    return arm.predict(Q)


# ------------------------------------------------------------------ policies and scoring
def policies(w, tau_det):
    A, y, n = w["A"], w["y"], N
    tau_eff = tau_det if tau_det > 0 else (5 * n) // 6
    P = {"FULL": np.full(n, "UNVERIFIED", dtype=object)}
    P["ORACLE"] = np.where(w["stale"], "EXCLUDED", "ORACLE").astype(object)
    for f in WINDOWS:
        P[f"WINDOW_{round(1 / f)}"] = np.where(np.arange(n) >= n - int(n * f), "UNVERIFIED", "EXCLUDED").astype(object)
    b_orc = w["boundary"]
    for tag, tau in (("det", tau_eff), ("orc", b_orc)):
        if tau <= 0:                                  # oracle says no change: every record is post-boundary
            P[f"STRICT_{tag}"] = np.full(n, "POST", dtype=object); P[f"HIER_{tag}"] = P[f"STRICT_{tag}"]; continue
        lab, _ = hier_keep(A, y, tau, stratify=True)
        P[f"HIER_{tag}"] = lab
        P[f"STRICT_{tag}"] = np.where(np.isin(lab, ["POST", "CERTIFIED_FRESH"]), lab, "EXCLUDED").astype(object)
    P["POPG_det"] = hier_keep(A, y, tau_eff, stratify=False)[0]
    for pm in P_MAX_SENS:
        P[f"HIER_det_p{int(pm * 100):02d}"] = hier_keep(A, y, tau_eff, stratify=True, p_max=pm)[0]
    return P, tau_eff


KEPT = ("POST", "CERTIFIED_FRESH", "POPULATION_SUPPORTED", "UNVERIFIED", "ORACLE")


def kendall(a, b):
    n = len(a); c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = np.sign(a[i] - a[j]) * np.sign(b[i] - b[j]); c += s > 0; d += s < 0
    return (c - d) / max(1, c + d)


def run_world(regime, seed):
    import warnings; warnings.simplefilter("ignore")
    t0 = time.time(); w = world(regime, seed)
    tau_det = last_regime_start(w["A"], w["y"], seed, alpha=0.01)
    P, tau_eff = policies(w, tau_det)
    _, sinfo = hier_keep(w["A"], w["y"], tau_eff, stratify=True)
    valid = ~w["stale"]; out = dict(regime=regime, seed=seed, gen=w["gen"], info=w["info"], boundary_frac=round(w["boundary"] / N, 3),
                                    tau_det_frac=round(tau_det / N, 3), strata_det=sinfo, stale_frac=round(float(w["stale"].mean()), 4), pol={})
    # REF*: the same walk re-observed from the FINAL field (independent noise draws). The conclusions a bounded memory must
    # preserve are the ones drawn from the world as it now is: the consensus of REF1-3. REF_HOLD is the noise control.
    for rname in REFS:
        rr = FAM._rng(seed, f"lm02:{regime}:{rname}")
        yref = w["xf"][tuple(w["A"].T)] + FAM.NOISE * rr.normal(size=N)
        out["pol"][rname] = dict(kept=N, contam=0.0, retained=1.0, unnec_quar=0.0, labels={},
                                 AC={sub: {sp: AC(fit_predict(sub, w["A"], yref, T), truth, 1.0) for sp, (T, truth) in w["splits"].items()} for sub in SUBSTRATES})
    for name, lab in P.items():
        keep = np.isin(lab, KEPT); kk = np.flatnonzero(keep)
        r = dict(kept=int(keep.sum()), contam=round(float(w["stale"][keep].mean()) if keep.any() else 0.0, 4),
                 retained=round(float((keep & valid).sum() / valid.sum()), 4),
                 unnec_quar=round(float((~keep & valid).sum() / valid.sum()), 4), labels={}, AC={})
        for L in ("CERTIFIED_FRESH", "POPULATION_SUPPORTED", "POST"):
            m = lab == L
            r["labels"][L] = dict(n=int(m.sum()), stale=int((m & w["stale"]).sum()))
        for sub in SUBSTRATES:
            r["AC"][sub] = {sp: AC(fit_predict(sub, w["A"][kk], w["y"][kk], T), truth, 1.0) for sp, (T, truth) in w["splits"].items()}
        out["pol"][name] = r
    out["wall_s"] = round(time.time() - t0, 1)
    return out


def plan():
    return [(rg, 9_815_000 + 100 * j + i) for j, rg in enumerate(REGIMES) for i in range(8)]


def _job(args):
    return run_world(*args)


if __name__ == "__main__":
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    from multiprocessing import Pool
    t0 = time.time(); rows = []
    with Pool(int(os.environ.get("ENSORAIN_WORKERS", "8"))) as pool:
        for r in pool.imap_unordered(_job, plan()):
            rows.append(r); print(r["regime"], r["seed"], "tau_det", r["tau_det_frac"], "bnd", r["boundary_frac"], r["wall_s"], "s", "%.0fs" % (time.time() - t0), flush=True)
    rows.sort(key=lambda r: (REGIMES.index(r["regime"]), r["seed"]))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "lm02_assay.json"), "w"), indent=1)
