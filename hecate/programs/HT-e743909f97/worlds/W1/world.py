"""HT-e743909f97 / W1: delayed clonal-gain loop with exhaustion.

Arms: TREATMENT, CONTROL, NULL_TWIN, POSITIVE_CONTROL, CHEAT.
See IMPLEMENTATION_NOTES.md for every reading and parameter.
Writes rows.jsonl (one row per arm x exhaustion x tau x seed, flushed).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json
import math
import sys
import time

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

# ---- parameters (fixed before any run) ----
R = 0.05
CDEC = 0.05
K = 1e-6
A0 = 0.025
PSTAR = CDEC * R / (A0 * K)      # 100000
CSTAR = R / K                    # 50000
STEPS = 5000
WIN = 2000
CV_THR = 0.2
TAUS = np.arange(40)             # 0..39
NSEEDS = 20
ETA = 0.5
KICK = 1.1
DIV_CAP = 1e13
MASTER = 20260929
ARM_CODE = {"TREATMENT": 1, "CONTROL": 2, "NULL_TWIN": 3, "POSITIVE_CONTROL": 4}
PC_K = 2 * math.sin(math.pi / 104)
PC_TAU_ANALYTIC = (math.pi / (2 * math.asin(PC_K / 2)) - 1) / 2   # 25.5
PC_NOISE = 0.001


def nyquist_tau(D, g):
    """Smallest positive real delay tau at which D(z) + g z^-tau has a root on |z|=1."""
    w = brentq(lambda w: abs(D(np.exp(1j * w))) - g, 1e-9, math.pi)
    tau = (math.pi - np.angle(D(np.exp(1j * w)))) / w
    return float(tau % (2 * math.pi / w)), float(w)


TAU_PRED, W_PRED = nyquist_tau(lambda z: (z - 1) * (z - 1 + CDEC), A0 * K * PSTAR)
T_EXH = int(round(TAU_PRED))
PC_TAU_NYQ, _ = nyquist_tau(lambda z: z - 1, PC_K)

PARAMS = dict(r=R, c=CDEC, k=K, a0=A0, p_star=PSTAR, C_star=CSTAR, steps=STEPS,
              window=WIN, cv_threshold=CV_THR, eta=ETA, T_exh=T_EXH, kick=KICK,
              div_cap=DIV_CAP, tau_pred=TAU_PRED, master_seed=MASTER,
              pc_K=PC_K, pc_tau_analytic=PC_TAU_ANALYTIC, pc_tau_nyquist=PC_TAU_NYQ,
              pc_noise_frac=PC_NOISE)


def rng_for(arm, exh, s):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([MASTER, ARM_CODE[arm], exh, s])))


def cv_of(ptraj, diverged):
    """ptraj: (STEPS+1, n). Returns cv (None where undefined/diverged), indicator, extinct."""
    w = ptraj[STEPS - WIN:STEPS].astype(float)
    m = w.mean(axis=0)
    sd = w.std(axis=0)
    out_cv, ind, ext = [], [], []
    for j in range(w.shape[1]):
        extinct_any = bool(ptraj[:, j].min() <= 0)
        if diverged[j]:
            out_cv.append(None); ind.append(True)
        elif m[j] <= 0:
            out_cv.append(None); ind.append(False)
        else:
            v = float(sd[j] / m[j]); out_cv.append(v); ind.append(v > CV_THR)
        ext.append(extinct_any)
    return out_cv, ind, ext


def run_loop(rng, a_mode, exh_on=False, a_fix=None, C_given=None):
    """Clone loop vectorised over TAUS. a_mode: 'adaptive' or 'fixed' or 'given_C'."""
    n = len(TAUS)
    cols = np.arange(n)
    O = int(TAUS.max()) + 1
    hist = np.full((STEPS + 1 + O, n), int(PSTAR), dtype=np.int64)
    p = np.full(n, int(round(KICK * PSTAR)), dtype=np.int64)
    hist[O] = p
    C = np.full(n, int(CSTAR), dtype=np.int64)
    Cser = np.zeros((STEPS, n), dtype=np.float64)
    run = np.zeros(n, dtype=np.int64)
    a_sum = np.zeros(n); exh_steps = np.zeros(n); kC_sum = np.zeros(n)
    div = np.zeros(n, dtype=bool)
    for t in range(STEPS):
        if C_given is not None:
            Ck = C_given[t]
        else:
            Ck = C
            Cser[t] = C
        pk = np.where(div, 0, p)
        kprob = np.minimum(1.0, K * Ck)
        kC_sum += K * Ck
        births = rng.poisson(R * pk)
        deaths = rng.binomial(pk, kprob)
        p_new = pk + births - deaths
        if C_given is None:
            if a_mode == "adaptive" and exh_on:
                X = run >= T_EXH
                a_t = A0 * (1 - ETA * X)
                exh_steps += X
            elif a_mode == "fixed":
                a_t = a_fix
            else:
                a_t = np.full(n, A0)
            a_sum += a_t
            pdel = hist[O + t - TAUS, cols]
            recruit = rng.poisson(a_t * pdel)
            cdeath = rng.binomial(C, CDEC)
            C = C + recruit - cdeath
        run = np.where(p_new >= p, run + 1, 0)
        newdiv = p_new > DIV_CAP
        div = div | newdiv
        p = np.where(div, np.maximum(p, p_new), p_new)
        hist[O + t + 1] = p
    ptraj = hist[O:]
    return dict(ptraj=ptraj, Cser=Cser, mean_a=a_sum / STEPS, exh_frac=exh_steps / STEPS,
                mean_kC=kC_sum / STEPS, diverged=div)


def surrogate(rng, series):
    """Phase-randomised surrogate per column: same mean, spectrum, variance."""
    F = np.fft.rfft(series, axis=0)
    ph = rng.uniform(0, 2 * np.pi, size=F.shape)
    ph[0] = 0.0
    if series.shape[0] % 2 == 0:
        ph[-1] = 0.0
    S = np.fft.irfft(np.abs(F) * np.exp(1j * (np.angle(F) + ph)), n=series.shape[0], axis=0)
    clip = (S < 0).mean(axis=0)
    return np.maximum(S, 0.0), clip


def run_pc(rng):
    n = len(TAUS)
    cols = np.arange(n)
    O = int(TAUS.max()) + 1
    hist = np.full((STEPS + 1 + O, n), PSTAR, dtype=np.float64)
    hist[O] = KICK * PSTAR
    div = np.zeros(n, dtype=bool)
    for t in range(STEPS):
        p = hist[O + t]
        pdel = hist[O + t - TAUS, cols]
        new = p - PC_K * (pdel - PSTAR) + rng.normal(0, PC_NOISE * PSTAR, n)
        div = div | (np.abs(new) > DIV_CAP)
        new = np.where(div, p, new)
        hist[O + t + 1] = new
    return hist[O:], div


def main():
    t0 = time.process_time()
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    f = open(ROWS, "w", encoding="utf-8")

    def emit(arm, exh, s, res_cv, res_ind, res_ext, extra):
        for j, tau in enumerate(TAUS):
            row = dict(arm=arm, exhaustion=bool(exh), tau=int(tau), seed=int(s), attempt=attempt,
                       cv=res_cv[j], indicator=bool(res_ind[j]), p_extinct=bool(res_ext[j]))
            for key, val in extra.items():
                row[key] = (val[j].item() if hasattr(val[j], "item") else val[j]) if isinstance(val, (list, np.ndarray)) else val
            row["params"] = PARAMS
            f.write(json.dumps(row) + "\n")
            f.flush()

    for s in range(NSEEDS):
        treat = {}
        for exh in (0, 1):
            res = run_loop(rng_for("TREATMENT", exh, s), "adaptive", exh_on=bool(exh))
            treat[exh] = res
            cv, ind, ext = cv_of(res["ptraj"], res["diverged"])
            emit("TREATMENT", exh, s, cv, ind, ext,
                 dict(mean_a=res["mean_a"], exh_frac=res["exh_frac"], mean_kC=res["mean_kC"],
                      diverged=res["diverged"], C_min=res["Cser"].min(axis=0)))
        for exh in (0, 1):
            a_fix = treat[exh]["mean_a"]
            res = run_loop(rng_for("CONTROL", exh, s), "fixed", a_fix=a_fix)
            cv, ind, ext = cv_of(res["ptraj"], res["diverged"])
            emit("CONTROL", exh, s, cv, ind, ext,
                 dict(a_fix=a_fix, mean_kC=res["mean_kC"], diverged=res["diverged"]))
        for exh in (0, 1):
            rng = rng_for("NULL_TWIN", exh, s)
            Cs, clip = surrogate(rng, treat[exh]["Cser"])
            res = run_loop(rng, "given_C", C_given=Cs)
            cv, ind, ext = cv_of(res["ptraj"], res["diverged"])
            emit("NULL_TWIN", exh, s, cv, ind, ext,
                 dict(surrogate_clip_frac=clip, surrogate_mean=Cs.mean(axis=0),
                      source_mean=treat[exh]["Cser"].mean(axis=0), mean_kC=res["mean_kC"],
                      diverged=res["diverged"]))
        del treat
        ptraj, div = run_pc(rng_for("POSITIVE_CONTROL", 0, s))
        cv, ind, ext = cv_of(ptraj, div)
        emit("POSITIVE_CONTROL", 0, s, cv, ind, ext, dict(diverged=div))
        # CHEAT: success injected directly into the observable.
        on_off = math.ceil(TAU_PRED)
        on_on = math.ceil(1.5 * on_off)
        for role, exh, onset in (("treatment", 0, on_off), ("treatment", 1, on_on),
                                 ("control", 0, on_off), ("control", 1, on_off)):
            ind = [bool(t >= onset) for t in TAUS]
            cvv = [1.0 if x else 0.0 for x in ind]
            emit("CHEAT", exh, s, cvv, ind, [False] * len(TAUS), dict(cheat_role=role, injected_onset=onset))
        print(f"seed {s} done cpu={time.process_time() - t0:.1f}s", flush=True)
    f.close()
    with open(os.path.join(HERE, "world_cpu.json"), "w", encoding="utf-8") as g:
        json.dump(dict(attempt=attempt, cpu_seconds=time.process_time() - t0), g)


if __name__ == "__main__":
    main()
