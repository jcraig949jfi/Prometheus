"""pyribs donor adapter -- MAP-Elites / quality-diversity archives, numpy-native.

Upstream: github.com/icaros-usc/pyribs (distribution name `ribs`; identity RESOLVED from
declared project URLs). Chosen over QDax because JAX ships no CUDA wheels for Windows, so QDax
would run CPU-only here and duplicate what pyribs already does in numpy.

SCOPE LIMIT, DELIBERATE. This adapter exposes the MECHANICS of a behavioural archive: build it,
run a seeded ask/tell loop, read occupancy back. It does NOT choose behavioural descriptors,
and it must not: the descriptor choice IS the experiment. The QD literature's documented
failure mode is exactly here -- novelty search maximising diversity along a trivial axis, and
archives whose coverage numbers are artefacts of a hand-picked descriptor. Whoever runs the
Worlds bench picks the descriptors and owns that choice.

THE SELECTION RELATION IS SUPPLIED BY THE CALLER. pyribs does not have an objective of its own;
it fills cells by whatever objective function it is handed. That makes the confound the
experiment's rather than the donor's, which is worth stating explicitly, because "the archive
found diverse high-performing solutions" means only "the archive found solutions that scored
well on the function the experimenter wrote". Coverage is not discovery.
"""
from __future__ import annotations

from typing import Any, Mapping

from .contract import (
    DonorAdapter, DonorCapability, DonorError, DonorIdentity, SelectionRelation, register,
)


@register("pyribs")
class PyribsAdapter(DonorAdapter):
    """A seeded GridArchive + GaussianEmitter + Scheduler loop, and archive readout."""

    native_selection_relation = SelectionRelation(
        kind="objective",
        direction="maximize",
        over="per-cell elite objective within a discretised behaviour space",
        supplied_by="caller",
        note="pyribs imposes no objective of its own -- it maximises whatever the caller "
             "passes, per behavioural cell. Archive coverage therefore measures the caller's "
             "descriptor choice as much as the search; it is not evidence of discovery.",
    )

    accepted_config = frozenset({
        "solution_dim", "dims", "ranges", "sigma", "x0", "batch_size", "iterations",
    })

    def _identity(self) -> DonorIdentity:
        try:
            import importlib.metadata as md
            v = md.version("ribs")
        except Exception as e:                                        # noqa: BLE001
            raise DonorError("pyribs", "identity", "ribs (pyribs) is not installed", e)
        return DonorIdentity(
            name="pyribs", distribution="ribs", version=v,
            upstream="github.com/icaros-usc/pyribs", license="MIT",
            identity_evidence="declared_url",
        )

    def _capabilities(self):
        return [
            DonorCapability(
                "archive_fill",
                "seeded MAP-Elites loop: GridArchive + GaussianEmitter + Scheduler",
                deterministic=True,
                inputs="payload = {'objective': callable(X)->obj, 'measures': callable(X)->bd}; "
                       "config solution_dim, dims, ranges, sigma, x0, batch_size, iterations",
                outputs="dict(num_elites, cells, coverage, obj_max, obj_mean, occupied_indices)",
            ),
        ]

    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None):
        import numpy as np
        from ribs.archives import GridArchive
        from ribs.emitters import GaussianEmitter
        from ribs.schedulers import Scheduler

        if capability != "archive_fill":
            raise DonorError("pyribs", "capability", "unreachable: " + repr(capability))
        if not isinstance(payload, Mapping) or "objective" not in payload \
                or "measures" not in payload:
            raise DonorError("pyribs", "input",
                             "payload must be a mapping with 'objective' and 'measures' "
                             "callables; the objective IS the selection relation and cannot "
                             "be defaulted by this adapter")
        for key in ("solution_dim", "dims", "ranges"):
            if key not in config:
                raise DonorError("pyribs", "config", "archive_fill requires config[" + repr(key) + "]")

        sd = int(config["solution_dim"])
        dims = [int(d) for d in config["dims"]]
        ranges = [(float(a), float(b)) for a, b in config["ranges"]]
        sigma = float(config.get("sigma", 0.1))
        x0 = np.asarray(config.get("x0", np.zeros(sd)), dtype=float)
        batch = int(config.get("batch_size", 16))
        iters = int(config.get("iterations", 10))
        # A seed is mandatory for the determinism claim in capabilities(); without one, pyribs
        # draws from global entropy and T3 would (correctly) fail.
        s = 0 if seed is None else int(seed)

        archive = GridArchive(solution_dim=sd, dims=dims, ranges=ranges, seed=s)
        emitter = GaussianEmitter(archive, sigma=sigma, x0=x0, batch_size=batch, seed=s)
        sched = Scheduler(archive, [emitter])

        obj_fn, meas_fn = payload["objective"], payload["measures"]
        for _ in range(iters):
            sols = sched.ask()
            obj = np.asarray(obj_fn(sols), dtype=float)
            meas = np.asarray(meas_fn(sols), dtype=float)
            if obj.shape[0] != sols.shape[0] or meas.shape[0] != sols.shape[0]:
                raise DonorError("pyribs", "input",
                                 "objective/measures must return one row per solution")
            sched.tell(obj, meas)

        st = archive.stats
        data = archive.data(return_type="dict")
        out = {
            "num_elites": int(st.num_elites),
            "cells": int(archive.cells),
            "coverage": float(np.asarray(st.coverage)),
            "qd_score": float(st.qd_score),
            "obj_max": float(st.obj_max) if st.num_elites else None,
            "obj_mean": float(np.asarray(st.obj_mean)) if st.num_elites else None,
            "occupied_indices": sorted(int(i) for i in np.asarray(data["index"]).ravel()),
        }
        # native_score is the archive's own aggregate. Reported, never aliased to a Prometheus
        # score: QD score rewards coverage x quality under the caller's objective, and says
        # nothing about whether any elite is useful.
        return out, float(st.qd_score)
