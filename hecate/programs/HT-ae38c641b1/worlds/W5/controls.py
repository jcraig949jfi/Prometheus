"""HT-ae38c641b1 / W5 controls (Pass 3 v2), revision 1. NO TREATMENT CODE.

World (identical for every arm; see spec.json):
  genome   = two linear maps A_1, A_2 in R^{2x2} (a switched linear system);
  runs     = R fixed runs per seed: x_0 on the circle of radius 0.5 (evenly
             spaced angles, random offset per seed), S steps, map index from
             a fixed random bit per step;
  safety   = every state of every run in the closed unit disc (isotropic);
  task     = persistence lam_hat = mean_r (ln|x_S| - ln 0.5)/S (clipped at
             -5) minus a rotation-invariant shape penalty
             2*sum_j max(0, s2_j/s1_j - 0.5) (forces anisotropic maps);
  GA       = (mu+lambda) truncation, P parents, one offspring each per
             generation by isotropic Gaussian mutation of all 8 entries.
  observable A4(dom) = sum w cos(4(phi - dom)) / sum w over the 2P maps of
             the final population, phi = angle of the top right-singular
             vector, w = (s1-s2)/(s1+s2).

Arms here:
  POSITIVE_CONTROL      concrete gate + fitness bonus LAM*align(dom=0).
  POSITIVE_CONTROL_ROT  concrete gate + fitness bonus LAM*align(dom=22.5 deg).
  NULL_TWIN             concrete gate + genome-independent random rejection,
                        acceptance fraction matched per generation to the arm
                        it is compared with (here POSITIVE_CONTROL, same seed).
  CHEAT                 NULL_TWIN final maps conjugated so every principal
                        direction lies on the domain axis (injected success).
The box-verifier treatment arms V / V_rot are NOT implemented here.
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

P = 60
G = 120
R = 16
S = 60
R0 = 0.5
SIGMA = 0.03
INIT_A = 0.3
LAM = 0.1
SEEDS = list(range(20))
ROT = math.radians(22.5)
TH = 0.40


def rot(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]])


def svd_dir(A):
    u, s, vt = np.linalg.svd(A)
    v = vt[..., 0, :]
    phi = np.arctan2(v[..., 1], v[..., 0])
    w = (s[..., 0] - s[..., 1]) / np.maximum(s[..., 0] + s[..., 1], 1e-12)
    return phi, w, s


def a_k(A, dom, k=4):
    phi, w, _ = svd_dir(A)
    return float((w * np.cos(k * (phi - dom))).sum() / max(w.sum(), 1e-12))


def align_individual(A, dom):
    phi, w, _ = svd_dir(A)
    return (w * np.cos(4.0 * (phi - dom))).mean(axis=1)


def shape_pen(A):
    _, _, s = svd_dir(A)
    return 2.0 * np.maximum(0.0, s[..., 1] / np.maximum(s[..., 0], 1e-12) - 0.5).sum(axis=1)


def abs_ratio(A):
    """diagnostic: rho(|A|)/rho(A) per map (1 = no wrapping loss)."""
    ra = np.abs(np.linalg.eigvals(np.abs(A))).max(-1)
    r = np.abs(np.linalg.eigvals(A)).max(-1)
    return ra / np.maximum(r, 1e-12)


def concrete(A, x0, bits):
    N = A.shape[0]
    x = np.broadcast_to(x0, (N, R, 2)).copy()
    safe = np.ones(N, bool)
    for s in range(S):
        Aj = A[:, bits[:, s]]
        x = np.einsum("nrij,nrj->nri", Aj, x)
        r2 = (x * x).sum(-1)
        safe &= np.all(r2 <= 1.0, axis=1)       # NaN/inf compare False -> unsafe
        x = np.where(np.isfinite(x), x, 1e6)
    nrm = np.sqrt((x * x).sum(-1))
    lam = np.clip((np.log(np.maximum(nrm, 1e-300)) - math.log(R0)) / S, -5.0, None).mean(1)
    return lam, safe


def world(seed):
    rng = np.random.default_rng([seed, 7])
    off = rng.random() * 2 * math.pi / R
    ang = off + 2 * math.pi * np.arange(R) / R
    x0 = R0 * np.stack([np.cos(ang), np.sin(ang)], 1)
    bits = rng.integers(0, 2, (R, S))
    A = rng.normal(0, INIT_A, (P, 2, 2, 2))
    for _ in range(200):
        _, ok = concrete(A, x0, bits)
        if ok.all():
            break
        A[~ok] = rng.normal(0, INIT_A, ((~ok).sum(), 2, 2, 2))
    _, ok = concrete(A, x0, bits)
    A[~ok] *= 0.3
    return x0, bits, A


def fitness(A, x0, bits, arm, dom):
    lam, safe = concrete(A, x0, bits)
    f = lam - shape_pen(A)
    if arm == "PC":
        f = f + LAM * align_individual(A, dom)
    return f, safe


def run(seed, arm, dom=0.0, ref_accept=None):
    x0, bits, A = world(seed)
    mrng = np.random.default_rng([seed, 11])
    nrng = np.random.default_rng([seed, 13])
    fit, _ = fitness(A, x0, bits, arm, dom)
    acc_hist = []
    for g in range(G):
        cA = A + mrng.normal(0, SIGMA, A.shape)
        cf, csafe = fitness(cA, x0, bits, arm, dom)
        coin = nrng.random(P)
        if arm == "PC":
            acc = csafe
        else:
            c = csafe.mean()
            p = min(1.0, ref_accept[g] / c) if c > 0 else 0.0
            acc = csafe & (coin < p)
        acc_hist.append(float(acc.mean()))
        allA = np.concatenate([A, cA[acc]]); allf = np.concatenate([fit, cf[acc]])
        idx = np.argsort(-allf, kind="stable")[:P]
        A, fit = allA[idx], allf[idx]
    lam, _ = concrete(A, x0, bits)
    return A, lam, acc_hist


def cheat(A, dom):
    phi, _, _ = svd_dir(A)
    out = A.copy()
    for i in range(A.shape[0]):
        for j in range(2):
            Q = rot(dom - phi[i, j])
            out[i, j] = Q @ A[i, j] @ Q.T
    return out


def emit(f, d):
    f.write(json.dumps(d) + "\n"); f.flush(); os.fsync(f.fileno())


def summary(A, lam):
    return dict(A4_axes0=a_k(A, 0.0), A4_axes22_5=a_k(A, ROT),
                A8_axes0=a_k(A, 0.0, 8), mean_w=float(svd_dir(A)[1].mean()),
                median_lam=float(np.median(lam)),
                median_abs_ratio=float(np.median(abs_ratio(A))))


def main():
    t0 = time.process_time()
    with open(ROWS, "w") as f:
        for seed in SEEDS:
            A, lam, ref = run(seed, "PC", 0.0)
            emit(f, dict(arm="POSITIVE_CONTROL", seed=seed, dom_deg=0.0,
                         mean_accept=float(np.mean(ref)), **summary(A, lam)))
            A, lam, acc = run(seed, "PC", ROT)
            emit(f, dict(arm="POSITIVE_CONTROL_ROT", seed=seed, dom_deg=22.5,
                         mean_accept=float(np.mean(acc)), **summary(A, lam)))
            A, lam, acc = run(seed, "NULL", 0.0, ref_accept=ref)
            gap = np.abs(np.array(acc) - np.array(ref))
            emit(f, dict(arm="NULL_TWIN", seed=seed, accept_matched_to="POSITIVE_CONTROL",
                         mean_accept=float(np.mean(acc)), mean_abs_accept_gap=float(gap.mean()),
                         **summary(A, lam)))
            emit(f, dict(arm="CHEAT", seed=seed, A4_axes0=a_k(cheat(A, 0.0), 0.0),
                         A4_axes22_5=a_k(cheat(A, ROT), ROT)))
            print(seed, round(time.process_time() - t0, 1), file=sys.stderr)
    return time.process_time() - t0


def evaluate(cpu_s, revisions):
    rows = [json.loads(l) for l in open(ROWS)]
    by = lambda arm, k: [r[k] for r in rows if r["arm"] == arm]
    mean = lambda v: float(np.mean(v))
    s1p, s1t = mean(by("POSITIVE_CONTROL", "A4_axes0")), mean(by("NULL_TWIN", "A4_axes0"))
    s2p, s2t = mean(by("POSITIVE_CONTROL_ROT", "A4_axes22_5")), mean(by("NULL_TWIN", "A4_axes22_5"))
    c1, c2 = mean(by("CHEAT", "A4_axes0")), mean(by("CHEAT", "A4_axes22_5"))
    clauses = [
        dict(id="S1", positive_value=s1p, twin_value=s1t, attainable=s1p >= TH,
             discriminating=s1t < TH,
             treatment_must_reach=TH, treatment_statistic="mean over 20 seeds of A4(dom=0), arm V"),
        dict(id="S2", positive_value=s2p, twin_value=s2t, attainable=s2p >= TH,
             discriminating=s2t < TH,
             treatment_must_reach=TH, treatment_statistic="mean over 20 seeds of A4(dom=22.5 deg), arm V_rot"),
    ]
    cheat_detected = c1 >= TH and c2 >= TH
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected
    sd = float(np.std(by("NULL_TWIN", "A4_axes0"), ddof=1))
    return dict(clauses=clauses, cheat_detected=cheat_detected,
                cheat_values=dict(S1=c1, S2=c2), frozen=frozen,
                diagnostics=dict(
                    pc_rot_A4_world_axes=mean(by("POSITIVE_CONTROL_ROT", "A4_axes0")),
                    null_twin_per_seed_sd_A4=sd,
                    null_twin_sd_of_20_seed_mean=sd / math.sqrt(len(SEEDS)),
                    null_twin_mean_abs_accept_gap=mean(by("NULL_TWIN", "mean_abs_accept_gap")),
                    pc_mean_accept=mean(by("POSITIVE_CONTROL", "mean_accept")),
                    twin_mean_accept=mean(by("NULL_TWIN", "mean_accept")),
                    pc_median_lam=mean(by("POSITIVE_CONTROL", "median_lam")),
                    twin_median_lam=mean(by("NULL_TWIN", "median_lam")),
                    pc_mean_w=mean(by("POSITIVE_CONTROL", "mean_w")),
                    twin_mean_w=mean(by("NULL_TWIN", "mean_w")),
                    pc_A8=mean(by("POSITIVE_CONTROL", "A8_axes0")),
                    twin_A8=mean(by("NULL_TWIN", "A8_axes0")),
                    pc_abs_ratio=mean(by("POSITIVE_CONTROL", "median_abs_ratio")),
                    twin_abs_ratio=mean(by("NULL_TWIN", "median_abs_ratio"))),
                cpu_core_seconds_last_run=cpu_s, revisions=revisions)


if __name__ == "__main__":
    cpu = main()
    rp = os.path.join(HERE, "revisions.json")
    revs = json.load(open(rp)) if os.path.exists(rp) else []
    res = evaluate(cpu, revs)
    json.dump(res, open(os.path.join(HERE, "ATTAINABILITY.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
