"""Claims that carry their domain — and the two kinds that behave differently. (Cycle 030.)

Three independent arrivals of the same complaint prompted this:

- **R11 (cycle 020)** — a forecaster that picks its own reference class can pick a flattering one.
- **Battery strength (cycle 028)** — F6 measured 0.9082 bits on a narrow candidate band and
  0.2285 on a wide one.
- **Constancy (cycle 029)** — F11 is constant on well-formed input and VARIES under hostile input.

The shared core is real: each is a property `Φ(O, D)` of an object AND a domain, stated as though
it were a property of the object alone, with the speaker choosing `D`. That much unifies, and the
fix is the same — make `D` part of the claim and refuse a claim that lacks one.

**But the unification is PARTIAL, and the split is the finding.** The three do not behave the same
way when `D` grows:

- **EXISTENTIAL** claims (`∃ x ∈ D` with some property) are **monotone**. A witness stays a
  witness, so a positive existential holds on every superset of the domain it was found in.
  Measured: F11 reads UNSETTLED on well-formed input, VARIES once hostile input is added, and
  VARIES on every superset thereafter. Only the NEGATIVE — "no witness found in D" — is
  domain-relative.
- **AGGREGATE** claims (an average or entropy over `D`) are **non-monotone**, and not merely
  decreasing. Measured on F6: 0.0000 bits on a subset excluding every firing case, 0.3651 after
  adding them, 0.2285 on the full set. Widening moved it **up and then down**. Every aggregate
  value is domain-relative in both directions, permanently.

So a witnessed existential may eventually be stated absolutely; an aggregate never may. This
module encodes that difference rather than treating all three arrivals as one thing.

**What it deliberately refuses:** a claim constructed without a domain. Not defaulted to "all
inputs", not defaulted to the sample in hand — refused, because every one of the three arrivals
above was an undeclared default being read as universal.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, Sequence, Tuple

__all__ = ["Domain", "RelativeClaim", "EXISTENTIAL", "AGGREGATE", "ClaimError"]

EXISTENTIAL = "EXISTENTIAL"
AGGREGATE = "AGGREGATE"


class ClaimError(ValueError):
    """Raised when a claim is malformed, or asserted without the domain it depends on."""


@dataclass(frozen=True)
class Domain:
    """A named, content-addressed set of inputs a claim was measured over.

    The digest exists so a claim can be checked rather than trusted: two parties quoting
    "strength 0.23 on the wide band" can confirm they mean the same band.
    """

    name: str
    members: Tuple[Any, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ClaimError("a domain must be named; an anonymous domain cannot be quoted")
        if not self.members:
            raise ClaimError(
                f"domain {self.name!r} is empty: a claim measured over nothing is not a weak "
                "claim, it is not a claim")

    @property
    def digest(self) -> str:
        try:
            blob = json.dumps([repr(m) for m in self.members], sort_keys=True)
        except (TypeError, ValueError):          # pragma: no cover - repr always works
            blob = repr(self.members)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def __len__(self) -> int:
        return len(self.members)

    def contains_all_of(self, other: "Domain") -> bool:
        """Is `other` a subset of this domain? Compared by member repr, so that domains built
        separately but holding equal values still compare equal."""
        mine = {repr(m) for m in self.members}
        return {repr(m) for m in other.members} <= mine


@dataclass(frozen=True)
class RelativeClaim:
    """A measured property, the domain it was measured on, and which kind of claim it is.

    `witness` is required for a positive EXISTENTIAL and is what makes it upward-closed: the
    claim travels to a superset only because the witness does.
    """

    property_name: str
    value: Any
    domain: Domain
    kind: str
    witness: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.kind not in (EXISTENTIAL, AGGREGATE):
            raise ClaimError(f"unknown claim kind {self.kind!r}")
        if not isinstance(self.domain, Domain):
            raise ClaimError(
                f"{self.property_name!r} was asserted without a domain. Not defaulted to 'all "
                "inputs' and not defaulted to the sample in hand — an undeclared domain is how "
                "a measurement becomes a universal claim by accident")
        if self.kind == EXISTENTIAL and bool(self.value) and self.witness is None:
            raise ClaimError(
                f"a positive existential ({self.property_name!r}) needs its witness; without one "
                "it cannot travel to a superset and is just an aggregate in disguise")

    @property
    def is_upward_closed(self) -> bool:
        """Does this claim survive domain growth? Only a witnessed positive existential does."""
        return self.kind == EXISTENTIAL and bool(self.value) and self.witness is not None

    def entails_on(self, other: Domain) -> bool:
        """Does this claim, as measured, already hold on `other` without re-measuring?

        Witnessed positive existential: yes, on any superset — the witness is still in there.
        Negative existential: no. "No witness in D" says nothing about D ∪ anything.
        Aggregate: never. Measured non-monotone in both directions, so a superset value cannot
        be inferred at all, only re-measured.
        """
        if not self.is_upward_closed:
            return False
        return other.contains_all_of(self.domain)

    def state_absolutely(self) -> str:
        """Render the claim without a domain qualifier — permitted only when it is upward-closed.

        Raises otherwise, which is the whole point: an aggregate quoted absolutely is the defect
        that showed up three separate times.
        """
        if not self.is_upward_closed:
            raise ClaimError(
                f"{self.property_name!r} is {self.kind} and cannot be stated absolutely; it holds "
                f"relative to domain {self.domain.name!r} ({len(self.domain)} members, "
                f"digest {self.domain.digest})")
        return f"{self.property_name} = {self.value!r} (witness: {self.witness!r})"

    def render(self) -> str:
        return (f"{self.property_name} = {self.value!r} on domain {self.domain.name!r} "
                f"(n={len(self.domain)}, digest={self.domain.digest}, kind={self.kind})")
