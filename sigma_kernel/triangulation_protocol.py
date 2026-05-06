"""sigma_kernel.triangulation_protocol — P6 Tier 2 primitive for substrate v2.3 §6.3.

When a verdict is INCONCLUSIVE, the substrate auto-spawns ≥3 verification
paths from a registered set and decides whether the collected paths
triangulate the verdict — i.e. whether the resolution is strong enough to
upgrade INCONCLUSIVE → LOCAL_LEMMA.

Convergent corrections from ChatGPT + Gemini reviews of v2.1 (folded
into v2.3) shaped the core rules:

1. **Method-class diversity, not just numerical replication.** Three
   numerical paths agreeing is precision replication, NOT triangulation.
   Each verification path carries a ``MethodClass`` (proof_bearing,
   numerical, catalog, robustness, exploratory) and the upgrade rule
   requires at least one *proof-bearing* path to certify.
2. **Clustering nominates boundary structure but cannot certify truth.**
   Exploratory paths (clustering, boundary-layer analysis) are useful for
   *finding* candidates, but they have no certifying weight — three
   exploratory paths agreeing is correlated noise.
3. **Independence enforcement is dual-keyed.** The ≥1 independent replay
   path must (a) carry a *different* :class:`IndependenceClass` than the
   primary proof-bearing path AND (b) pass
   :meth:`MethodSpec.is_independent_of` — both checks together. The latter
   catches behavioural-hash collisions (Aporia Study 15: same algorithm
   wearing two coats of paint).

ExclusionCertificate (P4) is a separate primitive; this module produces a
:class:`TriangulationResult` and the certificate emission is the
caller's job. We use string-typed ``certificate_ref`` placeholders rather
than reaching across primitive boundaries.

Stdlib-only by design (substrate v2.3 §6.3 P6 forbids new dependencies
for Tier 2 primitives).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Sequence, Tuple

from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# MethodClass — the epistemic role of a verification path
# ---------------------------------------------------------------------------


class MethodClass(str, enum.Enum):
    """Per substrate v2.3 §6.3 P6 — method classes registered with epistemic role.

    The five classes carry different certifying weight:

    * ``PROOF_BEARING`` — symbolic derivation, exhaustive enumeration,
      theorem-backed reduction. The only class that can independently
      *certify* a verdict.
    * ``NUMERICAL`` — high-precision floating, interval arithmetic,
      arbitrary-precision replay. Strong evidence; cannot certify alone
      but is a valid independent replay path when paired with a
      proof-bearing primary.
    * ``CATALOG`` — lookup against an authoritative external catalog
      (LMFDB, OEIS, Mossinghoff, literature cross-check). Independent
      replay strength.
    * ``ROBUSTNESS`` — perturbation, bootstrap, representation
      invariance. Confirms stability; valid independent replay class.
    * ``EXPLORATORY`` — clustering, boundary-layer analysis. Nominates
      candidates but **cannot certify truth** (v2.3 §6.3 hard rule).
    """

    PROOF_BEARING = "proof_bearing"
    NUMERICAL = "numerical"
    CATALOG = "catalog"
    ROBUSTNESS = "robustness"
    EXPLORATORY = "exploratory"


# Map IndependenceClass values → MethodClass per substrate v2.3 §6.3.
#
# Note on coverage: this dict's keys cover all 13 :class:`IndependenceClass`
# enum values minus ``UNKNOWN``. ``UNKNOWN`` deliberately has no entry so
# that :func:`method_class_for_independence_class` falls through to the
# conservative ``EXPLORATORY`` default — a path with an unclassified
# independence class cannot be silently upgraded to certifying weight.
INDEPENDENCE_TO_METHOD_CLASS = {
    "sympy_symbolic_factorization": MethodClass.PROOF_BEARING,
    "mahler_lookup_catalog": MethodClass.CATALOG,
    "lmfdb_catalog": MethodClass.CATALOG,
    "oeis_catalog": MethodClass.CATALOG,
    "literature_cross_check": MethodClass.CATALOG,
    "mpmath_polynomial_factorization": MethodClass.NUMERICAL,
    "mpmath_numerical_root_finding": MethodClass.NUMERICAL,
    "pari_number_field": MethodClass.NUMERICAL,
    "sage_elliptic_curve": MethodClass.NUMERICAL,
    "numpy_linear_algebra": MethodClass.NUMERICAL,
    "perturbation_robustness": MethodClass.ROBUSTNESS,
    "clustering_boundary": MethodClass.EXPLORATORY,
}


def method_class_for_independence_class(ic: str) -> MethodClass:
    """Look up the :class:`MethodClass` for a given independence-class string.

    Parameters
    ----------
    ic:
        The :class:`IndependenceClass` value — accepts either an enum
        instance or the bare string (since :class:`IndependenceClass` is
        a str-mixin, enum instances compare equal to their string value).

    Returns
    -------
    MethodClass
        The registered method class. Falls back to
        :attr:`MethodClass.EXPLORATORY` for any independence class not in
        the registry — this is deliberate: an unknown method cannot be
        silently upgraded to certifying weight (substrate v2.3 §6.3 hard
        rule). Callers that need a certifying classification must
        register the independence class explicitly.
    """
    # Accept either IndependenceClass enum or raw string; the str-mixin
    # makes both compare equal.
    key = str(ic) if not isinstance(ic, str) else ic
    # IndependenceClass(str, Enum) members render as the enum form
    # ("IndependenceClass.UNKNOWN") under str(); fall back to .value.
    if isinstance(ic, IndependenceClass):
        key = ic.value
    return INDEPENDENCE_TO_METHOD_CLASS.get(key, MethodClass.EXPLORATORY)


# ---------------------------------------------------------------------------
# TriangulationVerdict — the outcome of evaluate()
# ---------------------------------------------------------------------------


class TriangulationVerdict(str, enum.Enum):
    """Outcome of running :meth:`TriangulationProtocol.evaluate`.

    * ``INCONCLUSIVE_WAITING`` — fewer than three paths registered yet.
      Not enough evidence to decide; protocol is waiting for more paths.
    * ``INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE`` — paths exist and a
      proof-bearing path verified, but no independent replay path with a
      different :class:`IndependenceClass` succeeded. Precision
      replication, not triangulation.
    * ``UPGRADED_TO_LOCAL_LEMMA`` — all upgrade conditions satisfied.
      Caller may now emit an :class:`ExclusionCertificate` (P4) with
      ``strength = COMPLETE``.
    * ``CONTRADICTED`` — at least one registered path contradicts.
      This is a substrate finding to log, not noise to discard.
    * ``REJECTED`` — no proof-bearing path verified. Clustering and
      exploratory paths cannot certify on their own (v2.3 §6.3 hard
      rule), so the verdict cannot be upgraded.
    """

    INCONCLUSIVE_WAITING = "inconclusive_waiting"
    INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE = "inconclusive_insufficient_independence"
    UPGRADED_TO_LOCAL_LEMMA = "upgraded_to_local_lemma"
    CONTRADICTED = "contradicted"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# TriangulationPath — one verification path
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TriangulationPath:
    """One verification path attempting to resolve an INCONCLUSIVE verdict.

    The protocol does NOT run the verification itself; callers prepare a
    ``TriangulationPath`` from an already-evaluated method run and pass
    it to :meth:`TriangulationProtocol.evaluate`. The protocol's only
    job is to decide whether the *collected* paths triangulate.

    Attributes
    ----------
    path_id:
        Caller-chosen identifier (used in summaries and provenance).
    method_spec:
        :class:`MethodSpec` describing the engine, strategy, precision,
        and registered :class:`IndependenceClass` of the path. The
        ``independence_class`` is what determines :attr:`method_class`
        and is what the upgrade rule's independence check fires on.
    method_class:
        :class:`MethodClass` derived from the method_spec's
        ``independence_class``. Stored explicitly (rather than always
        recomputed) so callers can override the auto-derivation in
        cases where the registry is incomplete.
    verdict:
        One of ``"verified"``, ``"contradicted"``, ``"inconclusive"``.
    runtime_ms:
        Wall-clock runtime of the path, milliseconds.
    rationale:
        Human-readable summary of why the path produced its verdict.
    timestamp:
        Unix epoch seconds of when the path completed.
    """

    path_id: str
    method_spec: MethodSpec
    method_class: MethodClass
    verdict: str  # "verified" | "contradicted" | "inconclusive"
    runtime_ms: int
    rationale: str
    timestamp: float

    @property
    def is_proof_bearing(self) -> bool:
        """True iff this path's :class:`MethodClass` is ``PROOF_BEARING``."""
        return self.method_class == MethodClass.PROOF_BEARING

    @property
    def can_certify(self) -> bool:
        """True iff this path's class is allowed to certify under v2.3 §6.3.

        Exploratory paths (clustering, boundary-layer analysis) explicitly
        CANNOT certify per the substrate's hard rule. Every other class
        is allowed to participate in certification (though only
        proof-bearing paths can certify *primarily*).
        """
        return self.method_class != MethodClass.EXPLORATORY


# ---------------------------------------------------------------------------
# TriangulationResult — the protocol's verdict
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TriangulationResult:
    """Verdict from running :meth:`TriangulationProtocol.evaluate`.

    Frozen / immutable so result objects can be hashed, compared, and
    stored in append-only ledger rows without defensive copying.

    Attributes
    ----------
    verdict:
        One of the :class:`TriangulationVerdict` enum members.
    paths_run:
        Tuple of every :class:`TriangulationPath` that was considered.
    independence_classes_covered:
        ``frozenset`` of :class:`IndependenceClass` values seen across
        ``paths_run``. Useful for downstream :class:`ExclusionCertificate`
        ``verifier_set.independence_classes`` population.
    method_classes_covered:
        ``frozenset`` of :class:`MethodClass` values seen across
        ``paths_run``.
    summary:
        Human-readable one-line summary of the outcome.
    upgrade_eligible:
        True iff ``verdict == UPGRADED_TO_LOCAL_LEMMA``. Convenience
        flag for the common gating predicate.
    """

    verdict: TriangulationVerdict
    paths_run: Tuple[TriangulationPath, ...]
    independence_classes_covered: frozenset
    method_classes_covered: frozenset
    summary: str
    upgrade_eligible: bool


# ---------------------------------------------------------------------------
# TriangulationProtocol — the upgrade engine
# ---------------------------------------------------------------------------


class TriangulationProtocol:
    """Per substrate v2.3 §6.3 P6 — auto-decide whether collected paths
    triangulate an INCONCLUSIVE verdict.

    The protocol is stateless. Construction takes no arguments;
    :meth:`evaluate` consumes a ``Sequence[TriangulationPath]`` and
    returns a :class:`TriangulationResult`. Callers manage path-spawn
    scheduling separately.

    Upgrade rule
    ------------
    INCONCLUSIVE → LOCAL_LEMMA only if:

    * ≥3 paths registered (otherwise ``INCONCLUSIVE_WAITING``).
    * No registered path with ``verdict == "contradicted"`` (otherwise
      ``CONTRADICTED`` — substrate finding logged).
    * ≥1 path with ``method_class == PROOF_BEARING`` and
      ``verdict == "verified"`` (otherwise ``REJECTED`` — clustering /
      exploratory cannot certify alone).
    * ≥1 verified path with a *different* ``independence_class`` than the
      primary proof-bearing path **and** that passes
      :meth:`MethodSpec.is_independent_of` (otherwise
      ``INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE``).
    * (Caller's job, not P6's: assumptions are explicitly bounded
      and an :class:`ExclusionCertificate` is emitted.)
    """

    # --- helpers ---------------------------------------------------------

    @staticmethod
    def _coverage(paths: Sequence[TriangulationPath]) -> Tuple[frozenset, frozenset]:
        """Return ``(independence_classes_covered, method_classes_covered)``."""
        ics = frozenset(p.method_spec.independence_class for p in paths)
        mcs = frozenset(p.method_class for p in paths)
        return ics, mcs

    # --- public API ------------------------------------------------------

    def evaluate(self, paths: Sequence[TriangulationPath]) -> TriangulationResult:
        """Decide whether ``paths`` triangulate an INCONCLUSIVE verdict.

        Returns the appropriate :class:`TriangulationResult` per the
        upgrade rule documented on the class.
        """
        paths_tuple = tuple(paths)
        ics, mcs = self._coverage(paths_tuple)

        # Rule 1: not enough paths yet.
        if len(paths_tuple) < 3:
            return TriangulationResult(
                verdict=TriangulationVerdict.INCONCLUSIVE_WAITING,
                paths_run=paths_tuple,
                independence_classes_covered=ics,
                method_classes_covered=mcs,
                summary=(
                    f"Only {len(paths_tuple)} path(s) registered; "
                    f"need ≥3 for triangulation"
                ),
                upgrade_eligible=False,
            )

        # Rule 2: any contradiction is a substrate finding.
        contradicted = [p for p in paths_tuple if p.verdict == "contradicted"]
        if contradicted:
            return TriangulationResult(
                verdict=TriangulationVerdict.CONTRADICTED,
                paths_run=paths_tuple,
                independence_classes_covered=ics,
                method_classes_covered=mcs,
                summary=(
                    f"{len(contradicted)} path(s) contradict; "
                    f"substrate finding logged"
                ),
                upgrade_eligible=False,
            )

        # Rule 3: must have ≥1 proof-bearing verified path. Clustering /
        # exploratory cannot certify on their own (v2.3 §6.3 hard rule).
        verified = [p for p in paths_tuple if p.verdict == "verified"]
        proof_bearing_verified = [p for p in verified if p.is_proof_bearing]

        if not proof_bearing_verified:
            return TriangulationResult(
                verdict=TriangulationVerdict.REJECTED,
                paths_run=paths_tuple,
                independence_classes_covered=ics,
                method_classes_covered=mcs,
                summary=(
                    "No proof-bearing path verified; "
                    "clustering/exploratory cannot certify"
                ),
                upgrade_eligible=False,
            )

        # Rule 4: need ≥1 independent replay path. Dual key: different
        # IndependenceClass AND passes is_independent_of() (catches
        # behavioural-hash collisions per Aporia Study 15).
        primary = proof_bearing_verified[0]
        primary_ic = primary.method_spec.independence_class
        independent_replays = [
            p
            for p in verified
            if p is not primary
            and p.method_spec.independence_class != primary_ic
            and p.method_spec.is_independent_of(primary.method_spec)
        ]

        if not independent_replays:
            return TriangulationResult(
                verdict=TriangulationVerdict.INCONCLUSIVE_INSUFFICIENT_INDEPENDENCE,
                paths_run=paths_tuple,
                independence_classes_covered=ics,
                method_classes_covered=mcs,
                summary=(
                    "Proof-bearing path verified, but no independent "
                    "replay path with different independence_class"
                ),
                upgrade_eligible=False,
            )

        # All conditions met → upgrade.
        return TriangulationResult(
            verdict=TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA,
            paths_run=paths_tuple,
            independence_classes_covered=ics,
            method_classes_covered=mcs,
            summary=(
                f"Upgraded: proof-bearing ({primary.path_id}) + "
                f"{len(independent_replays)} independent replay(s)"
            ),
            upgrade_eligible=True,
        )

    def can_upgrade(self, paths: Sequence[TriangulationPath]) -> bool:
        """Quick predicate: would :meth:`evaluate` return UPGRADED_TO_LOCAL_LEMMA?

        Used by :class:`ExclusionCertificate` to validate
        ``triangulation_history`` before allowing ``strength = COMPLETE``
        without paying for a full :class:`TriangulationResult`
        construction (the result object's allocation is cheap, but the
        intent is to make the gate predicate explicit at call sites).
        """
        return self.evaluate(paths).verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA


__all__ = [
    "MethodClass",
    "INDEPENDENCE_TO_METHOD_CLASS",
    "method_class_for_independence_class",
    "TriangulationVerdict",
    "TriangulationPath",
    "TriangulationResult",
    "TriangulationProtocol",
]
