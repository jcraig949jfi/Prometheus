"""D2 SIGN INSTABILITY.

Nearby world configurations produce opposite-signed responses for the SAME
player comparison.

Grain: a (player_A, player_B, region_1, region_2) quadruple where region_1 and
region_2 are neighbours in normalized coordinate space.

  delta(r) = mean(metric | A, r) - mean(metric | B, r)

Fires when sign(delta(r1)) != sign(delta(r2)) and BOTH sides pass two
independent requirements:

  MATERIALITY  |delta| >= d2_min_magnitude_sd family SDs -- the ordering is a
               real gap, not a hair's breadth.
  RESOLUTION   the delta clears its OWN sampling error: a Welch t on the two
               players' means in that region, with the two-sided p surviving a
               Bonferroni correction across every eligible comparison in the
               corpus.

Both are needed and the v0 build had only the first. A family-SD threshold says
nothing about whether a difference of MEANS is resolvable at the n available:
at n=6 with sigma=0.1, the 0.30-family-SD bar is 0.52 standard errors, well
inside the noise, and a pair whose true delta is zero flips sign about half the
time. Calibration measured v0 firing on 98.3% of pure-null corpora. With the
resolution requirement a flip must be between two orderings that are each
individually resolved, which is a much rarer accident.

Bonferroni is over the number of ELIGIBLE comparisons, not the number that
fire, because Archaeon proposes once per corpus -- so the corpus-level
false-alarm rate is the one that matters, not the per-comparison rate.

Requires player identity AND coordinates for the neighbour relation.
"""
from __future__ import annotations

import itertools
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .. import stats
from .base import (DetectorResult, Eligibility, Signal, INTENT_DISCRIMINATE,
                   mean, stdev, variance, clamp01)

NAME = "SIGN_INSTABILITY"
VERSION = "d2.v1"
UNIT = "(player pair, region pair) comparison"


def _dist(a: Dict[str, float], b: Dict[str, float]) -> Optional[float]:
    keys = sorted(set(a) & set(b))
    if not keys:
        return None
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in keys))


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows

    if corpus.chart.player_field is None or not any(r.player for r in rows):
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("corpus carries no player identity; a player "
                            "comparison cannot be formed"),
            detail={"chart": corpus.chart.name, "rows": len(rows)}))

    if not corpus.chart.coord_fields:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("chart declares no coordinate axes, so 'nearby "
                            "world configurations' is undefined"),
            detail={"chart": corpus.chart.name}))

    scales = corpus.coord_scales()
    # region -> normalized centroid, and (player, region) -> metrics
    reg_coords: Dict[str, List[Dict[str, float]]] = defaultdict(list)
    pr: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    pr_rows: Dict[Tuple[str, str], List] = defaultdict(list)
    fam_of: Dict[str, str] = {}
    fam_metrics: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        reg_coords[r.region].append(corpus.normalized_coords(r, scales))
        pr[(r.player, r.region)].append(r.metric)
        pr_rows[(r.player, r.region)].append(r)
        fam_of[r.region] = r.family or "<nofamily>"
        fam_metrics[r.family or "<nofamily>"].append(r.metric)

    centroid = {}
    for reg, cs in reg_coords.items():
        acc: Dict[str, List[float]] = {}
        for c in cs:
            for k, v in c.items():
                acc.setdefault(k, []).append(v)
        centroid[reg] = {k: mean(v) for k, v in acc.items()}

    supported = {k for k, v in pr.items() if len(v) >= dcfg.d2_min_runs}
    players_of: Dict[str, set] = defaultdict(set)
    for (p, reg) in supported:
        players_of[reg].add(p)

    regions = sorted(centroid)
    # neighbour region pairs
    neigh: List[Tuple[str, str, float]] = []
    for r1, r2 in itertools.combinations(regions, 2):
        d = _dist(centroid[r1], centroid[r2])
        if d is not None and d <= dcfg.d2_neighbor_radius:
            neigh.append((r1, r2, d))

    units: List[Tuple[str, str, str, str, float]] = []
    for r1, r2, d in neigh:
        shared = sorted(players_of[r1] & players_of[r2])
        for a, b in itertools.combinations(shared, 2):
            units.append((a, b, r1, r2, d))

    total_units = len(units)
    if total_units == 0:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("no two regions within d2_neighbor_radius={} share "
                            "two players each supported by d2_min_runs={} "
                            "observations".format(dcfg.d2_neighbor_radius,
                                                  dcfg.d2_min_runs)),
            detail={"regions": len(regions),
                    "neighbour_region_pairs": len(neigh),
                    "supported_player_region_cells": len(supported)}))

    # Bonferroni over every eligible comparison: each unit contributes TWO
    # resolution tests (one per region), and both must survive.
    alpha_per_test = stats.bonferroni_threshold(2 * total_units, dcfg.d2_alpha)

    signals: List[Signal] = []
    for a, b, r1, r2, d in units:
        fam = fam_of.get(r1, "<nofamily>")
        scale = stdev(fam_metrics.get(fam, []))
        if scale <= 0:
            continue
        d1 = mean(pr[(a, r1)]) - mean(pr[(b, r1)])
        d2 = mean(pr[(a, r2)]) - mean(pr[(b, r2)])
        if d1 == 0 or d2 == 0 or (d1 > 0) == (d2 > 0):
            continue
        m1, m2 = abs(d1) / scale, abs(d2) / scale
        if m1 < dcfg.d2_min_magnitude_sd or m2 < dcfg.d2_min_magnitude_sd:
            continue

        # RESOLUTION: each side's delta against its own sampling error.
        _, t1, df1 = stats.welch(mean(pr[(a, r1)]), variance(pr[(a, r1)]),
                                 len(pr[(a, r1)]),
                                 mean(pr[(b, r1)]), variance(pr[(b, r1)]),
                                 len(pr[(b, r1)]))
        _, t2, df2 = stats.welch(mean(pr[(a, r2)]), variance(pr[(a, r2)]),
                                 len(pr[(a, r2)]),
                                 mean(pr[(b, r2)]), variance(pr[(b, r2)]),
                                 len(pr[(b, r2)]))
        p1, p2 = stats.t_sf(t1, df1), stats.t_sf(t2, df2)
        if not (stats.bonferroni_ok(p1, 2 * total_units, dcfg.d2_alpha)
                and stats.bonferroni_ok(p2, 2 * total_units, dcfg.d2_alpha)):
            continue

        ev = (pr_rows[(a, r1)] + pr_rows[(b, r1)] +
              pr_rows[(a, r2)] + pr_rows[(b, r2)])
        signals.append(Signal(
            detector=NAME, detector_version=VERSION,
            intent=INTENT_DISCRIMINATE,
            regions=(r1, r2), players=(a, b),
            values={"delta_region_1": d1, "delta_region_2": d2,
                    "magnitude_1_sd": m1, "magnitude_2_sd": m2,
                    "welch_t_region_1": t1, "welch_t_region_2": t2,
                    "p_region_1": p1, "p_region_2": p2,
                    "p_bonferroni_threshold": alpha_per_test,
                    "n_tests_in_corpus": 2 * total_units,
                    "coordinate_distance": d,
                    "family": fam, "family_sd": scale,
                    "n_a_r1": len(pr[(a, r1)]), "n_b_r1": len(pr[(b, r1)]),
                    "n_a_r2": len(pr[(a, r2)]), "n_b_r2": len(pr[(b, r2)])},
            thresholds={"d2_neighbor_radius": dcfg.d2_neighbor_radius,
                        "d2_min_magnitude_sd": dcfg.d2_min_magnitude_sd,
                        "d2_min_runs": dcfg.d2_min_runs,
                        "d2_alpha": dcfg.d2_alpha},
            support_n=len(ev),
            effect_norm=clamp01(min(m1, m2) / 2.0),
            # The probe targets the MIDPOINT: the sign must change somewhere
            # between r1 and r2, so that is where the record is unsettled.
            target_coords=_midpoint(centroid[r1], centroid[r2]),
            evidence_rows=tuple(r.anchor_ref() for r in ev),
        ))

    return DetectorResult(
        Eligibility(NAME, total_units, total_units, UNIT,
                    detail={"neighbour_region_pairs": len(neigh)}),
        tuple(signals))


def _midpoint(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    return {k: 0.5 * (a[k] + b[k]) for k in sorted(set(a) & set(b))}
