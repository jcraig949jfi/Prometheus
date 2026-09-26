"""STATUS: NOT USED in WTP-LM01 (D11; proposed deferral #728, pending concurrence). Kept to preserve the analysis.

WTP-LM01 INTERVENTION arm (secondary; the REQUIREMENT falsifier; #619, #625, #626; checklist F1).

At t* = half of the admitted stream (declared), the frozen SELECTIVE arm is cloned:
  KEEP   continues learning on the identical remaining stream (the collider guarantees identity)
  SWAP   its learned state is replaced by an IM-rate RandomMerge built from the SAME prefix, bisected to KEEP's HR2 at t*
         (bytes charged, not matched). The merge then continues on the remaining stream.
  NEG    negative control: an independently seeded SELECTIVE of the same substrate, trained on the same prefix,
         continues. Its HR2 at t* is reported. The KEEP - NEG gap must be ~0 (within the margin).
Reading: gap = AC(KEEP) - AC(SWAP) on the headline test set at the end of life.
POSITIVE CONTROL: a planted low-rank world where the remaining stream after t* is SHORT (the swapped merge cannot
rebuild what the selective state held), so the swap must hurt.
DEFECT D11 (found at build, 2026-09-26): with SWAP = IM-rate RandomMerge, the arm is DECIDED BY CONSTRUCTION on the
never-seen headline. At KEEP's HR2 (~.98) the matched merge is a near-injective lookup table (B 77k-108k bins over 1,728
cells). A table has no mechanism to predict an unseen cell, so the gap equals the SELECTIVE arm's own competence, and
the arm cannot fire as a falsifier (the memo G1 trap). NOT for use as specified; alternatives were reported to the
stewards.
CAVEAT, verbatim in the report: "the selective state was needed for the rest of THIS life", not "selectivity in general".
"""
import copy

import numpy as np

from ensorain.wtp3.world3 import AC
from .arms import Selective
from .fixtures import im_rate
from .recover import recoverability


def _split(segs, frac=0.5):
    A = np.concatenate([s[0] for s in segs])
    y = np.concatenate([s[1] for s in segs])
    s = np.concatenate([s[2] for s in segs])
    k = int(len(y) * frac)
    return (A[:k], y[:k], s[:k]), (A[k:], y[k:], s[k:])


def _feed(arm, A, y):
    for i in range(0, len(y), 50):
        arm.observe(A[i:i + 50], y[i:i + 50])
    return arm


def run(w, kind, cap, recipe=None, headline="never_seen", frac=0.5, seed=0):
    T, truth = w["tests"][headline]
    (Ap, yp, sp), (Ar, yr, _) = _split(w["train"], frac)
    keep = _feed(Selective(kind, w["dims"], cap, seed=seed, recipe=recipe), Ap, yp)
    rr = lambda arm: recoverability(arm, Ap, yp, 0.1, np.random.default_rng(seed + 1), signal=sp)
    h_keep = rr(keep)
    swap = im_rate(w["dims"], Ap, yp, h_keep["HR2"], rr, seed + 3)          # dict incl. B and HR2
    from .arms import RandomMerge
    swap_arm = _feed(RandomMerge(w["dims"], swap["B"], seed=seed + 3), Ap, yp)
    neg = _feed(Selective(kind, w["dims"], cap, seed=seed + 1, recipe=recipe), Ap, yp)
    h_neg = rr(neg)
    for arm in (keep, swap_arm, neg):
        _feed(arm, Ar, yr)
    acs = {k: AC(a.predict(T), truth, 1.0) for k, a in (("KEEP", keep), ("SWAP", swap_arm), ("NEG", neg))}
    return dict(AC=acs, gap=acs["KEEP"] - acs["SWAP"], neg_gap=acs["KEEP"] - acs["NEG"], HR2_keep=h_keep["HR2"],
                HR2_swap=swap["HR2"], HR2_neg=h_neg["HR2"], B_swap=swap["B"], n_prefix=len(yp), n_rest=len(yr),
                bytes=dict(KEEP=keep.meter.peak_persistent, SWAP=swap_arm.meter.peak_persistent))


def positive_control(seeds=range(9_350_000, 9_350_004), frac=0.9):
    """Planted F2-L2 lowrank worlds with a SHORT remainder (10% of the life after t*)."""
    from .families import make_world
    rows = []
    for sd in seeds:
        w = make_world("F2_latent", "L2", sd, gen="lowrank")
        rows.append(run(w, "lowrank", 432, frac=frac, seed=sd))
    return dict(rows=rows, median_gap=float(np.median([r["gap"] for r in rows])),
                median_neg_gap=float(np.median([abs(r["neg_gap"]) for r in rows])))
