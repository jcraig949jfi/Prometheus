"""prometheus_math.symbolic_tensor_decomp — canonical tensor decompositions.

First-class API for the three canonical decompositions used in
numerical multilinear algebra:

  * **CP (CANDECOMP/PARAFAC)** — sum of rank-1 outer products::

        T_{i_1...i_d} = Σ_r λ_r · u^{(1)}_{r, i_1} · ... · u^{(d)}_{r, i_d}

    Implemented via Alternating Least Squares (ALS).

  * **Tucker** — core tensor + factor matrices::

        T = G ×_1 U_1 ×_2 U_2 ... ×_d U_d

    Implemented via Higher-Order Orthogonal Iteration (HOOI), with SVD
    initialisation by default.

  * **Tensor-Train (TT)** — chain of 3-tensors with bond dimensions::

        T_{i_1...i_d} = G_1[:, i_1, :] · G_2[:, i_2, :] · ... · G_d[:, i_d, :]

    Implemented via successive SVD truncation of the unfoldings
    (the canonical Oseledets construction).

The numerical heavy-lifting is delegated to **tensorly**.  All inputs
are coerced to ``numpy.ndarray`` at the boundary, and all returned
factors / cores are plain ``numpy.ndarray`` objects (never ``tensorly``
tensor wrappers).

Forged: 2026-04-25 | Tier: 1 (tensorly) | REQ-PM-SYMBOLIC-TENSOR
Project #53 from techne/PROJECT_BACKLOG_1000.md.
"""
from __future__ import annotations

from typing import Optional, Sequence, Union

import numpy as np

from .registry import is_available

if not is_available("tensorly"):
    raise ImportError(
        "prometheus_math.symbolic_tensor_decomp requires tensorly "
        "(`pip install tensorly`)."
    )

import tensorly as tl  # noqa: E402
from tensorly.decomposition import (  # noqa: E402
    parafac,
    tucker as _tl_tucker,
    tensor_train as _tl_tensor_train,
)
from tensorly.cp_tensor import cp_to_tensor  # noqa: E402
from tensorly.tucker_tensor import tucker_to_tensor as _tucker_to_tensor  # noqa: E402
from tensorly.tt_tensor import tt_to_tensor as _tt_to_tensor  # noqa: E402

# Force the numpy backend regardless of TENSORLY_BACKEND env at import.
tl.set_backend("numpy")


# ---------------------------------------------------------------------------
# Coercion / validation helpers
# ---------------------------------------------------------------------------

def _as_numpy(tensor) -> np.ndarray:
    """Coerce input to a numpy.ndarray of dtype float64.

    Rejects bare scalars, lists-of-strings, etc.  Lists / tuples of
    numbers are accepted (per numpy's array constructor).
    """
    if tensor is None:
        raise ValueError("tensor input is None")
    if isinstance(tensor, (str, bytes)):
        raise ValueError("tensor input must be array-like, got string")
    try:
        arr = np.asarray(tensor, dtype=np.float64)
    except (TypeError, ValueError) as e:
        raise ValueError(f"cannot interpret input as a tensor: {e}")
    if arr.ndim == 0:
        raise ValueError("tensor must have ndim >= 1, got a scalar")
    if not np.all(np.isfinite(arr)):
        raise ValueError("tensor contains NaN or inf")
    return arr


def _check_tol(tol: float) -> None:
    if tol < 0:
        raise ValueError(f"tol must be >= 0, got {tol}")


def _check_max_iter(max_iter: int) -> None:
    if max_iter < 1:
        raise ValueError(f"max_iter must be >= 1, got {max_iter}")


def _frobenius(T: np.ndarray) -> float:
    return float(np.sqrt(np.sum(T * T)))


def _relative_fit_error(T: np.ndarray, T_hat: np.ndarray) -> float:
    """Relative Frobenius error  ||T - T_hat|| / ||T||  (or absolute if T == 0)."""
    num = float(np.linalg.norm((T - T_hat).ravel()))
    den = _frobenius(T)
    if den == 0.0:
        return num
    return num / den


# ---------------------------------------------------------------------------
# CP (CANDECOMP/PARAFAC)
# ---------------------------------------------------------------------------

def cp_decompose(
    tensor,
    rank: int,
    max_iter: int = 100,
    tol: float = 1e-9,
    init: str = "random",
    seed: Optional[int] = None,
) -> dict:
    """CP decomposition of an order-d tensor via ALS.

    T  ≈  Σ_{r=1..R} λ_r · u^{(1)}_r ⊗ u^{(2)}_r ⊗ ... ⊗ u^{(d)}_r

    Parameters
    ----------
    tensor : array-like
        Dense tensor of arbitrary order ≥ 1.
    rank : int
        Number of rank-1 components.  Must be ≥ 1 and ≤ T.size.
    max_iter : int
        Maximum ALS sweeps.
    tol : float
        Convergence tolerance on relative change in fit error.
    init : {"random", "svd"}
        Initialisation strategy passed to tensorly.
    seed : int, optional
        Numpy random seed for reproducibility (random init only).

    Returns
    -------
    dict with keys
        factors      : list[np.ndarray]   — each shape (n_k, rank)
        weights      : np.ndarray         — shape (rank,)
        rank         : int
        n_iter       : int                — number of ALS iterations run
        fit_error    : float              — relative Frobenius error
        converged    : bool               — whether fit_error decrease < tol

    Notes
    -----
    *1-D vectors* (order-1 tensors) are decomposed by an explicit
    rank-1 factorisation: ``λ = ||v||₂``, ``u = v / λ`` (or zeros if
    ``v == 0``).  ``rank > 1`` for a 1-D vector returns the same
    rank-1 factor padded with zeros, since any 1-D vector has CP rank
    at most 1.
    """
    T = _as_numpy(tensor)
    if not isinstance(rank, (int, np.integer)) or rank < 1:
        raise ValueError(f"rank must be a positive integer, got {rank!r}")
    if rank > T.size:
        raise ValueError(
            f"rank={rank} exceeds T.size={T.size}; CP rank cannot exceed it."
        )
    _check_tol(tol)
    _check_max_iter(max_iter)
    if init not in ("random", "svd"):
        raise ValueError(f"init must be 'random' or 'svd', got {init!r}")

    # Order-1 special case: tensorly's parafac doesn't handle 1D.
    if T.ndim == 1:
        norm = float(np.linalg.norm(T))
        if norm == 0.0:
            factor = np.zeros((T.size, rank), dtype=np.float64)
            weights = np.zeros(rank, dtype=np.float64)
        else:
            u = T / norm
            factor = np.zeros((T.size, rank), dtype=np.float64)
            factor[:, 0] = u
            weights = np.zeros(rank, dtype=np.float64)
            weights[0] = norm
        T_hat = cp_reconstruct([factor], weights)
        return {
            "factors": [factor],
            "weights": weights,
            "rank": rank,
            "n_iter": 0,
            "fit_error": _relative_fit_error(T, T_hat),
            "converged": True,
        }

    # All-zero tensor: tensorly's ALS can produce NaNs from 0/0 normalisation.
    if _frobenius(T) == 0.0:
        factors = [np.zeros((n, rank), dtype=np.float64) for n in T.shape]
        weights = np.zeros(rank, dtype=np.float64)
        return {
            "factors": factors,
            "weights": weights,
            "rank": rank,
            "n_iter": 0,
            "fit_error": 0.0,
            "converged": True,
        }

    if seed is not None:
        np.random.seed(int(seed))

    try:
        cp_tensor, errors = parafac(
            tl.tensor(T),
            rank=rank,
            n_iter_max=max_iter,
            tol=tol,
            init=init,
            random_state=seed,
            return_errors=True,
            normalize_factors=True,
        )
    except np.linalg.LinAlgError as e:
        # ALS gets a singular Khatri-Rao Gramian when rank is too high
        # for the tensor's geometry; surface as a clean ValueError.
        raise ValueError(
            f"CP-ALS failed: singular Gramian at rank={rank}. "
            "Try a smaller rank or different seed/init. "
            f"(Underlying: {e})"
        )
    weights = np.asarray(cp_tensor.weights, dtype=np.float64)
    factors = [np.asarray(f, dtype=np.float64) for f in cp_tensor.factors]

    n_iter = len(errors)
    converged = bool(
        n_iter >= 2 and abs(float(errors[-1]) - float(errors[-2])) < tol
    )
    T_hat = cp_reconstruct(factors, weights)
    return {
        "factors": factors,
        "weights": weights,
        "rank": int(rank),
        "n_iter": n_iter,
        "fit_error": _relative_fit_error(T, T_hat),
        "converged": converged,
    }


def cp_reconstruct(
    factors: Sequence[np.ndarray],
    weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Reconstruct a dense tensor from CP factors.

    T_{i_1...i_d} = Σ_r λ_r · ∏_k F^{(k)}_{i_k, r}
    """
    if not factors:
        raise ValueError("factors must be a non-empty sequence")
    factors = [np.asarray(f, dtype=np.float64) for f in factors]
    rank = factors[0].shape[1]
    for k, f in enumerate(factors):
        if f.ndim != 2:
            raise ValueError(f"factor {k} must be 2-D, got shape {f.shape}")
        if f.shape[1] != rank:
            raise ValueError(
                f"factor {k} has rank {f.shape[1]} but factor 0 has rank {rank}"
            )
    if weights is None:
        weights = np.ones(rank, dtype=np.float64)
    else:
        weights = np.asarray(weights, dtype=np.float64).reshape(-1)
        if weights.shape[0] != rank:
            raise ValueError(
                f"weights has length {weights.shape[0]} but rank is {rank}"
            )
    out = cp_to_tensor((weights, factors))
    return np.asarray(out, dtype=np.float64)


# ---------------------------------------------------------------------------
# Tucker
# ---------------------------------------------------------------------------

def tucker_decompose(
    tensor,
    ranks: Optional[Sequence[int]] = None,
    max_iter: int = 100,
    tol: float = 1e-9,
    init: str = "svd",
    seed: Optional[int] = None,
) -> dict:
    """Tucker decomposition via HOOI.

    T = G ×_1 U_1 ×_2 U_2 ... ×_d U_d

    Parameters
    ----------
    tensor : array-like
    ranks : sequence of int, optional
        Multilinear rank (one per mode).  If None, uses full rank
        per mode (= shape).
    max_iter : int
    tol : float
    init : {"svd", "random"}
    seed : int, optional

    Returns
    -------
    dict with keys
        core      : np.ndarray
        factors   : list[np.ndarray]   — each shape (n_k, r_k)
        ranks     : tuple[int, ...]
        n_iter    : int
        fit_error : float
    """
    T = _as_numpy(tensor)
    _check_tol(tol)
    _check_max_iter(max_iter)
    if init not in ("random", "svd"):
        raise ValueError(f"init must be 'random' or 'svd', got {init!r}")

    if ranks is None:
        ranks = tuple(int(s) for s in T.shape)
    else:
        ranks = tuple(int(r) for r in ranks)
        if len(ranks) != T.ndim:
            raise ValueError(
                f"ranks has length {len(ranks)} but tensor has ndim {T.ndim}"
            )
        for k, (r, n) in enumerate(zip(ranks, T.shape)):
            if r < 1:
                raise ValueError(f"ranks[{k}] must be >= 1, got {r}")
            if r > n:
                raise ValueError(
                    f"ranks[{k}]={r} exceeds shape[{k}]={n}; Tucker rank "
                    "cannot exceed mode dimension."
                )

    # 1-D special case: Tucker on a vector is just  v = u · σ  with σ scalar.
    if T.ndim == 1:
        norm = float(np.linalg.norm(T))
        r = ranks[0]
        if norm == 0.0:
            U = np.zeros((T.size, r), dtype=np.float64)
            U[: min(T.size, r), : min(T.size, r)] = np.eye(min(T.size, r))
            core = np.zeros(r, dtype=np.float64)
        else:
            U = np.zeros((T.size, r), dtype=np.float64)
            U[:, 0] = T / norm
            core = np.zeros(r, dtype=np.float64)
            core[0] = norm
        T_hat = tucker_reconstruct(core, [U])
        return {
            "core": core,
            "factors": [U],
            "ranks": ranks,
            "n_iter": 0,
            "fit_error": _relative_fit_error(T, T_hat),
        }

    # All-zero tensor: tensorly's HOOI can stall on degenerate SVDs.
    if _frobenius(T) == 0.0:
        factors = []
        for n, r in zip(T.shape, ranks):
            U = np.zeros((n, r), dtype=np.float64)
            U[: min(n, r), : min(n, r)] = np.eye(min(n, r))
            factors.append(U)
        core = np.zeros(ranks, dtype=np.float64)
        return {
            "core": core,
            "factors": factors,
            "ranks": ranks,
            "n_iter": 0,
            "fit_error": 0.0,
        }

    if seed is not None:
        np.random.seed(int(seed))

    core, factors = _tl_tucker(
        tl.tensor(T),
        rank=list(ranks),
        n_iter_max=max_iter,
        tol=tol,
        init=init,
        random_state=seed,
    )
    core = np.asarray(core, dtype=np.float64)
    factors = [np.asarray(f, dtype=np.float64) for f in factors]
    T_hat = tucker_reconstruct(core, factors)
    return {
        "core": core,
        "factors": factors,
        "ranks": ranks,
        "n_iter": max_iter,  # tensorly does not return iter count for tucker
        "fit_error": _relative_fit_error(T, T_hat),
    }


def tucker_reconstruct(
    core: np.ndarray,
    factors: Sequence[np.ndarray],
) -> np.ndarray:
    """Reconstruct dense tensor from Tucker decomposition."""
    core = np.asarray(core, dtype=np.float64)
    factors = [np.asarray(f, dtype=np.float64) for f in factors]
    if len(factors) != core.ndim:
        raise ValueError(
            f"factors has length {len(factors)} but core has ndim {core.ndim}"
        )
    out = _tucker_to_tensor((core, factors))
    return np.asarray(out, dtype=np.float64)


# ---------------------------------------------------------------------------
# Tensor-Train
# ---------------------------------------------------------------------------

def tt_decompose(
    tensor,
    max_bond_dim: Optional[int] = None,
    tol: float = 1e-12,
) -> dict:
    """Tensor-Train decomposition via successive SVD truncation.

    Parameters
    ----------
    tensor : array-like
    max_bond_dim : int, optional
        Cap on every internal bond dimension.  None  →  no cap (use the
        natural ranks; for tensorly this is interpreted as
        min(prod_left, prod_right) per bond).
    tol : float
        SVD truncation tolerance (currently informational; tensorly's
        deterministic-SVD TT honours `rank` only).

    Returns
    -------
    dict with keys
        cores     : list[np.ndarray]  — each of shape (r_{k-1}, n_k, r_k)
        bond_dims : tuple[int, ...]   — (r_0=1, r_1, ..., r_{d-1}, r_d=1)
        fit_error : float
    """
    T = _as_numpy(tensor)
    _check_tol(tol)
    if max_bond_dim is not None:
        if max_bond_dim < 1:
            raise ValueError(
                f"max_bond_dim must be >= 1 if given, got {max_bond_dim}"
            )

    # 1-D special case: TT on a vector is a single 1×n×1 core.
    if T.ndim == 1:
        core = T.reshape(1, -1, 1).copy()
        bond_dims = (1, 1)
        return {
            "cores": [core],
            "bond_dims": bond_dims,
            "fit_error": 0.0,
        }

    # All-zero tensor
    if _frobenius(T) == 0.0:
        cores = []
        prev = 1
        for k, n in enumerate(T.shape):
            nxt = 1
            cores.append(np.zeros((prev, n, nxt), dtype=np.float64))
            prev = nxt
        return {
            "cores": cores,
            "bond_dims": tuple([1] * (T.ndim + 1)),
            "fit_error": 0.0,
        }

    # Build the per-bond rank list:  [1, r_1, r_2, ..., r_{d-1}, 1].
    d = T.ndim
    natural = [1]
    left = 1
    total = int(np.prod(T.shape))
    for k in range(d - 1):
        left *= T.shape[k]
        right = total // left
        natural.append(min(left, right))
    natural.append(1)
    if max_bond_dim is not None:
        ranks = [min(r, int(max_bond_dim)) for r in natural]
        ranks[0] = 1
        ranks[-1] = 1
    else:
        ranks = natural

    cores = _tl_tensor_train(tl.tensor(T), rank=ranks)
    cores = [np.asarray(c, dtype=np.float64) for c in cores]
    bond_dims = tuple(c.shape[0] for c in cores) + (cores[-1].shape[2],)

    T_hat = tt_reconstruct(cores)
    return {
        "cores": cores,
        "bond_dims": bond_dims,
        "fit_error": _relative_fit_error(T, T_hat),
    }


def tt_reconstruct(cores: Sequence[np.ndarray]) -> np.ndarray:
    """Reconstruct a dense tensor from TT cores."""
    if not cores:
        raise ValueError("cores must be a non-empty sequence")
    cores = [np.asarray(c, dtype=np.float64) for c in cores]
    for k, c in enumerate(cores):
        if c.ndim != 3:
            raise ValueError(f"core {k} must be 3-D, got shape {c.shape}")
    if cores[0].shape[0] != 1:
        raise ValueError(
            f"first core must have leading bond dim 1, got {cores[0].shape[0]}"
        )
    if cores[-1].shape[2] != 1:
        raise ValueError(
            f"last core must have trailing bond dim 1, got {cores[-1].shape[2]}"
        )
    for k in range(len(cores) - 1):
        if cores[k].shape[2] != cores[k + 1].shape[0]:
            raise ValueError(
                f"bond mismatch between core {k} (right={cores[k].shape[2]}) "
                f"and core {k+1} (left={cores[k+1].shape[0]})"
            )
    out = _tt_to_tensor(cores)
    return np.asarray(out, dtype=np.float64)


# ---------------------------------------------------------------------------
# Rank estimation and storage utilities
# ---------------------------------------------------------------------------

def tensor_rank_estimate(
    tensor,
    method: str = "cp",
    rank_max: Optional[int] = None,
    seed: int = 0,
    eps_drop: float = 1e-2,
) -> int:
    """Heuristic rank estimate.

    For ``method='cp'``: try ALS at increasing rank, return the smallest
    rank R such that ``fit_error(R+1) >= fit_error(R) * (1 - eps_drop)``,
    i.e. the error has stabilised.

    For ``method='tucker'``: returns the multilinear rank of T (= the
    rank of each mode-k unfolding) rounded to ints.  This is the
    classical "n-rank" of de Lathauwer.
    """
    T = _as_numpy(tensor)
    if method == "cp":
        if T.ndim == 1:
            return 1
        cap = rank_max if rank_max is not None else min(T.size, max(T.shape) * 2)
        prev = None
        for R in range(1, cap + 1):
            res = cp_decompose(T, rank=R, max_iter=200, tol=1e-9, seed=seed)
            err = res["fit_error"]
            if prev is not None and err >= prev * (1 - eps_drop):
                return R - 1 if R > 1 else 1
            if err < 1e-10:
                return R
            prev = err
        return cap
    elif method == "tucker":
        ranks = []
        for k in range(T.ndim):
            unfold = np.moveaxis(T, k, 0).reshape(T.shape[k], -1)
            r = int(np.linalg.matrix_rank(unfold, tol=1e-10))
            ranks.append(max(r, 1))
        return max(ranks)
    else:
        raise ValueError(f"method must be 'cp' or 'tucker', got {method!r}")


def decomp_storage(decomp_dict: dict, kind: str) -> int:
    """Number of floats stored in a decomposition (compression measure).

    Parameters
    ----------
    decomp_dict : dict
        Output of cp_decompose / tucker_decompose / tt_decompose.
    kind : {"cp", "tucker", "tt"}
    """
    kind = kind.lower()
    if kind == "cp":
        n = sum(int(np.asarray(f).size) for f in decomp_dict["factors"])
        n += int(np.asarray(decomp_dict["weights"]).size)
        return n
    if kind == "tucker":
        n = int(np.asarray(decomp_dict["core"]).size)
        n += sum(int(np.asarray(f).size) for f in decomp_dict["factors"])
        return n
    if kind == "tt":
        return sum(int(np.asarray(c).size) for c in decomp_dict["cores"])
    raise ValueError(f"kind must be 'cp', 'tucker', or 'tt', got {kind!r}")


__all__ = [
    "cp_decompose",
    "cp_reconstruct",
    "tucker_decompose",
    "tucker_reconstruct",
    "tt_decompose",
    "tt_reconstruct",
    "tensor_rank_estimate",
    "decomp_storage",
]
