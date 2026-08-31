"""TensorLy donor adapter -- CP / Tucker / Tensor-Train as contestant representations.

Upstream: github.com/tensorly/tensorly (BSD, identity RESOLVED from declared project URLs).

WHAT THIS IS FOR. Prometheus already reaches tensorly through
`prometheus_math.symbolic_tensor_decomp`, which is the researcher-facing API and stays the
right entry point for ordinary use. This adapter exists for a different job: to let a bench
treat several decompositions as COMPETING REPRESENTATIONS under one provenance-carrying
interface, and to keep tensorly's own objective visible while doing it.

THE SELECTION RELATION MATTERS HERE. Every decomposition tensorly offers minimises
reconstruction error at a fixed rank. That is a compression criterion, and compression is not
predictive value -- a representation can reconstruct a tensor beautifully and carry nothing a
downstream task can use. If a bench ranks representations by tensorly's own fit error and then
reports that the winner is the better representation, it has measured tensorly's objective, not
the bench's. The relation is therefore declared and travels with every artifact.
"""
from __future__ import annotations

from typing import Any, Mapping

from .contract import (
    DonorAdapter, DonorCapability, DonorError, DonorIdentity, SelectionRelation, register,
)


def _dist_meta():
    import importlib.metadata as md
    return md.version("tensorly")


@register("tensorly")
class TensorLyAdapter(DonorAdapter):
    """CP (ALS), Tucker (HOOI) and TT (successive SVD) over a dense numpy tensor."""

    native_selection_relation = SelectionRelation(
        kind="objective",
        direction="minimize",
        over="relative Frobenius reconstruction error at fixed rank",
        supplied_by="donor",
        note="tensorly optimises fit only. It has no notion of predictive or transfer value; "
             "a low fit error is not evidence that a representation is useful downstream.",
    )

    accepted_config = frozenset({"rank", "ranks", "init", "n_iter_max", "tol", "random_state"})

    def _identity(self) -> DonorIdentity:
        try:
            v = _dist_meta()
        except Exception as e:                                        # noqa: BLE001
            raise DonorError("tensorly", "identity", "tensorly is not installed", e)
        return DonorIdentity(
            name="tensorly", distribution="tensorly", version=v,
            upstream="github.com/tensorly/tensorly", license="BSD-3-Clause (modified BSD)",
            identity_evidence="declared_url",
        )

    def _capabilities(self):
        return [
            DonorCapability(
                "cp", "CANDECOMP/PARAFAC via alternating least squares",
                deterministic=True,
                inputs="dense array-like tensor; config rank (required), init, n_iter_max, tol",
                outputs="dict(weights, factors, fit_error, rank)",
            ),
            DonorCapability(
                "tucker", "Tucker via higher-order orthogonal iteration",
                deterministic=True,
                inputs="dense array-like tensor; config ranks (required), init, n_iter_max, tol",
                outputs="dict(core_shape, factor_shapes, fit_error, ranks)",
            ),
            DonorCapability(
                "tt", "Tensor-Train via successive SVD truncation (Oseledets)",
                deterministic=True,
                inputs="dense array-like tensor; config rank (bond ranks or int)",
                outputs="dict(core_shapes, bond_ranks, fit_error)",
            ),
        ]

    # `init='svd'` plus an explicit random_state is what makes the determinism claim true;
    # ALS from a random start is NOT deterministic, and T3 would catch that if we defaulted to it.
    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None):
        import numpy as np
        import tensorly as tl
        from tensorly.decomposition import parafac, tucker, tensor_train

        T = np.asarray(payload, dtype=float)
        if T.ndim < 2:
            raise DonorError("tensorly", "input",
                             "need a tensor of ndim >= 2, got ndim=" + str(T.ndim))
        init = config.get("init", "svd")
        n_iter_max = int(config.get("n_iter_max", 100))
        tol = float(config.get("tol", 1e-8))
        rs = config.get("random_state", seed if seed is not None else 0)
        X = tl.tensor(T)

        def fit_error(recon) -> float:
            num = float(np.linalg.norm(np.asarray(recon) - T))
            den = float(np.linalg.norm(T))
            return num / den if den > 0 else num

        if capability == "cp":
            if "rank" not in config:
                raise DonorError("tensorly", "config", "capability 'cp' requires config['rank']")
            rank = int(config["rank"])
            cp = parafac(X, rank=rank, init=init, n_iter_max=n_iter_max, tol=tol, random_state=rs)
            from tensorly.cp_tensor import cp_to_tensor
            err = fit_error(cp_to_tensor(cp))
            out = {"kind": "cp", "rank": rank,
                   "weights": np.asarray(cp[0]).tolist(),
                   "factor_shapes": [list(np.asarray(f).shape) for f in cp[1]],
                   "fit_error": err}
            return out, err

        if capability == "tucker":
            if "ranks" not in config:
                raise DonorError("tensorly", "config",
                                 "capability 'tucker' requires config['ranks']")
            ranks = [int(r) for r in config["ranks"]]
            core, factors = tucker(X, rank=ranks, init=init, n_iter_max=n_iter_max, tol=tol,
                                   random_state=rs)
            from tensorly.tucker_tensor import tucker_to_tensor
            err = fit_error(tucker_to_tensor((core, factors)))
            out = {"kind": "tucker", "ranks": ranks,
                   "core_shape": list(np.asarray(core).shape),
                   "factor_shapes": [list(np.asarray(f).shape) for f in factors],
                   "fit_error": err}
            return out, err

        if capability == "tt":
            if "rank" not in config:
                raise DonorError("tensorly", "config", "capability 'tt' requires config['rank']")
            rank = config["rank"]
            rank = [int(r) for r in rank] if isinstance(rank, (list, tuple)) else int(rank)
            cores = tensor_train(X, rank=rank)
            from tensorly.tt_tensor import tt_to_tensor
            err = fit_error(tt_to_tensor(cores))
            shapes = [list(np.asarray(c).shape) for c in cores]
            out = {"kind": "tt", "core_shapes": shapes,
                   "bond_ranks": [s[0] for s in shapes] + [shapes[-1][-1]],
                   "fit_error": err}
            return out, err

        raise DonorError("tensorly", "capability", "unreachable: " + repr(capability))
