"""
Aether AETH-00 (semantics_id aeth00.v1) -- MINIMAL PRODUCTION CPU
transition implementation.

Disposable conformance specimen (AETHER_SPEC.md, AETH-00 "Scope"):
exists only to demonstrate that a production implementation can
satisfy the frozen aeth00.v1 contract exactly. Not a template or a
step toward a generalized future Aether engine. No GPU code, no
mutation/resource/observatory machinery, no ISA dispatch framework.

INDEPENDENCE STATEMENT: this module imports NOTHING from
reference.oracle, reference.oracle_independent, reference.mutants, or
reference.golden_vectors (see Aether/test/reference/). Its algorithm is
also a different SHAPE from both reference oracles: those are "scatter"
implementations (decode every WRITE source's one proposal, then group
proposals by target). This module is a "gather" implementation instead
-- for every (target cell, target field) it inspects only that
target's up to 4 physical von Neumann neighbors and asks whether each
neighbor's own (opcode, arg0, arg1) addresses this specific (target,
field), directly following AETHER_SPEC.md's non-normative "Deferred
implementation guidance" ("one owner per target cell -> inspects its
up to 4 neighbor sources"). This also makes "two proposals from the
same physical source in one contest" structurally impossible here (see
_NEIGHBOR_SLOTS docstring below) rather than something checked for
after the fact. Literal constants shared with the reference oracles
(the two SplitMix64 multipliers, the seed XOR constant, the
opcode/direction/field encodings) are frozen protocol constants
transcribed from AETHER_SPEC.md itself, not values copied from oracle
code.

Public surface (deliberately minimal): State, step(), arbitration_priority(),
InvalidStateError, TickOverflowError. No campaign runner, no simulation
class, no plugin system, no organism abstraction.
"""

from typing import Optional

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1

SEMANTICS_ID = "aeth00.v1"

WRITE_OPCODE = 0x01  # AETHER_SPEC.md "Instruction set": 0x01 = WRITE;
# every other byte value (0x00 included) is RESERVED_INERT.

OPCODE, ARG0, ARG1, PAYLOAD = 0, 1, 2, 3  # field indices within a cell.

# arg0 mod 4 direction encoding (AETHER_SPEC.md "Direction encoding").
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3

_SEED_XOR_CONSTANT = 0x9E3779B97F4A7C15
_MIX_MUL_A = 0xBF58476D1CE4E5B9
_MIX_MUL_B = 0x94D049BB133111EB


class InvalidStateError(ValueError):
    """An input cannot be represented by a frozen aeth00.v1 semantic
    type (AETHER_SPEC.md "Complete transition function parameters").
    Raised at the API boundary; the physics is never silently
    truncated or coerced (AETH-00B input-validation ruling)."""


class TickOverflowError(OverflowError):
    """step() was called with tick == 2**64 - 1 (AETHER_SPEC.md,
    tick-overflow behavior: REJECTED, never wrapped)."""


def _require_int(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidStateError(f"{name} must be int, got {type(value).__name__}")
    return value


def _mix64(x: int) -> int:
    """M(x): the SplitMix64 finalizer (AETHER_SPEC.md "Collision
    arbitration"). Public-domain integer-hashing technique."""
    x &= MASK64
    x = (x ^ (x >> 30)) & MASK64
    x = (x * _MIX_MUL_A) & MASK64
    x = (x ^ (x >> 27)) & MASK64
    x = (x * _MIX_MUL_B) & MASK64
    return (x ^ (x >> 31)) & MASK64


def _pack32(hi: int, lo: int) -> int:
    """C(hi, lo) = (uint64(hi) << 32) | uint64(lo); hi, lo in [0, 2**32-1]
    (AETHER_SPEC.md "Collision arbitration")."""
    if not (0 <= hi <= MASK32):
        raise InvalidStateError(f"coordinate component out of uint32 range: {hi}")
    if not (0 <= lo <= MASK32):
        raise InvalidStateError(f"coordinate component out of uint32 range: {lo}")
    return ((hi & MASK32) << 32) | (lo & MASK32)


def arbitration_priority(
    seed: int,
    tick: int,
    target_row: int,
    target_col: int,
    target_field: int,
    source_row: int,
    source_col: int,
) -> int:
    """Frozen chained-SplitMix64 priority (AETHER_SPEC.md "Collision
    arbitration"). Exposed as a standalone pure function (not tied to a
    State) so its output can be checked directly against
    AETHER_TEST_PLAN.md test 23's frozen golden vectors."""
    h0 = _mix64((seed & MASK64) ^ _SEED_XOR_CONSTANT)
    h1 = _mix64(h0 ^ (tick & MASK64))
    h2 = _mix64(h1 ^ _pack32(target_row, target_col))
    h3 = _mix64(h2 ^ (target_field & MASK64))
    return _mix64(h3 ^ _pack32(source_row, source_col))


class State:
    """One aeth00.v1 lattice snapshot: H, W, and the flat H*W*4 uint8
    buffer (row-major: row, then col, then field in opcode/arg0/arg1/
    payload order -- AETHER_SPEC.md "State"). Carries NO seed, tick, or
    history: those are supplied fresh to each step() call below. No
    hidden state."""

    __slots__ = ("H", "W", "data")

    def __init__(self, H: int, W: int, data):
        H = _require_int("H", H)
        W = _require_int("W", W)
        if not (1 <= H <= MASK32):
            raise InvalidStateError(f"H must satisfy 1 <= H <= 2**32-1; got {H}")
        if not (1 <= W <= MASK32):
            raise InvalidStateError(f"W must satisfy 1 <= W <= 2**32-1; got {W}")
        if isinstance(data, int):
            # bytes(int) silently builds an int-length zero buffer instead of
            # treating the int as invalid content -- explicitly rejected so
            # a caller's mistake can never be silently reinterpreted as a
            # request for that many zero bytes.
            raise InvalidStateError("data must be a byte sequence, not an int")
        try:
            normalized = bytes(data)  # raises for out-of-[0,255] / non-int elements
        except (TypeError, ValueError) as exc:
            raise InvalidStateError(
                f"data must be a byte-exact (uint8) sequence: {exc}"
            ) from exc
        expected_len = H * W * 4
        if len(normalized) != expected_len:
            raise InvalidStateError(
                f"data length {len(normalized)} != H*W*4 ({expected_len})"
            )
        self.H = H
        self.W = W
        self.data = normalized

    def cell(self, row: int, col: int):
        """Returns (opcode, arg0, arg1, payload) for (row, col)."""
        i = (row * self.W + col) * 4
        d = self.data
        return d[i], d[i + 1], d[i + 2], d[i + 3]

    def __eq__(self, other):
        return (
            isinstance(other, State)
            and self.H == other.H
            and self.W == other.W
            and self.data == other.data
        )

    def __repr__(self):
        return f"State(H={self.H}, W={self.W}, data=<{len(self.data)} bytes>)"


# The 4 physical von Neumann neighbors of a target cell, paired with the
# arg0 mod 4 direction value THAT NEIGHBOR must itself encode for its
# one proposal to land on this target (AETHER_SPEC.md "Direction
# encoding" + non-normative "Deferred implementation guidance"). E.g.
# the neighbor physically north of the target must itself encode SOUTH
# to reach the target. Because each physical cell has exactly one arg0
# value, it can satisfy the required-direction check of AT MOST ONE of
# these 4 slots for AT MOST ONE target overall (the 4 required
# directions below are pairwise distinct) -- so a single physical
# source can never be gathered into two different contests, including
# under toroidal self-aliasing at H<=2 or W<=2, where two slots of the
# SAME target may point at the SAME physical cell but still demand two
# DIFFERENT required directions.
_NEIGHBOR_SLOTS = (
    (-1, 0, SOUTH),  # neighbor to the north; must itself emit SOUTH to hit us
    (1, 0, NORTH),  # neighbor to the south; must itself emit NORTH to hit us
    (0, 1, WEST),  # neighbor to the east; must itself emit WEST to hit us
    (0, -1, EAST),  # neighbor to the west; must itself emit EAST to hit us
)


def _emit_proposal_trace(data: bytes, H: int, W: int, trace: list) -> None:
    """Pure trace side-channel: decodes every WRITE-opcode cell's one
    proposal and appends a `proposal_emitted` event. Never consulted by
    the state-computing code in step() below -- trace-enabled and
    trace-disabled runs execute the identical state-computing path."""
    for r in range(H):
        for c in range(W):
            i = (r * W + c) * 4
            if data[i + OPCODE] != WRITE_OPCODE:
                continue
            arg0, arg1, payload = data[i + ARG0], data[i + ARG1], data[i + PAYLOAD]
            direction, field = arg0 % 4, arg1 % 4
            if direction == NORTH:
                tr, tc = (r - 1) % H, c
            elif direction == EAST:
                tr, tc = r, (c + 1) % W
            elif direction == SOUTH:
                tr, tc = (r + 1) % H, c
            else:
                tr, tc = r, (c - 1) % W
            trace.append(("proposal_emitted", (r, c), (tr, tc), field, payload))


def step(state: State, seed: int, tick: int, trace: Optional[list] = None) -> State:
    """S[t] -> S[t+1] (AETHER_SPEC.md "Tick semantics"). `seed`/`tick`
    are supplied fresh by the caller (no hidden state). Rejects (never
    wraps) a step attempted FROM tick == 2**64-1. Returns a NEW State;
    `state` is never mutated."""
    if not isinstance(state, State):
        raise InvalidStateError(f"state must be a State, got {type(state).__name__}")
    seed = _require_int("seed", seed)
    tick = _require_int("tick", tick)
    if not (0 <= seed <= MASK64):
        raise InvalidStateError(f"seed must satisfy 0 <= seed <= 2**64-1; got {seed}")
    if not (0 <= tick <= MASK64):
        raise InvalidStateError(f"tick must satisfy 0 <= tick <= 2**64-1; got {tick}")
    if tick == MASK64:
        raise TickOverflowError(
            "cannot step from tick == 2**64 - 1 (AETHER_SPEC.md tick-overflow: "
            "rejected before transition, never wrapped)"
        )

    H, W, data = state.H, state.W, state.data
    if trace is not None:
        _emit_proposal_trace(data, H, W, trace)

    out = bytearray(data)  # commit target; `data` (S[t]) itself is untouched.
    for tr in range(H):
        for tc in range(W):
            for field in range(4):
                best_priority = -1
                best_value = None
                best_source = None
                for dr, dc, required_dir in _NEIGHBOR_SLOTS:
                    nr, nc = (tr + dr) % H, (tc + dc) % W
                    ni = (nr * W + nc) * 4
                    if data[ni + OPCODE] != WRITE_OPCODE:
                        continue
                    if data[ni + ARG0] % 4 != required_dir:
                        continue
                    if data[ni + ARG1] % 4 != field:
                        continue
                    prio = arbitration_priority(seed, tick, tr, tc, field, nr, nc)
                    if best_value is None or prio > best_priority:
                        best_priority = prio
                        best_value = data[ni + PAYLOAD]
                        best_source = (nr, nc)
                if best_value is not None:
                    idx = (tr * W + tc) * 4 + field
                    if trace is not None:
                        old = out[idx]
                        trace.append(("proposal_won", best_source, (tr, tc), field, best_value))
                        trace.append(
                            ("stored_bits_changed", (tr, tc), field, old != best_value)
                        )
                    out[idx] = best_value
    return State(H, W, bytes(out))
