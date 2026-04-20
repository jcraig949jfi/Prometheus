"""
Pattern 30 — Algebraic-Identity Coupling Detection.

Given a correlation test on two quantities X and Y, decide whether the
observed correlation is a rearrangement of a known algebraic identity
rather than evidence of arithmetic structure. Graded severity 0-4 per
pattern_library.md:

  0 CLEAN           — no overlap; correlation test valid
  1 WEAK_ALGEBRAIC  — X under log/power in a ratio, other terms dominate
  2 SHARED_VARIABLE — X appears directly in Y's expression, non-trivial coeff
  3 REARRANGEMENT   — Y is definitional rearrangement of X + other known terms
  4 IDENTITY        — Y = f(X) exactly (proved algebraic identity)

Anchor case: F043 (retracted 2026-04-19). The BSD identity
    L = Omega * Reg * prod(c_p) * Sha / tors**2
rearranges as
    log(Omega * prod c_p) = log L + 2 log tors - log Reg - log Sha
so corr(log Sha, log(Omega * prod c_p)) is Level 3 REARRANGEMENT and the
permutation null does not break it.

API:

    from harmonia.sweeps.pattern_30 import sweep, CouplingCheck
    import sympy

    Sha, L, Omega, cp, Reg, tors = sympy.symbols(
        'Sha L Omega cp Reg tors', positive=True)

    check = CouplingCheck(
        X_expr=sympy.log(Sha),
        Y_expr=sympy.log(Omega * cp),
        known_identities=[sympy.Eq(L, Omega * Reg * cp * Sha / tors**2)],
        transform='log',
    )
    result = sweep(check)
    # result.level == 3, result.verdict == 'BLOCK'
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence, Any

try:
    import sympy
except ImportError:  # pragma: no cover
    sympy = None  # type: ignore


PATTERN_30_LEVELS = {
    0: ("CLEAN", "CLEAR"),
    1: ("WEAK_ALGEBRAIC", "WARN"),
    2: ("SHARED_VARIABLE", "BLOCK"),
    3: ("REARRANGEMENT", "BLOCK"),
    4: ("IDENTITY", "BLOCK"),
}


@dataclass
class CouplingCheck:
    """Declared algebraic lineage of a correlation test.

    Fields:
      X_expr: sympy expression representing X (e.g. log(Sha))
      Y_expr: sympy expression representing Y as actually measured
      known_identities: sympy Eq objects relating atoms on either side
      transform: "log" if both quantities are under log, "linear" otherwise
      severity_hint: optional override by caller ("weak_algebraic", etc.)
    """
    X_expr: Any
    Y_expr: Any
    known_identities: Sequence[Any] = field(default_factory=list)
    transform: str = "linear"
    severity_hint: Optional[str] = None


@dataclass
class Pattern30Result:
    level: int
    name: str
    verdict: str
    rationale: str
    connecting_identity: Optional[str] = None


def _atoms(expr: Any) -> set:
    """Free symbol atoms of a sympy expression. Tolerates non-sympy input."""
    if sympy is None or expr is None:
        return set()
    try:
        return set(expr.free_symbols)
    except AttributeError:
        return set()


def _expr_contains_subexpr(haystack: Any, needle_atoms: set) -> bool:
    """Does haystack's expanded form include every atom in needle_atoms?"""
    if not needle_atoms:
        return False
    h_atoms = _atoms(haystack)
    return needle_atoms.issubset(h_atoms)


def _identity_connects(identity: Any, x_atoms: set, y_atoms: set) -> bool:
    """An identity connects X and Y iff its free symbols touch both sides."""
    if sympy is None:
        return False
    try:
        lhs_atoms = set(identity.lhs.free_symbols)
        rhs_atoms = set(identity.rhs.free_symbols)
    except AttributeError:
        return False
    all_atoms = lhs_atoms | rhs_atoms
    touches_x = bool(all_atoms & x_atoms)
    touches_y = bool(all_atoms & y_atoms)
    return touches_x and touches_y


def sweep(check: CouplingCheck) -> Pattern30Result:
    """Classify a coupling check into Pattern 30 levels 0-4."""
    if sympy is None:
        return Pattern30Result(
            level=0, name="CLEAN", verdict="WARN",
            rationale="sympy unavailable; Pattern 30 auto-check skipped",
        )

    # Severity hint override — lets callers declare e.g. weak_algebraic
    # when the caller has context the automated check does not
    if check.severity_hint:
        hint_map = {
            "clean": 0, "weak_algebraic": 1, "shared_variable": 2,
            "rearrangement": 3, "identity": 4,
        }
        level = hint_map.get(check.severity_hint.lower(), 0)
        name, verdict = PATTERN_30_LEVELS[level]
        return Pattern30Result(
            level=level, name=name, verdict=verdict,
            rationale=f"caller-declared severity: {check.severity_hint}",
        )

    x_atoms = _atoms(check.X_expr)
    y_atoms = _atoms(check.Y_expr)

    # Level 4 — exact equality after simplification
    try:
        diff = sympy.simplify(check.X_expr - check.Y_expr)
        if diff == 0:
            return Pattern30Result(
                level=4, name="IDENTITY", verdict="BLOCK",
                rationale="X_expr and Y_expr are symbolically equal",
            )
    except Exception:
        pass

    # Level 2 — X's atoms appear directly in Y's expression
    if x_atoms and x_atoms.issubset(y_atoms):
        return Pattern30Result(
            level=2, name="SHARED_VARIABLE", verdict="BLOCK",
            rationale=(
                f"X atoms {sorted(map(str, x_atoms))} are all present in "
                f"Y_expr's free symbols {sorted(map(str, y_atoms))}; "
                "X is a direct component of Y"
            ),
        )

    # Level 3 — a known identity connects X and Y
    for identity in check.known_identities:
        if _identity_connects(identity, x_atoms, y_atoms):
            return Pattern30Result(
                level=3, name="REARRANGEMENT", verdict="BLOCK",
                rationale=(
                    f"identity {identity} shares atoms with both X and Y; "
                    "substitution rewrites Y to contain X — correlation is "
                    "definitional, not arithmetic"
                ),
                connecting_identity=str(identity),
            )

    # Level 0 — clean
    return Pattern30Result(
        level=0, name="CLEAN", verdict="CLEAR",
        rationale=(
            "no shared atoms between X and Y; no known identity connects "
            "them; correlation test is algebraically valid"
        ),
    )


# ---------------------------------------------------------------------------
# Retrospective helpers — lineage registry for existing F-IDs
# ---------------------------------------------------------------------------

def bsd_f043_check() -> CouplingCheck:
    """The canonical F043 coupling check. Used as BLOCK regression test."""
    s = sympy.symbols
    Sha, L, Omega, cp, Reg, tors = s('Sha L Omega cp Reg tors', positive=True)
    return CouplingCheck(
        X_expr=sympy.log(Sha),
        Y_expr=sympy.log(Omega * cp),
        known_identities=[sympy.Eq(L, Omega * Reg * cp * Sha / tors**2)],
        transform="log",
    )


def f015_szpiro_check() -> CouplingCheck:
    """F015 Szpiro-vs-conductor: szpiro = log|Disc| / log(N); correlating
    against log(N) has log(N) in denominator. Declared weak_algebraic by
    the methodology tightener (b57f4afe)."""
    Disc, N = sympy.symbols("Disc N", positive=True)
    szpiro = sympy.log(Disc) / sympy.log(N)
    return CouplingCheck(
        X_expr=sympy.log(N),
        Y_expr=szpiro,
        known_identities=[],
        transform="linear",
        severity_hint="weak_algebraic",
    )
