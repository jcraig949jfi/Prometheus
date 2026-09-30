"""Spec criteria as written (readings in NOTES.md)."""
import numpy as np
from scipy.stats import wilcoxon


def success(arm_r, null_r, pos_mean):
    arm_r = np.asarray(arm_r); null_r = np.asarray(null_r)
    m, mn = float(arm_r.mean()), float(null_r.mean())
    d = arm_r - null_r
    if np.all(d == 0):
        p = 1.0
    else:
        p = float(wilcoxon(arm_r, null_r, alternative="greater", method="exact"
                           if np.count_nonzero(d) == len(d) else "auto").pvalue)
    clauses = {"mean_ge_0.5": m >= 0.5, "minus_null_ge_0.3": (m - mn) >= 0.3,
               "wilcoxon_p_lt_0.01": p < 0.01, "poscontrol_mean_ge_0.7": pos_mean >= 0.7}
    return all(clauses.values()), {"mean_r": m, "null_mean_r": mn, "diff": m - mn,
                                   "wilcoxon_p": p, "clauses": clauses}


def failure(arm_mean, null_mean, pos_mean):
    return (arm_mean - null_mean) < 0.1 or pos_mean < 0.5


def null_twin_meets(null_r):
    return float(np.mean(null_r)) >= 0.5
