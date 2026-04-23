"""Descriptor correlation diagnostic.

If two descriptors correlate above 0.9 across the population of evaluations,
the MAP-Elites grid that uses both of them is effectively 1-dimensional in
those axes. The archive looks rich but is collapsed.

This is the safety check on James's warning: avoid building a misleading
coordinate system where (rank, log_params, log_error, spectral_decay)
collapse into a single direction wearing four costumes.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np

from ..map_elites.grid import Archive


def _column_vectors(archive: Archive) -> dict[str, np.ndarray]:
    if not archive.history:
        return {}
    avg_rank = np.array([float(np.mean(e.ranks)) for e in archive.history])
    log_params = np.log10(np.maximum(1.0, [e.n_params for e in archive.history]))
    log_error = np.log10(np.maximum(1e-15, [e.rel_error for e in archive.history]))
    return {"avg_rank": avg_rank, "log_params": log_params, "log_error": log_error}


def correlation_audit(archive: Archive, threshold: float = 0.9,
                      function_level_descriptors: dict[str, float] | None = None) -> dict:
    """Pairwise Pearson correlation across in-archive descriptors.

    `function_level_descriptors` (e.g., {"spectral_alpha": 1.83}) are constants
    for this archive (one function), so they cannot be correlated within the
    archive — they are recorded separately and used in cross-archive analysis.
    """
    cols = _column_vectors(archive)
    if not cols or len(next(iter(cols.values()))) < 3:
        return {"matrix": {}, "flagged": [],
                "warning": "insufficient evaluations for correlation",
                "function_level_descriptors": function_level_descriptors or {}}

    keys = list(cols)
    matrix: dict[str, float] = {}
    flagged: list[dict] = []
    for a, b in combinations(keys, 2):
        x, y = cols[a], cols[b]
        if x.std() == 0 or y.std() == 0:
            r = 0.0
        else:
            r = float(np.corrcoef(x, y)[0, 1])
        matrix[f"{a}|{b}"] = r
        if abs(r) >= threshold:
            flagged.append({
                "pair": [a, b],
                "correlation": r,
                "implication": "axes may be collapsed; consider re-scaling or new descriptor",
            })

    warning = None
    if flagged:
        warning = (
            f"{len(flagged)} descriptor pair(s) above |r|={threshold} — "
            "MAP-Elites coordinate system at risk of dimensional collapse"
        )

    return {
        "matrix": matrix,
        "flagged": flagged,
        "threshold": threshold,
        "warning": warning,
        "function_level_descriptors": function_level_descriptors or {},
    }


def cross_function_audit(archives: dict[str, Archive],
                         function_descriptors: dict[str, dict]) -> dict:
    """Across functions, correlate function-level descriptors (e.g.,
    spectral_alpha) with archive-level summaries (min_error, pareto_size).
    Reveals whether the intrinsic axis predicts the empirical compressibility.
    """
    rows: list[dict] = []
    for label, arc in archives.items():
        s = arc.summary()
        fd = function_descriptors.get(label, {})
        rows.append({
            "function": label,
            "spectral_alpha": fd.get("spectral_alpha"),
            "min_error": s.get("min_error"),
            "pareto_size": s.get("pareto_front_size"),
            "min_params": s.get("min_params"),
        })

    # Correlate spectral_alpha vs log10(min_error) across functions
    valid = [r for r in rows
             if r["spectral_alpha"] is not None and r["min_error"] is not None
             and np.isfinite(r["spectral_alpha"]) and r["min_error"] > 0]
    if len(valid) >= 3:
        a = np.array([r["spectral_alpha"] for r in valid])
        e = np.log10([r["min_error"] for r in valid])
        if a.std() > 0 and e.std() > 0:
            corr = float(np.corrcoef(a, e)[0, 1])
        else:
            corr = 0.0
    else:
        corr = None

    return {
        "rows": rows,
        "spectral_alpha_vs_log_min_error": corr,
        "n_functions_with_valid_alpha": len(valid),
        "interpretation": (
            "expected sign: negative (high alpha = fast spectral decay = lower achievable error)"
        ),
    }
