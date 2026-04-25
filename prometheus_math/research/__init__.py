"""Research-grade modules for active Prometheus threads.

This subpackage hosts reusable primitives extracted from
research-thread one-off scripts (Aporia, Charon, Ergon, Harmonia).
Modules here are typically promoted from ``ergon/`` or ``aporia/`` after
their interface has stabilized and they have a TDD-quality test suite.

Submodules
----------
spectral_gaps
    L-function spectral-gap-k scan vs matched random-matrix-ensemble
    nulls (GUE, CUE, GOE, USp(4), O+, O-). Used by Aporia's F011
    paper-track for L-function compression studies.
bsd_audit
    (concurrent — created by another agent in this same package)
    BSD-formula consistency audit over LMFDB rank-0/1 EC samples.
vcm_scaling
    V-CM-scaling stratifier — per-disc regression of CM EC gap-1
    compression vs log|D|, codifying Aporia's F011 sub-void.

Defensive imports
-----------------
The submodule imports are wrapped in try/except because adjacent
agents may be writing other modules into this package concurrently
and a syntax error in one module should not break the others. The
failed import is silently dropped from the namespace; explicit
``from prometheus_math.research import <name>`` will still surface
the underlying ImportError.
"""

from __future__ import annotations

__all__: list[str] = []

try:
    from . import spectral_gaps  # noqa: F401
except Exception:  # pragma: no cover — defensive against concurrent agents
    pass
else:
    __all__.append("spectral_gaps")

try:
    from . import bsd_audit  # noqa: F401
except Exception:  # pragma: no cover — bsd_audit may not exist yet
    pass
else:
    __all__.append("bsd_audit")

try:
    from . import vcm_scaling  # noqa: F401
except Exception:  # pragma: no cover — defensive against concurrent agents
    pass
else:
    __all__.append("vcm_scaling")

try:
    from . import identity_join  # noqa: F401
except Exception:  # pragma: no cover — defensive against concurrent agents
    pass
else:
    __all__.append("identity_join")

try:
    from . import conjecture_engine  # noqa: F401
except Exception:  # pragma: no cover — defensive against concurrent agents
    pass
else:
    __all__.append("conjecture_engine")
