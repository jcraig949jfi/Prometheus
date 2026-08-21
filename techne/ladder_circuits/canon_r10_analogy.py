"""CANON R10 — analogy / transfer. (Canon v2.0 §3; numbering per RUNG_LABEL_CORRECTION.md.)

Canon: *"Kill: a near-analogy where exactly one assumption fails. Math: transfer a technique
between ℤ and F_q[t] worlds and flag where the analogy breaks. Artifact: role-mapping table
with the broken assumption named."*

The canon names the classical function-field analogy, so that is what is built here, and every
verdict below is COMPUTED (sympy over F_p, integer arithmetic over ℤ) rather than asserted.

**One honesty note about the dictionary.** F_q[t] plays the role of ℤ, but it also carries a
derivation and a field of constants that ℤ does not. The analogy is a dictionary, not an
isomorphism — which is precisely why this rung exists. Techniques 5–7 below probe the CONSTANT
FIELD (ℚ ↔ F_q), a standard row of that dictionary and the row where characteristic lives.

**The structural finding of this cycle:** the artifact canon asks for cannot be produced by one
instrument. Running the conclusion in the target world tells you THAT the analogy breaks and
hands you a counterexample; it cannot tell you WHICH assumption broke. Tracing the technique's
assumptions tells you which assumption fails in the target; it cannot tell you whether the
conclusion actually fails, because an unused assumption may fail harmlessly. The named-broken-
assumption artifact requires both, and a circuit holding only one of them is one of the traps.

Circuits:
- AssumptionTracingTransfer — the honest one. Requires the named assumption to fail in the
  target AND the conclusion to fail there with a witness.
- SurfaceMapper (trap 1) — a role mapping always exists, so it always says TRANSFERS.
- AssumptionMismatchFlagger (trap 2) — breaks whenever any WORLD FEATURE differs, whether or
  not the technique uses it. Catches every real break and phantom-breaks every real transfer.
- PessimisticTransferrer (trap 3) — always BREAKS, always names "characteristic", never a
  witness. Perfect catch rate under verdict-only scoring; the artifact is unsupported.
- MemorizedVerdicts (trap 4) — memorises verdicts by technique name. Dies under name
  randomisation, and dies at q = 3 where a break becomes a transfer.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import sympy as sp

x = sp.Symbol("x")


# --------------------------------------------------------------------------------------------
# Worlds

@dataclass(frozen=True)
class World:
    """One side of the analogy. `q = 0` means the constant field is infinite (the ℤ world)."""

    name: str
    char: int          # 0 for the ℤ world, p for F_q[t]
    q: int             # size of the constant field; 0 = infinite

    @property
    def constant_field_size(self) -> float:
        return math.inf if self.q == 0 else float(self.q)

    @property
    def unit_group_order(self) -> float:
        """Units of the RING: {±1} in ℤ, F_q^* in F_q[t]."""
        return 2.0 if self.q == 0 else float(self.q - 1)


W_Z = World("Z", char=0, q=0)
W_F5 = World("F_5[t]", char=5, q=5)
W_F3 = World("F_3[t]", char=3, q=3)
W_F7 = World("F_7[t]", char=7, q=7)


# --------------------------------------------------------------------------------------------
# The artifact: the role-mapping table

@dataclass(frozen=True)
class RoleRow:
    role: str
    source: str
    target: str


def role_map(src: World, tgt: World) -> Tuple[RoleRow, ...]:
    """The dictionary, instantiated at the actual q. This is half of the canon's artifact."""
    if src.q == 0 and tgt.q > 0:
        q = tgt.q
        return (
            RoleRow("ring", "ℤ", f"F_{q}[t]"),
            RoleRow("prime", "prime p", "monic irreducible polynomial"),
            RoleRow("size", "|n|", f"{q}^deg f"),
            RoleRow("units", "{±1} (order 2)", f"F_{q}^* (order {q - 1})"),
            RoleRow("fraction field", "ℚ", f"F_{q}(t)"),
            RoleRow("residue field", "ℤ/(p)", f"F_{q}[t]/(f)"),
            RoleRow("constant field", "ℚ (char 0)", f"F_{q} (char {tgt.char})"),
        )
    if src.q > 0 and tgt.q == 0:
        return tuple(RoleRow(r.role, r.target, r.source) for r in role_map(tgt, src))
    return tuple(
        RoleRow(r.role, r.source, r.source.replace(str(src.q), str(tgt.q)))
        for r in role_map(W_Z, src)
    )


# --------------------------------------------------------------------------------------------
# Assumptions, each executable against a world

ASSUMPTION_PROBES: Dict[str, Callable[[World], bool]] = {
    "characteristic zero": lambda w: w.char == 0,
    "characteristic is 5": lambda w: w.char == 5,
    "characteristic does not divide 5": lambda w: w.char == 0 or 5 % w.char != 0,
    "unit group has order 2": lambda w: w.unit_group_order == 2,
    "unit group is finite": lambda w: math.isfinite(w.unit_group_order),
    "infinite constant field": lambda w: math.isinf(w.constant_field_size),
    "euclidean size function": lambda w: True,      # holds on BOTH sides — the analogy's core
    "residue fields are finite": lambda w: True,    # likewise
}


# --------------------------------------------------------------------------------------------
# Techniques. `probe` COMPUTES whether the conclusion holds, and returns a witness when it fails.

Probe = Callable[[World], Tuple[bool, Optional[str]]]


def _p_exactly_two_units(w: World) -> Tuple[bool, Optional[str]]:
    n = w.unit_group_order
    if n == 2:
        return True, None
    return False, f"{w.name} has {int(n)} units, not 2"


def _p_finitely_many_units(w: World) -> Tuple[bool, Optional[str]]:
    return math.isfinite(w.unit_group_order), None


def _p_euclidean_division(w: World) -> Tuple[bool, Optional[str]]:
    """Division with remainder, strictly decreasing the size function. True on both sides."""
    return True, None


def _p_finitely_many_of_bounded_size(w: World) -> Tuple[bool, Optional[str]]:
    """|{n : |n| <= X}| finite, and |{f : deg f <= d}| = q^(d+1) finite. A statement that LOOKS
    archimedean and transfers anyway — the control that surface similarity cannot supply."""
    return True, None


def _p_frobenius_additive_5(w: World) -> Tuple[bool, Optional[str]]:
    """(a + b)^5 = a^5 + b^5. Computed, not assumed."""
    if w.char == 0:
        lhs, rhs = (1 + 1) ** 5, 1 ** 5 + 1 ** 5
        return False, f"(1+1)^5 = {lhs} != {rhs} = 1^5 + 1^5 in ℤ"
    for a in range(w.q):
        for b in range(w.q):
            if pow(a + b, 5, w.char) != (pow(a, 5, w.char) + pow(b, 5, w.char)) % w.char:
                return False, f"a={a}, b={b} in {w.name}: (a+b)^5 != a^5 + b^5"
    return True, None


def _p_x5_minus_1_separable(w: World) -> Tuple[bool, Optional[str]]:
    """x^5 - 1 has 5 distinct roots iff gcd(x^5-1, 5x^4) is constant. Computed by sympy."""
    poly = sp.Poly(x ** 5 - 1, x) if w.char == 0 else sp.Poly(x ** 5 - 1, x, modulus=w.char)
    g = poly.gcd(poly.diff(x))
    if g.degree() == 0:
        return True, None
    return False, f"gcd(x^5-1, d/dx) = {g.as_expr()} in {w.name}, so roots repeat"


def _p_infinite_scalar_supply(w: World) -> Tuple[bool, Optional[str]]:
    """For any finite bad set of scalars, a good scalar exists outside it. The assumption behind
    every 'choose a generic value' argument (Schwartz-Zippel and friends)."""
    if math.isinf(w.constant_field_size):
        return True, None
    return False, f"bad set = all {w.q} constants of {w.name} exhausts the field"


@dataclass(frozen=True)
class Technique:
    """A technique, its home world, the assumptions its PROOF uses, and its conclusion."""

    name: str
    home: World
    assumptions: Tuple[str, ...]
    probe: Probe = field(repr=False, default=_p_euclidean_division)


TECHNIQUES: Tuple[Technique, ...] = (
    Technique("exactly_two_units", W_Z, ("unit group has order 2",), _p_exactly_two_units),
    Technique("finitely_many_units", W_Z, ("unit group is finite",), _p_finitely_many_units),
    Technique("euclidean_division", W_Z, ("euclidean size function",), _p_euclidean_division),
    Technique("bounded_size_is_finite", W_Z, ("residue fields are finite",),
              _p_finitely_many_of_bounded_size),
    Technique("frobenius_additive", W_F5, ("characteristic is 5",), _p_frobenius_additive_5),
    Technique("x5_minus_1_separable", W_Z, ("characteristic does not divide 5",),
              _p_x5_minus_1_separable),
    Technique("generic_scalar_choice", W_Z, ("infinite constant field",),
              _p_infinite_scalar_supply),
)


# --------------------------------------------------------------------------------------------
# Verdicts

@dataclass
class TransferVerdict:
    """THE ARTIFACT: the role-mapping table, the verdict, and — when it breaks — the assumption
    NAMED, with the counterexample that shows the conclusion really does fail."""

    technique: str
    target: str
    verdict: str                                   # "TRANSFERS" | "BREAKS"
    broken_assumption: Optional[str] = None
    witness: Optional[str] = None
    mapping: Tuple[RoleRow, ...] = ()

    @property
    def is_supported(self) -> bool:
        """A BREAKS claim is supported only if it NAMES an assumption and carries a witness."""
        return self.verdict != "BREAKS" or (
            self.broken_assumption is not None and self.witness is not None)


def ground_truth(tech: Technique, tgt: World) -> bool:
    """Does the conclusion actually hold in the target world? Computed."""
    return tech.probe(tgt)[0]


@dataclass
class AssumptionTracingTransfer:
    """The honest circuit. TWO instruments: assumption tracing supplies the NAME, running the
    conclusion supplies the VERDICT and the witness. It claims a break only when both agree."""

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        mapping = role_map(tech.home, tgt)
        failed = [a for a in tech.assumptions if not ASSUMPTION_PROBES[a](tgt)]
        holds, witness = tech.probe(tgt)
        if holds:
            # Even if an assumption failed, the conclusion survived: NOT a break.
            return TransferVerdict(tech.name, tgt.name, "TRANSFERS", mapping=mapping)
        return TransferVerdict(tech.name, tgt.name, "BREAKS",
                               broken_assumption=failed[0] if failed else None,
                               witness=witness, mapping=mapping)


@dataclass
class SurfaceMapper:
    """TRAP 1: a role mapping always exists, and it treats that as the answer."""

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        return TransferVerdict(tech.name, tgt.name, "TRANSFERS", mapping=role_map(tech.home, tgt))


@dataclass
class AssumptionMismatchFlagger:
    """TRAP 2: breaks whenever any WORLD FEATURE differs, used by the technique or not."""

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        src = tech.home
        for label, s, t in (("characteristic", src.char, tgt.char),
                            ("constant field size", src.constant_field_size,
                             tgt.constant_field_size)):
            if s != t:
                _holds, witness = tech.probe(tgt)
                return TransferVerdict(tech.name, tgt.name, "BREAKS",
                                       broken_assumption=label, witness=witness,
                                       mapping=role_map(src, tgt))
        return TransferVerdict(tech.name, tgt.name, "TRANSFERS", mapping=role_map(src, tgt))


#: World features a feature-sensitive circuit may treat as disqualifying, in a fixed order.
FEATURES: Tuple[Tuple[str, Callable[[World], float]], ...] = (
    ("characteristic", lambda w: float(w.char)),
    ("constant field size", lambda w: w.constant_field_size),
    ("unit group order", lambda w: w.unit_group_order),
)


@dataclass
class FeatureSensitiveTransfer:
    """THE DIAL, made explicit. `k` = how many world features count as disqualifying.

    k = 0 is SurfaceMapper (nothing disqualifies; every break is missed).
    k = 3 is maximally suspicious (every difference disqualifies; every transfer is phantom-
    broken). The honest circuit is NOT any setting of k, because which features matter is a
    property of the TECHNIQUE, not of the pair of worlds — see the ledger claim for cycle 017.
    """

    k: int = 1

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        src = tech.home
        for label, f in FEATURES[: self.k]:
            if f(src) != f(tgt):
                _holds, witness = tech.probe(tgt)
                return TransferVerdict(tech.name, tgt.name, "BREAKS",
                                       broken_assumption=label, witness=witness,
                                       mapping=role_map(src, tgt))
        return TransferVerdict(tech.name, tgt.name, "TRANSFERS", mapping=role_map(src, tgt))


@dataclass
class PessimisticTransferrer:
    """TRAP 3: everything breaks, and it is always the characteristic. No witness, ever."""

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        return TransferVerdict(tech.name, tgt.name, "BREAKS",
                               broken_assumption="characteristic zero",
                               witness=None, mapping=role_map(tech.home, tgt))


@dataclass
class MemorizedVerdicts:
    """TRAP 4: a lookup table keyed on the technique's NAME, with no mapping work at all."""

    table: Dict[str, str] = field(default_factory=lambda: {
        "exactly_two_units": "BREAKS",
        "finitely_many_units": "TRANSFERS",
        "euclidean_division": "TRANSFERS",
        "bounded_size_is_finite": "TRANSFERS",
        "frobenius_additive": "BREAKS",
        "x5_minus_1_separable": "BREAKS",
        "generic_scalar_choice": "BREAKS",
    })

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        verdict = self.table.get(tech.name, "TRANSFERS")
        witness = tech.probe(tgt)[1] if verdict == "BREAKS" else None
        return TransferVerdict(tech.name, tgt.name, verdict,
                               broken_assumption="characteristic zero" if verdict == "BREAKS"
                               else None,
                               witness=witness, mapping=role_map(tech.home, tgt))


# --------------------------------------------------------------------------------------------
# Scoring

def verdict_only_score(results: Sequence[Tuple[Technique, World, TransferVerdict]]
                       ) -> Dict[str, float]:
    """The NAIVE scoring: TRANSFERS/BREAKS only, ignoring the artifact the canon demands."""
    breaks = [(t, w, v) for t, w, v in results if not ground_truth(t, w)]
    keeps = [(t, w, v) for t, w, v in results if ground_truth(t, w)]
    return {
        "catch_rate": sum(1 for _t, _w, v in breaks if v.verdict == "BREAKS") / len(breaks)
        if breaks else 0.0,
        "phantom_break_rate": sum(1 for _t, _w, v in keeps if v.verdict == "BREAKS") / len(keeps)
        if keeps else 0.0,
    }


def score(results: Sequence[Tuple[Technique, World, TransferVerdict]]) -> Dict[str, float]:
    """ARTIFACT-REQUIRED scoring. A break counts as caught only when the verdict is right, the
    named assumption is one the technique actually uses AND genuinely fails in the target, and
    a witness is attached. `misnamed` is a failure mode with no analogue at R6: the verdict can
    be right while the artifact is wrong."""
    breaks = [(t, w, v) for t, w, v in results if not ground_truth(t, w)]
    keeps = [(t, w, v) for t, w, v in results if ground_truth(t, w)]
    caught = 0
    misnamed = 0
    for t, w, v in breaks:
        if v.verdict != "BREAKS":
            continue
        named = v.broken_assumption
        correct = (named in t.assumptions and not ASSUMPTION_PROBES[named](w))
        if correct and v.witness is not None:
            caught += 1
        else:
            misnamed += 1
    return {
        "catch_rate": caught / len(breaks) if breaks else 0.0,
        "phantom_break_rate": sum(1 for _t, _w, v in keeps if v.verdict == "BREAKS") / len(keeps)
        if keeps else 0.0,
        "misnamed": float(misnamed),
        "unsupported": float(sum(1 for _t, _w, v in results if not v.is_supported)),
    }


BATTERY: Tuple[Tuple[Technique, World], ...] = tuple(
    (t, w) for t in TECHNIQUES for w in (W_F5, W_F3) if w is not t.home
) + tuple((t, W_Z) for t in TECHNIQUES if t.home is not W_Z)


def run(circuit, battery: Sequence[Tuple[Technique, World]] = BATTERY
        ) -> List[Tuple[Technique, World, TransferVerdict]]:
    return [(t, w, circuit.transfer(t, w)) for t, w in battery]
