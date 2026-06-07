"""In-band corpus loader for Stage 0b relational (v0.3).

The states are the IN-BAND (1.001 < M < 1.18) polynomials in
``prometheus_math.databases.mahler.MAHLER_TABLE`` — the only region where the full
falsifier battery runs (out-of-band = phase-0 kill, no per-falsifier vector). The
whole in-band slice is taken (no cherry-pick), in a deterministic order, and recorded
with count + source in the report's provenance.
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["InBandState", "load_in_band_states", "BAND_LOW", "BAND_HIGH", "CORPUS_SOURCE"]

BAND_LOW = 1.001
BAND_HIGH = 1.18
CORPUS_SOURCE = "prometheus_math.databases.mahler.MAHLER_TABLE"


@dataclass(frozen=True)
class InBandState:
    coeffs: tuple
    mahler_measure: float
    name: str


def load_in_band_states(m_low: float = BAND_LOW, m_high: float = BAND_HIGH) -> list:
    """Return all in-band states (m_low < M < m_high), deterministically ordered.

    Order: by (mahler_measure, coeffs) so the slice is reproducible across runs.
    """
    if not (m_low < m_high):
        raise ValueError(f"need m_low < m_high, got {m_low}, {m_high}")
    from prometheus_math.databases import mahler as _mdb

    table = getattr(_mdb, "MAHLER_TABLE", None) or []
    states = []
    for e in table:
        m = e.get("mahler_measure")
        coeffs = e.get("coeffs")
        if m is None or coeffs is None:
            continue
        mf = float(m)
        if m_low < mf < m_high:
            states.append(
                InBandState(
                    coeffs=tuple(int(c) for c in coeffs),
                    mahler_measure=mf,
                    name=str(e.get("name") or e.get("label") or "?"),
                )
            )
    states.sort(key=lambda s: (s.mahler_measure, s.coeffs))
    return states
