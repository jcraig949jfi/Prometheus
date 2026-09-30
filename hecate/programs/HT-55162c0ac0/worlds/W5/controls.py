"""W5 controls (HT-55162c0ac0, P3v2). POSITIVE_CONTROL, CHEAT, NULL_TWIN only.

No treatment code. The treatment (pure gLV recall vs chaos label) is NOT
computed here. Rows -> control_rows.jsonl, flushed per row.

World: 4-species competitive Lotka-Volterra family around the Vano et al.
(2006) chaotic matrix, off-diagonal nonzero entries perturbed
multiplicatively by U(1-ETA, 1+ETA).

POSITIVE_CONTROL (effect present by construction): phase A (0..T_A) pure
gLV, lambda_max measured over [T_BURN, T_A] by a renormalised twin
trajectory; phase B (T_A..T_A+T_B) adds an ABSORBING removal: any species
whose abundance drops below THETA_PC is set to 0 permanently. Large chaotic
excursions therefore cause item loss by construction.
CHEAT: PC rows with recall overwritten (chaotic -> 0.0, non-chaotic -> 1.0).
NULL_TWIN: PC rows with chaos labels permuted within seed (nuisance exactly
matched: same draws, same recall values, same label count; association
destroyed).
Also ESTIMATOR_CHECK rows: unperturbed Vano matrix and its symmetrised
version, pure gLV, lambda only.
"""
import json, os, sys, time
import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "control_rows.jsonl")

R = np.array([1.0, 0.72, 1.53, 1.27])
A0 = np.array([[1.0, 1.09, 1.52, 0.0],
               [0.0, 1.0, 0.44, 1.36],
               [2.33, 0.0, 1.0, 0.47],
               [1.21, 0.51, 0.35, 1.0]])
ETA = 0.10
DRAWS_PER_SEED = 100
SEEDS = [0, 1, 2, 3, 4]
DT = 0.05
T_BURN = 300.0
T_A = 1500.0
T_B = 1500.0
RENORM_EVERY = 1.0
DELTA0 = 1e-8
LAMBDA_CHAOS = 0.005
THETA_PC = 0.02
RECALL_FLOOR = 1e-3
RECALL_WINDOW = 200.0
# success clauses (must match spec.json): (id, statistic key, comparison, threshold)
CLAUSES = [("S1", "S1", ">=", 0.08), ("S2", "S2", "<", 0.01), ("S3", "S3", ">=", 0.06)]
MIN_PER_CLASS = 20


def clause_pass(ev):
    res = {}
    elig = ev["n_chaotic"] >= MIN_PER_CLASS and ev["n_nonchaotic"] >= MIN_PER_CLASS
    for cid, key, cmp, thr in CLAUSES:
        v = ev.get(key)
        ok = v is not None and elig and ((v >= thr) if cmp == ">=" else (v < thr))
        res[cid] = bool(ok)
    res["all"] = all(res[c[0]] for c in CLAUSES)
    return res


def draw_family(seed, n):
    rng = np.random.default_rng(seed)
    A = np.repeat(A0[None], n, axis=0).copy()
    mask = (A0 != 0) & ~np.eye(4, dtype=bool)
    mult = rng.uniform(1 - ETA, 1 + ETA, size=(n, 4, 4))
    A[:, mask] = A[:, mask] * mult[:, mask]
    x0 = rng.uniform(0.2, 0.4, size=(n, 4))
    return A, x0


def rhs(x, A):
    return R * x * (1.0 - np.einsum("bij,bj->bi", A, x))


def rk4(x, A):
    k1 = rhs(x, A)
    k2 = rhs(x + 0.5 * DT * k1, A)
    k3 = rhs(x + 0.5 * DT * k2, A)
    k4 = rhs(x + DT * k3, A)
    return x + DT / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def phase_a(A, x0):
    """pure gLV; returns state at T_A and lambda_max over [T_BURN, T_A]."""
    n = A.shape[0]
    AA = np.concatenate([A, A], axis=0)
    rng = np.random.default_rng(12345)
    d = rng.normal(size=x0.shape)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    X = np.concatenate([x0, x0 + DELTA0 * d], axis=0)
    steps = int(round(T_A / DT))
    every = int(round(RENORM_EVERY / DT))
    burn = int(round(T_BURN / DT))
    logsum = np.zeros(n)
    t_meas = 0.0
    for s in range(1, steps + 1):
        X = rk4(X, AA)
        if s % every == 0:
            diff = X[n:] - X[:n]
            nd = np.linalg.norm(diff, axis=1)
            nd = np.where(nd > 0, nd, DELTA0)
            if s > burn:
                logsum += np.log(nd / DELTA0)
                t_meas += RENORM_EVERY
            X[n:] = X[:n] + diff * (DELTA0 / nd)[:, None]
    return X[:n], logsum / t_meas


def phase_b_absorbing(A, x):
    steps = int(round(T_B / DT))
    win = int(round(RECALL_WINDOW / DT))
    acc = np.zeros_like(x)
    alive = np.ones_like(x, dtype=bool)
    for s in range(1, steps + 1):
        x = rk4(x, A)
        alive &= x >= THETA_PC
        x = np.where(alive, x, 0.0)
        if s > steps - win:
            acc += x
    mean_x = acc / win
    return mean_x, alive


def evaluate(rows):
    lab = np.array([r["chaotic"] for r in rows], dtype=bool)
    rec = np.array([r["recall"] for r in rows], dtype=float)
    stg = np.array([r["strength"] for r in rows], dtype=float)
    nc, nn = int(lab.sum()), int((~lab).sum())
    out = {"n_chaotic": nc, "n_nonchaotic": nn}
    if nc < 2 or nn < 2:
        out.update(S1=None, S2=None, S3=None)
        return out
    out["S1"] = float(rec[~lab].mean() - rec[lab].mean())
    out["S2"] = float(mannwhitneyu(rec[~lab], rec[lab], alternative="greater").pvalue)
    X = np.column_stack([np.ones_like(rec), stg, lab.astype(float)])
    beta, *_ = np.linalg.lstsq(X, rec, rcond=None)
    out["S3"] = float(-beta[2])
    return out


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(row):
        f.write(json.dumps(row) + "\n")
        f.flush()

    # estimator check
    Asym = 0.5 * (A0 + A0.T)
    Ae = np.stack([A0, Asym])
    xe = np.full((2, 4), 0.3)
    _, lam_e = phase_a(Ae, xe)
    for name, lam in zip(["vano_original", "vano_symmetrised"], lam_e):
        emit({"arm": "ESTIMATOR_CHECK", "system": name, "lambda": float(lam)})

    # positive control: all seeds in one batch
    As, xs, meta = [], [], []
    for sd in SEEDS:
        A, x0 = draw_family(sd, DRAWS_PER_SEED)
        As.append(A); xs.append(x0)
        meta += [(sd, i) for i in range(DRAWS_PER_SEED)]
    A = np.concatenate(As); x0 = np.concatenate(xs)
    xA, lam = phase_a(A, x0)
    mean_x, alive = phase_b_absorbing(A, xA)
    off = ~np.eye(4, dtype=bool)
    pc_rows = []
    for k, (sd, i) in enumerate(meta):
        row = {"arm": "POSITIVE_CONTROL", "seed": sd, "draw": i,
               "lambda": float(lam[k]), "chaotic": bool(lam[k] > LAMBDA_CHAOS),
               "strength": float(A[k][off].mean()),
               "recall": float((mean_x[k] > RECALL_FLOOR).mean()),
               "mean_x_final": [float(v) for v in mean_x[k]]}
        pc_rows.append(row); emit(row)

    # cheat: success injected into the observable
    cheat_rows = []
    for r in pc_rows:
        c = dict(r); c["arm"] = "CHEAT"; c["recall"] = 0.0 if r["chaotic"] else 1.0
        cheat_rows.append(c); emit(c)

    # null twin: chaos labels permuted within seed
    twin_rows = []
    for sd in SEEDS:
        sub = [r for r in pc_rows if r["seed"] == sd]
        perm = np.random.default_rng(1000 + sd).permutation([r["chaotic"] for r in sub])
        for r, l in zip(sub, perm):
            t = dict(r); t["arm"] = "NULL_TWIN"; t["chaotic"] = bool(l)
            twin_rows.append(t); emit(t)

    summary = {"arm": "SUMMARY",
               "POSITIVE_CONTROL": evaluate(pc_rows),
               "CHEAT": evaluate(cheat_rows),
               "NULL_TWIN": evaluate(twin_rows),
               "clauses": {arm: clause_pass(evaluate(rows)) for arm, rows in
                           [("POSITIVE_CONTROL", pc_rows), ("CHEAT", cheat_rows), ("NULL_TWIN", twin_rows)]},
               "per_seed_PC_S1": {sd: evaluate([r for r in pc_rows if r["seed"] == sd]).get("S1") for sd in SEEDS},
               "per_seed_TWIN_S1": {sd: evaluate([r for r in twin_rows if r["seed"] == sd]).get("S1") for sd in SEEDS},
               "estimator_check": {"vano_original": float(lam_e[0]), "vano_symmetrised": float(lam_e[1])},
               "params": {"ETA": ETA, "THETA_PC": THETA_PC, "DT": DT, "T_A": T_A, "T_B": T_B,
                          "LAMBDA_CHAOS": LAMBDA_CHAOS, "draws_per_seed": DRAWS_PER_SEED, "seeds": SEEDS},
               "cpu_seconds": time.process_time() - t0}
    emit(summary)
    f.close()
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
