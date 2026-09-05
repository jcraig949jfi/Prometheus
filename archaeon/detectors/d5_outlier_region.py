"""D5 REPEATED OUTLIER REGION.

Similar world/player configurations repeatedly produce observations far from
that family's recent baseline.

Grain: a CONFIGURATION CELL = (family, region, coordinate bin), where the bin
is the normalized coordinate rounded to d5_coord_bin. Cells are the "similar
configurations"; the family supplies the baseline.

Baseline is median + MAD, not mean + SD, for a specific reason: the thing being
detected is outliers, and a mean/SD baseline computed over data containing them
is inflated by the very rows it is meant to flag. MAD is not.

Fires when a cell contains d5_min_repeats or more observations whose robust z
exceeds d5_outlier_z. ONE extreme observation is not this detector's business
-- REPEATED is the word in the name.

A family whose MAD is zero (more than half its values identical) produces
robust_z = 0 everywhere and cannot fire; that is reported as a degenerate
baseline rather than as an absence of outliers.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple

from .base import (DetectorResult, Eligibility, Signal, INTENT_REPLICATE,
                   mean, median, mad, robust_z, clamp01)

NAME = "REPEATED_OUTLIER_REGION"
VERSION = "d5.v0"
UNIT = "(family, region, coordinate bin) configuration cell"


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows
    scales = corpus.coord_scales()

    fam_rows: Dict[str, List] = defaultdict(list)
    for r in rows:
        fam_rows[r.family or "<nofamily>"].append(r)

    def cell_key(r) -> Tuple[str, str, Tuple[Tuple[str, float], ...]]:
        nc = corpus.normalized_coords(r, scales)
        binned = tuple(sorted(
            (k, round(v / dcfg.d5_coord_bin) * dcfg.d5_coord_bin)
            for k, v in nc.items()))
        return (r.family or "<nofamily>", r.region, binned)

    cells: Dict[Any, List] = defaultdict(list)
    for r in rows:
        cells[cell_key(r)].append(r)
    total_units = len(cells)

    big_families = {f for f, rs in fam_rows.items()
                    if len(rs) >= dcfg.d5_min_family_n}
    degenerate = {f for f in big_families if mad([r.metric for r in fam_rows[f]]) <= 0}
    usable_families = big_families - degenerate

    eligible = [k for k, v in cells.items()
                if k[0] in usable_families and len(v) >= dcfg.d5_min_repeats]

    if not eligible:
        reason = ("no configuration cell has d5_min_repeats={} observations "
                  "inside a family of at least d5_min_family_n={} with a "
                  "non-degenerate MAD baseline"
                  .format(dcfg.d5_min_repeats, dcfg.d5_min_family_n))
        return DetectorResult(Eligibility(
            NAME, 0, total_units, UNIT, blocked_reason=reason,
            detail={"families": len(fam_rows),
                    "families_big_enough": len(big_families),
                    "families_with_degenerate_MAD": sorted(degenerate),
                    "largest_cell_n": max((len(v) for v in cells.values()),
                                          default=0)}))

    signals: List[Signal] = []
    baselines = {f: (median([r.metric for r in fam_rows[f]]),
                     mad([r.metric for r in fam_rows[f]]))
                 for f in usable_families}

    for key in sorted(eligible, key=lambda k: (k[0], k[1], k[2])):
        fam, region, binned = key
        med, m = baselines[fam]
        cell = sorted(cells[key], key=lambda r: (r.seq, r.row_id))
        zs = [robust_z(r.metric, med, m) for r in cell]
        outliers = [(r, z) for r, z in zip(cell, zs)
                    if abs(z) >= dcfg.d5_outlier_z]
        if len(outliers) < dcfg.d5_min_repeats:
            continue

        signals.append(Signal(
            detector=NAME, detector_version=VERSION,
            intent=INTENT_REPLICATE,
            regions=(region,),
            players=tuple(sorted({r.player for r, _ in outliers if r.player})),
            values={"family": fam,
                    "coordinate_bin": [list(b) for b in binned],
                    "cell_n": len(cell),
                    "n_outliers": len(outliers),
                    "max_abs_robust_z": max(abs(z) for _, z in outliers),
                    "mean_outlier_robust_z": mean([z for _, z in outliers]),
                    "family_median": med, "family_mad": m,
                    "family_n": len(fam_rows[fam])},
            thresholds={"d5_outlier_z": dcfg.d5_outlier_z,
                        "d5_min_repeats": dcfg.d5_min_repeats,
                        "d5_min_family_n": dcfg.d5_min_family_n,
                        "d5_coord_bin": dcfg.d5_coord_bin},
            support_n=len(cell),
            effect_norm=clamp01(max(abs(z) for _, z in outliers) / 10.0),
            target_coords={k: v for k, v in binned},
            evidence_rows=tuple(r.anchor_ref() for r, _ in outliers),
        ))

    return DetectorResult(
        Eligibility(NAME, len(eligible), total_units, UNIT,
                    detail={"usable_families": len(usable_families),
                            "families_with_degenerate_MAD": sorted(degenerate)}),
        tuple(signals))
