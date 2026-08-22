"""Claims that carry their domain — and the FOUR kinds, derived rather than surveyed.

(Cycle 030 built two of them; cycle 031 derived all four and found the missing pair.)

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

So a witnessed existential may eventually be stated absolutely; an aggregate never may.

**Cycle 031 replaced that two-item list with a derivation.** Write a domain-relative claim as an
aggregation over the domain's elements, `Phi(O, D) = A({phi(O, x) : x in D})`. Its behaviour
under domain extension is inherited entirely from `A`'s monotonicity under multiset extension,
and "monotone up?" and "monotone down?" are two independent booleans — so there are exactly four
kinds, and the taxonomy cannot grow without someone finding a third monotonicity direction. The
two cycle-030 kinds were the off-diagonal; UNIVERSAL and INVARIANT are the two I had missed. See
the derivation block at the foot of this module.

**What it deliberately refuses:** a claim constructed without a domain. Not defaulted to "all
inputs", not defaulted to the sample in hand — refused, because every one of the three arrivals
above was an undeclared default being read as universal.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, Sequence, Tuple

__all__ = ["Domain", "RelativeClaim", "EXISTENTIAL", "UNIVERSAL", "INVARIANT", "AGGREGATE",
           "ClaimError", "kind_from_monotonicity", "probe_monotonicity", "KIND_TABLE"]

EXISTENTIAL = "EXISTENTIAL"      # monotone UP:   once witnessed, holds on every superset
UNIVERSAL = "UNIVERSAL"          # monotone DOWN: holds on every subset; broken by widening
INVARIANT = "INVARIANT"          # monotone BOTH: independent of the domain entirely
AGGREGATE = "AGGREGATE"          # monotone NEITHER: normalised, so it moves both ways


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
        if self.kind not in (EXISTENTIAL, UNIVERSAL, INVARIANT, AGGREGATE):
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
        if self.kind == UNIVERSAL and not bool(self.value) and self.witness is None:
            raise ClaimError(
                f"a FAILED universal ({self.property_name!r}) needs its counterexample; the "
                "negation of a universal is an existential, and it travels only with its witness")

    @property
    def is_upward_closed(self) -> bool:
        """Survives domain GROWTH. An invariant, a witnessed positive existential, or a failed
        universal (whose counterexample is itself a witness)."""
        if self.kind == INVARIANT:
            return True
        if self.kind == EXISTENTIAL:
            return bool(self.value) and self.witness is not None
        if self.kind == UNIVERSAL:
            return (not bool(self.value)) and self.witness is not None
        return False

    @property
    def is_downward_closed(self) -> bool:
        """Survives domain SHRINKAGE. An invariant, or a holding universal — every subset of a
        set on which P holds everywhere also has P holding everywhere."""
        if self.kind == INVARIANT:
            return True
        if self.kind == UNIVERSAL:
            return bool(self.value)
        return False

    def entails_on(self, other: Domain) -> bool:
        """Does this claim, as measured, already hold on `other` without re-measuring?

        The four cases fall straight out of the 2x2:

            INVARIANT             any domain — the claim never depended on one
            EXISTENTIAL positive  any SUPERSET — the witness is still in there
            EXISTENTIAL negative  nothing. "No witness in D" says nothing about D union anything
            UNIVERSAL positive    any SUBSET — holding everywhere is inherited downward
            UNIVERSAL negative    any SUPERSET — the counterexample is still in there
            AGGREGATE             nothing, ever, not even its own domain: re-measure
        """
        if self.kind == INVARIANT:
            return True
        if self.is_upward_closed and other.contains_all_of(self.domain):
            return True
        if self.is_downward_closed and self.domain.contains_all_of(other):
            return True
        return False

    def state_absolutely(self) -> str:
        """Render the claim without a domain qualifier — permitted only when it is upward-closed.

        Raises otherwise, which is the whole point: an aggregate quoted absolutely is the defect
        that showed up three separate times.
        """
        if self.kind == INVARIANT:
            return f"{self.property_name} = {self.value!r} (independent of domain)"
        if not self.is_upward_closed:
            raise ClaimError(
                f"{self.property_name!r} is {self.kind} and cannot be stated absolutely; it holds "
                f"relative to domain {self.domain.name!r} ({len(self.domain)} members, "
                f"digest {self.domain.digest})")
        return f"{self.property_name} = {self.value!r} (witness: {self.witness!r})"

    def render(self) -> str:
        return (f"{self.property_name} = {self.value!r} on domain {self.domain.name!r} "
                f"(n={len(self.domain)}, digest={self.domain.digest}, kind={self.kind})")


# =============================================================================================
# The derivation (cycle 031) — the kinds are not a list, they are the cells of a 2x2.
#
# Write a domain-relative claim as an aggregation over the domain's elements:
#
#     Phi(O, D) = A({ phi(O, x) : x in D })
#
# Its behaviour under domain extension is inherited entirely from A's monotonicity under
# MULTISET EXTENSION, and there are exactly four possibilities because "monotone up?" and
# "monotone down?" are two independent booleans:
#
#     up   down   kind          example aggregations
#     ---------------------------------------------------------------------------
#     T    F      EXISTENTIAL   any / max / count / sum of non-negatives
#     F    T      UNIVERSAL     all / min-as-a-requirement
#     T    T      INVARIANT     an A that ignores the multiset (a constant)
#     F    F      AGGREGATE     mean / rate / entropy / variance — anything NORMALISED
#
# The classification is exhaustive by construction rather than by survey, which is what
# HITL #112 asked for.
#
# ---------------------------------------------------------------------------------------------
# CYCLE 033 — the normal form generalises to finite ARITY, and two preconditions were missing.
#
# Cycle 031 declared a soft spot (HITL #117): the derivation assumed every domain-relative claim
# is an aggregation over INDEPENDENT PER-ELEMENT values, and irreducibly RELATIONAL claims —
# "the domain contains two elements that disagree", which is exactly what `find_aliasing_witness`
# computes — did not obviously fit.
#
# **They fit. The repair is arity.**
#
#     Phi(O, D) = A({ phi(O, t) : t in D^k })      for some fixed k
#
# Monotonicity survives untouched, because D subset D' implies D^k subset D'^k. Measured at
# k = 2 over a threshold-crossing chain:
#
#     aliasing        (exists over D^2)   values 0,1,1,1     -> EXISTENTIAL
#     consistency     (forall over D^2)   values 1,0,0,0     -> UNIVERSAL
#     min pairwise distance (min over D^2) values 10,5,1     -> UNIVERSAL
#
# So the 2x2 stands and the exhaustiveness claim survives, over a wider normal form than the one
# it was stated for. But testing it surfaced two preconditions that were never written down:
#
#   (P1) `phi` MUST NOT READ THE DOMAIN, and in particular not |D|. A predicate that does is
#        normalised, and lands in AGGREGATE — the cycle-031 rate defect, now at arity 2.
#        Measured: "at least half of D is even" reads 1,1,0,1 over a nested chain.
#
#   (P2) THE VALUE MUST BE MEANINGFULLY ORDERED. "Monotone" is undefined otherwise, and the
#        empirical classifier will not notice: asked to classify an ARGMIN (which pair is
#        closest — a selection, not a magnitude) it returned UNIVERSAL, purely because Python
#        orders tuples lexicographically. The verdict was meaningless. `probe_monotonicity` now
#        refuses non-numeric values rather than producing one. Booleanise the selection first
#        ("is (0,1) the closest pair?") and it classifies honestly — EXISTENTIAL, measured.
# ---------------------------------------------------------------------------------------------
#
# **The load-bearing observation is that normalisation is what destroys monotonicity**, and it
# is measurable on one statistic rather than argued. Cycle 031, F6 over real candidates:
#
#     domain size    COUNT of firings    RATE of firings
#             20                    0             0.0000
#             23                    3   up        0.1304   up
#             53                    3   same      0.0566   DOWN
#             81                    3   same      0.0370   DOWN
#
# Same predicate, same data, same firings. The count is monotone up; dividing it by |D| makes
# it move both ways. So a claim's kind is a property of its AGGREGATION OPERATOR, not of its
# subject matter — and "is this rate a fact about the object?" always answers no.
# =============================================================================================

KIND_TABLE = {
    (True, False): EXISTENTIAL,
    (False, True): UNIVERSAL,
    (True, True): INVARIANT,
    (False, False): AGGREGATE,
}


def kind_from_monotonicity(monotone_up: bool, monotone_down: bool) -> str:
    """The 2x2, as code. Every combination of the two booleans maps to a kind, so the taxonomy
    cannot acquire a fifth member without someone finding a third monotonicity direction."""
    return KIND_TABLE[(bool(monotone_up), bool(monotone_down))]


def probe_monotonicity(measure, chain: Sequence[Domain]) -> str:
    """Classify a claim EMPIRICALLY by running it along a chain of nested growing domains.

    `chain` must be increasing and `measure(domain)` must return a NUMBER — see (P2) in the
    derivation block: an unordered value makes "monotone" meaningless, and this function used to
    return a confident kind for one. Returns the kind implied by the observed monotonicity.
    Evidence, not proof — a chain that happens not to exhibit a
    decrease will classify a genuinely non-monotone measure as monotone, which is the same
    sampling limit the constancy probe has. Use it to CLASSIFY, then keep the chain on record.
    """
    if len(chain) < 2:
        raise ClaimError("classifying monotonicity needs at least two nested domains")
    for a, b in zip(chain, chain[1:]):
        if not b.contains_all_of(a):
            raise ClaimError(f"domain chain is not increasing at {a.name!r} -> {b.name!r}")
    values = [measure(d) for d in chain]
    for v in values:
        if isinstance(v, bool):
            continue
        if not isinstance(v, (int, float)) or isinstance(v, complex):
            raise ClaimError(
                f"cannot classify a claim whose value is {type(v).__name__}: 'monotone' needs a "
                "meaningfully ordered value. Python will happily order tuples and strings "
                "lexicographically and this function would return a kind that means nothing "
                "(measured: an argmin-valued claim classified as UNIVERSAL on tuple ordering "
                "alone). Booleanise the selection, or map it to a magnitude, first")
    up = all(b >= a for a, b in zip(values, values[1:]))
    down = all(b <= a for a, b in zip(values, values[1:]))
    return kind_from_monotonicity(up, down)
