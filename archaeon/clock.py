"""The project clock.

One rule: **UTC internally, always, with an explicit tzinfo.**

Naive datetimes are banned here. A naive timestamp compared against a
timestamptz is a silent local-offset error, and the machine running Archaeon
(M1/M2, America/New_York) sits four or five hours off UTC depending on the
month -- which is the same order as the four-hour cadence boundary this module
exists to police. A DST transition on a naive clock could permit or deny a
proposal for no reason anyone could reconstruct.

The AUTHORITATIVE clock for cadence is the DATABASE clock (``now()`` in
PostgreSQL), not this module. Two Archaeon instances on two machines have two
system clocks; they share exactly one database. ``utc_now()`` here is for
labelling and for tests. Cadence decisions read the DB clock -- see
``archaeon/cadence.py``.
"""
from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Optional


def utc_now() -> datetime:
    """Timezone-aware UTC now. Never naive."""
    return datetime.now(timezone.utc)


def utc_day(dt: Optional[datetime] = None) -> date:
    dt = dt or utc_now()
    if dt.tzinfo is None:
        raise ValueError("naive datetime reached the project clock; "
                         "Archaeon requires an explicit timezone")
    return dt.astimezone(timezone.utc).date()


def utc_day_str(dt: Optional[datetime] = None) -> str:
    return utc_day(dt).isoformat()


def iso(dt: Optional[datetime] = None) -> str:
    dt = dt or utc_now()
    if dt.tzinfo is None:
        raise ValueError("naive datetime reached the project clock")
    return dt.astimezone(timezone.utc).isoformat()
