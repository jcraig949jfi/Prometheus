"""C3 foreign holdout D (author: Nestor, M1 SKULLPORT) -- a drifting reactive chemical medium.

Broker convention (roles/Cosmos/c3/D_CONTRACT.md s6): this package refuses import unless the
environment variable COSMOS_BROKER is exactly "1".
"""
import os as _os

if _os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("prometheus.cosmos.c3_holdout_D is a sealed holdout: set COSMOS_BROKER=1 (broker only)")
