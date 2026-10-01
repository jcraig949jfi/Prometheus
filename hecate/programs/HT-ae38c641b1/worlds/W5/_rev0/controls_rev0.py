"""HT-ae38c641b1 / W5 controls (Pass 3 v2). NO TREATMENT CODE.

Arms implemented here (all share the GA, genome, task and observable of spec.json):
  POSITIVE_CONTROL      concrete-safety gate + explicit alignment bonus to the
                        world axes (domain angle 0): imprint by construction.
  POSITIVE_CONTROL_ROT  same, bonus relative to axes rotated by 22.5 deg.
  NULL_TWIN             concrete-safety gate + genome-independent random
                        rejection matched per generation to the acceptance
                        fraction of the arm it is compared with (here: the
                        POSITIVE_CONTROL of the same seed). No geometric
                        selectivity. Scored against both domain angles.
  CHEAT                 NULL_TWIN final genomes with each map conjugated so
                        that its principal direction lies on the domain axes
                        (success injected into the observable).
The box-verifier arms V and V_rot (the treatment) are NOT implemented here.

Usage: python controls.py            -> control_rows.jsonl + ATTAINABILITY.json
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

# ---- frozen parameters (must equal spec.json "size") ----
P = 100          # population
G = 150          # generations
R = 32           # concrete test runs (fixed per seed)
S = 120          # steps per run
BURN = 10        # steps excluded from the spread statistic
SIGMA = 0.03     # isotropic Gaussian mutation, all entries of A and b
INIT_A = 0.2
INIT_B = 0.1
RADIUS = 1.0     # safety region: closed disc of radius 1 (isotropic)
LAM = 0.2        # positive-control alignment bonus weight
SEEDS = list(range(20))
ROT = math.radians(22.5)


def rot(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]])


def principal(A):
    """A: (...,2,2). Returns (phi, w): angle of the top right-singular vector
    and weight w = (s1-s2)/(s1+s2) (0 for a scaled rotation/isotropic map)."""
    u, s, vt = np.linalg.svd(A)
    v = vt[..., 0, :]                       # top right-singular vector
    phi = np.arctan2(v[..., 1], v[..., 0])
    w = (s[..., 0] - s[..., 1]) / np.maximum(s[..., 0] + s[..., 1], 1e-12)
    return phi, w


def a4(A, dom):
    """Weighted signed axial statistic of a population. A: (P,2,2,2)."""
    phi, w = principal(A)
    c = np.cos(4.0 * (phi - dom))
    return float((w * c).sum() / max(w.sum(), 1e-12)), float(w.mean())


def align_individual(A, dom):
    phi, w = principal(A)                   # (P,2)
    return (w * np.cos(4.0 * (phi - dom))).mean(axis=1)


def concrete(A, b, bits):
    """A (N,2,2,2), b (N,2,2), bits (R,S) in {0,1}. Returns spread, safe."""
    N = A.shape[0]
    x = np.zeros((N, R, 2))
    safe = np.ones(N, bool)
    pts = []
    for s in range(S):
        j = bits[:, s]
        Aj = A[:, j]                        # (N,R,2,2)
        bj = b[:, j]                        # (N,R,2)
        x = np.einsum("nrij,nrj->nri", Aj, x) + bj
        r2 = (x * x).sum(-1)
        safe &= np.all(np.isfinite(r2), axis=1) & np.all(r2 <= RADIUS ** 2, axis=1)
        x = np.where(np.isfinite(x), x, 1e6)
        if s >= BURN:
            pts.append(x.copy())
    pts = np.stack(pts, 2).reshape(N, -1, 2)
    m = pts.mean(1, keepdims=True)
    spread = np.sqrt(((pts - m) ** 2).sum(-1).mean(1))
    spread = np.where(safe, spread, 0.0)
    return spread, safe


def init_pop(rng, bits):
    A = rng.normal(0, INIT_A, (P, 2, 2, 2))
    b = rng.normal(0, INIT_B, (P, 2, 2))
    for _ in range(100):
        _, ok = concrete(A, b, bits)
        if ok.all():
            break
        bad = ~ok
        A[bad] = rng.normal(0, INIT_A, (bad.sum(), 2, 2, 2))
        b[bad] = rng.normal(0, INIT_B, (bad.sum(), 2, 2))
    _, ok = concrete(A, b, bits)
    A[~ok] *= 0.5; b[~ok] *= 0.5
    return A, b


def run(seed, arm, dom=0.0, ref_accept=None):
    rng = np.random.default_rng([seed, 7])          # world randomness (bits, init)
    bits = rng.integers(0, 2, (R, S))
    A, b = init_pop(rng, bits)
    mrng = np.random.default_rng([seed, 11])        # mutation randomness (shared by arms)
    nrng = np.random.default_rng([seed, 13])        # null-twin rejection coins
    spread, _ = concrete(A, b, bits)
    bonus = LAM * align_individual(A, dom) if arm == "PC" else 0.0
    fit = spread + bonus
    accept_hist = []
    for g in range(G):
        cA = A + mrng.normal(0, SIGMA, A.shape)
        cb = b + mrng.normal(0, SIGMA, b.shape)
        csp, csafe = concrete(cA, cb, bits)
        coin = nrng.random(P)
        if arm == "PC":
            acc = csafe
        elif arm == "NULL":
            c = csafe.mean()
            p = min(1.0, ref_accept[g] / c) if c > 0 else 0.0
            acc = csafe & (coin < p)
        accept_hist.append(float(acc.mean()))
        cfit = csp + (LAM * align_individual(cA, dom) if arm == "PC" else 0.0)
        allA = np.concatenate([A, cA[acc]]); allb = np.concatenate([b, cb[acc]])
        allf = np.concatenate([fit, cfit[acc]])
        idx = np.argsort(-allf, kind="stable")[:P]
        A, b, fit = allA[idx], allb[idx], allf[idx]
    spread, _ = concrete(A, b, bits)
    return A, b, spread, accept_hist


def cheat(A, dom):
    """Conjugate every map so its principal direction lies on the domain axis."""
    phi, w = principal(A)
    out = A.copy()
    for i in range(A.shape[0]):
        for j in range(2):
            Q = rot(dom - phi[i, j])
            out[i, j] = Q @ A[i, j] @ Q.T
    return out


def row_out(f, d):
    f.write(json.dumps(d) + "\n"); f.flush(); os.fsync(f.fileno())


def main():
    t0 = time.process_time()
    with open(ROWS, "w") as f:
        for seed in SEEDS:
            for arm, dom in (("POSITIVE_CONTROL", 0.0), ("POSITIVE_CONTROL_ROT", ROT)):
                A, b, sp, acc = run(seed, "PC", dom)
                if dom == 0.0:
                    ref, Apc = acc, A
                v0, m0 = a4(A, 0.0); vr, mr = a4(A, ROT)
                row_out(f, dict(arm=arm, seed=seed, dom_deg=math.degrees(dom),
                                A4_axes0=v0, A4_axes22_5=vr, A4_own=(v0 if dom == 0 else vr),
                                mean_w=m0, median_spread=float(np.median(sp)),
                                mean_accept=float(np.mean(acc))))
            A, b, sp, acc = run(seed, "NULL", 0.0, ref_accept=ref)
            v0, m0 = a4(A, 0.0); vr, _ = a4(A, ROT)
            row_out(f, dict(arm="NULL_TWIN", seed=seed, A4_axes0=v0, A4_axes22_5=vr,
                            mean_w=m0, median_spread=float(np.median(sp)),
                            mean_accept=float(np.mean(acc)),
                            accept_matched_to="POSITIVE_CONTROL",
                            max_abs_accept_gap=float(np.max(np.abs(np.array(acc) - np.array(ref))))))
            c0 = cheat(A, 0.0); cr = cheat(A, ROT)
            row_out(f, dict(arm="CHEAT", seed=seed, A4_axes0=a4(c0, 0.0)[0],
                            A4_axes22_5=a4(cr, ROT)[0], mean_w=m0,
                            median_spread=float(np.median(sp))))
            print(seed, round(time.process_time() - t0, 1), file=sys.stderr)
    return time.process_time() - t0


def evaluate(cpu_s, revisions):
    rows = [json.loads(l) for l in open(ROWS)]
    by = lambda arm, k: [r[k] for r in rows if r["arm"] == arm]
    mean = lambda v: float(np.mean(v))
    TH = 0.30
    s1_pos = mean(by("POSITIVE_CONTROL", "A4_axes0"))
    s1_twin = mean(by("NULL_TWIN", "A4_axes0"))
    s2_pos = mean(by("POSITIVE_CONTROL_ROT", "A4_axes22_5"))
    s2_twin = mean(by("NULL_TWIN", "A4_axes22_5"))
    s1_cheat = mean(by("CHEAT", "A4_axes0")); s2_cheat = mean(by("CHEAT", "A4_axes22_5"))
    # extra (not a clause): world-axis A4 of the rotated positive control (should be ~0)
    pcrot_world = mean(by("POSITIVE_CONTROL_ROT", "A4_axes0"))
    twin_sd = float(np.std(by("NULL_TWIN", "A4_axes0"), ddof=1))
    clauses = [
        dict(id="S1", positive_value=s1_pos, twin_value=s1_twin,
             attainable=s1_pos >= TH, discriminating=s1_twin < TH,
             treatment_must_reach=">= %.2f (mean over 20 seeds of A4_own, arm V)" % TH),
        dict(id="S2", positive_value=s2_pos, twin_value=s2_twin,
             attainable=s2_pos >= TH, discriminating=s2_twin < TH,
             treatment_must_reach=">= %.2f (mean over 20 seeds of A4_own, arm V_rot)" % TH),
    ]
    cheat_detected = (s1_cheat >= TH) and (s2_cheat >= TH)
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected
    out = dict(clauses=clauses, cheat_detected=cheat_detected,
               cheat_values=dict(S1=s1_cheat, S2=s2_cheat), frozen=frozen,
               diagnostics=dict(pc_rot_A4_world_axes=pcrot_world,
                                null_twin_seed_sd_A4=twin_sd,
                                null_twin_mean_abs_accept_gap=mean(by("NULL_TWIN", "max_abs_accept_gap")),
                                pc_median_spread=mean(by("POSITIVE_CONTROL", "median_spread")),
                                twin_median_spread=mean(by("NULL_TWIN", "median_spread")),
                                pc_mean_w=mean(by("POSITIVE_CONTROL", "mean_w")),
                                twin_mean_w=mean(by("NULL_TWIN", "mean_w"))),
               cpu_core_seconds_last_run=cpu_s, revisions=revisions)
    return out


if __name__ == "__main__":
    cpu = main()
    rev_path = os.path.join(HERE, "revisions.json")
    revisions = json.load(open(rev_path)) if os.path.exists(rev_path) else []
    res = evaluate(cpu, revisions)
    json.dump(res, open(os.path.join(HERE, "ATTAINABILITY.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
