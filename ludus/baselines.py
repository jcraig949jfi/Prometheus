"""LUDUS cycle 001, step 0 — the attainable range, measured before any model call.

`feedback_gate_must_be_shown_reachable`: compute the attainable range of an
instrument before reading anything off it. `feedback_counter_baseline_discriminator`:
the bar is never "beats random".

So this module answers, with zero API spend:

  * How wide is the band between a uniform-random LEGAL player and perfect play,
    at each rung of the ladder, in each world?
  * Does a one-ply greedy heuristic already close that band? If greedy scores
    ~perfect on rung R2, then R2 does not measure lookahead and is the wrong
    rung to read a ceiling from — the item set must be re-stratified or the
    world retired, BEFORE a model is pointed at it.
  * What is the majority-class score — i.e. what does "always say the modal
    answer" get, with no reading of the state at all?

Any rung where greedy or majority-class already sits near 1.0 is REPORTED AS
DEGENERATE and is not eligible to carry a ceiling reading.
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
import statistics
from datetime import datetime, timezone

from ludus.worlds import WORLDS, optimal_actions, reachable_states, solve

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ludus" / "ledgers"

#: Items are drawn only from states with >= 2 legal actions. A state with one
#: legal action makes rungs R0 and R2 trivially correct and would inflate every
#: score by an amount that varies per world — a per-item chance floor masquerading
#: as capability.
MIN_BRANCHING = 2
SAMPLE_N = 300
SEED = 20260826


def greedy_action(world, s) -> str:
    """One-ply greedy: the action maximising the mover's own immediate score.

    Deliberately naive and deliberately cheap. This is the counter-baseline R2
    has to beat before "strategic competence" means anything.
    """
    def own_score(st, who):
        if world.name.startswith("LOOM"):
            p = st.a if who == "A" else st.b
            return 5 * p[0] + p[2]
        if world.name.startswith("WEIR"):
            purse = st.ba if who == "A" else st.bb
            ends = ("P", "U") if who == "A" else ("Q", "R")
            mark = 1 if who == "A" else 2
            return (10 if world._connected(st.owner, mark, ends) else 0) + purse
        p = (st.ta, st.pa) if who == "A" else (st.tb, st.pb)
        return 2 * p[0] + p[1]

    who = s.to_move
    acts = world.legal_actions(s)
    scored = [(own_score(world.apply(s, a), who), a) for a in acts]
    best = max(v for v, _ in scored)
    # Deterministic tie-break by action name. AMA's fingerprint audit found that
    # resolving argmax ties to the first element smuggles a positional prior into
    # a measurement; here the tie-break is explicit and reported.
    return sorted(a for v, a in scored if v == best)[0]


def profile(world, n=SAMPLE_N, seed=SEED) -> dict:
    rng = random.Random(seed)
    states = [s for s in reachable_states(world)
              if len(world.legal_actions(s)) >= MIN_BRANCHING]
    pool = states if len(states) <= n else rng.sample(states, n)

    vocab = world_vocabulary(world)
    r0_random, r2_random = [], []
    r2_greedy, opt_first = [], []
    values, branch, nopt = [], [], []

    for s in pool:
        legal = world.legal_actions(s)
        opt = optimal_actions(world, s)
        branch.append(len(legal))
        nopt.append(len(opt))
        # R0: emit any legal action. Random draw is from the world's full action
        # vocabulary, which is what a model that ignores the state can produce.
        r0_random.append(len(legal) / len(vocab))
        # R2: emit an optimal action, given the answer must be legal.
        r2_random.append(len(opt) / len(legal))
        r2_greedy.append(1.0 if greedy_action(world, s) in opt else 0.0)
        opt_first.append(opt[0])
        values.append(solve(world, s))

    mode_act, mode_ct = collections.Counter(opt_first).most_common(1)[0]
    val_mode, val_ct = collections.Counter(values).most_common(1)[0]

    return {
        "world": world.name,
        "reachable_nonterminal": len(reachable_states(world)),
        "eligible_states_branching_ge_2": len(states),
        "sampled": len(pool),
        "action_vocabulary": len(vocab),
        "branching": {"mean": round(statistics.mean(branch), 3),
                      "min": min(branch), "max": max(branch)},
        "optimal_set_size_mean": round(statistics.mean(nopt), 3),
        "R0_random_legal_rate": round(statistics.mean(r0_random), 4),
        "R2_random_legal_player": round(statistics.mean(r2_random), 4),
        "R2_greedy_1ply": round(statistics.mean(r2_greedy), 4),
        "R2_majority_class": round(mode_ct / len(pool), 4),
        "R2_majority_action": mode_act,
        "R3_value_spread": {"min": min(values), "max": max(values),
                            "distinct": len(set(values))},
        "R3_majority_class": round(val_ct / len(pool), 4),
        "R3_majority_value": val_mode,
    }


def world_vocabulary(world) -> list[str]:
    """Every action string the world can ever accept, in any state."""
    if world.name.startswith("LOOM"):
        return ["DRAW", "SPIN", "CLIMB", "WAIT"]
    if world.name.startswith("WEIR"):
        return [f"TAKE {i}" for i in range(9)] + ["YIELD"]
    return ["CLAIM", "DECLINE"]


def headroom_verdict(p: dict) -> dict:
    """A rung is eligible to carry a ceiling reading only if a cheap
    state-blind or one-ply strategy does NOT already solve it."""
    notes = []
    r2_floor = max(p["R2_random_legal_player"], p["R2_greedy_1ply"],
                   p["R2_majority_class"])
    if p["R0_random_legal_rate"] >= 0.75:
        notes.append("R0 DEGENERATE: a state-blind guess is legal >=75% of the "
                     "time; this world cannot carry a legality ceiling.")
    if r2_floor >= 0.80:
        notes.append(f"R2 DEGENERATE: cheap floor {r2_floor:.2f} leaves <0.20 "
                     "headroom to perfect play.")
    if p["R3_majority_class"] >= 0.60:
        notes.append("R3 DEGENERATE: one value dominates; predicting the mode "
                     "scores most of the rung.")
    return {"R2_cheap_floor": round(r2_floor, 4),
            "R2_headroom_to_perfect": round(1.0 - r2_floor, 4),
            "R0_headroom_to_perfect": round(1.0 - p["R0_random_legal_rate"], 4),
            "eligible": not notes,
            "notes": notes}


def main() -> None:
    LEDGER.mkdir(parents=True, exist_ok=True)
    out = {"purpose": "attainable-range map for the LUDUS ladder, computed with "
                      "zero model calls; determines which rungs are eligible to "
                      "carry a ceiling reading",
           "seed": SEED, "sample_n": SAMPLE_N,
           "min_branching": MIN_BRANCHING,
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "worlds": {}}
    for name, w in WORLDS.items():
        p = profile(w)
        p["headroom"] = headroom_verdict(p)
        out["worlds"][name] = p
        print(json.dumps(p, indent=2))
    path = LEDGER / "cycle001_attainable_range.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
