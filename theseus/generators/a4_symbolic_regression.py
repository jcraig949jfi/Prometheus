"""A4 — symbolic-regression generator (numpy polyfit v0.1).

For each (knot_invariant, ec_invariant) pair, samples N (knot, EC)
pairs, fits polynomials of degree 1/2/3 via numpy.polyfit, computes
R². Emits a record claiming "ec_invariant ≈ polynomial_d(knot_invariant)"
with the best-fit degree and R².

v0.1 polyfit fallback. PySR upgrade Tier 2 (Cranmer 2023, BSD-licensed,
genetic-programming symbolic regression). The numpy version covers the
core use case — discover non-trivial functional relationships between
catalog invariants — without the Julia install surface.

Verdict mapping:
- SHADOW_CATALOG if best R² ≥ 0.7 (strong fit; non-trivial relationship)
- INCONCLUSIVE if 0.3 ≤ R² < 0.7 (weak but nonzero)
- REJECTED if R² < 0.3 (no detectable functional relationship)

The threshold 0.7 is conservative; sub-Lehmer-band-style signal hunt.
With only N=30 samples and degree-3 fit (4 parameters), random noise
can hit R² ~ 0.5 by chance — the high threshold filters out spurious
fits.
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


STRONG_R2 = 0.7
WEAK_R2 = 0.3
DEGREES = (1, 2, 3)


def _polyfit_r2(
    xs: List[float], ys: List[float], degree: int
) -> Tuple[List[float], float]:
    """Fit polynomial of given degree; return (coeffs, R²).

    Pure-Python implementation (no numpy hard dep) — uses numpy if
    available for stability, else closed-form for degree<=2.
    """
    try:
        import warnings
        import numpy as np  # type: ignore
        with warnings.catch_warnings():
            # RankWarning is expected on poorly-conditioned integer data
            warnings.simplefilter("ignore")
            coeffs = np.polyfit(xs, ys, degree).tolist()
        # R² = 1 - SS_res / SS_tot
        y_pred = [_poly_eval(coeffs, x) for x in xs]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
        my = sum(ys) / len(ys)
        ss_tot = sum((y - my) ** 2 for y in ys)
        if ss_tot == 0:
            return coeffs, 1.0 if ss_res == 0 else 0.0
        return coeffs, 1.0 - (ss_res / ss_tot)
    except ImportError:
        # Pure-Python fallback (degree<=2 only)
        if degree > 2:
            return [], 0.0
        return _polyfit_pure(xs, ys, degree)


def _poly_eval(coeffs: List[float], x: float) -> float:
    """Evaluate polynomial with descending-order coefficients (numpy
    convention)."""
    out = 0.0
    for c in coeffs:
        out = out * x + c
    return out


def _polyfit_pure(
    xs: List[float], ys: List[float], degree: int
) -> Tuple[List[float], float]:
    """Pure-Python polyfit fallback for degree 1 or 2."""
    n = len(xs)
    if degree == 1:
        mx = sum(xs) / n
        my = sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx == 0:
            return [0.0, my], 0.0
        a = sxy / sxx
        b = my - a * mx
        coeffs = [a, b]
        y_pred = [a * x + b for x in xs]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
        ss_tot = sum((y - my) ** 2 for y in ys)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        return coeffs, r2
    # Degree 2 closed form skipped; require numpy for v0.1
    return [], 0.0


class A4SymbolicRegressionGenerator(Generator):
    generator_id = "a4"
    claim_kind = ClaimKind.RATIO_INVARIANCE.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 40,
        sample_size: int = 30,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Apply tuned overrides if present
        from theseus.optimization.config_overrides import get_overrides_for
        ov = get_overrides_for("a4")
        self._n = int(ov.get("sample_size", sample_size))
        self._strong_r2 = float(ov.get("STRONG_R2", STRONG_R2))
        self._weak_r2 = float(ov.get("WEAK_R2", WEAK_R2))

    def description(self) -> str:
        return (
            f"a4: symbolic-regression numpy polyfit (degrees "
            f"{DEGREES}, sample_size={self._n}; R²≥{STRONG_R2}→SHADOW)"
        )

    def _gather_sample(
        self, knot_inv: str, ec_inv: str
    ) -> Tuple[List[float], List[float]]:
        xs: List[float] = []
        ys: List[float] = []
        for _ in range(self._n * 3):
            if len(xs) >= self._n:
                break
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            kv = _get_int(k, knot_inv)
            ev = _get_int(e, ec_inv)
            if kv is None or ev is None:
                continue
            xs.append(float(kv))
            ys.append(float(ev))
        return xs, ys

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(15):
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            xs, ys = self._gather_sample(ki, ei)
            if len(xs) < 10:
                self.attempts += 1
                continue

            best_r2 = -math.inf
            best_degree = 1
            best_coeffs: List[float] = []
            for d in DEGREES:
                coeffs, r2 = _polyfit_r2(xs, ys, d)
                if not coeffs:
                    continue
                if r2 > best_r2:
                    best_r2 = r2
                    best_degree = d
                    best_coeffs = coeffs

            self.attempts += 1
            if best_r2 < -10:  # all fits failed
                continue

            if best_r2 >= self._strong_r2:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
            elif best_r2 >= self._weak_r2:
                verdict = Verdict.INCONCLUSIVE.value
                kill_pattern = None
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"a4_polyfit_r2_below_{self._weak_r2}"

            coeffs_str = ",".join(f"{c:.4g}" for c in best_coeffs)
            canonical = (
                f"A4_SYMREG[deg={best_degree}] "
                f"{ei}(ec) ≈ poly_{best_degree}({ki}(knot)) "
                f"| n={len(xs)} R²={best_r2:.3f} coeffs=[{coeffs_str}]"
            )
            payload = {
                "knot_invariant": ki,
                "ec_invariant": ei,
                "sample_size": len(xs),
                "best_degree": best_degree,
                "best_r2": best_r2,
                "best_coeffs": best_coeffs,
                "strong_threshold": self._strong_r2,
                "weak_threshold": self._weak_r2,
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
                method="numpy_polyfit",
                convergence_status="n/a",
                extras={
                    "frontier_technique": "symbolic_regression_numpy_fallback",
                    "upgrade_path": "pysr_tier2",
                },
            )
            self.emitted.append(record_id)
            return r

        return None
