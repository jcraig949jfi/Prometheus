"""Cycle 010: the residue of the third round-3 relay — the three genuinely new items.

1. LEGALITY-gated paired transition (the pair gets STUCK; sharper than a value-changing guard)
2. Capacity theorem as a property: ANY finite palette has an exhausting context
3. CROSS-REALIZATION transfer: same higher-level operator, different internal primitives —
   the test that kills macro caching in a way symbolic held-out does not.
"""
from __future__ import annotations

import pathlib
import sys

import sympy as sp
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from techne.ladder_circuits.r5_relational import LegalityGatedPair  # noqa: E402
from techne.ladder_circuits.skolem_fresh import (  # noqa: E402
    counter_allocator, eliminate, exhausting_context_for, palette_allocator,
)
from techne.ladder_circuits.operator_plasticity import (  # noqa: E402
    AbstractOperator, CachedMacro, Domain,
)


# ---- 1. legality-gated pairs ---------------------------------------------------------------

def test_paired_execution_is_legal_while_the_relation_holds():
    p = LegalityGatedPair(w0=(0, 5), w1=(0, 5)).step(4)
    assert p.stuck_at is None and p.w0 == (4, 5) and p.w1 == (4, 5)


def test_perturbing_ONE_world_makes_the_joint_step_ILLEGAL_not_merely_different():
    """The stronger form: after b changes in one world only, the synchronized transition is
    inadmissible and the pair is STUCK. There is no 'second run' to diff — the joint
    execution is blocked, which independent runs cannot even represent."""
    p = LegalityGatedPair(w0=(0, 5), w1=(0, 5)).step(6, perturb_at=2)
    assert p.stuck_at == 2
    assert p.w0[0] == p.w1[0] == 2          # frozen at the step the relation broke
    assert not p.legal()


@given(st.integers(min_value=0, max_value=8), st.integers(min_value=1, max_value=4))
@settings(max_examples=25, deadline=None)
def test_stuck_step_is_exactly_the_perturbation_step(k, delta):
    p = LegalityGatedPair(w0=(0, 0), w1=(0, 0)).step(12, perturb_at=k, delta=delta)
    assert p.stuck_at == k


# ---- 2. the capacity theorem, as a property ------------------------------------------------

@given(st.lists(st.text(alphabet="abcdefg", min_size=1, max_size=3),
                min_size=1, max_size=8, unique=True))
@settings(max_examples=40, deadline=None)
def test_ANY_finite_palette_has_an_exhausting_context(palette):
    """|fresh namespace| < infinity => there EXISTS a Gamma exhausting it. Constructive:
    the context naming every palette symbol. The unbounded allocator is unaffected."""
    ctx = exhausting_context_for(palette)
    assert eliminate(ctx, palette_allocator(list(palette))) is None    # exhausted
    out = eliminate(ctx, counter_allocator())
    assert out is not None and out[0] not in ctx.symbols               # namespace survives


# ---- 3. cross-realization transfer ----------------------------------------------------------

INTS = Domain("ints", double=lambda x: 2 * x, succ=lambda x: x + 1)
#: same higher-level operator, genuinely different internal realization
POLY = Domain("poly", double=lambda p: sp.expand(2 * p), succ=lambda p: sp.expand(p + 1))
MOD7 = Domain("mod7", double=lambda x: (2 * x) % 7, succ=lambda x: (x + 1) % 7)


def test_cached_macro_is_perfect_on_its_training_domain():
    cache = CachedMacro()
    cache.learn(INTS)
    assert cache.apply(INTS, 5) == 11


def test_KILL_cached_macro_carries_the_REALIZATION_abstraction_carries_the_OPERATOR():
    """Train on ints; evaluate on mod-7 arithmetic, where the same operator has different
    internal code. The cache silently returns the INT answer (wrong for the domain); the
    schema-based operator instantiates against mod7 and is right."""
    cache, absop = CachedMacro(), AbstractOperator()
    cache.learn(INTS)
    absop.learn(("double", "succ"))

    assert absop.apply(MOD7, 5) == (2 * 5 + 1) % 7 == 4
    assert cache.apply(MOD7, 5) == 11            # the training domain's answer, silently wrong
    assert cache.apply(MOD7, 5) != absop.apply(MOD7, 5)


def test_abstraction_transfers_to_a_symbolic_domain_it_never_saw():
    """Third carrier, never used in training: polynomials. Same operator, third realization."""
    z = sp.Symbol("z")
    absop = AbstractOperator()
    absop.learn(("double", "succ"))
    assert absop.apply(POLY, z**2 + 3) == 2 * z**2 + 7


def test_schema_order_matters_the_operator_is_not_a_bag_of_primitives():
    """succ-then-double is a DIFFERENT operator; the schema records order, so a system that
    merely knows 'these two primitives are useful' cannot pass."""
    a, b = AbstractOperator(), AbstractOperator()
    a.learn(("double", "succ"))
    b.learn(("succ", "double"))
    assert a.apply(INTS, 5) == 11 and b.apply(INTS, 5) == 12
