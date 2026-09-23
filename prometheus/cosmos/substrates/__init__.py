"""Visible substrate families. The sealed holdout family is NOT registered here
(it lives behind prometheus/cosmos/holdout/ and is reachable only through the broker)."""
from __future__ import annotations

from typing import Dict

from prometheus.cosmos.contract import Family


def visible() -> Dict[str, Family]:
    from prometheus.cosmos.substrates import ca, regs, ring
    return {f.name: f for f in (regs.FAMILY, ring.FAMILY, ca.FAMILY)}
