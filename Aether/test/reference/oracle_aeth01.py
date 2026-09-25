"""
Aether AETH-01 (candidate semantics_id aeth01.v1, REPAIRED) -- CPU oracle.

Deliberately naive, directly-readable re-statement of the repaired
transition law in Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md
(the consolidated, post-repair text; see also PHYSICS_SPEC_DRAFT.md and
REPAIR_LEDGER_01.md for the full reasoning behind each formula below).
Test-support code, NOT a production implementation: no GPU-oriented
optimization. `aeth01.v1` is a CANDIDATE, not frozen -- this oracle
exists to make the candidate law executable so it can be tested against
KILL_GATES_01.md's hand-worked cases and new property/contract tests,
before any freeze decision.

Reuses AETH-00's unmodified SplitMix64 mix/arbitration/neighbor
primitives (restated here, not imported, so this file is a single
self-contained artifact an independent reviewer can check line-by-line
against the freeze-candidate text without cross-referencing AETH-00's
oracle module).
"""

from typing import Dict, List, NamedTuple, Optional, Tuple

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1
U33_MAX = 1 << 32  # legal domain top for REPLENISH_NUMER / MUT_NUMER (S02(a)).

OPCODE, ARG0, ARG1, PAYLOAD, ENERGY = 0, 1, 2, 3, 4
TEMPLATE_FIELDS = (OPCODE, ARG0, ARG1, PAYLOAD)
NUM_FIELDS = 5

WRITE_OPCODE = 0x01  # unchanged from AETH-00.

# Arbitration constant, unchanged from AETH-00 (AETHER_SPEC.md).
ARBITRATION_SEED_XOR = 0x9E3779B97F4A7C15
MIX_MUL_1 = 0xBF58476D1CE4E5B9
MIX_MUL_2 = 0x94D049BB133111EB

# New, domain-separated constants (PHYSICS_SPEC_DRAFT.md "Perturbation (Mu)"
# / "Replenishment (Rho)"), distinct from the arbitration constant and
# from each other.
MUT_DOMAIN_CONST = 0xD1B54A32D192ED03
REPLENISH_DOMAIN_CONST = 0x2545F4914F6CDD1D

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3


class DuplicateSourceProposalError(Exception):
    """Two proposals in one contest share a physical source site -- a
    harness/implementation defect (AETH-00's proposal-identity rule is
    unchanged for AETH-01: one WRITE site emits exactly one proposal)."""


class TickOverflowError(OverflowError):
    """Raised when step() is attempted from tick == 2**64 - 1 (inherited
    unchanged from AETH-00)."""


class Proposal(NamedTuple):
    source: Tuple[int, int]
    target: Tuple[int, int]
    field: int  # 0..4 (arg1 mod 5)
    value: int  # payload (fields 0-3) or transfer_amt (field 4)


Grid = List[List[Tuple[int, int, int, int, int]]]
Contests = Dict[Tuple[Tuple[int, int], int], List[Proposal]]


def splitmix64_mix(x: int) -> int:
    """M(x): unchanged SplitMix64 finalizer, shared by all three hash
    domains (arbitration, perturbation, replenishment)."""
    x &= MASK64
    u = ((x ^ (x >> 30)) * MIX_MUL_1) & MASK64
    v = ((u ^ (u >> 27)) * MIX_MUL_2) & MASK64
    return (v ^ (v >> 31)) & MASK64


def pack_coords(row: int, col: int) -> int:
    """C(row, col) = (uint64(row) << 32) | uint64(col), unchanged."""
    if not (0 <= row <= MASK32):
        raise ValueError(f"row out of uint32 range: {row}")
    if not (0 <= col <= MASK32):
        raise ValueError(f"col out of uint32 range: {col}")
    return ((row & MASK32) << 32) | (col & MASK32)


def neighbor(row: int, col: int, H: int, W: int, direction: int) -> Tuple[int, int]:
    """arg0 mod 4 -> von Neumann neighbor, toroidal Euclidean-modulo wrap.
    Unchanged from AETH-00."""
    if direction == NORTH:
        return (row - 1) % H, col
    if direction == EAST:
        return row, (col + 1) % W
    if direction == SOUTH:
        return (row + 1) % H, col
    if direction == WEST:
        return row, (col - 1) % W
    raise ValueError(f"direction must be 0..3, got {direction}")


def arbitration_priority(
    seed: int,
    tick: int,
    target_row: int,
    target_col: int,
    target_field: int,
    source_row: int,
    source_col: int,
) -> int:
    """Chained priority construction, unchanged from AETH-00 except that
    `target_field` now ranges 0..4 (a plain uint64 input; the law needs
    no modification for the widened range, PHYSICS_SPEC_DRAFT.md)."""
    h0 = splitmix64_mix((seed & MASK64) ^ ARBITRATION_SEED_XOR)
    h1 = splitmix64_mix(h0 ^ (tick & MASK64))
    h2 = splitmix64_mix(h1 ^ pack_coords(target_row, target_col))
    h3 = splitmix64_mix(h2 ^ (target_field & MASK64))
    return splitmix64_mix(h3 ^ pack_coords(source_row, source_col))


def mu_triggered_and_bit(
    seed: int, tick: int, row: int, col: int, field: int, mut_numer: int
) -> Tuple[bool, int]:
    """Mu's domain-separated hash chain (PHYSICS_SPEC_DRAFT.md, "Perturbation
    (Mu)"). `field` must be in {0,1,2,3} (template fields only -- Mu is
    never invoked for field 4, by construction of the caller). Returns
    (triggered, bit_index)."""
    g0 = splitmix64_mix((seed & MASK64) ^ MUT_DOMAIN_CONST)
    g1 = splitmix64_mix(g0 ^ (tick & MASK64))
    g2 = splitmix64_mix(g1 ^ pack_coords(row, col))
    key = splitmix64_mix(g2 ^ (field & MASK64))
    triggered = (key >> 32) < mut_numer
    bit_index = key & 0b111
    return triggered, bit_index


def rho_triggered(seed: int, tick: int, row: int, col: int, replenish_numer: int) -> bool:
    """Rho's domain-separated hash chain (PHYSICS_SPEC_DRAFT.md,
    "Replenishment (Rho)"), independent per site."""
    r0 = splitmix64_mix((seed & MASK64) ^ REPLENISH_DOMAIN_CONST)
    r1 = splitmix64_mix(r0 ^ (tick & MASK64))
    key = splitmix64_mix(r1 ^ pack_coords(row, col))
    return (key >> 32) < replenish_numer



def decode_and_emit(
    grid: Grid, H: int, W: int, write_cost: int, trace: Optional[list] = None
) -> List[Proposal]:
    """S[t] -> every active, non-starved WRITE site emits exactly one
    proposal (PHYSICS_SPEC_DRAFT.md tick phases 1-2). A site is STARVED
    if its energy < write_cost; a starved site emits nothing and pays no
    WRITE_COST (starvation affects behavior only, never stored state)."""
    proposals: List[Proposal] = []
    for r in range(H):
        for c in range(W):
            opcode, arg0, arg1, payload, energy = grid[r][c]
            if opcode != WRITE_OPCODE:
                continue  # RESERVED_INERT: emits no proposal.
            starved = energy < write_cost
            if trace is not None and starved:
                trace.append(("cell_starved", (r, c)))
            if starved:
                continue
            direction = arg0 % 4
            field = arg1 % NUM_FIELDS
            target = neighbor(r, c, H, W, direction)
            if field == ENERGY:
                value = min(payload, energy - write_cost)
            else:
                value = payload
            p = Proposal(source=(r, c), target=target, field=field, value=value)
            proposals.append(p)
            if trace is not None:
                trace.append(("proposal_emitted", p.source, p.target, p.field, p.value))
    return proposals


def group_contests(proposals: List[Proposal]) -> Contests:
    """Group by (target site, target field); each group is one
    independent arbitration contest, for target_field in 0..4."""
    contests: Contests = {}
    for p in proposals:
        key = (p.target, p.field)
        contests.setdefault(key, []).append(p)
    return contests


def assert_no_duplicate_sources(contests: Contests) -> None:
    """Harness-level defect detector, unchanged from AETH-00: a correct
    decode of any valid AETH-01 state can never produce two proposals
    from the same source site in one contest (each site emits at most
    one proposal per tick, to exactly one (target, field) pair)."""
    for key, plist in contests.items():
        sources = [p.source for p in plist]
        if len(sources) != len(set(sources)):
            raise DuplicateSourceProposalError(key, sources)


def arbitrate(
    seed: int, tick: int, contests: Contests
) -> Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]]:
    """Exactly one deterministic winner per contest: greatest unsigned
    priority wins. Unchanged law from AETH-00; iteration order of
    `plist` must not affect the result."""
    winners: Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]] = {}
    for (target, field), plist in contests.items():
        best_p: Optional[Proposal] = None
        best_priority = -1
        for p in plist:
            sr, sc = p.source
            tr, tc = target
            prio = arbitration_priority(seed, tick, tr, tc, field, sr, sc)
            if best_p is None or prio > best_priority:
                best_p, best_priority = p, prio
        assert best_p is not None
        winners[(target, field)] = (best_p, best_priority)
    return winners


def commit_template(
    grid: Grid,
    H: int,
    W: int,
    seed: int,
    tick: int,
    mut_numer: int,
    winners: Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]],
    trace: Optional[list] = None,
) -> List[List[int]]:
    """Fields 0-3 only (PHYSICS_SPEC_DRAFT.md phase 4): apply the
    winning value, after Mu, into a mutable copy of the template fields.
    Field 4 (energy) is left untouched here; settle_energy() handles it
    separately. Returns a list-of-lists (mutable) of the 4 template
    fields per site, copied from `grid`."""
    template = [[site[f] for f in TEMPLATE_FIELDS] for row in grid for site in row]
    # Reshape to [row][col][field] for readability below.
    template = [template[r * W : (r + 1) * W] for r in range(H)]
    for (target, field), (winner, _priority) in winners.items():
        if field == ENERGY:
            continue  # settled separately by settle_energy().
        tr, tc = target
        old_value = template[tr][tc][field]
        triggered, bit_index = mu_triggered_and_bit(seed, tick, tr, tc, field, mut_numer)
        stored_value = winner.value ^ (1 << bit_index) if triggered else winner.value
        template[tr][tc][field] = stored_value
        if trace is not None:
            trace.append(("proposal_won", winner.source, target, field, winner.value))
            trace.append(("stored_bits_changed", target, field, old_value != stored_value))
            if triggered:
                trace.append(("mutation_applied", target, field, bit_index))
    return template


def settle_energy(
    grid: Grid,
    H: int,
    W: int,
    write_cost: int,
    maintenance_cost: int,
    replenish_numer: int,
    replenish_amount: int,
    seed: int,
    tick: int,
    proposals: List[Proposal],
    contests: Contests,
    winners: Dict[Tuple[Tuple[int, int], int], Tuple[Proposal, int]],
    trace: Optional[list] = None,
) -> List[List[int]]:
    """Field 4 settlement (PHYSICS_SPEC_DRAFT.md phases 5-7), atomically
    per site. Returns the next tick's H x W energy grid (plain ints)."""
    next_energy = [[site[ENERGY] for site in row] for row in grid]

    # 5a + 5b: every emitting site is debited WRITE_COST; every field-4
    # emitting site is further debited its own transfer_amt. Guaranteed
    # non-negative because non-starved implies energy >= write_cost, and
    # transfer_amt <= energy - write_cost by construction (EMIT phase).
    for p in proposals:
        r, c = p.source
        next_energy[r][c] -= write_cost
        if trace is not None:
            trace.append(("energy_debited", p.source, write_cost))
        if p.field == ENERGY:
            next_energy[r][c] -= p.value
            if trace is not None:
                trace.append(("energy_debited", p.source, p.value))

    # 5c: only the winner of each field-4 contest is credited (the
    # accepted DELTA, saturating at 255); losers' amounts are destroyed.
    for (target, field), plist in contests.items():
        if field != ENERGY:
            continue
        winner, _priority = winners[(target, field)]
        tr, tc = target
        headroom = 255 - next_energy[tr][tc]
        delta = min(winner.value, headroom)
        next_energy[tr][tc] += delta
        overflow = winner.value - delta
        if trace is not None:
            trace.append(("proposal_won", winner.source, target, field, winner.value))
            trace.append(("energy_credited", target, delta))
            if overflow > 0:
                trace.append(("energy_overflow_spilled", target, overflow))
        for p in plist:
            if p is winner:
                continue
            if trace is not None:
                trace.append(("energy_lost", p.source, p.value))

    # 6: maintenance decay, floored at 0.
    for r in range(H):
        for c in range(W):
            d = min(maintenance_cost, next_energy[r][c])
            if d > 0:
                next_energy[r][c] -= d
                if trace is not None:
                    trace.append(("energy_decayed", (r, c), d))

    # 7: independent per-site replenishment, saturating at 255.
    for r in range(H):
        for c in range(W):
            if rho_triggered(seed, tick, r, c, replenish_numer):
                headroom = 255 - next_energy[r][c]
                credited = min(replenish_amount, headroom)
                if credited > 0:
                    next_energy[r][c] += credited
                    if trace is not None:
                        trace.append(("energy_replenished", (r, c), credited))

    return next_energy


def _require_int(name, value, low, high):
    # Reject, never truncate: fractional/nonintegral, bool (int/bool
    # ambiguity), NaN/infinity, numpy scalar, and out-of-range values are all
    # rejected here -- `isinstance(x, int)` is False for numpy int64/float64
    # and for float, and True/False are excluded explicitly despite being
    # `int` subclasses. See ASTRA_CLOSURE_REVIEW_02.md section 3.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an exact int in [{low}, {high}]; got {value!r}")
    if not (low <= value <= high):
        raise ValueError(f"{name} must satisfy {low} <= x <= {high}; got {value}")
    return value


class Aeth01World:
    """One AETH-01 (candidate `aeth01.v1`) lattice state S[t] plus
    (seed, tick, 5 run parameters) needed to compute S[t+1]. Construction
    validates every statically-checkable "Complete replay identity"
    component (PHYSICS_SPEC_DRAFT.md)."""

    SEMANTICS_ID = "aeth01.v1"  # CANDIDATE -- not frozen.

    def __init__(
        self,
        H: int,
        W: int,
        seed: int,
        write_cost: int,
        maintenance_cost: int,
        replenish_numer: int,
        replenish_amount: int,
        mut_numer: int,
        tick: int = 0,
        grid: Optional[Grid] = None,
    ):
        _require_int("H", H, 1, MASK32)
        _require_int("W", W, 1, MASK32)
        _require_int("seed", seed, 0, MASK64)
        _require_int("tick", tick, 0, MASK64)
        for name, value in (
            ("write_cost", write_cost),
            ("maintenance_cost", maintenance_cost),
            ("replenish_amount", replenish_amount),
        ):
            _require_int(name, value, 0, 255)
        for name, value in (
            ("replenish_numer", replenish_numer),
            ("mut_numer", mut_numer),
        ):
            _require_int(name, value, 0, U33_MAX)
        self.H, self.W, self.seed, self.tick = H, W, seed, tick
        self.write_cost = write_cost
        self.maintenance_cost = maintenance_cost
        self.replenish_numer = replenish_numer
        self.replenish_amount = replenish_amount
        self.mut_numer = mut_numer
        if grid is None:
            self.grid: Grid = [[(0, 0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
        else:
            if len(grid) != H or any(len(row) != W for row in grid):
                raise ValueError("grid shape does not match H, W")
            for row in grid:
                for site in row:
                    if len(site) != NUM_FIELDS:
                        raise ValueError(f"invalid site (must be 5 uint8 fields): {site}")
                    for index, field_value in enumerate(site):
                        _require_int("site field %d" % index, field_value, 0, 255)
            self.grid = [[tuple(site) for site in row] for row in grid]

    @classmethod
    def from_bytes(
        cls,
        H: int,
        W: int,
        seed: int,
        write_cost: int,
        maintenance_cost: int,
        replenish_numer: int,
        replenish_amount: int,
        mut_numer: int,
        data: bytes,
        tick: int = 0,
    ):
        """Full H*W*5 uint8 buffer, row-major (row, col, field), field
        order opcode/arg0/arg1/payload/energy (PHYSICS_SPEC_DRAFT.md)."""
        if len(data) != H * W * NUM_FIELDS:
            raise ValueError(
                f"lattice buffer length {len(data)} != H*W*5 ({H * W * NUM_FIELDS})"
            )
        grid: Grid = []
        idx = 0
        for _r in range(H):
            row = []
            for _c in range(W):
                row.append(tuple(data[idx : idx + NUM_FIELDS]))
                idx += NUM_FIELDS
            grid.append(row)
        return cls(
            H, W, seed, write_cost, maintenance_cost, replenish_numer,
            replenish_amount, mut_numer, tick=tick, grid=grid,
        )

    def to_bytes(self) -> bytes:
        out = bytearray(self.H * self.W * NUM_FIELDS)
        idx = 0
        for r in range(self.H):
            for c in range(self.W):
                out[idx : idx + NUM_FIELDS] = bytes(self.grid[r][c])
                idx += NUM_FIELDS
        return bytes(out)

    def step(self, trace: Optional[list] = None) -> "Aeth01World":
        """S[t] -> S[t+1] (PHYSICS_SPEC_DRAFT.md "Tick semantics").
        Returns a NEW world; does not mutate self."""
        if self.tick == MASK64:
            raise TickOverflowError(
                "cannot step from tick == 2**64 - 1 (inherited unchanged from AETH-00)"
            )
        proposals = decode_and_emit(self.grid, self.H, self.W, self.write_cost, trace=trace)
        contests = group_contests(proposals)
        assert_no_duplicate_sources(contests)
        winners = arbitrate(self.seed, self.tick, contests)
        template = commit_template(
            self.grid, self.H, self.W, self.seed, self.tick, self.mut_numer,
            winners, trace=trace,
        )
        next_energy = settle_energy(
            self.grid, self.H, self.W, self.write_cost, self.maintenance_cost,
            self.replenish_numer, self.replenish_amount, self.seed, self.tick,
            proposals, contests, winners, trace=trace,
        )
        next_grid: Grid = [
            [
                (
                    template[r][c][0], template[r][c][1],
                    template[r][c][2], template[r][c][3],
                    next_energy[r][c],
                )
                for c in range(self.W)
            ]
            for r in range(self.H)
        ]
        return Aeth01World(
            self.H, self.W, self.seed, self.write_cost, self.maintenance_cost,
            self.replenish_numer, self.replenish_amount, self.mut_numer,
            tick=self.tick + 1, grid=next_grid,
        )
