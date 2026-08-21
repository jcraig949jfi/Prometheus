"""Tensor-train ranks with the correct null baked into the API.

Wraps quimb's MatrixProductState.from_dense (Standing Order #1: quimb owns the SVD sweep; this
module owns the substrate-facing contract). TT bond rank at cut k equals the matrix rank of
the k-th unfolding — it measures CROSS-AXIS COUPLING, which is why the tensor-first program
cares: low observed rank vs a coupling-destroyed null = structure.

THE NULL IS PART OF THE API, deliberately (feedback_null_must_perturb_the_statistics_axis,
REQ-028): permuting whole slices along an axis is a relabeling and provably rank-invariant —
the tempting-but-degenerate row-null. The only null this module offers is `fiber_shuffle`:
independently permute entries within each fiber along the last axis, preserving per-fiber
value multisets while destroying cross-axis alignment. A property test in the suite proves the
degenerate null's invariance, so the design decision is documented by a theorem, not a comment.

Tests (written first): prometheus_math/tests/test_tensor_train.py.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

__all__ = [
    "tt_ranks",
    "tt_reconstruct",
    "tt_rank_null_test",
    "signature_occupancy_tensor",
]


def _validate(tensor: np.ndarray, cutoff: float) -> np.ndarray:
    t = np.asarray(tensor, dtype=float)
    if t.ndim < 2:
        raise ValueError(f"TT ranks need ndim >= 2, got ndim={t.ndim}")
    if not np.isfinite(t).all():
        raise ValueError("tensor contains NaN or inf")
    if cutoff < 0:
        raise ValueError(f"cutoff must be >= 0, got {cutoff}")
    if not t.any():
        raise ValueError("zero tensor: TT rank is undefined; refusing to fabricate one")
    return t


def _mps(t: np.ndarray, cutoff: float):
    import quimb.tensor as qtn

    return qtn.MatrixProductState.from_dense(t.reshape(-1), dims=t.shape, cutoff=cutoff)


def tt_ranks(tensor: np.ndarray, cutoff: float = 1e-10) -> List[int]:
    """TT bond ranks at each of the ndim-1 cuts, at relative truncation `cutoff`."""
    t = _validate(tensor, cutoff)
    return [int(b) for b in _mps(t, cutoff).bond_sizes()]


def tt_reconstruct(tensor: np.ndarray, cutoff: float = 1e-10) -> np.ndarray:
    """Round-trip through the TT at `cutoff` — the reconstruction the ranks certify."""
    t = _validate(tensor, cutoff)
    dense = np.asarray(_mps(t, cutoff).to_dense()).reshape(t.shape)
    return dense


def _fiber_shuffle(t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """The correct null: independently permute each fiber along the LAST axis. Preserves every
    fiber's value multiset (and hence all axis-(-1) marginals); destroys alignment across the
    other axes — exactly the coupling the rank statistic varies on."""
    flat = t.reshape(-1, t.shape[-1]).copy()
    for row in flat:
        rng.shuffle(row)
    return flat.reshape(t.shape)


def tt_rank_null_test(
    tensor: np.ndarray,
    cutoff: float = 1e-6,
    n_null: int = 100,
    seed: int = 0,
) -> Dict[str, Any]:
    """Observed TT ranks vs the fiber-shuffle null.

    Statistic: total bond rank (sum over cuts). Structure = coupling = LOW rank relative to
    the null, so `percentile` is the fraction of null samples with total rank <= observed —
    small percentile means the observed coupling is real.

    Returns observed ranks, null mean/sd, percentile, and `one_null_sample` (a shuffled
    tensor) so calibration checks can re-run the test on a structure-destroyed input.
    """
    t = _validate(tensor, cutoff)
    if n_null < 10:
        raise ValueError(f"n_null must be >= 10 for a usable percentile, got {n_null}")
    rng = np.random.default_rng(seed)
    observed = tt_ranks(t, cutoff)
    obs_total = sum(observed)
    null_totals = []
    sample = None
    for i in range(n_null):
        shuffled = _fiber_shuffle(t, rng)
        if sample is None:
            sample = shuffled
        null_totals.append(sum(tt_ranks(shuffled, cutoff)))
    null_arr = np.array(null_totals, dtype=float)
    return {
        "observed_ranks": observed,
        "observed_total": obs_total,
        "null": "fiber_shuffle",
        "null_mean": float(null_arr.mean()),
        "null_sd": float(null_arr.std(ddof=1)),
        "percentile": float((null_arr <= obs_total).mean()),
        "n_null": n_null,
        "cutoff": cutoff,
        "one_null_sample": sample,
    }


def signature_occupancy_tensor(
    db_path: Path | str,
) -> Tuple[np.ndarray, Dict[str, List[str]]]:
    """The Theseus signature_index ledger as an occupancy tensor.

    Axes (in order): generator_id x claim_kind x verdict_class; entries are seen-class counts
    (each ledger row is one signature class). This is the proto-tensor of the tensor-first
    program, loaded with its provenance intact: axis vocabularies are returned alongside so
    no downstream consumer has to re-derive them.
    """
    con = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT generator_id, claim_kind, verdict_class FROM signatures"
        ).fetchall()
    finally:
        con.close()
    if not rows:
        raise ValueError(f"no rows in signature_index at {db_path}")
    axes: Dict[str, List[str]] = {
        "generator_id": sorted({r[0] for r in rows}),
        "claim_kind": sorted({r[1] for r in rows}),
        "verdict_class": sorted({r[2] for r in rows}),
    }
    index = {
        name: {v: i for i, v in enumerate(vals)} for name, vals in axes.items()
    }
    t = np.zeros(
        (len(axes["generator_id"]), len(axes["claim_kind"]), len(axes["verdict_class"]))
    )
    for g, k, v in rows:
        t[index["generator_id"][g], index["claim_kind"][k], index["verdict_class"][v]] += 1
    return t, axes
