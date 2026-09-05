"""Every threshold Archaeon uses, in one inspectable place.

Nothing here is learned, fitted, or chosen by a model. These are conservative
hand-set numbers. Their consequences are MEASURED by ``archaeon/calibrate.py``
against synthetic fossils; the measured null firing rates live in
``archaeon/docs/CALIBRATION.md``. If a number here is wrong, the calibration
report is where that becomes visible.

Threshold changes are versioned: bump ``THRESHOLDS_VERSION`` whenever any value
below changes, because the version is written into every proposal's provenance
and is what makes an old proposal re-derivable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, Tuple

THRESHOLDS_VERSION = "archaeon.thresholds.v0"


# --------------------------------------------------------------------------
# Coordinate chart: how raw fossil fields become (region, coords, player,
# metric). This is the ONLY place field names from SFE/PEW are interpreted.
# A chart is data, not code, so a new substrate is a new chart -- not a new
# detector.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class CoordinateChart:
    name: str
    source: str                       # 'sfe' | 'pew'
    region_field: str                 # coarse locality (a world)
    family_field: Optional[str]       # coarser locality (a world family)
    player_field: Optional[str]       # player identity; None = absent in corpus
    metric_field: str                 # the numeric observable
    coord_fields: Tuple[str, ...]     # numeric parameter coordinates


# The chart matching today's SFE engine.db: experiments.spec carries a numeric
# `candidate` coordinate, observations.content carries `score`, and there is no
# player identity in the record at all (measured 2026-09-05: spec.owner is NULL
# on 2934/2934 joined rows). player_field=None is a statement of fact about the
# corpus, and it is what makes the player-dependent detectors report
# NOT_ELIGIBLE instead of silently returning nothing.
SFE_SCORE_CHART = CoordinateChart(
    name="sfe.candidate_score.v0",
    source="sfe",
    region_field="world_id",
    family_field="world_family",
    player_field=None,
    metric_field="content.score",
    coord_fields=("spec.candidate",),
)

# The chart for PEW player fossils: phenotype.score is the observable and
# genome_hash groups players into families.
PEW_PHENOTYPE_CHART = CoordinateChart(
    name="pew.phenotype_score.v0",
    source="pew",
    region_field="sfe_world_id",
    family_field="world_family",
    player_field="player_id",
    metric_field="phenotype.score",
    coord_fields=(),
)

CHARTS = {c.name: c for c in (SFE_SCORE_CHART, PEW_PHENOTYPE_CHART)}
DEFAULT_CHART = SFE_SCORE_CHART.name


# --------------------------------------------------------------------------
# Detector thresholds. Deliberately conservative: Archaeon proposing nothing is
# a fine outcome (it explores instead); Archaeon proposing on noise costs a
# Vivarium slot and pollutes the queue's provenance.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class DetectorConfig:
    # ---- shared support requirements ------------------------------------
    min_runs_per_cell: int = 3
    min_cells: int = 2

    # ---- D1 REPEATED_SMALL_DEVIATION ------------------------------------
    # "small but consistently nonzero". Effect measured in units of the
    # family metric SD, so the threshold is scale-free.
    #
    # REACHABILITY. t = effect_sd * sqrt(n), so the OPERATIVE lower edge of the
    # band is max(d1_min_effect_sd, d1_min_t / sqrt(n)) -- not d1_min_effect_sd
    # alone. With d1_min_t=2.5 and d1_min_runs=16 that floor is 0.625, so the
    # attainable band is [0.625, 1.00] and non-empty. The v0 values
    # (min_t=3.0, min_runs=4) gave a floor of 1.50 against a cap of 1.00: an
    # EMPTY band that no input could satisfy, which calibration measured as a
    # 43% null firing rate and a 15% hit rate. The detector now refuses to
    # report eligibility when the band is empty.
    d1_enabled: bool = True
    d1_min_effect_sd: float = 0.10
    d1_max_effect_sd: float = 1.00    # above this it is not SMALL, out of scope
    d1_min_t: float = 2.5             # |mean| / sem
    d1_require_sign_agreement: bool = True
    d1_consistency_blocks: int = 4    # agreement is over BLOCK means, not over
                                      # individual observations: the latter gets
                                      # harder as evidence accumulates, which is
                                      # backwards for a repetition detector
    d1_min_runs: int = 16             # sets the reachable floor at 0.625 SD

    # ---- D2 SIGN_INSTABILITY --------------------------------------------
    # Opposite-signed player-pair responses in NEARBY regions.
    #
    # TWO separate requirements, and the v0 build had only the first:
    #   MATERIALITY -- each side's |delta| >= d2_min_magnitude_sd family SDs,
    #                  so the flip is between two real orderings; and
    #   RESOLUTION  -- each side's delta must clear its OWN sampling error
    #                  (Welch t, Bonferroni-corrected across the corpus).
    # Family SD says nothing about whether a difference of MEANS is resolvable:
    # at n=6 and sigma=0.1 the 0.30-family-SD threshold is 0.52 standard errors,
    # i.e. inside the noise. Calibration measured the v0 build firing on 98% of
    # pure-null corpora.
    d2_enabled: bool = True
    d2_neighbor_radius: float = 0.15  # normalized coordinate distance
    d2_min_magnitude_sd: float = 0.30
    d2_min_runs: int = 3
    d2_alpha: float = 0.05            # corpus-level, split by Bonferroni

    # ---- D3 LOCAL_VARIANCE_ANOMALY --------------------------------------
    d3_enabled: bool = True
    d3_neighbors_k: int = 4
    d3_high_ratio: float = 3.0        # var(region) / var(neighborhood)
    d3_low_ratio: float = 0.3333
    d3_min_n_region: int = 8
    d3_min_n_neighborhood: int = 16

    # ---- D4 PLAYER_ORDER_REVERSAL ---------------------------------------
    # Same two-part requirement as D2, for the same reason: the v0 build fired
    # on 100% of pure-null corpora because a family-SD margin threshold does
    # not constrain a difference of means.
    d4_enabled: bool = True
    d4_min_margin_sd: float = 0.25
    d4_min_runs: int = 3
    d4_alpha: float = 0.05            # corpus-level, split by Bonferroni

    # ---- D5 REPEATED_OUTLIER_REGION -------------------------------------
    # Robust baseline: a few outliers must not inflate the baseline that is
    # supposed to detect them.
    d5_enabled: bool = True
    d5_outlier_z: float = 3.5         # 0.6745 * (x - median) / MAD
    d5_min_repeats: int = 3
    d5_min_family_n: int = 30
    d5_coord_bin: float = 0.05

    # ---- D6 BOUNDARY_TRANSITION_HINT ------------------------------------
    # A BOUNDARY is a step that is large relative to the OTHER steps along the
    # axis. Measuring it only against local scatter cannot separate a boundary
    # from a smooth trend: calibration measured the v0 build firing on 83% of
    # gradual-trend corpora carrying the same end-to-end change as the planted
    # step. d6_min_trend_ratio adds the missing comparison -- the step must
    # exceed the axis's own median adjacent step by this factor.
    d6_enabled: bool = True
    d6_max_gap: float = 0.10          # adjacent means adjacent
    d6_min_jump_sd: float = 1.50      # vs local scatter
    d6_min_trend_ratio: float = 4.0   # vs the axis's median adjacent step
    d6_min_n_side: int = 5
    d6_min_steps_for_trend: int = 6   # steps needed before a median step means
                                      # anything; below this, D6 is not eligible


@dataclass(frozen=True)
class CadenceConfig:
    """Cadence is enforced in PostgreSQL; these are the numbers it enforces."""
    max_per_utc_day: int = 6
    min_separation_seconds: int = 4 * 3600
    autonomous_actor: str = "archaeon"
    # Quota namespace. The cap, the separation and the serializing gate are all
    # scoped to a lane, so a test lane exercises the real database mechanism
    # without consuming or colliding with production quota.
    lane: str = "prod"
    # Human-created experiments do not consume Archaeon's quota. created_by is
    # the discriminator and the DB constraint is scoped to created_by='archaeon'.
    quota_applies_to: Tuple[str, ...] = ("archaeon",)


@dataclass(frozen=True)
class ExplorationConfig:
    """Coverage-biased fallback. Simple enough to audit by hand."""
    # A cell is UNDER-SAMPLED if its count is at or below this quantile of the
    # occupied-cell count distribution. Never-sampled legal cells always
    # qualify and are preferred.
    undersampled_quantile: float = 0.25
    prefer_never_sampled: bool = True
    # Cap the candidate set so candidate_set_hash stays meaningful and the
    # choice stays inspectable by hand.
    max_candidates: int = 512


@dataclass(frozen=True)
class ArchaeonConfig:
    chart: str = DEFAULT_CHART
    # Archaeon reads a deterministic window, never "everything", so two runs
    # against a growing corpus differ for a recorded reason.
    lookback_rows: int = 5000
    detectors: DetectorConfig = field(default_factory=DetectorConfig)
    cadence: CadenceConfig = field(default_factory=CadenceConfig)
    exploration: ExplorationConfig = field(default_factory=ExplorationConfig)

    # Deterministic ranking weights: they decide WHICH probe is proposed when
    # several signals fire. They are not evidence weights and carry no
    # scientific meaning.
    rank_weights: Dict[str, float] = field(default_factory=lambda: {
        "DISCRIMINATE": 3.0,
        "REFINE_BOUNDARY": 2.5,
        "REPLICATE": 1.0,
        "effect": 1.0,      # already normalized to [0, 1]
        "support": 0.5,     # already normalized to [0, 1]
    })

    def fingerprint(self) -> str:
        """Content hash of the whole configuration.

        Written into every proposal, so two proposals produced under different
        rules are distinguishable without diffing the repository.
        """
        blob = json.dumps(asdict(self), sort_keys=True,
                          separators=(",", ":"), default=str)
        return "cfg:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


DEFAULT = ArchaeonConfig()


# Phrases Archaeon is structurally forbidden from emitting, checked against
# every queue record before it is written (archaeon/queue.py). This tuple is
# the mechanical form of the charter's NEGATIVE AUTHORITY section.
FORBIDDEN_CLAIM_PATTERNS = (
    r"nothing\s+(is\s+)?interesting",
    r"no(thing)?\s+\w*\s*interesting\s+(exists|here)",
    r"lineage\s+is\s+(exhausted|dead|finished|over)",
    r"\bexhausted\b",
    r"do\s+not\s+run\s+(any\s+)?further",
    r"stop\s+(further\s+|running\s+)?experiment",
    r"(is|been|was)\s+disproven",
    r"\brefut(ed|es)\b",
    r"no\s+(further\s+)?(signal|phenomenon|effect)\s+(exists|remains)",
    r"(phenomenon|effect|discovery)\s+(has\s+been\s+|was\s+)?discovered",
    r"\bconfirms?\s+the\s+hypothesis\b",
    r"\bproves?\s+that\b",
    r"\bdead\s+end\b",
)
