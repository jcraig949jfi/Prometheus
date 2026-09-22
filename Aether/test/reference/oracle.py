"""
Aether AETH-00 (semantics_id aeth00.v1) -- PRIMARY independent CPU oracle.

This is a deliberately naive, directly-readable re-statement of the
frozen transition law in Aether/AETHER_SPEC.md. It is test-support code,
NOT the production implementation: no GPU-oriented optimization, no
generalized "future Aether" framework, no perturbation/resource/observatory
machinery. It exists to be ground truth for AETH-00A's tests.

Every formula below is copied verbatim (in meaning, not just style) from
Aether/AETHER_SPEC.md sections "State", "Instruction set", "WRITE
semantics and proposal identity", "Tick semantics", "Complete transition
function parameters", "Collision arbitration". Section names are cited
in comments so a reader can check this file line-by-line against the
frozen contract.

A SECOND, structurally independent implementation of the same law lives
in oracle_independent.py, used only for differential testing (spec test
22); this file must not be edited to resemble it or vice versa.
"""

from typing import Dict, List, NamedTuple, Optional, Tuple

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1

OPCODE, ARG0, ARG1, PAYLOAD = 0, 1, 2, 3
FIELD_NAMES = ("opcode", "arg0", "arg1", "payload")

WRITE_OPCODE = 0x01  # Instruction set (frozen -- Q27): 0x01 = WRITE.
# Every other byte value (0x00 included) is RESERVED_INERT.

SEED_XOR_CONSTANT = 0x9E3779B97F4A7C15
MIX_MUL_1 = 0xBF58476D1CE4E5B9
MIX_MUL_2 = 0x94D049BB133111EB

# Direction order frozen (arg0 mod 4): 0=N, 1=E, 2=S, 3=W.
NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3


class DuplicateSourceProposalError(Exception):
    """Two or more proposals in one contest share a physical source site.

    Forbidden by the proposal-identity rule (AETHER_SPEC.md, "WRITE
    semantics and proposal identity"). This can never happen from a
    correct decode of AETH-00 state; if it does, it is an
    IMPLEMENTATION DEFECT (AETHER_SPEC.md, "Collision arbitration"),
    not a case the arbitration law resolves. AETHER_TEST_PLAN.md test
    27 requires the harness to detect exactly this.
    """


class TickOverflowError(OverflowError):
    """Raised when step() is attempted from tick == 2**64 - 1."""


class Proposal(NamedTuple):
    source: Tuple[int, int]
    target: Tuple[int, int]
    field: int
    value: int


Grid = List[List[Tuple[int, int, int, int]]]
Contests = Dict[Tuple[Tuple[int, int], int], List[Proposal]]


def splitmix64_mix(x: int) -> int:
    """M(x): the SplitMix64 finalizer (AETHER_SPEC.md, Collision arbitration)."""
    x &= MASK64
    u = ((x ^ (x >> 30)) * MIX_MUL_1) & MASK64
    v = ((u ^ (u >> 27)) * MIX_MUL_2) & MASK64
    return (v ^ (v >> 31)) & MASK64


def pack_coords(row: int, col: int) -> int:
    """C(row, col) = (uint64(row) << 32) | uint64(col)."""
    if not (0 <= row <= MASK32):
        raise ValueError(f"row out of uint32 range: {row}")
    if not (0 <= col <= MASK32):
        raise ValueError(f"col out of uint32 range: {col}")
    return ((row & MASK32) << 32) | (col & MASK32)


def arbitration_priority(
    seed: int,
    tick: int,
    target_row: int,
    target_col: int,
    target_field: int,
    source_row: int,
    source_col: int,
) -> int:
    """Chained priority construction (AETHER_SPEC.md, Collision arbitration)."""
    h0 = splitmix64_mix((seed & MASK64) ^ SEED_XOR_CONSTANT)
    h1 = splitmix64_mix(h0 ^ (tick & MASK64))
    h2 = splitmix64_mix(h1 ^ pack_coords(target_row, target_col))
    h3 = splitmix64_mix(h2 ^ (target_field & MASK64))
    return splitmix64_mix(h3 ^ pack_coords(source_row, source_col))


def neighbor(row: int, col: int, H: int, W: int, direction: int) -> Tuple[int, int]:
    """arg0 mod 4 -> von Neumann neighbor, toroidal Euclidean-modulo wrap."""
    if direction == NORTH:
        return (row - 1) % H, col
    if direction == EAST:
        return row, (col + 1) % W
    if direction == SOUTH:
        return (row + 1) % H, col
    if direction == WEST:
        return row, (col - 1) % W
    raise ValueError(f"direction must be 0..3, got {direction}")



def decode_proposals(
    grid: Grid, H: int, W: int, trace: Optional[list] = None
) -> List[Proposal]:
    """S[t] -> every WRITE site emits exactly one proposal (AETHER_SPEC.md,
    "WRITE semantics and proposal identity"). Reads only the given grid
    (the tick-start snapshot); never mutates it."""
    proposals: List[Proposal] = []
    for r in range(H):
        for c in range(W):
            opcode, arg0, arg1, payload = grid[r][c]
            if opcode != WRITE_OPCODE:
                continue  # RESERVED_INERT: emits no proposal.
            direction = arg0 % 4
            field = arg1 % 4
            target = neighbor(r, c, H, W, direction)
            p = Proposal(source=(r, c), target=target, field=field, value=payload)
            proposals.append(p)
            if trace is not None:
                trace.append(("proposal_emitted", p.source, p.target, p.field, p.value))
    return proposals


def group_contests(proposals: List[Proposal]) -> Contests:
    """Group proposals by (target site, target field); each group is one
    independent arbitration contest (AETHER_SPEC.md, "Independent
    arbitration of different fields")."""
    contests: Contests = {}
    for p in proposals:
        key = (p.target, p.field)
        contests.setdefault(key, []).append(p)
    return contests


def assert_no_duplicate_sources(contests: Contests) -> None:
    """Harness-level defect detector (AETHER_TEST_PLAN.md test 27): the
    proposal-identity rule forbids two proposals in one contest sharing a
    physical source site. A correct decode of any valid AETH-00 state can
    never trigger this; if it does, the CANDIDATE implementation under
    test is defective, not the arbitration law."""
    for key, plist in contests.items():
        sources = [p.source for p in plist]
        if len(sources) != len(set(sources)):
            raise DuplicateSourceProposalError(key, sources)


def arbitrate(
    seed: int, tick: int, contests: Contests
) -> Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]]:
    """Exactly one deterministic winner per contest: greatest unsigned
    priority wins (AETHER_SPEC.md, "Collision arbitration"). Iteration
    order of `plist` must not affect the result (test 8)."""
    winners: Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]] = {}
    for (target, field), plist in contests.items():
        best_p: Optional[Proposal] = None
        best_priority = -1  # priority is always >= 0 (uint64).
        for p in plist:
            sr, sc = p.source
            tr, tc = target
            prio = arbitration_priority(seed, tick, tr, tc, field, sr, sc)
            if best_p is None or prio > best_priority:
                best_p, best_priority = p, prio
        assert best_p is not None
        winners[(target, field)] = (best_p, best_priority)
    return winners


def commit(
    grid: Grid,
    H: int,
    W: int,
    winners: Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]],
    trace: Optional[list] = None,
) -> Grid:
    """All winners commit simultaneously into a COPIED snapshot; S[t] is
    never perturbed in place (AETHER_SPEC.md, "Tick semantics"). Any field
    untouched by a winner is bit-identical to its S[t] value because it
    is only ever copied, never rewritten."""
    next_grid: Grid = [[site for site in row] for row in grid]
    for (target, field), (winner, _priority) in winners.items():
        tr, tc = target
        old_cell = list(next_grid[tr][tc])
        old_value = old_cell[field]
        old_cell[field] = winner.value
        next_grid[tr][tc] = tuple(old_cell)
        if trace is not None:
            trace.append(("proposal_won", winner.source, target, field, winner.value))
            trace.append(
                ("stored_bits_changed", target, field, old_value != winner.value)
            )
    return next_grid


class Aeth00World:
    """One AETH-00 lattice state S[t] plus the (seed, tick) needed to
    compute S[t+1]. Construction validates all "Complete transition
    function parameters" (AETHER_SPEC.md) that are checkable statically.
    """

    SEMANTICS_ID = "aeth00.v1"

    def __init__(
        self,
        H: int,
        W: int,
        seed: int,
        tick: int = 0,
        grid: Optional[Grid] = None,
    ):
        if not (isinstance(H, int) and isinstance(W, int)):
            raise ValueError("H and W must be int")
        if not (1 <= H <= MASK32) or not (1 <= W <= MASK32):
            raise ValueError(f"H, W must satisfy 1 <= H,W <= 2**32-1; got H={H} W={W}")
        if not (0 <= seed <= MASK64):
            raise ValueError(f"seed must be uint64; got {seed}")
        if not (0 <= tick <= MASK64):
            raise ValueError(f"tick must be uint64; got {tick}")
        self.H = H
        self.W = W
        self.seed = seed
        self.tick = tick
        if grid is None:
            self.grid: Grid = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
        else:
            if len(grid) != H or any(len(row) != W for row in grid):
                raise ValueError("grid shape does not match H, W")
            self.grid = [[tuple(site) for site in row] for row in grid]

    @classmethod
    def from_bytes(cls, H: int, W: int, seed: int, data: bytes, tick: int = 0):
        """Full H*W*4 uint8 buffer, row-major (row, col, field), field
        order opcode/arg0/arg1/payload (AETHER_SPEC.md, "State")."""
        if len(data) != H * W * 4:
            raise ValueError(
                f"lattice buffer length {len(data)} != H*W*4 ({H * W * 4})"
            )
        grid: Grid = []
        idx = 0
        for _r in range(H):
            row = []
            for _c in range(W):
                row.append((data[idx], data[idx + 1], data[idx + 2], data[idx + 3]))
                idx += 4
            grid.append(row)
        return cls(H, W, seed, tick=tick, grid=grid)

    def to_bytes(self) -> bytes:
        out = bytearray(self.H * self.W * 4)
        idx = 0
        for r in range(self.H):
            for c in range(self.W):
                out[idx : idx + 4] = bytes(self.grid[r][c])
                idx += 4
        return bytes(out)

    def step(self, trace: Optional[list] = None) -> "Aeth00World":
        """S[t] -> S[t+1] (AETHER_SPEC.md, "Tick semantics"). Returns a
        NEW world; does not mutate self."""
        if self.tick == MASK64:
            raise TickOverflowError(
                "cannot step from tick == 2**64 - 1 (AETHER_SPEC.md, "
                "Complete transition function parameters, tick-overflow)"
            )
        proposals = decode_proposals(self.grid, self.H, self.W, trace=trace)
        contests = group_contests(proposals)
        assert_no_duplicate_sources(contests)
        winners = arbitrate(self.seed, self.tick, contests)
        next_grid = commit(self.grid, self.H, self.W, winners, trace=trace)
        return Aeth00World(self.H, self.W, self.seed, tick=self.tick + 1, grid=next_grid)
