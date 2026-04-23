"""Tensor-train representation + TT-SVD + reconstruction + storage accounting.

A tensor T of shape (n_1, ..., n_d) is stored as d cores G_k of shape
(r_{k-1}, n_k, r_k) with r_0 = r_d = 1. The ranks (r_1, ..., r_{d-1}) are
the bond dimensions — the single knob TT gives us.
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class TTDecomposition:
    cores: list[np.ndarray] = field(default_factory=list)

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(c.shape[1] for c in self.cores)

    @property
    def ranks(self) -> tuple[int, ...]:
        """Internal bond dimensions r_1, ..., r_{d-1}."""
        return tuple(c.shape[2] for c in self.cores[:-1])

    @property
    def n_params(self) -> int:
        return sum(int(np.prod(c.shape)) for c in self.cores)

    def reconstruct(self) -> np.ndarray:
        """Contract cores left-to-right into the dense tensor."""
        if not self.cores:
            raise ValueError("Empty TT")
        out = self.cores[0]  # shape (1, n_1, r_1)
        out = out.reshape(out.shape[1], out.shape[2])  # (n_1, r_1)
        for k in range(1, len(self.cores)):
            c = self.cores[k]  # (r_{k-1}, n_k, r_k)
            r_prev, n_k, r_k = c.shape
            # out currently has shape (prod(n_1..n_{k-1}), r_{k-1})
            out = out @ c.reshape(r_prev, n_k * r_k)
            out = out.reshape(-1, r_k)
        return out.reshape(self.shape)


def tt_svd(tensor: np.ndarray, max_ranks: tuple[int, ...] | None = None,
           eps: float = 0.0) -> TTDecomposition:
    """Standard TT-SVD (Oseledets). Either specify max_ranks (length d-1) or eps.

    If max_ranks is given, truncate each bond to that rank.
    If eps > 0 and max_ranks is None, truncate each bond to the smallest rank
    that keeps per-bond relative Frobenius error below eps/sqrt(d-1).
    """
    shape = tensor.shape
    d = len(shape)
    if max_ranks is not None:
        if len(max_ranks) != d - 1:
            raise ValueError(f"max_ranks must have length {d - 1}, got {len(max_ranks)}")

    cores: list[np.ndarray] = []
    remainder = tensor.astype(np.float64)
    r_prev = 1

    for k in range(d - 1):
        n_k = shape[k]
        right_size = int(np.prod(shape[k + 1:]))
        M = remainder.reshape(r_prev * n_k, right_size)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)

        if max_ranks is not None:
            r_k = min(max_ranks[k], len(S))
        else:
            if eps > 0:
                per_bond = eps / np.sqrt(max(1, d - 1))
                total = np.linalg.norm(S)
                cumulative_tail_sq = np.cumsum(S[::-1] ** 2)[::-1]
                # include index i if the tail starting after i is within tol
                tol_sq = (per_bond * total) ** 2
                keep = np.searchsorted(-cumulative_tail_sq, -tol_sq) + 1
                r_k = max(1, int(keep))
                r_k = min(r_k, len(S))
            else:
                r_k = len(S)

        U_k = U[:, :r_k]
        S_k = S[:r_k]
        Vt_k = Vt[:r_k, :]

        core = U_k.reshape(r_prev, n_k, r_k)
        cores.append(core)
        remainder = (np.diag(S_k) @ Vt_k).reshape(r_k, *shape[k + 1:])
        r_prev = r_k

    # Final core: shape (r_{d-1}, n_d, 1)
    cores.append(remainder.reshape(r_prev, shape[-1], 1))
    return TTDecomposition(cores=cores)


def relative_l2_error(reference: np.ndarray, approximation: np.ndarray) -> float:
    ref_norm = np.linalg.norm(reference)
    if ref_norm == 0:
        return float(np.linalg.norm(approximation))
    return float(np.linalg.norm(reference - approximation) / ref_norm)


def max_possible_ranks(shape: tuple[int, ...]) -> tuple[int, ...]:
    """Ceiling ranks at each bond: min(left_size, right_size)."""
    d = len(shape)
    out = []
    for k in range(d - 1):
        left = int(np.prod(shape[: k + 1]))
        right = int(np.prod(shape[k + 1:]))
        out.append(min(left, right))
    return tuple(out)
