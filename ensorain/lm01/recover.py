"""WTP-LM01 history-recoverability meter (O5; steward #591: rate MATCHED, distinguishability REPORTED).

DEFECT D1 (dev, 2026-09-25, reported to the stewards): the thresholded R(tau) has a chance floor (the global-mean
predictor already "recovers" ~12% of a low-rank history at tau=0.1), and it is NON-MONOTONE in merge coarseness
(random merge: 1 bin .117, 64 bins .098, 512 bins .495). It cannot be the matched rate. The proposed MATCHED quantity
is HR2, a threshold-free measure monotone in merge coarseness on dev with seed SD <= .03:
  HR2 = 1 - mean((reconstruction - y)^2) / var(y) over the admitted history
R(tau) and Dist stay REPORTED.

R(t)  = fraction of the observations admitted up to step t whose exact value the arm's PERSISTENT STATE
        reproduces within tau (arm.reconstruct: a LOSSLESS arm returns the record, a lossy arm its readout
        at that cell). tau is declared per world from the observation noise, before any data.
Dist  = over sampled pairs of admitted records whose values differ by more than 2*tau, the fraction whose
        reconstructions still differ by more than tau (reported, never matched).
HR2_signal (#627, REPORTED): the same reconstruction scored against the generator's noise-free value at each admitted
        cell; HR2 - HR2_signal separates discarded noise from discarded signal.
Reconstruction maps (declared; never tuned): LOSSLESS/HYBRID return the stored record; SELECTIVE its substrate's
        readout at the cell; RandomMerge the bin mean (global mean for an empty bin).
None of these quantities reads task relevance: relevance comes only from the generator oracle (memo G2)."""
import numpy as np


def recoverability(arm, A, y, tau, rng, max_n=2000, n_pairs=2000, signal=None):
    n = len(y)
    if n == 0:
        return dict(HR2=None, HR2_signal=None, R=None, dist=None, n=0)
    idx = np.sort(rng.choice(n, size=min(n, max_n), replace=False))
    rec = arm.reconstruct(idx, A[idx])
    ok = np.abs(rec - y[idx]) <= tau
    i = rng.integers(0, len(idx), n_pairs)
    j = rng.integers(0, len(idx), n_pairs)
    far = np.abs(y[idx][i] - y[idx][j]) > 2 * tau
    hr2 = float(1 - np.mean((rec - y[idx]) ** 2) / max(np.var(y[idx]), 1e-12))
    hr2s = None
    if signal is not None:                      # #627: same map scored against the generator's noise-free values
        sg = np.asarray(signal)[idx]
        hr2s = float(1 - np.mean((rec - sg) ** 2) / max(np.var(sg), 1e-12))
    dist = float((np.abs(rec[i] - rec[j]) > tau)[far].mean()) if far.any() else None
    return dict(HR2=hr2, HR2_signal=hr2s, R=float(ok.mean()), dist=dist, n=int(len(idx)))
