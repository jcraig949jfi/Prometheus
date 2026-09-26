"""WTP-LM01 known-answer INSTRUMENT fixtures (directive s11). Not competitive arms.

The instrument must separate three kinds of memory on a planted world whose truth is known:
  F-L  no information loss        the exact store                           HR2 = 1
  F-S  relevance-selective loss   an ORACLE projector onto the generator's    HR2 < 1, HR2_signal ~ 1
                                  true low-rank subspace (discards noise only)
  F-B  relevance-blind loss       RandomMerge with B calibrated so that HR2   HR2 ~ HR2(F-S), HR2_signal < HR2_signal(F-S)
                                  matches F-S's (IM-rate construction)
DEFECT D4 (found here, 2026-09-26): an ABSOLUTE selectivity readout (HR2_signal - HR2 > 0) is not a certificate. A
relevance-blind random merge also shows it: per-bin averaging discards noise on revisits (dev: F-B HR2 .842, HR2_signal
.896). Selectivity is therefore read RELATIVE to the rate-matched blind reference (IM-rate):
  SELECTIVE_LOSS iff HR2_signal(arm) - HR2_signal(IM-rate matched to the arm's HR2) > BLIND_GAP_MIN.
The F-B fixture is a SECOND, independently seeded relevance-blind merge. It must read BLIND against the reference (no
false selectivity).
FINDING D5 (dev, 2026-09-26; seed 9_300_000; a rank-2 8x8x8 field, noise .3): the separation depends on REVISIT DENSITY.
  visits/cell   0.8   1.6   2.9   5.9   11.7
  F-S gap      .061  .058  .040  .018  .012     (F-B false-selectivity gap is always within +-.008)
Above ~3 visits/cell, per-cell averaging removes almost as much noise as the oracle projection, and the INDISCRIMINATE
comparison loses power. The default fixture uses n=800 (1.6 visits/cell).
If calibrate() cannot separate the three, LM01 STOPS (directive s11)."""
import numpy as np

from .accounting import Metered
from .arms import LosslessK, RandomMerge
from .recover import recoverability

LOSSLESS_HR2 = 0.999           # HR2 at or above this counts as no loss
SELECTIVITY_MIN = 0.02         # HR2_signal - HR2 above this: the lost part was noise (relevance-selective)
BLIND_GAP_MIN = 0.02           # at matched HR2, a blind arm's HR2_signal is lower than the selective arm's by this
MATCH_TOL = 0.01               # |HR2(arm) - HR2(IM-rate)| within this counts as rate-matched


class OracleProjector(Metered):
    """F-S: keeps a per-cell running mean, and reads it out through the TRUE low-rank basis of the generator (known only
    to this fixture). It discards exactly the component outside the relevant subspace, i.e. noise."""
    name, category = "F-S-oracle", "FIXTURE"

    def __init__(self, dims, Ubasis, s):
        super().__init__()
        self.dims, self.P, self.s = list(dims), Ubasis @ Ubasis.T, s
        self.sum = np.zeros(int(np.prod(dims)))
        self.cnt = np.zeros(int(np.prod(dims)))

    def persistent(self):
        return [self.sum, self.cnt]

    def _observe(self, A, y):
        c = np.ravel_multi_index(A.T.astype(int), self.dims)
        np.add.at(self.sum, c, y)
        np.add.at(self.cnt, c, 1)

    def _predict(self, Q):
        M = np.where(self.cnt > 0, self.sum / np.maximum(self.cnt, 1), 0.0)
        rows = int(np.prod(self.dims[:self.s]))
        M = M.reshape(rows, -1)
        W = (self.cnt > 0).reshape(rows, -1)
        # project each column's observed entries onto the true row space (least squares on the seen rows)
        X = np.zeros_like(M)
        for j in range(M.shape[1]):
            k = W[:, j]
            if k.any():
                B = self._U[k]
                coef = np.linalg.lstsq(B, M[k, j], rcond=None)[0]
                X[:, j] = self._U @ coef
        return X.reshape(-1)[np.ravel_multi_index(Q.T.astype(int), self.dims)]

    @property
    def _U(self):
        w, v = np.linalg.eigh(self.P)
        return v[:, w > 0.5]


def planted(seed=9_300_000, dims=(8, 8, 8), rank=2, n=6000, noise=0.3):
    """Low-rank + noise world with the true row basis exposed (fixture use only). n >> cells: every cell is revisited,
    so noise is averaged only where the memory keeps per-record detail."""
    rng = np.random.default_rng(seed)
    s = 1
    rows, cols = dims[0], int(np.prod(dims[1:]))
    U = np.linalg.qr(rng.normal(size=(rows, rank)))[0]
    x = (U @ rng.normal(size=(rank, cols))).reshape(dims)
    x = x / x.std()
    A = np.stack([rng.integers(0, d, n) for d in dims], 1)
    sig = x[tuple(A.T)]
    return dict(dims=list(dims), A=A, y=sig + noise * rng.normal(size=n), signal=sig, U=U, s=s, x=x)


def _feed(arm, A, y):
    for i in range(0, len(y), 200):
        arm.observe(A[i:i + 200], y[i:i + 200])
    return arm


def classify(r, ref):
    """r: the arm's recoverability; ref: the IM-rate blind merge matched to r's HR2 (None for a lossless arm)."""
    if r["HR2"] >= LOSSLESS_HR2:
        return "NO_LOSS"
    if ref is None or abs(ref["HR2"] - r["HR2"]) > MATCH_TOL:
        return "UNMATCHED"            # the blind reference cannot reach this HR2: no selectivity reading
    if r["HR2_signal"] - ref["HR2_signal"] > BLIND_GAP_MIN:
        return "SELECTIVE_LOSS"
    return "BLIND_LOSS"


def im_rate(dims, A, y, target, rr, seed, hi_mult=64):
    """IM-rate construction: bisection on B (log scale) so that HR2(RandomMerge) matches target."""
    lo, hi = 0.0, np.log2(int(np.prod(dims)) * hi_mult)
    best = None
    for _ in range(18):
        B = int(round(2 ** ((lo + hi) / 2)))
        r = dict(rr(_feed(RandomMerge(dims, B, seed=seed), A, y)), B=B)
        if best is None or abs(r["HR2"] - target) < abs(best["HR2"] - target):
            best = r
        if r["HR2"] < target:
            lo = (lo + hi) / 2
        else:
            hi = (lo + hi) / 2
    return best


def calibrate(seed=9_300_000, n=800):
    w = planted(seed, n=n)
    A, y, sg = w["A"], w["y"], w["signal"]
    rr = lambda arm: recoverability(arm, A, y, tau=0.1, rng=np.random.default_rng(seed + 1), signal=sg)
    fl = rr(_feed(LosslessK(w["dims"]), A, y))
    fs = rr(_feed(OracleProjector(w["dims"], w["U"], w["s"]), A, y))
    ref_s = im_rate(w["dims"], A, y, fs["HR2"], rr, seed + 2)
    fb = im_rate(w["dims"], A, y, fs["HR2"], rr, seed + 3)          # F-B: an independent blind merge at the same rate
    ref_b = im_rate(w["dims"], A, y, fb["HR2"], rr, seed + 2)
    out = {"F-L": dict(fl, verdict=classify(fl, None), expect="NO_LOSS"),
           "F-S": dict(fs, verdict=classify(fs, ref_s), expect="SELECTIVE_LOSS", ref=ref_s),
           "F-B": dict(fb, verdict=classify(fb, ref_b), expect="BLIND_LOSS", ref=ref_b)}
    out["PASS"] = all(out[k]["verdict"] == out[k]["expect"] for k in ("F-L", "F-S", "F-B"))
    return out
