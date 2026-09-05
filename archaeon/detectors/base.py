"""Shared types for the weak-signal detectors.

A detector returns TWO things, and conflating them is the failure this module
exists to prevent:

  ``eligibility``  how many units of the corpus were even ABLE to make this
                   detector fire, and why not when the answer is zero;
  ``signals``      the units that actually crossed a threshold.

"Zero signals" from an eligible corpus and "zero signals" from a corpus that
could not have produced one are completely different facts. The first is a
reading. The second is a statement about the instrument. Archaeon reports both
and never lets the second be read as the first.

A Signal is a PROBE TRIGGER. It says "this region may be worth interrogating
again". It is not a scientific claim, and nothing downstream may upgrade it
into one.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple


# Probe intents, in the order the charter prefers them: probes that separate
# explanations or sharpen a boundary beat probes that merely repeat.
INTENT_DISCRIMINATE = "DISCRIMINATE"
INTENT_REFINE_BOUNDARY = "REFINE_BOUNDARY"
INTENT_REPLICATE = "REPLICATE"


@dataclass(frozen=True)
class Eligibility:
    """How much of the corpus could have fired this detector."""
    detector: str
    eligible_units: int          # units meeting the SUPPORT preconditions
    total_units: int             # units of the detector's natural grain
    unit: str                    # what a "unit" is, in words
    blocked_reason: Optional[str] = None   # set iff eligible_units == 0
    detail: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_eligible(self) -> bool:
        return self.eligible_units > 0

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        d["is_eligible"] = self.is_eligible
        return d


@dataclass(frozen=True)
class Signal:
    """One detector firing. A probe trigger, never a conclusion."""
    detector: str
    detector_version: str
    intent: str                       # INTENT_* -- what kind of probe answers it
    regions: Tuple[str, ...]          # world(s) implicated
    players: Tuple[str, ...]          # player(s) implicated, may be empty
    # The numbers that crossed the line, and the lines they crossed. Both are
    # written verbatim into provenance so a reader can recompute the decision.
    values: Dict[str, Any] = field(default_factory=dict)
    thresholds: Dict[str, Any] = field(default_factory=dict)
    support_n: int = 0
    # Normalized [0, 1] magnitude used ONLY for deterministic ranking. It is a
    # scheduling number, not an effect size to be reported as a result.
    effect_norm: float = 0.0
    # Coordinates the probe should target.
    target_coords: Dict[str, float] = field(default_factory=dict)
    evidence_rows: Tuple[Dict[str, Any], ...] = ()

    def signal_id(self) -> str:
        payload = {
            "detector": self.detector, "version": self.detector_version,
            "regions": list(self.regions), "players": list(self.players),
            "values": _canon(self.values),
            "rows": [r.get("row_id") for r in self.evidence_rows],
        }
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          default=str)
        return "sig:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def to_json(self) -> Dict[str, Any]:
        d = asdict(self)
        d["signal_id"] = self.signal_id()
        d["regions"] = list(self.regions)
        d["players"] = list(self.players)
        d["evidence_rows"] = [dict(r) for r in self.evidence_rows]
        return d


@dataclass(frozen=True)
class DetectorResult:
    eligibility: Eligibility
    signals: Tuple[Signal, ...] = ()

    def to_json(self) -> Dict[str, Any]:
        return {"eligibility": self.eligibility.to_json(),
                "signals": [s.to_json() for s in self.signals],
                "n_signals": len(self.signals)}


def _canon(obj: Any) -> Any:
    """Round floats so a signal id is stable across platforms."""
    if isinstance(obj, float):
        return round(obj, 10)
    if isinstance(obj, dict):
        return {k: _canon(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    return obj


# --------------------------------------------------------------------------
# Small statistics. Written out rather than pulled from a library so every
# number a detector uses can be read here, in full, on one screen.
# --------------------------------------------------------------------------
def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def variance(xs: Sequence[float], ddof: int = 1) -> float:
    n = len(xs)
    if n - ddof <= 0:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - ddof)


def stdev(xs: Sequence[float], ddof: int = 1) -> float:
    return math.sqrt(variance(xs, ddof))


def sem(xs: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    return stdev(xs) / math.sqrt(n)


def median(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else 0.5 * (s[mid - 1] + s[mid])


def mad(xs: Sequence[float]) -> float:
    """Median absolute deviation. Robust scale; 0.0 when >half the values tie."""
    if not xs:
        return 0.0
    m = median(xs)
    return median([abs(x - m) for x in xs])


def robust_z(x: float, med: float, mad_val: float) -> float:
    """0.6745*(x-med)/MAD -- the consistency constant makes this comparable to
    a normal z. Returns 0.0 for a degenerate scale rather than +/-inf, so a
    tied-value cell cannot manufacture an outlier."""
    if mad_val <= 0:
        return 0.0
    return 0.6745 * (x - med) / mad_val


def clamp01(x: float) -> float:
    if x != x:          # NaN
        return 0.0
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
