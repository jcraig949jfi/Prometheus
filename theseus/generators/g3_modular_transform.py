"""G3 — Modular transform under SL_2(Z).

For each elliptic curve E/Q (corresponding via modularity to a weight-2
newform f_E on Γ_0(N)), the q-expansion coefficients a_p are eigenvalues
of the Hecke operators T_p (the SL_2(Z) modular-transform action on the
space of cusp forms). A direct structural consequence of the SL_2(Z)
action (= the Hasse–Weil theorem for ECs, originally proved by Hasse
1933 and tightly bounded by the Weil conjectures):

    |a_p|  ≤  2·√p     for every prime p of good reduction

For primes of bad reduction, a_p ∈ {−1, 0, 1} (split, additive, non-
split multiplicative cases), all trivially within the Hasse bound.

G3 emits one record per (EC, prime) pair from the catalog's stored
`a_p` arrays, asserting |a_p| ≤ 2√p. Verdict: SHADOW_CATALOG when
the bound holds, REJECTED when it doesn't. Any REJECTED record is
substrate-detected Hasse-bound failure — a Weil-conjecture-collapse
candidate and very high info density.

Token-free; entirely catalog-based; verification is exact arithmetic
(squaring both sides eliminates the sqrt).
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
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


def _sieve_primes(n: int) -> List[int]:
    """First n primes via a simple sieve sized at n*log(n)+10 buffer."""
    if n <= 0:
        return []
    import math
    if n < 6:
        return [2, 3, 5, 7, 11][:n]
    upper = int(n * (math.log(n) + math.log(math.log(n)))) + 10
    sieve = [True] * (upper + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(upper ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, upper + 1, i):
                sieve[j] = False
    primes = [p for p, ok in enumerate(sieve) if ok]
    return primes[:n]


# Pre-cache: a_p arrays in the BSD-rich catalog typically have up to
# ~150 entries. 200 is a safe headroom.
_PRIMES_CACHE: List[int] = _sieve_primes(200)


def _hasse_bound_squared(p: int) -> int:
    """(2√p)^2 = 4p — exact integer comparison via squaring."""
    return 4 * p


def _get_ap_list(ec: Dict[str, Any]) -> Optional[List[int]]:
    base = ec.get("base", {})
    ap = base.get("a_p")
    if ap is None:
        return None
    if not isinstance(ap, list):
        return None
    try:
        return [int(x) for x in ap]
    except (TypeError, ValueError):
        return None


class G3ModularTransformGenerator(Generator):
    generator_id = "g3"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    status = GeneratorStatus.ACTIVE
    # Fire #61 reclassification: g3 tests |a_p| ≤ 2√p (Hasse bound,
    # a theorem). Predicted behavior is 100% confirm; any KILL would
    # be a Weil-conjecture-collapse alarm (preserve as alive-monitor).
    # Lifetime 120K records / 0 kills / 0 novel shapes through Fire
    # #60 — never contributed to DISCOVERY novelty index. Same role
    # class as c4: keep firing, exclude from discovery stats.
    role = GeneratorRole.TAUTOLOGY_CONTROL

    def __init__(self, batch_id: str, seed: int = 8192) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Pre-filter: ECs with a non-empty a_p array.
        self._eligible: List[int] = [
            idx for idx, e in enumerate(self._ecs)
            if _get_ap_list(e)
        ]

    def description(self) -> str:
        return (
            f"g3: SL_2(Z) Hecke-eigenvalue bound test (|a_p| ≤ 2√p) "
            f"on {len(self._eligible)} eligible ECs of {len(self._ecs)} "
            f"catalog × up to {len(_PRIMES_CACHE)} primes each"
        )

    def next(self) -> Optional[TheseusRecord]:
        if not self._eligible:
            return None
        for _ in range(20):
            idx = self._rng.choice(self._eligible)
            ec = self._ecs[idx]
            ap_list = _get_ap_list(ec)
            if not ap_list:
                self.attempts += 1
                continue
            # Pick a random prime index within the list bound.
            k = self._rng.randint(0, min(len(ap_list), len(_PRIMES_CACHE)) - 1)
            p = _PRIMES_CACHE[k]
            a_p = ap_list[k]
            # Test |a_p|^2 ≤ 4p exactly (avoids float sqrt).
            holds = (a_p * a_p) <= _hasse_bound_squared(p)
            self.attempts += 1

            label = _label(ec, "ec")
            canonical = (
                f"G3[SL2Z_Hasse] |a_{p}(ec:{label})| ≤ 2√{p} "
                f"| a_p={a_p}, |a_p|²={a_p * a_p}, 4p={4 * p} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if holds
                else f"g3_hasse_bound_violated_p={p}_at_{label}"
            )
            payload = {
                "ec_label": label,
                "prime": p,
                "a_p": a_p,
                "a_p_squared": a_p * a_p,
                "hasse_bound_squared": 4 * p,
                "holds": holds,
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
                method="exact_integer_hasse_bound",
                convergence_status="exact",
                extras={"role": "sl2z_hecke_eigenvalue_bound"},
            )
            self.emitted.append(record_id)
            return r
        return None
