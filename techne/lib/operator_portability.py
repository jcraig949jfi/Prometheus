"""TOOL_OPERATOR_PORTABILITY - cross-region operator-portability falsification
orchestrator (REQ-028).

Sits at the orchestrator layer above REQ-027 (``tt_splice``). Given two region
tensors and (optionally) an operator to apply to the source, it asks: *does the
operator carry region A onto region B's structure beyond what a structure-
destroying null produces?* It composes:

  operator application  ->  prime-detrend control (PATTERN_PRIME_GRAVITATIONAL_
  OVERFIT)  ->  REQ-027 column-subspace bond-rank score  ->  matched null
  distribution  ->  z / permutation-p  ->  survived / killed / inconclusive
  verdict  ->  pattern-flag audit.

Output contract (frozen):
    {
      "effect_size": float,         # z = (obs - null_mean) / null_std
      "p_perm": float,              # one-sided perm p, (#null>=obs + 1)/(n+1)
      "bond_rank_delta": float,     # mean over axes of (rank_a + rank_b - rank_joint)
      "replication_status": "survived" | "killed" | "inconclusive",
      "pattern_flags": list[str],
      "audit": dict,
    }

The axis matters (and is the reason this tool exists in this form)
-----------------------------------------------------------------
The REQ-027 bond-rank statistic measures COLUMN-subspace overlap and is EXACTLY
invariant to row permutation (see test_row_permutation_invariance). Therefore
the F011 / F010 block-shuffle-WITHIN-CONDUCTOR discipline -- which destroys ROW
pairing (harmonia/audit_P028_block_shuffle.py: plain z=+2.38 "endorsed" ->
conductor-block z=-0.86 "killed") -- does NOT apply to this statistic: a
conductor-stratified row-shuffle would leave the score unchanged and report
z~=0 for everything. The discriminating nulls here act on the FEATURE/value
axis. ``null_model='row_permutation'`` (or any row-axis request) is rejected so
that the degenerate null can never be dressed up as a passed falsification.

The 1-D gap-variance F011 statistic, where conductor IS the live confound and
block-shuffle-within-conductor IS the correct null, is a SEPARATE row-pairing
measurement owned by the Charon/Harmonia DB scripts and is out of scope here.

Forged: 2026-06-15 | Tier: 1 | REQ-028
"""
from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np

from techne.lib.tt_splice import (
    splice_score_arrays,
    prime_detrend_arrays,
    _load_npz_tensor,
    _shape_pair,
    PATTERN_WARNING,
)

_VALID_NULLS = ("matched_GUE", "permutation", "block_shuffle")
_DEFAULT_SEED = 20260417


# --------------------------------------------------------------------------
# input resolution / validation
# --------------------------------------------------------------------------
def _resolve(source) -> np.ndarray:
    if isinstance(source, (str, Path)):
        return _load_npz_tensor(Path(source))
    arr = np.asarray(source, dtype=float)
    if arr.ndim < 2:
        raise ValueError(f"tensor must have ndim >= 2 for bond ranks, got shape {arr.shape}")
    if arr.shape[0] < 2 or arr.shape[1] < 1:
        raise ValueError(f"tensor too small to splice: shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("tensor contains NaN or infinite values")
    return arr


def _apply_operator(a: np.ndarray, operator_spec):
    if operator_spec is None:
        return a, {"operator": "identity"}
    if isinstance(operator_spec, str):
        raise NotImplementedError(
            f"operator_spec={operator_spec!r}: symbol@version registry resolution is "
            "out of scope for the standalone REQ-028 tool; pass a callable "
            "ndarray->ndarray instead."
        )
    if callable(operator_spec):
        out = np.asarray(operator_spec(a), dtype=float)
        if out.ndim < 2:
            raise ValueError("operator must return a tensor with ndim >= 2")
        if not np.all(np.isfinite(out)):
            raise ValueError("operator produced NaN or infinite values")
        return out, {"operator": "callable"}
    raise TypeError("operator_spec must be None, a callable, or a 'symbol@version' string")


# --------------------------------------------------------------------------
# null generators (all act on the FEATURE / value axis the statistic sees)
# --------------------------------------------------------------------------
def _null_matched_gue(b: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Scale-matched Gaussian: per-column (mean, std) of B preserved, all
    structure destroyed. NOTE: matched to the second moment, NOT a full
    eigenvalue-matched GUE ensemble -- it is the structure-free reference null."""
    return rng.standard_normal(b.shape) * b.std(axis=0, keepdims=True) + b.mean(axis=0, keepdims=True)


def _null_column_permutation(b: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Liberal null: permute whole columns (breaks inter-feature structure,
    preserves each feature's exact marginal)."""
    return b[:, rng.permutation(b.shape[1])]


def _null_block_shuffle(b: np.ndarray, rng: np.random.Generator, strata: np.ndarray) -> np.ndarray:
    """Conservative null: permute columns only WITHIN each feature stratum,
    preserving within-stratum structure. Analogue of F010's block-shuffle on the
    axis this statistic actually sees."""
    out = b.copy()
    for g in np.unique(strata):
        cols = np.where(strata == g)[0]
        out[:, cols] = b[:, cols[rng.permutation(cols.size)]]
    return out


# --------------------------------------------------------------------------
# main entry
# --------------------------------------------------------------------------
def operator_portability_test(
    source_a,
    source_b,
    operator_spec=None,
    null_model: str = "matched_GUE",
    detrend_primes: bool = True,
    feature_strata=None,
    n_perms: int = 300,
    seed: int = _DEFAULT_SEED,
    survive_z: float = 3.0,
    survive_p: float = 0.01,
    stratify_conductor: bool = True,
    conductor=None,
) -> dict:
    """Test whether ``operator_spec`` makes region A portable onto region B.

    Parameters
    ----------
    source_a, source_b : ndarray (ndim>=2) or path to an NPZ tensor.
    operator_spec : None (identity) | callable(ndarray)->ndarray |
        'symbol@version' str (raises NotImplementedError -- registry out of scope).
    null_model : 'matched_GUE' (default, most conservative) | 'permutation'
        (column permutation, liberal) | 'block_shuffle' (within feature_strata,
        conservative). Row-axis requests are rejected (see module docstring).
    feature_strata : per-column group labels (len == n_features). Required for
        null_model='block_shuffle'.
    conductor / stratify_conductor : accepted for interface fidelity with the
        REQ-028 spec. Conductor is a ROW-level label and is ORTHOGONAL to this
        column-subspace statistic; if supplied it is recorded and flagged, never
        used to stratify (a row-stratified null is degenerate here).
    """
    if null_model not in _VALID_NULLS:
        if "row" in null_model.lower():
            raise ValueError(
                f"null_model={null_model!r}: row-axis nulls are degenerate for the "
                "column-subspace bond-rank statistic (it is row-permutation "
                "invariant). Use 'matched_GUE', 'permutation', or 'block_shuffle'."
            )
        raise ValueError(f"unknown null_model={null_model!r}; valid: {_VALID_NULLS}")
    if n_perms <= 0:
        raise ValueError("n_perms must be positive (a null is required to falsify)")

    a_raw = _resolve(source_a)
    b_raw = _resolve(source_b)
    a_op, operator_audit = _apply_operator(a_raw, operator_spec)

    flags: list[str] = []

    # prime-detrend control --------------------------------------------------
    if detrend_primes:
        a_w, b_w, detrend_audit = prime_detrend_arrays(a_op, b_raw)
        flags.append("PATTERN_PRIME_GRAVITATIONAL_OVERFIT:detrended")
    else:
        warnings.warn(PATTERN_WARNING, RuntimeWarning, stacklevel=2)
        a_w, b_w = _shape_pair(np.asarray(a_op, float), np.asarray(b_raw, float))
        detrend_audit = {}
        flags.append("PATTERN_PRIME_GRAVITATIONAL_OVERFIT:NOT_DETRENDED")

    n_features = b_w.shape[1]

    # resolve block-shuffle strata before doing expensive work ----------------
    strata = None
    if null_model == "block_shuffle":
        if feature_strata is None:
            raise ValueError(
                "null_model='block_shuffle' requires feature_strata (per-column "
                "group labels); refusing to silently fall back to a weaker null."
            )
        strata = np.asarray(feature_strata)
        if strata.shape[0] != n_features:
            raise ValueError(
                f"feature_strata length {strata.shape[0]} != n_features {n_features}"
            )

    # observed effect (composition with the REQ-027 kernel) ------------------
    obs_score, joint_ranks, detail = splice_score_arrays(a_w, b_w)
    ranks_a = detail["independent_bond_ranks_a"]
    ranks_b = detail["independent_bond_ranks_b"]
    bond_rank_delta = float(
        np.mean([ra + rb - rj for ra, rb, rj in zip(ranks_a, ranks_b, joint_ranks)])
    )

    # null distribution ------------------------------------------------------
    rng = np.random.default_rng(seed)
    null_scores = np.empty(n_perms, dtype=float)
    for i in range(n_perms):
        if null_model == "matched_GUE":
            b_null = _null_matched_gue(b_w, rng)
        elif null_model == "permutation":
            b_null = _null_column_permutation(b_w, rng)
        else:  # block_shuffle
            b_null = _null_block_shuffle(b_w, rng, strata)
        null_scores[i], _, _ = splice_score_arrays(a_w, b_null)

    null_mean = float(null_scores.mean())
    null_std = float(null_scores.std())
    p_perm = float((np.count_nonzero(null_scores >= obs_score) + 1) / (n_perms + 1))
    effect_size = float((obs_score - null_mean) / null_std) if null_std > 0 else float("nan")

    # null-model flags -------------------------------------------------------
    flags.append(f"NULL_MODEL:{null_model}")
    if null_model == "permutation":
        flags.append("WEAK_NULL:column_permutation_liberal")
    elif null_model == "block_shuffle":
        flags.append("NULL_STRATIFIED:feature_strata")
    if conductor is not None:
        flags.append("PATTERN_CONDUCTOR_CONFOUND:row_level_orthogonal_to_bondrank")

    # verdict ----------------------------------------------------------------
    if null_std <= 0.0:
        status = "inconclusive"
        flags.append("DEGENERATE_NULL:zero_variance")
    elif n_perms < 30:
        status = "inconclusive"
        flags.append("UNDERPOWERED:n_perms_lt_30")
    elif effect_size >= survive_z and p_perm <= survive_p:
        status = "survived"
    else:
        status = "killed"

    return {
        "effect_size": effect_size,
        "p_perm": p_perm,
        "bond_rank_delta": bond_rank_delta,
        "replication_status": status,
        "pattern_flags": flags,
        "audit": {
            "observed_compatibility_score": obs_score,
            "null_model": null_model,
            "null_mean": null_mean,
            "null_std": null_std,
            "n_perms": int(n_perms),
            "seed": int(seed),
            "survive_z": survive_z,
            "survive_p": survive_p,
            "independent_bond_ranks_a": ranks_a,
            "independent_bond_ranks_b": ranks_b,
            "joint_bond_ranks": [int(r) for r in joint_ranks],
            "rank_compression_score": detail.get("rank_compression_score"),
            "subspace_alignment_score": detail.get("subspace_alignment_score"),
            "identity_splice": detail.get("identity_splice", False),
            "detrend_primes": bool(detrend_primes),
            "prime_detrend_audit": detrend_audit,
            "operator": operator_audit["operator"],
            "stratify_conductor_requested": bool(stratify_conductor),
            "conductor_supplied": conductor is not None,
            "conductor_note": (
                "row-level conductor is orthogonal to the column-subspace "
                "statistic; not used for stratification"
            ),
        },
    }


__all__ = ["operator_portability_test"]
