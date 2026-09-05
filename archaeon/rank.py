"""Deterministic ranking of fired signals.

Two jobs.

**Merge.** Detectors overlap by construction (D2 and D4 read the same four
cells; D3 and D5 can both flag one region). Two detectors reading the same rows
is one observation looked at twice, not two observations, so signals sharing a
probe target are MERGED into one candidate before ranking. Counting them
separately would let an arbitrary detector-suite composition decide which probe
wins.

**Rank.** Score is an explicit weighted sum, no learning and no model:

    score = w[intent] + w['effect'] * effect_norm + w['support'] * support_norm

``intent`` dominates because the charter says so: probes that discriminate
between explanations or refine a boundary are preferred over probes that only
repeat. ``support_norm`` is a saturating function of n so a huge cell cannot
outrank a genuinely better probe on volume alone.

Ties break on (detector order, signal_id) -- both fixed -- so the same corpus
always yields the same proposal. That is what makes a proposal reproducible
from its recorded provenance rather than merely plausible.

The score is a SCHEDULING number. It is not evidence strength, not a p-value,
and not a confidence. Nothing downstream may read it as one.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple

from .detectors import DETECTORS
from .detectors.base import Signal

DETECTOR_ORDER = {mod.NAME: i for i, (_, mod) in enumerate(DETECTORS)}

# n at which support_norm reaches ~0.63; beyond this, extra volume buys little.
SUPPORT_SATURATION_N = 20.0


@dataclass
class Candidate:
    """One probe target, backed by one or more signals."""
    target_key: str
    signals: List[Signal] = field(default_factory=list)
    score: float = 0.0
    score_terms: Dict[str, float] = field(default_factory=dict)

    @property
    def primary(self) -> Signal:
        """The signal that defines the probe: best intent, then detector order."""
        return sorted(self.signals, key=_signal_sort_key)[0]

    @property
    def detectors(self) -> List[str]:
        return sorted({s.detector for s in self.signals})

    def to_json(self) -> Dict[str, Any]:
        return {"target_key": self.target_key,
                "score": self.score,
                "score_terms": dict(self.score_terms),
                "detectors": self.detectors,
                "primary_detector": self.primary.detector,
                "intent": self.primary.intent,
                "regions": list(self.primary.regions),
                "players": list(self.primary.players),
                "signal_ids": sorted(s.signal_id() for s in self.signals)}


def target_key(sig: Signal) -> str:
    """Identity of the place a probe would go.

    Coordinates are rounded to 3 decimals so two detectors pointing at
    effectively the same spot merge instead of racing.
    """
    payload = {
        "regions": sorted(sig.regions),
        "players": sorted(sig.players),
        "coords": {k: round(v, 3) for k, v in sorted(sig.target_coords.items())},
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "tgt:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _signal_sort_key(s: Signal) -> Tuple[int, int, str]:
    intent_rank = {"DISCRIMINATE": 0, "REFINE_BOUNDARY": 1, "REPLICATE": 2}
    return (intent_rank.get(s.intent, 9),
            DETECTOR_ORDER.get(s.detector, 99),
            s.signal_id())


def support_norm(n: int) -> float:
    """Saturating support term in [0, 1)."""
    return 1.0 - math.exp(-max(n, 0) / SUPPORT_SATURATION_N)


def rank(signals: Sequence[Signal], weights: Dict[str, float]) -> List[Candidate]:
    """Merge signals into candidates and return them best-first."""
    groups: Dict[str, Candidate] = {}
    for s in signals:
        k = target_key(s)
        groups.setdefault(k, Candidate(target_key=k)).signals.append(s)

    cands: List[Candidate] = []
    for k in sorted(groups):
        c = groups[k]
        c.signals.sort(key=_signal_sort_key)
        p = c.primary
        # Effect and support are taken from the BEST-INTENT signal, not maxed
        # across the group: mixing the intent of one signal with the effect of
        # another would describe a probe that no detector actually proposed.
        w_intent = weights.get(p.intent, 0.0)
        t_effect = weights.get("effect", 0.0) * p.effect_norm
        t_support = weights.get("support", 0.0) * support_norm(p.support_n)
        c.score_terms = {"intent[{}]".format(p.intent): w_intent,
                         "effect": t_effect, "support": t_support}
        c.score = w_intent + t_effect + t_support
        cands.append(c)

    cands.sort(key=lambda c: (-c.score,
                              _signal_sort_key(c.primary),
                              c.target_key))
    return cands
