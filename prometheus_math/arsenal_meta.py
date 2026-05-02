"""prometheus_math.arsenal_meta — runtime metadata for arsenal callables.

Tags arsenal operations with the metadata an RL learner needs to choose
between them: cost model, postconditions, authority references,
canonicalizer subclass. Every decorated callable is registered in a
process-wide ``ARSENAL_REGISTRY`` for downstream introspection.

Usage::

    from prometheus_math.arsenal_meta import arsenal_op

    @arsenal_op(
        cost={"max_seconds": 0.5, "max_memory_mb": 64, "max_oracle_calls": 0},
        postconditions=["output >= 1.0 for non-zero integer poly"],
        authority_refs=["Mossinghoff Mahler tables", "Lehmer 1933"],
        equivalence_class="variety_fingerprint",
        category="numerics",
    )
    def mahler_measure(coeffs):
        ...

The decorator is a no-op at runtime (returns ``fn`` unchanged) but
populates ``ARSENAL_REGISTRY[fn.__module__ + ":" + fn.__qualname__]`` with
the metadata block. Test/CI tools can iterate the registry to verify
coverage; the BIND opcode in sigma_kernel.bind_eval can read directly
from it instead of asking the caller to re-supply cost models.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class ArsenalMeta:
    """Machine-readable metadata block attached to an arsenal callable."""

    callable_ref: str  # "module.path:qualname"
    cost: Dict[str, float] = field(default_factory=dict)
    postconditions: List[str] = field(default_factory=list)
    authority_refs: List[str] = field(default_factory=list)
    equivalence_class: Optional[str] = None  # canonicalizer subclass
    category: Optional[str] = None  # number_theory / topology / numerics / ...
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "callable_ref": self.callable_ref,
            "cost": dict(self.cost),
            "postconditions": list(self.postconditions),
            "authority_refs": list(self.authority_refs),
            "equivalence_class": self.equivalence_class,
            "category": self.category,
            "notes": self.notes,
        }


# Process-global registry. Keys are "module.path:qualname"; values are
# ArsenalMeta instances. Plain dict; concurrent-decoration is fine because
# decoration runs at import time and Python's import lock serializes that.
ARSENAL_REGISTRY: Dict[str, ArsenalMeta] = {}


def arsenal_op(
    cost: Optional[Dict[str, float]] = None,
    postconditions: Optional[List[str]] = None,
    authority_refs: Optional[List[str]] = None,
    equivalence_class: Optional[str] = None,
    category: Optional[str] = None,
    notes: str = "",
) -> Callable[[Callable], Callable]:
    """Decorator that registers a callable in ``ARSENAL_REGISTRY``.

    Returns the original callable unchanged. The decorator's only side
    effect is populating the registry. Idempotent: re-decorating the same
    callable overwrites the prior registry entry (the most recent
    decoration wins).
    """

    def _decorate(fn: Callable) -> Callable:
        ref = f"{fn.__module__}:{fn.__qualname__}"
        meta = ArsenalMeta(
            callable_ref=ref,
            cost=dict(cost or {}),
            postconditions=list(postconditions or []),
            authority_refs=list(authority_refs or []),
            equivalence_class=equivalence_class,
            category=category,
            notes=notes,
        )
        ARSENAL_REGISTRY[ref] = meta
        # Attach to the function itself for direct introspection
        # (`fn.__arsenal_meta__`).
        try:
            fn.__arsenal_meta__ = meta  # type: ignore[attr-defined]
        except (AttributeError, TypeError):
            # Some callables (e.g. C-implemented) reject attribute assignment.
            pass
        return fn

    return _decorate


def get_meta(callable_ref_or_fn: Any) -> Optional[ArsenalMeta]:
    """Look up metadata by ``"module:qualname"`` string or by the callable."""
    if isinstance(callable_ref_or_fn, str):
        return ARSENAL_REGISTRY.get(callable_ref_or_fn)
    if callable(callable_ref_or_fn):
        ref = f"{callable_ref_or_fn.__module__}:{callable_ref_or_fn.__qualname__}"
        return ARSENAL_REGISTRY.get(ref)
    return None


def registry_summary() -> Dict[str, Any]:
    """Aggregate stats for tooling."""
    by_cat: Dict[str, int] = {}
    by_eq: Dict[str, int] = {}
    n_with_cost = 0
    n_with_post = 0
    n_with_auth = 0
    for meta in ARSENAL_REGISTRY.values():
        cat = meta.category or "uncategorized"
        by_cat[cat] = by_cat.get(cat, 0) + 1
        eq = meta.equivalence_class or "untagged"
        by_eq[eq] = by_eq.get(eq, 0) + 1
        if meta.cost:
            n_with_cost += 1
        if meta.postconditions:
            n_with_post += 1
        if meta.authority_refs:
            n_with_auth += 1
    return {
        "total": len(ARSENAL_REGISTRY),
        "by_category": dict(sorted(by_cat.items())),
        "by_equivalence_class": dict(sorted(by_eq.items())),
        "with_cost_model": n_with_cost,
        "with_postconditions": n_with_post,
        "with_authority_refs": n_with_auth,
    }


def _bootstrap_registry() -> None:
    """Decorate a starter set of representative arsenal operations.

    Tagged via a side-call (rather than editing each module) so that the
    MVP demo can exercise the BIND/EVAL → registry → Gym env loop without
    waiting on the full enrichment pass.
    """
    try:
        from . import numerics_special_dilogarithm as _ns_dilog

        ARSENAL_REGISTRY[
            f"prometheus_math.numerics_special_dilogarithm:dilogarithm"
        ] = ArsenalMeta(
            callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
            cost={"max_seconds": 1.0, "max_memory_mb": 32, "max_oracle_calls": 0},
            postconditions=[
                "output is real-valued for z in (-inf, 1]",
                "Li_2(0) == 0",
                "Li_2(1) ≈ pi^2/6",
            ],
            authority_refs=[
                "Lewin 1981 (dilogarithm identities)",
                "Li_2(1)=zeta(2)=pi^2/6 (Basel)",
            ],
            equivalence_class="ideal_reduction",
            category="numerics_special",
            notes="Bootstrapped via arsenal_meta._bootstrap_registry; dilogarithm Li_2(z).",
        )
    except Exception:
        pass

    try:
        from . import numerics_special_theta as _ns_theta

        ARSENAL_REGISTRY[
            f"prometheus_math.numerics_special_theta:theta_null_value"
        ] = ArsenalMeta(
            callable_ref="prometheus_math.numerics_special_theta:theta_null_value",
            cost={"max_seconds": 0.5, "max_memory_mb": 32, "max_oracle_calls": 0},
            postconditions=[
                "theta_3(0,q)^4 == theta_2(0,q)^4 + theta_4(0,q)^4 (Jacobi)",
                "theta_2(0,0) == 0",
            ],
            authority_refs=["Whittaker & Watson §21.41"],
            equivalence_class="ideal_reduction",
            category="numerics_special",
            notes="Jacobi nullwert.",
        )
    except Exception:
        pass

    try:
        from techne.lib import mahler_measure as _mm

        ARSENAL_REGISTRY[
            f"techne.lib.mahler_measure:mahler_measure"
        ] = ArsenalMeta(
            callable_ref="techne.lib.mahler_measure:mahler_measure",
            cost={"max_seconds": 0.5, "max_memory_mb": 64, "max_oracle_calls": 0},
            postconditions=[
                "M(P) >= 1 for any non-zero integer polynomial",
                "M(cyclotomic) == 1",
                "M(Lehmer's polynomial) ≈ 1.17628081826",
            ],
            authority_refs=[
                "Mossinghoff Mahler tables",
                "Lehmer 1933",
            ],
            equivalence_class="variety_fingerprint",
            category="research_lehmer",
            notes="Mahler measure of an integer polynomial; central to Lehmer's conjecture.",
        )
    except Exception:
        pass

    try:
        from . import combinatorics_partitions as _cp

        ARSENAL_REGISTRY[
            f"prometheus_math.combinatorics_partitions:num_partitions"
        ] = ArsenalMeta(
            callable_ref="prometheus_math.combinatorics_partitions:num_partitions",
            cost={"max_seconds": 0.5, "max_memory_mb": 32, "max_oracle_calls": 0},
            postconditions=[
                "num_partitions(0) == 1",
                "num_partitions(n) > 0 for n >= 0",
                "p(100) == 190569292 (Hardy-Ramanujan)",
            ],
            authority_refs=["OEIS A000041", "Hardy & Ramanujan 1918"],
            equivalence_class="partition_refinement",
            category="combinatorics",
            notes="Integer partition counting via Euler pentagonal recurrence.",
        )
    except Exception:
        pass

    try:
        from . import numerics_special_q_pochhammer as _qp

        ARSENAL_REGISTRY[
            f"prometheus_math.numerics_special_q_pochhammer:euler_function"
        ] = ArsenalMeta(
            callable_ref="prometheus_math.numerics_special_q_pochhammer:euler_function",
            cost={"max_seconds": 1.0, "max_memory_mb": 32, "max_oracle_calls": 0},
            postconditions=[
                "euler_function(0) == 1",
                "|q| < 1 required",
            ],
            authority_refs=["Whittaker & Watson §22"],
            equivalence_class="ideal_reduction",
            category="numerics_special",
            notes="Euler function phi(q) = (q;q)_inf; cusp form Δ(τ) = (2π)^12 η^24 builds on this.",
        )
    except Exception:
        pass


# Eagerly bootstrap on import — keeps the MVP closed-loop runnable
# without an explicit setup step.
_bootstrap_registry()
