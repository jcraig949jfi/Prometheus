"""sigma_kernel — Σ-substrate runtime + extensions.

Public surface:
- ``SigmaKernel`` — the v0.1 7-opcode kernel (RESOLVE / CLAIM / FALSIFY /
  GATE / PROMOTE / ERRATA / TRACE).
- ``BindEvalExtension`` — adds BIND + EVAL opcodes (sidecar, no edits to
  the core kernel).

The package was originally laid out as a flat directory of scripts.
Adding ``__init__.py`` so ``from sigma_kernel.sigma_kernel import ...``
and ``from sigma_kernel.bind_eval import ...`` resolve correctly when
the repo root is on ``sys.path`` — which is the convention used by both
the test suite and demo scripts.
"""
from __future__ import annotations

# Re-export the most-used public types so callers can do
# ``from sigma_kernel import SigmaKernel`` if they prefer.
from .sigma_kernel import (  # noqa: F401
    Capability,
    CapabilityError,
    Claim,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)

__all__ = [
    "SigmaKernel",
    "Symbol",
    "Claim",
    "Capability",
    "CapabilityError",
    "Tier",
    "Verdict",
    "VerdictResult",
]
