"""Synthetic fossils with KNOWN properties.

The detectors are calibrated against these, not against the live corpus. A
detector tuned on real data is fitted to whatever that data happens to contain,
and its firing rate then says nothing about noise -- which is the one number
that matters for an instrument whose output is a scheduling decision.

Every generator here is seeded and reproducible. Each returns a Corpus whose
ground truth is stated in the docstring, so a test can assert the detector
found the thing that was put there and did not find the thing that was not.

Paired construction throughout: every generator that PLANTS an effect has a
sibling that plants the identical structure WITHOUT the effect. A detector that
fires on both has learned the structure, not the effect.
"""
from __future__ import annotations

import random
from typing import List, Optional

from .config import CoordinateChart
from .fossils import Corpus, FossilRow, corpus_from_rows

# A chart with BOTH a player identity and a coordinate axis, so all six
# detectors can be exercised. The live SFE chart has no player field, which is
# exactly why calibration cannot be done on the live corpus.
SYNTH_CHART = CoordinateChart(
    name="synthetic.full.v0",
    source="sfe",
    region_field="world_id",
    family_field="world_family",
    player_field="spec.owner",
    metric_field="content.score",
    coord_fields=("spec.candidate",),
)

_counter = [0]


def _row(region: str, family: str, player: Optional[str], metric: float,
         coord: Optional[float] = None, seq: Optional[int] = None) -> FossilRow:
    _counter[0] += 1
    i = _counter[0]
    return FossilRow(
        row_id="syn_{:07d}".format(i),
        source="synthetic",
        seq=seq if seq is not None else i,
        region=region, family=family, player=player, metric=metric,
        coords=({"spec.candidate": coord} if coord is not None else {}),
        anchors={"synthetic": True, "row_index": i},
    )


def _wrap(rows: List[FossilRow], name: str) -> Corpus:
    return corpus_from_rows(rows, SYNTH_CHART, source_ref="synthetic:" + name)


def reset() -> None:
    """Reset the row counter so row ids are stable per test."""
    _counter[0] = 0


# --------------------------------------------------------------------------
# PURE NULL
# --------------------------------------------------------------------------
def pure_null(seed: int = 0, n_regions: int = 8, n_players: int = 4,
              n_runs: int = 20, mu: float = 0.5, sigma: float = 0.1) -> Corpus:
    """Ground truth: NOTHING. Every observation is iid N(mu, sigma).

    Same players, same regions, same run counts as the effect corpora, so the
    only difference between this and a planted corpus is the effect itself.

    n_runs defaults to 20 so that EVERY detector is eligible on this corpus.
    A null corpus on which a detector is not eligible measures nothing about
    that detector: a 0.000 firing rate would then mean "could not fire", not
    "did not fire", which is precisely the conflation Archaeon exists to avoid.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for ri in range(n_regions):
        reg = "w{:02d}".format(ri)
        coord = ri / max(n_regions - 1, 1)
        for pi in range(n_players):
            for _ in range(n_runs):
                rows.append(_row(reg, "F", "p{}".format(pi),
                                 rng.gauss(mu, sigma), coord))
    return _wrap(rows, "pure_null")


# --------------------------------------------------------------------------
# D1: repeated small deviation
# --------------------------------------------------------------------------
def repeated_small_deviation(seed: int = 1, effect_sd: float = 0.80,
                             sigma: float = 0.1, n_runs: int = 20) -> Corpus:
    """Ground truth: cell (p0, w03) sits `effect_sd` SDs above the family.

    Every other (player, region) cell is null.

    The defaults are chosen to sit inside D1's ATTAINABLE band, not merely
    inside its configured one. With d1_min_t=2.5 the reachable floor is
    2.5/sqrt(n): at n=20 that is 0.559, so effect_sd=0.80 clears it with room
    while staying under d1_max_effect_sd=1.00. The original defaults
    (effect_sd=0.45, n_runs=8) sat in a band that was structurally EMPTY --
    the planted effect could not have fired the detector at all, and the 15%
    hit rate the first calibration measured was noise, not detection.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for ri in range(8):
        reg = "w{:02d}".format(ri)
        coord = ri / 7.0
        for pi in range(4):
            player = "p{}".format(pi)
            shift = effect_sd * sigma if (player == "p0" and reg == "w03") else 0.0
            for _ in range(n_runs):
                rows.append(_row(reg, "F", player,
                                 rng.gauss(0.5 + shift, sigma), coord))
    return _wrap(rows, "d1_effect")


def repeated_no_deviation(seed: int = 1, **kw) -> Corpus:
    """PAIRED CONTROL for D1: identical structure, zero shift."""
    c = repeated_small_deviation(seed=seed, effect_sd=0.0,
                                 **{k: v for k, v in kw.items()
                                    if k in ("sigma", "n_runs")})
    c.source_ref = "synthetic:d1_control"
    return c


# --------------------------------------------------------------------------
# D2: sign instability
# --------------------------------------------------------------------------
def sign_instability(seed: int = 2, gap: float = 0.06,
                     sigma: float = 0.05, n_runs: int = 6) -> Corpus:
    """Ground truth: in ADJACENT regions w00 and w01, the A-vs-B ordering flips.

    A beats B by `gap` in w00; B beats A by `gap` in w01. Regions w00/w01 are
    close on the coordinate axis (0.00 and 0.02 normalized) so they fall inside
    d2_neighbor_radius; all other regions are spread out and null.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    coords = {"w00": 0.0, "w01": 0.02, "w02": 0.5, "w03": 1.0}
    for reg, coord in coords.items():
        for player in ("A", "B"):
            if reg == "w00":
                shift = +gap if player == "A" else -gap
            elif reg == "w01":
                shift = -gap if player == "A" else +gap
            else:
                shift = 0.0
            for _ in range(n_runs):
                rows.append(_row(reg, "F", player,
                                 rng.gauss(0.5 + shift, sigma), coord))
    return _wrap(rows, "d2_effect")


def sign_stable(seed: int = 2, gap: float = 0.06, sigma: float = 0.05,
                n_runs: int = 6) -> Corpus:
    """PAIRED CONTROL for D2: A beats B by the SAME gap in BOTH regions.

    Same magnitudes, same adjacency, same support -- only the sign is stable.
    A detector firing here is detecting a player difference, not instability.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    coords = {"w00": 0.0, "w01": 0.02, "w02": 0.5, "w03": 1.0}
    for reg, coord in coords.items():
        for player in ("A", "B"):
            shift = 0.0
            if reg in ("w00", "w01"):
                shift = +gap if player == "A" else -gap
            for _ in range(n_runs):
                rows.append(_row(reg, "F", player,
                                 rng.gauss(0.5 + shift, sigma), coord))
    return _wrap(rows, "d2_control")


# --------------------------------------------------------------------------
# D3: local variance anomaly
# --------------------------------------------------------------------------
def variance_anomaly(seed: int = 3, ratio: float = 6.0, sigma: float = 0.08,
                     n_regions: int = 8, n_per: int = 20) -> Corpus:
    """Ground truth: region w03 has sqrt(ratio) times the SD of every other."""
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for ri in range(n_regions):
        reg = "w{:02d}".format(ri)
        coord = ri / max(n_regions - 1, 1)
        s = sigma * (ratio ** 0.5) if reg == "w03" else sigma
        for _ in range(n_per):
            rows.append(_row(reg, "F", "p0", rng.gauss(0.5, s), coord))
    return _wrap(rows, "d3_effect")


def variance_equal(seed: int = 3, sigma: float = 0.08, n_regions: int = 8,
                   n_per: int = 20) -> Corpus:
    """PAIRED CONTROL for D3: identical structure, every region same SD."""
    c = variance_anomaly(seed=seed, ratio=1.0, sigma=sigma,
                         n_regions=n_regions, n_per=n_per)
    c.source_ref = "synthetic:d3_control"
    return c


# --------------------------------------------------------------------------
# D4: player order reversal
# --------------------------------------------------------------------------
def order_reversal(seed: int = 4, gap: float = 0.08, sigma: float = 0.04,
                   n_runs: int = 6) -> Corpus:
    """Ground truth: A > B in w00, B > A in w05, both same family, both by `gap`.

    Unlike D2's corpus the regions are FAR apart on the axis, so this is a
    reversal between related worlds rather than an adjacency instability.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    coords = {"w00": 0.0, "w05": 0.9}
    for reg, coord in coords.items():
        for player in ("A", "B"):
            if reg == "w00":
                shift = +gap if player == "A" else -gap
            else:
                shift = -gap if player == "A" else +gap
            for _ in range(n_runs):
                rows.append(_row(reg, "F", player,
                                 rng.gauss(0.5 + shift, sigma), coord))
    return _wrap(rows, "d4_effect")


def order_stable(seed: int = 4, gap: float = 0.08, sigma: float = 0.04,
                 n_runs: int = 6) -> Corpus:
    """PAIRED CONTROL for D4: A beats B in BOTH regions by the same gap."""
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for reg, coord in (("w00", 0.0), ("w05", 0.9)):
        for player in ("A", "B"):
            shift = +gap if player == "A" else -gap
            for _ in range(n_runs):
                rows.append(_row(reg, "F", player,
                                 rng.gauss(0.5 + shift, sigma), coord))
    return _wrap(rows, "d4_control")


# --------------------------------------------------------------------------
# D5: repeated outlier region
# --------------------------------------------------------------------------
def repeated_outliers(seed: int = 5, n_outliers: int = 5,
                      offset_sd: float = 12.0, sigma: float = 0.05) -> Corpus:
    """Ground truth: region w02 holds `n_outliers` observations far from the
    family's robust baseline; every other row is null.

    The offset is deliberately large: D5 asks about REPEATED far-from-baseline
    values, so the planted rows must clear a robust z of 3.5 individually.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for ri in range(8):
        reg = "w{:02d}".format(ri)
        coord = ri / 7.0
        for _ in range(12):
            rows.append(_row(reg, "F", "p0", rng.gauss(0.5, sigma), coord))
    for _ in range(n_outliers):
        rows.append(_row("w02", "F", "p0",
                         0.5 + offset_sd * sigma, 2 / 7.0))
    return _wrap(rows, "d5_effect")


def no_outliers(seed: int = 5, sigma: float = 0.05) -> Corpus:
    """PAIRED CONTROL for D5: same shape and same row count, no offset."""
    c = repeated_outliers(seed=seed, n_outliers=5, offset_sd=0.0, sigma=sigma)
    c.source_ref = "synthetic:d5_control"
    return c


# --------------------------------------------------------------------------
# D6: boundary / transition hint
# --------------------------------------------------------------------------
def boundary_step(seed: int = 6, step: float = 0.5, sigma: float = 0.03,
                  n_per_bin: int = 10) -> Corpus:
    """Ground truth: a step of `step` in the metric at normalized coordinate 0.5.

    Rows are laid on a fine coordinate grid; below 0.5 the mean is 0.5, above
    it is 0.5 + step. The gap between the bins straddling the step is small, so
    a large jump across a small gap is exactly what D6 looks for.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for i in range(26):
        coord = i / 25.0
        base = 0.5 + (step if coord >= 0.5 else 0.0)
        for _ in range(n_per_bin):
            rows.append(_row("w{:02d}".format(i), "F", "p0",
                             rng.gauss(base, sigma), coord))
    return _wrap(rows, "d6_effect")


def boundary_smooth(seed: int = 6, sigma: float = 0.03,
                    n_per_bin: int = 10) -> Corpus:
    """PAIRED CONTROL for D6: no step; the metric is flat across the axis."""
    c = boundary_step(seed=seed, step=0.0, sigma=sigma, n_per_bin=n_per_bin)
    c.source_ref = "synthetic:d6_control"
    return c


def boundary_gradual(seed: int = 6, total: float = 0.5, sigma: float = 0.03,
                     n_per_bin: int = 10) -> Corpus:
    """SECOND CONTROL for D6: the SAME total change, spread smoothly.

    This is the control that matters. A detector that fires here is detecting a
    trend, not a boundary -- the end-to-end change is identical to
    boundary_step and only its localization differs.
    """
    reset()
    rng = random.Random(seed)
    rows: List[FossilRow] = []
    for i in range(26):
        coord = i / 25.0
        base = 0.5 + total * coord
        for _ in range(n_per_bin):
            rows.append(_row("w{:02d}".format(i), "F", "p0",
                             rng.gauss(base, sigma), coord))
    return _wrap(rows, "d6_control_gradual")
