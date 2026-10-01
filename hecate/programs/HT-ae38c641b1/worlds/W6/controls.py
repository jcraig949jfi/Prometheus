"""HT-ae38c641b1 / W6 controls (Pass 3 v2). NO TREATMENT CODE.

Measurement pipeline (shared by every arm; see spec.json "observable"):
  per seed: N base points x uniform in the inner square [-0.75, 0.75]^2 of the
  misspecification square [-1, 1]^2; for each eps in 2^-2..2^-9 a partner
  x + eps*(cos a, sin a), a uniform; f(eps) = fraction of pairs whose labels
  differ; alpha = OLS slope of ln f on ln eps (uncertainty exponent,
  alpha = 2 - D_boundary). R^2 and coarse/fine half slopes are also kept.

Arms here:
  POSITIVE_CONTROL  label = root reached by Newton's method for z^3 - 1 from
                    z_0 = g1 + i g2 (fractal Julia-set basin boundary by construction).
  NULL_TWIN         label = sign of the GLOBAL maximiser of the Cauchy location
                    log-likelihood of the misspecified data (no iteration; smooth
                    boundary expected). Seeds 0-4; replicate seeds 5-9 give the
                    twin's value on the relative clause.
  CHEAT             NULL_TWIN labels, but f(eps) overwritten with
                    f_twin(2^-2) * (eps / 2^-2)^0.5 (success injected into the observable).
The Newton-iterated Cauchy estimator (the treatment) is NOT implemented here.
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

D0 = np.array([-1.9, -1.4, -1.0, 0.8, 1.2, 1.9])  # base unit-level differences
GRP = np.array([0, 0, 1, 1, 0, 1])              # subgroup: 0 shifted by g1, 1 by g2
SC = 0.5                                    # Cauchy scale
EPS = 2.0 ** -np.arange(2, 10)              # 2^-2 .. 2^-9
NBASE = 30000
INNER = 0.75
SEEDS_MAIN = [0, 1, 2, 3, 4]
SEEDS_REP = [5, 6, 7, 8, 9]
TH_S1 = 0.80
TH_S2 = 0.15


def data(g):
    """g: (N,2) -> misspecified data (N,4)."""
    return D0[None, :] + np.where(GRP[None, :] == 0, g[:, :1], g[:, 1:2])


def twin_label(g, chunk=20000):
    out = np.empty(len(g), np.int8)
    for a in range(0, len(g), chunk):
        d = data(g[a:a + chunk])                                  # (n,4)
        lo, hi = d.min(1) - 0.5, d.max(1) + 0.5
        M = 200
        t = lo[:, None] + (hi - lo)[:, None] * np.linspace(0, 1, M)[None, :]
        r = d[:, None, :] - t[:, :, None]                          # (n,M,4)
        ll = -np.log(SC * SC + r * r).sum(-1)                      # (n,M)
        # candidate local maxima: best grid point in each of 4 windows around data
        cand = []
        for k in range(len(D0)):
            m = np.abs(t - d[:, k:k + 1]) <= 0.6
            cand.append(t[np.arange(len(t)), np.argmax(np.where(m, ll, -np.inf), 1)])
        cand.append(t[np.arange(len(t)), np.argmax(ll, 1)])
        c = np.stack(cand, 1)
        for _ in range(30):                                         # damped Newton polish on l
            rr = d[:, None, :] - c[:, :, None]
            q = SC * SC + rr * rr
            g1 = (2 * rr / q).sum(-1)
            h = (2 * (SC * SC - rr * rr) / (q * q)).sum(-1)           # = -l''
            step = np.where(h > 0, g1 / np.maximum(h, 1e-12), 0.0)
            c = c + np.clip(step, -0.05, 0.05)
        rr = d[:, None, :] - c[:, :, None]
        lc = -np.log(SC * SC + rr * rr).sum(-1)
        best = c[np.arange(len(c)), np.argmax(lc, 1)]
        out[a:a + chunk] = np.sign(best).astype(np.int8)
    return out


ROOTS = np.exp(2j * np.pi * np.arange(3) / 3)


def pc_label(g):
    z = g[:, 0] + 1j * g[:, 1]
    with np.errstate(all="ignore"):
        for _ in range(60):
            z = z - (z ** 3 - 1) / (3 * z * z)
        dist = np.abs(z[:, None] - ROOTS[None, :])
        lab = np.argmin(dist, 1).astype(np.int8)
        lab[~(dist.min(1) < 1e-6)] = 3
    return lab


def pairs(seed):
    rng = np.random.default_rng([seed, 101])
    x = rng.uniform(-INNER, INNER, (NBASE, 2))
    a = rng.uniform(0, 2 * np.pi, (len(EPS), NBASE))
    xp = x[None] + EPS[:, None, None] * np.stack([np.cos(a), np.sin(a)], -1)
    return x, xp


def fit(eps, f):
    if np.any(f <= 0):
        return dict(alpha=None, r2=None, alpha_coarse=None, alpha_fine=None)
    X, Y = np.log(eps), np.log(f)
    p = np.polyfit(X, Y, 1)
    res = Y - np.polyval(p, X)
    r2 = 1 - (res ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
    h = len(eps) // 2
    pc = np.polyfit(X[:h], Y[:h], 1)[0]; pf = np.polyfit(X[h:], Y[h:], 1)[0]
    return dict(alpha=float(p[0]), r2=float(r2), alpha_coarse=float(pc), alpha_fine=float(pf))


def measure(labfun, seed):
    x, xp = pairs(seed)
    l0 = labfun(x)
    lp = labfun(xp.reshape(-1, 2)).reshape(len(EPS), NBASE)
    f = (lp != l0[None]).mean(1)
    vals, cnt = np.unique(l0, return_counts=True)
    return f, l0, dict(zip([int(v) for v in vals], [int(c) for c in cnt])), (lp != l0[None]).sum(1)


def emit(fh, d):
    fh.write(json.dumps(d) + "\n"); fh.flush(); os.fsync(fh.fileno())


def main():
    t0 = time.process_time()
    with open(ROWS, "w") as fh:
        for seed in SEEDS_MAIN:
            f, _, bal, n = measure(pc_label, seed)
            emit(fh, dict(arm="POSITIVE_CONTROL", seed=seed, f=f.tolist(), disagree_counts=n.tolist(),
                          label_counts=bal, **fit(EPS, f)))
            print("pc", seed, round(time.process_time() - t0, 1), file=sys.stderr)
        for seed in SEEDS_MAIN + SEEDS_REP:
            f, _, bal, n = measure(twin_label, seed)
            arm = "NULL_TWIN" if seed in SEEDS_MAIN else "NULL_TWIN_REPLICATE"
            emit(fh, dict(arm=arm, seed=seed, f=f.tolist(), disagree_counts=n.tolist(),
                          label_counts=bal, **fit(EPS, f)))
            if seed in SEEDS_MAIN:
                fc = f[0] * (EPS / EPS[0]) ** 0.5
                emit(fh, dict(arm="CHEAT", seed=seed, f=fc.tolist(), **fit(EPS, fc)))
            print("twin", seed, round(time.process_time() - t0, 1), file=sys.stderr)
    return time.process_time() - t0


def evaluate(cpu, revisions):
    rows = [json.loads(l) for l in open(ROWS)]
    med = lambda arm, k="alpha": float(np.median([r[k] for r in rows if r["arm"] == arm]))
    a_pc, a_tw, a_rep, a_ch = med("POSITIVE_CONTROL"), med("NULL_TWIN"), med("NULL_TWIN_REPLICATE"), med("CHEAT")
    clauses = [
        dict(id="S1", positive_value=a_pc, twin_value=a_tw, attainable=a_pc <= TH_S1,
             discriminating=a_tw > TH_S1, treatment_must_reach=TH_S1,
             treatment_statistic="median over seeds 0-4 of alpha, TREATMENT (must be <=)"),
        dict(id="S2", positive_value=a_tw - a_pc, twin_value=a_tw - a_rep,
             attainable=(a_tw - a_pc) >= TH_S2, discriminating=(a_tw - a_rep) < TH_S2,
             treatment_must_reach="alpha_treatment <= alpha_twin(probe rerun) - %.2f; with this run's twin: <= %.3f" % (TH_S2, a_tw - TH_S2),
             treatment_statistic="median alpha NULL_TWIN minus median alpha TREATMENT, seeds 0-4 (must be >=)"),
    ]
    cheat_detected = (a_ch <= TH_S1) and (a_tw - a_ch >= TH_S2)
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected
    diag = {arm: dict(alpha=med(arm), r2=med(arm, "r2"), alpha_coarse=med(arm, "alpha_coarse"),
                      alpha_fine=med(arm, "alpha_fine"))
            for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "NULL_TWIN_REPLICATE", "CHEAT")}
    return dict(clauses=clauses, cheat_detected=cheat_detected, cheat_values=dict(S1=a_ch, S2=a_tw - a_ch),
                frozen=frozen, diagnostics=diag, cpu_core_seconds_last_run=cpu, revisions=revisions)


if __name__ == "__main__":
    cpu = main()
    rp = os.path.join(HERE, "revisions.json")
    revs = json.load(open(rp)) if os.path.exists(rp) else []
    res = evaluate(cpu, revs)
    json.dump(res, open(os.path.join(HERE, "ATTAINABILITY.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
