"""
Aether AETH-00 (semantics_id aeth00.v1) -- deliberately BROKEN candidate
transition implementations ("mutants"), used ONLY to test that the test
suite (test_mutants.py, test_golden_vectors.py) actually rejects wrong
universes. None of these is, or may ever become, a production
implementation; each encodes exactly one plausible bug relative to
Aether/AETHER_SPEC.md, named after the bug it encodes.

Each mutant function has the same shape as the relevant primary-oracle
stage it corrupts, reusing oracle.py helpers ONLY for the stages it does
NOT deliberately break (this is normal, expected practice for mutation
testing: the point is "does the suite catch this one bug", not
"is this file structurally independent of the oracle").
"""

from typing import Dict, List, Optional, Tuple

from . import oracle as ok

MASK64 = ok.MASK64


def mutant_min_priority_arbitrate(seed: int, tick: int, contests: ok.Contests):
    """Bug: picks the LEAST unsigned priority instead of the greatest."""
    winners = {}
    for (target, field), plist in contests.items():
        best_p, best_priority = None, None
        for p in plist:
            sr, sc = p.source
            tr, tc = target
            prio = ok.arbitration_priority(seed, tick, tr, tc, field, sr, sc)
            if best_p is None or prio < best_priority:
                best_p, best_priority = p, prio
        winners[(target, field)] = (best_p, best_priority)
    return winners


def mutant_signed_priority_arbitrate(seed: int, tick: int, contests: ok.Contests):
    """Bug: compares priorities as signed 64-bit two's complement, so a
    high-bit-set (numerically huge unsigned) priority looks NEGATIVE and
    loses to a small positive-signed one that is unsigned-smaller."""

    def to_signed64(x: int) -> int:
        return x - (1 << 64) if x >= (1 << 63) else x

    winners = {}
    for (target, field), plist in contests.items():
        best_p, best_signed, best_unsigned = None, None, None
        for p in plist:
            sr, sc = p.source
            tr, tc = target
            prio = ok.arbitration_priority(seed, tick, tr, tc, field, sr, sc)
            signed = to_signed64(prio)
            if best_p is None or signed > best_signed:
                best_p, best_signed, best_unsigned = p, signed, prio
        winners[(target, field)] = (best_p, best_unsigned)
    return winners


def mutant_global_arbitration_step(world: "ok.Aeth00World") -> ok.Grid:
    """Bug: groups contests by TARGET CELL ONLY (ignoring field), so
    proposals aimed at different fields of the same cell wrongly compete;
    only the single overall-highest-priority proposal's field is written,
    other genuinely-targeted fields are silently dropped that tick."""
    proposals = ok.decode_proposals(world.grid, world.H, world.W)
    by_cell: Dict[Tuple[int, int], List[ok.Proposal]] = {}
    for p in proposals:
        by_cell.setdefault(p.target, []).append(p)
    next_grid = [[cell for cell in row] for row in world.grid]
    for target, plist in by_cell.items():
        best_p, best_priority = None, -1
        for p in plist:
            sr, sc = p.source
            tr, tc = target
            prio = ok.arbitration_priority(world.seed, world.tick, tr, tc, p.field, sr, sc)
            if prio > best_priority:
                best_p, best_priority = p, prio
        tr, tc = target
        row = list(next_grid[tr][tc])
        row[best_p.field] = best_p.value
        next_grid[tr][tc] = tuple(row)
    return next_grid


def mutant_wrong_direction_step(world: "ok.Aeth00World") -> ok.Grid:
    """Bug: swaps the East/South direction mapping (0=N,1=S,2=E,3=W
    instead of the frozen 0=N,1=E,2=S,3=W)."""
    H, W = world.H, world.W

    def wrong_neighbor(row, col, direction):
        if direction == 0:
            return (row - 1) % H, col
        if direction == 1:
            return (row + 1) % H, col  # BUG: should be East
        if direction == 2:
            return row, (col + 1) % W  # BUG: should be South
        return row, (col - 1) % W

    proposals = []
    for r in range(H):
        for c in range(W):
            opcode, arg0, arg1, payload = world.grid[r][c]
            if opcode != ok.WRITE_OPCODE:
                continue
            target = wrong_neighbor(r, c, arg0 % 4)
            proposals.append(ok.Proposal((r, c), target, arg1 % 4, payload))
    contests = ok.group_contests(proposals)
    winners = ok.arbitrate(world.seed, world.tick, contests)
    return ok.commit(world.grid, H, W, winners)


def mutant_duplicate_source_proposals(world: "ok.Aeth00World") -> ok.Contests:
    """Bug: at small dimensions where a source's own N/S (or E/W) resolve
    to the same physical target, the (defective) decoder emits TWO
    proposal records for that one source cell -- one "as if via N" and
    one "as if via S" -- instead of the single proposal the frozen
    proposal-identity rule requires. Returns raw contests (not a
    committed grid) so the harness-level duplicate-source detector
    (oracle.assert_no_duplicate_sources) can be exercised directly."""
    H, W = world.H, world.W
    proposals: List[ok.Proposal] = []
    for r in range(H):
        for c in range(W):
            opcode, arg0, arg1, payload = world.grid[r][c]
            if opcode != ok.WRITE_OPCODE:
                continue
            field = arg1 % 4
            n_target = ok.neighbor(r, c, H, W, ok.NORTH)
            s_target = ok.neighbor(r, c, H, W, ok.SOUTH)
            direction = arg0 % 4
            real_target = ok.neighbor(r, c, H, W, direction)
            proposals.append(ok.Proposal((r, c), real_target, field, payload))
            if n_target == s_target and direction in (ok.NORTH, ok.SOUTH):
                # BUG: manufactures a second competitor from the SAME source.
                proposals.append(ok.Proposal((r, c), real_target, field, payload))
    return ok.group_contests(proposals)


def mutant_priority_payload_swap_step(world: "ok.Aeth00World") -> ok.Grid:
    """Bug: priority/winner SELECTION is correct, but the value actually
    committed is taken from the first-enumerated proposal in the contest
    rather than from the winning proposal -- detectable only by checking
    that the committed value matches the WINNER's own payload, not merely
    that some valid proposal's value was written."""
    proposals = ok.decode_proposals(world.grid, world.H, world.W)
    contests = ok.group_contests(proposals)
    winners = ok.arbitrate(world.seed, world.tick, contests)
    next_grid = [[cell for cell in row] for row in world.grid]
    for (target, field), (_winner, _priority) in winners.items():
        first_proposal = contests[(target, field)][0]  # BUG: ignores _winner
        tr, tc = target
        row = list(next_grid[tr][tc])
        row[field] = first_proposal.value
        next_grid[tr][tc] = tuple(row)
    return next_grid


def _mix_no_wrap(x: int) -> int:
    """Bug: SplitMix64 finalizer with the `& MASK64` wraps removed; Python
    ints are unbounded, so multiplication never wraps modulo 2**64."""
    u = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9
    v = (u ^ (u >> 27)) * 0x94D049BB133111EB
    return v ^ (v >> 31)


def mutant_priority_missing_wrap(
    seed: int, tick: int, tr: int, tc: int, field: int, sr: int, sc: int
) -> int:
    h0 = _mix_no_wrap(seed ^ 0x9E3779B97F4A7C15)
    h1 = _mix_no_wrap(h0 ^ tick)
    h2 = _mix_no_wrap(h1 ^ ok.pack_coords(tr, tc))
    h3 = _mix_no_wrap(h2 ^ field)
    return _mix_no_wrap(h3 ^ ok.pack_coords(sr, sc))


def mutant_in_place_sequential_step(world: "ok.Aeth00World") -> ok.Grid:
    """Bug: violates tick-start snapshot semantics. Processes cells in
    row-major order, decoding and immediately committing each cell's
    write against whatever the grid ALREADY looks like this tick (so an
    earlier cell's write can be observed, same tick, by a later cell's
    decode) instead of decoding every cell from a frozen S[t] snapshot
    first. No arbitration is performed; the last sequential writer to a
    given field simply overwrites it."""
    grid = [[cell for cell in row] for row in world.grid]  # mutated as we go
    H, W = world.H, world.W
    for r in range(H):
        for c in range(W):
            opcode, arg0, arg1, payload = grid[r][c]  # BUG: reads mutated grid
            if opcode != ok.WRITE_OPCODE:
                continue
            tr, tc = ok.neighbor(r, c, H, W, arg0 % 4)
            field = arg1 % 4
            row = list(grid[tr][tc])
            row[field] = payload  # BUG: overwrites immediately, no arbitration
            grid[tr][tc] = tuple(row)
    return grid


class MutantStaleNextState:
    """Bug: forgets to re-copy the CURRENT snapshot as the base for the
    next state; instead commits winners onto whatever grid object was
    used as the base one call ago, so any field that changed on the
    previous tick without being re-touched this tick reverts to its
    value from two ticks back. Stateful by construction: call step() on
    the SAME instance repeatedly to observe the one-tick lag."""

    def __init__(self):
        self._stale_base: Optional[ok.Grid] = None

    def step(self, world: "ok.Aeth00World") -> ok.Grid:
        proposals = ok.decode_proposals(world.grid, world.H, world.W)
        contests = ok.group_contests(proposals)
        winners = ok.arbitrate(world.seed, world.tick, contests)
        base = self._stale_base if self._stale_base is not None else world.grid
        next_grid = ok.commit(base, world.H, world.W, winners)  # BUG: stale base
        self._stale_base = [[cell for cell in row] for row in world.grid]
        return next_grid
