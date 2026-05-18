"""A2 — statistical-correlation generator with mandatory prime-detrending.

For (catalog_A, invariant_i) × (catalog_B, invariant_j) pairs, samples N
objects from each catalog and computes Pearson correlation. Per
`feedback_prime_atmosphere.md`: 96%+ of cross-dataset structure is
prime-driven; we report BOTH raw correlation and a prime-detrended
correlation (residualized against the EC conductor's bulk-prime signal).

Verdict logic:
- REJECTED if |r_detrended| < 0.1 (no signal beyond prime atmosphere)
- SHADOW_CATALOG if |r_detrended| >= 0.1 AND p_detrended < 0.05

A2 inherits A1's anti-conventional discipline: we don't test pre-
specified deep relationships, we let the data show whether correlation
SURVIVES detrending. The substrate's verdict is honest about prime-bulk
washout.
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


SIGNIFICANT_R = 0.1
SIGNIFICANCE_P = 0.05


def _pearson(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """Pearson r + two-sided p-value (no scipy dep; uses t-approximation)."""
    n = len(xs)
    if n < 5:
        return 0.0, 1.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 0.0, 1.0
    r = sxy / math.sqrt(sxx * syy)
    # Two-sided p-value via t-statistic + normal approx (sloppy but OK
    # for filtering; bandit downweights weak signals via info_density).
    if abs(r) >= 0.9999:
        return r, 0.0
    t = r * math.sqrt((n - 2) / max(1 - r * r, 1e-9))
    # crude normal-approximation tail
    z = abs(t)
    p = math.erfc(z / math.sqrt(2))  # two-sided
    return r, p


def _detrend_against(values: List[float], control: List[float]) -> List[float]:
    """Regress out a linear-in-control trend; return residuals.

    The control variable for EC-side invariants is log(conductor) — a
    proxy for the prime-bulk structure that dominates EC catalogs.
    """
    n = len(values)
    if n != len(control) or n == 0:
        return list(values)
    mc = sum(control) / n
    mv = sum(values) / n
    scc = sum((c - mc) ** 2 for c in control)
    if scc == 0:
        return list(values)
    scv = sum((c - mc) * (v - mv) for c, v in zip(control, values))
    beta = scv / scc
    return [v - beta * (c - mc) - mv for v, c in zip(values, control)]


class A2StatisticalCorrelationGenerator(Generator):
    generator_id = "a2"
    claim_kind = ClaimKind.STATISTICAL_CORRELATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 10,
        sample_size: int = 50,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        from theseus.optimization.config_overrides import get_overrides_for
        ov = get_overrides_for("a2")
        self._n = int(ov.get("sample_size", sample_size))
        self._significant_r = float(ov.get("SIGNIFICANT_R", SIGNIFICANT_R))

    def description(self) -> str:
        return (
            f"a2: cross-catalog statistical correlation (knot inv × ec inv) "
            f"with mandatory prime-detrending against log(conductor), "
            f"sample_size={self._n}"
        )

    def _gather_paired_sample(
        self, knot_inv: str, ec_inv: str
    ) -> Tuple[List[float], List[float], List[float]]:
        """Return (knot_values, ec_values, log_conductors) for n paired
        (knot, EC) draws. Pairs are random (independent samples)."""
        xs: List[float] = []
        ys: List[float] = []
        logc: List[float] = []
        for _ in range(self._n * 3):  # retry budget for missing values
            if len(xs) >= self._n:
                break
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            kv = _get_int(k, knot_inv)
            ev = _get_int(e, ec_inv)
            cond = _get_int(e, "conductor")
            if kv is None or ev is None or cond is None or cond <= 0:
                continue
            xs.append(float(kv))
            ys.append(float(ev))
            logc.append(math.log(cond))
        return xs, ys, logc

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(15):
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            xs, ys, logc = self._gather_paired_sample(ki, ei)
            if len(xs) < 10:
                self.attempts += 1
                continue

            r_raw, p_raw = _pearson(xs, ys)
            ys_detrended = _detrend_against(ys, logc)
            r_det, p_det = _pearson(xs, ys_detrended)

            survived = abs(r_det) >= self._significant_r and p_det < SIGNIFICANCE_P
            verdict = (
                Verdict.SHADOW_CATALOG.value if survived
                else Verdict.REJECTED.value
            )
            kill_pattern = None if survived else (
                "a2_detrended_correlation_below_threshold"
                if abs(r_det) < self._significant_r
                else "a2_detrended_correlation_not_significant"
            )

            canonical = (
                f"corr({ki}_knot, {ei}_ec, n={len(xs)}): "
                f"r_raw={r_raw:+.3f} (p={p_raw:.3g}) → "
                f"r_detrended_logcond={r_det:+.3f} (p={p_det:.3g}) | "
                f"survives_prime_detrend={survived}"
            )
            payload = {
                "knot_invariant": ki,
                "ec_invariant": ei,
                "sample_size": len(xs),
                "r_raw": r_raw,
                "p_raw": p_raw,
                "r_detrended": r_det,
                "p_detrended": p_det,
                "detrend_control": "log(conductor)",
                "survived_detrending": survived,
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
                method="pearson_correlation_with_logcond_detrend",
                convergence_status="n/a",
                extras={"feedback_anchor": "feedback_prime_atmosphere"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
