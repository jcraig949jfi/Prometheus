"""D1 REPEATED SMALL DEVIATION.

The same player/world relationship shows a small but consistently nonzero
deviation across multiple independent runs.

Grain: a CELL = (player, region). Its deviation is measured against the
baseline of its own family, EXCLUDING the cell itself -- a cell must not be
part of the baseline it is being compared to, or a large cell drags the
baseline toward itself and hides exactly the deviation being looked for.

Conditions, all required:

  1. SMALL:      d1_min_effect_sd <= |dev| <= d1_max_effect_sd, in family SD
                 units. The upper bound matters: a huge deviation is not this
                 detector's business and firing on one misroutes the probe.
  2. CONSISTENT: the cell is split into d1_consistency_blocks contiguous
                 blocks in ledger order, and every BLOCK MEAN deviates the
                 same way.
  3. NOT NOISE:  the cell's two-sided t p-value survives a Bonferroni
                 correction across every eligible cell in the corpus.

CONSISTENCY IS BLOCK-WISE, and that is a correction, not a detail. The v0
build required every individual observation to fall on the same side of the
baseline. That requirement gets HARDER as evidence accumulates -- which is
backwards for a detector whose whole premise is repetition. For a real 0.8-SD
effect at n=20 the probability that all 20 observations share a sign is 0.0086,
so v0 could not fire on the very effect it was built to find, and calibration
measured a hit rate of 0.000. Blocks fix the direction: each block mean is an
independent repetition of the cell, so agreement among block means is what
"consistent across runs" actually means, and more runs now help.

REACHABILITY (added after calibration). Because t = effect_sd * sqrt(n), a cell
with n runs cannot reach ``d1_min_t`` unless effect_sd >= d1_min_t / sqrt(n).
The first calibration run measured this detector firing on 43% of pure-null
corpora and only 15% of planted ones -- because with n <= 9 the required floor
sat ABOVE d1_max_effect_sd, making the band EMPTY. Nothing could satisfy it
except a cell whose internal scatter happened to be small, which is noise. The
detector now computes that floor before testing anything and reports a cell
whose band is empty as NOT ELIGIBLE, rather than letting an unreachable gate
masquerade as a quiet one.

MULTIPLICITY. A corpus contains many cells. A per-cell alpha of 0.05 over 32
cells is a corpus-level false-alarm rate near 80%, and Archaeon proposes per
CORPUS, so the corpus-level rate is the one that matters.

Requires a player identity. On a corpus with none, eligibility is zero and that
is reported as a property of the CORPUS, not as a reading.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from .. import stats
from .base import (DetectorResult, Eligibility, Signal, INTENT_REPLICATE,
                   mean, sem, stdev, variance, clamp01)

NAME = "REPEATED_SMALL_DEVIATION"
VERSION = "d1.v1"
UNIT = "(player, region) cell"

# Corpus-level false-alarm budget, split across eligible cells by Bonferroni.
FAMILY_ALPHA = 0.05


def detect(corpus, dcfg) -> DetectorResult:
    rows = corpus.rows

    if corpus.chart.player_field is None or not any(r.player for r in rows):
        return DetectorResult(Eligibility(
            NAME, 0, 0, UNIT,
            blocked_reason=("corpus carries no player identity; this detector's "
                            "unit cannot be formed"),
            detail={"chart": corpus.chart.name,
                    "player_field": corpus.chart.player_field,
                    "rows": len(rows)}))

    fam_rows: Dict[str, List] = defaultdict(list)
    for r in rows:
        fam_rows[r.family or "<nofamily>"].append(r)

    cells: Dict[Tuple[str, str, str], List] = defaultdict(list)
    for r in rows:
        cells[(r.family or "<nofamily>", r.player, r.region)].append(r)

    total_units = len(cells)
    big = [k for k, v in cells.items() if len(v) >= dcfg.d1_min_runs]

    # ---- reachability gate ------------------------------------------------
    # A cell is eligible only if its n makes the configured band non-empty.
    eligible: List[Tuple[str, str, str]] = []
    floors: Dict[int, float] = {}
    for k in big:
        n = len(cells[k])
        floor = floors.setdefault(n, stats.attainable_effect_floor(dcfg.d1_min_t, n))
        if floor <= dcfg.d1_max_effect_sd:
            eligible.append(k)

    if not eligible:
        largest = max((len(v) for v in cells.values()), default=0)
        if not big:
            reason = ("no (player, region) cell has d1_min_runs={} repeated "
                      "observations; largest cell has {}"
                      .format(dcfg.d1_min_runs, largest))
        else:
            need = stats.attainable_effect_floor(dcfg.d1_min_t, largest)
            reason = ("every cell's effect band is EMPTY: with n={} runs an "
                      "effect must reach {:.3f} SD to attain d1_min_t={}, but "
                      "d1_max_effect_sd={} caps it below that. No input could "
                      "fire this detector."
                      .format(largest, need, dcfg.d1_min_t,
                              dcfg.d1_max_effect_sd))
        return DetectorResult(Eligibility(
            NAME, 0, total_units, UNIT, blocked_reason=reason,
            detail={"largest_cell_n": largest,
                    "cells_meeting_min_runs": len(big),
                    "d1_min_runs": dcfg.d1_min_runs,
                    "d1_min_t": dcfg.d1_min_t,
                    "d1_max_effect_sd": dcfg.d1_max_effect_sd,
                    "attainable_effect_floor_by_n": floors,
                    "reachability": "EMPTY_BAND" if big else "INSUFFICIENT_RUNS"}))

    n_tests = len(eligible)
    alpha_per_test = stats.bonferroni_threshold(n_tests, FAMILY_ALPHA)

    signals: List[Signal] = []
    for key in sorted(eligible):
        fam, player, region = key
        cell = sorted(cells[key], key=lambda r: (r.seq, r.row_id))
        others = [r.metric for r in fam_rows[fam]
                  if not (r.player == player and r.region == region)]
        if len(others) < dcfg.d1_min_runs:
            continue
        base = mean(others)
        scale = stdev(others)
        if scale <= 0:
            # A family with no dispersion supplies no unit in which "small"
            # is defined. Skipped rather than fired.
            continue

        devs = [r.metric - base for r in cell]
        m = mean(devs)
        se = sem(devs)
        eff_sd = abs(m) / scale
        n = len(devs)

        # Block-wise consistency: contiguous blocks in ledger order, so each
        # block is an independent stretch of the cell's history.
        k = max(int(dcfg.d1_consistency_blocks), 2)
        size = n // k
        block_means = [mean(devs[i * size:(i + 1) * size]) for i in range(k)]             if size >= 1 else []
        signs = {(1 if b > 0 else (-1 if b < 0 else 0)) for b in block_means}
        consistent = bool(block_means) and len(signs) == 1 and 0 not in signs
        t = (abs(m) / se) if se > 0 else float("inf")
        p = stats.t_sf(t, n - 1)

        if not (dcfg.d1_min_effect_sd <= eff_sd <= dcfg.d1_max_effect_sd):
            continue
        if dcfg.d1_require_sign_agreement and not consistent:
            continue
        if t < dcfg.d1_min_t:
            continue
        if not stats.bonferroni_ok(p, n_tests, FAMILY_ALPHA):
            continue

        signals.append(Signal(
            detector=NAME, detector_version=VERSION,
            intent=INTENT_REPLICATE,
            regions=(region,), players=(player,),
            values={"cell_mean_deviation": m,
                    "effect_sd_units": eff_sd,
                    "t_statistic": t,
                    "p_two_sided": p,
                    "p_bonferroni_threshold": alpha_per_test,
                    "n_tests_in_corpus": n_tests,
                    "sign_consistent": consistent,
                    "consistency_blocks": k,
                    "block_mean_deviations": block_means,
                    "cell_n": n,
                    "attainable_effect_floor": floors.get(n),
                    "family": fam,
                    "family_baseline_mean": base,
                    "family_baseline_sd": scale,
                    "family_baseline_n": len(others)},
            thresholds={"d1_min_effect_sd": dcfg.d1_min_effect_sd,
                        "d1_max_effect_sd": dcfg.d1_max_effect_sd,
                        "d1_min_t": dcfg.d1_min_t,
                        "d1_min_runs": dcfg.d1_min_runs,
                        "d1_require_sign_agreement":
                            dcfg.d1_require_sign_agreement,
                        "d1_consistency_blocks": dcfg.d1_consistency_blocks,
                        "family_alpha": FAMILY_ALPHA},
            support_n=n,
            effect_norm=clamp01(eff_sd / max(dcfg.d1_max_effect_sd, 1e-12)),
            target_coords=_centroid(corpus, cell),
            evidence_rows=tuple(r.anchor_ref() for r in cell),
        ))

    return DetectorResult(
        Eligibility(NAME, len(eligible), total_units, UNIT,
                    detail={"d1_min_runs": dcfg.d1_min_runs,
                            "n_tests": n_tests,
                            "bonferroni_alpha_per_test": alpha_per_test,
                            "attainable_effect_floor_by_n": floors}),
        tuple(signals))


def _centroid(corpus, cell) -> Dict[str, float]:
    scales = corpus.coord_scales()
    acc: Dict[str, List[float]] = {}
    for r in cell:
        for k, v in corpus.normalized_coords(r, scales).items():
            acc.setdefault(k, []).append(v)
    return {k: mean(v) for k, v in acc.items()}
