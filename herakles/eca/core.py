"""eca_rule_eval_v1: elementary (radius-1) cellular automata. H5 alpha.

SEPARATE FROM `herakles.evca` ON PURPOSE. The radius-3 density-classification
library is finished and qualified and is not touched by this module. Nothing
here imports it, and in particular the radius-3 hex decoder is NOT reused
under a new number: an elementary rule is a NUMBER 0..255, not a 32-hex
string, and the two encodings mean different things.

PINNED CONVENTIONS, from the design brief, each enforced and each tested.

  RADIUS
      r = 1. Three cells: left, centre, right.

  NEIGHBOURHOOD INDEX
      index = 4 * left + 2 * centre + right
      So the LEFT neighbour is the most significant of the three bits. This
      is the standard Wolfram convention and it is stated here because it is
      the opposite end of the same decision that had to be re-earned for the
      radius-3 library.

  OUTPUT
      output = (rule_number >> index) & 1
      Bit `index` of the rule number, counting from the LEAST significant
      end. Note this is the OPPOSITE indexing direction from the radius-3
      table, where bit k from the LEFT is index k. Two conventions, two
      kinds, no shared decoder.

  BOUNDARY
      Periodic ring. Cell 0's left neighbour is cell n-1.

  RULE NUMBER
      An integer 0..255. Any other value is refused.

  LATTICE
      Any n >= 3. There is no odd-N requirement here: this kind performs no
      majority classification, so no tie can arise and inventing a
      constraint the task does not have would be wrong.

  HORIZON
      No default. `steps` is required, as in the radius-3 library.

WHAT THIS MODULE DOES NOT DO. It does not decode 12-bit genomes. The design
places the decoder producer-side, and this evaluator consumes only a resolved
rule number. Adding a decoder here would move a scientific choice inside the
executor.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

import numpy as np

RADIUS = 1
WIDTH = 2 * RADIUS + 1          # 3
TABLE_BITS = 1 << WIDTH         # 8
N_RULES = 1 << TABLE_BITS       # 256


class EcaError(ValueError):
    """Any violation of a pinned convention. Always raised, never warned."""


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def require_rule(rule_number: int) -> int:
    if isinstance(rule_number, bool) or \
            not isinstance(rule_number, (int, np.integer)):
        raise EcaError("rule number must be an integer, got %r"
                       % (rule_number,))
    r = int(rule_number)
    if not (0 <= r < N_RULES):
        raise EcaError("rule number %d is outside 0..%d" % (r, N_RULES - 1))
    return r


def require_lattice(n_cells: int) -> int:
    if isinstance(n_cells, bool) or \
            not isinstance(n_cells, (int, np.integer)):
        raise EcaError("lattice size must be an integer, got %r" % (n_cells,))
    n = int(n_cells)
    if n < WIDTH:
        raise EcaError(
            "lattice size %d is smaller than the %d-cell neighbourhood; the "
            "ring would make a cell its own neighbour twice" % (n, WIDTH))
    return n


def require_steps(steps: int) -> int:
    if isinstance(steps, bool) or not isinstance(steps, (int, np.integer)):
        raise EcaError("steps must be an integer, got %r" % (steps,))
    if int(steps) < 0:
        raise EcaError("steps must be non-negative, got %d" % int(steps))
    return int(steps)


# ---------------------------------------------------------------------------
# The rule
# ---------------------------------------------------------------------------

def rule_table(rule_number: int) -> np.ndarray:
    """(8,) uint8. Entry `index` is the output for that neighbourhood."""
    r = require_rule(rule_number)
    return np.array([(r >> i) & 1 for i in range(TABLE_BITS)], dtype=np.uint8)


def table_to_rule(table: np.ndarray) -> int:
    """Exact inverse of `rule_table`."""
    t = np.asarray(table)
    if t.shape != (TABLE_BITS,) or not np.isin(t, (0, 1)).all():
        raise EcaError("table must be a (%d,) array of 0/1" % TABLE_BITS)
    return int(sum(int(b) << i for i, b in enumerate(t)))


def neighbourhood_index(states: np.ndarray) -> np.ndarray:
    """(n, N) -> (n, N) indices, index = 4*left + 2*centre + right."""
    s = np.asarray(states)
    if s.ndim != 2:
        raise EcaError("states must be 2-D (n_runs, n_cells), got %r"
                       % (s.shape,))
    require_lattice(s.shape[1])
    left = np.roll(s, 1, axis=1).astype(np.int32)     # cell i-1
    centre = s.astype(np.int32)
    right = np.roll(s, -1, axis=1).astype(np.int32)   # cell i+1
    return 4 * left + 2 * centre + right


def step(states: np.ndarray, rule_number: int) -> np.ndarray:
    t = rule_table(rule_number)
    return t[neighbourhood_index(states)]


def evolve(states: np.ndarray, rule_number: int, steps: int,
           record: bool = False) -> np.ndarray:
    require_steps(steps)
    r = require_rule(rule_number)
    cur = np.asarray(states).astype(np.uint8)
    if not record:
        for _ in range(steps):
            cur = step(cur, r)
        return cur
    frames = np.empty((steps + 1,) + cur.shape, dtype=np.uint8)
    frames[0] = cur
    for k in range(steps):
        cur = step(cur, r)
        frames[k + 1] = cur
    return frames


# ---------------------------------------------------------------------------
# The assay: all initial configurations of a small ring, fixed horizon
# ---------------------------------------------------------------------------

def all_configurations(n_cells: int) -> np.ndarray:
    """Every one of the 2^n configurations, in ascending integer order."""
    n = require_lattice(n_cells)
    if n > 20:
        raise EcaError("refusing to enumerate 2^%d configurations" % n)
    idx = np.arange(1 << n, dtype=np.int64)
    bits = ((idx[:, None] >> np.arange(n - 1, -1, -1)[None, :]) & 1)
    return bits.astype(np.uint8)


def behaviour(rule_number: int, n_cells: int, steps: int) -> np.ndarray:
    """The complete observable behaviour of a rule on the declared scope.

    Every initial configuration, evolved the fixed horizon. This IS the
    observable, so two rules with identical output here are behaviourally
    indistinguishable on this scope and must not be counted as two tasks.
    """
    ics = all_configurations(n_cells)
    return evolve(ics, rule_number, steps)


def behaviour_digest(rule_number: int, n_cells: int, steps: int) -> str:
    b = behaviour(rule_number, n_cells, steps)
    h = hashlib.sha256()
    h.update(("eca.v1|%d|%d|" % (n_cells, steps)).encode("ascii"))
    h.update(np.ascontiguousarray(b).tobytes())
    return "sha256:" + h.hexdigest()[:32]


def equivalence_classes(n_cells: int, steps: int) -> Dict[str, List[int]]:
    """Group all 256 rules by observable behaviour on the declared scope.

    The design is explicit that synonymous teachers must not be pretended
    independent. This returns the classes so a task set can be built from
    class representatives while the class membership stays visible.
    """
    out: Dict[str, List[int]] = {}
    for r in range(N_RULES):
        out.setdefault(behaviour_digest(r, n_cells, steps), []).append(r)
    return out


# ---------------------------------------------------------------------------
# The hand-derived rules, for the convention check
# ---------------------------------------------------------------------------

def derive_constant_zero() -> int:
    return table_to_rule(np.zeros(TABLE_BITS, dtype=np.uint8))


def derive_constant_one() -> int:
    return table_to_rule(np.ones(TABLE_BITS, dtype=np.uint8))


def _from_selector(fn) -> int:
    """Build a rule number from a function of (left, centre, right)."""
    t = np.zeros(TABLE_BITS, dtype=np.uint8)
    for idx in range(TABLE_BITS):
        left = (idx >> 2) & 1
        centre = (idx >> 1) & 1
        right = idx & 1
        t[idx] = int(fn(left, centre, right)) & 1
    return table_to_rule(t)


def derive_identity() -> int:
    """Output = centre. Expected to be rule 204."""
    return _from_selector(lambda l, c, r: c)


def derive_shift_left() -> int:
    """Output = right neighbour, so the pattern moves LEFT. Expected 170."""
    return _from_selector(lambda l, c, r: r)


def derive_shift_right() -> int:
    """Output = left neighbour, so the pattern moves RIGHT. Expected 240."""
    return _from_selector(lambda l, c, r: l)


def derive_xor_neighbours() -> int:
    """Output = left XOR right. Expected rule 90."""
    return _from_selector(lambda l, c, r: l ^ r)


#: The six rules the design names, with the derivation that fixes each.
HAND_DERIVED: Tuple[Tuple[str, int, object], ...] = (
    ("constant_zero", 0, derive_constant_zero),
    ("constant_one", 255, derive_constant_one),
    ("identity", 204, derive_identity),
    ("shift_left", 170, derive_shift_left),
    ("shift_right", 240, derive_shift_right),
    ("xor_neighbours", 90, derive_xor_neighbours),
)

# ---------------------------------------------------------------------------
# Initial conditions and the block-output criterion (Capcarrere, Sipper,
# Tomassini 1996, PRL 77:4969). Protocol committed first:
# herakles/specimens/spec-capcarrere-r1-density/PROTOCOL.md
# ---------------------------------------------------------------------------

def make_ics(n_ics: int, n_cells: int, seed: int,
             variant: str = "bernoulli") -> np.ndarray:
    """Seeded initial conditions. No global RNG is touched.

    variant="bernoulli"        each cell iid Bernoulli(0.5). PROTOCOL U1
                               variant A.
    variant="uniform_density"  a density drawn uniformly on [0, 1] per IC,
                               then each cell iid Bernoulli(that density).
                               PROTOCOL U1 variant B.
    The paper says only "randomly generated"; the variant is part of every
    number and is never defaulted silently by a caller that reports one.
    """
    if isinstance(n_ics, bool) or not isinstance(n_ics, (int, np.integer))             or int(n_ics) < 1:
        raise EcaError("n_ics must be a positive integer, got %r" % (n_ics,))
    n = require_lattice(n_cells)
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise EcaError("seed must be an integer, got %r" % (seed,))
    rng = np.random.default_rng(int(seed))
    u = rng.random((int(n_ics), n))
    if variant == "bernoulli":
        return (u < 0.5).astype(np.uint8)
    if variant == "uniform_density":
        rho = rng.random((int(n_ics), 1))
        return (u < rho).astype(np.uint8)
    raise EcaError("unknown IC variant %r" % (variant,))


def density(states: np.ndarray) -> np.ndarray:
    """Exact density of 1s per row, (n,) float64."""
    s = np.asarray(states)
    if s.ndim != 2:
        raise EcaError("states must be 2-D (n_runs, n_cells), got %r"
                       % (s.shape,))
    return s.sum(axis=1) / float(s.shape[1])


def adjacent_pairs(states: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(has00, has11) per row, circular: pair (i, i+1 mod N) for every i."""
    s = np.asarray(states).astype(np.uint8)
    right = np.roll(s, -1, axis=1)
    has11 = ((s == 1) & (right == 1)).any(axis=1)
    has00 = ((s == 0) & (right == 0)).any(axis=1)
    return has00, has11


def block_output_correct(ics: np.ndarray, final: np.ndarray) -> np.ndarray:
    """The theorem's output convention, per IC. Bool (n,).

    density > 0.5 : a 11 pair exists and no 00 pair
    density < 0.5 : a 00 pair exists and no 11 pair
    density = 0.5 : neither (strict alternation)
    Every IC is eligible; there is no tie exclusion and no odd-N rule.
    """
    d = density(ics)
    has00, has11 = adjacent_pairs(final)
    above = (d > 0.5) & has11 & ~has00
    below = (d < 0.5) & has00 & ~has11
    tie = (d == 0.5) & ~has00 & ~has11
    return above | below | tie


def block_output_score(rule_number: int, ics: np.ndarray,
                       steps: int) -> Dict[str, object]:
    """Capcarrere-Sipper-Tomassini block output at horizon `steps`.

    Published-figure horizon is steps = ceil(N/2) (PRL 77:4969, theorem).
    Comparable ONLY to footnote [13] of that paper and to nothing in the
    radius-3 fixed-point line; chance floor 0.5 (a constant rule scores
    the ICs on one side of 0.5), attainable range [0, 1].
    """
    r = require_rule(rule_number)
    s = np.asarray(ics).astype(np.uint8)
    final = evolve(s, r, steps)
    correct = block_output_correct(s, final)
    n = int(s.shape[0])
    return {"criterion": "block_output", "rule": r, "n_cells": int(s.shape[1]),
            "steps": int(steps), "n_eligible": n, "n_correct": int(correct.sum()),
            "score": float(correct.mean()), "correct_mask": correct}


def uniform_at_T_correct(ics: np.ndarray, final: np.ndarray) -> np.ndarray:
    """The fixed-point convention, for the WRONG-CRITERION control only.

    Correct iff the final state is uniform in the majority state of the IC.
    Ties (density exactly 0.5) are counted incorrect here rather than
    excluded, so the eligible count stays n; on odd N no tie exists.
    """
    d = density(ics)
    f = np.asarray(final).astype(np.uint8)
    all1 = (f == 1).all(axis=1)
    all0 = (f == 0).all(axis=1)
    return ((d > 0.5) & all1) | ((d < 0.5) & all0)


def uniform_at_T_score(rule_number: int, ics: np.ndarray,
                       steps: int) -> Dict[str, object]:
    r = require_rule(rule_number)
    s = np.asarray(ics).astype(np.uint8)
    correct = uniform_at_T_correct(s, evolve(s, r, steps))
    return {"criterion": "uniform_at_T", "rule": r, "n_cells": int(s.shape[1]),
            "steps": int(steps), "n_eligible": int(s.shape[0]),
            "n_correct": int(correct.sum()), "score": float(correct.mean()),
            "correct_mask": correct}


def planted_block_configuration(n_cells: int, target: str) -> np.ndarray:
    """The CHEAT control: the answer pattern written directly, no dynamics.

    target "above": one planted 11 block in an otherwise alternating ring;
           "below": one planted 00 block likewise;
           "tie":   pure alternation (needs even N).
    On an odd ring a plain alternation already wraps into exactly one
    same-state pair; on an even ring the block is written explicitly.
    """
    n = require_lattice(n_cells)
    if target == "tie":
        if n % 2:
            raise EcaError("a strict alternation needs even N, got %d" % n)
        cfg = np.array([i % 2 for i in range(n)], dtype=np.uint8)
    elif target in ("above", "below"):
        one = 1 if target == "above" else 0
        if n % 2:
            cfg = np.array([(i + one) % 2 for i in range(n)], dtype=np.uint8)
        else:
            cfg = np.array([one, one] + [(i + one + 1) % 2
                                         for i in range(n - 2)],
                           dtype=np.uint8)
    else:
        raise EcaError("unknown target %r" % (target,))
    has00, has11 = adjacent_pairs(cfg[None, :])
    want11 = target == "above"
    want00 = target == "below"
    if bool(has11[0]) != want11 or bool(has00[0]) != want00:
        raise EcaError("planted configuration did not come out as intended")
    return cfg[None, :]
