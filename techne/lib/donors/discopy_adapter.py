"""DisCoPy donor adapter -- string diagrams, composition, and tensor interpretation.

Upstream: github.com/discopy/discopy (BSD-3; identity RESOLVED from declared project URLs).

WHAT IS MECHANICALLY AVAILABLE. DisCoPy represents a computation as a string diagram -- typed
boxes composed in sequence (`>>`) and in parallel (`@`) -- and can then INTERPRET that same
diagram in a different category, e.g. evaluate it as a tensor network. The capability that
matters for a lensing bench is precisely that split: one structure, several interpretations,
none of them privileged.

WHAT THIS ADAPTER DOES NOT CLAIM. Nothing here is a "reasoning lens". A diagram is a syntax
with a functorial semantics; whether presenting a problem in an alternative but equivalent form
changes what a solver can reach is an empirical question, and it belongs to whoever runs the
Lensing bench. This adapter's only job is to make the mechanics callable and replayable so that
question can be asked.

SELECTION RELATION: NONE. DisCoPy constructs and evaluates; it does not rank alternatives.
That is stated rather than left blank, because "no preference order" is exactly the property a
downstream experiment needs to know in order to trust that any ordering it observes is its own.
"""
from __future__ import annotations

from typing import Any, Mapping

from .contract import (
    NO_SELECTION, DonorAdapter, DonorCapability, DonorError, DonorIdentity, register,
)


@register("discopy")
class DisCoPyAdapter(DonorAdapter):
    """Build a diagram from a wire spec; report its structure; evaluate it as a tensor."""

    native_selection_relation = NO_SELECTION

    accepted_config = frozenset({"normal_form", "dtype"})

    def _identity(self) -> DonorIdentity:
        try:
            import importlib.metadata as md
            v = md.version("discopy")
        except Exception as e:                                        # noqa: BLE001
            raise DonorError("discopy", "identity", "discopy is not installed", e)
        return DonorIdentity(
            name="discopy", distribution="discopy", version=v,
            upstream="github.com/discopy/discopy", license="BSD-3-Clause",
            identity_evidence="declared_url",
        )

    def _capabilities(self):
        return [
            DonorCapability(
                "compose",
                "build a monoidal diagram from a list of boxes composed in sequence",
                deterministic=True,
                inputs="payload = {'boxes': [{'name','dom','cod'}, ...]}; config normal_form",
                outputs="dict(dom, cod, boxes, n_layers, repr)",
            ),
            DonorCapability(
                "tensor_eval",
                "evaluate a matrix pipeline in the category of tensors (tensor-network semantics)",
                deterministic=True,
                inputs="payload = {'factors': [2-D array-like, ...]} composed left to right",
                outputs="dict(shape, array, dom, cod)",
            ),
        ]

    def _propose(self, capability: str, payload: Any, config: Mapping[str, Any],
                 seed: int | None):
        from discopy.monoidal import Box, Ty

        if capability == "compose":
            if not isinstance(payload, Mapping) or "boxes" not in payload:
                raise DonorError("discopy", "input", "payload must be a mapping with 'boxes'")
            specs = list(payload["boxes"])
            if not specs:
                raise DonorError("discopy", "input", "'boxes' must be non-empty")
            diagram = None
            for i, spec in enumerate(specs):
                try:
                    box = Box(str(spec["name"]), Ty(str(spec["dom"])), Ty(str(spec["cod"])))
                except KeyError as e:
                    raise DonorError("discopy", "input",
                                     "box " + str(i) + " missing key " + str(e))
                if diagram is None:
                    diagram = box
                else:
                    if diagram.cod != box.dom:
                        # A type mismatch is a real failure and is reported as one. Silently
                        # inserting an identity wire here would manufacture a valid-looking
                        # diagram the caller never described (T10).
                        raise DonorError(
                            "discopy", "compose",
                            "type mismatch composing box " + str(i) + ": cod "
                            + str(diagram.cod) + " != dom " + str(box.dom))
                    diagram = diagram >> box
            if config.get("normal_form"):
                try:
                    diagram = diagram.normal_form()
                except Exception as e:                                # noqa: BLE001
                    raise DonorError("discopy", "compose", "normal_form failed", e)
            out = {"dom": str(diagram.dom), "cod": str(diagram.cod),
                   "boxes": [b.name for b in diagram.boxes],
                   "n_layers": len(diagram), "repr": str(diagram)}
            return out, None

        if capability == "tensor_eval":
            import numpy as np
            from discopy.tensor import Dim, Tensor
            if not isinstance(payload, Mapping) or "factors" not in payload:
                raise DonorError("discopy", "input", "payload must be a mapping with 'factors'")
            mats = [np.asarray(m, dtype=float) for m in payload["factors"]]
            if not mats:
                raise DonorError("discopy", "input", "'factors' must be non-empty")
            for i, m in enumerate(mats):
                if m.ndim != 2:
                    raise DonorError("discopy", "input",
                                     "factor " + str(i) + " must be 2-D, got ndim="
                                     + str(m.ndim))
            acc = None
            for i, m in enumerate(mats):
                t = Tensor[float](m.ravel().tolist(), Dim(m.shape[0]), Dim(m.shape[1]))
                if acc is None:
                    acc = t
                else:
                    if acc.cod != t.dom:
                        raise DonorError(
                            "discopy", "tensor_eval",
                            "dimension mismatch at factor " + str(i) + ": cod " + str(acc.cod)
                            + " != dom " + str(t.dom))
                    acc = acc >> t
            arr = np.asarray(acc.array, dtype=float)
            out = {"dom": str(acc.dom), "cod": str(acc.cod),
                   "shape": list(arr.shape), "array": arr.tolist()}
            return out, None

        raise DonorError("discopy", "capability", "unreachable: " + repr(capability))
