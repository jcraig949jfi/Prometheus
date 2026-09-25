"""Information-theoretic measurement with honest nulls.

Why this exists as a shared component rather than inside one experiment:

  Mutual information is BIASED UPWARD on small samples. With 120 observations,
  4 classes and a handful of distinct patterns, a raw MI reads comfortably above
  zero on data with no relationship whatsoever. Reporting that as "conditionality"
  would manufacture coalitions exactly as e02's gain detector manufactured ratchets
  from noise (CW01-D022) -- a detector that fires on nothing will find the
  phenomenon everywhere.

  So MI is never reported alone here. `mi_with_null` shuffles the labels, builds
  the null distribution of MI under no relationship, and reports the excess over
  that null's high quantile. The bias is measured rather than assumed away.

Expected reuse: e03 (coalitions), e06 (representation ecology), e09 (algorithmic
soup) -- anywhere "does X depend on Y" needs an answer that survives a null.
"""
from __future__ import annotations

import numpy as np


def entropy_bits(labels):
    """Shannon entropy of a discrete sequence, in bits."""
    if len(labels) == 0:
        return 0.0
    _, counts = np.unique(np.asarray(labels), return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def mutual_information_bits(x, y):
    """Discrete MI I(X;Y) in bits, from the empirical joint."""
    x = np.asarray(x)
    y = np.asarray(y)
    if len(x) == 0 or len(x) != len(y):
        return 0.0
    xs, xi = np.unique(x, return_inverse=True)
    ys, yi = np.unique(y, return_inverse=True)
    if len(xs) < 2 or len(ys) < 2:
        return 0.0                      # no variation -> no information
    joint = np.zeros((len(xs), len(ys)), dtype=float)
    np.add.at(joint, (xi, yi), 1.0)
    joint /= joint.sum()
    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = joint * np.log2(joint / (px * py))
    return float(np.nansum(np.where(joint > 0, term, 0.0)))


def mi_with_null(x, y, n_shuffles=200, seed=0, quantile=99.0):
    """MI against a shuffled-label null. The ONLY sanctioned way to report MI here.

    Returns the raw MI, the null distribution's centre and high quantile, the
    excess over that quantile, and a boolean `significant`. A positive raw MI that
    does not clear the null is NOT evidence of dependence -- it is the small-sample
    bias being read as signal.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    mi = mutual_information_bits(x, y)
    rng = np.random.Generator(np.random.PCG64(seed))
    yy = np.array(y, copy=True)
    null = np.empty(n_shuffles, dtype=float)
    for i in range(n_shuffles):
        rng.shuffle(yy)
        null[i] = mutual_information_bits(x, yy)
    q = float(np.percentile(null, quantile))
    return {
        "mi_bits": mi,
        "null_mean": float(null.mean()),
        "null_p50": float(np.percentile(null, 50)),
        "null_q": q,
        "quantile": quantile,
        "excess_bits": mi - q,
        "significant": bool(mi > q),
        "n": int(len(x)),
        "n_shuffles": int(n_shuffles),
        "_caveat": "a raw MI above zero proves nothing at this sample size; only the excess over the "
                   "shuffled null does",
    }


def normalised_mi(x, y):
    """I(X;Y) / H(X), the fraction of the label's entropy explained. 0 when H(X)=0."""
    hx = entropy_bits(x)
    return (mutual_information_bits(x, y) / hx) if hx > 0 else 0.0


# ---------------------------------------------------------------- effect nulls
#
# CW01-D035, the third member of one family. All three are conditions satisfiable
# in the ABSENCE of the phenomenon:
#   D022  a gain detector with no noise floor fired on pure noise
#   D034  a matched-arms check passed with info=0.0 -- nothing happened
#   D035  an intervention verdict tested DIRECTION but not MAGNITUDE
#
# e04's decisive intervention was recorded as (scramble < sham), a bare sign test.
# It reported 4/4. Measuring the sham against ITSELF across independent seed blocks
# gives the null for an intervention that does nothing; one replicate's -3.27% sat
# inside [-6.69, +7.17] and the claim was really 3/4.
#
# An effect claim must name its null and clear it.


def sham_null(sham_estimates):
    """Null distribution for 'an intervention that does nothing'.

    sham_estimates: independent estimates of the SAME cost-matched sham, one per
    seed block. Their pairwise relative differences are the run-to-run noise in the
    score estimate -- exactly what an inert intervention would produce.
    """
    import numpy as np
    s = np.asarray(sham_estimates, dtype=float)
    if len(s) < 3:
        raise ValueError("need at least 3 independent sham estimates to form a null")
    null = np.array([100.0 * (s[i] - s[j]) / s[j]
                     for i in range(len(s)) for j in range(len(s)) if i != j])
    return {"null": null, "p05": float(np.percentile(null, 5)),
            "p50": float(np.percentile(null, 50)), "p95": float(np.percentile(null, 95)),
            "n_blocks": int(len(s))}


def effect_clears_null(effect_pct, sham_estimates, direction="negative"):
    """Does an intervention effect exceed the noise floor, in the expected direction?

    direction 'negative' expects the intervention to HURT (effect below p05);
    'positive' expects it to help (above p95). Returns a verdict dict; `clears`
    false means the effect is indistinguishable from doing nothing.
    """
    n = sham_null(sham_estimates)
    if direction == "negative":
        clears = effect_pct < n["p05"]
        bound = n["p05"]
    else:
        clears = effect_pct > n["p95"]
        bound = n["p95"]
    return {"clears": bool(clears), "effect_pct": float(effect_pct), "direction": direction,
            "bound": bound, "null_p05": n["p05"], "null_p95": n["p95"],
            "n_blocks": n["n_blocks"],
            "verdict": ("CLEARS the noise floor" if clears else "INSIDE NOISE - proves nothing"),
            "_caveat": "a sign test is safe only when the margin is enormous; measure the floor"}
