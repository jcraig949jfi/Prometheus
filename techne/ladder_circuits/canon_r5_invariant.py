"""CANON R5 — invariant detection. (Canon v2.0 §3; numbering per RUNG_LABEL_CORRECTION.md.)

Canon: *"Kill: a near-identical problem where the obvious invariant is insufficient. Math:
mutilated chessboard (parity); monovariants in termination proofs. Artifact: the conserved
quantity, NAMED."*

The artifact requirement is the whole rung. A circuit that outputs "impossible" has said
nothing; a circuit that outputs *"colour-count difference is conserved by every domino
placement, and the mutilated board starts at ±2"* has produced something checkable — and
checkably WRONG when it is wrong.

Three circuits, chosen so the two canon-implied traps are separable:
- InvariantReasoner: proposes a quantity, VERIFIES conservation under the move set on sampled
  states, then checks DECISIVENESS (does it actually separate start from goal?). Reports the
  named quantity or abstains.
- ParityPatternMatcher (trap 1): answers "parity, impossible" for anything board-shaped,
  without checking that the quantity is conserved by THIS move set. Right on the classic,
  wrong the moment the moves change.
- ConservedButUselessReporter (trap 2): reports a quantity that IS genuinely conserved but is
  not decisive (it takes the same value on start and goal), so it proves nothing. Passes any
  battery that only checks "is the reported quantity conserved?".

Together those two traps are the reason the artifact needs BOTH properties checked:
conservation without decisiveness is vacuous; decisiveness without conservation is a guess.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

Cell = Tuple[int, int]
Placement = Tuple[Cell, Cell]           # a domino/tromino covering two or more cells


@dataclass(frozen=True)
class TilingProblem:
    """Cover `board` exactly using pieces drawn from `moves`. `name` is for reporting."""

    name: str
    board: FrozenSet[Cell]
    moves: Tuple[str, ...]              # e.g. ("horizontal", "vertical") or ("horizontal",)


def full_board(n: int = 8) -> FrozenSet[Cell]:
    return frozenset((r, c) for r in range(n) for c in range(n))


def mutilated_board(n: int = 8) -> FrozenSet[Cell]:
    """Opposite corners removed — the canon's named probe. Both removed cells share a colour,
    so the colour counts differ by 2 and no domino tiling exists."""
    return full_board(n) - {(0, 0), (n - 1, n - 1)}


def same_colour_removed_board(n: int = 8) -> FrozenSet[Cell]:
    """A NEAR-IDENTICAL problem where the obvious invariant is INSUFFICIENT: remove two cells
    of OPPOSITE colour. Colour parity is now balanced, so the parity argument says nothing —
    and the honest answer is 'this invariant does not decide it'."""
    return full_board(n) - {(0, 0), (0, 1)}


#: Candidate invariants: name -> (value function, the moves under which it is conserved)
def colour_difference(board: FrozenSet[Cell]) -> int:
    """#black - #white under the standard chequer colouring."""
    return sum(1 if (r + c) % 2 == 0 else -1 for r, c in board)


def cell_count(board: FrozenSet[Cell]) -> int:
    return len(board)


def row_zero_count(board: FrozenSet[Cell]) -> int:
    """A quantity that is conserved by nothing in particular — included as a decoy."""
    return sum(1 for r, _c in board if r == 0)


CANDIDATES: Dict[str, Callable[[FrozenSet[Cell]], int]] = {
    "colour_difference": colour_difference,
    "cell_count_mod_2": lambda b: cell_count(b) % 2,
    "row_zero_count": row_zero_count,
}


@dataclass
class InvariantClaim:
    """The artifact: the conserved quantity, NAMED, with both properties recorded."""

    quantity: Optional[str]
    conserved: bool = False
    decisive: bool = False
    start_value: Optional[int] = None
    goal_value: Optional[int] = None
    verdict: str = "abstain"            # "impossible" | "abstain"

    @property
    def is_supported(self) -> bool:
        """An impossibility verdict is supported only by a quantity that is BOTH conserved
        and decisive."""
        return self.verdict != "impossible" or (self.conserved and self.decisive)


def _domino_delta(quantity: Callable[[FrozenSet[Cell]], int], moves: Sequence[str]) -> Set[int]:
    """How much the quantity changes when one legal piece is removed, over sample placements.
    Conserved (in the relevant sense) iff every legal move changes it by the same amount."""
    deltas: Set[int] = set()
    probe = full_board(6)
    for r in range(5):
        for c in range(5):
            for move in moves:
                if move == "horizontal":
                    piece = {(r, c), (r, c + 1)}
                elif move == "vertical":
                    piece = {(r, c), (r + 1, c)}
                elif move == "diagonal":       # a move set that BREAKS colour balance
                    piece = {(r, c), (r + 1, c + 1)}
                else:
                    continue
                if piece <= probe:
                    deltas.add(quantity(probe) - quantity(probe - frozenset(piece)))
    return deltas


@dataclass
class InvariantReasoner:
    """Checks conservation under the ACTUAL move set, then decisiveness. Abstains otherwise."""

    def analyse(self, problem: TilingProblem) -> InvariantClaim:
        for name, fn in CANDIDATES.items():
            deltas = _domino_delta(fn, problem.moves)
            conserved = len(deltas) == 1            # every legal move shifts it identically
            if not conserved:
                continue
            start, goal = fn(problem.board), 0      # goal state: empty board
            per_move = next(iter(deltas))
            # decisive iff the start value cannot be driven to the goal by whole moves
            decisive = per_move == 0 and start != goal
            if decisive:
                return InvariantClaim(name, True, True, start, goal, "impossible")
        return InvariantClaim(None, verdict="abstain")


@dataclass
class ParityPatternMatcher:
    """TRAP 1: says 'parity ⇒ impossible' for anything board-shaped, never checking that the
    quantity is conserved by THIS move set."""

    def analyse(self, problem: TilingProblem) -> InvariantClaim:
        start = colour_difference(problem.board)
        return InvariantClaim("colour_difference", conserved=True, decisive=start != 0,
                              start_value=start, goal_value=0,
                              verdict="impossible" if start != 0 else "abstain")


@dataclass
class ConservedButUselessReporter:
    """TRAP 2: reports a genuinely conserved quantity that is NOT decisive — it takes the
    same value on start and goal, so it proves nothing, while passing any check that only
    asks 'is the reported quantity conserved?'."""

    def analyse(self, problem: TilingProblem) -> InvariantClaim:
        deltas = _domino_delta(CANDIDATES["cell_count_mod_2"], problem.moves)
        conserved = len(deltas) == 1
        start = CANDIDATES["cell_count_mod_2"](problem.board)
        return InvariantClaim("cell_count_mod_2", conserved=conserved, decisive=False,
                              start_value=start, goal_value=0, verdict="impossible")
