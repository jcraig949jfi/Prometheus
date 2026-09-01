"""r0002 — the depth profile, and why r0001 alone is not enough to admit a world.

r0001 asks whether a ONE-PLY greedy heuristic already plays optimally. Its stated
weakness (`ROLE.md` §4) is that greedy reads the world's own score function, which
the world's author also wrote. That admits a specific false positive:

    a world whose score function is a poor proxy for position will show a LARGE
    r0001 gap while still being shallow -- greedy fails, but two plies of search
    finds the answer, and nothing resembling reasoning was ever required.

GATE-W1 would admit that world. It should not.

So the primitive generalises from a scalar to a curve:

    gap(k) = 1 - P[ argmax of depth-k minimax (heuristic eval at the cutoff)
                    lands in optimal(s) ]           over reachable s, |A(s)| >= 2

    r0002  depth profile = ( gap(1), gap(2), gap(3), gap(4) )

A world is worth measuring in only if the gap SURVIVES depth. A curve that
collapses to ~0 by k = 2 describes a world that is merely awkward at one ply, not
one that requires lookahead. The quantity that matters for admission is therefore
the gap at the deepest affordable k, not the gap at k = 1.

The cutoff evaluation is `world.result(s)` applied to a non-terminal state -- the
same score formula the world scores by, read early. That is deliberately the most
FAVOURABLE heuristic available to the cheap player: it knows exactly what the
world rewards. A gap that survives against a searcher armed with the true scoring
function is not an artefact of a badly chosen proxy.

Free: exact, exhaustive where the state set allows, no model calls.
"""
from __future__ import annotations

import json
import pathlib
import random
import statistics
from datetime import datetime, timezone

from ludus.baselines import MIN_BRANCHING, greedy_action
from ludus.worlds import WORLDS, optimal_actions, reachable_states

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"

SEED = 20260826
SAMPLE_N = 250
MAX_DEPTH = 4


def depth_value(world, s, k: int) -> int:
    """Depth-k minimax; at the cutoff, score the position with the world's own
    scoring formula read early. A maximises, B minimises."""
    if world.is_terminal(s):
        return world.result(s)
    if k == 0:
        return world.result(s)
    vals = [depth_value(world, world.apply(s, a), k - 1)
            for a in world.legal_actions(s)]
    return max(vals) if s.to_move == "A" else min(vals)


def depth_actions(world, s, k: int) -> list[str]:
    acts = world.legal_actions(s)
    vals = {a: depth_value(world, world.apply(s, a), k - 1) for a in acts}
    best = max(vals.values()) if s.to_move == "A" else min(vals.values())
    return sorted(a for a, v in vals.items() if v == best)


def profile(world, n=SAMPLE_N, seed=SEED, max_depth=MAX_DEPTH) -> dict:
    rng = random.Random(seed)
    states = [s for s in reachable_states(world)
              if len(world.legal_actions(s)) >= MIN_BRANCHING]
    pool = states if len(states) <= n else rng.sample(states, n)

    opt = {}
    for s in pool:
        opt[s] = set(optimal_actions(world, s))

    out = {"world": world.name, "sampled": len(pool),
           "eligible_states": len(states), "gaps": {}}
    # k = 1 with this eval is NOT identical to r0001's greedy: greedy maximises the
    # mover's OWN score, depth-1 maximises the A-minus-B differential. Both are
    # reported so the two instruments stay comparable rather than conflated.
    g1 = sum(1 for s in pool if greedy_action(world, s) in opt[s]) / len(pool)
    out["r0001_greedy_own_score_gap"] = round(1 - g1, 4)
    for k in range(1, max_depth + 1):
        hits = sum(1 for s in pool
                   if any(a in opt[s] for a in depth_actions(world, s, k)[:1]))
        out["gaps"][f"k={k}"] = round(1 - hits / len(pool), 4)
    gaps = list(out["gaps"].values())
    out["gap_at_max_depth"] = gaps[-1]
    out["survives_depth"] = gaps[-1] >= 0.20
    out["collapse_ratio"] = (round(gaps[-1] / gaps[0], 4) if gaps[0] > 0 else None)
    return out


def main() -> None:
    LEDGER.mkdir(parents=True, exist_ok=True)
    out = {"primitive": "r0002 depth profile",
           "why": "r0001 admits a false positive: a world whose score function is "
                  "a poor proxy shows a large one-ply gap while still being "
                  "shallow. Admission must use the gap at depth, not at k=1.",
           "cutoff_eval": "world.result(s) read early -- the most favourable "
                          "heuristic available to the cheap player",
           "seed": SEED, "sample_n": SAMPLE_N, "max_depth": MAX_DEPTH,
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "worlds": {}}
    for name, w in WORLDS.items():
        p = profile(w)
        out["worlds"][name] = p
        curve = "  ".join(f"{k}:{v:.3f}" for k, v in p["gaps"].items())
        print(f"{name:6s} r0001={p['r0001_greedy_own_score_gap']:.3f} | "
              f"depth gap {curve} | survives_depth={p['survives_depth']}")
    path = LEDGER / "cycle001_r0002_depth_profile.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
