"""D3 LOCAL VARIANCE ANOMALY.

A region of world/player parameter space has materially different dispersion
from its recent neighbourhood.

Grain: a REGION. Its sample variance is compared to the pooled variance of its
k nearest regions in normalized coordinate space -- the region itself excluded
from that pool, for the same reason as D1: a region cannot be part of the
baseline it is being tested against.

Fires when the ratio leaves [d3_low_ratio, d3_high_ratio], in EITHER direction.
Unusually LOW dispersion is as much a reason to look again as unusually high:
a region that has stopped varying is a region where something is pinning the
outcome, and the charter forbids reading that as "settled".

This detector needs no player identity. On the SFE corpus as it stands, it is
the only one of the six that is eligible at all.

Neighbourhood when the chart declares no coordinates: all OTHER regions in the
same family. That is a coarser neighbourhood and it is labelled as such in the
signal, because a threshold tuned for k nearest neighbours means something
different when the "neighbourhood" is the whole family.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .base import (DetectorResult, Eligibility, Signal, INTENT_DISCRIMINATE,
                   mean, variance, stdev, clamp01)

NAME = "LOCAL_VARIANCE_ANOMALY"
VERSION = "d3.v0"
UNIT = "region"


def _dist(a: Dict[str, float], b: Dict[str, float]) -> Optional[float]:
    keys = sorted(set(a) & set(b))
    if not keys:
        return None
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in keys))


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows
    scales = corpus.coord_scales()

    by_region: Dict[str, List] = defaultdict(list)
    for r in rows:
        by_region[r.region].append(r)

    total_units = len(by_region)
    if total_units == 0:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT, blocked_reason="corpus is empty"))

    centroid: Dict[str, Dict[str, float]] = {}
    fam_of: Dict[str, str] = {}
    for reg, rs in by_region.items():
        acc: Dict[str, List[float]] = {}
        for r in rs:
            for k, v in corpus.normalized_coords(r, scales).items():
                acc.setdefault(k, []).append(v)
        centroid[reg] = {k: mean(v) for k, v in acc.items()}
        fam_of[reg] = rs[0].family or "<nofamily>"

    has_coords = bool(corpus.chart.coord_fields) and any(centroid.values())
    neighbourhood_kind = "k_nearest" if has_coords else "family"

    big_enough = [reg for reg, rs in by_region.items()
                  if len(rs) >= dcfg.d3_min_n_region]

    # A region is ELIGIBLE only when it is big enough AND has a big enough
    # neighbourhood to be compared against.
    eligible: List[str] = []
    neighbours_of: Dict[str, List[str]] = {}
    for reg in sorted(big_enough):
        nb = _neighbours(reg, by_region, centroid, fam_of, dcfg, has_coords)
        n_pool = sum(len(by_region[o]) for o in nb)
        if n_pool >= dcfg.d3_min_n_neighborhood:
            eligible.append(reg)
            neighbours_of[reg] = nb

    if not eligible:
        largest = max((len(v) for v in by_region.values()), default=0)
        return DetectorResult(Eligibility(
            NAME, 0, total_units, UNIT,
            blocked_reason=("no region has d3_min_n_region={} observations "
                            "AND a neighbourhood of d3_min_n_neighborhood={}; "
                            "largest region has {}"
                            .format(dcfg.d3_min_n_region,
                                    dcfg.d3_min_n_neighborhood, largest)),
            detail={"regions": total_units, "largest_region_n": largest,
                    "regions_big_enough": len(big_enough),
                    "neighbourhood_kind": neighbourhood_kind}))

    signals: List[Signal] = []
    for reg in eligible:
        rs = by_region[reg]
        vals = [r.metric for r in rs]
        nb = neighbours_of[reg]
        pool = [x.metric for o in nb for x in by_region[o]]

        v_reg = variance(vals)
        v_nb = variance(pool)
        if v_nb <= 0:
            # A neighbourhood with zero dispersion gives no ratio. Reporting
            # "infinitely more variable" from a degenerate denominator would be
            # an artefact of the baseline, not a property of the region.
            continue
        ratio = v_reg / v_nb
        if dcfg.d3_low_ratio <= ratio <= dcfg.d3_high_ratio:
            continue

        direction = "HIGHER_DISPERSION" if ratio > dcfg.d3_high_ratio \
            else "LOWER_DISPERSION"
        # Rank magnitude: distance from the band, in log space so that a
        # 4x-under and a 4x-over anomaly rank the same.
        excess = (math.log(ratio / dcfg.d3_high_ratio)
                  if ratio > dcfg.d3_high_ratio
                  else math.log(dcfg.d3_low_ratio / ratio))

        signals.append(Signal(
            detector=NAME, detector_version=VERSION,
            intent=INTENT_DISCRIMINATE,
            regions=(reg,), players=(),
            values={"region_variance": v_reg,
                    "neighbourhood_variance": v_nb,
                    "variance_ratio": ratio,
                    "direction": direction,
                    "region_n": len(vals),
                    "region_sd": stdev(vals),
                    "neighbourhood_n": len(pool),
                    "neighbourhood_sd": stdev(pool),
                    "neighbourhood_kind": neighbourhood_kind,
                    "neighbours": list(nb),
                    "family": fam_of[reg]},
            thresholds={"d3_high_ratio": dcfg.d3_high_ratio,
                        "d3_low_ratio": dcfg.d3_low_ratio,
                        "d3_min_n_region": dcfg.d3_min_n_region,
                        "d3_min_n_neighborhood": dcfg.d3_min_n_neighborhood,
                        "d3_neighbors_k": dcfg.d3_neighbors_k},
            support_n=len(vals),
            effect_norm=clamp01(excess / math.log(10.0)),
            target_coords=dict(centroid[reg]),
            evidence_rows=tuple(r.anchor_ref() for r in rs[:64]),
        ))

    return DetectorResult(
        Eligibility(NAME, len(eligible), total_units, UNIT,
                    detail={"neighbourhood_kind": neighbourhood_kind,
                            "regions_big_enough": len(big_enough)}),
        tuple(signals))


def _neighbours(reg, by_region, centroid, fam_of, dcfg, has_coords) -> List[str]:
    if has_coords:
        cand = []
        for other in by_region:
            if other == reg:
                continue
            d = _dist(centroid[reg], centroid[other])
            if d is not None:
                cand.append((d, other))
        cand.sort(key=lambda t: (t[0], t[1]))
        return [o for _, o in cand[:dcfg.d3_neighbors_k]]
    fam = fam_of[reg]
    return sorted(o for o in by_region if o != reg and fam_of[o] == fam)
