"""The weak-signal detector registry.

Six detectors, all arithmetic, all with thresholds in ``archaeon/config.py``.
No detector calls a model, reads prose, or consults a scientific prior.

Order is fixed and is the tie-break order used by the ranker, so a corpus that
fires several detectors always yields the same proposal.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from . import (d1_repeated_deviation, d2_sign_instability,
               d3_variance_anomaly, d4_order_reversal,
               d5_outlier_region, d6_boundary_hint)
from .base import DetectorResult, Eligibility, Signal   # re-export

DETECTORS = (
    ("d1", d1_repeated_deviation),
    ("d2", d2_sign_instability),
    ("d3", d3_variance_anomaly),
    ("d4", d4_order_reversal),
    ("d5", d5_outlier_region),
    ("d6", d6_boundary_hint),
)

DETECTOR_BY_NAME = {m.NAME: m for _, m in DETECTORS}


def run_all(corpus, dcfg) -> Dict[str, DetectorResult]:
    """Run every enabled detector. Returns {detector_name: DetectorResult}.

    A disabled detector is reported with an explicit blocked_reason rather
    than omitted: a detector that is off and a detector that found nothing must
    not look the same in the record.
    """
    out: Dict[str, DetectorResult] = {}
    for key, mod in DETECTORS:
        if not getattr(dcfg, "{}_enabled".format(key), True):
            out[mod.NAME] = DetectorResult(Eligibility(
                mod.NAME, 0, 0, mod.UNIT,
                blocked_reason="detector disabled in configuration ({}_enabled=False)".format(key)))
            continue
        out[mod.NAME] = mod.detect(corpus, dcfg)
    return out


def all_signals(results: Dict[str, DetectorResult]) -> List[Signal]:
    """Every signal from every detector, in fixed detector order."""
    sigs: List[Signal] = []
    for _, mod in DETECTORS:
        r = results.get(mod.NAME)
        if r:
            sigs.extend(r.signals)
    return sigs


def eligibility_census(results: Dict[str, DetectorResult]) -> Dict[str, Any]:
    """The census that must be reported alongside any 'nothing fired'.

    ``any_eligible`` False means the corpus could not have produced a signal.
    That is a fact about the corpus and the instrument. It is NOT a finding
    about the science, and nothing may render it as one.
    """
    per = {name: r.eligibility.to_json() for name, r in results.items()}
    eligible = [n for n, r in results.items() if r.eligibility.is_eligible]
    fired = [n for n, r in results.items() if r.signals]
    return {
        "per_detector": per,
        "detectors_total": len(results),
        "detectors_eligible": len(eligible),
        "detectors_eligible_names": sorted(eligible),
        "detectors_fired": len(fired),
        "detectors_fired_names": sorted(fired),
        "any_eligible": bool(eligible),
        "reading": ("some detectors were eligible to fire"
                    if eligible else
                    "no detector was eligible to fire on this corpus; "
                    "this is a statement about corpus coverage, not about "
                    "the presence or absence of any phenomenon"),
    }
