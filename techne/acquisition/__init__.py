"""techne.acquisition -- bounded, receipted acquisition of external tooling.

Four deliverables are kept SEPARATE here, because the H0-H5 design v0.1 says so and
because collapsing them is how a tool claim inflates:

    1. tool installation      -- the bytes arrived, pinned and hashed
    2. paper reproduction     -- a published number was reproduced within a declared tolerance
    3. adapter qualification  -- a Prometheus consumer can call it under a typed contract
    4. local scientific benefit -- an experiment got a better answer because of it

(1) is what this package does. It does NOT do (2), (3) or (4), and a receipt from here
must never be read as evidence for them. `reproduction/` holds the MANIFESTS for (2),
which are written BEFORE a benchmark claim, not after.

Nothing here installs into the live interpreter. Everything lands in an isolated cache
and an isolated virtual environment whose location is host-local and never hardcoded.
"""
from __future__ import annotations

__all__ = ["paths", "manifest", "budget", "pypi", "repo", "receipt"]
