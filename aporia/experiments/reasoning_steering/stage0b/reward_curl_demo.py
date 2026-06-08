"""Path B: curl explains 'combined reward < random while single heads work'.

The substrate's memory records that a linearly-COMBINED reward scored WORSE than random
while a single head (PRM v0) worked (+22pp). The hypothesis: that is the fingerprint of
CURL among the heads -- when evaluators are non-weightably (cyclically) related, averaging
them DILUTES / cancels the informative signal, so the linear combination can rank worse
than the best single head and even worse than random. A scalar combination provably
cannot order non-transitive preferences.

The original head-score data was never persisted, so we cannot test that SPECIFIC failure
here. Instead we establish the LAW with the validated instrument: as evaluator-set curl
rises, combined-ranking quality falls below best-single (and toward/below random), and the
instrument's non_gradient_mass tracks the damage. This gives the substrate a diagnostic:
when combined reward underperforms the best single head, MEASURE the curl -- high curl
means the heads are non-weightable and scalar combination is lossy -> use vector rewards
or select the best-aligned head, do not average.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from aporia.experiments.reasoning_steering.stage0.hodge import hodge_decompose
from aporia.experiments.reasoning_steering.stage0b.flow import relational_flow

__all__ = ["make_reward_scenario", "ranking_qualities", "curl_of", "sweep_curl_vs_combination"]


def make_reward_scenario(n: int, k_cyclic: int, cyclic_weight: float, noise: float, seed: int):
    """A reward scenario over n candidates with a true quality q_i = i/n.

    One INFORMATIVE head ~ q + noise; k_cyclic heads = rotational (ring) scores scaled by
    cyclic_weight -- collectively cyclic (induce curl) and, when averaged, cancel/dilute
    the informative signal. Returns (records[{margins}], q).
    """
    rng = np.random.default_rng(seed)
    q = [i / (n - 1) for i in range(n)]
    records = []
    offsets = [round(k * n / max(k_cyclic, 1)) % n for k in range(k_cyclic)]
    for i in range(n):
        margins = {"informative": q[i] + float(rng.normal(0, noise))}
        for k, off in enumerate(offsets):
            margins[f"cyc{k}"] = cyclic_weight * float(-((i - off) % n))
        records.append({"label": f"c{i}", "margins": margins, "q": q[i]})
    return records, q


def ranking_qualities(records, q) -> dict:
    """Spearman-with-q of: the best single head, and the mean-combined score.
    (random baseline ~ 0)."""
    names = sorted(records[0]["margins"])
    best_single = 0.0
    for nm in names:
        col = [r["margins"][nm] for r in records]
        rho = spearmanr(col, q).statistic
        if rho is not None and np.isfinite(rho):
            best_single = max(best_single, abs(float(rho)))
    combined = [float(np.mean(list(r["margins"].values()))) for r in records]
    rho_c = spearmanr(combined, q).statistic
    combined_q = float(rho_c) if (rho_c is not None and np.isfinite(rho_c)) else 0.0
    return {"best_single": best_single, "combined": combined_q}


def curl_of(records) -> float:
    G, flow = relational_flow([r["margins"] for r in records])
    return hodge_decompose(G, flow).non_gradient_mass


def sweep_curl_vs_combination(n=40, k_cyclic=4, noise=0.05, seed=0, weights=None):
    """Sweep cyclic_weight; return rows (weight, curl, best_single, combined)."""
    if weights is None:
        weights = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]
    rows = []
    for w in weights:
        recs, q = make_reward_scenario(n, k_cyclic, w, noise, seed)
        rows.append({"cyclic_weight": w, "curl": curl_of(recs), **ranking_qualities(recs, q)})
    return rows
