"""Growth-class battery — the calibrated classifier from PARADIGM-P21, lifted
into an importable module because Campaign X needs it as a real dependency.

Provenance: calibrated over a four-run mechanism-diagnosed arc against ten
labeled OEIS anchors (see aporia/paradigms/PARADIGM_P21_curated_corpus_sweep.md
and paradigm_p21_results.json — final state SWEEP-CALIBRATES, 12/12 including
two decline legs). Nothing here is re-tuned; re-tuning would void that
calibration.

Consumer: aporia/search/build_blinded_benchmark.py, which needs growth class to
build NEGATIVE pairs matched on growth so that a retrieval win cannot be
explained by "the right answer was the only one of that size."

Classes: POLY | EXP | SUPEREXP | ABSTAIN. Abstention is a first-class verdict.
"""
from __future__ import annotations

import numpy as np


def growth_class(vals, max_terms: int = 60, window: int = 40):
    """Return (class, diagnostics) for a sequence of positive-ish integers."""
    pairs = [(i + 1, x) for i, x in enumerate(vals[:max_terms]) if x > 0]
    if len(pairs) < 15:
        return "ABSTAIN", {"reason": "too short"}
    if len(pairs) > window:
        pairs = pairs[-window:]              # trailing window, ORIGINAL indices kept
    n = np.array([i for i, _ in pairs], dtype=float)
    ln = np.log(np.array([float(x) for _, x in pairs], dtype=float))

    A = np.vstack([np.log(n), np.ones_like(n)]).T
    coef_p, res_p = np.linalg.lstsq(A, ln, rcond=None)[:2]
    r2_p = 1 - float(res_p[0]) / max(float(np.sum((ln - ln.mean()) ** 2)), 1e-300) if len(res_p) else 1.0

    B = np.vstack([n, np.log(n), np.ones_like(n)]).T      # exp WITH log-poly correction
    sol_e = np.linalg.lstsq(B, ln, rcond=None)
    coef_e = sol_e[0]
    fit_e = B @ coef_e
    r2_e = 1 - float(np.sum((ln - fit_e) ** 2)) / max(float(np.sum((ln - ln.mean()) ** 2)), 1e-300)

    ratios = np.diff(ln)
    k = np.arange(1, len(ratios) + 1, dtype=float)
    C = np.vstack([np.log(k), np.ones_like(k)]).T
    coef_s, res_s = np.linalg.lstsq(C, ratios, rcond=None)[:2]
    r2_s = 1 - float(res_s[0]) / max(float(np.sum((ratios - ratios.mean()) ** 2)), 1e-300) if len(res_s) else 1.0

    half = len(n) // 2                        # b-stability across window halves
    def _b(nn, ll):
        M = np.vstack([nn, np.log(nn), np.ones_like(nn)]).T
        return float(np.linalg.lstsq(M, ll, rcond=None)[0][0])
    if half >= 4:
        b1, b2 = _b(n[:half], ln[:half]), _b(n[half:], ln[half:])
        b_stable = (abs(b1) > 1e-12 and 0.8 < b2 / b1 < 1.25)
    else:
        b_stable = False

    diag = {"poly_slope": round(float(coef_p[0]), 3), "r2_poly": round(r2_p, 5),
            "exp_slope": round(float(coef_e[0]), 4), "r2_exp": round(r2_e, 5),
            "superexp_r2": round(r2_s, 5)}
    if r2_s > 0.98 and coef_s[0] > 0.5:
        return "SUPEREXP", diag
    if r2_e > 0.9995 and coef_e[0] > 0.05 and b_stable:
        return "EXP", diag
    if r2_p > 0.999 and abs(coef_e[0]) < 0.05:
        return "POLY", diag
    return "ABSTAIN", diag
