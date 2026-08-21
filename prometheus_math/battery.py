"""Battery strength — how many members of a falsification battery actually discriminate.

Motivated by cycle 028's audit of `discovery_pipeline`'s kill path, where two of four checks
returned the same verdict for every candidate measured.

The distinction this module exists to make precise is between a battery's **advertised** size —
how many checks it contains — and its **measured** discriminating size — how many of them
separate any pair of candidates. A member that returns the same verdict for everything
contributes zero bits and is observationally identical to a member that is not there. That is
canon R11's hedging forecaster, relocated from forecasting to falsification.

Two things this deliberately does NOT do.

It does not call a non-firing member useless. A check guarding a rare failure mode has zero
resolution until the rare failure arrives, and that is correct behaviour. What it reports is a
measurement over the candidates actually seen, which is why `n_candidates` is part of the result.

And it does not distinguish a member that CANNOT fire from one that merely HAS not. That
distinction is structural rather than statistical — it needs the member's source, not more
samples — and cycle 028 found both kinds in one battery. `member_resolution` measures; deciding
which kind you have is a reading task.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, List, Mapping, Sequence

from prometheus_math.partition import entropy, induced_partition

__all__ = ["member_resolution", "BatteryStrength", "battery_strength", "BatteryError",
           "reads_its_parameters", "find_flipping_input", "ConstancyVerdict",
           "structural_constancy", "VARIES", "PARAMETER_INDEPENDENT", "UNSETTLED",
           "INVALID_PROBE"]


class BatteryError(ValueError):
    """Raised when the verdict table cannot support a strength measurement."""


def _validate(verdicts: Mapping[str, Sequence[Hashable]]) -> int:
    if not verdicts:
        raise BatteryError("a battery with no members has no strength to measure")
    lengths = {len(v) for v in verdicts.values()}
    if len(lengths) != 1:
        raise BatteryError(f"members disagree on candidate count: {sorted(lengths)}")
    n = lengths.pop()
    if n == 0:
        raise BatteryError(
            "no candidates: a battery's strength over an empty set is undefined, not zero")
    return n


def member_resolution(verdicts: Mapping[str, Sequence[Hashable]]) -> Dict[str, float]:
    """Bits each member contributes over the candidate set — the entropy of its verdict column.

    Zero exactly when the member returned the same verdict for every candidate.
    """
    n = _validate(verdicts)
    return {name: entropy(induced_partition(list(range(n)), lambda i, col=col: col[i]), n)
            for name, col in verdicts.items()}


@dataclass(frozen=True)
class BatteryStrength:
    """Advertised size against measured discriminating size."""

    n_candidates: int
    resolution: Dict[str, float]

    @property
    def advertised(self) -> int:
        return len(self.resolution)

    @property
    def discriminating(self) -> int:
        return sum(1 for bits in self.resolution.values() if bits > 1e-12)

    @property
    def silent_members(self) -> List[str]:
        return sorted(name for name, bits in self.resolution.items() if bits <= 1e-12)

    @property
    def total_bits(self) -> float:
        """Sum of member resolutions. An UPPER bound on the battery's joint discriminating
        power, not the power itself — correlated members double-count here."""
        return sum(self.resolution.values())

    def report(self) -> str:  # pragma: no cover - reporting only
        silent = ", ".join(self.silent_members) or "none"
        return (f"battery of {self.advertised} advertised, {self.discriminating} discriminating "
                f"over {self.n_candidates} candidates; silent: {silent}")


def battery_strength(verdicts: Mapping[str, Sequence[Hashable]]) -> BatteryStrength:
    """Measure a battery from its verdict table: {member name: verdict per candidate}."""
    n = _validate(verdicts)
    return BatteryStrength(n_candidates=n, resolution=member_resolution(verdicts))


# =============================================================================================
# Structural constancy (cycle 029) — making cycle 028's lesson mechanical.
#
# A member that CANNOT fire and one that merely HAS NOT fired both read 0.000 bits, and no
# amount of sampling separates them: sampling can only ever exhibit variation, never rule it
# out. What settles it is the member's SOURCE, so the probe has two tiers with different
# logical force, and an honest middle category for what neither settles.
# =============================================================================================

VARIES = "VARIES"                                 # a flipping input was exhibited
PARAMETER_INDEPENDENT = "PARAMETER_INDEPENDENT"   # the body never reads its arguments
UNSETTLED = "UNSETTLED"                           # reads them, no flip found in the probed space
INVALID_PROBE = "INVALID_PROBE"                   # every probe raised: nothing was measured


def reads_its_parameters(fn) -> bool:
    """Does `fn`'s body reference any of its own parameters?

    A function whose body never loads a parameter cannot have a return value that depends on
    one, so its verdict is the same for every candidate — it is a constant wearing a predicate's
    signature. This is the static half of the probe and it is what caught F9.

    Deliberately conservative: unreadable source, decorators, or anything it cannot parse
    returns True, so an unanalysable function is never *claimed* to be parameter-independent.

    Caveat kept in the open: this asks whether the verdict can depend on the ARGUMENTS. A
    function reading globals or randomness is not constant in general, but is still unable to
    discriminate candidates, which is the property a battery member is being counted for.
    """
    import ast
    import inspect
    import textwrap

    try:
        src = textwrap.dedent(inspect.getsource(fn))
        tree = ast.parse(src)
    except (OSError, TypeError, SyntaxError, IndentationError):
        return True                               # cannot analyse: never claim independence

    node = next((n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))), None)
    if node is None:
        return True

    args = node.args
    names = {a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)}
    for extra in (args.vararg, args.kwarg):
        if extra is not None:
            names.add(extra.arg)
    if not names:
        return True                               # no parameters: not our question

    body = node.body if isinstance(node.body, list) else [node.body]
    for stmt in body:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Name) and sub.id in names and isinstance(sub.ctx, ast.Load):
                return True
    return False


def find_flipping_input(predicate, inputs: Sequence):
    """Search `inputs` for two that make `predicate` disagree.

    Returns `(pair_or_None, n_evaluated)`. `n_evaluated` counts probes that did not raise, and
    it exists because of a defect this function had in its first hour: mapping every exception
    to one sentinel made an all-raising probe space indistinguishable from a constant predicate.
    Both produced "one distinct value, no flip". A caller that cannot tell "nothing varied" from
    "nothing ran" will report the second as the first, which is exactly the error the whole probe
    was built to prevent.

    Finding a pair PROVES the member can fire. Not finding one proves nothing.
    """
    seen: Dict[Hashable, object] = {}
    evaluated = 0
    for item in inputs:
        try:
            v = predicate(item)
        except Exception:
            continue                              # raised: not evidence about the verdict
        evaluated += 1
        key = v if isinstance(v, Hashable) else repr(v)
        if key not in seen:
            seen[key] = item
            if len(seen) > 1:
                a, b = list(seen.values())[:2]
                return (a, b), evaluated
    return None, evaluated


@dataclass(frozen=True)
class ConstancyVerdict:
    """Three-valued, because two of the three cases are provable and one is not.

    VARIES                — a flipping input was exhibited. Proof that the member can fire.
    PARAMETER_INDEPENDENT — the body never reads its arguments. Proof that it cannot.
    UNSETTLED             — it reads them and nothing in the probed space flipped it. Honest.
    """

    name: str
    status: str
    witness: object = None
    n_probed: int = 0
    n_evaluated: int = 0        # probes that did not raise; 0 means nothing was measured

    @property
    def can_fire(self):
        """True / False / None — None means genuinely unknown, not 'assume the worst'."""
        return {VARIES: True, PARAMETER_INDEPENDENT: False}.get(self.status)


def structural_constancy(name: str, predicate, inputs: Sequence,
                         fn_for_source=None) -> ConstancyVerdict:
    """Run both tiers. Dynamic evidence first, because a witness settles it outright.

    INVALID_PROBE precedes every other verdict when nothing ran: a probe space the predicate
    rejects entirely has measured nothing, and must not be reported as quietness.
    """
    flip, evaluated = find_flipping_input(predicate, inputs)
    if flip is not None:
        return ConstancyVerdict(name, VARIES, witness=flip,
                                n_probed=len(inputs), n_evaluated=evaluated)
    if evaluated == 0:
        return ConstancyVerdict(name, INVALID_PROBE, n_probed=len(inputs), n_evaluated=0)
    target = fn_for_source if fn_for_source is not None else predicate
    if not reads_its_parameters(target):
        return ConstancyVerdict(name, PARAMETER_INDEPENDENT,
                                n_probed=len(inputs), n_evaluated=evaluated)
    return ConstancyVerdict(name, UNSETTLED, n_probed=len(inputs), n_evaluated=evaluated)
