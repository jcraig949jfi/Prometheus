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

import dataclasses
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
    #: The dual, and the assumption behind every Weil-bound / character-sum argument: those
    #: proofs need the constant field to be FINITE, which is exactly what ℤ does not supply.
    "finite constant field": lambda w: w.q > 0,
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
    #: Subset of `assumptions` the SOURCE proof genuinely uses; None means "all of them".
    #: Declaring an assumption the proof never touches is the gaming route flagged in cycle 017
    #: and made auditable by `prometheus_math.lean_oracle.traced_classes`.
    used_in_source_proof: Optional[Tuple[str, ...]] = None


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
    """THE ARTIFACT: the role-mapping table, the assumption NAMED when one breaks, the witness,
    and — added cycle 018 on external review — **two orthogonal status fields**.

    `assumption_status` ∈ {PRESERVED, BROKEN} and `conclusion_status` ∈ {SURVIVES, REFUTED,
    UNKNOWN} are independent, because a broken assumption does not entail a false conclusion
    (see `test_AN_ASSUMPTION_CAN_FAIL_HARMLESSLY`). Collapsing them loses exactly the
    distinction the rung is for, so `verdict` is DERIVED from the pair and (BROKEN, UNKNOWN)
    derives to UNVERIFIED rather than to BREAKS.
    """

    technique: str
    target: str
    verdict: str                                   # "TRANSFERS" | "BREAKS" | "UNVERIFIED"
    broken_assumption: Optional[str] = None
    witness: Optional[str] = None                  # CONCLUSION-channel evidence
    mapping: Tuple[RoleRow, ...] = ()
    assumption_status: str = "PRESERVED"           # "PRESERVED" | "BROKEN"
    conclusion_status: str = "SURVIVES"            # "SURVIVES" | "REFUTED" | "UNKNOWN"
    assumption_witness: Optional[str] = None       # ASSUMPTION-channel evidence
    used_in_source_proof: Optional[bool] = None    # was the named assumption used at home?

    @property
    def is_supported(self) -> bool:
        """A BREAKS claim is supported only if it NAMES an assumption and carries a witness."""
        return self.verdict != "BREAKS" or (
            self.broken_assumption is not None and self.witness is not None)

    @property
    def is_supported_strict(self) -> bool:
        """CYCLE 019, replacing the cycle-018 repair, which was right about the bug and wrong
        about the rule.

        Cycle 018 demanded that a witness witness the CONCLUSION. External review (round 7)
        pointed out that this is too strong as a universal rule: assumption-side evidence is
        the *correct* artifact for an assumption-failure claim. In F_3, `3 * 1 = 0` legitimately
        certifies that the characteristic is not 5 — it simply cannot certify that the
        conclusion is false.

        So the rule is evidence TYPING, not conclusion-preference:

            **every artifact must witness the proposition attached to its own verdict.**

        - `assumption_status == BROKEN` requires assumption-channel evidence.
        - `conclusion_status == REFUTED` requires conclusion-channel evidence.
        - A `BREAKS` verdict asserts both, so it needs both.

        The collapser bug was a type confusion between evidence channels, not a missing witness.
        """
        if self.assumption_status == "BROKEN" and self.assumption_witness is None:
            return False
        if self.conclusion_status == "REFUTED" and self.witness is None:
            return False
        if self.verdict == "BREAKS":
            return (self.broken_assumption is not None
                    and self.witness is not None
                    and self.conclusion_status == "REFUTED")
        return True


#: Assumption-channel evidence: what makes an assumption failure CERTIFIED rather than asserted.
#: The reviewer supplied the first entry as the motivating case: in F_3, 3 * 1 = 0 certifies
#: that the characteristic is not 5, and that is a perfectly good artifact -- for THAT claim.
ASSUMPTION_WITNESSES: Dict[str, Callable[[World], str]] = {
    "characteristic is 5":
        lambda w: (f"{w.char} * 1 = 0 in {w.name}, so char = {w.char}, not 5" if w.char
                   else f"n * 1 != 0 for every n in {w.name}, so char = 0, not 5"),
    "characteristic zero":
        lambda w: f"{w.char} * 1 = 0 in {w.name}, so the characteristic is not 0",
    "characteristic does not divide 5":
        lambda w: f"char({w.name}) = {w.char} divides 5",
    "unit group has order 2":
        lambda w: f"{w.name} has {int(w.unit_group_order)} units, not 2",
    "unit group is finite":
        lambda w: f"the unit group of {w.name} is infinite",
    "infinite constant field":
        lambda w: f"the constant field of {w.name} has exactly {w.q} elements",
    "finite constant field":
        lambda w: f"the constant field of {w.name} is infinite (it contains 1/n for every n)",
}


def assumption_witness(name: str, w: World) -> str:
    """Certify an assumption FAILURE in `w`.

    Falls back to a generic statement rather than returning None, because an uncertified
    assumption claim is what this cycle forbids -- but the fallback is marked in its own text so
    an audit can find it.
    """
    gen = ASSUMPTION_WITNESSES.get(name)
    if gen is not None:
        return gen(w)
    for a in (2, 3, 5, 6, 10, 11):
        if name == f"{a} is a nonsquare in the constant field" and w.q:
            r = next((r for r in range(w.q) if (r * r - a) % w.q == 0), None)
            return f"{r}^2 = {a} mod {w.q}, so {a} is a square in the constant field of {w.name}"
    return f"[unspecified] assumption {name!r} evaluates false in {w.name}"


def used_assumptions(tech: "Technique") -> Tuple[str, ...]:
    """Which declared assumptions the SOURCE proof actually uses. Defaults to all of them; a
    technique may declare more than it uses, which is the gaming route the Lean tracer audits."""
    return tech.assumptions if tech.used_in_source_proof is None else tech.used_in_source_proof


def derive_verdict(assumption_status: str, conclusion_status: str) -> str:
    """The only sanctioned collapse of the two fields into one label.

    (·, REFUTED)  -> BREAKS       the analogy demonstrably fails here
    (·, SURVIVES) -> TRANSFERS    the conclusion holds, whatever the assumptions did
    (·, UNKNOWN)  -> UNVERIFIED   not enough reality-bits for a verdict — NOT a refutation
    """
    if conclusion_status == "REFUTED":
        return "BREAKS"
    if conclusion_status == "SURVIVES":
        return "TRANSFERS"
    return "UNVERIFIED"


@dataclass(frozen=True)
class Audit:
    """The result of checking a verdict against the world instead of against its own labels."""

    typed_ok: bool          # passes the declaration-level typing check
    verified_ok: bool       # survives independent re-derivation of every status it asserts
    notes: Tuple[str, ...] = ()

    @property
    def sound(self) -> bool:
        return self.typed_ok and self.verified_ok


def audit_verdict(v: "TransferVerdict", tech: "Technique", tgt: World) -> Audit:
    """CYCLE 019, and the lesson that cost two red tests to learn.

    Round-7 review gave the rule *"evidence must witness the proposition attached to its own
    verdict"*, and I first implemented it as a check over the verdict's own fields. That does
    not hold: `UnknownCollapser` simply relabels its `conclusion_status` as REFUTED and moves
    the assumption witness into the conclusion slot, and the typed check waves it through.

    **A type the circuit declares is a label, not a type.** Typing is only load-bearing when
    something outside the circuit checks it, so this function re-derives every status from the
    world and compares. It is deliberately not a method on `TransferVerdict`: a verdict must not
    be able to certify itself.
    """
    notes = []
    truth = ground_truth(tech, tgt)
    really_broken = [a for a in tech.assumptions if not ASSUMPTION_PROBES[a](tgt)]

    expected_conclusion = {True: "SURVIVES", False: "REFUTED", None: "UNKNOWN"}[truth]
    if v.conclusion_status != expected_conclusion:
        notes.append(f"conclusion_status claims {v.conclusion_status}, world says "
                     f"{expected_conclusion}")
    expected_assumption = "BROKEN" if really_broken else "PRESERVED"
    if v.assumption_status != expected_assumption:
        notes.append(f"assumption_status claims {v.assumption_status}, world says "
                     f"{expected_assumption}")
    if v.broken_assumption is not None and v.broken_assumption not in really_broken:
        notes.append(f"names {v.broken_assumption!r}, which does not fail in {tgt.name}")
    if v.verdict != derive_verdict(expected_assumption, expected_conclusion):
        notes.append(f"verdict {v.verdict} is not what the world supports")

    return Audit(typed_ok=v.is_supported_strict, verified_ok=not notes, notes=tuple(notes))


def ground_truth(tech: Technique, tgt: World) -> Optional[bool]:
    """Does the conclusion actually hold in the target world? Computed, or None when open."""
    return tech.probe(tgt)[0]


@dataclass
class AssumptionTracingTransfer:
    """The honest circuit. TWO instruments: assumption tracing supplies the NAME, running the
    conclusion supplies the VERDICT and the witness. It claims a break only when both agree,
    and abstains when the conclusion is open in the target."""

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        mapping = role_map(tech.home, tgt)
        failed = [a for a in tech.assumptions if not ASSUMPTION_PROBES[a](tgt)]
        holds, witness = tech.probe(tgt)
        a_status = "BROKEN" if failed else "PRESERVED"
        c_status = {True: "SURVIVES", False: "REFUTED", None: "UNKNOWN"}[holds]
        named = failed[0] if failed else None
        return TransferVerdict(
            tech.name, tgt.name, derive_verdict(a_status, c_status),
            broken_assumption=named if c_status == "REFUTED" else None,
            witness=witness if c_status == "REFUTED" else None,
            mapping=mapping, assumption_status=a_status, conclusion_status=c_status,
            assumption_witness=assumption_witness(named, tgt) if named else None,
            used_in_source_proof=(named in used_assumptions(tech)) if named else None)


@dataclass
class UnknownCollapser:
    """TRAP 5 (external review, round 6): identical to the honest circuit except that it reads
    (BROKEN, UNKNOWN) as a refutation.

    This is the loop's oldest lesson in a new place — **absence of certification is not the
    opposite verdict** — and it is the trap most likely to be committed in good faith, because
    a witnessed assumption violation feels like evidence against the conclusion. It is not: the
    F_3 Frobenius case is a witnessed assumption violation whose conclusion holds.
    """

    def transfer(self, tech: Technique, tgt: World) -> TransferVerdict:
        v = AssumptionTracingTransfer().transfer(tech, tgt)
        if v.assumption_status == "BROKEN" and v.conclusion_status == "UNKNOWN":
            failed = [a for a in tech.assumptions if not ASSUMPTION_PROBES[a](tgt)]
            # The bug, stated precisely (round-7 review): it copies ASSUMPTION-channel evidence
            # into the CONCLUSION slot. The evidence itself is perfectly good -- it just does not
            # certify the proposition the verdict now asserts.
            return dataclasses.replace(v, verdict="BREAKS", broken_assumption=failed[0],
                                       witness=v.assumption_witness,
                                       conclusion_status="REFUTED")
        return v


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
    breaks = [(t, w, v) for t, w, v in results if ground_truth(t, w) is False]
    keeps = [(t, w, v) for t, w, v in results if ground_truth(t, w) is True]
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
    # Entries whose ground truth is None (open in the target) are scored by NEITHER rate —
    # they belong to the UNVERIFIED lane and counting them as breaks would bake the
    # UnknownCollapser's error into the scorer itself.
    breaks = [(t, w, v) for t, w, v in results if ground_truth(t, w) is False]
    keeps = [(t, w, v) for t, w, v in results if ground_truth(t, w) is True]
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
        "unsupported_strict": float(sum(1 for _t, _w, v in results
                                        if not v.is_supported_strict)),
    }


BATTERY: Tuple[Tuple[Technique, World], ...] = tuple(
    (t, w) for t in TECHNIQUES for w in (W_F5, W_F3) if w is not t.home
) + tuple((t, W_Z) for t in TECHNIQUES if t.home is not W_Z)


def run(circuit, battery: Sequence[Tuple[Technique, World]] = BATTERY
        ) -> List[Tuple[Technique, World, TransferVerdict]]:
    return [(t, w, circuit.transfer(t, w)) for t, w in battery]


# ============================================================================================
# Cycle 018 additions, from external review (round 6).
#
# Two extensions the reviewer asked for, and one they designed:
#   (a) a near-analogy whose break is a RESIDUE-CLASS property buried inside the technique,
#       so that no amount of world knowledge determines the verdict;
#   (b) techniques whose conclusion is OPEN in the target world, forcing the UNKNOWN state.
# ============================================================================================

def _is_nonsquare(a: int, w: World) -> bool:
    """Is `a` a nonsquare in the world's constant field? Computed."""
    if w.q == 0:                                   # ℚ: a is a square iff it is a perfect square
        r = math.isqrt(abs(a))
        return not (a >= 0 and r * r == a)
    return (a % w.q) not in {(s * s) % w.q for s in range(w.q)}


for _a in range(2, 12):
    ASSUMPTION_PROBES[f"{_a} is a nonsquare in the constant field"] = (
        lambda w, a=_a: _is_nonsquare(a, w))


def _p_quadratic_irreducible(a: int) -> Probe:
    """Conclusion: x^2 - a is irreducible over the constant field.

    Computed by sympy factorisation — an INDEPENDENT code path from the residue test used for
    the assumption, so the two instruments agree by mathematics rather than by construction.
    """
    def probe(w: World) -> Tuple[Optional[bool], Optional[str]]:
        poly = (sp.Poly(x ** 2 - a, x) if w.q == 0
                else sp.Poly(x ** 2 - a, x, modulus=w.q))
        if poly.is_irreducible:
            return True, None
        root = next((r for r in range(w.q) if (r * r - a) % w.q == 0), None) if w.q else None
        return False, (f"x^2 - {a} factors in {w.name}"
                       + (f": {root}^2 = {a} mod {w.q}" if root is not None else ""))
    return probe


def nonsquare_technique(a: int) -> Technique:
    """THE SHARPER NEAR-ANALOGY (external review, round 6).

    Everything visible about the two worlds is held fixed — same domain kind F_q[t], odd
    characteristic, field of constants, PID, identical polynomial machinery — and the verdict
    turns on whether `a` is a quadratic residue in F_q. Varying `a` at FIXED q gives two
    instances with byte-identical world features and opposite verdicts, so a circuit is forced
    to run technique -> its own assumption -> a target-world test. Nothing about the worlds
    alone can supply the answer.
    """
    return Technique(f"nonsquare_{a}", W_Z,
                     (f"{a} is a nonsquare in the constant field",),
                     _p_quadratic_irreducible(a))


#: Fixed q = 7, varying a. 2 is a square mod 7 (3^2 = 2); 3 and 5 are not.
QR_BATTERY: Tuple[Tuple[Technique, World], ...] = tuple(
    (nonsquare_technique(a), W_F7) for a in (2, 3, 5))


# --------------------------------------------------------------------------------------------
# Open conclusions: the (BROKEN, UNKNOWN) state.

def _p_open_in_Z(name: str) -> Probe:
    """A conclusion that is settled in F_q[t] and OPEN over ℤ. The probe returns None — the
    circuit has no reality-bits here and must say so."""
    def probe(w: World) -> Tuple[Optional[bool], Optional[str]]:
        if w.q > 0:
            return True, None                      # settled on the function-field side
        return None, f"{name} is open over ℤ; no probe available"
    return probe


#: Both of these are OPEN over ℤ — that half is not in doubt and is all the UNKNOWN verdict
#: rests on. The function-field half is cited for context and is TIER-2 pending verification
#: against primary sources (per the upstream-attribution rule):
#:   - Artin's primitive-root conjecture for function fields: Bilharz (1937), Math. Ann.,
#:     conditional on the Riemann hypothesis for curves (later established by Weil).
#:   - Twin primes over F_q[T]: Sawin & Shusterman, Annals of Mathematics (2022).
OPEN_TECHNIQUES: Tuple[Technique, ...] = (
    Technique("artin_primitive_root", W_F5, ("finite constant field",),
              _p_open_in_Z("Artin's primitive-root conjecture")),
    Technique("twin_prime_counting", W_F5, ("finite constant field",),
              _p_open_in_Z("the twin-prime conjecture")),
)

#: A technique that DECLARES an assumption its source proof never touches. The declared set is
#: ("characteristic zero", "euclidean size function"); only the second is used. This is the
#: gaming route flagged in cycle 017 -- a circuit that authors its own assumption list can pad
#: it -- and `used_in_source_proof` is what makes the padding visible. The mechanical audit is
#: `prometheus_math.lean_oracle.traced_classes`.
PADDED_TECHNIQUE = Technique(
    "euclidean_division_padded", W_Z,
    ("characteristic zero", "euclidean size function"),
    _p_euclidean_division,
    used_in_source_proof=("euclidean size function",),
)


OPEN_BATTERY: Tuple[Tuple[Technique, World], ...] = tuple((t, W_Z) for t in OPEN_TECHNIQUES)


#: Convenience index used by the cycle-019 tests.
BY_NAME_CY19: Dict[str, Technique] = {t.name: t for t in TECHNIQUES}
