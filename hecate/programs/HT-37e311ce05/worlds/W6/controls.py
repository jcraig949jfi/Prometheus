"""HT-37e311ce05 / W6 controls (Pass 3 v2). No treatment code.

Arms written to control_rows.jsonl (one JSON row per (arm, seed), flushed):
  POSITIVE_CONTROL constructed population: each pair's host and symbiont hold
                  rows from disjoint coherence classes (complementary), pairs
                  drawn independently (partner-specific by construction).
  NULL_TWIN       horizontal transmission: pair-level truncation selection on
                  OMP joint recovery, symbionts re-paired at random each
                  generation (evolution stream 1).
  NULL_TWIN_B     independent replicate of NULL_TWIN (evolution stream 2),
                  used as the reference in the twin's own S2 ratio.
  CHEAT           rows whose R_own / R_other are injected (0.0 / 0.30) while
                  the stored genomes are the NULL_TWIN's genomes.
The treatment (vertical transmission) is NOT implemented here.
"""
import json, os, time, hashlib

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "spec.json"), encoding="utf-8"))
P_ = SPEC["parameters"]
N, K, NC = P_["n"], P_["k"], P_["classes"]
NPAL = 2 * NC
RPP, PAIRS, GENS = P_["rows_per_partner"], P_["pairs"], P_["generations"]
T, TE, PMUT = P_["test_signals"], P_["eval_signals"], P_["mut_prob"]
CUT = P_["coherence_cut"]
SEEDS = list(range(P_["control_seeds"]))
OUT = os.path.join(HERE, "control_rows.jsonl")


def palette(seed):
    rng = np.random.default_rng([seed, 11])
    B = rng.normal(size=(NC, N))
    B /= np.linalg.norm(B, axis=1, keepdims=True)
    U = rng.normal(size=(NC, N))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    Cp = B + P_["copy_noise"] * U
    Cp /= np.linalg.norm(Cp, axis=1, keepdims=True)
    Pal = np.vstack([B, Cp])                     # row i and i+NC share a class
    coh = np.abs(Pal @ Pal.T) >= CUT             # coherence relation on palette
    return Pal, coh


def signals(rng, count):
    X = np.zeros((count, N))
    sup = np.argsort(rng.random((count, N)), axis=1)[:, :K]
    np.put_along_axis(X, sup, rng.normal(size=(count, K)), axis=1)
    return X, np.sort(sup, axis=1)


def omp_success(M, X, sup):
    """M: (B, m, n) stacked matrices; X: (B, n) signals; exact support recovery."""
    Bn, m, n = M.shape
    Y = np.einsum("bmn,bn->bm", M, X)
    Mn = M / np.linalg.norm(M, axis=1, keepdims=True).clip(1e-12)
    r = Y.copy()
    S = np.zeros((Bn, K), int)
    idx = np.arange(Bn)
    for t in range(K):
        c = np.abs(np.einsum("bmn,bm->bn", Mn, r))
        for j in range(t):
            c[idx, S[:, j]] = -1.0
        S[:, t] = c.argmax(1)
        As = M[idx[:, None], :, S[:, : t + 1]].transpose(0, 2, 1)
        G = np.einsum("bmi,bmj->bij", As, As) + 1e-9 * np.eye(t + 1)
        h = np.einsum("bmi,bm->bi", As, Y)
        coef = np.linalg.solve(G, h[..., None])[..., 0]
        r = Y - np.einsum("bmi,bi->bm", As, coef)
    return (np.sort(S, axis=1) == sup).all(1)


def pair_success(Pal, H, S, X, sup):
    """mean exact-recovery rate per pair over the given signals."""
    P = H.shape[0]
    M = Pal[np.concatenate([H, S], axis=1)]              # (P, 2*RPP, N)
    Mb = np.repeat(M, X.shape[0], axis=0)
    Xb = np.tile(X, (P, 1))
    sb = np.tile(sup, (P, 1))
    return omp_success(Mb, Xb, sb).reshape(P, X.shape[0]).mean(1)


def redundancy(coh, H, S):
    """R_own, R_other for a paired population (H[i] with S[i])."""
    P = H.shape[0]
    # red[i, j] = fraction of S[i]'s rows coherent with some row of H[j]
    red = np.zeros((P, P))
    for j in range(P):
        cj = coh[:, H[j]].any(1)                         # palette rows coherent with host j
        red[:, j] = cj[S].mean(1)
    own = float(np.mean(np.diag(red)))
    off = red[~np.eye(P, dtype=bool)]
    return own, float(off.mean())


def mutate(G, rng):
    G = G.copy()
    for i in np.nonzero(rng.random(G.shape[0]) < PMUT)[0]:
        pos = rng.integers(RPP)
        choices = np.setdiff1d(np.arange(NPAL), G[i])
        G[i, pos] = rng.choice(choices)
    return G


def random_genomes(rng, P):
    return np.array([rng.choice(NPAL, RPP, replace=False) for _ in range(P)])


def evolve_horizontal(seed, stream):
    Pal, coh = palette(seed)
    rng = np.random.default_rng([seed, stream, 5])
    sig_rng = np.random.default_rng([seed, 9])            # common signals, shared across arms
    H, S = random_genomes(rng, PAIRS), random_genomes(rng, PAIRS)
    half = PAIRS // 2
    for _ in range(GENS):
        X, sup = signals(sig_rng, T)
        f = pair_success(Pal, H, S, X, sup) + 1e-6 * rng.random(PAIRS)   # random tie-break
        top = np.argsort(-f)[:half]
        par = np.repeat(top, 2)
        H, S = H[par], S[par]
        S = S[rng.permutation(PAIRS)]                     # horizontal: re-pair at random
        H, S = mutate(H, rng), mutate(S, rng)
    return H, S


def positive_population(seed):
    rng = np.random.default_rng([seed, 3])
    H, S = [], []
    for _ in range(PAIRS):
        cls = rng.permutation(NC)
        hc, sc = cls[:RPP], cls[RPP: 2 * RPP]
        H.append(hc + NC * rng.integers(0, 2, RPP))       # base row or its near-copy
        S.append(sc + NC * rng.integers(0, 2, RPP))
    return np.array(H), np.array(S)


def measure(seed, H, S):
    Pal, coh = palette(seed)
    own, other = redundancy(coh, H, S)
    Xe, se = signals(np.random.default_rng([seed, 21]), TE)
    succ = float(pair_success(Pal, H, S, Xe, se).mean())
    return {"R_own": own, "R_other": other, "D": other - own, "joint_success": succ}


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(row):
        f.write(json.dumps(row) + "\n")
        f.flush()

    res = {a: {} for a in ("POSITIVE_CONTROL", "NULL_TWIN", "NULL_TWIN_B", "CHEAT")}
    for seed in SEEDS:
        H, S = positive_population(seed)
        m = measure(seed, H, S)
        res["POSITIVE_CONTROL"][seed] = m
        emit({"arm": "POSITIVE_CONTROL", "seed": seed, **m, "H": H.tolist(), "S": S.tolist()})
    twin_genomes = {}
    for arm, stream in (("NULL_TWIN", 1), ("NULL_TWIN_B", 2)):
        for seed in SEEDS:
            H, S = evolve_horizontal(seed, stream)
            m = measure(seed, H, S)
            res[arm][seed] = m
            if arm == "NULL_TWIN":
                twin_genomes[seed] = (H, S)
            emit({"arm": arm, "seed": seed, **m, "H": H.tolist(), "S": S.tolist(),
                  "cpu_s": time.process_time() - t0})
    for seed in SEEDS:
        H, S = twin_genomes[seed]
        m = {"R_own": 0.0, "R_other": 0.30, "D": 0.30, "joint_success": 1.0}   # injected
        res["CHEAT"][seed] = m
        emit({"arm": "CHEAT", "seed": seed, **m, "H": H.tolist(), "S": S.tolist()})
    f.close()

    # audit: recompute redundancy observables from the stored genomes
    flagged, total = {a: 0 for a in res}, {a: 0 for a in res}
    for line in open(OUT, encoding="utf-8"):
        r = json.loads(line)
        m = measure(r["seed"], np.array(r["H"]), np.array(r["S"]))
        total[r["arm"]] += 1
        if any(abs(m[k] - r[k]) > 1e-9 for k in ("R_own", "R_other", "D")):
            flagged[r["arm"]] += 1

    def mean(arm, key):
        return float(np.mean([res[arm][s][key] for s in SEEDS]))

    twin_own, twinB_own = mean("NULL_TWIN", "R_own"), mean("NULL_TWIN_B", "R_own")
    ref_ok = twin_own >= P_["min_twin_redundancy"]
    stats = {}
    for arm, ref in (("POSITIVE_CONTROL", twin_own), ("NULL_TWIN", twinB_own),
                     ("NULL_TWIN_B", twin_own), ("CHEAT", twin_own)):
        stats[arm] = {"S1_specificity": mean(arm, "D"),
                      "S2_redundancy_ratio": mean(arm, "R_own") / ref if ref > 0 else float("inf"),
                      "R_own": mean(arm, "R_own"), "R_other": mean(arm, "R_other"),
                      "joint_success": mean(arm, "joint_success"),
                      "S2_reference": ("NULL_TWIN_B" if arm == "NULL_TWIN" else "NULL_TWIN"),
                      "per_seed_D": [res[arm][s]["D"] for s in SEEDS],
                      "per_seed_R_own": [res[arm][s]["R_own"] for s in SEEDS]}
    summary = {"stats": stats, "twin_reference_ok": ref_ok,
               "audit_flagged": flagged, "audit_total": total,
               "cpu_seconds": time.process_time() - t0,
               "rows_sha256": hashlib.sha256(open(OUT, "rb").read()).hexdigest()}
    json.dump(summary, open(os.path.join(HERE, "control_summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
