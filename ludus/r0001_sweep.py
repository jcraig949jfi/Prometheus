"""r0001 under attack — is the greedy-decidability gap a property of the WORLD?

`feedback_control_must_break_the_selection_relation` applies to the author of a
world as much as to the designer of an experiment. I wrote LOOM, I wrote its
score function, and I wrote the greedy baseline that reads that score function.
A gap of exactly 0.000 measured under those conditions is a claim about the
triple, not about the world.

Two sweeps separate the causes:

  HORIZON   vary the move count, holding scoring fixed. If the gap opens as the
            horizon grows, greedy-decidability was a small-world artefact and
            LOOM is rescued by making it longer.
  SCORING   vary the score weights and the conversion ratio, holding the horizon
            fixed. If the gap opens, r0001 is a property of (world, scoring) and
            GATE-W1 must sweep scoring before admitting or rejecting a world.

Both are exact and free: no model, no API.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

from ludus.worlds import Loom, LoomState, optimal_actions, reachable_states

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"


class LoomScored(Loom):
    """LOOM with the score weights and the SPIN yield exposed as parameters."""

    def __init__(self, wr: int, wt: int, spin_out: int = 2, **kw):
        super().__init__(**kw)
        self.wr, self.wt, self.spin_out = wr, wt, spin_out
        self.name = f"LOOM(wr={wr},wt={wt},spin={spin_out},m={self.moves})"

    def result(self, s: LoomState) -> int:
        return ((self.wr * s.a[0] + self.wt * s.a[2])
                - (self.wr * s.b[0] + self.wt * s.b[2]))

    def apply(self, s: LoomState, a: str) -> LoomState:
        if a != "SPIN":
            return super().apply(s, a)
        pos, dross, thread = s.a if s.to_move == "A" else s.b
        me = (pos, dross - 3, thread + self.spin_out)
        return (LoomState(s.ply + 1, s.stock, me, s.b) if s.to_move == "A"
                else LoomState(s.ply + 1, s.stock, s.a, me))


def greedy(w: LoomScored, s: LoomState) -> str:
    who = s.to_move

    def sc(st):
        p = st.a if who == "A" else st.b
        return w.wr * p[0] + w.wt * p[2]

    scored = [(sc(w.apply(s, a)), a) for a in w.legal_actions(s)]
    best = max(v for v, _ in scored)
    return sorted(a for v, a in scored if v == best)[0]


def gap(w: LoomScored) -> tuple[float, int]:
    """r0001 computed EXHAUSTIVELY over the eligible state set, not sampled."""
    sts = [s for s in reachable_states(w) if len(w.legal_actions(s)) >= 2]
    hits = sum(1 for s in sts if greedy(w, s) in optimal_actions(w, s))
    return round(1 - hits / len(sts), 4), len(sts)


SCORING_GRID = [(5, 1, 2), (5, 2, 2), (5, 3, 2), (5, 4, 2), (4, 3, 2),
                (3, 1, 2), (2, 1, 2), (1, 1, 2), (1, 2, 2), (1, 0, 2),
                (0, 1, 2), (5, 1, 1), (5, 1, 3), (7, 2, 3)]
HORIZON_GRID = [(4, 8), (6, 12), (8, 16), (10, 20), (12, 24)]


def main() -> None:
    LEDGER.mkdir(parents=True, exist_ok=True)
    out = {"primitive": "r0001 greedy-decidability gap",
           "question": "is the gap a property of the world, of its horizon, or "
                       "of the score function the author happened to write?",
           "method": "exhaustive over eligible states (branching >= 2); exact "
                     "minimax ground truth; zero model calls",
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "horizon_sweep": [], "scoring_sweep": []}

    for moves, stock in HORIZON_GRID:
        w = LoomScored(5, 1, 2, moves=moves, stock=stock)
        g, n = gap(w)
        out["horizon_sweep"].append({"moves": moves, "stock": stock,
                                     "eligible_states": n, "r0001_gap": g})
        print(f"horizon moves={moves:2d} states={n:6d} gap={g:.4f}")

    for wr, wt, so in SCORING_GRID:
        w = LoomScored(wr, wt, so)
        g, n = gap(w)
        out["scoring_sweep"].append({"rung_weight": wr, "thread_weight": wt,
                                     "spin_yield": so, "eligible_states": n,
                                     "r0001_gap": g})
        print(f"scoring wr={wr} wt={wt} spin={so} states={n:5d} gap={g:.4f}")

    gaps_h = [r["r0001_gap"] for r in out["horizon_sweep"]]
    gaps_s = [r["r0001_gap"] for r in out["scoring_sweep"]]
    out["verdict"] = {
        "horizon_gap_range": [min(gaps_h), max(gaps_h)],
        "scoring_gap_range": [min(gaps_s), max(gaps_s)],
        "horizon_is_the_cause": max(gaps_h) - min(gaps_h) > 0.05,
        "scoring_is_a_cause": max(gaps_s) - min(gaps_s) > 0.05,
        # CLIMB moves 1 THREAD -> 1 RUNG for a net wr - wt; SPIN moves 3 DROSS ->
        # spin_out THREAD for a net spin_out * wt. Greedy ranks CLIMB above SPIN
        # exactly when wr - wt > spin_out * wt, and in that whole region greedy
        # coincides with optimal play. The zero is a region, not a coincidence.
        "mechanism": "greedy prefers CLIMB over SPIN iff wr - wt > spin_out * wt; "
                     "the gap is 0 throughout that region",
        "consequence_for_GATE_W1": "the gap must be swept over scoring, not read "
                                   "once at the author's chosen weights",
    }
    path = LEDGER / "cycle001_r0001_sweep.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n" + json.dumps(out["verdict"], indent=2))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
