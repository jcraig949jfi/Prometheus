"""D4 PLAYER ORDER REVERSAL.

Relative player performance changes between related worlds.

Grain: a (player_A, player_B, region_1, region_2) quadruple where the two
regions are RELATED -- same family, or (when the chart has coordinates) within
d2's neighbour radius. Unlike D2 this detector does not require the regions to
be adjacent: a reversal between two worlds of the same family is interesting
wherever they sit.

Fires when A outranks B in one region and B outranks A in the other, and BOTH
orderings pass two independent requirements:

  MATERIALITY  |margin| >= d4_min_margin_sd family SDs.
  RESOLUTION   the margin clears its own sampling error (Welch t, Bonferroni-
               corrected across every eligible comparison in the corpus).

The v0 build had only materiality and fired on 100% of pure-null corpora: a
family-SD margin threshold does not constrain a difference of MEANS, so two
players whose true difference is zero reverse between any two regions about
half the time. A reversal is only interesting if each ordering was individually
resolved.

D4 and D2 overlap by construction: an adjacent-region reversal with large
margins satisfies both. That is intended and is NOT double evidence -- the
ranker treats co-firing detectors as one probe target (see archaeon/rank.py),
because two detectors reading the same four cells is one observation looked at
twice, not two observations.
"""
from __future__ import annotations

import itertools
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from .. import stats
from .base import (DetectorResult, Eligibility, Signal, INTENT_DISCRIMINATE,
                   mean, stdev, variance, clamp01)

NAME = "PLAYER_ORDER_REVERSAL"
VERSION = "d4.v1"
UNIT = "(player pair, related region pair) comparison"


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows

    if corpus.chart.player_field is None or not any(r.player for r in rows):
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("corpus carries no player identity; relative player "
                            "performance cannot be formed"),
            detail={"chart": corpus.chart.name, "rows": len(rows)}))

    pr: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    pr_rows: Dict[Tuple[str, str], List] = defaultdict(list)
    fam_of: Dict[str, str] = {}
    fam_metrics: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        pr[(r.player, r.region)].append(r.metric)
        pr_rows[(r.player, r.region)].append(r)
        fam_of[r.region] = r.family or "<nofamily>"
        fam_metrics[r.family or "<nofamily>"].append(r.metric)

    supported = {k for k, v in pr.items() if len(v) >= dcfg.d4_min_runs}
    players_of: Dict[str, set] = defaultdict(set)
    for (p, reg) in supported:
        players_of[reg].add(p)

    by_family: Dict[str, List[str]] = defaultdict(list)
    for reg, fam in fam_of.items():
        by_family[fam].append(reg)

    units: List[Tuple[str, str, str, str, str]] = []
    for fam, regs in by_family.items():
        for r1, r2 in itertools.combinations(sorted(regs), 2):
            shared = sorted(players_of[r1] & players_of[r2])
            for a, b in itertools.combinations(shared, 2):
                units.append((a, b, r1, r2, fam))

    total_units = len(units)
    if total_units == 0:
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("no family contains two regions that share two "
                            "players each supported by d4_min_runs={} "
                            "observations".format(dcfg.d4_min_runs)),
            detail={"families": len(by_family),
                    "supported_player_region_cells": len(supported)}))

    alpha_per_test = stats.bonferroni_threshold(2 * total_units, dcfg.d4_alpha)

    signals: List[Signal] = []
    for a, b, r1, r2, fam in units:
        scale = stdev(fam_metrics.get(fam, []))
        if scale <= 0:
            continue
        d1 = mean(pr[(a, r1)]) - mean(pr[(b, r1)])
        d2 = mean(pr[(a, r2)]) - mean(pr[(b, r2)])
        if d1 == 0 or d2 == 0 or (d1 > 0) == (d2 > 0):
            continue
        m1, m2 = abs(d1) / scale, abs(d2) / scale
        if m1 < dcfg.d4_min_margin_sd or m2 < dcfg.d4_min_margin_sd:
            continue

        _, t1, df1 = stats.welch(mean(pr[(a, r1)]), variance(pr[(a, r1)]),
                                 len(pr[(a, r1)]),
                                 mean(pr[(b, r1)]), variance(pr[(b, r1)]),
                                 len(pr[(b, r1)]))
        _, t2, df2 = stats.welch(mean(pr[(a, r2)]), variance(pr[(a, r2)]),
                                 len(pr[(a, r2)]),
                                 mean(pr[(b, r2)]), variance(pr[(b, r2)]),
                                 len(pr[(b, r2)]))
        p1, p2 = stats.t_sf(t1, df1), stats.t_sf(t2, df2)
        if not (stats.bonferroni_ok(p1, 2 * total_units, dcfg.d4_alpha)
                and stats.bonferroni_ok(p2, 2 * total_units, dcfg.d4_alpha)):
            continue

        ev = (pr_rows[(a, r1)] + pr_rows[(b, r1)] +
              pr_rows[(a, r2)] + pr_rows[(b, r2)])
        leader_1, leader_2 = (a if d1 > 0 else b), (a if d2 > 0 else b)
        signals.append(Signal(
            detector=NAME, detector_version=VERSION,
            intent=INTENT_DISCRIMINATE,
            regions=(r1, r2), players=(a, b),
            values={"margin_region_1": d1, "margin_region_2": d2,
                    "margin_1_sd": m1, "margin_2_sd": m2,
                    "welch_t_region_1": t1, "welch_t_region_2": t2,
                    "p_region_1": p1, "p_region_2": p2,
                    "p_bonferroni_threshold": alpha_per_test,
                    "n_tests_in_corpus": 2 * total_units,
                    "leader_region_1": leader_1, "leader_region_2": leader_2,
                    "family": fam, "family_sd": scale,
                    "n_a_r1": len(pr[(a, r1)]), "n_b_r1": len(pr[(b, r1)]),
                    "n_a_r2": len(pr[(a, r2)]), "n_b_r2": len(pr[(b, r2)])},
            thresholds={"d4_min_margin_sd": dcfg.d4_min_margin_sd,
                        "d4_min_runs": dcfg.d4_min_runs,
                        "d4_alpha": dcfg.d4_alpha},
            support_n=len(ev),
            effect_norm=clamp01(min(m1, m2) / 2.0),
            target_coords={},
            evidence_rows=tuple(r.anchor_ref() for r in ev),
        ))

    return DetectorResult(
        Eligibility(NAME, total_units, total_units, UNIT,
                    detail={"families": len(by_family)}),
        tuple(signals))
