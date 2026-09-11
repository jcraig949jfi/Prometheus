"""TECHNE-12: a Hypothesis strategy over the Boolean PROGRAM space at proteus.boolean3.v0.

HYPOTHESIS IS IMPORTED LAZILY, inside the functions. Importing this module costs nothing and
requires nothing, so Proteus keeps its stdlib-only property and a machine without Hypothesis can
still run every Proteus test. Only a caller that actually asks for a strategy needs the package.

WHAT IS GENERATED. Well-typed expressions of the declared grammar -- `input`, constants 0/1,
NOT, AND, OR, XOR -- and nothing else. Every generated program is checked by Proteus's own
`check` and must COMPILE, so a value that reaches a test is a real member of the program space
rather than a shape that merely looks like one.

THE COMPILE FILTER IS NOT COSMETIC. Register pressure depends on tree SHAPE: codegen emits the
left child at t and the right at t+1, so a right-leaning chain exhausts the 11 declared
temporaries while a left-leaning chain of the same node count compiles. Generation cannot know
that in advance, so the strategy filters on `compiles`. A filtered-out value is not a defect.
"""
from __future__ import annotations

from proteus.eval import boolean as B
from proteus.eval.shrink import compiles

INTERFACE_VERSION = B.INTERFACE_VERSION
STRATEGY_CONTRACT = "proteus.program_strategy.v1"


def _require():
    try:
        import hypothesis.strategies as st           # noqa: F401
        return st
    except ImportError as e:                          # pragma: no cover
        raise ImportError(
            "hypothesis is not installed. proteus.eval.shrink -- the size order and the "
            "validity predicates -- is stdlib-only and works without it; only this strategy "
            "needs the package."
        ) from e


def leaves(n_inputs=B.N_INPUTS):
    """The size-1 programs. Constants first, then inputs, matching enumerate_programs."""
    return [B.C(0), B.C(1)] + [B.I(i) for i in range(n_inputs)]


def programs(max_leaves=8, n_inputs=B.N_INPUTS):
    """A strategy over compilable well-typed programs.

    `max_leaves` bounds Hypothesis's recursion, not Proteus's node count; the two are related but
    not equal, so the declared size order is applied by `size_key`, never inferred from this.
    """
    st = _require()
    base = st.sampled_from(leaves(n_inputs))

    def extend(children):
        pair = st.tuples(children, children)
        return st.one_of(
            children.map(B.Not),
            pair.map(lambda p: B.And(p[0], p[1])),
            pair.map(lambda p: B.Or(p[0], p[1])),
            pair.map(lambda p: B.Xor(p[0], p[1])),
        )

    return st.recursive(base, extend, max_leaves=max_leaves).filter(compiles)


def counterexample_programs(target, max_leaves=8, n_inputs=B.N_INPUTS):
    """Programs that DISAGREE with `target` -- the asked-for shrink domain.

    Note the measured triviality recorded in shrink.py: the minimum here is node count 1 for
    every 3-input target, so this domain is sound to shrink and cheap to enumerate.
    """
    from proteus.eval.shrink import still_a_counterexample
    return programs(max_leaves, n_inputs).filter(
        lambda e: still_a_counterexample(e, target))


def solving_programs(target, max_leaves=8, n_inputs=B.N_INPUTS):
    """Programs that SOLVE `target`. The non-trivial minimisation target.

    Hypothesis will find these rarely by blind generation; the honest use is to shrink a KNOWN
    solution, which is what the committed fixture supplies.
    """
    from proteus.eval.shrink import still_solves
    return programs(max_leaves, n_inputs).filter(lambda e: still_solves(e, target))
