"""Turn a ranked candidate into an ordinary SFE-compatible experiment spec.

The mapping from detector to probe is a fixed table, not a judgement:

  D1 REPEATED_SMALL_DEVIATION  -> REPLICATE_AT_COORDINATE + a nearby control.
        A small consistent deviation is either real or it is the cell's own
        sampling history; repeating it at the same coordinate separates those,
        and the control says whether the neighbourhood moved too.

  D2 SIGN_INSTABILITY          -> INTERPOLATE_BETWEEN.
        The sign changes somewhere between the two regions. The midpoint is
        where the record is unsettled.

  D3 LOCAL_VARIANCE_ANOMALY    -> RESAMPLE_REGION.
        Dispersion is the quantity in question, and dispersion needs n.

  D4 PLAYER_ORDER_REVERSAL     -> CROSS_REPLICATE.
        Both players in both regions, so the reversal either reproduces or it
        does not.

  D5 REPEATED_OUTLIER_REGION   -> REPEAT_OUTLIER_CELL + a nearby control.

  D6 BOUNDARY_TRANSITION_HINT  -> BISECT_BOUNDARY.
        Halve the interval the step sits in.

Every spec carries ``archaeon`` metadata but is otherwise an ordinary SFE
experiment spec: a dict that goes to ``POST /v2/worlds/{wid}/experiments`` as
``spec``. Archaeon does not invent an execution format.

A generated spec contains NO interpretation of the pattern. It says where to
look and what to hold fixed. It does not say what is there.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# THE SEALED SPEC CONTAINS EXACTLY THE EXECUTION INPUTS.
# PROVENANCE LIVES OUTSIDE THE HASH.  (2026-09-06, Vivarium Tier 1)
#
# `archaeon` metadata (which detector fired, the intent, the chart) and the
# spec's own hash used to sit INSIDE the spec. Both are now split out:
#
#   * the detector is the POLICY that proposed the experiment. Inside the
#     sealed spec it changes spec_hash without changing what is executed, so a
#     fossil-directed row and a random-control row running identical science
#     would get different hashes and any spec_hash-derived universe would split
#     along the arm boundary -- the exact confound that would make "policy C
#     beat policy A" unattributable to selection (Harmonia S14/S18).
#   * a hash may not live inside the object it hashes: with spec_hash embedded,
#     Archaeon's value could never equal the content_hash SFE seals at commit.
#
# The metadata is returned separately and belongs in source_evidence, which is
# a queue column: immutable, recorded, archaeologically readable, unhashed.
# ---------------------------------------------------------------------------

from .detectors.base import Signal
from .rank import Candidate

# detector -> (probe kind, what the probe holds fixed)
PROBE_TABLE = {
    "REPEATED_SMALL_DEVIATION": ("REPLICATE_AT_COORDINATE", "player+region"),
    "SIGN_INSTABILITY":         ("INTERPOLATE_BETWEEN",     "player pair"),
    "LOCAL_VARIANCE_ANOMALY":   ("RESAMPLE_REGION",         "region"),
    "PLAYER_ORDER_REVERSAL":    ("CROSS_REPLICATE",         "player pair"),
    "REPEATED_OUTLIER_REGION":  ("REPEAT_OUTLIER_CELL",     "region+bin"),
    "BOUNDARY_TRANSITION_HINT": ("BISECT_BOUNDARY",         "axis"),
}

# Replication counts. Conservative and explicit; a probe is a look, not a study.
DEFAULT_REPLICATES = 8
RESAMPLE_REPLICATES = 16      # D3 asks about dispersion, which needs more n


def denormalize(axis: str, value: float, scales: Dict[str, Dict[str, float]]
                ) -> Optional[float]:
    """Map a normalized coordinate back to the raw parameter value.

    Returns None when the axis is unknown or degenerate, because emitting a
    fabricated raw value would make the spec un-runnable in a way that is hard
    to notice downstream.
    """
    s = scales.get(axis)
    if not s or s.get("span", 0) <= 0:
        return None
    return s["min"] + value * s["span"]


def build_spec(cand: Candidate, corpus) -> Dict[str, Any]:
    """The SFE-compatible experiment spec for this candidate."""
    sig = cand.primary
    kind, held = PROBE_TABLE.get(sig.detector, ("RESAMPLE_REGION", "region"))
    scales = corpus.coord_scales()

    raw_target: Dict[str, Any] = {}
    for axis, v in sorted(sig.target_coords.items()):
        raw = denormalize(axis, v, scales)
        raw_target[axis] = {"normalized": round(v, 6), "raw": raw}

    replicates = RESAMPLE_REPLICATES if kind == "RESAMPLE_REGION" \
        else DEFAULT_REPLICATES

    spec: Dict[str, Any] = {
        # ---- ordinary SFE experiment fields -----------------------------
        "procedure": "archaeon.probe.v0",
        "probe_kind": kind,
        "replicates": replicates,
        "worlds": list(sig.regions),
        "players": list(sig.players),
        "target": raw_target,
        "hold_fixed": held,
    }

    # `controls` is ALWAYS present, [] when there are none: a probe with no
    # controls and a probe whose controls were forgotten are different
    # experiments, and only an explicit empty list says which was requested.
    spec["controls"] = _controls(sig, corpus, scales)
    return spec


def probe_provenance(cand: Candidate, corpus) -> Dict[str, Any]:
    """Which policy proposed this probe. PROVENANCE -- a queue column, never
    inside the sealed spec. See the note at the top of this module."""
    sig = cand.primary
    return {"detector": sig.detector,
            "detector_version": sig.detector_version,
            "intent": sig.intent,
            "chart": corpus.chart.name,
            "co_firing_detectors": cand.detectors}


def _controls(sig: Signal, corpus, scales) -> List[Dict[str, Any]]:
    """Nearby control conditions, where the probe kind calls for one.

    A control here is a NEARBY CONDITION, not a null: Archaeon is not testing a
    hypothesis, it is asking whether the neighbourhood behaves the way the
    flagged cell does. Nothing about the control adjudicates anything.
    """
    kind = PROBE_TABLE.get(sig.detector, ("", ""))[0]
    if kind not in ("REPLICATE_AT_COORDINATE", "REPEAT_OUTLIER_CELL"):
        return []
    out: List[Dict[str, Any]] = []
    for axis, v in sorted(sig.target_coords.items()):
        for offset in (-0.05, +0.05):
            nv = v + offset
            if not (0.0 <= nv <= 1.0):
                continue
            raw = denormalize(axis, nv, scales)
            if raw is None:
                continue
            out.append({"role": "NEARBY_CONTROL", "axis": axis,
                        "normalized": round(nv, 6), "raw": raw,
                        "replicates": DEFAULT_REPLICATES // 2})
    return out


def _hash(spec: Dict[str, Any]) -> str:
    blob = json.dumps({k: v for k, v in spec.items() if k != "spec_hash"},
                      sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
