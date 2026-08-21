"""COMPOSITION — do individually-sound rungs stay sound when chained? (Cycle 024.)

Every rung R0–R12 was built and killed in isolation. A system that passes each one separately
has not been shown to pass them composed, and Prometheus's real failures have always been at
seams. This is the first composition probe: **R1 (local rule application) downstream of R2
(pipeline)**, chosen because cycle 023 *measured* R1's surplus at 0.951 excess bits rather than
guessing at it, so there is a specific quantity to ask about.

The chain solves `f(x) = 0` for a rational `f`:

    input  --together-->  single fraction  --numer-->  linear polynomial  --R1 rule-->  root

**The theory the instruments supply, and it is sharper than I expected.** A pipeline induces a
refinement chain automatically: if stage k+1 sees only stage k's output, its fibres are unions of
stage k's. The data-processing inequality then forces the two sweep quantities in OPPOSITE
directions along the chain:

    deficit = H(T | P_k)   non-DECREASING    information about the truth can only be lost
    excess  = H(P_k | T)   non-INCREASING    surplus distinctions can only be discarded

So composition can only lose, and the whole question is *what* it lost. Excess is the resource
a chain spends; deficit is the damage it cannot undo. **The first stage where deficit rises
above zero is the seam** — which makes seam-location a measurement rather than a hunt.

Three traps, all of which pass their stages individually:

- `LOCALLY_SOUND_CHAIN` — every stage is sound for its own local target and the chain still
  loses the end target. The stage-wise green suite says nothing.
- `SHORTCUT_CHAIN` — reaches the right answer by a route that ignores the intermediate stages.
  Caught by ablation, which is canon R9's deletion test lifted from lemmas to stages.
- `LAUNDERING_CHAIN` — a stage that passes the raw input through alongside its declared output,
  so a downstream stage measures as sufficient on borrowed bits. My first detector for this was
  wrong and the module records why: "discards nothing" also describes every lossless stage, so
  injectivity and laundering are indistinguishable to any information measure. The working
  detector is an INTERVENTION — corrupt everything but the declared output and see whether the
  answers move.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Sequence, Tuple

import sympy as sp

from prometheus_math.partition import (
    conditional_entropy, induced_partition, information_profile, is_refinement_chain,
    variation_of_information,
)
from techne.ladder_circuits.r1_local_op import R1LocalOpCircuit, linear_root_rule
from techne.ladder_circuits.r2_pipeline import REGISTRY

__all__ = ["Stage", "Chain", "ChainReport", "analyse_chain", "ablate",
           "stage_is_load_bearing", "is_injective_on", "reads_beyond_declared_output",
           "SOUND_CHAIN", "LOCALLY_SOUND_CHAIN", "SHORTCUT_CHAIN", "LAUNDERING_CHAIN",
           "PROBLEMS", "true_root"]

x = sp.Symbol("x")


@dataclass(frozen=True)
class Stage:
    """One link. `apply` maps the running value forward; None means the stage did not fire."""

    name: str
    apply: Callable[[Any], Optional[Any]]
    declares_reduction: bool = True     # does it CLAIM to discard something?


@dataclass(frozen=True)
class Chain:
    """A named pipeline of stages."""

    name: str
    stages: Tuple[Stage, ...]

    def run(self, value: Any) -> List[Any]:
        """States after each stage, starting with the input. A stage that does not fire leaves
        the value unchanged, so the trace length is always len(stages) + 1."""
        trace = [value]
        cur = value
        for st in self.stages:
            nxt = st.apply(cur)
            cur = cur if nxt is None else nxt
            trace.append(cur)
        return trace

    def answer(self, value: Any) -> Any:
        return self.run(value)[-1]


# --------------------------------------------------------------------------------------------
# The problems: rational equations whose roots the chain must find.

def _rational(a: int, b: int) -> sp.Expr:
    """a/(x+1) + b/(x-1) — a sum of fractions, so `together` has something to do."""
    return sp.Integer(a) / (x + 1) + sp.Integer(b) / (x - 1)


PROBLEMS: Tuple[sp.Expr, ...] = tuple(
    _rational(a, b) for a, b in ((3, 4), (1, 2), (2, 6), (5, 1), (1, 3), (4, 8)))


def true_root(e: sp.Expr) -> str:
    """Ground truth, computed independently of the chain."""
    sols = sp.solve(sp.Eq(e, 0), x)
    return str(sols[0]) if sols else "none"


# --------------------------------------------------------------------------------------------
# Stages

_R1 = R1LocalOpCircuit()
_R1.give_rule(linear_root_rule())


def _stage_from_registry(name: str, declares: bool = True) -> Stage:
    rule = REGISTRY[name]()
    return Stage(name, rule.apply, declares)


def _r1_root(e: Any) -> Optional[str]:
    """The DOWNSTREAM rung: R1 applies one guarded rule at the root and returns the answer."""
    if not isinstance(e, sp.Expr):
        return None
    a = _R1.answer(e)
    return None if a is None else str(a)


def _degree_only(e: Any) -> Optional[Any]:
    """A stage that is sound for the local target "is this linear?" and destroys the end
    target. Keeps the degree and throws the coefficients away."""
    if not isinstance(e, sp.Expr) or not e.free_symbols:
        return None
    try:
        return sp.Symbol(f"deg_{sp.Poly(e, x).degree()}")
    except sp.PolynomialError:
        return None


def _launder(e: Any) -> Any:
    """A stage that CLAIMS to reduce and quietly keeps the input alongside its output, so a
    downstream stage measures as sufficient on bits it was never handed."""
    return ("declared_output", e)


def _unlaunder_root(e: Any) -> Optional[str]:
    """Downstream of the launderer: reaches past the declared output to the smuggled input."""
    if isinstance(e, tuple) and len(e) == 2:
        return _r1_root(_stage_from_registry("numer").apply(e[1]) or e[1])
    return _r1_root(e)


def _shortcut(e: Any) -> Any:
    """Ignores whatever it is handed and re-derives the answer from the original problem. The
    stages before it are decorative."""
    return e


SOUND_CHAIN = Chain("sound", (
    _stage_from_registry("together"),
    _stage_from_registry("numer"),
    Stage("r1_root", _r1_root),
))

LOCALLY_SOUND_CHAIN = Chain("locally_sound", (
    _stage_from_registry("together"),
    _stage_from_registry("numer"),
    Stage("degree_only", _degree_only),
    Stage("r1_root", _r1_root),
))

LAUNDERING_CHAIN = Chain("laundering", (
    _stage_from_registry("together"),
    Stage("launder", _launder),
    Stage("unlaunder_root", _unlaunder_root),
))


class _ShortcutChain(Chain):
    """Answers from the ORIGINAL input regardless of what the stages produced."""

    def run(self, value: Any) -> List[Any]:
        trace = super().run(value)
        trace[-1] = SOUND_CHAIN.answer(value)
        return trace


SHORTCUT_CHAIN = _ShortcutChain("shortcut", (
    Stage("annotate", REGISTRY["annotate"]().apply),
    Stage("annotate2", REGISTRY["annotate"]().apply),
    Stage("shortcut_answer", _shortcut),
))


# --------------------------------------------------------------------------------------------
# Analysis

@dataclass
class ChainReport:
    """The composition profile: (deficit, excess) after each stage, plus the located seam."""

    chain: str
    profile: List[Tuple[float, float]]
    is_chain: bool
    stage_names: Tuple[str, ...]

    @property
    def deficit_monotone(self) -> bool:
        return all(self.profile[k][0] <= self.profile[k + 1][0] + 1e-12
                   for k in range(len(self.profile) - 1))

    @property
    def excess_monotone(self) -> bool:
        return all(self.profile[k][1] >= self.profile[k + 1][1] - 1e-12
                   for k in range(len(self.profile) - 1))

    @property
    def seam(self) -> Optional[str]:
        """The first stage at which deficit rises above zero — where the chain broke."""
        for k in range(1, len(self.profile)):
            if self.profile[k][0] > 1e-12:
                return self.stage_names[k - 1]
        return None

    @property
    def sound(self) -> bool:
        return self.seam is None

    @property
    def excess_spent(self) -> float:
        """Surplus bits the chain consumed. On a sound chain this is the whole budget."""
        return self.profile[0][1] - self.profile[-1][1]


def analyse_chain(chain: Chain, problems: Sequence[sp.Expr] = PROBLEMS) -> ChainReport:
    """Measure the chain against the end target, stage by stage."""
    traces = [chain.run(p) for p in problems]
    n = len(problems)
    depth = len(traces[0])
    partitions = [induced_partition(list(range(n)), lambda i, k=k: sp.srepr(traces[i][k])
                                    if isinstance(traces[i][k], sp.Expr) else str(traces[i][k]))
                  for k in range(depth)]
    truth = induced_partition(list(range(n)), lambda i: true_root(problems[i]))
    return ChainReport(
        chain=chain.name,
        profile=information_profile(partitions, truth, n),
        is_chain=is_refinement_chain(partitions, n),
        stage_names=tuple(st.name for st in chain.stages),
    )


def ablate(chain: Chain, index: int) -> Chain:
    """Drop one stage. Canon R9's deletion test, lifted from lemmas to pipeline stages: if the
    answers are unchanged, that stage was decorative."""
    # type(chain), not Chain: a shortcut chain must stay a shortcut chain under ablation, or
    # the ablation would be testing the class rather than the stage.
    return type(chain)(f"{chain.name}-minus-{chain.stages[index].name}",
                       chain.stages[:index] + chain.stages[index + 1:])


def stage_is_load_bearing(chain: Chain, index: int,
                          problems: Sequence[sp.Expr] = PROBLEMS) -> bool:
    before = [chain.answer(p) for p in problems]
    after = [ablate(chain, index).answer(p) for p in problems]
    return before != after


def is_injective_on(chain: Chain, index: int,
                    problems: Sequence[sp.Expr] = PROBLEMS) -> bool:
    """Does stage `index` discard nothing on this battery? `VI(P_k, P_{k−1}) = 0`.

    **This is NOT the laundering detector, and the naming records a measured failure.** I built
    it as one, on the reasoning that a stage which claims to reduce and discards nothing must be
    smuggling. Measured: the SOUND chain's `together` stage also reports True, because it is
    injective on these six problems — a lossless transform discards nothing either. Injectivity
    and laundering are indistinguishable to any information measure.

    What actually separates them is the declared interface, not the information flow, so the
    real detector is `reads_beyond_declared_output` below, and it is an INTERVENTION rather than
    an observation.
    """
    traces = [chain.run(p) for p in problems]
    n = len(problems)
    key = lambda k: (lambda i: sp.srepr(traces[i][k]) if isinstance(traces[i][k], sp.Expr)
                     else str(traces[i][k]))
    before = induced_partition(list(range(n)), key(index))
    after = induced_partition(list(range(n)), key(index + 1))
    return variation_of_information(before, after, n) < 1e-12


def reads_beyond_declared_output(chain: Chain, index: int, declared_component: int = 0,
                                 problems: Sequence[sp.Expr] = PROBLEMS) -> bool:
    """THE LAUNDERING DETECTOR, and it has to be an intervention.

    Corrupt everything the stage emitted EXCEPT its declared output, then re-run the rest of the
    chain. If the answers change, some downstream stage was reading past the declared interface.

    This is why it cannot be an information measurement: laundering is a CONTRACT violation, not
    an information-flow property. The bits are genuinely present in both the honest and the
    dishonest chain; what differs is whether a downstream stage was entitled to them. Third
    instance in this loop of the same shape — completeness (claim v13) and R11's reference class
    were the others — where the measurement cannot see it and an external declaration must.
    """
    baseline = [chain.answer(pb) for pb in problems]
    corrupted = []
    for pb in problems:
        trace = chain.run(pb)
        mid = trace[index + 1]
        if isinstance(mid, tuple):
            blanked = tuple(v if i == declared_component else sp.Symbol("REDACTED")
                            for i, v in enumerate(mid))
        else:
            corrupted.append(chain.answer(pb))       # nothing else was emitted to corrupt
            continue
        cur = blanked
        for st in chain.stages[index + 1:]:
            nxt = st.apply(cur)
            cur = cur if nxt is None else nxt
        corrupted.append(cur)
    return baseline != corrupted
