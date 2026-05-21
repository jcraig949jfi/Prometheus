"""G1 — Galois twist invariance test.

Two elliptic curves over Q sharing the same j-invariant are related by a
quadratic (or for j=0/1728, sextic/quartic) twist. The Galois twist
action on Q(E) factors through Gal(K/Q) for some abelian extension K/Q;
on the curve's invariants, the twist preserves some (j-invariant, the
isogeny class up to twist) and breaks others (conductor, regulator,
rank parity in some cases).

G1's claim shape: pick a twist-pair (E1, E2) — two catalog ECs sharing
exactly the same rational j-invariant — and a target invariant I, then
emit:
    "I(E1) == I(E2) for twist-class j={j_str}"
with verdict based on observed equality.

The substrate downstream will route SHADOW_CATALOG observations to
sigma's verification pipeline; the kill_pattern names which Galois
twist invariant the substrate failed.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from theseus.config import BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _label,
    EC_INTEGER_INVARIANTS,
)
from theseus.generators.base import Generator, GeneratorStatus


def _j_invariant_from_ainvs(ainvs: List[int]) -> Optional[Fraction]:
    """Compute j = 1728 c4^3 / Delta from a-invariants exactly.

    Returns None if Delta = 0 (the curve is singular — shouldn't happen
    in LMFDB catalogs, but defensive)."""
    if not ainvs or len(ainvs) != 5:
        return None
    try:
        a1, a2, a3, a4, a6 = (int(x) for x in ainvs)
    except (TypeError, ValueError):
        return None
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = (
        a1 * a1 * a6
        - a1 * a3 * a4
        + 4 * a2 * a6
        + a2 * a3 * a3
        - a4 * a4
    )
    c4 = b2 * b2 - 24 * b4
    delta = (
        -(b2 * b2) * b8
        - 8 * (b4 ** 3)
        - 27 * (b6 * b6)
        + 9 * b2 * b4 * b6
    )
    if delta == 0:
        return None
    return Fraction(c4 ** 3, delta)


def _build_j_groups(ecs: List[Dict[str, Any]]) -> Dict[Fraction, List[int]]:
    """Group EC indices by exact rational j-invariant. Returns
    {j: [idx, ...]}. Singletons are kept (caller filters)."""
    groups: Dict[Fraction, List[int]] = {}
    for idx, e in enumerate(ecs):
        ainvs = e.get("base", {}).get("ainvs")
        if not ainvs:
            continue
        j = _j_invariant_from_ainvs(ainvs)
        if j is None:
            continue
        groups.setdefault(j, []).append(idx)
    return groups


def _get_int(obj: Dict[str, Any], key: str) -> Optional[int]:
    if "base" in obj and key in obj["base"]:
        v = obj["base"][key]
    elif "rich" in obj and key in obj["rich"]:
        v = obj["rich"][key]
    elif key in obj:
        v = obj[key]
    else:
        return None
    if isinstance(v, (int, float)) and v == int(v):
        return int(v)
    return None


class G1GaloisTwistGenerator(Generator):
    generator_id = "g1"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 2048) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Pre-compute twist groups at init. With 1000 ECs this is cheap.
        full = _build_j_groups(self._ecs)
        self._groups: List[Tuple[Fraction, List[int]]] = [
            (j, idxs) for j, idxs in full.items() if len(idxs) >= 2
        ]

    def description(self) -> str:
        n_pairs = sum(
            len(idxs) * (len(idxs) - 1) // 2 for _, idxs in self._groups
        )
        return (
            f"g1: Galois twist invariance (EC×EC sharing exact j-invariant); "
            f"{len(self._groups)} twist-classes spanning {n_pairs} pairs "
            f"× {len(EC_INTEGER_INVARIANTS)} invariants"
        )

    def next(self) -> Optional[TheseusRecord]:
        if not self._groups:
            return None
        for _ in range(20):
            j_val, idxs = self._rng.choice(self._groups)
            i1, i2 = self._rng.sample(idxs, 2)
            inv = self._rng.choice(EC_INTEGER_INVARIANTS)
            e1 = self._ecs[i1]
            e2 = self._ecs[i2]
            v1 = _get_int(e1, inv)
            v2 = _get_int(e2, inv)
            if v1 is None or v2 is None:
                self.attempts += 1
                continue

            holds = v1 == v2
            self.attempts += 1

            l1 = _label(e1, "ec")
            l2 = _label(e2, "ec")
            j_str = f"{j_val.numerator}/{j_val.denominator}" if j_val.denominator != 1 else str(j_val.numerator)
            canonical = (
                f"G1[twist] {inv}(ec:{l1}) == {inv}(ec:{l2}) "
                f"| j={j_str} | {v1} vs {v2} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if holds
                else f"g1_twist_breaks_{inv}_at_j={j_str[:16]}"
            )
            payload = {
                "twist_class_j": j_str,
                "ec_a": l1,
                "ec_b": l2,
                "invariant": inv,
                "value_a": v1,
                "value_b": v2,
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
                method="exact_j_grouping",
                convergence_status="exact",
                extras={"role": "galois_twist_invariance"},
            )
            self.emitted.append(record_id)
            return r
        return None
