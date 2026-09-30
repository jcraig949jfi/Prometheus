"""HT-a9e2ba7618 / W4: carrier-relative phase code under monotone time warps.

See IMPLEMENTATION_NOTES.md for the spec -> code mapping. Writes rows.jsonl
(one JSON object per (arm, seed)), flushed per row.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import json
import time
import numpy as np

ATTEMPT = 1
HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

F0 = 6.0
T = 1.0 / F0
NSLOT = 5
NCYC = 20
PAD_CYC = 2
NSEQ = 200
FS = 200.0
NOISE_SD = 0.1
W0 = 6.0
FREQS = np.geomspace(3.0, 15.0, 40)
W_LEVELS = [0.0, 0.1, 0.2, 0.4]
SEEDS = list(range(10))
PC_SEEDS = list(range(100, 110))
CHEAT_SEEDS = list(range(200, 210))
NFFT = 2048
CHUNK = 25

PARAMS = dict(F0=F0, NSLOT=NSLOT, NCYC=NCYC, PAD_CYC=PAD_CYC, NSEQ=NSEQ, FS=FS,
              NOISE_SD=NOISE_SD, MORLET_W0=W0, FREQ_MIN=3.0, FREQ_MAX=15.0,
              NFREQ=len(FREQS), W_LEVELS=W_LEVELS, NFFT=NFFT,
              KNOT_INTERVAL="Uniform[0.5,1.5]*T", SLOPE="1+w*Uniform[-1,1]",
              clock_onset="oracle received onset", ATTEMPT=ATTEMPT)

# Morlet kernels in the frequency domain (analytic, unit gain at centre freq)
_omega = 2 * np.pi * np.fft.rfftfreq(NFFT, d=1.0 / FS)
_scales = W0 / (2 * np.pi * FREQS)
KERN = 2.0 * np.exp(-0.5 * (_scales[:, None] * _omega[None, :] - W0) ** 2)
KERN[:, 0] = 0.0


def make_warp(rng, w):
    """Knots (tau_k, g_k) of a piecewise-linear monotone map, source->received."""
    tau0, tau1 = -PAD_CYC * T, (NCYC + PAD_CYC) * T
    taus = [tau0]
    while taus[-1] < tau1:
        taus.append(taus[-1] + rng.uniform(0.5, 1.5) * T)
    taus = np.array(taus)
    slopes = 1.0 + w * rng.uniform(-1.0, 1.0, size=len(taus) - 1)
    g = np.concatenate([[0.0], np.cumsum(slopes * np.diff(taus))])
    return taus, g


def make_transmission(rng, w):
    sym = rng.integers(0, NSLOT, size=NCYC)
    taus, g = make_warp(rng, w)
    onset_src = np.arange(NCYC) * T
    pulse_src = (np.arange(NCYC) + (sym + 0.5) / NSLOT) * T
    onset_rx = np.interp(onset_src, taus, g)
    pulse_rx = np.interp(pulse_src, taus, g)
    t_end = np.interp((NCYC + PAD_CYC) * T, taus, g)
    t = np.arange(0.0, t_end, 1.0 / FS)
    tau_of_t = np.interp(t, g, taus)
    noise_a = rng.normal(0.0, NOISE_SD, size=t.size)
    noise_b = rng.normal(0.0, NOISE_SD, size=t.size)
    carrier_cowarp = np.cos(2 * np.pi * F0 * tau_of_t) + noise_a
    carrier_unwarp = np.cos(2 * np.pi * F0 * t) + noise_b  # null twin
    pulse_idx = np.clip(np.round(pulse_rx * FS).astype(int), 0, t.size - 1)
    # stupid-explanation-2 diagnostic: does true elapsed time cross a slot edge
    elapsed = pulse_rx - onset_rx
    clock_slot = np.minimum(NSLOT - 1, np.floor(elapsed / (T / NSLOT))).astype(int)
    return dict(sym=sym, pulse_idx=pulse_idx, pulse_rx=pulse_rx,
                onset_rx=onset_rx, c_co=carrier_cowarp, c_un=carrier_unwarp,
                crossed=(clock_slot != sym))


def cwt_ridge_phase(signals, pulse_idx):
    """signals: list of 1-D arrays; returns ridge phase at pulse indices."""
    X = np.zeros((len(signals), NFFT))
    for i, s in enumerate(signals):
        X[i, :s.size] = s
    Xf = np.fft.rfft(X, axis=1)
    # analytic (complex) Morlet coefficients: ifft of the one-sided spectrum
    full = np.zeros((len(signals), len(FREQS), NFFT), dtype=complex)
    full[:, :, :Xf.shape[1]] = Xf[:, None, :] * KERN[None, :, :]
    Wc = np.fft.ifft(full, axis=2)
    out = []
    for i in range(len(signals)):
        vals = Wc[i][:, pulse_idx[i]]           # (nfreq, npulse)
        ridge = np.argmax(np.abs(vals), axis=0)
        ph = np.angle(vals[ridge, np.arange(vals.shape[1])])
        out.append(np.mod(ph, 2 * np.pi))
    return out


def phase_to_slot(ph):
    return np.minimum(NSLOT - 1, np.floor(ph / (2 * np.pi) * NSLOT)).astype(int)


def decode_clock(tx):
    elapsed = tx["pulse_rx"] - tx["onset_rx"]
    return np.minimum(NSLOT - 1, np.floor(elapsed / (T / NSLOT))).astype(int)


def run_condition(seed, wi, w):
    rng = np.random.default_rng([4, seed, wi])
    txs = [make_transmission(rng, w) for _ in range(NSEQ)]
    n = NSEQ * NCYC
    corr_T = corr_C = corr_N = crossed = 0
    for a in range(0, NSEQ, CHUNK):
        chunk = txs[a:a + CHUNK]
        pidx = [tx["pulse_idx"] for tx in chunk]
        ph_T = cwt_ridge_phase([tx["c_co"] for tx in chunk], pidx)
        ph_N = cwt_ridge_phase([tx["c_un"] for tx in chunk], pidx)
        for tx, pt, pn in zip(chunk, ph_T, ph_N):
            corr_T += int(np.sum(phase_to_slot(pt) == tx["sym"]))
            corr_N += int(np.sum(phase_to_slot(pn) == tx["sym"]))
            corr_C += int(np.sum(decode_clock(tx) == tx["sym"]))
            crossed += int(np.sum(tx["crossed"]))
    return dict(acc_T=corr_T / n, acc_C=corr_C / n, acc_N=corr_N / n,
                frac_boundary_crossed=crossed / n, n_symbols=n)


def write_row(fh, row):
    fh.write(json.dumps(row) + "\n")
    fh.flush()
    os.fsync(fh.fileno())


def main():
    cpu0 = time.process_time()
    wall0 = time.time()
    with open(ROWS, "w", encoding="utf-8") as fh:
        # TREATMENT / CONTROL / NULL_TWIN share the same transmissions
        for seed in SEEDS:
            res = {w: run_condition(seed, wi, w) for wi, w in enumerate(W_LEVELS)}
            cpu = time.process_time() - cpu0
            for arm, key, dec in (("TREATMENT", "acc_T", "carrier_phase_cowarped"),
                                  ("CONTROL", "acc_C", "clock_time"),
                                  ("NULL_TWIN", "acc_N", "carrier_phase_unwarped_carrier")):
                write_row(fh, dict(arm=arm, seed=seed, decoder=dec, params=PARAMS,
                                   acc_by_w={str(w): res[w][key] for w in W_LEVELS},
                                   frac_boundary_crossed_by_w={str(w): res[w]["frac_boundary_crossed"] for w in W_LEVELS},
                                   n_symbols_per_w=res[W_LEVELS[0]]["n_symbols"],
                                   cpu_seconds_cumulative=cpu))
            print(f"seed {seed}: cpu {cpu:.1f}s", flush=True)
        for seed in PC_SEEDS:
            r = run_condition(seed, 0, 0.0)
            write_row(fh, dict(arm="POSITIVE_CONTROL", seed=seed, params=PARAMS,
                               w=0.0, acc_carrier=r["acc_T"], acc_clock=r["acc_C"],
                               n_symbols_per_w=r["n_symbols"],
                               cpu_seconds_cumulative=time.process_time() - cpu0))
        for seed in CHEAT_SEEDS:
            rng = np.random.default_rng([4, seed, 99])
            n = NSEQ * NCYC
            truth = {w: rng.integers(0, NSLOT, size=n) for w in W_LEVELS}
            def acc(w, inject_truth):
                dec = truth[w] if inject_truth else rng.integers(0, NSLOT, size=n)
                return float(np.mean(dec == truth[w]))
            write_row(fh, dict(arm="CHEAT", seed=seed, params=PARAMS,
                               injection="carrier decoded := truth at all w; clock and null-twin := truth at w=0, uniform random at w>0",
                               acc_T_by_w={str(w): acc(w, True) for w in W_LEVELS},
                               acc_C_by_w={str(w): acc(w, w == 0.0) for w in W_LEVELS},
                               acc_N_by_w={str(w): acc(w, w == 0.0) for w in W_LEVELS},
                               n_symbols_per_w=n,
                               cpu_seconds_cumulative=time.process_time() - cpu0))
    print(f"done: cpu {time.process_time() - cpu0:.1f}s wall {time.time() - wall0:.1f}s")


if __name__ == "__main__":
    main()
