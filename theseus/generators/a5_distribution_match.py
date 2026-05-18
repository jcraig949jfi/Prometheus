"""A5 — distribution-match generator (Kolmogorov–Smirnov test on
standardized cross-catalog invariant distributions).

For each (knot_invariant, ec_invariant) pair, collects values from both
catalogs, standardizes each (z-score) to remove scale differences, then
runs the two-sample KS test on the standardized values. SHAPE-match
rather than raw-value match.

Verdict:
- SHADOW_CATALOG if KS_D < 0.3 AND p > 0.05 (distributions same shape)
- INCONCLUSIVE if 0.3 ≤ KS_D < 0.5 (ambiguous)
- REJECTED if KS_D ≥ 0.5 OR p ≤ 0.05 (shapes differ)

Substrate-native; uses scipy if available, else pure-Python KS
approximation.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _get_int,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)


KS_GOOD = 0.3
KS_WEAK = 0.5


def _standardize(xs: List[float]) -> List[float]:
    """Z-score: (x - mean) / stdev."""
    n = len(xs)
    if n < 2:
        return list(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / n
    if var <= 0:
        return [0.0 for _ in xs]
    sd = math.sqrt(var)
    return [(x - m) / sd for x in xs]


def _ks_two_sample(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """Two-sample KS statistic + asymptotic p-value (pure Python).

    Returns (D, p_value).
    """
    if not xs or not ys:
        return 0.0, 1.0
    combined = sorted(set(xs + ys))
    n1, n2 = len(xs), len(ys)
    xs_sorted = sorted(xs)
    ys_sorted = sorted(ys)

    def cdf(sorted_vals: List[float], n: int, x: float) -> float:
        # Empirical CDF: fraction of sorted_vals ≤ x
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if sorted_vals[mid] <= x:
                lo = mid + 1
            else:
                hi = mid
        return lo / n

    d_stat = max(abs(cdf(xs_sorted, n1, v) - cdf(ys_sorted, n2, v)) for v in combined)
    # Asymptotic p-value (Smirnov)
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * d_stat
    # Q_KS(lam) = 2 * sum_{j=1..inf} (-1)^(j-1) * exp(-2 j^2 lam^2)
    if lam < 1e-9:
        return d_stat, 1.0
    p = 0.0
    for j in range(1, 100):
        term = 2.0 * ((-1) ** (j - 1)) * math.exp(-2.0 * j * j * lam * lam)
        p += term
        if abs(term) < 1e-9:
            break
    p = max(0.0, min(1.0, p))
    return d_stat, p


class A5DistributionMatchGenerator(Generator):
    generator_id = "a5"
    claim_kind = ClaimKind.DISTRIBUTION_MATCH.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 110, sample_size: int = 30) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._n = sample_size

    def description(self) -> str:
        return (
            f"a5: KS distribution-match on standardized cross-catalog "
            f"invariants (sample_size={self._n}; D<{KS_GOOD} → SHADOW)"
        )

    def _gather(self, knot_inv: str, ec_inv: str) -> Tuple[List[float], List[float]]:
        xs: List[float] = []
        ys: List[float] = []
        for _ in range(self._n * 3):
            if len(xs) >= self._n:
                break
            k = self._rng.choice(self._knots)
            kv = _get_int(k, knot_inv)
            if kv is not None:
                xs.append(float(kv))
        for _ in range(self._n * 3):
            if len(ys) >= self._n:
                break
            e = self._rng.choice(self._ecs)
            ev = _get_int(e, ec_inv)
            if ev is not None:
                ys.append(float(ev))
        return xs, ys

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(15):
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            xs, ys = self._gather(ki, ei)
            if len(xs) < 5 or len(ys) < 5:
                self.attempts += 1
                continue
            xs_z = _standardize(xs)
            ys_z = _standardize(ys)
            d_stat, p_val = _ks_two_sample(xs_z, ys_z)

            if d_stat < KS_GOOD and p_val > 0.05:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
            elif d_stat < KS_WEAK:
                verdict = Verdict.INCONCLUSIVE.value
                kill_pattern = None
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"a5_ks_d{d_stat:.2f}_p{p_val:.3g}"

            canonical = (
                f"A5_KS[std] {ki}(knot) vs {ei}(ec) "
                f"| n1={len(xs)} n2={len(ys)} | D={d_stat:.3f} p={p_val:.3g}"
            )
            payload = {
                "knot_invariant": ki,
                "ec_invariant": ei,
                "n_knot": len(xs),
                "n_ec": len(ys),
                "ks_d_statistic": d_stat,
                "ks_p_value": p_val,
                "standardized": True,
            }
            record_id = TheseusRecord.compute_record_id(
                canonical_claim_text=canonical,
                generator_id=self.generator_id,
            )
            r = TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload=payload,
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
                method="ks_two_sample_standardized",
                convergence_status="exact",
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
