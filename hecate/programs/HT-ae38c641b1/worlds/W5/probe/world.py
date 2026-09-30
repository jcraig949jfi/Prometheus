"""HT-ae38c641b1 / W5 probe: TREATMENT (V, V_rot) and CONTROL arms.

Controls are re-run through the frozen controls.py functions (same code path);
controls.main() is not called because it overwrites frozen files.
Writes probe/rows.jsonl, one row per (arm, seed), flushed + fsynced.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, math, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import controls as C  # frozen

ROWS = os.path.join(HERE, "rows.jsonl")
KLEENE = 30
WIDEN = 1.05
H0 = np.array([0.5, 0.5])
PARAMS = dict(P=C.P, G=C.G, R=C.R, S=C.S, SIGMA=C.SIGMA, INIT_A=C.INIT_A, LAM=C.LAM,
              KLEENE=KLEENE, WIDEN=WIDEN, H0=H0.tolist())


def proven(A, dom):
    """Budgeted box verifier. A: (N, 2, 2, 2). Returns bool (N,)."""
    Q = C.rot(dom)
    with np.errstate(all="ignore"):
        B = np.abs(np.einsum("ki,njkl,lm->njim", Q, A, Q))  # |Q^T A_j Q|
        h = np.broadcast_to(H0, (A.shape[0], 2)).copy()
        for _ in range(KLEENE):
            h1 = np.einsum("nij,nj->ni", B[:, 0], h)
            h2 = np.einsum("nij,nj->ni", B[:, 1], h)
            h = np.maximum(np.maximum(H0, h1), h2)
        hs = WIDEN * h
        ind = np.ones(A.shape[0], bool)
        for j in range(2):
            ind &= np.all(np.einsum("nij,nj->ni", B[:, j], hs) <= hs, axis=1)
        disc = (hs * hs).sum(1) <= 1.0
    return ind & disc


def run_verifier(seed, dom):
    """controls.run with the gate replaced by PROVEN(dom); no concrete gate, no bonus."""
    x0, bits, A = C.world(seed)
    mrng = np.random.default_rng([seed, 11])
    nrng = np.random.default_rng([seed, 13])
    fit, _ = C.fitness(A, x0, bits, "V", dom)
    acc_hist = []
    for g in range(C.G):
        cA = A + mrng.normal(0, C.SIGMA, A.shape)
        cf, _ = C.fitness(cA, x0, bits, "V", dom)
        nrng.random(C.P)  # drawn, unused: keeps streams parallel with controls.run
        acc = proven(cA, dom)
        acc_hist.append(float(acc.mean()))
        allA = np.concatenate([A, cA[acc]]); allf = np.concatenate([fit, cf[acc]])
        idx = np.argsort(-allf, kind="stable")[:C.P]
        A, fit = allA[idx], allf[idx]
    lam, _ = C.concrete(A, x0, bits)
    return A, lam, acc_hist


def main():
    t0 = time.process_time()
    with open(ROWS, "w") as f:
        for seed in C.SEEDS:
            # ---- controls, same code path as controls.main ----
            A, lam, ref = C.run(seed, "PC", 0.0)
            C.emit(f, dict(arm="POSITIVE_CONTROL", seed=seed, dom_deg=0.0,
                           mean_accept=float(np.mean(ref)), params=PARAMS, **C.summary(A, lam)))
            A, lam, acc = C.run(seed, "PC", C.ROT)
            C.emit(f, dict(arm="POSITIVE_CONTROL_ROT", seed=seed, dom_deg=22.5,
                           mean_accept=float(np.mean(acc)), params=PARAMS, **C.summary(A, lam)))
            A, lam, acc = C.run(seed, "NULL", 0.0, ref_accept=ref)
            gap = np.abs(np.array(acc) - np.array(ref))
            C.emit(f, dict(arm="NULL_TWIN", seed=seed, accept_matched_to="POSITIVE_CONTROL",
                           mean_accept=float(np.mean(acc)), mean_abs_accept_gap=float(gap.mean()),
                           params=PARAMS, **C.summary(A, lam)))
            C.emit(f, dict(arm="CHEAT", seed=seed, A4_axes0=C.a_k(C.cheat(A, 0.0), 0.0),
                           A4_axes22_5=C.a_k(C.cheat(A, C.ROT), C.ROT), params=PARAMS))
            # ---- treatment ----
            for arm, dom, twin in (("V", 0.0, "NULL_TWIN_V"), ("V_rot", C.ROT, "NULL_TWIN_VROT")):
                A, lam, vacc = run_verifier(seed, dom)
                C.emit(f, dict(arm=arm, seed=seed, dom_deg=math.degrees(dom),
                               mean_accept=float(np.mean(vacc)), accept_by_gen=vacc,
                               params=PARAMS, **C.summary(A, lam)))
                A, lam, acc = C.run(seed, "NULL", 0.0, ref_accept=vacc)
                gap = np.abs(np.array(acc) - np.array(vacc))
                C.emit(f, dict(arm=twin, seed=seed, accept_matched_to=arm,
                               mean_accept=float(np.mean(acc)), mean_abs_accept_gap=float(gap.mean()),
                               params=PARAMS, **C.summary(A, lam)))
            print(seed, round(time.process_time() - t0, 1), file=sys.stderr, flush=True)
    cpu = time.process_time() - t0
    json.dump(dict(cpu_core_seconds=cpu), open(os.path.join(HERE, "run_meta.json"), "w"))
    return cpu


if __name__ == "__main__":
    print("cpu_core_s", main())
