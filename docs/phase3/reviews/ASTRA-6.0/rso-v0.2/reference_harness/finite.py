"""Exact, small reference worlds; not adapters to native scientific runtimes."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product


def small_int(value, low=0, high=4):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("integer outside finite domain")
    return value


def recovery(encoder, decoder):
    """Uniform key, one message, no additional key-dependent observation."""
    m, channels = len(encoder), len(decoder)
    small_int(m, 1)
    small_int(channels, 1)
    for message in encoder:
        small_int(message, 0, channels - 1)
    for answer in decoder:
        small_int(answer, 0, m - 1)
    return Fraction(sum(decoder[encoder[k]] == k for k in range(m)), m)


def channel_bound(keys, channels):
    small_int(keys, 1)
    small_int(channels, 1)
    return Fraction(min(keys, channels), keys)


def channel_optimum(keys, channels):
    """Enumerate every deterministic encoder/decoder in the bounded class."""
    channel_bound(keys, channels)
    return max(recovery(e, d)
               for e in product(range(channels), repeat=keys)
               for d in product(range(keys), repeat=channels))


def bit_answers(intervention):
    if intervention not in ("carry", "reset", "flip"):
        raise ValueError("unknown intervention")
    return tuple(b if intervention == "carry" else
                 0 if intervention == "reset" else 1 - b for b in (0, 1))


def detector_counts():
    return tuple(sum(a == b for b, a in enumerate(bit_answers(mode)))
                 for mode in ("carry", "reset", "flip"))


@dataclass(frozen=True)
class SearchTrace:
    proposals: tuple
    states: tuple

    @property
    def hit_step(self):
        return next((i for i, state in enumerate(self.states) if state == 2), None)


def search(scores, founder, policy, budget=2):
    """Directed chain 0->1->2; founder evaluation is given, rejections charged."""
    if len(scores) != 3 or any(type(s) is not int for s in scores):
        raise ValueError("three integer scores required")
    small_int(founder, 0, 2)
    small_int(budget, 0, 8)
    if policy not in ("strict", "nondecreasing", "enumerate"):
        raise ValueError("unknown search policy")
    current, proposals, states = founder, [], [founder]
    for _ in range(budget):
        if current == 2:
            break
        candidate = current + 1
        proposals.append(candidate)
        accept = (policy == "enumerate" or scores[candidate] > scores[current]
                  or (policy == "nondecreasing" and scores[candidate] == scores[current]))
        if accept:
            current = candidate
        states.append(current)
    return SearchTrace(tuple(proposals), tuple(states))


def search_record(lineage, policy):
    """Lineage is reported finite ancestry, not authenticated physical custody."""
    if tuple(lineage) not in ((0,), (2, 1)):
        raise ValueError("unknown finite founder construction")
    trace = search((0, -1, 1), lineage[-1], policy)
    return {"lineage": list(lineage), "policy": policy,
            "proposals": list(trace.proposals), "states": list(trace.states)}


def continuation(checkpoint, steps=2):
    """T(q,c)=(1-q,c XOR q); output the new c, not a capture-complete flag."""
    q, c = checkpoint
    small_int(q, 0, 1)
    small_int(c, 0, 1)
    small_int(steps, 0, 8)
    outputs = []
    for _ in range(steps):
        q, c = 1 - q, c ^ q
        outputs.append(c)
    return tuple(outputs)


@dataclass(frozen=True)
class BoundaryState:
    allowed: int
    displayed: int
    pending: tuple

    def __post_init__(self):
        small_int(self.allowed, 0, 1)
        small_int(self.displayed, 0, 1)
        pending = tuple(self.pending)
        if len(pending) > 1:
            raise ValueError("only one in-flight bit modeled")
        for bit in pending:
            small_int(bit, 0, 1)
        object.__setattr__(self, "pending", pending)

    def clean_reset(self):
        return BoundaryState(self.allowed, 0, ())

    def leaky_reset(self):
        return BoundaryState(self.allowed, 0, self.pending)

    def tick(self):
        displayed = self.pending[0] if self.pending else self.displayed
        return BoundaryState(self.allowed, displayed, ())

    def observe(self):
        return self.allowed, self.displayed


def encode_bit(bit, encoding):
    small_int(bit, 0, 1)
    if encoding == "plain":
        return (bit,)
    if encoding == "one_hot":
        return (1 - bit, bit)
    raise ValueError("unknown re-encoding")


def read_bit(state, encoding):
    if encoding not in ("plain", "one_hot"):
        raise ValueError("unknown re-encoding")
    if state not in tuple(encode_bit(b, encoding) for b in (0, 1)):
        raise ValueError("invalid encoded bit")
    return state[0] if encoding == "plain" else state[1]


def biased_ruler(state):
    """Deliberately wrong outside the plain encoding."""
    return state[0]


def positive_rational(value):
    if type(value) not in (int, Fraction) or value <= 0:
        raise ValueError("positive exact rational required")
    return Fraction(value)


@dataclass(frozen=True)
class History:
    beta: Fraction

    def __post_init__(self):
        object.__setattr__(self, "beta", positive_rational(self.beta))

    @classmethod
    def learn(cls, pairs):
        pairs = tuple(pairs)
        if not pairs:
            raise ValueError("calibration history required")
        ratios = {positive_rational(h) / positive_rational(x) for x, h in pairs}
        if len(ratios) != 1:
            raise ValueError("inconsistent calibration history")
        return cls(ratios.pop())

    def build(self, x):
        return Updater(1 / (self.beta * positive_rational(x)))


@dataclass(frozen=True)
class Updater:
    eta: Fraction

    def __post_init__(self):
        object.__setattr__(self, "eta", positive_rational(self.eta))

    def step(self, state, gradient):
        if any(type(v) not in (int, Fraction) for v in (state, gradient)):
            raise ValueError("exact task inputs required")
        return Fraction(state) - self.eta * gradient


def task_gradient(curvature, target):
    if type(target) is not int or target not in (-1, 1):
        raise ValueError("fresh binary target required")
    return -positive_rational(curvature) * target  # Fresh task state is zero.


def flattened(beta, x, gradient):
    return -gradient / (positive_rational(beta) * positive_rational(x))


def sign_gradient_r0(gradient):
    return -1 if gradient > 0 else 1 if gradient < 0 else 0


def updater_rows():
    """A/B finish before BOTH C targets are branched; U carries only frozen eta."""
    rows = []
    for beta, x in product((1, 2), repeat=2):
        history = History.learn(((1, beta), (2, 2 * beta)))
        updater = history.build(x)
        swapped = History.learn(((1, 3 - beta),)).build(x)
        del history  # No V input to C, not merely a disconnected=true label.
        for target in (-1, 1):
            g = task_gradient(beta * x, target)
            rows.append(tuple(str(v) for v in (
                updater.step(0, g), flattened(beta, x, g),
                Updater(Fraction(1)).step(0, g), swapped.step(0, g),
                updater.step(0, 0), sign_gradient_r0(g))))
    return tuple(rows)