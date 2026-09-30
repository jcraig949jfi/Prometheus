"""W6 controls (HT-e106e1603b, pass P3v2). NO TREATMENT CODE.

World: a redundancy thermostat (scrub protection lowered after quiet
periods, raised after failures). Does persistence of the residual errors
left by a failed scrub couple epochs and make failures cluster on long
time scales beyond a memoryless twin driven by the same failure curve and
the same update rule?

Observable: failure indicator per epoch. Statistic (L7 inter-failure clock):
    F = Fano(1000) / Fano(10)
Fano(W) = variance / mean of failure counts in non-overlapping windows of
W epochs over the measured epochs.

Arms here (the treatment, real bit-flip scrubs with residue persisting
between epochs, is NOT implemented here):
  calibration:      Pfail(s) = fresh-start failure probability of the real
                    scrub decoder at each protection level s (substrate
                    measurement, no controller, no persistence).
  NULL_TWIN:        the controller driven by Bernoulli(Pfail(s)) failures.
                    This is exactly the treatment with the residue reset to
                    zero after every failure (every epoch starts clean), so
                    it keeps the curve and the rule and destroys persistence.
  POSITIVE_CONTROL: the twin plus an explicit slow persistent-damage state
                    that raises failure probability for a long, random
                    time after a failure (epoch coupling present by
                    construction), under the same controller.
  RATE_TWIN_DIAG:   diagnostic only (no clause): NULL_TWIN with a constant
                    added failure probability matched to the positive
                    control's failure rate; shows rate alone does not pass.
  CHEAT:            failure stream written directly with long-window rate
                    modulation (success injected into the observable).
All arms share the controller (step_controller) and the statistic
(fano_ratio). Rows -> control_rows.jsonl, flushed per row.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

N = 504
DV, DC = 3, 6
M = N * DV // DC
SWEEPS = 30               # scrub = up to 30 parallel bit-flip sweeps
S_MAX = 24                # protection levels 0..24
P0, RHO = 0.04, 0.75      # per-epoch noise p(s) = P0 * RHO**s
QUIET = 20                # clean epochs before protection is lowered by 1
UP = 3                    # protection raised by 3 after a failure
S_START = 12
BURN = 2000
EPOCHS = 100_000          # measured epochs
CAL_BLOCKS = 600          # fresh starts per level for Pfail(s)
SEEDS = [0, 1, 2, 3, 4]

# positive-control persistent damage
PC_ENTER = 0.05           # prob a failure opens a damage episode
PC_MEAN_LEN = 1000        # mean episode length (geometric)
PC_KAPPA = 0.05           # added failure prob during an episode

# diagnostic: memoryless twin with an always-on added failure prob,
# chosen so its failure rate matches the positive control's (~0.03)
RATE_KAPPA = 0.016

# cheat modulation
CH_LO, CH_HI, CH_BLOCK = 0.004, 0.030, 1000


def p_of_s(s):
    return P0 * RHO ** s


def make_graph(seed):
    rng = np.random.default_rng(10_000 + seed)
    var_sockets = np.repeat(np.arange(N), DV)
    for _ in range(1000):
        cv = rng.permutation(var_sockets).reshape(M, DC)
        bad = [c for c in range(M) if len(set(cv[c])) < DC]
        tries = 0
        while bad and tries < 20000:
            c = bad[0]
            seen = set()
            for j, v in enumerate(cv[c]):
                if v in seen:
                    c2, j2 = rng.integers(M), rng.integers(DC)
                    cv[c, j], cv[c2, j2] = cv[c2, j2], cv[c, j]
                    break
                seen.add(v)
            bad = [c for c in range(M) if len(set(cv[c])) < DC]
            tries += 1
        if not bad:
            return cv
    raise RuntimeError("graph repair failed")


def var_checks(cv):
    vc = [[] for _ in range(N)]
    for c in range(M):
        for v in cv[c]:
            vc[v].append(c)
    return np.array(vc)  # N x DV


def scrub_batch(e, cv, vc):
    """Parallel bit-flip scrub on a batch (B x N): each sweep flips every
    variable with >= 2 of its 3 checks unsatisfied; stops at quiescence or
    SWEEPS. Returns residual error array. Substrate decoder (shared with the
    treatment by specification)."""
    e = e.copy()
    for _ in range(SWEEPS):
        synd = e[:, cv].sum(axis=2) % 2            # B x M
        unsat = synd[:, vc].sum(axis=2)            # B x N
        flip = unsat >= 2
        if not flip.any():
            break
        e ^= flip.astype(np.uint8)
    return e


def calibrate(cv, vc, seed):
    rng = np.random.default_rng(20_000 + seed)
    pf = np.zeros(S_MAX + 1)
    for s in range(S_MAX + 1):
        e = (rng.random((CAL_BLOCKS, N)) < p_of_s(s)).astype(np.uint8)
        r = scrub_batch(e, cv, vc)
        pf[s] = float((r.sum(axis=1) > 0).mean())
    return pf


def step_controller(s, quiet, failed):
    """Shared update rule. Returns (s, quiet)."""
    if failed:
        return min(s + UP, S_MAX), 0
    quiet += 1
    if quiet >= QUIET:
        return max(s - 1, 0), 0
    return s, quiet


def run_twin(pf, seed, persistent=False, always_kappa=0.0):
    rng = np.random.default_rng(30_000 + seed + (500 if persistent else 0)
                                + (900 if always_kappa else 0))
    s, quiet, dmg = S_START, 0, 0
    fails = np.zeros(BURN + EPOCHS, dtype=np.uint8)
    levels = np.zeros(BURN + EPOCHS, dtype=np.int16)
    for i in range(BURN + EPOCHS):
        pfail = pf[s] + always_kappa * (1.0 - pf[s])
        if persistent and dmg > 0:
            pfail = pfail + PC_KAPPA * (1.0 - pfail)
            dmg -= 1
        f = rng.random() < pfail
        if persistent and f and dmg == 0 and rng.random() < PC_ENTER:
            dmg = int(rng.geometric(1.0 / PC_MEAN_LEN))
        fails[i], levels[i] = f, s
        s, quiet = step_controller(s, quiet, f)
    return fails[BURN:], levels[BURN:]


def run_cheat(seed):
    rng = np.random.default_rng(40_000 + seed)
    nb = EPOCHS // CH_BLOCK
    rates = np.where(rng.random(nb) < 0.5, CH_LO, CH_HI)
    return (rng.random(EPOCHS) < np.repeat(rates, CH_BLOCK)).astype(np.uint8)


def fano(fails, w):
    k = len(fails) // w
    c = fails[: k * w].reshape(k, w).sum(axis=1).astype(float)
    m = c.mean()
    return float(c.var(ddof=1) / m) if m > 0 else float("nan")


def fano_ratio(fails):
    """The single statistic code path used by every arm (and the treatment)."""
    f10, f100, f1000 = fano(fails, 10), fano(fails, 100), fano(fails, 1000)
    return f1000 / f10, f10, f100, f1000


def main():
    t0, w0 = time.process_time(), time.time()
    open(ROWS, "w").close()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for seed in SEEDS:
            cv = make_graph(seed)
            vc = var_checks(cv)
            pf = calibrate(cv, vc, seed)
            fh.write(json.dumps({"arm": "CALIBRATION", "seed": seed,
                                 "p_of_s": [p_of_s(s) for s in range(S_MAX + 1)],
                                 "pfail": pf.tolist()}) + "\n")
            fh.flush()
            print("cal", seed, np.round(pf, 3).tolist(), flush=True)
            for arm in ("NULL_TWIN", "POSITIVE_CONTROL", "CHEAT", "RATE_TWIN_DIAG"):
                if arm == "CHEAT":
                    fails, levels = run_cheat(seed), None
                elif arm == "RATE_TWIN_DIAG":
                    fails, levels = run_twin(pf, seed, always_kappa=RATE_KAPPA)
                else:
                    fails, levels = run_twin(pf, seed, arm == "POSITIVE_CONTROL")
                F, f10, f100, f1000 = fano_ratio(fails)
                row = {"arm": arm, "seed": seed, "epochs": int(len(fails)),
                       "F": F, "fano10": f10, "fano100": f100, "fano1000": f1000,
                       "fail_rate": float(fails.mean()),
                       "mean_level": None if levels is None else float(levels.mean()),
                       "frac_at_smax": None if levels is None else float((levels == S_MAX).mean())}
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                print(arm, seed, round(F, 3), round(float(fails.mean()), 4), flush=True)
    with open(os.path.join(HERE, "controls_cpu.json"), "w") as fh:
        json.dump({"cpu_seconds": time.process_time() - t0,
                   "wall_seconds": time.time() - w0}, fh)
    print("cpu_s", round(time.process_time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main())
