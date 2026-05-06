"""sigma_kernel.method_spec — P3 Tier 1 primitive for substrate v2.3 §6.2.

Replaces the flat ``method: str`` field on KillComponent (and downstream
evidence dicts) with a structured ``MethodSpec`` that carries:

  * ``engine`` and ``strategy`` (parsed from legacy ``"<engine>_<strategy>"``
    strings via :py:meth:`MethodSpec.from_string`),
  * ``precision_dps``, ``version``, ``parameters``, ``fallback_chain`` for
    instrumentation,
  * ``independence_class`` — the registered class against which P6
    TriangulationProtocol checks independence (ChatGPT convergent critique:
    ``mpmath_factor_first`` and ``mpmath_direct`` are NOT independent if both
    depend on the same Mahler measure implementation),
  * ``drift_channel`` — Aporia Study 15: distinguishes intensional drift
    (cosmetic refactor, behaviour preserved) from behavioural drift
    (algorithm changed). Two methods with same behavioural_hash but
    different intensional_hash are *not* a triangulation independence pair.

Backwards compatibility
-----------------------
This module is purely additive. Existing callers using ``method: str``
continue to work; they can adopt MethodSpec incrementally via
``MethodSpec.from_string`` (read path) and ``.to_string()`` (write path,
when the legacy flat shape must be preserved).

Stdlib-only by design (substrate v2.3 §6.2 P3 explicitly forbids new
dependencies for Tier 1 primitives).
"""
from __future__ import annotations

import enum
import hashlib
import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, Union


# ---------------------------------------------------------------------------
# IndependenceClass
# ---------------------------------------------------------------------------


class IndependenceClass(str, enum.Enum):
    """Registered independence classes for triangulation purposes.

    Two MethodSpecs with the *same* IndependenceClass are NOT independent
    — they likely share an underlying implementation, library, or oracle,
    so co-agreement does not constitute independent triangulation.

    The set below is the substrate v2.3 canonical inventory. The vocabulary
    is open in spirit (callers may register new classes by extending this
    enum in a follow-on patch); ``UNKNOWN`` is the safe default whenever
    the caller has not yet classified the method.
    """

    MPMATH_POLYNOMIAL_FACTORIZATION = "mpmath_polynomial_factorization"
    MPMATH_NUMERICAL_ROOT_FINDING = "mpmath_numerical_root_finding"
    SYMPY_SYMBOLIC_FACTORIZATION = "sympy_symbolic_factorization"
    PARI_NUMBER_FIELD = "pari_number_field"
    SAGE_ELLIPTIC_CURVE = "sage_elliptic_curve"
    NUMPY_LINEAR_ALGEBRA = "numpy_linear_algebra"
    MAHLER_LOOKUP_CATALOG = "mahler_lookup_catalog"
    LMFDB_CATALOG = "lmfdb_catalog"
    OEIS_CATALOG = "oeis_catalog"
    LITERATURE_CROSS_CHECK = "literature_cross_check"
    PERTURBATION_ROBUSTNESS = "perturbation_robustness"
    # NOTE: clustering-boundary methods are explicitly NOT proof-bearing.
    # Listed so they have a stable independence_class identifier, but
    # callers should prefer a proof-bearing class for promotion gates.
    CLUSTERING_BOUNDARY = "clustering_boundary"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# DriftChannel — intensional vs behavioural (Aporia Study 15)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DriftChannel:
    """Two-channel drift fingerprint per Aporia Study 15.

    Attributes
    ----------
    intensional_hash:
        sha256 over the (whitespace-normalized) source code of the method.
        Changes whenever the source text changes — *including* cosmetic
        refactors that preserve behaviour.
    behavioural_hash:
        sha256 over the ``(test_input -> output)`` fingerprint set produced
        by running the method against a registered probe suite. Changes
        only when the algorithm's I/O behaviour changes.
    fingerprint_inputs:
        Tuple of test inputs used to produce ``behavioural_hash``. Stored
        so the fingerprint is reproducible across machines and so a
        downstream consumer can detect "different probe suites used →
        behavioural hashes are not directly comparable".

    Triangulation rule (substrate v2.3 §6.2 P3):
        Two methods with the *same* ``behavioural_hash`` but *different*
        ``intensional_hash`` are NOT a valid independence pair — they're
        the same algorithm wearing two coats of paint.
    """

    intensional_hash: str
    behavioural_hash: str
    fingerprint_inputs: tuple = ()


# ---------------------------------------------------------------------------
# MethodSpec
# ---------------------------------------------------------------------------


# Engines we recognize when parsing legacy ``<engine>_<strategy>`` strings.
# The list is intentionally conservative: an unrecognized engine falls
# through to ``engine=<full string>, strategy="direct"`` so we don't
# silently misparse novel legacy entries.
_KNOWN_ENGINES: frozenset = frozenset({
    "mpmath",
    "sage",
    "pari",
    "magma",
    "numpy",
    "sympy",
    "postgres",
    "custom",
    "lmfdb",
    "oeis",
    "catalog",
})

# Strategies we recognize as the second component. Anything else is kept
# verbatim as the strategy slug.
_KNOWN_STRATEGIES: frozenset = frozenset({
    "direct",
    "factor_first",
    "catalog_aware",
    "symbolic",
    "numeric",
    "lookup",
    "polyroots",
    "eigvals",
    "factor",
    "exact",
    "heuristic",
})


@dataclass(frozen=True)
class MethodSpec:
    """Structured replacement for the flat ``method`` string field.

    Substrate v2.3 §6.2 P3. This is a value object: it is hashable
    (frozen), JSON-friendly via ``dataclasses.asdict`` once mappings are
    converted, and stdlib-only.
    """

    engine: str
    strategy: str
    precision_dps: Optional[int] = None
    version: str = "1.0.0"
    parameters: Mapping[str, Any] = field(default_factory=dict)
    fallback_chain: Tuple["MethodSpec", ...] = ()
    independence_class: IndependenceClass = IndependenceClass.UNKNOWN
    drift_channel: Optional[DriftChannel] = None

    # ------------------------------------------------------------------
    # Legacy bridge
    # ------------------------------------------------------------------

    @classmethod
    def from_string(cls, s: str) -> "MethodSpec":
        """Parse a legacy ``method`` string like ``"mpmath_factor_first"``.

        Recognition rules:

        * Try splitting on the *first* ``"_"`` and check whether the prefix
          is a known engine. If yes, take the suffix as the strategy verbatim
          (this preserves multi-token strategies like ``"factor_first"``,
          ``"catalog_aware"``).
        * Otherwise, try splitting on the *last* ``"_"`` and check whether
          the suffix is a known strategy. If yes, use the prefix as engine.
        * Otherwise, treat the whole string as the engine and default the
          strategy to ``"direct"``. This is the safe fallback for novel
          legacy entries; callers can always override.

        The independence_class is left UNKNOWN by default — legacy strings
        carry no triangulation metadata, and silently inferring a class
        would be epistemically dishonest.
        """
        if not isinstance(s, str):
            raise TypeError(f"MethodSpec.from_string expects str, got {type(s).__name__}")
        if not s:
            raise ValueError("MethodSpec.from_string: empty string")

        # Normalize: strip whitespace, lowercase. Underscores preserved.
        norm = s.strip().lower()

        # Strategy 1: <known_engine>_<rest>
        if "_" in norm:
            head, _, tail = norm.partition("_")
            if head in _KNOWN_ENGINES and tail:
                return cls(engine=head, strategy=tail)

            # Strategy 2: <rest>_<known_strategy_suffix>
            # Try right-anchored matches against multi-token strategies first
            # so e.g. "magma_factor_first" → engine='magma', strategy='factor_first'
            # is preferred over engine='magma_factor', strategy='first'.
            for known in sorted(_KNOWN_STRATEGIES, key=len, reverse=True):
                suffix = "_" + known
                if norm.endswith(suffix):
                    prefix = norm[: -len(suffix)]
                    if prefix:
                        return cls(engine=prefix, strategy=known)

        # Fallback: whole string is the engine, strategy is "direct".
        return cls(engine=norm, strategy="direct")

    def to_string(self) -> str:
        """Render to the legacy ``"<engine>_<strategy>"`` flat shape.

        Used by consumers (and serializers) that have not yet migrated to
        consuming MethodSpec objects. Drops everything except the engine
        and strategy — that's a deliberate lossiness; callers that need
        the rest should consume the dataclass directly.
        """
        return f"{self.engine}_{self.strategy}"

    # ------------------------------------------------------------------
    # Triangulation independence
    # ------------------------------------------------------------------

    def is_independent_of(self, other: "MethodSpec") -> bool:
        """Return True iff *self* and *other* are independent for P6.

        Rule (substrate v2.3 §6.2 P3):

        1. If ``independence_class`` differs *and* neither side is
           ``UNKNOWN`` → independent.
        2. If ``independence_class`` matches *and* neither side is
           ``UNKNOWN`` → NOT independent.
        3. If either side is ``UNKNOWN``, fall back to behavioural_hash:
           * both have a ``drift_channel`` and the ``behavioural_hash``
             values differ → independent.
           * both have a ``drift_channel`` and the ``behavioural_hash``
             values match → NOT independent (same algorithm).
           * at least one is missing a ``drift_channel`` → NOT
             independent (we cannot prove it; absence-of-evidence is
             treated conservatively).

        The fallback also fires when both classes are UNKNOWN and the
        intensional_hash matches with same behavioural_hash — clearly the
        same code, so not independent.
        """
        if not isinstance(other, MethodSpec):
            raise TypeError(
                f"is_independent_of expects MethodSpec, got {type(other).__name__}"
            )

        cls_self = self.independence_class
        cls_other = other.independence_class

        # Path 1: both classes known → class-based decision is authoritative.
        if cls_self != IndependenceClass.UNKNOWN and cls_other != IndependenceClass.UNKNOWN:
            return cls_self != cls_other

        # Path 2: at least one UNKNOWN → fall back to behavioural fingerprint.
        if self.drift_channel is None or other.drift_channel is None:
            # Cannot prove independence → conservative: not independent.
            return False

        return self.drift_channel.behavioural_hash != other.drift_channel.behavioural_hash


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


# Matches Python comments (full-line and trailing). We strip them as part
# of "ignores whitespace/comments where reasonable" — purely cosmetic
# changes shouldn't perturb the intensional hash.
_COMMENT_RE = re.compile(r"#[^\n]*")
# Collapses runs of whitespace (including newlines) to a single space.
_WS_RE = re.compile(r"\s+")


def _normalize_source(src: str) -> str:
    """Whitespace-and-comment normalization for intensional hashing.

    * Strips ``#``-comments (full-line and trailing).
    * Collapses any whitespace run to a single space.
    * Strips leading/trailing whitespace.

    This is intentionally conservative: it will *not* normalize semantic
    differences (e.g. variable renames, expression reorderings). It only
    absorbs the cosmetic noise that BIND/EVAL hash-drift was overreacting
    to (see Aporia Study 15).
    """
    no_comments = _COMMENT_RE.sub("", src)
    collapsed = _WS_RE.sub(" ", no_comments)
    return collapsed.strip()


def compute_intensional_hash(callable_or_source: Union[Callable, str]) -> str:
    """sha256 hex digest over the normalized source of a callable or string.

    Accepts either a callable (in which case ``inspect.getsource`` is used
    to recover the source) or a raw source string. The hash is whitespace-
    and comment-insensitive — see :py:func:`_normalize_source`.

    Raises
    ------
    TypeError
        If ``callable_or_source`` is neither callable nor a string.
    OSError
        If ``inspect.getsource`` cannot recover source for the callable
        (e.g. a built-in or a lambda defined in an interactive REPL).
    """
    if isinstance(callable_or_source, str):
        src = callable_or_source
    elif callable(callable_or_source):
        src = inspect.getsource(callable_or_source)
    else:
        raise TypeError(
            "compute_intensional_hash expects callable or str, "
            f"got {type(callable_or_source).__name__}"
        )

    normalized = _normalize_source(src)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_behavioural_hash(
    callable: Callable,
    test_inputs: Sequence[Any],
) -> Tuple[str, tuple]:
    """sha256 hex digest over ``(input, output)`` pairs from a probe suite.

    Runs ``callable`` against each entry in ``test_inputs`` and hashes the
    canonical repr of the resulting pairs. Returns ``(hash, inputs_used)``
    so the caller can store the probe suite alongside the hash for later
    reproduction (see :py:class:`DriftChannel.fingerprint_inputs`).

    Determinism caveats
    -------------------
    The hash is only stable for *deterministic, side-effect-free* callables
    fed the same inputs in the same order. Callers that wish to fingerprint
    a stochastic method must pin its seed at the caller level — this helper
    deliberately does not try to inject randomness control because the right
    seeding API is method-specific.

    If ``callable`` raises on a particular input, the exception's class
    name is recorded in lieu of an output value so that "raises X" remains
    a stable, hashable behavioural signal.
    """
    if not callable_is_callable(callable):
        raise TypeError(
            f"compute_behavioural_hash expects a callable, got {type(callable).__name__}"
        )

    inputs_tuple = tuple(test_inputs)
    pairs = []
    for inp in inputs_tuple:
        try:
            out = callable(inp)
            pairs.append((repr(inp), repr(out)))
        except Exception as exc:  # noqa: BLE001 — fingerprint exception class
            pairs.append((repr(inp), f"<raised:{type(exc).__name__}>"))

    fingerprint_blob = repr(pairs).encode("utf-8")
    return hashlib.sha256(fingerprint_blob).hexdigest(), inputs_tuple


def callable_is_callable(obj: Any) -> bool:
    """Tiny helper so the parameter name ``callable`` in
    :py:func:`compute_behavioural_hash` doesn't shadow the builtin where
    we need it."""
    return hasattr(obj, "__call__")


__all__ = [
    "IndependenceClass",
    "DriftChannel",
    "MethodSpec",
    "compute_intensional_hash",
    "compute_behavioural_hash",
]
