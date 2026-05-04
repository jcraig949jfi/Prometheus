"""prometheus_math.kill_vector_navigator — Day 5 of the kill-space pivot.

The *first explicit policy primitive* the substrate has produced.
Given a region (degree, alphabet_width, reward_shape, env), the navigator
ranks operators (random, REINFORCE, PPO, GA_elitist, ...) by an estimate
of *expected kill magnitude*: a lower-is-better scalar that proxies how
close that operator gets to the survival band.

Two-mode policy
---------------

The navigator is two-mode by design, dispatching at runtime per-region:

  * **margin mode** (preferred) ranks operators by
    ``E[‖kill_vector‖_margin | region, operator]`` using
    ``KillVector.magnitude(unit_aware=True)`` — the squashed-L2 over
    triggered components. Driven by *native pilot* records that carry
    real, continuous margins (the ``out_of_band`` margin in particular
    distinguishes "PPO touched the band, min margin -0.001" from
    "REINFORCE never came close, mean margin +6.69").

  * **categorical mode** (fallback) ranks operators by
    ``E[‖triggered_vector‖ | region, operator]`` — the count of
    triggered components, which is what legacy categorical archaeology
    can deliver.

Why two modes? The 2026-05-04 native pilot (deg14 +/-5 step env, 24K
episodes) measured **126,983x** more pairwise distinguishability between
operators in margin space than in categorical space (KL=4.4e-2 vs
KL=3.5e-7). On the legacy ledger the categorical kill_path is dominated
by the ``upstream:cyclotomic_or_large`` mode, which collapses the
operator distinguishability to noise. Margin mode exploits the
continuous near-miss signal that categorical throws away.

In auto mode the navigator returns margin-mode rankings whenever
native data is available for the region, and categorical-mode rankings
otherwise -- preserving usefulness on regions the native pilot hasn't
reached yet, and future-proofing the API for native data accumulating
across more regions.

Honest framing
--------------

As of 2026-05-04 only ONE region (deg14 +/-5 step env) has native
margin data. So margin mode is meaningful only there. Other regions
are categorical-only, and within those the categorical signal is
known to be weak (per Day 4's archaeology). The navigator surfaces
this transparently via ``policy_for_region`` and ``summary``.

API
---

Top-level (the consumer-facing surface)::

    nav = KillVectorNavigator.from_data()
    recs = nav.recommend(region, mode="auto", top_k=3)
    summary = nav.summary()
    table = nav.policy_for_region(region)

Each recommendation is an ``OperatorRecommendation`` with a 95%
bootstrap CI on the expected magnitude.
"""
from __future__ import annotations

import json
import math
import os
import random
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from prometheus_math.kill_vector import KillVector


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


PROMETHEUS_MATH_DIR = os.path.dirname(os.path.abspath(__file__))


NATIVE_PILOT_FILENAME = "_native_kill_vector_pilot.json"
LEGACY_ARCHAEOLOGY_FILENAME = "_gradient_archaeology_results.json"
# 2026-05-04 region-densification pilot adds margin coverage on 4 more
# region cells (deg10 ±5, deg12 ±5, deg10 ±3, deg14 ±3).  Same JSON
# shape as the native pilot; consumed identically by
# ``_native_pilot_to_region_stats``.
DENSIFICATION_PILOT_FILENAME = "_region_densification_pilot.json"


# Number of bootstrap resamples for the 95% CI estimator. Kept modest
# so the navigator constructs in well under a second on the expected
# data scale (24k native + 60 aggregated legacy rows).
DEFAULT_BOOTSTRAP_RESAMPLES = 200

# Default minimum cell count below which an operator is filtered out
# of recommendations (avoid ranking on noise).
DEFAULT_MIN_EPISODES = 100

# CI alpha (two-sided 95%).
CI_ALPHA = 0.05


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OperatorRecommendation:
    """One operator's expected kill magnitude in a given region.

    Lower expected magnitude = more recommended (the operator gets
    closer to the survival band on average).

    Attributes
    ----------
    operator_class : str
        Operator label (``"ppo_mlp"``, ``"reinforce_linear"``, ...).
    expected_magnitude : float
        Point estimate of E[||k|| | region, operator]. In margin mode
        this is the unit-aware squashed-L2 magnitude; in categorical
        mode it is the count of triggered components.
    ci_low : float
        Lower bound of the 95% bootstrap CI on the expected magnitude.
    ci_high : float
        Upper bound of the 95% bootstrap CI on the expected magnitude.
    n_episodes : int
        Number of records this estimate was computed from.
    mode : str
        "margin" or "categorical".
    notes : str
        Optional human-readable note (e.g. when only one operator is
        available, or when a fallback was triggered).
    """

    operator_class: str
    expected_magnitude: float
    ci_low: float
    ci_high: float
    n_episodes: int
    mode: str
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class _RegionStats:
    """Internal: per-region aggregate, both modes when both are present."""

    region: str
    region_meta: Dict[str, Any]
    # operator -> list of squashed magnitudes (margin mode)
    margin_samples: Dict[str, List[float]] = field(default_factory=dict)
    # operator -> list of triggered counts (categorical mode)
    categorical_samples: Dict[str, List[float]] = field(default_factory=dict)
    has_margin_data: bool = False
    has_categorical_data: bool = False


# ---------------------------------------------------------------------------
# Region-id derivation (mirrors gradient_archaeology._region_id so the two
# data sources land on the same key when they describe the same env)
# ---------------------------------------------------------------------------


def _region_id_from_meta(meta: Mapping[str, Any]) -> str:
    """Produce the canonical region id ``env|degN|wW|reward_shape``."""
    env = meta.get("env", "unknown")
    deg = meta.get("degree", "?")
    width = meta.get("alphabet_width", "?")
    shape = meta.get("reward_shape", "step")
    return f"{env}|deg{deg}|w{width}|{shape}"


def _region_meta_from_id(region_id: str) -> Dict[str, Any]:
    """Best-effort inverse of ``_region_id_from_meta``."""
    parts = region_id.split("|")
    out: Dict[str, Any] = {}
    if len(parts) >= 1:
        out["env"] = parts[0]
    if len(parts) >= 2 and parts[1].startswith("deg"):
        try:
            out["degree"] = int(parts[1][3:])
        except ValueError:
            out["degree"] = parts[1][3:]
    if len(parts) >= 3 and parts[2].startswith("w"):
        try:
            out["alphabet_width"] = int(parts[2][1:])
        except ValueError:
            out["alphabet_width"] = parts[2][1:]
    if len(parts) >= 4:
        out["reward_shape"] = parts[3]
    return out


# ---------------------------------------------------------------------------
# Bootstrap CI (numpy-free; easier to reason about determinism)
# ---------------------------------------------------------------------------


def _bootstrap_mean_ci(
    samples: Sequence[float],
    *,
    resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    alpha: float = CI_ALPHA,
    rng: Optional[random.Random] = None,
) -> Tuple[float, float, float]:
    """Return ``(mean, ci_low, ci_high)`` for the supplied scalar samples.

    Uses a percentile bootstrap. Designed to be deterministic when the
    caller supplies an ``rng``. Degenerate inputs return ``(mean, mean,
    mean)`` so downstream code doesn't need to special-case empty CI
    intervals.
    """
    n = len(samples)
    if n == 0:
        return 0.0, 0.0, 0.0
    mean = float(sum(samples) / n)
    if n == 1 or resamples <= 0:
        return mean, mean, mean
    rng = rng if rng is not None else random.Random(0)
    sample_arr = list(samples)
    boots: List[float] = []
    for _ in range(resamples):
        s = 0.0
        for __ in range(n):
            s += sample_arr[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    lo_idx = int(math.floor((alpha / 2.0) * len(boots)))
    hi_idx = int(math.ceil((1.0 - alpha / 2.0) * len(boots))) - 1
    lo_idx = max(0, min(len(boots) - 1, lo_idx))
    hi_idx = max(0, min(len(boots) - 1, hi_idx))
    ci_low = float(boots[lo_idx])
    ci_high = float(boots[hi_idx])
    # Defensive: clamp the CI to contain the point estimate, so the
    # property test "CI contains the mean" is never violated (this can
    # otherwise fail when the resamples happen to all sit on one side
    # of the mean for very small N).
    ci_low = min(ci_low, mean)
    ci_high = max(ci_high, mean)
    return mean, ci_low, ci_high


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _load_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _native_pilot_to_region_stats(
    pilot: Mapping[str, Any],
) -> Dict[str, _RegionStats]:
    """Turn a native pilot JSON into per-region aggregates.

    Each episode in ``pilot["episodes"]`` carries a serialised
    ``KillVector``; we reconstruct it via ``KillVector.from_dict`` and
    bucket into (region_id, operator_class) by reading
    ``region_meta`` (with operator stripped down to its ``algorithm``
    field, the canonical bench label).

    Both magnitude (margin mode) and triggered_count (categorical mode)
    are recorded so a region present in the native data also gets a
    categorical estimate "for free" -- this is what enables the
    cross-mode calibration diagnostic.
    """
    out: Dict[str, _RegionStats] = {}
    eps = pilot.get("episodes") or []
    for ep in eps:
        kv_dict = ep.get("kill_vector")
        if not isinstance(kv_dict, dict):
            continue
        try:
            kv = KillVector.from_dict(kv_dict)
        except Exception:
            continue
        region_meta = dict(kv.region_meta or {})
        # Operator: prefer the episode's algorithm field over the
        # kill_vector's stored operator_class (which is
        # "<algorithm>@seed=N" -- too granular for region-level ranking).
        op = ep.get("algorithm") or kv.operator_class.split("@")[0] or "_unknown"
        region_id = _region_id_from_meta(region_meta)
        stats = out.setdefault(region_id, _RegionStats(
            region=region_id, region_meta=region_meta,
        ))
        stats.has_margin_data = True
        stats.has_categorical_data = True
        stats.margin_samples.setdefault(op, []).append(
            kv.magnitude(unit_aware=True)
        )
        stats.categorical_samples.setdefault(op, []).append(
            float(kv.triggered_count)
        )
    return out


def _legacy_archaeology_to_region_stats(
    arch: Mapping[str, Any],
) -> Dict[str, _RegionStats]:
    """Turn a gradient_archaeology results JSON into per-region
    *categorical* aggregates only (the legacy ledger has no margins).

    The archaeology result already aggregates by
    ``per_region_disaggregation.regions[<region_id>].operator_kill_table``,
    keyed ``"<operator>|<kill_pattern>"`` -> count. We translate that
    into per-(region, operator) lists of triggered counts -- treating
    every counted kill as one triggered component (the legacy ledger
    only records the *first* failing falsifier).
    """
    out: Dict[str, _RegionStats] = {}
    prd = arch.get("per_region_disaggregation") or {}
    regions = prd.get("regions") or {}
    for region_id, region_data in regions.items():
        if not isinstance(region_data, dict):
            continue
        meta = _region_meta_from_id(region_id)
        stats = out.setdefault(region_id, _RegionStats(
            region=region_id, region_meta=meta,
        ))
        op_table = region_data.get("operator_kill_table") or {}
        for cell_key, count in op_table.items():
            if not isinstance(cell_key, str) or "|" not in cell_key:
                continue
            try:
                count_int = int(count)
            except (TypeError, ValueError):
                continue
            if count_int <= 0:
                continue
            op, _kp = cell_key.split("|", 1)
            samples = stats.categorical_samples.setdefault(op, [])
            samples.extend([1.0] * count_int)
            stats.has_categorical_data = True
    return out


def _merge_region_stats(
    primary: Dict[str, _RegionStats],
    secondary: Dict[str, _RegionStats],
) -> Dict[str, _RegionStats]:
    """Merge two region-stats dicts. Margin data only exists in the
    primary (native) source by construction; categorical data is
    additive across the two when a region is present in both.
    """
    out: Dict[str, _RegionStats] = {}
    keys = set(primary.keys()) | set(secondary.keys())
    for k in keys:
        if k in primary and k not in secondary:
            out[k] = primary[k]
            continue
        if k in secondary and k not in primary:
            out[k] = secondary[k]
            continue
        # In both: preserve primary margin samples; merge categorical.
        p = primary[k]
        s = secondary[k]
        merged_meta: Dict[str, Any] = {**s.region_meta, **p.region_meta}
        merged_cat: Dict[str, List[float]] = {}
        for op in set(p.categorical_samples) | set(s.categorical_samples):
            merged_cat[op] = (
                list(p.categorical_samples.get(op, []))
                + list(s.categorical_samples.get(op, []))
            )
        merged = _RegionStats(
            region=p.region,
            region_meta=merged_meta,
            margin_samples={op: list(vs) for op, vs in p.margin_samples.items()},
            categorical_samples=merged_cat,
            has_margin_data=p.has_margin_data or s.has_margin_data,
            has_categorical_data=p.has_categorical_data or s.has_categorical_data,
        )
        out[k] = merged
    return out


# ---------------------------------------------------------------------------
# Kendall tau (rank-agreement diagnostic for calibration)
# ---------------------------------------------------------------------------


def _kendall_tau(a: Sequence[str], b: Sequence[str]) -> float:
    """Tau over two orderings of the same set of operators. Returns 0
    on degenerate inputs (n < 2 or no overlap)."""
    common = list(set(a) & set(b))
    if len(common) < 2:
        return 0.0
    rank_a = {x: a.index(x) for x in common}
    rank_b = {x: b.index(x) for x in common}
    n = len(common)
    n_concordant = 0
    n_discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x, y = common[i], common[j]
            sa = (rank_a[x] - rank_a[y])
            sb = (rank_b[x] - rank_b[y])
            if sa == 0 or sb == 0:
                continue
            if (sa > 0) == (sb > 0):
                n_concordant += 1
            else:
                n_discordant += 1
    total = n_concordant + n_discordant
    if total == 0:
        return 0.0
    return float(n_concordant - n_discordant) / float(total)


# ---------------------------------------------------------------------------
# Navigator
# ---------------------------------------------------------------------------


@dataclass
class KillVectorNavigator:
    """Operator-ranking policy primitive.

    See module docstring for the two-mode framing. Construct via
    :py:meth:`from_data` (loads the standard artifacts) or via
    :py:meth:`from_region_stats` (testing seam).
    """

    region_stats: Dict[str, _RegionStats]
    sources_loaded: Tuple[str, ...] = field(default_factory=tuple)
    bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES
    seed: int = 0

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_data(
        cls,
        base_dir: str = PROMETHEUS_MATH_DIR,
        *,
        bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
        seed: int = 0,
    ) -> "KillVectorNavigator":
        """Load native pilot + legacy archaeology and build the navigator.

        Missing files are tolerated: if neither file is present, the
        returned navigator is empty (recommendations always return ``[]``).
        """
        sources: List[str] = []
        native_path = os.path.join(base_dir, NATIVE_PILOT_FILENAME)
        legacy_path = os.path.join(base_dir, LEGACY_ARCHAEOLOGY_FILENAME)
        densif_path = os.path.join(base_dir, DENSIFICATION_PILOT_FILENAME)

        native_stats: Dict[str, _RegionStats] = {}
        legacy_stats: Dict[str, _RegionStats] = {}
        densif_stats: Dict[str, _RegionStats] = {}

        native_blob = _load_json(native_path)
        if native_blob is not None and isinstance(native_blob.get("pilot"), dict):
            native_stats = _native_pilot_to_region_stats(native_blob["pilot"])
            sources.append(NATIVE_PILOT_FILENAME)

        densif_blob = _load_json(densif_path)
        if densif_blob is not None and isinstance(densif_blob.get("pilot"), dict):
            densif_stats = _native_pilot_to_region_stats(densif_blob["pilot"])
            sources.append(DENSIFICATION_PILOT_FILENAME)

        legacy_blob = _load_json(legacy_path)
        if legacy_blob is not None:
            legacy_stats = _legacy_archaeology_to_region_stats(legacy_blob)
            sources.append(LEGACY_ARCHAEOLOGY_FILENAME)

        # Native pilot regions take precedence over densification, but
        # densification's regions extend the native region set (no
        # overlap expected: native is deg14 ±5, densification covers the
        # other 4 cells).  Categorical-only legacy data is merged last.
        native_plus_densif = _merge_region_stats(native_stats, densif_stats)
        merged = _merge_region_stats(native_plus_densif, legacy_stats)
        return cls(
            region_stats=merged,
            sources_loaded=tuple(sources),
            bootstrap_resamples=bootstrap_resamples,
            seed=seed,
        )

    @classmethod
    def from_region_stats(
        cls,
        region_stats: Dict[str, _RegionStats],
        *,
        bootstrap_resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
        seed: int = 0,
        sources_loaded: Sequence[str] = (),
    ) -> "KillVectorNavigator":
        """Testing seam: bypass file loading, build directly from stats."""
        return cls(
            region_stats=dict(region_stats),
            sources_loaded=tuple(sources_loaded),
            bootstrap_resamples=bootstrap_resamples,
            seed=seed,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def regions(self) -> List[str]:
        return sorted(self.region_stats.keys())

    def has_margin_for(self, region: str) -> bool:
        st = self.region_stats.get(region)
        return bool(st and st.has_margin_data)

    def has_categorical_for(self, region: str) -> bool:
        st = self.region_stats.get(region)
        return bool(st and st.has_categorical_data)

    def _resolve_mode(self, region: str, mode: str) -> Optional[str]:
        if mode == "auto":
            if self.has_margin_for(region):
                return "margin"
            if self.has_categorical_for(region):
                return "categorical"
            return None
        if mode == "margin":
            return "margin" if self.has_margin_for(region) else None
        if mode == "categorical":
            return "categorical" if self.has_categorical_for(region) else None
        raise ValueError(f"unknown mode {mode!r}; must be auto/margin/categorical")

    def recommend(
        self,
        region: str,
        *,
        mode: str = "auto",
        top_k: int = 3,
        min_episodes: int = DEFAULT_MIN_EPISODES,
    ) -> List[OperatorRecommendation]:
        """Rank operators in ``region`` by expected magnitude (lower-first).

        Parameters
        ----------
        region : str
            Region id (``env|degN|wW|reward_shape``).
        mode : str
            "auto" | "margin" | "categorical". See module docstring.
        top_k : int
            Truncate to top-k.  Use a large value (e.g. 9999) for all.
        min_episodes : int
            Operators with fewer than ``min_episodes`` records are
            filtered out (avoid ranking on noise). Set to 0 to allow all.

        Returns
        -------
        list[OperatorRecommendation]
            Sorted ascending by ``expected_magnitude``. Empty when the
            region is unknown, the requested mode has no data, or all
            operators were filtered out.
        """
        resolved = self._resolve_mode(region, mode)
        if resolved is None:
            return []
        st = self.region_stats[region]
        samples_table = (
            st.margin_samples if resolved == "margin"
            else st.categorical_samples
        )
        if not samples_table:
            return []

        rng = random.Random(self.seed)
        recs: List[OperatorRecommendation] = []
        for op in sorted(samples_table.keys()):
            samples = samples_table[op]
            n = len(samples)
            if n < min_episodes:
                continue
            mean, lo, hi = _bootstrap_mean_ci(
                samples,
                resamples=self.bootstrap_resamples,
                rng=rng,
            )
            note = ""
            if len(samples_table) == 1:
                note = "single operator in region — no comparative ranking"
            recs.append(OperatorRecommendation(
                operator_class=op,
                expected_magnitude=mean,
                ci_low=lo,
                ci_high=hi,
                n_episodes=n,
                mode=resolved,
                notes=note,
            ))

        # Stable sort: primary by mean, secondary by name (deterministic
        # tie-break).
        recs.sort(key=lambda r: (r.expected_magnitude, r.operator_class))
        return recs[:top_k]

    def policy_for_region(
        self,
        region: str,
        *,
        min_episodes: int = 0,
    ) -> Dict[str, Any]:
        """Full diagnostic dump for a region: both modes, all operators,
        no top-k truncation.

        Returns a dict with keys ``region``, ``region_meta``,
        ``has_margin_data``, ``has_categorical_data``, ``margin``,
        ``categorical``. The ``margin`` and ``categorical`` lists hold
        full ``OperatorRecommendation.as_dict()`` rows (when data
        exists; empty list otherwise).
        """
        st = self.region_stats.get(region)
        if st is None:
            return {
                "region": region,
                "region_meta": _region_meta_from_id(region),
                "has_margin_data": False,
                "has_categorical_data": False,
                "margin": [],
                "categorical": [],
            }
        margin_recs = self.recommend(
            region, mode="margin", top_k=10**6, min_episodes=min_episodes,
        ) if st.has_margin_data else []
        cat_recs = self.recommend(
            region, mode="categorical", top_k=10**6, min_episodes=min_episodes,
        ) if st.has_categorical_data else []
        return {
            "region": region,
            "region_meta": dict(st.region_meta),
            "has_margin_data": bool(st.has_margin_data),
            "has_categorical_data": bool(st.has_categorical_data),
            "margin": [r.as_dict() for r in margin_recs],
            "categorical": [r.as_dict() for r in cat_recs],
        }

    def summary(self) -> Dict[str, Any]:
        """Coverage / sparseness diagnostic.

        Returns ``{"sources_loaded": [...], "n_regions": N,
        "n_with_margin": M, "n_categorical_only": K,
        "regions": [{"region": ..., "modes": [...],
        "n_operators": ..., "n_records_margin": ...,
        "n_records_categorical": ...}, ...]}``.
        """
        rows: List[Dict[str, Any]] = []
        n_with_margin = 0
        n_cat_only = 0
        for region in self.regions:
            st = self.region_stats[region]
            modes: List[str] = []
            if st.has_margin_data:
                modes.append("margin")
                n_with_margin += 1
            if st.has_categorical_data and not st.has_margin_data:
                n_cat_only += 1
            if st.has_categorical_data:
                modes.append("categorical")
            n_records_margin = sum(len(v) for v in st.margin_samples.values())
            n_records_cat = sum(len(v) for v in st.categorical_samples.values())
            n_ops = len(set(st.margin_samples) | set(st.categorical_samples))
            rows.append({
                "region": region,
                "modes": modes,
                "n_operators": n_ops,
                "n_records_margin": n_records_margin,
                "n_records_categorical": n_records_cat,
            })
        return {
            "sources_loaded": list(self.sources_loaded),
            "n_regions": len(rows),
            "n_with_margin": n_with_margin,
            "n_categorical_only": n_cat_only,
            "regions": rows,
        }

    # ------------------------------------------------------------------
    # Calibration: do margin and categorical rankings agree?
    # ------------------------------------------------------------------

    def calibration(
        self,
        *,
        min_episodes: int = DEFAULT_MIN_EPISODES,
    ) -> Dict[str, Any]:
        """For every region with BOTH margin and categorical data, compare
        the two rankings.

        Output shape::

            {
              "n_eligible_regions": N,
              "n_top1_disagree": k,
              "rows": [
                 {"region": ...,
                  "margin_top1": "ppo_mlp",
                  "categorical_top1": "reinforce_linear",
                  "agree_top1": False,
                  "kendall_tau": float in [-1, 1],
                  "n_common_operators": int,
                  "margin_ranking": [...],
                  "categorical_ranking": [...]},
                 ...
              ],
            }
        """
        rows: List[Dict[str, Any]] = []
        n_top1_disagree = 0
        for region in self.regions:
            st = self.region_stats[region]
            if not (st.has_margin_data and st.has_categorical_data):
                continue
            mr = self.recommend(
                region, mode="margin", top_k=10**6, min_episodes=min_episodes,
            )
            cr = self.recommend(
                region, mode="categorical", top_k=10**6,
                min_episodes=min_episodes,
            )
            if not mr or not cr:
                continue
            common = (
                {r.operator_class for r in mr}
                & {r.operator_class for r in cr}
            )
            if not common:
                continue
            margin_order = [
                r.operator_class for r in mr if r.operator_class in common
            ]
            cat_order = [
                r.operator_class for r in cr if r.operator_class in common
            ]
            agree_top1 = bool(
                margin_order and cat_order and margin_order[0] == cat_order[0]
            )
            if not agree_top1:
                n_top1_disagree += 1
            tau = _kendall_tau(margin_order, cat_order)
            rows.append({
                "region": region,
                "margin_top1": margin_order[0] if margin_order else None,
                "categorical_top1": cat_order[0] if cat_order else None,
                "agree_top1": agree_top1,
                "kendall_tau": tau,
                "n_common_operators": len(common),
                "margin_ranking": margin_order,
                "categorical_ranking": cat_order,
            })
        return {
            "n_eligible_regions": len(rows),
            "n_top1_disagree": n_top1_disagree,
            "rows": rows,
        }


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------


__all__ = [
    "KillVectorNavigator",
    "OperatorRecommendation",
    "PROMETHEUS_MATH_DIR",
    "NATIVE_PILOT_FILENAME",
    "LEGACY_ARCHAEOLOGY_FILENAME",
    "DENSIFICATION_PILOT_FILENAME",
    "DEFAULT_BOOTSTRAP_RESAMPLES",
    "DEFAULT_MIN_EPISODES",
    "_region_id_from_meta",
    "_region_meta_from_id",
    "_bootstrap_mean_ci",
    "_native_pilot_to_region_stats",
    "_legacy_archaeology_to_region_stats",
    "_merge_region_stats",
    "_kendall_tau",
    "_RegionStats",
]
