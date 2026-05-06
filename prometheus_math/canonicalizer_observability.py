"""prometheus_math.canonicalizer_observability — log canonicalizer used per claim.

Pre-Tier-0 deliverable (joint sprint sync point S4 / commitment T3,
see ``pivot/techne_ergon_joint_sprint_2026-05-05.md``).

Why this exists
---------------
Ergon's session-journal measurement (2026-05-04) showed
``variety_fingerprint`` taking ~52% of cells on seed=42 / 1K eps, with
the descriptor's hot-swap threshold at 70%. If she runs more episodes
before P0 CoordinateChart + CanonicalizationProtocol land (Day 3-4 of
the joint sprint), variety_fingerprint may exceed 70% and trigger an
implicit hot-swap that silently inflates archive coverage. R21 in the
joint sprint risk register names this; T3 is the mitigation.

This module is the substrate-side observability hook: callers (Ergon's
descriptor in particular, but any agent that runs canonicalization)
log which canonicalizer they used per claim, and we aggregate to
detect hot-swap proximity. No canonicalizer logic is changed; this is
pure instrumentation.

What this DOES NOT do
---------------------
* Implement the actual hot-swap (that's P0 CoordinateChart with
  CanonicalizationProtocol, Day 3-4).
* Replace any existing canonicalizer.
* Force callers to use a specific canonicalizer.

What this DOES do
-----------------
* Provides ``CanonicalizerObserver`` — a thin file-backed JSONL logger
  that records (timestamp, canonicalizer_name, claim_id_or_context).
* Provides ``observed_distribution(log_path)`` — aggregates the log
  into a {canonicalizer_name → fraction} mapping.
* Provides ``hot_swap_imminent(distribution, threshold=0.7)`` — returns
  True when any single canonicalizer dominates above the threshold.
* Default log path is configurable; default lives at
  ``F:/Prometheus/sigma_kernel/_canonicalizer_observed.jsonl``.
"""
from __future__ import annotations

import json
import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Counter as CounterType, Dict, Iterable, Mapping, Optional


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


DEFAULT_LOG_PATH = Path("sigma_kernel") / "_canonicalizer_observed.jsonl"
"""Default observability log location. Relative to repo root by convention;
callers can override per-run."""


HOT_SWAP_THRESHOLD = 0.70
"""Default hot-swap threshold per Ergon's descriptor logic. When any single
canonicalizer's observed fraction >= this, hot-swap is imminent and the
substrate's downstream consumers should be alerted."""


# Known canonicalizer names from substrate v2.3 §6.1 P0 + Ergon's
# descriptor.py axis 1 enumeration. Adding a new canonicalizer is fine
# (the aggregator is open-vocabulary); this list is for documentation.
KNOWN_CANONICALIZERS = (
    "group_quotient",
    "partition_refinement",
    "ideal_reduction",
    "variety_fingerprint",
    "cohomological_functor",  # Aporia Study 07; subsumed under
                               # CanonicalizationProtocol per Study 17
)


# ---------------------------------------------------------------------------
# Observation record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalizerObservation:
    """One log entry."""

    timestamp: float
    canonicalizer: str
    claim_id: Optional[str] = None
    context: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.timestamp,
            "canonicalizer": self.canonicalizer,
            "claim_id": self.claim_id,
            "context": dict(self.context),
        }

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "CanonicalizerObservation":
        return cls(
            timestamp=float(d["ts"]),
            canonicalizer=str(d["canonicalizer"]),
            claim_id=d.get("claim_id"),
            context=dict(d.get("context", {})),
        )


# ---------------------------------------------------------------------------
# Observer (thread-safe append-only logger)
# ---------------------------------------------------------------------------


class CanonicalizerObserver:
    """Thread-safe append-only observer for canonicalizer-usage events.

    Writes one JSONL entry per ``observe()`` call. Append-only; rotation
    is the caller's responsibility (substrate convention: rotate at
    1M entries via a sidecar tool, not in this hot path).
    """

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path: Path = Path(log_path) if log_path is not None else DEFAULT_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def observe(
        self,
        canonicalizer: str,
        *,
        claim_id: Optional[str] = None,
        context: Optional[Mapping[str, Any]] = None,
    ) -> CanonicalizerObservation:
        """Log a canonicalizer-usage event.

        Idempotent in the sense that callers are free to call multiple
        times per claim if needed (the aggregator counts events, not
        unique claims, by default).
        """
        obs = CanonicalizerObservation(
            timestamp=time.time(),
            canonicalizer=str(canonicalizer),
            claim_id=claim_id,
            context=dict(context or {}),
        )
        with self._lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obs.to_dict()) + "\n")
        return obs

    def read_all(self) -> Iterable[CanonicalizerObservation]:
        """Stream all logged observations from disk. Reads in append order."""
        if not self.log_path.exists():
            return
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield CanonicalizerObservation.from_dict(json.loads(line))


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def observed_distribution(
    log_path: Optional[Path] = None,
    *,
    since: Optional[float] = None,
    unique_claims: bool = False,
) -> Dict[str, float]:
    """Aggregate the observability log into a {canonicalizer → fraction} mapping.

    Parameters
    ----------
    log_path : optional Path
        Defaults to DEFAULT_LOG_PATH.
    since : optional float
        Filter to events with timestamp >= since (unix epoch seconds).
        Useful for windowed analysis (e.g., "last hour's distribution").
    unique_claims : bool, default False
        If True, count one event per (canonicalizer, claim_id) pair —
        repeated observations on the same claim count once. If False,
        count every event.

    Returns
    -------
    dict mapping canonicalizer_name → fraction in [0, 1]; sums to 1.0
    (or empty if no events).
    """
    obs = CanonicalizerObserver(log_path=log_path)
    counts: CounterType[str] = Counter()
    seen_pairs: set = set()
    for o in obs.read_all():
        if since is not None and o.timestamp < since:
            continue
        if unique_claims and o.claim_id is not None:
            key = (o.canonicalizer, o.claim_id)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
        counts[o.canonicalizer] += 1

    total = sum(counts.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counts.items()}


def hot_swap_imminent(
    distribution: Mapping[str, float],
    threshold: float = HOT_SWAP_THRESHOLD,
) -> bool:
    """True when any single canonicalizer's fraction >= threshold.

    Per Ergon's descriptor.py hot-swap logic. Returns False on empty
    distribution.
    """
    if not distribution:
        return False
    return max(distribution.values()) >= threshold


def dominant_canonicalizer(
    distribution: Mapping[str, float],
) -> Optional[tuple]:
    """Return (name, fraction) of the highest-fraction canonicalizer.
    Returns None on empty distribution."""
    if not distribution:
        return None
    name = max(distribution, key=distribution.get)
    return (name, distribution[name])


# ---------------------------------------------------------------------------
# Convenience: alert summary for log review
# ---------------------------------------------------------------------------


def alert_summary(
    log_path: Optional[Path] = None,
    *,
    threshold: float = HOT_SWAP_THRESHOLD,
) -> Dict[str, Any]:
    """One-call summary suitable for monitoring dashboards.

    Returns
    -------
    dict with keys:
        distribution: {canonicalizer → fraction}
        n_events: int (total events logged)
        hot_swap_imminent: bool
        dominant: (name, fraction) tuple or None
        threshold: float (the threshold used)
    """
    dist = observed_distribution(log_path=log_path)
    obs = CanonicalizerObserver(log_path=log_path)
    n = sum(1 for _ in obs.read_all())
    return {
        "distribution": dist,
        "n_events": n,
        "hot_swap_imminent": hot_swap_imminent(dist, threshold=threshold),
        "dominant": dominant_canonicalizer(dist),
        "threshold": threshold,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


__all__ = [
    "DEFAULT_LOG_PATH",
    "HOT_SWAP_THRESHOLD",
    "KNOWN_CANONICALIZERS",
    "CanonicalizerObservation",
    "CanonicalizerObserver",
    "observed_distribution",
    "hot_swap_imminent",
    "dominant_canonicalizer",
    "alert_summary",
]
