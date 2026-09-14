"""cheatlib -- construct incapable populations that an instrument accepts.

    No instrument earns trust merely because it rejects negatives.
    Nemesis must attempt to make it ACCEPT A FRAUD.
    (operator, 2026-09-11)

The base role makes three controls constitutional: an instrument must be
able to demonstrate that it CAN FAIL (negative), that it DETECTS REAL
SUCCESS (positive), and that it DETECTS CHEATING (cheat). The cheat
control is the hard one, because building it means inventing a way to
succeed WITHOUT the capability. This module is that construction kit.

Two families, because instruments come in two shapes.

RESPONDERS answer items, for instruments that score answers. A responder
is anything with ``.respond(item) -> answer``; it is INCAPABLE by
construction, and the point is what it scores anyway.

    DegenerateConstant   one answer, always
    MajorityClass        the most common correct answer in the population
    PayloadReader        reads the answer out of a field carried beside the
                         question -- the leak, not the reasoning

FORGERIES fill structured claims, for instruments that gate on fields.
Each helper produces a value that SATISFIES a predicate while carrying
none of the capability the predicate is there to establish.

    borrow_real_path     a path that exists, chosen without reading it
    token_from_file      a token that occurs in a file, taken from its bytes
    filler               n characters that satisfy a length floor
    absent_marker        a string guaranteed to have zero occurrences

And two measurements that must precede any attack:

    chance_floor         what an incapable responder scores by construction
    shrink               the cheapest member of the crossing population

NOTHING HERE READS OR UNDERSTANDS ANYTHING. That is the entire point: if
an instrument accepts what this module builds, the instrument is not
observing the capability it names.

Self-controls live in roles/Nemesis/science/tests/test_cheatlib.py. The
cheat controls are fired against a KNOWN population (the April Nemesis
ledger) so that a control which has gone silent is detectable: a cheat
control that has never fired is not a control.
"""
from __future__ import annotations

import random
import string
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "Responder", "DegenerateConstant", "MajorityClass", "PayloadReader",
    "ChanceFloor", "chance_floor", "score_responder",
    "borrow_real_path", "token_from_file", "filler", "absent_marker",
    "shrink", "Shrink",
]


# ---------------------------------------------------------------------------
# Responders -- the declared interface is one method
# ---------------------------------------------------------------------------

class Responder:
    """Anything that answers an item. Subclasses are INCAPABLE by design."""

    name = "responder"

    def respond(self, item: Any) -> Any:  # pragma: no cover - interface
        raise NotImplementedError


class DegenerateConstant(Responder):
    """Always the same answer. The cheapest possible strategy."""

    def __init__(self, value: Any, name: str = ""):
        self.value = value
        self.name = name or "constant[{!r}]".format(value)

    def respond(self, item: Any) -> Any:
        return self.value


class MajorityClass(Responder):
    """Always the most common correct answer in the population.

    This is the strategy an instrument must beat before any of its numbers
    mean anything, and it needs no access to the item at all.
    """

    def __init__(self, correct_answers: Iterable[Any], name: str = ""):
        counts = Counter(correct_answers)
        if not counts:
            raise ValueError("majority class needs a non-empty population")
        self.value, self.count = counts.most_common(1)[0]
        self.total = sum(counts.values())
        self.name = name or "majority[{!r}]".format(self.value)

    def respond(self, item: Any) -> Any:
        return self.value


class PayloadReader(Responder):
    """Answers by reading a field carried beside the question.

    The classic leak: the grading payload ships with the item, so a
    three-line reader ties the top of the leaderboard while possessing
    none of the capability. Give it the accessor; it does no inference.
    """

    def __init__(self, accessor: Callable[[Any], Any], field_name: str = "payload"):
        self.accessor = accessor
        self.name = "payload_reader[{}]".format(field_name)

    def respond(self, item: Any) -> Any:
        try:
            return self.accessor(item)
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Chance floors -- computed BEFORE the attack, published beside every number
# ---------------------------------------------------------------------------

@dataclass
class ChanceFloor:
    eligible: int
    majority_value: Any
    majority_rate: float
    uniform_rate: float
    distinct_answers: int

    def as_row(self) -> Dict[str, Any]:
        return {
            "eligible": self.eligible,
            "majority_value": self.majority_value,
            "majority_rate": round(self.majority_rate, 6),
            "uniform_rate": round(self.uniform_rate, 6),
            "distinct_answers": self.distinct_answers,
        }


def chance_floor(correct_answers: Sequence[Any],
                 candidate_counts: Optional[Sequence[int]] = None) -> ChanceFloor:
    """The attainable score of an incapable responder on this population.

    ``majority_rate`` is what a constant responder scores. ``uniform_rate``
    is the expected score of picking uniformly among the offered candidates
    (requires candidate_counts; 0.0 when it cannot be computed). Both are
    reported: a number that does not beat them has not been shown to
    measure anything.
    """
    n = len(correct_answers)
    if n == 0:
        raise ValueError("chance floor needs a non-empty population")
    counts = Counter(correct_answers)
    _, top = counts.most_common(1)[0]
    uniform = 0.0
    if candidate_counts:
        usable = [c for c in candidate_counts if c and c > 0]
        if usable:
            uniform = sum(1.0 / c for c in usable) / n
    return ChanceFloor(
        eligible=n,
        majority_value=counts.most_common(1)[0][0],
        majority_rate=top / n,
        uniform_rate=uniform,
        distinct_answers=len(counts),
    )


def score_responder(responder: Responder,
                    items: Sequence[Any],
                    correct_of: Callable[[Any], Any]) -> Tuple[int, int, float]:
    """(hits, eligible, rate) for a responder over a population."""
    eligible = len(items)
    if eligible == 0:
        raise ValueError("cannot score over an empty population")
    hits = sum(1 for it in items if responder.respond(it) == correct_of(it))
    return hits, eligible, hits / eligible


# ---------------------------------------------------------------------------
# Forgeries -- satisfy a predicate while carrying none of the capability
# ---------------------------------------------------------------------------

def borrow_real_path(candidates: Sequence[str], rng: random.Random) -> str:
    """A path that exists. Chosen at random; its CONTENT is never read."""
    if not candidates:
        raise ValueError("no candidate paths")
    return rng.choice(list(candidates))


def token_from_file(path: Path, rng: random.Random, length: int = 1) -> Optional[str]:
    """A token guaranteed to occur in ``path``, lifted from its bytes.

    Mechanical: no parsing, no meaning, no relation to anything. A
    length-1 token is the cheapest possible satisfier of a
    "token occurs in file" predicate.
    """
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    body = body.strip()
    if len(body) < length:
        return None
    start = rng.randrange(0, len(body) - length + 1)
    tok = body[start:start + length]
    return tok if tok.strip() else None


def filler(n: int, rng: Optional[random.Random] = None) -> str:
    """Exactly ``n`` characters that satisfy a length floor and say nothing."""
    rng = rng or random.Random(0)
    alphabet = string.ascii_lowercase + " "
    return "".join(rng.choice(alphabet) for _ in range(n))


def absent_marker(rng: random.Random, length: int = 24) -> str:
    """A string with zero occurrences anywhere, by construction.

    Satisfies any "the program does not already have this" predicate that
    is implemented as a search, without the item being novel in any sense.
    """
    alphabet = string.ascii_lowercase + string.digits
    return "nemz" + "".join(rng.choice(alphabet) for _ in range(length))


# ---------------------------------------------------------------------------
# Shrinking -- the cheapest member of the crossing population
# ---------------------------------------------------------------------------

@dataclass
class Shrink:
    start_cost: int
    final_cost: int
    steps: List[str]
    final: Any

    def as_row(self) -> Dict[str, Any]:
        return {
            "start_cost": self.start_cost,
            "final_cost": self.final_cost,
            "reduction": self.start_cost - self.final_cost,
            "steps": self.steps,
        }


def shrink(candidate: Any,
           still_crosses: Callable[[Any], bool],
           reductions: Sequence[Tuple[str, Callable[[Any], Optional[Any]]]],
           cost: Callable[[Any], int],
           max_steps: int = 10000) -> Shrink:
    """Reduce a crossing fraud toward its cheapest crossing form.

    ``reductions`` are named single-step simplifications; each returns a
    reduced candidate or None when it does not apply. A reduction is kept
    only if the reduced candidate STILL crosses. Greedy, deterministic,
    and it runs to FIXPOINT -- it stops only when no reduction survives,
    so the result is a local minimum. ``max_steps`` is a runaway guard,
    not a budget: if it is ever reached the result is not a minimum and
    ``steps`` says so.

    (The first version of this function bounded single reductions rather
    than passes and stopped at 28 where the known minimum was 5. Its own
    positive control caught it; the control is pinned in
    tests/test_cheatlib.py::test_positive_shrink_reaches_the_known_minimum.)
    """
    if not still_crosses(candidate):
        raise ValueError("shrink was given a candidate that does not cross")
    current = candidate
    start = cost(current)
    steps: List[str] = []
    while len(steps) < max_steps:
        progressed = False
        for name, fn in reductions:
            try:
                reduced = fn(current)
            except Exception:
                reduced = None
            if reduced is None:
                continue
            if cost(reduced) >= cost(current):
                continue
            if still_crosses(reduced):
                current = reduced
                steps.append(name)
                progressed = True
                break
        if not progressed:
            break
    else:
        steps.append("MAX_STEPS_REACHED -- not a minimum")
    return Shrink(start_cost=start, final_cost=cost(current), steps=steps, final=current)
