"""G2 — Functional equation L(s) ↔ L(k-s) claim emitter.

For each elliptic curve E/Q in the catalog, emit a structured claim
asserting that the completed L-function Λ_E(s) satisfies the FE:
    Λ_E(s) = ε(E) · Λ_E(2 − s)
where Λ_E(s) = N^(s/2) · (2π)^(-s) · Γ(s) · L_E(s) and ε(E) ∈ {±1}
is the global root number.

Verdict: UNVERIFIED. Numerical FE verification requires evaluating
L(s) at non-trivial s — beyond the catalog's stored values. The
substrate's sigma layer downstream picks these up and routes them
through the L-function FE verifier (mpmath/pari/lcalc).

Rationale for emitting unverified claims: (1) the substrate's value
is in routing-by-structure, not in-generator verification; (2) the
Learner can train on the (claim_text → terminal_verdict) labels even
when the generator only emits the claim; (3) the FE claim is
substantively non-trivial — Wiles' modularity theorem is what
guarantees ECs HAVE this functional equation at all, and verifying
it at the precision the substrate requires is real downstream work.

For ECs with no known modular form lifting (none in the catalog as
they're all over Q and modular by Wiles), this emission would be
INCONCLUSIVE; for ECs the catalog includes, modularity is proved.

Token-free; catalog-only.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from theseus.config import BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _label,
)
from theseus.generators.base import Generator, GeneratorStatus


def _get_conductor(ec: Dict[str, Any]) -> Optional[int]:
    base = ec.get("base", {})
    n = base.get("conductor")
    if n is None:
        return None
    try:
        return int(n)
    except (TypeError, ValueError):
        return None


def _get_rank(ec: Dict[str, Any]) -> Optional[int]:
    base = ec.get("base", {})
    r = base.get("rank")
    if r is None:
        return None
    try:
        return int(r)
    except (TypeError, ValueError):
        return None


# Sample s-values on the critical strip at which sigma's downstream
# FE verifier will pair s with (2-s). Includes the central point s=1.
SAMPLE_S_VALUES = (0.5, 1.0, 1.5)


class G2FunctionalEquationGenerator(Generator):
    generator_id = "g2"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 4096) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Eligible: has conductor (everything we need for the FE statement).
        self._eligible: List[int] = [
            idx for idx, e in enumerate(self._ecs)
            if _get_conductor(e) is not None
        ]

    def description(self) -> str:
        return (
            f"g2: L(s)↔L(2-s) functional-equation claim emission "
            f"(verdict=UNVERIFIED; sigma verifies); "
            f"{len(self._eligible)} eligible ECs"
        )

    def next(self) -> Optional[TheseusRecord]:
        if not self._eligible:
            return None
        for _ in range(20):
            idx = self._rng.choice(self._eligible)
            ec = self._ecs[idx]
            conductor = _get_conductor(ec)
            if conductor is None:
                self.attempts += 1
                continue

            s = self._rng.choice(SAMPLE_S_VALUES)
            label = _label(ec, "ec")
            rank = _get_rank(ec)

            canonical = (
                f"G2[FE] L_ec:{label}(s={s}) satisfies "
                f"Λ(s)=ε·Λ(2-s) with N={conductor}, "
                f"Γ_factor=(2π)^(-s)·Γ(s) | weight=2 | route_to=sigma_FE_verifier"
            )
            payload = {
                "ec_label": label,
                "conductor": conductor,
                "rank_known": rank,
                "weight": 2,
                "s_sample": s,
                "gamma_factor": "(2*pi)^(-s) * Gamma(s)",
                "completed_L": f"N^(s/2) * (2pi)^(-s) * Gamma(s) * L_E(s)",
                "FE_relation": "Lambda(s) == epsilon(E) * Lambda(2-s)",
                "epsilon_E": "in {-1, +1}",
            }
            self.attempts += 1
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
                verdict=Verdict.UNVERIFIED.value,
                method="catalog_FE_claim_emission",
                convergence_status="n/a",
                extras={"role": "functional_equation_unverified_claim"},
            )
            self.emitted.append(record_id)
            return r
        return None
