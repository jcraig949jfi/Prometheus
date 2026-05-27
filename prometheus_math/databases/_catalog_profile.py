"""Catalog density profiles for data-driven threshold calibration.

Per Erebos v3 + DR amendment §3.2 (DR Anti-Pattern B: local geometry
ignored at thresholds). Loaders that hardcode constants (EPSILON_BAND
=0.05, SMOOTH_THRESHOLD=3.0, CHI2_THRESHOLD=10, DECAY_SLOPE_TOLERANCE
=0.5) must instead reference catalog_profile(domain).{property} so
thresholds are tied to the catalog's natural scale.

Pickle cache at prometheus_math/databases/_catalog_profile_cache/
<domain>.pkl with mtime-based invalidation.

Reading: pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md §3.2
"""
from __future__ import annotations

import math
import pickle
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional


# Cache directory (lives next to the catalog data files)
_CACHE_DIR = Path(__file__).parent / "_catalog_profile_cache"
_CACHE_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class CatalogProfile:
    """Per-catalog density profile + scale parameters."""
    domain: str
    n_entries: int
    primary_axis_field: str
    median_pairwise_gap: float
    p05: float
    p25: float
    p50: float
    p75: float
    p95: float
    p99: float
    bootstrap_ci: dict[str, tuple[float, float]] = field(default_factory=dict)
    computed_at: str = ""
    # KDE bandwidth (Silverman's rule by default); the density function
    # itself is reconstructed lazily because lambdas don't pickle.
    kde_bandwidth: float = 0.0

    def density_kde(self, x: float, *, values: Optional[list[float]] = None) -> float:
        """Gaussian KDE evaluated at x. If values is supplied, use it;
        otherwise reconstruct from the catalog (slower)."""
        if values is None:
            values = _load_axis_values(self.domain, self.primary_axis_field)
        h = self.kde_bandwidth if self.kde_bandwidth > 0 else 0.1
        n = len(values)
        if n == 0:
            return 0.0
        coeff = 1.0 / (n * h * math.sqrt(2 * math.pi))
        return coeff * sum(
            math.exp(-0.5 * ((x - v) / h) ** 2) for v in values
        )


class HardcodedThresholdError(Exception):
    """Raised when a loader uses a literal threshold without referencing
    catalog_profile."""


class UnknownDomainError(Exception):
    """Raised when catalog_profile() is called for a domain without an
    installed accessor."""


# --------------------------------------------------------------------
# Domain accessors — minimal stubs for the 4 in-scope domains
# --------------------------------------------------------------------

def _load_axis_values(domain: str, axis_field: str) -> list[float]:
    """Load the primary axis values for a domain.

    Currently wired for "mahler" via prometheus_math.databases.mahler.
    BSD / OEIS / NF stubs raise UnknownDomainError until the per-domain
    accessors land in v3 Phase 1.
    """
    if domain == "mahler":
        from prometheus_math.databases.mahler import all_below
        entries = all_below(2.0)
        out: list[float] = []
        for e in entries:
            m = e.get("mahler_measure")
            if m is None or m <= 1.0 + 1e-9:
                continue
            out.append(float(m))
        return out
    elif domain in ("bsd", "oeis", "number_field"):
        raise UnknownDomainError(
            f"Domain {domain!r} accessor not yet installed (Phase 1 work)"
        )
    else:
        raise UnknownDomainError(
            f"Domain {domain!r} unknown. Registered: mahler"
        )


_KNOWN_DOMAINS = {
    "mahler": ("mahler_measure", _load_axis_values),
    # Stubs (raise UnknownDomainError when queried; reserved slots)
    "bsd": ("conductor", _load_axis_values),
    "oeis": ("connectivity_score", _load_axis_values),
    "number_field": ("discriminant", _load_axis_values),
}


# --------------------------------------------------------------------
# Profile computation
# --------------------------------------------------------------------

def _median_pairwise_gap(values: list[float]) -> float:
    """Median of consecutive-sorted-gap distribution. Natural scale
    for epsilon-band thresholds."""
    if len(values) < 2:
        return 0.0
    sorted_v = sorted(values)
    gaps = [sorted_v[i + 1] - sorted_v[i] for i in range(len(sorted_v) - 1)]
    return statistics.median(gaps)


def _percentiles(values: list[float]) -> dict[str, float]:
    """Compute {p05, p25, p50, p75, p95, p99} via statistics.quantiles."""
    if not values:
        return {k: 0.0 for k in ("p05", "p25", "p50", "p75", "p95", "p99")}
    sorted_v = sorted(values)
    n = len(sorted_v)

    def pct(p: float) -> float:
        # Linear interpolation; matches numpy's default percentile behavior
        idx = p * (n - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return sorted_v[lo]
        frac = idx - lo
        return sorted_v[lo] * (1 - frac) + sorted_v[hi] * frac

    return {
        "p05": pct(0.05),
        "p25": pct(0.25),
        "p50": pct(0.50),
        "p75": pct(0.75),
        "p95": pct(0.95),
        "p99": pct(0.99),
    }


def _silverman_bandwidth(values: list[float]) -> float:
    """Silverman's rule of thumb for Gaussian KDE bandwidth."""
    n = len(values)
    if n < 2:
        return 0.1
    std = statistics.stdev(values)
    if std == 0:
        return 0.1
    return 1.06 * std * (n ** (-0.2))


def _bootstrap_ci(
    values: list[float], *, n_boot: int = 200, seed: int = 42
) -> dict[str, tuple[float, float]]:
    """Bootstrap 95% CI for mean and median. Returns {param: (lo, hi)}.

    Loaders that fit a parameter (slope tolerance, chi² boundary) read
    the CI bound as their data-driven threshold.
    """
    if len(values) < 10:
        return {}
    import random
    rng = random.Random(seed)
    n = len(values)
    mean_boots: list[float] = []
    median_boots: list[float] = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        mean_boots.append(sum(sample) / n)
        median_boots.append(statistics.median(sample))
    mean_boots.sort()
    median_boots.sort()
    lo_idx = max(0, int(0.025 * (n_boot - 1)))
    hi_idx = min(n_boot - 1, int(0.975 * (n_boot - 1)))
    return {
        "mean": (mean_boots[lo_idx], mean_boots[hi_idx]),
        "median": (median_boots[lo_idx], median_boots[hi_idx]),
    }


def _compute_profile(domain: str) -> CatalogProfile:
    """Heavy lift: load values + compute all stats."""
    if domain not in _KNOWN_DOMAINS:
        raise UnknownDomainError(
            f"Domain {domain!r} unknown. Registered: {sorted(_KNOWN_DOMAINS.keys())}"
        )
    axis_field, _loader = _KNOWN_DOMAINS[domain]
    values = _load_axis_values(domain, axis_field)
    pcts = _percentiles(values)
    return CatalogProfile(
        domain=domain,
        n_entries=len(values),
        primary_axis_field=axis_field,
        median_pairwise_gap=_median_pairwise_gap(values),
        p05=pcts["p05"], p25=pcts["p25"], p50=pcts["p50"],
        p75=pcts["p75"], p95=pcts["p95"], p99=pcts["p99"],
        bootstrap_ci=_bootstrap_ci(values),
        computed_at=datetime.now(timezone.utc).isoformat(),
        kde_bandwidth=_silverman_bandwidth(values),
    )


# --------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------

_runtime_cache: dict[str, CatalogProfile] = {}


def _cache_path_for(domain: str) -> Path:
    return _CACHE_DIR / f"{domain}.pkl"


def catalog_profile(
    domain: str, *, refresh: bool = False
) -> CatalogProfile:
    """Return cached profile for domain. Recompute if refresh=True or
    cache miss / stale."""
    if not refresh and domain in _runtime_cache:
        return _runtime_cache[domain]

    cache_path = _cache_path_for(domain)
    if not refresh and cache_path.exists():
        try:
            with cache_path.open("rb") as f:
                profile: CatalogProfile = pickle.load(f)
            if profile.domain == domain:
                _runtime_cache[domain] = profile
                return profile
        except Exception:
            pass  # fall through to recompute

    # Compute fresh
    profile = _compute_profile(domain)
    try:
        with cache_path.open("wb") as f:
            pickle.dump(profile, f)
    except Exception:
        pass  # cache is best-effort
    _runtime_cache[domain] = profile
    return profile


def epsilon_band_for(domain: str, *, multiplier: float = 1.0) -> float:
    """Data-driven epsilon = multiplier * median_pairwise_gap. Replaces
    hardcoded EPSILON_BAND constants in G03 / G16 / similar loaders."""
    return multiplier * catalog_profile(domain).median_pairwise_gap


def percentile_threshold_for(domain: str, p: float) -> float:
    """Return the value at percentile p (0.05, 0.25, 0.50, 0.75, 0.95, 0.99)
    of the catalog's primary axis. Replaces hardcoded thresholds like
    M=1.30 with M=catalog_profile('mahler').p95."""
    profile = catalog_profile(domain)
    if abs(p - 0.05) < 1e-9: return profile.p05
    if abs(p - 0.25) < 1e-9: return profile.p25
    if abs(p - 0.50) < 1e-9: return profile.p50
    if abs(p - 0.75) < 1e-9: return profile.p75
    if abs(p - 0.95) < 1e-9: return profile.p95
    if abs(p - 0.99) < 1e-9: return profile.p99
    raise ValueError(
        f"percentile_threshold_for: only {{0.05, 0.25, 0.50, 0.75, 0.95, 0.99}} "
        f"supported, got {p}"
    )


def bootstrap_ci_for(
    domain: str, parameter_name: str
) -> tuple[float, float]:
    """Return the bootstrap 95% CI (lo, hi) for a parameter. Used as
    data-driven tolerance / boundary in loaders that fit parameters."""
    ci = catalog_profile(domain).bootstrap_ci
    if parameter_name not in ci:
        raise ValueError(
            f"bootstrap_ci_for: parameter {parameter_name!r} not in "
            f"{sorted(ci.keys())} for domain {domain!r}"
        )
    return ci[parameter_name]


def known_domains() -> list[str]:
    """Return sorted list of registered catalog domains."""
    return sorted(_KNOWN_DOMAINS.keys())


def clear_runtime_cache() -> None:
    """Test helper — clear in-memory cache only (pickle stays)."""
    _runtime_cache.clear()
